"""FastAPI entrypoint for the local Black Albion RAG service.

Endpoints:
    GET  /health  -> service status + document count
    GET  /dashboard -> read-only operator dashboard
    POST /query   -> grounded, tier-aware retrieval + answer

Local-first: reads only ``data/raw/*.json`` from the repo (overridable via
``BLACK_ALBION_DATA_DIR``). No network calls, no paid APIs.
"""
from __future__ import annotations

from html import escape
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

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

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard(q: Optional[str] = None) -> str:
        modules_payload = retriever.modules()
        sites_payload = retriever.sites()
        claims_payload = retriever.claims()
        search_query = (q or "").strip()
        search_results = (
            retriever.search(search_query, k=10)
            if search_query
            else []
        )
        health_payload = {
            "service": "black-albion-rag",
            "status": "ok",
            "documents": len(retriever.documents),
        }
        links = [
            ("/health", "Health"),
            ("/modules", "Modules"),
            ("/sites", "Sites"),
            ("/claims", "Claims"),
            ("/map/layers", "Map Layers"),
            ("/openapi.json", "OpenAPI JSON"),
            ("/docs", "Swagger Docs"),
        ]
        link_items = "\n".join(
            f'<li><a href="{escape(href)}">{escape(label)}</a></li>'
            for href, label in links
        )
        status = escape(str(health_payload["status"]))
        service = escape(str(health_payload["service"]))
        documents = escape(str(health_payload["documents"]))
        data_dir = escape(os.pathsep.join(str(d) for d in data_dirs))
        escaped_query = escape(search_query, quote=True)
        if search_query:
            if search_results:
                result_items = "\n".join(
                    "<li>"
                    f"<strong>{escape(item.title)}</strong> "
                    f"<span>({escape(item.tier)})</span>"
                    f"<p>{escape(item.excerpt)}</p>"
                    "</li>"
                    for item in search_results
                )
                search_section = f"""
      <section class="panel">
        <h2>Search Results</h2>
        <p>Query: <strong>{escaped_query}</strong></p>
        <p>Result count: <strong>{len(search_results)}</strong></p>
        <ol class="results">
          {result_items}
        </ol>
      </section>"""
            else:
                search_section = f"""
      <section class="panel">
        <h2>Search Results</h2>
        <p>Query: <strong>{escaped_query}</strong></p>
        <p>No results found.</p>
      </section>"""
        else:
            search_section = """
      <section class="panel">
        <h2>Search</h2>
        <p>Enter a search term to query sites, claims, and modules.</p>
      </section>"""
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BLACK ALBION RAG — Operator Dashboard</title>
  <style>
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f6f4ef;
      color: #1f2933;
    }}
    main {{
      max-width: 1040px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 30px;
    }}
    .subtitle {{
      margin: 0 0 28px;
      color: #52606d;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin-bottom: 24px;
    }}
    .panel {{
      background: #ffffff;
      border: 1px solid #d9e2ec;
      border-radius: 8px;
      padding: 18px;
    }}
    .metric {{
      font-size: 32px;
      font-weight: 700;
    }}
    .label {{
      color: #52606d;
      font-size: 14px;
    }}
    .ok {{
      color: #146c43;
      font-weight: 700;
    }}
    ul {{
      margin: 10px 0 0;
      padding-left: 20px;
    }}
    a {{
      color: #1d4ed8;
    }}
    form {{
      display: flex;
      gap: 10px;
      margin: 18px 0 24px;
    }}
    input[type="search"] {{
      flex: 1;
      min-width: 0;
      padding: 10px 12px;
      border: 1px solid #bcccdc;
      border-radius: 6px;
      font: inherit;
    }}
    button {{
      padding: 10px 14px;
      border: 1px solid #1d4ed8;
      border-radius: 6px;
      background: #1d4ed8;
      color: #ffffff;
      font: inherit;
      cursor: pointer;
    }}
    .results li {{
      margin-bottom: 12px;
    }}
    .results p {{
      margin: 4px 0 0;
      color: #52606d;
    }}
  </style>
</head>
<body>
  <main>
    <h1>BLACK ALBION RAG — Operator Dashboard</h1>
    <p class="subtitle">Read-only runtime view for local evidence retrieval operations.</p>

    <form method="get" action="/dashboard" role="search">
      <input
        type="search"
        name="q"
        value="{escaped_query}"
        placeholder="Search sites, claims, modules..."
        aria-label="Search sites, claims, modules">
      <button type="submit">Search</button>
    </form>

    <section class="grid" aria-label="Runtime summary">
      <div class="panel">
        <div class="label">Health</div>
        <div class="metric ok">{status}</div>
        <p>{service}</p>
      </div>
      <div class="panel">
        <div class="label">Modules</div>
        <div class="metric">{len(modules_payload)}</div>
      </div>
      <div class="panel">
        <div class="label">Sites</div>
        <div class="metric">{len(sites_payload)}</div>
      </div>
      <div class="panel">
        <div class="label">Claims</div>
        <div class="metric">{len(claims_payload)}</div>
      </div>
    </section>

    <section class="grid" aria-label="Operator links">
      <div class="panel">
        <h2>API Links</h2>
        <ul>
          {link_items}
        </ul>
      </div>
      <div class="panel">
        <h2>Enterprise GPT OS</h2>
        <p>Status summary: manifest validator and eval runner are enforced by local validation and GitHub Actions.</p>
        <p>Validation wrapper: <code>bash scripts/validate_enterprise_gpt_os.sh</code></p>
      </div>
      <div class="panel">
        <h2>Release</h2>
        <p>Current dashboard milestone: <strong>v0.3.0-planned</strong></p>
        <p>Repo estate status: <code>REPO_ESTATE_AUDIT.md</code></p>
      </div>
      <div class="panel">
        <h2>Data</h2>
        <p>Documents indexed: <strong>{documents}</strong></p>
        <p>Data directory: <code>{data_dir}</code></p>
      </div>
    </section>

    {search_section}
  </main>
</body>
</html>"""

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
