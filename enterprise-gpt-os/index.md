# Enterprise GPT Operating System Index

Master navigation and control page for the Enterprise GPT Operating System
pack.

## Start Here

- [README](README.md)
- [Machine-Readable Manifest](manifest.yaml)
- [Manifest Validator](scripts/validate_manifest.py)
- [Standard GPT Build Template](templates/standard_gpt_build_template.md)
- [90-Day Rollout Plan](workflows/rollout_plan_90_days.md)

## Registry

- [GPT Registry Template](registry/gpt_registry_template.md)

## Governance

- [Risk Matrix](governance/risk_matrix.md)
- [Approval Matrix](governance/approval_matrix.md)
- [Audit Policy](governance/audit_policy.md)
- [Incident Response](governance/incident_response.md)

## GPT Operating Briefs

- [Company Knowledge GPT](gpts/company_knowledge_gpt.md)
- [Executive Strategy GPT](gpts/executive_strategy_gpt.md)
- [Operations SOP GPT](gpts/operations_sop_gpt.md)
- [Sales GPT](gpts/sales_gpt.md)
- [Support GPT](gpts/support_gpt.md)
- [Governance Auditor GPT](gpts/governance_auditor_gpt.md)

## Workflows

- [New GPT Request Workflow](workflows/new_gpt_request_workflow.md)
- [High-Risk Approval Workflow](workflows/high_risk_approval_workflow.md)
- [90-Day Rollout Plan](workflows/rollout_plan_90_days.md)

## Templates

- [Standard GPT Build Template](templates/standard_gpt_build_template.md)

## Evaluations

- [Risk Classification Cases](evals/risk_classification_cases.yaml)
- [Approval Trigger Cases](evals/approval_trigger_cases.yaml)
- [Expected Escalations](evals/expected_escalations.yaml)

## How To Use This Pack

1. Start with the README to understand the operating model.
2. Register every GPT in the GPT registry before build or rollout.
3. Classify each GPT using the risk matrix and permission levels.
4. Use the standard build template to document purpose, owner, data sources,
   permissions, test cases, audit requirements, and approvals.
5. Apply the approval matrix before piloting medium, high, or critical risk
   GPTs.
6. Roll out in phases using the 90-day rollout plan.
7. Review active GPTs on the required cadence and record changes, incidents,
   and approvals.

## Manifest Validation

Run the manifest validator before rollout reviews, governance changes, or
dashboard imports:

```bash
python3 enterprise-gpt-os/scripts/validate_manifest.py
```

Use the project-level validation wrapper when running repo checks:

```bash
bash scripts/validate_enterprise_gpt_os.sh
```

Run the eval case checker directly when updating governance evals:

```bash
python3 enterprise-gpt-os/scripts/run_evals.py
```

## Current Rollout Order

1. Company Knowledge GPT
2. Executive Strategy GPT
3. Operations SOP GPT
4. Sales GPT
5. Support GPT
6. Governance Auditor GPT
