#!/usr/bin/env python3
"""Run every published contract example against the bundled validator."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "skill" / "repo-agent-orchestration" / "scripts" / "validate_dispatch_contract.py"
CASES = {
    "valid-binding-windows.txt": ("binding", ()),
    "valid-write-luna-max.txt": ("write", ()),
    "valid-review.txt": ("review", ()),
    "valid-final-update.txt": ("update", ()),
    "invalid-projectless.txt": (
        "binding",
        ("TASK_PROJECT_ID must identify", "ACTUAL_THREAD_CWD must equal REPOSITORY_ROOT"),
    ),
    "invalid-worktree-escape.txt": (
        "binding",
        ("EXECUTION_WORKTREE must be below WORKTREE_ROOT",),
    ),
    "invalid-local-final-only.txt": (
        "update",
        ("REPORT_DELIVERY must be task_message",),
    ),
    "invalid-ended-owner-task.txt": (
        "update",
        (
            "final milestone must hand ownership to controller",
            "TURN_STATE=ending requires owner=controller",
        ),
    ),
    "invalid-continuous-controller-wait.txt": (
        "write",
        (
            "CONTROLLER_AFTER_DISPATCH must be event_driven_yield",
            "current_turn is ambiguous and forbidden",
        ),
    ),
}


def load_validator():
    spec = importlib.util.spec_from_file_location("dispatch_validator_examples", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load dispatch validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_examples() -> dict[str, object]:
    validator = load_validator()
    contracts = ROOT / "examples" / "contracts"
    results: dict[str, object] = {}
    passed = True
    for name, (kind, expected_errors) in CASES.items():
        text = (contracts / name).read_text(encoding="utf-8")
        errors = validator.validate(kind, validator.parse_fields(text))
        if expected_errors:
            matched = all(any(fragment in error for error in errors) for fragment in expected_errors)
        else:
            matched = not errors
        passed = passed and matched
        results[name] = {
            "kind": kind,
            "expected": "invalid" if expected_errors else "valid",
            "matched": matched,
            "errors": errors,
        }
    return {"passed": passed, "cases": results}


def main() -> int:
    result = run_examples()
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
