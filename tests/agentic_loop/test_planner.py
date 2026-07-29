from backend.app.agentic_loop.models import Gap, Subquestion
from backend.app.agentic_loop.planner import (
    QueryRepetitionTracker,
    StaticPlanner,
    normalise_query_text,
    query_hash,
)


def test_decompose_default_single_subquestion():
    planner = StaticPlanner()
    subquestions = planner.decompose("Where is Tewkesbury Abbey?")
    assert len(subquestions) == 1
    assert subquestions[0].text == "Where is Tewkesbury Abbey?"


def test_decompose_uses_supplied_subquestions():
    fixed = [Subquestion(subquestion_id="sq-1", text="first"), Subquestion(subquestion_id="sq-2", text="second")]
    planner = StaticPlanner(subquestions=fixed)
    assert planner.decompose("ignored") == fixed


def test_first_iteration_queries_one_per_subquestion():
    fixed = [Subquestion(subquestion_id="sq-1", text="first"), Subquestion(subquestion_id="sq-2", text="second")]
    planner = StaticPlanner(subquestions=fixed)
    planner.decompose("ignored")
    queries = planner.next_queries(1, fixed, [], set())
    assert len(queries) == 2
    assert {q.parent_subquestion_ids[0] for q in queries} == {"sq-1", "sq-2"}


def test_refinement_iteration_targets_open_gaps():
    fixed = [Subquestion(subquestion_id="sq-1", text="first")]
    planner = StaticPlanner(subquestions=fixed)
    gaps = [
        Gap(gap_id="g1", subquestion_id="sq-1", description="need more sources", status="open"),
        Gap(gap_id="g2", subquestion_id="sq-1", description="addressed already", status="addressed"),
    ]
    queries = planner.next_queries(2, fixed, gaps, set())
    assert len(queries) == 1
    assert queries[0].text == "need more sources"
    assert queries[0].strategy == "refinement"


def test_refinement_stops_when_strategy_exhausted():
    fixed = [Subquestion(subquestion_id="sq-1", text="first")]
    planner = StaticPlanner(subquestions=fixed)
    gaps = [Gap(gap_id="g1", subquestion_id="sq-1", description="need more", status="open")]
    queries = planner.next_queries(2, fixed, gaps, {"refinement"})
    assert queries == []


# ---------------------------------------------------------------------------
# Normalisation + repetition
# ---------------------------------------------------------------------------


def test_normalisation_casing():
    assert normalise_query_text("Tewkesbury Abbey") == normalise_query_text("tewkesbury abbey")


def test_normalisation_punctuation():
    assert normalise_query_text("Tewkesbury, Abbey!") == normalise_query_text("Tewkesbury Abbey")


def test_normalisation_whitespace():
    assert normalise_query_text("Tewkesbury   Abbey\t\n") == normalise_query_text("Tewkesbury Abbey")


def test_normalisation_distinct_queries_differ():
    assert normalise_query_text("Tewkesbury Abbey") != normalise_query_text("Severn Ham")


def test_query_hash_stable_for_equivalent_text():
    assert query_hash("Tewkesbury, Abbey!") == query_hash("tewkesbury abbey")


def test_repetition_tracker_exact_repeat():
    tracker = QueryRepetitionTracker()
    assert tracker.register("Tewkesbury Abbey") is False
    assert tracker.register("Tewkesbury Abbey") is True


def test_repetition_tracker_casing_repeat():
    tracker = QueryRepetitionTracker()
    tracker.register("Tewkesbury Abbey")
    assert tracker.is_repeat("TEWKESBURY ABBEY") is True


def test_repetition_tracker_punctuation_repeat():
    tracker = QueryRepetitionTracker()
    tracker.register("Tewkesbury Abbey")
    assert tracker.is_repeat("Tewkesbury, Abbey!") is True


def test_repetition_tracker_whitespace_repeat():
    tracker = QueryRepetitionTracker()
    tracker.register("Tewkesbury Abbey")
    assert tracker.is_repeat("Tewkesbury    Abbey") is True


def test_repetition_tracker_genuinely_different_query():
    tracker = QueryRepetitionTracker()
    tracker.register("Tewkesbury Abbey")
    assert tracker.is_repeat("Severn Ham floodplain") is False
