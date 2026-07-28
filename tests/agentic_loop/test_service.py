from backend.app.agentic_loop.models import AgenticQueryRequest, RetrievalQuery, Subquestion, TerminalOutcome
from backend.app.agentic_loop.planner import StaticPlanner, query_hash
from backend.app.agentic_loop.retriever import EvidenceRecord, InMemoryRetriever
from backend.app.agentic_loop.service import AgenticLoopService


def _fixed_clock():
    return "2026-07-28T00:00:00Z"


def _service(planner, records):
    return AgenticLoopService(planner, InMemoryRetriever(records), clock=_fixed_clock)


def _good_record(record_id, content, source_id="src", supports=None, opposes=None, tier="I"):
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


class RepeatPlanner:
    """Always issues the exact same query text, every iteration."""

    def __init__(self, text: str) -> None:
        self._text = text

    def decompose(self, question):
        return [Subquestion(subquestion_id="sq-1", text=question)]

    def next_queries(self, iteration, subquestions, open_gaps, exhausted_strategies):
        return [
            RetrievalQuery(
                query_id=f"q-{iteration}",
                iteration=iteration,
                text=self._text,
                parent_subquestion_ids=["sq-1"],
                normalised_hash=query_hash(self._text),
            )
        ]


class SingleAttemptPlanner:
    """Tries exactly once, then reports no further retrieval strategy."""

    def __init__(self, subquestion, text) -> None:
        self._subquestion = subquestion
        self._text = text

    def decompose(self, question):
        return [self._subquestion]

    def next_queries(self, iteration, subquestions, open_gaps, exhausted_strategies):
        if iteration != 1:
            return []
        return [
            RetrievalQuery(
                query_id="q-1",
                iteration=1,
                text=self._text,
                parent_subquestion_ids=[self._subquestion.subquestion_id],
                normalised_hash=query_hash(self._text),
            )
        ]


class TwoSubquestionSingleAttemptPlanner:
    """Issues one query per subquestion on iteration 1, then reports no
    further retrieval strategy -- simulates a planner that has genuinely
    exhausted what it knows how to try."""

    def __init__(self, subquestions, texts) -> None:
        self._subquestions = subquestions
        self._texts = texts

    def decompose(self, question):
        return list(self._subquestions)

    def next_queries(self, iteration, subquestions, open_gaps, exhausted_strategies):
        if iteration != 1:
            return []
        return [
            RetrievalQuery(
                query_id=f"q-{sq.subquestion_id}",
                iteration=1,
                text=text,
                parent_subquestion_ids=[sq.subquestion_id],
                normalised_hash=query_hash(text),
            )
            for sq, text in zip(self._subquestions, self._texts)
        ]


class PersistentAttemptPlanner:
    """Issues a new, non-repeating query every iteration (never runs dry,
    never repeats) so the run is driven purely by budgets."""

    def decompose(self, question):
        return [Subquestion(subquestion_id="sq-1", text=question)]

    def next_queries(self, iteration, subquestions, open_gaps, exhausted_strategies):
        text = f"attempt number {iteration} for an unfindable topic"
        return [
            RetrievalQuery(
                query_id=f"q-{iteration}",
                iteration=iteration,
                text=text,
                parent_subquestion_ids=["sq-1"],
                normalised_hash=query_hash(text),
            )
        ]


def _assert_well_formed(result):
    assert result.run_id
    assert result.iterations_completed >= 1
    assert isinstance(result.outcome, TerminalOutcome)
    assert result.stop_reason
    assert result.receipt_chain_head


def test_answered():
    sq = Subquestion(subquestion_id="sq-1", text="granite quarry survey")
    planner = StaticPlanner(subquestions=[sq], initial_query_texts=["granite quarry survey"])
    records = [_good_record("r1", "granite quarry survey record")]
    service = _service(planner, records)
    request = AgenticQueryRequest(question="granite quarry survey status", mode="fast")
    result = service.run(request, run_id="run-answered")
    assert result.outcome == TerminalOutcome.ANSWERED
    assert result.supported_claims
    assert not result.unsupported_claims
    _assert_well_formed(result)


def test_partial_evidence():
    sq1 = Subquestion(subquestion_id="sq-1", text="granite quarry survey")
    sq2 = Subquestion(subquestion_id="sq-2", text="unrelated missing topic zzz")
    planner = TwoSubquestionSingleAttemptPlanner(
        [sq1, sq2], ["granite quarry survey", "unrelated missing topic zzz"]
    )
    records = [_good_record("r1", "granite quarry survey record")]
    service = _service(planner, records)
    request = AgenticQueryRequest(question="mixed coverage question", mode="deep")
    result = service.run(request, run_id="run-partial")
    assert result.outcome == TerminalOutcome.PARTIAL_EVIDENCE
    assert result.supported_claims  # at least the granite subquestion made it through
    assert result.unsupported_claims  # the unfindable subquestion never got covered
    assert "NO_ADDRESSABLE_GAP_REMAINS" in result.stop_reason
    _assert_well_formed(result)


def test_insufficient_evidence():
    planner = PersistentAttemptPlanner()
    service = _service(planner, records=[])
    request = AgenticQueryRequest(
        question="deep dive into a topic with no sources",
        mode="deep",
        max_iterations=3,
        stop_on_repeated_query=False,
        stop_after_consecutive_no_gain=10,
    )
    result = service.run(request, run_id="run-insufficient")
    assert result.outcome == TerminalOutcome.INSUFFICIENT_EVIDENCE
    assert not result.supported_claims
    _assert_well_formed(result)


def test_contradiction_unresolved():
    sq1 = Subquestion(subquestion_id="sq-1", text="granite quarry survey")
    sq2 = Subquestion(subquestion_id="sq-2", text="riverford crossing claim")
    planner = StaticPlanner(
        subquestions=[sq1, sq2],
        initial_query_texts=["granite quarry survey", "riverford crossing claim"],
    )
    records = [
        _good_record("r1", "granite quarry survey record"),
        _good_record("r2", "riverford crossing claim pro", source_id="s2", supports=["disputed claim label"]),
        _good_record("r3", "riverford crossing claim contra", source_id="s3", opposes=["disputed claim label"]),
    ]
    service = _service(planner, records)
    request = AgenticQueryRequest(question="mixed with a contested claim", mode="fast", minimum_confidence=0.4)
    result = service.run(request, run_id="run-contradiction")
    assert result.outcome == TerminalOutcome.CONTRADICTION_UNRESOLVED
    assert result.contradictions
    assert result.operator_review_required is True
    _assert_well_formed(result)


def test_operator_review_required():
    sq1 = Subquestion(subquestion_id="sq-1", text="riverford crossing claim")
    planner = SingleAttemptPlanner(sq1, "riverford crossing claim")
    records = [
        _good_record("r2", "riverford crossing claim pro", source_id="s2", supports=["disputed claim label"]),
        _good_record("r3", "riverford crossing claim contra", source_id="s3", opposes=["disputed claim label"]),
    ]
    service = _service(planner, records)
    request = AgenticQueryRequest(question="only a contested claim to resolve", mode="deep", minimum_confidence=0.99)
    result = service.run(request, run_id="run-escalate")
    assert result.outcome == TerminalOutcome.OPERATOR_REVIEW_REQUIRED
    assert result.operator_review_required is True
    _assert_well_formed(result)


def test_budget_exhausted_iterations():
    sq = Subquestion(subquestion_id="sq-1", text="granite quarry survey")
    planner = StaticPlanner(subquestions=[sq], initial_query_texts=["granite quarry survey"])
    weak_record = EvidenceRecord(
        record_id="r1",
        content="granite quarry survey faint mention",
        source_id="src",
        source_type="archival",
        source_reference="ref-r1",
        tier="III",
        authority=0.2,
        freshness=0.2,
        consistency=0.2,
        completeness=0.2,
        provenance_quality=0.2,
    )
    service = _service(planner, [weak_record])
    request = AgenticQueryRequest(question="a weakly evidenced question", mode="fast", max_iterations=1)
    result = service.run(request, run_id="run-budget-iter")
    assert result.outcome == TerminalOutcome.BUDGET_EXHAUSTED
    assert result.iterations_completed == 1
    assert "MAX_ITERATIONS_REACHED" in result.stop_reason
    _assert_well_formed(result)


def test_budget_exhausted_retrieval_calls():
    sq1 = Subquestion(subquestion_id="sq-1", text="granite quarry survey")
    sq2 = Subquestion(subquestion_id="sq-2", text="riverford crossing record")
    planner = StaticPlanner(
        subquestions=[sq1, sq2],
        initial_query_texts=["granite quarry survey", "riverford crossing record"],
    )
    records = [
        _good_record("r1", "granite quarry survey record"),
        _good_record("r2", "riverford crossing record entry", source_id="s2"),
    ]
    service = _service(planner, records)
    request = AgenticQueryRequest(
        question="two subquestions, one retrieval call budget",
        mode="deep",
        max_retrieval_calls=1,
        minimum_confidence=0.99,  # unreachable so success never short-circuits the budget check
    )
    result = service.run(request, run_id="run-budget-retrieval")
    assert result.retrieval_calls_used == 1
    assert result.outcome in (TerminalOutcome.BUDGET_EXHAUSTED, TerminalOutcome.PARTIAL_EVIDENCE)
    assert "RETRIEVAL_CALL_BUDGET_EXHAUSTED" in result.stop_reason
    _assert_well_formed(result)


def test_budget_exhausted_evidence_items():
    sq = Subquestion(subquestion_id="sq-1", text="granite quarry survey")
    planner = StaticPlanner(subquestions=[sq], initial_query_texts=["granite quarry survey"])
    records = [
        _good_record("r1", "granite quarry survey record one", source_id="s1"),
        _good_record("r2", "granite quarry survey record two", source_id="s2"),
        _good_record("r3", "granite quarry survey record three", source_id="s3"),
    ]
    service = _service(planner, records)
    request = AgenticQueryRequest(
        question="one subquestion, tiny evidence budget",
        mode="deep",
        max_evidence_items=1,
        minimum_confidence=0.99,
    )
    result = service.run(request, run_id="run-budget-evidence")
    assert result.outcome in (TerminalOutcome.BUDGET_EXHAUSTED, TerminalOutcome.PARTIAL_EVIDENCE)
    assert "EVIDENCE_ITEM_BUDGET_EXHAUSTED" in result.stop_reason
    _assert_well_formed(result)


def test_no_information_gain():
    sq = Subquestion(subquestion_id="sq-1", text="a topic with nothing in the corpus")
    planner = StaticPlanner(subquestions=[sq])
    service = _service(planner, records=[])
    request = AgenticQueryRequest(question="a topic with nothing in the corpus", mode="fast")
    result = service.run(request, run_id="run-no-gain")
    assert result.outcome == TerminalOutcome.NO_INFORMATION_GAIN
    _assert_well_formed(result)


def test_repeated_query():
    planner = RepeatPlanner("same query every time")
    records = [_good_record("r1", "same query every time content")]
    service = _service(planner, records)
    request = AgenticQueryRequest(question="repeated query scenario", mode="deep", minimum_confidence=0.99)
    result = service.run(request, run_id="run-repeated")
    assert result.outcome == TerminalOutcome.REPEATED_QUERY
    assert result.iterations_completed >= 2
    _assert_well_formed(result)


def test_policy_blocked():
    planner = StaticPlanner()
    service = _service(planner, records=[])
    request = AgenticQueryRequest(question="a proof-mode request", mode="proof", include_tiers=["II", "III"])
    result = service.run(request, run_id="run-policy")
    assert result.outcome == TerminalOutcome.POLICY_BLOCKED
    assert result.iterations_completed == 1
    _assert_well_formed(result)


def test_hard_ceiling_cannot_be_bypassed_by_caller():
    sq = Subquestion(subquestion_id="sq-1", text="granite quarry survey")
    planner = StaticPlanner(subquestions=[sq], initial_query_texts=["granite quarry survey"])
    records = [_good_record("r1", "granite quarry survey record")]
    service = _service(planner, records)
    request = AgenticQueryRequest(
        question="ceiling test question",
        mode="fast",
        max_iterations=999,
        minimum_confidence=0.99,
    )
    result = service.run(request, run_id="run-ceiling")
    assert result.iterations_completed <= 10  # HARD_CEILING_ITERATIONS
