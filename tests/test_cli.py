"""Tests for refverify CLI entry points, argument parsing, JSON reports, and verbatim quotation verification."""

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


def test_cli_verify_verbatim_pass(tmp_path: Path):
    witness_dir = tmp_path / "witnesses"
    witness_dir.mkdir()
    (witness_dir / "faraday1832.txt").write_text(
        "By magnetic curves, I mean the lines of magnetic forces, however produced by the magnet."
    )

    manuscript = tmp_path / "manuscript.md"
    manuscript.write_text(
        """# Electromagnetic Discovery

> By magnetic curves, I mean the lines of magnetic forces... (Faraday 1832)

## References
* Faraday, M. (1832). Experimental Researches in Electricity. Philosophical Transactions.
"""
    )
    json_out = tmp_path / "verbatim_report.json"

    fake_result = VerdictResult(
        verdict=Verdict.VERIFIED,
        score=98.0,
        reasons=("exact_match",),
        matched_title="Experimental Researches in Electricity",
    )

    with patch("phosphene.refverify.__main__.verify_all", return_value=[fake_result]):
        code = main([
            str(manuscript),
            "--verify-verbatim", str(witness_dir),
            "--no-cache",
            "--json-out", str(json_out),
        ])

    assert code == EXIT_OK
    assert json_out.exists()
    data = json.loads(json_out.read_text())
    assert data["gate"] == "pass"
    file_rep = data["files"][0]
    assert file_rep["verbatim_decision"] == "pass"
    assert len(file_rep["verbatim_quotes"]) == 1
    assert file_rep["verbatim_quotes"][0]["status"] == "verbatim_verified"


def test_cli_verify_verbatim_mutated_blocks(tmp_path: Path):
    witness_dir = tmp_path / "witnesses"
    witness_dir.mkdir()
    (witness_dir / "faraday1832.txt").write_text(
        "By magnetic curves, I mean the lines of magnetic forces, however produced by the magnet."
    )

    manuscript = tmp_path / "mutated_manuscript.md"
    manuscript.write_text(
        """# Distorted Claim

> By magnetic curves, I mean the lines of magnetic energy... (Faraday 1832)

## References
* Faraday, M. (1832). Experimental Researches in Electricity. Philosophical Transactions.
"""
    )

    fake_result = VerdictResult(
        verdict=Verdict.VERIFIED,
        score=98.0,
        reasons=("exact_match",),
        matched_title="Experimental Researches in Electricity",
    )

    with patch("phosphene.refverify.__main__.verify_all", return_value=[fake_result]):
        code = main([
            str(manuscript),
            "--verify-verbatim", str(witness_dir),
            "--no-cache",
        ])

    assert code == EXIT_BLOCK
