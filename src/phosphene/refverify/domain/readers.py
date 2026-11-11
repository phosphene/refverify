"""Document intake readers and AST-aware markdown orchestration.

Extracts bibliography blocks, parses citations, and synchronizes frontmatter
using phosphene-mdrag and phosphene-frontmatters.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from phosphene.core.models import InvariantStatic
from phosphene.refverify.domain.reference import Reference, from_wikitext_entry

# Recognized headings for bibliography and provenance sections in manuscripts
PROVENANCE_HEADING_REGEX = (
    r"^(references|bibliography|literature cited|data sources|provenance|"
    r"empirical baseline|standards & regulatory references|citations)\b"
)


class DocumentVerificationAudit(InvariantStatic):
    """Audit metadata to project into markdown frontmatter."""

    verified: bool
    score: float
    gate: str
    total_references: int
    verified_count: int
    mismatch_count: int
    unresolved_count: int


def extract_from_markdown(text: str) -> str:
    """Extract references section using mdrag AST parsing when available."""
    # Check for explicit refverify comment anchors first: <!-- refverify:begin --> ... <!-- refverify:end -->
    comment_anchor_match = re.search(
        r"<!--\s*refverify:begin\s*-->\s*(.*?)\s*<!--\s*refverify:end\s*-->",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if comment_anchor_match:
        return comment_anchor_match.group(1).strip()

    ref_heading_pattern = re.compile(PROVENANCE_HEADING_REGEX, re.IGNORECASE)

    try:
        from phosphene.mdrag.engine import MarkdownEngine

        engine = MarkdownEngine()
        # If document lacks frontmatter, prepend a lightweight transient header for the AST parser
        doc_text = text if text.strip().startswith("---") else f"---\nuri: transient/document\n---\n\n{text}"
        ast = engine.read(doc_text)

        in_ref_section = False
        items: list[str] = []

        for block in ast.blocks:
            if block.type == "heading":
                title = str(block.attrs.get("text", "")).strip()
                if ref_heading_pattern.match(title):
                    in_ref_section = True
                    continue
                elif in_ref_section:
                    break

            if in_ref_section:
                if block.type == "list":
                    list_items = block.attrs.get("items", [])
                    items.extend(str(item) for item in list_items)
                elif block.type == "paragraph":
                    content = str(block.attrs.get("content", ""))
                    if content:
                        items.append(content)

        if items:
            return "\n".join(items).strip()
    except Exception:
        pass

    # Deterministic fallback line parser
    lines = text.splitlines()
    header_pattern = re.compile(rf"^#{{1,4}}\s*{PROVENANCE_HEADING_REGEX}", re.IGNORECASE)

    start_idx = -1
    for idx, line in enumerate(lines):
        if header_pattern.match(line.strip()):
            start_idx = idx + 1
            break

    if start_idx != -1:
        extracted = []
        for line in lines[start_idx:]:
            if re.match(r"^#{1,2}\s+[A-Za-z]", line.strip()):
                break
            extracted.append(line)
        return "\n".join(extracted).strip()

    citation_lines = []
    for line in lines:
        s = line.strip()
        if s.startswith(("* ", "- ")) and re.search(r"\(\d{4}[a-z]?\)", s):
            citation_lines.append(s.lstrip("*- "))
    return "\n".join(citation_lines).strip()


def patch_document_frontmatter(
    content: str,
    audit: DocumentVerificationAudit,
) -> str:
    """Synchronize verification audit into markdown frontmatter using phosphene-frontmatters."""
    try:
        from phosphene.frontmatters.core.manager import FrontmatterManager
        from phosphene.frontmatters.frontmatter import OpenFrontmatter

        manager = FrontmatterManager(OpenFrontmatter)
        model, body, shadow = manager.load(content)

        # Inject or update verification audit fields
        model.references_verified = audit.verified
        model.verification_score = audit.score
        model.verification_gate = audit.gate
        model.verification_summary = {
            "total": audit.total_references,
            "verified": audit.verified_count,
            "mismatch": audit.mismatch_count,
            "unresolved": audit.unresolved_count,
        }

        return manager.save(model, body, shadow)
    except Exception:
        # If frontmatter engine is unconfigured or unavailable, return content unchanged
        return content


def extract_from_docx(file_path: str | Path) -> str:
    """Extract references from Word .docx file by inspecting text paragraphs."""
    try:
        import docx

        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return extract_from_markdown("\n".join(paragraphs))
    except Exception:
        import zipfile
        import xml.etree.ElementTree as ET

        paragraphs: list[str] = []
        with zipfile.ZipFile(file_path) as z:
            xml_content = z.read("word/document.xml")
            root = ET.fromstring(xml_content)
            namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            for p_node in root.findall(".//w:p", namespaces):
                texts = [node.text for node in p_node.findall(".//w:t", namespaces) if node.text]
                if texts:
                    paragraphs.append("".join(texts))
        return extract_from_markdown("\n".join(paragraphs))


def extract_bibliography(file_path: str | Path) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in (".docx",):
        return extract_from_docx(path)

    text = path.read_text(encoding="utf-8", errors="replace")
    if suffix in (".wiki",):
        from phosphene.refverify.domain.wikitext import extract_article_field
        val = extract_article_field(text, "Bibliography")
        return val if val else extract_from_markdown(text)

    if suffix in (".md", ".markdown"):
        extracted = extract_from_markdown(text)
        return extracted if extracted else text

    return text
