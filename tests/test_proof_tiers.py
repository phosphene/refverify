"""Tests for ProofTier and ProofVector domain types."""

from __future__ import annotations

from phosphene.refverify.domain.proof import ProofTier, ProofVector


def test_proof_tier_ordering_and_levels():
    assert ProofTier.L0_ASSERTED.level == 0
    assert ProofTier.L4_VERBATIM_EXTRACTED.level == 4
    assert ProofTier.L4_VERBATIM_EXTRACTED > ProofTier.L1_CATALOG_RESOLVED
    assert ProofTier.L2_WITNESS_LOCKED >= ProofTier.L2_WITNESS_LOCKED
    assert ProofTier.L1_CATALOG_RESOLVED < ProofTier.L3_LOCUS_ATTESTED


def test_proof_vector_immutability():
    pv = ProofVector(
        citation_urn="urn:cts:doc#1",
        tier=ProofTier.L3_LOCUS_ATTESTED,
        score=92.0,
        source="local_library",
        witness_sha256="abc123",
        page_number=14,
    )
    assert pv.tier == ProofTier.L3_LOCUS_ATTESTED
    assert pv.page_number == 14
