"""Verbatim quotation and empirical representation verification.

Extends refverify with deterministic substring and coordinate-bounded
quotation checking against primary source texts / witness corpora.
Adheres to the Nietzsche standard: the physical witness is the arbiter.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class VerbatimStatus(str, Enum):
    VERBATIM_VERIFIED = "verbatim_verified"
    VERBATIM_MUTATED = "verbatim_mutated"
    WITNESS_NOT_FOUND = "witness_not_found"


@dataclass(frozen=True)
class VerbatimResult:
    status: VerbatimStatus
    coordinate: str
    target_citation: str
    claimed_text: str
    matched_span: tuple[int, int] | None
    divergence_reason: str | None = None


def normalize_verbatim_text(text: str) -> str:
    """Normalize typography without altering semantics or tokens.

    Strips soft hyphens, translates curly quotes/dashes, strips outer quotes,
    and collapses internal whitespace.
    """
    t = text.replace("\xad", "")  # soft hyphen
    t = t.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    t = t.replace("—", "--").replace("–", "-")
    # Strip leading/trailing quotation marks from the excerpt
    t = t.strip().strip('"').strip("'")
    # Normalize unicode whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


def verify_verbatim_quote(
    claimed_text: str,
    witness_text: str,
    coordinate: str = "doc:sec:quote",
    target_citation: str = "",
) -> VerbatimResult:
    """Check whether claimed_text exists verbatim within witness_text.

    Supports ellipsis (...) splitting: all sub-segments must occur
    in strictly monotonic order within witness_text.
    """
    clean_witness = normalize_verbatim_text(witness_text)
    clean_claim = normalize_verbatim_text(claimed_text)

    if not clean_witness:
        return VerbatimResult(
            status=VerbatimStatus.WITNESS_NOT_FOUND,
            coordinate=coordinate,
            target_citation=target_citation,
            claimed_text=claimed_text,
            matched_span=None,
            divergence_reason="witness_text_empty",
        )

    # Check for ellipsis-delimited spans
    parts = [p.strip() for p in re.split(r"\.{3,}|…", clean_claim) if p.strip()]

    if not parts:
        return VerbatimResult(
            status=VerbatimStatus.VERBATIM_MUTATED,
            coordinate=coordinate,
            target_citation=target_citation,
            claimed_text=claimed_text,
            matched_span=None,
            divergence_reason="empty_claim",
        )

    last_idx = 0
    start_span: int | None = None
    end_span: int | None = None

    for idx, part in enumerate(parts):
        pos = clean_witness.find(part, last_idx)
        if pos == -1:
            return VerbatimResult(
                status=VerbatimStatus.VERBATIM_MUTATED,
                coordinate=coordinate,
                target_citation=target_citation,
                claimed_text=claimed_text,
                matched_span=None,
                divergence_reason=f"subspan_not_found: {part[:40]}...",
            )
        if idx == 0:
            start_span = pos
        end_span = pos + len(part)
        last_idx = end_span

    return VerbatimResult(
        status=VerbatimStatus.VERBATIM_VERIFIED,
        coordinate=coordinate,
        target_citation=target_citation,
        claimed_text=claimed_text,
        matched_span=(start_span or 0, end_span or 0),
        divergence_reason=None,
    )
