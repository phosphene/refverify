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
builds-on:
  - phosphene.tooling/refverify/docs/mdrag-and-frontmatters-innovations
  - phosphene.tooling/refverify/docs/architecture
converges-with:
  - team/platform/doc-standards
  - team/platform/md-rags/hickey
abstract: |
  Technical specification projecting the structural capacities developed in refverify
  (AST node demarcation, lossless CST shadow patching, and Hickey coordinate block addressing)
  to general software systems where Markdown serves as the system of record. Analyzes concrete
  data structures, parser failure modes, state synchronization protocols, and tree-addressing
  mechanics across ticketing, federated research wikis, and structured block namespacing.
---

# Projections — Technical Architecture & Problem Space for Structured Markdown

> **Coordinate Namespace:** `phosphene.tooling.refverify.projections.*`  
> Formal decomposition of AST demarcation, Concrete Syntax Tree (CST) shadow patching, and coordinate-addressed block graphs.

---

## 1. Technical Problem Space: The Failure of String-Oriented Tooling

When engineering teams and research platforms use Markdown as an authoritative system of record—for ticket trackers, architectural records, or federated wikis—tooling frequently treats files as flat strings or raw character buffers.

This string-oriented approach introduces three deterministic failure modes in automated software workflows:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          STRING-ORIENTED PARSER COLLAPSE MODES                         │
├──────────────────────────────┬──────────────────────────────┬──────────────────────────┤
│    Boundary Permeability     │  Destructive Serialization   │  Transient Coordinate    │
│       (Regex Bleed)          │       (AST -> Dump)          │        Invalidation      │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────┤
│ Regex `^## ` matches inside  │ Round-trip parsing drops     │ Line-number or heading-  │
│ code fences, blockquotes,    │ comments, strips whitespace, │ slug links break under   │
│ or nested lists. Scope has   │ reorders mapping keys, and   │ document edits. No       │
│ no syntax-tree awareness.    │ mangles multiline scalars.   │ invariant content hash.  │
└──────────────────────────────┴──────────────────────────────┴──────────────────────────┘
```

1. **Boundary Permeability:** Regular expressions cannot evaluate lexical context. A pattern scanning for `### T-\d+` cannot distinguish a ticket header from a code fence containing an example shell session (`echo "### T-123"`), leading to false block splits and syntax leakage.
2. **Destructive Serialization:** Standard parser libraries parse Markdown or YAML into transient in-memory dictionaries or ASTs that discard trivia (whitespace, comments, column offsets, multiline scalar styles). Serializing back to disk destroys the human author's formatting.
3. **Transient Coordinate Invalidation:** Referencing document sections via URI fragments (`#verification-results`) or line ranges (`L45-L60`) is brittle. Any upstream insertion or heading rephrasing breaks all downstream references.

---

## 2. Technical Primitives in `mdrag` & `frontmatters`

`refverify` decomposes these problems into three distinct technical layers:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. AST Structural Demarcation (phosphene-mdrag)                                        │
│    Token Stream -> Lexical Depth Stack -> Block AST Nodes (type, attrs, children)       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. Dual-Layer CST Shadow Patching (phosphene-frontmatters)                             │
│    Source Buffer -> Concrete Syntax Tree (with Trivia) + Open Domain Model (OWA)       │
│    Surgical Splice: Target Key Mutation -> Token Offset Recalculation -> Clean Output  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Triadic Block Addressability (Hickey Coordinates)                                   │
│    Document Coordinate : Block Type / Discriminator : Content Anchor                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Layer 1: AST Structural Slicing (`:projection.capacity/ast-extraction`)
Instead of line-based heuristics, `phosphene-mdrag` parses Markdown into an AST where block boundaries are governed by syntax tree depth:
- Headings establish scope frames on a stack.
- A block starting at heading level $L$ terminates strictly when encountering an adjacent heading of level $\le L$, or on EOF.
- Fenced code blocks (`code_block`), HTML blocks, and blockquotes are leaf or container nodes evaluated within their own isolated grammar rules, preventing internal token collisions.

### Layer 2: Dual-Layer Shadow Patching (`:projection.capacity/shadow-patching`)
`phosphene-frontmatters` maintains two parallel representations of the document header:
1. **The CST (Concrete Syntax Tree):** A tokenized stream tracking byte offsets, comment tokens (`# ...`), whitespace sequences, and scalar quotation styles (`|`, `>`, `"`, `'`).
2. **The Open Domain Model:** A typed dictionary/model operating under the Open-World Assumption (OWA). Unknown keys are held in an open set; known audit keys are typed and validated.

When mutating metadata:
- The domain model updates the target values.
- The shadow patcher identifies the exact byte span occupied by the target key in the CST.
- It performs a surgical replacement of that token span only, leaving all surrounding tokens, preceding comments, and trailing layout unaltered.

### Layer 3: Coordinate Block Addressing (`:projection.capacity/block-addressability`)
Drawing on Rich Hickey's coordinate design:
- Blocks are addressed via namespaced coordinates: `namespace:collection/entity:block-id`.
- Coordinates separate the *identifier* of the block from its mutable position in the file.
- Changes to surrounding paragraphs do not alter the coordinate identity of adjacent blocks.

---

## 3. Domain 1: Markdown-Native Ticketing & Lifecycle Engines

> **Coordinate:** `:projection.domain/markdown-ticketing`  
> Technical implementation for teams maintaining git-native issue trackers (`TICKETS-*.md`).

### The Architecture of a Markdown Ticket System
Teams running git-native workflows store tasks in structured Markdown files where each ticket is an AST heading subtree:

```markdown
### T-581: Implement asynchronous verification pipeline
- Status: OPEN
- Priority: P1
- Owner: edphos
- Acceptance Criteria:
  - [ ] Non-blocking task dispatch via taskflow
  - [ ] Event loop utilization < 15% under load
<!-- Note: upstream PR #42 must merge first -->
```

### Technical Workflow with `mdrag` and `frontmatters`

```
  Git Push / CI Trigger
            │
            ▼
┌───────────────────────┐
│  mdrag AST Slicer     │ ──► Isolates block: Heading(level=3, text="T-581...")
└───────────┬───────────┘     Collects child AST: List(items=[...]), Comment(...)
            │
            ▼
┌───────────────────────┐
│ Execution Engine      │ ──► Runs tests associated with T-581 criteria
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ CST Shadow Patcher    │ ──► Slices token `- Status: OPEN`
└───────────┬───────────┘     Mutates to `- Status: DELIVERED`
            │                 Appends `- Verified-In: commit 9af079bd`
            ▼                 Preserves `<!-- Note: upstream PR #42... -->` exactly
  Atomic Git Commit
```

1. **AST Isolation:** `mdrag` traverses the file AST, locates the heading matching `r"^T-\d+"`, and returns the discrete AST node containing only that ticket's properties and acceptance criteria.
2. **Deterministic Status Patching:** When CI executes the tests, the runner updates the ticket status. Instead of rewriting `TICKETS.md` via regex (which risks mangling adjacent tickets or stripping comments), the shadow patcher performs an in-situ token replacement.
3. **Lockless Concurrent Modifications:** Because tickets are delineated AST blocks, automated tools can compute git merge resolutions at the AST block level rather than line-by-line, reducing merge conflicts when multiple agents update different tickets in the same file.

---

## 4. Domain 2: Federated Knowledge Wikis & Block Namespacing

> **Coordinates:** `:projection.domain/federated-wiki-corpora`, `:projection.domain/structured-block-namespacing`  
> Technical implementation for multi-author research wikis and coordinate-indexed knowledge graphs.

### The Problem of Granular Addressing in Distributed Wikis
In federated wiki systems (e.g., `research-wiki/wiki/`), documents are technical assets carrying formal definitions, proofs, and claims.
When a document in `math.logic/` references a specific lemma inside `phil.epistemics/foundations.md`, conventional markdown links (`[Lemma 2](foundations.md#lemma-2)`) fail when:
- The author renames `## Lemma 2` to `## Lemma 2 (Soundness)`;
- The file is split or relocated within the namespace hierarchy;
- The consuming tool needs to transclude the exact lemma text into an evaluation harness.

### Technical Implementation of Coordinate Block Namespacing

```
                federated-wiki/
                ├── math.logic/
                │   └── incompleteness.md
                │       ├── Coordinate: :math.logic/goedel:block:first-theorem
                │       └── Body: AST Paragraph + Proof List
                └── phil.epistemics/
                    └── foundations.md
                        └── Points to: :math.logic/goedel:block:first-theorem
```

1. **Deterministic Coordinate Assignment:**  
   `mdrag` assigns each heading, list, or formal paragraph a block coordinate derived from the document's namespaced URI and a stable block slug:
   ```
   Coordinate = <namespace> / <document_id> : <block_type> : <block_slug>
   Example: :sci.bio/valence:lemma:cambrian-gradient
   ```
2. **AST Transclusion Engine:**  
   When a document transcludes or verifies a referenced block, `mdrag` retrieves the target AST node directly without loading or evaluating surrounding commentary.
3. **Lossless Graph Stamping:**  
   Knowledge crawlers mapping relationships (`inherits-from`, `critiques`, `refines`) use shadow patching to write edge lists into the document's YAML frontmatter:
   ```yaml
   ---
   uri: sci.bio/valence
   coordinates:
     - :sci.bio/valence:lemma:cambrian-gradient
   fka_edges:
     - predicate: refines
       target: :sci.bio/chemiosmosis:sec:proton-gradient
       verified_hash: sha256:d41d8cd98f00b204e9800998ecf8427e
   ---
   ```
   The researcher's manual annotations, draft markers, and custom keys are preserved byte-for-byte.

---

## 5. Domain 3: High-Assurance Technical Specifications & Protocols

> **Coordinate:** `:projection.tier/external-compliance-critical`  
> Technical implementation for normative technical standards (RFCs), compliance contracts, and clinical protocol manifests.

### The Requirements Verification Model
In high-assurance technical writing (e.g., IETF RFCs with RFC 2119 keywords `MUST`, `SHOULD`, `REQUIRED`), automated compliance tools must verify that implementations fulfill every normative clause.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ AST Parser isolates: Heading(level=2, text="Security Considerations")                   │
│ Extracts child node: Paragraph("An implementation MUST NOT reuse nonces...")           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Verification Engine maps requirement to test suite: test_nonce_reuse_prevention()      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Shadow Patcher stamps verification record in specification frontmatter:                │
│   conformance_audit:                                                                   │
│     rfc2119_must_total: 14                                                             │
│     rfc2119_must_verified: 14                                                          │
│     audit_gate: PASS                                                                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Syntactic Normative Extraction:** `mdrag` AST visitors scan paragraph children for uppercase normative keywords, indexing each as an addressable test target (`spec:sec:4.1:req:nonce-reuse`).
2. **Audit Telemetry Persistence:** `frontmatters` writes the resulting verification proofs into the file's metadata header without altering standard RFC layout or formatting conventions.

---

## 6. Technical Invariant Summary

| System / Component | Failure Mode Prevented | Invariant Enforced |
|---|---|---|
| **`phosphene-mdrag` (AST Parsing)** | False-positive heading matches inside code fences, tables, and blockquotes. | Block boundaries are determined strictly by AST node hierarchy, never flat regex matching. |
| **`phosphene-frontmatters` (Shadow Patching)** | Loss of human comments, reordering of YAML mappings, clobbering unmodeled schema keys. | Surgical byte-range token replacement; CST trivia (whitespace, comments) preserved with zero mutation outside target keys. |
| **Hickey Coordinate Addressing** | Link rot from heading renames; coarse-grained document retrieval. | Immutable, namespaced coordinate anchors (`namespace/doc:type:id`) decoupled from file line numbers. |
