from parser.extract import RawRow
from parser.normalize import normalize, parse_dates, parse_numbers, split_name


def test_split_name_all_parentheticals():
    r = split_name("Sikkim Road Project (Border Roads Organisation) (612793) (N04000110) (PMG12345)")
    assert r["project_name"] == "Sikkim Road Project"
    assert r["agency_raw"] == "Border Roads Organisation"
    assert r["project_code"] == "612793"
    assert r["legacy_ocms_code"] == "N04000110"
    assert r["pmgid"] == "PMG12345"
    assert r["flags"] == []


def test_split_name_missing_ids_flags():
    r = split_name("Some Project\n(Agency Name Ltd)\n(612794)")
    assert r["project_code"] == "612794" and r["legacy_ocms_code"] is None and r["pmgid"] is None
    assert set(r["flags"]) == {"NO_LEGACY_CODE", "NO_PMGID"}
    r2 = split_name("Nameless Codes (Agency)")
    assert r2["project_code"] is None and "NO_PROJECT_CODE" in r2["flags"]


def test_parse_dates():
    assert parse_dates("11/2023 (01/2024)") == ("2023-11", "2024-01", [])
    assert parse_dates("06/2026\n(06/2027)") == ("2026-06", "2027-06", [])
    assert parse_dates("06/2026") == ("2026-06", None, [])
    assert parse_dates("-") == (None, None, ["DATE_PARSE_FAIL"])


def test_parse_numbers():
    assert parse_numbers("323.26\n350.00") == [323.26, 350.0]
    assert parse_numbers("1,856.36 / 3,800.00") == [1856.36, 3800.0]
    assert parse_numbers("") == []


def test_normalize_sample_row():
    raw = RawRow(page=57, section="Road Transport and Highways", spans_page=False, cells=[
        "12", "Sikkim Road Project (Border Roads Organisation) (612793) (N04000110) (PMG12345)", "Sikkim",
        "11/2023 (01/2024)", "06/2026 (06/2027)", "323.26\n350.00", "80.84", "34.25"])
    row = normalize(raw, "2026-04", "Flash_Report_April_2026.pdf", "a" * 64)
    assert row["snapshot"] == "2026-04" and row["page"] == 57 and row["sl_no"] == 12
    assert row["project_code"] == "612793" and row["state"] == "Sikkim" and row["table_section"] == "Road Transport and Highways"
    assert row["approval_month"] == "2023-11" and row["start_month"] == "2024-01"
    assert row["doc_original"] == "2026-06" and row["doc_revised"] == "2027-06"
    assert row["cost_original_cr"] == 323.26 and row["cost_revised_cr"] == 350.0
    assert row["expenditure_cum_cr"] == 80.84 and row["physical_progress_pct"] == 34.25
    assert row["parse_flags"] == ""
    assert len(row) == 21


def test_normalize_multiline_state_and_missing_numbers():
    raw = RawRow(page=60, section=None, spans_page=True, cells=[
        "13", "Island Jetty (Port Authority) (100012)", "Andaman and\nNicobar Islands", "08/2023", "01/2027", "250.00", "-", "27"])
    row = normalize(raw, "2026-04", "f.pdf", "b" * 64)
    assert row["state"] == "Andaman and Nicobar Islands"
    assert row["expenditure_cum_cr"] is None
    flags = set(row["parse_flags"].split(";"))
    assert {"MULTILINE_STATE", "NUM_PARSE_FAIL", "ROW_SPANS_PAGE", "NO_LEGACY_CODE", "NO_PMGID"} <= flags


# --- variants below use cell text copied verbatim out of Flash_Report_April_2026.pdf ---


def test_split_name_real_row_legacy_code_is_bare_digits():
    """PDF page 56, Sl.No 32: legacy OCMS code prints as '060100093', not the 'N06000290' shape."""
    r = split_name("GEVRA OC [70 MTY]\n(South Eastern Coalfields Limited [SECL])\n(400424)\n(060100093) (192)")
    assert r["project_name"] == "GEVRA OC [70 MTY]"
    assert r["agency_raw"] == "South Eastern Coalfields Limited [SECL]"
    assert r["project_code"] == "400424"
    assert r["legacy_ocms_code"] == "060100093"
    assert r["pmgid"] == "192"
    assert r["flags"] == []


def test_split_name_real_row_dash_means_not_printed():
    """PDF page 56, Sl.No 39 and 40: '-' stands for a code the report does not print."""
    r = split_name("KUSMUNDA OC EXPANSION PROJECT\n(SECL - CIL)\n(617287)\n(-) (9611)")
    assert r["agency_raw"] == "SECL - CIL" and r["project_code"] == "617287"
    assert r["legacy_ocms_code"] is None and r["pmgid"] == "9611"
    assert r["flags"] == ["NO_LEGACY_CODE"]
    r2 = split_name("MANIKPUR OC EXPANSION PROJECT\n(South Eastern Coalfields Limited [SECL])\n(617288)\n(-) (-)")
    assert r2["legacy_ocms_code"] is None and r2["pmgid"] is None
    assert set(r2["flags"]) == {"NO_LEGACY_CODE", "NO_PMGID"}


def test_split_name_extra_parentheticals_fold_into_agency_raw():
    """Nothing in April prints more than the four documented groups (fires zero times). parse_flag
    is a closed enum (contracts/enums.json) with no slot for this shape, so surplus
    parentheticals are folded into agency_raw instead of a flag being invented for them -- see
    the SPEC? comment in split_name."""
    r = split_name("Some Project (Phase II) (Agency) (612793) (N04000110) (PMG1) (extra)")
    assert r["project_code"] == "612793"
    assert r["legacy_ocms_code"] == "N04000110" and r["pmgid"] == "PMG1"
    assert r["agency_raw"] == "Agency Phase II extra"
    assert r["flags"] == []


def test_parse_dates_real_na_approval_and_missing_revised_doc():
    """PDF page 64, Sl.No 200: approval prints 'NA' but the start date is still given."""
    assert parse_dates("NA\n(10/2024)") == (None, "2024-10", ["DATE_PARSE_FAIL"])
    assert parse_dates("10/2026\n(-)") == ("2026-10", None, [])
    assert parse_dates("12/2020\n(10/2022)") == ("2020-12", "2022-10", [])


def test_parse_numbers_real_cost_cell_is_original_then_revised_in_parens():
    """PDF page 56: cost prints 'Orignal Cost\\n(Revised Cost)'; integers appear without decimals."""
    assert parse_numbers("323.26\n(323.26)") == [323.26, 323.26]
    assert parse_numbers("1207\n(1207)") == [1207.0, 1207.0]
    assert parse_numbers("11816.4\n(11816.4)") == [11816.4, 11816.4]


def test_normalize_real_april_row_page_56_sl_21():
    raw = RawRow(page=56, section="Aviation & Aviation Infrastructure", spans_page=False, cells=[
        "21",
        "Widening of basic strip at Western Side of Runway Chainage 80m to 920m i/c slope\n"
        "stabilization Measures [Balance work] of uphill and Improvement of Storm Water\n"
        "Drainage System at Pakyong Airport, Sikkim on design & build basis [EPC] with\n"
        "integrated 10 years maintenance.\n(Airport Authority of India [AAI])\n(612793)\n(N04000110) (-)",
        "Sikkim", "11/2023\n(12/2023)", "06/2026\n(06/2027)", "323.26\n(323.26)", "80.84", "34.25"])
    row = normalize(raw, "2026-04", "Flash_Report_April_2026.pdf", "c" * 64)
    assert row["sl_no"] == 21 and row["page"] == 56
    assert row["project_code"] == "612793" and row["legacy_ocms_code"] == "N04000110" and row["pmgid"] is None
    assert row["agency_raw"] == "Airport Authority of India [AAI]"
    assert row["project_name"].startswith("Widening of basic strip at Western Side of Runway Chainage 80m")
    assert "\n" not in row["project_name"]
    assert row["table_section"] == "Aviation & Aviation Infrastructure" and row["state"] == "Sikkim"
    assert row["approval_month"] == "2023-11" and row["start_month"] == "2023-12"
    assert row["doc_original"] == "2026-06" and row["doc_revised"] == "2027-06"
    assert row["cost_original_cr"] == 323.26 and row["cost_revised_cr"] == 323.26
    assert row["expenditure_cum_cr"] == 80.84 and row["physical_progress_pct"] == 34.25
    assert row["parse_flags"] == "NO_PMGID"


def test_normalize_real_multi_state_row_page_55_sl_17():
    raw = RawRow(page=55, section="Aviation & Aviation Infrastructure", spans_page=False, cells=[
        "17",
        "SITC of ATM Automation System and ASMGCS [Including SMR & MLAT] for Mumbai,\n"
        "Navi Mumbai, Jewar [earlier MOPA, without ASMGCS], HIAL & BIAL\n"
        "(Airport Authority of India [AAI])\n(611570)\n(-) (-)",
        "Multi-States\n(Karnataka,\nMaharashtra,\nTelangana, Uttar\nPradesh)",
        "12/2020\n(10/2022)", "09/2025\n(08/2026)", "500.48\n(500.48)", "381.2", "78"])
    row = normalize(raw, "2026-04", "Flash_Report_April_2026.pdf", "c" * 64)
    assert row["state"] == "Multi-States (Karnataka, Maharashtra, Telangana, Uttar Pradesh)"
    assert row["cost_original_cr"] == 500.48 and row["physical_progress_pct"] == 78.0
    assert set(row["parse_flags"].split(";")) == {"MULTILINE_STATE", "NO_LEGACY_CODE", "NO_PMGID"}


def test_epoch_date_is_null_not_a_date():
    """The reports print 01/1900 as a date. It is the source system's zero date, not a month.

    Real cells, July 2026 page 76: GMC Leh 707057 approval reads "10/2019 (01/1900)" and its
    Orignal/Target DoC reads "01/1900"; GMC Handwara 707052 reads "NA (01/1900)".
    """
    assert parse_dates("01/1900") == (None, None, ["EPOCH_DATE"])
    assert parse_dates("10/2019\n(01/1900)") == ("2019-10", None, ["EPOCH_DATE"])
    assert parse_dates("NA\n(01/1900)") == (None, None, ["DATE_PARSE_FAIL", "EPOCH_DATE"])


def test_epoch_date_does_not_disturb_real_dates():
    assert parse_dates("11/2023 (01/2024)") == ("2023-11", "2024-01", [])
    assert parse_dates("01/2000 (01/1901)") == ("2000-01", "1901-01", [])
