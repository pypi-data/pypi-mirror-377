#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
endnote_utils.fullscreen

One-shot pipeline:
  (1) Export EndNote XML / RIS → CSV/JSON/XLSX (+TXT report)
  (2) LLM screening the resulting CSV → add columns (exclude, reason, ...)
      and write a separate LLM log/report if your screen module does so.

Console script entry point: endnote-full-screen
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---- Import core exporter & screen engine ----
from endnote_utils.core import (
    CSV_QUOTING_MAP,
    DEFAULT_FIELDNAMES,
    export_files_with_report,  # returns (total, out_path, report_path)
)
from endnote_utils.screen import (
    DEFAULT_LOG_EVERY,
    DEFAULT_MAX_TOKENS,
    DEFAULT_NUM_CTX,
    DEFAULT_TEMPERATURE,
    MODEL_PRESETS,  # presets: qwen / mistral
    screen_csv_with_ollama,  # returns (processed, wrote) OR (processed, wrote, llm_report_path)
)

SUPPORTED_FORMATS = ("csv", "json", "xlsx")
EXT_TO_FORMAT = {".csv": "csv", ".json": "json", ".xlsx": "xlsx"}


# ----------------------------
# Helpers (inputs / outputs)
# ----------------------------

def _resolve_inputs(args: argparse.Namespace) -> List[Path]:
    """
    Build list of input files for export stage.
    Supports:
      --xml (single) OR --ris (single) OR --folder (mixed .xml/.ris)
    If --csv-in is used, this function won't be called.
    """
    if args.xml:
        p = Path(args.xml)
        if not p.is_file():
            raise FileNotFoundError(p)
        return [p]
    if args.ris:
        p = Path(args.ris)
        if not p.is_file():
            raise FileNotFoundError(p)
        return [p]
    if args.folder:
        folder = Path(args.folder)
        if folder.is_file():
            raise SystemExit(f"--folder expects a directory, but got a file: {folder}")
        if not folder.is_dir():
            raise FileNotFoundError(folder)
        # accept mixed XML & RIS
        inputs = sorted([*folder.glob("*.xml"), *folder.glob("*.ris")])
        inputs = [p for p in inputs if p.is_file()]
        if not inputs:
            raise FileNotFoundError(f"No *.xml or *.ris found in folder: {folder}")
        return inputs
    raise SystemExit("You must provide one of: --xml | --ris | --folder | --csv-in")


def _infer_format_from_path(out_path: Path) -> str:
    fmt = EXT_TO_FORMAT.get(out_path.suffix.lower())
    if not fmt:
        raise SystemExit(
            "Cannot infer output format from extension. "
            "Use --format {csv,json,xlsx} or set a supported extension."
        )
    return fmt


def _resolve_export_outputs(args: argparse.Namespace) -> Tuple[Optional[Path], Optional[str], Optional[Path]]:
    """
    Decide final out_path, out_format, and report_path for the export stage.
    """
    if args.out is None and args.csv_in is None:
        raise SystemExit("Provide either --out for export+screen OR --csv-in to only screen an existing CSV.")

    out_path: Optional[Path] = Path(args.out) if args.out else None
    out_format: Optional[str] = None
    report_path: Optional[Path] = None

    if out_path:
        if args.format:
            out_format = args.format.lower()
            if out_format not in SUPPORTED_FORMATS:
                raise SystemExit(f"--format must be one of: {', '.join(SUPPORTED_FORMATS)}")
        else:
            out_format = _infer_format_from_path(out_path)
        # Always set export report path (export stage)
        report_path = Path(args.report) if args.report else out_path.with_name(out_path.stem + "_report.txt")
    else:
        # screen-only mode (csv-in provided). No export out_path/format/report needed.
        report_path = None

    return out_path, out_format, report_path


# ----------------------------
# Pipeline
# ----------------------------

def run_full_screen(
    args: argparse.Namespace,
) -> Tuple[int, Path, Optional[Path], int]:
    """
    Execute export (optional) then screen.
    Returns (exported_rows, screened_csv_path, export_report_path, screened_rows).
    """

    # Resolve model from preset (qwen / mistral), with user's overrides
    effective_model = args.model
    effective_temp = args.temperature
    effective_max_tokens = args.max_tokens
    effective_num_ctx = args.num_ctx

    if args.preset:
        cfg = MODEL_PRESETS[args.preset]
        effective_model = cfg.get("model", effective_model or cfg.get("model"))
        # Only override temp/tokens if user left them at defaults
        if args.temperature == DEFAULT_TEMPERATURE:
            effective_temp = cfg.get("temperature", effective_temp)
        if args.max_tokens == DEFAULT_MAX_TOKENS:
            effective_max_tokens = cfg.get("max_tokens", effective_max_tokens)
        # num_ctx from preset always applied unless user custom-set a different value
        if args.num_ctx == DEFAULT_NUM_CTX:
            effective_num_ctx = cfg.get("num_ctx", effective_num_ctx)

    # Decide export parameters
    out_path, out_format, export_report_path = _resolve_export_outputs(args)

    # If user provided --csv-in, skip export stage (screen-only)
    if args.csv_in:
        csv_in = Path(args.csv_in)
        if not csv_in.is_file():
            raise FileNotFoundError(csv_in)
        # We'll write screened CSV to args.out (must end with .csv)
        if out_path is None:
            raise SystemExit("When using --csv-in, you must still provide --out (a CSV path) for screened results.")
        if out_path.suffix.lower() != ".csv":
            raise SystemExit("--out must be a .csv path when using --csv-in (screen-only mode).")

        logging.info("Screen-only mode: using existing CSV: %s", csv_in)
        export_total = 0  # no export
        screened_out = out_path
        screened_out.parent.mkdir(parents=True, exist_ok=True)

        # Call screen engine (accept 2 or 3 return values)
        result = screen_csv_with_ollama(
            input_csv=csv_in,
            output_csv=screened_out,
            criteria_txt=Path(args.criteria),
            model=effective_model,
            title_col=args.title_col,
            abstract_col=args.abstract_col,
            temperature=effective_temp,
            max_tokens=effective_max_tokens,
            num_ctx=effective_num_ctx,
            retry=args.retry,
            max_records=args.max_records,
            log_every=args.log_every,
        )
        if isinstance(result, tuple):
            if len(result) == 2:
                processed, wrote = result
            else:
                processed, wrote = result[0], result[1]  # ignore any extra returns
        else:
            processed = wrote = int(result)

        return export_total, screened_out, None, wrote

    # Otherwise: run export
    inputs = _resolve_inputs(args)
    logging.info("Export stage: %d input file(s)", len(inputs))

    # Always write export TXT report (export_report_path computed earlier)
    export_total, export_out_path, export_report_written = export_files_with_report(
        inputs=inputs,
        out_path=out_path,                   # type: ignore[arg-type]
        out_format=out_format,               # type: ignore[arg-type]
        fieldnames=DEFAULT_FIELDNAMES,
        delimiter=args.delimiter,
        quoting=args.quoting,
        include_header=not args.no_header,
        encoding=args.encoding,
        ref_type=args.ref_type,
        year=args.year,
        max_records_per_file=args.max_records_export,
        report_path=export_report_path,
        # If your core supports these kwargs; otherwise remove:
        dedupe=args.dedupe,
        dedupe_keep=args.dedupe_keep,
        stats=args.stats,
        stats_json=(Path(args.stats_json) if args.stats_json else None),
    )

    # Ensure we surface the actual report path written (for logging)
    export_report_path = export_report_written

    # We need a CSV to feed into the screen stage.
    # If user exported json/xlsx, create a CSV next to it. If exported csv, use it directly.
    export_out = export_out_path  # type: ignore[assignment]
    if out_format != "csv":
        screen_input_csv = export_out.with_suffix(".csv")
        logging.info("Exported format is %s; creating CSV for screening: %s", out_format, screen_input_csv)
        # Re-run a lightweight export to CSV WITHOUT another report
        export_files_with_report(
            inputs=inputs,
            out_path=screen_input_csv,
            out_format="csv",
            fieldnames=DEFAULT_FIELDNAMES,
            delimiter=args.delimiter,
            quoting=args.quoting,
            include_header=not args.no_header,
            encoding=args.encoding,
            ref_type=args.ref_type,
            year=args.year,
            max_records_per_file=args.max_records_export,
            report_path=None,   # don't create a duplicate report for the helper CSV
            dedupe=args.dedupe,
            dedupe_keep=args.dedupe_keep,
            stats=False,
        )
    else:
        screen_input_csv = export_out

    # IMPORTANT: never screen "in-place".
    # Always write screening results to a DIFFERENT file <stem>_screened.csv
    screened_out = export_out.with_name(export_out.stem + "_screened.csv")

    result = screen_csv_with_ollama(
        input_csv=screen_input_csv,
        output_csv=screened_out,
        criteria_txt=Path(args.criteria),
        model=effective_model,
        title_col=args.title_col,
        abstract_col=args.abstract_col,
        temperature=effective_temp,
        max_tokens=effective_max_tokens,
        num_ctx=effective_num_ctx,
        retry=args.retry,
        max_records=args.max_records,
        log_every=args.log_every,
    )
    if isinstance(result, tuple):
        if len(result) == 2:
            processed, wrote = result
        else:
            processed, wrote = result[0], result[1]
    else:
        processed = wrote = int(result)

    return export_total, screened_out, export_report_path, wrote


# ----------------------------
# CLI
# ----------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Export EndNote XML/RIS → CSV/JSON/XLSX then LLM-screen the CSV in one command."
    )

    # Input source (mutually exclusive) — OR use --csv-in to skip export
    g = p.add_mutually_exclusive_group(required=False)
    g.add_argument("--xml", help="Path to a single EndNote XML file. Example: --xml data/IEEE.xml")
    g.add_argument("--ris", help="Path to a single RIS file. Example: --ris data/PubMed.ris")
    g.add_argument("--folder", help="Path to a folder containing *.xml / *.ris files. Example: --folder data/refs")
    p.add_argument("--csv-in", help="Skip export and screen an existing CSV. Example: --csv-in output/all.csv")

    # Export output (required unless using --csv-in)
    p.add_argument("--out", help="Final export path (CSV/JSON/XLSX) OR screened CSV (when --csv-in).")
    p.add_argument(
        "--format",
        choices=SUPPORTED_FORMATS,
        help="Export format if not inferred from --out extension.",
    )
    p.add_argument("--report", help="Export TXT report path (default: <out>_report.txt).")

    # CSV formatting (export)
    p.add_argument("--delimiter", default=",", help="CSV delimiter (export). Default: ','.")
    p.add_argument(
        "--quoting",
        default="minimal",
        choices=list(CSV_QUOTING_MAP.keys()),
        help="CSV quoting mode (export). Default: minimal.",
    )
    p.add_argument("--no-header", action="store_true", help="Do not write CSV header row (export).")
    p.add_argument("--encoding", default="utf-8", help="Output encoding (export). Default: utf-8.")

    # Filters / limits (export)
    p.add_argument("--ref-type", default=None, help="Filter by ref_type name (export).")
    p.add_argument("--year", default=None, help="Filter by year (export).")
    p.add_argument("--max-records-export", type=int, default=None, help="Stop after N records per file (export testing).")

    # Dedup & stats (export)
    p.add_argument("--dedupe", choices=["none", "doi", "title-year"], default="none", help="Deduplicate mode (export).")
    p.add_argument("--dedupe-keep", choices=["first", "last"], default="first", help="Which duplicate to keep (export).")
    p.add_argument("--stats", action="store_true", help="Add summary stats to export report.")
    p.add_argument("--stats-json", help="Save export stats+duplicates as JSON to this path.")

    # Screening (LLM) — presets or manual knobs
    p.add_argument(
        "--preset",
        choices=list(MODEL_PRESETS.keys()),
        default="qwen",
        help="LLM preset to use. Choices: " + ", ".join(MODEL_PRESETS.keys()) + " (default: qwen)",
    )
    p.add_argument("--model", default=None, help="Override model name (rarely needed if using --preset).")
    p.add_argument("--title-col", default="title", help="Column name for title (screen). Default: 'title'.")
    p.add_argument("--abstract-col", default="abstract", help="Column name for abstract (screen). Default: 'abstract'.")
    p.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE, help="Sampling temperature (screen).")
    p.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, help="Max tokens to generate (screen).")
    p.add_argument("--num-ctx", type=int, default=DEFAULT_NUM_CTX, help="Model context window (screen).")
    p.add_argument("--retry", type=int, default=3, help="Retry attempts on model error (screen).")
    p.add_argument("--criteria", required=True, help="Path to criteria.txt used by the LLM (screen).")
    p.add_argument("--max-records", type=int, default=None, help="Limit rows for screening (testing).")
    p.add_argument("--log-every", type=int, default=DEFAULT_LOG_EVERY, help="Log progress every N rows (screen).")
    p.add_argument("--log-file", help="Optional path to write a screening log file.")

    # Verbosity
    p.add_argument("--verbose", action="store_true", help="Verbose logging.")

    return p


def main() -> None:
    args = _build_parser().parse_args()

    # Logging handlers: console
    handlers: List[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
        handlers=handlers,
    )

    try:
        # Basic validation for typical misuse
        if args.folder and Path(args.folder).is_file():
            raise SystemExit(f"--folder expects a directory, but got a file: {args.folder}")

        if not args.csv_in and not args.out:
            raise SystemExit("Missing --out. Provide --out for export+screen, or use --csv-in to screen an existing CSV.")

        if args.csv_in and args.out and Path(args.out).suffix.lower() != ".csv":
            raise SystemExit("--out must end with .csv when using --csv-in (screen-only mode).")

        # Show essentials
        if args.csv_in:
            logging.info("Mode: screen-only (using CSV): %s", args.csv_in)
        else:
            logging.info("Mode: export + screen")

        logging.info("Preset: %s", args.preset or "-")
        if args.model:
            logging.info("Model override: %s", args.model)
        logging.info("Criteria: %s", args.criteria)

        # Run pipeline
        export_total, screened_out, export_report, wrote = run_full_screen(args)

        if export_total:
            logging.info("Exported %d record(s).", export_total)
        logging.info("Screened output → %s", screened_out)
        if export_report:
            logging.info("Export report → %s", export_report)
        if args.log_file:
            logging.info("Screen log → %s", args.log_file)

    except KeyboardInterrupt:
        logging.warning("Interrupted by user (Ctrl+C).")
        sys.exit(130)
    except Exception as e:
        logging.error("Error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
