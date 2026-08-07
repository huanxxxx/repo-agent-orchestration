#!/usr/bin/env python3
"""Install repo-agent-orchestration into one target Git repository."""

from __future__ import annotations

import argparse
import codecs
import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


BEGIN_MARKER = "<!-- repo-agent-orchestration:begin -->"
END_MARKER = "<!-- repo-agent-orchestration:end -->"
DEFAULT_EXTERNAL_GATES = (
    "merge main; push; deploy; publish; production data; credentials; permissions"
)
TEXT_PACKAGE_SUFFIXES = {".md", ".py", ".txt", ".yaml", ".yml", ".toml", ".json"}


@dataclass(frozen=True)
class Settings:
    main_branch: str
    worktree_root: Path
    branch_prefix: str = "codex/"
    task_host_policy: str = "repository_project_local"
    controller_model_policy: str = "app_current_task"
    write_task_model: str = "gpt-5.6-luna/max"
    review_task_model: str = "app_default"
    shared_integration_paths: str = "none"
    external_gates: str = DEFAULT_EXTERNAL_GATES


def run_git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={repo}", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ValueError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip() if result.returncode == 0 else ""


def resolve_repository(value: Path) -> Path:
    if not value.is_absolute():
        raise ValueError("--repo must be an absolute path")
    if not value.is_dir() or value.is_symlink():
        raise ValueError("--repo must be an existing non-symlink directory")
    supplied = value.resolve()
    top_level = Path(run_git(supplied, "rev-parse", "--show-toplevel")).resolve()
    if os.path.normcase(str(supplied)) != os.path.normcase(str(top_level)):
        raise ValueError("--repo must name the exact Git repository root")
    return supplied


def primary_worktree_root(repo: Path) -> Path:
    common_dir = Path(
        run_git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    ).resolve()
    if common_dir.name.casefold() != ".git":
        return repo
    primary = common_dir.parent.resolve()
    registered = {
        Path(line.removeprefix("worktree ")).resolve()
        for line in run_git(repo, "worktree", "list", "--porcelain").splitlines()
        if line.startswith("worktree ")
    }
    return primary if primary in registered else repo


def detect_main_branch(repo: Path) -> str:
    remote_head = run_git(
        repo, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD", check=False
    )
    if remote_head.startswith("origin/"):
        return remote_head.removeprefix("origin/")
    for candidate in ("main", "master", "trunk"):
        if run_git(
            repo, "show-ref", "--verify", "--quiet", f"refs/heads/{candidate}", check=False
        ) == "":
            result = subprocess.run(
                [
                    "git",
                    "-c",
                    f"safe.directory={repo}",
                    "-C",
                    str(repo),
                    "show-ref",
                    "--verify",
                    "--quiet",
                    f"refs/heads/{candidate}",
                ],
                check=False,
            )
            if result.returncode == 0:
                return candidate
    current = run_git(repo, "branch", "--show-current", check=False)
    return current or "main"


def setting_values(settings: Settings) -> tuple[tuple[str, str], ...]:
    return (
        ("ORCHESTRATION_SKILL", "$repo-agent-orchestration"),
        ("MAIN_BRANCH", settings.main_branch),
        ("ROOT_WORKTREE_POLICY", "observe_integrate_validate"),
        ("WORKTREE_ROOT", str(settings.worktree_root)),
        ("BRANCH_PREFIX", settings.branch_prefix),
        ("TASK_HOST_POLICY", settings.task_host_policy),
        ("CONTROLLER_MODEL_POLICY", settings.controller_model_policy),
        ("WRITE_TASK_MODEL", settings.write_task_model),
        ("REVIEW_TASK_MODEL", settings.review_task_model),
        ("SHARED_INTEGRATION_PATHS", settings.shared_integration_paths),
        ("EXTERNAL_GATES", settings.external_gates),
    )


def render_block(
    settings: Settings, newline: str = "\n", include_keys: set[str] | None = None
) -> str:
    values = setting_values(settings)
    for key, value in values:
        if not value or any(token in value for token in ("\r", "\n", "\0", "```", BEGIN_MARKER, END_MARKER)):
            raise ValueError(f"invalid AGENTS.md configuration value: {key}")
    if include_keys is not None:
        values = tuple((key, value) for key, value in values if key in include_keys)
    body = newline.join(f"{key}: {value}" for key, value in values)
    activation = (
        "- Use the repository-local `$repo-agent-orchestration` Skill for implementation, "
        "formal review, parallel dispatch, handoffs, recovery, integration, and closure."
    )
    failure = (
        "- If the Skill or a required task, path, message, or model-binding capability is "
        "unavailable, stop and report; do not silently fall back to another execution route."
    )
    return newline.join(
        (
            BEGIN_MARKER,
            "## Agent Orchestration Profile",
            "",
            activation,
            failure,
            "",
            "```text",
            body,
            "```",
            END_MARKER,
        )
    )


def update_agents_content(existing: str | None, settings: Settings, newline: str) -> str:
    if existing is None:
        block = render_block(settings, newline)
        return f"# Repository Agent Instructions{newline}{newline}{block}{newline}"
    begin_count = existing.count(BEGIN_MARKER)
    end_count = existing.count(END_MARKER)
    if begin_count != end_count or begin_count > 1:
        raise ValueError("AGENTS.md has malformed or duplicate orchestration markers")
    outside = existing
    if begin_count == 1:
        start = existing.index(BEGIN_MARKER)
        end = existing.index(END_MARKER, start) + len(END_MARKER)
        outside = existing[:start] + existing[end:]
    existing_keys = {
        match.group(1)
        for match in re.finditer(r"(?m)^([A-Z][A-Z0-9_]*)\s*:", outside)
    }
    include_keys = {key for key, _ in setting_values(settings) if key not in existing_keys}
    block = render_block(settings, newline, include_keys)
    if begin_count == 1:
        return existing[:start] + block + existing[end:]
    separator = "" if not existing else newline * (1 if existing.endswith(newline) else 2)
    return existing + separator + block + newline


def read_text_format(path: Path) -> tuple[str | None, str, bool]:
    if not path.exists():
        return None, os.linesep, False
    if not path.is_file() or path.is_symlink():
        raise ValueError("AGENTS.md must be a regular non-symlink file")
    raw = path.read_bytes()
    has_bom = raw.startswith(codecs.BOM_UTF8)
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    return text, newline, has_bom


def managed_profile_values(existing: str | None) -> dict[str, str]:
    if not existing or BEGIN_MARKER not in existing or END_MARKER not in existing:
        return {}
    start = existing.index(BEGIN_MARKER) + len(BEGIN_MARKER)
    end = existing.index(END_MARKER, start)
    block = existing[start:end]
    return {
        match.group(1): match.group(2).strip()
        for match in re.finditer(r"(?m)^([A-Z][A-Z0-9_]*)\s*:\s*(.+)$", block)
    }


def write_bytes_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content)
    try:
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def source_skill_root() -> Path:
    root = Path(__file__).resolve().parents[1]
    source = root / "skill" / "repo-agent-orchestration"
    if not (source / "SKILL.md").is_file():
        raise ValueError("installable Skill package is missing")
    return source


def package_files(source: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Skill package contains a symlink: {path}")
        if path.is_file():
            relative = path.relative_to(source)
            if "__pycache__" in relative.parts or relative.suffix.casefold() == ".pyc":
                continue
            files.append(relative)
    return files


def package_payload(path: Path) -> bytes:
    payload = path.read_bytes()
    if path.suffix.casefold() in TEXT_PACKAGE_SUFFIXES:
        return payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return payload


def install_repository(repo_value: Path, settings: Settings, dry_run: bool = False) -> dict[str, object]:
    repo = resolve_repository(repo_value)
    profile_root = primary_worktree_root(repo)
    resolved_worktree_root = settings.worktree_root.resolve()
    try:
        relative_worktree_root = resolved_worktree_root.relative_to(profile_root)
    except ValueError as exc:
        raise ValueError("WORKTREE_ROOT must be inside the target repository") from exc
    if not relative_worktree_root.parts:
        raise ValueError("WORKTREE_ROOT must not equal the repository root")
    source = source_skill_root()
    destination = repo / ".agents" / "skills" / "repo-agent-orchestration"
    if destination.exists() and (not destination.is_dir() or destination.is_symlink()):
        raise ValueError("Skill destination must be a regular directory")

    files = package_files(source)
    if destination.exists():
        extras = [
            path.relative_to(destination)
            for path in destination.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
            and path.relative_to(destination) not in files
        ]
        if extras:
            joined = ", ".join(str(path) for path in extras)
            raise ValueError(f"Skill destination contains unmanaged files: {joined}")

    agents_path = repo / "AGENTS.md"
    existing, newline, has_bom = read_text_format(agents_path)
    updated = update_agents_content(existing, settings, newline)
    agents_changed = existing != updated

    changed_skill_files = 0
    for relative in files:
        source_file = source / relative
        target_file = destination / relative
        payload = package_payload(source_file)
        if target_file.exists():
            if not target_file.is_file() or target_file.is_symlink():
                raise ValueError(f"Skill target is not a regular file: {target_file}")
            if target_file.read_bytes() == payload:
                continue
        changed_skill_files += 1
        if not dry_run:
            write_bytes_atomic(target_file, payload)

    if agents_changed and not dry_run:
        encoding = "utf-8-sig" if has_bom else "utf-8"
        write_bytes_atomic(agents_path, updated.encode(encoding))

    result = {
        "repository": str(repo),
        "skill_destination": str(destination),
        "skill_files": len(files),
        "changed_skill_files": changed_skill_files,
        "agents_created": existing is None,
        "agents_changed": agents_changed,
        "dry_run": dry_run,
    }
    result["up_to_date"] = not changed_skill_files and not agents_changed
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--main-branch")
    parser.add_argument("--worktree-root", type=Path)
    parser.add_argument("--branch-prefix")
    parser.add_argument("--write-task-model")
    parser.add_argument("--review-task-model")
    parser.add_argument("--shared-integration-paths")
    parser.add_argument("--external-gates")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--check",
        action="store_true",
        help="write nothing and exit nonzero when the installed Skill or managed profile differs",
    )
    args = parser.parse_args()

    repo = resolve_repository(args.repo)
    existing, _, _ = read_text_format(repo / "AGENTS.md")
    current = managed_profile_values(existing)
    profile_root = primary_worktree_root(repo)
    worktree_root = (
        args.worktree_root
        or Path(current.get("WORKTREE_ROOT", str(profile_root / ".worktrees")))
    ).resolve()
    if not worktree_root.is_absolute():
        raise ValueError("worktree root must be absolute")
    settings = Settings(
        main_branch=args.main_branch or current.get("MAIN_BRANCH") or detect_main_branch(repo),
        worktree_root=worktree_root,
        branch_prefix=args.branch_prefix or current.get("BRANCH_PREFIX", "codex/"),
        task_host_policy=current.get("TASK_HOST_POLICY", "repository_project_local"),
        controller_model_policy=current.get("CONTROLLER_MODEL_POLICY", "app_current_task"),
        write_task_model=args.write_task_model
        or current.get("WRITE_TASK_MODEL", "gpt-5.6-luna/max"),
        review_task_model=args.review_task_model
        or current.get("REVIEW_TASK_MODEL", "app_default"),
        shared_integration_paths=args.shared_integration_paths
        or current.get("SHARED_INTEGRATION_PATHS", "none"),
        external_gates=args.external_gates
        or current.get("EXTERNAL_GATES", DEFAULT_EXTERNAL_GATES),
    )
    result = install_repository(repo, settings, dry_run=args.dry_run or args.check)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not args.check or result["up_to_date"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
