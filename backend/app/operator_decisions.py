"""Read-only operator decision packet engine for Black Albion RAG.

The v0.7.0 Operator Decision Packet Engine turns v0.6 promotion readiness
records into operator-readable decision labels. It does not approve,
promote, mutate, sign, or write to canonical ledgers.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


DECISION_LABELS = (
    "approve_for_corrected_wording_review",
    "needs_more_source_work",
    "do_not_promote",
    "tier_iii_only",
    "ready_for_separate_promotion_commit",
)


def _as_text(value: Any) -> str:
    return "" if value is None else str(value)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "yes", "approved", "1"}


def _explicit_operator_approval(claim: Dict[str, Any], candidate: Optional[Dict[str, Any]]) -> bool:
    candidate = candidate or {}
    approval_values = (
        claim.get("operator_approval_exists"),
        claim.get("operator_approved"),
        claim.get("approval_status"),
        claim.get("final_decision"),
        candidate.get("operator_approval_exists"),
        candidate.get("operator_approved"),
        candidate.get("approval_status"),
        candidate.get("final_decision"),
    )
    return any(
        _truthy(value)
        or str(value).strip().lower()
        in {
            "approved_for_separate_promotion_commit",
            "ready_for_separate_promotion_commit",
        }
        for value in approval_values
    )


def _metadata_bool(
    claim: Dict[str, Any],
    candidate: Optional[Dict[str, Any]],
    key: str,
) -> bool:
    """Read a safety flag without letting candidate metadata override a claim.

    Candidate-level flags are useful defaults, but a claim-level false value is
    more specific and must keep that individual claim locked.
    """
    if key in claim:
        return _truthy(claim.get(key))
    return _truthy((candidate or {}).get(key))


def _canonical_and_commit_allowed(
    claim: Dict[str, Any],
    candidate: Optional[Dict[str, Any]],
) -> bool:
    canonical_allowed = _metadata_bool(
        claim,
        candidate,
        "canonical_ingestion_allowed",
    )
    commit_allowed = _metadata_bool(
        claim,
        candidate,
        "promotion_commit_allowed",
    )
    return canonical_allowed and commit_allowed


def _decision_reason(label: str, claim: Dict[str, Any]) -> str:
    readiness = _as_text(claim.get("readiness"))
    recommendation = _as_text(claim.get("recommendation"))
    if label == "tier_iii_only":
        return "Tier III / speculative material has no Tier I promotion path."
    if label == "needs_more_source_work":
        if readiness == "blocked_unverified_identifier":
            return "Exact identifier, accession, catalogue, or archive support is unresolved."
        if readiness == "blocked_exact_text_unverified":
            return "Exact text, RIB id, object identity, or accession evidence is unresolved."
        if readiness == "blocked_missing_sources":
            return "Required source support is still missing."
        return recommendation or "Claim is not ready and needs further source work."
    if label == "do_not_promote":
        return "Original or unsupported phrasing must not enter canonical data."
    if label == "ready_for_separate_promotion_commit":
        return "Explicit metadata permits future promotion, but only in a separate operator-approved commit."
    return "Corrected wording can be reviewed by an operator; this is not canonical promotion."


def classify_operator_decision(
    claim_readiness: Dict[str, Any],
    candidate: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Map one v0.6 readiness record to a read-only operator decision label."""
    readiness = _as_text(claim_readiness.get("readiness"))
    blocked_terms = list(claim_readiness.get("blocked_terms") or [])
    source_gaps = list(claim_readiness.get("missing_sources") or [])
    explicit_promotion_ready = (
        _canonical_and_commit_allowed(claim_readiness, candidate)
        and _explicit_operator_approval(claim_readiness, candidate)
    )

    local_text = " ".join(
        [
            readiness,
            _as_text(claim_readiness.get("source_status")),
            _as_text(claim_readiness.get("promotion_readiness_raw")),
            _as_text(claim_readiness.get("recommendation")),
            " ".join(blocked_terms),
        ]
    ).lower()

    if claim_readiness.get("tier_iii_containment") or readiness == "tier_iii_only":
        label = "tier_iii_only"
    elif any(term in local_text for term in ("do_not_promote", "do not promote", "rejected original")):
        label = "do_not_promote"
    elif readiness in {
        "blocked_unverified_identifier",
        "blocked_exact_text_unverified",
        "blocked_missing_sources",
        "not_ready",
        "unknown",
    }:
        label = "needs_more_source_work"
    elif explicit_promotion_ready:
        label = "ready_for_separate_promotion_commit"
    elif readiness in {
        "ready_for_corrected_wording_review",
        "nearly_ready_for_operator_review",
    }:
        label = "approve_for_corrected_wording_review"
    else:
        label = "needs_more_source_work"

    canonical_allowed = label == "ready_for_separate_promotion_commit"
    required_approval = (
        "Separate operator-approved promotion commit required"
        if canonical_allowed
        else "Operator review required; no canonical promotion allowed from this packet"
    )

    return {
        "claim_id": _as_text(claim_readiness.get("claim_id")),
        "claim_number": claim_readiness.get("claim_number"),
        "decision_label": label,
        "decision_is_recommendation_only": True,
        "executed": False,
        "reason": _decision_reason(label, claim_readiness),
        "evidence_basis": {
            "readiness": readiness,
            "source_status": _as_text(claim_readiness.get("source_status")),
            "recommendation": _as_text(claim_readiness.get("recommendation")),
        },
        "source_gaps": source_gaps,
        "corrected_wording_available": bool(
            claim_readiness.get("corrected_wording_available", False)
        ),
        "tier_iii_containment": bool(
            claim_readiness.get("tier_iii_containment", False)
        ),
        "canonical_promotion_allowed": canonical_allowed,
        "future_promotion_path_possible": label == "ready_for_separate_promotion_commit",
        "required_approval": required_approval,
        "safety_notes": [
            "Decision label is a recommendation only.",
            "Engine does not execute decisions.",
            "No canonical ledger writes are performed.",
            "Promotion requires a separate operator-approved commit.",
        ],
    }


def summarize_candidate_decision_packet(
    candidate_readiness: Dict[str, Any],
) -> Dict[str, Any]:
    """Summarise operator decisions for one promotion-readiness candidate."""
    claims = [
        classify_operator_decision(claim, candidate_readiness)
        for claim in candidate_readiness.get("claims", []) or []
        if isinstance(claim, dict)
    ]
    label_counts = {label: 0 for label in DECISION_LABELS}
    for claim in claims:
        label_counts[claim["decision_label"]] += 1

    explicit_unlocked = _canonical_and_commit_allowed({}, candidate_readiness)
    return {
        "candidate_id": _as_text(candidate_readiness.get("candidate_id")),
        "proposed_site_id": _as_text(candidate_readiness.get("proposed_site_id")),
        "name": _as_text(candidate_readiness.get("name")),
        "review_status": _as_text(candidate_readiness.get("review_status")),
        "operator_packet": _as_text(candidate_readiness.get("operator_packet")),
        "total_claims": len(claims),
        "decision_label_counts": label_counts,
        "canonical_promotion_locked": not explicit_unlocked,
        "has_future_promotion_candidates": any(
            claim["future_promotion_path_possible"] for claim in claims
        ),
        "claims": claims,
    }


def summarize_operator_decision_queue(
    promotion_readiness_queue: Dict[str, Any],
) -> Dict[str, Any]:
    """Roll up read-only operator decision packets for the queue."""
    candidates = [
        summarize_candidate_decision_packet(candidate)
        for candidate in promotion_readiness_queue.get("candidates", []) or []
        if isinstance(candidate, dict)
    ]
    label_counts = {label: 0 for label in DECISION_LABELS}
    for candidate in candidates:
        for label, count in candidate["decision_label_counts"].items():
            label_counts[label] += count

    return {
        "total_candidates": len(candidates),
        "total_claims": sum(candidate["total_claims"] for candidate in candidates),
        "label_counts": label_counts,
        "total_ready_for_separate_promotion_commit": label_counts[
            "ready_for_separate_promotion_commit"
        ],
        "total_tier_iii_only": label_counts["tier_iii_only"],
        "total_needs_more_source_work": label_counts["needs_more_source_work"],
        "total_approve_for_corrected_wording_review": label_counts[
            "approve_for_corrected_wording_review"
        ],
        "candidates": candidates,
    }
