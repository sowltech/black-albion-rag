# Changelog

## Unreleased — v0.4.0 Approval Queue

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
