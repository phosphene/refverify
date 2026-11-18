"""Tests for SqliteVerificationLedger relational storage."""

from __future__ import annotations

from pathlib import Path
from phosphene.refverify.storage.sqlite import SqliteVerificationLedger


def test_sqlite_ledger_witness_and_citations(tmp_path: Path):
    db_file = tmp_path / "test_ledger.db"
    ledger = SqliteVerificationLedger(db_file)

    # 1. Register physical witness
    ledger.register_witness(
        sha256="abc123sha",
        file_path="/vault/Almecija_2021.pdf",
        filename="Almecija_2021.pdf",
        title="Fossil apes and human evolution",
        authors=["Almécija, S.", "Hammond, A.S."],
        year=2021,
        doi="10.1126/science.abb4363",
        page_count=42,
    )

    # 2. Register citation in manuscript
    urn = "urn:cts:phosphene:doc:v29#cit:almecija2021"
    ledger.register_citation(
        citation_urn=urn,
        doc_id="valence-v29",
        raw_text="Almécija, S., et al. (2021). Fossil apes and human evolution. Science, 372, eabb4363.",
        title="Fossil apes and human evolution",
        authors=["Almécija, S."],
        year=2021,
        doi="10.1126/science.abb4363",
    )

    # 3. Record proof state elevation
    ledger.record_proof_state(
        citation_urn=urn,
        proof_tier="L4_VERBATIM_EXTRACTED",
        score=98.5,
        source="local_library",
        witness_sha256="abc123sha",
        page_number=2,
    )

    # 4. Record verbatim slip
    ledger.record_verbatim_slip(
        citation_urn=urn,
        witness_sha256="abc123sha",
        coordinate="valence-v29:quote:1",
        claimed_text="unlike any living species",
        contiguous_text="Africa from Miocene ape ancestors unlike any living species.",
        status="verbatim_verified",
        page_number=2,
        char_start=120,
        char_end=178,
        rect_bbox=(50.0, 120.0, 480.0, 135.0),
    )

    summary = ledger.get_citation_summary(doc_id="valence-v29")
    assert len(summary) == 1
    item = summary[0]
    assert item["citation_urn"] == urn
    assert item["proof_tier"] == "L4_VERBATIM_EXTRACTED"
    assert item["witness_filename"] == "Almecija_2021.pdf"
    assert item["has_verbatim"] is True
    assert item["verbatim_status"] == "verbatim_verified"
