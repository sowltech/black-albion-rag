# Operator Packet Export Contract

This document describes the `v0.8.0` read-only operator packet export builder.

## Purpose

The export builder turns existing operator decision packet summaries into
reviewable JSON and Markdown artifacts. It is a pure transformation layer: it
does not create files, approve decisions, promote candidates, or write to
canonical ledgers.

## Inputs

The builder expects the output of the v0.7.0 Operator Decision Packet Engine:

- candidate decision packets
- claim decision labels
- source gaps
- readiness evidence basis
- Tier III containment flags
- canonical promotion lock status

## JSON Packet Shape

Each candidate export includes:

- `schema_version: "0.8.0"`
- `artifact_type: "operator_packet_export"`
- `candidate_id`
- `review_status`
- `operator_packet_source`
- `generated_from: "operator_decision_packet_engine"`
- `read_only: true`
- `executed: false`
- `canonical_lock`
- `decision_summary`
- `claims`
- `tier_iii_containment`
- `export_safety`

Each claim export includes:

- `claim_id`
- `claim_number`
- `decision_label`
- `readiness`
- `source_status`
- `source_gaps`
- `corrected_wording_available`
- `tier_iii_containment`
- `executed: false`
- `required_approval`
- `safety_notes`

## Markdown Layout

Markdown exports include:

- Operator Packet Export heading
- Export Status
- Candidate Summary
- Decision Label Summary
- Claim Review Table
- Claim Details
- Tier III Containment
- Canonical Protection

The Markdown text must include `executed: false` and the statement:

```text
promotion requires separate operator-approved commit
```

## Safety Guarantees

Exports are read-only snapshots. They must not imply approval, execution, or
canonical promotion.

Required export safety flags:

- `read_only: true`
- `does_not_approve: true`
- `does_not_promote: true`
- `does_not_write_canonical_ledgers: true`
- `requires_separate_operator_approved_commit: true`

## Non-Goals

The v0.8.0 builder does not:

- add API endpoints
- add dashboard panels
- write generated export files
- mutate candidate data
- mutate canonical ledgers
- approve decisions
- promote candidates
- create promotion commits
- add mutation routes
