"""Contradiction lifecycle: creation, materiality, and resolution.

Resolution is always an explicit, reasoned action -- never an automatic
consequence of one side scoring higher than the other. A numeric score
difference is a hint for what to retrieve next, not a verdict.
"""
from __future__ import annotations

from typing import List, Sequence

from .errors import InvalidRequestError
from .models import Contradiction, ContradictionMateriality, EvidenceItem

_TIER_WEIGHT = {"I": 3, "II": 2, "III": 1}


def classify_materiality(
    supporting: Sequence[EvidenceItem], opposing: Sequence[EvidenceItem]
) -> ContradictionMateriality:
    """A contradiction is material when both sides include Tier I evidence --
    that is exactly the case an operator cannot safely wave away. It is
    low materiality when neither side rises above Tier III speculation."""
    supporting_tiers = {item.tier for item in supporting}
    opposing_tiers = {item.tier for item in opposing}

    if "I" in supporting_tiers and "I" in opposing_tiers:
        return "high"
    if supporting_tiers <= {"III"} and opposing_tiers <= {"III"}:
        return "low"
    return "medium"


def create_contradiction(
    contradiction_id: str,
    claim_or_question: str,
    supporting: Sequence[EvidenceItem],
    opposing: Sequence[EvidenceItem],
) -> Contradiction:
    if not supporting or not opposing:
        raise InvalidRequestError(
            "a contradiction requires at least one supporting and one opposing evidence item"
        )
    return Contradiction(
        contradiction_id=contradiction_id,
        claim_or_question=claim_or_question,
        supporting_evidence_ids=[item.evidence_id for item in supporting],
        opposing_evidence_ids=[item.evidence_id for item in opposing],
        materiality=classify_materiality(supporting, opposing),
        status="open",
    )


def resolve_partially(
    contradiction: Contradiction, resolved_by_evidence_ids: Sequence[str], reason: str
) -> Contradiction:
    _require_reason(reason)
    _require_known_evidence(contradiction, resolved_by_evidence_ids)
    return contradiction.model_copy(
        update={
            "status": "partially_resolved",
            "resolution_reason": reason,
            "resolved_by_evidence_ids": list(resolved_by_evidence_ids),
        }
    )


def resolve_fully(
    contradiction: Contradiction, resolved_by_evidence_ids: Sequence[str], reason: str
) -> Contradiction:
    _require_reason(reason)
    _require_known_evidence(contradiction, resolved_by_evidence_ids)
    return contradiction.model_copy(
        update={
            "status": "resolved",
            "resolution_reason": reason,
            "resolved_by_evidence_ids": list(resolved_by_evidence_ids),
        }
    )


def escalate(contradiction: Contradiction, reason: str) -> Contradiction:
    _require_reason(reason)
    return contradiction.model_copy(
        update={"status": "operator_review_required", "resolution_reason": reason}
    )


def _require_reason(reason: str) -> None:
    if not reason or not reason.strip():
        raise InvalidRequestError("contradiction resolution requires a non-empty reason")


def _require_known_evidence(contradiction: Contradiction, evidence_ids: Sequence[str]) -> None:
    known = set(contradiction.supporting_evidence_ids) | set(contradiction.opposing_evidence_ids)
    unknown = [eid for eid in evidence_ids if eid not in known]
    if unknown:
        raise InvalidRequestError(
            f"resolution references evidence not part of the contradiction: {unknown}"
        )


def detect_from_evidence(evidence: Sequence[EvidenceItem]) -> List[Contradiction]:
    """Structural contradiction detection: no semantic judgement, just a
    deterministic pairing rule. If one evidence item's ``supports_claims``
    names a claim label and another's ``opposes_claims`` names the same
    label, that pair is a contradiction over that claim. Fixtures decide
    what the claim labels mean; this function only pairs them up,
    deterministically sorted so results are stable across runs."""
    supporting_by_claim: dict[str, List[EvidenceItem]] = {}
    opposing_by_claim: dict[str, List[EvidenceItem]] = {}
    for item in evidence:
        for claim in item.supports_claims:
            supporting_by_claim.setdefault(claim, []).append(item)
        for claim in item.opposes_claims:
            opposing_by_claim.setdefault(claim, []).append(item)

    contradictions: List[Contradiction] = []
    for claim in sorted(set(supporting_by_claim) & set(opposing_by_claim)):
        contradictions.append(
            create_contradiction(
                contradiction_id=f"contradiction-{claim}",
                claim_or_question=claim,
                supporting=supporting_by_claim[claim],
                opposing=opposing_by_claim[claim],
            )
        )
    return contradictions


def has_unresolved_material_contradiction(contradictions: Sequence[Contradiction]) -> bool:
    return any(
        c.materiality == "high" and c.status in ("open", "partially_resolved")
        for c in contradictions
    )


def open_contradiction_ids(contradictions: Sequence[Contradiction]) -> List[str]:
    return [c.contradiction_id for c in contradictions if c.status in ("open", "partially_resolved")]
