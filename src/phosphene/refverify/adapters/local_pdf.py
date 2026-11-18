"""Local PDF witness index adapter and offline lookup.

Implements LookupClient and WitnessClient against a directory of local PDF primary sources.
Uses PyMuPDF (fitz) for deterministic text layer extraction and caching.
Zero network IO, zero rate limits. Priority 0 in lookup chains.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from phosphene.refverify.domain.scoring import CandidateRecord, title_similarity, author_token_overlap

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

_DOI_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)")


@dataclass(frozen=True)
class LocalPdfMetadata:
    """Metadata record for a locally indexed PDF witness."""

    sha256: str
    file_path: str
    filename: str
    title: str
    authors: tuple[str, ...]
    year: int | None
    doi: str | None
    page_count: int


class LocalPdfWitnessIndex:
    """Indexed local repository of PDF primary sources."""

    name = "local_library"

    def __init__(
        self,
        pdf_dir: Path | str,
        index_cache_path: Path | str | None = None,
    ) -> None:
        self.pdf_dir = Path(pdf_dir)
        self.index_cache_path = Path(index_cache_path) if index_cache_path else self.pdf_dir / ".refverify_index.json"
        self._entries: list[LocalPdfMetadata] = []
        self._doi_map: dict[str, LocalPdfMetadata] = {}
        self._sha_map: dict[str, LocalPdfMetadata] = {}
        self._load_or_build_index()

    def _load_or_build_index(self) -> None:
        if self.index_cache_path.exists():
            try:
                data = json.loads(self.index_cache_path.read_text(encoding="utf-8"))
                for item in data.get("entries", []):
                    entry = LocalPdfMetadata(
                        sha256=item["sha256"],
                        file_path=item["file_path"],
                        filename=item["filename"],
                        title=item["title"],
                        authors=tuple(item["authors"]),
                        year=item["year"],
                        doi=item["doi"],
                        page_count=item["page_count"],
                    )
                    self._entries.append(entry)
                    if entry.doi:
                        self._doi_map[entry.doi.lower()] = entry
                    self._sha_map[entry.sha256] = entry
                return
            except Exception:
                pass
        self.rebuild_index()

    def rebuild_index(self) -> None:
        """Scan directory and index all PDFs."""
        if not self.pdf_dir.is_dir():
            return

        entries: list[LocalPdfMetadata] = []
        doi_map: dict[str, LocalPdfMetadata] = {}
        sha_map: dict[str, LocalPdfMetadata] = {}

        for p in self.pdf_dir.glob("*.pdf"):
            try:
                entry = self._index_pdf_file(p)
                if entry:
                    entries.append(entry)
                    if entry.doi:
                        doi_map[entry.doi.lower()] = entry
                    sha_map[entry.sha256] = entry
            except Exception:
                continue

        self._entries = entries
        self._doi_map = doi_map
        self._sha_map = sha_map

        # Save cache
        try:
            cache_payload = {
                "version": 1,
                "entries": [
                    {
                        "sha256": e.sha256,
                        "file_path": e.file_path,
                        "filename": e.filename,
                        "title": e.title,
                        "authors": list(e.authors),
                        "year": e.year,
                        "doi": e.doi,
                        "page_count": e.page_count,
                    }
                    for e in entries
                ],
            }
            self.index_cache_path.write_text(json.dumps(cache_payload, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _index_pdf_file(self, path: Path) -> LocalPdfMetadata | None:
        raw_bytes = path.read_bytes()
        sha = hashlib.sha256(raw_bytes).hexdigest()

        # Heuristic 1: Parse from standardized filename e.g. Author_Year_Title.pdf
        filename = path.name
        stem = path.stem
        fn_author: str | None = None
        fn_year: int | None = None
        fn_title: str | None = None

        m = re.match(r"^([A-Za-z\-]+)_(\d{4})_(.+)$", stem)
        if m:
            fn_author, y_str, t_part = m.groups()
            fn_year = int(y_str)
            fn_title = t_part.replace("_", " ")

        doc_doi: str | None = None
        page_count = 0
        extracted_text_p1 = ""

        if fitz is not None:
            try:
                doc = fitz.open(stream=raw_bytes, filetype="pdf")
                page_count = len(doc)
                if page_count > 0:
                    extracted_text_p1 = doc[0].get_text()
                    doi_match = _DOI_RE.search(extracted_text_p1)
                    if doi_match:
                        # Clean trailing punctuation from regex match
                        doc_doi = doi_match.group(1).rstrip(".,;)>")
                doc.close()
            except Exception:
                pass

        title = fn_title or stem.replace("_", " ")
        authors = (fn_author,) if fn_author else ()
        year = fn_year

        return LocalPdfMetadata(
            sha256=sha,
            file_path=str(path.resolve()),
            filename=filename,
            title=title,
            authors=authors,
            year=year,
            doi=doc_doi,
            page_count=page_count,
        )

    def by_doi(self, doi: str) -> CandidateRecord | None:
        """Exact DOI lookup in local library."""
        norm_doi = doi.lower().strip()
        hit = self._doi_map.get(norm_doi)
        if hit:
            return CandidateRecord(
                title=hit.title,
                authors=hit.authors,
                year=hit.year,
                doi=hit.doi,
                source=self.name,
            )
        return None

    def search(
        self, title: str, author: str | None = None, year: int | None = None
    ) -> list[CandidateRecord]:
        """Search local PDF corpus by title, author, and year."""
        candidates: list[tuple[float, LocalPdfMetadata]] = []

        for entry in self._entries:
            sim = title_similarity(title, entry.title)
            # If title similarity is promising
            if sim >= 0.40:
                score = sim
                if year and entry.year:
                    if entry.year == year:
                        score += 0.2
                    elif abs(entry.year - year) == 1:
                        score += 0.1
                if author and entry.authors:
                    overlap = author_token_overlap(tuple(entry.authors), (author,))
                    score += overlap * 0.2
                candidates.append((score, entry))

        candidates.sort(key=lambda x: x[0], reverse=True)
        results: list[CandidateRecord] = []
        for s, entry in candidates[:5]:
            results.append(
                CandidateRecord(
                    title=entry.title,
                    authors=entry.authors,
                    year=entry.year,
                    doi=entry.doi,
                    source=self.name,
                )
            )
        return results

    def get_full_text(self, identifier: str) -> str | None:
        """Get full plain text of an indexed PDF by DOI, filename, or SHA-256."""
        if fitz is None:
            return None

        entry: LocalPdfMetadata | None = None
        norm_id = identifier.lower().strip()
        if norm_id in self._doi_map:
            entry = self._doi_map[norm_id]
        elif identifier in self._sha_map:
            entry = self._sha_map[identifier]
        else:
            for e in self._entries:
                if e.filename == identifier or Path(e.file_path).name == identifier:
                    entry = e
                    break

        if not entry:
            return None

        try:
            doc = fitz.open(entry.file_path)
            pages = [doc[i].get_text() for i in range(len(doc))]
            doc.close()
            return "\n\n".join(pages)
        except Exception:
            return None

    def search_page_loci(self, identifier: str, query: str) -> list[int]:
        """Return 1-indexed page numbers containing query substring in PDF."""
        if fitz is None:
            return []

        entry: LocalPdfMetadata | None = None
        norm_id = identifier.lower().strip()
        if norm_id in self._doi_map:
            entry = self._doi_map[norm_id]
        else:
            for e in self._entries:
                if e.filename == identifier or Path(e.file_path).name == identifier:
                    entry = e
                    break

        if not entry:
            return []

        clean_q = query.strip().lower()
        matching_pages: list[int] = []
        try:
            doc = fitz.open(entry.file_path)
            for page_idx in range(len(doc)):
                page_text = doc[page_idx].get_text().lower()
                if clean_q in page_text:
                    matching_pages.append(page_idx + 1)
            doc.close()
        except Exception:
            pass

        return matching_pages
