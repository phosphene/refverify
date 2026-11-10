# refverify

Scholarly reference verification and quality-control gate.

 parses bibliographic entries from academic manuscripts (Markdown, text) and wikitext, resolving citations against primary metadata registries (Crossref, OpenAlex, Semantic Scholar, arXiv) with an offline-first caching layer.

## Architecture

- **Domain:** Pure verification, scoring, deduplication, and gate decisions. Zero I/O or network dependencies.
- **Ports & Adapters:** Hexagonal lookup client protocol with thin HTTP adapters (Crossref, OpenAlex, Semantic Scholar, arXiv) and local disk cache.
- **Specification:** Formal Gherkin feature specs in .

## Installation

Defaulting to user installation because normal site-packages is not writeable

Or with :



## Usage

Verify a raw bibliography or manuscript section:



Verify Wikipedia/Observatory wikitext pages:



Run without cache:



## Gate Decisions

- **PASS:** All citations resolve with high metadata confidence ($\ge 0.85$ title similarity, matching author and publication year).
- **WARN:** Low-confidence matches or missing DOI fallbacks that require human verification.
- **BLOCK:** Metadata mismatch (wrong year/author/title), duplicate citation, or unresolvable reference.

## License

MIT
