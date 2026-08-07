#!/usr/bin/env python3
"""Run a local Git-worktree and dispatch-contract demonstration."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "skill" / "repo-agent-orchestration" / "scripts" / "validate_dispatch_contract.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("dispatch_validator_demo", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load dispatch validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def validate(validator, kind: str, packet: str) -> list[str]:
    return validator.validate(kind, validator.parse_fields(packet))


def binding_packet(repository: Path, worktree_root: Path, execution_worktree: Path, task_id: str) -> str:
    return f"""
TASK_ID: {task_id}
TASK_MODE: write
REPOSITORY_ROOT: {repository}
WORKTREE_ROOT: {worktree_root}
EXECUTION_PATH: {execution_worktree}
TASK_PROJECT_ID: demo-saved-project
ACTUAL_THREAD_CWD: {repository}
ACTUAL_THREAD_PROJECT_ID: demo-saved-project
"""


def write_packet(worktree_root: Path, worktree: Path, branch: str, head: str) -> str:
    task_name = branch.removeprefix("codex/")
    return f"""
TASK_ID: {task_name}
WORKTREE_ROOT: {worktree_root}
WORKTREE: {worktree}
BRANCH: {branch}
BASE_COMMIT: {head}
OBJECTIVE: demonstrate one isolated writer
OWNED_PATHS: {task_name}/*
DO_NOT_TOUCH: the sibling writer and repository root
ACCEPTANCE: binding and isolation checks pass
REQUIRED_TESTS: python scripts/run_local_demo.py
MODEL_POLICY: repo_write_default:gpt-5.6-luna/max
"""


def run_demo() -> dict[str, object]:
    validator = load_validator()
    with tempfile.TemporaryDirectory(prefix="repo-agent-orchestration-demo-") as directory:
        repository = Path(directory).resolve() / "repository"
        repository.mkdir()
        subprocess.run(["git", "init", "-b", "main", str(repository)], check=True, capture_output=True)
        (repository / ".gitignore").write_text(".worktrees/\n", encoding="utf-8")
        (repository / "README.md").write_text("# Local demo\n", encoding="utf-8")
        git(repository, "add", ".gitignore", "README.md")
        environment = os.environ.copy()
        environment.update(
            {
                "GIT_AUTHOR_NAME": "Repo Agent Demo",
                "GIT_AUTHOR_EMAIL": "demo@example.invalid",
                "GIT_COMMITTER_NAME": "Repo Agent Demo",
                "GIT_COMMITTER_EMAIL": "demo@example.invalid",
            }
        )
        commit = subprocess.run(
            ["git", "-C", str(repository), "commit", "-m", "demo baseline"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=environment,
        )
        if commit.returncode != 0:
            raise RuntimeError(commit.stderr.strip() or commit.stdout.strip())

        head = git(repository, "rev-parse", "HEAD")
        worktree_root = repository / ".worktrees"
        worktree_root.mkdir()
        workers = {
            "backend": ("codex/demo-backend", worktree_root / "backend"),
            "frontend": ("codex/demo-frontend", worktree_root / "frontend"),
        }
        for branch, path in workers.values():
            git(repository, "worktree", "add", "-b", branch, str(path), head)

        binding_errors = {
            name: validate(validator, "binding", binding_packet(repository, worktree_root, path, f"write-{name}"))
            for name, (_, path) in workers.items()
        }
        write_errors = {
            name: validate(validator, "write", write_packet(worktree_root, path, branch, head))
            for name, (branch, path) in workers.items()
        }

        backend_branch, backend_path = workers["backend"]
        review = f"""
REVIEW_TASK_ID: review-backend
TARGET_MODE: existing_worktree
TARGET_PATH: {backend_path}
TARGET_COMMIT_OR_RANGE: {head}
READ_ONLY: true
REVIEW_SCOPE: frozen backend demo candidate
ACCEPTANCE: report PASS or findings
MODEL_POLICY: app_default
"""
        final_update = f"""
TASK_ID: write-backend
STATUS: final
SUMMARY: local demo complete
EVIDENCE: commit={head}; local_demo=PASS
RISKS_OR_LIMITS: no Codex task API or runtime-model verification
PENDING_ITEMS: none
DELIVERY: task_message:demo-controller-thread
TARGET_SETTINGS: preserve
NEXT: controller verifies and closes
"""
        escaped = worktree_root / "child" / ".." / ".." / "outside"
        invalid = binding_packet(repository, worktree_root, escaped, "invalid-projectless")
        invalid = invalid.replace("demo-saved-project", "projectless")

        registry = git(repository, "worktree", "list", "--porcelain")
        registered_paths = {
            validator.normalized_path(line.removeprefix("worktree "))
            for line in registry.splitlines()
            if line.startswith("worktree ")
        }
        invalid_errors = validate(validator, "binding", invalid)
        result = {
            "passed": all(not errors for errors in binding_errors.values())
            and all(not errors for errors in write_errors.values())
            and not validate(validator, "review", review)
            and not validate(validator, "update", final_update)
            and bool(invalid_errors),
            "writers_isolated": all(
                validator.normalized_path(str(path)) in registered_paths
                for _, path in workers.values()
            ),
            "valid_binding_errors": binding_errors,
            "valid_write_errors": write_errors,
            "invalid_binding_rejected": bool(invalid_errors),
            "invalid_binding_errors": invalid_errors,
            "root_clean": not bool(git(repository, "status", "--porcelain")),
            "evidence_limit": "Local Git and contract-gate evidence only; no Codex task was created and no runtime model was verified.",
        }
        result["passed"] = bool(result["passed"] and result["writers_isolated"] and result["root_clean"])
        return result


def main() -> int:
    result = run_demo()
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
