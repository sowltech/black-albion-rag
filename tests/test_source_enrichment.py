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
INVENTORY_CLAIM_IDS = {
    "claim_043_inventory",
    "claim_044_inventory",
    "claim_045_inventory",
    "claim_046_inventory",
    "claim_047_inventory",
    "claim_048_inventory",
    "claim_049_inventory",
    "claim_050_inventory",
    "claim_051_inventory",
    "claim_052_inventory",
    "claim_053a_inventory",
    "claim_053b_inventory",
    "claim_055_inventory",
    "claim_056_inventory",
}
ITEM_LEVEL_CLAIM_IDS = {
    "claim_048_staffordshire_hoard",
    "claim_048_wroxeter_viroconium",
    "claim_048_lunt_roman_fort",
    "claim_048_wrens_nest",
    "claim_048_old_oswestry",
    "claim_048_kinver_rock_houses",
    "claim_048_creswell_crags",
    "claim_048_nottingham_city_of_caves",
    "claim_048_borough_hill",
    "claim_051_avebury",
    "claim_051_silbury_hill",
    "claim_051_west_kennet_long_barrow",
    "claim_051_barbury_castle",
    "claim_051_liddington_castle",
    "claim_051_wanborough_durocornovium",
    "claim_051_uffington_white_horse",
    "claim_051_ridgeway_national_trail",
    "claim_055_great_witcombe_villa",
    "claim_055_horsbere_brook",
    "claim_055_coopers_hill_nature_reserve",
    "claim_055_framilode_frome_mouth",
    "claim_055_innsworth_arrc",
    "claim_056_oddas_chapel",
    "claim_056_st_mary_deerhurst",
    "claim_056_deerhurst_monastic_site",
    "claim_056_westminster_abbey_estate_link",
    "claim_056_mercia_mudstone_context",
}
ITEM_LEVEL_PASS_002_CLAIM_IDS = {
    "claim_048_metchley_roman_forts",
    "claim_048_wolverhampton_anglian_cross",
    "claim_051_coate_water_country_park",
    "claim_051_day_house_coate_stone_circle",
    "claim_055_coopers_hill_high_brotheridge",
    "claim_055_hardwicke_domesday_index",
    "claim_055_hawkesbury_domesday_entry",
    "claim_055_brockworth_court",
    "claim_055_brockworth_parish_history",
    "claim_055_witcombe_reservoirs_brockworth_mill",
    "claim_055_witcombe_reservoirs_modern_hydrology",
    "claim_056_deerhurst_exact_domesday_entry",
    "claim_056_apperley_local_context",
    "claim_055_056_local_geology_tewkesbury_sheet",
}


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

    def test_inventory_claims_are_at_least_partially_sourced(self) -> None:
        claims_by_id = {claim["claim_id"]: claim for claim in self.claims}
        for claim_id in INVENTORY_CLAIM_IDS:
            claim = claims_by_id[claim_id]
            self.assertIn(claim.get("source_status"), {"partial", "verified"}, claim_id)
            self.assertTrue(claim.get("source_ids"), claim_id)

    def test_verified_item_level_claims_have_sources(self) -> None:
        for claim in self.claims:
            if (
                (
                    claim["claim_id"] in ITEM_LEVEL_CLAIM_IDS
                    or claim["claim_id"] in ITEM_LEVEL_PASS_002_CLAIM_IDS
                )
                and claim.get("source_status") == "verified"
            ):
                self.assertTrue(claim.get("source_ids"), claim["claim_id"])

    def test_sourced_priority_item_level_claims_exist(self) -> None:
        claims_by_id = {claim["claim_id"]: claim for claim in self.claims}
        for claim_id in ITEM_LEVEL_CLAIM_IDS:
            self.assertIn(claim_id, claims_by_id)
            claim = claims_by_id[claim_id]
            self.assertEqual(claim.get("tier"), "I", claim_id)
            self.assertIn(claim.get("source_status"), {"partial", "verified"}, claim_id)
            self.assertTrue(claim.get("source_ids"), claim_id)

    def test_pass_002_item_level_claims_exist(self) -> None:
        claims_by_id = {claim["claim_id"]: claim for claim in self.claims}
        for claim_id in ITEM_LEVEL_PASS_002_CLAIM_IDS:
            self.assertIn(claim_id, claims_by_id)
            claim = claims_by_id[claim_id]
            self.assertEqual(claim.get("tier"), "I", claim_id)
            self.assertIn(claim.get("source_status"), {"partial", "verified"}, claim_id)
            self.assertTrue(claim.get("source_ids"), claim_id)

    def test_pass_002_documentation_exists(self) -> None:
        doc = (PROJECT_ROOT / "docs" / "black-albion-module-expansion.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Item-Level Tier I Source Pass 002", doc)
        for gap in ("Metchley", "Wolverhampton Cross", "Coate Water", "Apperley"):
            self.assertIn(gap, doc)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
