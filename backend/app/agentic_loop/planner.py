"""Query planning: decomposition, retrieval-query generation, normalisation,
and repeated-query detection.

Phase 1 ships a deterministic, configuration-driven ``StaticPlanner`` rather
than a generative one. It is a legitimate implementation of the ``Planner``
protocol, not a stub -- it is what the loop kernel runs against in tests and
is what any future model-backed planner must remain a drop-in replacement
for.
"""
from __future__ import annotations

import re
import unicodedata
from hashlib import sha256
from typing import Dict, List, Protocol, Sequence, Set

from .models import Gap, RetrievalQuery, Subquestion

_WHITESPACE_RE = re.compile(r"\s+")
_NON_SEMANTIC_PUNCTUATION_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)


def normalise_query_text(text: str) -> str:
    """Deterministic normalisation used for repetition detection.

    Lowercases, applies Unicode NFKC normalisation, strips punctuation that
    carries no semantic weight for a lexical query, and collapses
    whitespace. Two queries that differ only by casing, punctuation, or
    incidental whitespace normalise to the same string.
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.lower().strip()
    text = _NON_SEMANTIC_PUNCTUATION_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def query_hash(text: str) -> str:
    """Stable hash of a query's normalised form."""
    normalised = normalise_query_text(text)
    return sha256(normalised.encode("utf-8")).hexdigest()


class QueryRepetitionTracker:
    """Tracks normalised query hashes seen across a run and reports
    exact/normalised repeats. Test-double retrievers reuse the same
    normalisation, so a repeat here reliably means a repeat there too."""

    def __init__(self) -> None:
        self._seen: Set[str] = set()

    def register(self, text: str) -> bool:
        """Returns True if ``text`` normalises to something already seen."""
        digest = query_hash(text)
        if digest in self._seen:
            return True
        self._seen.add(digest)
        return False

    def is_repeat(self, text: str) -> bool:
        return query_hash(text) in self._seen

    @property
    def seen_hashes(self) -> Set[str]:
        return set(self._seen)


class Planner(Protocol):
    """Decomposes a question and produces retrieval queries. Read-only:
    a planner never writes to any ledger and never calls a retriever
    itself -- it only describes what should be retrieved."""

    def decompose(self, question: str) -> List[Subquestion]:
        ...

    def next_queries(
        self,
        iteration: int,
        subquestions: Sequence[Subquestion],
        open_gaps: Sequence[Gap],
        exhausted_strategies: Set[str],
    ) -> List[RetrievalQuery]:
        ...


class StaticPlanner:
    """Deterministic planner test double.

    Decomposition is either caller-supplied (``subquestions``) or falls back
    to treating the whole question as a single subquestion. First-iteration
    queries come from ``initial_query_texts`` (defaulting to the
    subquestion text itself); later iterations refine each open gap into one
    targeted query so the loop has something new to try when it detects a
    coverage hole, without ever repeating a prior query's normalised text.
    """

    def __init__(
        self,
        subquestions: Sequence[Subquestion] | None = None,
        initial_query_texts: Sequence[str] | None = None,
    ) -> None:
        self._subquestions = list(subquestions) if subquestions else None
        self._initial_query_texts = list(initial_query_texts) if initial_query_texts else None
        self._query_counter = 0

    def decompose(self, question: str) -> List[Subquestion]:
        if self._subquestions is not None:
            return list(self._subquestions)
        return [
            Subquestion(subquestion_id="sq-1", text=question, priority=0, status="pending")
        ]

    def _next_query_id(self) -> str:
        self._query_counter += 1
        return f"q-{self._query_counter}"

    def next_queries(
        self,
        iteration: int,
        subquestions: Sequence[Subquestion],
        open_gaps: Sequence[Gap],
        exhausted_strategies: Set[str],
    ) -> List[RetrievalQuery]:
        queries: List[RetrievalQuery] = []
        if iteration == 1:
            texts_by_subquestion: Dict[str, str] = {}
            if self._initial_query_texts:
                for sq, text in zip(subquestions, self._initial_query_texts):
                    texts_by_subquestion[sq.subquestion_id] = text
            for sq in subquestions:
                text = texts_by_subquestion.get(sq.subquestion_id, sq.text)
                queries.append(
                    RetrievalQuery(
                        query_id=self._next_query_id(),
                        iteration=iteration,
                        text=text,
                        strategy="lexical",
                        target_sources=[],
                        parent_subquestion_ids=[sq.subquestion_id],
                        normalised_hash=query_hash(text),
                    )
                )
            return queries

        if "refinement" in exhausted_strategies:
            return []
        for gap in open_gaps:
            if gap.status != "open":
                continue
            text = f"{gap.description}".strip()
            if not text:
                continue
            queries.append(
                RetrievalQuery(
                    query_id=self._next_query_id(),
                    iteration=iteration,
                    text=text,
                    strategy="refinement",
                    target_sources=[],
                    parent_subquestion_ids=[gap.subquestion_id],
                    normalised_hash=query_hash(text),
                )
            )
        return queries
