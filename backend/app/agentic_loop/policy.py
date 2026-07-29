"""Execution modes, budget resolution, hard ceilings, and scoring weights.

This module holds no behaviour tied to a specific run -- it is pure
configuration plus the arithmetic needed to resolve a caller's request into
concrete, ceiling-clamped budgets. Nothing here talks to a retriever, a
model, or a ledger.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .errors import CanonicalWriteDeniedError
from .models import AgenticQueryRequest, LoopMode

# ---------------------------------------------------------------------------
# Mode defaults (docs/elite-agentic-rag-loop.md "Loop governor" table, as
# refined by the Phase 1 implementation contract).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ModeDefaults:
    max_iterations: int
    max_retrieval_calls: int
    max_evidence_items: int
    minimum_confidence: float
    minimum_evidence_gain: float
    stop_after_consecutive_no_gain: int


MODE_DEFAULTS: Dict[LoopMode, ModeDefaults] = {
    "fast": ModeDefaults(
        max_iterations=2,
        max_retrieval_calls=4,
        max_evidence_items=30,
        minimum_confidence=0.75,
        minimum_evidence_gain=0.10,
        stop_after_consecutive_no_gain=1,
    ),
    "deep": ModeDefaults(
        max_iterations=5,
        max_retrieval_calls=12,
        max_evidence_items=100,
        minimum_confidence=0.85,
        minimum_evidence_gain=0.08,
        stop_after_consecutive_no_gain=2,
    ),
    "proof": ModeDefaults(
        max_iterations=7,
        max_retrieval_calls=20,
        max_evidence_items=200,
        minimum_confidence=0.92,
        minimum_evidence_gain=0.05,
        stop_after_consecutive_no_gain=2,
    ),
}

# Hard ceilings: no caller-supplied override, from any mode, may exceed
# these. resolve_budgets() clamps silently down to the ceiling because a
# clamp is a safety floor, not a discovery cap -- the caller asked for "at
# most N" and received "at most min(N, ceiling)", which is still a truthful
# answer to what they asked for.
HARD_CEILING_ITERATIONS = 10
HARD_CEILING_RETRIEVAL_CALLS = 30
HARD_CEILING_EVIDENCE_ITEMS = 300
HARD_CEILING_CONSECUTIVE_NO_GAIN = 5


@dataclass(frozen=True)
class ResolvedBudgets:
    max_iterations: int
    max_retrieval_calls: int
    max_evidence_items: int
    minimum_confidence: float
    minimum_evidence_gain: float
    stop_after_consecutive_no_gain: int
    stop_on_repeated_query: bool


def resolve_budgets(request: AgenticQueryRequest) -> ResolvedBudgets:
    """Fill unset fields from the mode default, then clamp to hard ceilings."""
    defaults = MODE_DEFAULTS[request.mode]
    return ResolvedBudgets(
        max_iterations=min(
            request.max_iterations or defaults.max_iterations, HARD_CEILING_ITERATIONS
        ),
        max_retrieval_calls=min(
            request.max_retrieval_calls or defaults.max_retrieval_calls,
            HARD_CEILING_RETRIEVAL_CALLS,
        ),
        max_evidence_items=min(
            request.max_evidence_items or defaults.max_evidence_items,
            HARD_CEILING_EVIDENCE_ITEMS,
        ),
        minimum_confidence=(
            request.minimum_confidence
            if request.minimum_confidence is not None
            else defaults.minimum_confidence
        ),
        minimum_evidence_gain=(
            request.minimum_evidence_gain
            if request.minimum_evidence_gain is not None
            else defaults.minimum_evidence_gain
        ),
        stop_after_consecutive_no_gain=min(
            request.stop_after_consecutive_no_gain
            or defaults.stop_after_consecutive_no_gain,
            HARD_CEILING_CONSECUTIVE_NO_GAIN,
        ),
        stop_on_repeated_query=request.stop_on_repeated_query,
    )


# ---------------------------------------------------------------------------
# Evidence scoring weights (docs/elite-agentic-rag-loop.md "Evidence model").
# ---------------------------------------------------------------------------

EVIDENCE_SCORE_WEIGHTS: Dict[str, float] = {
    "relevance": 0.30,
    "authority": 0.20,
    "provenance_quality": 0.15,
    "freshness": 0.10,
    "consistency": 0.15,
    "completeness": 0.10,
}

# ---------------------------------------------------------------------------
# Information-gain weights (docs/elite-agentic-rag-loop.md "Evidence gain",
# expanded to the component list in the Phase 1 implementation contract).
# Positive terms reward genuine progress; penalties subtract for retrieval
# that produced nothing new. The sum is clamped to [0.0, 1.0] by the caller.
# ---------------------------------------------------------------------------

GAIN_WEIGHTS: Dict[str, float] = {
    "coverage_delta": 0.30,
    "confidence_delta": 0.15,
    "unique_evidence": 0.20,
    "contradiction_resolution": 0.15,
    "source_diversity": 0.10,
    "duplicate_penalty": 0.15,
    "repeated_query_penalty": 0.25,
}

# ---------------------------------------------------------------------------
# Tier policy
# ---------------------------------------------------------------------------

#: Tier III material is speculative by definition and may never be treated
#: as if it were Tier I archival evidence. Consulted by the scorer and the
#: synthesiser rather than enforced by a single chokepoint, because both
#: sides of that boundary need the same answer.
TIER_ELEVATION_FORBIDDEN = frozenset({"III"})


def forbid_canonical_write(reason: str) -> None:
    """Always raises. Nothing in the agentic loop is wired to call this with
    intent to succeed -- it exists so the read-only invariant is a concrete,
    testable assertion rather than only a comment."""
    raise CanonicalWriteDeniedError(reason)
