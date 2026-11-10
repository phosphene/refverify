"""Thin CLI: bibliography verification gate.

All logic lives in the domain; this is arg parsing + output only.

Modes:
    uv run python -m phosphene.refverify bib.txt [--no-cache] [--ttl-seconds N]
    uv run python -m phosphene.refverify --wiki page.wiki [page2.wiki ...]
                                                   [--no-cache] [--ttl-seconds N]

--wiki extracts the ``|Bibliography=`` field from {{Article}} pages and
verifies those entries; pages without the field are skipped (nothing to
verify). Exit code: 0 pass/warn, 1 no input, 2 gate BLOCK.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from phosphene.refverify.adapters.cache import FileCache
from phosphene.refverify.adapters.providers import default_chain
from phosphene.refverify.domain.reference import Reference, parse_bibliography_wikitext
from phosphene.refverify.domain.verdict import Verdict, VerdictResult
from phosphene.refverify.domain.verify import gate_decision, verify_all
from phosphene.refverify.domain.wikitext import extract_article_field

EXIT_OK = 0
EXIT_NO_INPUT = 1
EXIT_BLOCK = 2

_BLOCKING = {Verdict.METADATA_MISMATCH, Verdict.NOT_FOUND, Verdict.DUPLICATE}


def _read_bibliography_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text()


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
        "bibliography",
        nargs="?",
        default="-",
        help="path to Bibliography-field text ('-' = stdin)",
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

    cache = FileCache(enabled=not args.no_cache)
    if args.ttl_seconds is not None:
        cache.ttl = args.ttl_seconds

    worst = "pass"
    blocking_total = 0

    for wiki_path in args.wiki:
        text = Path(wiki_path).read_text()
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

    if not args.wiki:
        decision, blocking = _verify_bibliography(
            _read_bibliography_text(args.bibliography), cache, args.bibliography
        )
        worst, blocking_total = decision, blocking

    if worst == "block":
        return EXIT_BLOCK
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
