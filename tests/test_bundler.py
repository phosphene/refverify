"""Tests for VerificationBundler and SpatioGraph bounding box extractions."""

from __future__ import annotations

import fitz
import tarfile
from pathlib import Path

from phosphene.refverify.adapters.local_pdf import LocalPdfWitnessIndex
from phosphene.refverify.domain.proof import ProofTier
from phosphene.refverify.domain.provenance_slip import ProvenanceSlip
from phosphene.refverify.storage.bundler import VerificationBundler
from phosphene.refverify.storage.sqlite import SqliteVerificationLedger


def test_spatiograph_bounding_box_extraction(tmp_path: Path):
    pdf_dir = tmp_path / "vault"
    pdf_dir.mkdir()

    doc = fitz.open()
    page = doc.new_page(width=600, height=800)
    page.insert_text((72, 100), "Ancient ape locomotion and bipedal divergence.")
    doc.save(str(pdf_dir / "Ape_2020.pdf"))
    doc.close()

    index = LocalPdfWitnessIndex(pdf_dir)
    boxes = index.search_bounding_boxes("Ape_2020.pdf", "Ancient ape locomotion")
    assert len(boxes) >= 1
    page_num, bbox = boxes[0]
    assert page_num == 1
    assert bbox[0] > 0 and bbox[1] > 0

    urn = index.format_spatiograph_urn("Ape_2020.pdf", page_number=1, rect_bbox=bbox)
    assert urn.startswith("urn:cts:phosphene:vault.")
    assert ":p1#rect=" in urn


def test_bundler_hermetic_export(tmp_path: Path):
    db_file = tmp_path / "ledger.db"
    ledger = SqliteVerificationLedger(db_file)
    urn = "urn:cts:doc#1"
    ledger.register_citation(urn, "v29", "Darwin 1881", "Earthworms", year=1881)
    ledger.record_proof_state(urn, "L4_VERBATIM_EXTRACTED", 95.0, "local_library")

    prov_dir = tmp_path / "provenance"
    slip = ProvenanceSlip(
        provenance_id="prov:1",
        citation_urn=urn,
        doc_id="v29",
        claimed_text="lowly organised creatures",
        contiguous_witness_text="as have these lowly organised creatures.",
        proof_tier=ProofTier.L4_VERBATIM_EXTRACTED,
        witness_sha256="abcsha",
        witness_filename="Darwin_1881.pdf",
    )
    slip.save(prov_dir / "darwin.provenance.md")

    bundler = VerificationBundler(output_dir=tmp_path / "bundles")
    bundle_tar = bundler.export_bundle(doc_id="v29", sqlite_db_path=db_file, provenance_dir=prov_dir)

    assert bundle_tar.exists()
    assert bundle_tar.name.endswith(".tar.gz")

    # Verify tar contents
    with tarfile.open(bundle_tar, "r:gz") as tar:
        names = tar.getnames()
        assert any("manifest.json" in n for n in names)
        assert any("ledger.db" in n for n in names)
        assert any("darwin.provenance.md" in n for n in names)
