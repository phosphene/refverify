"""Tests for ProvenanceSlip markdown generation and zero-ellipses extraction."""

from __future__ import annotations

from pathlib import Path
from phosphene.refverify.domain.proof import ProofTier
from phosphene.refverify.domain.provenance_slip import ProvenanceSlip
from phosphene.refverify.domain.verbatim import extract_contiguous_witness_unit


def test_extract_contiguous_witness_unit_zero_ellipses():
    witness = (
        "Reconstructing the hominin ancestral morphotype is essential. "
        "Modern hominoids evolved in Africa from Miocene ape ancestors unlike any living species. "
        "Locomotor diversity was exceptional across Europe and Africa."
    )
    unit = extract_contiguous_witness_unit(witness, "unlike any living species")
    assert unit is not None
    assert "..." not in unit
    assert "…" not in unit
    assert unit == "Modern hominoids evolved in Africa from Miocene ape ancestors unlike any living species."


def test_provenance_slip_markdown_format(tmp_path: Path):
    slip = ProvenanceSlip(
        provenance_id="prov:2026-11-18:almecija:p2",
        citation_urn="urn:cts:phosphene:doc:v29#cit:almecija",
        doc_id="valence-v29",
        claimed_text="unlike any living species",
        contiguous_witness_text="Modern hominoids evolved in Africa from Miocene ape ancestors unlike any living species.",
        proof_tier=ProofTier.L4_VERBATIM_EXTRACTED,
        witness_sha256="abc12345sha",
        witness_filename="Almecija_2021.pdf",
        page_number=2,
        bounding_box=(72.0, 150.0, 450.0, 165.0),
    )

    out_file = tmp_path / "almecija.provenance.md"
    slip.save(out_file)

    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "proof_tier: L4_VERBATIM_EXTRACTED" in content
    assert "witness_sha256: abc12345sha" in content
    assert "page_number: 2" in content
    assert "### Primary Witness Extracted Unit" in content
    assert "Modern hominoids evolved in Africa from Miocene ape ancestors unlike any living species." in content
