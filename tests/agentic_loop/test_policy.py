from backend.app.agentic_loop.models import AgenticQueryRequest
from backend.app.agentic_loop.policy import (
    HARD_CEILING_EVIDENCE_ITEMS,
    HARD_CEILING_ITERATIONS,
    HARD_CEILING_RETRIEVAL_CALLS,
    MODE_DEFAULTS,
    resolve_budgets,
)


def test_mode_defaults_used_when_unset():
    for mode, defaults in MODE_DEFAULTS.items():
        req = AgenticQueryRequest(question="a research question here", mode=mode)
        resolved = resolve_budgets(req)
        assert resolved.max_iterations == defaults.max_iterations
        assert resolved.max_retrieval_calls == defaults.max_retrieval_calls
        assert resolved.max_evidence_items == defaults.max_evidence_items
        assert resolved.minimum_confidence == defaults.minimum_confidence
        assert resolved.minimum_evidence_gain == defaults.minimum_evidence_gain


def test_caller_override_respected_under_ceiling():
    req = AgenticQueryRequest(question="a research question here", mode="fast", max_iterations=3)
    resolved = resolve_budgets(req)
    assert resolved.max_iterations == 3


def test_hard_ceiling_clamps_oversized_caller_request():
    req = AgenticQueryRequest(
        question="a research question here",
        mode="proof",
        max_iterations=HARD_CEILING_ITERATIONS + 50,
        max_retrieval_calls=HARD_CEILING_RETRIEVAL_CALLS + 50,
        max_evidence_items=HARD_CEILING_EVIDENCE_ITEMS + 50,
    )
    resolved = resolve_budgets(req)
    assert resolved.max_iterations == HARD_CEILING_ITERATIONS
    assert resolved.max_retrieval_calls == HARD_CEILING_RETRIEVAL_CALLS
    assert resolved.max_evidence_items == HARD_CEILING_EVIDENCE_ITEMS
