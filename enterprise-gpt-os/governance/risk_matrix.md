# GPT Risk Matrix

Use this matrix to classify every GPT before build, pilot, rollout, and major
change.

## Risk Levels

| Risk Level | Description | Examples | Minimum Controls |
|---|---|---|---|
| Low | Drafting or brainstorming with no sensitive data and no operational impact | Blog outlines, meeting agenda drafts, internal brainstorming | Owner assigned, basic registry entry, 6-month review |
| Medium | Uses internal documents or affects staff workflows, but does not make high-impact decisions | SOP helper, internal policy assistant, training assistant | Owner assigned, approved data sources, quarterly review, sample output checks |
| High | Handles confidential data, customer interaction, operational recommendations, or regulated-adjacent processes | Sales assistant, support assistant, operational triage GPT | Department approval, audit log, monthly review, incident route, restricted permissions |
| Critical | Touches legal, finance, HR, security, regulated advice, or decisions with material business/customer impact | Contract review assistant, HR disciplinary assistant, financial recommendation GPT | Executive approval, legal/compliance review, enhanced audit, restricted access, pre-rollout testing |

## Risk Factors

| Factor | Low | Medium | High | Critical |
|---|---|---|---|---|
| Data sensitivity | Public | Internal | Confidential | Regulated or highly sensitive |
| Audience | Internal owner only | Internal team | Customers or cross-functional staff | Customers, regulators, legal/finance/HR/security |
| Output impact | Draft only | Workflow guidance | Operational recommendation | Decision support for high-impact action |
| Autonomy | Human asks, human reviews | Human asks, human reviews | Recommends next action | May trigger workflow or influence formal decision |
| Error impact | Minor inconvenience | Staff confusion | Customer/business harm | Legal, financial, security, or compliance harm |

## Permission Levels

| Permission Level | Access Boundary | Examples |
|---|---|---|
| Level 0 | No data access | General writing helper |
| Level 1 | Public or approved internal knowledge | Public FAQ assistant |
| Level 2 | Internal documents and SOPs | Operations SOP GPT |
| Level 3 | Confidential business data | Sales account GPT |
| Level 4 | Regulated or high-sensitivity data | HR, legal, finance, security GPT |

## Risk Review Cadence

- Low: every 6 months.
- Medium: quarterly.
- High: monthly.
- Critical: monthly and before any major update.

## Escalation Triggers

- GPT starts using new data sources.
- GPT is exposed to a new user group.
- GPT becomes customer-facing.
- GPT output influences decisions instead of drafts.
- GPT produces harmful, inaccurate, confidential, or policy-breaking output.
- GPT owner changes.
