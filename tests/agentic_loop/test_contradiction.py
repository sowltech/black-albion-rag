import pytest

from backend.app.agentic_loop.contradiction import (
    classify_materiality,
    create_contradiction,
    detect_from_evidence,
    escalate,
    has_unresolved_material_contradiction,
    open_contradiction_ids,
    resolve_fully,
    resolve_partially,
)
from backend.app.agentic_loop.errors import InvalidRequestError
from backend.app.agentic_loop.models import EvidenceItem


def _evidence(evidence_id, tier, supports=None, opposes=None):
    return EvidenceItem(
        evidence_id=evidence_id,
        content="content",
        source_id=f"src-{evidence_id}",
        source_type="archival",
        source_reference="ref",
        tier=tier,
        retrieval_query_id="q-1",
        relevance=0.7,
        authority=0.7,
        freshness=0.7,
        consistency=0.7,
        completeness=0.7,
        provenance_quality=0.7,
        overall_score=0.7,
        supports_claims=supports or [],
        opposes_claims=opposes or [],
        content_hash=f"hash-{evidence_id}",
    )


def test_materiality_high_when_both_sides_tier_i():
    supporting = [_evidence("ev-1", "I")]
    opposing = [_evidence("ev-2", "I")]
    assert classify_materiality(supporting, opposing) == "high"


def test_materiality_low_when_both_sides_tier_iii():
    supporting = [_evidence("ev-1", "III")]
    opposing = [_evidence("ev-2", "III")]
    assert classify_materiality(supporting, opposing) == "low"


def test_materiality_medium_mixed_tiers():
    supporting = [_evidence("ev-1", "II")]
    opposing = [_evidence("ev-2", "III")]
    assert classify_materiality(supporting, opposing) == "medium"


def test_create_contradiction_requires_both_sides():
    with pytest.raises(InvalidRequestError):
        create_contradiction("c-1", "claim", [], [_evidence("ev-2", "I")])


def test_create_contradiction_status_open():
    c = create_contradiction("c-1", "claim", [_evidence("ev-1", "I")], [_evidence("ev-2", "I")])
    assert c.status == "open"
    assert c.materiality == "high"


def test_resolve_partially_requires_reason():
    c = create_contradiction("c-1", "claim", [_evidence("ev-1", "I")], [_evidence("ev-2", "I")])
    with pytest.raises(InvalidRequestError):
        resolve_partially(c, ["ev-1"], "")


def test_resolve_partially_rejects_unknown_evidence():
    c = create_contradiction("c-1", "claim", [_evidence("ev-1", "I")], [_evidence("ev-2", "I")])
    with pytest.raises(InvalidRequestError):
        resolve_partially(c, ["ev-not-part-of-this"], "found a newer survey")


def test_resolve_partially_updates_status():
    c = create_contradiction("c-1", "claim", [_evidence("ev-1", "I")], [_evidence("ev-2", "I")])
    resolved = resolve_partially(c, ["ev-1"], "one source corroborated independently")
    assert resolved.status == "partially_resolved"
    assert resolved.resolution_reason == "one source corroborated independently"


def test_resolve_fully_updates_status():
    c = create_contradiction("c-1", "claim", [_evidence("ev-1", "I")], [_evidence("ev-2", "I")])
    resolved = resolve_fully(c, ["ev-1", "ev-2"], "archival re-survey superseded ev-2")
    assert resolved.status == "resolved"


def test_escalate_updates_status():
    c = create_contradiction("c-1", "claim", [_evidence("ev-1", "I")], [_evidence("ev-2", "I")])
    escalated = escalate(c, "requires operator judgement call")
    assert escalated.status == "operator_review_required"


def test_has_unresolved_material_contradiction_true_when_open_and_high():
    c = create_contradiction("c-1", "claim", [_evidence("ev-1", "I")], [_evidence("ev-2", "I")])
    assert has_unresolved_material_contradiction([c]) is True


def test_has_unresolved_material_contradiction_false_once_resolved():
    c = create_contradiction("c-1", "claim", [_evidence("ev-1", "I")], [_evidence("ev-2", "I")])
    resolved = resolve_fully(c, ["ev-1", "ev-2"], "reason")
    assert has_unresolved_material_contradiction([resolved]) is False


def test_open_contradiction_ids_excludes_resolved():
    open_c = create_contradiction("c-1", "claim a", [_evidence("ev-1", "I")], [_evidence("ev-2", "I")])
    resolved_c = resolve_fully(
        create_contradiction("c-2", "claim b", [_evidence("ev-3", "I")], [_evidence("ev-4", "I")]),
        ["ev-3", "ev-4"],
        "reason",
    )
    assert open_contradiction_ids([open_c, resolved_c]) == ["c-1"]


def test_detect_from_evidence_pairs_supporting_and_opposing():
    supporting = _evidence("ev-1", "I", supports=["claim-x"])
    opposing = _evidence("ev-2", "I", opposes=["claim-x"])
    detected = detect_from_evidence([supporting, opposing])
    assert len(detected) == 1
    assert detected[0].claim_or_question == "claim-x"
    assert detected[0].supporting_evidence_ids == ["ev-1"]
    assert detected[0].opposing_evidence_ids == ["ev-2"]


def test_detect_from_evidence_no_pairing_without_opposition():
    supporting = _evidence("ev-1", "I", supports=["claim-x"])
    assert detect_from_evidence([supporting]) == []
