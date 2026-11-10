"""phosphene-refverify -- reference-verification QC gate.

Pure domain (Reference, Verdict, scoring, dedup, verification) + provider
ports (LookupClient protocol) + thin httpx adapters. Spec:
FlowFeel/imi-pipeline#22. Policy: Upstream Code Adoption Policy
(meta/reference/operational-policies.md) -- rewritten from an externally
assessed tool, upstream kept as reference-only.
"""

from phosphene.refverify.domain.reference import Reference
from phosphene.refverify.domain.verdict import Verdict, VerdictResult
from phosphene.refverify.domain.verify import gate_decision, verify_all, verify_one
from phosphene.refverify.ports.lookup import CandidateRecord, LookupClient

__all__ = [
    "CandidateRecord",
    "LookupClient",
    "Reference",
    "Verdict",
    "VerdictResult",
    "gate_decision",
    "verify_all",
    "verify_one",
]
