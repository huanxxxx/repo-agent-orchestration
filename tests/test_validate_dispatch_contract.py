from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = (
    ROOT
    / "skill"
    / "repo-agent-orchestration"
    / "scripts"
    / "validate_dispatch_contract.py"
)
SPEC = importlib.util.spec_from_file_location("dispatch_validator", VALIDATOR_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


VALID_WRITE = """
TASK_ID: write-1
WORKTREE_POLICY: repo_local_only
WORKTREE_ROOT: D:\\repo\\.worktrees
WORKTREE: D:\\repo\\.worktrees\\write-1
BRANCH: codex/write-1
BASE_COMMIT: 0123456789abcdef0123456789abcdef01234567
OBJECTIVE: implement one change
OWNED_PATHS: src/example.ts
DO_NOT_TOUCH: shared state
ACCEPTANCE: focused tests pass
REQUIRED_TESTS: python -m unittest
INTEGRATION_TARGET: main
MODEL_POLICY: repo_write_default:execution-model/medium
EXPECTED_NEXT_MILESTONE: tests_complete
NO_REPORT_CHECK_AFTER: none
"""

VALID_BINDING = """
TASK_ID: write-1
EXPECTED_WORKTREE: D:\\repo\\.worktrees\\write-1
TASK_PROJECT_ID: local-write-1
TASK_PROJECT_PATH: D:\\repo\\.worktrees\\write-1
TASK_ENVIRONMENT: local
ACTUAL_THREAD_CWD: D:\\repo\\.worktrees\\write-1
ACTUAL_THREAD_PROJECT_ID: local-write-1
BINDING_STATUS: verified
"""

VALID_REVIEW = """
REVIEW_TASK_ID: review-1
TARGET_WORKTREE: D:\\repo\\.worktrees\\write-1
TARGET_BRANCH: codex/write-1
TARGET_COMMIT_OR_RANGE: 0123456789abcdef0123456789abcdef01234567
READ_ONLY: true
REVIEW_SCOPE: frozen candidate
ACCEPTANCE: report PASS or findings
REQUIRED_CHECKS: inspect diff
REPORT_FORMAT: findings with evidence
MODEL_POLICY: app_default
EXPECTED_NEXT_MILESTONE: final
NO_REPORT_CHECK_AFTER: current_turn
"""

VALID_FINAL = """
TASK_ID: write-1
MILESTONE: final
SUMMARY: implementation and verification complete
EVIDENCE: commit=0123456789abcdef0123456789abcdef01234567; tests=PASS
RISKS_OR_LIMITS: none
PENDING_ITEMS: none
BLOCKER_OR_NEXT: owner=controller; action=verify_and_close; check_after=none
"""


class ContractValidationTests(unittest.TestCase):
    def validate(self, kind: str, text: str) -> list[str]:
        return VALIDATOR.validate(kind, VALIDATOR.parse_fields(text))

    def test_valid_write(self) -> None:
        self.assertEqual(self.validate("write", VALID_WRITE), [])

    def test_valid_existing_worktree_binding(self) -> None:
        self.assertEqual(self.validate("binding", VALID_BINDING), [])

    def test_binding_accepts_equivalent_windows_extended_path(self) -> None:
        equivalent = VALID_BINDING.replace(
            "TASK_PROJECT_PATH: D:\\repo\\.worktrees\\write-1",
            "TASK_PROJECT_PATH: \\\\?\\D:\\repo\\.worktrees\\write-1\\",
        )
        self.assertEqual(self.validate("binding", equivalent), [])

    def test_binding_rejects_projectless_foreign_cwd_and_app_worktree(self) -> None:
        invalid = (
            VALID_BINDING.replace("local-write-1", "projectless")
            .replace(
                "ACTUAL_THREAD_CWD: D:\\repo\\.worktrees\\write-1",
                "ACTUAL_THREAD_CWD: C:\\Users\\person\\Documents\\Codex\\write-1",
            )
            .replace("TASK_ENVIRONMENT: local", "TASK_ENVIRONMENT: worktree")
        )
        errors = "\n".join(self.validate("binding", invalid))
        self.assertIn("TASK_PROJECT_ID must identify", errors)
        self.assertIn("ACTUAL_THREAD_PROJECT_ID must be non-null", errors)
        self.assertIn("ACTUAL_THREAD_CWD must equal", errors)
        self.assertIn("TASK_ENVIRONMENT must be local", errors)

    def test_binding_rejects_root_project_path_and_mismatched_project_id(self) -> None:
        invalid = (
            VALID_BINDING.replace(
                "TASK_PROJECT_PATH: D:\\repo\\.worktrees\\write-1",
                "TASK_PROJECT_PATH: D:\\repo",
            )
            .replace(
                "ACTUAL_THREAD_PROJECT_ID: local-write-1",
                "ACTUAL_THREAD_PROJECT_ID: local-other",
            )
        )
        errors = "\n".join(self.validate("binding", invalid))
        self.assertIn("TASK_PROJECT_PATH must equal", errors)
        self.assertIn("ACTUAL_THREAD_PROJECT_ID must equal", errors)

    def test_write_rejects_implicit_model_short_sha_and_external_tree(self) -> None:
        invalid = (
            VALID_WRITE.replace("D:\\repo\\.worktrees\\write-1", "D:\\outside\\write-1")
            .replace("0123456789abcdef0123456789abcdef01234567", "abc123")
            .replace("repo_write_default:execution-model/medium", "app_default")
        )
        errors = "\n".join(self.validate("write", invalid))
        self.assertIn("WORKTREE must be below WORKTREE_ROOT", errors)
        self.assertIn("BASE_COMMIT must be a full", errors)
        self.assertIn("app_default is reserved", errors)

    def test_valid_review(self) -> None:
        self.assertEqual(self.validate("review", VALID_REVIEW), [])

    def test_review_rejects_a_writable_boundary(self) -> None:
        invalid = VALID_REVIEW + "\nWORKTREE: D:\\repo\\.worktrees\\review-1\n"
        errors = "\n".join(self.validate("review", invalid))
        self.assertIn("must not create a writable boundary", errors)

    def test_valid_final_update(self) -> None:
        self.assertEqual(self.validate("update", VALID_FINAL), [])

    def test_final_requires_evidence_risks_pending_and_controller_owner(self) -> None:
        invalid = """
TASK_ID: write-1
MILESTONE: final
SUMMARY: done
EVIDENCE: none
BLOCKER_OR_NEXT: owner=task; action=none; check_after=daily
"""
        errors = "\n".join(self.validate("update", invalid))
        self.assertIn("final EVIDENCE must include", errors)
        self.assertIn("final milestone missing field: RISKS_OR_LIMITS", errors)
        self.assertIn("final milestone missing field: PENDING_ITEMS", errors)
        self.assertIn("check_after must be", errors)
        self.assertIn("must hand ownership to controller", errors)


if __name__ == "__main__":
    unittest.main()
