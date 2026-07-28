"""Deterministic, non-generative synthesis.

Assembles a structured answer directly from evidence and gap state. It never
invents prose beyond what the subquestions and evidence already say, so it
runs correctly with no LLM present. A later, model-assisted synthesiser must
consume only this same governed evidence packet -- it does not get a wider
window onto raw ledgers than this one has.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from .gap_detector import group_evidence_by_subquestion
from .models import Contradiction, EvidenceItem, RetrievalQuery, Subquestion


@dataclass(frozen=True)
class SynthesisResult:
    answer: str
    supported_claims: List[str] = field(default_factory=list)
    qualified_claims: List[str] = field(default_factory=list)
    unsupported_claims: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)


def _open_contradiction_ids_for(
    evidence_ids: Sequence[str], contradictions: Sequence[Contradiction]
) -> List[str]:
    ids = set(evidence_ids)
    return [
        c.contradiction_id
        for c in contradictions
        if c.status in ("open", "partially_resolved")
        and ids & (set(c.supporting_evidence_ids) | set(c.opposing_evidence_ids))
    ]


def synthesise(
    question: str,
    subquestions: Sequence[Subquestion],
    evidence: Sequence[EvidenceItem],
    queries: Sequence[RetrievalQuery],
    contradictions: Sequence[Contradiction],
) -> SynthesisResult:
    grouped = group_evidence_by_subquestion(evidence, queries)

    supported: List[str] = []
    qualified: List[str] = []
    unsupported: List[str] = []

    for sq in subquestions:
        sq_evidence = grouped.get(sq.subquestion_id, [])
        if not sq_evidence:
            unsupported.append(f"{sq.text} [no evidence retrieved]")
            continue

        sq_evidence_ids = sorted({item.evidence_id for item in sq_evidence})
        blocking_contradictions = _open_contradiction_ids_for(sq_evidence_ids, contradictions)
        if blocking_contradictions:
            qualified.append(
                f"{sq.text} [contradicted; see {', '.join(blocking_contradictions)}]"
            )
            continue

        tier_i_or_ii = [item for item in sq_evidence if item.tier in ("I", "II")]
        if tier_i_or_ii:
            supported.append(f"{sq.text} [supported by {', '.join(sq_evidence_ids)}]")
        else:
            qualified.append(
                f"{sq.text} [only Tier III speculative evidence available: "
                f"{', '.join(sq_evidence_ids)}]"
            )

    lines: List[str] = [f"Question: {question}"]
    if supported:
        lines.append("Supported claims:")
        lines.extend(f"- {claim}" for claim in supported)
    if qualified:
        lines.append("Qualified claims (weak, speculative, or contradicted evidence):")
        lines.extend(f"- {claim}" for claim in qualified)
    if unsupported:
        lines.append("Unsupported or unanswered:")
        lines.extend(f"- {claim}" for claim in unsupported)
    if not supported and not qualified and not unsupported:
        lines.append("No subquestions were decomposed for this question.")

    return SynthesisResult(
        answer="\n".join(lines),
        supported_claims=supported,
        qualified_claims=qualified,
        unsupported_claims=unsupported,
        evidence_ids=sorted({item.evidence_id for item in evidence}),
    )
