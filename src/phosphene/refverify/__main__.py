"""CLI: bibliography and manuscript reference verification gate.

All logic lives in the domain; this is arg parsing + output only.

Modes:
    refverify bib.md [bib2.docx ...] [--no-cache] [--ttl-seconds N]
    refverify --wiki page.wiki [page2.wiki ...] [--no-cache] [--ttl-seconds N]

Exit code: 0 pass/warn, 1 no input, 2 gate BLOCK.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from phosphene.refverify.adapters.cache import FileCache
from phosphene.refverify.adapters.providers import default_chain
from phosphene.refverify.domain.readers import extract_bibliography
from phosphene.refverify.domain.reference import Reference, parse_bibliography_wikitext
from phosphene.refverify.domain.verdict import Verdict, VerdictResult
from phosphene.refverify.domain.verify import gate_decision, verify_all
from phosphene.refverify.domain.wikitext import extract_article_field

EXIT_OK = 0
EXIT_NO_INPUT = 1
EXIT_BLOCK = 2

_BLOCKING = {Verdict.METADATA_MISMATCH, Verdict.NOT_FOUND, Verdict.DUPLICATE}


def _verify_bibliography(text: str, cache: FileCache, label: str) -> tuple[str, int]:
    """Verify one bibliography text; returns (gate decision, blocking count)."""
    refs = parse_bibliography_wikitext(text)
    if not refs:
        print(f"no bibliography entries found in {label}")
        return "pass", 0
    results = verify_all(refs, default_chain(cache=cache))
    decision = gate_decision(r.verdict for r in results)
    blocking = sum(1 for r in results if r.verdict in _BLOCKING)
    _print_report(refs, results, decision, label)
    return decision, blocking


def _print_report(
    refs: Sequence[Reference],
    results: Sequence[VerdictResult],
    decision: str,
    label: str,
) -> None:
    print(f"\n=== REPORT: {label} ===")
    for ref, r in zip(refs, results, strict=True):
        marker = r.verdict.value.upper()
        src = r.matched_source or "-"
        print(f"[{marker}] {ref.text[:80]}")
        print(f"    score={r.score} source={src} {r.matched_title[:70]}")
        for reason in r.reasons:
            print(f"    - {reason}")
    print(f"\nGATE: {decision.upper()} ({label})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="refverify")
    parser.add_argument(
        "files",
        nargs="*",
        help="path(s) to manuscript (.md), document (.docx), or bibliography (.txt)",
    )
    parser.add_argument(
        "--wiki",
        action="append",
        default=[],
        help=".wiki {{Article}} page; verifies its |Bibliography= field (repeatable)",
    )
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--ttl-seconds", type=int, default=None)
    args = parser.parse_args(argv)

    if not args.files and not args.wiki:
        parser.print_help()
        return EXIT_NO_INPUT

    cache = FileCache(enabled=not args.no_cache)
    if args.ttl_seconds is not None:
        cache.ttl = args.ttl_seconds

    worst = "pass"
    blocking_total = 0

    for wiki_path in args.wiki:
        text = Path(wiki_path).read_text(encoding="utf-8", errors="replace")
        field = extract_article_field(text, "Bibliography")
        if not field:
            print(f"no |Bibliography= field, skipped: {wiki_path}")
            continue
        decision, blocking = _verify_bibliography(field, cache, wiki_path)
        if decision == "block":
            worst = "block"
        elif decision == "warn" and worst != "block":
            worst = "warn"
        blocking_total += blocking

    for file_path in args.files:
        p = Path(file_path)
        if not p.exists():
            print(f"file not found: {p}", file=sys.stderr)
            return EXIT_NO_INPUT
        bib_text = extract_bibliography(p)
        decision, blocking = _verify_bibliography(bib_text, cache, str(p))
        if decision == "block":
            worst = "block"
        elif decision == "warn" and worst != "block":
            worst = "warn"
        blocking_total += blocking

    if worst == "block":
        return EXIT_BLOCK
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
