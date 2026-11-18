"""Hermetic replication bundler for verification proofs and evidence packets.

Enforces the JSON Boundary Discipline:
- JSON is used strictly as a wire manifest and checksum exchange payload.
- Bundles the relational SQLite database snapshot, companion provenance markdown slips,
  and a signed/checksummed manifest for portable, network-free replication.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ReplicationBundleManifest:
    """Wire manifest metadata for a hermetic verification bundle."""

    bundle_id: str
    created_at: str
    doc_id: str
    verifier_version: str
    total_citations: int
    verified_l4: int
    verified_l3: int
    verified_l2: int
    verified_l1: int
    unresolved_l0: int
    sqlite_sha256: str
    provenance_slips: list[dict[str, Any]]


class VerificationBundler:
    """Packages and exports hermetic verification bundles."""

    def __init__(self, output_dir: Path | str) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_bundle(
        self,
        doc_id: str,
        sqlite_db_path: Path | str,
        provenance_dir: Path | str,
        bundle_name: str | None = None,
    ) -> Path:
        """Export a self-contained tar.gz bundle containing SQLite snapshot, slips, and manifest."""
        now = datetime.now(timezone.utc).isoformat()
        b_name = bundle_name or f"bundle_{doc_id}_{int(datetime.now(timezone.utc).timestamp())}"
        staging_dir = self.output_dir / b_name
        staging_dir.mkdir(parents=True, exist_ok=True)

        # 1. Copy SQLite database snapshot
        db_src = Path(sqlite_db_path)
        db_dst = staging_dir / "ledger.db"
        if db_src.exists():
            shutil.copy2(db_src, db_dst)
            db_sha = hashlib.sha256(db_dst.read_bytes()).hexdigest()
        else:
            db_dst.write_bytes(b"")
            db_sha = "empty"

        # 2. Copy provenance markdown slips
        slips_dst = staging_dir / "provenance"
        slips_dst.mkdir(parents=True, exist_ok=True)
        prov_src = Path(provenance_dir)
        slip_files: list[Path] = []
        if prov_src.is_dir():
            for slip in prov_src.glob("*.md"):
                shutil.copy2(slip, slips_dst / slip.name)
                slip_files.append(slip)

        # 3. Read statistics from SQLite ledger
        from phosphene.refverify.storage.sqlite import SqliteVerificationLedger

        ledger = SqliteVerificationLedger(db_dst)
        citations = ledger.get_citation_summary(doc_id=doc_id)

        l4 = sum(1 for c in citations if c["proof_tier"] == "L4_VERBATIM_EXTRACTED")
        l3 = sum(1 for c in citations if c["proof_tier"] == "L3_LOCUS_ATTESTED")
        l2 = sum(1 for c in citations if c["proof_tier"] == "L2_WITNESS_LOCKED")
        l1 = sum(1 for c in citations if c["proof_tier"] == "L1_CATALOG_RESOLVED")
        l0 = sum(1 for c in citations if c["proof_tier"] == "L0_ASSERTED")

        slips_meta = []
        for slip in slip_files:
            content = slip.read_text(encoding="utf-8")
            slips_meta.append({
                "filename": slip.name,
                "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            })

        manifest = {
            "version": "1.0.0",
            "bundle_id": f"urn:phosphene:bundle:{doc_id}",
            "doc_id": doc_id,
            "created_at": now,
            "verifier_version": "refverify-0.2.0",
            "proof_tier_summary": {
                "total": len(citations),
                "L4_VERBATIM_EXTRACTED": l4,
                "L3_LOCUS_ATTESTED": l3,
                "L2_WITNESS_LOCKED": l2,
                "L1_CATALOG_RESOLVED": l1,
                "L0_ASSERTED": l0,
            },
            "sqlite_ledger": {
                "filename": "ledger.db",
                "sha256": db_sha,
            },
            "provenance_slips": slips_meta,
        }

        # Write wire manifest
        manifest_file = staging_dir / "manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        # 4. Pack into tar.gz
        archive_path = self.output_dir / f"{b_name}.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(staging_dir, arcname=b_name)

        # Cleanup staging directory
        shutil.rmtree(staging_dir, ignore_errors=True)

        return archive_path
