# `refverify` — Scholarly Reference Verification & Quality-Control Gate

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![Architecture: Hexagonal](https://img.shields.io/badge/architecture-hexagonal-success)](docs/architecture.md)
[![Docs: Literate](https://img.shields.io/badge/docs-literate%20prolix-success)](docs/index.md)

`refverify` is a deterministic quality-control gate that validates academic citations, bibliographic entries, and in-text quotations against primary metadata registries (Crossref, OpenAlex, arXiv, OpenLibrary) and local PDF text witnesses.

Unlike generative AI verifiers that hallucinate plausible post-rationalizations, `refverify` performs deterministic catalog resolution, token-overlap heuristic scoring, exact character-span locus attestation, and offline-first caching.

---

## ⚡ Quickstart

### Installation

Install via `pip`:

```bash
pip install phosphene-refverify
```

Or install locally with `uv`:

```bash
uv pip install -e .
```

### Basic Usage

Verify manuscripts, bibliographies, or wikitext files with automatic format detection:

```bash
# Academic Markdown manuscript
refverify manuscript.md

# Raw APA / Chicago / Harvard reference list
refverify references.txt

# Microsoft Word document
refverify draft.docx

# MediaWiki wikitext page (checks |Bibliography= template field)
refverify --wiki article.wiki
```

### Verifying In-Text Quotations & Physical PDF Witnesses

Verify cited quotations directly against local primary PDF sources with OCR ligature normalization and exact character span matching:

```bash
refverify manuscript.md --verify-quotes --local-pdf-dir /path/to/pdf/vault
```

---

## 📊 Verification Scoring & Gate Decisions

Each reference receives an empirical composite match score $[0, 100]$ based on weighted heuristic components:
- **Title Similarity (60%):** Sequence matching ratio over normalized letter-digit strings.
- **Author Match (25%):** Primary surname agreement.
- **Publication Year (15%):** Exact year agreement (15 pts) or $\pm 1$ year divergence (10 pts).

The publication gate evaluates composite verdicts across the bibliography:

| Verdict | Criteria | Gate Action |
|---|---|---|
| **PASS** | All citations resolve with high metadata confidence ($\ge 85$ composite score, exact DOI verification, or verified arXiv identity). | Publication approved |
| **WARN** | Low-confidence matches ($45 \le \text{score} < 85$) or unindexed entries requiring human editorial review. | Editorial review flagged |
| **BLOCK** | Metadata mismatch (divergent title/year under cited DOI), duplicate citations of identical works, or unresolvable references. | Publication blocked |

---

## 🛠️ Advanced Features

### Markdown Frontmatter Synchronization
When evaluating academic manuscripts with YAML frontmatter, `refverify` integrates with `phosphene-frontmatters` to project verification audit results directly into the document's metadata without altering human-authored comments, indentation, or document styling:

```yaml
---
title: Empirical Dynamics of Valence
author: Lead Researcher # Primary author note
references_verified: true
verification_score: 96.5
verification_gate: pass
verification_summary:
  total: 42
  verified: 42
  mismatch: 0
  unresolved: 0
---
```

### Caching & Network Controls
By default, query results are cached locally in `~/.cache/refverify/cache-v2.json` with a 30-day TTL.

```bash
# Bypass cache and force direct upstream verification
refverify manuscript.md --no-cache

# Custom cache time-to-live (in seconds)
refverify manuscript.md --ttl-seconds 86400
```

---

## 🏛️ Architecture & Core Invariants

`refverify` implements strict logic and I/O separation via a hexagonal architecture:

```
  ┌─────────────────────────────────────────────────────────────┐
  │         Intake Readers & Markdown Orchestration             │
  │     - phosphene-mdrag AST parser (Open World Assumption)    │
  │     - phosphene-frontmatters Shadow Patch Sync Engine       │
  │     - Word Document (.docx) & Wikitext (.wiki) Adapters     │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                  Pure Domain Core (DFT)                     │
  │     - Reference Extraction & Normalization                  │
  │     - Pure Scoring Algorithm (Title, Author, Year)          │
  │     - Intra-Manuscript Duplicate & Discrepancy Detection    │
  │     - Tripartite Gate Decision (PASS / WARN / BLOCK)        │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                   Ports & Infrastructure                    │
  │     - Protocol Port: LookupClient                           │
  │     - Local Disk Cache Adapter (FileCache, TTL)             │
  │     - Registry Adapters: Crossref, OpenAlex, arXiv, OpenLib │
  │     - Physical Text Witness Index: LocalPdfClient (fitz)    │
  └─────────────────────────────────────────────────────────────┘
```

- **Pure Domain Core:** Pure verification, scoring, deduplication, and gate decisions. Value objects (`Reference`, `CandidateRecord`, `VerdictResult`) inherit from `phosphene.core.models.InvariantStatic`, guaranteeing immutability, mathematical hashability, and zero tolerance for schema drift (`extra='forbid'`).
- **Ports & Adapters:** Defines an abstract `LookupClient` protocol satisfied by HTTP adapters (`CrossrefClient`, `OpenAlexClient`, `ArxivClient`, `OpenLibraryClient`) and local storage (`FileCache`, `LocalPdfClient`).
- **Living Specifications:** Formal Gherkin feature specifications in `features/reference_verification.feature`.

---

## 📚 Literate Documentation Suite & Theoretical Foundations

Under the **Principle of Sufficient Reason** and the **Phosphene Federated Knowledge Architecture (FKA)**, `refverify` maintains a standalone, self-documenting literate knowledge suite in `docs/`:

| Document | Primary Coordinate | Focus |
|---|---|---|
| 📖 [**Documentation Index**](docs/index.md) | `:refverify/fka-registry` | Topological map, FKA coordinate index, and navigation graph. |
| 🏛️ [**Ethos & Sufficient Reason**](docs/ethos.md) | `:refverify.ethos/sufficient-reason` | Writing to ourselves, sufficient reason, and public science commitments. |
| 💡 [**`mdrag` & Frontmatter Innovations**](docs/mdrag-and-frontmatters-innovations.md) | `:mdrag.core/ast-aware`<br>`:frontmatters.patch/shadow` | AST block isolation vs. regex fragility, lossless YAML shadow patching, and coordinate block addressability. |
| 🌐 [**General Capacity Projections**](docs/projections/general-capacities.md) | `:projection.capacity/*`<br>`:projection.tier/*`<br>`:projection.domain/*` | Grounding in software practices (Markdown ticketing, federated research wikis) and projecting to high-assurance external concerns. |
| 🧠 [**Conceptual & Terminological Verification**](docs/projections/conceptual-and-terminological-verification.md) | `:projection.apparatus/lexical-consistency`<br>`:projection.epistemics/inferentialism` | Grounding in Robert Brandom (*Making It Explicit*), mythographic/Hellenic citation lineage, and verbatim text/formula tracking. |
| 🛡️ [**Design for Falsifiability (DFF) & Episteval Boundary**](docs/projections/design-for-falsifiability-and-episteval.md) | `:projection.epistemics/dff-axiomatics`<br>`:projection.boundary/episteval-vs-refverify` | Extending DFT to hypothesis falsifiability; formalizing the episteval (inference/defeat) vs. refverify (provenance/record) boundary. |
| 🔍 [**RAG Citation Critique & Deterministic Provenance**](docs/projections/llm-rag-critique-and-deterministic-provenance.md) | `:projection.meta/rag-citation-critique`<br>`:projection.meta/correctness-vs-faithfulness` | Meta-critique of generative verifiers (Wallat 2025, Caruzzo 2026); establishing Phosphene's deterministic AST provenance. |
| 🔬 [**Citation Verification & Scoring**](docs/citation-verification.md) | `:refverify.apparatus/citations` | Multi-registry reconciliation (Crossref, OpenAlex, arXiv, S2), composite scoring weights $[0, 100]$, and `PASS`/`WARN`/`BLOCK` gates. |
| ⚙️ [**Hexagonal Architecture**](docs/architecture.md) | `:refverify.arch/hexagonal` | Logic/IO separation, `LookupClient` port, offline-first SQLite tier, and telemetry models. |
| 📐 [**Scientific Documentation Standards**](docs/scientific-documentation-standards.md) | `:phos.standards/scientific-docs` | The literate engineering standard, docstring contracts, and epistemic basis tiers. |

---

## 📄 License

MIT
