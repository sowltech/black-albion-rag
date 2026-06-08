"""Prompt builder tier-doctrine tests."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.prompt_builder import SYSTEM_PROMPT, build_prompt
from backend.app.retriever import RetrievedEvidence


class PromptBuilderTests(unittest.TestCase):
    def test_system_prompt_states_tier_doctrine(self) -> None:
        self.assertIn("Tier I", SYSTEM_PROMPT)
        self.assertIn("Tier II", SYSTEM_PROMPT)
        self.assertIn("Tier III", SYSTEM_PROMPT)
        self.assertIn("Speculatively", SYSTEM_PROMPT)
        self.assertIn("Never invent", SYSTEM_PROMPT)

    def test_user_prompt_carries_question_and_tier_tagged_citations(self) -> None:
        evidence = [
            RetrievedEvidence(
                source_file="data/raw/sites.json",
                record_id="site_001",
                title="Glevum Colonia",
                tier="I",
                score=2.0,
                excerpt="Roman colonia at Gloucester.",
            ),
            RetrievedEvidence(
                source_file="data/raw/claims.json",
                record_id="claim_speculative",
                title="Bright Fort pineal lens",
                tier="III",
                score=1.0,
                excerpt="Operator-framework interpretation.",
            ),
        ]
        prompt = build_prompt("What is Glevum?", evidence)
        self.assertIn("What is Glevum?", prompt["user_prompt"])
        self.assertIn("[1] (Tier I) Glevum Colonia", prompt["user_prompt"])
        self.assertIn("[2] (Tier III)", prompt["user_prompt"])
        self.assertEqual(SYSTEM_PROMPT, prompt["system_prompt"])

    def test_empty_evidence_produces_explicit_marker(self) -> None:
        prompt = build_prompt("Anything?", [])
        self.assertIn("(no grounded evidence retrieved)", prompt["user_prompt"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
