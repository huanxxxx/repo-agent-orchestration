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
CONTROLLER_AFTER_DISPATCH: event_driven_yield
NO_REPORT_CHECK_AFTER: current_turn_once
"""

VALID_BINDING = """
TASK_ID: write-1
REPOSITORY_ROOT: D:\\repo
WORKTREE_ROOT: D:\\repo\\.worktrees
EXECUTION_WORKTREE: D:\\repo\\.worktrees\\write-1
TASK_PROJECT_ID: local-write-1
TASK_PROJECT_PATH: D:\\repo
TASK_ENVIRONMENT: local
ACTUAL_THREAD_CWD: D:\\repo
ACTUAL_THREAD_PROJECT_ID: local-write-1
COMMAND_WORKDIR_POLICY: exact_execution_worktree
ROOT_WRITE_POLICY: forbidden
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
CONTROLLER_AFTER_DISPATCH: event_driven_yield
NO_REPORT_CHECK_AFTER: current_turn_once
"""

VALID_FINAL = """
TASK_ID: write-1
MILESTONE: final
SUMMARY: implementation and verification complete
EVIDENCE: commit=0123456789abcdef0123456789abcdef01234567; tests=PASS
RISKS_OR_LIMITS: none
PENDING_ITEMS: none
REPORT_DELIVERY: task_message:controller-thread-1
TURN_STATE: ending
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
            "TASK_PROJECT_PATH: D:\\repo",
            "TASK_PROJECT_PATH: \\\\?\\D:\\repo\\",
        )
        self.assertEqual(self.validate("binding", equivalent), [])

    def test_binding_rejects_projectless_foreign_cwd_and_app_worktree(self) -> None:
        invalid = (
            VALID_BINDING.replace("local-write-1", "projectless")
            .replace(
                "ACTUAL_THREAD_CWD: D:\\repo",
                "ACTUAL_THREAD_CWD: C:\\Users\\person\\Documents\\Codex\\write-1",
            )
            .replace("TASK_ENVIRONMENT: local", "TASK_ENVIRONMENT: worktree")
        )
        errors = "\n".join(self.validate("binding", invalid))
        self.assertIn("TASK_PROJECT_ID must identify", errors)
        self.assertIn("ACTUAL_THREAD_PROJECT_ID must be non-null", errors)
        self.assertIn("ACTUAL_THREAD_CWD must equal REPOSITORY_ROOT", errors)
        self.assertIn("TASK_ENVIRONMENT must be local", errors)

    def test_binding_rejects_root_project_path_and_mismatched_project_id(self) -> None:
        invalid = (
            VALID_BINDING.replace(
                "TASK_PROJECT_PATH: D:\\repo",
                "TASK_PROJECT_PATH: D:\\other",
            )
            .replace(
                "ACTUAL_THREAD_PROJECT_ID: local-write-1",
                "ACTUAL_THREAD_PROJECT_ID: local-other",
            )
        )
        errors = "\n".join(self.validate("binding", invalid))
        self.assertIn("TASK_PROJECT_PATH must equal REPOSITORY_ROOT", errors)
        self.assertIn("ACTUAL_THREAD_PROJECT_ID must equal", errors)

    def test_binding_rejects_execution_tree_outside_declared_root(self) -> None:
        invalid = VALID_BINDING.replace(
            "EXECUTION_WORKTREE: D:\\repo\\.worktrees\\write-1",
            "EXECUTION_WORKTREE: D:\\outside\\write-1",
        )
        errors = "\n".join(self.validate("binding", invalid))
        self.assertIn("EXECUTION_WORKTREE must be below WORKTREE_ROOT", errors)

    def test_binding_rejects_windows_parent_traversal_outside_worktree_root(self) -> None:
        for escaped in (
            "D:\\repo\\.worktrees\\..\\outside",
            "D:\\repo\\.worktrees\\child\\..\\..\\outside",
        ):
            with self.subTest(escaped=escaped):
                invalid = VALID_BINDING.replace(
                    "EXECUTION_WORKTREE: D:\\repo\\.worktrees\\write-1",
                    f"EXECUTION_WORKTREE: {escaped}",
                )
                errors = "\n".join(self.validate("binding", invalid))
                self.assertIn(
                    "EXECUTION_WORKTREE must be below WORKTREE_ROOT", errors
                )

    def test_binding_rejects_extended_windows_parent_traversal(self) -> None:
        invalid = VALID_BINDING.replace(
            "EXECUTION_WORKTREE: D:\\repo\\.worktrees\\write-1",
            "EXECUTION_WORKTREE: \\\\?\\D:\\repo\\.worktrees\\..\\outside",
        )
        errors = "\n".join(self.validate("binding", invalid))
        self.assertIn("EXECUTION_WORKTREE must be below WORKTREE_ROOT", errors)

    def test_binding_rejects_worktree_root_parent_traversal_outside_repository(self) -> None:
        invalid = VALID_BINDING.replace(
            "WORKTREE_ROOT: D:\\repo\\.worktrees",
            "WORKTREE_ROOT: D:\\repo\\child\\..\\..\\outside",
        )
        errors = "\n".join(self.validate("binding", invalid))
        self.assertIn("WORKTREE_ROOT must be below REPOSITORY_ROOT", errors)

    def test_binding_rejects_posix_parent_traversal_for_nonexistent_paths(self) -> None:
        posix = (
            VALID_BINDING.replace("D:\\repo\\.worktrees", "/repo/.worktrees")
            .replace("D:\\repo", "/repo")
            .replace(
                "EXECUTION_WORKTREE: /repo/.worktrees\\write-1",
                "EXECUTION_WORKTREE: /repo/.worktrees/child/../../outside",
            )
        )
        errors = "\n".join(self.validate("binding", posix))
        self.assertIn("EXECUTION_WORKTREE must be below WORKTREE_ROOT", errors)

    def test_binding_accepts_parent_segments_that_normalize_inside_root(self) -> None:
        normalized_inside = VALID_BINDING.replace(
            "EXECUTION_WORKTREE: D:\\repo\\.worktrees\\write-1",
            "EXECUTION_WORKTREE: D:\\repo\\.worktrees\\child\\..\\write-1",
        )
        self.assertEqual(self.validate("binding", normalized_inside), [])

    def test_binding_requires_exact_workdir_and_forbidden_root_writes(self) -> None:
        invalid = (
            VALID_BINDING.replace(
                "COMMAND_WORKDIR_POLICY: exact_execution_worktree",
                "COMMAND_WORKDIR_POLICY: prompt_path_only",
            )
            .replace("ROOT_WRITE_POLICY: forbidden", "ROOT_WRITE_POLICY: allowed")
        )
        errors = "\n".join(self.validate("binding", invalid))
        self.assertIn("COMMAND_WORKDIR_POLICY must be exact_execution_worktree", errors)
        self.assertIn("ROOT_WRITE_POLICY must be forbidden", errors)

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

    def test_write_and_review_require_a_missing_report_checkpoint(self) -> None:
        for kind, packet in (("write", VALID_WRITE), ("review", VALID_REVIEW)):
            with self.subTest(kind=kind):
                invalid = packet.replace(
                    "NO_REPORT_CHECK_AFTER: current_turn_once",
                    "NO_REPORT_CHECK_AFTER: none",
                )
                errors = "\n".join(self.validate(kind, invalid))
                self.assertIn("NO_REPORT_CHECK_AFTER must be current_turn_once", errors)

    def test_write_and_review_reject_ambiguous_or_continuous_controller_wait(self) -> None:
        for kind, packet in (("write", VALID_WRITE), ("review", VALID_REVIEW)):
            with self.subTest(kind=kind):
                invalid = packet.replace(
                    "CONTROLLER_AFTER_DISPATCH: event_driven_yield",
                    "CONTROLLER_AFTER_DISPATCH: keep_waiting",
                ).replace(
                    "NO_REPORT_CHECK_AFTER: current_turn_once",
                    "NO_REPORT_CHECK_AFTER: current_turn",
                )
                errors = "\n".join(self.validate(kind, invalid))
                self.assertIn(
                    "CONTROLLER_AFTER_DISPATCH must be event_driven_yield", errors
                )
                self.assertIn("current_turn is ambiguous and forbidden", errors)

    def test_update_requires_direct_task_message_delivery(self) -> None:
        invalid = VALID_FINAL.replace(
            "REPORT_DELIVERY: task_message:controller-thread-1",
            "REPORT_DELIVERY: local_final_only",
        )
        errors = "\n".join(self.validate("update", invalid))
        self.assertIn("REPORT_DELIVERY must be task_message", errors)

    def test_report_delivery_failure_is_valid_only_as_a_blocked_ending_turn(self) -> None:
        blocked = """
TASK_ID: write-1
MILESTONE: blocked
SUMMARY: controller task-message capability unavailable
EVIDENCE: send_message_to_thread returned unavailable
REPORT_DELIVERY: blocked:task_message_unavailable
TURN_STATE: ending
BLOCKER_OR_NEXT: owner=controller; action=recover_at_due_checkpoint; check_after=none
"""
        self.assertEqual(self.validate("update", blocked), [])
        invalid = blocked.replace("MILESTONE: blocked", "MILESTONE: tests_complete")
        errors = "\n".join(self.validate("update", invalid))
        self.assertIn("blocked REPORT_DELIVERY requires MILESTONE=blocked", errors)
        self.assertIn("non-blocked milestone REPORT_DELIVERY", errors)

    def test_update_rejects_invented_ready_milestone(self) -> None:
        invalid = VALID_FINAL.replace(
            "MILESTONE: final",
            "MILESTONE: READY_FOR_INDEPENDENT_READ_ONLY_REVIEW",
        )
        errors = "\n".join(self.validate("update", invalid))
        self.assertIn("MILESTONE must be one of the declared milestone values", errors)

    def test_ending_turn_cannot_leave_owner_with_task(self) -> None:
        invalid = VALID_FINAL.replace(
            "BLOCKER_OR_NEXT: owner=controller;",
            "BLOCKER_OR_NEXT: owner=task;",
        )
        errors = "\n".join(self.validate("update", invalid))
        self.assertIn("final milestone must hand ownership to controller", errors)
        self.assertIn("TURN_STATE=ending requires owner=controller", errors)

    def test_continuing_task_requires_task_owner_and_checkpoint(self) -> None:
        continuing = """
TASK_ID: write-1
MILESTONE: tests_complete
SUMMARY: focused tests passed and full validation continues
EVIDENCE: python -m unittest=PASS
REPORT_DELIVERY: task_message:controller-thread-1
TURN_STATE: continuing
BLOCKER_OR_NEXT: owner=task; action=run_full_validation; check_after=current_turn_once
"""
        self.assertEqual(self.validate("update", continuing), [])
        invalid = continuing.replace("check_after=current_turn_once", "check_after=none")
        errors = "\n".join(self.validate("update", invalid))
        self.assertIn("owner=task requires a non-none check_after", errors)

    def test_final_requires_evidence_risks_pending_and_controller_owner(self) -> None:
        invalid = """
TASK_ID: write-1
MILESTONE: final
SUMMARY: done
EVIDENCE: none
REPORT_DELIVERY: local_final_only
TURN_STATE: ending
BLOCKER_OR_NEXT: owner=task; action=none; check_after=daily
"""
        errors = "\n".join(self.validate("update", invalid))
        self.assertIn("final EVIDENCE must include", errors)
        self.assertIn("final milestone missing field: RISKS_OR_LIMITS", errors)
        self.assertIn("final milestone missing field: PENDING_ITEMS", errors)
        self.assertIn("check_after must be", errors)
        self.assertIn("must hand ownership to controller", errors)
        self.assertIn("REPORT_DELIVERY must be task_message", errors)


if __name__ == "__main__":
    unittest.main()
