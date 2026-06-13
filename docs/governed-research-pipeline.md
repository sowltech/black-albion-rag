# Governed Research Pipeline

This document explains the Black Albion RAG review pipeline as of
`v0.7.0 — Operator Decision Packet Engine`.

## Purpose

Black Albion RAG separates source-backed canonical evidence from quarantined
candidate material. The system lets an operator inspect candidate claims,
score their sources, classify their readiness, and see recommended decision
labels without writing to canonical ledgers.

## Pipeline Diagram

```text
Candidate intake
  - pasted notes
  - Gemini / Claude / manual material
  - operator-supplied research leads
        |
        v
Quarantine
  - raw intake artifact
  - review note
  - candidate ledger row
        |
        v
Source verification
  - source tier scoring
  - institutional / primary / secondary / weak / speculative checks
        |
        v
Per-claim source verification
  - claim-by-claim attachments
  - correction notes
  - unresolved gaps
        |
        v
Promotion readiness
  - nearly ready
  - missing sources
  - blocked identifiers
  - exact text unresolved
  - Tier III only
        |
        v
Operator decision packets
  - approve_for_corrected_wording_review
  - needs_more_source_work
  - do_not_promote
  - tier_iii_only
  - ready_for_separate_promotion_commit
        |
        v
Separate operator-approved promotion commit only
```

## Candidate Versus Canonical Data

Canonical ledgers are the load-bearing data files:

- `data/raw/black_albion_sites.json`
- `data/raw/black_albion_claims.json`
- `data/raw/black_albion_modules.json`
- `data/raw/black_albion_sources.json`

Candidate material lives outside those ledgers until explicitly promoted in a
future commit. Candidate rows and review files can describe proposed claims,
source gaps, corrections, and operator packet status, but they are not
canonical evidence.

Current canonical ledger counts:

| Ledger | Count |
|---|---:|
| Sites | 8 |
| Claims | 90 |
| Modules | 14 |
| Sources | 71 |

## Source Verification Flow

The source verification layer scores evidence references without promoting
anything. It distinguishes:

- primary sources
- institutional sources
- reputable secondary sources
- weak sources
- orientation-only sources
- speculative-only material
- missing sources

Source scoring is a review aid. It does not approve promotion and does not
write canonical ledgers.

## Promotion Readiness Flow

The promotion readiness layer classifies candidate claims into operator-facing
states such as:

- `nearly_ready_for_operator_review`
- `blocked_missing_sources`
- `blocked_unverified_identifier`
- `blocked_exact_text_unverified`
- `ready_for_corrected_wording_review`
- `tier_iii_only`
- `not_ready`
- `unknown`

Corrected wording can be surfaced for review, but corrected wording is not
canonical promotion.

## Operator Decision Flow

The operator decision layer maps readiness into canonical decision labels:

- `approve_for_corrected_wording_review`
- `needs_more_source_work`
- `do_not_promote`
- `tier_iii_only`
- `ready_for_separate_promotion_commit`

Only `ready_for_separate_promotion_commit` may imply a future promotion path,
and only when explicit metadata permits it. Even then, the system does not
execute the promotion. A separate operator-approved commit is required.

## Tier III Containment

Tier III speculative, mythic, symbolic, or creative-worldbuilding material is
allowed as clearly labelled review context. It must not be presented as Tier I
history and must not enter canonical ledgers as evidence.

The dashboard and decision engine keep Tier III material non-promotable.

## Safety Model

The v0.7.0 safety baseline is:

- Read-only dashboard governance.
- No automatic promotion.
- No approve/promote buttons.
- No dashboard write actions.
- No canonical write endpoints.
- No operator signature actions.
- Decision labels are recommendations only.
- Corrected wording review is not promotion.
- Canonical promotion requires a separate operator-approved commit.
- Candidate material remains separate from canonical ledgers until explicitly
  promoted.

## Validation

Use the standard local gate before any release or promotion work:

```bash
python3 -m json.tool data/raw/black_albion_candidate_claims.json
bash scripts/smoke_live_uvicorn.sh
bash scripts/validate_enterprise_gpt_os.sh
python3 -m pytest -q
python3 -m compileall -q backend
git diff --check
git diff --cached --check
```
