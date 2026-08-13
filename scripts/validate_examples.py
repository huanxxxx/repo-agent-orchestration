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
    "valid-write-app-default.txt": ("write", ()),
    "valid-write-luna-max.txt": ("write", ()),
    "valid-review.txt": ("review", ()),
    "valid-final-update.txt": ("update", ()),
    "valid-design-handoff.txt": ("design_handoff", ()),
    "valid-delivery-plan.txt": ("delivery_update", ()),
    "valid-delivery-milestone.txt": ("delivery_update", ()),
    "valid-design-reopen.txt": ("design_reopen", ()),
    "valid-design-decision.txt": ("design_decision", ()),
    "invalid-projectless.txt": (
        "binding",
        ("TASK_PROJECT_ID must identify", "ACTUAL_THREAD_CWD must equal REPOSITORY_ROOT"),
    ),
    "invalid-worktree-escape.txt": (
        "binding",
        ("EXECUTION_PATH must be below WORKTREE_ROOT",),
    ),
    "invalid-app-worktree-environment.txt": (
        "write",
        ("TASK_ENVIRONMENT must be local",),
    ),
    "invalid-local-final-only.txt": (
        "update",
        ("DELIVERY must be task_message",),
    ),
    "invalid-controller-model-override.txt": (
        "update",
        ("TARGET_SETTINGS must be preserve",),
    ),
    "invalid-obsolete-report-fields.txt": (
        "update",
        ("obsolete protocol fields must be removed",),
    ),
    "invalid-obsolete-dispatch-fields.txt": (
        "write",
        ("obsolete protocol fields must be removed",),
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
