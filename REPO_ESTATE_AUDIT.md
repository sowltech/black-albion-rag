# Repo Estate Audit — June 2026

## Executive Summary

- Total repos found: 46
- COMPLETE / WORKING: 1
- MOSTLY WORKING: 19
- PARTIAL: 21
- STALE: 1
- BROKEN / NEEDS ATTENTION: 3
- UNKNOWN: 1

## Current Gold Standard

`black-albion-rag` is the current gold-standard repo because it has:

- Clean working tree.
- Synced GitHub `main`.
- README.
- CHANGELOG.
- Passing tests.
- Backend compile check.
- Live uvicorn smoke test.
- Enterprise GPT OS governance pack.
- Manifest validator.
- Eval runner.
- Local validation wrapper.
- GitHub Actions governance validation.
- GitHub Actions live runtime smoke test.

## Top 5 Strongest Repos

1. `black-albion-rag`
   - Status: COMPLETE / WORKING.
   - Why it matters: Current reference implementation for governed, tested,
     documented, CI-enforced repo quality.
   - Recommended next action: Protect, keep clean, and tag `v0.2`.

2. `sowltech-shinobi-orca`
   - Status: MOSTLY WORKING.
   - Why it matters: Strong security/governance repo with CI, tests, smoke
     assets, and documented operational structure.
   - Recommended next action: Verify current CI/test status and add release
     notes if missing.

3. `loopguard-engine`
   - Status: MOSTLY WORKING.
   - Why it matters: Approval-gated execution engine with tests, CI, README,
     and a clear Python package structure.
   - Recommended next action: Run tests, add changelog, and document current
     validation command.

4. `assetsourced`
   - Status: MOSTLY WORKING.
   - Why it matters: Local-first MVP with README, CI, tests, Docker entrypoint,
     and smoke assets.
   - Recommended next action: Run tests, add release notes, and confirm CI.

5. `gcde-repo-v1`
   - Status: MOSTLY WORKING.
   - Why it matters: Governance/demo repo with tests, CI, Makefile, Dockerfile,
     and README.
   - Recommended next action: Run tests, add changelog, and document smoke or
     validation proof.

## Top 5 Repos Needing Attention

1. `OMNI-CORE` — dirty working tree
   - Issue: Modified `CLAUDE.md`.
   - Risk: Governance or routing instructions may be locally changed but not
     captured in Git.
   - Recommended next action: Review the diff, then commit, stash, or discard
     intentionally.

2. `stepc-purchasegate` — dirty working tree
   - Issue: Modified `docker-compose.yml`.
   - Risk: Runtime ports or service wiring may differ from committed state.
   - Recommended next action: Review the compose diff and decide whether the
     port change belongs in Git.

3. `phoenix-voice-agent-engine.archived-2026-05-17` — dirty archived repo
   - Issue: Archived repo still has uncommitted changes.
   - Risk: Archive cannot be trusted as a fixed snapshot.
   - Recommended next action: Either commit an archive-final state or mark the
     repo as intentionally abandoned.

4. `Sirius Nexus` vault — untracked daily files
   - Issue: Untracked `2026-06-08.md` and `2026-06-09.md`.
   - Risk: Witness or daily notes may be outside version control.
   - Recommended next action: Decide whether these are real vault records and
     commit only intended documentation changes.

5. `claude-skills` — diverged from upstream, behind 40 / ahead 1
   - Issue: Local branch has one local commit and is 40 commits behind upstream.
   - Risk: Fork drift makes future updates and merges risky.
   - Recommended next action: Decide whether this is a maintained fork,
     rebase/sync if needed, or archive the local copy.

## Repo Status Table

| Status | Repo | Path | Branch | Sync | Tests | CI | Docs | Smoke | Stack | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| COMPLETE / WORKING | black-albion-rag | `/Users/siriusnexus/Documents/Sirius Nexus/black-albion-rag` | main | synced | pass recently | pass | README + CHANGELOG | yes | Python/FastAPI | Protect/tag v0.2 |
| MOSTLY WORKING | assetsourced | `/Users/siriusnexus/assetsourced` | main | synced | exists | yes | README | yes | Python | Run tests, add changelog |
| MOSTLY WORKING | gcde-repo-v1 | `/Users/siriusnexus/gcde-repo-v1` | main | synced | exists | yes | README | unclear | Python | Run tests, add release notes |
| MOSTLY WORKING | loopguard-engine | `/Users/siriusnexus/loopguard-engine` | main | synced | exists | yes | README | unclear | Python | Run tests, add changelog |
| MOSTLY WORKING | sowltech-shinobi-orca | `/Users/siriusnexus/sowltech-shinobi-orca` | main | synced | exists | yes | README | yes | Python | Verify CI/test status |
| PARTIAL | Sirius Nexus | `/Users/siriusnexus/Documents/Sirius Nexus` | main | synced | exists | no | weak | no | Vault/Python | Review untracked files |
| BROKEN / NEEDS ATTENTION | OMNI-CORE | `/Users/siriusnexus/OMNI-CORE` | main | synced | no | no | README | no | Python/docs | Resolve dirty `CLAUDE.md` |
| STALE | claude-skills | `/Users/siriusnexus/claude-skills` | main | behind 40, ahead 1 | exists | yes | README + CHANGELOG | yes | Python | Decide fork strategy |
| BROKEN / NEEDS ATTENTION | stepc-purchasegate | `/Users/siriusnexus/stepc-purchasegate` | feature/initial-scaffold | no remote | exists | no | README | no | Python | Resolve dirty compose file |
| UNKNOWN | ozone | `/Users/siriusnexus/ozone` | main | synced | no | yes | no README | no | unclear | Inspect or archive |
| PARTIAL | crown-etn | `/Users/siriusnexus/crown-etn` | main | synced | exists | yes | no README | no | Python/docs | Add README/entrypoint |
| PARTIAL | moneycylium-engine | `/Users/siriusnexus/moneycylium-engine` | main | ahead 1 | exists | no | no README | no | Python | Add README, push/park commit |
| PARTIAL | obsidian-command-listener | `/Users/siriusnexus/obsidian-command-listener` | main | synced | exists | no | no README | no | Node/TS | Clean dirty tree |
| PARTIAL | serpent-language-engine | `/Users/siriusnexus/serpent-language-engine` | main | ahead 1 | exists | no | no README | no | Python | Add README/CI proof |
| PARTIAL | sol-voltron-core | `/Users/siriusnexus/sol-voltron-core` | main | ahead 3 | exists | no | no README | no | Python | Document and push/park |
| PARTIAL | sovereign-router | `/Users/siriusnexus/sovereign-router` | main | ahead 1 | exists | no | no README | no | Python | Add README and validation |
| PARTIAL | stepc | `/Users/siriusnexus/stepc` | main | ahead 1 | exists | no | no README | no | Python | Add README/CI |
| MOSTLY WORKING | phoenix-revival-os | `/Users/siriusnexus/phoenix-revival-os` | main | synced | exists | yes | README | no | Python | Run tests, add release notes |
| MOSTLY WORKING | phoenix-voice-agent | `/Users/siriusnexus/phoenix-voice-agent` | main | synced | exists | yes | README | no | Node | Run tests, add changelog |
| MOSTLY WORKING | st-elmo | `/Users/siriusnexus/st-elmo` | main | synced | exists | yes | README | no | Python | Run tests, add smoke proof |

## Priority 1 — Protect / Keep Clean

- `black-albion-rag`
- `sowltech-shinobi-orca`
- `loopguard-engine`
- `assetsourced`
- `gcde-repo-v1`

Rule: Do not make experimental changes directly in these repos without a clear
branch, validation plan, and rollback path.

## Priority 2 — Finish Next

- `nexus-prime-trading-engine`
- `phoenix-agent-registry`
- `phoenix-revival-os`
- `sowltalk-core`
- `st-elmo`

Standard graduation checklist:

- README present.
- Clear entrypoint.
- Tests pass.
- Smoke test or validation script exists.
- CI workflow exists.
- CHANGELOG or release notes exists.
- Working tree clean.
- `main` synced with `origin`.
- Secret scan clean.

## Priority 3 — Archive Later

- `phoenix-voice-agent-engine.archived-2026-05-17`
- `ozone`
- Older duplicate or superseded local-only repos after review.

## Priority 4 — Investigate / Clean

- `Sirius Nexus`
- `OMNI-CORE`
- `stepc-purchasegate`
- `claude-skills`
- Repos with local `.env` files before public pushes.

## Secret and Environment File Guardrail

Run these before publishing, pushing sensitive repos, or preparing a release:

```bash
git status --short
git check-ignore .env
git ls-files | grep -E '(^|/)\.env$' || true
```

Local `.env` files are acceptable only if ignored. Committed `.env` files are
dangerous because they can expose live secrets, credentials, internal URLs, or
production configuration. `.env.example` files are usually acceptable, but they
should still be scanned before public release.

## Graduation Standard

A repo graduates to COMPLETE / WORKING only when it has:

- Clean working tree.
- Synced with GitHub or intentional ahead commit.
- README or clear usage instructions.
- Clear app/script entrypoint.
- Tests pass or documented reason tests are not applicable.
- Smoke test or validation script.
- CI workflow where appropriate.
- Secret scan clean.
- CHANGELOG or release notes for milestone repos.

## Next 3 Actions

1. Protect and tag `black-albion-rag` v0.2.
2. Clean dirty repos: `Sirius Nexus`, `OMNI-CORE`, `stepc-purchasegate`, and
   archived voice agent.
3. Pick 3 mostly-working repos and graduate them to Black Albion standard.
