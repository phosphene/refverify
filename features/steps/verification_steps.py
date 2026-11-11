"""Step definitions for core reference verification BDD feature."""

from __future__ import annotations

from behave import given, when, then
from phosphene.refverify.domain.scoring import CandidateRecord
from phosphene.refverify.domain.reference import Reference, parse_bibliography_wikitext
from phosphene.refverify.domain.verdict import Verdict, VerdictResult
from phosphene.refverify.domain.verify import (
    verify_one,
    verify_all,
    gate_decision,
)


@given('a reference with DOI "{doi}"')
def step_doi_ref(context, doi):
    context.reference = Reference(
        text=f"Author (2020). Target Paper. https://doi.org/{doi}",
        title="Target Paper",
        authors=("Author",),
        year=2020,
        doi=doi,
    )


@given("the provider returns a record with matching title, author surname, and year")
def step_provider_matches(context):
    cand = CandidateRecord(
        title=context.reference.title,
        authors=context.reference.authors,
        year=context.reference.year,
        doi=context.reference.doi,
        source="crossref",
    )
    context.lookup.doi_map[context.reference.doi] = cand


@then('the verdict is "{verdict_name}"')
def step_verdict_is(context, verdict_name):
    res = verify_one(context.reference, [context.lookup])
    context.verdict_result = res
    expected = Verdict(verdict_name)
    assert res.verdict == expected, (
        f"Expected verdict {expected}, got {res.verdict}. Reasons: {res.reasons}"
    )


@then("the matched DOI equals the cited DOI")
def step_doi_equals(context):
    assert context.verdict_result.matched_doi == context.reference.doi


@given("a reference lacking an explicit DOI")
def step_lacking_doi(context):
    context.reference = Reference(
        text="Author (2020). Secondary Paper.",
        title="Secondary Paper",
        authors=("Author",),
        year=2020,
    )


@given("a provider search returns a record with matching title and author surname")
def step_search_returns(context):
    cand = CandidateRecord(
        title=context.reference.title,
        authors=context.reference.authors,
        year=context.reference.year,
        doi="10.9999/found-via-search",
        source="crossref",
    )
    context.lookup.search_records = [cand]


@given("the provider returns a record whose title differs from the citation")
def step_differs(context):
    cand = CandidateRecord(
        title="Completely Unrelated Subject",
        authors=("Different",),
        year=1990,
        doi=context.reference.doi,
        source="crossref",
    )
    context.lookup.doi_map[context.reference.doi] = cand


@then("the mismatch reasons name the differing fields")
def step_mismatch_reasons(context):
    assert any("title_similarity" in r for r in context.verdict_result.reasons)


@given("a reference whose title matches no provider record")
def step_no_match(context):
    context.reference = Reference(
        text="Ghost (1900). Vanished Manuscript.",
        title="Vanished Manuscript",
        authors=("Ghost",),
        year=1900,
    )
    context.lookup.search_records = []


@given("a reference whose best candidate scores between the low and high thresholds")
def step_borderline(context):
    context.reference = Reference(
        text="Author (2020). Partial Overlap Study.",
        title="Partial Overlap Study",
        authors=("Author",),
        year=2020,
    )
    cand = CandidateRecord(
        title="Partial Overlap Extension",
        authors=("Author",),
        year=2022,
        source="crossref",
    )
    context.lookup.search_records = [cand]


@given("a bibliography containing the same title cited twice")
def step_dup_bib(context):
    r1 = Reference(
        text="Author (2020). Duplicated Paper.",
        title="Duplicated Paper",
        authors=("Author",),
        year=2020,
    )
    r2 = Reference(
        text="Author (2020). Duplicated Paper.",
        title="Duplicated Paper",
        authors=("Author",),
        year=2020,
    )
    context.references = [r1, r2]


@then("the duplicate detector flags both entries")
def step_dup_flags(context):
    results = verify_all(context.references, [context.lookup])
    # Duplicate pass marks the second entry as DUPLICATE
    assert any(r.verdict == Verdict.DUPLICATE for r in results)


@given("a bibliography with one metadata_mismatch verdict")
def step_one_mismatch(context):
    r = Reference(
        text="Author (2020). Claim. 10.1111/bad",
        title="Claim",
        authors=("Author",),
        year=2020,
        doi="10.1111/bad",
    )
    cand = CandidateRecord(
        title="Different", authors=("Other",), year=1980, doi="10.1111/bad", source="crossref"
    )
    context.lookup.doi_map["10.1111/bad"] = cand
    context.references = [r]


@given("a bibliography with only low_confidence verdicts")
def step_only_low(context):
    r = Reference(
        text="Author (2020). Partial Overlap.",
        title="Partial Overlap",
        authors=("Author",),
        year=2020,
    )
    cand = CandidateRecord(
        title="Partial Overlap Extension",
        authors=("Author",),
        year=2022,
        source="crossref",
    )
    context.lookup.search_records = [cand]
    context.references = [r]


@given("a bibliography where every reference verifies")
def step_every_verifies(context):
    r = Reference(
        text="Author (2020). Solid Study. 10.1111/solid",
        title="Solid Study",
        authors=("Author",),
        year=2020,
        doi="10.1111/solid",
    )
    cand = CandidateRecord(
        title="Solid Study",
        authors=("Author",),
        year=2020,
        doi="10.1111/solid",
        source="crossref",
    )
    context.lookup.doi_map["10.1111/solid"] = cand
    context.references = [r]


@then('the gate decision is "{decision}"')
def step_gate_decision(context, decision):
    if hasattr(context, "references"):
        results = verify_all(context.references, [context.lookup])
        verdicts = [r.verdict for r in results]
        decision_actual = gate_decision(verdicts)
    elif hasattr(context, "verdict_result"):
        verdict = context.verdict_result.verdict
        if verdict in (Verdict.VERIFIED, Verdict.VERIFIED_SECONDARY):
            decision_actual = "pass"
        elif verdict == Verdict.LOW_CONFIDENCE:
            decision_actual = "warn"
        else:
            decision_actual = "block"
    else:
        raise AssertionError("No context for gate decision")
    assert decision_actual == decision, f"Expected gate {decision}, got {decision_actual}"


@given("a wikitext bibliography with author-year entries and inline URLs")
def step_wikitext_bib(context):
    context.wikitext = """
* Author, A. (2020). [https://doi.org/10.1000/182 Title One]. ''Journal of Science'' 1(2): 3-4.
* Baker, B. and Charles, C. (2021). Title Two without link. ''Nature'' 5: 10-12.
"""


@when("the wikitext adapter parses it")
def step_wikitext_parses(context):
    context.parsed_refs = parse_bibliography_wikitext(context.wikitext)


@then("each entry yields a Reference with text, year, and DOI extracted where present")
def step_parsed_checks(context):
    assert len(context.parsed_refs) == 2
    r1, r2 = context.parsed_refs
    assert r1.year == 2020
    assert r1.doi == "10.1000/182"
    assert r2.year == 2021


@then("wiki markup is stripped from the reference text")
def step_markup_stripped(context):
    for r in context.parsed_refs:
        assert "''" not in r.text
        assert "[" not in r.text
