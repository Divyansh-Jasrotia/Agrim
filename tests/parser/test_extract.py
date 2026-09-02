from parser.extract import merge_tables


def test_merge_tables_synthetic_page_span_when_next_page_has_no_repeated_header():
    """Synthetic case: page 2 here does NOT start with a repeated column header, so the
    continuation row on it merges into the still-open row from page 1 and spans_page fires.
    Every real April page DOES start with that header (see the test below), which clears the
    open row and drops the tail instead -- so this exact merge path never happens on the real
    report; it documents what the code does in the absence of a repeated header, not what
    ROW_SPANS_PAGE looks like in practice."""
    page1 = [
        ["Sl.No", "Project Name", "State", "Date of Approval", "DoC", "Cost", "Expenditure", "Progress"],
        ["Railways", "", "", "", "", "", "", ""],
        ["1", "Alpha Line (Railways) (100001)", "Bihar", "01/2020", "12/2026", "500\n520", "100", "20"],
        ["", "(N04000001) (PMG1)", "", "", "", "", "", ""],
    ]
    page2 = [
        ["", "continued name part", "", "", "", "", "", ""],
        ["2", "Beta Road (NHAI) (100002)", "Gujarat", "02/2021", "06/2027", "900\n950", "500", "60"],
    ]
    rows = merge_tables([(55, [page1]), (56, [page2])])
    assert len(rows) == 2
    assert rows[0].section == "Railways" and rows[0].page == 55
    assert rows[0].cells[1] == "Alpha Line (Railways) (100001)\n(N04000001) (PMG1)\ncontinued name part"
    assert rows[0].spans_page is True
    assert rows[1].cells[0] == "2" and rows[1].spans_page is False


def test_merge_tables_real_page_span_continuation_dropped_when_next_page_has_repeated_header():
    """Every real April page starts with the repeated column header. HEADER_FIRST clears
    `current` on it (see merge_tables' docstring), so a row that genuinely continues onto the
    next page has its tail silently dropped -- spans_page stays False and ROW_SPANS_PAGE is
    unreachable on the real report. This documents that loss rather than hiding it; the only
    cross-check is the declared Total(N) vs parsed-row-count comparison (see
    test_merge_tables_records_declared_totals and parser.run.report)."""
    page1 = [
        ["1", "Alpha Line (Railways) (100001)", "Bihar", "01/2020", "12/2026", "500\n520", "100", "20"],
    ]
    page2 = [
        ["Sl.No", "Project Name", "State", "Date of Approval", "DoC", "Cost", "Expenditure", "Progress"],
        ["", "(N04000001) (PMG1)", "", "", "", "", "", ""],
        ["2", "Beta Road (NHAI) (100002)", "Gujarat", "02/2021", "06/2027", "900\n950", "500", "60"],
    ]
    rows = merge_tables([(55, [page1]), (56, [page2])])
    assert len(rows) == 2
    assert rows[0].cells[1] == "Alpha Line (Railways) (100001)"  # continuation tail is dropped
    assert rows[0].spans_page is False


def test_merge_tables_records_declared_totals():
    """Each skipped "Total (N)" subtotal row declares how many projects belong to the block
    above it. Passing a list as `totals` records those N values so a caller (parser.run.report,
    via extract_rows_with_totals) can cross-check completeness by count -- the detector the
    Task 4 report proposed, now implemented and testable without a real PDF."""
    page = [
        ["1", "Alpha (Agency) (100001)", "Bihar", "01/2020", "12/2026", "500\n(520)", "100", "20"],
        ["2", "Beta (Agency) (100002)", "Gujarat", "02/2021", "06/2027", "900\n(950)", "500", "60"],
        ["", "Total (2)", "", "", "", "1400", "600", ""],
        ["", "Ministry of Coal", "", "", "", "", "", ""],
        ["", "Coal", "", "", "", "", "", ""],
        ["3", "Gamma (Agency) (100003)", "Odisha", "03/2022", "07/2028", "300\n(320)", "150", "40"],
        ["", "Total (1)", "", "", "", "300", "150", ""],
    ]
    totals = []
    rows = merge_tables([(80, [page])], totals=totals)
    assert len(rows) == 3
    assert totals == [2, 1]
    assert sum(totals) == len(rows)


def test_merge_tables_real_april_page_56_total_row_and_headings():
    """Rows copied verbatim from Flash_Report_April_2026.pdf PDF page 56.

    Two variants the synthetic fixture above does not have: the "Total (26)" subtotal row (which
    carries a cost and an expenditure number and must not be merged into Sl.No 26) and heading
    rows whose text sits in column 1 with an empty column 0 -- the same shape as a continuation.
    """
    page = [
        ["Sl.No", "Project Name\n(Agency)\n(Project Code) (Legacy OCMS Code) (PMGID)", "State",
         "Date of Approval\n(Start Date)\nMM/YYYY", "Orignal/Target DoC\n(Revised DoC)\nMM/YYYY",
         "Orignal Cost\nRevised Cost\nin Rs. Crore", "Cumulative\nExpenditure\nin Rs. Crore", "Physical Progress\n(%)"],
        ["26", "Re-Construction of Rigid portions of Secondary Runway, K and A Taxiway and\n"
               "Strengthening of C Taxiway at NSCBI Airport Kolkata.\n(Airport Authority of India [AAI])\n"
               "(612791)\n(N04000109) (-)", "West Bengal", "03/2023\n(12/2023)", "10/2025\n(08/2026)",
         "328.3\n(328.3)", "139.77", "64.5"],
        ["", "Total (26)", "", "", "", "21600.76", "10762.01", ""],
        ["", "Ministry of Coal", "", "", "", "", "", ""],
        ["", "Coal", "", "", "", "", "", ""],
        ["27", "TIKAK EXTENSION OCP\n(MIS MoCoal Integration Logins)\n(615820)\n(N06000290) (-)",
         "Assam", "07/2022\n(07/2022)", "07/2031\n(-)", "159.77\n(159.77)", "111.47", "88.18"],
    ]
    rows = merge_tables([(56, [page])])
    assert len(rows) == 2
    assert rows[0].cells[0] == "26" and rows[1].cells[0] == "27"
    assert "Total (26)" not in rows[0].cells[1]
    assert rows[0].cells[5] == "328.3\n(328.3)" and rows[0].cells[6] == "139.77"
    # the sector heading, not the ministry heading, is the one in force for the next block
    assert rows[1].section == "Coal"
    assert rows[0].section is None and rows[0].spans_page is False


def test_merge_tables_column_header_closes_the_open_row():
    """Every April page repeats the column header; a heading right after it is a heading, not a tail."""
    page1 = [["1", "Alpha (Agency) (100001)", "Bihar", "01/2020", "12/2026", "500\n(520)", "100", "20"]]
    page2 = [
        ["Sl.No", "Project Name", "State", "Date of Approval", "DoC", "Cost", "Expenditure", "Progress"],
        ["", "Ministry of Mines", "", "", "", "", "", ""],
        ["2", "Beta (Agency) (100002)", "Gujarat", "02/2021", "06/2027", "900\n(950)", "500", "60"],
    ]
    rows = merge_tables([(69, [page1]), (70, [page2])])
    assert len(rows) == 2
    assert rows[0].cells[1] == "Alpha (Agency) (100001)"
    assert rows[0].spans_page is False
    assert rows[1].section == "Ministry of Mines"
