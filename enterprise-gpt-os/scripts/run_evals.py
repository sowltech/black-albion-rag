#!/usr/bin/env python3
"""Run Enterprise GPT OS governance eval file checks."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - environment failure path
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[2]
ENTERPRISE_ROOT = REPO_ROOT / "enterprise-gpt-os"
MANIFEST_PATH = ENTERPRISE_ROOT / "manifest.yaml"
RISK_CASES_PATH = ENTERPRISE_ROOT / "evals" / "risk_classification_cases.yaml"
TRIGGER_CASES_PATH = ENTERPRISE_ROOT / "evals" / "approval_trigger_cases.yaml"
ESCALATIONS_PATH = ENTERPRISE_ROOT / "evals" / "expected_escalations.yaml"

RISK_CASE_FIELDS = [
    "id",
    "title",
    "user_request",
    "expected_risk_level",
    "expected_permission_level",
    "expected_human_approval",
    "expected_reason",
]

TRIGGER_CASE_FIELDS = [
    "id",
    "trigger",
    "user_request",
    "expected_detected",
    "expected_escalation_owner",
    "expected_reason",
]

ESCALATION_FIELDS = [
    "escalation_key",
    "owner_role",
    "when_to_escalate",
    "required_log_fields",
    "allowed_gpt_action",
    "forbidden_gpt_action",
]


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def load_yaml(path: Path, label: str, errors: list[str]) -> Any:
    if yaml is None:
        add_error(errors, "PyYAML is not installed; cannot parse YAML.")
        return None

    if not path.exists():
        add_error(errors, f"{label} not found: {path.relative_to(REPO_ROOT)}")
        return None

    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        add_error(errors, f"{label} YAML syntax error: {exc}")
    except OSError as exc:
        add_error(errors, f"{label} could not be read: {exc}")
    return None


def validate_required_fields(
    records: list[Any],
    required_fields: list[str],
    label: str,
    errors: list[str],
) -> None:
    seen_ids: set[str] = set()
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            add_error(errors, f"{label} #{index} must be a mapping/object.")
            continue

        record_id = record.get("id") or record.get("escalation_key")
        if isinstance(record_id, str):
            if record_id in seen_ids:
                add_error(errors, f"{label} duplicate id/key: {record_id}")
            seen_ids.add(record_id)

        for field in required_fields:
            if field not in record:
                add_error(errors, f"{label} #{index} missing required field: {field}")
            elif record[field] in ("", None):
                add_error(errors, f"{label} #{index}.{field} must not be empty.")


def get_records(data: Any, key: str, label: str, errors: list[str]) -> list[Any]:
    if not isinstance(data, dict):
        add_error(errors, f"{label} root must be a mapping/object.")
        return []

    records = data.get(key)
    if not isinstance(records, list) or not records:
        add_error(errors, f"{label} must include non-empty '{key}'.")
        return []

    return records


def manifest_sets(manifest: dict[str, Any], errors: list[str]) -> tuple[set[str], set[str], set[str]]:
    risk_levels = manifest.get("risk_levels", {})
    if not isinstance(risk_levels, dict):
        add_error(errors, "manifest.risk_levels must be a mapping/object.")
        valid_risks: set[str] = set()
    else:
        valid_risks = {
            value.get("name")
            for value in risk_levels.values()
            if isinstance(value, dict) and isinstance(value.get("name"), str)
        }

    permission_levels = manifest.get("permission_levels", {})
    if not isinstance(permission_levels, dict):
        add_error(errors, "manifest.permission_levels must be a mapping/object.")
        valid_permissions: set[str] = set()
    else:
        valid_permissions = set(permission_levels)

    approval_triggers = manifest.get("approval_triggers", [])
    if not isinstance(approval_triggers, list):
        add_error(errors, "manifest.approval_triggers must be a list.")
        valid_triggers: set[str] = set()
    else:
        valid_triggers = {trigger for trigger in approval_triggers if isinstance(trigger, str)}

    return valid_risks, valid_permissions, valid_triggers


def validate_risk_cases(
    records: list[Any],
    valid_risks: set[str],
    valid_permissions: set[str],
    errors: list[str],
) -> None:
    validate_required_fields(records, RISK_CASE_FIELDS, "risk case", errors)
    for record in records:
        if not isinstance(record, dict):
            continue

        risk_level = record.get("expected_risk_level")
        if risk_level not in valid_risks:
            add_error(errors, f"risk case {record.get('id')} uses invalid risk level: {risk_level!r}")

        permission_level = record.get("expected_permission_level")
        if permission_level not in valid_permissions:
            add_error(
                errors,
                f"risk case {record.get('id')} uses invalid permission level: {permission_level!r}",
            )

        if not isinstance(record.get("expected_human_approval"), bool):
            add_error(errors, f"risk case {record.get('id')} expected_human_approval must be boolean.")


def validate_trigger_cases(
    records: list[Any],
    valid_triggers: set[str],
    errors: list[str],
) -> None:
    validate_required_fields(records, TRIGGER_CASE_FIELDS, "approval trigger case", errors)
    for record in records:
        if not isinstance(record, dict):
            continue

        trigger = record.get("trigger")
        if trigger not in valid_triggers:
            add_error(errors, f"approval trigger case {record.get('id')} uses invalid trigger: {trigger!r}")

        if not isinstance(record.get("expected_detected"), bool):
            add_error(errors, f"approval trigger case {record.get('id')} expected_detected must be boolean.")


def validate_escalations(records: list[Any], errors: list[str]) -> None:
    validate_required_fields(records, ESCALATION_FIELDS, "escalation mapping", errors)
    for record in records:
        if not isinstance(record, dict):
            continue

        required_log_fields = record.get("required_log_fields")
        if not isinstance(required_log_fields, list) or not required_log_fields:
            add_error(
                errors,
                f"escalation mapping {record.get('escalation_key')} required_log_fields must be a non-empty list.",
            )


def main() -> int:
    print("Enterprise GPT OS Eval Runner")

    load_errors: list[str] = []
    manifest = load_yaml(MANIFEST_PATH, "manifest", load_errors)
    risk_data = load_yaml(RISK_CASES_PATH, "risk classification cases", load_errors)
    trigger_data = load_yaml(TRIGGER_CASES_PATH, "approval trigger cases", load_errors)
    escalation_data = load_yaml(ESCALATIONS_PATH, "expected escalations", load_errors)

    if load_errors:
        print("FAIL")
        for error in load_errors:
            print(f"- {error}")
        return 1

    errors: list[str] = []
    if not isinstance(manifest, dict):
        add_error(errors, "manifest root must be a mapping/object.")
        valid_risks: set[str] = set()
        valid_permissions: set[str] = set()
        valid_triggers: set[str] = set()
    else:
        valid_risks, valid_permissions, valid_triggers = manifest_sets(manifest, errors)

    risk_cases = get_records(risk_data, "cases", "risk classification cases", errors)
    trigger_cases = get_records(trigger_data, "cases", "approval trigger cases", errors)
    escalations = get_records(escalation_data, "mappings", "expected escalations", errors)

    validate_risk_cases(risk_cases, valid_risks, valid_permissions, errors)
    validate_trigger_cases(trigger_cases, valid_triggers, errors)
    validate_escalations(escalations, errors)

    print(f"- Total risk cases checked: {len(risk_cases)}")
    print(f"- Total approval trigger cases checked: {len(trigger_cases)}")
    print(f"- Total escalation mappings checked: {len(escalations)}")

    if errors:
        print("Failures:")
        for error in errors:
            print(f"- {error}")
        print("FAIL")
        return 1

    print("Failures: none")
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
