"""Orchestration: the one place that wires planner, retriever, scorer, gap
detector, contradiction lifecycle, governor, receipts, and synthesiser into
a bounded run.

The loop is read-only end to end. Nothing in this module writes to a
canonical or candidate ledger, promotes a claim, changes a tier, or deletes
a contradiction -- there is no such method on any collaborator it holds.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, List, Optional, Sequence, Set

from . import contradiction as contradiction_ops
from . import scorer as scoring
from .errors import AgenticLoopError, InvariantViolationError
from .gap_detector import coverage_ratio, detect_gaps, group_evidence_by_subquestion
from .governor import (
    BUDGET_REASON_CODES,
    GovernorInputs,
    REASON_TO_OUTCOME,
    compute_information_gain,
    decide,
)
from .models import (
    AgenticQueryRequest,
    AgenticResult,
    BudgetSnapshot,
    Contradiction,
    EvidenceItem,
    GovernorAction,
    IterationReceipt,
    LoopState,
    RetrievalQuery,
    Subquestion,
    TerminalOutcome,
    validate_transition,
)
from .planner import Planner, QueryRepetitionTracker
from .policy import resolve_budgets
from .receipts import GENESIS_HASH, seal_receipt, verify_chain
from .retriever import Retriever
from .synthesiser import SynthesisResult, synthesise

Clock = Callable[[], str]


def _default_clock() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check_policy(request: AgenticQueryRequest) -> Optional[str]:
    """Request-level policy boundary. Proof mode exists to produce a
    verifiable answer; it cannot do that with Tier I evidence excluded, so
    it is rejected before any retrieval is attempted."""
    if request.mode == "proof" and "I" not in request.include_tiers:
        return "proof mode requires Tier I evidence to be included in include_tiers"
    return None


def _source_diversity(evidence: Sequence[EvidenceItem]) -> float:
    if not evidence:
        return 0.0
    return len({item.source_id for item in evidence}) / len(evidence)


def _confidence(
    subquestions: Sequence[Subquestion],
    evidence: Sequence[EvidenceItem],
    queries: Sequence[RetrievalQuery],
    contradictions: Sequence[Contradiction],
) -> float:
    if not subquestions:
        return 0.0
    grouped = group_evidence_by_subquestion(evidence, queries)
    scores: List[float] = []
    for sq in subquestions:
        items = grouped.get(sq.subquestion_id, [])
        if not items:
            scores.append(0.0)
            continue
        ids = {item.evidence_id for item in items}
        blocked = any(
            ids & (set(c.supporting_evidence_ids) | set(c.opposing_evidence_ids))
            for c in contradictions
            if c.status in ("open", "partially_resolved")
        )
        scores.append(0.0 if blocked else max(item.overall_score for item in items))
    return sum(scores) / len(scores)


def _outcome_for_success(synthesis: SynthesisResult) -> TerminalOutcome:
    if synthesis.unsupported_claims or synthesis.qualified_claims:
        return TerminalOutcome.PARTIAL_EVIDENCE
    return TerminalOutcome.ANSWERED


def _outcome_for_no_addressable_gap(synthesis: SynthesisResult) -> TerminalOutcome:
    if not synthesis.supported_claims and not synthesis.qualified_claims:
        return TerminalOutcome.INSUFFICIENT_EVIDENCE
    if synthesis.unsupported_claims or synthesis.qualified_claims:
        return TerminalOutcome.PARTIAL_EVIDENCE
    return TerminalOutcome.ANSWERED


def _outcome_for_budget_exhaustion(synthesis: SynthesisResult) -> TerminalOutcome:
    if not synthesis.supported_claims and not synthesis.qualified_claims:
        return TerminalOutcome.INSUFFICIENT_EVIDENCE
    return TerminalOutcome.BUDGET_EXHAUSTED


class AgenticLoopService:
    def __init__(self, planner: Planner, retriever: Retriever, clock: Clock = _default_clock) -> None:
        self._planner = planner
        self._retriever = retriever
        self._clock = clock

    def run(self, request: AgenticQueryRequest, run_id: str) -> AgenticResult:
        try:
            return self._run(request, run_id)
        except AgenticLoopError as exc:
            return self._failure_result(request, run_id, str(exc))
        except Exception as exc:  # noqa: BLE001 - deliberate INTERNAL_ERROR boundary
            return self._failure_result(request, run_id, f"internal error: {exc}")

    def _failure_result(self, request: AgenticQueryRequest, run_id: str, reason: str) -> AgenticResult:
        return AgenticResult(
            run_id=run_id,
            question=request.question,
            outcome=TerminalOutcome.INTERNAL_ERROR,
            answer="",
            supported_claims=[],
            unsupported_claims=[],
            evidence_ids=[],
            open_gaps=[],
            contradictions=[],
            iterations_completed=0,
            retrieval_calls_used=0,
            stop_reason=reason,
            final_confidence=0.0,
            final_coverage=0.0,
            receipt_chain_head=GENESIS_HASH,
            operator_review_required=False,
        )

    def _run(self, request: AgenticQueryRequest, run_id: str) -> AgenticResult:
        budgets = resolve_budgets(request)
        policy_block_reason = _check_policy(request)

        state = LoopState.RECEIVED
        state = self._advance(state, LoopState.DECOMPOSING)
        subquestions = self._planner.decompose(request.question)

        state = self._advance(state, LoopState.PLANNING)

        queries_all: List[RetrievalQuery] = []
        evidence_all: List[EvidenceItem] = []
        contradictions: List[Contradiction] = []
        receipts: List[IterationReceipt] = []
        exhausted_strategies: Set[str] = set()
        repetition_tracker = QueryRepetitionTracker()

        retrieval_calls_used = 0
        consecutive_no_gain = 0
        previous_hash = GENESIS_HASH
        confidence_before = 0.0
        coverage_before = 0.0
        source_diversity_before = 0.0

        iteration = 0
        final_decision = None
        synthesis: Optional[SynthesisResult] = None

        while True:
            iteration += 1
            state_before_iteration = state

            gaps_before = detect_gaps(subquestions, evidence_all, queries_all, contradictions)
            new_queries = self._planner.next_queries(
                iteration, subquestions, gaps_before, exhausted_strategies
            )
            has_addressable_gap = bool(new_queries)

            repeated_query_detected = any(
                repetition_tracker.is_repeat(query.text) for query in new_queries
            )

            state = self._advance(state, LoopState.RETRIEVING)
            retrieval_calls_used_before = retrieval_calls_used
            evidence_count_before = len(evidence_all)
            iteration_new_raw: List[EvidenceItem] = []
            for query in new_queries:
                if repetition_tracker.is_repeat(query.text):
                    continue
                if retrieval_calls_used >= budgets.max_retrieval_calls:
                    break
                repetition_tracker.register(query.text)
                retrieval_calls_used += 1
                queries_all.append(query)
                iteration_new_raw.extend(self._retriever.retrieve(query))

            state = self._advance(state, LoopState.SCORING)
            scored = scoring.score_batch(iteration_new_raw)
            evidence_seen_ids = sorted({item.evidence_id for item in scored})

            existing_ids = {item.evidence_id for item in evidence_all}
            combined = evidence_all + scored
            unique_combined, duplicates_combined = scoring.deduplicate(combined)
            new_items = [item for item in unique_combined if item.evidence_id not in existing_ids]
            new_evidence_ids = sorted({item.evidence_id for item in new_items})
            duplicate_evidence_ids = sorted({item.evidence_id for item in duplicates_combined})
            evidence_all = unique_combined
            if len(evidence_all) > budgets.max_evidence_items:
                evidence_all = evidence_all[: budgets.max_evidence_items]

            state = self._advance(state, LoopState.ASSESSING_GAPS)
            gaps_after = detect_gaps(subquestions, evidence_all, queries_all, contradictions)
            coverage_after = coverage_ratio(subquestions, gaps_after)

            state = self._advance(state, LoopState.ASSESSING_CONTRADICTIONS)
            detected = contradiction_ops.detect_from_evidence(evidence_all)
            existing_by_id = {c.contradiction_id: c for c in contradictions}
            merged: List[Contradiction] = []
            contradictions_opened: List[str] = []
            for candidate in detected:
                prior = existing_by_id.get(candidate.contradiction_id)
                if prior is None:
                    merged.append(candidate)
                    contradictions_opened.append(candidate.contradiction_id)
                else:
                    merged.append(
                        prior.model_copy(
                            update={
                                "supporting_evidence_ids": sorted(
                                    set(prior.supporting_evidence_ids)
                                    | set(candidate.supporting_evidence_ids)
                                ),
                                "opposing_evidence_ids": sorted(
                                    set(prior.opposing_evidence_ids)
                                    | set(candidate.opposing_evidence_ids)
                                ),
                            }
                        )
                    )
            contradictions = merged
            # Phase 1 never resolves a contradiction automatically (see
            # contradiction.py) -- resolution is always an explicit,
            # reasoned operator/planner action outside this loop.
            contradictions_resolved: List[str] = []

            confidence_after = _confidence(subquestions, evidence_all, queries_all, contradictions)
            source_diversity_after = _source_diversity(evidence_all)

            gain = compute_information_gain(
                coverage_before=coverage_before,
                coverage_after=coverage_after,
                confidence_before=confidence_before,
                confidence_after=confidence_after,
                new_evidence_count=len(new_items),
                duplicate_evidence_count=len(duplicate_evidence_ids),
                contradictions_resolved=len(contradictions_resolved),
                source_diversity_before=source_diversity_before,
                source_diversity_after=source_diversity_after,
                repeated_query_detected=repeated_query_detected,
            )
            if gain < budgets.minimum_evidence_gain:
                consecutive_no_gain += 1
            else:
                consecutive_no_gain = 0

            state = self._advance(state, LoopState.GOVERNING)
            governor_inputs = GovernorInputs(
                iteration=iteration,
                max_iterations=budgets.max_iterations,
                retrieval_calls_used=retrieval_calls_used,
                max_retrieval_calls=budgets.max_retrieval_calls,
                evidence_items_used=len(evidence_all),
                max_evidence_items=budgets.max_evidence_items,
                confidence=confidence_after,
                coverage=coverage_after,
                minimum_confidence=budgets.minimum_confidence,
                latest_gain=gain,
                minimum_evidence_gain=budgets.minimum_evidence_gain,
                consecutive_no_gain=consecutive_no_gain,
                stop_after_consecutive_no_gain=budgets.stop_after_consecutive_no_gain,
                repeated_query_detected=repeated_query_detected,
                stop_on_repeated_query=budgets.stop_on_repeated_query,
                has_unresolved_material_contradiction=(
                    contradiction_ops.has_unresolved_material_contradiction(contradictions)
                ),
                has_addressable_gap=has_addressable_gap,
                policy_blocked=policy_block_reason is not None,
                policy_block_reason=policy_block_reason,
            )
            decision = decide(governor_inputs)

            budget_before = BudgetSnapshot(
                iterations_remaining=max(0, budgets.max_iterations - (iteration - 1)),
                retrieval_calls_remaining=max(
                    0, budgets.max_retrieval_calls - retrieval_calls_used_before
                ),
                evidence_items_remaining=max(0, budgets.max_evidence_items - evidence_count_before),
            )
            budget_after = BudgetSnapshot(
                iterations_remaining=max(0, budgets.max_iterations - iteration),
                retrieval_calls_remaining=max(0, budgets.max_retrieval_calls - retrieval_calls_used),
                evidence_items_remaining=max(0, budgets.max_evidence_items - len(evidence_all)),
            )

            receipt = IterationReceipt(
                run_id=run_id,
                iteration=iteration,
                state_before=state_before_iteration.value,
                queries_issued=[q.query_id for q in new_queries],
                evidence_seen=evidence_seen_ids,
                new_evidence_ids=new_evidence_ids,
                duplicate_evidence_ids=duplicate_evidence_ids,
                coverage_before=coverage_before,
                coverage_after=coverage_after,
                confidence_before=confidence_before,
                confidence_after=confidence_after,
                evidence_gain=gain,
                contradictions_opened=contradictions_opened,
                contradictions_resolved=contradictions_resolved,
                budget_before=budget_before,
                budget_after=budget_after,
                decision=decision.action,
                decision_reason=f"{decision.reason_code}: {decision.explanation}",
                previous_receipt_hash=previous_hash,
                receipt_hash="",
                timestamp=self._clock(),
            )
            receipt = seal_receipt(receipt)
            receipts.append(receipt)
            previous_hash = receipt.receipt_hash

            coverage_before = coverage_after
            confidence_before = confidence_after
            source_diversity_before = source_diversity_after

            if decision.action == GovernorAction.CONTINUE:
                if not new_queries:
                    exhausted_strategies.add("refinement")
                state = self._advance(state, LoopState.PLANNING)
                continue

            final_decision = decision
            break

        verify_chain(receipts)

        state = self._advance(state, LoopState.SYNTHESISING)
        synthesis = synthesise(request.question, subquestions, evidence_all, queries_all, contradictions)

        assert final_decision is not None  # loop only exits via `break` after setting this
        outcome = REASON_TO_OUTCOME.get(final_decision.reason_code)
        if outcome is None:
            if final_decision.reason_code == "SUCCESS_THRESHOLD_REACHED":
                outcome = _outcome_for_success(synthesis)
            elif final_decision.reason_code == "NO_ADDRESSABLE_GAP_REMAINS":
                outcome = _outcome_for_no_addressable_gap(synthesis)
            elif final_decision.reason_code in BUDGET_REASON_CODES:
                outcome = _outcome_for_budget_exhaustion(synthesis)
            else:
                raise InvariantViolationError(
                    f"governor reason code {final_decision.reason_code!r} has no outcome mapping"
                )

        final_state = LoopState.COMPLETED if outcome == TerminalOutcome.ANSWERED else LoopState.STOPPED
        state = self._advance(state, final_state)

        gaps_final = detect_gaps(subquestions, evidence_all, queries_all, contradictions)

        return AgenticResult(
            run_id=run_id,
            question=request.question,
            outcome=outcome,
            answer=synthesis.answer,
            supported_claims=synthesis.supported_claims,
            unsupported_claims=synthesis.unsupported_claims + synthesis.qualified_claims,
            evidence_ids=synthesis.evidence_ids,
            open_gaps=[gap.gap_id for gap in gaps_final if gap.status == "open"],
            contradictions=contradiction_ops.open_contradiction_ids(contradictions),
            iterations_completed=iteration,
            retrieval_calls_used=retrieval_calls_used,
            stop_reason=f"{final_decision.reason_code}: {final_decision.explanation}",
            final_confidence=confidence_before,
            final_coverage=coverage_before,
            receipt_chain_head=previous_hash,
            operator_review_required=outcome
            in (TerminalOutcome.OPERATOR_REVIEW_REQUIRED, TerminalOutcome.CONTRADICTION_UNRESOLVED),
        )

    @staticmethod
    def _advance(current: LoopState, target: LoopState) -> LoopState:
        validate_transition(current, target)
        return target
