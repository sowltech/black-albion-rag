import pytest
from pydantic import ValidationError

from backend.app.agentic_loop.errors import InvalidTransitionError, TerminalStateError
from backend.app.agentic_loop.models import (
    AgenticQueryRequest,
    EvidenceItem,
    LoopState,
    TERMINAL_STATES,
    TRANSITIONS,
    validate_transition,
)


def test_valid_request_defaults():
    req = AgenticQueryRequest(question="What lies beneath Tewkesbury?")
    assert req.mode == "fast"
    assert req.include_tiers == ["I", "II", "III"]
    assert req.max_iterations is None


@pytest.mark.parametrize(
    "field,value",
    [
        ("max_iterations", 0),
        ("max_iterations", -1),
        ("max_retrieval_calls", 0),
        ("max_evidence_items", -5),
        ("stop_after_consecutive_no_gain", 0),
    ],
)
def test_invalid_budget_rejected(field, value):
    with pytest.raises(ValidationError):
        AgenticQueryRequest(question="valid question text", **{field: value})


@pytest.mark.parametrize("field,value", [("minimum_confidence", 1.5), ("minimum_evidence_gain", -0.1)])
def test_invalid_unit_interval_rejected(field, value):
    with pytest.raises(ValidationError):
        AgenticQueryRequest(question="valid question text", **{field: value})


def test_empty_tiers_rejected():
    with pytest.raises(ValidationError):
        AgenticQueryRequest(question="valid question text", include_tiers=[])


def test_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        AgenticQueryRequest(question="valid question text", not_a_real_field=True)


def test_evidence_scores_clamped():
    item = EvidenceItem(
        evidence_id="ev-1",
        content="x",
        source_id="s",
        source_type="archival",
        source_reference="ref",
        tier="I",
        retrieval_query_id="q-1",
        relevance=2.0,
        authority=-1.0,
        freshness=0.5,
        consistency=0.5,
        completeness=0.5,
        provenance_quality=0.5,
        overall_score=5.0,
        content_hash="hash",
    )
    assert item.relevance == 1.0
    assert item.authority == 0.0
    assert item.overall_score == 1.0


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------


def test_every_documented_transition_is_valid():
    for from_state, targets in TRANSITIONS.items():
        for to_state in targets:
            validate_transition(from_state, to_state)  # must not raise


def test_invalid_transition_raises():
    with pytest.raises(InvalidTransitionError):
        validate_transition(LoopState.RECEIVED, LoopState.COMPLETED)


def test_skipping_states_is_invalid():
    with pytest.raises(InvalidTransitionError):
        validate_transition(LoopState.PLANNING, LoopState.SCORING)


@pytest.mark.parametrize("terminal", sorted(TERMINAL_STATES, key=lambda s: s.value))
def test_terminal_states_cannot_resume(terminal):
    with pytest.raises(TerminalStateError):
        validate_transition(terminal, LoopState.PLANNING)


def test_any_nonterminal_state_can_fail():
    for state in LoopState:
        if state in TERMINAL_STATES:
            continue
        validate_transition(state, LoopState.FAILED)  # must not raise
