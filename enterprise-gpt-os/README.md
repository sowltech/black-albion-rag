# Enterprise GPT Operating System

This pack provides a markdown-based operating system for governing GPTs,
agents, assistants, and AI-enabled workflows across a business.

It is designed for teams that need practical controls before GPTs spread across
departments without ownership, auditability, or risk boundaries.

## What This Pack Governs

- Internal GPTs used by staff.
- Customer-facing assistants.
- Department-specific GPTs for sales, support, operations, strategy, and
  company knowledge.
- Agent workflows that read, draft, classify, summarize, or recommend actions.
- Approval gates for high-risk use cases.
- Review cadence, audit requirements, and incident response.

## Core Operating Principles

- Every GPT has an owner.
- Every GPT has a risk level.
- Every GPT has a permission level.
- Every GPT has an audit requirement.
- High-risk GPTs require approval before rollout.
- GPTs that touch sensitive data require documented boundaries.
- GPTs that influence customers, legal, finance, HR, or operations require
  stricter review.
- No GPT should have unclear purpose, uncontrolled access, or unmanaged prompts.

## Directory Map

- `registry/` contains the central GPT registry template.
- `governance/` contains risk, approval, audit, and incident controls.
- `gpts/` contains role-specific GPT operating briefs.
- `workflows/` contains request, approval, and rollout workflows.
- `templates/` contains the standard GPT build template.

## How To Use This Pack

1. Start with `registry/gpt_registry_template.md`.
2. Register every GPT before rollout.
3. Assign an owner, business purpose, risk level, permission level, and review
   cadence.
4. Use `governance/risk_matrix.md` to classify the GPT.
5. Use `governance/approval_matrix.md` to decide who must approve it.
6. Use `templates/standard_gpt_build_template.md` to design the GPT.
7. Use the workflows in `workflows/` to manage rollout and review.
8. Review active GPTs monthly or quarterly based on risk.

## Permission Levels

- `Level 0`: No data access. General drafting or brainstorming only.
- `Level 1`: Public or approved internal knowledge only.
- `Level 2`: Internal documents, SOPs, and non-sensitive business context.
- `Level 3`: Confidential business data with owner approval.
- `Level 4`: Regulated, customer-sensitive, financial, legal, HR, or security
  data. Requires executive approval and enhanced audit controls.

## Review Cadence

- Low risk: every 6 months.
- Medium risk: quarterly.
- High risk: monthly.
- Critical risk: before every major change and at least monthly.

## Minimum Launch Requirements

- GPT registered.
- Owner assigned.
- Risk level assigned.
- Permission level assigned.
- Prompt and knowledge sources documented.
- Audit requirements documented.
- Approval gate completed where required.
- Test cases completed.
- Rollout plan agreed.

## What This Pack Does Not Do

- It does not guarantee legal, financial, medical, security, or compliance
  outcomes.
- It does not replace qualified professional review.
- It does not make AI outputs automatically correct.
- It does not remove the need for access controls, staff training, or ongoing
  monitoring.
