from __future__ import annotations

"""Tests for document readers."""

from pathlib import Path
from phosphene.refverify.domain.readers import (
    extract_from_markdown,
    extract_bibliography,
)


def test_extract_from_markdown_explicit_header():
    md = """# My Manuscript

Some text introducing concepts.

## References

* Doe, J. (2020). The First Study. Journal of Examples, 1(1), 1-10.
* Smith, A. (2021). Another Study. Science, 2(2), 20-30.

## Appendix
Extra details.
"""
    bib = extract_from_markdown(md)
    assert "Doe, J. (2020)" in bib
    assert "Smith, A. (2021)" in bib
    assert "Extra details" not in bib


def test_extract_from_markdown_provenance_headings():
    headings = [
        "Data Sources and Provenance",
        "Empirical Baseline & Citations",
        "Standards & Regulatory References",
        "Data Sources",
        "Provenance",
    ]
    for h in headings:
        md = f"""# Engineering Spec

Some body paragraph discussing parameter (2020).

## {h}
* Doe, J. (2020). Primary Groundwork.
* Smith, A. (2021). Experimental Test.

## Appendix
* Extra details (2022).
"""
        bib = extract_from_markdown(md)
        assert "Doe, J. (2020)" in bib, f"Failed for heading {h}"
        assert "Smith, A. (2021)" in bib, f"Failed for heading {h}"
        assert "Extra details" not in bib, f"Leaked appendix for heading {h}"


def test_extract_from_markdown_explicit_comment_anchors():
    md = """# Document With Anchors

Body text mentioning various works.

<!-- refverify:begin -->
* Anchored, A. (2022). Explicit Target Study.
<!-- refverify:end -->

Post-anchor notes.
"""
    bib = extract_from_markdown(md)
    assert "Anchored, A. (2022)" in bib
    assert "Post-anchor notes" not in bib


def test_extract_from_markdown_fallback_bullets():
    md = """# Notes

* Doe, J. (2020). The First Study.
* Smith, A. (2021). Another Study.
"""
    bib = extract_from_markdown(md)
    assert "Doe, J. (2020)" in bib
    assert "Smith, A. (2021)" in bib


def test_extract_bibliography_dispatch_text(tmp_path: Path):
    p = tmp_path / "refs.txt"
    p.write_text("Doe, J. (2020). A test.")
    bib = extract_bibliography(p)
    assert bib.strip() == "Doe, J. (2020). A test."
