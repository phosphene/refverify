---
uri: phosphene.tooling/refverify/docs/projections/llm-rag-critique-and-deterministic-provenance
owner: edphos
status: proposed
created: 2026-11-11
updated: 2026-11-11
namespace: phosphene.tooling.refverify.projections.meta
coordinates:
  - :projection.meta/rag-citation-critique
  - :projection.meta/correctness-vs-faithfulness
  - :projection.meta/deceptive-grounding
  - :projection.apparatus/deterministic-redundancy
  - :projection.apparatus/verbatim-extraction
builds-on:
  - phosphene.tooling/refverify/docs/projections/conceptual-and-terminological-verification
  - phosphene.tooling/refverify/docs/projections/design-for-falsifiability-and-episteval
  - phosphene.tooling/refverify/docs/ethos
converges-with:
  - team/specs/topic-scoped-calculation-and-verification-architecture
  - team/platform/doc-standards
abstract: |
  Critique of naive Retrieval-Augmented Generation (RAG) and probabilistic LLM-as-judge
  citation verification systems (e.g. consensus.app). Synthesizes recent empirical literature
  on citation unfaithfulness (Wallat 2025), deceptive grounding and entity-swapping (Caruzzo 2026),
  and attribution drift (Dassen 2026). Explains why neural citation chips generate misplaced trust,
  and specifies Phosphene's deterministic architecture: AST coordinate block addressability,
  constrained verbatim extraction, and multi-layered epistemic redundancy.
---

# Projections — Meta-Critique of LLM/RAG Citation Verification & The Mandate for Deterministic Provenance

> **Coordinate Namespace:** `phosphene.tooling.refverify.projections.meta.*`  
> Why probabilistic RAG citation verification produces misplaced trust, and how deterministic AST provenance resolves it.

---

## 1. The Generative RAG Illusion

The prevailing paradigm in AI-assisted scientific research relies on **Retrieval-Augmented Generation (RAG)** coupled with an LLM (such as OpenAI models or platforms like `consensus.app`) acting as an end-to-end synthesizer and verifier. In this model, an agent retrieves relevant papers from a vector index, generates an analytical summary, and attaches citation "chips" or numeric brackets (`[1]`, `[Doe 2024]`) to individual sentences.

This approach creates a powerful **cosmetic authority trap**:
- The prose is fluent, balanced, and stylistically indistinguishable from peer-reviewed literature;
- Every cited DOI resolves to an authentic published paper in Crossref or PubMed;
- The user is presented with visual evidence of grounding.

However, recent empirical evaluations of commercial and frontier RAG verifiers demonstrate that **grounding in real retrieved sources does not guarantee that the cited document genuinely supports the claim attached to it.**

The failure of naive RAG is not primarily fabricated or hallucinated references (which simple DOI checkers easily catch); rather, it is **citations that look completely authentic while the model's reliance on them is fictitious, smoothed, or post-rationalized.**

---

## 2. Empirical Failure Modes in RAG Citation Systems

Recent literature across NLP and biomedical informatics identifies three distinct, severe failure modes inherent to probabilistic generation and RAG-based citation:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        EMPIRICAL RAG CITATION FAILURE TAXONOMY                         │
├──────────────────────────────┬──────────────────────────────┬──────────────────────────┤
│    Post-Rationalization      │     Deceptive Grounding      │    Attribution Drift     │
│  (Correctness != Faithfulness)│    (Entity-Swapping Collisions│   (Long-Form Decay)      │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────┤
│ Model writes from internal   │ Real paper, real citation,   │ Over extended outputs,   │
│ parametric weights, then     │ real fact—attributed to the  │ model loses track of     │
│ attaches plausible citation. │ wrong entity (e.g. Drug Y's  │ source spans; cites      │
│ Rate: up to 57% unfaithful.  │ efficacy given to Drug X).   │ earlier sources for      │
│ (Wallat et al., 2025)        │ Rate: 8%–87% error.          │ subsequent unrelated     │
│                              │ (Caruzzo et al., 2026)       │ claims. (Dassen 2026)    │
└──────────────────────────────┴──────────────────────────────┴──────────────────────────┘
```

### A. Correctness Is Not Faithfulness (Post-Rationalized Attributions)
The fundamental conceptual division, formalized by **Wallat et al. (2025)**, separates:
- **Citation Correctness:** Does the cited document broadly support or align with the asserted statement?
- **Citation Faithfulness:** Did the model actually derive its assertion from that document, or did it generate the text from its pre-trained parametric weights and subsequently attach a plausible-looking source to justify it?

Wallat et al. demonstrated that **up to 57% of citations in standard RAG pipelines lack faithfulness**. The model hallucinates the *dependence relation* rather than the paper. Penzkofer and Baumann (2024) and Shen et al. (2025) corroborate that how generative models leverage internal versus retrieved knowledge remains opaque, rendering citation chips untrustworthy as epistemic warrants.

### B. Deceptive Grounding & Entity-Swapping Collisions
Even more dangerous is the failure mode identified by **Caruzzo et al. (2026)** in clinical and technical RAG systems:
- A medical query regarding *Drug X* produces a response summarizing clinical trial results with valid citations.
- The trial results are real, the statistics are accurate, and the citations resolve to peer-reviewed publications.
- **The Fatal Flaw:** The trial results actually belong to *Drug Y*. The model substituted the entity while preserving the syntactic and statistical structure of the retrieved context.

Standard automated verification—including NLI (Natural Language Inference) models and LLM-as-judge evaluators—consistently **pass these responses as verified** because the predicate structure matches the document text. Crucially, Caruzzo et al. found that domain-specialized, fine-tuned biomedical models reached error rates of **86.7%**, demonstrating that domain fine-tuning amplifies rather than eliminates deceptive grounding.

### C. Attribution Drift & Synthetic Trust Inflation
**Dassen et al. (2026)** demonstrate that citations artificially inflate reader trust regardless of validity. In long-form scientific documents, source-attribution signals decay monotonically: the longer the generated section, the higher the probability that citations from paragraph 1 are recycled or smoothed across paragraphs 4 and 5 to support completely unrelated claims.

Furthermore, **Signé et al. (2026)** evaluated hybrid generative extraction and showed that exact quotation accuracy drops **below 40% in technical domains**, with models routinely hallucinating phrases within supposedly verbatim quotes.

---

## 3. Why Probabilistic "LLM-as-Judge" Evaluators Cannot Fix This

Many platforms attempt to solve RAG unfaithfulness by adding a second LLM layer (an "evaluator" or "judge" prompt). This introduces second-order epistemic failure:

1. **Shared Inductive Bias:** The judge LLM shares the same linguistic and parametric training distributions as the generator. It is equally susceptible to the aesthetic plausibility of smoothed academic prose.
2. **NLI Metric Conflation:** As noted by Zhang et al. (2024) and Fadeeva et al. (2025), automated faithfulness metrics conflate factuality with attribution. An evaluator labels a statement "verified" if it matches general world knowledge, even when the cited source says nothing of the sort.
3. **Non-Determinism & Unbounded Latency:** A verification gate that returns `PASS` on turn 1 and `BLOCK` on turn 2 due to sampling temperature cannot serve as a reliable gate in scientific CI/CD pipelines.

---

## 4. The Phosphene Deterministic Alternative

To establish genuine epistemic provenance under the aegis of public science, `phosphene/refverify` and `phosphene/episteval` replace probabilistic generative judgment with **deterministic, redundant, and structurally constrained verification**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   DETERMINISTIC & REDUNDANT PROVENANCE ARCHITECTURE                    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Structural AST Demarcation (phosphene-mdrag)                                        │
│    - Claims and citations bound to immutable coordinates (doc:sec:p3:cite:1)           │
│    - Eliminates citation floating, attribution drift, and scope bleed                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. Exact Bibliographic Reconciliation (phosphene-refverify)                            │
│    - Multi-registry query: Crossref, OpenAlex, Semantic Scholar, arXiv                │
│    - Multi-tier mathematical scoring [0, 100]; zero neural hallucination of existence  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Constrained Verbatim Extraction & Data Formalism Parity                             │
│    - Byte-for-byte quotation checking against source texts                             │
│    - Mathematical formula and empirical scalar anchoring (MLT units, SI constants)     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. Inferential Defeat & Epistemic Derivation (phosphene-episteval)                     │
│    - Warrant derivation hypergraphs with explicit defeater / undercutter sets          │
│    - Pre-registered forbidden complement spaces (S_forbidden != empty)                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. Lossless Frontmatter Stamping (phosphene-frontmatters)                              │
│    - Surgical CST shadow patching; machine telemetry injected without human corruption │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Invariant 1: Invariant Coordinate Block Anchoring (CTS / Hickey Parity)
A citation must never exist as a floating typographical token in an unconstrained string. By parsing manuscripts into explicit AST blocks (`phosphene-mdrag`), every assertion and citation is bound to a deterministic coordinate (`doc:sec:methodology:p2:cite:1`). If the author or model alters surrounding paragraphs, the coordinate anchor preserves the exact structural link to the cited evidence.

### Invariant 2: Mathematical Registry Reconciliation Over Vector Similarity
Instead of relying on cosine similarity over dense vector embeddings (which routinely collapses antonyms, related drugs, and competing hypotheses), `refverify` executes deterministic metadata reconciliation:
- Author surname sequence matching;
- Normalized letter-digit Levenshtein title ratios;
- Exact publication year offsets ($\pm 1$ year for preprints);
- Authoritative DOI/arXiv resolution via primary registries.

### Invariant 3: Verbatim Textual & Formalism Parity
In technical literature, paraphrasing is where semantic smoothing and entity-swapping occur. `refverify` requires that:
- Quoted textual evidence match primary source spans byte-for-byte;
- Empirical scalars cited in prose match underlying dataset records;
- Equations balance dimensionally (units invariance) before any empirical claim is admitted.

### Invariant 4: Decomplecting Provenance from Inferential Evaluation
By separating `refverify` (the apparatus of record, bibliographic validity, and textual provenance) from `episteval` (the inferential derivation engine evaluating defeaters and truth-functional warrants), the system avoids the fatal error of using one neural model to judge both whether a citation exists and whether it logically supports the claim.

---

## 5. Architectural Comparison: Naive RAG vs. Phosphene Deterministic Pipeline

| Dimension | Naive Generative RAG (e.g. consensus.app / OpenAI) | Phosphene Refverify / Episteval Architecture |
|---|---|---|
| **Citation Attachment** | Post-hoc generative token generation; unfaithful smoothing (Wallat 2025). | Pre-registered coordinate binding (`doc:sec:p:cite`) via AST parser. |
| **Entity Verification** | Probabilistic vector cosine similarity; high entity-swapping failure (Caruzzo 2026). | Deterministic metadata reconciliation & entity cross-check across primary registries. |
| **Quotation Fidelity** | Neural generation; <40% exact extraction accuracy (Signé 2026). | Verbatim string comparison against canonical digital texts. |
| **Evaluation Method** | LLM-as-judge or NLI semantic entailment (blind to entity collisions). | Multi-tier mathematical scoring $[0, 100]$ + formal defeater trees in `episteval`. |
| **Audit Persistence** | Ephemeral chat transcript or synthetic PDF with floating chips. | Lossless YAML frontmatter shadow patching (`phosphene-frontmatters`) + JSON reports. |
| **Failure Modes** | Silent hallucination of dependency; smooth, persuasive inaccuracies. | Immediate deterministic gate stop (`BLOCK` on mismatch, retraction, or collision). |

---

## 6. Synthesis

A citation chip in a generative AI response is proof of retrieval, not proof of support. 

In public science and high-assurance engineering, treating probabilistic RAG as an authority oracle creates a veneer of rigor that actively conceals deep misattributions and post-rationalized claims. True scientific verification demands **structural determinism**: isolating document AST blocks, mathematically reconciling registry metadata, verifying textual and formal parity byte-for-byte, and formally evaluating inferential defeaters in an isolated derivation engine.
