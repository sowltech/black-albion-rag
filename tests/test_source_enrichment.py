"""Source enrichment ledger integrity tests."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "data" / "raw"
VALID_SOURCE_STATUSES = {"verified", "partial", "needs_verification", "speculative"}


class SourceEnrichmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sources = json.loads(
            (RAW_DIR / "black_albion_sources.json").read_text(encoding="utf-8")
        )
        cls.claims = json.loads(
            (RAW_DIR / "black_albion_claims.json").read_text(encoding="utf-8")
        )

    def test_no_duplicate_source_ids(self) -> None:
        source_ids = [source["source_id"] for source in self.sources]
        self.assertEqual(len(source_ids), len(set(source_ids)))

    def test_no_duplicate_claim_ids(self) -> None:
        claim_ids = [claim["claim_id"] for claim in self.claims]
        self.assertEqual(len(claim_ids), len(set(claim_ids)))

    def test_claim_source_references_exist(self) -> None:
        source_ids = {source["source_id"] for source in self.sources}
        for claim in self.claims:
            for source_id in claim.get("source_ids", []):
                self.assertIn(source_id, source_ids, claim["claim_id"])

    def test_enriched_sources_reference_modules(self) -> None:
        for source in self.sources:
            self.assertTrue(source.get("supports_modules"), source["source_id"])

    def test_tier_iii_claims_are_never_verified(self) -> None:
        for claim in self.claims:
            if claim.get("tier") == "III":
                self.assertNotEqual("verified", claim.get("source_status"))

    def test_source_status_values_are_valid(self) -> None:
        for claim in self.claims:
            self.assertIn(claim.get("source_status"), VALID_SOURCE_STATUSES)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
