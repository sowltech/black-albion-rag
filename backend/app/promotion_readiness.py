"""Read-only promotion readiness classifier for Black Albion RAG.

The v0.6.0 Promotion Readiness Engine normalises candidate-claim metadata
into operator-readable states. It never writes files, never approves
promotion, and never infers canonical write permission.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


READINESS_STATES = (
    "nearly_ready_for_operator_review",
    "blocked_missing_sources",
    "blocked_unverified_identifier",
    "blocked_exact_text_unverified",
    "ready_for_corrected_wording_review",
    "tier_iii_only",
    "not_ready",
    "unknown",
)

_CLAIM_ID_NUMBER_RE = re.compile(r"_(\d{3})$")
_CLAIM_HEADING_RE = re.compile(
    r"^### Claim\s+(?P<number>\d+)\s+[^\n]*\n(?P<body>.*?)(?=^### Claim\s+\d+\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)
_CORRECTED_WORDING_RE = re.compile(
    r"corrected_claim_text|corrected canonical candidate wording|draft only",
    re.IGNORECASE,
)


def _as_text(value: Any) -> str:
    return "" if value is None else str(value)


def _claim_number(claim: Dict[str, Any]) -> Optional[int]:
    claim_id = _as_text(claim.get("candidate_claim_id") or claim.get("claim_id"))
    match = _CLAIM_ID_NUMBER_RE.search(claim_id)
    if match:
        return int(match.group(1))
    return None


def _worksheet_section(number: Optional[int], text: str) -> str:
    if number is None or not text:
        return ""
    for match in _CLAIM_HEADING_RE.finditer(text):
        if int(match.group("number")) == number:
            return match.group(0)
    return ""


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(needle in lowered for needle in needles)


def _contains_exact_text_blocker(text: str) -> bool:
    return bool(
        re.search(r"\bRIB\b", text)
        or re.search(r"\bexact\s+Latin\b", text, flags=re.IGNORECASE)
        or re.search(r"\bVivas\s+in\s+Deo\b", text, flags=re.IGNORECASE)
        or re.search(r"\bSOROR\s+AVE\b", text, flags=re.IGNORECASE)
    )


def _listify(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _extract_missing_sources(claim: Dict[str, Any], section: str) -> List[str]:
    missing: List[str] = []
    missing.extend(_listify(claim.get("required_sources")))
    missing.extend(_listify(claim.get("remaining_gaps")))
    for key in (
        "accession_identifier_status",
        "inscription_text_status",
        "object_identification_status",
    ):
        value = _as_text(claim.get(key))
        if value and _contains_any(value, ("unverified", "unresolved", "blocked")):
            missing.append(value)

    for pattern in (
        r"- \*\*remaining_gaps\*\*:\n(?P<body>.*?)(?=^- \*\*|^###|\Z)",
        r"- \*\*evidence_gap\*\*: (?P<body>.*?)(?=^- \*\*|^###|\Z)",
    ):
        match = re.search(pattern, section, flags=re.MULTILINE | re.DOTALL)
        if match:
            body = " ".join(line.strip(" -") for line in match.group("body").splitlines())
            if body.strip():
                missing.append(body.strip())

    deduped: List[str] = []
    seen = set()
    for item in missing:
        normalized = " ".join(item.split())
        if normalized and normalized not in seen:
            seen.add(normalized)
            deduped.append(normalized)
    return deduped


def _extract_blocked_terms(claim: Dict[str, Any], section: str) -> List[str]:
    terms = _listify(claim.get("unsupported_terms"))
    known_terms = (
        "YORYM : 1996.115",
        "exact Latin / RIB ID unresolved",
        "Tier III-only Claim 8",
        "Vale of York Fault Flexures",
        "Howardian Hills Fault Margin",
        "Ouse-Foss fluvial siphon loop",
        "subsurface aquifer saturated clays",
    )
    haystack = f"{claim} {section}"
    for term in known_terms:
        if term.lower() in haystack.lower() and term not in terms:
            terms.append(term)
    if (
        _contains_exact_text_blocker(haystack)
        and "exact Latin / RIB ID unresolved" not in terms
    ):
        terms.append("exact Latin / RIB ID unresolved")
    return terms


def _recommendation(readiness: str, missing_sources: List[str]) -> str:
    if readiness == "tier_iii_only":
        return "Keep as Tier III speculative-only material; no Tier I promotion path."
    if readiness == "blocked_unverified_identifier":
        return "Keep blocked until the exact accession / catalogue / archive identifier is independently verified."
    if readiness == "blocked_exact_text_unverified":
        return "Keep blocked until exact inscription text, RIB id, or object accession is independently verified."
    if readiness == "ready_for_corrected_wording_review":
        return "Operator may review corrected wording only; unsupported phrases must remain excluded."
    if readiness == "nearly_ready_for_operator_review":
        return "Ready for operator review only; promotion requires a separate approved commit."
    if readiness == "blocked_missing_sources":
        first = missing_sources[0] if missing_sources else "required source"
        return f"Keep blocked until missing source is attached: {first}"
    if readiness == "not_ready":
        return "Not ready for promotion; continue source hunting or correction."
    return "Manual review required."


def classify_claim_readiness(
    claim: Dict[str, Any],
    worksheet_text: str = "",
    packet_text: str = "",
) -> Dict[str, Any]:
    """Classify one candidate claim into a read-only readiness state."""
    number = _claim_number(claim)
    section = _worksheet_section(number, worksheet_text)
    combined = " ".join(
        [
            _as_text(claim.get("claim_text")),
            _as_text(claim.get("source_status")),
            _as_text(claim.get("promotion_readiness")),
            _as_text(claim.get("promotion_path")),
            _as_text(claim.get("accession_identifier_status")),
            _as_text(claim.get("inscription_text_status")),
            _as_text(claim.get("object_identification_status")),
            " ".join(_listify(claim.get("unsupported_terms"))),
            section,
            packet_text if number in (5, 6, 7, 8) else "",
        ]
    )
    local_combined = " ".join(
        [
            _as_text(claim.get("claim_text")),
            _as_text(claim.get("source_status")),
            _as_text(claim.get("promotion_readiness")),
            _as_text(claim.get("promotion_path")),
            _as_text(claim.get("accession_identifier_status")),
            _as_text(claim.get("inscription_text_status")),
            _as_text(claim.get("object_identification_status")),
            " ".join(_listify(claim.get("unsupported_terms"))),
            section,
        ]
    )
    lowered = combined.lower()
    local_lowered = local_combined.lower()
    claim_only_text = " ".join(
        [
            _as_text(claim.get("claim_text")),
            _as_text(claim.get("source_status")),
            _as_text(claim.get("promotion_path")),
            _as_text(claim.get("promotion_recommendation")),
        ]
    ).lower()
    source_status = _as_text(claim.get("source_status"))
    readiness_raw = _as_text(claim.get("promotion_readiness"))
    tier_candidate = _as_text(claim.get("tier_candidate")).upper()
    tier_iii_containment = (
        tier_candidate == "III"
        or source_status == "speculative_lens_only"
        or (
            claim.get("tier_i_promotion_allowed") is False
            and tier_candidate != "I"
        )
        or (
            _as_text(claim.get("promotion_path")).lower() == "none"
            and tier_candidate != "I"
        )
        or number == 8
        or "speculative_lens_only" in claim_only_text
    )

    if tier_iii_containment:
        readiness = "tier_iii_only"
    elif (
        _contains_exact_text_blocker(local_combined)
        and _contains_any(local_lowered, ("unverified", "unresolved", "blocked"))
        and "not_ready" in readiness_raw
    ):
        readiness = "blocked_exact_text_unverified"
    elif (
        _contains_any(local_lowered, ("yorym", "accession", "catalogue", "identifier"))
        and _contains_any(local_lowered, ("unverified", "unresolved", "blocked"))
        and "not_ready" in readiness_raw
    ):
        readiness = "blocked_unverified_identifier"
    elif claim.get("unsupported_terms") or "corrected bgs" in lowered:
        readiness = "ready_for_corrected_wording_review"
    elif "nearly_ready" in readiness_raw:
        readiness = "nearly_ready_for_operator_review"
    elif "partial_sources_attached" in source_status and _contains_any(
        lowered, ("gap", "missing", "required", "unverified", "unresolved", "blocked")
    ):
        readiness = "blocked_missing_sources"
    elif "not_ready" in readiness_raw:
        readiness = "not_ready"
    elif source_status:
        readiness = "not_ready"
    else:
        readiness = "unknown"

    missing_sources = _extract_missing_sources(claim, section)
    blocked_terms = _extract_blocked_terms(claim, section)
    corrected_wording_available = bool(_CORRECTED_WORDING_RE.search(section) or _CORRECTED_WORDING_RE.search(packet_text))
    canonical_ingestion_allowed = bool(claim.get("canonical_data_allowed", False))
    promotion_commit_allowed = bool(claim.get("promotion_commit_allowed", False))

    return {
        "claim_id": _as_text(claim.get("candidate_claim_id") or claim.get("claim_id")),
        "claim_number": number,
        "title": _as_text(claim.get("claim_text"))[:120],
        "readiness": readiness,
        "source_status": source_status,
        "promotion_readiness_raw": readiness_raw,
        "missing_sources": missing_sources,
        "blocked_terms": blocked_terms,
        "corrected_wording_available": corrected_wording_available,
        "operator_approval_required": bool(claim.get("operator_approval_required", True)),
        "canonical_ingestion_allowed": canonical_ingestion_allowed,
        "promotion_commit_allowed": promotion_commit_allowed,
        "tier_iii_containment": tier_iii_containment,
        "recommendation": _recommendation(readiness, missing_sources),
    }


def summarize_candidate_readiness(
    candidate: Dict[str, Any],
    worksheet_text: str = "",
    packet_text: str = "",
) -> Dict[str, Any]:
    """Summarise promotion readiness for one candidate intake row."""
    claims = [
        classify_claim_readiness(claim, worksheet_text, packet_text)
        for claim in candidate.get("candidate_claims", []) or []
        if isinstance(claim, dict)
    ]
    nearly_ready_count = sum(
        1 for claim in claims if claim["readiness"] == "nearly_ready_for_operator_review"
    )
    blocked_count = sum(1 for claim in claims if claim["readiness"].startswith("blocked_"))
    tier_iii_only_count = sum(1 for claim in claims if claim["readiness"] == "tier_iii_only")
    missing_source_count = sum(len(claim["missing_sources"]) for claim in claims)
    corrected_wording_count = sum(
        1 for claim in claims if claim["corrected_wording_available"]
    )
    return {
        "candidate_id": _as_text(candidate.get("candidate_id")),
        "proposed_site_id": _as_text(candidate.get("proposed_site_id")),
        "name": _as_text(candidate.get("name")),
        "review_status": _as_text(candidate.get("review_status") or "unknown"),
        "operator_packet": _as_text(
            candidate.get("operator_packet")
            or candidate.get("operator_packet_file")
            or ""
        ),
        "nearly_ready_count": nearly_ready_count,
        "blocked_count": blocked_count,
        "tier_iii_only_count": tier_iii_only_count,
        "missing_source_count": missing_source_count,
        "corrected_wording_count": corrected_wording_count,
        "canonical_promotion_locked": not bool(
            candidate.get("canonical_ingestion_allowed", False)
            and candidate.get("promotion_commit_allowed", False)
        ),
        "canonical_ingestion_allowed": bool(
            candidate.get("canonical_ingestion_allowed", False)
        ),
        "promotion_commit_allowed": bool(
            candidate.get("promotion_commit_allowed", False)
        ),
        "claims": claims,
    }


def _read_optional_text(base_path: Path, relative_path: Any) -> str:
    if not relative_path:
        return ""
    path = base_path / str(relative_path)
    try:
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8")
    except OSError:
        return ""
    return ""


def summarize_promotion_readiness_queue(
    candidates: List[Dict[str, Any]],
    base_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Summarise readiness across candidate rows without mutating anything."""
    root = base_path or Path(".")
    summaries: List[Dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        worksheet_text = _read_optional_text(root, candidate.get("source_review_file"))
        packet_text = _read_optional_text(
            root,
            candidate.get("operator_packet") or candidate.get("operator_packet_file"),
        )
        summaries.append(
            summarize_candidate_readiness(candidate, worksheet_text, packet_text)
        )

    total_claims = sum(len(candidate["claims"]) for candidate in summaries)
    total_nearly_ready = sum(candidate["nearly_ready_count"] for candidate in summaries)
    total_blocked = sum(candidate["blocked_count"] for candidate in summaries)
    total_tier_iii_only = sum(candidate["tier_iii_only_count"] for candidate in summaries)
    total_missing_sources = sum(candidate["missing_source_count"] for candidate in summaries)

    return {
        "total_candidates": len(summaries),
        "total_claims": total_claims,
        "total_nearly_ready": total_nearly_ready,
        "total_blocked": total_blocked,
        "total_tier_iii_only": total_tier_iii_only,
        "total_missing_sources": total_missing_sources,
        "candidates": summaries,
    }
