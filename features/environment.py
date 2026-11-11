"""Behave environment hooks for refverify BDD."""

from __future__ import annotations

from phosphene.refverify.adapters.cache import FileCache
from phosphene.refverify.domain.scoring import CandidateRecord


class FakeLookup:
    def __init__(self) -> None:
        self.name = "fake-provider"
        self.doi_map: dict[str, CandidateRecord] = {}
        self.search_records: list[CandidateRecord] = []

    def by_doi(self, doi: str) -> CandidateRecord | None:
        return self.doi_map.get(doi)

    def search(
        self,
        title: str,
        author: str | None = None,
        year: int | None = None,
    ) -> list[CandidateRecord]:
        return self.search_records


def before_scenario(context, scenario):
    context.lookup = FakeLookup()
    context.cache = FileCache(enabled=False)
    context.reference = None
    context.result = None
    context.verdict = None
    context.glossary = {}
    context.provenance_records = []
