# Operator Promotion Approval Template

## Candidate details

- candidate_id:
- intake_file:
- source_review_file:
- operator_packet_file:
- requested_by:
- review_date:

## Promotion request type

Choose one:

- promote_selected_corrected_sub_claims
- keep_in_source_hunting
- reject_original_claim
- archive_as_speculative_only
- request_more_sources

## Canonical target ledger

Choose one or more:

- `data/raw/black_albion_sites.json`
- `data/raw/black_albion_claims.json`
- `data/raw/black_albion_modules.json`
- `data/raw/black_albion_sources.json`
- none

## Claims under review

For each claim:

- claim_number:
- original_claim_text:
- corrected_claim_text:
- source_status:
- promotion_readiness:
- promotion_decision:
- rationale:
- required_sources_attached:
- remaining_gaps:
- Tier III contamination check:
- operator_initials:

## Safety gates

- [ ] Corrected wording has been reviewed.
- [ ] Unsupported original phrasing has been removed or rejected.
- [ ] Tier III/speculative language has not entered Tier I canonical data.
- [ ] Every promoted statement has at least one named source.
- [ ] Primary or institutional sources are preferred where available.
- [ ] The exact canonical target file is identified.
- [ ] Promotion is happening in a separate commit from the review packet.
- [ ] Rollback path is clear.
- [ ] Operator approval is explicit.

## Required command checks before promotion commit

- `python3 -m json.tool` for any modified JSON ledger
- `bash scripts/smoke_live_uvicorn.sh`
- `bash scripts/validate_enterprise_gpt_os.sh`
- `python3 -m pytest -q`
- `python3 -m compileall backend`
- `git diff --check`
- `git diff --cached --check`
- secret-pattern scan on changed files

## Final decision

Choose one:

- approved_for_separate_promotion_commit
- not_approved_keep_in_source_hunting
- rejected
- archive_speculative_only
- more_sources_required

## Operator signature block

- operator_name:
- operator_initials:
- approval_date:
- approval_scope:
- notes:
