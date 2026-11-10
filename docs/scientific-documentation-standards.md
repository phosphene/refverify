---
uri: phosphene.tooling/refverify/docs/scientific-documentation-standards
owner: edphos
status: canonical
created: 2026-11-10
updated: 2026-11-10
namespace: phosphene.tooling.refverify
coordinates:
  - :phos.standards/scientific-docs
  - :epistemics/calibration
  - :epistemics/literate-engineering
builds-on:
  - phosphene.tooling/refverify/docs/ethos
converges-with:
  - team/platform/doc-standards
  - meta/reference/writing-and-comms-standards
abstract: |
  Defines the Phosphene standards for scientific documentation within refverify:
  literate docstrings, the prolix vs. specification form distinction, and epistemic
  basis calibration tiers across scholarly verification artifacts.
---

# Phosphene Standards for Scientific Documentation

> **Coordinate:** `:phos.standards/scientific-docs`  
> The code is the specification form; the docstring and literate document are the prolix.

---

## 1. The Literate Documentation Ethos

In scientific and research engineering, code alone is insufficient. Code expresses the *mechanism*
of execution, but is silent on:
- **The Epistemic Justification:** Why does this mathematical threshold exist? What empirical corpus calibrated it?
- **The Decomplecting Rationale:** What two concepts were tangled together, and what failure mode required separating them?
- **The Historical Edge Cases:** What real-world scientific paper broke the prior implementation?

Within `refverify`, we apply the **Phosphene Documentation Standard**. We classify documentation into
three distinct levels of rigor:

| Level | Classification | Definition & Expectation |
|---|---|---|
| ✅ **Literate** | Required for all Domain, Architecture & Protocol units | Carries the full argument. Explains *why* the interface exists, what failure mode it eliminates, and what invariants it preserves. |
| ⚠️ **Functional** | Permitted only for low-level configuration and utility helpers | Accurately describes *what* the code does and its parameters, but lacks intellectual or architectural justification. |
| ❌ **Missing** | Prohibited | Undocumented modules, magic numbers, or unannotated thresholds. |

---

## 2. Epistemic Basis Calibration Tiers

When asserting facts, audit outcomes, or verification statuses within the scholarly pipeline,
`refverify` adheres to strict epistemic calibration. Every statement and audit stamp belongs to
one of three basis tiers:

```
                                  ▲
                                 / \
                                /   \
                               / Tier\
                              /   1   \   Empirical / Direct Registry Grounding
                             /─────────\  Exact DOI / arXiv match, verified hash
                            /   Tier    \
                           /     2       \  Inferential / Composite Fuzzy Match
                          /───────────────\ Score >= 85, author + title agreement
                         /     Tier 3      \
                        /───────────────────\ Heuristic / Grey Literature Guess
                       /                     \ Unindexed URL, regex fallback
```

### Tier 1: Grounded Empirical Truth
- **Criterion:** An exact identifier match (DOI, arXiv ID, PubMed ID) resolved against an authoritative upstream registry.
- **Verification Guarantee:** Immutable metadata confirmed by Crossref or arXiv API.
- **Scoring Basis:** Exact match ($100.0$).

### Tier 2: Inferential Concordance
- **Criterion:** Unindexed or free-text reference resolved via fuzzy search across registry indices.
- **Verification Guarantee:** Composite score $\ge 85.0$, with strong sequence alignment ($S_{\text{title}} \ge 80$) and verified primary author surname.
- **Epistemic Treatment:** Accepted under `PASS` gate, but audit trail records the confidence delta.

### Tier 3: Unindexed Heuristic
- **Criterion:** Reference points to external websites, institutional reports, or preprint servers not indexed in standard scholarly registries.
- **Verification Guarantee:** Syntactically well-formed, but lacking independent third-party confirmation.
- **Epistemic Treatment:** Assigned `WARN` gate. Requires human editorial verification before publication.

---

## 3. Literate Docstring Contract in Python Code

Every pure domain module and adapter in `refverify` must satisfy the literate docstring standard:

```python
def calculate_composite_score(
    title_ratio: float,
    author_match: float,
    year_match: float,
) -> float:
    """Compute empirical composite confidence score for a bibliographic match.

    Epistemic Justification:
        Title similarity alone is insufficient because scientific titles often share
        formulaic prefixes (e.g., "A Novel Approach to...", "Studies in..."). Author
        matching alone fails due to common surnames (Smith, Zhang, Müller). The
        weighted combination (60% title, 25% author, 15% year) was empirically
        calibrated against a corpus of 1,200 verified cross-disciplinary citations,
        yielding zero false positives above the 85.0 publication threshold.

    Args:
        title_ratio: Sequence matcher ratio in [0, 100].
        author_match: Primary surname agreement score in [0, 100].
        year_match: Publication year agreement score in [0, 100].

    Returns:
        Weighted composite score in [0, 100].
    """
    return (0.60 * title_ratio) + (0.25 * author_match) + (0.15 * year_match)
```

By maintaining this literate standard throughout both our prose documentation and our codebase,
we ensure that the intellectual foundations of our software remain transparent, verifiable,
and durable over time.
