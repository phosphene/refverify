"""Companion markdown materialization for audit-ready verbatim provenance slips.

Generates reproducible .provenance.md artifacts recording proof tiers, witness SHA-256,
page coordinates, claimed text, and the zero-ellipses contiguous primary witness extract.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from phosphene.refverify.domain.proof import ProofTier


@dataclass(frozen=True)
class ProvenanceSlip:
    """Provenance slip representing an empirical proof and extraction artifact."""

    provenance_id: str
    citation_urn: str
    doc_id: str
    claimed_text: str
    contiguous_witness_text: str
    proof_tier: ProofTier
    witness_sha256: str
    witness_filename: str
    page_number: int | None = None
    locus_coordinate: str | None = None
    char_span: tuple[int, int] | None = None
    bounding_box: tuple[float, float, float, float] | None = None
    status: str = "VERIFIED_REPRODUCIBLE"
    verified_at: str | None = None

    def to_markdown(self) -> str:
        """Render the provenance slip to canonical Markdown format with YAML frontmatter."""
        ts = self.verified_at or datetime.now(timezone.utc).isoformat()
        span_str = f"[{self.char_span[0]}, {self.char_span[1]}]" if self.char_span else "null"
        bbox_str = f"[{self.bounding_box[0]:.2f}, {self.bounding_box[1]:.2f}, {self.bounding_box[2]:.2f}, {self.bounding_box[3]:.2f}]" if self.bounding_box else "null"

        return f"""---
provenance_id: {self.provenance_id}
citation_urn: {self.citation_urn}
doc_id: {self.doc_id}
proof_tier: {self.proof_tier.value}
witness_sha256: {self.witness_sha256}
witness_filename: {self.witness_filename}
page_number: {self.page_number if self.page_number is not None else 'null'}
locus_coordinate: {self.locus_coordinate or 'null'}
char_span: {span_str}
bounding_box: {bbox_str}
status: {self.status}
verified_at: {ts}
verifier: refverify-v0.2.0
---

# Verbatim Citation Provenance Slip

### Claimed In-Text Quote
> {self.claimed_text}

### Primary Witness Extracted Unit (Zero-Ellipses Contiguous Text)
{self.contiguous_witness_text}
"""

    def save(self, output_path: Path | str) -> Path:
        """Write the markdown provenance slip to disk."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.to_markdown(), encoding="utf-8")
        return p
