"""OpenLibrary provider adapter -- book/monograph resolution port.

Implements LookupClient via the OpenLibrary search and works API.
Resolves academic books, university press volumes, and edited collections
(e.g., Boyd & Richerson 1985, Cavalli-Sforza & Feldman 1981) to eliminate
false-negative NOT_FOUND verdicts.
"""

from __future__ import annotations

import re
import urllib.parse
from typing import Any

import httpx

from phosphene.refverify.adapters.cache import FileCache
from phosphene.refverify.domain.scoring import CandidateRecord

USER_AGENT = "refverify/0.1 (observatory-wiki; mailto:refverify@observatory.wiki)"


class OpenLibraryClient:
    """https://openlibrary.org -- book catalog search."""

    name = "openlibrary"

    def __init__(
        self,
        client: httpx.Client | None = None,
        cache: FileCache | None = None,
    ) -> None:
        self.client = client or httpx.Client(
            base_url="https://openlibrary.org",
            headers={"User-Agent": USER_AGENT},
            timeout=10.0,
        )
        self.cache = cache

    def by_doi(self, doi: str) -> CandidateRecord | None:
        """OpenLibrary is book/ISBN oriented; DOI lookup not supported directly."""
        return None

    def search(
        self, title: str, author: str | None = None, year: int | None = None
    ) -> list[CandidateRecord]:
        """Search books by title and optional author."""
        clean_title = title.strip()
        if not clean_title:
            return []

        key = f"openlibrary:search:{clean_title.lower()}:{str(author).lower()}:{year}"
        if self.cache is not None:
            hit = self.cache.get(key)
            if hit is not None:
                return [CandidateRecord(**c) for c in hit]

        params: dict[str, Any] = {
            "title": clean_title[:200],
            "limit": 5,
        }
        if author:
            # Strip initials / commas to search surname or name tokens
            clean_author = re.sub(r"[,\.]", " ", author).strip()
            params["author"] = clean_author

        try:
            r = self.client.get("/search.json", params=params)
            if r.status_code == 404:
                return []
            r.raise_for_status()
            data = r.json()
        except httpx.HTTPError:
            return []

        docs = data.get("docs", [])
        candidates: list[CandidateRecord] = []
        for doc in docs:
            t = doc.get("title", "")
            authors = tuple(doc.get("author_name", []))
            first_year = doc.get("first_publish_year")
            # If ISBN exists, note it in venue or candidate
            isbn_list = doc.get("isbn", [])
            isbn = isbn_list[0] if isbn_list else ""
            cand = CandidateRecord(
                title=t,
                authors=authors,
                year=int(first_year) if first_year else None,
                doi=None,
                venue=f"ISBN: {isbn}" if isbn else "",
                source=self.name,
            )
            candidates.append(cand)

        if self.cache is not None:
            # Store dict representations in file cache
            self.cache.set(
                key,
                [
                    {
                        "title": c.title,
                        "authors": list(c.authors),
                        "year": c.year,
                        "doi": c.doi,
                        "venue": c.venue,
                        "source": c.source,
                    }
                    for c in candidates
                ],
            )

        return candidates
