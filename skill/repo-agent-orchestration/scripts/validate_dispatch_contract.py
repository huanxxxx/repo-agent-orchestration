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


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from packet_schema import REQUIRED, allowed_fields

FIELD_RE = re.compile(r"^([A-Z][A-Z0-9_]*)\s*[:=]\s*(.*)$")
FULL_SHA_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
PLACEHOLDER_RE = re.compile(r"<[A-Za-z][^<>\r\n]*>")
DELEGATION_FRAME_RE = re.compile(
    r"(?:<|&lt;)/?codex_delegation\b", re.IGNORECASE
)
MODEL_POLICY_RE = re.compile(
    r"^(?:repo_write_default|repo_review_default|repo_delivery_default|user_explicit):[^<>\s]+/[^<>/\s]+$"
)
PROFILE_MODEL_RE = re.compile(r"^(?:[^<>\s]+/[^<>/\s]+)$")
TASK_MESSAGE_RE = re.compile(r"^task_message:[^<>\s]+$")
TASK_MODES = {
    "design_authority",
    "delivery_controller",
    "write",
    "review_root",
    "review_worktree",
}
REVIEW_MODES = {"root_readonly", "existing_worktree", "detached_snapshot"}
REVIEW_DEPTHS = {"delta", "full"}
STATUSES = {"progress", "blocked", "final"}
ORCHESTRATION_MODES = {"delivery", "architected"}
REVIEW_CLASSES = {"design", "governance", "implementation"}
UPDATE_CLASSES = {"design_review", "governance_audit", "implementation"}
DELIVERY_UPDATE_TYPES = {"plan", "milestone", "final"}
DESIGN_DECISIONS = {
    "clarify",
    "continue",
    "hold",
    "reopen_approved",
    "reopen_rejected",
}

OBSOLETE_DISPATCH_FIELDS = {
    "WORKTREE_POLICY",
    "INTEGRATION_TARGET",
    "EXPECTED_NEXT_MILESTONE",
    "CONTROLLER_AFTER_DISPATCH",
    "NO_REPORT_CHECK_AFTER",
}
OBSOLETE_REPORT_FIELDS = {
    "REPORT_DELIVERY",
    "TURN_STATE",
    "BLOCKER_OR_NEXT",
}
REVIEW_WRITABLE_FIELDS = {"WORKTREE", "BRANCH", "BASE_COMMIT", "OWNED_PATHS"}
DELIVERY_PLAN_FIELDS = (
    "READY_SET",
    "PARALLEL_DISPATCH",
    "DEPENDENCY_GRAPH",
    "SHARED_PATH_OWNER",
)
REVIEW_BUDGET_PARTS = ("context=", "checks=", "expand_if=")
REVIEW_PACKET_CHAR_LIMITS = {"delta": 5_000, "full": 9_000}


def obsolete_fields(kind: str) -> set[str]:
    fields: set[str] = set()
    if kind in {"write", "review", "design_handoff"}:
        fields.update(OBSOLETE_DISPATCH_FIELDS)
    if kind in {"update", "delivery_update", "design_reopen", "design_decision"}:
        fields.update(OBSOLETE_REPORT_FIELDS)
    return fields


def schema_integrity_errors(kind: str | None = None) -> list[str]:
    """Return contradictions between declared packet fields and rejection rules."""
    kinds = (kind,) if kind is not None else tuple(REQUIRED)
    errors: list[str] = []
    for packet_kind in kinds:
        conflicts = sorted(
            set(allowed_fields(packet_kind)) & obsolete_fields(packet_kind)
        )
        if conflicts:
            errors.append(
                f"{packet_kind} schema declares obsolete fields: "
                + ", ".join(conflicts)
            )
    return errors


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
    return bool(PLACEHOLDER_RE.search(value))


def has_delegation_framing(value: str) -> bool:
    return bool(DELEGATION_FRAME_RE.search(value))


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
    elif kind == "design_handoff":
        errors.extend(
            validate_live_worktree("REPOSITORY_ROOT", fields["REPOSITORY_ROOT"])
        )
    return errors


def validate_model(kind: str, value: str) -> list[str]:
    if has_placeholder(value):
        return ["MODEL_POLICY must not contain placeholders"]
    if kind == "write":
        if value == "app_default":
            return []
        if MODEL_POLICY_RE.fullmatch(value) and value.startswith(
            ("repo_write_default:", "user_explicit:")
        ):
            return []
        return [
            "write MODEL_POLICY must be app_default, "
            "repo_write_default:<model>/<reasoning>, or user_explicit:<model>/<reasoning>"
        ]
    if kind == "delivery":
        if value == "app_default":
            return []
        if MODEL_POLICY_RE.fullmatch(value) and value.startswith(
            ("repo_delivery_default:", "user_explicit:")
        ):
            return []
        return [
            "delivery MODEL_POLICY must be app_default, "
            "repo_delivery_default:<model>/<reasoning>, or user_explicit:<model>/<reasoning>"
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


def repository_model_policy(kind: str, value: str) -> str:
    """Translate a repository profile model value into a packet MODEL_POLICY."""
    value = value.strip()
    if value == "app_default":
        return value
    if not PROFILE_MODEL_RE.fullmatch(value):
        raise ValueError(
            f"{kind} model value must be app_default or <model>/<reasoning>: {value}"
        )
    if kind == "write":
        return f"repo_write_default:{value}"
    if kind == "review":
        return f"repo_review_default:{value}"
    if kind == "delivery":
        return f"repo_delivery_default:{value}"
    raise ValueError(f"unsupported model policy kind: {kind}")


def validate_commit_or_range(value: str) -> bool:
    if FULL_SHA_RE.fullmatch(value):
        return True
    separator = "..." if "..." in value else ".." if ".." in value else None
    if separator is None:
        return False
    left, right = value.split(separator, 1)
    return bool(FULL_SHA_RE.fullmatch(left) and FULL_SHA_RE.fullmatch(right))


def packet_char_count(fields: dict[str, str]) -> int:
    return sum(len(name) + len(value) + 3 for name, value in fields.items())


def add_obsolete_errors(
    errors: list[str], fields: dict[str, str], obsolete: set[str]
) -> None:
    found = sorted(obsolete.intersection(fields))
    if found:
        errors.append("obsolete protocol fields must be removed: " + ", ".join(found))


def validate_orchestration_mode(fields: dict[str, str]) -> list[str]:
    mode = fields.get("ORCHESTRATION_MODE", "")
    if mode and mode not in ORCHESTRATION_MODES:
        return ["ORCHESTRATION_MODE must be delivery or architected"]
    return []


def validate_checkpoint(field_name: str, value: str) -> list[str]:
    if value and not FULL_SHA_RE.fullmatch(value):
        return [f"{field_name} must be a full 40- or 64-character hex SHA"]
    return []


def validate_concrete_task_id(field_name: str, value: str) -> list[str]:
    if not value:
        return []
    if has_placeholder(value) or value.casefold() in {"none", "null", "pending"}:
        return [f"{field_name} must identify an actual task"]
    return []


def validate_task_message_target(
    fields: dict[str, str], *, target_field: str = "TARGET_TASK_ID"
) -> list[str]:
    delivery = fields.get("DELIVERY", "")
    target = fields.get(target_field, "")
    if delivery and TASK_MESSAGE_RE.fullmatch(delivery):
        delivered_target = delivery.split(":", 1)[1]
        if target and delivered_target != target:
            return [f"DELIVERY task id must equal {target_field}"]
    return []


def validate_target_settings(fields: dict[str, str]) -> list[str]:
    if fields.get("TARGET_SETTINGS", "").casefold() != "preserve":
        return [
            "TARGET_SETTINGS must be preserve; task-message reports must omit model and thinking overrides"
        ]
    return []


def validate_required_task_message(fields: dict[str, str]) -> list[str]:
    errors: list[str] = []
    delivery = fields.get("DELIVERY", "")
    if delivery and not TASK_MESSAGE_RE.fullmatch(delivery):
        errors.append("DELIVERY must be task_message:<target-task-id>")
    errors.extend(validate_task_message_target(fields))
    errors.extend(validate_target_settings(fields))
    return errors


def validate(kind: str, fields: dict[str, str]) -> list[str]:
    """Validate portable packet shape; use validate_live or the CLI at boundaries."""
    errors = schema_integrity_errors(kind)
    framed_fields = sorted(
        name for name, value in fields.items() if has_delegation_framing(value)
    )
    if framed_fields:
        errors.append(
            "App-managed delegation framing must not appear inside packet fields: "
            + ", ".join(framed_fields)
        )
    recognized_obsolete = obsolete_fields(kind)
    unknown = sorted(
        set(fields) - set(allowed_fields(kind)) - recognized_obsolete
    )
    if unknown:
        errors.append("unknown packet fields: " + ", ".join(unknown))
    for name in REQUIRED[kind]:
        if name not in fields:
            errors.append(f"missing field: {name}")
        elif not fields[name]:
            errors.append(f"empty field: {name}")

    add_obsolete_errors(errors, fields, recognized_obsolete)

    if kind in {"binding", "write", "review", "design_handoff"}:
        if fields.get("TASK_ENVIRONMENT", "").casefold() != "local":
            errors.append(
                "TASK_ENVIRONMENT must be local; App-managed worktree tasks are forbidden"
            )
    if kind in {"write", "review", "design_handoff"}:
        if (
            fields.get("TASK_ARCHIVE_POLICY", "").casefold()
            != "dispatching_authority_after_acceptance"
        ):
            errors.append(
                "TASK_ARCHIVE_POLICY must be dispatching_authority_after_acceptance"
            )

    if kind in {
        "write",
        "review",
        "update",
        "design_handoff",
        "delivery_update",
        "design_reopen",
        "design_decision",
    }:
        errors.extend(validate_orchestration_mode(fields))

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
            errors.append(
                "TASK_MODE must be design_authority, delivery_controller, write, "
                "review_root, or review_worktree"
            )
        if repository_root and actual_cwd and normalized_path(repository_root) != normalized_path(actual_cwd):
            errors.append("ACTUAL_THREAD_CWD must equal REPOSITORY_ROOT")
        if repository_root and worktree_root and not is_descendant_path(worktree_root, repository_root):
            errors.append("WORKTREE_ROOT must be below REPOSITORY_ROOT")
        if mode in {"design_authority", "delivery_controller", "review_root"}:
            if repository_root and execution_path and normalized_path(repository_root) != normalized_path(execution_path):
                errors.append(f"{mode} EXECUTION_PATH must equal REPOSITORY_ROOT")
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
        if fields.get("SOURCE_ROLE") != "delivery_controller":
            errors.append("write SOURCE_ROLE must be delivery_controller")
        if fields.get("TARGET_ROLE") != "peer_writer":
            errors.append("write TARGET_ROLE must be peer_writer")
        errors.extend(
            validate_concrete_task_id(
                "REPORT_TO_TASK_ID", fields.get("REPORT_TO_TASK_ID", "")
            )
        )
        if fields.get("AUTHORITY_BASELINE") and has_placeholder(
            fields["AUTHORITY_BASELINE"]
        ):
            errors.append("AUTHORITY_BASELINE must not contain placeholders")
        design_checkpoint = fields.get("DESIGN_CHECKPOINT", "")
        if fields.get("ORCHESTRATION_MODE") == "architected":
            if not design_checkpoint:
                errors.append("architected write requires DESIGN_CHECKPOINT")
            else:
                errors.extend(
                    validate_checkpoint("DESIGN_CHECKPOINT", design_checkpoint)
                )
        elif design_checkpoint:
            errors.append("delivery write must not declare DESIGN_CHECKPOINT")
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
        review_class = fields.get("REVIEW_CLASS", "")
        review_depth = fields.get("REVIEW_DEPTH", "")
        if review_class and review_class not in REVIEW_CLASSES:
            errors.append("REVIEW_CLASS must be design, governance, or implementation")
        if review_depth and review_depth not in REVIEW_DEPTHS:
            errors.append("REVIEW_DEPTH must be delta or full")
        if fields.get("TARGET_ROLE") != "peer_reviewer":
            errors.append("review TARGET_ROLE must be peer_reviewer")
        if review_class == "design":
            if fields.get("ORCHESTRATION_MODE") != "architected":
                errors.append("design review requires ORCHESTRATION_MODE=architected")
            if fields.get("SOURCE_ROLE") != "design_authority":
                errors.append("design review SOURCE_ROLE must be design_authority")
        elif review_class == "implementation" and fields.get(
            "SOURCE_ROLE"
        ) != "delivery_controller":
            errors.append(
                "implementation review SOURCE_ROLE must be delivery_controller"
            )
        elif review_class == "governance":
            source_role = fields.get("SOURCE_ROLE", "")
            if source_role not in {"delivery_controller", "design_authority"}:
                errors.append(
                    "governance review SOURCE_ROLE must be delivery_controller or design_authority"
                )
            if (
                source_role == "design_authority"
                and fields.get("ORCHESTRATION_MODE") != "architected"
            ):
                errors.append(
                    "governance review from design_authority requires ORCHESTRATION_MODE=architected"
                )
        errors.extend(
            validate_concrete_task_id(
                "REPORT_TO_TASK_ID", fields.get("REPORT_TO_TASK_ID", "")
            )
        )
        design_checkpoint = fields.get("DESIGN_CHECKPOINT", "")
        if fields.get("ORCHESTRATION_MODE") == "architected":
            if not design_checkpoint:
                errors.append("architected review requires DESIGN_CHECKPOINT")
            else:
                errors.extend(
                    validate_checkpoint("DESIGN_CHECKPOINT", design_checkpoint)
                )
        elif design_checkpoint:
            errors.append("delivery review must not declare DESIGN_CHECKPOINT")
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
        if review_depth == "delta" and ".." not in commit_or_range:
            errors.append("delta review requires an exact full-SHA range")
        full_review_reason = fields.get("FULL_REVIEW_REASON", "")
        if review_depth == "full" and not full_review_reason:
            errors.append("full review requires FULL_REVIEW_REASON")
        if review_depth == "delta" and full_review_reason:
            errors.append("delta review must not declare FULL_REVIEW_REASON")
        review_budget = fields.get("REVIEW_BUDGET", "")
        if review_budget:
            budget_folded = review_budget.casefold()
            missing_parts = [
                part for part in REVIEW_BUDGET_PARTS if part not in budget_folded
            ]
            if missing_parts:
                errors.append(
                    "REVIEW_BUDGET must declare context=, checks=, and expand_if="
                )
        limit = REVIEW_PACKET_CHAR_LIMITS.get(review_depth)
        if limit is not None and packet_char_count(fields) > limit:
            errors.append(
                f"{review_depth} review packet exceeds {limit} characters; "
                "reference exact paths and criterion ids instead of restating history"
            )
        if review_class == "design":
            design_checkpoint = fields.get("DESIGN_CHECKPOINT", "")
            target_checkpoint = re.split(r"\.\.\.?", commit_or_range)[-1]
            if (
                FULL_SHA_RE.fullmatch(design_checkpoint)
                and FULL_SHA_RE.fullmatch(target_checkpoint)
                and design_checkpoint.casefold() != target_checkpoint.casefold()
            ):
                errors.append(
                    "design review TARGET_COMMIT_OR_RANGE must end at DESIGN_CHECKPOINT"
                )
        for name in (
            "ACCEPTANCE_BASELINE",
            "THREAT_MODEL",
            "NON_GOALS",
            "REVIEW_SCOPE",
            "REVIEW_BUDGET",
            "FULL_REVIEW_REASON",
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
    if kind == "design_handoff" and model_policy:
        errors.extend(validate_model("delivery", model_policy))

    if kind == "design_handoff":
        if fields.get("ORCHESTRATION_MODE") != "architected":
            errors.append("design handoff requires ORCHESTRATION_MODE=architected")
        if fields.get("SOURCE_ROLE") != "design_authority":
            errors.append("design handoff SOURCE_ROLE must be design_authority")
        if fields.get("TARGET_ROLE") != "delivery_controller":
            errors.append("design handoff TARGET_ROLE must be delivery_controller")
        design_task_id = fields.get("DESIGN_TASK_ID", "")
        delivery_task_id = fields.get("DELIVERY_TASK_ID", "")
        report_to = fields.get("REPORT_TO_TASK_ID", "")
        errors.extend(validate_concrete_task_id("DESIGN_TASK_ID", design_task_id))
        if delivery_task_id.casefold() != "pending":
            errors.extend(
                validate_concrete_task_id("DELIVERY_TASK_ID", delivery_task_id)
            )
        errors.extend(validate_concrete_task_id("REPORT_TO_TASK_ID", report_to))
        if design_task_id and report_to and design_task_id != report_to:
            errors.append("REPORT_TO_TASK_ID must equal DESIGN_TASK_ID")
        repository_root = fields.get("REPOSITORY_ROOT", "")
        if repository_root and not is_absolute_path(repository_root):
            errors.append("REPOSITORY_ROOT must be absolute")
        errors.extend(
            validate_checkpoint(
                "DESIGN_CHECKPOINT", fields.get("DESIGN_CHECKPOINT", "")
            )
        )
        if fields.get("DESIGN_REVIEW_STATUS", "").casefold() != "pass":
            errors.append("DESIGN_REVIEW_STATUS must be PASS")
        for name in (
            "DESIGN_REVIEW_EVIDENCE",
            "OBJECTIVE",
            "AUTHORITATIVE_INPUTS",
            "FROZEN_DECISIONS",
            "NON_GOALS",
            "ACCEPTANCE_BASELINE",
            "IMPLEMENTATION_BOUNDARY",
            "EXTERNAL_GATES",
            "DESIGN_REOPEN_RULE",
        ):
            if fields.get(name) and has_placeholder(fields[name]):
                errors.append(f"{name} must not contain placeholders")

    if kind == "delivery_update":
        if fields.get("ORCHESTRATION_MODE") != "architected":
            errors.append("delivery update requires ORCHESTRATION_MODE=architected")
        if fields.get("SOURCE_ROLE") != "delivery_controller":
            errors.append("delivery update SOURCE_ROLE must be delivery_controller")
        if fields.get("TARGET_ROLE") != "design_authority":
            errors.append("delivery update TARGET_ROLE must be design_authority")
        design_task_id = fields.get("DESIGN_TASK_ID", "")
        delivery_task_id = fields.get("DELIVERY_TASK_ID", "")
        target_task_id = fields.get("TARGET_TASK_ID", "")
        errors.extend(validate_concrete_task_id("DESIGN_TASK_ID", design_task_id))
        errors.extend(
            validate_concrete_task_id("DELIVERY_TASK_ID", delivery_task_id)
        )
        errors.extend(validate_concrete_task_id("TARGET_TASK_ID", target_task_id))
        if design_task_id and target_task_id and design_task_id != target_task_id:
            errors.append("TARGET_TASK_ID must equal DESIGN_TASK_ID")
        errors.extend(
            validate_checkpoint(
                "DESIGN_CHECKPOINT", fields.get("DESIGN_CHECKPOINT", "")
            )
        )
        update_type = fields.get("UPDATE_TYPE", "")
        if update_type and update_type not in DELIVERY_UPDATE_TYPES:
            errors.append("UPDATE_TYPE must be plan, milestone, or final")
        if fields.get("DECISION_REQUIRED", "").casefold() not in {"yes", "no"}:
            errors.append("DECISION_REQUIRED must be yes or no")
        if update_type == "plan":
            for name in DELIVERY_PLAN_FIELDS:
                if not fields.get(name):
                    errors.append(f"delivery plan missing field: {name}")
            if fields.get("MILESTONE"):
                errors.append("delivery plan must not declare MILESTONE")
        if update_type == "milestone":
            if not fields.get("MILESTONE"):
                errors.append("delivery milestone missing field: MILESTONE")
            plan_fields = sorted(
                name for name in DELIVERY_PLAN_FIELDS if fields.get(name)
            )
            if plan_fields:
                errors.append(
                    "delivery milestone must not declare plan-only fields: "
                    + ", ".join(plan_fields)
                )
        if update_type == "final":
            if fields.get("DECISION_REQUIRED", "").casefold() != "yes":
                errors.append("delivery final requires DECISION_REQUIRED=yes")
            variant_fields = sorted(
                name
                for name in set(DELIVERY_PLAN_FIELDS) | {"MILESTONE"}
                if fields.get(name)
            )
            if variant_fields:
                errors.append(
                    "delivery final must not declare plan or milestone fields: "
                    + ", ".join(variant_fields)
                )
        for name in (
            "SUMMARY",
            "DESIGN_ALIGNMENT",
            "EVIDENCE",
            "RISKS_OR_LIMITS",
            "PENDING_ITEMS",
            "READY_SET",
            "PARALLEL_DISPATCH",
            "DEPENDENCY_GRAPH",
            "SHARED_PATH_OWNER",
            "MILESTONE",
            "NEXT",
        ):
            if fields.get(name) and has_placeholder(fields[name]):
                errors.append(f"{name} must not contain placeholders")
        errors.extend(validate_required_task_message(fields))

    if kind == "design_reopen":
        if fields.get("ORCHESTRATION_MODE") != "architected":
            errors.append("design reopen requires ORCHESTRATION_MODE=architected")
        if fields.get("SOURCE_ROLE") != "delivery_controller":
            errors.append("design reopen SOURCE_ROLE must be delivery_controller")
        if fields.get("TARGET_ROLE") != "design_authority":
            errors.append("design reopen TARGET_ROLE must be design_authority")
        design_task_id = fields.get("DESIGN_TASK_ID", "")
        delivery_task_id = fields.get("DELIVERY_TASK_ID", "")
        target_task_id = fields.get("TARGET_TASK_ID", "")
        errors.extend(validate_concrete_task_id("DESIGN_TASK_ID", design_task_id))
        errors.extend(
            validate_concrete_task_id("DELIVERY_TASK_ID", delivery_task_id)
        )
        errors.extend(validate_concrete_task_id("TARGET_TASK_ID", target_task_id))
        if design_task_id and target_task_id and design_task_id != target_task_id:
            errors.append("TARGET_TASK_ID must equal DESIGN_TASK_ID")
        errors.extend(
            validate_checkpoint(
                "DESIGN_CHECKPOINT", fields.get("DESIGN_CHECKPOINT", "")
            )
        )
        for name in (
            "AFFECTED_SCOPE",
            "CONFLICT",
            "EVIDENCE",
            "OPTIONS",
            "RECOMMENDATION",
            "PAUSED_SCOPE",
            "UNAFFECTED_WORK",
        ):
            if fields.get(name) and has_placeholder(fields[name]):
                errors.append(f"{name} must not contain placeholders")
        errors.extend(validate_required_task_message(fields))

    if kind == "design_decision":
        if fields.get("ORCHESTRATION_MODE") != "architected":
            errors.append("design decision requires ORCHESTRATION_MODE=architected")
        if fields.get("SOURCE_ROLE") != "design_authority":
            errors.append("design decision SOURCE_ROLE must be design_authority")
        if fields.get("TARGET_ROLE") != "delivery_controller":
            errors.append("design decision TARGET_ROLE must be delivery_controller")
        delivery_task_id = fields.get("DELIVERY_TASK_ID", "")
        design_task_id = fields.get("DESIGN_TASK_ID", "")
        target_task_id = fields.get("TARGET_TASK_ID", "")
        errors.extend(validate_concrete_task_id("DESIGN_TASK_ID", design_task_id))
        errors.extend(validate_concrete_task_id("DELIVERY_TASK_ID", delivery_task_id))
        errors.extend(validate_concrete_task_id("TARGET_TASK_ID", target_task_id))
        if delivery_task_id and target_task_id and delivery_task_id != target_task_id:
            errors.append("TARGET_TASK_ID must equal DELIVERY_TASK_ID")
        errors.extend(
            validate_checkpoint(
                "PRIOR_DESIGN_CHECKPOINT",
                fields.get("PRIOR_DESIGN_CHECKPOINT", ""),
            )
        )
        decision = fields.get("DECISION", "")
        if decision and decision not in DESIGN_DECISIONS:
            errors.append(
                "DECISION must be clarify, continue, hold, "
                "reopen_approved, or reopen_rejected"
            )
        updated = fields.get("UPDATED_DESIGN_CHECKPOINT", "")
        if decision == "reopen_approved":
            errors.extend(validate_checkpoint("UPDATED_DESIGN_CHECKPOINT", updated))
            prior = fields.get("PRIOR_DESIGN_CHECKPOINT", "")
            if FULL_SHA_RE.fullmatch(updated) and updated.casefold() == prior.casefold():
                errors.append(
                    "reopen_approved requires a new UPDATED_DESIGN_CHECKPOINT"
                )
            design_review_evidence = fields.get("DESIGN_REVIEW_EVIDENCE", "")
            if not design_review_evidence:
                errors.append("reopen_approved requires DESIGN_REVIEW_EVIDENCE")
            elif has_placeholder(design_review_evidence):
                errors.append("DESIGN_REVIEW_EVIDENCE must not contain placeholders")
            elif not re.search(r"\bPASS\b", design_review_evidence, re.IGNORECASE):
                errors.append("reopen_approved DESIGN_REVIEW_EVIDENCE must record PASS")
        elif updated and updated != "unchanged":
            errors.append(
                "only reopen_approved may change UPDATED_DESIGN_CHECKPOINT"
            )
        elif fields.get("DESIGN_REVIEW_EVIDENCE") and has_placeholder(
            fields["DESIGN_REVIEW_EVIDENCE"]
        ):
            errors.append("DESIGN_REVIEW_EVIDENCE must not contain placeholders")
        for name in (
            "RATIONALE",
            "AFFECTED_SCOPE",
            "AUTHORITY_BOUNDARY",
            "NEXT",
        ):
            if fields.get(name) and has_placeholder(fields[name]):
                errors.append(f"{name} must not contain placeholders")
        errors.extend(validate_required_task_message(fields))

    if kind == "update":
        errors.extend(validate_concrete_task_id("TASK_ID", fields.get("TASK_ID", "")))
        update_class = fields.get("UPDATE_CLASS", "")
        if update_class and update_class not in UPDATE_CLASSES:
            errors.append(
                "UPDATE_CLASS must be design_review, governance_audit, or implementation"
            )
        source_role = fields.get("SOURCE_ROLE", "")
        target_role = fields.get("TARGET_ROLE", "")
        if update_class == "design_review":
            if fields.get("ORCHESTRATION_MODE") != "architected":
                errors.append("design review update requires ORCHESTRATION_MODE=architected")
            if source_role != "peer_reviewer":
                errors.append("design review update SOURCE_ROLE must be peer_reviewer")
            if target_role != "design_authority":
                errors.append("design review update TARGET_ROLE must be design_authority")
        elif update_class == "implementation":
            if source_role not in {"peer_reviewer", "peer_writer"}:
                errors.append(
                    "implementation update SOURCE_ROLE must be peer_writer or peer_reviewer"
                )
            if target_role != "delivery_controller":
                errors.append(
                    "implementation update TARGET_ROLE must be delivery_controller"
                )
        elif update_class == "governance_audit":
            if source_role != "peer_reviewer":
                errors.append(
                    "governance audit update SOURCE_ROLE must be peer_reviewer"
                )
            if target_role not in {"delivery_controller", "design_authority"}:
                errors.append(
                    "governance audit update TARGET_ROLE must be delivery_controller or design_authority"
                )
            if (
                target_role == "design_authority"
                and fields.get("ORCHESTRATION_MODE") != "architected"
            ):
                errors.append(
                    "governance audit update to design_authority requires ORCHESTRATION_MODE=architected"
                )
        errors.extend(
            validate_concrete_task_id(
                "TARGET_TASK_ID", fields.get("TARGET_TASK_ID", "")
            )
        )
        design_checkpoint = fields.get("DESIGN_CHECKPOINT", "")
        if fields.get("ORCHESTRATION_MODE") == "architected":
            if not design_checkpoint:
                errors.append("architected update requires DESIGN_CHECKPOINT")
            else:
                errors.extend(
                    validate_checkpoint("DESIGN_CHECKPOINT", design_checkpoint)
                )
        elif design_checkpoint:
            errors.append("delivery update must not declare DESIGN_CHECKPOINT")
        status = fields.get("STATUS", "")
        if status and status not in STATUSES:
            errors.append("STATUS must be progress, blocked, or final")
        errors.extend(validate_required_task_message(fields))
        if status == "final":
            if fields.get("EVIDENCE", "").casefold() == "none":
                errors.append("final EVIDENCE must include commands or artifacts")
            for name in ("RISKS_OR_LIMITS", "PENDING_ITEMS"):
                if name not in fields:
                    errors.append(f"final report missing field: {name}")
                elif not fields[name]:
                    errors.append(f"final report empty field: {name}")
        for name in (
            "SUMMARY",
            "EVIDENCE",
            "RISKS_OR_LIMITS",
            "PENDING_ITEMS",
            "NEXT",
        ):
            if fields.get(name) and has_placeholder(fields[name]):
                errors.append(f"{name} must not contain placeholders")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=sorted(REQUIRED), required=True)
    parser.add_argument(
        "contract",
        help="UTF-8 packet path, or - to read the packet from stdin",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        text = (
            sys.stdin.read()
            if args.contract == "-"
            else Path(args.contract).read_text(encoding="utf-8")
        )
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
