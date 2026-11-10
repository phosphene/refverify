"""Verdict enum + result value object. Pure."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field

# Verdict rubric (imi-pipeline#22; upstream vocabulary where compatible):
#   verified            -- cited metadata matches the provider record
#   verified-secondary  -- no DOI cited; strong title/author match
#   metadata_mismatch   -- identifier resolves but metadata disagrees
#   not_found           -- no provider record matches
#   low_confidence      -- borderline score between the two thresholds
#   duplicate           -- same work cited under two entries


@enum.unique
class Verdict(enum.StrEnum):
    VERIFIED = "verified"
    VERIFIED_SECONDARY = "verified-secondary"
    METADATA_MISMATCH = "metadata_mismatch"
    NOT_FOUND = "not_found"
    LOW_CONFIDENCE = "low_confidence"
    DUPLICATE = "duplicate"


@dataclass(frozen=True, slots=True)
class VerdictResult:
    """Outcome of verifying one Reference against the providers."""

    verdict: Verdict
    score: float
    reasons: tuple[str, ...] = field(default_factory=tuple)
    matched_title: str = ""
    matched_doi: str | None = None
    matched_source: str = ""  # provider name
