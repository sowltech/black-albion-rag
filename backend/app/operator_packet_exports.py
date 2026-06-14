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


def _canonical_lock(candidate_decision_packet: Dict[str, Any]) -> Dict[str, bool]:
    canonical_allowed = _bool(
        candidate_decision_packet.get("canonical_ingestion_allowed")
    )
    commit_allowed = _bool(candidate_decision_packet.get("promotion_commit_allowed"))
    locked = _bool(candidate_decision_packet.get("canonical_promotion_locked", True))
    if not (canonical_allowed and commit_allowed):
        locked = True
    return {
        "canonical_ingestion_allowed": canonical_allowed,
        "promotion_commit_allowed": commit_allowed,
        "canonical_promotion_locked": locked,
        "executed": False,
    }


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
    canonical_lock = _canonical_lock(candidate_decision_packet)
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
        "canonical_lock": canonical_lock,
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
    candidate_id = _as_text(export_packet.get("candidate_id")) or "unknown_candidate"
    schema_version = _as_text(export_packet.get("schema_version")) or SCHEMA_VERSION
    artifact_type = (
        _as_text(export_packet.get("artifact_type")) or "operator_packet_export"
    )
    generated_from = _as_text(export_packet.get("generated_from")) or GENERATED_FROM
    decision_summary = {
        label: int((export_packet.get("decision_summary") or {}).get(label, 0) or 0)
        for label in DECISION_LABELS
    }
    claims = [
        claim
        for claim in export_packet.get("claims", []) or []
        if isinstance(claim, dict)
    ]
    tier_iii = export_packet.get("tier_iii_containment") or {}
    lock = export_packet.get("canonical_lock") or {}
    safety = {**EXPORT_SAFETY, **(export_packet.get("export_safety") or {})}
    lines: List[str] = [
        f"# Operator Packet Export — {candidate_id}",
        "",
        "## Export Status",
        f"- schema_version: {schema_version}",
        f"- artifact_type: {artifact_type}",
        f"- generated_from: {generated_from}",
        f"- read_only: {_markdown_bool(export_packet.get('read_only', True))}",
        f"- executed: {_markdown_bool(export_packet.get('executed', False))}",
        "",
        "## Candidate Summary",
        f"- candidate_id: {candidate_id}",
        f"- review_status: {_as_text(export_packet.get('review_status')) or 'unknown'}",
        f"- operator_packet_source: {_as_text(export_packet.get('operator_packet_source')) or 'not detected'}",
        "",
        "## Decision Label Summary",
        "| Label | Count |",
        "|---|---:|",
    ]
    for label, count in decision_summary.items():
        lines.append(f"| {label} | {count} |")

    lines.extend(
        [
            "",
            "## Claim Review Table",
            "| Claim | Decision | Readiness | Source Gaps | Tier III | Required Approval |",
            "|---|---|---|---:|---|---|",
        ]
    )
    for claim in claims:
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
    if not claims:
        lines.append("- No candidate claims extracted; no promotable facts.")
    for claim in claims:
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

    lines.extend(
        [
            "",
            "## Tier III Containment",
            f"- present: {_markdown_bool(tier_iii.get('present', False))}",
            f"- claim_numbers: {tier_iii.get('claim_numbers', [])}",
            f"- canonical_data_allowed: {_markdown_bool(tier_iii.get('canonical_data_allowed', False))}",
            f"- tier_i_promotion_allowed: {_markdown_bool(tier_iii.get('tier_i_promotion_allowed', False))}",
            "",
            "## Canonical Protection",
            f"- canonical_ingestion_allowed: {_markdown_bool(lock.get('canonical_ingestion_allowed', False))}",
            f"- promotion_commit_allowed: {_markdown_bool(lock.get('promotion_commit_allowed', False))}",
            f"- canonical_promotion_locked: {_markdown_bool(lock.get('canonical_promotion_locked', True))}",
            f"- executed: {_markdown_bool(lock.get('executed', False))}",
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
    schema_version = _as_text(export_queue.get("schema_version")) or SCHEMA_VERSION
    artifact_type = (
        _as_text(export_queue.get("artifact_type"))
        or "operator_packet_export_queue"
    )
    generated_from = _as_text(export_queue.get("generated_from")) or GENERATED_FROM
    exports = [
        packet
        for packet in export_queue.get("exports", []) or []
        if isinstance(packet, dict)
    ]
    decision_summary = {
        label: int((export_queue.get("decision_summary") or {}).get(label, 0) or 0)
        for label in DECISION_LABELS
    }
    safety = {**EXPORT_SAFETY, **(export_queue.get("export_safety") or {})}
    lines: List[str] = [
        "# Operator Packet Export Queue",
        "",
        "## Export Status",
        f"- schema_version: {schema_version}",
        f"- artifact_type: {artifact_type}",
        f"- generated_from: {generated_from}",
        f"- read_only: {_markdown_bool(export_queue.get('read_only', True))}",
        f"- executed: {_markdown_bool(export_queue.get('executed', False))}",
        "",
        "## Queue Summary",
        f"- total_candidates: {export_queue.get('total_candidates', len(exports))}",
        f"- total_claims: {export_queue.get('total_claims', 0)}",
        "",
        "## Decision Label Summary",
        "| Label | Count |",
        "|---|---:|",
    ]
    for label, count in decision_summary.items():
        lines.append(f"| {label} | {count} |")

    lines.extend(["", "## Candidate Exports"])
    if not exports:
        lines.append("- No candidate exports available.")
    for packet in exports:
        lines.extend(
            [
                "",
                f"## Candidate — {_as_text(packet.get('candidate_id')) or 'unknown_candidate'}",
                build_operator_packet_markdown(packet).strip(),
            ]
        )

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
