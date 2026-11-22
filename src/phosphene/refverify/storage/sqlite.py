"""Typed relational SQLite storage for verification ledgers, witnesses, and proofs.

Enforces the JSON Boundary Discipline: SQLite is our internal relational query
engine; JSON is never used as an accumulating or nested internal store.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Sequence

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS witnesses (
    sha256 TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    filename TEXT NOT NULL,
    title TEXT,
    authors_json TEXT, -- JSON array of author strings for serializing tuple
    year INTEGER,
    doi TEXT,
    page_count INTEGER NOT NULL DEFAULT 0,
    ingest_ts TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_witnesses_doi ON witnesses(doi);
CREATE INDEX IF NOT EXISTS idx_witnesses_filename ON witnesses(filename);

CREATE TABLE IF NOT EXISTS citations (
    citation_urn TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    title TEXT,
    authors_json TEXT,
    year INTEGER,
    doi TEXT,
    isbn TEXT,
    created_ts TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_citations_doc_id ON citations(doc_id);
CREATE INDEX IF NOT EXISTS idx_citations_doi ON citations(doi);

CREATE TABLE IF NOT EXISTS proof_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    citation_urn TEXT NOT NULL REFERENCES citations(citation_urn) ON DELETE CASCADE,
    proof_tier TEXT NOT NULL, -- L0_ASSERTED, L1_CATALOG_RESOLVED, L2_WITNESS_LOCKED, L3_LOCUS_ATTESTED, L4_VERBATIM_EXTRACTED
    score REAL NOT NULL DEFAULT 0.0,
    source TEXT NOT NULL,
    witness_sha256 TEXT REFERENCES witnesses(sha256) ON DELETE SET NULL,
    page_number INTEGER,
    verified_ts TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_proof_states_urn ON proof_states(citation_urn);
CREATE INDEX IF NOT EXISTS idx_proof_states_tier ON proof_states(proof_tier);

CREATE TABLE IF NOT EXISTS verbatim_slips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    citation_urn TEXT NOT NULL REFERENCES citations(citation_urn) ON DELETE CASCADE,
    witness_sha256 TEXT NOT NULL REFERENCES witnesses(sha256) ON DELETE CASCADE,
    coordinate TEXT NOT NULL,
    page_number INTEGER,
    char_start INTEGER,
    char_end INTEGER,
    rect_x0 REAL,
    rect_y0 REAL,
    rect_x1 REAL,
    rect_y1 REAL,
    claimed_text TEXT NOT NULL,
    contiguous_text TEXT NOT NULL,
    divergence_reason TEXT,
    status TEXT NOT NULL, -- verbatim_verified, verbatim_mutated, witness_not_found
    extracted_ts TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_verbatim_slips_urn ON verbatim_slips(citation_urn);
CREATE INDEX IF NOT EXISTS idx_verbatim_slips_sha ON verbatim_slips(witness_sha256);
"""


class SqliteVerificationLedger:
    """Relational SQLite ledger for physical witnesses, citations, and graded proof states."""

    def __init__(self, db_path: Path | str = ":memory:") -> None:
        self.db_path = str(db_path)
        self._init_db()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connection() as conn:
            conn.executescript(SCHEMA_SQL)

    def register_witness(
        self,
        sha256: str,
        file_path: str,
        filename: str,
        title: str | None = None,
        authors: Sequence[str] = (),
        year: int | None = None,
        doi: str | None = None,
        page_count: int = 0,
    ) -> None:
        """Upsert a physical document witness into the ledger."""
        import json

        now = datetime.now(timezone.utc).isoformat()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO witnesses (sha256, file_path, filename, title, authors_json, year, doi, page_count, ingest_ts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(sha256) DO UPDATE SET
                    file_path=excluded.file_path,
                    filename=excluded.filename,
                    title=excluded.title,
                    authors_json=excluded.authors_json,
                    year=excluded.year,
                    doi=excluded.doi,
                    page_count=excluded.page_count;
                """,
                (
                    sha256,
                    file_path,
                    filename,
                    title,
                    json.dumps(list(authors)),
                    year,
                    doi,
                    page_count,
                    now,
                ),
            )

    def register_citation(
        self,
        citation_urn: str,
        doc_id: str,
        raw_text: str,
        title: str | None = None,
        authors: Sequence[str] = (),
        year: int | None = None,
        doi: str | None = None,
        isbn: str | None = None,
    ) -> None:
        """Upsert a citation entry into the ledger."""
        import json

        now = datetime.now(timezone.utc).isoformat()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO citations (citation_urn, doc_id, raw_text, title, authors_json, year, doi, isbn, created_ts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(citation_urn) DO UPDATE SET
                    doc_id=excluded.doc_id,
                    raw_text=excluded.raw_text,
                    title=excluded.title,
                    authors_json=excluded.authors_json,
                    year=excluded.year,
                    doi=excluded.doi,
                    isbn=excluded.isbn;
                """,
                (
                    citation_urn,
                    doc_id,
                    raw_text,
                    title,
                    json.dumps(list(authors)),
                    year,
                    doi,
                    isbn,
                    now,
                ),
            )

    def record_proof_state(
        self,
        citation_urn: str,
        proof_tier: str,
        score: float,
        source: str,
        witness_sha256: str | None = None,
        page_number: int | None = None,
    ) -> int:
        """Record an evaluated proof state tier for a citation."""
        now = datetime.now(timezone.utc).isoformat()
        with self._connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO proof_states (citation_urn, proof_tier, score, source, witness_sha256, page_number, verified_ts)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    citation_urn,
                    proof_tier,
                    score,
                    source,
                    witness_sha256,
                    page_number,
                    now,
                ),
            )
            return cur.lastrowid or 0

    def record_verbatim_slip(
        self,
        citation_urn: str,
        witness_sha256: str,
        coordinate: str,
        claimed_text: str,
        contiguous_text: str,
        status: str,
        page_number: int | None = None,
        char_start: int | None = None,
        char_end: int | None = None,
        rect_bbox: tuple[float, float, float, float] | None = None,
        divergence_reason: str | None = None,
    ) -> int:
        """Record a physical verbatim extraction slip."""
        now = datetime.now(timezone.utc).isoformat()
        r0, r1, r2, r3 = rect_bbox if rect_bbox else (None, None, None, None)
        with self._connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO verbatim_slips (
                    citation_urn, witness_sha256, coordinate, page_number,
                    char_start, char_end, rect_x0, rect_y0, rect_x1, rect_y1,
                    claimed_text, contiguous_text, divergence_reason, status, extracted_ts
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    citation_urn,
                    witness_sha256,
                    coordinate,
                    page_number,
                    char_start,
                    char_end,
                    r0,
                    r1,
                    r2,
                    r3,
                    claimed_text,
                    contiguous_text,
                    divergence_reason,
                    status,
                    now,
                ),
            )
            return cur.lastrowid or 0

    def get_citation_summary(self, doc_id: str | None = None) -> list[dict[str, Any]]:
        """Query joined citation status, highest proof tier, and witness info."""
        import json

        sql = """
        SELECT
            c.citation_urn,
            c.doc_id,
            c.title,
            c.authors_json,
            c.year,
            c.doi,
            ps.proof_tier,
            ps.score,
            ps.source,
            ps.witness_sha256,
            w.filename AS witness_filename,
            vs.contiguous_text,
            vs.status AS verbatim_status
        FROM citations c
        LEFT JOIN proof_states ps ON ps.id = (
            SELECT id FROM proof_states WHERE citation_urn = c.citation_urn ORDER BY score DESC, id DESC LIMIT 1
        )
        LEFT JOIN witnesses w ON w.sha256 = ps.witness_sha256
        LEFT JOIN verbatim_slips vs ON vs.id = (
            SELECT id FROM verbatim_slips WHERE citation_urn = c.citation_urn ORDER BY id DESC LIMIT 1
        )
        """
        params: list[Any] = []
        if doc_id:
            sql += " WHERE c.doc_id = ?"
            params.append(doc_id)
        sql += " ORDER BY c.year ASC, c.title ASC;"

        results: list[dict[str, Any]] = []
        with self._connection() as conn:
            for row in conn.execute(sql, params):
                results.append({
                    "citation_urn": row["citation_urn"],
                    "doc_id": row["doc_id"],
                    "title": row["title"],
                    "authors": json.loads(row["authors_json"]) if row["authors_json"] else [],
                    "year": row["year"],
                    "doi": row["doi"],
                    "proof_tier": row["proof_tier"] or "L0_ASSERTED",
                    "score": row["score"] or 0.0,
                    "source": row["source"],
                    "witness_sha256": row["witness_sha256"],
                    "witness_filename": row["witness_filename"],
                    "has_verbatim": bool(row["contiguous_text"]),
                    "verbatim_status": row["verbatim_status"],
                })
        return results
