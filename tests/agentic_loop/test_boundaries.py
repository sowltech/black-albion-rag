"""Boundary-enforcement tests for the agentic loop service.

Covers the three review findings on PR #3:

1. Policy-blocked requests must stop before any planner or retriever call.
2. ``include_tiers`` must be enforced at the service boundary, not merely
   validated on the request model.
3. Internal exception detail must never leak through the public
   ``stop_reason``.
"""
import pytest

from backend.app.agentic_loop.models import (
    AgenticQueryRequest,
    RetrievalQuery,
    Subquestion,
    TerminalOutcome,
)
from backend.app.agentic_loop.planner import StaticPlanner, query_hash
from backend.app.agentic_loop.receipts import GENESIS_HASH
from backend.app.agentic_loop.retriever import EvidenceRecord, InMemoryRetriever
from backend.app.agentic_loop.service import AgenticLoopService


def _fixed_clock():
    return "2026-07-28T00:00:00Z"


def _record(record_id, content, tier, source_id="src", supports=None, opposes=None):
    return EvidenceRecord(
        record_id=record_id,
        content=content,
        source_id=source_id,
        source_type="archival",
        source_reference=f"ref-{record_id}",
        tier=tier,
        authority=0.9,
        freshness=0.9,
        consistency=0.9,
        completeness=0.9,
        provenance_quality=0.9,
        supports_claims=supports or [],
        opposes_claims=opposes or [],
    )


class CountingPlanner:
    """StaticPlanner wrapper that counts every call it receives."""

    def __init__(self, inner=None):
        self._inner = inner or StaticPlanner()
        self.decompose_calls = 0
        self.next_queries_calls = 0

    def decompose(self, question):
        self.decompose_calls += 1
        return self._inner.decompose(question)

    def next_queries(self, iteration, subquestions, open_gaps, exhausted_strategies):
        self.next_queries_calls += 1
        return self._inner.next_queries(iteration, subquestions, open_gaps, exhausted_strategies)


class CountingRetriever:
    """InMemoryRetriever wrapper that counts every retrieve() call."""

    def __init__(self, records):
        self._inner = InMemoryRetriever(records)
        self.retrieve_calls = 0

    def retrieve(self, query):
        self.retrieve_calls += 1
        return self._inner.retrieve(query)

    def available_source_types(self):
        return self._inner.available_source_types()


class ExplodingRetriever:
    """Raises an unexpected exception whose text simulates leaked secrets."""

    SECRET_MESSAGE = (
        "database password=supersecret token=abc123 at /Users/operator/private/creds.env"
    )

    def retrieve(self, query):
        raise RuntimeError(self.SECRET_MESSAGE)

    def available_source_types(self):
        return set()


# ---------------------------------------------------------------------------
# Finding 1: policy gate fires before planner and retriever
# ---------------------------------------------------------------------------


def _policy_blocked_run():
    planner = CountingPlanner()
    retriever = CountingRetriever([_record("r1", "tier one archival record", "I")])
    service = AgenticLoopService(planner, retriever, clock=_fixed_clock)
    request = AgenticQueryRequest(
        question="proof mode without tier one", mode="proof", include_tiers=["II", "III"]
    )
    return service.run(request, run_id="run-policy-gate"), planner, retriever


def test_policy_block_returns_policy_blocked_outcome():
    result, _, _ = _policy_blocked_run()
    assert result.outcome == TerminalOutcome.POLICY_BLOCKED


def test_policy_block_makes_zero_planner_calls():
    _, planner, _ = _policy_blocked_run()
    assert planner.decompose_calls == 0
    assert planner.next_queries_calls == 0


def test_policy_block_makes_zero_retriever_calls():
    _, _, retriever = _policy_blocked_run()
    assert retriever.retrieve_calls == 0


def test_policy_block_result_carries_no_evidence_and_no_iterations():
    result, _, _ = _policy_blocked_run()
    assert result.evidence_ids == []
    assert result.supported_claims == []
    assert result.unsupported_claims == []
    assert result.iterations_completed == 0
    assert result.retrieval_calls_used == 0
    assert result.operator_review_required is False


def test_policy_block_leaves_receipt_chain_at_genesis():
    # No retrieval cycle completed, so no iteration receipt exists to carry
    # evidence -- the chain head is exactly the genesis value.
    result, _, _ = _policy_blocked_run()
    assert result.receipt_chain_head == GENESIS_HASH


def test_policy_block_stop_reason_is_deterministic():
    first, _, _ = _policy_blocked_run()
    second, _, _ = _policy_blocked_run()
    assert first.stop_reason == second.stop_reason
    assert first.stop_reason.startswith("POLICY_BLOCKED:")


def test_policy_block_overrides_any_success_condition():
    # Even with trivially satisfiable thresholds and rich matching evidence,
    # the policy gate must win.
    planner = CountingPlanner()
    retriever = CountingRetriever([_record("r1", "proof mode without tier one", "II")])
    service = AgenticLoopService(planner, retriever, clock=_fixed_clock)
    request = AgenticQueryRequest(
        question="proof mode without tier one",
        mode="proof",
        include_tiers=["II", "III"],
        minimum_confidence=0.0,
    )
    result = service.run(request, run_id="run-policy-precedence")
    assert result.outcome == TerminalOutcome.POLICY_BLOCKED
    assert retriever.retrieve_calls == 0


# ---------------------------------------------------------------------------
# Finding 2: include_tiers enforcement at the service boundary
# ---------------------------------------------------------------------------

_MIXED_RECORDS = [
    _record("r1", "winchcombe minster charter record", "I", source_id="s1"),
    _record("r2", "winchcombe minster charter speculation", "III", source_id="s2"),
]


def _tier_i_only_run(records=None, **request_overrides):
    sq = Subquestion(subquestion_id="sq-1", text="winchcombe minster charter")
    planner = StaticPlanner(subquestions=[sq], initial_query_texts=["winchcombe minster charter"])
    retriever = InMemoryRetriever(records if records is not None else _MIXED_RECORDS)
    service = AgenticLoopService(planner, retriever, clock=_fixed_clock)
    request_kwargs = dict(
        question="winchcombe minster charter status", mode="fast", include_tiers=["I"]
    )
    request_kwargs.update(request_overrides)
    request = AgenticQueryRequest(**request_kwargs)
    return service.run(request, run_id="run-tier-filter")


def test_tier_iii_excluded_when_only_tier_i_requested():
    result = _tier_i_only_run()
    assert "ev-r1" in result.evidence_ids
    assert "ev-r2" not in result.evidence_ids


def test_mixed_retrieval_admits_only_allowed_tier():
    result = _tier_i_only_run()
    assert result.evidence_ids == ["ev-r1"]


def test_excluded_evidence_does_not_lower_confidence_or_coverage():
    mixed = _tier_i_only_run()
    clean = _tier_i_only_run(records=[_MIXED_RECORDS[0]])
    assert mixed.final_confidence == clean.final_confidence
    assert mixed.final_coverage == clean.final_coverage


def test_excluded_evidence_does_not_change_outcome_or_gain_path():
    # Identical runs except for the presence of out-of-scope Tier III
    # records must take the same governed path end to end.
    mixed = _tier_i_only_run()
    clean = _tier_i_only_run(records=[_MIXED_RECORDS[0]])
    assert mixed.outcome == clean.outcome
    assert mixed.stop_reason == clean.stop_reason
    assert mixed.iterations_completed == clean.iterations_completed


def test_excluded_evidence_does_not_consume_evidence_budget():
    # Budget of exactly 1: the single allowed Tier I item must fit, meaning
    # the excluded Tier III item consumed none of the budget.
    result = _tier_i_only_run(max_evidence_items=1)
    assert result.evidence_ids == ["ev-r1"]


def test_excluded_evidence_absent_from_receipt_chain_hash():
    # Same receipts => same chain head. If the Tier III item had entered
    # any receipt field, the chain heads would differ.
    mixed = _tier_i_only_run()
    clean = _tier_i_only_run(records=[_MIXED_RECORDS[0]])
    assert mixed.receipt_chain_head == clean.receipt_chain_head


def test_excluded_evidence_cannot_create_contradictions():
    records = [
        _record("r1", "winchcombe minster charter pro", "I", source_id="s1", supports=["claim-x"]),
        _record("r2", "winchcombe minster charter contra", "III", source_id="s2", opposes=["claim-x"]),
    ]
    result = _tier_i_only_run(records=records)
    assert result.contradictions == []


def test_excluded_evidence_absent_from_synthesis():
    result = _tier_i_only_run()
    assert "ev-r2" not in result.answer


def test_empty_allowed_evidence_after_filtering_terminates_correctly():
    # Only Tier III exists; the Tier I-only request must behave exactly as
    # if nothing was retrievable.
    result = _tier_i_only_run(records=[_MIXED_RECORDS[1]])
    assert result.evidence_ids == []
    assert result.outcome in (
        TerminalOutcome.NO_INFORMATION_GAIN,
        TerminalOutcome.INSUFFICIENT_EVIDENCE,
        TerminalOutcome.BUDGET_EXHAUSTED,
    )
    assert result.supported_claims == []


@pytest.mark.parametrize("mode", ["fast", "deep", "proof"])
def test_all_modes_respect_include_tiers(mode):
    result = _tier_i_only_run(mode=mode)
    assert result.evidence_ids == ["ev-r1"]


def test_tier_filtering_happens_before_dedup_and_scoring():
    # A Tier III item sharing content (same content hash) with an allowed
    # Tier I item from a different source: if filtering ran after dedup,
    # the Tier III copy could have been kept as the "unique" survivor or
    # counted as corroboration. It must simply never enter.
    records = [
        _record("r1", "winchcombe minster charter record", "I", source_id="s1"),
        _record("r2", "winchcombe minster charter record", "III", source_id="s2"),
    ]
    result = _tier_i_only_run(records=records)
    assert result.evidence_ids == ["ev-r1"]


# ---------------------------------------------------------------------------
# Finding 3: internal errors never leak detail through stop_reason
# ---------------------------------------------------------------------------


def _exploding_run():
    planner = StaticPlanner()
    service = AgenticLoopService(planner, ExplodingRetriever(), clock=_fixed_clock)
    request = AgenticQueryRequest(question="a question that will explode", mode="fast")
    return service.run(request, run_id="run-explode")


def test_unexpected_exception_maps_to_internal_error():
    result = _exploding_run()
    assert result.outcome == TerminalOutcome.INTERNAL_ERROR


def test_stop_reason_contains_no_exception_message():
    result = _exploding_run()
    assert ExplodingRetriever.SECRET_MESSAGE not in result.stop_reason
    assert "RuntimeError" not in result.stop_reason


def test_stop_reason_contains_no_credentials():
    result = _exploding_run()
    assert "supersecret" not in result.stop_reason
    assert "abc123" not in result.stop_reason
    assert "password" not in result.stop_reason
    assert "token" not in result.stop_reason


def test_stop_reason_contains_no_filesystem_paths():
    result = _exploding_run()
    assert "/Users/" not in result.stop_reason
    assert "creds.env" not in result.stop_reason


def test_internal_error_result_is_structurally_valid():
    result = _exploding_run()
    assert result.run_id == "run-explode"
    assert result.answer == ""
    assert result.evidence_ids == []
    assert result.iterations_completed == 0
    assert result.retrieval_calls_used == 0
    assert result.receipt_chain_head == GENESIS_HASH


def test_internal_error_presents_no_evidence_as_supported():
    result = _exploding_run()
    assert result.supported_claims == []
    assert result.unsupported_claims == []


def test_internal_error_classification_is_stable_across_runs():
    first = _exploding_run()
    second = _exploding_run()
    assert first.stop_reason == second.stop_reason
    assert first.stop_reason == "internal error [ERR_UNEXPECTED]"
