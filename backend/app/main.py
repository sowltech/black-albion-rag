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
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Query

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

    @app.get("/modules")
    def modules() -> List[Dict[str, Any]]:
        return retriever.modules()

    @app.get("/modules/{module_id}")
    def module(module_id: str) -> Dict[str, Any]:
        for item in retriever.modules():
            if item.get("module_id") == module_id:
                return item
        return {"module_id": module_id, "status": "not_found"}

    @app.get("/sites")
    def sites() -> List[Dict[str, Any]]:
        return retriever.sites()

    @app.get("/search")
    def search(
        q: str = Query(..., min_length=1),
        module_id: Optional[str] = None,
        site_id: Optional[str] = None,
        county: Optional[str] = None,
        nearest_place: Optional[str] = None,
        period: Optional[str] = None,
        tier: Optional[str] = None,
        theme: Optional[str] = None,
        geology: Optional[str] = None,
        hydrology: Optional[str] = None,
        route: Optional[str] = None,
        place: Optional[str] = None,
        k: int = Query(default=10, ge=1, le=50),
    ) -> Dict[str, Any]:
        include_tiers = [tier] if tier else None
        filters = {
            "module_id": module_id,
            "site_id": site_id,
            "county": county,
            "nearest_place": nearest_place,
            "period": period,
            "theme": theme,
            "geology": geology,
            "hydrology": hydrology,
            "route": route,
            "place": place,
        }
        evidence = retriever.search(q, k=k, include_tiers=include_tiers, filters=filters)
        return {
            "query": q,
            "count": len(evidence),
            "results": [
                {
                    "source_file": item.source_file,
                    "record_id": item.record_id,
                    "title": item.title,
                    "tier": item.tier,
                    "score": item.score,
                    "excerpt": item.excerpt,
                    "metadata": item.metadata,
                }
                for item in evidence
            ],
        }

    @app.get("/claims")
    def claims(module_id: Optional[str] = None, tier: Optional[str] = None) -> List[Dict[str, Any]]:
        return retriever.claims(module_id=module_id, tier=tier)

    @app.get("/map/layers")
    def map_layers() -> Dict[str, Any]:
        modules_payload = retriever.modules()
        return {
            "layers": {
                "geology": [
                    {
                        "module_id": item.get("module_id"),
                        "name": item.get("name"),
                        "layer_0_geology": item.get("layer_0_geology"),
                    }
                    for item in modules_payload
                ],
                "tier_i_evidence": [
                    {
                        "module_id": item.get("module_id"),
                        "name": item.get("name"),
                        "tier_i_evidence": item.get("tier_i_evidence"),
                    }
                    for item in modules_payload
                ],
                "tier_ii_interpretation": [
                    {
                        "module_id": item.get("module_id"),
                        "name": item.get("name"),
                        "tier_ii_interpretation": item.get("tier_ii_interpretation"),
                    }
                    for item in modules_payload
                ],
                "tier_iii_speculative_logic": [
                    {
                        "module_id": item.get("module_id"),
                        "name": item.get("name"),
                        "tier_iii_speculative_logic": item.get("tier_iii_speculative_logic"),
                    }
                    for item in modules_payload
                ],
            }
        }

    @app.get("/export/modules.json")
    def export_modules() -> List[Dict[str, Any]]:
        return retriever.modules()

    @app.get("/export/claims.json")
    def export_claims() -> List[Dict[str, Any]]:
        return retriever.claims()

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
