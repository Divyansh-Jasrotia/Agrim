"""Turn Table 6 pages into RawRow records. Uses pdfplumber's ruling-line strategy; merges wrapped/continuation rows."""
import re
from dataclasses import dataclass, field

import pdfplumber

TABLE_SETTINGS = {"vertical_strategy": "lines", "horizontal_strategy": "lines", "snap_tolerance": 3,
                  "join_tolerance": 3, "intersection_tolerance": 3}
HEADER_FIRST = re.compile(r"^\s*Sl\.?\s*No", re.I)
SERIAL = re.compile(r"^\s*\d+\s*$")
# The report closes every sector block with a "Total (N)" subtotal row. Its cells[0] is empty,
# so without this it would be merged into the last project row and inflate that row's cost and
# expenditure. Verified: April 2026 prints 31 such rows, always as (col1, col5, col6). The
# captured N is the block's declared project count -- see merge_tables(totals=...) below.
TOTAL = re.compile(r"^\s*Total\s*\(\s*(\d+)\s*\)\s*$", re.I)
NCOLS = 8


@dataclass
class RawRow:
    page: int
    cells: list = field(default_factory=list)
    section: str = None
    spans_page: bool = False


def _clean(c):
    return (c or "").replace("\r", "").strip()


def merge_tables(pages_tables, totals=None):
    """pages_tables: iterable of (page_no, [table, ...]) where table = list of rows (lists of cell strings).

    A row with a single non-empty cell is ambiguous in this report: it is either a ministry/sector
    heading or the wrapped tail of the project row above it. They are told apart by whether a project
    row is still open -- `current` is cleared by the repeated column header and by a "Total (N)"
    subtotal, and in April 2026 all 48 heading rows follow one of those two (never a project row).

    Consequence worth stating plainly: because the repeated column header clears the open row,
    a row that genuinely spans a page break has its tail dropped silently whenever the next page
    opens (as every real April page does) with that header -- ROW_SPANS_PAGE is therefore
    unreachable on the real report; it only fires in a synthetic fixture with no repeated header
    (see tests/parser/test_extract.py). This function does not detect or recover the loss. The
    cross-check available instead is completeness by count: pass a list as `totals` and every
    skipped "Total (N)" subtotal row appends its declared N to it, so a caller (parser.run.report,
    via extract_rows_with_totals) can compare sum(totals) against the number of rows actually
    parsed and flag a mismatch.
    """
    rows, current, section = [], None, None
    for page_no, tables in pages_tables:
        for table in tables:
            for raw in table:
                cells = [_clean(c) for c in raw]
                if len(cells) < NCOLS:
                    cells = cells + [""] * (NCOLS - len(cells))
                cells = cells[:NCOLS]
                nonempty = [c for c in cells if c]
                if not nonempty:
                    continue
                if HEADER_FIRST.match(cells[0]):
                    current = None
                    continue
                if SERIAL.match(cells[0]):
                    current = RawRow(page=page_no, cells=cells, section=section)
                    rows.append(current)
                    continue
                total_match = next((TOTAL.match(c) for c in cells if TOTAL.match(c)), None)
                if total_match:
                    if totals is not None:
                        totals.append(int(total_match.group(1)))
                    current = None
                    continue
                if len(nonempty) == 1 and current is None:
                    section = nonempty[0].replace("\n", " ")
                    continue
                if current is not None and not cells[0]:
                    for i, c in enumerate(cells):
                        if c:
                            current.cells[i] = (current.cells[i] + "\n" + c).strip("\n")
                    if page_no != current.page:
                        current.spans_page = True
    return rows


def _has_project_table(page):
    tables = page.extract_tables(TABLE_SETTINGS)
    for t in tables:
        for r in t:
            if r and len(r) >= NCOLS and SERIAL.match(_clean(r[0])):
                return True
    return False


def find_table_pages(pdf):
    """Auto-detect (start, end) 1-based page numbers of the ongoing-projects table. Adapters may override."""
    start = end = None
    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        if start is None and "Ongoing Projects" in text and _has_project_table(page):
            start = i
        if start is not None and _has_project_table(page):
            end = i
    if start is None:
        raise RuntimeError("could not find the ongoing-projects table; pass explicit pages in the adapter")
    return start, end


def _pages_tables(pdf_path, pages):
    with pdfplumber.open(pdf_path) as pdf:
        if pages is None:
            pages = find_table_pages(pdf)
        start, end = pages
        return [(n, pdf.pages[n - 1].extract_tables(TABLE_SETTINGS)) for n in range(start, end + 1)]


def extract_rows(pdf_path, pages=None):
    return merge_tables(_pages_tables(pdf_path, pages))


def extract_rows_with_totals(pdf_path, pages=None):
    """Same as extract_rows, but also returns the declared N of every skipped "Total (N)" row.

    Used by parser.run.report() as the completeness cross-check: a genuinely page-spanning row
    is dropped silently by merge_tables (see its docstring), so the parsed row count alone cannot
    prove nothing was lost -- comparing it against sum(declared totals) can.
    """
    totals = []
    rows = merge_tables(_pages_tables(pdf_path, pages), totals=totals)
    return rows, totals
