"""End-to-end test for POST /query against a temp Tier-tagged corpus."""
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


class QueryEndpointTests(unittest.TestCase):
    def _seed(self, tmpdir: str) -> Path:
        raw_dir = Path(tmpdir) / "raw"
        raw_dir.mkdir()
        (raw_dir / "sites.json").write_text(
            json.dumps(
                [
                    {
                        "id": "site_winchcombe_corridor",
                        "tier": "I",
                        "title": "Winchcombe Corridor",
                        "summary": "A corridor of recurring importance through the Cotswold escarpment.",
                    },
                    {
                        "id": "claim_speculative_bright_fort",
                        "tier": "III",
                        "title": "Bright Fort pineal lens",
                        "summary": "Speculative reading: Caerloyw / Gleawanceaster as a metaphor for the pineal gland.",
                    },
                ]
            ),
            encoding="utf-8",
        )
        return raw_dir

    def test_query_returns_grounded_answer_with_tier_breakdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw = self._seed(tmpdir)
            os.environ["BLACK_ALBION_DATA_DIR"] = str(raw)
            try:
                from backend.app.main import create_app

                app = create_app()
                client = TestClient(app)
                resp = client.post(
                    "/query",
                    json={
                        "question": "Why has the Winchcombe corridor remained important?",
                        "k": 5,
                        "include_tiers": ["I", "II", "III"],
                        "generate_answer": True,
                    },
                )
                self.assertEqual(200, resp.status_code)
                body = resp.json()
                self.assertEqual(2, body["document_count"])
                self.assertGreaterEqual(body["evidence_count"], 1)
                self.assertIn("Winchcombe Corridor", body["answer"])
                self.assertIn("tier_breakdown", body)
                self.assertEqual(
                    sum(body["tier_breakdown"].values()),
                    body["evidence_count"],
                )
                # System prompt should carry the tier doctrine
                self.assertIn("Tier I", body["prompts"]["system_prompt"])
            finally:
                os.environ.pop("BLACK_ALBION_DATA_DIR", None)

    def test_query_with_tier_filter_excludes_speculative(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw = self._seed(tmpdir)
            os.environ["BLACK_ALBION_DATA_DIR"] = str(raw)
            try:
                from backend.app.main import create_app

                app = create_app()
                client = TestClient(app)
                resp = client.post(
                    "/query",
                    json={
                        "question": "bright fort pineal",
                        "k": 5,
                        "include_tiers": ["I"],
                        "generate_answer": False,
                    },
                )
                self.assertEqual(200, resp.status_code)
                body = resp.json()
                # No Tier III speculative evidence should make it through
                for item in body["evidence"]:
                    self.assertNotEqual("III", item["tier"])
                self.assertEqual(0, body["tier_breakdown"]["tier_iii"])
            finally:
                os.environ.pop("BLACK_ALBION_DATA_DIR", None)

    def test_query_returns_no_evidence_marker_when_corpus_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw = Path(tmpdir) / "raw"
            raw.mkdir()
            (raw / "empty.json").write_text("[]", encoding="utf-8")
            os.environ["BLACK_ALBION_DATA_DIR"] = str(raw)
            try:
                from backend.app.main import create_app

                app = create_app()
                client = TestClient(app)
                resp = client.post(
                    "/query",
                    json={
                        "question": "Anything about Glevum?",
                        "k": 3,
                        "include_tiers": ["I", "II", "III"],
                        "generate_answer": True,
                    },
                )
                self.assertEqual(200, resp.status_code)
                body = resp.json()
                self.assertEqual(0, body["evidence_count"])
                self.assertIn("No grounded evidence", body["answer"])
            finally:
                os.environ.pop("BLACK_ALBION_DATA_DIR", None)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
