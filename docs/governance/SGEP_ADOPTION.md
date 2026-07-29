# SGEP Adoption Record

## Repository

- Repository: `sowltech/black-albion-rag`
- Adoption status: `proposed`
- Canonical standard: `sowltech/OMNI-CORE@refs/tags/sgep-v1.0.0`
- Canonical path: `docs/standards/SOWLTECH_GOVERNED_ENGINEERING_PROTOCOL.md`
- Adoption scope: evidence-ledger services, agentic retrieval, APIs, validators, receipts and governed knowledge operations

## Risk tier

- Default: **Tier C** for evidence, ledger, policy, canonical-write, provenance, contradiction, security and public API changes.
- Tier B may be used for bounded non-sensitive implementation changes.
- Tier A may be used for trivial documentation outside protected governance paths.

## Existing controls remain authoritative

This adoption preserves the repository's existing policy gate, tier enforcement, evidence budgets, contradiction handling, immutable receipts, read-only boundaries, CI, smoke tests and operator approval controls.

## Local validation

Use the exact current repository commands at implementation time. The established baseline includes, where applicable:

- focused pytest suites for changed components
- full pytest suite
- `python3 -m compileall -q backend`
- enterprise validation scripts
- live Uvicorn smoke test
- `git diff --check`
- independent canaries for security, logging, evidence and policy claims

## Protected paths

Tier C handling applies by default to:

- `backend/app/agentic_loop/`
- evidence-ledger and canonical-write code
- policy, tier, budget, contradiction and receipt logic
- public API routes and response models
- authentication, secret handling and internal logging
- schemas, validators, migration logic and governance records

## Role mapping

- Architect: strongest available reasoning model or human architect
- Builder: bounded implementation model
- Test engineer: separate testing pass or independently prompted model
- Reviewer: different model or agent from the builder for the reviewed SHA
- Governor: repository policy, CI and approval controls
- Operator: Saint / authorised human operator

Providers are replaceable. Role separation, provenance and exact-SHA evidence are mandatory.

## Merge gates

1. Approved directive and risk tier.
2. Exact scope confirmed.
3. Focused and full validation complete.
4. Independent review of the exact head SHA.
5. All findings required by the directive resolved.
6. Expected-head SHA merge guard.
7. Operator approval.
8. Witness seal for material phases or releases.

## Evidence and witness

- Local hash-linked receipts remain authoritative for run reconstruction.
- Authoritative estate Witness Memory records sealed milestones.
- Review reports must record repository, PR, reviewed SHA, validation, findings and verdict.

## Approved deviations

None at adoption.

## Non-interference statement

This record introduces no automatic promotion, canonical write, merge, deployment or estate-wide enforcement. It maps SGEP to the repository without changing the sealed Elite Agentic RAG Phase 1 implementation.
