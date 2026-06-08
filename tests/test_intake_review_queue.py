"""Tests for the Black Albion intake review queue."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "data" / "raw"
CANDIDATE_LEDGER = RAW_DIR / "black_albion_candidate_claims.json"
WORKFLOW_DOC = PROJECT_ROOT / "docs" / "intake-review-workflow.md"
GEMINI_RAW = PROJECT_ROOT / "research" / "intake" / "gemini_share_002_raw.md"
GEMINI_REVIEW = PROJECT_ROOT / "research" / "intake" / "gemini_share_002_review.md"

ALLOWED_REVIEW_STATUSES = {
    "quarantined",
    "pending_review",
    "source_hunting",
    "rejected",
    "approved_for_source_search",
    "promoted_to_claims",
}
VALID_RISK_LEVELS = {"low", "medium", "high"}


class IntakeReviewQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidates = json.loads(CANDIDATE_LEDGER.read_text(encoding="utf-8"))

    def test_candidate_ledger_exists_and_is_array(self) -> None:
        self.assertTrue(CANDIDATE_LEDGER.exists())
        self.assertIsInstance(self.candidates, list)

    def test_candidate_ids_are_unique(self) -> None:
        candidate_ids = [candidate["candidate_id"] for candidate in self.candidates]
        self.assertEqual(len(candidate_ids), len(set(candidate_ids)))

    def test_review_status_values_are_allowed(self) -> None:
        for candidate in self.candidates:
            self.assertIn(candidate.get("review_status"), ALLOWED_REVIEW_STATUSES)

    def test_risk_level_values_are_valid(self) -> None:
        for candidate in self.candidates:
            self.assertIn(candidate.get("risk_level"), VALID_RISK_LEVELS)

    def test_gemini_candidate_is_quarantined_without_extracted_claims(self) -> None:
        gemini = self._candidate("cand_gemini_share_002")
        self.assertEqual(gemini["origin_type"], "gemini_share")
        self.assertEqual(gemini["fetch_status"], "failed_auth_walled")
        self.assertEqual(gemini["candidate_claims"], [])
        self.assertTrue(gemini["operator_approval_required"])

    def test_gemini_candidate_forbids_tier_i_sourcing(self) -> None:
        gemini = self._candidate("cand_gemini_share_002")
        forbidden = " ".join(gemini["forbidden_use"]).lower()
        self.assertIn("tier i sourcing", forbidden)
        self.assertIn("verified claim creation", forbidden)

    def test_no_candidate_promoted_without_operator_approval(self) -> None:
        for candidate in self.candidates:
            if candidate.get("review_status") == "promoted_to_claims":
                self.assertTrue(candidate.get("operator_approval_required"))
                self.assertIn("independent", " ".join(candidate.get("forbidden_use", [])).lower())

    def test_no_gemini_candidate_is_tier_i_authority(self) -> None:
        for candidate in self.candidates:
            if candidate.get("origin_type") == "gemini_share":
                self.assertNotEqual(candidate.get("review_status"), "promoted_to_claims")
                forbidden = " ".join(candidate.get("forbidden_use", [])).lower()
                self.assertIn("tier i sourcing", forbidden)

    def test_workflow_doc_exists(self) -> None:
        self.assertTrue(WORKFLOW_DOC.exists())
        doc = WORKFLOW_DOC.read_text(encoding="utf-8")
        self.assertIn("Intake cannot directly become Tier I", doc)
        self.assertIn("operator approval", doc.lower())

    def test_gemini_quarantine_files_still_exist(self) -> None:
        self.assertTrue(GEMINI_RAW.exists())
        self.assertTrue(GEMINI_REVIEW.exists())

    def _candidate(self, candidate_id: str) -> dict[str, object]:
        for candidate in self.candidates:
            if candidate.get("candidate_id") == candidate_id:
                return candidate
        raise AssertionError(f"missing candidate: {candidate_id}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
