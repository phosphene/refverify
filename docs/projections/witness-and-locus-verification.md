---
uri: phosphene.tooling/refverify/docs/projections/witness-and-locus-verification
owner: edphos
status: proposed
created: 2026-11-17
updated: 2026-11-17
namespace: phosphene.tooling.refverify.projections
coordinates:
  - :projection.capacity/witness-verification
  - :projection.capacity/locus-checking
  - :projection.capacity/local-pdf-provider
  - :projection.tier/internal-software-engineering
  - :projection.tier/institutional-knowledge-wikis
  - :projection.domain/corpus-ground-truth
  - :projection.domain/textual-philology
builds-on:
  - phosphene.tooling/refverify/docs/architecture
  - phosphene.tooling/refverify/docs/citation-verification
  - phosphene.tooling/refverify/docs/projections/general-capacities
converges-with:
  - team/platform/doc-standards
  - meta/reference/hard-rules
abstract: |
  Specification decomposing refverify's Phase 2 evolution from catalog-level
  identity resolution (Layer 1: DOIs, Crossref, OpenAlex) to primary witness
  and locus verification (Layer 2: Local PDF indexing, text-layer extraction,
  exact span/quotation verification, and table/data collation). Grounded in
  classical philological collation and Phosphene deterministic verification principles.
---

# Specification: Primary Witness & Locus Verification (Layer 2)

> **Coordinate Namespace:** `phosphene.tooling.refverify.projections.witness.*`  
> Direct verification of citations and claims against physical text witnesses (local PDF/EPUB library and authoritative registries).

---

## 1. Problem Statement & Motivation

Existing academic AI tooling (Consensus, Elicit, SciSpace, PaperOrchestra) approaches literature verification through citation graph traversal, abstract scraping, and sentiment aggregation. This introduces a structural vulnerability: **the cascade failure of secondary transmission**. When a secondary review misinterprets an empirical finding, misattributes a date, or cites a phantom volume number, consensus metrics amplify the error as "consensus."

`phosphene-refverify` Layer 1 established deterministic **catalog-level identity hygiene**:
1. Parsing in-text citations and bibliography blocks via AST walkers (`phosphene-mdrag`).
2. Exact matching against bibliographic authorities (Crossref, OpenAlex, arXiv) via a pure `LookupClient` protocol.
3. Scoring title similarity, author overlap, and publication year agreement.

However, Layer 1 leaves a critical epistemic gap: **proving a cited paper exists does not prove the paper contains the asserted claim or quotation.**

Layer 2 extends `refverify` from **catalog existence** to **witness collation**—treating the text as a physical empirical artifact with an immutable token sequence.

---

## 2. Architectural Invariants

In accordance with Phosphene Method standards:

1. **Deterministic Execution:** No LLM inference in the critical verification loop. Scoring and matching must be computable via standard string collation, regular expressions, and interval arithmetic.
2. **Local Vault Precedence (Vault First, Registries Second):** Local primary source files (`acquired/*.pdf`, `acquired/*.epub`) represent ground truth. If an item exists in the local archive, verification must resolve locally without network IO.
3. **Immutability & Integrity Hashing:** Text witnesses are indexed by cryptographic digest (SHA-256) and canonical DOI. Local file paths and human-assigned filenames are treated as untrusted metadata.
4. **Normalized Token Collation:** String comparisons between claims and witnesses must account for typography (curly quotes, dashes, soft hyphens, OCR ligatures) without altering semantic token order.

---

## 3. System Architecture & Component Model

```
                    ┌───────────────────────────────┐
                    │ Document Under Audit (.md)    │
                    └──────────────┬────────────────┘
                                   │
                                   ▼
                    ┌───────────────────────────────┐
                    │ Readers & In-Text AST Parser  │
                    │   (Claims, Quotes, Citations) │
                    └──────────────┬────────────────┘
                                   │
                    ┌──────────────┴────────────────┐
                    │                               │
                    ▼                               ▼
       [Layer 1: Identity/Catalog]      [Layer 2: Witness & Locus]
       ┌────────────────────────┐       ┌────────────────────────┐
       │ LookupClient Protocol  │       │ WitnessClient Protocol │
       ├────────────────────────┤       ├────────────────────────┤
       │ • CrossrefAdapter      │       │ • LocalPdfWitnessIndex │
       │ • OpenAlexAdapter      │       │ • OpenLibraryAdapter   │
       │ • ArxivAdapter         │       │ • PubMedXmlAdapter     │
       └────────────────────────┘       └───────────┬────────────┘
                                                    │
                                                    ▼
                                        ┌────────────────────────┐
                                        │ Verbatim & Locus Engine│
                                        ├────────────────────────┤
                                        │ • Quote Monotonic Span │
                                        │ • Numerical Assertion  │
                                        │ • Stratum/Interval Math│
                                        └───────────┬────────────┘
                                                    │
                                                    ▼
                                        ┌────────────────────────┐
                                        │ WitnessAuditLedger     │
                                        │ (Exit Code: 0 / 2)     │
                                        └────────────────────────┘
```

---

## 4. Component Decomposition

### 4.1. Local Library Witness Index (`LocalPdfWitnessIndex`)
An adapter implementing `LookupClient` and `WitnessClient` fronting the local PDF repository (`acquired/`):

* **Index Schema (SQLite / JSON cache):**
  * `sha256`: Unique file hash.
  * `doi`: Extracted canonical DOI from header/metadata.
  * `title`: Normalized title from PDF metadata and page 1–2 text heuristics.
  * `authors`: Extracted author surnames.
  * `year`: Extracted publication year.
  * `fulltext_path`: Path to cached plain text extracted via `pymupdf` (`fitz`).
* **Lookup Resolution:**
  * When `by_doi(doi)` is invoked: exact lookup against local index.
  * When `search(title, author, year)` is invoked: token similarity against indexed local papers.
  * If hit: returns `CandidateRecord(..., source="local_library")` with a priority weight that short-circuits external HTTP requests.

### 4.2. Extended Authority Adapters (Books & Primary Catalogs)
To eliminate false-negative `NOT_FOUND` verdicts on standard academic books and monographs:

* **`OpenLibraryClient` / `GoogleBooksClient`:**
  * Implements `LookupClient`.
  * Resolves ISBNs, university press titles, and multi-author edited volumes (e.g., Boyd & Richerson 1985, Cavalli-Sforza & Feldman 1981).
* **`PubMedXmlClient`:**
  * Direct resolution of biomedical literature via Europe PMC / NCBI e-utils for open-access papers, returning exact XML full text for locus checking.

### 4.3. Verbatim Quote & Locus Checker (`domain/verbatim.py`)
Building on the existing `verify_verbatim_quote()` implementation:

* **Monotonic Subspan Search:** For blockquotes containing ellipses (`...` or `…`), verifies that every sub-segment exists in strictly increasing character offsets within the witness text layer.
* **OCR & Hyphenation Normalization:**
  * Collapses discretionary linebreaks (`word-\nbreak` -> `wordbreak`).
  * Normalizes Unicode quotes, ligatures (`ﬁ` -> `fi`, `ﬂ` -> `fl`), and whitespace.
* **Locus Reporting:**
  * Returns `VerbatimResult(status, coordinate, matched_span=(start, end), page_number)`.

### 4.4. Numerical & Stratigraphic Assertion Verifier
* **Extraction:** AST reader identifies numerical claims co-located with citations (e.g., `Danuvius guggenmosi (11.6 Ma, Bavaria) (Böhme et al., 2019)`).
* **Locus Check:** Asserts that the string `11.6` occurs within a ±200 token window of `Danuvius` inside the Böhme 2019 witness text.

---

## 5. Phased Implementation Roadmap for Refverify Team

| Phase | Milestone | Deliverable |
|---|---|---|
| **Phase 2.1** | Plain-Text & APA Parser | Add `parse_plain_bibliography()` to `phosphene.refverify.domain.reference` supporting APA, Chicago, and unlinked reference strings. |
| **Phase 2.2** | Local Vault Adapter | Implement `LocalPdfWitnessIndex` using PyMuPDF to index local PDF corpora and register it as Priority 0 in `default_chain()`. |
| **Phase 2.3** | Book Authority Adapter | Implement `OpenLibraryClient` for ISBN/book monograph resolution to clear false-positive book `NOT_FOUND`s. |
| **Phase 2.4** | Locus & Quote CLI Mode | Expose `--verify-quotes` on `phosphene.refverify` CLI to cross-examine extracted markdown blockquotes against resolved witness texts. |

---

## 6. Verification & Falsifiability

1. **Pure Unit Suite:** Mock `WitnessClient` fixtures verifying monotonic subspan matching, OCR ligature unfolding, and out-of-order ellipsis failure modes without filesystem IO.
2. **Acceptance Benchmark (Valence Drive Monograph v29):**
   * Target: `work/marsyas6/papers/valence-ingress/monograph-v29-text.md`.
   * Corpus: `work/marsyas6/papers/valence-ingress/acquired/*.pdf` (1,048 witnesses).
   * Success criteria:
     * Catch all known mislabeled/hallucinated items (`balcarcel_2022`, `Gjoen_2023`, `Lesch_2022`).
     * Achieve 0 false-positive `NOT_FOUND`s on real books and papers.
     * Verify all 14 in-text blockquotes against witness text layers.
