"""Typed contracts for the elite governed agentic RAG loop.

These models are intentionally self-contained: nothing here imports the
existing Black Albion retriever, ledgers, or FastAPI app. Phase 1 wires the
loop kernel to deterministic in-memory test doubles only. A later phase adds
a read-only adapter over the real ledgers behind the ``Retriever`` protocol
defined in ``retriever.py``.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, FrozenSet, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

SourceTier = Literal["I", "II", "III"]
LoopMode = Literal["fast", "deep", "proof"]


# ---------------------------------------------------------------------------
# Loop state machine
# ---------------------------------------------------------------------------


class LoopState(str, Enum):
    RECEIVED = "RECEIVED"
    DECOMPOSING = "DECOMPOSING"
    PLANNING = "PLANNING"
    RETRIEVING = "RETRIEVING"
    SCORING = "SCORING"
    ASSESSING_GAPS = "ASSESSING_GAPS"
    ASSESSING_CONTRADICTIONS = "ASSESSING_CONTRADICTIONS"
    GOVERNING = "GOVERNING"
    SYNTHESISING = "SYNTHESISING"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


#: Allowed forward transitions. Any non-terminal state may also transition to
#: ``FAILED`` (an internal invariant violation can surface at any stage) --
#: that edge is added programmatically below rather than repeated by hand.
_BASE_TRANSITIONS: Dict[LoopState, FrozenSet[LoopState]] = {
    LoopState.RECEIVED: frozenset({LoopState.DECOMPOSING}),
    LoopState.DECOMPOSING: frozenset({LoopState.PLANNING}),
    LoopState.PLANNING: frozenset({LoopState.RETRIEVING}),
    LoopState.RETRIEVING: frozenset({LoopState.SCORING}),
    LoopState.SCORING: frozenset({LoopState.ASSESSING_GAPS}),
    LoopState.ASSESSING_GAPS: frozenset({LoopState.ASSESSING_CONTRADICTIONS}),
    LoopState.ASSESSING_CONTRADICTIONS: frozenset({LoopState.GOVERNING}),
    LoopState.GOVERNING: frozenset({LoopState.PLANNING, LoopState.SYNTHESISING}),
    LoopState.SYNTHESISING: frozenset({LoopState.COMPLETED, LoopState.STOPPED}),
    LoopState.COMPLETED: frozenset(),
    LoopState.STOPPED: frozenset(),
    LoopState.FAILED: frozenset(),
}

TERMINAL_STATES: FrozenSet[LoopState] = frozenset(
    {LoopState.COMPLETED, LoopState.STOPPED, LoopState.FAILED}
)

TRANSITIONS: Dict[LoopState, FrozenSet[LoopState]] = {
    state: (targets | {LoopState.FAILED} if state not in TERMINAL_STATES else targets)
    for state, targets in _BASE_TRANSITIONS.items()
}


def validate_transition(from_state: LoopState, to_state: LoopState) -> None:
    """Raise a typed error if ``from_state -> to_state`` is not permitted."""
    from .errors import InvalidTransitionError, TerminalStateError

    if from_state in TERMINAL_STATES:
        raise TerminalStateError(from_state.value)
    if to_state not in TRANSITIONS[from_state]:
        raise InvalidTransitionError(from_state.value, to_state.value)


class TerminalOutcome(str, Enum):
    ANSWERED = "ANSWERED"
    PARTIAL_EVIDENCE = "PARTIAL_EVIDENCE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONTRADICTION_UNRESOLVED = "CONTRADICTION_UNRESOLVED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    NO_INFORMATION_GAIN = "NO_INFORMATION_GAIN"
    REPEATED_QUERY = "REPEATED_QUERY"
    OPERATOR_REVIEW_REQUIRED = "OPERATOR_REVIEW_REQUIRED"
    POLICY_BLOCKED = "POLICY_BLOCKED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class GovernorAction(str, Enum):
    CONTINUE = "CONTINUE"
    SYNTHESISE = "SYNTHESISE"
    STOP = "STOP"
    ESCALATE = "ESCALATE"


# ---------------------------------------------------------------------------
# Request contract
# ---------------------------------------------------------------------------


class AgenticQueryRequest(BaseModel):
    """A bounded request to run the agentic retrieval loop."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=3)
    mode: LoopMode = "fast"
    include_tiers: List[SourceTier] = Field(default_factory=lambda: ["I", "II", "III"])
    max_iterations: Optional[int] = Field(default=None, description="Overrides mode default.")
    max_retrieval_calls: Optional[int] = None
    max_evidence_items: Optional[int] = None
    minimum_confidence: Optional[float] = None
    minimum_evidence_gain: Optional[float] = None
    stop_on_repeated_query: bool = True
    stop_after_consecutive_no_gain: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "max_iterations", "max_retrieval_calls", "max_evidence_items", "stop_after_consecutive_no_gain"
    )
    @classmethod
    def _positive_when_present(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value <= 0:
            raise ValueError("budget values must be greater than zero")
        return value

    @field_validator("minimum_confidence", "minimum_evidence_gain")
    @classmethod
    def _unit_interval_when_present(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not (0.0 <= value <= 1.0):
            raise ValueError("confidence and gain thresholds must be within [0.0, 1.0]")
        return value

    @field_validator("include_tiers")
    @classmethod
    def _non_empty_tiers(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("include_tiers must not be empty")
        return value


# ---------------------------------------------------------------------------
# Decomposition + planning
# ---------------------------------------------------------------------------

SubquestionStatus = Literal["pending", "in_progress", "answered", "unsupported"]


class Subquestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subquestion_id: str
    text: str
    priority: int = 0
    required_evidence_types: List[str] = Field(default_factory=list)
    status: SubquestionStatus = "pending"


RetrievalStrategy = Literal["lexical", "targeted", "refinement", "corroboration"]


class RetrievalQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query_id: str
    iteration: int = Field(ge=1)
    text: str
    strategy: RetrievalStrategy = "lexical"
    target_sources: List[str] = Field(default_factory=list)
    parent_subquestion_ids: List[str] = Field(default_factory=list)
    normalised_hash: str


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    content: str
    source_id: str
    source_type: str
    source_reference: str
    tier: SourceTier
    retrieval_query_id: str
    relevance: float
    authority: float
    freshness: float
    consistency: float
    completeness: float
    provenance_quality: float
    overall_score: float
    supports_claims: List[str] = Field(default_factory=list)
    opposes_claims: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    content_hash: str

    @field_validator(
        "relevance",
        "authority",
        "freshness",
        "consistency",
        "completeness",
        "provenance_quality",
        "overall_score",
    )
    @classmethod
    def _clamp_score(cls, value: float) -> float:
        return _clamp_unit(float(value))


# ---------------------------------------------------------------------------
# Gaps
# ---------------------------------------------------------------------------

GapSeverity = Literal["low", "medium", "high"]
GapStatus = Literal["open", "addressed"]


class Gap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gap_id: str
    subquestion_id: str
    description: str
    severity: GapSeverity = "medium"
    required_evidence: List[str] = Field(default_factory=list)
    status: GapStatus = "open"


# ---------------------------------------------------------------------------
# Contradictions
# ---------------------------------------------------------------------------

ContradictionMateriality = Literal["low", "medium", "high"]
ContradictionStatus = Literal[
    "open", "partially_resolved", "resolved", "operator_review_required"
]


class Contradiction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contradiction_id: str
    claim_or_question: str
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    opposing_evidence_ids: List[str] = Field(default_factory=list)
    materiality: ContradictionMateriality = "medium"
    status: ContradictionStatus = "open"
    resolution_reason: Optional[str] = None
    resolved_by_evidence_ids: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Receipts
# ---------------------------------------------------------------------------


class BudgetSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    iterations_remaining: int
    retrieval_calls_remaining: int
    evidence_items_remaining: int


class IterationReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    iteration: int
    state_before: str
    queries_issued: List[str] = Field(default_factory=list)
    evidence_seen: List[str] = Field(default_factory=list)
    new_evidence_ids: List[str] = Field(default_factory=list)
    duplicate_evidence_ids: List[str] = Field(default_factory=list)
    coverage_before: float
    coverage_after: float
    confidence_before: float
    confidence_after: float
    evidence_gain: float
    contradictions_opened: List[str] = Field(default_factory=list)
    contradictions_resolved: List[str] = Field(default_factory=list)
    budget_before: BudgetSnapshot
    budget_after: BudgetSnapshot
    decision: GovernorAction
    decision_reason: str
    previous_receipt_hash: str
    receipt_hash: str
    timestamp: str


# ---------------------------------------------------------------------------
# Final result
# ---------------------------------------------------------------------------


class AgenticResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    question: str
    outcome: TerminalOutcome
    answer: str
    supported_claims: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    open_gaps: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    iterations_completed: int
    retrieval_calls_used: int
    stop_reason: str
    final_confidence: float
    final_coverage: float
    receipt_chain_head: str
    operator_review_required: bool = False
