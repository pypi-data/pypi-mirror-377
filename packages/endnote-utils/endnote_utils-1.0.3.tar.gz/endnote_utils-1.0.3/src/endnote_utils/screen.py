#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
endnote_utils.screen

Screen papers (title + abstract) using a local LLM via Ollama.

- NO JSON requirement. Model replies in a 3-line template parsed via regex.
- Also accepts ONE-LINE format with optional labels:
    <decision> | <reason> | <confidence>
    <decision> | Reason: <reason> | Confidence: <confidence>
    Decision: <decision> | Reason: <reason> | Confidence: <confidence>
- Confidence is optional in one-liner; defaults to 0.0 if absent.
- Abstract is CHUNKED (not truncated) into multiple parts for the prompt.
- On EMPTY_RESPONSE only, do a one-shot fallback with a softer title-only prompt.
- Logging with progress, ETA, retries
- --log-file writes a full log to disk (with timestamps)
- --preset lets you pick tuned settings for qwen / mistral quickly.

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
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ----------------------------
# Defaults / env
# ----------------------------
ENV_MAX_RECORDS = os.getenv('MAX_RECORDS')
ENV_LOG_EVERY = os.getenv('LOG_EVERY')  # log progress every N rows

DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 256
DEFAULT_NUM_CTX = 8192
DEFAULT_RETRY = 3
DEFAULT_LOG_EVERY = int(ENV_LOG_EVERY) if (ENV_LOG_EVERY or '').isdigit() else 25

# --- Model presets (only qwen / mistral) ---
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

# Title truncation (keep this tiny for stability)
TITLE_MAX_CHARS = 300

# Abstract chunking (lighter context)
ABSTRACT_CHUNK_CHARS = 1200  # target size per chunk
ABSTRACT_MAX_CHUNKS = 2  # hard cap; if exceeded -> abstract_truncated=yes

SYSTEM_MSG = """You are an expert reviewer screening AI/XAI papers in healthcare neurology.
Decide INCLUDE / EXCLUDE strictly by the given criteria, or mark as UNCERTAIN.
Reply concisely following the requested template. No extra commentary."""

# ----------------------------
# Helpers (public for reuse)
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
    """
    Make the model output easier to parse:
    - strip Markdown bold/inline code markers
    - collapse bullets like '- Decision:'
    - trim trailing spaces per line
    """
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

Alternatively, it's OK to reply in ONE line (no labels):
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

Alternatively, it's OK to reply in ONE line (no labels):
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
    """
    Call Ollama REST API and return raw 'response' text.
    Raises RuntimeError('EMPTY_RESPONSE') when response is empty.
    """
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


# ---- Output parsing (3-line or 1-line) ----

_DECISION_RE = re.compile(r'^\s*Decision\s*:\s*(.+?)\s*$', re.I | re.M)
_REASON_RE = re.compile(r'^\s*Reason\s*:\s*(.+?)\s*$', re.I | re.M)
_CONF_RE = re.compile(r'^\s*Confidence\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*$', re.I | re.M)

# Tolerant one-liner:
# - optional leading "Decision:"
# - optional "Reason:" label before reason
# - optional "| Confidence: <num>" part (confidence may be missing)
_PIPE_RE = re.compile(
    r'^\s*'
    r'(?:decision\s*:\s*)?'
    r'(include|exclude_no_relevance|exclude_low_relevance|exclude_review|uncertain)'
    r'\s*\|\s*'
    r'(?:reason\s*:\s*)?'
    r'(.+?)'
    r'(?:\s*\|\s*(?:confidence\s*:\s*)?([0-9]+(?:\.[0-9]+)?))?'
    r'\s*$',
    re.I | re.M,
)


def parse_model_output(text: str) -> Dict[str, Any]:
    s = _normalize_response_text(text or '')

    # 1) Try strict 3-line parse
    m_dec = _DECISION_RE.search(s)
    m_rea = _REASON_RE.search(s)
    m_conf = _CONF_RE.search(s)

    decision = (m_dec.group(1) if m_dec else '').strip().lower()
    reason = (m_rea.group(1) if m_rea else '').strip()
    conf_s = (m_conf.group(1) if m_conf else '').strip()

    # 2) If no decision, try tolerant one-liner
    if not decision:
        m_pipe = _PIPE_RE.search(s)
        if m_pipe:
            decision = (m_pipe.group(1) or '').strip().lower()
            reason = (m_pipe.group(2) or '').strip()
            conf_s = (m_pipe.group(3) or '').strip()

            # Remove any leftover labels at the start just in case
            reason = re.sub(r'^\s*reason\s*:\s*', '', reason, flags=re.I).strip()
            if conf_s:
                conf_s = re.sub(
                    r'^\s*confidence\s*:\s*', '', conf_s, flags=re.I
                ).strip()

    # 3) Confidence normalization (0..1), default 0.0 if missing/invalid
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
# Core engine (callable API)
# ----------------------------


def screen_csv_with_ollama(
    input_csv: Path,
    output_csv: Path,
    criteria_txt: Path,
    *,
    model: str,
    title_col: str = 'title',
    abstract_col: str = 'abstract',
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    num_ctx: int = DEFAULT_NUM_CTX,
    retry: int = DEFAULT_RETRY,
    max_records: Optional[int] = None,
    log_every: int = DEFAULT_LOG_EVERY,
) -> Tuple[int, int]:
    """
    Screen a CSV and write a new CSV with added columns:
      exclude, reason, confidence, truncated_title, abstract_chunks, abstract_truncated
    Returns (processed_rows, wrote_rows).
    """
    total_rows = count_rows(input_csv)
    logging.info('Input rows (excluding header): %d', total_rows)
    if max_records:
        logging.info('Max records (test mode): %d', max_records)

    criteria = load_text(criteria_txt)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

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
            'confidence',
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

            raw_abstract = row.get(abstract_col, '')
            parts, was_truncated = _chunk_text(
                raw_abstract, ABSTRACT_CHUNK_CHARS, ABSTRACT_MAX_CHUNKS
            )

            prompt = build_prompt(criteria, title, parts)

            last_err: Optional[Exception] = None
            raw_text: Optional[str] = None
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
                            logging.info(
                                '[Row %d] Fallback (title-only) succeeded after EMPTY_RESPONSE.',
                                row_idx,
                            )
                            break
                        except Exception as ee:
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

            # If we got a response but couldn't parse decision, log snippet and coerce to uncertain
            if raw_text is not None and isinstance(resp, dict):
                parsed_decision = (resp.get('decision') or '').strip().lower()
                if not parsed_decision:
                    snippet = (raw_text or '').replace('\n', ' ')[:300]
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

            mapped = decide_columns(
                resp.get('decision', ''), resp.get('reason_short', '')
            )
            row.update(mapped)
            # keep confidence column (bounded 0..1)
            conf_val = resp.get('confidence', 0.0)
            try:
                conf_val = float(conf_val)
            except Exception:
                conf_val = 0.0
            row['confidence'] = f'{max(0.0, min(1.0, conf_val)):.3f}'

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

    elapsed = time.time() - t_start
    logging.info(
        'Done. Processed: %d, Wrote: %d, Elapsed: %.2fs (%.2f rows/s)',
        processed,
        wrote,
        elapsed,
        (processed / elapsed if elapsed else 0.0),
    )
    return processed, wrote


# ----------------------------
# CLI
# ----------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Screen CSV with a local LLM via Ollama.')
    p.add_argument(
        'input_csv', help='Path to input CSV (must contain title/abstract columns).'
    )
    p.add_argument(
        'output_csv',
        help='Path to output CSV (will add columns: exclude, reason, confidence).',
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
        help=f'Override model name (defaults come from --preset).',
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
    p.add_argument('--verbose', action='store_true', help='Verbose logging.')
    return p


def main() -> None:
    args = _build_parser().parse_args()

    # Resolve effective model params from preset (if provided)
    effective_model = None
    effective_temp = args.temperature
    effective_max_tokens = args.max_tokens
    effective_num_ctx = args.num_ctx

    if args.preset:
        cfg = MODEL_PRESETS[args.preset]
        effective_model = cfg.get('model')
        # Only override temp/tokens if user left them at defaults
        if args.temperature == DEFAULT_TEMPERATURE:
            effective_temp = cfg.get('temperature', effective_temp)
        if args.max_tokens == DEFAULT_MAX_TOKENS:
            effective_max_tokens = cfg.get('max_tokens', effective_max_tokens)
        if args.num_ctx == DEFAULT_NUM_CTX:
            effective_num_ctx = cfg.get('num_ctx', effective_num_ctx)

    # User override (rare)
    if args.model:
        effective_model = args.model

    if not effective_model:
        raise SystemExit(
            'No model resolved. Use --preset qwen|mistral or --model <tag>.'
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
            args.preset or '-',
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

        screen_csv_with_ollama(
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
        )
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
