"""Tests for LocalPdfWitnessIndex adapter."""

from __future__ import annotations

import fitz
from pathlib import Path

from phosphene.refverify.adapters.local_pdf import LocalPdfWitnessIndex


def _create_sample_pdf(path: Path, title: str, author: str, content: str, doi: str | None = None):
    doc = fitz.open()
    page = doc.new_page()
    text = f"{title}\n{author}\n\n{content}"
    if doi:
        text += f"\nDOI: {doi}"
    page.insert_text((50, 50), text)
    doc.save(str(path))
    doc.close()


def test_local_pdf_indexing_and_lookup(tmp_path: Path):
    pdf_dir = tmp_path / "acquired"
    pdf_dir.mkdir()

    # Create dummy PDFs matching naming conventions
    p1 = pdf_dir / "Begun_2015_Real_Planet_of_the_Apes.pdf"
    _create_sample_pdf(
        p1,
        title="The Real Planet of the Apes",
        author="David R. Begun",
        content="Fossil hominoids show remarkable diversity across the Miocene.",
        doi="10.1515/9781400874156",
    )

    p2 = pdf_dir / "Bohme_2019_Miocene_ape_Danuvius_guggenmosi_Nature.pdf"
    _create_sample_pdf(
        p2,
        title="A new Miocene ape and locomotion in the ancestor of great apes and humans",
        author="Madelaine Böhme",
        content="Danuvius guggenmosi provides evidence for extended limb clambering.",
        doi="10.1038/s41586-019-1731-0",
    )

    index = LocalPdfWitnessIndex(pdf_dir=pdf_dir)
    assert len(index._entries) == 2

    # Exact DOI hit
    hit_doi = index.by_doi("10.1038/s41586-019-1731-0")
    assert hit_doi is not None
    assert hit_doi.source == "local_library"
    assert hit_doi.doi == "10.1038/s41586-019-1731-0"

    # Search by title & author
    search_hits = index.search(title="Real Planet of the Apes", author="Begun", year=2015)
    assert len(search_hits) >= 1
    assert "Real Planet of the Apes" in search_hits[0].title

    # Full text retrieval
    full_text = index.get_full_text(p1.name)
    assert full_text is not None
    assert "Fossil hominoids show remarkable diversity" in full_text

    # Page locus search
    pages = index.search_page_loci(p2.name, "clambering")
    assert pages == [1]

    # Persistent index cache works
    assert index.index_cache_path.exists()
    index_reloaded = LocalPdfWitnessIndex(pdf_dir=pdf_dir)
    assert len(index_reloaded._entries) == 2
