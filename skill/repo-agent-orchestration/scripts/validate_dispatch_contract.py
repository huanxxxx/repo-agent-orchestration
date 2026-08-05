#!/usr/bin/env python3
"""Validate the shape of repository agent dispatch and milestone contracts."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath


REQUIRED = {
    "binding": (
        "TASK_ID",
        "REPOSITORY_ROOT",
        "WORKTREE_ROOT",
        "EXECUTION_WORKTREE",
        "TASK_PROJECT_ID",
        "TASK_PROJECT_PATH",
        "TASK_ENVIRONMENT",
        "ACTUAL_THREAD_CWD",
        "ACTUAL_THREAD_PROJECT_ID",
        "COMMAND_WORKDIR_POLICY",
        "ROOT_WRITE_POLICY",
        "BINDING_STATUS",
    ),
    "write": (
        "TASK_ID",
        "WORKTREE_POLICY",
        "WORKTREE_ROOT",
        "WORKTREE",
        "BRANCH",
        "BASE_COMMIT",
        "OBJECTIVE",
        "OWNED_PATHS",
        "DO_NOT_TOUCH",
        "ACCEPTANCE",
        "REQUIRED_TESTS",
        "INTEGRATION_TARGET",
        "MODEL_POLICY",
        "EXPECTED_NEXT_MILESTONE",
        "NO_REPORT_CHECK_AFTER",
    ),
    "review": (
        "REVIEW_TASK_ID",
        "TARGET_WORKTREE",
        "TARGET_BRANCH",
        "TARGET_COMMIT_OR_RANGE",
        "READ_ONLY",
        "REVIEW_SCOPE",
        "ACCEPTANCE",
        "REQUIRED_CHECKS",
        "REPORT_FORMAT",
        "MODEL_POLICY",
        "EXPECTED_NEXT_MILESTONE",
        "NO_REPORT_CHECK_AFTER",
    ),
    "update": (
        "TASK_ID",
        "MILESTONE",
        "SUMMARY",
        "EVIDENCE",
        "BLOCKER_OR_NEXT",
    ),
}

FIELD_RE = re.compile(r"^([A-Z][A-Z0-9_]*)\s*[:=]\s*(.*)$")
FULL_SHA_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
ISO_8601_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})$"
)
MODEL_POLICY_RE = re.compile(
    r"^(?:repo_write_default|repo_review_default|user_explicit):[^<>\s]+/[^<>/\s]+$"
)
MILESTONES = {
    "baseline_confirmed",
    "plan_frozen",
    "blocked",
    "fix_ready",
    "tests_complete",
    "final",
}
REVIEW_FORBIDDEN_FIELDS = {
    "WORKTREE_POLICY",
    "WORKTREE_ROOT",
    "WORKTREE",
    "BRANCH",
    "BASE_COMMIT",
    "OWNED_PATHS",
}


def parse_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = FIELD_RE.match(line)
        if match:
            fields[match.group(1)] = match.group(2).strip()
    return fields


def has_placeholder(value: str) -> bool:
    return "<" in value or ">" in value


def is_absolute_path(value: str) -> bool:
    return PureWindowsPath(value).is_absolute() or PurePosixPath(value).is_absolute()


def is_descendant_path(child: str, root: str) -> bool:
    if PureWindowsPath(root).is_absolute():
        root_path = PureWindowsPath(root)
        child_path = PureWindowsPath(child)
    else:
        root_path = PurePosixPath(root)
        child_path = PurePosixPath(child)
    try:
        relative = child_path.relative_to(root_path)
    except ValueError:
        return False
    return bool(relative.parts)


def normalized_path(value: str) -> str:
    if PureWindowsPath(value).is_absolute():
        normalized = str(PureWindowsPath(value))
        if normalized.startswith("\\\\?\\UNC\\"):
            normalized = "\\\\" + normalized[8:]
        elif normalized.startswith("\\\\?\\"):
            normalized = normalized[4:]
        return normalized.rstrip("\\").casefold()
    return str(PurePosixPath(value)).rstrip("/")


def validate_checkpoint(value: str, field_name: str) -> list[str]:
    if value in {"current_turn", "none"} or ISO_8601_RE.fullmatch(value):
        return []
    return [
        f"{field_name} must be current_turn, none, or an ISO-8601 timestamp with timezone"
    ]


def validate_model_policy(kind: str, value: str) -> list[str]:
    if has_placeholder(value):
        return ["MODEL_POLICY must not contain placeholders"]
    if kind == "write":
        if value.startswith("app_default"):
            return [
                "write MODEL_POLICY must explicitly bind the execution model; "
                "app_default is reserved for declared review policy"
            ]
        if not MODEL_POLICY_RE.fullmatch(value) or not value.startswith(
            ("repo_write_default:", "user_explicit:")
        ):
            return [
                "write MODEL_POLICY must be "
                "repo_write_default:<model>/<reasoning> or "
                "user_explicit:<model>/<reasoning>"
            ]
        return []
    if value == "app_default":
        return []
    if not MODEL_POLICY_RE.fullmatch(value) or not value.startswith(
        ("repo_review_default:", "user_explicit:")
    ):
        return [
            "review MODEL_POLICY must be app_default, "
            "repo_review_default:<model>/<reasoning>, or "
            "user_explicit:<model>/<reasoning>"
        ]
    return []


def validate_existing_path_resolution(root: str, worktree: str) -> list[str]:
    errors: list[str] = []
    root_path = Path(root)
    worktree_path = Path(worktree)
    if not root_path.exists() or not worktree_path.exists():
        return errors
    resolved_root = root_path.resolve()
    resolved_worktree = worktree_path.resolve()
    if os.path.normcase(str(resolved_root)) != os.path.normcase(str(root_path.absolute())):
        errors.append("WORKTREE_ROOT must not resolve through a path substitute")
    if os.path.normcase(str(resolved_worktree)) != os.path.normcase(
        str(worktree_path.absolute())
    ):
        errors.append("WORKTREE must not resolve through a path substitute")
    if not is_descendant_path(str(resolved_worktree), str(resolved_root)):
        errors.append("resolved WORKTREE must be below resolved WORKTREE_ROOT")
    return errors


def validate(kind: str, fields: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED[kind]:
        if name not in fields:
            errors.append(f"missing field: {name}")
        elif not fields[name]:
            errors.append(f"empty field: {name}")

    if kind == "binding":
        repository_root = fields.get("REPOSITORY_ROOT", "")
        worktree_root = fields.get("WORKTREE_ROOT", "")
        execution_worktree = fields.get("EXECUTION_WORKTREE", "")
        project_path = fields.get("TASK_PROJECT_PATH", "")
        actual_cwd = fields.get("ACTUAL_THREAD_CWD", "")
        project_id = fields.get("TASK_PROJECT_ID", "")
        actual_project_id = fields.get("ACTUAL_THREAD_PROJECT_ID", "")
        for field_name, value in (
            ("REPOSITORY_ROOT", repository_root),
            ("WORKTREE_ROOT", worktree_root),
            ("EXECUTION_WORKTREE", execution_worktree),
            ("TASK_PROJECT_PATH", project_path),
            ("ACTUAL_THREAD_CWD", actual_cwd),
        ):
            if value and not is_absolute_path(value):
                errors.append(f"{field_name} must be absolute")
            if value and has_placeholder(value):
                errors.append(f"{field_name} must not contain placeholders")
        if repository_root and project_path and normalized_path(repository_root) != normalized_path(project_path):
            errors.append("TASK_PROJECT_PATH must equal REPOSITORY_ROOT")
        if repository_root and actual_cwd and normalized_path(repository_root) != normalized_path(actual_cwd):
            errors.append("ACTUAL_THREAD_CWD must equal REPOSITORY_ROOT")
        if repository_root and worktree_root and not is_descendant_path(worktree_root, repository_root):
            errors.append("WORKTREE_ROOT must be below REPOSITORY_ROOT")
        if worktree_root and execution_worktree and not is_descendant_path(execution_worktree, worktree_root):
            errors.append("EXECUTION_WORKTREE must be below WORKTREE_ROOT")
        forbidden_ids = {"null", "none", "projectless", "<none>"}
        if project_id.casefold() in forbidden_ids:
            errors.append("TASK_PROJECT_ID must identify the exact saved worktree project")
        if actual_project_id.casefold() in forbidden_ids:
            errors.append("ACTUAL_THREAD_PROJECT_ID must be non-null")
        if project_id and actual_project_id and project_id != actual_project_id:
            errors.append("ACTUAL_THREAD_PROJECT_ID must equal TASK_PROJECT_ID")
        if fields.get("TASK_ENVIRONMENT") != "local":
            errors.append("TASK_ENVIRONMENT must be local for repository_project_local")
        if fields.get("COMMAND_WORKDIR_POLICY") != "exact_execution_worktree":
            errors.append("COMMAND_WORKDIR_POLICY must be exact_execution_worktree")
        if fields.get("ROOT_WRITE_POLICY") != "forbidden":
            errors.append("ROOT_WRITE_POLICY must be forbidden")
        if fields.get("BINDING_STATUS") != "verified":
            errors.append("BINDING_STATUS must be verified")

    if kind == "write" and fields.get("WORKTREE_POLICY") != "repo_local_only":
        errors.append("WORKTREE_POLICY must be repo_local_only")

    if kind == "write":
        root = fields.get("WORKTREE_ROOT", "")
        worktree = fields.get("WORKTREE", "")
        if root and not is_absolute_path(root):
            errors.append("WORKTREE_ROOT must be absolute")
        if worktree and not is_absolute_path(worktree):
            errors.append("WORKTREE must be absolute")
        if root and worktree and not is_descendant_path(worktree, root):
            errors.append("WORKTREE must be below WORKTREE_ROOT")
        if root and worktree and is_absolute_path(root) and is_absolute_path(worktree):
            errors.extend(validate_existing_path_resolution(root, worktree))
        base_commit = fields.get("BASE_COMMIT", "")
        if base_commit and not FULL_SHA_RE.fullmatch(base_commit):
            errors.append("BASE_COMMIT must be a full 40- or 64-character hex SHA")
        for field_name in ("BRANCH", "OBJECTIVE", "OWNED_PATHS", "ACCEPTANCE"):
            value = fields.get(field_name, "")
            if value and has_placeholder(value):
                errors.append(f"{field_name} must not contain placeholders")

    if kind == "review" and fields.get("READ_ONLY", "").lower() != "true":
        errors.append("READ_ONLY must be true")

    if kind == "review":
        target = fields.get("TARGET_WORKTREE", "")
        if target and not is_absolute_path(target):
            errors.append("TARGET_WORKTREE must be absolute")
        forbidden = sorted(REVIEW_FORBIDDEN_FIELDS.intersection(fields))
        if forbidden:
            errors.append(
                "review contract must not create a writable boundary: "
                + ", ".join(forbidden)
            )

    model_policy = fields.get("MODEL_POLICY", "")
    if kind in {"write", "review"} and model_policy:
        errors.extend(validate_model_policy(kind, model_policy))

    if kind in {"write", "review"}:
        checkpoint = fields.get("NO_REPORT_CHECK_AFTER", "")
        if checkpoint:
            errors.extend(validate_checkpoint(checkpoint, "NO_REPORT_CHECK_AFTER"))

    if kind == "update":
        milestone = fields.get("MILESTONE", "")
        if milestone and milestone not in MILESTONES:
            errors.append("MILESTONE must be one of the declared milestone values")
        evidence = fields.get("EVIDENCE", "")
        if milestone in {"tests_complete", "final"} and evidence.lower() == "none":
            errors.append(f"{milestone} EVIDENCE must include actual commands or artifacts")
        if milestone == "final":
            for field_name in ("RISKS_OR_LIMITS", "PENDING_ITEMS"):
                if field_name not in fields:
                    errors.append(f"final milestone missing field: {field_name}")
                elif not fields[field_name]:
                    errors.append(f"final milestone empty field: {field_name}")
        handoff = fields.get("BLOCKER_OR_NEXT", "")
        owner_match = re.search(r"\bowner\s*=\s*(controller|task)\b", handoff)
        action_match = re.search(r"\baction\s*=\s*([^;]+)", handoff)
        check_match = re.search(r"\bcheck_after\s*=\s*([^;]+)", handoff)
        if not owner_match:
            errors.append("BLOCKER_OR_NEXT must include owner=controller|task")
        if not action_match or not action_match.group(1).strip():
            errors.append("BLOCKER_OR_NEXT must include action=<value>")
        if not check_match or not check_match.group(1).strip():
            errors.append("BLOCKER_OR_NEXT must include check_after=<value>")
        else:
            errors.extend(
                validate_checkpoint(
                    check_match.group(1).strip(), "BLOCKER_OR_NEXT check_after"
                )
            )
        if milestone in {"blocked", "final"} and owner_match:
            if owner_match.group(1) != "controller":
                errors.append(f"{milestone} milestone must hand ownership to controller")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=sorted(REQUIRED), required=True)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        text = args.contract.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read contract: {exc}", file=sys.stderr)
        return 2

    fields = parse_fields(text)
    errors = validate(args.kind, fields)
    result = {
        "kind": args.kind,
        "valid": not errors,
        "errors": errors,
        "fields": sorted(fields),
    }

    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif errors:
        print(f"INVALID {args.kind} contract")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"VALID {args.kind} contract")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
