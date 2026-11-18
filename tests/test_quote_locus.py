"""Tests for OCR / ligature unfolding and locus verification against PDF witnesses."""

from __future__ import annotations

import fitz
from pathlib import Path
from unittest.mock import patch

from phosphene.refverify.__main__ import EXIT_OK, main
from phosphene.refverify.adapters.local_pdf import LocalPdfWitnessIndex
from phosphene.refverify.domain.verbatim import (
    VerbatimStatus,
    normalize_verbatim_text,
    verify_verbatim_quote,
)
from phosphene.refverify.domain.verdict import Verdict, VerdictResult


def test_normalize_verbatim_text_ligatures_and_hyphenation():
    raw = "The ﬁrst clambering ape exhibited a disc-\nretionary loc-\n   omotor adaptation."
    norm = normalize_verbatim_text(raw)
    assert "first" in norm
    assert "discretionary" in norm
    assert "locomotor" in norm
    assert "ﬁ" not in norm


def test_verify_verbatim_quote_page_number_and_ocr():
    witness = (
        "Modern hominoids evolved in Africa from Miocene ape ancestors "
        "unlike any living species. Locomotor diversity was high."
    )
    claim = "Miocene ape ancestors unlike any living species"
    res = verify_verbatim_quote(claim, witness, coordinate="almecija:p1", page_number=2)
    assert res.status == VerbatimStatus.VERBATIM_VERIFIED
    assert res.page_number == 2
    assert res.matched_span is not None


def test_cli_verify_quotes_with_local_pdf(tmp_path: Path):
    pdf_dir = tmp_path / "acquired"
    pdf_dir.mkdir()

    # Generate a small PDF witness
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text((50, 50), "Almécija et al. 2021 Science Review\nAncestors unlike any living species.")
    doc.save(str(pdf_dir / "Almecija_2021_Science.pdf"))
    doc.close()

    manuscript = tmp_path / "test_paper.md"
    manuscript.write_text(
        """# Miocene Apes

Almécija et al. (2021) demonstrated that early hominoids were "unlike any living species" (Almécija et al., 2021, p. 1).

## References
Almécija, S., et al. (2021). Fossil apes and human evolution. Science, 372, eabb4363.
"""
    )

    json_out = tmp_path / "quote_report.json"

    fake_result = VerdictResult(
        verdict=Verdict.VERIFIED,
        score=95.0,
        reasons=("title_exact",),
        matched_title="Fossil apes and human evolution",
        matched_source="local_library",
    )

    with patch("phosphene.refverify.__main__.verify_all", return_value=[fake_result]):
        code = main([
            str(manuscript),
            "--local-pdf-dir", str(pdf_dir),
            "--verify-quotes",
            "--no-cache",
            "--json-out", str(json_out),
        ])

    assert code == EXIT_OK
    assert json_out.exists()
