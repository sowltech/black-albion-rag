"""Read-only operator packet export builders for Black Albion RAG.

The v0.8.0 export layer turns existing v0.7 operator decision packets into
deterministic JSON-safe and Markdown review artifacts. It does not write files,
approve decisions, promote candidates, or mutate canonical ledgers.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .operator_decisions import DECISION_LABELS


SCHEMA_VERSION = "0.8.0"
GENERATED_FROM = "operator_decision_packet_engine"
EXPORT_SAFETY = {
    "read_only": True,
    "does_not_approve": True,
    "does_not_promote": True,
    "does_not_write_canonical_ledgers": True,
    "requires_separate_operator_approved_commit": True,
}


def _as_text(value: Any) -> str:
    return "" if value is None else str(value)


def _bool(value: Any) -> bool:
    return bool(value)


def _label_counts(candidate_decision_packet: Dict[str, Any]) -> Dict[str, int]:
    raw_counts = candidate_decision_packet.get("decision_label_counts") or {}
    return {label: int(raw_counts.get(label, 0) or 0) for label in DECISION_LABELS}


def _claim_export(claim: Dict[str, Any]) -> Dict[str, Any]:
    evidence_basis = claim.get("evidence_basis") or {}
    return {
        "claim_id": _as_text(claim.get("claim_id")),
        "claim_number": claim.get("claim_number"),
        "decision_label": _as_text(claim.get("decision_label")),
        "readiness": _as_text(evidence_basis.get("readiness")),
        "source_status": _as_text(evidence_basis.get("source_status")),
        "source_gaps": list(claim.get("source_gaps") or []),
        "corrected_wording_available": _bool(
            claim.get("corrected_wording_available")
        ),
        "tier_iii_containment": _bool(claim.get("tier_iii_containment")),
        "executed": False,
        "required_approval": _as_text(claim.get("required_approval")),
        "safety_notes": list(claim.get("safety_notes") or []),
    }


def build_operator_packet_export(
    candidate_decision_packet: Dict[str, Any],
) -> Dict[str, Any]:
    """Build one JSON-safe, read-only operator packet export."""
    claims = [
        _claim_export(claim)
        for claim in candidate_decision_packet.get("claims", []) or []
        if isinstance(claim, dict)
    ]
    tier_iii_claim_numbers = [
        claim.get("claim_number")
        for claim in claims
        if claim.get("tier_iii_containment")
        or claim.get("decision_label") == "tier_iii_only"
    ]
    canonical_promotion_locked = _bool(
        candidate_decision_packet.get("canonical_promotion_locked", True)
    )
    decision_summary = _label_counts(candidate_decision_packet)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "operator_packet_export",
        "candidate_id": _as_text(candidate_decision_packet.get("candidate_id")),
        "review_status": _as_text(candidate_decision_packet.get("review_status")),
        "operator_packet_source": _as_text(
            candidate_decision_packet.get("operator_packet")
        ),
        "generated_from": GENERATED_FROM,
        "read_only": True,
        "executed": False,
        "canonical_lock": {
            "canonical_ingestion_allowed": not canonical_promotion_locked,
            "promotion_commit_allowed": not canonical_promotion_locked,
            "canonical_promotion_locked": canonical_promotion_locked,
            "executed": False,
        },
        "decision_summary": decision_summary,
        "claims": claims,
        "tier_iii_containment": {
            "present": bool(tier_iii_claim_numbers),
            "claim_numbers": tier_iii_claim_numbers,
            "canonical_data_allowed": False,
            "tier_i_promotion_allowed": False,
        },
        "export_safety": dict(EXPORT_SAFETY),
    }


def build_operator_packet_export_queue(decision_queue: Dict[str, Any]) -> Dict[str, Any]:
    """Build a queue-level JSON-safe export from operator decision output."""
    exports = [
        build_operator_packet_export(candidate)
        for candidate in decision_queue.get("candidates", []) or []
        if isinstance(candidate, dict)
    ]
    raw_counts = decision_queue.get("label_counts") or {}
    decision_summary = {
        label: int(raw_counts.get(label, 0) or 0) for label in DECISION_LABELS
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "operator_packet_export_queue",
        "generated_from": GENERATED_FROM,
        "read_only": True,
        "executed": False,
        "total_candidates": len(exports),
        "total_claims": sum(len(item["claims"]) for item in exports),
        "decision_summary": decision_summary,
        "exports": exports,
        "export_safety": dict(EXPORT_SAFETY),
    }


def _markdown_bool(value: Any) -> str:
    return "true" if bool(value) else "false"


def _markdown_list(values: List[Any]) -> str:
    if not values:
        return "- none"
    return "\n".join(f"- {_as_text(value)}" for value in values)


def build_operator_packet_markdown(export_packet: Dict[str, Any]) -> str:
    """Render one operator packet export as deterministic Markdown."""
    lines: List[str] = [
        f"# Operator Packet Export — {export_packet['candidate_id']}",
        "",
        "## Export Status",
        f"- schema_version: {export_packet['schema_version']}",
        f"- artifact_type: {export_packet['artifact_type']}",
        f"- generated_from: {export_packet['generated_from']}",
        f"- read_only: {_markdown_bool(export_packet['read_only'])}",
        f"- executed: {_markdown_bool(export_packet['executed'])}",
        "",
        "## Candidate Summary",
        f"- candidate_id: {export_packet['candidate_id']}",
        f"- review_status: {export_packet['review_status']}",
        f"- operator_packet_source: {export_packet['operator_packet_source'] or 'not detected'}",
        "",
        "## Decision Label Summary",
        "| Label | Count |",
        "|---|---:|",
    ]
    for label, count in export_packet["decision_summary"].items():
        lines.append(f"| {label} | {count} |")

    lines.extend(
        [
            "",
            "## Claim Review Table",
            "| Claim | Decision | Readiness | Source Gaps | Tier III | Required Approval |",
            "|---|---|---|---:|---|---|",
        ]
    )
    for claim in export_packet["claims"]:
        lines.append(
            "| {claim_number} | {decision_label} | {readiness} | {gap_count} | {tier_iii} | {approval} |".format(
                claim_number=claim.get("claim_number") or "n/a",
                decision_label=claim["decision_label"],
                readiness=claim["readiness"] or "unknown",
                gap_count=len(claim["source_gaps"]),
                tier_iii=_markdown_bool(claim["tier_iii_containment"]),
                approval=claim["required_approval"],
            )
        )

    lines.extend(["", "## Claim Details"])
    if not export_packet["claims"]:
        lines.append("- No candidate claims extracted; no promotable facts.")
    for claim in export_packet["claims"]:
        lines.extend(
            [
                "",
                f"### Claim {claim.get('claim_number') or 'n/a'}",
                f"- claim_id: {claim['claim_id']}",
                f"- decision_label: {claim['decision_label']}",
                f"- readiness: {claim['readiness'] or 'unknown'}",
                f"- source_status: {claim['source_status'] or 'unknown'}",
                f"- corrected_wording_available: {_markdown_bool(claim['corrected_wording_available'])}",
                f"- tier_iii_containment: {_markdown_bool(claim['tier_iii_containment'])}",
                f"- executed: {_markdown_bool(claim['executed'])}",
                f"- required_approval: {claim['required_approval']}",
                "- source_gaps:",
                _markdown_list(claim["source_gaps"]),
                "- safety_notes:",
                _markdown_list(claim["safety_notes"]),
            ]
        )

    tier_iii = export_packet["tier_iii_containment"]
    lock = export_packet["canonical_lock"]
    safety = export_packet["export_safety"]
    lines.extend(
        [
            "",
            "## Tier III Containment",
            f"- present: {_markdown_bool(tier_iii['present'])}",
            f"- claim_numbers: {tier_iii['claim_numbers']}",
            f"- canonical_data_allowed: {_markdown_bool(tier_iii['canonical_data_allowed'])}",
            f"- tier_i_promotion_allowed: {_markdown_bool(tier_iii['tier_i_promotion_allowed'])}",
            "",
            "## Canonical Protection",
            f"- canonical_ingestion_allowed: {_markdown_bool(lock['canonical_ingestion_allowed'])}",
            f"- promotion_commit_allowed: {_markdown_bool(lock['promotion_commit_allowed'])}",
            f"- canonical_promotion_locked: {_markdown_bool(lock['canonical_promotion_locked'])}",
            f"- executed: {_markdown_bool(lock['executed'])}",
            f"- read_only: {_markdown_bool(safety['read_only'])}",
            f"- does_not_approve: {_markdown_bool(safety['does_not_approve'])}",
            f"- does_not_promote: {_markdown_bool(safety['does_not_promote'])}",
            f"- does_not_write_canonical_ledgers: {_markdown_bool(safety['does_not_write_canonical_ledgers'])}",
            "- promotion requires separate operator-approved commit",
        ]
    )
    return "\n".join(lines) + "\n"


def build_operator_packet_markdown_queue(export_queue: Dict[str, Any]) -> str:
    """Render a queue-level operator packet export as deterministic Markdown."""
    lines: List[str] = [
        "# Operator Packet Export Queue",
        "",
        "## Export Status",
        f"- schema_version: {export_queue['schema_version']}",
        f"- artifact_type: {export_queue['artifact_type']}",
        f"- generated_from: {export_queue['generated_from']}",
        f"- read_only: {_markdown_bool(export_queue['read_only'])}",
        f"- executed: {_markdown_bool(export_queue['executed'])}",
        "",
        "## Queue Summary",
        f"- total_candidates: {export_queue['total_candidates']}",
        f"- total_claims: {export_queue['total_claims']}",
        "",
        "## Decision Label Summary",
        "| Label | Count |",
        "|---|---:|",
    ]
    for label, count in export_queue["decision_summary"].items():
        lines.append(f"| {label} | {count} |")

    lines.extend(["", "## Candidate Exports"])
    for packet in export_queue["exports"]:
        lines.extend(
            [
                "",
                f"## Candidate — {packet['candidate_id']}",
                build_operator_packet_markdown(packet).strip(),
            ]
        )

    safety = export_queue["export_safety"]
    lines.extend(
        [
            "",
            "## Queue Safety",
            f"- read_only: {_markdown_bool(safety['read_only'])}",
            f"- does_not_approve: {_markdown_bool(safety['does_not_approve'])}",
            f"- does_not_promote: {_markdown_bool(safety['does_not_promote'])}",
            f"- does_not_write_canonical_ledgers: {_markdown_bool(safety['does_not_write_canonical_ledgers'])}",
            "- promotion requires separate operator-approved commit",
        ]
    )
    return "\n".join(lines) + "\n"
