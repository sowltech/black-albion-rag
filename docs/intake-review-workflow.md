# Intake Review Workflow

## Purpose

The intake review workflow stores future Gemini, Claude, pasted, exported, or
manually supplied Black Albion material without allowing it to affect live Tier
I evidence, modules, claims, or source records.

Intake material is treated as quarantine research until an operator explicitly
approves independent source hunting and a later source-validation pass attaches
reputable evidence.

## Directory Layout

- `research/intake/` stores raw unreviewed or minimally reviewed intake files.
- `research/review_queue/` stores items ready for structured review.
- `research/reviewed/` stores reviewed items that produced candidate leads.
- `research/rejected/` stores unusable, unsafe, duplicate, or unsupported
  material.
- `data/raw/black_albion_candidate_claims.json` stores candidate intake
  metadata and unpromoted candidate claims.

## Candidate Claim Lifecycle

- `quarantined`: raw intake is preserved but not reviewed for content.
- `pending_review`: intake is queued for structured review.
- `source_hunting`: candidate leads are being checked against independent
  sources.
- `rejected`: material is unusable, unsupported, duplicate, or unsafe.
- `approved_for_source_search`: operator approved independent source hunting.
- `promoted_to_claims`: a later pass moved independently sourced, item-level
  claims into the live claims ledger.

## Promotion Rules

- Intake cannot directly become Tier I.
- Tier I requires independent reputable source records.
- Candidate claims must be split into item-level statements before promotion.
- Broad claims stay partial unless every item is sourced.
- Tier III must remain labelled speculative.
- AI-generated or pasted material can only suggest leads; it cannot verify
  claims.
- Live ledgers under `data/raw/black_albion_claims.json`,
  `data/raw/black_albion_modules.json`, and
  `data/raw/black_albion_sources.json` are updated only in a separate,
  explicit source-validation pass.

## Approval Gate

Operator approval is required before moving any candidate into live claims.

Approval means:

- the candidate has been reviewed;
- the claim has been reduced to item-level wording;
- independent source hunting has found reputable source records;
- Tier II and Tier III language has been separated from Tier I evidence;
- the next commit explicitly states which candidate was promoted and why.

## Gemini / AI-Generated Material Rules

- Gemini, Claude, pasted AI output, or similar generated text is never source
  authority.
- It may be used only for lead generation.
- It must be independently sourced before promotion.
- It must not be cited as Tier I.
- It must not create verified claims by itself.
- It must not upgrade broad regional claims.

## Example Candidate Claim Object

```json
{
  "candidate_id": "cand_example_001",
  "source_artifact": "research/intake/example_raw.md",
  "review_note": "research/review_queue/example_review.md",
  "origin_type": "manual_paste",
  "origin_url": "",
  "fetch_status": "manual",
  "review_status": "pending_review",
  "risk_level": "medium",
  "allowed_use": [
    "research lead generation",
    "candidate source hunting"
  ],
  "forbidden_use": [
    "Tier I sourcing",
    "verified claim creation"
  ],
  "related_modules": [
    "UK-RAG-MOD-055"
  ],
  "candidate_claims": [
    {
      "candidate_claim_id": "cand_claim_example_001",
      "claim_text": "Example unsourced claim requiring independent verification.",
      "tier_candidate": "I",
      "source_status": "needs_independent_sources"
    }
  ],
  "required_action": "source_hunting",
  "operator_approval_required": true,
  "created_at": "2026-06-08",
  "notes": "Example only; not a live claim."
}
```

## Example Safe Promotion Path

1. Store raw intake in `research/intake/`.
2. Add candidate metadata to `black_albion_candidate_claims.json`.
3. Review the candidate and split broad statements into item-level claims.
4. Move the candidate to `source_hunting`.
5. Find independent reputable sources such as Historic England, English
   Heritage, BGS, VCH/BHO, HER, Open Domesday, or official local authority
   records.
6. Get operator approval for promotion.
7. Add source records and item-level claims in a separate commit.
8. Keep unsupported or speculative material out of Tier I.

## Example Unsafe Promotion Path

Unsafe:

1. Paste AI text into intake.
2. Copy its statements into `black_albion_claims.json`.
3. Mark the claims `verified`.
4. Treat AI text as a source.

This path is forbidden because intake material is not authority and cannot
directly become Tier I.

## Validation Commands

```bash
python3 -m json.tool data/raw/black_albion_candidate_claims.json
python3 -m pytest -q
python3 -m compileall backend
python3 scripts/list_candidate_claims.py
git diff --check
git diff --cached --check
```
