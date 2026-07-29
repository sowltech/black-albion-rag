"""Typed errors for the elite governed agentic RAG loop.

Every expected failure mode in the loop must raise one of these so the
orchestration service can map it to an explicit terminal outcome instead of
collapsing everything into a generic exception.
"""
from __future__ import annotations


class AgenticLoopError(Exception):
    """Base class for all agentic-loop errors."""


class InvalidRequestError(AgenticLoopError):
    """Raised when an ``AgenticQueryRequest`` fails validation or exceeds a
    hard safety ceiling that cannot be relaxed by caller-supplied budgets."""


class InvalidTransitionError(AgenticLoopError):
    """Raised when the loop state machine is asked to make a transition that
    is not present in the allowed transition table."""

    def __init__(self, from_state: str, to_state: str) -> None:
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(f"invalid state transition: {from_state} -> {to_state}")


class TerminalStateError(AgenticLoopError):
    """Raised when a transition is attempted out of a terminal state."""

    def __init__(self, state: str) -> None:
        self.state = state
        super().__init__(f"state {state} is terminal and cannot resume")


class PolicyBlockedError(AgenticLoopError):
    """Raised when a policy boundary (tier elevation, canonical write, etc.)
    would be violated by the requested operation."""


class BudgetExceededError(AgenticLoopError):
    """Raised when an operation would exceed a configured or hard-ceiling
    budget (iterations, retrieval calls, evidence items)."""


class ReceiptChainError(AgenticLoopError):
    """Raised when the hash-chained receipt ledger fails verification."""


class CanonicalWriteDeniedError(PolicyBlockedError):
    """Raised if any code path attempts a canonical or candidate-ledger
    mutation from within the agentic loop. The loop is read-only by
    invariant; this error exists so that invariant is enforceable and
    testable rather than merely documented."""


class InvariantViolationError(AgenticLoopError):
    """Raised when an internal invariant (e.g. monotonic iteration counter,
    non-empty receipt chain) is violated. Maps to ``INTERNAL_ERROR``."""
