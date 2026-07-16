"""Disabled-by-default Aegis recommendation canary for Black Albion.

This module is an adapter, not a reasoning engine. It maps an existing
candidate-claim review snapshot to the Sirius Nexus Brain API Aegis contract
and returns a recommendation for Black Albion operator review. It never
promotes claims, mutates evidence tiers, writes source records, or opens
canonical ledgers.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import httpx
import yaml


ADAPTER_VERSION = "black-albion-aegis-canary.v1"
AEGIS_SCHEMA_VERSION = "aegis.v1"
RECOMMEND_PROMOTE = "recommend_promote"
RECOMMEND_HOLD = "recommend_hold"
RECOMMEND_REJECT = "recommend_reject"
UNAVAILABLE = "unavailable"
VALID_RECOMMENDATIONS = {RECOMMEND_PROMOTE, RECOMMEND_HOLD, RECOMMEND_REJECT, UNAVAILABLE}


class BlackAlbionAegisConfigError(ValueError):
    """Raised when the Aegis canary configuration is ambiguous or unsafe."""


class AegisClientError(RuntimeError):
    """Raised when the Aegis transport cannot return a valid recommendation."""


@dataclass(frozen=True)
class AegisCanaryConfig:
    enabled: bool = False
    base_url: str = "http://localhost:8055"
    timeout_seconds: float = 2.0
    excerpt_limit: int = 500
    require_audit_reference: bool = True


@dataclass(frozen=True)
class CandidateClaim:
    claim_id: str
    claim_text: str
    module: str = ""
    evidence_tier: str = ""
    candidate_status: str = ""
    created_at: str = ""
    provenance_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    source_id: str
    excerpt: str
    relationship: str = "supports"
    authority_score: float = 0.5
    quality_score: float = 0.5
    freshness_timestamp: str = ""
    evidence_tier: str = ""
    provenance_location: str = ""


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    title: str
    source_tier: str = ""
    authority_score: float = 0.5
    provenance_location: str = ""


@dataclass(frozen=True)
class AegisRecommendation:
    recommendation: str
    request_fingerprint: str
    machine_status: str = "Unavailable"
    aegis_decision_id: str = ""
    support_score: float = 0.0
    attack_score: float = 0.0
    confidence: float = 0.0
    supporting_source_ids: tuple[str, ...] = ()
    opposing_source_ids: tuple[str, ...] = ()
    unresolved_conflicts: tuple[str, ...] = ()
    audit_reference: str = ""
    aegis_schema_version: str = AEGIS_SCHEMA_VERSION
    adapter_version: str = ADAPTER_VERSION
    reason: str = ""
    evaluated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _strict_bool(value: Any, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    raise BlackAlbionAegisConfigError(f"{field_name} must be a YAML boolean")


def load_aegis_canary_config(path: Optional[Path] = None) -> AegisCanaryConfig:
    """Load strict Aegis canary config.

    Absent config and explicit YAML null are treated as disabled. Strings,
    integers, lists, and mappings for the `enabled` field are rejected rather
    than coerced.
    """
    raw_path = path or (Path(os.environ["BLACK_ALBION_AEGIS_CONFIG"]) if os.getenv("BLACK_ALBION_AEGIS_CONFIG") else None)
    if raw_path is None:
        return AegisCanaryConfig(enabled=False)
    try:
        payload = yaml.safe_load(raw_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise BlackAlbionAegisConfigError("Aegis canary config could not be read") from exc
    except yaml.YAMLError as exc:
        raise BlackAlbionAegisConfigError("Aegis canary config is not valid YAML") from exc
    if payload is None:
        return AegisCanaryConfig(enabled=False)
    if not isinstance(payload, dict):
        raise BlackAlbionAegisConfigError("Aegis canary config root must be a mapping")
    section = payload.get("aegis_canary", {})
    if section is None:
        return AegisCanaryConfig(enabled=False)
    if not isinstance(section, dict):
        raise BlackAlbionAegisConfigError("aegis_canary must be a mapping")
    enabled = section.get("enabled", False)
    if enabled is None:
        return AegisCanaryConfig(enabled=False)
    enabled = _strict_bool(enabled, "aegis_canary.enabled")
    base_url = str(section.get("base_url") or "http://localhost:8055").rstrip("/")
    timeout = section.get("timeout_seconds", 2.0)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 30:
        raise BlackAlbionAegisConfigError("aegis_canary.timeout_seconds must be a positive number <= 30")
    excerpt_limit = section.get("excerpt_limit", 500)
    if isinstance(excerpt_limit, bool) or not isinstance(excerpt_limit, int) or excerpt_limit < 80 or excerpt_limit > 2000:
        raise BlackAlbionAegisConfigError("aegis_canary.excerpt_limit must be an integer between 80 and 2000")
    require_audit = section.get("require_audit_reference", True)
    if require_audit is None:
        require_audit = True
    require_audit = _strict_bool(require_audit, "aegis_canary.require_audit_reference")
    return AegisCanaryConfig(
        enabled=enabled,
        base_url=base_url,
        timeout_seconds=float(timeout),
        excerpt_limit=excerpt_limit,
        require_audit_reference=require_audit,
    )


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]
    return f"ba-{prefix}-{digest}"


def _normalise_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _tier_authority(tier: str) -> float:
    return {"I": 0.95, "II": 0.7, "III": 0.35}.get(str(tier or "").upper(), 0.5)


def _bounded_excerpt(text: str, limit: int) -> str:
    clean = _normalise_text(text)
    return clean[:limit]


def candidate_from_dict(candidate: Mapping[str, Any], claim: Mapping[str, Any]) -> CandidateClaim:
    claim_id = _normalise_text(claim.get("candidate_claim_id") or claim.get("claim_id"))
    return CandidateClaim(
        claim_id=claim_id,
        claim_text=_normalise_text(claim.get("claim_text")),
        module=",".join(sorted(str(item) for item in candidate.get("related_modules", []) or [])),
        evidence_tier=_normalise_text(claim.get("tier_candidate")),
        candidate_status=_normalise_text(candidate.get("review_status")),
        created_at=_normalise_text(claim.get("created_at") or candidate.get("created_at")),
        provenance_refs=tuple(
            sorted(
                item
                for item in (
                    _normalise_text(candidate.get("source_artifact")),
                    _normalise_text(candidate.get("source_review_file")),
                    _normalise_text(candidate.get("operator_packet_file")),
                    _normalise_text(candidate.get("review_note")),
                )
                if item
            )
        ),
    )


def evidence_from_dicts(
    candidate: Mapping[str, Any],
    claim: Mapping[str, Any],
    *,
    excerpt_limit: int = 500,
) -> tuple[list[EvidenceRecord], list[SourceRecord]]:
    tier = _normalise_text(claim.get("tier_candidate")) or "III"
    provenance = _normalise_text(candidate.get("source_review_file") or candidate.get("review_note") or candidate.get("source_artifact"))
    supports = list(claim.get("attached_source_names") or claim.get("supporting_source_names") or [])
    attacks = list(claim.get("opposing_source_names") or claim.get("contradicting_source_names") or [])
    evidence: list[EvidenceRecord] = []
    sources: list[SourceRecord] = []
    for relationship, names in (("supports", supports), ("attacks", attacks)):
        for index, name in enumerate(names):
            source_title = _normalise_text(name)
            if not source_title:
                continue
            source_id = _stable_id("source", source_title)
            evidence_id = _stable_id("evidence", f"{claim.get('candidate_claim_id')}:{relationship}:{source_title}:{index}")
            authority = _tier_authority(tier)
            sources.append(
                SourceRecord(
                    source_id=source_id,
                    title=source_title,
                    source_tier=tier,
                    authority_score=authority,
                    provenance_location=provenance,
                )
            )
            evidence.append(
                EvidenceRecord(
                    evidence_id=evidence_id,
                    source_id=source_id,
                    excerpt=_bounded_excerpt(source_title, excerpt_limit),
                    relationship=relationship,
                    authority_score=authority,
                    quality_score=authority,
                    freshness_timestamp=_normalise_text(claim.get("source_attachment_pass") or candidate.get("created_at")),
                    evidence_tier=tier,
                    provenance_location=provenance,
                )
            )
    return evidence, sorted(sources, key=lambda item: item.source_id)


def request_fingerprint(
    candidate_claim: CandidateClaim,
    evidence: Sequence[EvidenceRecord],
    sources: Sequence[SourceRecord],
) -> str:
    payload = {
        "adapter_version": ADAPTER_VERSION,
        "aegis_schema_version": AEGIS_SCHEMA_VERSION,
        "claim_id": candidate_claim.claim_id,
        "claim_text": _normalise_text(candidate_claim.claim_text),
        "evidence_ids": sorted(item.evidence_id for item in evidence),
        "source_ids": sorted(item.source_id for item in sources),
        "evidence_versions": sorted(
            f"{item.evidence_id}:{item.freshness_timestamp}:{item.evidence_tier}:{item.relationship}"
            for item in evidence
        ),
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def normalised_aegis_request(
    candidate_claim: CandidateClaim,
    evidence: Sequence[EvidenceRecord],
    sources: Sequence[SourceRecord],
    *,
    fingerprint: Optional[str] = None,
) -> Dict[str, Any]:
    fp = fingerprint or request_fingerprint(candidate_claim, evidence, sources)
    claim_aegis_id = _stable_id("claim", f"{candidate_claim.claim_id}:{fp}")
    return {
        "claim": {
            "id": claim_aegis_id,
            "object_type": "Claim",
            "statement": candidate_claim.claim_text,
            "source_ids": sorted(candidate_claim.provenance_refs),
            "metadata": {
                "black_albion_claim_id": candidate_claim.claim_id,
                "candidate_status": candidate_claim.candidate_status,
                "evidence_tier": candidate_claim.evidence_tier,
                "request_fingerprint": fp,
                "adapter_version": ADAPTER_VERSION,
            },
        },
        "evidence": [
            {
                "id": _stable_id("evidence", f"{item.evidence_id}:{fp}"),
                "object_type": "Evidence",
                "statement": item.excerpt,
                "source_ids": [item.source_id],
                "confidence": item.quality_score,
                "evidence_quality": item.quality_score,
                "source_authority": item.authority_score,
                "temporal_freshness": 0.8 if item.freshness_timestamp else 0.5,
                "metadata": {
                    "black_albion_evidence_id": item.evidence_id,
                    "evidence_tier": item.evidence_tier,
                    "provenance_location": item.provenance_location,
                    "request_fingerprint": fp,
                },
            }
            for item in sorted(evidence, key=lambda row: (row.relationship, row.evidence_id))
        ],
        "relationships": [
            {
                "relationship_type": "SUPPORTS" if item.relationship == "supports" else "ATTACKS",
                "source_id": _stable_id("evidence", f"{item.evidence_id}:{fp}"),
                "target_id": claim_aegis_id,
                "metadata": {
                    "black_albion_source_id": item.source_id,
                    "request_fingerprint": fp,
                },
            }
            for item in sorted(evidence, key=lambda row: (row.relationship, row.evidence_id))
        ],
        "sources": [asdict(item) for item in sorted(sources, key=lambda row: row.source_id)],
        "evaluate": {"claim_id": claim_aegis_id},
    }


class AegisRecommendationClient:
    def review_candidate(
        self,
        candidate_claim: CandidateClaim,
        evidence: Sequence[EvidenceRecord],
        sources: Sequence[SourceRecord],
    ) -> AegisRecommendation:
        raise NotImplementedError


class HttpAegisRecommendationClient(AegisRecommendationClient):
    def __init__(self, config: AegisCanaryConfig) -> None:
        self.config = config

    def _post(self, client: httpx.Client, path: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
        response = client.post(path, json=payload)
        if response.status_code >= 400 and response.status_code not in {409}:
            raise AegisClientError("Aegis request failed")
        try:
            body = response.json()
        except ValueError as exc:
            raise AegisClientError("Aegis response was not JSON") from exc
        if not isinstance(body, dict):
            raise AegisClientError("Aegis response schema mismatch")
        return body

    def review_candidate(
        self,
        candidate_claim: CandidateClaim,
        evidence: Sequence[EvidenceRecord],
        sources: Sequence[SourceRecord],
    ) -> AegisRecommendation:
        fingerprint = request_fingerprint(candidate_claim, evidence, sources)
        request = normalised_aegis_request(candidate_claim, evidence, sources, fingerprint=fingerprint)
        with httpx.Client(base_url=self.config.base_url, timeout=self.config.timeout_seconds) as client:
            self._post(client, "/claims", request["claim"])
            for item in request["evidence"]:
                self._post(client, "/evidence", item)
            for relationship in request["relationships"]:
                endpoint = "/support" if relationship["relationship_type"] == "SUPPORTS" else "/attack"
                self._post(client, endpoint, relationship)
            decision = self._post(client, "/evaluate", request["evaluate"])
        return recommendation_from_aegis_decision(decision, fingerprint, self.config)


def recommendation_from_aegis_decision(
    decision: Mapping[str, Any],
    fingerprint: str,
    config: AegisCanaryConfig,
) -> AegisRecommendation:
    status = _normalise_text(decision.get("conclusion"))
    decision_id = _normalise_text(decision.get("decision_id"))
    audit_reference = _normalise_text(decision.get("audit_reference"))
    if not decision_id:
        raise AegisClientError("Aegis response missing decision_id")
    if config.require_audit_reference and not audit_reference:
        raise AegisClientError("Aegis response missing audit_reference")
    recommendation = {
        "Accepted": RECOMMEND_PROMOTE,
        "Rejected": RECOMMEND_REJECT,
        "Undecided": RECOMMEND_HOLD,
    }.get(status, RECOMMEND_HOLD)
    supporting = tuple(
        sorted(
            str(source_id)
            for row in decision.get("supporting_evidence", []) or []
            if isinstance(row, Mapping)
            for source_id in row.get("source_ids", []) or []
        )
    )
    opposing = tuple(
        sorted(
            str(source_id)
            for row in decision.get("opposing_evidence", []) or []
            if isinstance(row, Mapping)
            for source_id in row.get("source_ids", []) or []
        )
    )
    unresolved = tuple(sorted(str(item) for item in decision.get("unresolved_conflicts", []) or []))
    return AegisRecommendation(
        recommendation=recommendation,
        request_fingerprint=fingerprint,
        machine_status=status,
        aegis_decision_id=decision_id,
        support_score=float(decision.get("support_score") or 0.0),
        attack_score=float(decision.get("attack_score") or 0.0),
        confidence=float(decision.get("confidence") or 0.0),
        supporting_source_ids=supporting,
        opposing_source_ids=opposing,
        unresolved_conflicts=unresolved,
        audit_reference=audit_reference,
        reason=_normalise_text(decision.get("reason_for_preference")),
        evaluated_at=datetime.now(timezone.utc).isoformat(),
    )


def hold_recommendation(fingerprint: str, reason: str) -> AegisRecommendation:
    return AegisRecommendation(
        recommendation=RECOMMEND_HOLD,
        request_fingerprint=fingerprint,
        reason=reason,
        evaluated_at=datetime.now(timezone.utc).isoformat(),
    )


def review_candidate_claim(
    candidate: Mapping[str, Any],
    claim: Mapping[str, Any],
    *,
    config: AegisCanaryConfig,
    client: Optional[AegisRecommendationClient] = None,
) -> AegisRecommendation:
    candidate_claim = candidate_from_dict(candidate, claim)
    evidence, sources = evidence_from_dicts(candidate, claim, excerpt_limit=config.excerpt_limit)
    fingerprint = request_fingerprint(candidate_claim, evidence, sources)
    if not config.enabled:
        return hold_recommendation(fingerprint, "aegis_canary_disabled")
    if not candidate_claim.claim_id or not candidate_claim.claim_text:
        return hold_recommendation(fingerprint, "missing_claim_identity")
    if not evidence or not sources or not candidate_claim.provenance_refs:
        return hold_recommendation(fingerprint, "missing_provenance")
    reviewer = client or HttpAegisRecommendationClient(config)
    try:
        result = reviewer.review_candidate(candidate_claim, evidence, sources)
    except (AegisClientError, httpx.TimeoutException, httpx.HTTPError, OSError, ValueError):
        return hold_recommendation(fingerprint, "aegis_unavailable")
    if result.recommendation not in VALID_RECOMMENDATIONS:
        return hold_recommendation(fingerprint, "unknown_recommendation")
    return result


def append_recommendation_history(
    existing_history: Iterable[Mapping[str, Any]],
    recommendation: AegisRecommendation,
) -> List[Dict[str, Any]]:
    """Return immutable history with idempotent reuse for the same fingerprint."""
    history = [dict(item) for item in existing_history if isinstance(item, Mapping)]
    for item in history:
        if item.get("request_fingerprint") == recommendation.request_fingerprint:
            return history
    history.append(recommendation.to_dict())
    return history

