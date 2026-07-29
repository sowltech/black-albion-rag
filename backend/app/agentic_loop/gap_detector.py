"""Deterministic gap detection.

Phase 1 gap detection is structural: it compares planner expectations
(subquestions, required evidence types) against what was actually retrieved.
There is no generative semantic judgement here -- that is explicitly left as
an extension point for a later, model-assisted phase (the interface below
does not change to add one).
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Set

from .models import Contradiction, EvidenceItem, Gap, RetrievalQuery, Subquestion

_LOW_PROVENANCE_THRESHOLD = 0.4
_LOW_FRESHNESS_THRESHOLD = 0.3


def group_evidence_by_subquestion(
    evidence: Sequence[EvidenceItem], queries: Sequence[RetrievalQuery]
) -> Dict[str, List[EvidenceItem]]:
    parents_by_query: Dict[str, List[str]] = {
        query.query_id: query.parent_subquestion_ids for query in queries
    }
    grouped: Dict[str, List[EvidenceItem]] = {}
    for item in evidence:
        for subquestion_id in parents_by_query.get(item.retrieval_query_id, []):
            grouped.setdefault(subquestion_id, []).append(item)
    return grouped


def detect_gaps(
    subquestions: Sequence[Subquestion],
    evidence: Sequence[EvidenceItem],
    queries: Sequence[RetrievalQuery],
    contradictions: Sequence[Contradiction],
) -> List[Gap]:
    """Return the open gaps implied by the current state.

    Callers are expected to call this once per iteration; it is stateless
    and does not merge against a previous call's results.
    """
    grouped = group_evidence_by_subquestion(evidence, queries)
    gaps: List[Gap] = []

    for sq in subquestions:
        sq_evidence = grouped.get(sq.subquestion_id, [])

        if not sq_evidence:
            gaps.append(
                Gap(
                    gap_id=f"gap-{sq.subquestion_id}-coverage",
                    subquestion_id=sq.subquestion_id,
                    description=f"No evidence retrieved yet for: {sq.text}",
                    severity="high",
                    required_evidence=list(sq.required_evidence_types),
                    status="open",
                )
            )
            continue

        covered_types: Set[str] = {item.source_type for item in sq_evidence}
        missing_types = [t for t in sq.required_evidence_types if t not in covered_types]
        if missing_types:
            gaps.append(
                Gap(
                    gap_id=f"gap-{sq.subquestion_id}-evidence-type",
                    subquestion_id=sq.subquestion_id,
                    description=(
                        f"Missing required evidence types for '{sq.text}': "
                        + ", ".join(sorted(missing_types))
                    ),
                    severity="medium",
                    required_evidence=missing_types,
                    status="open",
                )
            )

        source_ids = {item.source_id for item in sq_evidence}
        if len(source_ids) == 1 and len(sq_evidence) > 1:
            gaps.append(
                Gap(
                    gap_id=f"gap-{sq.subquestion_id}-source-diversity",
                    subquestion_id=sq.subquestion_id,
                    description=f"All evidence for '{sq.text}' comes from a single source.",
                    severity="low",
                    required_evidence=[],
                    status="open",
                )
            )

        avg_provenance = sum(item.provenance_quality for item in sq_evidence) / len(sq_evidence)
        if avg_provenance < _LOW_PROVENANCE_THRESHOLD:
            gaps.append(
                Gap(
                    gap_id=f"gap-{sq.subquestion_id}-provenance",
                    subquestion_id=sq.subquestion_id,
                    description=f"Evidence for '{sq.text}' has weak provenance.",
                    severity="medium",
                    required_evidence=[],
                    status="open",
                )
            )

        avg_freshness = sum(item.freshness for item in sq_evidence) / len(sq_evidence)
        if avg_freshness < _LOW_FRESHNESS_THRESHOLD:
            gaps.append(
                Gap(
                    gap_id=f"gap-{sq.subquestion_id}-freshness",
                    subquestion_id=sq.subquestion_id,
                    description=f"Evidence for '{sq.text}' is stale-only.",
                    severity="low",
                    required_evidence=[],
                    status="open",
                )
            )

    for contradiction in contradictions:
        if contradiction.status in ("open", "partially_resolved"):
            gaps.append(
                Gap(
                    gap_id=f"gap-contradiction-{contradiction.contradiction_id}",
                    subquestion_id="",
                    description=(
                        f"Unresolved contradiction over: {contradiction.claim_or_question}"
                    ),
                    severity=contradiction.materiality,
                    required_evidence=[],
                    status="open",
                )
            )

    return gaps


def coverage_ratio(subquestions: Sequence[Subquestion], gaps: Sequence[Gap]) -> float:
    """Fraction of subquestions with no open medium/high-severity gap.

    Low-severity gaps (source diversity, freshness) do not count against
    coverage -- they are quality signals, not "this subquestion is
    unanswered" signals.
    """
    if not subquestions:
        return 1.0
    blocked = {
        gap.subquestion_id
        for gap in gaps
        if gap.status == "open" and gap.severity in ("medium", "high")
    }
    covered = sum(1 for sq in subquestions if sq.subquestion_id not in blocked)
    return covered / len(subquestions)
