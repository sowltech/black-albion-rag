# Changelog

## v0.6.0 — Promotion Readiness Engine

Release date: 2026-06-13

v0.6.0 adds a deterministic, read-only Promotion Readiness Engine for
candidate claim review. It classifies candidate claims into
operator-readable readiness states without promoting, approving, or
writing anything into canonical ledgers.

### Added

- Read-only promotion readiness classifier in
  `backend/app/promotion_readiness.py`.
- Candidate-level and claim-level readiness rollups for quarantined /
  reviewed candidate rows.
- New dashboard **Promotion Readiness** panel.
- Missing source, blocked identifier, exact-text blocker, corrected
  wording, and Tier III-only display.
- Explicit dashboard lock language:
  "Read-only promotion readiness", "Does not approve promotion",
  "Does not write canonical ledgers", and "Promotion requires separate
  operator-approved commit".
- Safety handling for York/Eburacum review states: Claims 1–4 as
  nearly ready for operator review, Claim 5 blocked on accession /
  identifier verification, Claim 6 blocked on exact Latin / RIB /
  object verification, Claim 7 ready only for corrected BGS wording
  review, and Claim 8 as Tier III-only.
- Safety handling for Gloucestershire/Egypt Tier III material and the
  Gemini quarantine row so neither can become promotable from the
  readiness engine.
- New unit coverage for promotion readiness classification and
  non-promotion guarantees.
- New live smoke probes for the Promotion Readiness dashboard panel.
- Safety hardening for blocked claims with draft corrected wording:
  corrected wording can be surfaced for review, but cannot make a
  blocked claim promotable.
- Negative no-promotion tests proving there is no direct "promote now"
  readiness state and no dashboard approve/promote form action.
- Dashboard lock-language hardening for canonical promotion lock,
  corrected wording availability, blocked identifiers, and Tier
  III-only containment.
- Canonical ledger non-mutation guarantee remains enforced; the
  Promotion Readiness Engine reads candidate metadata and supplemental
  review text only.

### Safety Guarantees

- No canonical writes.
- No promotion actions.
- No approve or promote buttons.
- No canonical write endpoint.
- No inference of `canonical_ingestion_allowed: true`.
- No inference of `promotion_commit_allowed: true`.
- Tier III claims never return a promotable readiness state.
- Corrected wording remains draft-only.
- Promotion still requires a separate operator-approved commit.
- v0.5.0 Source Verification remains intact.

## v0.5.0 — Source Verification Engine

Release date: 2026-06-13

v0.5.0 adds a deterministic source verification engine and a new read-only
Source Verification dashboard panel. The engine classifies candidate-claim
evidence references into seven tiers and aggregates per-row verification
status without ever approving or promoting anything into the canonical
ledgers.

### Added

- Added deterministic source-strength classification.
- Added read-only Source Verification dashboard panel.
- Added source-tier visibility for candidate review items.
- Maintains no-promotion/no-canonical-write guarantees.
- Added unit and smoke coverage for source verification.
- New `backend/app/source_verification.py` module exposing
  `SOURCE_TIERS`, `SOURCE_TIER_WEIGHT`, `classify_source_strength()`,
  and `summarize_claim_verification()`. The seven evidence tiers are
  `primary_source`, `institutional_source`,
  `reputable_secondary_source`, `weak_secondary_source`,
  `orientation_only`, `speculative_only`, and `no_source`.
- `classify_source_strength()` returns `source_tier`, `confidence`,
  `reason`, `promotion_weight`, and `requires_operator_review`. Examples:
  The London Gazette → `primary_source`; National Archives Discovery →
  `institutional_source`; National Army Museum / Imperial War Museums /
  Soldiers of Gloucestershire Museum / Royal Wessex Yeomanry / Army
  Museums Ogilby Trust → `institutional_source`; The Long, Long Trail
  → `reputable_secondary_source`; Wikipedia → `orientation_only`;
  Tier III / "Amenta" / "Back-Badge Sensory Vector" / "Trans-Continental
  Grid" / "counter-intelligence" → `speculative_only`; missing URL +
  missing name → `no_source`.
- `summarize_claim_verification()` returns `strongest_source_tier`,
  `source_count`, per-tier counts, and a `verification_status` of
  `verified_primary`, `institutionally_supported`,
  `partially_supported`, `orientation_only`, `speculative_only`,
  `unsourced`, `requires_correction`, or `blocked`.
- Source Verification panel in `/dashboard` rendering the explicit
  lock statements "Read-only source verification", "Source scoring
  does not approve promotion", and "Promotion still requires a
  separate operator-approved commit". Per-candidate rows show
  `candidate_id`, `review_status`, `verification_status`,
  `strongest_source_tier`, the eight per-tier counts,
  `requires_correction_count`, `canonical_ingestion_allowed`,
  and `promotion_commit_allowed`. Items are ordered highest
  verification strength first, then `candidate_id`. Empty-state
  message: `No source verification records available.`
- New live smoke probes for the Source Verification panel:
  `dashboard_source_verification`,
  `dashboard_source_verification_intro`,
  `dashboard_source_verification_no_approve`,
  `dashboard_source_verification_candidate`.
- Added read-only Per-Claim Source Verification dashboard panel.
- Breaks candidate verification into per-claim source strength summaries.
- Surfaces primary, institutional, secondary, orientation-only,
  speculative-only, and no-source counts per claim.
- Keeps per-claim scoring separate from promotion approval.
- Adds CI/smoke coverage for per-claim verification visibility.
- `backend/app/source_verification.py` extended with
  `extract_claim_sections_from_review()` (splits a worksheet
  markdown by `### Claim N` headings) and
  `summarize_per_claim_verification()` (runs the engine on each
  section's URLs; injects a speculative_only source when Tier III
  tokens appear in the section text; flips Claim 6 to
  `verification_status: blocked` when the row carries
  `claim_6_tier_i_allowed: false`).
- `_per_claim_source_verification_summary()` in `backend/app/main.py`
  walks every candidate row with a `source_review_file`, runs the
  per-claim engine, and emits one dashboard row per claim sorted by
  `candidate_id` then `claim_number`. Empty-state message:
  `No per-claim verification records available.`
- New live smoke probes for the Per-Claim Source Verification panel:
  `dashboard_per_claim_verification`,
  `dashboard_per_claim_verification_intro`,
  `dashboard_per_claim_verification_claim2`,
  `dashboard_per_claim_verification_primary`,
  `dashboard_per_claim_verification_speculative`.
- Added read-only Source Strength Summary dashboard panel.
- Summarises evidence-tier counts across candidate and claim review records.
- Surfaces primary, institutional, secondary, orientation-only,
  speculative-only, no-source, correction, and blocked totals.
- Keeps source scoring separate from promotion approval.
- Adds CI/smoke coverage for source strength visibility.
- New `summarize_source_strength_queue()` aggregator in
  `backend/app/source_verification.py` that rolls up per-candidate
  and per-claim items into total counts (`total_candidates_reviewed`,
  `total_claims_reviewed`, the seven per-tier counts,
  `requires_correction_count`, `blocked_count`) plus a health
  summary (`strongest_available_tier`, `weakest_detected_tier`,
  `candidates_with_primary_sources`, `candidates_with_no_sources`,
  `candidates_with_speculative_only_material`,
  `candidates_blocked_from_promotion`). Pure / stateless / reads no
  files.
- New `_source_strength_summary()` wiring helper in
  `backend/app/main.py` that feeds the existing Source Verification
  and Per-Claim Source Verification item lists into the aggregator
  without re-walking the candidate ledger.
- Source Strength Summary panel rendered inside `/dashboard` with
  the three explicit lock statements ("Read-only source strength
  summary", "Evidence scoring does not approve promotion",
  "Promotion still requires a separate operator-approved commit")
  and two subsections: **Totals** and **Health Summary**. Empty
  state message: `No source strength records available.`
- New live smoke probes for the Source Strength Summary panel:
  `dashboard_source_strength_summary`,
  `dashboard_source_strength_intro`,
  `dashboard_source_strength_primary`,
  `dashboard_source_strength_correction`.
- Added quarantined York/Eburacum intake record
  `cand_york_eburacum_059` for the Ivory Bangle Lady / Sycamore
  Terrace / Vale of York geology candidate.
- Added York/Eburacum raw intake artifact:
  `research/intake/york_eburacum_ivory_bangle_raw.md`.
- Added York/Eburacum intake review note:
  `research/intake/york_eburacum_ivory_bangle_review.md`.
- Added York/Eburacum source review worksheet:
  `research/intake/york_eburacum_ivory_bangle_source_review.md`.
- Added York/Eburacum operator review packet:
  `research/intake/york_eburacum_ivory_bangle_operator_packet.md`.
- Attached source-review notes for York/Eburacum Claims 1-7 without
  promoting any candidate material into canonical ledgers:
  - Claim 1: Sycamore Terrace / Roman York burial source attachment.
  - Claim 2: ivory bracelets / high-status grave goods source attachment.
  - Claim 3: isotope testing / strontium / oxygen evidence source
    attachment.
  - Claim 4: African or North African ancestry / origin interpretation
    documented with careful wording and no overstatement of exact
    birthplace, ethnicity, or modern race category.
  - Claim 5: accession verification attempted; `YORYM : 1996.115`
    remains unverified and blocked.
  - Claim 6: "Vivas in Deo" / inscription / bone mount has partial
    support for the English rendering and broad object context; exact
    Latin / RIB / accession evidence remains unresolved and blocked.
  - Claim 7: BGS-supported geology wording added; unsupported hydrology,
    aquifer, basin, and fault phrases remain blocked.
- Added explicit York/Eburacum Tier III containment:
  - Claim 8 remains `speculative_lens_only`.
  - `canonical_data_allowed: false`.
  - `tier_i_promotion_allowed: false`.
  - `promotion_path: none`.
  - Amenta / jet-ivory capacitor / fluvial siphon loop /
    counter-intelligence / `system_lock` vocabulary remains
    non-canonical interpretive material only.
- Candidate queue now includes `cand_gemini_share_002`,
  `cand_gloucestershire_egypt_058`, and `cand_york_eburacum_059`.
- Approval Queue, Promotion Blockers, Approval Evidence Links,
  Canonical Ledger Integrity, and System Checks panels remain intact
  alongside the v0.5.0 Source Verification panels.

### Verified

- `cand_gloucestershire_egypt_058` surfaces with
  `verification_status: verified_primary`,
  `strongest_source_tier: primary_source` (London Gazette URL
  attached for Claim 2), `primary_source_count >= 1`,
  `institutional_source_count >= 1` (NAM / IWM / Soldiers of
  Gloucestershire Museum / RWY / AMOT), and
  `speculative_only_count >= 1` (Claim 6 Tier III lens). The row
  remains `canonical_ingestion_allowed: false` and
  `promotion_commit_allowed: false`.
- `cand_york_eburacum_059` is held at the operator review gate with
  `canonical_ingestion_allowed: false`,
  `promotion_commit_allowed: false`, and an operator packet prepared.
- York/Eburacum Claims 1-4 are `partial_sources_attached` and
  `nearly_ready` for careful operator review only.
- York/Eburacum Claim 5 remains blocked on direct accession / archive
  verification for `YORYM : 1996.115`.
- York/Eburacum Claim 6 remains blocked on exact Latin / RIB /
  accession verification while preserving partial support for the
  English inscription rendering and broad bone-mount context.
- York/Eburacum Claim 7 is nearly ready only for corrected
  BGS-supported geology wording; unsupported hydrology / fault
  phrases remain blocked.
- York/Eburacum Claim 8 remains Tier III speculative-only with no
  Tier I promotion path.
- Canonical ledgers unchanged (sites 8 / claims 90 / modules 14 /
  sources 71).
- No canonical ledger promotion occurred.
- `python3 -m json.tool data/raw/black_albion_candidate_claims.json`
  passed.
- `bash scripts/smoke_live_uvicorn.sh` passed.
- `bash scripts/validate_enterprise_gpt_os.sh` passed.
- `python3 -m pytest -q` 78 passed.
- `python3 -m compileall -q backend` passed.
- `git diff --check` / `git diff --cached --check` clean.
- Secret-pattern scan clean.

## v0.4.0 — Approval Queue

Release date: 2026-06-10

v0.4.0 extends the v0.3.0 Operator Dashboard with a read-only Approval Queue
panel that surfaces every candidate intake row currently held behind the
operator approval gate.

### Added

- Added read-only approval queue dashboard panel.
- Surfaces candidates requiring operator approval.
- Keeps promotions blocked from dashboard.
- Maintains canonical ledger protection.
- Surfaces, per candidate:
  - `candidate_id`, `review_status`
  - `operator_approval_required`, `operator_review_ready`
  - `canonical_ingestion_allowed`, `promotion_commit_allowed`
  - `operator_packet_file`, `operator_approval_draft`
  - `tier_iii_contamination_check`, `claim_6_promotion_path`
  - `risk_level`, `promotion_blocked_reason`
- Renders the explicit panel statements:
  - "Read-only approval queue"
  - "No promotion occurs from this dashboard"
  - "Promotion requires a separate operator-approved commit"
- New live smoke probes: `dashboard_approval_queue`,
  `dashboard_approval_queue_candidate`,
  `dashboard_approval_queue_separate_commit`,
  `dashboard_approval_queue_count`.
- New `tests/test_health.py` assertions covering the Approval Queue panel
  contract.
- Added deterministic approval queue ordering: highest `risk_level` first
  (`high` → `medium` → `low` → `unknown`), then `operator_review_ready`
  true before false, then `candidate_id` alphabetically; sort is stable.
- Added approval queue item count rendered as `Approval queue items: N`.
- Added empty-state messaging for no pending approvals:
  `No candidates currently require operator approval.` The panel stays
  visible when the queue is empty.
- Added read-only Promotion Blockers panel.
- Surfaces why candidate items cannot yet be promoted.
- Keeps promotion blocked from the dashboard.
- Adds CI/smoke coverage for blocker visibility.
- Promotion Blockers panel surfaces per-candidate blocker bullets such
  as `canonical ingestion blocked`, `promotion commit blocked`,
  `operator approval required`, `promotion requires separate commit`,
  `final_decision: …`, `more sources required`,
  `tier_iii_contamination_check: …`, `claim 6 blocked from Tier I`,
  and `claim 6 Tier I promotion path: none`. Items are ordered by
  highest `blocker_count` first, then `candidate_id`. Empty-state
  message: `No promotion blockers detected.`
- New live smoke probes for the Promotion Blockers panel:
  `dashboard_promotion_blockers`,
  `dashboard_promotion_blockers_intro`,
  `dashboard_promotion_blockers_canonical`,
  `dashboard_promotion_blockers_commit`.
- Added read-only Approval Evidence Links panel.
- Surfaces intake, source review, operator packet, and approval draft paths.
- Keeps evidence navigation separate from approval/promote actions.
- Adds CI/smoke coverage for evidence-trail visibility.
- Approval Evidence Links panel surfaces, per candidate, the
  `raw_artifact`, `review_note`, `source_review_file`,
  `operator_packet_file`, `operator_approval_draft`,
  `operator_approval_template`, `intake_workflow`,
  `canonical_ingestion_allowed`, and `promotion_commit_allowed`
  paths/values. Items are ordered candidates-with-packet first,
  then candidates-with-source-review, then `candidate_id`.
  Empty-state message: `No approval evidence links available.`
- New live smoke probes for the Approval Evidence Links panel:
  `dashboard_evidence_links`, `dashboard_evidence_links_intro`,
  `dashboard_evidence_links_packet`,
  `dashboard_evidence_links_draft`.
- Added read-only Canonical Ledger Integrity panel.
- Surfaces canonical ledger counts for sites, claims, modules, and sources.
- Confirms dashboard write access and canonical promotion are disabled.
- Adds CI/smoke coverage for ledger-integrity visibility.
- Canonical Ledger Integrity panel renders the four canonical ledger
  paths and counts (`sites: 8`, `claims: 90`, `modules: 14`,
  `sources: 71`), each with a `status` of `ok` / `missing` /
  `invalid_json` / `unexpected_shape`. Lock statements rendered:
  "Read-only canonical ledger integrity",
  "Dashboard write access: disabled",
  "Canonical promotion from dashboard: disabled",
  "Promotion requires a separate operator-approved commit",
  and "Operator approval required before promotion: true". Cross-
  reference governance counts (`Approval queue items`, `Blocked
  candidates`, `Evidence-bearing candidates`) are surfaced verbatim
  from the sibling panels for traceability.
- New live smoke probes for the Canonical Ledger Integrity panel:
  `dashboard_canonical_integrity`,
  `dashboard_canonical_integrity_intro`,
  `dashboard_canonical_integrity_write_lock`,
  `dashboard_canonical_integrity_promotion_lock`,
  `dashboard_canonical_integrity_sites_path`.

### Verified

- `cand_gloucestershire_egypt_058` appears in the panel with all required
  read-only fields and no promotion action surface.
- Canonical ledgers untouched (sites 8 / claims 90 / modules 14 / sources
  71).
- `python3 -m json.tool data/raw/black_albion_candidate_claims.json` clean.
- `bash scripts/smoke_live_uvicorn.sh` 25 probes pass.
- `bash scripts/validate_enterprise_gpt_os.sh` PASS.
- `python3 -m pytest -q` 48 passed.
- `python3 -m compileall -q backend` exit 0.
- `git diff --check` / `git diff --cached --check` clean.
- Secret-pattern scan clean.

## v0.3.0 — Operator Dashboard

Release date: 2026-06-10

v0.3.0 adds a read-only browser-accessible operator dashboard on top of
the existing Black Albion RAG FastAPI backend.

### Added

- Read-only `/dashboard` route.
- Dashboard health/status panel.
- Module/site/claim/document counts.
- Endpoint links panel.
- Browser search form using existing search behavior.
- Browser query form using existing query behavior.
- Supporting matches shown in query results.
- Release/version status panel sourced from `CHANGELOG.md`.
- Repo Estate panel sourced from `REPO_ESTATE_AUDIT.md`.
- Source / Intake Review panel.
- System Checks panel.
- Dashboard smoke-test probes.

### Verified

- `/dashboard` returns `200`.
- `/dashboard?q=Winchcombe` returns `200` and shows Search Results.
- `/dashboard?query=What%20is%20Winchcombe` returns `200` and shows Query Result.
- Live smoke test now checks 22 probes.
- Enterprise GPT OS Validation workflow passes.
- Live Uvicorn Smoke workflow passes.
- Python tests pass: 48 tests.
- Backend compile check passes.
- Secret-pattern scan clean.
- Working tree clean before push.
- `main` aligned with `origin/main` after push.

### Current Dashboard Panels

- Operator Dashboard.
- Release / Version Status.
- Repo Estate.
- Source / Intake Review.
- System Checks.
- Search Results.
- Query Result.
- Enterprise GPT OS summary.

### Non-Goals Still Respected

- No authentication yet.
- No database migration.
- No heavy frontend framework.
- No editing/deleting/admin actions.
- No autonomous agent actions.
- No paid API integration.
- Read-only dashboard contract preserved.

### Next Candidates

- Improve dashboard layout/readability.
- Add dedicated `/dashboard/search` route if needed.
- Add dedicated `/dashboard/query` route if needed.
- Add dashboard docs/screenshots.
- Add v0.3.0 release once the dashboard contract is stable.

## v0.2 — Governed Runtime Proof

Release date: 2026-06-09

### Added

- Enterprise GPT OS documentation pack.
- Enterprise GPT OS index/navigation page.
- Machine-readable `manifest.yaml` control layer.
- Manifest validator.
- Machine-readable eval cases.
- Eval runner.
- Project-level validation wrapper.
- GitHub Actions governance validation workflow.
- Live uvicorn smoke test script.
- GitHub Actions live uvicorn smoke workflow.

### Verified

- Enterprise GPT OS Validation workflow passed.
- Live Uvicorn Smoke workflow passed.
- FastAPI app boots under uvicorn.
- Live endpoint probes pass.
- Unit tests pass.
- Backend compile check passes.
- Secret-pattern scan clean.
- Working tree clean.
- `main` aligned with `origin/main`.

### Current CI Gates

- Enterprise GPT OS Validation.
- Live Uvicorn Smoke.

### Milestone Meaning

BLACK ALBION RAG v0.2 establishes governed runtime proof for the project. The
repo now has CI-enforced governance validation for the Enterprise GPT OS control
layer and CI-enforced live API runtime proof for the FastAPI service.

This means future changes are checked both for governance-control integrity and
for live application boot/probe behavior before they are accepted on `main`.
