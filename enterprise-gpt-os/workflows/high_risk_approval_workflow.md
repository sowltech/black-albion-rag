# High-Risk Approval Workflow

## Purpose

Control GPTs that touch confidential data, customer impact, regulated-adjacent
workflows, legal, finance, HR, security, or operational decisions.

## Required Roles

- GPT owner.
- Department lead.
- Data owner.
- IT/security.
- Legal/compliance where relevant.
- Executive sponsor for critical use cases.

## Workflow Steps

1. Confirm use case and business need.
2. Complete standard build template.
3. Classify risk and permission level.
4. Review data sources.
5. Review prompt and system instructions.
6. Define allowed and forbidden outputs.
7. Define audit requirements.
8. Define incident route.
9. Run test cases.
10. Approve pilot or reject.
11. Review pilot outputs.
12. Approve rollout, restrict, or retire.

## Required Evidence

- Completed registry entry.
- Completed build template.
- Risk assessment.
- Data source list.
- Approval record.
- Test outputs.
- Audit plan.
- Incident response route.

## Approval Decision

| Decision | Meaning |
|---|---|
| Approved | GPT can proceed under documented controls |
| Approved with conditions | GPT can proceed only if listed controls are implemented |
| Needs changes | GPT must be revised and resubmitted |
| Rejected | GPT must not be built or deployed |
