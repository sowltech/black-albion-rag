from backend.app.agentic_loop.governor import GovernorInputs, compute_information_gain, decide
from backend.app.agentic_loop.models import GovernorAction


def _inputs(**overrides):
    base = dict(
        iteration=1,
        max_iterations=5,
        retrieval_calls_used=1,
        max_retrieval_calls=10,
        evidence_items_used=1,
        max_evidence_items=50,
        confidence=0.5,
        coverage=0.5,
        minimum_confidence=0.8,
        latest_gain=0.5,
        minimum_evidence_gain=0.1,
        consecutive_no_gain=0,
        stop_after_consecutive_no_gain=2,
        repeated_query_detected=False,
        stop_on_repeated_query=True,
        has_unresolved_material_contradiction=False,
        has_addressable_gap=True,
        policy_blocked=False,
        policy_block_reason=None,
    )
    base.update(overrides)
    return GovernorInputs(**base)


def test_success_threshold_reached():
    decision = decide(_inputs(confidence=0.9, coverage=1.0, minimum_confidence=0.8))
    assert decision.action == GovernorAction.SYNTHESISE
    assert decision.reason_code == "SUCCESS_THRESHOLD_REACHED"


def test_max_iterations_reached():
    decision = decide(_inputs(iteration=5, max_iterations=5))
    assert decision.reason_code == "MAX_ITERATIONS_REACHED"
    assert decision.action == GovernorAction.SYNTHESISE


def test_retrieval_budget_exhausted():
    decision = decide(_inputs(retrieval_calls_used=10, max_retrieval_calls=10))
    assert decision.reason_code == "RETRIEVAL_CALL_BUDGET_EXHAUSTED"


def test_evidence_budget_exhausted():
    decision = decide(_inputs(evidence_items_used=50, max_evidence_items=50))
    assert decision.reason_code == "EVIDENCE_ITEM_BUDGET_EXHAUSTED"


def test_repeated_query_stops():
    decision = decide(_inputs(repeated_query_detected=True, stop_on_repeated_query=True))
    assert decision.action == GovernorAction.STOP
    assert decision.reason_code == "REPEATED_QUERY"


def test_repeated_query_ignored_when_policy_allows():
    decision = decide(_inputs(repeated_query_detected=True, stop_on_repeated_query=False))
    assert decision.reason_code != "REPEATED_QUERY"


def test_one_no_gain_iteration_below_configured_threshold_continues():
    decision = decide(_inputs(consecutive_no_gain=1, stop_after_consecutive_no_gain=2))
    assert decision.action == GovernorAction.CONTINUE


def test_configured_consecutive_no_gain_stops():
    decision = decide(_inputs(consecutive_no_gain=2, stop_after_consecutive_no_gain=2))
    assert decision.reason_code == "NO_INFORMATION_GAIN"


def test_unresolved_contradiction_escalates_when_no_gap_left():
    decision = decide(
        _inputs(has_unresolved_material_contradiction=True, has_addressable_gap=False)
    )
    assert decision.action == GovernorAction.ESCALATE
    assert decision.reason_code == "CONTRADICTION_REQUIRES_OPERATOR_REVIEW"


def test_unresolved_contradiction_does_not_escalate_while_gap_addressable():
    decision = decide(
        _inputs(has_unresolved_material_contradiction=True, has_addressable_gap=True, coverage=0.2)
    )
    assert decision.action != GovernorAction.ESCALATE


def test_success_blocked_by_material_contradiction():
    decision = decide(
        _inputs(
            confidence=0.9,
            coverage=1.0,
            minimum_confidence=0.8,
            has_unresolved_material_contradiction=True,
            has_addressable_gap=True,
        )
    )
    assert decision.reason_code == "CONTRADICTION_BLOCKS_ANSWER"


def test_policy_block_takes_priority_over_everything():
    decision = decide(
        _inputs(
            policy_blocked=True,
            policy_block_reason="proof mode requires tier I",
            confidence=1.0,
            coverage=1.0,
        )
    )
    assert decision.action == GovernorAction.STOP
    assert decision.reason_code == "POLICY_BLOCKED"


def test_no_strategy_remaining_stops():
    decision = decide(_inputs(has_addressable_gap=False, coverage=0.3))
    assert decision.reason_code == "NO_ADDRESSABLE_GAP_REMAINS"


def test_continue_when_budgets_and_gaps_remain():
    decision = decide(_inputs(coverage=0.3, confidence=0.3))
    assert decision.action == GovernorAction.CONTINUE
    assert decision.reason_code == "CONTINUE_ITERATING"


# ---------------------------------------------------------------------------
# Information gain
# ---------------------------------------------------------------------------


def _gain(**overrides):
    base = dict(
        coverage_before=0.0,
        coverage_after=0.0,
        confidence_before=0.0,
        confidence_after=0.0,
        new_evidence_count=0,
        duplicate_evidence_count=0,
        contradictions_resolved=0,
        source_diversity_before=0.0,
        source_diversity_after=0.0,
        repeated_query_detected=False,
    )
    base.update(overrides)
    return compute_information_gain(**base)


def test_gain_strong_improvement():
    strong = _gain(
        coverage_before=0.2,
        coverage_after=0.8,
        confidence_before=0.2,
        confidence_after=0.6,
        new_evidence_count=4,
        source_diversity_before=0.2,
        source_diversity_after=0.6,
    )
    assert strong > 0.3


def test_gain_marginal_improvement_is_smaller_than_strong():
    marginal = _gain(coverage_before=0.5, coverage_after=0.55, new_evidence_count=1)
    strong = _gain(
        coverage_before=0.2,
        coverage_after=0.8,
        confidence_before=0.2,
        confidence_after=0.6,
        new_evidence_count=4,
        source_diversity_before=0.2,
        source_diversity_after=0.6,
    )
    assert 0 < marginal < strong


def test_gain_zero_when_nothing_changes():
    assert _gain() == 0.0


def test_gain_duplicate_only_retrieval_is_zero():
    assert _gain(duplicate_evidence_count=5) == 0.0


def test_gain_negative_confidence_movement_bounded_nonnegative():
    result = _gain(confidence_before=0.8, confidence_after=0.3)
    assert result >= 0.0


def test_gain_contradiction_resolution_contributes():
    with_resolution = _gain(contradictions_resolved=1)
    without_resolution = _gain(contradictions_resolved=0)
    assert with_resolution > without_resolution


def test_gain_new_source_diversity_contributes():
    with_diversity = _gain(source_diversity_before=0.2, source_diversity_after=0.9)
    without_diversity = _gain(source_diversity_before=0.2, source_diversity_after=0.2)
    assert with_diversity > without_diversity


def test_gain_output_bounded_unit_interval():
    extreme = _gain(
        coverage_before=0.0,
        coverage_after=1.0,
        confidence_before=0.0,
        confidence_after=1.0,
        new_evidence_count=100,
        contradictions_resolved=10,
        source_diversity_before=0.0,
        source_diversity_after=1.0,
    )
    assert 0.0 <= extreme <= 1.0


def test_gain_repeated_query_penalised():
    penalised = _gain(coverage_before=0.1, coverage_after=0.2, repeated_query_detected=True)
    not_penalised = _gain(coverage_before=0.1, coverage_after=0.2, repeated_query_detected=False)
    assert penalised <= not_penalised
