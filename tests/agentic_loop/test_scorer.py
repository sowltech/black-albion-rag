from backend.app.agentic_loop.models import EvidenceItem
from backend.app.agentic_loop.policy import EVIDENCE_SCORE_WEIGHTS
from backend.app.agentic_loop.scorer import deduplicate, score_batch, score_evidence


def _item(**overrides):
    base = dict(
        evidence_id="ev-1",
        content="content",
        source_id="src-1",
        source_type="archival",
        source_reference="ref",
        tier="I",
        retrieval_query_id="q-1",
        relevance=0.5,
        authority=0.5,
        freshness=0.5,
        consistency=0.5,
        completeness=0.5,
        provenance_quality=0.5,
        overall_score=0.0,
        content_hash="hash-1",
    )
    base.update(overrides)
    return EvidenceItem(**base)


def test_score_evidence_uses_documented_weights():
    item = _item(relevance=1.0, authority=0.0, freshness=0.0, consistency=0.0, completeness=0.0, provenance_quality=0.0)
    scored = score_evidence(item)
    assert scored.overall_score == EVIDENCE_SCORE_WEIGHTS["relevance"]


def test_score_evidence_all_ones_gives_one():
    item = _item(relevance=1.0, authority=1.0, freshness=1.0, consistency=1.0, completeness=1.0, provenance_quality=1.0)
    scored = score_evidence(item)
    assert abs(scored.overall_score - 1.0) < 1e-9


def test_score_evidence_does_not_mutate_tier():
    item = _item(tier="III")
    scored = score_evidence(item)
    assert scored.tier == "III"


def test_score_batch_preserves_order_and_count():
    items = [_item(evidence_id=f"ev-{i}", content_hash=f"h{i}") for i in range(3)]
    scored = score_batch(items)
    assert [s.evidence_id for s in scored] == ["ev-0", "ev-1", "ev-2"]


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


def test_dedup_exact_duplicate_evidence_id():
    a = _item(evidence_id="ev-1", content_hash="h1")
    b = _item(evidence_id="ev-1", content_hash="h1")
    unique, duplicates = deduplicate([a, b])
    assert len(unique) == 1
    assert len(duplicates) == 1


def test_dedup_same_source_same_content_different_id():
    a = _item(evidence_id="ev-1", source_id="src-1", content_hash="h1")
    b = _item(evidence_id="ev-2", source_id="src-1", content_hash="h1")
    unique, duplicates = deduplicate([a, b])
    assert len(unique) == 1
    assert len(duplicates) == 1


def test_dedup_preserves_independent_corroboration():
    a = _item(evidence_id="ev-1", source_id="src-1", content_hash="h1")
    b = _item(evidence_id="ev-2", source_id="src-2", content_hash="h1")
    unique, duplicates = deduplicate([a, b])
    assert len(unique) == 2
    assert duplicates == []


def test_dedup_same_evidence_reached_via_different_queries():
    a = _item(evidence_id="ev-1", content_hash="h1", retrieval_query_id="q-1")
    b = _item(evidence_id="ev-1", content_hash="h1", retrieval_query_id="q-2")
    unique, duplicates = deduplicate([a, b])
    assert len(unique) == 1
    assert len(duplicates) == 1
