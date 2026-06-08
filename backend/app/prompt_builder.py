"""Prompt builder for grounded, tier-aware answers."""
from __future__ import annotations

from typing import Dict, Sequence

from .retriever import RetrievedEvidence


SYSTEM_PROMPT = (
    "You are the Black Albion Research Agent.\n"
    "\n"
    "Doctrine:\n"
    "  Tier I  = archival / hard historical evidence (treat as load-bearing fact).\n"
    "  Tier II = scholarly interpretation (clearly attribute to scholars).\n"
    "  Tier III = speculative / mythic / interpretive lens "
    "(label explicitly as speculative; never present as historical fact).\n"
    "\n"
    "Rules:\n"
    "  1. Only use the EVIDENCE block below. If evidence is thin, say so plainly.\n"
    "  2. Cite every factual claim with a bracketed evidence number, e.g. [2].\n"
    "  3. When you cite Tier III evidence, prefix the sentence with 'Speculatively,' "
    "or 'In the Bobby Hemmit framework,' or an equivalent caveat.\n"
    "  4. Never invent dates, place names, archival records, or coordinates "
    "that are not in the evidence."
)


def build_prompt(question: str, evidence: Sequence[RetrievedEvidence]) -> Dict[str, str]:
    """Return ``{"system_prompt": ..., "user_prompt": ...}``.

    The user prompt embeds each retrieved record with its tier tag so a
    downstream LLM has the source-tier signal even if the agent loses the
    metadata envelope.
    """
    lines = []
    for idx, item in enumerate(evidence, start=1):
        lines.append(
            f"[{idx}] (Tier {item.tier}) {item.title} — {item.source_file}\n"
            f"    {item.excerpt}"
        )

    evidence_block = "\n\n".join(lines) if lines else "(no grounded evidence retrieved)"
    user_prompt = (
        f"Question: {question}\n\n"
        "EVIDENCE:\n"
        f"{evidence_block}\n\n"
        "Respond with a concise, cited answer that respects the tier doctrine above."
    )
    return {"system_prompt": SYSTEM_PROMPT, "user_prompt": user_prompt}
