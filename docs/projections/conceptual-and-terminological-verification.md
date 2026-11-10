---
uri: phosphene.tooling/refverify/docs/projections/conceptual-and-terminological-verification
owner: edphos
status: proposed
created: 2026-11-10
updated: 2026-11-10
namespace: phosphene.tooling.refverify.projections.lexicon
coordinates:
  - :projection.apparatus/textual-reference
  - :projection.epistemics/inferentialism
  - :projection.epistemics/brandom-scorekeeping
  - :projection.apparatus/lexical-provenance
  - :projection.lineage/mythography-and-hellenic-citation
  - :projection.boundary/episteval-vs-refverify
builds-on:
  - phosphene.tooling/refverify/docs/projections/general-capacities
  - phosphene.tooling/refverify/docs/mdrag-and-frontmatters-innovations
converges-with:
  - phil/brandom-robert
  - concepts/lexicon-study-posture
  - lexicography/index
  - team/SPEC_LOG
abstract: |
  Decomplects the overlapping concerns of episteval (evaluating inferential validity,
  claim regimes, and epistemic states) and refverify (keeping track of glossaries,
  corpus lexicons, and verbatim textual/data provenance). Traces the lineage of
  granular reference from classical mythography and the Hellenic studies CTS (Canonical
  Text Services) standards to modern AST coordinate block addressability, establishing
  refverify's role as an informative instrument of textual, formal, and lexical provenance
  that informs without naively gating.
---

# Projections — Textual Reference, Lexical Provenance & Decomplecting `episteval` from `refverify`

> **Coordinate Namespace:** `phosphene.tooling.refverify.projections.lexicon.*`  
> Invariant tracking of verbatim text, formalisms, data representations, and namespace-isolated lexicons.

---

## 1. Decomplecting `episteval` and `refverify`

In the development of automated scholarly evaluation, two overlapping concerns frequently tangle:
1. **The Epistemic Evaluation of Claims (`phosphene/episteval`):** Evaluating the *inferential validity* of an argument, scoring truth-functional confidence, assigning composite indices, and tracking warrant derivation trees (`EpistemicState`).
2. **The Scholarly Apparatus & Textual Provenance (`phosphene/refverify`):** Verifying that citations resolve, that quoted text matches primary sources verbatim, that data formalisms are anchored to exact coordinates, and that terminological operating definitions are cataloged and tracked across namespaces.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        DECOMPLECTED RESEARCH EVALUATION ROLES                          │
├──────────────────────────────────────────┬─────────────────────────────────────────────┤
│         phosphene/refverify              │            phosphene/episteval              │
│    (Scholarly Apparatus & Provenance)    │     (Inferential & Epistemic Evaluation)    │
├──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ • Canonical identifier resolution (DOI)  │ • Warrant derivation trees & inferential AST│
│ • Verbatim textual & formulaic matching  │ • Defeater / undercutter condition evaluation│
│ • Local glossary & corpus lexicon registry│ • Dual-faceted state (numeric + structural) │
│ • CTS-style coordinate block addressing  │ • Hypothesis ranking, loss functions & WCI   │
│ • Lossless frontmatter audit stamping    │ • Regime semantics & epistemic truth values  │
├──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ Ethos: INFORM & PRESERVE (No naive gates)│ Ethos: EVALUATE & CALIBRATE (Dual Facets)   │
└──────────────────────────────────────────┴─────────────────────────────────────────────┘
```

`refverify` is not a truth engine; it is the **apparatus of record and provenance**. Its task is to guarantee that when a claim is made, its textual citations, empirical data points, and mathematical formalisms can be traced verbatim to primary coordinates.

---

## 2. Lineage of Textual Reference: From Classical Mythography to Hellenic Citation Standards

The modern need to verify citations and formalisms down to the block level is not an artifact of modern software. It has a deep scholarly genealogy rooted in the humanities:

### The Mythographic Apparatus
Mythography—the comparative study, variant collation, and lineage tracing of mythological traditions—was historically the pioneer of granular citation systems. When mythographers compared variants of a myth across Hesiod, Apollodorus, and Pausanias, standard page numbers failed: manuscripts were distributed across multiple recensions, codices, and translations.

Mythographers developed **structural coordinate addressing** (e.g., *Iliad* Book 1, line 1; Apollodorus *Library* 2.4.1), anchoring citations to invariant textual units rather than transient physical pages.

### Hellenic Studies & Canonical Text Services (CTS)
In contemporary classical scholarship, the **Homer Multitext Project** and Hellenic studies institutions formalized this into public citation standards: the **Canonical Text Services (CTS) URN** architecture (`urn:cts:greekLit:tlg0012.tlg001:1.1`).
A CTS URN separates:
- The work identity from its specific edition or physical manifestation.
- Citations from transient line offsets, indexing texts into hierarchical, addressable citation nodes (book $\to$ poem $\to$ stanza $\to$ line $\to$ word token).

### The Translation into `refverify` and `mdrag`
In `refverify`, our use of `phosphene-mdrag` AST block coordinates (`doc:sec:methods:p2:cite:1`) directly inherits this classical lineage:
- **ID-Path and Block Parity:** Just as Homeric scholarship addresses lines independently of modern typography, `refverify` addresses claims, citations, and formulas independently of markdown line breaks or font renderings.
- **Verbatim Textual Provenance:** Verifying that a quoted passage or cited equation in a scientific paper is a verbatim transcription of the primary source or record.

---

## 3. The Lexicon Posture: Inform and Rehearse, Do Not Naively Gate

As established in Brandomian inferentialism (*Making It Explicit*) and the Phosphene lexicon study posture (`concepts/lexicon-study-posture.md`):

```
                                  ▲
                                 / \
                                /   \
                               /     \
                              /       \
                             /  NAIVE  \    "Term X does not match Dictionary D:
                            / GATING ❌ \    BLOCK MANUSCRIPT"
                           /─────────────\   (Catastrophic: rejects innovation)
                          /   INFORM &    \
                         /   REHEARSE ✅   \  "Make explicit the commitments of X;
                        /───────────────────\  trace idiolect divergence from norm"
```

### Why Naive Gating Around Lexicons is a Category Error
1. **Meaning is Inferential Role, Not Fixed Reference:** Meaning in active science is forged under pressure from empirical phenomena. A dictionary definition records past consensus; living science progresses by redefining boundaries.
2. **Idiolect as Cognitive Record:** A researcher's private language (idiolect) is the raw trace of their thinking. Gating around a community lexicon would crush scientific discovery at its inception.
3. **The Role of the Instrument:**
   - **Provoke:** Challenge unstated assumptions ("By asserting $T$, do you accept consequence $K$?").
   - **Rehearse:** Walk the inferential paths across blocks to surface where premises and conclusions hold or fracture.
   - **Inform:** Present an auditable divergence map showing how the local idiolect sits relative to community norms—without enforcing a blocking gate.

---

## 4. Technical Architecture: Namespace-Isolated Lexicon Tracking

To allow research programs to develop novel vocabularies without interference or naive gating, `refverify` implements **Namespace-Isolated Lexicon Tracking**:

```
                       ┌───────────────────────────────────────────────┐
                       │   Manuscript AST Block Coordinates (mdrag)    │
                       └───────────────────────┬───────────────────────┘
                                               │
                               Traverse Blocks │ doc:sec:p:token
                                               ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        REFVERIFY TEXTUAL & LEXICAL PROVENANCE                          │
│                                                                                        │
│  1. Local Namespace Lexicon Registry        2. Corpus Authority Port (LookupClient)    │
│     Isolated by research program:              Provides reference domain baseline:     │
│     :prog.valence/lexicon:*                    - MeSH, UMLS, Wikitext, Crossref        │
│     (Stipulations, axioms, genus/diff)         (Rigid designations vs. family clusters)│
│                 │                                                  │                   │
│                 └─────────────────────┬────────────────────────────┘                   │
│                                       ▼                                                │
│  3. Verbatim & Provenance Engine (DFT Core)                                            │
│     - Verbatim Rendition Check: Does quoted text match primary text byte-for-byte?     │
│     - Formulaic Parity Check: Do equations match cited mathematical sources?           │
│     - Data Point Anchoring: Are empirical scalars bound to explicit dataset records?   │
│                                       │                                                │
│                                       ▼                                                │
│  4. Inferential Divergence Mapper (Informing, Not Gating)                             │
│     - Intrasite Inconsistency: Definition in Section 2 diverges in Section 5.          │
│     - Disciplinary Shift: Community norm differs from local idiolect (Annotated).      │
└───────────────────────────────────────┬────────────────────────────────────────────────┘
                                        │
                                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                     SURGICAL FRONTMATTER INJECTION (frontmatters)                      │
│                                                                                        │
│   Shadow patch frontmatter with provenance & lexicon readings:                         │
│   lexicon_provenance:                                                                  │
│     status: INFORMED                                                                   │
│     namespace: "prog.valence.monograph"                                                │
│     stipulated_terms: 14                                                               │
│     verbatim_quotations_verified: 8/8                                                  │
│     inferential_divergences:                                                           │
│       - term: "valence gradient"                                                       │
│         stipulated_at: "doc:sec:1:p3"                                                  │
│         shift_at: "doc:sec:4:p7"                                                       │
│         note: "stipulated as directional vector; asserted colloquially as scalar sum"  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Technical Invariants of Verbatim & Lexical Provenance

1. **Verbatim Fidelity (`:projection.apparatus/textual-reference`):**  
   Quoted text and cited mathematical formulas must match upstream sources within normalized punctuation tolerances. Discrepancies are flagged with character-level diffs.
2. **Namespace Isolation:**  
   Lexicon terms defined within a research program's namespace (`:prog.NAME/lexicon:*`) are evaluated for internal coherence within that namespace. External corpus ontologies inform the reading, but never clobber or gate local stipulations.
3. **Decoupled Telemetry:**  
   Bibliographic verification continues to gate on verifiable metadata (`references_verified: true/false`, `gate: PASS/WARN/BLOCK`). Lexicon evaluation outputs informative reading maps (`lexicon_provenance: INFORMED`), never synthetic gates.
