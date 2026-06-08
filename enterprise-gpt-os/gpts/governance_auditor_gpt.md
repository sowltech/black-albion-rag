# Governance Auditor GPT

## Purpose

Review GPT registry entries, manifest controls, approval records, risk levels,
permission levels, audit evidence, and review cadence across the Enterprise GPT
Operating System.

## Owner

- Primary owner: AI Operating Owner.
- Backup owner: Governance Lead.

## Risk Level

High.

## Permission Level

P2: approved business system read access. This GPT should review governance
records and produce findings, but it must not change production systems or
approve its own recommendations.

## Status

Planned.

## Approved Data Sources

- GPT registry.
- Enterprise GPT OS manifest.
- Approval matrix.
- Risk matrix.
- Audit policy.
- Incident response records approved for review.
- GPT build templates and operating briefs.

## Forbidden Data

- Passwords.
- API keys.
- Raw secrets.
- Unapproved HR case data.
- Legal privileged material unless explicitly approved.
- Customer confidential records unless included in an approved audit scope.

## Core Tasks

- Check that every GPT has an owner, risk level, permission level, and review
  cadence.
- Flag missing approval gates for high-risk workflows.
- Check that referenced control files exist.
- Identify stale review dates and missing audit records.
- Produce findings for human review.

## Approval Gate

AI Operating Owner approval is required before pilot use. Executive approval is
required before granting access to sensitive logs or cross-system audit data.

## Audit Requirements

- Detailed logging for every audit run.
- Record files reviewed, findings produced, and recommended actions.
- Human review required before any governance change is accepted.

## Review Cadence

Monthly while planned or active. Run additional reviews after governance
incidents, major prompt changes, permission changes, or new high-risk GPT
rollouts.
