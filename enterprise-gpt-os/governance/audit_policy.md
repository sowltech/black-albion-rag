# GPT Audit Policy

## Purpose

The audit policy ensures GPTs and agents remain traceable, reviewable, and
accountable after launch.

## Minimum Audit Records

Every GPT must have:

- registry entry;
- owner;
- business purpose;
- risk level;
- permission level;
- approved data sources;
- approval status;
- review cadence;
- change log;
- incident contact.

## Output Review

| Risk Level | Output Review Requirement |
|---|---|
| Low | Spot check at review cadence |
| Medium | Sample outputs reviewed quarterly |
| High | Monthly sample review and issue log |
| Critical | Formal output review before launch, after changes, and monthly |

## Change Log Requirements

Record:

- prompt changes;
- instruction changes;
- knowledge source changes;
- permission changes;
- owner changes;
- user group changes;
- tool or automation changes;
- incident remediation changes.

## Audit Evidence

Store audit evidence in the business-approved location. Evidence can include:

- review notes;
- approval records;
- screenshots;
- test cases;
- output samples;
- incident tickets;
- access review notes.

## Retention

- Low risk: 6 months.
- Medium risk: 12 months.
- High risk: 24 months.
- Critical risk: follow legal/compliance retention policy.

## Audit Failures

Pause or restrict a GPT if:

- no owner exists;
- review cadence is missed;
- data sources are unknown;
- outputs repeatedly fail quality checks;
- sensitive data appears in unauthorized outputs;
- risk level is outdated;
- approval records are missing.
