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
ENTERPRISE_GPT_OS_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "enterprise-gpt-os.yml"
LIVE_UVICORN_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "smoke-live-uvicorn.yml"
ENTERPRISE_GPT_OS_WRAPPER_PATH = REPO_ROOT / "scripts" / "validate_enterprise_gpt_os.sh"
LIVE_SMOKE_SCRIPT_PATH = REPO_ROOT / "scripts" / "smoke_live_uvicorn.sh"
MANIFEST_VALIDATOR_PATH = REPO_ROOT / "enterprise-gpt-os" / "scripts" / "validate_manifest.py"
EVAL_RUNNER_PATH = REPO_ROOT / "enterprise-gpt-os" / "scripts" / "run_evals.py"
TESTS_DIR = REPO_ROOT / "tests"
BACKEND_DIR = REPO_ROOT / "backend"
CANDIDATE_CLAIMS_PATH = DEFAULT_DATA_DIR / "black_albion_candidate_claims.json"
SITES_PATH = DEFAULT_DATA_DIR / "black_albion_sites.json"
CLAIMS_PATH = DEFAULT_DATA_DIR / "black_albion_claims.json"
MODULES_PATH = DEFAULT_DATA_DIR / "black_albion_modules.json"
SOURCES_PATH = DEFAULT_DATA_DIR / "black_albion_sources.json"
MODULE_EXPANSION_DOC_PATH = REPO_ROOT / "docs" / "black-albion-module-expansion.md"
INTAKE_REVIEW_WORKFLOW_PATH = REPO_ROOT / "docs" / "intake-review-workflow.md"
OPERATOR_APPROVAL_TEMPLATE_PATH = (
    REPO_ROOT / "docs" / "templates" / "operator_promotion_approval_template.md"
)
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


APPROVAL_QUEUE_EMPTY_MESSAGE = (
    "No candidates currently require operator approval."
)

# Lower number sorts earlier. "high" first, then "medium", "low", and
# finally any unknown / empty value. Keep this map stable so the sort
# contract is deterministic.
_APPROVAL_QUEUE_RISK_RANK: Dict[str, int] = {
    "high": 0,
    "medium": 1,
    "low": 2,
    "": 3,
    "unknown": 3,
}


def _approval_queue_sort_key(item: Dict[str, Any]) -> tuple:
    """Deterministic sort key for the read-only approval queue.

    Order:
      1. highest `risk_level` first (high -> medium -> low -> unknown)
      2. `operator_review_ready` true before false
      3. `candidate_id` alphabetically (case-insensitive)

    Python's `sorted` is stable, so equal keys preserve input order.
    The third tuple element guarantees total ordering on any well-formed
    input.
    """
    risk = str(item.get("risk_level") or "").strip().lower()
    risk_rank = _APPROVAL_QUEUE_RISK_RANK.get(risk, 3)
    review_ready_rank = 0 if bool(item.get("operator_review_ready")) else 1
    candidate_id = str(item.get("candidate_id") or "").lower()
    return (risk_rank, review_ready_rank, candidate_id)


def _approval_queue_summary() -> Dict[str, Any]:
    """Return a read-only operator approval queue derived from the candidate
    claims ledger.

    The dashboard only surfaces the queue. It cannot approve or promote.
    Promotion requires a separate operator-approved commit per
    `docs/intake-review-workflow.md` and `docs/templates/operator_promotion_approval_template.md`.
    """
    pending: List[Dict[str, Any]] = []
    skipped: List[str] = []
    if CANDIDATE_CLAIMS_PATH.exists():
        try:
            payload = json.loads(CANDIDATE_CLAIMS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = []
        if isinstance(payload, list):
            for row in payload:
                if not isinstance(row, dict):
                    continue
                candidate_id = str(row.get("candidate_id") or "")
                approval_required = bool(row.get("operator_approval_required"))
                review_ready = bool(row.get("operator_review_ready"))
                canonical_allowed = row.get("canonical_ingestion_allowed", False)
                promotion_allowed = row.get("promotion_commit_allowed", False)
                if not approval_required and not review_ready:
                    if canonical_allowed is True or promotion_allowed is True:
                        # already cleared and outside the read-only queue
                        skipped.append(candidate_id)
                        continue
                    if review_ready is False and approval_required is False:
                        # nothing pending and nothing cleared — still surface so
                        # the operator can see a quarantined-only row.
                        pass
                tier_iii_check = row.get("tier_iii_contamination_check")
                claim_6_path = row.get("claim_6_promotion_path")
                pending.append(
                    {
                        "candidate_id": candidate_id or "(missing id)",
                        "review_status": str(row.get("review_status") or "unknown"),
                        "operator_approval_required": approval_required,
                        "operator_review_ready": review_ready,
                        "canonical_ingestion_allowed": bool(canonical_allowed),
                        "promotion_commit_allowed": bool(promotion_allowed),
                        "operator_packet_file": str(row.get("operator_packet_file") or ""),
                        "operator_approval_draft": str(
                            row.get("operator_approval_draft") or ""
                        ),
                        "tier_iii_contamination_check": (
                            str(tier_iii_check) if tier_iii_check is not None else ""
                        ),
                        "claim_6_promotion_path": (
                            str(claim_6_path) if claim_6_path is not None else ""
                        ),
                        "promotion_blocked_reason": str(row.get("reason") or ""),
                        "risk_level": str(row.get("risk_level") or ""),
                    }
                )
    pending.sort(key=_approval_queue_sort_key)
    return {
        "title": "Approval Queue",
        "intro": "Read-only approval queue",
        "promotion_note": (
            "Promotion requires a separate operator-approved commit"
        ),
        "no_promotion_note": "No promotion occurs from this dashboard",
        "items": pending,
        "item_count": len(pending),
        "item_count_label": f"Approval queue items: {len(pending)}",
        "empty_message": APPROVAL_QUEUE_EMPTY_MESSAGE,
        "skipped_cleared": skipped,
        "intake_queue_path": _repo_relative(CANDIDATE_CLAIMS_PATH),
        "workflow_doc": (
            _repo_relative(INTAKE_REVIEW_WORKFLOW_PATH)
            if INTAKE_REVIEW_WORKFLOW_PATH.exists()
            else "not detected"
        ),
        "approval_template_path": (
            _repo_relative(OPERATOR_APPROVAL_TEMPLATE_PATH)
            if OPERATOR_APPROVAL_TEMPLATE_PATH.exists()
            else "not detected"
        ),
    }


PROMOTION_BLOCKERS_EMPTY_MESSAGE = "No promotion blockers detected."
PROMOTION_BLOCKERS_BLOCKED_DECISIONS = frozenset(
    {
        "more_sources_required",
        "not_approved",
        "rejected",
        "preserve_as_speculative_only",
        "archive_as_speculative_only",
        "do_not_promote_to_tier_i",
    }
)


def _promotion_blockers_for_row(row: Dict[str, Any]) -> List[str]:
    """Return the list of promotion blockers visible on a single candidate row.

    Conservative: each blocker is only added when its triggering field has a
    value that explicitly indicates the candidate cannot yet be promoted.
    The strings are short and lower-case so the dashboard and the smoke
    probes can match them stably.
    """
    blockers: List[str] = []
    if row.get("canonical_ingestion_allowed") is False:
        blockers.append("canonical ingestion blocked")
    if row.get("promotion_commit_allowed") is False:
        blockers.append("promotion commit blocked")
    if bool(row.get("operator_approval_required")) and not bool(
        row.get("operator_approval_granted")
    ):
        blockers.append("operator approval required")
    if bool(row.get("promotion_requires_separate_commit")):
        blockers.append("promotion requires separate commit")
    final_decision = str(row.get("final_decision") or "").strip().lower()
    if final_decision and final_decision in PROMOTION_BLOCKERS_BLOCKED_DECISIONS:
        blockers.append(f"final_decision: {final_decision}")
    required_action = str(row.get("required_action") or "").strip().lower()
    if required_action == "source_hunting":
        blockers.append("more sources required")
    elif required_action == "manual_raw_content_needed_or_independent_source_hunting":
        blockers.append("manual raw content or independent source hunting required")
    tier_iii_check = row.get("tier_iii_contamination_check")
    if tier_iii_check is not None:
        blockers.append(
            f"tier_iii_contamination_check: {str(tier_iii_check).strip().lower()}"
        )
    if row.get("claim_6_tier_i_allowed") is False:
        blockers.append("claim 6 blocked from Tier I")
    claim_6_path = str(row.get("claim_6_promotion_path") or "").strip().lower()
    if claim_6_path == "none":
        blockers.append("claim 6 Tier I promotion path: none")
    return blockers


def _promotion_blockers_sort_key(item: Dict[str, Any]) -> tuple:
    """Deterministic sort key: highest blocker_count first, then candidate_id."""
    blocker_count = int(item.get("blocker_count") or 0)
    candidate_id = str(item.get("candidate_id") or "").lower()
    # Negate the count so a higher count sorts earlier under ascending sort.
    return (-blocker_count, candidate_id)


def _promotion_blockers_summary() -> Dict[str, Any]:
    """Return a read-only blocker summary derived from the candidate ledger.

    The dashboard only surfaces the blockers. It cannot approve or promote.
    Promotion requires a separate operator-approved commit per
    `docs/intake-review-workflow.md` and
    `docs/templates/operator_promotion_approval_template.md`.
    """
    blocked: List[Dict[str, Any]] = []
    if CANDIDATE_CLAIMS_PATH.exists():
        try:
            payload = json.loads(CANDIDATE_CLAIMS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = []
        if isinstance(payload, list):
            for row in payload:
                if not isinstance(row, dict):
                    continue
                blockers = _promotion_blockers_for_row(row)
                if not blockers:
                    continue
                blocked.append(
                    {
                        "candidate_id": str(row.get("candidate_id") or "(missing id)"),
                        "review_status": str(row.get("review_status") or "unknown"),
                        "blocker_count": len(blockers),
                        "blockers": blockers,
                        "operator_packet_file": str(
                            row.get("operator_packet_file") or ""
                        ),
                        "operator_approval_draft": str(
                            row.get("operator_approval_draft") or ""
                        ),
                    }
                )
    blocked.sort(key=_promotion_blockers_sort_key)
    return {
        "title": "Promotion Blockers",
        "intro": "Read-only blocker summary",
        "explanation": "This panel explains why promotion is blocked",
        "no_promotion_note": "No promotion occurs from this dashboard",
        "items": blocked,
        "item_count": len(blocked),
        "item_count_label": f"Blocked candidates: {len(blocked)}",
        "empty_message": PROMOTION_BLOCKERS_EMPTY_MESSAGE,
        "intake_queue_path": _repo_relative(CANDIDATE_CLAIMS_PATH),
        "workflow_doc": (
            _repo_relative(INTAKE_REVIEW_WORKFLOW_PATH)
            if INTAKE_REVIEW_WORKFLOW_PATH.exists()
            else "not detected"
        ),
    }


APPROVAL_EVIDENCE_LINKS_EMPTY_MESSAGE = "No approval evidence links available."


def _approval_evidence_links_sort_key(item: Dict[str, Any]) -> tuple:
    """Deterministic sort key for the read-only approval evidence panel.

    Order:
      1. candidates with `operator_packet_file` first
      2. then candidates with `source_review_file`
      3. then `candidate_id` alphabetically (case-insensitive)
    """
    has_packet = 0 if item.get("operator_packet_file") else 1
    has_review = 0 if item.get("source_review_file") else 1
    candidate_id = str(item.get("candidate_id") or "").lower()
    return (has_packet, has_review, candidate_id)


def _approval_evidence_links_summary() -> Dict[str, Any]:
    """Return a read-only evidence-trail summary for operator review.

    Surfaces the per-candidate file paths the operator needs to navigate from
    "approval required / promotion blocked" to the exact review documents.
    This panel does not approve anything and does not promote anything.
    """
    intake_workflow = (
        _repo_relative(INTAKE_REVIEW_WORKFLOW_PATH)
        if INTAKE_REVIEW_WORKFLOW_PATH.exists()
        else "not detected"
    )
    approval_template = (
        _repo_relative(OPERATOR_APPROVAL_TEMPLATE_PATH)
        if OPERATOR_APPROVAL_TEMPLATE_PATH.exists()
        else "not detected"
    )
    items: List[Dict[str, Any]] = []
    if CANDIDATE_CLAIMS_PATH.exists():
        try:
            payload = json.loads(CANDIDATE_CLAIMS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = []
        if isinstance(payload, list):
            for row in payload:
                if not isinstance(row, dict):
                    continue
                approval_required = bool(row.get("operator_approval_required"))
                packet = str(row.get("operator_packet_file") or "")
                draft = str(row.get("operator_approval_draft") or "")
                if not approval_required and not packet and not draft:
                    continue
                items.append(
                    {
                        "candidate_id": str(
                            row.get("candidate_id") or "(missing id)"
                        ),
                        "review_status": str(row.get("review_status") or "unknown"),
                        "raw_artifact": str(row.get("source_artifact") or ""),
                        "review_note": str(row.get("review_note") or ""),
                        "source_review_file": str(
                            row.get("source_review_file") or ""
                        ),
                        "operator_packet_file": packet,
                        "operator_approval_draft": draft,
                        "canonical_ingestion_allowed": bool(
                            row.get("canonical_ingestion_allowed", False)
                        ),
                        "promotion_commit_allowed": bool(
                            row.get("promotion_commit_allowed", False)
                        ),
                    }
                )
    items.sort(key=_approval_evidence_links_sort_key)
    return {
        "title": "Approval Evidence Links",
        "intro": "Read-only evidence trail",
        "no_approve_note": "Evidence links do not approve promotion",
        "separate_commit_note": (
            "Promotion still requires a separate operator-approved commit"
        ),
        "items": items,
        "item_count": len(items),
        "item_count_label": f"Evidence-bearing candidates: {len(items)}",
        "empty_message": APPROVAL_EVIDENCE_LINKS_EMPTY_MESSAGE,
        "intake_queue_path": _repo_relative(CANDIDATE_CLAIMS_PATH),
        "workflow_doc": intake_workflow,
        "approval_template_path": approval_template,
    }


CANONICAL_LEDGER_INTEGRITY_LOCK_STATEMENTS = (
    "Read-only canonical ledger integrity",
    "Dashboard write access: disabled",
    "Canonical promotion from dashboard: disabled",
    "Promotion requires a separate operator-approved commit",
)

SOURCE_VERIFICATION_EMPTY_MESSAGE = "No source verification records available."
SOURCE_VERIFICATION_LOCK_STATEMENTS = (
    "Read-only source verification",
    "Source scoring does not approve promotion",
    "Promotion still requires a separate operator-approved commit",
)

PER_CLAIM_SOURCE_VERIFICATION_EMPTY_MESSAGE = (
    "No per-claim verification records available."
)
PER_CLAIM_SOURCE_VERIFICATION_LOCK_STATEMENTS = (
    "Read-only per-claim verification",
    "Per-claim scoring does not approve promotion",
    "Promotion still requires a separate operator-approved commit",
)

_URL_RE = re.compile(r"https?://[^\s<>)\"']+")
_REQUIRES_CORRECTION_RE = re.compile(r"requires_correction", re.IGNORECASE)


def _extract_urls(text: str) -> List[str]:
    """Return de-duplicated URLs found in ``text``, trimmed of trailing punct."""
    seen: Dict[str, None] = {}
    for match in _URL_RE.finditer(text):
        url = match.group(0).rstrip(".,;:)]>")
        if url not in seen:
            seen[url] = None
    return list(seen.keys())


def _collect_candidate_sources(row: Dict[str, Any]) -> List[Dict[str, str]]:
    """Collect ``{name, url, notes}`` source references from a candidate row.

    Sources are read from:
      1. URLs in the candidate's referenced ``source_review_file`` markdown.
      2. Any ``candidate_claims[*]`` entry whose ``source_status`` is
         ``speculative_lens_only`` — surfaced as a Tier III speculative entry.
    """
    sources: List[Dict[str, str]] = []
    review_file = row.get("source_review_file")
    if review_file:
        path = REPO_ROOT / str(review_file)
        if path.exists():
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                text = ""
            for url in _extract_urls(text):
                sources.append({"name": "", "url": url, "notes": ""})
    for claim in row.get("candidate_claims", []) or []:
        if not isinstance(claim, dict):
            continue
        if str(claim.get("source_status") or "").lower() == "speculative_lens_only":
            sources.append(
                {
                    "name": str(claim.get("claim_text") or ""),
                    "url": "",
                    "notes": "Tier III speculative_lens_only",
                }
            )
    return sources


def _count_requires_correction(row: Dict[str, Any]) -> int:
    """Count occurrences of ``requires_correction`` across the row and the
    referenced worksheet, used as a coarse "how many claims need rewriting"
    signal for the dashboard panel.
    """
    total = 0
    review_file = row.get("source_review_file")
    if review_file:
        path = REPO_ROOT / str(review_file)
        if path.exists():
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                text = ""
            total += len(_REQUIRES_CORRECTION_RE.findall(text))
    return total


def _per_claim_source_verification_summary() -> Dict[str, Any]:
    """Return per-claim source verification for every candidate that has a
    ``source_review_file`` worksheet on disk.

    Walks the candidate ledger, reads each row's worksheet markdown, splits
    it into ``### Claim N`` sections, and runs the engine on each section.
    Output is sorted by ``candidate_id`` alphabetically then ``claim_number``
    ascending.
    """
    from .source_verification import summarize_per_claim_verification

    items: List[Dict[str, Any]] = []
    if CANDIDATE_CLAIMS_PATH.exists():
        try:
            payload = json.loads(CANDIDATE_CLAIMS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = []
        if isinstance(payload, list):
            for row in payload:
                if not isinstance(row, dict):
                    continue
                review_file = row.get("source_review_file")
                if not review_file:
                    continue
                path = REPO_ROOT / str(review_file)
                if not path.exists():
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except OSError:
                    continue
                claim6_blocked = row.get("claim_6_tier_i_allowed") is False
                summaries = summarize_per_claim_verification(
                    text, claim6_blocked=claim6_blocked
                )
                candidate_id = str(row.get("candidate_id") or "(missing id)")
                review_status = str(row.get("review_status") or "unknown")
                canonical_ingestion_allowed = bool(
                    row.get("canonical_ingestion_allowed", False)
                )
                promotion_commit_allowed = bool(
                    row.get("promotion_commit_allowed", False)
                )
                for summary in summaries:
                    items.append(
                        {
                            "candidate_id": candidate_id,
                            "review_status": review_status,
                            "claim_number": summary["claim_number"],
                            "claim_title": summary["claim_title"],
                            "verification_status": summary["verification_status"],
                            "strongest_source_tier": summary[
                                "strongest_source_tier"
                            ],
                            "source_count": summary["source_count"],
                            "primary_source_count": summary["primary_source_count"],
                            "institutional_source_count": summary[
                                "institutional_source_count"
                            ],
                            "reputable_secondary_count": summary[
                                "reputable_secondary_count"
                            ],
                            "weak_source_count": summary["weak_source_count"],
                            "orientation_only_count": summary[
                                "orientation_only_count"
                            ],
                            "speculative_only_count": summary[
                                "speculative_only_count"
                            ],
                            "no_source_count": summary["no_source_count"],
                            "requires_correction": bool(
                                summary["requires_correction"]
                            ),
                            "canonical_ingestion_allowed": canonical_ingestion_allowed,
                            "promotion_commit_allowed": promotion_commit_allowed,
                        }
                    )

    items.sort(
        key=lambda it: (
            str(it.get("candidate_id") or "").lower(),
            int(it.get("claim_number") or 0),
        )
    )
    return {
        "title": "Per-Claim Source Verification",
        "intro": "Read-only per-claim verification",
        "no_approve_note": "Per-claim scoring does not approve promotion",
        "separate_commit_note": (
            "Promotion still requires a separate operator-approved commit"
        ),
        "items": items,
        "item_count": len(items),
        "item_count_label": f"Per-claim rows: {len(items)}",
        "empty_message": PER_CLAIM_SOURCE_VERIFICATION_EMPTY_MESSAGE,
        "lock_statements": list(PER_CLAIM_SOURCE_VERIFICATION_LOCK_STATEMENTS),
    }


def _source_verification_summary() -> Dict[str, Any]:
    """Return a read-only source verification summary for the dashboard.

    Walks every candidate row in the candidate ledger, collects source URLs
    from the candidate's referenced worksheet, classifies each via the
    deterministic source verification engine, and aggregates per-row counts.
    """
    from .source_verification import summarize_claim_verification

    items: List[Dict[str, Any]] = []
    if CANDIDATE_CLAIMS_PATH.exists():
        try:
            payload = json.loads(CANDIDATE_CLAIMS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = []
        if isinstance(payload, list):
            for row in payload:
                if not isinstance(row, dict):
                    continue
                if not (
                    row.get("operator_approval_required")
                    or row.get("source_review_file")
                    or row.get("operator_packet_file")
                ):
                    continue
                sources = _collect_candidate_sources(row)
                blocked = row.get("claim_6_tier_i_allowed") is False
                requires_correction_count = _count_requires_correction(row)
                summary = summarize_claim_verification(
                    sources,
                    blocked=blocked and not sources,
                    requires_correction=False,
                )
                items.append(
                    {
                        "candidate_id": str(
                            row.get("candidate_id") or "(missing id)"
                        ),
                        "review_status": str(
                            row.get("review_status") or "unknown"
                        ),
                        "strongest_source_tier": summary["strongest_source_tier"],
                        "strongest_source_weight": summary[
                            "strongest_source_weight"
                        ],
                        "verification_status": summary["verification_status"],
                        "source_count": summary["source_count"],
                        "primary_source_count": summary["primary_source_count"],
                        "institutional_source_count": summary[
                            "institutional_source_count"
                        ],
                        "reputable_secondary_count": summary[
                            "reputable_secondary_count"
                        ],
                        "weak_source_count": summary["weak_source_count"],
                        "orientation_only_count": summary[
                            "orientation_only_count"
                        ],
                        "speculative_only_count": summary[
                            "speculative_only_count"
                        ],
                        "no_source_count": summary["no_source_count"],
                        "requires_correction_count": requires_correction_count,
                        "canonical_ingestion_allowed": bool(
                            row.get("canonical_ingestion_allowed", False)
                        ),
                        "promotion_commit_allowed": bool(
                            row.get("promotion_commit_allowed", False)
                        ),
                        "claim_6_tier_i_allowed": row.get(
                            "claim_6_tier_i_allowed"
                        ),
                    }
                )

    # Deterministic sort: highest verification strength first, then candidate_id.
    items.sort(
        key=lambda item: (
            -int(item.get("strongest_source_weight") or 0),
            str(item.get("candidate_id") or "").lower(),
        )
    )
    return {
        "title": "Source Verification",
        "intro": "Read-only source verification",
        "no_approve_note": "Source scoring does not approve promotion",
        "separate_commit_note": (
            "Promotion still requires a separate operator-approved commit"
        ),
        "items": items,
        "item_count": len(items),
        "item_count_label": f"Verified candidates: {len(items)}",
        "empty_message": SOURCE_VERIFICATION_EMPTY_MESSAGE,
        "lock_statements": list(SOURCE_VERIFICATION_LOCK_STATEMENTS),
    }


def _canonical_ledger_status(path: Path) -> Dict[str, Any]:
    """Read a canonical ledger and report (count, status).

    Status semantics (per the v0.4.0 Canonical Ledger Integrity panel):
      - `ok` if file loads and the root shape is a list/dict.
      - `missing` if the file is absent.
      - `invalid_json` if JSON cannot be parsed.
      - `unexpected_shape` if root is neither list nor dict.
    """
    label = path.name
    if not path.exists():
        return {
            "label": label,
            "path": _repo_relative(path),
            "count": 0,
            "status": "missing",
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "label": label,
            "path": _repo_relative(path),
            "count": 0,
            "status": "invalid_json",
        }
    if isinstance(payload, list):
        count = len(payload)
        return {
            "label": label,
            "path": _repo_relative(path),
            "count": count,
            "status": "ok",
        }
    if isinstance(payload, dict):
        # Pick the first list-shaped value (e.g. {"records": [...]}) for the
        # count; otherwise fall back to the number of top-level keys.
        for key in ("records", "sites", "claims", "modules", "sources", "items"):
            inner = payload.get(key)
            if isinstance(inner, list):
                return {
                    "label": label,
                    "path": _repo_relative(path),
                    "count": len(inner),
                    "status": "ok",
                }
        return {
            "label": label,
            "path": _repo_relative(path),
            "count": len(payload),
            "status": "ok",
        }
    return {
        "label": label,
        "path": _repo_relative(path),
        "count": 0,
        "status": "unexpected_shape",
    }


def _canonical_ledger_integrity_summary(
    approval_queue_count: Optional[int] = None,
    promotion_blockers_count: Optional[int] = None,
    approval_evidence_count: Optional[int] = None,
) -> Dict[str, Any]:
    """Return a read-only canonical ledger integrity summary for the dashboard.

    The dashboard reads the four canonical ledger files for counts only and
    confirms the dashboard cannot mutate canonical data. Optional governance
    counts from sibling panels are surfaced verbatim for cross-reference.
    """
    ledgers = [
        {"key": "sites", "path_obj": SITES_PATH},
        {"key": "claims", "path_obj": CLAIMS_PATH},
        {"key": "modules", "path_obj": MODULES_PATH},
        {"key": "sources", "path_obj": SOURCES_PATH},
    ]
    rows: List[Dict[str, Any]] = []
    for spec in ledgers:
        status = _canonical_ledger_status(spec["path_obj"])
        status["key"] = spec["key"]
        rows.append(status)
    return {
        "title": "Canonical Ledger Integrity",
        "intro": "Read-only canonical ledger integrity",
        "lock_statements": list(CANONICAL_LEDGER_INTEGRITY_LOCK_STATEMENTS),
        "write_access_note": "Dashboard write access: disabled",
        "canonical_promotion_note": (
            "Canonical promotion from dashboard: disabled"
        ),
        "separate_commit_note": (
            "Promotion requires a separate operator-approved commit"
        ),
        "operator_approval_note": (
            "Operator approval required before promotion: true"
        ),
        "rows": rows,
        "approval_queue_count": approval_queue_count,
        "promotion_blockers_count": promotion_blockers_count,
        "approval_evidence_count": approval_evidence_count,
    }


def _exists_label(path: Path) -> str:
    """Return a readable exists/missing label for a local check artifact."""
    return "present" if path.exists() else "not detected"


def _system_checks_summary() -> Dict[str, str]:
    """Return read-only local validation and CI guardrail status."""
    test_file_count = (
        len([path for path in TESTS_DIR.glob("test_*.py") if path.is_file()])
        if TESTS_DIR.exists()
        else 0
    )
    latest_known_status = "last validated CI run passed"
    if CHANGELOG_PATH.exists():
        text = CHANGELOG_PATH.read_text(encoding="utf-8")
        if (
            "Enterprise GPT OS Validation workflow passed" in text
            and "Live Uvicorn Smoke workflow passed" in text
        ):
            latest_known_status = "v0.2 release notes confirm both CI gates passed"

    return {
        "governance_ci": _exists_label(ENTERPRISE_GPT_OS_WORKFLOW_PATH),
        "governance_ci_path": _repo_relative(ENTERPRISE_GPT_OS_WORKFLOW_PATH),
        "runtime_ci": _exists_label(LIVE_UVICORN_WORKFLOW_PATH),
        "runtime_ci_path": _repo_relative(LIVE_UVICORN_WORKFLOW_PATH),
        "local_wrapper": _exists_label(ENTERPRISE_GPT_OS_WRAPPER_PATH),
        "local_wrapper_path": _repo_relative(ENTERPRISE_GPT_OS_WRAPPER_PATH),
        "manifest_validator": _exists_label(MANIFEST_VALIDATOR_PATH),
        "manifest_validator_path": _repo_relative(MANIFEST_VALIDATOR_PATH),
        "eval_runner": _exists_label(EVAL_RUNNER_PATH),
        "eval_runner_path": _repo_relative(EVAL_RUNNER_PATH),
        "live_smoke_script": _exists_label(LIVE_SMOKE_SCRIPT_PATH),
        "live_smoke_script_path": _repo_relative(LIVE_SMOKE_SCRIPT_PATH),
        "test_suite": f"{test_file_count} test files" if test_file_count else "not detected",
        "backend_compile": "python3 -m compileall backend" if BACKEND_DIR.exists() else "not detected",
        "secret_scan": "secret-pattern scan on changed files",
        "latest_test_count": "48 tests passing from latest validated run",
        "latest_status": latest_known_status,
        "source_note": "Confirm latest CI on GitHub Actions for live truth.",
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
        approval_queue = _approval_queue_summary()
        promotion_blockers = _promotion_blockers_summary()
        approval_evidence = _approval_evidence_links_summary()
        canonical_ledger_integrity = _canonical_ledger_integrity_summary(
            approval_queue_count=approval_queue["item_count"],
            promotion_blockers_count=promotion_blockers["item_count"],
            approval_evidence_count=approval_evidence["item_count"],
        )
        source_verification = _source_verification_summary()
        per_claim_source_verification = _per_claim_source_verification_summary()
        system_checks = _system_checks_summary()
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
        approval_queue_title = escape(approval_queue["title"])
        approval_queue_intro = escape(approval_queue["intro"])
        approval_queue_promotion_note = escape(approval_queue["promotion_note"])
        approval_queue_no_promotion_note = escape(approval_queue["no_promotion_note"])
        approval_queue_workflow = escape(str(approval_queue["workflow_doc"]))
        approval_queue_template = escape(str(approval_queue["approval_template_path"]))
        approval_queue_source = escape(str(approval_queue["intake_queue_path"]))
        approval_queue_count_label = escape(str(approval_queue["item_count_label"]))
        approval_queue_empty_message = escape(str(approval_queue["empty_message"]))
        if approval_queue["items"]:
            approval_queue_items_html = "\n".join(
                "<li>"
                f"<strong>{escape(item['candidate_id'])}</strong>"
                f" — review_status: <code>{escape(item['review_status'])}</code>"
                "<ul>"
                f"<li>operator_approval_required: <code>{escape(str(item['operator_approval_required']).lower())}</code></li>"
                f"<li>operator_review_ready: <code>{escape(str(item['operator_review_ready']).lower())}</code></li>"
                f"<li>canonical_ingestion_allowed: <code>{escape(str(item['canonical_ingestion_allowed']).lower())}</code></li>"
                f"<li>promotion_commit_allowed: <code>{escape(str(item['promotion_commit_allowed']).lower())}</code></li>"
                f"<li>operator_packet_file: <code>{escape(item['operator_packet_file']) or 'not detected'}</code></li>"
                f"<li>operator_approval_draft: <code>{escape(item['operator_approval_draft']) or 'not detected'}</code></li>"
                + (
                    f"<li>tier_iii_contamination_check: <code>{escape(item['tier_iii_contamination_check'])}</code></li>"
                    if item["tier_iii_contamination_check"]
                    else ""
                )
                + (
                    f"<li>claim_6_promotion_path: <code>{escape(item['claim_6_promotion_path'])}</code></li>"
                    if item["claim_6_promotion_path"]
                    else ""
                )
                + (
                    f"<li>risk_level: <code>{escape(item['risk_level'])}</code></li>"
                    if item["risk_level"]
                    else ""
                )
                + (
                    f"<li>promotion_blocked_reason: {escape(item['promotion_blocked_reason'])}</li>"
                    if item["promotion_blocked_reason"]
                    else ""
                )
                + "</ul>"
                "</li>"
                for item in approval_queue["items"]
            )
        else:
            approval_queue_items_html = (
                f"<li>{approval_queue_empty_message}</li>"
            )
        promotion_blockers_title = escape(promotion_blockers["title"])
        promotion_blockers_intro = escape(promotion_blockers["intro"])
        promotion_blockers_explanation = escape(promotion_blockers["explanation"])
        promotion_blockers_no_promotion_note = escape(
            promotion_blockers["no_promotion_note"]
        )
        promotion_blockers_count_label = escape(
            str(promotion_blockers["item_count_label"])
        )
        promotion_blockers_empty_message = escape(
            str(promotion_blockers["empty_message"])
        )
        promotion_blockers_source = escape(str(promotion_blockers["intake_queue_path"]))
        promotion_blockers_workflow = escape(str(promotion_blockers["workflow_doc"]))
        if promotion_blockers["items"]:
            promotion_blockers_items_html = "\n".join(
                "<li>"
                f"<strong>{escape(item['candidate_id'])}</strong>"
                f" — review_status: <code>{escape(item['review_status'])}</code>"
                f" — blocker_count: <strong>{escape(str(item['blocker_count']))}</strong>"
                "<ul>"
                + "".join(
                    f"<li>{escape(b)}</li>" for b in item["blockers"]
                )
                + (
                    f"<li>operator_packet_file: <code>{escape(item['operator_packet_file'])}</code></li>"
                    if item["operator_packet_file"]
                    else ""
                )
                + (
                    f"<li>operator_approval_draft: <code>{escape(item['operator_approval_draft'])}</code></li>"
                    if item["operator_approval_draft"]
                    else ""
                )
                + "</ul>"
                "</li>"
                for item in promotion_blockers["items"]
            )
        else:
            promotion_blockers_items_html = (
                f"<li>{promotion_blockers_empty_message}</li>"
            )
        approval_evidence_title = escape(approval_evidence["title"])
        approval_evidence_intro = escape(approval_evidence["intro"])
        approval_evidence_no_approve_note = escape(
            approval_evidence["no_approve_note"]
        )
        approval_evidence_separate_commit_note = escape(
            approval_evidence["separate_commit_note"]
        )
        approval_evidence_count_label = escape(
            str(approval_evidence["item_count_label"])
        )
        approval_evidence_empty_message = escape(
            str(approval_evidence["empty_message"])
        )
        approval_evidence_source = escape(str(approval_evidence["intake_queue_path"]))
        approval_evidence_workflow = escape(str(approval_evidence["workflow_doc"]))
        approval_evidence_template = escape(
            str(approval_evidence["approval_template_path"])
        )

        def _evidence_link_line(label: str, path: str) -> str:
            if not path:
                return ""
            return f"<li>{label}: <code>{escape(path)}</code></li>"

        if approval_evidence["items"]:
            approval_evidence_items_html = "\n".join(
                "<li>"
                f"<strong>{escape(item['candidate_id'])}</strong>"
                f" — review_status: <code>{escape(item['review_status'])}</code>"
                "<ul>"
                + _evidence_link_line("raw_artifact", item["raw_artifact"])
                + _evidence_link_line("review_note", item["review_note"])
                + _evidence_link_line(
                    "source_review_file", item["source_review_file"]
                )
                + _evidence_link_line(
                    "operator_packet_file", item["operator_packet_file"]
                )
                + _evidence_link_line(
                    "operator_approval_draft", item["operator_approval_draft"]
                )
                + f"<li>operator_approval_template: <code>{approval_evidence_template}</code></li>"
                + f"<li>intake_workflow: <code>{approval_evidence_workflow}</code></li>"
                + f"<li>canonical_ingestion_allowed: <code>{escape(str(item['canonical_ingestion_allowed']).lower())}</code></li>"
                + f"<li>promotion_commit_allowed: <code>{escape(str(item['promotion_commit_allowed']).lower())}</code></li>"
                + "</ul>"
                "</li>"
                for item in approval_evidence["items"]
            )
        else:
            approval_evidence_items_html = (
                f"<li>{approval_evidence_empty_message}</li>"
            )
        canonical_integrity_title = escape(canonical_ledger_integrity["title"])
        canonical_integrity_intro = escape(canonical_ledger_integrity["intro"])
        canonical_integrity_write_access = escape(
            canonical_ledger_integrity["write_access_note"]
        )
        canonical_integrity_canonical_promotion = escape(
            canonical_ledger_integrity["canonical_promotion_note"]
        )
        canonical_integrity_separate_commit = escape(
            canonical_ledger_integrity["separate_commit_note"]
        )
        canonical_integrity_operator_approval = escape(
            canonical_ledger_integrity["operator_approval_note"]
        )
        canonical_integrity_rows_html = "\n".join(
            "<li>"
            f"{escape(row['key'])}: <strong>{escape(str(row['count']))}</strong>"
            f" (<code>{escape(row['path'])}</code>,"
            f" status: <code>{escape(row['status'])}</code>)"
            "</li>"
            for row in canonical_ledger_integrity["rows"]
        )
        canonical_integrity_governance_html = (
            f"<li>Approval queue items: <strong>{escape(str(canonical_ledger_integrity['approval_queue_count']))}</strong></li>"
            f"<li>Blocked candidates: <strong>{escape(str(canonical_ledger_integrity['promotion_blockers_count']))}</strong></li>"
            f"<li>Evidence-bearing candidates: <strong>{escape(str(canonical_ledger_integrity['approval_evidence_count']))}</strong></li>"
        )
        source_verification_title = escape(source_verification["title"])
        source_verification_intro = escape(source_verification["intro"])
        source_verification_no_approve_note = escape(
            source_verification["no_approve_note"]
        )
        source_verification_separate_commit_note = escape(
            source_verification["separate_commit_note"]
        )
        source_verification_count_label = escape(
            str(source_verification["item_count_label"])
        )
        source_verification_empty_message = escape(
            str(source_verification["empty_message"])
        )
        if source_verification["items"]:
            source_verification_items_html = "\n".join(
                "<li>"
                f"<strong>{escape(item['candidate_id'])}</strong>"
                f" — review_status: <code>{escape(item['review_status'])}</code>"
                f" — verification_status: <code>{escape(item['verification_status'])}</code>"
                f" — strongest_source_tier: <code>{escape(item['strongest_source_tier'])}</code>"
                "<ul>"
                f"<li>source_count: <strong>{escape(str(item['source_count']))}</strong></li>"
                f"<li>primary_source_count: <strong>{escape(str(item['primary_source_count']))}</strong></li>"
                f"<li>institutional_source_count: <strong>{escape(str(item['institutional_source_count']))}</strong></li>"
                f"<li>reputable_secondary_count: <strong>{escape(str(item['reputable_secondary_count']))}</strong></li>"
                f"<li>weak_source_count: <strong>{escape(str(item['weak_source_count']))}</strong></li>"
                f"<li>orientation_only_count: <strong>{escape(str(item['orientation_only_count']))}</strong></li>"
                f"<li>speculative_only_count: <strong>{escape(str(item['speculative_only_count']))}</strong></li>"
                f"<li>no_source_count: <strong>{escape(str(item['no_source_count']))}</strong></li>"
                f"<li>requires_correction_count: <strong>{escape(str(item['requires_correction_count']))}</strong></li>"
                f"<li>canonical_ingestion_allowed: <code>{escape(str(item['canonical_ingestion_allowed']).lower())}</code></li>"
                f"<li>promotion_commit_allowed: <code>{escape(str(item['promotion_commit_allowed']).lower())}</code></li>"
                "</ul>"
                "</li>"
                for item in source_verification["items"]
            )
        else:
            source_verification_items_html = (
                f"<li>{source_verification_empty_message}</li>"
            )
        per_claim_title = escape(per_claim_source_verification["title"])
        per_claim_intro = escape(per_claim_source_verification["intro"])
        per_claim_no_approve_note = escape(
            per_claim_source_verification["no_approve_note"]
        )
        per_claim_separate_commit_note = escape(
            per_claim_source_verification["separate_commit_note"]
        )
        per_claim_count_label = escape(
            str(per_claim_source_verification["item_count_label"])
        )
        per_claim_empty_message = escape(
            str(per_claim_source_verification["empty_message"])
        )
        if per_claim_source_verification["items"]:
            per_claim_items_html = "\n".join(
                "<li>"
                f"<strong>{escape(item['candidate_id'])}</strong>"
                f" — Claim {escape(str(item['claim_number']))}: "
                f"<em>{escape(item.get('claim_title') or '')}</em>"
                "<ul>"
                f"<li>review_status: <code>{escape(item['review_status'])}</code></li>"
                f"<li>verification_status: <code>{escape(item['verification_status'])}</code></li>"
                f"<li>strongest_source_tier: <code>{escape(item['strongest_source_tier'])}</code></li>"
                f"<li>source_count: <strong>{escape(str(item['source_count']))}</strong></li>"
                f"<li>primary_source_count: <strong>{escape(str(item['primary_source_count']))}</strong></li>"
                f"<li>institutional_source_count: <strong>{escape(str(item['institutional_source_count']))}</strong></li>"
                f"<li>reputable_secondary_count: <strong>{escape(str(item['reputable_secondary_count']))}</strong></li>"
                f"<li>orientation_only_count: <strong>{escape(str(item['orientation_only_count']))}</strong></li>"
                f"<li>speculative_only_count: <strong>{escape(str(item['speculative_only_count']))}</strong></li>"
                f"<li>no_source_count: <strong>{escape(str(item['no_source_count']))}</strong></li>"
                f"<li>requires_correction: <code>{escape(str(item['requires_correction']).lower())}</code></li>"
                f"<li>canonical_ingestion_allowed: <code>{escape(str(item['canonical_ingestion_allowed']).lower())}</code></li>"
                f"<li>promotion_commit_allowed: <code>{escape(str(item['promotion_commit_allowed']).lower())}</code></li>"
                "</ul>"
                "</li>"
                for item in per_claim_source_verification["items"]
            )
        else:
            per_claim_items_html = f"<li>{per_claim_empty_message}</li>"
        read_only_note = escape(str(source_intake["read_only_note"]))
        governance_ci_status = escape(system_checks["governance_ci"])
        governance_ci_path = escape(system_checks["governance_ci_path"])
        runtime_ci_status = escape(system_checks["runtime_ci"])
        runtime_ci_path = escape(system_checks["runtime_ci_path"])
        local_wrapper_status = escape(system_checks["local_wrapper"])
        local_wrapper_path = escape(system_checks["local_wrapper_path"])
        manifest_validator_status = escape(system_checks["manifest_validator"])
        manifest_validator_path = escape(system_checks["manifest_validator_path"])
        eval_runner_status = escape(system_checks["eval_runner"])
        eval_runner_path = escape(system_checks["eval_runner_path"])
        live_smoke_status = escape(system_checks["live_smoke_script"])
        live_smoke_path = escape(system_checks["live_smoke_script_path"])
        test_suite_status = escape(system_checks["test_suite"])
        backend_compile_status = escape(system_checks["backend_compile"])
        secret_scan_guardrail = escape(system_checks["secret_scan"])
        latest_test_count = escape(system_checks["latest_test_count"])
        latest_system_status = escape(system_checks["latest_status"])
        system_checks_source_note = escape(system_checks["source_note"])
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
      <div class="panel">
        <h2>{approval_queue_title}</h2>
        <p><strong>{approval_queue_intro}</strong></p>
        <p>{approval_queue_no_promotion_note}.</p>
        <p>{approval_queue_promotion_note}.</p>
        <p><strong>{approval_queue_count_label}</strong></p>
        <p>Source: <code>{approval_queue_source}</code></p>
        <p>Workflow: <code>{approval_queue_workflow}</code></p>
        <p>Approval template: <code>{approval_queue_template}</code></p>
        <ol>
          {approval_queue_items_html}
        </ol>
      </div>
      <div class="panel">
        <h2>{promotion_blockers_title}</h2>
        <p><strong>{promotion_blockers_intro}</strong></p>
        <p>{promotion_blockers_explanation}.</p>
        <p>{promotion_blockers_no_promotion_note}.</p>
        <p><strong>{promotion_blockers_count_label}</strong></p>
        <p>Source: <code>{promotion_blockers_source}</code></p>
        <p>Workflow: <code>{promotion_blockers_workflow}</code></p>
        <ol>
          {promotion_blockers_items_html}
        </ol>
      </div>
      <div class="panel">
        <h2>{approval_evidence_title}</h2>
        <p><strong>{approval_evidence_intro}</strong></p>
        <p>{approval_evidence_no_approve_note}.</p>
        <p>{approval_evidence_separate_commit_note}.</p>
        <p><strong>{approval_evidence_count_label}</strong></p>
        <p>Source: <code>{approval_evidence_source}</code></p>
        <p>Workflow: <code>{approval_evidence_workflow}</code></p>
        <p>Approval template: <code>{approval_evidence_template}</code></p>
        <ol>
          {approval_evidence_items_html}
        </ol>
      </div>
      <div class="panel">
        <h2>{source_verification_title}</h2>
        <p><strong>{source_verification_intro}</strong></p>
        <p>{source_verification_no_approve_note}.</p>
        <p>{source_verification_separate_commit_note}.</p>
        <p><strong>{source_verification_count_label}</strong></p>
        <ol>
          {source_verification_items_html}
        </ol>
      </div>
      <div class="panel">
        <h2>{per_claim_title}</h2>
        <p><strong>{per_claim_intro}</strong></p>
        <p>{per_claim_no_approve_note}.</p>
        <p>{per_claim_separate_commit_note}.</p>
        <p><strong>{per_claim_count_label}</strong></p>
        <ol>
          {per_claim_items_html}
        </ol>
      </div>
      <div class="panel">
        <h2>{canonical_integrity_title}</h2>
        <p><strong>{canonical_integrity_intro}</strong></p>
        <p>{canonical_integrity_write_access}.</p>
        <p>{canonical_integrity_canonical_promotion}.</p>
        <p>{canonical_integrity_separate_commit}.</p>
        <p>{canonical_integrity_operator_approval}.</p>
        <h3>Canonical ledgers</h3>
        <ul>
          {canonical_integrity_rows_html}
        </ul>
        <h3>Governance cross-reference</h3>
        <ul>
          {canonical_integrity_governance_html}
        </ul>
      </div>
      <div class="panel">
        <h2>System Checks</h2>
        <p>Governance CI: <strong>Enterprise GPT OS Validation</strong> — {governance_ci_status}</p>
        <p><code>{governance_ci_path}</code></p>
        <p>Runtime CI: <strong>Live Uvicorn Smoke</strong> — {runtime_ci_status}</p>
        <p><code>{runtime_ci_path}</code></p>
        <p>Local Validation Wrapper: {local_wrapper_status}</p>
        <p><code>{local_wrapper_path}</code></p>
        <p>Manifest Validator: {manifest_validator_status}</p>
        <p><code>{manifest_validator_path}</code></p>
        <p>Eval Runner: {eval_runner_status}</p>
        <p><code>{eval_runner_path}</code></p>
        <p>Live Smoke Script: {live_smoke_status}</p>
        <p><code>{live_smoke_path}</code></p>
        <p>Test Suite: <strong>{test_suite_status}</strong></p>
        <p>Backend Compile Check: <code>{backend_compile_status}</code></p>
        <p>Secret Scan Guardrail: {secret_scan_guardrail}</p>
        <p>Latest known test count: <strong>{latest_test_count}</strong></p>
        <p>Latest Known Status: {latest_system_status}</p>
        <p>{system_checks_source_note}</p>
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
