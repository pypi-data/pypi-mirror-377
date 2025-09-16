# src/endnote_utils/core.py
from __future__ import annotations

import csv
import json
import logging
import re
import time
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

# ----------------------------
# Public constants
# ----------------------------

DEFAULT_FIELDNAMES: List[str] = [
    'database',
    'ref_type',
    'title',
    'journal',
    'authors',
    'year',
    'volume',
    'number',
    'abstract',
    'doi',
    'urls',
    'keywords',
    'publisher',
    'isbn',
    'language',
    'extracted_date',
]

CSV_QUOTING_MAP = {
    'minimal': csv.QUOTE_MINIMAL,
    'all': csv.QUOTE_ALL,
    'nonnumeric': csv.QUOTE_NONNUMERIC,
    'none': csv.QUOTE_NONE,
}

# Report layout
DUPES_DETAILS_LIMIT = 50
STATS_LIST_LIMIT = 20


# ----------------------------
# FS helpers
# ----------------------------


def ensure_parent_dir(p: Path) -> None:
    """Create parent directory if it doesn't exist."""
    p.parent.mkdir(parents=True, exist_ok=True)


# ----------------------------
# Text helpers
# ----------------------------


def clean_text(text: Optional[str]) -> str:
    """
    Trim, collapse internal whitespace, remove stray CRs, keep punctuation intact.
    """
    if not text:
        return ''
    text = text.replace('\r', ' ')
    return ' '.join(text.split()).strip()


def safe_find_text(node: ET.Element, path: str) -> str:
    """Find text with XPath and return cleaned string."""
    elem = node.find(path)
    return clean_text(elem.text) if elem is not None and elem.text is not None else ''


def join_nonempty(items: Iterable[str], sep: str) -> str:
    return sep.join(x for x in (i.strip() for i in items) if x)


def normalize_text_for_key(s: str) -> str:
    """Lowercase + strip non-alnum + single-space. Good for stable keys."""
    if not s:
        return ''
    s = s.lower()
    s = ''.join(ch for ch in s if ch.isalnum() or ch.isspace())
    return ' '.join(s.split())


# ----------------------------
# Record extraction (XML)
# ----------------------------


def process_doi_xml(record: ET.Element) -> str:
    """Extract and format DOI information to a canonical URL if possible."""
    doi_raw = safe_find_text(record, './/electronic-resource-num/style')
    if not doi_raw:
        return ''
    if doi_raw.startswith('10.'):
        return f'https://doi.org/{doi_raw}'
    if doi_raw.startswith(('http://', 'https://')):
        return doi_raw
    return ''


def extract_authors_xml(record: ET.Element) -> str:
    """Collect authors from //author/style, joined by '; '."""
    authors: List[str] = []
    for author in record.findall('.//author'):
        style = author.find('style')
        if style is not None and style.text:
            authors.append(clean_text(style.text))
    return join_nonempty(authors, '; ')


def extract_urls_xml(record: ET.Element) -> str:
    """Collect related URLs from //urls/related-urls/url/style, joined by ' | '."""
    urls: List[str] = []
    for url in record.findall('.//urls/related-urls/url'):
        style = url.find('style')
        if style is not None and style.text:
            urls.append(clean_text(style.text))
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            deduped.append(u)
    return join_nonempty(deduped, ' | ')


def extract_keywords_xml(record: ET.Element) -> str:
    """Collect keywords from //keywords/keyword/style, joined by '; ' (deduped)."""
    items: List[str] = []
    for kw in record.findall('.//keywords/keyword'):
        style = kw.find('style')
        if style is not None and style.text:
            items.append(clean_text(style.text))
    seen = set()
    out: List[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return join_nonempty(out, '; ')


def process_record_xml(record: ET.Element, database: str) -> Dict[str, str]:
    """Transform a <record> element into a flat dictionary (XML source)."""
    ref_type_name = ''
    ref_type = record.find('ref-type')
    if ref_type is not None:
        ref_type_name = ref_type.get('name') or ''

    return {
        'database': database,
        'ref_type': clean_text(ref_type_name),
        'title': safe_find_text(record, './/title/style'),
        'journal': safe_find_text(record, './/secondary-title/style'),
        'authors': extract_authors_xml(record),
        'year': safe_find_text(record, './/year/style'),
        'volume': safe_find_text(record, './/volume/style'),
        'number': safe_find_text(record, './/number/style'),
        'abstract': safe_find_text(record, './/abstract/style'),
        'doi': process_doi_xml(record),
        'urls': extract_urls_xml(record),
        'keywords': extract_keywords_xml(record),
        'publisher': safe_find_text(record, './/publisher/style'),
        'isbn': safe_find_text(record, './/isbn/style'),
        'language': safe_find_text(record, './/language/style'),
        'extracted_date': datetime.now().strftime('%Y-%m-%d'),
    }


# ----------------------------
# XML streaming + filters
# ----------------------------


def iter_records_xml(xml_path: Path) -> Iterable[ET.Element]:
    """Stream <record> elements with low memory footprint."""
    context = ET.iterparse(str(xml_path), events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag == 'record':
            yield elem
            elem.clear()
            root.clear()


# ----------------------------
# RIS parsing & mapping
# ----------------------------

_RIS_TAG_RE = re.compile(r'^([A-Z0-9]{2})  - (.*)$')


def _finish_ris_record(buf: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Map RIS buffer dict (tag -> list[str]) to our flat row.
    Common RIS tags:
      TY, AU, TI, T2/JO/JA, PY/Y1, VL, IS, AB, DO/DI, UR, KW, PB, SN, LA, N1
    """

    def first(tag_list: List[str]) -> str:
        return clean_text(tag_list[0]) if tag_list else ''

    def all_join(tag_list: List[str], sep: str) -> str:
        return join_nonempty(tag_list, sep)

    # Authors
    authors = all_join([clean_text(x) for x in buf.get('AU', [])], '; ')

    # Title
    title = first([clean_text(x) for x in buf.get('TI', [])])

    # Journal
    journal = first([*buf.get('T2', []), *buf.get('JO', []), *buf.get('JA', [])])

    # Year: PY or Y1; try to extract 4-digit year from possible full date
    year_raw = first([*buf.get('PY', []), *buf.get('Y1', [])])
    m = re.search(r'\b(\d{4})\b', year_raw) if year_raw else None
    year = m.group(1) if m else year_raw

    volume = first(buf.get('VL', []))
    number = first(buf.get('IS', []))
    abstract = first(buf.get('AB', []))

    # DOI: DO or DI
    doi_raw = first([*buf.get('DO', []), *buf.get('DI', [])])
    doi = ''
    if doi_raw:
        doi_raw = clean_text(doi_raw)
        if doi_raw.startswith('10.'):
            doi = f'https://doi.org/{doi_raw}'
        elif doi_raw.startswith(('http://', 'https://')):
            doi = doi_raw

    # URLs
    urls = join_nonempty([clean_text(x) for x in buf.get('UR', [])], ' | ')

    # Keywords
    keywords = join_nonempty([clean_text(x) for x in buf.get('KW', [])], '; ')

    publisher = first(buf.get('PB', []))
    # SN can be ISSN or ISBN depending on type; map to 'isbn' for compatibility with your schema
    isbn = first(buf.get('SN', []))
    language = first(buf.get('LA', []))

    # Notes for retraction heuristic (not exported but used internally)
    notes = first(buf.get('N1', []))

    row = {
        'ref_type': first(buf.get('TY', [])),
        'title': title,
        'journal': journal,
        'authors': authors,
        'year': year,
        'volume': volume,
        'number': number,
        'abstract': abstract,
        'doi': doi,
        'urls': urls,
        'keywords': keywords,
        'publisher': publisher,
        'isbn': isbn,
        'language': language,
        # internal
        '_notes': notes,
    }
    return row


def iter_records_ris(ris_path: Path) -> Iterable[Dict[str, str]]:
    """
    Stream RIS records as flat dicts (without database/extracted_date),
    yielding at every ER  - line.
    """
    buf: Dict[str, List[str]] = {}
    with open(ris_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue
            if line.startswith('ER  -'):
                # finalize
                if buf:
                    yield _finish_ris_record(buf)
                    buf = {}
                continue
            m = _RIS_TAG_RE.match(line)
            if not m:
                # continuation line? append to last tag if present
                if buf:
                    # append to the last key if exists
                    last_key = next(reversed(buf)) if buf else None
                    if last_key:
                        buf[last_key][-1] = clean_text(
                            buf[last_key][-1] + ' ' + line.strip()
                        )
                continue
            tag, val = m.group(1), m.group(2)
            buf.setdefault(tag, []).append(clean_text(val))
    # handle last record if file does not end with ER
    if buf:
        yield _finish_ris_record(buf)


# ----------------------------
# Filters & helpers
# ----------------------------


def record_matches_filters(
    row: Dict[str, str], ref_type: Optional[str], year: Optional[str]
) -> bool:
    if ref_type and row.get('ref_type') != ref_type:
        return False
    if year and row.get('year') != str(year):
        return False
    return True


def is_retraction_text(*texts: str) -> bool:
    """
    Heuristic: mark as 'retraction' if any text contains key substrings.
    """
    blob = ' '.join(t or '' for t in texts).lower()
    indicators = ('retraction', 'retracted', 'withdrawn', 'erratum')
    return any(tok in blob for tok in indicators)


# ----------------------------
# Deduplication helpers
# ----------------------------


def dedupe_key(row: Dict[str, str], mode: str) -> Optional[str]:
    """
    mode: 'none' | 'doi' | 'title-year'
    Returns None when no applicable key can be formed (row passes through).
    """
    if mode == 'doi':
        k = (row.get('doi') or '').strip()
        return k or None
    if mode == 'title-year':
        title = normalize_text_for_key(row.get('title', ''))
        year = (row.get('year') or '').strip()
        if title and year:
            return f'{title}::{year}'
        return None
    return None


# ----------------------------
# Writers (CSV / JSON / XLSX)
# ----------------------------


def _write_rows_csv(
    rows_iter: Iterable[Dict[str, str]],
    out_path: Path,
    fieldnames: List[str],
    delimiter: str,
    quoting: str,
    include_header: bool,
    encoding: str,
) -> int:
    qmode = CSV_QUOTING_MAP[quoting.lower()]
    ensure_parent_dir(out_path)
    count = 0
    with open(out_path, 'w', newline='', encoding=encoding) as f:
        writer = csv.DictWriter(
            f, fieldnames=fieldnames, delimiter=delimiter, quoting=qmode
        )
        if include_header:
            writer.writeheader()
        for row in rows_iter:
            writer.writerow({k: row.get(k, '') for k in fieldnames})
            count += 1
    return count


def _write_rows_json(
    rows_iter: Iterable[Dict[str, str]],
    out_path: Path,
    fieldnames: List[str],
    encoding: str,
) -> int:
    """Write a JSON array streaming without holding all rows in memory."""
    ensure_parent_dir(out_path)
    count = 0
    with open(out_path, 'w', encoding=encoding) as f:
        f.write('[')
        first = True
        for row in rows_iter:
            obj = {k: row.get(k, '') for k in fieldnames}
            if first:
                first = False
            else:
                f.write(',')
            f.write(json.dumps(obj, ensure_ascii=False))
            count += 1
        f.write(']')
    return count


def _write_rows_xlsx(
    rows_iter: Iterable[Dict[str, str]],
    out_path: Path,
    fieldnames: List[str],
) -> int:
    """Write an Excel file using openpyxl (installed via project dependencies)."""
    try:
        from openpyxl import Workbook
    except ImportError as e:
        raise RuntimeError(
            "Excel output requires 'openpyxl'. Ensure it is installed."
        ) from e

    ensure_parent_dir(out_path)
    wb = Workbook()
    ws = wb.active
    ws.title = 'records'
    ws.append(fieldnames)  # header

    count = 0
    for row in rows_iter:
        ws.append([row.get(k, '') for k in fieldnames])
        count += 1

    wb.save(out_path)
    return count


# ----------------------------
# Generic export + report (+ dedupe + stats, pretty report + duplicates table)
# ----------------------------


def export_files_with_report(
    inputs: List[Path],
    out_path: Path,
    out_format: str,  # "csv" | "json" | "xlsx"
    *,
    fieldnames: List[str] = None,
    delimiter: str = ',',
    quoting: str = 'minimal',
    include_header: bool = True,
    encoding: str = 'utf-8',
    ref_type: Optional[str] = None,
    year: Optional[str] = None,
    max_records_per_file: Optional[int] = None,
    report_path: Optional[Path] = None,
    # Dedup + stats
    dedupe: str = 'none',
    dedupe_keep: str = 'first',
    stats: bool = False,
    stats_json: Optional[Path] = None,
    top_authors: int = 10,
) -> Tuple[int, Path, Optional[Path]]:
    """
    Stream records from one or many EndNote XML / RIS files and write to CSV/JSON/XLSX.
    Writes a pretty TXT report unless report_path is None.

    Deduplication:
      - dedupe='doi'        → unique by DOI
      - dedupe='title-year' → unique by normalized (title, year)
      - dedupe_keep='first' or 'last' (applies within each input file)

    Stats (when stats=True) add counts by year/ref_type/journal and top authors.
    stats_json (if provided) writes a JSON snapshot of these stats + duplicates.

    The report includes a per-database table: Origin / Retractions / Duplicates / Remaining.

    Returns (total_rows_written, out_path, report_path or None if disabled).
    """
    fieldnames = fieldnames or DEFAULT_FIELDNAMES
    out_format = out_format.lower()
    if out_format not in {'csv', 'json', 'xlsx'}:
        raise ValueError(f'Unknown out_format: {out_format}')

    # Per-run accumulators
    per_file_lines: List[str] = []

    year_counter = Counter()
    type_counter = Counter()
    journal_counter = Counter()
    author_counter = Counter()

    # Dedupe state
    seen_keys: set[str] = set()
    duplicates_counter = Counter()  # global key -> duplicate count

    # Per-database accounting table
    per_db: Dict[
        str, Dict[str, int]
    ] = {}  # db -> {origin,retractions,duplicates,remaining}

    def rows() -> Iterable[Dict[str, str]]:
        nonlocal per_file_lines, seen_keys, duplicates_counter, per_db
        nonlocal year_counter, type_counter, journal_counter, author_counter

        for in_path in inputs:
            database = in_path.stem
            per_db.setdefault(
                database,
                {'origin': 0, 'retractions': 0, 'duplicates': 0, 'remaining': 0},
            )

            logging.info('Processing %s (database=%s)', in_path.name, database)

            produced = 0
            skipped = 0

            buffered: List[Dict[str, str]] = []
            buffered_keys_index: Dict[str, int] = {}

            is_xml = in_path.suffix.lower() == '.xml'
            # iterator depending on type
            if is_xml:
                iterator = iter_records_xml(in_path)
            else:
                iterator = iter_records_ris(in_path)

            for rec in iterator:
                try:
                    if is_xml:
                        row = process_record_xml(rec, database=database)
                        # retraction heuristic using XML fields
                        retraction_hit = is_retraction_text(
                            safe_find_text(rec, './/notes/style'),
                            row.get('title', ''),
                        )
                    else:
                        # rec already a row-ish dict from RIS
                        base = rec
                        row = {
                            'database': database,
                            'ref_type': clean_text(base.get('ref_type', '')),
                            'title': base.get('title', ''),
                            'journal': base.get('journal', ''),
                            'authors': base.get('authors', ''),
                            'year': base.get('year', ''),
                            'volume': base.get('volume', ''),
                            'number': base.get('number', ''),
                            'abstract': base.get('abstract', ''),
                            'doi': base.get('doi', ''),
                            'urls': base.get('urls', ''),
                            'keywords': base.get('keywords', ''),
                            'publisher': base.get('publisher', ''),
                            'isbn': base.get('isbn', ''),
                            'language': base.get('language', ''),
                            'extracted_date': datetime.now().strftime('%Y-%m-%d'),
                        }
                        retraction_hit = is_retraction_text(
                            base.get('_notes', ''), row.get('title', '')
                        )

                    # Filters
                    if not record_matches_filters(row, ref_type, year):
                        continue

                    # Origin++ (after filter, before dedupe)
                    per_db[database]['origin'] += 1
                    # Retractions++
                    if retraction_hit:
                        per_db[database]['retractions'] += 1

                    # Dedup
                    k = dedupe_key(row, dedupe)
                    if k and dedupe != 'none':
                        if dedupe_keep == 'first':
                            if k in seen_keys:
                                duplicates_counter[k] += 1
                                per_db[database]['duplicates'] += 1
                                continue
                            seen_keys.add(k)
                            buffered.append(row)
                            produced += 1
                        else:  # keep last within this file
                            if k in buffered_keys_index:
                                prev_idx = buffered_keys_index[k]
                                buffered[prev_idx] = row
                                duplicates_counter[k] += 1
                                per_db[database]['duplicates'] += 1
                            else:
                                buffered_keys_index[k] = len(buffered)
                                buffered.append(row)
                                produced += 1
                            seen_keys.add(k)
                    else:
                        buffered.append(row)
                        produced += 1

                    if max_records_per_file and produced >= max_records_per_file:
                        break

                except Exception:
                    skipped += 1
                    logging.debug('Record error in %s', in_path, exc_info=True)

            # Remaining = exported from this file
            per_db[database]['remaining'] += len(buffered)

            per_file_lines.append(
                f'{in_path.name:<15} : {len(buffered)} exported, {skipped} skipped'
            )

            # Stats
            if stats:
                for r in buffered:
                    y = (r.get('year') or '').strip()
                    t = (r.get('ref_type') or '').strip()
                    j = (r.get('journal') or '').strip()
                    if y:
                        year_counter[y] += 1
                    if t:
                        type_counter[t] += 1
                    if j:
                        journal_counter[j] += 1
                    if r.get('authors'):
                        for a in (x.strip() for x in r['authors'].split(';')):
                            if a:
                                author_counter[a] += 1

            # Yield to writer
            for r in buffered:
                yield r

    # Select writer
    start_ts = time.time()
    run_start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if out_format == 'csv':
        total = _write_rows_csv(
            rows(), out_path, fieldnames, delimiter, quoting, include_header, encoding
        )
    elif out_format == 'json':
        total = _write_rows_json(rows(), out_path, fieldnames, encoding)
    else:  # xlsx
        total = _write_rows_xlsx(rows(), out_path, fieldnames)

    duration = time.time() - start_ts

    # ---------- Pretty report builder ----------
    def _header_line(title: str) -> List[str]:
        bar = '=' * 40
        return [bar, title, bar]

    def _section_line(title: str) -> List[str]:
        return ['', title, '-' * 40]

    report_lines: List[str] = []
    report_lines += _header_line('EndNote Export Report')
    report_lines += [
        f'Run started : {run_start}',
        f'Files       : {len(inputs)}',
        f'Duration    : {duration:.2f} seconds',
    ]

    # Per-file section
    report_lines += _section_line('Per-file results')
    report_lines += per_file_lines
    report_lines.append(f'TOTAL exported: {total}')

    # Per-database duplicates table
    if per_db:
        report_lines += _section_line('Duplicates table (by database)')
        # compute column widths
        db_names = list(per_db.keys())
        db_col_w = max([len('Database')] + [len(db) for db in db_names])

        # totals
        tot_origin = sum(d['origin'] for d in per_db.values())
        tot_retract = sum(d['retractions'] for d in per_db.values())
        tot_dupes = sum(d['duplicates'] for d in per_db.values())
        tot_remain = sum(d['remaining'] for d in per_db.values())

        header = f'{"Database":<{db_col_w}}  {"Origin":>8}  {"Retractions":>12}  {"Duplicates":>10}  {"Remaining":>10}'
        report_lines.append(header)
        report_lines.append('-' * len(header))

        for db in sorted(per_db.keys()):
            d = per_db[db]
            line = (
                f'{db:<{db_col_w}}  '
                f'{d["origin"]:>8}  '
                f'{d["retractions"]:>12}  '
                f'{d["duplicates"]:>10}  '
                f'{d["remaining"]:>10}'
            )
            report_lines.append(line)

        total_line = (
            f'{"TOTAL":<{db_col_w}}  '
            f'{tot_origin:>8}  '
            f'{tot_retract:>12}  '
            f'{tot_dupes:>10}  '
            f'{tot_remain:>10}'
        )
        report_lines.append(total_line)

    # Duplicates key summary (top)
    if dedupe != 'none':
        report_lines += _section_line('Duplicate keys (top)')
        total_dupes_global = sum(duplicates_counter.values())
        report_lines.append(f'Mode   : {dedupe}')
        report_lines.append(f'Keep   : {dedupe_keep}')
        report_lines.append(f'Removed: {total_dupes_global}')
        if total_dupes_global > 0:
            report_lines.append('Details (top):')
            for k, c in duplicates_counter.most_common(DUPES_DETAILS_LIMIT):
                report_lines.append(f'  {k} : {c} duplicate(s)')

    # Summary stats
    if stats:

        def head(counter: Counter, n: int = 10):
            return [(k, c) for k, c in counter.most_common(n) if k]

        report_lines += _section_line('Summary stats')
        # Year
        report_lines.append('By year:')
        for y in sorted(year_counter.keys()):
            report_lines.append(f'  {y:>6} : {year_counter[y]}')
        # Ref type
        report_lines.append('')
        report_lines.append('By ref_type (top):')
        for k, c in head(type_counter, STATS_LIST_LIMIT):
            report_lines.append(f'  {k}: {c}')
        # Journal
        report_lines.append('')
        report_lines.append(f'By journal (top {STATS_LIST_LIMIT}):')
        for k, c in head(journal_counter, STATS_LIST_LIMIT):
            report_lines.append(f'  {k}: {c}')
        # Authors
        report_lines.append('')
        report_lines.append(f'Top authors (top {top_authors}):')
        for k, c in head(author_counter, top_authors):
            report_lines.append(f'  {k}: {c}')

        # Optional JSON dump
        if stats_json:
            ensure_parent_dir(stats_json)
            with open(stats_json, 'w', encoding='utf-8') as jf:
                json.dump(
                    {
                        'totals': {
                            'exported': total,
                            'files_processed': len(inputs),
                            'duration_seconds': duration,
                        },
                        'by_year': dict(year_counter),
                        'by_ref_type': dict(type_counter),
                        'by_journal': dict(journal_counter),
                        'top_authors': author_counter.most_common(top_authors),
                        'duplicates': {
                            'mode': dedupe,
                            'keep': dedupe_keep,
                            'removed': sum(duplicates_counter.values())
                            if dedupe != 'none'
                            else 0,
                            'top': duplicates_counter.most_common(DUPES_DETAILS_LIMIT)
                            if dedupe != 'none'
                            else [],
                            'by_database': per_db,
                        },
                    },
                    jf,
                    ensure_ascii=False,
                    indent=2,
                )

    # Write report unless disabled
    final_report_path: Optional[Path] = report_path
    if final_report_path is not None:
        final_report_path = final_report_path or out_path.with_name(
            out_path.stem + '_report.txt'
        )
        ensure_parent_dir(final_report_path)
        with open(final_report_path, 'w', encoding='utf-8') as rf:
            rf.write('\n'.join(report_lines))

    return total, out_path, final_report_path


# ----------------------------
# Back-compat convenience wrappers (CSV only)
# ----------------------------


def export_files_to_csv_with_report(
    inputs: List[Path],
    csv_path: Path,
    report_path: Optional[Path] = None,
    *,
    fieldnames: List[str] = None,
    delimiter: str = ',',
    quoting: str = 'minimal',
    include_header: bool = True,
    encoding: str = 'utf-8',
    ref_type: Optional[str] = None,
    year: Optional[str] = None,
    max_records_per_file: Optional[int] = None,
) -> Tuple[int, Path, Optional[Path]]:
    """Legacy API: export to CSV + TXT report (or no report if report_path=None)."""
    return export_files_with_report(
        inputs=inputs,
        out_path=csv_path,
        out_format='csv',
        fieldnames=fieldnames,
        delimiter=delimiter,
        quoting=quoting,
        include_header=include_header,
        encoding=encoding,
        ref_type=ref_type,
        year=year,
        max_records_per_file=max_records_per_file,
        report_path=report_path,
    )


def export(
    xml_file: Path, csv_path: Path, **kwargs
) -> Tuple[int, Path, Optional[Path]]:
    """Convenience: single XML file to CSV (+report unless disabled)."""
    return export_files_to_csv_with_report([xml_file], csv_path, **kwargs)


def export_folder(
    folder: Path, csv_path: Path, **kwargs
) -> Tuple[int, Path, Optional[Path]]:
    """Convenience: all *.xml in folder to CSV (+report unless disabled)."""
    inputs = sorted(
        p for pat in ('*.xml', '*.ris') for p in Path(folder).glob(pat) if p.is_file()
    )
    if not inputs:
        raise FileNotFoundError(f'No *.xml or *.ris found in {folder}')
    return export_files_to_csv_with_report(inputs, csv_path, **kwargs)
