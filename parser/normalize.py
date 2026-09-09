"""RawRow -> canonical panel row (dict with the 21 columns). NULL = None. Never derives anything."""
import re

COLUMNS = ["snapshot", "source_file", "source_sha256", "page", "sl_no", "project_code", "legacy_ocms_code", "pmgid",
           "project_name", "agency_raw", "table_section", "state", "approval_month", "start_month", "doc_original",
           "doc_revised", "cost_original_cr", "cost_revised_cr", "expenditure_cum_cr", "physical_progress_pct", "parse_flags"]
PAREN = re.compile(r"\(([^()]*)\)")
CODE6 = re.compile(r"^\d{6}$")
MONTH = re.compile(r"(\d{1,2})\s*/\s*(\d{4})")
# The report itself prints 01/1900 in the date columns for some rows: the source
# spreadsheet's zero date, not a month anyone typed. Read as a date it is ~1500 months
# in the past, so it is normalised to NULL and flagged instead.
EPOCH_YEAR = "1900"
NUMBER = re.compile(r"\d[\d,]*\.?\d*")
# The report prints a literal "-" (and "NA" in the approval column) where a value is not available.
MISSING = {"", "-", "--", "NA", "N/A"}


def _ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def _present(p):
    return p not in MISSING


def split_name(cell):
    """The name cell prints  <name> (Agency) (Project Code) (Legacy OCMS Code) (PMGID).

    Read by position, anchored on the 6-digit project code. Classifying the parentheticals by
    shape does not work on the real report: legacy OCMS codes appear both as "N06000290" (1170
    April rows) and as bare digits "060100093" (14 rows), and a missing code is printed "-",
    which any id-shaped regex would happily accept as a value.

    # SPEC?: a parenthetical group beyond the four documented positions (agency, code, legacy,
    # pmgid) has no field of its own to go into. `parse_flags` is a closed enum
    # (contracts/enums.json; tools/validate.py fails on any value not listed there) and this
    # shape never occurs in April 2026 (fires zero times), so rather than inventing a flag for
    # a trap Task 5 would have to special-case, surplus parentheticals are folded into
    # agency_raw -- the reading stays lossless without touching the contract.
    """
    text = cell or ""
    parens = [_ws(p) for p in PAREN.findall(text)]
    out = {"project_name": _ws(text.split("(", 1)[0]), "agency_raw": None, "project_code": None,
           "legacy_ocms_code": None, "pmgid": None, "flags": []}
    idx = next((i for i, p in enumerate(parens) if CODE6.match(p)), None)
    if idx is None:
        agency, after, extra = (parens[0] if parens else None), [], (parens[1:] if parens else [])
    else:
        out["project_code"] = parens[idx]
        agency = parens[idx - 1] if idx > 0 else None
        after = parens[idx + 1:]
        extra = (parens[:idx - 1] if idx > 1 else []) + after[2:]
        after = after[:2]
    agency_parts = [p for p in ([agency] + extra) if p is not None and _present(p)]
    if agency_parts:
        out["agency_raw"] = " ".join(agency_parts)
    if len(after) > 0 and _present(after[0]):
        out["legacy_ocms_code"] = after[0]
    if len(after) > 1 and _present(after[1]):
        out["pmgid"] = after[1]
    for key, flag in [("project_code", "NO_PROJECT_CODE"), ("legacy_ocms_code", "NO_LEGACY_CODE"), ("pmgid", "NO_PMGID")]:
        if out[key] is None:
            out["flags"].append(flag)
    return out


def _ym(m):
    mm, yyyy = int(m.group(1)), m.group(2)
    return f"{yyyy}-{mm:02d}" if 1 <= mm <= 12 else None


def parse_dates(cell):
    """Returns (first_token, first_parenthesised_token, flags). Tokens are MM/YYYY -> YYYY-MM.

    A token printed in EPOCH_YEAR is the source system's zero date, not a real month; it is
    returned as NULL and flagged EPOCH_DATE. DATE_PARSE_FAIL still means only that no
    unparenthesised month could be read at all, so the two stay distinguishable.
    """
    text = cell or ""
    first = paren = None
    for m in MONTH.finditer(text):
        before = text[:m.start()]
        inside = before.count("(") > before.count(")")
        v = _ym(m)
        if inside and paren is None:
            paren = v
        elif not inside and first is None:
            first = v
    flags = [] if first is not None else ["DATE_PARSE_FAIL"]
    epoch = [v for v in (first, paren) if v is not None and v.startswith(EPOCH_YEAR)]
    if first is not None and first.startswith(EPOCH_YEAR):
        first = None
    if paren is not None and paren.startswith(EPOCH_YEAR):
        paren = None
    if epoch:
        flags.append("EPOCH_DATE")
    return first, paren, flags


def parse_numbers(cell):
    return [float(t.replace(",", "")) for t in NUMBER.findall(cell or "") if t not in (".",)]


def normalize(raw, snapshot, source_file, sha):
    c = raw.cells + [""] * (8 - len(raw.cells))
    flags = []
    ident = split_name(c[1])
    flags += ident.pop("flags")
    state_raw = c[2] or ""
    if "\n" in state_raw.strip():
        flags.append("MULTILINE_STATE")
    approval, start, f1 = parse_dates(c[3])
    doc_o, doc_r, f2 = parse_dates(c[4])
    flags += f1 + f2
    costs = parse_numbers(c[5])
    exp = parse_numbers(c[6])
    prog = parse_numbers(c[7])
    if not costs or not exp or not prog:
        flags.append("NUM_PARSE_FAIL")
    if raw.spans_page:
        flags.append("ROW_SPANS_PAGE")
    row = {
        "snapshot": snapshot, "source_file": source_file, "source_sha256": sha, "page": raw.page, "sl_no": int(c[0]),
        "project_code": ident["project_code"], "legacy_ocms_code": ident["legacy_ocms_code"], "pmgid": ident["pmgid"],
        "project_name": ident["project_name"] or "(unnamed)", "agency_raw": ident["agency_raw"],
        "table_section": _ws(raw.section) if raw.section else None, "state": _ws(state_raw) or None,
        "approval_month": approval, "start_month": start, "doc_original": doc_o, "doc_revised": doc_r,
        "cost_original_cr": costs[0] if costs else None, "cost_revised_cr": costs[1] if len(costs) > 1 else None,
        "expenditure_cum_cr": exp[0] if exp else None, "physical_progress_pct": prog[0] if prog else None,
        "parse_flags": ";".join(dict.fromkeys(flags)),
    }
    assert list(row) == COLUMNS
    return row
