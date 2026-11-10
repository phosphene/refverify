---
uri: phosphene.tooling/refverify/docs/mdrag-and-frontmatters-innovations
owner: edphos
status: canonical
created: 2026-11-10
updated: 2026-11-10
namespace: phosphene.tooling.refverify
coordinates:
  - :mdrag.core/ast-aware
  - :frontmatters.patch/shadow
  - :mdrag.block/addressability
  - :phos.arch/symbolic-loop
builds-on:
  - phosphene.tooling/refverify/docs/ethos
  - phosphene.tooling/refverify/docs/architecture
converges-with:
  - work/inferno-labs/handoff/mdrag-philosophy
  - .agents/skills/mdrag-engine/SKILL.md
abstract: |
  Documents the primary innovations in refverify: replacing brittle regex parsing
  with AST-level block extraction via phosphene-mdrag, and eliminating destructive
  metadata writes through lossless YAML shadow patching via phosphene-frontmatters.
  Analyzes what these innovations teach us about document-oriented AI tooling and
  the evolution of block addressability.
---

# Innovations in `mdrag` & Frontmatters — AST Extraction, Shadow Patching & Block Addressability

> **Coordinates:**  
> `:mdrag.core/ast-aware` — Structured Markdown parsing via AST node boundaries  
> `:frontmatters.patch/shadow` — Non-destructive round-trip YAML mutation  
> `:mdrag.block/addressability` — Invariant coordinate addressing within documents

---

## 1. The Real-World Use Case: Scholarly Verification in Flight

In the workflow of public science, academic manuscripts arrive as living documents:
written in Markdown, enriched with YAML frontmatter, cited with inline references, and containing
extensive human formatting, comments, and structural headings.

The operational requirement for `refverify` is deceptively simple:
1. **Intake:** Read the manuscript and isolate the bibliographic apparatus (`## References`, `## Bibliography`, `## Literature Cited`).
2. **Verify:** Check every citation against primary registries (Crossref, OpenAlex, arXiv, Semantic Scholar).
3. **Audit Stamp:** Write the verification results (`references_verified`, `verification_score`, `verification_gate`, summary statistics) back into the document's YAML frontmatter.

While seemingly routine, executing this in automated pipelines using conventional tools consistently
produces **catastrophic context destruction**. Below, we record the two primary innovations developed
in `refverify` to solve this, and the broader lessons they provide for document tooling.

---

## 2. Innovation 1: AST-Level Block Extraction (`phosphene-mdrag`)

### The Failure Mode of Regex
Historically, bibliography extraction has relied on regular expressions:
```python
# The brittle prior art:
ref_match = re.search(r"^##\s+(?:References|Bibliography)\s*\n(.*)", text, re.DOTALL | re.MULTILINE)
```

In production across thousands of research manuscripts, this pattern fails systematically:
- **Heading Level Collisions:** An author uses `# References` (h1), `### References` (h3 under Discussion), or `## References and Notes`. Regex patterns either miss the boundary or match false positives.
- **Section Bleed:** A naive `re.DOTALL` consumes the remainder of the document, including subsequent appendices, acknowledgments, or author biography sections.
- **Syntactic Masquerading:** If an author includes a code block illustrating Markdown syntax (e.g., ````markdown\n## References\n````) or quotes a passage containing a heading, regex greedily anchors on the text inside the code fence.

### The AST Solution in `refverify`
`refverify` delegates structural parsing to `phosphene-mdrag`. Instead of treating the manuscript as a
flat string, `mdrag` compiles it into an Abstract Syntax Tree (AST):

```
Document AST
├── Heading [level=1, text="Introduction"]
├── Paragraph [content="..."]
├── Heading [level=2, text="References"]  <-- Recognized target block
│   ├── List [ordered=False]
│   │   ├── ListItem [text="Einstein, A. (1905)..."]
│   │   └── ListItem [text="Darwin, C. (1859)..."]
│   └── Paragraph [content="..."]
└── Heading [level=2, text="Appendix A"]  <-- Natural terminating boundary
```

In `phosphene.refverify.domain.readers.extract_from_markdown`:
```python
ast = parse_markdown_ast(text)
ref_heading_pattern = re.compile(r"^(references|bibliography|literature cited)\b", re.IGNORECASE)

in_ref_section = False
items: list[str] = []

for block in ast.blocks:
    if block.type == "heading":
        title = str(block.attrs.get("text", "")).strip()
        if ref_heading_pattern.match(title):
            in_ref_section = True
            continue
        elif in_ref_section:
            # Terminate cleanly on encountering the next heading of equal or higher scope
            break

    if in_ref_section:
        if block.type == "list":
            items.extend(str(item) for item in block.attrs.get("items", []))
        elif block.type == "paragraph":
            items.append(str(block.attrs.get("content", "")))
```

**What was achieved:**
- The parser respects document syntax: code blocks, blockquotes, and nested styling are AST-isolated.
- Termination is deterministic: the boundary of the references section is governed by AST tree depth,
  not arbitrary newline regexes.

---

## 3. Innovation 2: Frontmatter Shadow Patching (`phosphene-frontmatters`)

### The Failure Mode of Standard Serializers
Standard YAML parsers (`yaml.safe_load` / `yaml.dump`) are **destructive round-trippers**. When an agent
or script loads a manuscript's frontmatter, adds verification fields, and writes it back:
1. **Comment Elimination:** All YAML comments (`# Author notes`, `# TODO: check grants`) are discarded.
2. **Key Reordering:** Dictionary keys are sorted alphabetically or randomly, destroying the logical
   author layout (`title`, `authors`, `date` gets scrambled).
3. **Whitespace Corruption:** Custom spacing, multiline string formatting (`|`, `>`), and trailing newlines
   are normalized away.
4. **Schema Rejection:** If the frontmatter contains unknown custom keys from another tool, closed-world
   parsers crash or drop the keys.

For an author whose manuscript is actively being processed, having an automated gate rewrite their
formatting is unacceptable.

### The Shadow Patching Architecture
`phosphene-frontmatters` implements **Shadow Patching**. The document's frontmatter is represented as
a dual-layer structure:
1. **The Concrete Syntax Tree (CST / Shadow):** Retains raw text, precise token offsets, comments,
   indentation style, and formatting anchors.
2. **The Open Domain Model:** A schema-tolerant Pydantic model (`OpenFrontmatter`) adhering to the
   **Open-World Assumption (OWA)**. Unknown fields are retained in an open bag; known fields are
   typed and accessible.

When `refverify` writes back the audit stamp:
```python
from phosphene.frontmatters.core.manager import FrontmatterManager
from phosphene.frontmatters.frontmatter import OpenFrontmatter

manager = FrontmatterManager(OpenFrontmatter)
model, body, shadow = manager.load(content)

# Surgical mutation of audit metadata only
model.references_verified = audit.verified
model.verification_score = audit.score
model.verification_gate = audit.gate
model.verification_summary = {
    "total": audit.total_references,
    "verified": audit.verified_count,
    "mismatch": audit.mismatch_count,
    "unresolved": audit.unresolved_count,
}

# Lossless re-synthesis
patched_content = manager.save(model, body, shadow)
```

**The Invariant:** Only the targeted audit keys are injected or updated in the YAML text. Every existing
comment, unparsed custom field, newline, and indentation level remains byte-for-byte identical.

---

## 4. Innovation 3: Block Addressability & Invariant Coordinates

Moving to AST-level processing unlocks a deeper capability: **fine-grained block addressability**.

In scientific manuscripts, verifying that a paper's bibliography exists is merely table stakes.
The real epistemic challenge is **claim anchoring**: verifying that an assertion made in Section 3,
Paragraph 2 is actually supported by the citation it invokes, and that the citation resolves
to a valid scholarly record.

### Hickey Coordinate Addressing
By combining `mdrag` block identifiers with Rich Hickey's coordinate design:
- Every block receives an immutable, reproducible coordinate within the document graph:
  - `doc:sec:methodology`
  - `doc:sec:methodology:p3`
  - `doc:sec:methodology:p3:cite:1`
- The citation anchor (`cite:1`) references a verified bibliography node:
  - `doc:ref:einstein1905`
- The bibliography node carries the verified registry metadata:
  - `doi:10.1002/andp.19053221004` (verified via Crossref, score: 98.4, gate: PASS).

This transforms the manuscript from a flat text file into an **addressable knowledge graph**.

---

## 5. What This Teaches Us About Tools and Tools Like Them

The engineering lessons learned from `refverify`'s use of `mdrag` and `frontmatters` extend far beyond
reference checking:

### 1. File Rewriting Must Be Decomplected into AST Reading and Shadow Writing
Large Language Models and automated scripts are notoriously unreliable at full-file rewriting. When an
LLM is asked to "add verification metadata to this document," it invariably alters phrasing, truncates
sections, or reformats markdown tables.
By separating:
- **Extraction:** AST-level isolation (read only what is needed);
- **Computation:** Pure domain verification (zero side effects); and
- **Injection:** Shadow patching (surgical update of exact AST/CST tokens);  
we eliminate non-deterministic file corruption entirely.

### 2. The Open-World Assumption is Mandatory for Living Documents
Closed schemas that validate strictly and reject unknown properties cannot survive in collaborative,
multi-tool scientific ecosystems. Tools must adopt OWA: parse and validate what you understand,
faithfully preserve what you do not, and never drop data simply because it was not in your schema.

### 3. Structured Markdown as a Dual Signal
As demonstrated in the Phosphene platform architecture, structured Markdown is the ideal medium for
dual-signal AI and human collaboration:
- For **humans and generative LLMs**, it is clean, legible, expressive prose;
- For **deterministic verification engines (RLVR, AST analyzers, QC gates)**, it is a strictly addressable,
  hierarchical data structure with verifiable invariants.

---

## 6. Projections to General Concerns

The capacities documented here (AST structural extraction, lossless YAML shadow patching, and block coordinate addressability)
are formally projected into generalized tools and cross-domain architectures in the proposed projection namespace:
👉 **[`projections/general-capacities.md`](projections/general-capacities.md)** (`:projection.capacity/*`, `:projection.domain/*`).

