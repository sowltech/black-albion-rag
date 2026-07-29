"""Evidence scoring and deduplication.

This is the single authoritative place that turns an evidence item's
decomposed component scores into ``overall_score``. Nothing else in the
package computes it, so there is exactly one formula to audit.
"""
from __future__ import annotations

from typing import List, Tuple

from .models import EvidenceItem
from .policy import EVIDENCE_SCORE_WEIGHTS


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def score_evidence(item: EvidenceItem) -> EvidenceItem:
    """Return a copy of ``item`` with ``overall_score`` recomputed from its
    decomposed components using ``EVIDENCE_SCORE_WEIGHTS``. Only
    ``overall_score`` changes -- the item's declared ``tier`` is never
    touched here. A high score never overrides tier policy: Tier III
    material stays Tier III however high its overall score comes out."""
    components = {name: getattr(item, name) for name in EVIDENCE_SCORE_WEIGHTS}
    overall = sum(value * EVIDENCE_SCORE_WEIGHTS[name] for name, value in components.items())
    return item.model_copy(update={"overall_score": _clamp_unit(overall)})


def score_batch(items: List[EvidenceItem]) -> List[EvidenceItem]:
    return [score_evidence(item) for item in items]


def deduplicate(items: List[EvidenceItem]) -> Tuple[List[EvidenceItem], List[EvidenceItem]]:
    """Split ``items`` into (unique, duplicates).

    Two items are the same evidence if they share an ``evidence_id``, or if
    they share both ``source_id`` and ``content_hash`` (the same source
    handed back the same content under a different id). Independent
    corroboration -- identical content reached through a *different*
    source -- is preserved as two distinct unique items on purpose: source
    diversity is a signal the governor and gain calculation depend on, and
    collapsing corroborating sources into one would destroy it.
    """
    unique: List[EvidenceItem] = []
    duplicates: List[EvidenceItem] = []
    seen_ids: set[str] = set()
    seen_source_content: set[Tuple[str, str]] = set()

    for item in items:
        source_content_key = (item.source_id, item.content_hash)
        if item.evidence_id in seen_ids or source_content_key in seen_source_content:
            duplicates.append(item)
            continue
        seen_ids.add(item.evidence_id)
        seen_source_content.add(source_content_key)
        unique.append(item)

    return unique, duplicates
