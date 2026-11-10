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
  - :projection.domain/legal-regulatory
  - :projection.domain/clinical-trials
  - :projection.domain/standards-conformance
  - :projection.domain/software-auditing
builds-on:
  - phosphene.tooling/refverify/docs/mdrag-and-frontmatters-innovations
  - phosphene.tooling/refverify/docs/ethos
converges-with:
  - work/inferno-labs/handoff/mdrag-philosophy
  - team/fka-explainer
abstract: |
  Projects the capacities proven in refverify (AST block extraction via mdrag,
  lossless YAML shadow patching via frontmatters, and Hickey coordinate block addressability)
  into generalized abstractions for other concerns, industries, and problem spaces requiring
  non-destructive document auditing, semantic provenance, and hybrid human-AI governance.
---

# Projections — General Capacities for External Concerns

> **Coordinate Namespace:** `phosphene.tooling.refverify.projections.*`  
> Projecting specific innovations into generalized, reusable architectural capacities.

---

## 1. The Projection Principle

In `refverify`, we proved three interconnected capacities under the pressure of public science:
1. **AST-Level Demarcation (`phosphene-mdrag`):** Isolating discrete structural sections without regex fragility or syntax-boundary leakage.
2. **Lossless Shadow Patching (`phosphene-frontmatters`):** Surgically injecting and updating machine-verifiable audit stamps into YAML frontmatter while preserving author comments, indentation, custom keys, and formatting byte-for-byte.
3. **Coordinate Block Addressability:** Transforming linear Markdown into an addressable graph where in-text assertions link to verified authority nodes via immutable coordinates (`doc:sec:p3:cite:1`).

These capacities are not unique to academic citation checking. They represent **fundamental primitives for any system where machines must read, audit, and annotate living human-authored documents without corrupting them**.

Under the **projection namespace** (`phosphene.tooling.refverify.projections`), we formalize how these capabilities abstract into generalized tools for external concerns.

---

## 2. Abstracted Capacities & Primitives

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   GENERALIZED PRIMITIVES                                │
├──────────────────────────────┬──────────────────────────────┬───────────────────────────┤
│    AST Structural Slicing    │    Lossless Shadow Patch     │    Block Addressability   │
│   (:projection.capacity/     │   (:projection.capacity/     │   (:projection.capacity/  │
│        ast-extraction)       │       shadow-patching)       │    block-addressability)  │
├──────────────────────────────┼──────────────────────────────┼───────────────────────────┤
│ Extracts semantic targets    │ Reads & writes metadata      │ Binds arbitrary prose to  │
│ based on AST node depth,     │ without destructive AST      │ an immutable coordinate;  │
│ type, and heading scope.     │ serialization. Preserves     │ enables bidirectional     │
│ Immune to code fences,       │ human whitespace, layout,    │ provenance links between  │
│ blockquotes, and formatting. │ and unknown foreign keys.    │ claim and verification.   │
└──────────────────────────────┴──────────────────────────────┴───────────────────────────┘
```

---

## 3. Projected Use Cases Across External Concerns

### Projection A: Legal & Regulatory Compliance Contracts
- **Coordinate:** `:projection.domain/legal-regulatory`
- **The Problem:** Contracts, terms of service, and regulatory filings (e.g., SEC disclosures, GDPR compliance manifests) are living documents edited by counsel. Automated compliance engines must verify statutory citations, clause cross-references, and risk scores, then stamp compliance metadata into the file.
- **How the Capacities Apply:**
  - *AST Extraction:* Extracts `## Indemnification`, `## Governing Law`, or `## Termination` blocks cleanly regardless of numbering style (`Section 4.1` vs `Article IV`).
  - *Shadow Patching:* Injects compliance audit blocks (`statutory_review_date`, `jurisdiction_risk_tier`, `counsel_signoff_hash`) without reformatting legal indentation, preserving attorney inline comments (`# Pending final review from Munich office`).
  - *Block Addressability:* Assigns invariant coordinates to specific clauses (`contract:clause:indemnity:p2`), linking them directly to verified case law citations or statutory codes.

---

### Projection B: Clinical Trial Protocols & Medical Literature
- **Coordinate:** `:projection.domain/clinical-trials`
- **The Problem:** Clinical trial protocols (IRB submissions, FDA investigational new drug packages) require strict provenance. Every claim regarding drug dosage, adverse event history, or mechanism of action must reference pre-clinical trial data or FDA approval numbers.
- **How the Capacities Apply:**
  - *AST Extraction:* Separates adverse event reporting tables, inclusion/exclusion criteria, and dosing regimens into structured AST blocks without regex degradation on tabular or nested data.
  - *Shadow Patching:* Injects FDA/EMA regulatory gate stamps (`irb_approval_id`, `gcp_audit_score`, `biostat_review_status`) into protocol frontmatters while maintaining clinical trial registry schemas under the Open-World Assumption.
  - *Block Addressability:* Creates direct coordinate anchors from trial inclusion criteria (`protocol:sec:inclusion:crit4`) to primary PubMed/ClinicalTrials.gov registry entries.

---

### Projection C: Technical Standards, RFCs & Conformance Verification
- **Coordinate:** `:projection.domain/standards-conformance`
- **The Problem:** Technical standards (IETF RFCs, W3C specifications, ISO drafts) contain normative references (`RFC 2119` MUST/SHALL keywords) and dependency bibliographies. Standards bodies need automated tools to verify that referenced specifications are active and not deprecated or superseded.
- **How the Capacities Apply:**
  - *AST Extraction:* Isolates normative vs. informative references sections and parses requirement blocks (`SHALL`, `MUST`, `RECOMMENDED`).
  - *Shadow Patching:* Injects dependency status stamps (`normative_deps_valid`, `superseded_ref_count`, `iso_ballot_gate`) into the standard document's metadata header.
  - *Block Addressability:* Tracks exact RFC section references (`rfc:sec:5.2:req:1`) to upstream specification requirements.

---

### Projection D: Architectural Decision Records (ADRs) & Software Governance
- **Coordinate:** `:projection.domain/software-auditing`
- **The Problem:** Modern engineering organizations document architecture in ADRs (Markdown files in git repos). As microservices evolve, ADRs become stale. Automated CI pipelines need to audit ADRs against actual deployed infrastructure, package dependencies, and vulnerability databases.
- **How the Capacities Apply:**
  - *AST Extraction:* Parses `## Context`, `## Decision`, and `## Consequences` blocks independently.
  - *Shadow Patching:* Stamped by CI runners with live deployment telemetry (`implemented_in_commit`, `live_service_verified`, `cve_audit_pass`) directly in the ADR frontmatter, preserving architect rationale and notes.
  - *Block Addressability:* Links architectural decision coordinates (`adr:104:decision:auth`) to active source code modules or deployment manifests.

---

## 4. What This Teaches Us About the Tool Class

Documenting these projections clarifies the broader design paradigm for this class of tools:

1. **Documents as Decentralized Databases:**  
   Instead of forcing human knowledge workers into centralized relational databases or proprietary SaaS silos, Markdown with typed frontmatter and AST addressability functions as a **distributed, git-versioned, human-first database**.

2. **Non-Destructive Mutation as a Hard Invariant:**  
   Any automated tool operating in human document spaces must treat human formatting, whitespace, and commentary as sacred. If an auditing tool alters one byte of un-targeted text, humans will reject it or turn it off.

3. **Hybrid Verification Loops (RLVR & Expert Review):**  
   By generating deterministic, mathematically verifiable audit stamps and coordinate anchors, documents become directly consumable by both reinforcement learning verification engines (RLVR) and human peer reviewers without translation loss.
