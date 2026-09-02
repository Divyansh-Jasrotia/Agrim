"""One adapter per snapshot: which file, which pages, what the month is known to omit. Task 5 fills the other four."""
from dataclasses import dataclass

from tools.fetch_pdfs import PDFS


@dataclass(frozen=True)
class Adapter:
    snapshot: str
    file: str
    pages: tuple = None          # (start, end) 1-based; None = auto-detect
    expect_pmgid: bool = True    # False => NO_PMGID is not counted as a miss in the coverage report
    expect_legacy: bool = True


ADAPTERS = {
    "2025-12": Adapter("2025-12", PDFS["2025-12"][0], pages=(50, 107), expect_pmgid=False, expect_legacy=False),
    "2026-04": Adapter("2026-04", PDFS["2026-04"][0], pages=(55, 162)),
    "2026-05": Adapter("2026-05", PDFS["2026-05"][0], pages=(54, 158), expect_pmgid=False),
    "2026-06": Adapter("2026-06", PDFS["2026-06"][0], pages=(59, 159), expect_pmgid=False, expect_legacy=False),
    "2026-07": Adapter("2026-07", PDFS["2026-07"][0], pages=(55, 152), expect_pmgid=False, expect_legacy=False),
}
