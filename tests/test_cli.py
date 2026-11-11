"""Tests for refverify CLI entry points, argument parsing, and JSON report emission."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from phosphene.refverify.__main__ import EXIT_BLOCK, EXIT_OK, EXIT_USAGE, main
from phosphene.refverify.domain.verdict import Verdict, VerdictResult


def test_cli_usage_no_args():
    assert main([]) == EXIT_USAGE


def test_cli_file_not_found(tmp_path: Path):
    non_existent = tmp_path / "missing.md"
    assert main([str(non_existent)]) == EXIT_USAGE


def test_cli_markdown_file_and_json_out(tmp_path: Path):
    md_file = tmp_path / "paper.md"
    md_file.write_text(
        """# Sample Paper

## Data Sources and Provenance
* Bell, R. H. V. (1971). A grazing ecosystem in the Serengeti. Scientific American, 224(1), 86-93.
"""
    )
    json_out = tmp_path / "report.json"

    # Mock verify_all to return a fast deterministic verdict without network
    fake_result = VerdictResult(
        verdict=Verdict.VERIFIED,
        score=95.0,
        reasons=("exact_match",),
        matched_title="A grazing ecosystem in the Serengeti",
        matched_doi="10.1038/scientificamerican0171-86",
        matched_source="crossref",
    )

    with patch("phosphene.refverify.__main__.verify_all", return_value=[fake_result]):
        code = main([str(md_file), "--no-cache", "--json-out", str(json_out)])

    assert code == EXIT_OK
    assert json_out.exists()

    data = json.loads(json_out.read_text())
    assert data["gate"] == "pass"
    assert data["total_blocking"] == 0
    assert len(data["files"]) == 1

    file_rep = data["files"][0]
    assert file_rep["summary"]["total"] == 1
    assert file_rep["summary"]["verified"] == 1
    assert file_rep["references"][0]["verdict"] == "verified"
    assert file_rep["references"][0]["score"] == 95.0


def test_cli_blocking_gate(tmp_path: Path):
    md_file = tmp_path / "bad.md"
    md_file.write_text(
        """# Sample

## References
* Nonexistent, Z. (1900). Phantom study.
"""
    )
    fake_blocking = VerdictResult(
        verdict=Verdict.NOT_FOUND,
        score=0.0,
        reasons=("not_found",),
    )

    with patch("phosphene.refverify.__main__.verify_all", return_value=[fake_blocking]):
        code = main([str(md_file), "--no-cache"])

    assert code == EXIT_BLOCK
