"""Step definitions for AST block verbatim quotation verification."""

from __future__ import annotations

import re
from behave import given, when, then
from phosphene.refverify.domain.verbatim import (
    verify_verbatim_quote,
    VerbatimStatus,
    VerbatimResult,
)


@given('a canonical primary witness text for "{witness_label}"')
def step_given_witness(context, witness_label):
    context.witness_label = witness_label
    context.witness_text = context.text.strip()


@given('an mdrag blockquote block with coordinate "{coord}"')
def step_given_block(context, coord):
    context.coordinate = coord
    raw = context.text.strip()
    # Strip Markdown blockquote '>' prefixes to simulate AST content extraction
    lines = []
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith(">"):
            line = line.lstrip(">").strip()
        lines.append(line)
    context.claimed_text = " ".join(lines)


@when("the block is verified against the primary witness")
def step_verify_block(context):
    context.verbatim_result = verify_verbatim_quote(
        claimed_text=context.claimed_text,
        witness_text=context.witness_text,
        coordinate=context.coordinate,
        target_citation=getattr(context, "witness_label", ""),
    )


@then('the verbatim status is "{expected_status}"')
def step_status_check(context, expected_status):
    expected = VerbatimStatus(expected_status)
    assert context.verbatim_result.status == expected, (
        f"Expected {expected}, got {context.verbatim_result.status}. Divergence: {context.verbatim_result.divergence_reason}"
    )


@then("the matched span covers the verified characters")
def step_span_covers(context):
    assert context.verbatim_result.matched_span is not None
    start, end = context.verbatim_result.matched_span
    assert end > start


@then("the divergence reason indicates a missing subspan")
def step_divergence_indicates(context):
    assert context.verbatim_result.divergence_reason is not None
    assert "subspan_not_found" in context.verbatim_result.divergence_reason
