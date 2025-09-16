#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
endnote_utils.screen

Screen papers (title + abstract) using a local LLM via Ollama.

- NO JSON requirement. Model replies in a 3-line template parsed via regex.
- Abstract is CHUNKED (not truncated) into multiple parts for the prompt.
- On EMPTY_RESPONSE only, do a one-shot fallback with a softer title-only prompt.
- Logging with progress, ETA, retries
- --log-file writes a full log to disk (with timestamps)
- Presets: qwen (qwen2.5:7b-instruct), mistral (mistral-nemo:12b)
- Writes an LLM TXT report with decision/engine/input-quality stats.

Console script entry point: endnote-screen
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ----------------------------
# Defaults / env
# ----------------------------
ENV_MAX_RECORDS = os.getenv('MAX_RECORDS')
ENV_LOG_EVERY = os.getenv('LOG_EVERY')  # log progress every N rows

DEFAULT_MODEL = 'qwen2.5:7b-instruct'
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 256
DEFAULT_NUM_CTX = 8192
DEFAULT_RETRY = 3
DEFAULT_LOG_EVERY = int(ENV_LOG_EVERY) if (ENV_LOG_EVERY or '').isdigit() else 25

# --- Model presets ---
MODEL_PRESETS: Dict[str, Dict[str, Any]] = {
    'qwen': {
        'model': 'qwen2.5:7b-instruct',
        'temperature': 0.1,
        'max_tokens': 256,
        'num_ctx': 4096,
    },
    'mistral': {
        'model': 'mistral-nemo:12b',
        'temperature': 0.1,
        'max_tokens': 256,
        'num_ctx': 8192,
    },
}

# Title truncation
TITLE_MAX_CHARS = 300

# Abstract chunking
ABSTRACT_CHUNK_CHARS = 1200  # target size per chunk
ABSTRACT_MAX_CHUNKS = 2  # hard cap; if exceeded -> abstract_truncated=yes

SYSTEM_MSG = """You are an expert reviewer screening AI/XAI papers in healthcare neurology.
Decide INCLUDE / EXCLUDE strictly by the given criteria, or mark as UNCERTAIN.
Reply concisely following the requested template. No extra commentary."""

# ----------------------------
# Helpers
# ----------------------------


def count_rows(csv_path: Path) -> int:
    with csv_path.open(newline='', encoding='utf-8') as f:
        r = csv.reader(f)
        try:
            _ = next(r)
        except StopIteration:
            return 0
        return sum(1 for _ in r)


def load_text(p: Path) -> str:
    return p.read_text(encoding='utf-8')


def _normalize_response_text(text: str) -> str:
    if not text:
        return ''
    s = text.replace('**', '').replace('`', '')
    s = re.sub(r'^[\-\*\u2022]\s*', '', s, flags=re.M)
    s = '\n'.join(line.strip() for line in s.splitlines())
    return s


def _truncate_title(text: str, max_chars: int) -> Tuple[str, bool]:
    s = (text or '').strip()
    if len(s) <= max_chars:
        return s, False
    cut = s[:max_chars]
    if ' ' in cut:
        cut = cut.rsplit(' ', 1)[0]
    return cut + '…', True


def _chunk_text(text: str, chunk_chars: int, max_chunks: int) -> Tuple[List[str], bool]:
    s = (text or '').strip()
    if not s:
        return [], False
    words = s.split()
    chunks: List[str] = []
    curr: List[str] = []
    curr_len = 0
    for w in words:
        add_len = len(w) + (1 if curr else 0)
        if curr_len + add_len > chunk_chars and curr:
            chunks.append(' '.join(curr))
            curr = [w]
            curr_len = len(w)
        else:
            curr.append(w)
            curr_len += add_len
        if len(chunks) == max_chunks:
            break
    if len(chunks) < max_chunks and curr:
        chunks.append(' '.join(curr))
    truncated = False
    if len(chunks) >= max_chunks:
        used_words = ' '.join(chunks).split()
        if len(used_words) < len(words):
            truncated = True
    if truncated and chunks:
        chunks[-1] = chunks[-1].rstrip(' .,…') + '…'
    return chunks, truncated


def build_prompt(criteria: str, title: str, abstract_parts: List[str]) -> str:
    if abstract_parts:
        parts_str = '\n'.join(
            f'Abstract (part {i + 1}/{len(abstract_parts)}): "{abstract_parts[i]}"'
            for i in range(len(abstract_parts))
        )
    else:
        parts_str = 'Abstract: ""'
    return f"""You are an expert reviewer screening AI/XAI papers in healthcare neurology.

Criteria:
{criteria}

Paper:
Title: "{title or ''}"
{parts_str}

Decide if the paper should be included or excluded.
Preferred format = 3 lines:
Decision: include | exclude_no_relevance | exclude_low_relevance | exclude_review | uncertain
Reason: short explanation (max 2 sentences, ≤25 words each; must start with the required prefix)
Confidence: number between 0 and 1

Alternatively, it's OK to reply in ONE line:
<decision> | <reason> | <confidence>
"""


def build_prompt_min(criteria: str, title: str) -> str:
    return f"""You are an expert reviewer.

Criteria (short):
{criteria[:800]}

Title: "{title or ''}"

Answer briefly using these three fields:

Decision: include | exclude_no_relevance | exclude_low_relevance | exclude_review | uncertain
Reason: start with the required prefix; max 2 short sentences
Confidence: 0..1

Alternatively, it's OK to reply in ONE line:
<decision> | <reason> | <confidence>
"""


def call_ollama(
    model: str,
    temperature: float,
    max_tokens: int,
    system: str,
    prompt: str,
    *,
    num_ctx: int = DEFAULT_NUM_CTX,
) -> str:
    url = 'http://localhost:11434/api/generate'
    payload = {
        'model': model,
        'prompt': prompt,
        'system': system,
        'options': {
            'temperature': temperature,
            'num_predict': max_tokens,
            'num_ctx': num_ctx,
        },
        'keep_alive': '30m',
        'stream': False,
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url, data=data, headers={'Content-Type': 'application/json'}, method='POST'
    )
    for spin in range(2):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                raw = resp.read().decode('utf-8', errors='ignore')
        except urllib.error.HTTPError as e:
            raise RuntimeError(
                f'Ollama HTTP {e.code}: {e.read().decode("utf-8", errors="ignore")}'
            )
        except urllib.error.URLError as e:
            raise RuntimeError(f'Ollama server not reachable: {e}')
        obj = json.loads(raw)
        text = (obj.get('response') or '').strip()
        if text:
            return text
        time.sleep(0.8 + 0.4 * spin)
    raise RuntimeError('EMPTY_RESPONSE')


# ---- Output parsing (3-line template or one-line pipes) ----
_DECISION_RE = re.compile(r'^\s*Decision\s*:\s*(.+?)\s*$', re.I | re.M)
_REASON_RE = re.compile(r'^\s*Reason\s*:\s*(.+?)\s*$', re.I | re.M)
_CONF_RE = re.compile(r'^\s*Confidence\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*$', re.I | re.M)
_PIPE_RE = re.compile(
    r'^\s*'
    r'(include|exclude_no_relevance|exclude_low_relevance|exclude_review|uncertain)'
    r'\s*\|\s*'
    r'(.+?)'
    r'\s*\|\s*'
    r'([0-9]+(?:\.[0-9]+)?)'
    r'\s*$',
    re.I | re.M,
)


def parse_model_output(text: str) -> Dict[str, Any]:
    s = _normalize_response_text(text or '')
    m_dec = _DECISION_RE.search(s)
    m_rea = _REASON_RE.search(s)
    m_conf = _CONF_RE.search(s)
    decision = (m_dec.group(1) if m_dec else '').strip().lower()
    reason = (m_rea.group(1) if m_rea else '').strip()
    conf_s = (m_conf.group(1) if m_conf else '').strip()
    if not decision:
        m_pipe = _PIPE_RE.search(s)
        if m_pipe:
            decision = m_pipe.group(1).strip().lower()
            reason = m_pipe.group(2).strip()
            conf_s = m_pipe.group(3).strip()
    conf = 0.0
    try:
        if conf_s:
            cv = float(conf_s)
            conf = cv / 100.0 if 1.0 < cv <= 100.0 else cv
            conf = max(0.0, min(1.0, conf))
    except Exception:
        conf = 0.0
    return {
        'decision': decision,
        'reason_short': reason,
        'confidence': conf,
    }


# ---- Decision mapping & reason formatting ----
def normalize_decision(decision: str) -> str:
    d = (decision or '').strip().lower()
    if d in {
        'include',
        'exclude_no_relevance',
        'exclude_low_relevance',
        'exclude_review',
        'uncertain',
    }:
        return d
    if d in ('exclude', 'excluded'):
        return 'exclude_no_relevance'
    if d in ('include', 'included'):
        return 'include'
    return 'uncertain'


def _clamp_words(sentence: str, max_words: int = 25) -> str:
    words = sentence.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words])
    return sentence


def enforce_reason_format(decision: str, reason_short: str) -> str:
    reason = (reason_short or '').strip()
    if not reason:
        defaults = {
            'exclude_no_relevance': 'no relevance because insufficient alignment with clinical neurology/XAI criteria.',
            'exclude_low_relevance': 'low relevance because the abstract suggests partial alignment but lacks required XAI scope/evaluation.',
            'exclude_review': 'exclude because review article without new empirical XAI results.',
            'uncertain': 'uncertain because the abstract lacks sufficient detail to verify XAI and clinical neurology inclusion criteria.',
        }
        reason = defaults.get(decision, 'no relevance because criteria are not met.')
    prefix_map = {
        'exclude_no_relevance': 'no relevance because',
        'exclude_low_relevance': 'low relevance because',
        'exclude_review': 'exclude because review',
        'uncertain': 'uncertain because',
    }
    prefix = prefix_map.get(decision, 'no relevance because')
    if not reason.lower().startswith(prefix):
        core = reason[0].lower() + reason[1:] if reason else 'criteria are not met.'
        reason = f'{prefix} {core}'
    raw = reason.replace(';', '.')
    sentences = [s.strip() for s in raw.split('.') if s.strip()]
    if not sentences:
        sentences = [f'{prefix} criteria are not met']
    sentences = sentences[:2]
    sentences = [_clamp_words(s, 25).strip() for s in sentences]
    final = '. '.join(sentences)
    if not final.endswith('.'):
        final += '.'
    return final


def decide_columns(decision: str, reason_short: str) -> Dict[str, str]:
    d = normalize_decision(decision)
    if d == 'include':
        return {'exclude': 'no', 'reason': ''}
    if d in ('exclude_no_relevance', 'exclude_low_relevance', 'exclude_review'):
        r = enforce_reason_format(d, reason_short)
        return {'exclude': 'yes', 'reason': r}
    r = enforce_reason_format('uncertain', reason_short)
    return {'exclude': 'maybe', 'reason': r}


# ----------------------------
# LLM report writer
# ----------------------------


def _write_llm_report(
    report_path: Path,
    *,
    start_ts: float,
    end_ts: float,
    input_csv: Path,
    output_csv: Path,
    model: str,
    preset: Optional[str],
    n_rows: int,
    decisions: Counter,
    conf_sum: float,
    conf_n: int,
    engine_events: Dict[str, int],
    input_quality: Dict[str, int],
    reasons_counter: Counter,
    by_db: Dict[str, Counter],
) -> None:
    dt = end_ts - start_ts if end_ts > start_ts else 0.0
    throughput = (n_rows / dt) if dt > 0 else 0.0

    def pct(x: int) -> float:
        return (100.0 * x / n_rows) if n_rows else 0.0

    lines: List[str] = []
    lines += [
        '========================================',
        'LLM Screening Report',
        '========================================',
        f'Started    : {datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M:%S")}',
        f'Finished   : {datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M:%S")}',
        f'Input CSV  : {input_csv}',
        f'Output CSV : {output_csv}',
        f'Model      : {model} (preset={preset or "-"})',
        f'Rows       : {n_rows}',
        f'Duration   : {dt:.2f} seconds',
        f'Throughput : {throughput:.2f} rows/s',
        '',
        'Decisions',
        '----------------------------------------',
        f'include               : {decisions["include"]:6d}  ({pct(decisions["include"]):.1f}%)',
        f'exclude_no_relevance  : {decisions["exclude_no_relevance"]:6d}  ({pct(decisions["exclude_no_relevance"]):.1f}%)',
        f'exclude_low_relevance : {decisions["exclude_low_relevance"]:6d}  ({pct(decisions["exclude_low_relevance"]):.1f}%)',
        f'exclude_review        : {decisions["exclude_review"]:6d}  ({pct(decisions["exclude_review"]):.1f}%)',
        f'uncertain             : {decisions["uncertain"]:6d}  ({pct(decisions["uncertain"]):.1f}%)',
        f'avg confidence        : {(conf_sum / conf_n if conf_n else 0.0):.3f}  (n={conf_n})',
        '',
        'Engine events',
        '----------------------------------------',
        f'EMPTY_RESPONSE        : {engine_events.get("EMPTY_RESPONSE", 0)}',
        f'MISSING_ANSWER        : {engine_events.get("MISSING_ANSWER", 0)}',
        'Fallback (title-only) : '
        f'success={engine_events.get("FALLBACK_OK", 0)}, '
        f'fail={engine_events.get("FALLBACK_FAIL", 0)}',
        '',
        'Input quality',
        '----------------------------------------',
        f'Title truncated       : {input_quality.get("title_trunc", 0)}',
        f'Abstract truncated    : {input_quality.get("abstract_trunc", 0)}',
        '',
        'Top reasons (exact match, top 10)',
        '----------------------------------------',
    ]
    for reason, c in reasons_counter.most_common(10):
        lines.append(f'{c:5d}  {reason}')
    if not reasons_counter:
        lines.append('(no reasons)')
    lines += [
        '',
        'By database (decision counts)',
        '----------------------------------------',
        'Database            include ex_no_rel ex_low_rel  ex_review  uncertain    total',
        '-------------------------------------------------------------------------------',
    ]
    for db in sorted(by_db.keys()):
        c = by_db[db]
        total = (
            c['include']
            + c['exclude_no_relevance']
            + c['exclude_low_relevance']
            + c['exclude_review']
            + c['uncertain']
        )
        lines.append(
            f'{db:<20} {c["include"]:7d} {c["exclude_no_relevance"]:10d} {c["exclude_low_relevance"]:10d}'
            f' {c["exclude_review"]:10d} {c["uncertain"]:10d} {total:8d}'
        )
    if not by_db:
        lines.append('(no database column)')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text('\n'.join(lines), encoding='utf-8')


# ----------------------------
# Core engine (callable API)
# ----------------------------


def screen_csv_with_ollama(
    input_csv: Path,
    output_csv: Path,
    criteria_txt: Path,
    *,
    model: str = DEFAULT_MODEL,
    title_col: str = 'title',
    abstract_col: str = 'abstract',
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    num_ctx: int = DEFAULT_NUM_CTX,
    retry: int = DEFAULT_RETRY,
    max_records: Optional[int] = None,
    log_every: int = DEFAULT_LOG_EVERY,
    preset: Optional[str] = None,
    llm_report_path: Optional[Path] = None,
) -> Tuple[int, int, Path]:
    """
    Screen a CSV and write a new CSV with added columns:
      exclude, reason, truncated_title, abstract_chunks, abstract_truncated
    Also writes a TXT LLM report.
    Returns (processed_rows, wrote_rows, llm_report_path).
    """
    total_rows = count_rows(input_csv)
    logging.info('Input rows (excluding header): %d', total_rows)
    if max_records:
        logging.info('Max records (test mode): %d', max_records)

    criteria = load_text(criteria_txt)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    if llm_report_path is None:
        llm_report_path = output_csv.with_name(output_csv.stem + '_llm_report.txt')

    # Stats
    decisions = Counter()
    conf_sum = 0.0
    conf_n = 0
    engine_events = {
        'EMPTY_RESPONSE': 0,
        'MISSING_ANSWER': 0,
        'FALLBACK_OK': 0,
        'FALLBACK_FAIL': 0,
    }
    input_quality = {'title_trunc': 0, 'abstract_trunc': 0}
    reasons_counter = Counter()
    by_db: Dict[str, Counter] = defaultdict(Counter)

    processed = 0
    wrote = 0
    t_start = time.time()

    with input_csv.open(newline='', encoding='utf-8') as f_in, output_csv.open(
        'w', newline='', encoding='utf-8'
    ) as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames or [])
        for col in (
            'exclude',
            'reason',
            'truncated_title',
            'abstract_chunks',
            'abstract_truncated',
        ):
            if col not in fieldnames:
                fieldnames.append(col)
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row_idx, row in enumerate(reader, 1):
            if max_records and processed >= max_records:
                break

            raw_title = row.get(title_col, '')
            title, title_trunc = _truncate_title(raw_title, TITLE_MAX_CHARS)
            if title_trunc:
                input_quality['title_trunc'] += 1

            raw_abstract = row.get(abstract_col, '')
            parts, was_truncated = _chunk_text(
                raw_abstract, ABSTRACT_CHUNK_CHARS, ABSTRACT_MAX_CHUNKS
            )
            if was_truncated:
                input_quality['abstract_trunc'] += 1

            prompt = build_prompt(criteria, title, parts)

            last_err: Optional[Exception] = None
            raw_text: Optional[str] = None
            resp: Dict[str, Any] = {}
            for attempt in range(1, retry + 1):
                try:
                    raw_text = call_ollama(
                        model,
                        temperature,
                        max_tokens,
                        SYSTEM_MSG,
                        prompt,
                        num_ctx=num_ctx,
                    )
                    resp = parse_model_output(raw_text)
                    break
                except Exception as e:
                    last_err = e
                    if str(e) == 'EMPTY_RESPONSE':
                        engine_events['EMPTY_RESPONSE'] += 1
                        logging.warning(
                            '[Row %d] LLM call failed (attempt %d/%d): EMPTY_RESPONSE',
                            row_idx,
                            attempt,
                            retry,
                        )
                        # Fallback only when EMPTY_RESPONSE: title-only softer prompt
                        try:
                            raw_text_fallback = call_ollama(
                                model,
                                max(0.3, temperature),
                                max_tokens,
                                SYSTEM_MSG,
                                build_prompt_min(criteria, title),
                                num_ctx=num_ctx,
                            )
                            resp = parse_model_output(raw_text_fallback)
                            engine_events['FALLBACK_OK'] += 1
                            logging.info(
                                '[Row %d] Fallback (title-only) succeeded after EMPTY_RESPONSE.',
                                row_idx,
                            )
                            break
                        except Exception as ee:
                            engine_events['FALLBACK_FAIL'] += 1
                            logging.warning(
                                '[Row %d] Fallback (title-only) also failed: %s',
                                row_idx,
                                ee,
                            )
                    else:
                        logging.warning(
                            '[Row %d] LLM call failed (attempt %d/%d): %s',
                            row_idx,
                            attempt,
                            retry,
                            e,
                        )
                    if attempt < retry:
                        time.sleep(1.2 * attempt + 0.2 * (attempt % 3))
            else:
                logging.error(
                    '[Row %d] Giving up after %d attempts. Error=%s',
                    row_idx,
                    retry,
                    last_err,
                )
                resp = {
                    'decision': 'uncertain',
                    'reason_short': 'uncertain because the LLM call failed.',
                    'confidence': 0.0,
                }

            # If model responded but no decision parsed, log MISSING_ANSWER
            if raw_text is not None and isinstance(resp, dict):
                parsed_decision = (resp.get('decision') or '').strip()
                if not parsed_decision:
                    engine_events['MISSING_ANSWER'] += 1
                    snippet = raw_text.replace('\n', ' ')[:300]
                    logging.error(
                        '[Row %d] MISSING_ANSWER: Model response had no decision. Raw="%s"',
                        row_idx,
                        snippet,
                    )
                    resp = {
                        'decision': 'uncertain',
                        'reason_short': 'uncertain because the model gave no decision.',
                        'confidence': 0.0,
                    }

            # Normalize decision ONCE and accumulate stats ONCE
            d_norm = normalize_decision(resp.get('decision', ''))
            decisions[d_norm] += 1  # <-- only here; do not increment elsewhere

            conf = resp.get('confidence', 0.0)
            try:
                conf = float(conf)
            except Exception:
                conf = 0.0
            if 0.0 <= conf <= 1.0:
                conf_sum += conf
                conf_n += 1

            # Count reasons only for excludes/uncertain (include has empty reason)
            if d_norm in (
                'exclude_no_relevance',
                'exclude_low_relevance',
                'exclude_review',
                'uncertain',
            ):
                formatted_reason = enforce_reason_format(
                    d_norm, resp.get('reason_short', '')
                )
                reasons_counter[formatted_reason] += 1
            else:
                formatted_reason = ''

            # By database
            db = (row.get('database') or '').strip() or '(unknown)'
            by_db[db][d_norm] += 1

            # Write row with mapped columns
            mapped = decide_columns(d_norm, resp.get('reason_short', ''))
            # Ensure reason we counted matches what we write (for excludes/uncertain)
            if d_norm == 'include':
                mapped['reason'] = ''
            else:
                mapped['reason'] = enforce_reason_format(
                    d_norm, resp.get('reason_short', '')
                )

            row.update(mapped)
            row['truncated_title'] = 'yes' if title_trunc else 'no'
            row['abstract_chunks'] = str(len(parts))
            row['abstract_truncated'] = 'yes' if was_truncated else 'no'
            writer.writerow(row)

            processed += 1
            wrote += 1

            if processed % log_every == 0:
                elapsed = time.time() - t_start
                rate = processed / elapsed if elapsed > 0 else 0.0
                target = max_records or total_rows or 1
                pct = 100.0 * processed / target
                logging.info(
                    'Processed %d/%d (%.1f%%) | %.2f rows/s | elapsed %.1fs',
                    processed,
                    target,
                    pct,
                    rate,
                    elapsed,
                )

    t_end = time.time()
    logging.info(
        'Done. Processed: %d, Wrote: %d, Elapsed: %.2fs (%.2f rows/s)',
        processed,
        wrote,
        (t_end - t_start),
        (processed / (t_end - t_start) if (t_end - t_start) else 0.0),
    )

    # Write LLM report (use wrote as the “Rows”)
    _write_llm_report(
        llm_report_path,
        start_ts=t_start,
        end_ts=t_end,
        input_csv=input_csv,
        output_csv=output_csv,
        model=model,
        preset=preset,
        n_rows=wrote,
        decisions=decisions,
        conf_sum=conf_sum,
        conf_n=conf_n,
        engine_events=engine_events,
        input_quality=input_quality,
        reasons_counter=reasons_counter,
        by_db=by_db,
    )
    return processed, wrote, llm_report_path


# ----------------------------
# CLI
# ----------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Screen CSV with a local LLM via Ollama.')
    p.add_argument(
        'input_csv', help='Path to input CSV (must contain title/abstract columns).'
    )
    p.add_argument(
        'output_csv', help='Path to output CSV (will add columns: exclude, reason).'
    )
    p.add_argument('criteria_txt', help='Path to criteria text file.')

    # Preset & manual knobs
    p.add_argument(
        '--preset',
        choices=list(MODEL_PRESETS.keys()),
        default='qwen',
        help='Model preset to use. Choices: '
        + ', '.join(MODEL_PRESETS.keys())
        + ' (default: qwen)',
    )
    p.add_argument(
        '--model',
        default=None,
        help='Override model name (rarely needed if using --preset).',
    )
    p.add_argument(
        '--title-col', default='title', help="Column name for title (default: 'title')."
    )
    p.add_argument(
        '--abstract-col',
        default='abstract',
        help="Column name for abstract (default: 'abstract').",
    )
    p.add_argument(
        '--temperature',
        type=float,
        default=DEFAULT_TEMPERATURE,
        help='Sampling temperature (default: 0.2).',
    )
    p.add_argument(
        '--max-tokens',
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help='Max tokens to generate (default: 256).',
    )
    p.add_argument(
        '--num-ctx',
        type=int,
        default=DEFAULT_NUM_CTX,
        help='Model context window (default: 8192).',
    )
    p.add_argument(
        '--retry',
        type=int,
        default=DEFAULT_RETRY,
        help='Retry attempts on model error (default: 3).',
    )

    # testing / progress
    p.add_argument(
        '--max-records',
        type=int,
        default=int(ENV_MAX_RECORDS) if (ENV_MAX_RECORDS or '').isdigit() else None,
        help='Limit number of rows for quick testing (env: MAX_RECORDS).',
    )
    p.add_argument(
        '--log-every',
        type=int,
        default=DEFAULT_LOG_EVERY,
        help=f'Log progress every N rows (env LOG_EVERY, default: {DEFAULT_LOG_EVERY}).',
    )
    p.add_argument(
        '--log-file',
        help='Optional path to log file (all messages will also be saved).',
    )
    p.add_argument('--llm-report', help='Optional path to write the LLM TXT report.')

    p.add_argument('--verbose', action='store_true', help='Verbose logging.')
    return p


def main() -> None:
    args = _build_parser().parse_args()

    # Resolve effective model params from preset
    effective_model = args.model or MODEL_PRESETS[args.preset]['model']
    effective_temp = (
        args.temperature
        if args.temperature != DEFAULT_TEMPERATURE
        else MODEL_PRESETS[args.preset]['temperature']
    )
    effective_max_tokens = (
        args.max_tokens
        if args.max_tokens != DEFAULT_MAX_TOKENS
        else MODEL_PRESETS[args.preset]['max_tokens']
    )
    effective_num_ctx = (
        args.num_ctx
        if args.num_ctx != DEFAULT_NUM_CTX
        else MODEL_PRESETS[args.preset]['num_ctx']
    )

    # Handlers: console + optional file
    handlers: List[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if args.log_file:
        Path(args.log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(args.log_file, encoding='utf-8'))

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=handlers,
    )

    try:
        in_csv = Path(args.input_csv)
        out_csv = Path(args.output_csv)
        criteria = Path(args.criteria_txt)

        if not in_csv.is_file():
            raise FileNotFoundError(in_csv)
        if not criteria.is_file():
            raise FileNotFoundError(criteria)

        logging.info(
            'Resolved model: %s (preset=%s) | Temp: %.1f | MaxTokens: %d | num_ctx: %d | Retry: %d',
            effective_model,
            args.preset,
            effective_temp,
            effective_max_tokens,
            effective_num_ctx,
            args.retry,
        )
        logging.info('Input: %s → Output: %s', in_csv, out_csv)
        logging.info('Criteria: %s', criteria)
        if args.max_records:
            logging.info('Test mode: limiting to %d records', args.max_records)
        if args.log_file:
            logging.info('Logging to file: %s', args.log_file)

        # Optional warm-up (ignore errors).
        try:
            _ = call_ollama(
                effective_model,
                max(effective_temp, 0.2),
                64,
                SYSTEM_MSG,
                'OK?',
                num_ctx=effective_num_ctx,
            )
        except Exception as e:
            logging.warning('Warmup failed (continuing anyway): %s', e)

        processed, wrote, report_path = screen_csv_with_ollama(
            input_csv=in_csv,
            output_csv=out_csv,
            criteria_txt=criteria,
            model=effective_model,
            title_col=args.title_col,
            abstract_col=args.abstract_col,
            temperature=effective_temp,
            max_tokens=effective_max_tokens,
            num_ctx=effective_num_ctx,
            retry=args.retry,
            max_records=args.max_records,
            log_every=args.log_every,
            preset=args.preset,
            llm_report_path=(Path(args.llm_report) if args.llm_report else None),
        )
        logging.info('LLM report → %s', report_path)

    except KeyboardInterrupt:
        logging.warning(
            'Interrupted by user (Ctrl+C). Partial output may exist at the target path.'
        )
        sys.exit(130)
    except Exception as e:
        logging.error('Error: %s', e)
        sys.exit(1)


if __name__ == '__main__':
    main()
