#!/usr/bin/env python3
"""Validate the shape of repository agent dispatch and milestone contracts."""

from __future__ import annotations

import argparse
import json
import ntpath
import os
import posixpath
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
        "CONTROLLER_AFTER_DISPATCH",
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
        "CONTROLLER_AFTER_DISPATCH",
        "NO_REPORT_CHECK_AFTER",
    ),
    "update": (
        "TASK_ID",
        "MILESTONE",
        "SUMMARY",
        "EVIDENCE",
        "REPORT_DELIVERY",
        "TURN_STATE",
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
TASK_MESSAGE_DELIVERY_RE = re.compile(r"^task_message:[^<>\s]+$")
BLOCKED_DELIVERY_RE = re.compile(r"^blocked:[^<>\s].*$")
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


def canonical_path(value: str) -> tuple[str, PureWindowsPath | PurePosixPath] | None:
    windows = PureWindowsPath(value)
    if windows.is_absolute():
        normalized = value
        folded = normalized.casefold()
        if folded.startswith("\\\\?\\unc\\"):
            normalized = "\\\\" + normalized[8:]
        elif folded.startswith("\\\\?\\"):
            normalized = normalized[4:]
        return "windows", PureWindowsPath(ntpath.normpath(normalized))

    posix = PurePosixPath(value)
    if posix.is_absolute():
        return "posix", PurePosixPath(posixpath.normpath(value))
    return None


def is_descendant_path(child: str, root: str) -> bool:
    root_canonical = canonical_path(root)
    child_canonical = canonical_path(child)
    if root_canonical is None or child_canonical is None:
        return False
    root_kind, root_path = root_canonical
    child_kind, child_path = child_canonical
    if root_kind != child_kind:
        return False
    try:
        relative = child_path.relative_to(root_path)
    except ValueError:
        return False
    return bool(relative.parts)


def normalized_path(value: str) -> str:
    canonical = canonical_path(value)
    if canonical is None:
        return value
    kind, path = canonical
    normalized = str(path)
    return normalized.casefold() if kind == "windows" else normalized


def validate_checkpoint(value: str, field_name: str) -> list[str]:
    if value in {"current_turn_once", "none"} or ISO_8601_RE.fullmatch(value):
        return []
    if value == "current_turn":
        return [
            f"{field_name} current_turn is ambiguous and forbidden; "
            "use current_turn_once and yield after at most one immediate snapshot"
        ]
    return [
        f"{field_name} must be current_turn_once, none, or an ISO-8601 timestamp with timezone"
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
            errors.append("TASK_PROJECT_ID must identify the current saved repository project")
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
        wait_policy = fields.get("CONTROLLER_AFTER_DISPATCH", "")
        if wait_policy and wait_policy != "event_driven_yield":
            errors.append(
                "CONTROLLER_AFTER_DISPATCH must be event_driven_yield"
            )
        checkpoint = fields.get("NO_REPORT_CHECK_AFTER", "")
        if checkpoint:
            errors.extend(validate_checkpoint(checkpoint, "NO_REPORT_CHECK_AFTER"))
            if checkpoint == "none":
                errors.append(
                    "NO_REPORT_CHECK_AFTER must be current_turn_once or a supported "
                    "one-shot ISO-8601 checkpoint"
                )

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
        delivery = fields.get("REPORT_DELIVERY", "")
        delivery_is_task_message = bool(
            delivery and TASK_MESSAGE_DELIVERY_RE.fullmatch(delivery)
        )
        delivery_is_blocked = bool(delivery and BLOCKED_DELIVERY_RE.fullmatch(delivery))
        if delivery and not delivery_is_task_message and not delivery_is_blocked:
            errors.append(
                "REPORT_DELIVERY must be task_message:<controller-thread-id> "
                "or blocked:<reason>"
            )
        if delivery_is_blocked and milestone != "blocked":
            errors.append("blocked REPORT_DELIVERY requires MILESTONE=blocked")
        if milestone and milestone != "blocked" and not delivery_is_task_message:
            errors.append(
                "non-blocked milestone REPORT_DELIVERY must use task_message:<controller-thread-id>"
            )
        turn_state = fields.get("TURN_STATE", "")
        if turn_state and turn_state not in {"continuing", "ending"}:
            errors.append("TURN_STATE must be continuing or ending")
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
        if milestone in {"blocked", "final"} and turn_state and turn_state != "ending":
            errors.append(f"{milestone} milestone must use TURN_STATE=ending")
        if owner_match and turn_state:
            expected_owner = "task" if turn_state == "continuing" else "controller"
            if owner_match.group(1) != expected_owner:
                errors.append(
                    f"TURN_STATE={turn_state} requires owner={expected_owner}"
                )
        if (
            owner_match
            and owner_match.group(1) == "task"
            and check_match
            and check_match.group(1).strip() == "none"
        ):
            errors.append("owner=task requires a non-none check_after checkpoint")

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
