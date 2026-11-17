"""Comprehensive tests for philological citation and verbatim quotation verification.

Reorients verification evaluation toward classical philology, comparative mythology,
and ethnographic field records (Parker 1923, Propp 1968, Thompson 1936, Lévi-Strauss 1964,
d'Huy & Berezkin 2018), enforcing strict textual verbatim gates without scientific notation overhead.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from phosphene.refverify.__main__ import EXIT_BLOCK, EXIT_OK, main
from phosphene.refverify.domain.reference import from_wikitext_entry
from phosphene.refverify.domain.scoring import CandidateRecord, score_match
from phosphene.refverify.domain.verbatim import (
    VerbatimResult,
    VerbatimStatus,
    verify_verbatim_quote,
)
from phosphene.refverify.domain.verdict import Verdict, VerdictResult

CORPUS_DIR = Path(__file__).parent / "corpus" / "witnesses" / "philological"


def test_philological_witness_fixtures_present():
    """Verify all 5 primary philological witness fixtures exist and are non-empty."""
    expected_witnesses = [
        "parker1923.txt",
        "propp1968.txt",
        "thompson1936.txt",
        "levistrauss1964.txt",
        "dhuy_berezkin2018.txt",
    ]
    for filename in expected_witnesses:
        path = CORPUS_DIR / filename
        assert path.is_file(), f"Missing witness fixture: {path}"
        assert len(path.read_text(encoding="utf-8").strip()) > 100


# =========================================================================
# 1. Vladimir Propp (1968) - Morphology of the Folktale
# =========================================================================

def test_propp_exact_verbatim_match():
    witness = (CORPUS_DIR / "propp1968.txt").read_text(encoding="utf-8")
    claim = (
        "Functions of dramatis personae serve as stable, constant elements in a tale, "
        "independent of how and by whom they are fulfilled."
    )
    res = verify_verbatim_quote(claim, witness, coordinate="propp1968:ch2:p1")
    assert res.status == VerbatimStatus.VERBATIM_VERIFIED
    assert res.matched_span is not None
    assert res.divergence_reason is None


def test_propp_ellipsis_monotonic_extraction():
    witness = (CORPUS_DIR / "propp1968.txt").read_text(encoding="utf-8")
    claim = (
        "The study of the folktale has been conducted largely by descriptive methods ... "
        "the number of basic functions does not exceed thirty-one."
    )
    res = verify_verbatim_quote(claim, witness, coordinate="propp1968:ch2:p2")
    assert res.status == VerbatimStatus.VERBATIM_VERIFIED
    assert res.matched_span is not None


def test_propp_translation_smoothing_blocked():
    """Adversarial LLM paraphrasing: changing 'Functions of dramatis personae' to 'Character functions'."""
    witness = (CORPUS_DIR / "propp1968.txt").read_text(encoding="utf-8")
    claim = (
        "Character functions serve as stable, constant elements in a tale, "
        "independent of how and by whom they are fulfilled."
    )
    res = verify_verbatim_quote(claim, witness, coordinate="propp1968:ch2:p1:mutated")
    assert res.status == VerbatimStatus.VERBATIM_MUTATED
    assert "subspan_not_found" in res.divergence_reason


# =========================================================================
# 2. Arthur C. Parker (1923) - Seneca Myths (Earth-Diver / Turtle Island)
# =========================================================================

def test_parker_exact_verbatim_match():
    witness = (CORPUS_DIR / "parker1923.txt").read_text(encoding="utf-8")
    claim = (
        "The great Snapping Turtle offered his carapace to support her. The creatures dived "
        "for earth mud from the deep bottom, and the muskrat brought up a small morsel"
    )
    res = verify_verbatim_quote(claim, witness, coordinate="parker1923:p1:earth-diver")
    assert res.status == VerbatimStatus.VERBATIM_VERIFIED
    assert res.matched_span is not None


def test_parker_adversarial_entity_swap_blocked():
    """Adversarial entity swap: substituting 'beaver' for 'muskrat'."""
    witness = (CORPUS_DIR / "parker1923.txt").read_text(encoding="utf-8")
    claim = (
        "The great Snapping Turtle offered his carapace to support her. The creatures dived "
        "for earth mud from the deep bottom, and the beaver brought up a small morsel"
    )
    res = verify_verbatim_quote(claim, witness, coordinate="parker1923:p1:mutated")
    assert res.status == VerbatimStatus.VERBATIM_MUTATED
    assert "subspan_not_found" in res.divergence_reason


# =========================================================================
# 3. Stith Thompson (1936) - Motif-Index of Folk-Literature
# =========================================================================

def test_thompson_verbatim_quote_with_curly_quotes():
    witness = (CORPUS_DIR / "thompson1936.txt").read_text(encoding="utf-8")
    claim = (
        '“A motif is the smallest element in a tale having a power to persist in tradition. '
        'In order to have this power it must have in it something of the unusual and striking.”'
    )
    res = verify_verbatim_quote(claim, witness, coordinate="thompson1936:intro:motif-def")
    assert res.status == VerbatimStatus.VERBATIM_VERIFIED


def test_thompson_bibliographic_and_scoring_alignment():
    """Verify bibliographic identity match of Stith Thompson monograph without scientific notation."""
    ref_text = (
        "Thompson, S. (1936). Motif-Index of Folk-Literature. Indiana University Press."
    )
    ref = from_wikitext_entry(ref_text)
    candidate = CandidateRecord(
        title="Motif-Index of Folk-Literature",
        authors=("Stith Thompson",),
        year=1936,
        source="crossref",
    )
    score, reasons = score_match(ref, candidate)
    assert score >= 85.0


# =========================================================================
# 4. Claude Lévi-Strauss (1964) - Le Cru et le Cuit (French Accents & Quotes)
# =========================================================================

def test_levistrauss_french_diacritics_verbatim():
    witness = (CORPUS_DIR / "levistrauss1964.txt").read_text(encoding="utf-8")
    claim = (
        "Le mythe est un système clos dans lequel tout se tient. "
        "La récurrence des schèmes mythiques atteste la présence de structures invariantes sous la diversité des récits."
    )
    res = verify_verbatim_quote(claim, witness, coordinate="levistrauss1964:ouverture")
    assert res.status == VerbatimStatus.VERBATIM_VERIFIED


# =========================================================================
# 5. Julien d'Huy & Yuri Berezkin (2018) - Phylogenetic Comparative Mythology
# =========================================================================

def test_dhuy_berezkin_cosmic_hunt_claim():
    witness = (CORPUS_DIR / "dhuy_berezkin2018.txt").read_text(encoding="utf-8")
    claim = (
        "The Cosmic Hunt is one of the most widespread mythological motifs across Eurasia and the Americas. "
        "The core plot involves one or more hunters pursuing one or more animals, "
        "which are subsequently transformed into stars or constellations."
    )
    res = verify_verbatim_quote(claim, witness, coordinate="dhuy:sec2:cosmic-hunt")
    assert res.status == VerbatimStatus.VERBATIM_VERIFIED


# =========================================================================
# 6. CLI Integration & Hard Verification Gate on Philological Manuscript
# =========================================================================

def test_cli_philological_manuscript_pass(tmp_path: Path):
    """End-to-end CLI gate verification on a philological manuscript quoting Parker (1923)."""
    manuscript = tmp_path / "seneca_cosmology.md"
    manuscript.write_text(
        """# Iroquois Cosmological Stratigraphy

> In the center of this celestial town grew a celestial tree which blossomed and bore fruit continuously...
> The birds saw her falling and flew up with joined wings to cushion her descent. (Parker 1923)

## References
* Parker, A. C. (1923). Seneca Myths and Folk Tales. Buffalo Historical Society.
""",
        encoding="utf-8",
    )
    json_out = tmp_path / "report.json"

    fake_bib_result = VerdictResult(
        verdict=Verdict.VERIFIED,
        score=95.0,
        reasons=("title_exact", "author_match"),
        matched_title="Seneca Myths and Folk Tales",
        matched_source="crossref",
    )

    with patch("phosphene.refverify.__main__.verify_all", return_value=[fake_bib_result]):
        code = main([
            str(manuscript),
            "--verify-verbatim", str(CORPUS_DIR),
            "--no-cache",
            "--json-out", str(json_out),
        ])

    assert code == EXIT_OK
    assert json_out.exists()
    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["gate"] == "pass"
    assert data["total_blocking"] == 0

    file_report = data["files"][0]
    assert file_report["verbatim_decision"] == "pass"
    assert len(file_report["verbatim_quotes"]) == 1
    assert file_report["verbatim_quotes"][0]["status"] == "verbatim_verified"


def test_cli_philological_manuscript_blocks_on_translation_smoothing(tmp_path: Path):
    """End-to-end CLI gate blocks when an LLM smoothed quote is present in the manuscript."""
    manuscript = tmp_path / "propp_analysis.md"
    manuscript.write_text(
        """# Morphology and Narrative Grammar

> Character actions serve as permanent, fixed units in a tale... (Propp 1968)

## References
* Propp, V. (1968). Morphology of the Folktale. University of Texas Press.
""",
        encoding="utf-8",
    )

    fake_bib_result = VerdictResult(
        verdict=Verdict.VERIFIED,
        score=95.0,
        reasons=("title_exact",),
        matched_title="Morphology of the Folktale",
        matched_source="crossref",
    )

    with patch("phosphene.refverify.__main__.verify_all", return_value=[fake_bib_result]):
        code = main([
            str(manuscript),
            "--verify-verbatim", str(CORPUS_DIR),
            "--no-cache",
        ])

    # Must trigger gate BLOCK due to mutated quote
    assert code == EXIT_BLOCK
