#!/usr/bin/env python3
"""Validate the small safety boundary of repository task packets."""

from __future__ import annotations

import argparse
import json
import ntpath
import os
import posixpath
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath


REQUIRED = {
    "binding": (
        "TASK_ID",
        "TASK_MODE",
        "TASK_ENVIRONMENT",
        "REPOSITORY_ROOT",
        "WORKTREE_ROOT",
        "EXECUTION_PATH",
        "TASK_PROJECT_ID",
        "ACTUAL_THREAD_CWD",
        "ACTUAL_THREAD_PROJECT_ID",
    ),
    "write": (
        "TASK_ID",
        "TASK_ENVIRONMENT",
        "TASK_ARCHIVE_POLICY",
        "WORKTREE_ROOT",
        "WORKTREE",
        "BRANCH",
        "BASE_COMMIT",
        "OBJECTIVE",
        "OWNED_PATHS",
        "DO_NOT_TOUCH",
        "ACCEPTANCE",
        "REQUIRED_TESTS",
        "MODEL_POLICY",
    ),
    "review": (
        "REVIEW_TASK_ID",
        "TASK_ENVIRONMENT",
        "TASK_ARCHIVE_POLICY",
        "TARGET_MODE",
        "TARGET_PATH",
        "TARGET_COMMIT_OR_RANGE",
        "READ_ONLY",
        "ACCEPTANCE_BASELINE",
        "THREAT_MODEL",
        "NON_GOALS",
        "REVIEW_SCOPE",
        "ACCEPTANCE",
        "MODEL_POLICY",
    ),
    "update": (
        "TASK_ID",
        "STATUS",
        "SUMMARY",
        "EVIDENCE",
        "DELIVERY",
        "TARGET_SETTINGS",
        "NEXT",
    ),
}

FIELD_RE = re.compile(r"^([A-Z][A-Z0-9_]*)\s*[:=]\s*(.*)$")
FULL_SHA_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
MODEL_POLICY_RE = re.compile(
    r"^(?:repo_write_default|repo_review_default|user_explicit):[^<>\s]+/[^<>/\s]+$"
)
TASK_MESSAGE_RE = re.compile(r"^task_message:[^<>\s]+$")
BLOCKED_DELIVERY_RE = re.compile(r"^blocked:[^<>\s].*$")
TASK_MODES = {"write", "review_root", "review_worktree"}
REVIEW_MODES = {"root_readonly", "existing_worktree", "detached_snapshot"}
STATUSES = {"progress", "blocked", "final"}

OBSOLETE_DISPATCH_FIELDS = {
    "WORKTREE_POLICY",
    "INTEGRATION_TARGET",
    "EXPECTED_NEXT_MILESTONE",
    "CONTROLLER_AFTER_DISPATCH",
    "NO_REPORT_CHECK_AFTER",
}
OBSOLETE_REPORT_FIELDS = {
    "MILESTONE",
    "REPORT_DELIVERY",
    "TURN_STATE",
    "BLOCKER_OR_NEXT",
}
REVIEW_WRITABLE_FIELDS = {"WORKTREE", "BRANCH", "BASE_COMMIT", "OWNED_PATHS"}


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


def normalized_path(value: str) -> str:
    canonical = canonical_path(value)
    if canonical is None:
        return value
    kind, path = canonical
    normalized = str(path)
    return normalized.casefold() if kind == "windows" else normalized


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


def validate_resolution_if_present(root: str, execution_path: str) -> list[str]:
    """Check path substitution when static example paths happen to exist."""
    root_path = Path(root)
    execution = Path(execution_path)
    if not root_path.exists() or not execution.exists():
        return []
    resolved_root = root_path.resolve()
    resolved_execution = execution.resolve()
    errors: list[str] = []
    if os.path.normcase(str(resolved_root)) != os.path.normcase(str(root_path.absolute())):
        errors.append("WORKTREE_ROOT must not resolve through a path substitute")
    if os.path.normcase(str(resolved_execution)) != os.path.normcase(
        str(execution.absolute())
    ):
        errors.append("execution path must not resolve through a path substitute")
    if not is_descendant_path(str(resolved_execution), str(resolved_root)):
        errors.append("resolved execution path must be below resolved WORKTREE_ROOT")
    return errors


def git_output(worktree: Path, *args: str) -> tuple[str | None, str | None]:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={worktree.resolve()}",
            "-C",
            str(worktree),
            *args,
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode:
        return None, result.stderr.strip() or result.stdout.strip() or "Git command failed"
    return result.stdout.strip(), None


def validate_live_worktree(
    field_name: str,
    value: str,
    *,
    expected_branch: str | None = None,
    expected_head: str | None = None,
    require_clean: bool = False,
) -> list[str]:
    path = Path(value)
    if not path.is_dir():
        return [f"{field_name} does not exist or is not a directory"]

    top_level, error = git_output(path, "rev-parse", "--show-toplevel")
    if error:
        return [f"{field_name} is not a readable Git worktree: {error}"]
    if normalized_path(top_level or "") != normalized_path(str(path.resolve())):
        return [f"{field_name} must be the exact Git worktree root"]

    registry, error = git_output(path, "worktree", "list", "--porcelain")
    if error:
        return [f"cannot read Git worktree registry for {field_name}: {error}"]
    registered = {
        normalized_path(line.removeprefix("worktree "))
        for line in (registry or "").splitlines()
        if line.startswith("worktree ")
    }
    if normalized_path(str(path.resolve())) not in registered:
        return [f"{field_name} is not registered in the current Git worktree list"]

    errors: list[str] = []
    if expected_branch:
        branch, branch_error = git_output(path, "symbolic-ref", "--short", "-q", "HEAD")
        if branch_error or not branch:
            errors.append(f"{field_name} must not use detached HEAD for a write task")
        elif branch != expected_branch:
            errors.append(f"{field_name} branch must equal BRANCH")
    if expected_head:
        head, head_error = git_output(path, "rev-parse", "HEAD")
        if head_error or not head:
            errors.append(f"cannot read HEAD for {field_name}: {head_error or 'unknown error'}")
        elif head.casefold() != expected_head.casefold():
            errors.append(f"{field_name} HEAD must equal the contracted commit")
    if require_clean:
        status, status_error = git_output(path, "status", "--porcelain")
        if status_error:
            errors.append(f"cannot read status for {field_name}: {status_error}")
        elif status:
            errors.append(f"{field_name} must be clean at the route gate")
    return errors


def validate_live(kind: str, fields: dict[str, str]) -> list[str]:
    """Add current-filesystem and Git identity checks to the static packet checks."""
    errors = validate(kind, fields)
    if errors:
        return errors

    if kind == "binding":
        repository_root = fields["REPOSITORY_ROOT"]
        worktree_root = Path(fields["WORKTREE_ROOT"])
        errors.extend(validate_live_worktree("REPOSITORY_ROOT", repository_root))
        if not worktree_root.is_dir():
            errors.append("WORKTREE_ROOT does not exist or is not a directory")
        if fields["TASK_MODE"] in {"write", "review_worktree"}:
            errors.extend(
                validate_live_worktree(
                    "EXECUTION_PATH", fields["EXECUTION_PATH"], require_clean=True
                )
            )
    elif kind == "write":
        if not Path(fields["WORKTREE_ROOT"]).is_dir():
            errors.append("WORKTREE_ROOT does not exist or is not a directory")
        errors.extend(
            validate_live_worktree(
                "WORKTREE",
                fields["WORKTREE"],
                expected_branch=fields["BRANCH"],
                expected_head=fields["BASE_COMMIT"],
                require_clean=True,
            )
        )
    elif kind == "review":
        commit_or_range = fields["TARGET_COMMIT_OR_RANGE"]
        expected_head = re.split(r"\.\.\.?", commit_or_range)[-1]
        errors.extend(
            validate_live_worktree(
                "TARGET_PATH",
                fields["TARGET_PATH"],
                expected_head=expected_head,
                require_clean=True,
            )
        )
    return errors


def validate_model(kind: str, value: str) -> list[str]:
    if has_placeholder(value):
        return ["MODEL_POLICY must not contain placeholders"]
    if kind == "write":
        if MODEL_POLICY_RE.fullmatch(value) and value.startswith(
            ("repo_write_default:", "user_explicit:")
        ):
            return []
        return [
            "write MODEL_POLICY must explicitly bind "
            "repo_write_default:<model>/<reasoning> or user_explicit:<model>/<reasoning>"
        ]
    if value == "app_default":
        return []
    if MODEL_POLICY_RE.fullmatch(value) and value.startswith(
        ("repo_review_default:", "user_explicit:")
    ):
        return []
    return [
        "review MODEL_POLICY must be app_default, "
        "repo_review_default:<model>/<reasoning>, or user_explicit:<model>/<reasoning>"
    ]


def validate_commit_or_range(value: str) -> bool:
    if FULL_SHA_RE.fullmatch(value):
        return True
    separator = "..." if "..." in value else ".." if ".." in value else None
    if separator is None:
        return False
    left, right = value.split(separator, 1)
    return bool(FULL_SHA_RE.fullmatch(left) and FULL_SHA_RE.fullmatch(right))


def add_obsolete_errors(
    errors: list[str], fields: dict[str, str], obsolete: set[str]
) -> None:
    found = sorted(obsolete.intersection(fields))
    if found:
        errors.append("obsolete protocol fields must be removed: " + ", ".join(found))


def validate(kind: str, fields: dict[str, str]) -> list[str]:
    """Validate portable packet shape; use validate_live or the CLI at boundaries."""
    errors: list[str] = []
    for name in REQUIRED[kind]:
        if name not in fields:
            errors.append(f"missing field: {name}")
        elif not fields[name]:
            errors.append(f"empty field: {name}")

    if kind in {"write", "review"}:
        add_obsolete_errors(errors, fields, OBSOLETE_DISPATCH_FIELDS)
    if kind == "update":
        add_obsolete_errors(errors, fields, OBSOLETE_REPORT_FIELDS)

    if kind in {"binding", "write", "review"}:
        if fields.get("TASK_ENVIRONMENT", "").casefold() != "local":
            errors.append(
                "TASK_ENVIRONMENT must be local; App-managed worktree tasks are forbidden"
            )
    if kind in {"write", "review"}:
        if fields.get("TASK_ARCHIVE_POLICY", "").casefold() != "controller_after_acceptance":
            errors.append(
                "TASK_ARCHIVE_POLICY must be controller_after_acceptance"
            )

    if kind == "binding":
        repository_root = fields.get("REPOSITORY_ROOT", "")
        worktree_root = fields.get("WORKTREE_ROOT", "")
        execution_path = fields.get("EXECUTION_PATH", "")
        actual_cwd = fields.get("ACTUAL_THREAD_CWD", "")
        mode = fields.get("TASK_MODE", "")
        for field_name, value in (
            ("REPOSITORY_ROOT", repository_root),
            ("WORKTREE_ROOT", worktree_root),
            ("EXECUTION_PATH", execution_path),
            ("ACTUAL_THREAD_CWD", actual_cwd),
        ):
            if value and not is_absolute_path(value):
                errors.append(f"{field_name} must be absolute")
            if value and has_placeholder(value):
                errors.append(f"{field_name} must not contain placeholders")
        if mode and mode not in TASK_MODES:
            errors.append("TASK_MODE must be write, review_root, or review_worktree")
        if repository_root and actual_cwd and normalized_path(repository_root) != normalized_path(actual_cwd):
            errors.append("ACTUAL_THREAD_CWD must equal REPOSITORY_ROOT")
        if repository_root and worktree_root and not is_descendant_path(worktree_root, repository_root):
            errors.append("WORKTREE_ROOT must be below REPOSITORY_ROOT")
        if mode == "review_root":
            if repository_root and execution_path and normalized_path(repository_root) != normalized_path(execution_path):
                errors.append("review_root EXECUTION_PATH must equal REPOSITORY_ROOT")
        elif mode in {"write", "review_worktree"}:
            if worktree_root and execution_path and not is_descendant_path(execution_path, worktree_root):
                errors.append("EXECUTION_PATH must be below WORKTREE_ROOT")
            if worktree_root and execution_path and is_absolute_path(worktree_root) and is_absolute_path(execution_path):
                errors.extend(validate_resolution_if_present(worktree_root, execution_path))
        project_id = fields.get("TASK_PROJECT_ID", "")
        actual_project_id = fields.get("ACTUAL_THREAD_PROJECT_ID", "")
        forbidden_ids = {"null", "none", "projectless", "<none>"}
        if project_id.casefold() in forbidden_ids:
            errors.append("TASK_PROJECT_ID must identify the saved repository project")
        if actual_project_id.casefold() in forbidden_ids:
            errors.append("ACTUAL_THREAD_PROJECT_ID must be non-null")
        if project_id and actual_project_id and project_id != actual_project_id:
            errors.append("ACTUAL_THREAD_PROJECT_ID must equal TASK_PROJECT_ID")

    if kind == "write":
        root = fields.get("WORKTREE_ROOT", "")
        worktree = fields.get("WORKTREE", "")
        for field_name, value in (("WORKTREE_ROOT", root), ("WORKTREE", worktree)):
            if value and not is_absolute_path(value):
                errors.append(f"{field_name} must be absolute")
        if root and worktree and not is_descendant_path(worktree, root):
            errors.append("WORKTREE must be below WORKTREE_ROOT")
        if root and worktree and is_absolute_path(root) and is_absolute_path(worktree):
            errors.extend(validate_resolution_if_present(root, worktree))
        base_commit = fields.get("BASE_COMMIT", "")
        if base_commit and not FULL_SHA_RE.fullmatch(base_commit):
            errors.append("BASE_COMMIT must be a full 40- or 64-character hex SHA")
        for name in ("BRANCH", "OBJECTIVE", "OWNED_PATHS", "ACCEPTANCE"):
            if fields.get(name) and has_placeholder(fields[name]):
                errors.append(f"{name} must not contain placeholders")

    if kind == "review":
        mode = fields.get("TARGET_MODE", "")
        target = fields.get("TARGET_PATH", "")
        if mode and mode not in REVIEW_MODES:
            errors.append(
                "TARGET_MODE must be root_readonly, existing_worktree, or detached_snapshot"
            )
        if target and not is_absolute_path(target):
            errors.append("TARGET_PATH must be absolute")
        if fields.get("READ_ONLY", "").casefold() != "true":
            errors.append("READ_ONLY must be true")
        commit_or_range = fields.get("TARGET_COMMIT_OR_RANGE", "")
        if commit_or_range and not validate_commit_or_range(commit_or_range):
            errors.append("TARGET_COMMIT_OR_RANGE must be a full SHA or full-SHA range")
        for name in (
            "ACCEPTANCE_BASELINE",
            "THREAT_MODEL",
            "NON_GOALS",
            "REVIEW_SCOPE",
            "ACCEPTANCE",
        ):
            if fields.get(name) and has_placeholder(fields[name]):
                errors.append(f"{name} must not contain placeholders")
        forbidden = sorted(REVIEW_WRITABLE_FIELDS.intersection(fields))
        if forbidden:
            errors.append("review must not declare a writable boundary: " + ", ".join(forbidden))

    model_policy = fields.get("MODEL_POLICY", "")
    if kind in {"write", "review"} and model_policy:
        errors.extend(validate_model(kind, model_policy))

    if kind == "update":
        status = fields.get("STATUS", "")
        if status and status not in STATUSES:
            errors.append("STATUS must be progress, blocked, or final")
        delivery = fields.get("DELIVERY", "")
        direct = bool(delivery and TASK_MESSAGE_RE.fullmatch(delivery))
        blocked_delivery = bool(delivery and BLOCKED_DELIVERY_RE.fullmatch(delivery))
        if delivery and not direct and not blocked_delivery:
            errors.append(
                "DELIVERY must be task_message:<controller-task-id> or blocked:<reason>"
            )
        if blocked_delivery and status != "blocked":
            errors.append("blocked DELIVERY requires STATUS=blocked")
        if status and status != "blocked" and not direct:
            errors.append("progress and final DELIVERY must use task_message:<controller-task-id>")
        if fields.get("TARGET_SETTINGS", "").casefold() != "preserve":
            errors.append(
                "TARGET_SETTINGS must be preserve; controller-bound reports must omit model and thinking overrides"
            )
        if status == "final":
            if fields.get("EVIDENCE", "").casefold() == "none":
                errors.append("final EVIDENCE must include commands or artifacts")
            for name in ("RISKS_OR_LIMITS", "PENDING_ITEMS"):
                if name not in fields:
                    errors.append(f"final report missing field: {name}")
                elif not fields[name]:
                    errors.append(f"final report empty field: {name}")

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
    errors = validate_live(args.kind, fields)
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
        print(f"VALID live {args.kind} contract")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
