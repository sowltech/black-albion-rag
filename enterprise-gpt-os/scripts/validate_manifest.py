#!/usr/bin/env python3
"""Validate the Enterprise GPT OS manifest control file."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - environment failure path
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "enterprise-gpt-os" / "manifest.yaml"

REQUIRED_TOP_LEVEL = [
    "system",
    "registry",
    "governance",
    "gpts",
    "workflows",
    "templates",
    "evals",
    "risk_levels",
    "permission_levels",
    "approval_triggers",
    "rollout_order",
    "audit_requirements",
    "review_cadence",
]

REQUIRED_SYSTEM_FIELDS = [
    "name",
    "version",
    "status",
    "owner",
    "repo_module",
    "control_file",
]

REQUIRED_GPT_FIELDS = [
    "name",
    "file",
    "owner",
    "risk_level",
    "permission_level",
    "status",
    "approval_required_for",
    "review_cadence",
]

VALID_RISK_LEVELS = {"Low", "Medium", "High", "Critical"}
VALID_PERMISSION_LEVELS = {"P0", "P1", "P2", "P3", "P4", "P5", "P6"}
REQUIRED_APPROVAL_TRIGGERS = {
    "money",
    "legal_commitment",
    "hr_decision",
    "customer_account_change",
    "security_incident",
    "public_communication",
    "data_deletion_or_export",
    "policy_exception",
    "production_change",
    "regulatory_matter",
}

REQUIRED_EVAL_FILES = {
    "risk_classification_cases": ("cases", "risk classification cases"),
    "approval_trigger_cases": ("cases", "approval trigger cases"),
    "expected_escalations": ("mappings", "expected escalation mappings"),
}


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def load_manifest(errors: list[str]) -> dict[str, Any] | None:
    if yaml is None:
        add_error(errors, "PyYAML is not installed; cannot parse YAML.")
        return None

    if not MANIFEST_PATH.exists():
        add_error(errors, f"Manifest not found: {MANIFEST_PATH}")
        return None

    try:
        data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        add_error(errors, f"YAML syntax error: {exc}")
        return None

    if not isinstance(data, dict):
        add_error(errors, "Manifest root must be a mapping/object.")
        return None

    return data


def require_mapping(data: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        add_error(errors, f"Section '{key}' must be a mapping/object.")
        return {}
    return value


def validate_file_path(path_value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(path_value, str) or not path_value.strip():
        add_error(errors, f"{label} must be a non-empty file path string.")
        return

    full_path = REPO_ROOT / path_value
    try:
        full_path.relative_to(REPO_ROOT)
    except ValueError:
        add_error(errors, f"{label} points outside the repository: {path_value}")
        return

    if not full_path.is_file():
        add_error(errors, f"{label} does not exist: {path_value}")


def validate_reference_group(
    group: dict[str, Any],
    group_name: str,
    errors: list[str],
) -> int:
    checked = 0
    for entry_name, entry in group.items():
        if isinstance(entry, dict) and "file" in entry:
            validate_file_path(entry["file"], f"{group_name}.{entry_name}.file", errors)
            checked += 1
        else:
            add_error(errors, f"{group_name}.{entry_name} must include a file reference.")
    return checked


def load_yaml_file(path_value: str, label: str, errors: list[str]) -> Any:
    full_path = REPO_ROOT / path_value
    try:
        return yaml.safe_load(full_path.read_text(encoding="utf-8"))
    except OSError as exc:
        add_error(errors, f"{label} could not be read: {exc}")
    except yaml.YAMLError as exc:
        add_error(errors, f"{label} YAML syntax error: {exc}")
    return None


def validate_eval_files(evals: dict[str, Any], errors: list[str]) -> int:
    checked = 0
    for eval_key, (list_key, description) in REQUIRED_EVAL_FILES.items():
        entry = evals.get(eval_key)
        if not isinstance(entry, dict) or "file" not in entry:
            add_error(errors, f"evals.{eval_key} must include a file reference.")
            continue

        file_path = entry["file"]
        validate_file_path(file_path, f"evals.{eval_key}.file", errors)
        checked += 1

        if not isinstance(file_path, str):
            continue

        eval_data = load_yaml_file(file_path, f"evals.{eval_key}.file", errors)
        if not isinstance(eval_data, dict):
            add_error(errors, f"evals.{eval_key}.file must contain a mapping/object.")
            continue

        records = eval_data.get(list_key)
        if not isinstance(records, list) or not records:
            add_error(errors, f"evals.{eval_key}.file must include {description}.")

    for eval_key in evals:
        if eval_key not in REQUIRED_EVAL_FILES:
            add_error(errors, f"Unknown eval manifest entry: evals.{eval_key}")

    return checked


def validate_manifest(data: dict[str, Any]) -> tuple[list[str], int]:
    errors: list[str] = []
    referenced_files = 0

    for section in REQUIRED_TOP_LEVEL:
        if section not in data:
            add_error(errors, f"Missing required top-level section: {section}")

    system = require_mapping(data, "system", errors)
    for field in REQUIRED_SYSTEM_FIELDS:
        if field not in system:
            add_error(errors, f"system missing required field: {field}")
        elif not system[field]:
            add_error(errors, f"system.{field} must not be empty.")

    if "control_file" in system:
        validate_file_path(system["control_file"], "system.control_file", errors)
        referenced_files += 1

    registry = require_mapping(data, "registry", errors)
    if "file" in registry:
        validate_file_path(registry["file"], "registry.file", errors)
        referenced_files += 1
    elif registry:
        referenced_files += validate_reference_group(registry, "registry", errors)
    else:
        add_error(errors, "registry must include a file reference.")

    for group_name in ("governance", "workflows", "templates"):
        group = require_mapping(data, group_name, errors)
        referenced_files += validate_reference_group(group, group_name, errors)

    evals = require_mapping(data, "evals", errors)
    referenced_files += validate_eval_files(evals, errors)

    gpts = require_mapping(data, "gpts", errors)
    for gpt_key, gpt in gpts.items():
        if not isinstance(gpt, dict):
            add_error(errors, f"gpts.{gpt_key} must be a mapping/object.")
            continue

        for field in REQUIRED_GPT_FIELDS:
            if field not in gpt:
                add_error(errors, f"gpts.{gpt_key} missing required field: {field}")
            elif gpt[field] in ("", None):
                add_error(errors, f"gpts.{gpt_key}.{field} must not be empty.")

        if "file" in gpt:
            validate_file_path(gpt["file"], f"gpts.{gpt_key}.file", errors)
            referenced_files += 1

        risk_level = gpt.get("risk_level")
        if risk_level not in VALID_RISK_LEVELS:
            add_error(
                errors,
                f"gpts.{gpt_key}.risk_level invalid: {risk_level!r}",
            )

        permission_level = gpt.get("permission_level")
        if permission_level not in VALID_PERMISSION_LEVELS:
            add_error(
                errors,
                f"gpts.{gpt_key}.permission_level invalid: {permission_level!r}",
            )

        if not isinstance(gpt.get("approval_required_for"), list):
            add_error(errors, f"gpts.{gpt_key}.approval_required_for must be a list.")

    approval_triggers = data.get("approval_triggers")
    if not isinstance(approval_triggers, list):
        add_error(errors, "approval_triggers must be a list.")
    else:
        missing = sorted(REQUIRED_APPROVAL_TRIGGERS - set(approval_triggers))
        if missing:
            add_error(errors, f"approval_triggers missing required values: {missing}")

    return errors, referenced_files


def main() -> int:
    print("Enterprise GPT OS Manifest Validator")
    print(f"Manifest: {MANIFEST_PATH.relative_to(REPO_ROOT)}")

    load_errors: list[str] = []
    data = load_manifest(load_errors)
    if data is None:
        print("FAIL")
        for error in load_errors:
            print(f"- {error}")
        return 1

    errors, referenced_files = validate_manifest(data)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS")
    print(f"- Top-level sections checked: {len(REQUIRED_TOP_LEVEL)}")
    print(f"- GPT entries checked: {len(data.get('gpts', {}))}")
    print(f"- Referenced files checked: {referenced_files}")
    print(f"- Eval files checked: {len(REQUIRED_EVAL_FILES)}")
    print(f"- Approval triggers checked: {len(REQUIRED_APPROVAL_TRIGGERS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
