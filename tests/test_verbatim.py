"""Tests for verbatim quotation verification."""

from __future__ import annotations

from phosphene.refverify.domain.verbatim import (
    verify_verbatim_quote,
    VerbatimStatus,
    normalize_verbatim_text,
)

FARADAY_WITNESS = """
By magnetic curves, I mean the lines of magnetic forces, however produced by the magnet or the electric current,
which would be depicted on surfaces by the use of iron filings; or towards which a very small magnetic needle
would form a tangent. The nature of these lines has been discussed by various philosophers.
"""


def test_verbatim_exact_match():
    claim = "By magnetic curves, I mean the lines of magnetic forces, however produced by the magnet or the electric current"
    res = verify_verbatim_quote(claim, FARADAY_WITNESS, coordinate="doc:faraday:p1:quote1")
    assert res.status == VerbatimStatus.VERBATIM_VERIFIED
    assert res.matched_span is not None
    assert res.divergence_reason is None


def test_verbatim_curly_quote_and_whitespace_normalization():
    claim = "“By magnetic curves,   I mean the lines of magnetic forces”"
    res = verify_verbatim_quote(claim, FARADAY_WITNESS)
    assert res.status == VerbatimStatus.VERBATIM_VERIFIED


def test_verbatim_ellipsis_monotonic():
    claim = "By magnetic curves ... towards which a very small magnetic needle would form a tangent."
    res = verify_verbatim_quote(claim, FARADAY_WITNESS)
    assert res.status == VerbatimStatus.VERBATIM_VERIFIED


def test_verbatim_mutated_text_fails():
    # LLM smoothing: changing "lines of magnetic forces" to "lines of magnetic energy"
    claim = "By magnetic curves, I mean the lines of magnetic energy, however produced"
    res = verify_verbatim_quote(claim, FARADAY_WITNESS)
    assert res.status == VerbatimStatus.VERBATIM_MUTATED
    assert "subspan_not_found" in res.divergence_reason


def test_verbatim_empty_witness():
    res = verify_verbatim_quote("Some claim", "")
    assert res.status == VerbatimStatus.WITNESS_NOT_FOUND
