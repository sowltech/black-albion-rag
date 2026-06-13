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
                self.assertIn(
                    "Unreleased — v0.7.0 Operator Decision Packet Engine",
                    body,
                )
                self.assertIn(
                    "v0.6.0 — Promotion Readiness Engine",
                    (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8"),
                )
                self.assertIn(
                    "v0.5.0 — Source Verification Engine",
                    (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8"),
                )
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
                # v0.4.0 Approval Queue panel — read-only, no promotion path
                self.assertIn("Approval Queue", body)
                self.assertIn("Read-only approval queue", body)
                self.assertIn("No promotion occurs from this dashboard", body)
                self.assertIn(
                    "Promotion requires a separate operator-approved commit",
                    body,
                )
                self.assertIn("cand_gloucestershire_egypt_058", body)
                self.assertIn(
                    "gloucestershire_egypt_operator_packet.md", body
                )
                self.assertIn(
                    "gloucestershire_egypt_operator_approval_draft.md", body
                )
                self.assertIn("canonical_ingestion_allowed", body)
                self.assertIn("promotion_commit_allowed", body)
                self.assertIn("tier_iii_contamination_check", body)
                # v0.4.0 Approval Queue display contract: count label
                self.assertIn("Approval queue items:", body)
                # v0.4.0 Promotion Blockers panel contract
                self.assertIn("Promotion Blockers", body)
                self.assertIn("Read-only blocker summary", body)
                self.assertIn(
                    "This panel explains why promotion is blocked", body
                )
                self.assertIn("Blocked candidates:", body)
                self.assertIn("canonical ingestion blocked", body)
                self.assertIn("promotion commit blocked", body)
                self.assertIn("operator approval required", body)
                self.assertIn("claim 6", body)
                # v0.4.0 Approval Evidence Links panel
                self.assertIn("Approval Evidence Links", body)
                self.assertIn("Read-only evidence trail", body)
                self.assertIn(
                    "Evidence links do not approve promotion", body
                )
                self.assertIn(
                    "Promotion still requires a separate operator-approved commit",
                    body,
                )
                self.assertIn("Evidence-bearing candidates:", body)
                self.assertIn("gloucestershire_egypt_intercept_raw.md", body)
                self.assertIn("gloucestershire_egypt_source_review.md", body)
                self.assertIn("gloucestershire_egypt_operator_packet.md", body)
                self.assertIn(
                    "gloucestershire_egypt_operator_approval_draft.md", body
                )
                self.assertIn("operator_promotion_approval_template.md", body)
                self.assertIn("docs/intake-review-workflow.md", body)
                # v0.4.0 Canonical Ledger Integrity panel
                self.assertIn("Canonical Ledger Integrity", body)
                self.assertIn("Read-only canonical ledger integrity", body)
                self.assertIn("Dashboard write access: disabled", body)
                self.assertIn(
                    "Canonical promotion from dashboard: disabled", body
                )
                self.assertIn(
                    "Operator approval required before promotion: true", body
                )
                self.assertIn("data/raw/black_albion_sites.json", body)
                self.assertIn("data/raw/black_albion_claims.json", body)
                self.assertIn("data/raw/black_albion_modules.json", body)
                self.assertIn("data/raw/black_albion_sources.json", body)
                self.assertIn("sites: <strong>8</strong>", body)
                self.assertIn("claims: <strong>90</strong>", body)
                self.assertIn("modules: <strong>14</strong>", body)
                self.assertIn("sources: <strong>71</strong>", body)
                # v0.5.0 Source Verification panel
                self.assertIn("Source Verification", body)
                self.assertIn("Read-only source verification", body)
                self.assertIn(
                    "Source scoring does not approve promotion", body
                )
                # cand_gloucestershire_egypt_058 surfaces in the panel and at
                # least one of the expected tier names must be present.
                self.assertIn("cand_gloucestershire_egypt_058", body)
                self.assertTrue(
                    any(
                        tier in body
                        for tier in (
                            "primary_source",
                            "institutional_source",
                            "speculative_only",
                            "no_source",
                        )
                    ),
                    "Source Verification panel must surface at least one tier name",
                )
                # v0.6.0 Promotion Readiness panel
                self.assertIn("Promotion Readiness", body)
                self.assertIn("Read-only promotion readiness", body)
                self.assertIn("Does not approve promotion", body)
                self.assertIn("Does not write canonical ledgers", body)
                self.assertIn("cand_york_eburacum_059", body)
                self.assertIn("YORYM : 1996.115", body)
                self.assertIn("exact Latin / RIB", body)
                self.assertIn("Tier III-only", body)
                self.assertIn("canonical_promotion_locked", body)
                self.assertIn("corrected_wording_count", body)
                self.assertIn("corrected_wording_available", body)
                self.assertIn("ready_for_corrected_wording_review", body)
                self.assertIn("separate operator-approved commit", body)
                # v0.7.0 Operator Decision Packets panel
                self.assertIn("Operator Decision Packets", body)
                self.assertIn("Read-only operator decision packets", body)
                self.assertIn("Does not approve decisions", body)
                self.assertIn("Decision labels are recommendations only", body)
                self.assertIn("approve_for_corrected_wording_review", body)
                self.assertIn("needs_more_source_work", body)
                self.assertIn("tier_iii_only", body)
                for forbidden in (
                    ">Approve<",
                    ">Promote<",
                    ">Edit<",
                    ">Sign<",
                    'action="/approve',
                    'action="/promote',
                    'action="/edit',
                    'action="/sign',
                    'name="approve"',
                    'name="promote"',
                    'name="signature"',
                    "promote_now",
                ):
                    self.assertNotIn(forbidden, body)
            finally:
                os.environ.pop("BLACK_ALBION_DATA_DIR", None)

    def test_promotion_readiness_york_claims_classify_safely(self) -> None:
        from backend.app.promotion_readiness import (
            summarize_promotion_readiness_queue,
        )

        candidates = json.loads(
            (PROJECT_ROOT / "data/raw/black_albion_candidate_claims.json").read_text(
                encoding="utf-8"
            )
        )
        queue = summarize_promotion_readiness_queue(candidates, PROJECT_ROOT)
        york = next(
            item
            for item in queue["candidates"]
            if item["candidate_id"] == "cand_york_eburacum_059"
        )
        by_number = {claim["claim_number"]: claim for claim in york["claims"]}

        for number in (1, 2, 3, 4):
            self.assertEqual(
                "nearly_ready_for_operator_review",
                by_number[number]["readiness"],
            )
        self.assertEqual(
            "blocked_unverified_identifier",
            by_number[5]["readiness"],
        )
        self.assertEqual(
            "blocked_exact_text_unverified",
            by_number[6]["readiness"],
        )
        self.assertEqual(
            "ready_for_corrected_wording_review",
            by_number[7]["readiness"],
        )
        self.assertTrue(by_number[7]["corrected_wording_available"])
        self.assertEqual("tier_iii_only", by_number[8]["readiness"])
        self.assertFalse(by_number[8]["canonical_ingestion_allowed"])
        self.assertFalse(by_number[8]["promotion_commit_allowed"])

    def test_promotion_readiness_never_promotes_quarantine_candidates(self) -> None:
        from backend.app.promotion_readiness import (
            summarize_promotion_readiness_queue,
        )

        candidates = json.loads(
            (PROJECT_ROOT / "data/raw/black_albion_candidate_claims.json").read_text(
                encoding="utf-8"
            )
        )
        queue = summarize_promotion_readiness_queue(candidates, PROJECT_ROOT)
        candidates_by_id = {
            item["candidate_id"]: item for item in queue["candidates"]
        }

        gemini = candidates_by_id["cand_gemini_share_002"]
        self.assertEqual([], gemini["claims"])
        self.assertEqual(0, gemini["nearly_ready_count"])

        glos = candidates_by_id["cand_gloucestershire_egypt_058"]
        glos_tier_iii = next(
            claim for claim in glos["claims"] if claim["claim_number"] == 6
        )
        self.assertEqual("tier_iii_only", glos_tier_iii["readiness"])

        for candidate in queue["candidates"]:
            self.assertFalse(candidate["canonical_ingestion_allowed"])
            self.assertFalse(candidate["promotion_commit_allowed"])
            for claim in candidate["claims"]:
                self.assertFalse(claim["canonical_ingestion_allowed"])
                self.assertFalse(claim["promotion_commit_allowed"])
                if claim["tier_iii_containment"]:
                    self.assertEqual("tier_iii_only", claim["readiness"])

    def test_promotion_readiness_negative_safety_rules(self) -> None:
        from backend.app.promotion_readiness import classify_claim_readiness

        defaulted = classify_claim_readiness(
            {
                "candidate_claim_id": "cand_claim_safety_001",
                "claim_text": "Generic sourced claim.",
                "source_status": "partial_sources_attached",
            }
        )
        self.assertFalse(defaulted["canonical_ingestion_allowed"])
        self.assertFalse(defaulted["promotion_commit_allowed"])

        tier_iii = classify_claim_readiness(
            {
                "candidate_claim_id": "cand_claim_safety_008",
                "claim_text": "Tier III symbolic lens.",
                "tier_candidate": "III",
                "source_status": "speculative_lens_only",
                "promotion_readiness": "nearly_ready",
            }
        )
        self.assertEqual("tier_iii_only", tier_iii["readiness"])

        blocked_with_wording = classify_claim_readiness(
            {
                "candidate_claim_id": "cand_claim_safety_005",
                "claim_text": "YORYM : 1996.115 accession identifier.",
                "source_status": "partial_sources_attached",
                "promotion_readiness": "not_ready",
                "accession_identifier_status": "unverified",
            },
            worksheet_text=(
                "### Claim 5 — Accession\n"
                "- **corrected_claim_text**: draft only\n"
            ),
        )
        self.assertEqual(
            "blocked_unverified_identifier",
            blocked_with_wording["readiness"],
        )
        self.assertTrue(blocked_with_wording["corrected_wording_available"])

        for result in (defaulted, tier_iii, blocked_with_wording):
            self.assertNotIn(
                result["readiness"],
                {
                    "promote_now",
                    "approved_for_promotion",
                    "ready_for_canonical_promotion",
                },
            )

    def test_operator_decision_packets_map_current_candidates_safely(self) -> None:
        from backend.app.operator_decisions import summarize_operator_decision_queue
        from backend.app.promotion_readiness import (
            summarize_promotion_readiness_queue,
        )

        candidates = json.loads(
            (PROJECT_ROOT / "data/raw/black_albion_candidate_claims.json").read_text(
                encoding="utf-8"
            )
        )
        readiness = summarize_promotion_readiness_queue(candidates, PROJECT_ROOT)
        decisions = summarize_operator_decision_queue(readiness)
        by_candidate = {
            item["candidate_id"]: item for item in decisions["candidates"]
        }
        york = by_candidate["cand_york_eburacum_059"]
        york_claims = {claim["claim_number"]: claim for claim in york["claims"]}

        for number in (1, 2, 3, 4):
            self.assertEqual(
                "approve_for_corrected_wording_review",
                york_claims[number]["decision_label"],
            )
            self.assertFalse(york_claims[number]["future_promotion_path_possible"])

        self.assertEqual(
            "needs_more_source_work",
            york_claims[5]["decision_label"],
        )
        self.assertEqual(
            "needs_more_source_work",
            york_claims[6]["decision_label"],
        )
        self.assertEqual(
            "approve_for_corrected_wording_review",
            york_claims[7]["decision_label"],
        )
        self.assertEqual("tier_iii_only", york_claims[8]["decision_label"])

        glos = by_candidate["cand_gloucestershire_egypt_058"]
        glos_claim_6 = next(
            claim for claim in glos["claims"] if claim["claim_number"] == 6
        )
        self.assertEqual("tier_iii_only", glos_claim_6["decision_label"])

        gemini = by_candidate["cand_gemini_share_002"]
        self.assertEqual([], gemini["claims"])
        self.assertFalse(gemini["has_future_promotion_candidates"])

        self.assertEqual(0, decisions["total_ready_for_separate_promotion_commit"])
        for candidate in decisions["candidates"]:
            self.assertFalse(candidate["has_future_promotion_candidates"])
            for claim in candidate["claims"]:
                self.assertTrue(claim["decision_is_recommendation_only"])
                self.assertFalse(claim["executed"])
                self.assertIn("reason", claim)
                self.assertIn("evidence_basis", claim)
                self.assertIn("source_gaps", claim)
                self.assertIn("corrected_wording_available", claim)
                self.assertIn("required_approval", claim)
                self.assertFalse(claim["canonical_promotion_allowed"])

    def test_operator_decision_promotion_label_requires_explicit_metadata(self) -> None:
        from backend.app.operator_decisions import classify_operator_decision

        nearly_ready_without_approval = classify_operator_decision(
            {
                "claim_id": "claim_without_approval",
                "claim_number": 1,
                "readiness": "nearly_ready_for_operator_review",
                "canonical_ingestion_allowed": True,
                "promotion_commit_allowed": True,
                "operator_approved": False,
            }
        )
        self.assertEqual(
            "approve_for_corrected_wording_review",
            nearly_ready_without_approval["decision_label"],
        )

        explicitly_approved = classify_operator_decision(
            {
                "claim_id": "claim_with_approval",
                "claim_number": 1,
                "readiness": "nearly_ready_for_operator_review",
                "canonical_ingestion_allowed": True,
                "promotion_commit_allowed": True,
                "operator_approved": True,
            }
        )
        self.assertEqual(
            "ready_for_separate_promotion_commit",
            explicitly_approved["decision_label"],
        )
        self.assertTrue(explicitly_approved["future_promotion_path_possible"])
        self.assertTrue(explicitly_approved["canonical_promotion_allowed"])

    def test_classify_source_london_gazette_url_is_primary(self) -> None:
        from backend.app.source_verification import classify_source_strength

        result = classify_source_strength(
            source_name="The London Gazette",
            source_url="https://www.thegazette.co.uk/London/issue/25356/page/2278",
        )
        self.assertEqual(result["source_tier"], "primary_source")

    def test_classify_source_national_army_museum_is_institutional(self) -> None:
        from backend.app.source_verification import classify_source_strength

        result = classify_source_strength(
            source_url="https://www.nam.ac.uk/explore/28th-north-gloucestershire-regiment-foot",
        )
        self.assertEqual(result["source_tier"], "institutional_source")

    def test_classify_source_imperial_war_museums_is_institutional(self) -> None:
        from backend.app.source_verification import classify_source_strength

        result = classify_source_strength(
            source_url="https://www.iwm.org.uk/collections/item/object/30076245",
        )
        self.assertEqual(result["source_tier"], "institutional_source")

    def test_classify_source_soldiers_of_gloucestershire_is_institutional(self) -> None:
        from backend.app.source_verification import classify_source_strength

        result = classify_source_strength(
            source_url="https://soldiersofglos.com/visit-us/",
        )
        self.assertEqual(result["source_tier"], "institutional_source")

    def test_classify_source_long_long_trail_is_reputable_secondary(self) -> None:
        from backend.app.source_verification import classify_source_strength

        result = classify_source_strength(
            source_url=(
                "https://www.longlongtrail.co.uk/army/regiments-and-corps/"
                "the-british-yeomanry-regiments-of-1914-1918/"
                "gloucestershire-yeomanry-royal-gloucestershire-hussars/"
            ),
        )
        self.assertEqual(result["source_tier"], "reputable_secondary_source")

    def test_classify_source_wikipedia_is_orientation_only(self) -> None:
        from backend.app.source_verification import classify_source_strength

        result = classify_source_strength(
            source_url="https://en.wikipedia.org/wiki/Percival_Marling",
        )
        self.assertEqual(result["source_tier"], "orientation_only")

    def test_classify_source_tier_iii_text_is_speculative_only(self) -> None:
        from backend.app.source_verification import classify_source_strength

        result = classify_source_strength(
            source_name="Back-Badge Sensory Vector / Amenta Subsurface Core Extraction",
            source_url="",
            source_notes="Tier III speculative_lens_only",
        )
        self.assertEqual(result["source_tier"], "speculative_only")
        self.assertTrue(result["requires_operator_review"])

    def test_classify_source_missing_returns_no_source(self) -> None:
        from backend.app.source_verification import classify_source_strength

        result = classify_source_strength("", "", "")
        self.assertEqual(result["source_tier"], "no_source")
        self.assertTrue(result["requires_operator_review"])

    def test_summarize_claim_verification_prefers_primary_when_present(self) -> None:
        from backend.app.source_verification import summarize_claim_verification

        summary = summarize_claim_verification(
            [
                {"name": "London Gazette"},
                {"url": "https://www.nam.ac.uk/explore/test"},
                {"url": "https://en.wikipedia.org/wiki/X"},
            ]
        )
        self.assertEqual(summary["strongest_source_tier"], "primary_source")
        self.assertEqual(summary["verification_status"], "verified_primary")
        self.assertEqual(summary["primary_source_count"], 1)
        self.assertEqual(summary["institutional_source_count"], 1)
        self.assertEqual(summary["orientation_only_count"], 1)

    def test_summarize_claim_verification_empty_returns_unsourced(self) -> None:
        from backend.app.source_verification import summarize_claim_verification

        summary = summarize_claim_verification([])
        self.assertEqual(summary["verification_status"], "unsourced")
        self.assertEqual(summary["strongest_source_tier"], "no_source")

    def test_source_verification_panel_surfaces_gloucestershire(self) -> None:
        from backend.app.main import _source_verification_summary

        summary = _source_verification_summary()
        ids = [item["candidate_id"] for item in summary["items"]]
        self.assertIn("cand_gloucestershire_egypt_058", ids)
        glos = next(
            item
            for item in summary["items"]
            if item["candidate_id"] == "cand_gloucestershire_egypt_058"
        )
        self.assertEqual(glos["strongest_source_tier"], "primary_source")
        self.assertEqual(glos["verification_status"], "verified_primary")
        self.assertGreaterEqual(glos["primary_source_count"], 1)
        self.assertGreaterEqual(glos["institutional_source_count"], 1)
        self.assertGreaterEqual(glos["speculative_only_count"], 1)
        self.assertFalse(glos["canonical_ingestion_allowed"])
        self.assertFalse(glos["promotion_commit_allowed"])

    def test_extract_claim_sections_from_gloucestershire_review(self) -> None:
        from backend.app.source_verification import extract_claim_sections_from_review

        path = Path(__file__).resolve().parents[1] / (
            "research/intake/gloucestershire_egypt_source_review.md"
        )
        text = path.read_text(encoding="utf-8")
        sections = extract_claim_sections_from_review(text)
        numbers = [section["claim_number"] for section in sections]
        self.assertEqual(numbers, [1, 2, 3, 4, 5, 6])
        titles = {
            section["claim_number"]: section["claim_title"]
            for section in sections
        }
        self.assertIn("1801", titles[1])
        self.assertIn("Marling", titles[2])
        self.assertIn("Royal Gloucestershire Hussars", titles[3])
        self.assertIn("Cathedral", titles[5])
        self.assertIn("Tier III speculative lens", titles[6])

    def test_per_claim_panel_surfaces_gloucestershire_claims(self) -> None:
        from backend.app.main import _per_claim_source_verification_summary

        summary = _per_claim_source_verification_summary()
        glos_rows = [
            item
            for item in summary["items"]
            if item["candidate_id"] == "cand_gloucestershire_egypt_058"
        ]
        self.assertEqual(len(glos_rows), 6)
        by_claim = {row["claim_number"]: row for row in glos_rows}

        # Claim 2 — Marling VC: London Gazette primary URL is in the worksheet
        # so strongest tier must be primary_source and the requires_correction
        # flag must be true because the worksheet records the correction.
        claim2 = by_claim[2]
        self.assertEqual(claim2["strongest_source_tier"], "primary_source")
        self.assertGreaterEqual(claim2["primary_source_count"], 1)
        self.assertTrue(claim2["requires_correction"])

        # Claim 6 — Tier III speculative lens: must be blocked / speculative.
        claim6 = by_claim[6]
        self.assertEqual(claim6["strongest_source_tier"], "speculative_only")
        self.assertEqual(claim6["verification_status"], "blocked")
        self.assertGreaterEqual(claim6["speculative_only_count"], 1)

        # No claim is promoted from the dashboard view.
        for row in glos_rows:
            self.assertFalse(row["canonical_ingestion_allowed"])
            self.assertFalse(row["promotion_commit_allowed"])

    def test_dashboard_renders_per_claim_panel(self) -> None:
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
                            "summary": "Tier I baseline.",
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
                body = client.get("/dashboard").text
                self.assertIn("Per-Claim Source Verification", body)
                self.assertIn("Read-only per-claim verification", body)
                self.assertIn(
                    "Per-claim scoring does not approve promotion", body
                )
                self.assertIn("cand_gloucestershire_egypt_058", body)
                self.assertIn("Claim 1", body)
                self.assertIn("Claim 2", body)
                self.assertIn("Claim 6", body)
                self.assertIn("primary_source", body)
                self.assertIn("speculative_only", body)
                self.assertIn("requires_correction", body)
                # v0.5.0 Source Strength Summary panel contract.
                self.assertIn("Source Strength Summary", body)
                self.assertIn("Read-only source strength summary", body)
                self.assertIn(
                    "Evidence scoring does not approve promotion", body
                )
                self.assertIn("total candidates reviewed", body)
                self.assertIn("total claims reviewed", body)
                self.assertIn("institutional_source", body)
                self.assertIn("blocked", body)
                self.assertIn("strongest_available_tier", body)
                self.assertIn("weakest_detected_tier", body)
                self.assertIn("candidates_with_primary_sources", body)
                self.assertIn("candidates_blocked_from_promotion", body)
            finally:
                os.environ.pop("BLACK_ALBION_DATA_DIR", None)

    def test_summarize_source_strength_queue_aggregates_counts(self) -> None:
        from backend.app.source_verification import (
            summarize_source_strength_queue,
        )

        per_candidate = [
            {
                "candidate_id": "cand_a",
                "verification_status": "verified_primary",
                "strongest_source_tier": "primary_source",
                "source_count": 3,
                "primary_source_count": 1,
                "institutional_source_count": 1,
                "speculative_only_count": 1,
            },
            {
                "candidate_id": "cand_b",
                "verification_status": "unsourced",
                "strongest_source_tier": "no_source",
                "source_count": 0,
                "primary_source_count": 0,
                "institutional_source_count": 0,
                "speculative_only_count": 0,
            },
        ]
        per_claim = [
            {
                "candidate_id": "cand_a",
                "verification_status": "verified_primary",
                "primary_source_count": 1,
                "institutional_source_count": 2,
                "reputable_secondary_count": 0,
                "weak_source_count": 0,
                "orientation_only_count": 0,
                "speculative_only_count": 0,
                "no_source_count": 0,
                "requires_correction": False,
            },
            {
                "candidate_id": "cand_a",
                "verification_status": "requires_correction",
                "primary_source_count": 0,
                "institutional_source_count": 1,
                "reputable_secondary_count": 1,
                "weak_source_count": 0,
                "orientation_only_count": 1,
                "speculative_only_count": 0,
                "no_source_count": 0,
                "requires_correction": True,
            },
            {
                "candidate_id": "cand_a",
                "verification_status": "blocked",
                "primary_source_count": 0,
                "institutional_source_count": 0,
                "reputable_secondary_count": 0,
                "weak_source_count": 0,
                "orientation_only_count": 0,
                "speculative_only_count": 1,
                "no_source_count": 0,
                "requires_correction": True,
            },
        ]
        summary = summarize_source_strength_queue(per_candidate, per_claim)
        self.assertEqual(summary["total_candidates_reviewed"], 2)
        self.assertEqual(summary["total_claims_reviewed"], 3)
        self.assertEqual(summary["primary_source_count"], 1)
        self.assertEqual(summary["institutional_source_count"], 3)
        self.assertEqual(summary["reputable_secondary_count"], 1)
        self.assertEqual(summary["orientation_only_count"], 1)
        self.assertEqual(summary["speculative_only_count"], 1)
        self.assertEqual(summary["requires_correction_count"], 2)
        self.assertEqual(summary["blocked_count"], 1)
        self.assertEqual(summary["strongest_available_tier"], "primary_source")
        self.assertEqual(
            summary["weakest_detected_tier"], "speculative_only"
        )
        self.assertEqual(summary["candidates_with_primary_sources"], 1)
        self.assertEqual(summary["candidates_with_no_sources"], 1)
        self.assertEqual(
            summary["candidates_with_speculative_only_material"], 1
        )
        self.assertEqual(summary["candidates_blocked_from_promotion"], 1)

    def test_summarize_source_strength_queue_empty_inputs(self) -> None:
        from backend.app.source_verification import (
            summarize_source_strength_queue,
        )

        summary = summarize_source_strength_queue([], [])
        self.assertEqual(summary["total_candidates_reviewed"], 0)
        self.assertEqual(summary["total_claims_reviewed"], 0)
        self.assertEqual(summary["primary_source_count"], 0)
        self.assertEqual(summary["strongest_available_tier"], "no_source")
        self.assertEqual(summary["weakest_detected_tier"], "no_source")
        self.assertEqual(summary["candidates_blocked_from_promotion"], 0)

    def test_canonical_ledger_integrity_lock_statements_are_canonical(self) -> None:
        from backend.app.main import CANONICAL_LEDGER_INTEGRITY_LOCK_STATEMENTS

        self.assertEqual(
            CANONICAL_LEDGER_INTEGRITY_LOCK_STATEMENTS,
            (
                "Read-only canonical ledger integrity",
                "Dashboard write access: disabled",
                "Canonical promotion from dashboard: disabled",
                "Promotion requires a separate operator-approved commit",
            ),
        )

    def test_canonical_ledger_status_classifies_each_state(self) -> None:
        from backend.app.main import _canonical_ledger_status

        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # missing
            missing_path = base / "missing.json"
            missing = _canonical_ledger_status(missing_path)
            self.assertEqual(missing["status"], "missing")
            self.assertEqual(missing["count"], 0)

            # invalid_json
            bad_path = base / "bad.json"
            bad_path.write_text("{not-json", encoding="utf-8")
            bad = _canonical_ledger_status(bad_path)
            self.assertEqual(bad["status"], "invalid_json")
            self.assertEqual(bad["count"], 0)

            # ok (list)
            good_path = base / "good.json"
            good_path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
            good = _canonical_ledger_status(good_path)
            self.assertEqual(good["status"], "ok")
            self.assertEqual(good["count"], 3)

            # ok (dict with records list)
            envelope_path = base / "envelope.json"
            envelope_path.write_text(
                json.dumps({"records": [{}, {}, {}, {}]}),
                encoding="utf-8",
            )
            envelope = _canonical_ledger_status(envelope_path)
            self.assertEqual(envelope["status"], "ok")
            self.assertEqual(envelope["count"], 4)

            # unexpected_shape
            wrong_path = base / "wrong.json"
            wrong_path.write_text("42", encoding="utf-8")
            wrong = _canonical_ledger_status(wrong_path)
            self.assertEqual(wrong["status"], "unexpected_shape")
            self.assertEqual(wrong["count"], 0)

    def test_canonical_ledger_integrity_summary_carries_expected_counts(self) -> None:
        from backend.app.main import _canonical_ledger_integrity_summary

        summary = _canonical_ledger_integrity_summary(
            approval_queue_count=2,
            promotion_blockers_count=2,
            approval_evidence_count=2,
        )
        rows = {row["key"]: row for row in summary["rows"]}
        self.assertEqual(rows["sites"]["count"], 8)
        self.assertEqual(rows["claims"]["count"], 90)
        self.assertEqual(rows["modules"]["count"], 14)
        self.assertEqual(rows["sources"]["count"], 71)
        for key in ("sites", "claims", "modules", "sources"):
            self.assertEqual(rows[key]["status"], "ok")
        self.assertEqual(summary["approval_queue_count"], 2)
        self.assertEqual(summary["promotion_blockers_count"], 2)
        self.assertEqual(summary["approval_evidence_count"], 2)
        self.assertIn(
            "Promotion requires a separate operator-approved commit",
            summary["lock_statements"],
        )

    def test_approval_evidence_links_sort_key_is_deterministic(self) -> None:
        from backend.app.main import _approval_evidence_links_sort_key

        items = [
            {"candidate_id": "cand_d", "operator_packet_file": "", "source_review_file": ""},
            {"candidate_id": "cand_a", "operator_packet_file": "packet.md", "source_review_file": "sr.md"},
            {"candidate_id": "cand_c", "operator_packet_file": "", "source_review_file": "sr.md"},
            {"candidate_id": "cand_b", "operator_packet_file": "packet.md", "source_review_file": ""},
        ]
        ordered = sorted(items, key=_approval_evidence_links_sort_key)
        self.assertEqual(
            [item["candidate_id"] for item in ordered],
            # candidates with packet first (a, b), then with source_review
            # only (c), then candidates with neither (d).
            ["cand_a", "cand_b", "cand_c", "cand_d"],
        )

    def test_approval_evidence_links_empty_message_is_canonical(self) -> None:
        from backend.app.main import APPROVAL_EVIDENCE_LINKS_EMPTY_MESSAGE

        self.assertEqual(
            APPROVAL_EVIDENCE_LINKS_EMPTY_MESSAGE,
            "No approval evidence links available.",
        )

    def test_approval_evidence_links_summary_surfaces_gloucestershire(self) -> None:
        from backend.app.main import _approval_evidence_links_summary

        summary = _approval_evidence_links_summary()
        ids = [item["candidate_id"] for item in summary["items"]]
        self.assertIn("cand_gloucestershire_egypt_058", ids)
        glos = next(
            item
            for item in summary["items"]
            if item["candidate_id"] == "cand_gloucestershire_egypt_058"
        )
        self.assertEqual(
            glos["operator_packet_file"],
            "research/intake/gloucestershire_egypt_operator_packet.md",
        )
        self.assertEqual(
            glos["operator_approval_draft"],
            "research/intake/gloucestershire_egypt_operator_approval_draft.md",
        )
        self.assertEqual(
            glos["source_review_file"],
            "research/intake/gloucestershire_egypt_source_review.md",
        )
        self.assertEqual(
            glos["raw_artifact"],
            "research/intake/gloucestershire_egypt_intercept_raw.md",
        )
        self.assertFalse(glos["canonical_ingestion_allowed"])
        self.assertFalse(glos["promotion_commit_allowed"])
        self.assertEqual(
            summary["approval_template_path"],
            "docs/templates/operator_promotion_approval_template.md",
        )
        self.assertEqual(
            summary["workflow_doc"], "docs/intake-review-workflow.md"
        )
        self.assertEqual(
            summary["item_count_label"],
            f"Evidence-bearing candidates: {summary['item_count']}",
        )

    def test_promotion_blockers_for_row_detects_each_blocker(self) -> None:
        from backend.app.main import _promotion_blockers_for_row

        row = {
            "candidate_id": "cand_x",
            "canonical_ingestion_allowed": False,
            "promotion_commit_allowed": False,
            "operator_approval_required": True,
            "promotion_requires_separate_commit": True,
            "final_decision": "more_sources_required",
            "required_action": "source_hunting",
            "tier_iii_contamination_check": "passed",
            "claim_6_tier_i_allowed": False,
            "claim_6_promotion_path": "none",
        }
        blockers = _promotion_blockers_for_row(row)
        self.assertIn("canonical ingestion blocked", blockers)
        self.assertIn("promotion commit blocked", blockers)
        self.assertIn("operator approval required", blockers)
        self.assertIn("promotion requires separate commit", blockers)
        self.assertIn("final_decision: more_sources_required", blockers)
        self.assertIn("more sources required", blockers)
        self.assertIn("tier_iii_contamination_check: passed", blockers)
        self.assertIn("claim 6 blocked from Tier I", blockers)
        self.assertIn("claim 6 Tier I promotion path: none", blockers)

    def test_promotion_blockers_for_row_clean_row_returns_empty(self) -> None:
        from backend.app.main import _promotion_blockers_for_row

        row = {
            "candidate_id": "cand_clear",
            "canonical_ingestion_allowed": True,
            "promotion_commit_allowed": True,
            "operator_approval_required": False,
            "promotion_requires_separate_commit": False,
        }
        self.assertEqual(_promotion_blockers_for_row(row), [])

    def test_promotion_blockers_sort_key_is_deterministic(self) -> None:
        from backend.app.main import _promotion_blockers_sort_key

        items = [
            {"candidate_id": "cand_charlie", "blocker_count": 1},
            {"candidate_id": "cand_alpha", "blocker_count": 4},
            {"candidate_id": "cand_bravo", "blocker_count": 4},
            {"candidate_id": "cand_delta", "blocker_count": 2},
        ]
        ordered = sorted(items, key=_promotion_blockers_sort_key)
        self.assertEqual(
            [item["candidate_id"] for item in ordered],
            ["cand_alpha", "cand_bravo", "cand_delta", "cand_charlie"],
        )

    def test_promotion_blockers_empty_message_is_canonical(self) -> None:
        from backend.app.main import PROMOTION_BLOCKERS_EMPTY_MESSAGE

        self.assertEqual(
            PROMOTION_BLOCKERS_EMPTY_MESSAGE,
            "No promotion blockers detected.",
        )

    def test_promotion_blockers_summary_includes_gloucestershire(self) -> None:
        from backend.app.main import _promotion_blockers_summary

        summary = _promotion_blockers_summary()
        self.assertIn("items", summary)
        ids = [item["candidate_id"] for item in summary["items"]]
        self.assertIn("cand_gloucestershire_egypt_058", ids)
        glos = next(
            item
            for item in summary["items"]
            if item["candidate_id"] == "cand_gloucestershire_egypt_058"
        )
        self.assertIn("canonical ingestion blocked", glos["blockers"])
        self.assertIn("promotion commit blocked", glos["blockers"])
        self.assertIn("operator approval required", glos["blockers"])
        self.assertIn("claim 6 blocked from Tier I", glos["blockers"])
        self.assertIn("claim 6 Tier I promotion path: none", glos["blockers"])
        self.assertEqual(
            summary["item_count_label"],
            f"Blocked candidates: {summary['item_count']}",
        )

    def test_approval_queue_sort_key_is_deterministic(self) -> None:
        from backend.app.main import _approval_queue_sort_key

        items = [
            {"candidate_id": "cand_bravo", "risk_level": "low", "operator_review_ready": True},
            {"candidate_id": "cand_alpha", "risk_level": "high", "operator_review_ready": False},
            {"candidate_id": "cand_charlie", "risk_level": "high", "operator_review_ready": True},
            {"candidate_id": "cand_delta", "risk_level": "medium", "operator_review_ready": False},
            {"candidate_id": "cand_echo", "risk_level": "", "operator_review_ready": True},
        ]
        ordered = sorted(items, key=_approval_queue_sort_key)
        order = [item["candidate_id"] for item in ordered]
        # high (review_ready true) -> high (review_ready false)
        # -> medium -> low -> unknown
        self.assertEqual(
            order,
            [
                "cand_charlie",  # high, review_ready true
                "cand_alpha",    # high, review_ready false
                "cand_delta",    # medium
                "cand_bravo",    # low
                "cand_echo",     # unknown risk
            ],
        )
        # Stable on equal keys: re-sorting same input yields same output.
        again = sorted(items, key=_approval_queue_sort_key)
        self.assertEqual(
            [item["candidate_id"] for item in again], order
        )

    def test_approval_queue_empty_message_is_canonical(self) -> None:
        from backend.app.main import APPROVAL_QUEUE_EMPTY_MESSAGE

        self.assertEqual(
            APPROVAL_QUEUE_EMPTY_MESSAGE,
            "No candidates currently require operator approval.",
        )

    def test_approval_queue_summary_carries_count_and_empty_message(self) -> None:
        from backend.app.main import (
            APPROVAL_QUEUE_EMPTY_MESSAGE,
            _approval_queue_summary,
        )

        summary = _approval_queue_summary()
        self.assertIn("item_count", summary)
        self.assertEqual(summary["item_count"], len(summary["items"]))
        self.assertEqual(
            summary["item_count_label"],
            f"Approval queue items: {summary['item_count']}",
        )
        self.assertEqual(summary["empty_message"], APPROVAL_QUEUE_EMPTY_MESSAGE)
        self.assertEqual(
            summary["promotion_note"],
            "Promotion requires a separate operator-approved commit",
        )
        # Items are emitted in the deterministic sort order.
        from backend.app.main import _approval_queue_sort_key

        self.assertEqual(
            summary["items"],
            sorted(summary["items"], key=_approval_queue_sort_key),
        )

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
