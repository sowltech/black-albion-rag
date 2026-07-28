from backend.app.agentic_loop.gap_detector import coverage_ratio, detect_gaps
from backend.app.agentic_loop.models import Contradiction, EvidenceItem, Gap, RetrievalQuery, Subquestion


def _evidence(evidence_id, source_id, tier="I", source_type="archival", **overrides):
    base = dict(
        evidence_id=evidence_id,
        content="content",
        source_id=source_id,
        source_type=source_type,
        source_reference="ref",
        tier=tier,
        retrieval_query_id="q-1",
        relevance=0.8,
        authority=0.8,
        freshness=0.8,
        consistency=0.8,
        completeness=0.8,
        provenance_quality=0.8,
        overall_score=0.8,
        content_hash=f"hash-{evidence_id}",
    )
    base.update(overrides)
    return EvidenceItem(**base)


def _query(query_id, subquestion_id):
    return RetrievalQuery(
        query_id=query_id,
        iteration=1,
        text="x",
        parent_subquestion_ids=[subquestion_id],
        normalised_hash="h",
    )


def test_no_evidence_creates_high_severity_gap():
    sq = Subquestion(subquestion_id="sq-1", text="unanswered question")
    gaps = detect_gaps([sq], [], [], [])
    assert len(gaps) == 1
    assert gaps[0].severity == "high"
    assert gaps[0].gap_id == "gap-sq-1-coverage"


def test_missing_required_evidence_type():
    sq = Subquestion(subquestion_id="sq-1", text="q", required_evidence_types=["geological"])
    ev = _evidence("ev-1", "src-1", source_type="archival")
    query = _query("q-1", "sq-1")
    gaps = detect_gaps([sq], [ev], [query], [])
    kinds = {g.gap_id for g in gaps}
    assert "gap-sq-1-evidence-type" in kinds


def test_low_source_diversity_gap():
    sq = Subquestion(subquestion_id="sq-1", text="q")
    ev1 = _evidence("ev-1", "src-1", content_hash="h1")
    ev2 = _evidence("ev-2", "src-1", content_hash="h2")
    query = _query("q-1", "sq-1")
    gaps = detect_gaps([sq], [ev1, ev2], [query], [])
    assert any(g.gap_id == "gap-sq-1-source-diversity" for g in gaps)


def test_weak_provenance_gap():
    sq = Subquestion(subquestion_id="sq-1", text="q")
    ev = _evidence("ev-1", "src-1", provenance_quality=0.1)
    query = _query("q-1", "sq-1")
    gaps = detect_gaps([sq], [ev], [query], [])
    assert any(g.gap_id == "gap-sq-1-provenance" for g in gaps)


def test_stale_evidence_gap():
    sq = Subquestion(subquestion_id="sq-1", text="q")
    ev = _evidence("ev-1", "src-1", freshness=0.05)
    query = _query("q-1", "sq-1")
    gaps = detect_gaps([sq], [ev], [query], [])
    assert any(g.gap_id == "gap-sq-1-freshness" for g in gaps)


def test_well_supported_subquestion_has_no_gap():
    sq = Subquestion(subquestion_id="sq-1", text="q")
    ev = _evidence("ev-1", "src-1")
    query = _query("q-1", "sq-1")
    gaps = detect_gaps([sq], [ev], [query], [])
    assert gaps == []


def test_unresolved_contradiction_creates_gap():
    contradiction = Contradiction(
        contradiction_id="c-1",
        claim_or_question="claim x",
        supporting_evidence_ids=["ev-1"],
        opposing_evidence_ids=["ev-2"],
        materiality="high",
        status="open",
    )
    gaps = detect_gaps([], [], [], [contradiction])
    assert len(gaps) == 1
    assert gaps[0].gap_id == "gap-contradiction-c-1"


def test_resolved_contradiction_creates_no_gap():
    contradiction = Contradiction(
        contradiction_id="c-1",
        claim_or_question="claim x",
        supporting_evidence_ids=["ev-1"],
        opposing_evidence_ids=["ev-2"],
        materiality="high",
        status="resolved",
    )
    gaps = detect_gaps([], [], [], [contradiction])
    assert gaps == []


def test_coverage_ratio_full_when_no_subquestions():
    assert coverage_ratio([], []) == 1.0


def test_coverage_ratio_half_when_one_of_two_blocked():
    sq1 = Subquestion(subquestion_id="sq-1", text="a")
    sq2 = Subquestion(subquestion_id="sq-2", text="b")
    gaps = [Gap(gap_id="g1", subquestion_id="sq-1", description="d", severity="high", status="open")]
    assert coverage_ratio([sq1, sq2], gaps) == 0.5


def test_coverage_ratio_ignores_low_severity_gaps():
    sq1 = Subquestion(subquestion_id="sq-1", text="a")
    gaps = [Gap(gap_id="g1", subquestion_id="sq-1", description="d", severity="low", status="open")]
    assert coverage_ratio([sq1], gaps) == 1.0
