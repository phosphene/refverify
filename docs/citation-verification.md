---
uri: phosphene.tooling/refverify/docs/citation-verification
owner: edphos
status: canonical
created: 2026-11-10
updated: 2026-11-10
namespace: phosphene.tooling.refverify
coordinates:
  - :refverify.apparatus/citations
  - :refverify.apparatus/scoring
  - :refverify.apparatus/gates
builds-on:
  - phosphene.tooling/refverify/docs/architecture
  - phosphene.tooling/refverify/docs/mdrag-and-frontmatters-innovations
converges-with:
  - phosphene.standards/scientific-documentation
abstract: |
  Comprehensive specification of the scholarly reference verification apparatus.
  Details the multi-registry reconciliation process across Crossref, OpenAlex,
  Semantic Scholar, and arXiv; defines the weighted composite scoring algorithm;
  and formalizes the PASS, WARN, and BLOCK publication gate criteria.
---

# Scholarly Citation Verification — Mechanics, Scoring & Publication Gates

> **Coordinate:** `:refverify.apparatus/citations`  
> Verifying the scholarly apparatus: from unstructured citation strings to high-confidence epistemic grounding.

---

## 1. The Verification Objective

The scholarly citation is the fundamental atomic unit of epistemic provenance in scientific publishing.
A flawed apparatus—containing phantom citations, hallucinated DOIs, mismatched authors, or unverified
preprints masquerading as peer-reviewed publications—compromises the entire manuscript.

`refverify` formalizes the process of citation verification into a deterministic, multi-registry pipeline:
1. **Extraction & Normalization:** Parsing citations from Markdown, Word (`.docx`), plain text, or Wikitext `<ref>` templates.
2. **Identifier & Search Dispatch:** Resolving explicit DOIs/arXiv IDs or executing fuzzy title/author queries.
3. **Multi-Registry Reconciliation:** Querying Crossref, OpenAlex, Semantic Scholar, and arXiv.
4. **Empirical Composite Scoring:** Computing an objective match score $[0, 100]$ based on string distance, author overlap, and publication year.
5. **Quality-Control Gating:** Enforcing deterministic publication thresholds (`PASS`, `WARN`, `BLOCK`).

---

## 2. Multi-Registry Reconciliation Architecture

Scientific literature is distributed across heterogeneous registries, each with distinct coverage and latency profiles:

```
                          ┌───────────────────────────┐
                          │   Parsed Reference String │
                          └─────────────┬─────────────┘
                                        │
                         Has DOI or     │    Free Text /
                         arXiv ID?      │    Author + Title
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
               ┌───────────────────┐         ┌───────────────────┐
               │  Direct Identifier│         │   Fuzzy Search    │
               │    Resolution     │         │    Resolution     │
               └─────────┬─────────┘         └─────────┬─────────┘
                         │                             │
       ┌─────────────────┼─────────────────────────────┼─────────────────┐
       ▼                 ▼                             ▼                 ▼
┌──────────────┐  ┌──────────────┐              ┌──────────────┐  ┌──────────────┐
│   Crossref   │  │   OpenAlex   │              │   Semantic   │  │    arXiv     │
│  (Primary    │  │  (Open graph │              │   Scholar    │  │  (Preprints  │
│   DOIs)      │  │  & metadata) │              │  (S2 engine) │  │   & CS/math) │
└──────┬───────┘  └──────┬───────┘              └──────┬───────┘  └──────┬───────┘
       │                 │                             │                 │
       └─────────────────┴──────────────┬──────────────┴─────────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │   Resolved Work Metadata    │
                         │   - Canonical DOI           │
                         │   - Official Title          │
                         │   - Author List             │
                         │   - Publication Year        │
                         │   - Open Access / Retracted │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │   Pure Composite Scorer     │
                         └─────────────────────────────┘
```

### Registry Port & Priority Protocol
- **Crossref (Primary for DOI):** Authoritative registration agency for scholarly publishers. Resolves DOIs directly.
- **OpenAlex (Graph & Metadata Enrichment):** Broad open coverage; ideal for resolving author identity and institutional affiliations.
- **arXiv (Preprints & Exact Epistemic Status):** Detects whether a cited work is a preprint and flags whether a subsequent journal version exists.
- **Semantic Scholar (S2 Fallback):** High-quality citation graph for computer science and biomedical literature.

---

## 3. The Composite Scoring Algorithm

Comparing a cited reference to a registry record requires resilient fuzzy metrics that resist typographical
errors, subtitle variations, and punctuation differences while strictly penalizing false-positive matches.

The composite score $S \in [0, 100]$ is computed as a weighted linear combination of three independent
epistemic dimensions:

$$S = 0.60 \cdot S_{\text{title}} + 0.25 \cdot S_{\text{author}} + 0.15 \cdot S_{\text{year}}$$

### Component 1: Title Similarity ($S_{\text{title}} \in [0, 100]$) — 60% Weight
- Both strings are stripped of punctuation, lowercased, and normalized against whitespace.
- Ratio calculated via sequence matcher:
  $$S_{\text{title}} = \text{ratio}(\text{norm}(T_{\text{cited}}), \text{norm}(T_{\text{registry}})) \times 100$$
- If the registry work has a subtitle separated by a colon, matching is computed against both the full title
  and the primary clause, adopting the higher score.

### Component 2: Author Agreement ($S_{\text{author}} \in [0, 100]$) — 25% Weight
- Extracts primary surname from cited entry.
- Checked against all authors listed in the registry record:
  - Exact primary surname match: $100$ pts.
  - Secondary co-author match: $75$ pts.
  - Substring / fuzzy surname match: scaled proportionally.
  - Zero author overlap: $0$ pts.

### Component 3: Publication Year Agreement ($S_{\text{year}} \in [0, 100]$) — 15% Weight
- Exact year match ($Y_{\text{cited}} == Y_{\text{registry}}$): $100$ pts ($15.0$ effective points).
- Pre-print to publication offset ($\pm 1$ year): $66.7$ pts ($10.0$ effective points).
- Divergence $> 1$ year: $0$ pts ($0.0$ effective points).

---

## 4. Publication Quality-Control Gates

Based on individual citation verdicts and aggregated document statistics, `refverify` assigns one of three
deterministic quality gates:

```
Total Bibliography Evaluation
  │
  ├── Any unresolvable citations or DOI metadata collisions? ──► [ BLOCK ]
  │
  ├── Average Score >= 85 AND All Citations Verified? ─────────► [ PASS  ]
  │
  └── Low-confidence matches (45 <= Score < 85)? ──────────────► [ WARN  ]
```

### Gate Definitions

| Gate | Status | Criteria | Action & Operational Impact |
|---|---|---|---|
| **`PASS`** | High Confidence | - All citations successfully resolved to registry records.<br>- Composite match score $\ge 85.0$ for each entry.<br>- Zero metadata collisions or duplicate citations. | **Publication Approved:** The manuscript passes directly into production or downstream publication pipelines. |
| **`WARN`** | Editorial Review Required | - Citations resolved with intermediate confidence ($45.0 \le \text{score} < 85.0$).<br>- Slight author or year variance (e.g., preprint cited with conference year).<br>- Unindexed grey literature with valid external URLs. | **Flagged for Human Review:** The document is flagged with an audit warning in its frontmatter. Editorial inspection is required before publication. |
| **`BLOCK`** | Publication Blocked | - **Metadata Collision:** Citation specifies a DOI, but the resolved registry title/authors diverge completely from the manuscript text.<br>- **Phantom Reference:** Citations completely unresolvable across all registries.<br>- **Retraction:** Cited record carries a formal retraction flag.<br>- **Duplicate Citations:** Identical paper cited under multiple keys. | **Pipeline Halting:** The document is rejected at the CI/CD gate. Downstream publishing steps are halted until corrected. |

---

## 5. Offline-First Caching & Hermetic Testing

To prevent rate-limiting, maintain fast CI/CD loops, and allow offline scientific audits:
- Every registry query is hashed and cached locally in SQLite (`~/.cache/refverify/cache.db` or configured path).
- Cache records store raw API responses, parsed metadata, TTL timestamps, and the registry provider identity.
- Hermetic test suites use mock adapters (`tests/fakes.py`) to simulate flaky networks, rate limits,
  and corrupted registry responses without network I/O.
