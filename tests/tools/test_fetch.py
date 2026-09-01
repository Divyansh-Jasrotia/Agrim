import hashlib
from pathlib import Path

import pytest

from tools import fetch_pdfs as fp


def test_pdfs_table_has_all_snapshots():
    assert list(fp.PDFS) == ["2025-12", "2026-04", "2026-05", "2026-06", "2026-07"]
    for snap, (name, url, size) in fp.PDFS.items():
        assert name.endswith(".pdf") and url.startswith("https://www.mospi.gov.in/") and size > 6_000_000


def test_sums_roundtrip(tmp_path):
    f = tmp_path / "a.pdf"
    f.write_bytes(b"hello")
    sums = tmp_path / "SHA256SUMS"
    fp.write_sums([f], sums)
    assert sums.read_text().strip() == hashlib.sha256(b"hello").hexdigest() + "  a.pdf"
    assert fp.verify_sums(sums, tmp_path) == []
    f.write_bytes(b"tampered")
    assert fp.verify_sums(sums, tmp_path) == ["a.pdf"]


@pytest.mark.skipif(not Path("data/pdfs/SHA256SUMS").exists(), reason="PDFs not fetched yet")
def test_committed_pdfs_match_sums_and_sizes():
    assert fp.verify_sums(Path("data/pdfs/SHA256SUMS"), Path("data/pdfs")) == []
    for snap, (name, url, size) in fp.PDFS.items():
        assert (Path("data/pdfs") / name).stat().st_size == size, f"{name} size changed; re-fetch or update PDFS"
