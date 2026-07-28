"""Retrieval interface for the agentic loop.

The ``Retriever`` protocol is deliberately narrow: one read-only method to
execute a query and return evidence, one method to expose what source types
exist. There is no write method anywhere on this interface -- a retriever
structurally cannot mutate a ledger through it. Phase 2 adds a read-only
adapter over the real Black Albion ledgers behind this same protocol; Phase 1
ships only the deterministic in-memory double below.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Dict, List, Optional, Protocol, Sequence, Set

from .models import EvidenceItem, RetrievalQuery, SourceTier

_WORD_RE = re.compile(r"[A-Za-z0-9']+")


def _tokens(text: str) -> Set[str]:
    return {token.lower() for token in _WORD_RE.findall(text)}


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def content_hash(content: str) -> str:
    return sha256(content.strip().lower().encode("utf-8")).hexdigest()


class Retriever(Protocol):
    def retrieve(self, query: RetrievalQuery) -> List[EvidenceItem]:
        ...

    def available_source_types(self) -> Set[str]:
        ...


@dataclass(frozen=True)
class EvidenceRecord:
    """A fixed, deterministic evidence fixture consumed by
    ``InMemoryRetriever``. Score components other than relevance are fixed
    at fixture-authoring time -- Phase 1 does not compute authority,
    freshness, consistency, completeness, or provenance quality from real
    signals; that belongs to the ledger adapter in a later phase."""

    record_id: str
    content: str
    source_id: str
    source_type: str
    source_reference: str
    tier: SourceTier
    authority: float = 0.5
    freshness: float = 0.5
    consistency: float = 0.5
    completeness: float = 0.5
    provenance_quality: float = 0.5
    supports_claims: List[str] = field(default_factory=list)
    opposes_claims: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    keywords: Optional[Set[str]] = None


class InMemoryRetriever:
    """Deterministic, in-process, network-free retriever test double.

    Same query text always returns the same evidence in the same order for
    the same fixture set -- required so Phase 1 tests do not flake and so
    the loop can run entirely offline.
    """

    def __init__(self, records: Sequence[EvidenceRecord]) -> None:
        self._records = list(records)

    def retrieve(self, query: RetrievalQuery) -> List[EvidenceItem]:
        query_tokens = _tokens(query.text)
        if not query_tokens:
            return []

        results: List[EvidenceItem] = []
        for record in self._records:
            record_tokens = record.keywords if record.keywords is not None else _tokens(record.content)
            overlap = len(query_tokens & record_tokens)
            if overlap == 0:
                continue
            relevance = _clamp_unit(overlap / max(len(query_tokens), 1))
            results.append(
                EvidenceItem(
                    evidence_id=f"ev-{record.record_id}",
                    content=record.content,
                    source_id=record.source_id,
                    source_type=record.source_type,
                    source_reference=record.source_reference,
                    tier=record.tier,
                    retrieval_query_id=query.query_id,
                    relevance=relevance,
                    authority=record.authority,
                    freshness=record.freshness,
                    consistency=record.consistency,
                    completeness=record.completeness,
                    provenance_quality=record.provenance_quality,
                    # Overall score is intentionally left at 0.0 here: the
                    # scorer stage (scorer.py) is the single authoritative
                    # place that turns decomposed components into a combined
                    # score, per the documented evidence-scoring weights.
                    overall_score=0.0,
                    supports_claims=list(record.supports_claims),
                    opposes_claims=list(record.opposes_claims),
                    metadata=dict(record.metadata),
                    content_hash=content_hash(record.content),
                )
            )

        results.sort(key=lambda item: item.relevance, reverse=True)
        return results

    def available_source_types(self) -> Set[str]:
        return {record.source_type for record in self._records}
