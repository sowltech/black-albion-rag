"""FastAPI entrypoint for the local Black Albion RAG service.

Endpoints:
    GET  /health  -> service status + document count
    POST /query   -> grounded, tier-aware retrieval + answer

Local-first: reads only ``data/raw/*.json`` from the repo (overridable via
``BLACK_ALBION_DATA_DIR``). No network calls, no paid APIs.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

from fastapi import FastAPI

from .answer_generator import generate_answer
from .models import (
    EvidenceItem,
    HealthResponse,
    QueryRequest,
    QueryResponse,
    TierBreakdown,
)
from .prompt_builder import build_prompt
from .retriever import BlackAlbionRetriever


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO_ROOT / "data" / "raw"
DEFAULT_INDEX_DIR = REPO_ROOT / "data" / "index"


def _resolve_data_dirs() -> List[Path]:
    """Return one or more data directories to load JSON ledgers from."""
    override = os.getenv("BLACK_ALBION_DATA_DIR")
    if not override:
        return [DEFAULT_DATA_DIR]
    dirs: List[Path] = []
    for piece in override.split(os.pathsep):
        piece = piece.strip()
        if not piece:
            continue
        path = Path(piece)
        if not path.is_absolute():
            path = REPO_ROOT / piece
        dirs.append(path)
    return dirs or [DEFAULT_DATA_DIR]


def create_app() -> FastAPI:
    data_dirs = _resolve_data_dirs()
    cache_path = DEFAULT_INDEX_DIR / ".retriever_cache.pkl"
    retriever = BlackAlbionRetriever(data_dirs=data_dirs, cache_path=cache_path)

    app = FastAPI(
        title="Black Albion RAG",
        version="0.1.0",
        description=(
            "Local-first, source-tier-aware retrieval API for the Black Albion "
            "evidence corpus. Tier I = archival, Tier II = scholarly, "
            "Tier III = speculative."
        ),
    )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            service="black-albion-rag",
            status="ok",
            documents=len(retriever.documents),
            data_dir=os.pathsep.join(str(d) for d in data_dirs),
            cache_path=str(cache_path),
        )

    @app.post("/query", response_model=QueryResponse)
    def query(payload: QueryRequest) -> QueryResponse:
        evidence = retriever.search(
            payload.question,
            k=payload.k,
            include_tiers=payload.include_tiers,
        )
        prompts = build_prompt(payload.question, evidence)
        answer = (
            generate_answer(payload.question, evidence)
            if payload.generate_answer
            else ""
        )

        breakdown = TierBreakdown(
            tier_i=sum(1 for e in evidence if e.tier == "I"),
            tier_ii=sum(1 for e in evidence if e.tier == "II"),
            tier_iii=sum(1 for e in evidence if e.tier == "III"),
        )

        return QueryResponse(
            question=payload.question,
            document_count=len(retriever.documents),
            evidence_count=len(evidence),
            tier_breakdown=breakdown,
            evidence=[
                EvidenceItem(
                    source_file=item.source_file,
                    record_id=item.record_id,
                    title=item.title,
                    tier=item.tier,  # type: ignore[arg-type]
                    score=item.score,
                    excerpt=item.excerpt,
                    metadata=item.metadata,
                )
                for item in evidence
            ],
            prompts=prompts,
            answer=answer,
        )

    return app


app = create_app()
