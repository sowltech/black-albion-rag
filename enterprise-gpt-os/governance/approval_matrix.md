# GPT Approval Matrix

Use this matrix to decide who must approve a GPT before pilot or rollout.

## Approval By Risk Level

| Risk Level | Required Approvers | Optional Reviewers | Evidence Required |
|---|---|---|---|
| Low | GPT owner | Department lead | Registry entry, build template |
| Medium | GPT owner, department lead | IT/security | Registry entry, build template, test outputs |
| High | GPT owner, department lead, IT/security | Legal/compliance, data owner | Risk assessment, audit plan, access plan, test outputs |
| Critical | Executive sponsor, department lead, IT/security, legal/compliance, data owner | External professional reviewer if needed | Full risk assessment, audit policy, incident plan, restricted rollout plan |

## Approval Gates

1. Request accepted.
2. Owner assigned.
3. Risk level confirmed.
4. Permission level confirmed.
5. Data sources approved.
6. Prompt and instructions reviewed.
7. Test cases completed.
8. Audit requirements agreed.
9. Incident path agreed.
10. Pilot or rollout approved.

## Change Approval

Re-approval is required when:

- the GPT receives new data sources;
- the GPT changes audience;
- the GPT moves from internal to customer-facing;
- the GPT moves from drafting to recommendation;
- the GPT changes risk level;
- the GPT connects to tools, systems, or automations;
- the GPT is used in legal, finance, HR, security, or regulated workflows.

## Approval Record Template

| Field | Value |
|---|---|
| GPT name | |
| GPT ID | |
| Requested by | |
| Owner | |
| Risk level | |
| Permission level | |
| Approvers | |
| Decision | Approved / Rejected / Needs changes |
| Conditions | |
| Approval date | |
| Next review date | |
