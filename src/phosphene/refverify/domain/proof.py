"""Formalization of Graded Verification Proof Tiers and Vectors.

Defines the progression of empirical certainty from raw assertion to verbatim witness extraction:
- L0_ASSERTED: Unparsed authorial assertion / citation string.
- L1_CATALOG_RESOLVED: Bibliographic identity resolved via global catalog (DOI/Crossref/OpenLibrary).
- L2_WITNESS_LOCKED: Physical primary source artifact secured in vault with pinned SHA-256.
- L3_LOCUS_ATTESTED: Citation or claim located at specific page coordinate P and text window.
- L4_VERBATIM_EXTRACTED: Contiguous unit of reason extracted byte-for-byte from primary text layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProofTier(str, Enum):
    """Graded levels of empirical verification proof."""

    L0_ASSERTED = "L0_ASSERTED"
    L1_CATALOG_RESOLVED = "L1_CATALOG_RESOLVED"
    L2_WITNESS_LOCKED = "L2_WITNESS_LOCKED"
    L3_LOCUS_ATTESTED = "L3_LOCUS_ATTESTED"
    L4_VERBATIM_EXTRACTED = "L4_VERBATIM_EXTRACTED"

    @property
    def level(self) -> int:
        return int(self.value[1])

    def __ge__(self, other: ProofTier) -> bool:
        if not isinstance(other, ProofTier):
            return NotImplemented
        return self.level >= other.level

    def __gt__(self, other: ProofTier) -> bool:
        if not isinstance(other, ProofTier):
            return NotImplemented
        return self.level > other.level

    def __le__(self, other: ProofTier) -> bool:
        if not isinstance(other, ProofTier):
            return NotImplemented
        return self.level <= other.level

    def __lt__(self, other: ProofTier) -> bool:
        if not isinstance(other, ProofTier):
            return NotImplemented
        return self.level < other.level


@dataclass(frozen=True)
class ProofVector:
    """Immutable audit vector representing the empirical proof state of a citation or claim."""

    citation_urn: str
    tier: ProofTier
    score: float
    source: str
    witness_sha256: str | None = None
    witness_path: str | None = None
    page_number: int | None = None
    locus_span: tuple[int, int] | None = None
    reasons: tuple[str, ...] = ()
