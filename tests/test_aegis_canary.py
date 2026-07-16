from __future__ import annotations

import json
from pathlib import Path

import pytest

import backend.app.aegis_canary as aegis_canary
from backend.app.aegis_canary import (
    AEGIS_SCHEMA_VERSION,
    ADAPTER_VERSION,
    AegisCanaryConfig,
    AegisClientError,
    AegisRecommendation,
    AegisRecommendationClient,
    BlackAlbionAegisConfigError,
    append_recommendation_history,
    candidate_from_dict,
    evidence_from_dicts,
    fingerprint_payload,
    load_aegis_canary_config,
    normalised_aegis_request,
    recommendation_from_aegis_decision,
    request_fingerprint,
    review_candidate_claim,
)
from backend.app.promotion_readiness import summarize_candidate_readiness


def _candidate() -> dict:
    return {
        "candidate_id": "cand_aegis_synthetic_001",
        "review_status": "source_hunting",
        "risk_level": "high",
        "source_artifact": "research/intake/synthetic_raw.md",
        "source_review_file": "research/intake/synthetic_source_review.md",
        "operator_packet_file": "research/intake/synthetic_operator_packet.md",
        "operator_approval_required": True,
        "promotion_commit_allowed": False,
        "canonical_ingestion_allowed": False,
        "created_at": "2026-07-16",
        "related_modules": ["albion"],
    }


def _claim() -> dict:
    return {
        "candidate_claim_id": "cand_claim_aegis_001",
        "claim_text": "Synthetic Black Albion canary claim has bounded support and opposition.",
        "tier_candidate": "I",
        "source_status": "partial_sources_attached",
        "promotion_readiness": "nearly_ready",
        "source_attachment_pass": "2026-07-16",
        "attached_source_names": ["Tier I archive source", "Tier III contextual source"],
        "opposing_source_names": ["Credible opposing source"],
        "required_sources": ["Operator packet review"],
        "operator_approval_required": True,
    }


class RecordingClient(AegisRecommendationClient):
    def __init__(self, recommendation: AegisRecommendation | None = None, exc: Exception | None = None) -> None:
        self.calls = 0
        self.recommendation = recommendation
        self.exc = exc

    def review_candidate(self, candidate_claim, evidence, sources):
        self.calls += 1
        if self.exc:
            raise self.exc
        assert self.recommendation is not None
        return self.recommendation


def _recommendation(value: str = "recommend_promote", fingerprint: str = "fp") -> AegisRecommendation:
    return AegisRecommendation(
        recommendation=value,
        request_fingerprint=fingerprint,
        machine_status="Accepted",
        aegis_decision_id="decision-001",
        support_score=0.8,
        attack_score=0.2,
        confidence=0.7,
        supporting_source_ids=("source:a",),
        opposing_source_ids=("source:b",),
        unresolved_conflicts=("one contradiction remains",),
        audit_reference="audit-001",
        reason="support stronger than attack",
    )


def _write_config(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "config.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_feature_flag_defaults_disabled_and_accepts_only_yaml_booleans(tmp_path: Path) -> None:
    assert load_aegis_canary_config().enabled is False
    assert load_aegis_canary_config(_write_config(tmp_path, "")).enabled is False
    assert load_aegis_canary_config(_write_config(tmp_path, "aegis_canary:\n  enabled: false\n")).enabled is False
    assert load_aegis_canary_config(_write_config(tmp_path, "aegis_canary:\n  enabled: true\n")).enabled is True
    assert load_aegis_canary_config(_write_config(tmp_path, "aegis_canary:\n")).enabled is False

    for value in (
        "True",
        "False",
        "TRUE",
        "FALSE",
        "yes",
        "no",
        "on",
        "off",
        '"false"',
        '"true"',
        '"yes"',
        '"no"',
        '"1"',
        '"0"',
        "0",
        "1",
        "[]",
        "{}",
    ):
        with pytest.raises(BlackAlbionAegisConfigError):
            load_aegis_canary_config(_write_config(tmp_path, f"aegis_canary:\n  enabled: {value}\n"))


def test_invalid_config_cannot_trigger_aegis_call(tmp_path: Path) -> None:
    client = RecordingClient(_recommendation())

    with pytest.raises(BlackAlbionAegisConfigError):
        load_aegis_canary_config(_write_config(tmp_path, "aegis_canary:\n  enabled: yes\n"))

    assert client.calls == 0


def test_disabled_path_preserves_baseline_and_makes_zero_aegis_calls() -> None:
    candidate = _candidate()
    claim = _claim()
    baseline = summarize_candidate_readiness(candidate | {"candidate_claims": [claim]})
    client = RecordingClient(_recommendation())

    with_canary = summarize_candidate_readiness(
        candidate | {"candidate_claims": [claim]},
        aegis_config=AegisCanaryConfig(enabled=False),
        aegis_client=client,
    )

    assert client.calls == 0
    assert "aegis_canary" not in baseline["claims"][0]
    assert with_canary["claims"][0]["readiness"] == baseline["claims"][0]["readiness"]
    assert with_canary["claims"][0]["aegis_canary"]["recommendation"] == "recommend_hold"
    assert with_canary["claims"][0]["aegis_canary"]["reason"] == "aegis_canary_disabled"


def test_mapping_preserves_provenance_and_deterministic_fingerprint() -> None:
    candidate = _candidate()
    claim = _claim()
    mapped = candidate_from_dict(candidate, claim)
    evidence, sources = evidence_from_dicts(candidate, claim)

    assert mapped.claim_id == "cand_claim_aegis_001"
    assert "research/intake/synthetic_source_review.md" in mapped.provenance_refs
    assert {item.relationship for item in evidence} == {"supports", "attacks"}
    assert all(item.provenance_location for item in evidence)

    first = request_fingerprint(mapped, list(reversed(evidence)), list(reversed(sources)))
    second = request_fingerprint(mapped, evidence, sources)
    assert first == second
    request = normalised_aegis_request(mapped, list(reversed(evidence)), list(reversed(sources)), fingerprint=first)
    request_again = normalised_aegis_request(mapped, evidence, sources, fingerprint=second)
    assert json.dumps(request, sort_keys=True) == json.dumps(request_again, sort_keys=True)


def test_fingerprint_payload_includes_material_fields() -> None:
    candidate = candidate_from_dict(_candidate(), _claim())
    evidence, sources = evidence_from_dicts(_candidate(), _claim())
    payload = fingerprint_payload(candidate, evidence, sources)

    assert payload["adapter_version"] == ADAPTER_VERSION
    assert payload["aegis_schema_version"] == AEGIS_SCHEMA_VERSION
    assert payload["mapping_version"] == aegis_canary.MAPPING_VERSION
    assert payload["canonicalization_version"] == aegis_canary.CANONICALIZATION_VERSION
    assert payload["claim"]["content_hash"]
    assert payload["evidence"][0]["content_hash"]
    assert {"authority", "quality", "freshness", "relationship", "provenance", "source_title"} <= set(
        payload["evidence"][0]
    )


def _fingerprint_with_change(**updates) -> str:
    candidate = candidate_from_dict(_candidate(), _claim())
    evidence, sources = evidence_from_dicts(_candidate(), _claim())
    if "claim_text" in updates:
        candidate = type(candidate)(**{**candidate.__dict__, "claim_text": updates["claim_text"]})
        updates = {key: value for key, value in updates.items() if key != "claim_text"}
    if "claim_created_at" in updates:
        candidate = type(candidate)(**{**candidate.__dict__, "created_at": updates["claim_created_at"]})
        updates = {key: value for key, value in updates.items() if key != "claim_created_at"}
    if "adapter_version" in updates:
        original = aegis_canary.ADAPTER_VERSION
        aegis_canary.ADAPTER_VERSION = updates["adapter_version"]
        try:
            return request_fingerprint(candidate, evidence, sources)
        finally:
            aegis_canary.ADAPTER_VERSION = original
    if "mapping_version" in updates:
        original = aegis_canary.MAPPING_VERSION
        aegis_canary.MAPPING_VERSION = updates["mapping_version"]
        try:
            return request_fingerprint(candidate, evidence, sources)
        finally:
            aegis_canary.MAPPING_VERSION = original
    if "aegis_schema_version" in updates:
        original = aegis_canary.AEGIS_SCHEMA_VERSION
        aegis_canary.AEGIS_SCHEMA_VERSION = updates["aegis_schema_version"]
        try:
            return request_fingerprint(candidate, evidence, sources)
        finally:
            aegis_canary.AEGIS_SCHEMA_VERSION = original
    if updates:
        first = evidence[0]
        evidence[0] = type(first)(**{**first.__dict__, **updates})
    return request_fingerprint(candidate, evidence, sources)


@pytest.mark.parametrize(
    "updates",
    [
        {"excerpt": "new contradictory meaning"},
        {"authority_score": 0.1},
        {"quality_score": 0.1},
        {"evidence_tier": "III"},
        {"freshness_timestamp": "2026-07-17"},
        {"relationship": "attacks"},
        {"provenance_location": "research/intake/changed.md"},
        {"source_id": "changed-source"},
        {"claim_text": "Materially changed claim text"},
        {"evidence_version": "version-2"},
        {"claim_created_at": "2026-07-17"},
        {"adapter_version": "black-albion-aegis-canary.v2"},
        {"mapping_version": "black-albion-aegis-mapping.v2"},
        {"aegis_schema_version": "aegis.v2"},
    ],
)
def test_material_fingerprint_changes(updates: dict) -> None:
    baseline = _fingerprint_with_change()

    assert _fingerprint_with_change(**updates) != baseline


def test_source_title_change_invalidates_fingerprint() -> None:
    candidate = candidate_from_dict(_candidate(), _claim())
    evidence, sources = evidence_from_dicts(_candidate(), _claim())
    baseline = request_fingerprint(candidate, evidence, sources)
    sources[0] = type(sources[0])(**{**sources[0].__dict__, "title": "Changed source title"})

    assert request_fingerprint(candidate, evidence, sources) != baseline


def test_fingerprint_stability_for_equivalent_snapshots() -> None:
    candidate = candidate_from_dict(_candidate(), _claim())
    evidence, sources = evidence_from_dicts(_candidate(), _claim())
    baseline = request_fingerprint(candidate, evidence, sources)
    whitespace_candidate = type(candidate)(
        **{**candidate.__dict__, "claim_text": "Synthetic   Black Albion canary claim has bounded support and opposition."}
    )
    unicode_candidate = type(candidate)(**{**candidate.__dict__, "claim_text": "Cafe\u0301"})
    unicode_candidate_nfc = type(candidate)(**{**candidate.__dict__, "claim_text": "Café"})

    assert request_fingerprint(candidate, list(reversed(evidence)), list(reversed(sources))) == baseline
    assert request_fingerprint(whitespace_candidate, evidence, sources) == baseline
    assert request_fingerprint(unicode_candidate, evidence, sources) == request_fingerprint(
        unicode_candidate_nfc, evidence, sources
    )


def test_mapping_handles_source_quality_cases_and_missing_provenance_holds() -> None:
    candidate = _candidate()
    claim = _claim()
    claim["tier_candidate"] = "III"
    evidence, sources = evidence_from_dicts(candidate, claim)
    assert all(item.authority_score == 0.35 for item in evidence)
    assert all(source.authority_score == 0.35 for source in sources)

    no_provenance = {"candidate_id": "missing", "candidate_claims": [claim]}
    client = RecordingClient(_recommendation())
    result = review_candidate_claim(
        no_provenance,
        claim,
        config=AegisCanaryConfig(enabled=True),
        client=client,
    )
    assert result.recommendation == "recommend_hold"
    assert result.reason == "missing_provenance"
    assert client.calls == 0


def test_aegis_decision_maps_to_recommendations_and_safe_hold_cases() -> None:
    config = AegisCanaryConfig(enabled=True)
    for conclusion, expected in {
        "Accepted": "recommend_promote",
        "Rejected": "recommend_reject",
        "Undecided": "recommend_hold",
        "Surprising": "recommend_hold",
    }.items():
        result = recommendation_from_aegis_decision(
            {
                "conclusion": conclusion,
                "decision_id": "decision-001",
                "audit_reference": "audit-001",
                "support_score": 0.5,
                "attack_score": 0.2,
                "confidence": 0.6,
                "supporting_evidence": [{"source_ids": ["source:support"]}],
                "opposing_evidence": [{"source_ids": ["source:attack"]}],
            },
            "fingerprint",
            config,
        )
        assert result.recommendation == expected

    with pytest.raises(AegisClientError, match="decision_id"):
        recommendation_from_aegis_decision({"conclusion": "Accepted", "audit_reference": "audit"}, "fp", config)
    with pytest.raises(AegisClientError, match="audit_reference"):
        recommendation_from_aegis_decision({"conclusion": "Accepted", "decision_id": "decision"}, "fp", config)


def test_unavailable_timeout_malformed_and_unknown_results_hold() -> None:
    candidate = _candidate()
    claim = _claim()
    config = AegisCanaryConfig(enabled=True)
    for exc in (AegisClientError("bad"), TimeoutError("timeout"), ValueError("malformed")):
        result = review_candidate_claim(candidate, claim, config=config, client=RecordingClient(exc=exc))
        assert result.recommendation == "recommend_hold"
        assert result.reason == "aegis_unavailable"

    result = review_candidate_claim(
        candidate,
        claim,
        config=config,
        client=RecordingClient(_recommendation("unexpected")),
    )
    assert result.recommendation == "recommend_hold"
    assert result.reason == "unknown_recommendation"


def test_recommendation_is_attached_without_promotion_or_tier_mutation() -> None:
    candidate = _candidate()
    claim = _claim()
    mapped = candidate_from_dict(candidate, claim)
    evidence, sources = evidence_from_dicts(candidate, claim)
    fp = request_fingerprint(mapped, evidence, sources)
    client = RecordingClient(_recommendation("recommend_promote", fp))

    summary = summarize_candidate_readiness(
        candidate | {"candidate_claims": [claim]},
        aegis_config=AegisCanaryConfig(enabled=True),
        aegis_client=client,
    )

    row = summary["claims"][0]
    assert client.calls == 1
    assert row["aegis_canary"]["recommendation"] == "recommend_promote"
    assert row["promotion_commit_allowed"] is False
    assert row["operator_approval_required"] is True
    assert claim["tier_candidate"] == "I"
    assert candidate["promotion_commit_allowed"] is False
    assert candidate["canonical_ingestion_allowed"] is False


def test_history_is_idempotent_and_changed_evidence_creates_new_record() -> None:
    first = _recommendation("recommend_hold", "fingerprint-a")
    second_same = _recommendation("recommend_reject", "fingerprint-a")
    third_changed = _recommendation("recommend_reject", "fingerprint-b")

    history = append_recommendation_history([], first)
    assert append_recommendation_history(history, second_same) == history
    updated = append_recommendation_history(history, third_changed)
    assert len(updated) == 2
    assert history[0]["recommendation"] == "recommend_hold"
    assert updated[1]["request_fingerprint"] == "fingerprint-b"


def test_material_change_prevents_stale_history_reuse() -> None:
    candidate = candidate_from_dict(_candidate(), _claim())
    evidence, sources = evidence_from_dicts(_candidate(), _claim())
    original = request_fingerprint(candidate, evidence, sources)
    changed = list(evidence)
    changed[0] = type(changed[0])(**{**changed[0].__dict__, "excerpt": "new contradictory meaning"})
    changed_fingerprint = request_fingerprint(candidate, changed, sources)

    history = append_recommendation_history([], _recommendation("recommend_hold", original))
    updated = append_recommendation_history(history, _recommendation("recommend_reject", changed_fingerprint))

    assert changed_fingerprint != original
    assert len(updated) == 2
    assert updated[0]["request_fingerprint"] == original
    assert updated[1]["request_fingerprint"] == changed_fingerprint


def test_security_limits_and_inert_claim_text() -> None:
    candidate = _candidate()
    claim = _claim()
    claim["claim_text"] = "$(rm -rf /) <script>alert(1)</script>"
    claim["attached_source_names"] = ["A" * 2000]
    evidence, sources = evidence_from_dicts(candidate, claim, excerpt_limit=120)
    mapped = candidate_from_dict(candidate, claim)
    request = normalised_aegis_request(mapped, evidence, sources)

    assert request["claim"]["statement"] == "$(rm -rf /) <script>alert(1)</script>"
    assert any(len(item["statement"]) == 120 for item in request["evidence"])
    assert "headers" not in json.dumps(request).lower()
    assert any(source.title.startswith("A") for source in sources)


def test_deterministic_mapping_runs_25_times_with_shuffled_inputs() -> None:
    candidate = _candidate()
    claim = _claim()
    hashes = set()
    for index in range(25):
        evidence, sources = evidence_from_dicts(candidate, claim)
        if index % 2:
            evidence = list(reversed(evidence))
            sources = list(reversed(sources))
        mapped = candidate_from_dict(candidate, claim)
        fingerprint = request_fingerprint(mapped, evidence, sources)
        payload = normalised_aegis_request(mapped, evidence, sources, fingerprint=fingerprint)
        hashes.add(json.dumps(payload, sort_keys=True))
    assert len(hashes) == 1


def test_synthetic_canary_fixture_proves_recommendation_not_promotion() -> None:
    candidate = _candidate()
    claim = _claim()
    mapped = candidate_from_dict(candidate, claim)
    evidence, sources = evidence_from_dicts(candidate, claim)
    fp = request_fingerprint(mapped, evidence, sources)
    client = RecordingClient(
        AegisRecommendation(
            recommendation="recommend_hold",
            request_fingerprint=fp,
            machine_status="Undecided",
            aegis_decision_id="decision-synthetic",
            support_score=0.64,
            attack_score=0.52,
            confidence=0.41,
            supporting_source_ids=("ba-source-support",),
            opposing_source_ids=("ba-source-attack",),
            unresolved_conflicts=("credible opposing source remains",),
            audit_reference="audit-synthetic",
            aegis_schema_version=AEGIS_SCHEMA_VERSION,
            adapter_version=ADAPTER_VERSION,
            reason="support and attack remain close",
        )
    )

    summary = summarize_candidate_readiness(
        candidate | {"candidate_claims": [claim]},
        aegis_config=AegisCanaryConfig(enabled=True),
        aegis_client=client,
    )

    recommendation = summary["claims"][0]["aegis_canary"]
    assert recommendation["recommendation"] == "recommend_hold"
    assert recommendation["unresolved_conflicts"] == ("credible opposing source remains",)
    assert summary["claims"][0]["operator_approval_required"] is True
    assert summary["canonical_promotion_locked"] is True
    assert summary["promotion_commit_allowed"] is False
