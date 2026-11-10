"""Document intake readers and frontmatter audit synchronization.

Extracts bibliography blocks and citation lists from:
- Plain text / bibliography files (.txt)
- Academic Markdown manuscripts (.md)
- Word documents (.docx)
- Wikitext articles (.wiki)

Also provides frontmatter patch synchronization to record verification audits
in-place while preserving human-authored YAML comments and custom formatting.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentVerificationAudit:
    """Audit summary payload to record into document frontmatter."""

    verified: bool
    score: float
    gate: str
    total_references: int
    verified_count: int
    mismatch_count: int
    unresolved_count: int


def patch_document_frontmatter(
    markdown_text: str, audit: DocumentVerificationAudit
) -> str:
    """Patch markdown document frontmatter with verification audit results.

    Uses phosphene.frontmatters shadow patching when available to preserve
    human-authored comments, indentation, and structure. Falls back to clean
    regex insertion if frontmatters is not installed.
    """
    try:
        from phosphene.frontmatters.frontmatter import parse, write

        result = parse(markdown_text)
        result.model.references_verified = audit.verified
        result.model.verification_score = audit.score
        result.model.verification_gate = audit.gate
        return write(result)
    except Exception:
        # Fallback: regex frontmatter updater
        if markdown_text.startswith("---"):
            parts = markdown_text.split("---", 2)
            if len(parts) >= 3:
                header = parts[1]
                body = parts[2]
                # Strip existing verification keys if any
                lines = [
                    l
                    for l in header.splitlines()
                    if not re.match(
                        r"^(references_verified|verification_score|verification_gate)\s*:",
                        l.strip(),
                    )
                ]
                audit_lines = [
                    f"references_verified: {'true' if audit.verified else 'false'}",
                    f"verification_score: {audit.score}",
                    f"verification_gate: {audit.gate}",
                ]
                new_header = "\n".join(lines).strip() + "\n" + "\n".join(audit_lines)
                return f"---{new_header}\n---{body}"
        return markdown_text


def extract_from_markdown(text: str) -> str:
    lines = text.splitlines()
    header_pattern = re.compile(
        r"^#{1,4}\s*(references|bibliography|literature cited)\b", re.IGNORECASE
    )

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


def extract_from_docx(docx_path: str | Path) -> str:
    try:
        import docx

        doc = docx.Document(docx_path)
        full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return extract_from_markdown(full_text)
    except ImportError:
        import xml.etree.ElementTree as ET
        import zipfile

        with zipfile.ZipFile(docx_path) as z:
            xml_content = z.read("word/document.xml")
        tree = ET.fromstring(xml_content)
        namespaces = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }
        paragraphs = []
        for p in tree.iterfind(".//w:p", namespaces):
            texts = [
                node.text
                for node in p.iterfind(".//w:t", namespaces)
                if node.text
            ]
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
