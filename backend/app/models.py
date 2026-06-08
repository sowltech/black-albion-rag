"""Pydantic request/response models for the Black Albion RAG API."""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


SourceTier = Literal["I", "II", "III"]


class QueryRequest(BaseModel):
    """A user query against the local Black Albion evidence corpus."""

    question: str = Field(min_length=3, description="Natural-language research question.")
    k: int = Field(default=5, ge=1, le=20, description="Number of evidence records to retrieve.")
    include_tiers: List[SourceTier] = Field(
        default_factory=lambda: ["I", "II", "III"],
        description=(
            "Which source tiers to include. I = archival evidence, II = scholarly "
            "interpretation, III = speculative / mythic interpretation."
        ),
    )
    generate_answer: bool = Field(
        default=True,
        description="If true, return a grounded summary; if false, return evidence only.",
    )


class EvidenceItem(BaseModel):
    """A single retrieved evidence record."""

    source_file: str
    record_id: Optional[str] = None
    title: str
    tier: SourceTier
    score: float
    excerpt: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TierBreakdown(BaseModel):
    """Per-tier counts attached to a query response."""

    tier_i: int = 0
    tier_ii: int = 0
    tier_iii: int = 0


class QueryResponse(BaseModel):
    """Result envelope for POST /query."""

    question: str
    document_count: int
    evidence_count: int
    tier_breakdown: TierBreakdown
    evidence: List[EvidenceItem]
    prompts: Dict[str, str]
    answer: str
    disclaimer: str = (
        "Answers are grounded in the local corpus only. Tier III material is "
        "speculative / interpretive and must not be presented as established fact."
    )


class HealthResponse(BaseModel):
    """Result envelope for GET /health."""

    service: str
    status: str
    documents: int
    data_dir: str
    cache_path: str
