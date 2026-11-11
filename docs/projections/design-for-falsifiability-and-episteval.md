---
uri: phosphene.tooling/refverify/docs/projections/design-for-falsifiability-and-episteval
owner: edphos
status: proposed
created: 2026-11-10
updated: 2026-11-10
namespace: phosphene.tooling.refverify.projections.epistemics
coordinates:
  - :projection.epistemics/dff-axiomatics
  - :projection.boundary/episteval-vs-refverify
  - :projection.epistemics/defeater-trees
  - :projection.epistemics/deductive-pre-clearance
builds-on:
  - phosphene.tooling/refverify/docs/projections/conceptual-and-terminological-verification
  - phosphene.tooling/refverify/docs/ethos
converges-with:
  - team/SPEC_LOG
  - team/platform/doc-standards
abstract: |
  Formalizes Design for Falsifiability (DFF) as the axiomatic scientific counterpart
  to software's Design for Testability (DFT). Explicitly documents the architectural division
  of labor between episteval (inferential validity, warrant derivation graphs, defeater sets,
  and inferential retreat) and refverify (scholarly apparatus, verbatim factual provenance,
  and data coordinate anchoring). Details the "for-free" deductive pre-clearance phase between
  hypothesis formation and testbed execution, projecting these principles outward for other teams.
---

# Projections — Design for Falsifiability (DFF) & The `episteval` / `refverify` Division of Labor

> **Coordinate Namespace:** `phosphene.tooling.refverify.projections.epistemics.*`  
> Extending Design for Testability (DFT) into Design for Falsifiability (DFF) under strict Logic/IO and Inferential/Provenance boundaries.

---

## 1. The Lineage: From DFT to DFF

In Phosphene software engineering, **Design for Testability (DFT)** is not an external audit tacked onto a finished codebase; it is an **intrinsic structural property** established before writing functional internals:
- Every state transition must be observable and assertable;
- Logic is decoupled from I/O through ports and adapters so transitions can be tested hermetically;
- Boundary conditions and invariant violations trigger immediate, non-negotiable test failures.

In scientific research, **Design for Falsifiability (DFF)** extends this identical axiomatic method from code to scientific hypotheses:

> **A hypothesis cannot be admitted into a research program unless its falsification conditions, complement space, and inferential defeater trees are formally specified as structural properties prior to empirical execution.**

Falsifiability is not a virtue you hope a peer reviewer probes after a 50-page monograph is written. It is an **intrinsic architectural constraint designed into the claim up front**.

---

## 2. Decomplecting Inference from Provenance: `episteval` vs. `refverify`

A critical architectural failure mode in scientific automation is conflating **inferential evaluation** with **scholarly and factual provenance**. 

Per Phosphene platform standards, these are separate concerns handled by two distinct packages:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        DECOMPLECTED RESEARCH ARCHITECTURE                              │
├──────────────────────────────────────────┬─────────────────────────────────────────────┤
│         phosphene/refverify              │            phosphene/episteval              │
│   (Scholarly Apparatus & Provenance)     │    (Inferential & Epistemic Evaluation)     │
├──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ Primary Role:                            │ Primary Role:                               │
│ The APPARATUS OF RECORD & PROVENANCE.    │ The INFERENTIAL DEDUCTION & DEFEAT ENGINE.  │
│                                          │                                             │
│ Key Responsibilities:                    │ Key Responsibilities:                       │
│ • Bibliographic identifier resolution    │ • Warrant derivation trees & hypergraphs    │
│ • Verbatim quote & formulaic verification│ • Design for Falsifiability (DFF) contracts │
│ • Empirical scalar & dataset coordinate  │ • Explicit defeater / undercutter sets      │
│   anchoring (e.g. data:p4:scalar1)       │ • Inferential retreat path mapping          │
│ • Local glossary & corpus lexicon indices│ • Dual-faceted state (numeric + structural) │
│ • Informative scorekeeping (NO gating)   │ • Regime boundaries & epistemic truth values│
├──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ Core Primitive:                          │ Core Primitive:                             │
│ Verbatim Fact & Coordinate Provenance    │ Inferential State (`EpistemicState`)        │
└──────────────────────────────────────────┴─────────────────────────────────────────────┘
```

### Why Falsifiability Belongs Exclusively in `episteval`
Falsifiability is an **inferential property**, not a typographic or registry property:
- `refverify` verifies that an empirical observation $O$ at coordinate $C$ has exact scalar value $V$, that it was gathered under methodology $M$, and that the cited literature matches primary registries verbatim.
- `episteval` takes that verified factual record and executes the inferential derivation: checking whether $V$ enters the complement space $\mathcal{S}_{\text{forbidden}}$ of hypothesis $H$, triggering a formal defeater node and updating the `EpistemicState`.

`refverify` guarantees that the facts fed into the inference engine are pristine and tamper-evident; `episteval` determines whether those facts falsify the thesis.

---

## 3. The DFF Axiomatic Method in `episteval`

Within `episteval`, DFF is formalized through three structural axioms:

### Axiom 1: The Forbidden State Axiom ($\mathcal{S}_{\text{forbidden}} \ne \emptyset$)
Every hypothesis admitted into the evaluation pipeline must define its non-empty complement state space:
$$\mathcal{S}_{\text{hypothesis}} \cap \mathcal{S}_{\text{forbidden}} = \emptyset \quad \text{where} \quad \mathcal{S}_{\text{forbidden}} \ne \emptyset$$
If a proposed model can accommodate any empirical outcome via post-hoc parameter adjustments (e.g., adding epicycles or unbounded latent variables), $\mathcal{S}_{\text{forbidden}} = \emptyset$. The model is rejected at the entry layer as mathematically unfalsifiable.

### Axiom 2: Explicit Defeater & Undercutter Trees
Borrowing from formal epistemology (Pollock / Toulmin / Brandom), every claim in `episteval` carries an explicit graph of:
- **Rebutting Defeaters:** Empirical observations that directly entail $\neg H$.
- **Undercutting Defeaters:** Observations that sever the warrant connecting evidence $E$ to claim $H$ (e.g., systematic measurement bias, demographic confounding).

### Axiom 3: Pre-Registered Inferential Retreat
In traditional science, when an experiment yields anomalous data, researchers face the Duhem-Quine ambiguity: did the hypothesis fail, or did an auxiliary assumption fail?
Under DFF, the inferential derivation tree pre-registers the **retreat path**:
- Which auxiliary assumptions are core nomological commitments;
- Which parameters are subject to revision;
- At what threshold anomaly the core hypothesis must be fully abandoned rather than shielded.

---

## 4. Asking Questions "For Free": Deductive Pre-Clearance

Between **hypothesis formation** and **experiment/testing design**, researchers have an extraordinary opportunity that is frequently squandered: **you can ask dozens of critical questions "for free" before spending a single dollar of empirical budget (compute, field trials, or wet lab).**

```
Hypothesis Formation
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│        DEDUCTIVE PRE-CLEARANCE (Zero Empirical Budget)          │
│                                                                 │
│  1. Dimensional Analysis & Units Invariance                     │
│     Does the equation balance? (MLT dimensions / SI units)      │
│                                                                 │
│  2. Thermodynamic & Conservation Feasibility                    │
│     Does it require negative entropy or impossible ΔG'?         │
│                                                                 │
│  3. Requisite Variety Bounds (Ashby's Law)                      │
│     Is regulator variety >= disturbance variety? (VR >= VD - VO)│
│                                                                 │
│  4. Extreme Boundary Probing                                    │
│     Evaluate at limits: t -> ∞, T -> 0, N -> 1, N -> ∞.         │
│     Do limits produce singularities or absurdities?             │
│                                                                 │
│  5. Inferential Entailment & Auxilary Decoupling                │
│     What unstated premises are required for H to hold?          │
└────────────────────────────────┬────────────────────────────────┘
                                 │ Passed Free Gauntlet
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              EXPERIMENT & TESTBED DESIGN (Costly I/O)           │
│                                                                 │
│  • Targeted solely at remaining un-eliminated degrees of freedom │
│  • Pre-registered defeater thresholds wired directly to inputs  │
└─────────────────────────────────────────────────────────────────┘
```

1. **Dimensional Analysis:** Interrogating whether proposed equations conserve units across tensors and scalars.
2. **Thermodynamic Feasibility:** Checking whether postulated biochemical or cognitive mechanisms violate free energy constraints ($\Delta G' < 0$) or second-law boundaries.
3. **Requisite Variety Gating (Ashby):** Ensuring that proposed control structures possess sufficient internal states to regulate the environmental disturbances they claim to manage ($\mathcal{V}_R \ge \mathcal{V}_D - \mathcal{V}_O$).
4. **Asymptotic Limit Testing:** Probing mathematical behavior at zero, infinity, and boundary transitions. If a model predicts infinite biomass or negative probability at the limit, it is broken deductively.

Every hypothesis eliminated during this pre-clearance phase saves weeks of empirical simulation and lab resources.

---

## 5. Projection for Collaborating Teams & Platforms

For platform teams, research stables, and external laboratories adopting this architecture, we project the following organizational guidelines:

1. **Adopt DFF as an Entry Gate, Not an Exit Review:**  
   Require research proposals and model specifications to include a formal DFF block in their frontmatter:
   ```yaml
   dff_specification:
     hypothesis_id: "H-VALENCE-01"
     forbidden_outcomes:
       - "Reversal of capacity reallocation depth gamma > 0.95 without lineage extinction"
       - "Group heritability H2_group < 0.20 in coalesced multiorganismal state"
     retreat_path: "Downgrade from universal ratchet to contingent ecological guild"
   ```
2. **Preserve Tool Boundaries Religiously:**  
   Do not ask `refverify` to evaluate whether a hypothesis is true or falsifiable; use it to verify that citations, formulas, and data values are accurate and verbatim. Delegate inferential evaluation, defeater processing, and falsification tracking entirely to `episteval`.
3. **Automate the "For Free" Deductive Suite:**  
   Build automated pre-clearance linters that run unit analysis, asymptotic limit checks, and variety bounds in CI/CD before allocating cluster compute or laboratory assets.
