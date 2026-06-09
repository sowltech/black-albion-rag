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
                self.assertIn("v0.2 — Governed Runtime Proof", body)
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
            finally:
                os.environ.pop("BLACK_ALBION_DATA_DIR", None)

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
