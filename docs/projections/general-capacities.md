---
uri: phosphene.tooling/refverify/docs/projections/general-capacities
owner: edphos
status: proposed
created: 2026-11-10
updated: 2026-11-10
namespace: phosphene.tooling.refverify.projections
coordinates:
  - :projection.capacity/ast-extraction
  - :projection.capacity/shadow-patching
  - :projection.capacity/block-addressability
  - :projection.tier/internal-software-engineering
  - :projection.tier/institutional-knowledge-wikis
  - :projection.tier/external-compliance-critical
  - :projection.domain/markdown-ticketing
  - :projection.domain/federated-wiki-corpora
  - :projection.domain/structured-block-namespacing
  - :projection.domain/legal-regulatory
  - :projection.domain/clinical-trials
builds-on:
  - phosphene.tooling/refverify/docs/mdrag-and-frontmatters-innovations
  - phosphene.tooling/refverify/docs/ethos
converges-with:
  - work/inferno-labs/handoff/mdrag-philosophy
  - team/fka-explainer
  - team/platform/doc-standards
abstract: |
  Projects the capacities proven in refverify (AST block extraction via mdrag,
  lossless YAML shadow patching via frontmatters, and Hickey coordinate block addressability)
  across multiple tiers of practice. Grounds the primary domain in actual software engineering
  teams actively using Markdown for living ticket systems, federated research wikis, and structured
  block namespacing, before projecting outwards to external high-assurance domains.
---

# Projections — General Capacities Across Operational Levels

> **Coordinate Namespace:** `phosphene.tooling.refverify.projections.*`  
> Projecting proven verification and AST primitives into tiered operational software domains.

---

## 1. The Multi-Level Projection Principle

In `refverify`, three foundational capacities were proven in the crucible of public science:
1. **AST-Level Demarcation (`phosphene-mdrag`):** Isolating discrete structural sections without regex fragility or syntax-boundary leakage.
2. **Lossless Shadow Patching (`phosphene-frontmatters`):** Surgically injecting and updating machine-verifiable audit stamps into YAML frontmatter while preserving author comments, indentation, custom keys, and formatting byte-for-byte.
3. **Coordinate Block Addressability:** Transforming linear Markdown into an addressable graph where in-text assertions link to verified authority nodes via immutable coordinates (`doc:sec:p3:cite:1`).

Per Phosphene standards, projections must not begin as abstract speculations about hypothetical industries.
**They must be grounded in actual software engineering practices by teams that actively use Markdown as their primary system of record.**

We structure our projections into **three operational tiers**:
- **Level 1 (Direct Software Practice):** Teams using Markdown for living ticket architectures (`TICKETS-*.md`), initiative tracking, and CI/CD gating.
- **Level 2 (Federated Knowledge Corpora):** Multi-author research wikis, architectural decision records (ADRs), and documentation systems organized around namespaced Hickey coordinates.
- **Level 3 (External Compliance-Critical Systems):** High-assurance regulatory, legal, and clinical domains that demand the same mathematical guarantees of non-destructive mutation and claim-to-evidence provenance.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ LEVEL 1: DIRECT SOFTWARE ENGINEERING PRACTICE                                          │
│ Markdown Ticketing • Living Issue Trackers • CI/CD Verification & Status Stamping      │
│ Coordinates: :projection.domain/markdown-ticketing, :projection.capacity/*              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ LEVEL 2: FEDERATED KNOWLEDGE & RESEARCH WIKIS                                          │
│ Distributed Markdown Wikis • Structured Block Namespacing • Hickey Coordinate Graphs   │
│ Coordinates: :projection.domain/federated-wiki-corpora, :projection.domain/namespacing │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ LEVEL 3: EXTERNAL HIGH-ASSURANCE DOMAINS                                               │
│ Legal / Regulatory Compliance • Clinical Protocols • Normative Technical RFCs          │
│ Coordinates: :projection.domain/legal-regulatory, :projection.domain/clinical-trials    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Level 1: Markdown Ticketing & Software Lifecycle Governance

> **Coordinates:** `:projection.tier/internal-software-engineering`, `:projection.domain/markdown-ticketing`

Modern engineering organizations increasingly abandon monolithic, opaque SaaS issue trackers (Jira, linear databases) in favor of **in-repo, git-versioned Markdown ticketing** (e.g., `team/TICKETS-*.md`, `INITIATIVES.md`). In this paradigm, tickets live directly alongside code, branches, and architectural specifications.

However, git-native ticketing introduces severe operational friction when automated agents and CI bots interact with human-authored files:

### The Failure Mode in Ticketing Workflows
1. **Status Clashing:** A human engineer writes ticket details, checklists, and notes with custom markdown comments (`<!-- blocked on upstream PR #42 -->`). When an automated bot updates the ticket status from `OPEN` to `VERIFIED`, naive parsers or LLMs rewrite the whole file, reordering tickets, wiping comments, and clobbering unmerged edits.
2. **Regex Ticket Slicing:** Extracting individual ticket specifications (e.g., `### T-571: Synchronous Hook`) via regex fails when tickets contain embedded Markdown code blocks, nested test runs, or multiline bash transcripts.

### How `mdrag` and `frontmatters` Resolve This
- **AST Ticket Demarcation (`:projection.capacity/ast-extraction`):**  
  `mdrag` treats each ticket heading (`### T-571`) as an isolated AST subtree. The boundaries are mathematically defined: from heading token to next heading of equal or higher depth. Embedded bash fences, backticks, or nested lists cannot leak across ticket boundaries.
- **Shadow Patching Ticket Metadata (`:projection.capacity/shadow-patching`):**  
  When an automated test runner passes all acceptance criteria, it invokes shadow patching to update ticket metadata:
  ```yaml
  status: DELIVERED
  verified_in_commit: 9af079bd
  test_coverage: 96.4%
  ```
  Every human comment, task checkbox order, and conversational annotation remains byte-for-byte identical.
- **CI/CD Quality-Control Gating:**  
  Just as `refverify` enforces `PASS`/`WARN`/`BLOCK` on bibliographies, a ticket verification engine enforces automated gates before a PR can merge: checking that every acceptance criterion in the ticket block corresponds to a passing test report.

---

## 3. Level 2: Federated Research Wikis & Structured Block Namespacing

> **Coordinates:** `:projection.tier/institutional-knowledge-wikis`, `:projection.domain/federated-wiki-corpora`, `:projection.domain/structured-block-namespacing`

In research organizations and engineering collectives, knowledge is organized into **distributed Markdown wikis** (e.g., `research-wiki/`, `docs/platform/`, `RFC/`). These wikis avoid centralized databases, relying instead on federated repositories linked through namespaced coordinates.

### The Operational Challenge in Federated Corpora
Wikis suffer from two fatal ailments:
1. **Link Rot and Semantic Drift:** A link to `wiki/architecture.md#caching` breaks when a heading is renamed or rewritten.
2. **Coarse-Grained Retrieval:** Search engines return entire 10,000-word files rather than the specific 3-line axiom, formula, or proof being cited.

### How Our Innovations Transform Wiki Architecture
- **Hickey Coordinate Block Addressability (`:projection.capacity/block-addressability`):**  
  By parsing Markdown with `mdrag`, every block acquires a deterministic, content- or path-addressed coordinate:
  ```
  wiki:sys.arch/cache:block:l2-invalidation
  wiki:sci.bio/valence:sec:cambrian:p4
  ```
  Cross-document references link to **immutable block coordinates** rather than fragile heading anchors or transient line numbers.
- **Lossless Provenance Stamping:**  
  When automated knowledge graph crawlers (FKA indexing agents) map influence edges (`inherits-from`, `critiques`, `operationalizes`), they record discovered relations directly into the document's YAML frontmatter via shadow patching without disturbing the researcher's prose:
  ```yaml
  fka:
    graph_type: influence
    inbound_edges:
      - from: wiki:math.logic/goedel
        predicate: operationalizes
        discovered_at: 2026-11-10
  ```
- **Namespaced Dialect Coexistence:**  
  Under the Open-World Assumption (OWA), different research teams register their own namespace semantics (e.g., `inv.forensics.*` vs. `anthro.etho.*`) in the same wiki corpus. Shadow patching guarantees that an agent understanding only `:sci.bio/*` can update biological metadata without corrupting forensic metadata blocks.

---

## 4. Level 3: External High-Assurance Domains

> **Coordinates:** `:projection.tier/external-compliance-critical`, `:projection.domain/legal-regulatory`, `:projection.domain/clinical-trials`

Once grounded in concrete software and wiki practices, the exact same mathematical properties project directly into mission-critical external industries where document corruption carries severe regulatory or life-safety liability:

### Domain A: Legal, Statutory & Regulatory Contracts
- **Coordinate:** `:projection.domain/legal-regulatory`
- **Application:** Legal teams drafting contracts, credit agreements, or statutory filings in Markdown.
- **Workflow:**  
  - `mdrag` slices `## Indemnification` or `## Covenants` AST blocks.
  - Automated compliance engines verify statutory citations and court precedent.
  - Shadow patching stamps `counsel_signoff_hash` and `jurisdiction_risk_tier` without altering legal indentation or attorney comments (`# Pending Munich partner signoff`).
  - Block coordinates (`contract:clause:indemnity:p2`) link clauses directly to verified precedent databases.

### Domain B: Clinical Trial Protocols & Regulatory Filings (FDA / EMA)
- **Coordinate:** `:projection.domain/clinical-trials`
- **Application:** Medical research protocols where every assertion regarding drug efficacy, inclusion/exclusion criteria, or dosing must link to validated clinical trial records.
- **Workflow:**  
  - `mdrag` separates tabular adverse event reporting and dosing regimens into structured AST blocks.
  - Verification engines resolve PubMed IDs and ClinicalTrials.gov NCT identifiers.
  - Shadow patching stamps GCP/IRB audit approval gates into protocol headers while respecting OWA medical ontology keys.

---

## 5. Architectural Generalization Matrix

| Operational Tier | Primary Medium | What `mdrag` Slices | What `frontmatters` Injects | What Block Coordinates Anchor |
|---|---|---|---|---|
| **Level 1: Software Practice** | Git `TICKETS-*.md`, PRs | Individual ticket bodies (`### T-NNN`), acceptance tests, logs | Test verdicts, CI commit hashes, review approvals | Acceptance criteria $\to$ Test execution traces |
| **Level 2: Research Wikis** | Federated Markdown Corpora | Concept definitions, literature reviews, lemmas | FKA graph edges, discovery dates, epistemic basis tiers | In-text claims $\to$ Primary citations & proofs |
| **Level 3: Regulatory & Legal** | Contracts, Protocols, RFCs | Clauses, statutory references, adverse event tables | Compliance hashes, IRB approval IDs, audit risk scores | Legal clauses $\to$ Statutory precedent / Case law |

---

## 6. Synthesis: The Universal Paradigm

Across all three levels, `refverify`'s innovations demonstrate a unified paradigm:

1. **Documents as Decentralized Databases:**  
   Markdown with typed YAML frontmatter and AST addressability is not just text; it is a **git-versioned, decentralized database** that humans can read and write with ordinary text editors, and machines can audit with mathematical precision.
2. **The Inviolability of Human Artifacts:**  
   Auditing, verification, and AI assistance must be strictly non-destructive. The moment an automated tool scrambles whitespace, deletes comments, or alters un-targeted prose, it fails as a collaborative partner.
3. **The Dual Training and Verification Signal:**  
   By maintaining a clean separation between human prose (content) and machine-addressable coordinates/audit stamps (structure), these systems provide the exact substrate needed for modern hybrid intelligence: natural prose for human deliberation, and rigorous AST targets for formal verification (RLVR) and automated quality-control gates.
