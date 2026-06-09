# Changelog

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
