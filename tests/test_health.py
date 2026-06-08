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


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
