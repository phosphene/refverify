"""Tests for plain APA/Chicago bibliography parsing and CLI integration."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from phosphene.refverify.__main__ import EXIT_OK, main
from phosphene.refverify.domain.reference import from_plain_entry, parse_bibliography_plain
from phosphene.refverify.domain.verdict import Verdict, VerdictResult


def test_from_plain_entry_apa():
    line = "Boyd, R., & Richerson, P.J. (1985). Culture and the Evolutionary Process. University of Chicago Press."
    ref = from_plain_entry(line)
    assert ref.year == 1985
    assert ref.title == "Culture and the Evolutionary Process"
    assert "Boyd, R." in ref.authors
    assert "Richerson, P.J." in ref.authors


def test_parse_bibliography_plain_multiple_lines():
    text = """
    Almécija, S., Hammond, A.S., et al. (2021). Fossil apes and human evolution. Science, 372(6542), eabb4363.
    Cavalli-Sforza, L.L., & Feldman, M.W. (1981). Cultural Transmission and Evolution. Princeton University Press.
    """
    refs = parse_bibliography_plain(text)
    assert len(refs) == 2
    assert refs[0].year == 2021
    assert refs[0].title == "Fossil apes and human evolution"
    assert refs[1].year == 1981
    assert refs[1].title == "Cultural Transmission and Evolution"


def test_cli_plain_bibliography_with_local_pdf(tmp_path: Path):
    doc_path = tmp_path / "monograph.md"
    doc_path.write_text(
        """# Monograph Draft

## References
Boyd, R., & Richerson, P.J. (1985). Culture and the Evolutionary Process. University of Chicago Press.
"""
    )
    json_out = tmp_path / "report.json"

    fake_result = VerdictResult(
        verdict=Verdict.VERIFIED,
        score=95.0,
        reasons=("title_exact",),
        matched_title="Culture and the Evolutionary Process",
        matched_source="local_library",
    )

    with patch("phosphene.refverify.__main__.verify_all", return_value=[fake_result]):
        code = main([
            str(doc_path),
            "--no-cache",
            "--json-out", str(json_out),
        ])

    assert code == EXIT_OK
    assert json_out.exists()
    data = json.loads(json_out.read_text())
    assert data["gate"] == "pass"
    assert data["files"][0]["summary"]["verified"] == 1
    assert data["files"][0]["references"][0]["parsed_year"] == 1985
