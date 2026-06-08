"""Quarantine intake tests for non-authoritative research shares."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RAW_INTAKE = PROJECT_ROOT / "research" / "intake" / "gemini_share_002_raw.md"
REVIEW_NOTE = PROJECT_ROOT / "research" / "intake" / "gemini_share_002_review.md"
RAW_DIR = PROJECT_ROOT / "data" / "raw"


class IntakeQuarantineTests(unittest.TestCase):
    def test_gemini_share_002_intake_files_exist(self) -> None:
        self.assertTrue(RAW_INTAKE.exists())
        self.assertTrue(REVIEW_NOTE.exists())

    def test_raw_intake_contains_tier_warning(self) -> None:
        raw = RAW_INTAKE.read_text(encoding="utf-8")
        self.assertIn("Gemini content is not Tier I evidence", raw)
        self.assertIn("fetch_status: failed_auth_walled", raw)
        self.assertIn("promoted_to_claims: false", raw)

    def test_no_verified_claim_is_gemini_sourced(self) -> None:
        claims = json.loads(
            (RAW_DIR / "black_albion_claims.json").read_text(encoding="utf-8")
        )
        for claim in claims:
            if claim.get("source_status") == "verified":
                text = " ".join(
                    str(claim.get(key, ""))
                    for key in ("claim_text", "title", "summary", "notes")
                ).lower()
                self.assertNotIn("gemini", text, claim["claim_id"])

    def test_no_source_record_treats_gemini_as_tier_i_authority(self) -> None:
        sources = json.loads(
            (RAW_DIR / "black_albion_sources.json").read_text(encoding="utf-8")
        )
        for source in sources:
            text = " ".join(
                str(source.get(key, ""))
                for key in ("source_id", "title", "author_or_body", "url", "notes")
            ).lower()
            if "gemini" in text:
                self.assertNotEqual(source.get("evidence_tier"), "I")
                self.assertNotEqual(source.get("reliability"), "high")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
