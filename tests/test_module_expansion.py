"""Validation tests for the expanded Black Albion module grid."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.retriever import BlackAlbionRetriever

RAW_DIR = PROJECT_ROOT / "data" / "raw"
MODULES_PATH = RAW_DIR / "black_albion_modules.json"
CLAIMS_PATH = RAW_DIR / "black_albion_claims.json"


class ModuleExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.modules = json.loads(MODULES_PATH.read_text(encoding="utf-8"))
        cls.claims = json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))
        cls.retriever = BlackAlbionRetriever(data_dirs=[RAW_DIR])

    def test_module_ids_and_site_ids_are_unique(self) -> None:
        module_ids = [item["module_id"] for item in self.modules]
        site_ids = [item["site_id"] for item in self.modules]
        self.assertEqual(len(module_ids), len(set(module_ids)))
        self.assertEqual(len(site_ids), len(set(site_ids)))

    def test_node_053_collision_is_resolved(self) -> None:
        module_ids = {item["module_id"] for item in self.modules}
        self.assertIn("UK-RAG-MOD-053A", module_ids)
        self.assertIn("UK-RAG-MOD-053B", module_ids)
        self.assertNotIn("UK-RAG-MOD-053", module_ids)

    def test_every_module_has_all_tier_fields(self) -> None:
        for module in self.modules:
            self.assertIn("tier_i_evidence", module)
            self.assertIn("tier_ii_interpretation", module)
            self.assertIn("tier_iii_speculative_logic", module)
            self.assertIn(
                module["tier_iii_speculative_logic"]["source_status"],
                {"speculative"},
            )

    def test_tier_iii_is_never_marked_verified(self) -> None:
        for module in self.modules:
            tier_iii = module["tier_iii_speculative_logic"]
            self.assertNotEqual("verified", tier_iii.get("source_status"))
        for claim in self.claims:
            if claim.get("tier") == "III":
                self.assertNotEqual("verified", claim.get("source_status"))

    def test_all_modules_are_retrievable_by_module_id(self) -> None:
        for module in self.modules:
            results = self.retriever.search(module["module_id"], k=3)
            self.assertTrue(results, module["module_id"])
            self.assertEqual(module["module_id"], results[0].metadata.get("module_id"))

    def test_required_search_terms_find_modules(self) -> None:
        cases = {
            "Stroud": "UK-RAG-MOD-046",
            "Cirencester": "UK-RAG-MOD-052",
            "Tewkesbury": "UK-RAG-MOD-053A",
            "Hereford": "UK-RAG-MOD-053B",
            "Forest of Dean": "UK-RAG-MOD-047",
            "Cotswold Way": "UK-RAG-MOD-044",
            "Fenland": "UK-RAG-MOD-050",
            "London Oxford": "UK-RAG-MOD-049",
            "Swindon": "UK-RAG-MOD-051",
            "Gloucester radials": "UK-RAG-MOD-055",
        }
        for query, module_id in cases.items():
            results = self.retriever.search(query, k=10)
            module_ids = {item.metadata.get("module_id") for item in results}
            self.assertIn(module_id, module_ids, query)

    def test_metadata_filters_cover_required_dimensions(self) -> None:
        self.assertTrue(
            self.retriever.search(
                "Gloucestershire",
                filters={"county": "Gloucestershire"},
                k=20,
            )
        )
        self.assertTrue(
            self.retriever.search(
                "Roman villas",
                filters={"theme": "Roman villa"},
                k=20,
            )
        )
        self.assertTrue(
            self.retriever.search(
                "spring hydrology confluence",
                filters={"hydrology": "confluence"},
                k=20,
            )
        )
        self.assertTrue(
            self.retriever.search(
                "oolitic limestone",
                filters={"geology": "oolitic limestone"},
                k=20,
            )
        )
        self.assertTrue(
            self.retriever.search(
                "Ridgeway",
                filters={"route": "Ridgeway"},
                k=20,
            )
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
