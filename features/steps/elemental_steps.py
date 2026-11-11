"""Step definitions for hypothetico-axiomatic elemental verification."""

from __future__ import annotations

from behave import given, when, then
from phosphene.refverify.domain.scoring import CandidateRecord, score_match
from phosphene.refverify.domain.reference import from_wikitext_entry
from phosphene.refverify.domain.verdict import Verdict, VerdictResult


@given("an initialized hermetic verification apparatus with offline cache")
def step_init(context):
    assert context.lookup is not None
    assert context.cache is not None


@given('a domain glossary review for "{domain}"')
def step_glossary(context, domain):
    context.current_domain = domain
    for row in context.table:
        term = row["Term"].strip()
        commitment = row["Inferential Commitment"].strip()
        context.glossary[term] = commitment


@given("an empirical citation from early electrical study")
@given("an empirical citation from geometry")
@given("an empirical citation from chemistry")
@given("an empirical citation from geology")
@given("an empirical citation from elemental biology")
def step_citation(context):
    text = context.text.strip()
    lines = text.split("\n")
    first_line = lines[0].strip()
    context.reference = from_wikitext_entry(first_line)


@given("the registry record matches")
@given("the registry record has been entity-swapped")
def step_registry(context):
    data = {row["Field"].strip(): row["Value"].strip() for row in context.table}
    authors = tuple(a.strip() for a in data["author"].split(","))
    context.candidate = CandidateRecord(
        title=data["title"],
        authors=authors,
        year=int(data["year"]) if "year" in data else None,
        doi=data.get("doi"),
        source=data.get("source", "crossref"),
    )


@when("the citation is scored against the registry record")
def step_score(context):
    score, reasons = score_match(context.reference, context.candidate)
    context.score = score
    context.reasons = reasons

    if score >= 80.0:
        verdict = Verdict.VERIFIED
    elif score >= 55.0:
        verdict = Verdict.LOW_CONFIDENCE
    else:
        verdict = Verdict.METADATA_MISMATCH

    context.verdict_result = VerdictResult(
        verdict=verdict,
        score=score,
        reasons=tuple(reasons),
        matched_title=context.candidate.title,
        matched_doi=context.candidate.doi,
        matched_source=context.candidate.source,
    )


@then("the composite match score is at least {min_score:f}")
def step_min_score(context, min_score):
    assert context.score >= min_score, (
        f"Score {context.score} is below expected min {min_score}. Reasons: {context.reasons}"
    )


@then("the composite match score is below {max_score:f}")
def step_below_score(context, max_score):
    assert context.score < max_score, (
        f"Score {context.score} is not below {max_score}. Reasons: {context.reasons}"
    )


@then("the composite match score is {exact_score:f}")
def step_exact_score(context, exact_score):
    assert abs(context.score - exact_score) < 0.01, (
        f"Score {context.score} != {exact_score}. Reasons: {context.reasons}"
    )


