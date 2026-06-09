# Changelog

## Unreleased — v0.3.0 Operator Dashboard

v0.3.0 is adding a read-only browser-accessible operator dashboard on top of
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
