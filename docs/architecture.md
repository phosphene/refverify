---
uri: phosphene.tooling/refverify/docs/architecture
owner: edphos
status: canonical
created: 2026-11-10
updated: 2026-11-10
namespace: phosphene.tooling.refverify
coordinates:
  - :refverify.arch/hexagonal
  - :phos.arch/logic-io-separation
  - :phos.arch/dft
builds-on:
  - phosphene.tooling/refverify/docs/ethos
converges-with:
  - team/platform/rational-decomposition-ethos
abstract: |
  Details the hexagonal architecture of refverify: decomposing the system into
  pure domain logic (DFT), abstract ports for external lookup, concrete HTTP/cache
  adapters, and intake readers orchestrating mdrag and frontmatters.
---

# Architecture — Hexagonal Design, Ports, Adapters & Telemetry

> **Coordinate:** `:refverify.arch/hexagonal`  
> Decoupling pure verification thought from I/O mechanics.

---

## 1. Architectural Philosophy: Logic / IO Separation

In accordance with the foundational axioms of the Phosphene platform, `refverify` enforces a strict
**Logic / I/O Separation** via Hexagonal Architecture (Ports and Adapters).

Scientific citation verification is vulnerable to subtle failure modes: network latency, API rate limits,
schema changes by third-party metadata providers, and file format corruptions. If network requests and
file parsing are interleaved with scoring algorithms, the system becomes impossible to test deterministically.

By isolating:
- **Pure Domain:** Unaware of network, databases, or operating systems. Pure mathematical scoring,
  token normalization, and gate evaluations (Deterministic Finite Transitions / DFT).
- **Ports:** Abstract structural protocols defining what the domain requires from the external world.
- **Adapters:** Concrete implementations handling HTTP network calls, SQLite cache persistence,
  and filesystem reads.

```
                    ┌────────────────────────────────────────────────────────┐
                    │                      DRIVING LAYER                     │
                    │   CLI (__main__.py)   │   Readers (Markdown / DOCX)    │
                    └───────────────────┬────────────────────────────────────┘
                                        │ invokes
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────────────┐
    │                                PURE DOMAIN CORE                                │
    │                                                                                │
    │   Reference Models   │   Scoring Engine   │   Verdicts   │   Gate Decision     │
    │   - Reference        │   - Sequence Match │   - Match    │   - PASS / WARN     │
    │   - InvariantStatic  │   - Author Jaro    │   - Verdict  │   - BLOCK           │
    │                                                                                │
    └───────────────────────────────────┬────────────────────────────────────────────┘
                                        │ calls through
                                        ▼
                    ┌────────────────────────────────────────────────────────┐
                    │                       PORTS LAYER                      │
                    │   LookupClient (Protocol)                              │
                    │   - resolve_doi(doi: str) -> WorkMetadata              │
                    │   - search_title(title: str, author: str) -> list      │
                    └───────────────────┬────────────────────────────────────┘
                                        │ implemented by
                                        ▼
                    ┌────────────────────────────────────────────────────────┐
                    │                     ADAPTERS LAYER                     │
                    │                                                        │
                    │   CachingLookupClient (SQLite Cache Layer)             │
                    │   ├── CrossrefProvider (HTTPX REST Client)             │
                    │   ├── OpenAlexProvider (HTTPX REST Client)             │
                    │   ├── ArxivProvider (HTTPX XML Client)                 │
                    │   └── FakeLookupClient (In-Memory Hermetic Test Stub)  │
                    └────────────────────────────────────────────────────────┘
```

---

## 2. The Core Components

### 1. Pure Domain (`phosphene.refverify.domain`)
- **`reference.py`:** Atomic data models (`Reference`, `Author`, `WorkMetadata`). Inherits from `phosphene.core.models.InvariantStatic` to enforce immutable data structures and explicit typing.
- **`scoring.py`:** Pure scoring functions ($S_{\text{title}}$, $S_{\text{author}}$, $S_{\text{year}}$, $S_{\text{composite}}$). Given two pure data records, produces an identical floating-point score regardless of execution environment.
- **`verdict.py`:** Evaluates composite scores against threshold boundaries, yielding structured `Verdict` objects (`VERIFIED`, `MISMATCH`, `UNRESOLVED`).
- **`dedup.py`:** Detects duplicate citations within a single manuscript using normalized token hashes and DOI matching.
- **`readers.py`:** Intake orchestrator. Binds `phosphene-mdrag` for AST section isolation and `phosphene-frontmatters` for shadow patching.

### 2. Ports (`phosphene.refverify.ports`)
- **`lookup.py`:** Defines the `LookupClient` protocol using Python's `typing.Protocol`.
```python
class LookupClient(Protocol):
    def resolve_doi(self, doi: str) -> WorkMetadata | None: ...
    def search_title(self, title: str, author: str | None = None) -> list[WorkMetadata]: ...
```

### 3. Adapters (`phosphene.refverify.adapters`)
- **`providers.py`:** Implements `LookupClient` against live web endpoints:
  - Crossref API (`https://api.crossref.org/works/`)
  - OpenAlex API (`https://api.openalex.org/works/`)
  - arXiv API (`http://export.arxiv.org/api/query`)
- **`cache.py`:** Implements `CachingLookupClient` wrapping any downstream provider with an offline-first SQLite database.
- **`tests/fakes.py`:** In-memory test double enabling 100% test coverage without touching live networks.

---

## 3. Telemetry and Audit Guarantees

Every verification execution generates a structured audit model:
```python
class DocumentVerificationAudit(InvariantStatic):
    verified: bool
    score: float
    gate: str
    total_references: int
    verified_count: int
    mismatch_count: int
    unresolved_count: int
```

This audit model provides complete epistemic traceability. When injected into a document's frontmatter,
it records not just whether the document passed, but the empirical metrics that justified the gate decision.
