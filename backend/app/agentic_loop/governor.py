"""Information-gain scoring and the single authoritative continue/stop
decision.

``compute_information_gain`` is arithmetic over observed deltas -- never a
model's self-report of how useful an iteration "felt". It is a governed
operational score, not a probabilistic certainty.

``decide`` is the one place that inspects budgets, gain, repetition, and
contradiction state and produces a structured decision. Nothing else in the
package is allowed to independently decide to keep looping.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .models import GovernorAction, TerminalOutcome
from .policy import GAIN_WEIGHTS


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def compute_information_gain(
    coverage_before: float,
    coverage_after: float,
    confidence_before: float,
    confidence_after: float,
    new_evidence_count: int,
    duplicate_evidence_count: int,
    contradictions_resolved: int,
    source_diversity_before: float,
    source_diversity_after: float,
    repeated_query_detected: bool,
) -> float:
    """Bounded [0.0, 1.0] measure of how much an iteration actually moved
    the run forward. Declines (confidence or coverage going down) contribute
    zero rather than a negative number -- they are punished separately by
    the duplicate/repeated-query penalties and by the governor's no-gain
    counter, not folded into this score as a negative contribution."""
    coverage_delta = max(0.0, coverage_after - coverage_before)
    confidence_delta = max(0.0, confidence_after - confidence_before)
    source_diversity_delta = max(0.0, source_diversity_after - source_diversity_before)

    total_seen = new_evidence_count + duplicate_evidence_count
    unique_ratio = (new_evidence_count / total_seen) if total_seen else 0.0
    duplicate_ratio = (duplicate_evidence_count / total_seen) if total_seen else 0.0
    contradiction_term = 1.0 if contradictions_resolved > 0 else 0.0
    repeated_query_term = 1.0 if repeated_query_detected else 0.0

    gain = (
        GAIN_WEIGHTS["coverage_delta"] * coverage_delta
        + GAIN_WEIGHTS["confidence_delta"] * confidence_delta
        + GAIN_WEIGHTS["unique_evidence"] * unique_ratio
        + GAIN_WEIGHTS["contradiction_resolution"] * contradiction_term
        + GAIN_WEIGHTS["source_diversity"] * source_diversity_delta
        - GAIN_WEIGHTS["duplicate_penalty"] * duplicate_ratio
        - GAIN_WEIGHTS["repeated_query_penalty"] * repeated_query_term
    )
    return _clamp_unit(gain)


# Reason codes that map to exactly one terminal outcome regardless of what
# the synthesiser later finds. ``SUCCESS_THRESHOLD_REACHED``,
# ``NO_ADDRESSABLE_GAP_REMAINS``, and the three budget-exhaustion codes are
# deliberately absent: whether those land on ``ANSWERED``, ``PARTIAL_EVIDENCE``,
# ``INSUFFICIENT_EVIDENCE``, or ``BUDGET_EXHAUSTED`` depends on what the
# synthesiser actually managed to support, so service.py resolves them after
# synthesis rather than here.
REASON_TO_OUTCOME: Dict[str, TerminalOutcome] = {
    "POLICY_BLOCKED": TerminalOutcome.POLICY_BLOCKED,
    "CONTRADICTION_REQUIRES_OPERATOR_REVIEW": TerminalOutcome.OPERATOR_REVIEW_REQUIRED,
    "REPEATED_QUERY": TerminalOutcome.REPEATED_QUERY,
    "NO_INFORMATION_GAIN": TerminalOutcome.NO_INFORMATION_GAIN,
    "CONTRADICTION_BLOCKS_ANSWER": TerminalOutcome.CONTRADICTION_UNRESOLVED,
}

#: Reason codes that represent some flavour of budget exhaustion. Grouped so
#: service.py can apply one dynamic resolution rule to all three.
BUDGET_REASON_CODES = frozenset(
    {"MAX_ITERATIONS_REACHED", "RETRIEVAL_CALL_BUDGET_EXHAUSTED", "EVIDENCE_ITEM_BUDGET_EXHAUSTED"}
)


@dataclass(frozen=True)
class GovernorInputs:
    iteration: int
    max_iterations: int
    retrieval_calls_used: int
    max_retrieval_calls: int
    evidence_items_used: int
    max_evidence_items: int
    confidence: float
    coverage: float
    minimum_confidence: float
    latest_gain: float
    minimum_evidence_gain: float
    consecutive_no_gain: int
    stop_after_consecutive_no_gain: int
    repeated_query_detected: bool
    stop_on_repeated_query: bool
    has_unresolved_material_contradiction: bool
    has_addressable_gap: bool
    policy_blocked: bool
    policy_block_reason: Optional[str] = None


@dataclass(frozen=True)
class GovernorDecision:
    action: GovernorAction
    reason_code: str
    explanation: str
    metrics: Dict[str, Any] = field(default_factory=dict)


def decide(inputs: GovernorInputs) -> GovernorDecision:
    metrics = {
        "iteration": inputs.iteration,
        "retrieval_calls_used": inputs.retrieval_calls_used,
        "evidence_items_used": inputs.evidence_items_used,
        "confidence": inputs.confidence,
        "coverage": inputs.coverage,
        "latest_gain": inputs.latest_gain,
        "consecutive_no_gain": inputs.consecutive_no_gain,
    }

    if inputs.policy_blocked:
        return GovernorDecision(
            GovernorAction.STOP,
            "POLICY_BLOCKED",
            inputs.policy_block_reason or "A policy boundary was reached.",
            metrics,
        )

    if inputs.has_unresolved_material_contradiction and not inputs.has_addressable_gap:
        return GovernorDecision(
            GovernorAction.ESCALATE,
            "CONTRADICTION_REQUIRES_OPERATOR_REVIEW",
            "A material contradiction remains unresolved and no further "
            "retrieval strategy can address it.",
            metrics,
        )

    # Success is checked before budget/repetition/no-gain concerns so that
    # reaching the goal on the same iteration a budget happens to run out
    # is still reported as success, not degraded to a budget outcome.
    success = inputs.confidence >= inputs.minimum_confidence and inputs.coverage >= 1.0
    if success:
        if inputs.has_unresolved_material_contradiction:
            return GovernorDecision(
                GovernorAction.SYNTHESISE,
                "CONTRADICTION_BLOCKS_ANSWER",
                "Confidence and coverage targets were met, but a material "
                "contradiction remains unresolved.",
                metrics,
            )
        return GovernorDecision(
            GovernorAction.SYNTHESISE,
            "SUCCESS_THRESHOLD_REACHED",
            f"Confidence {inputs.confidence:.2f} and full coverage reached.",
            metrics,
        )

    if inputs.iteration >= inputs.max_iterations:
        return GovernorDecision(
            GovernorAction.SYNTHESISE,
            "MAX_ITERATIONS_REACHED",
            f"Reached the maximum of {inputs.max_iterations} iterations.",
            metrics,
        )

    if inputs.retrieval_calls_used >= inputs.max_retrieval_calls:
        return GovernorDecision(
            GovernorAction.SYNTHESISE,
            "RETRIEVAL_CALL_BUDGET_EXHAUSTED",
            f"Reached the maximum of {inputs.max_retrieval_calls} retrieval calls.",
            metrics,
        )

    if inputs.evidence_items_used >= inputs.max_evidence_items:
        return GovernorDecision(
            GovernorAction.SYNTHESISE,
            "EVIDENCE_ITEM_BUDGET_EXHAUSTED",
            f"Reached the maximum of {inputs.max_evidence_items} evidence items.",
            metrics,
        )

    if inputs.repeated_query_detected and inputs.stop_on_repeated_query:
        return GovernorDecision(
            GovernorAction.STOP,
            "REPEATED_QUERY",
            "The planner issued a query equivalent to one already run this run.",
            metrics,
        )

    if inputs.consecutive_no_gain >= inputs.stop_after_consecutive_no_gain:
        return GovernorDecision(
            GovernorAction.SYNTHESISE,
            "NO_INFORMATION_GAIN",
            (
                f"{inputs.consecutive_no_gain} consecutive iteration(s) fell below the "
                f"minimum gain threshold of {inputs.minimum_evidence_gain}."
            ),
            metrics,
        )

    if not inputs.has_addressable_gap:
        return GovernorDecision(
            GovernorAction.SYNTHESISE,
            "NO_ADDRESSABLE_GAP_REMAINS",
            "No open gap has a remaining retrieval strategy.",
            metrics,
        )

    return GovernorDecision(
        GovernorAction.CONTINUE,
        "CONTINUE_ITERATING",
        "Budgets remain and at least one addressable gap exists.",
        metrics,
    )
