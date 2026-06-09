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
import json
import os
from pathlib import Path
import re
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
CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"
REPO_ESTATE_AUDIT_PATH = REPO_ROOT / "REPO_ESTATE_AUDIT.md"
CANDIDATE_CLAIMS_PATH = DEFAULT_DATA_DIR / "black_albion_candidate_claims.json"
CLAIMS_PATH = DEFAULT_DATA_DIR / "black_albion_claims.json"
SOURCES_PATH = DEFAULT_DATA_DIR / "black_albion_sources.json"
MODULE_EXPANSION_DOC_PATH = REPO_ROOT / "docs" / "black-albion-module-expansion.md"
INTAKE_REVIEW_WORKFLOW_PATH = REPO_ROOT / "docs" / "intake-review-workflow.md"
RESEARCH_INTAKE_DIR = REPO_ROOT / "research" / "intake"
RESEARCH_REVIEW_QUEUE_DIR = REPO_ROOT / "research" / "review_queue"
RESEARCH_REVIEWED_DIR = REPO_ROOT / "research" / "reviewed"
RESEARCH_REJECTED_DIR = REPO_ROOT / "research" / "rejected"


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


def _latest_release_metadata() -> Dict[str, str]:
    """Return the latest local release metadata from CHANGELOG.md."""
    fallback = {
        "title": "v0.3.0-planned",
        "date": "unreleased",
        "source": "dashboard fallback",
    }
    if not CHANGELOG_PATH.exists():
        return fallback

    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    heading = re.search(r"^##\s+(.+)$", text, flags=re.MULTILINE)
    if not heading:
        return fallback

    release_block = text[heading.end():]
    next_heading = re.search(r"^##\s+", release_block, flags=re.MULTILINE)
    if next_heading:
        release_block = release_block[:next_heading.start()]

    date_match = re.search(r"^Release date:\s*(.+)$", release_block, flags=re.MULTILINE)
    return {
        "title": heading.group(1).strip(),
        "date": date_match.group(1).strip() if date_match else "unknown",
        "source": "CHANGELOG.md",
    }


def _repo_estate_summary() -> Dict[str, Any]:
    """Return repo estate summary values from REPO_ESTATE_AUDIT.md."""
    fallback: Dict[str, Any] = {
        "counts": {
            "Total repos found": "46",
            "COMPLETE / WORKING": "1",
            "MOSTLY WORKING": "19",
            "PARTIAL": "21",
            "STALE": "1",
            "BROKEN / NEEDS ATTENTION": "3",
            "UNKNOWN": "1",
        },
        "gold_standard": "black-albion-rag",
        "strongest": [
            "black-albion-rag",
            "sowltech-shinobi-orca",
            "loopguard-engine",
            "assetsourced",
            "gcde-repo-v1",
        ],
        "attention": [
            "OMNI-CORE",
            "stepc-purchasegate",
            "phoenix-voice-agent-engine.archived-2026-05-17",
            "Sirius Nexus vault",
            "claude-skills",
        ],
        "source": "dashboard fallback",
    }
    if not REPO_ESTATE_AUDIT_PATH.exists():
        return fallback

    text = REPO_ESTATE_AUDIT_PATH.read_text(encoding="utf-8")
    counts = dict(fallback["counts"])
    for key in counts:
        match = re.search(rf"^- {re.escape(key)}:\s*(.+)$", text, flags=re.MULTILINE)
        if match:
            counts[key] = match.group(1).strip()

    def section_items(section: str) -> List[str]:
        heading = re.search(rf"^## {re.escape(section)}$", text, flags=re.MULTILINE)
        if not heading:
            return []
        block = text[heading.end():]
        next_heading = re.search(r"^##\s+", block, flags=re.MULTILINE)
        if next_heading:
            block = block[:next_heading.start()]
        return [
            match.group(1).strip()
            for match in re.finditer(r"^\d+\.\s+`([^`]+)`", block, flags=re.MULTILINE)
        ][:5]

    strongest = section_items("Top 5 Strongest Repos") or fallback["strongest"]
    attention = section_items("Top 5 Repos Needing Attention") or fallback["attention"]
    return {
        "counts": counts,
        "gold_standard": "black-albion-rag",
        "strongest": strongest,
        "attention": attention,
        "source": "REPO_ESTATE_AUDIT.md",
    }


def _repo_relative(path: Path) -> str:
    """Return a stable repo-relative display path."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _visible_files(path: Path) -> List[str]:
    """Return visible file paths from a local folder without mutating it."""
    if not path.exists() or not path.is_dir():
        return []
    return sorted(
        _repo_relative(item)
        for item in path.iterdir()
        if item.is_file() and not item.name.startswith(".")
    )


def _json_array_count(path: Path) -> str:
    """Return a safe count for a JSON array ledger."""
    if not path.exists():
        return "not detected"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "manual review required"
    if not isinstance(payload, list):
        return "manual review required"
    return str(len(payload))


def _source_intake_summary() -> Dict[str, Any]:
    """Return a read-only source/intake review summary for the dashboard."""
    quarantine_files = _visible_files(RESEARCH_INTAKE_DIR)
    review_queue_files = _visible_files(RESEARCH_REVIEW_QUEUE_DIR)
    reviewed_files = _visible_files(RESEARCH_REVIEWED_DIR)
    rejected_files = _visible_files(RESEARCH_REJECTED_DIR)
    claims_sources = [
        _repo_relative(path)
        for path in (CLAIMS_PATH, SOURCES_PATH, CANDIDATE_CLAIMS_PATH)
        if path.exists()
    ]
    tier_one_files = [
        _repo_relative(path)
        for path in (SOURCES_PATH, MODULE_EXPANSION_DOC_PATH)
        if path.exists()
    ]
    total_items = _json_array_count(CANDIDATE_CLAIMS_PATH)
    review_status = (
        "Candidate ledger present; Gemini Share 002 remains quarantined; "
        "live claims/modules/sources require independent Tier I sources before promotion."
        if CANDIDATE_CLAIMS_PATH.exists()
        else "Candidate ledger not detected; manual review required."
    )
    return {
        "intake_queue_path": _repo_relative(CANDIDATE_CLAIMS_PATH),
        "total_items": total_items,
        "quarantine_files": quarantine_files,
        "review_queue_count": len(review_queue_files),
        "reviewed_count": len(reviewed_files),
        "rejected_count": len(rejected_files),
        "tier_one_files": tier_one_files,
        "claims_sources": claims_sources,
        "latest_intake_commit": "0442d86 feat: add black albion intake review queue",
        "review_status": review_status,
        "workflow_doc": (
            _repo_relative(INTAKE_REVIEW_WORKFLOW_PATH)
            if INTAKE_REVIEW_WORKFLOW_PATH.exists()
            else "not detected"
        ),
        "next_action": (
            "Review quarantined intake manually, split any candidate material into "
            "item-level statements, and source independently before promotion."
        ),
        "read_only_note": "read-only status panel; no intake files are modified.",
    }


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

    def _run_query(payload: QueryRequest) -> QueryResponse:
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
    def dashboard(
        q: Optional[str] = None,
        query: Optional[str] = None,
        question: Optional[str] = None,
    ) -> str:
        modules_payload = retriever.modules()
        sites_payload = retriever.sites()
        claims_payload = retriever.claims()
        search_query = (q or "").strip()
        search_results = (
            retriever.search(search_query, k=10)
            if search_query
            else []
        )
        dashboard_question = (query or question or "").strip()
        query_result = (
            _run_query(QueryRequest(question=dashboard_question))
            if len(dashboard_question) >= 3
            else None
        )
        health_payload = {
            "service": "black-albion-rag",
            "status": "ok",
            "documents": len(retriever.documents),
        }
        release_metadata = _latest_release_metadata()
        repo_estate = _repo_estate_summary()
        source_intake = _source_intake_summary()
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
        release_title = escape(release_metadata["title"])
        release_date = escape(release_metadata["date"])
        release_source = escape(release_metadata["source"])
        repo_estate_counts = repo_estate["counts"]
        repo_estate_rows = "\n".join(
            f"<li>{escape(label)}: <strong>{escape(str(value))}</strong></li>"
            for label, value in repo_estate_counts.items()
        )
        strongest_repos = "\n".join(
            f"<li>{escape(repo)}</li>" for repo in repo_estate["strongest"]
        )
        attention_repos = "\n".join(
            f"<li>{escape(repo)}</li>" for repo in repo_estate["attention"]
        )
        gold_standard_repo = escape(str(repo_estate["gold_standard"]))
        repo_estate_source = escape(str(repo_estate["source"]))
        quarantine_items = "\n".join(
            f"<li>{escape(item)}</li>" for item in source_intake["quarantine_files"]
        ) or "<li>not detected</li>"
        tier_one_source_items = "\n".join(
            f"<li>{escape(item)}</li>" for item in source_intake["tier_one_files"]
        ) or "<li>not detected</li>"
        claims_source_items = "\n".join(
            f"<li>{escape(item)}</li>" for item in source_intake["claims_sources"]
        ) or "<li>not detected</li>"
        intake_queue_path = escape(str(source_intake["intake_queue_path"]))
        intake_total_items = escape(str(source_intake["total_items"]))
        review_queue_count = escape(str(source_intake["review_queue_count"]))
        reviewed_count = escape(str(source_intake["reviewed_count"]))
        rejected_count = escape(str(source_intake["rejected_count"]))
        latest_intake_commit = escape(str(source_intake["latest_intake_commit"]))
        review_status = escape(str(source_intake["review_status"]))
        next_review_action = escape(str(source_intake["next_action"]))
        workflow_doc = escape(str(source_intake["workflow_doc"]))
        read_only_note = escape(str(source_intake["read_only_note"]))
        escaped_query = escape(search_query, quote=True)
        escaped_question = escape(dashboard_question, quote=True)
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
        if dashboard_question:
            if query_result and query_result.answer:
                source_items = "\n".join(
                    "<li>"
                    f"<strong>{escape(item.title)}</strong> "
                    f"<span>({escape(item.tier)})</span>"
                    f"<p>{escape(item.excerpt)}</p>"
                    "</li>"
                    for item in query_result.evidence[:5]
                )
                sources_html = (
                    f"""
        <h3>Supporting Matches</h3>
        <ol class="results">
          {source_items}
        </ol>"""
                    if source_items
                    else "<p>No supporting matches returned.</p>"
                )
                query_section = f"""
      <section class="panel">
        <h2>Query Result</h2>
        <p>Question: <strong>{escaped_question}</strong></p>
        <p>{escape(query_result.answer)}</p>
        <p>Supporting matches: <strong>{query_result.evidence_count}</strong></p>
        {sources_html}
      </section>"""
            else:
                query_section = f"""
      <section class="panel">
        <h2>Query Result</h2>
        <p>Question: <strong>{escaped_question}</strong></p>
        <p>No answer generated.</p>
      </section>"""
        else:
            query_section = """
      <section class="panel">
        <h2>Ask</h2>
        <p>Submit a question to run the existing read-only query workflow.</p>
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

    <form method="get" action="/dashboard">
      <input
        type="search"
        name="query"
        value="{escaped_question}"
        placeholder="Ask Black Albion RAG..."
        aria-label="Ask Black Albion RAG">
      <button type="submit">Ask</button>
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
        <p>Latest release: <strong>{release_title}</strong></p>
        <p>Release date: <strong>{release_date}</strong></p>
        <p>Release source: <code>{release_source}</code></p>
        <p>Current dashboard milestone: <strong>v0.3.0-planned</strong></p>
        <p>Repo estate status: <code>REPO_ESTATE_AUDIT.md</code></p>
      </div>
      <div class="panel">
        <h2>Data</h2>
        <p>Documents indexed: <strong>{documents}</strong></p>
        <p>Data directory: <code>{data_dir}</code></p>
      </div>
      <div class="panel">
        <h2>Repo Estate</h2>
        <p>Gold standard repo: <strong>{gold_standard_repo}</strong></p>
        <ul>
          {repo_estate_rows}
        </ul>
        <h3>Top 5 Strongest</h3>
        <ol>
          {strongest_repos}
        </ol>
        <h3>Top 5 Needing Attention</h3>
        <ol>
          {attention_repos}
        </ol>
        <p>Source: <code>{repo_estate_source}</code></p>
      </div>
      <div class="panel">
        <h2>Source / Intake Review</h2>
        <p><strong>{read_only_note}</strong></p>
        <p>Intake Queue: <code>{intake_queue_path}</code></p>
        <p>Total intake/review items: <strong>{intake_total_items}</strong></p>
        <p>Review queue: <strong>{review_queue_count}</strong> pending, <strong>{reviewed_count}</strong> reviewed, <strong>{rejected_count}</strong> rejected.</p>
        <h3>Quarantine</h3>
        <ul>
          {quarantine_items}
        </ul>
        <h3>Tier One Sources</h3>
        <ul>
          {tier_one_source_items}
        </ul>
        <h3>Claims / Sources</h3>
        <ul>
          {claims_source_items}
        </ul>
        <p>Latest Intake Commit: <code>{latest_intake_commit}</code></p>
        <p>Review status summary: {review_status}</p>
        <p>Workflow: <code>{workflow_doc}</code></p>
        <p>Next Review Action: {next_review_action}</p>
      </div>
    </section>

    {search_section}
    {query_section}
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
        return _run_query(payload)

    return app


app = create_app()
