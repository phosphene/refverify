---
uri: phosphene.tooling/refverify/docs/index
owner: edphos
status: canonical
created: 2026-11-10
updated: 2026-11-10
namespace: phosphene.tooling.refverify
coordinates:
  - :refverify/fka-registry
  - :phos.arch/fka
  - :refverify.ethos/sufficient-reason
builds-on:
  - phosphene.tooling/refverify/README
converges-with:
  - team/fka-explainer
  - team/platform/doc-standards
abstract: |
  Federated Knowledge Architecture (FKA) navigation index and coordinate registry
  for the refverify documentation suite. Establishes the topological map of
  scholarly verification, AST-level md-rag block parsing, frontmatter shadow patching,
  hexagonal architecture, foundational principles of sufficient reason, and projections
  to generalized external capacities.
---

# `refverify` Literate Documentation Index

This directory establishes the comprehensive literate documentation suite for `refverify`,
patterned on the Phosphene Federated Knowledge Architecture (FKA) and Rich Hickey's
coordinate addressing methodology.

Under our governing philosophy, documentation is not an external cosmetic artifact or marketing
prose for spectators; it is an **internal instrument of reasoning, continuity, and defect prevention**,
written to ourselves as authors, operators, and future maintainers under the aegis of public science.

---

## 1. Coordinate Topology

| Coordinate | Document | Epistemic Role |
|---|---|---|
| `:refverify.ethos/sufficient-reason` | [`ethos.md`](ethos.md) | The Principle of Sufficient Reason, self-documentation to ourselves, prolix vs. specification form. |
| `:mdrag.core/ast-aware`<br>`:frontmatters.patch/shadow` | [`mdrag-and-frontmatters-innovations.md`](mdrag-and-frontmatters-innovations.md) | Primary use case & innovations: AST demarcation vs. regex fragility, shadow patching invariants, block addressability, and tool lessons. |
| `:projection.capacity/*`<br>`:projection.tier/*`<br>`:projection.domain/*` | [`projections/general-capacities.md`](projections/general-capacities.md) | **Operational Projections:** Multi-level operational projections: Level 1 Markdown ticketing/CI, Level 2 federated research wikis & structured block namespacing, and Level 3 high-assurance domains (legal, clinical). |
| `:projection.apparatus/lexical-consistency`<br>`:projection.epistemics/inferentialism` | [`projections/conceptual-and-terminological-verification.md`](projections/conceptual-and-terminological-verification.md) | **Conceptual Projections:** Grounding in Robert Brandom's inferentialism (*Making It Explicit*), tracking deontic scorekeeping, idiolect-to-norm divergence, and catching human/LLM semantic drift. |
| `:projection.epistemics/dff-axiomatics`<br>`:projection.boundary/episteval-vs-refverify` | [`projections/design-for-falsifiability-and-episteval.md`](projections/design-for-falsifiability-and-episteval.md) | **Design for Falsifiability (DFF):** Extending DFT to scientific hypothesis architecture, formalizing the episteval (inferential) vs refverify (provenance) boundary, and asking questions "for free". |
| `:projection.meta/rag-citation-critique`<br>`:projection.meta/correctness-vs-faithfulness` | [`projections/llm-rag-critique-and-deterministic-provenance.md`](projections/llm-rag-critique-and-deterministic-provenance.md) | **Meta-Critique of RAG Verifiers:** Why generative LLM/RAG citation checkers (consensus.app) produce post-rationalization and deceptive grounding; specifying Phosphene's deterministic alternative. |
| `:refverify.apparatus/citations` | [`citation-verification.md`](citation-verification.md) | Multi-registry bibliographic reconciliation, fuzzy metric weights, composite scoring $[0, 100]$, and publication gates (`PASS`, `WARN`, `BLOCK`). |
| `:refverify.arch/hexagonal` | [`architecture.md`](architecture.md) | Logic/IO separation, `LookupClient` port, offline-first SQLite tier, and telemetry contracts. |
| `:phos.standards/scientific-docs` | [`scientific-documentation-standards.md`](scientific-documentation-standards.md) | Phosphene scientific documentation ethos, literate docstring standards, and epistemic basis tiers. |

---

## 2. Navigating the Knowledge Units

```
                  ┌──────────────────────────────────────────────┐
                  │                   ethos.md                   │
                  │   :refverify.ethos/sufficient-reason         │
                  │   Self-documentation & public science        │
                  └──────────────────────┬───────────────────────┘
                                         │ grounds
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │                architecture.md               │
                  │   :refverify.arch/hexagonal                  │
                  │   Hexagonal domain / ports / adapters        │
                  └──────────────┬────────────────┬──────────────┘
                                 │                │
            decomplects via      │                │ implements
                                 ▼                ▼
┌───────────────────────────────────────┐  ┌─────────────────────────────────────┐
│  mdrag-and-frontmatters-innovations.md│  │       citation-verification.md      │
│  :mdrag.core/ast-aware                │  │  :refverify.apparatus/citations     │
│  :frontmatters.patch/shadow           │  │  Multi-registry matching & gates    │
│  AST blocks & lossless YAML patching  │  │  Crossref / OpenAlex / arXiv / S2   │
└──────────────────┬────────────────────┘  └─────────────────────────────────────┘
                   │                                  │
       projects to │                                  │ evaluated against
                   ▼                                  ▼
┌───────────────────────────────────────┐  ┌─────────────────────────────────────┐
│  projections/general-capacities.md    │  │scientific-documentation-standards.md│
│  :projection.capacity/*               │  │  :phos.standards/scientific-docs   │
│  Generalized domain applications      │  │  Literate prolix & epistemic tiers  │
└───────────────────────────────────────┘  └─────────────────────────────────────┘
```

---

## 3. Self-Sufficiency Invariant

Each document within this suite is crafted to satisfy the **Principle of Sufficient Reason**: it contains
within its own boundaries the necessary definitions, architectural reasoning, and failure modes to be
comprehensible in isolation. When vendored or distributed as part of standalone wheels or independent
repository clones, no external path crawling across private monorepos is required to understand its
operational commitments.
