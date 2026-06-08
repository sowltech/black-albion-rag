"""Deterministic, local-first grounded answer assembler.

This module never calls an external LLM. It synthesises a tier-labelled,
source-cited summary directly from the retrieved evidence so the API is
useful out-of-the-box. A real LLM step can be wired in later by replacing
``generate_answer`` with one that hands the prompts from
``prompt_builder.build_prompt`` to a chat model.
"""
from __future__ import annotations

from typing import Sequence

from .retriever import RetrievedEvidence


_TIER_LABEL = {
    "I": "Archival evidence",
    "II": "Scholarly interpretation",
    "III": "Speculative / mythic lens",
}


def generate_answer(question: str, evidence: Sequence[RetrievedEvidence]) -> str:
    if not evidence:
        return (
            f"No grounded evidence found for: {question}\n"
            "The local corpus needs more source-backed records before a cited "
            "answer is safe. See data/raw/ and the source-tier doctrine in README.md."
        )

    lines = [
        "EVIDENCE MODE:",
        "- Tier I: verified / source-backed evidence",
        "- Tier II: interpretation / analysis",
        "- Tier III: speculative / mythic / creative layer",
        "",
        f"Question: {question}",
        "",
    ]
    by_tier: dict[str, list[RetrievedEvidence]] = {"I": [], "II": [], "III": []}
    for item in evidence:
        by_tier.setdefault(item.tier, []).append(item)

    citation_index = 1
    citation_map: list[tuple[int, RetrievedEvidence]] = []
    for tier in ("I", "II", "III"):
        bucket = by_tier.get(tier) or []
        if not bucket:
            continue
        label = _TIER_LABEL.get(tier, f"Tier {tier}")
        lines.append(f"## {label}")
        for item in bucket:
            citation_map.append((citation_index, item))
            prefix = ""
            if tier == "II":
                prefix = "Scholars argue that "
            elif tier == "III":
                prefix = "Speculatively, "
            lines.append(f"- [{citation_index}] {prefix}{item.title}: {item.excerpt}")
            citation_index += 1
        lines.append("")

    lines.append("## Sources")
    for idx, item in citation_map:
        record_ref = f" (id={item.record_id})" if item.record_id else ""
        lines.append(f"- [{idx}] Tier {item.tier} — {item.source_file}{record_ref}")

    lines.append("")
    lines.append(
        "Note: This answer is constrained to the retrieved evidence above. "
        "Tier III content is interpretive, not historical fact."
    )
    return "\n".join(lines)
