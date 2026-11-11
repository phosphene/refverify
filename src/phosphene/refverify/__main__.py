"""CLI: bibliography and manuscript reference verification gate.

Modes:
    refverify document.md [document2.docx ...] [--no-cache] [--ttl-seconds N] [--json-out report.json]
    refverify --wiki page.wiki [page2.wiki ...] [--no-cache] [--ttl-seconds N] [--json-out report.json]
    refverify document.md --verify-verbatim <witness-dir> [--json-out report.json]

Exit codes:
    0: pass or warn
    1: invocation error or no input
    2: gate BLOCK (severe mismatch, duplication, unresolvable citation, or verbatim quote mutation)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from phosphene.refverify.adapters.cache import FileCache
from phosphene.refverify.adapters.providers import default_chain
from phosphene.refverify.domain.readers import extract_bibliography, extract_blockquotes_from_markdown
from phosphene.refverify.domain.reference import Reference, parse_bibliography_wikitext
from phosphene.refverify.domain.verdict import GateDecision, Verdict, VerdictResult
from phosphene.refverify.domain.verify import gate_decision, verify_all
from phosphene.refverify.domain.verbatim import (
    VerbatimResult,
    VerbatimStatus,
    verify_verbatim_quote,
)
from phosphene.refverify.domain.wikitext import extract_article_field

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_BLOCK = 2

_BLOCKING = {Verdict.NOT_FOUND, Verdict.METADATA_MISMATCH, Verdict.DUPLICATE}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="refverify",
        description="Scholarly reference verification and quality-control gate.",
    )
    p.add_argument(
        "files",
        nargs="*",
        help="Path(s) to manuscript (.md), document (.docx), bibliography (.txt), or wikitext (.wiki).",
    )
    p.add_argument(
        "--wiki",
        action="append",
        default=[],
        help=".wiki {{Article}} page; verifies its |Bibliography= field (repeatable).",
    )
    p.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass on-disk HTTP response cache.",
    )
    p.add_argument(
        "--ttl-seconds",
        type=int,
        default=None,
        help="Cache time-to-live in seconds (default: 7 days).",
    )
    p.add_argument(
        "--json-out",
        type=str,
        default=None,
        help="Path to emit structured verification report as JSON.",
    )
    p.add_argument(
        "--verify-verbatim",
        type=str,
        default=None,
        help="Path to directory containing primary witness texts (.txt / .md) for verbatim quotation checking.",
    )
    return p


def _build_cache(no_cache: bool, ttl_seconds: int | None) -> FileCache:
    if no_cache:
        return FileCache(enabled=False)
    cache_dir = Path.home() / ".cache" / "refverify"
    cache_dir.mkdir(parents=True, exist_ok=True)
    if ttl_seconds is not None:
        return FileCache(cache_dir, ttl_seconds=ttl_seconds)
    return FileCache(cache_dir)


def _load_witness_corpus(witness_dir: Path) -> dict[str, str]:
    """Loads all text files in witness_dir into a memory dictionary keyed by stem."""
    witnesses: dict[str, str] = {}
    if not witness_dir.is_dir():
        return witnesses
    for f in witness_dir.rglob("*"):
        if f.is_file() and f.suffix.lower() in (".txt", ".md", ".tex", ".json"):
            witnesses[f.stem.lower()] = f.read_text(encoding="utf-8", errors="replace")
    return witnesses


def _find_matching_witness(target_citation: str, claimed_text: str, witnesses: dict[str, str]) -> str | None:
    """Finds the best matching witness text by target citation or filename key."""
    if not witnesses:
        return None
    # Check exact stem match
    if target_citation:
        target_norm = "".join(c for c in target_citation.lower() if c.isalnum() or c in ("-", "_"))
        for k, v in witnesses.items():
            if k in target_norm or target_norm in k:
                return v
    # Fallback: check if the first 30 chars of the claim appear in any witness
    first_part = claimed_text[:30].strip()
    for v in witnesses.values():
        if first_part and first_part in v:
            return v
    # If single witness in directory, return it
    if len(witnesses) == 1:
        return next(iter(witnesses.values()))
    return None


def _verify_verbatim_blockquotes(
    file_path: Path,
    witness_corpus: dict[str, str],
) -> tuple[str, list[dict[str, Any]]]:
    """Extracts blockquotes from markdown and verifies them against witness corpus."""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    doc_id = file_path.stem
    quotes = extract_blockquotes_from_markdown(content, doc_id=doc_id)
    if not quotes:
        return "pass", []

    results: list[dict[str, Any]] = []
    has_mutation = False

    for q in quotes:
        witness = _find_matching_witness(q.target_citation, q.text, witness_corpus)
        if not witness:
            res = VerbatimResult(
                status=VerbatimStatus.WITNESS_NOT_FOUND,
                coordinate=q.coordinate,
                target_citation=q.target_citation,
                claimed_text=q.text,
                matched_span=None,
                divergence_reason="witness_not_found_in_corpus",
            )
        else:
            res = verify_verbatim_quote(
                claimed_text=q.text,
                witness_text=witness,
                coordinate=q.coordinate,
                target_citation=q.target_citation,
            )

        if res.status == VerbatimStatus.VERBATIM_MUTATED:
            has_mutation = True

        results.append({
            "coordinate": res.coordinate,
            "target_citation": res.target_citation,
            "claimed_text": res.claimed_text,
            "status": res.status.value,
            "matched_span": list(res.matched_span) if res.matched_span else None,
            "divergence_reason": res.divergence_reason,
        })

    decision = "block" if has_mutation else "pass"
    return decision, results


def _verify_bibliography_payload(
    text: str,
    cache: FileCache,
    label: str,
) -> tuple[str, int, dict[str, Any]]:
    """Verify one bibliography text; returns (gate decision, blocking count, file report dict)."""
    refs = parse_bibliography_wikitext(text)
    if not refs:
        print(f"no bibliography entries found in {label}")
        empty_report: dict[str, Any] = {
            "file": label,
            "decision": "pass",
            "blocking": 0,
            "summary": {"total": 0, "verified": 0, "mismatches": 0, "duplicates": 0, "unresolved": 0},
            "references": [],
        }
        return "pass", 0, empty_report

    results = verify_all(refs, default_chain(cache=cache))
    decision = gate_decision(r.verdict for r in results)
    blocking = sum(1 for r in results if r.verdict in _BLOCKING)

    _print_report(refs, results, decision, label)

    verified_cnt = sum(1 for r in results if r.verdict in (Verdict.VERIFIED, Verdict.VERIFIED_SECONDARY))
    mismatch_cnt = sum(1 for r in results if r.verdict == Verdict.METADATA_MISMATCH)
    duplicate_cnt = sum(1 for r in results if r.verdict == Verdict.DUPLICATE)
    unresolved_cnt = sum(1 for r in results if r.verdict == Verdict.NOT_FOUND)

    ref_reports = []
    for ref, r in zip(refs, results, strict=True):
        entry = {
            "raw": ref.text,
            "parsed_authors": list(ref.authors),
            "parsed_year": ref.year,
            "parsed_title": ref.title,
            "parsed_doi": ref.doi,
            "verdict": r.verdict.value,
            "score": r.score,
            "reasons": list(r.reasons),
            "matched_title": r.matched_title,
            "matched_doi": r.matched_doi,
            "matched_source": r.matched_source,
        }
        ref_reports.append(entry)

    file_report = {
        "file": label,
        "decision": decision,
        "blocking": blocking,
        "summary": {
            "total": len(refs),
            "verified": verified_cnt,
            "mismatches": mismatch_cnt,
            "duplicates": duplicate_cnt,
            "unresolved": unresolved_cnt,
        },
        "references": ref_reports,
    }
    return decision, blocking, file_report


def _print_report(
    refs: Sequence[Reference],
    results: Sequence[VerdictResult],
    decision: str,
    label: str,
) -> None:
    print(f"\n=== REPORT: {label} ===")
    for ref, r in zip(refs, results, strict=True):
        tag = r.verdict.value.upper()
        print(f"[{tag}] {ref.text}")
        print(f"  score={r.score:.2f} matched={r.matched_title!r}")
        if r.matched_doi:
            print(f"  doi={r.matched_doi} via={r.matched_source}")
        for reason in r.reasons:
            print(f"    - {reason}")
    print(f"\nGATE: {decision.upper()} ({label})")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.files and not args.wiki:
        parser.print_help()
        return EXIT_USAGE

    cache = _build_cache(args.no_cache, args.ttl_seconds)
    worst: GateDecision = "pass"
    blocking_total = 0
    all_reports: list[dict[str, Any]] = []

    witness_corpus: dict[str, str] = {}
    if args.verify_verbatim:
        w_dir = Path(args.verify_verbatim)
        if not w_dir.is_dir():
            print(f"witness directory not found: {w_dir}", file=sys.stderr)
            return EXIT_USAGE
        witness_corpus = _load_witness_corpus(w_dir)
        print(f"Loaded {len(witness_corpus)} witness documents from {w_dir}")

    for wiki_path in args.wiki:
        p = Path(wiki_path)
        if not p.exists():
            print(f"file not found: {p}", file=sys.stderr)
            return EXIT_USAGE
        text = p.read_text(encoding="utf-8", errors="replace")
        field = extract_article_field(text, "Bibliography")
        if not field:
            print(f"no |Bibliography= field, skipped: {wiki_path}")
            continue
        decision, blocking, report = _verify_bibliography_payload(field, cache, wiki_path)
        all_reports.append(report)
        if decision == "block":
            worst = "block"
        elif decision == "warn" and worst != "block":
            worst = "warn"
        blocking_total += blocking

    for file_path in args.files:
        p = Path(file_path)
        if not p.exists():
            print(f"file not found: {p}", file=sys.stderr)
            return EXIT_USAGE
        bib_text = extract_bibliography(p)
        decision, blocking, report = _verify_bibliography_payload(bib_text, cache, str(p))

        # If verbatim verification is requested and file is markdown, verify blockquotes
        if args.verify_verbatim and p.suffix.lower() in (".md", ".markdown"):
            v_decision, v_quotes = _verify_verbatim_blockquotes(p, witness_corpus)
            report["verbatim_decision"] = v_decision
            report["verbatim_quotes"] = v_quotes
            if v_decision == "block":
                worst = "block"
                blocking_total += sum(1 for q in v_quotes if q["status"] == VerbatimStatus.VERBATIM_MUTATED.value)
                print(f"[VERBATIM BLOCK] Mutated quotation detected in {p}")
            elif v_quotes:
                print(f"[VERBATIM PASS] Verified {len(v_quotes)} blockquote(s) in {p}")

        all_reports.append(report)
        if decision == "block":
            worst = "block"
        elif decision == "warn" and worst != "block":
            worst = "warn"
        blocking_total += blocking

    if args.json_out:
        out_p = Path(args.json_out)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        final_payload = {
            "gate": worst,
            "total_blocking": blocking_total,
            "files": all_reports,
        }
        out_p.write_text(json.dumps(final_payload, indent=2), encoding="utf-8")
        print(f"\nWrote verification JSON report to {out_p}")

    if worst == "block":
        return EXIT_BLOCK
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
