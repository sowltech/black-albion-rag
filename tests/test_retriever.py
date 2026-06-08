"""Lexical retriever tests against a temp Tier-tagged corpus."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.retriever import BlackAlbionRetriever, _coerce_tier, _record_text


class RetrieverTests(unittest.TestCase):
    def _build_corpus(self, tmp: Path) -> Path:
        raw = tmp / "raw"
        raw.mkdir()
        (raw / "sites.json").write_text(
            json.dumps(
                [
                    {
                        "id": "site_winchcombe_corridor",
                        "tier": "I",
                        "title": "Winchcombe Corridor",
                        "summary": "A long-lived route linking settlement, trade, and pilgrimage.",
                        "claims": ["Route importance over centuries"],
                    },
                    {
                        "id": "site_unrelated_node",
                        "tier": "I",
                        "title": "Unrelated Node",
                        "summary": "Different topic entirely.",
                    },
                    {
                        "id": "claim_speculative",
                        "tier": "III",
                        "title": "Bright Fort as pineal metaphor",
                        "summary": "Speculative reading of Caerloyw.",
                    },
                ]
            ),
            encoding="utf-8",
        )
        return raw

    def test_search_returns_best_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw = self._build_corpus(Path(tmpdir))
            retriever = BlackAlbionRetriever(data_dirs=[raw])
            results = retriever.search("Why is the Winchcombe corridor important?", k=1)
            self.assertEqual(1, len(results))
            self.assertIn("Winchcombe", results[0].title)
            self.assertEqual("I", results[0].tier)
            self.assertGreater(results[0].score, 0)

    def test_tier_filter_excludes_speculative_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw = self._build_corpus(Path(tmpdir))
            retriever = BlackAlbionRetriever(data_dirs=[raw])
            results = retriever.search(
                "bright fort pineal",
                k=5,
                include_tiers=["I"],
            )
            # Tier III speculative match must be filtered out
            for item in results:
                self.assertNotEqual("III", item.tier)

    def test_tier_coercion_handles_legacy_labels(self) -> None:
        self.assertEqual("I", _coerce_tier("ARCHIVAL_LEDGER"))
        self.assertEqual("III", _coerce_tier("speculative"))
        self.assertEqual("I", _coerce_tier(None))

    def test_record_text_flattens_nested_fields(self) -> None:
        record = {
            "title": "Test",
            "layer_0_geology": {"mineral_strata": "chalk"},
            "themes": ["henge", "chalk-aquifer"],
        }
        text = _record_text(record)
        self.assertIn("chalk", text)
        self.assertIn("henge", text)

    def test_cache_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw = self._build_corpus(Path(tmpdir))
            cache_path = Path(tmpdir) / "index" / ".retriever_cache.pkl"
            retriever = BlackAlbionRetriever(data_dirs=[raw], cache_path=cache_path)
            self.assertTrue(cache_path.exists())
            # Second construction should reuse cache silently
            retriever2 = BlackAlbionRetriever(data_dirs=[raw], cache_path=cache_path)
            self.assertEqual(len(retriever.documents), len(retriever2.documents))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
