"""Smoke test for GET /health on a temp-corpus FastAPI app."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class HealthTests(unittest.TestCase):
    def test_health_returns_ok_and_document_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_dir = Path(tmpdir) / "raw"
            raw_dir.mkdir()
            (raw_dir / "seed.json").write_text(
                json.dumps(
                    [
                        {
                            "id": "seed_site_001",
                            "tier": "I",
                            "title": "Seed Site",
                            "summary": "Tier I baseline test record.",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            os.environ["BLACK_ALBION_DATA_DIR"] = str(raw_dir)
            try:
                from backend.app.main import create_app

                app = create_app()
                client = TestClient(app)
                resp = client.get("/health")
                self.assertEqual(200, resp.status_code)
                body = resp.json()
                self.assertEqual("black-albion-rag", body["service"])
                self.assertEqual("ok", body["status"])
                self.assertEqual(1, body["documents"])
                self.assertIn("raw", body["data_dir"])

                modules_resp = client.get("/modules")
                self.assertEqual(200, modules_resp.status_code)
                self.assertEqual([], modules_resp.json())

                sites_resp = client.get("/sites")
                self.assertEqual(200, sites_resp.status_code)
                self.assertEqual(1, len(sites_resp.json()))
            finally:
                os.environ.pop("BLACK_ALBION_DATA_DIR", None)

    def test_dashboard_returns_read_only_operator_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_dir = Path(tmpdir) / "raw"
            raw_dir.mkdir()
            (raw_dir / "seed.json").write_text(
                json.dumps(
                    [
                        {
                            "module_id": "UK-RAG-MOD-DASH",
                            "site_id": "dashboard_site",
                            "name": "Dashboard Module",
                            "title": "Dashboard Module",
                            "tier": "I",
                            "claim_id": "claim_dashboard_001",
                            "claim_text": "Dashboard test claim.",
                            "summary": "Dashboard test record.",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            os.environ["BLACK_ALBION_DATA_DIR"] = str(raw_dir)
            try:
                from backend.app.main import create_app

                app = create_app()
                client = TestClient(app)
                resp = client.get("/dashboard")
                self.assertEqual(200, resp.status_code)
                self.assertIn("text/html", resp.headers["content-type"])
                body = resp.text
                self.assertIn("Operator Dashboard", body)
                for path in (
                    "/health",
                    "/modules",
                    "/sites",
                    "/claims",
                    "/map/layers",
                    "/openapi.json",
                    "/docs",
                ):
                    self.assertIn(f'href="{path}"', body)
                self.assertIn("v0.3.0-planned", body)
                self.assertIn("Latest release", body)
                self.assertIn("v0.4.0 Approval Queue", body)
                self.assertIn("CHANGELOG.md", body)
                self.assertIn("Repo Estate", body)
                self.assertIn("Total repos found", body)
                self.assertIn("black-albion-rag", body)
                self.assertIn("sowltech-shinobi-orca", body)
                self.assertIn("OMNI-CORE", body)
                self.assertIn("REPO_ESTATE_AUDIT.md", body)
                self.assertIn("Source / Intake Review", body)
                self.assertIn("read-only", body)
                self.assertIn("black_albion_candidate_claims.json", body)
                self.assertIn("gemini_share_002_raw.md", body)
                self.assertIn("Latest Intake Commit", body)
                self.assertIn("Next Review Action", body)
                self.assertIn("System Checks", body)
                self.assertIn("Enterprise GPT OS Validation", body)
                self.assertIn("Live Uvicorn Smoke", body)
                self.assertIn("Manifest Validator", body)
                self.assertIn("Eval Runner", body)
                self.assertIn("Confirm latest CI on GitHub Actions", body)
                self.assertIn("scripts/validate_enterprise_gpt_os.sh", body)
                # v0.4.0 Approval Queue panel — read-only, no promotion path
                self.assertIn("Approval Queue", body)
                self.assertIn("Read-only approval queue", body)
                self.assertIn("No promotion occurs from this dashboard", body)
                self.assertIn(
                    "Promotion requires a separate operator-approved commit",
                    body,
                )
                self.assertIn("cand_gloucestershire_egypt_058", body)
                self.assertIn(
                    "gloucestershire_egypt_operator_packet.md", body
                )
                self.assertIn(
                    "gloucestershire_egypt_operator_approval_draft.md", body
                )
                self.assertIn("canonical_ingestion_allowed", body)
                self.assertIn("promotion_commit_allowed", body)
                self.assertIn("tier_iii_contamination_check", body)
                # v0.4.0 Approval Queue display contract: count label
                self.assertIn("Approval queue items:", body)
                # v0.4.0 Promotion Blockers panel contract
                self.assertIn("Promotion Blockers", body)
                self.assertIn("Read-only blocker summary", body)
                self.assertIn(
                    "This panel explains why promotion is blocked", body
                )
                self.assertIn("Blocked candidates:", body)
                self.assertIn("canonical ingestion blocked", body)
                self.assertIn("promotion commit blocked", body)
                self.assertIn("operator approval required", body)
                self.assertIn("claim 6", body)
            finally:
                os.environ.pop("BLACK_ALBION_DATA_DIR", None)

    def test_promotion_blockers_for_row_detects_each_blocker(self) -> None:
        from backend.app.main import _promotion_blockers_for_row

        row = {
            "candidate_id": "cand_x",
            "canonical_ingestion_allowed": False,
            "promotion_commit_allowed": False,
            "operator_approval_required": True,
            "promotion_requires_separate_commit": True,
            "final_decision": "more_sources_required",
            "required_action": "source_hunting",
            "tier_iii_contamination_check": "passed",
            "claim_6_tier_i_allowed": False,
            "claim_6_promotion_path": "none",
        }
        blockers = _promotion_blockers_for_row(row)
        self.assertIn("canonical ingestion blocked", blockers)
        self.assertIn("promotion commit blocked", blockers)
        self.assertIn("operator approval required", blockers)
        self.assertIn("promotion requires separate commit", blockers)
        self.assertIn("final_decision: more_sources_required", blockers)
        self.assertIn("more sources required", blockers)
        self.assertIn("tier_iii_contamination_check: passed", blockers)
        self.assertIn("claim 6 blocked from Tier I", blockers)
        self.assertIn("claim 6 Tier I promotion path: none", blockers)

    def test_promotion_blockers_for_row_clean_row_returns_empty(self) -> None:
        from backend.app.main import _promotion_blockers_for_row

        row = {
            "candidate_id": "cand_clear",
            "canonical_ingestion_allowed": True,
            "promotion_commit_allowed": True,
            "operator_approval_required": False,
            "promotion_requires_separate_commit": False,
        }
        self.assertEqual(_promotion_blockers_for_row(row), [])

    def test_promotion_blockers_sort_key_is_deterministic(self) -> None:
        from backend.app.main import _promotion_blockers_sort_key

        items = [
            {"candidate_id": "cand_charlie", "blocker_count": 1},
            {"candidate_id": "cand_alpha", "blocker_count": 4},
            {"candidate_id": "cand_bravo", "blocker_count": 4},
            {"candidate_id": "cand_delta", "blocker_count": 2},
        ]
        ordered = sorted(items, key=_promotion_blockers_sort_key)
        self.assertEqual(
            [item["candidate_id"] for item in ordered],
            ["cand_alpha", "cand_bravo", "cand_delta", "cand_charlie"],
        )

    def test_promotion_blockers_empty_message_is_canonical(self) -> None:
        from backend.app.main import PROMOTION_BLOCKERS_EMPTY_MESSAGE

        self.assertEqual(
            PROMOTION_BLOCKERS_EMPTY_MESSAGE,
            "No promotion blockers detected.",
        )

    def test_promotion_blockers_summary_includes_gloucestershire(self) -> None:
        from backend.app.main import _promotion_blockers_summary

        summary = _promotion_blockers_summary()
        self.assertIn("items", summary)
        ids = [item["candidate_id"] for item in summary["items"]]
        self.assertIn("cand_gloucestershire_egypt_058", ids)
        glos = next(
            item
            for item in summary["items"]
            if item["candidate_id"] == "cand_gloucestershire_egypt_058"
        )
        self.assertIn("canonical ingestion blocked", glos["blockers"])
        self.assertIn("promotion commit blocked", glos["blockers"])
        self.assertIn("operator approval required", glos["blockers"])
        self.assertIn("claim 6 blocked from Tier I", glos["blockers"])
        self.assertIn("claim 6 Tier I promotion path: none", glos["blockers"])
        self.assertEqual(
            summary["item_count_label"],
            f"Blocked candidates: {summary['item_count']}",
        )

    def test_approval_queue_sort_key_is_deterministic(self) -> None:
        from backend.app.main import _approval_queue_sort_key

        items = [
            {"candidate_id": "cand_bravo", "risk_level": "low", "operator_review_ready": True},
            {"candidate_id": "cand_alpha", "risk_level": "high", "operator_review_ready": False},
            {"candidate_id": "cand_charlie", "risk_level": "high", "operator_review_ready": True},
            {"candidate_id": "cand_delta", "risk_level": "medium", "operator_review_ready": False},
            {"candidate_id": "cand_echo", "risk_level": "", "operator_review_ready": True},
        ]
        ordered = sorted(items, key=_approval_queue_sort_key)
        order = [item["candidate_id"] for item in ordered]
        # high (review_ready true) -> high (review_ready false)
        # -> medium -> low -> unknown
        self.assertEqual(
            order,
            [
                "cand_charlie",  # high, review_ready true
                "cand_alpha",    # high, review_ready false
                "cand_delta",    # medium
                "cand_bravo",    # low
                "cand_echo",     # unknown risk
            ],
        )
        # Stable on equal keys: re-sorting same input yields same output.
        again = sorted(items, key=_approval_queue_sort_key)
        self.assertEqual(
            [item["candidate_id"] for item in again], order
        )

    def test_approval_queue_empty_message_is_canonical(self) -> None:
        from backend.app.main import APPROVAL_QUEUE_EMPTY_MESSAGE

        self.assertEqual(
            APPROVAL_QUEUE_EMPTY_MESSAGE,
            "No candidates currently require operator approval.",
        )

    def test_approval_queue_summary_carries_count_and_empty_message(self) -> None:
        from backend.app.main import (
            APPROVAL_QUEUE_EMPTY_MESSAGE,
            _approval_queue_summary,
        )

        summary = _approval_queue_summary()
        self.assertIn("item_count", summary)
        self.assertEqual(summary["item_count"], len(summary["items"]))
        self.assertEqual(
            summary["item_count_label"],
            f"Approval queue items: {summary['item_count']}",
        )
        self.assertEqual(summary["empty_message"], APPROVAL_QUEUE_EMPTY_MESSAGE)
        self.assertEqual(
            summary["promotion_note"],
            "Promotion requires a separate operator-approved commit",
        )
        # Items are emitted in the deterministic sort order.
        from backend.app.main import _approval_queue_sort_key

        self.assertEqual(
            summary["items"],
            sorted(summary["items"], key=_approval_queue_sort_key),
        )

    def test_dashboard_search_renders_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_dir = Path(tmpdir) / "raw"
            raw_dir.mkdir()
            (raw_dir / "seed.json").write_text(
                json.dumps(
                    [
                        {
                            "id": "winchcombe_site_001",
                            "tier": "I",
                            "title": "Winchcombe Corridor",
                            "summary": "Winchcombe appears in a dashboard search test record.",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            os.environ["BLACK_ALBION_DATA_DIR"] = str(raw_dir)
            try:
                from backend.app.main import create_app

                app = create_app()
                client = TestClient(app)
                resp = client.get("/dashboard?q=Winchcombe")
                self.assertEqual(200, resp.status_code)
                body = resp.text
                self.assertIn("Search Results", body)
                self.assertIn("Winchcombe", body)
                self.assertIn("Result count", body)
                for path in (
                    "/health",
                    "/modules",
                    "/sites",
                    "/claims",
                    "/map/layers",
                    "/openapi.json",
                    "/docs",
                ):
                    self.assertIn(f'href="{path}"', body)
            finally:
                os.environ.pop("BLACK_ALBION_DATA_DIR", None)

    def test_dashboard_query_renders_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_dir = Path(tmpdir) / "raw"
            raw_dir.mkdir()
            (raw_dir / "seed.json").write_text(
                json.dumps(
                    [
                        {
                            "id": "winchcombe_query_001",
                            "tier": "I",
                            "title": "Winchcombe Query Evidence",
                            "summary": "Winchcombe has query evidence for the dashboard.",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            os.environ["BLACK_ALBION_DATA_DIR"] = str(raw_dir)
            try:
                from backend.app.main import create_app

                app = create_app()
                client = TestClient(app)
                resp = client.get("/dashboard?query=What%20is%20Winchcombe")
                self.assertEqual(200, resp.status_code)
                body = resp.text
                self.assertIn("Query Result", body)
                self.assertIn("What is Winchcombe", body)
                self.assertIn("Supporting Matches", body)
                self.assertIn("Winchcombe Query Evidence", body)
                for path in (
                    "/health",
                    "/modules",
                    "/sites",
                    "/claims",
                    "/map/layers",
                    "/openapi.json",
                    "/docs",
                ):
                    self.assertIn(f'href="{path}"', body)
            finally:
                os.environ.pop("BLACK_ALBION_DATA_DIR", None)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
