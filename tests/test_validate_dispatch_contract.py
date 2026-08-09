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

FULL_SHA = "0123456789abcdef0123456789abcdef01234567"

VALID_BINDING = r"""
TASK_ID: write-1
TASK_MODE: write
TASK_ENVIRONMENT: local
REPOSITORY_ROOT: C:\repo
WORKTREE_ROOT: C:\repo\.worktrees
EXECUTION_PATH: C:\repo\.worktrees\write-1
TASK_PROJECT_ID: saved-project
ACTUAL_THREAD_CWD: C:\repo
ACTUAL_THREAD_PROJECT_ID: saved-project
"""

VALID_WRITE = rf"""
TASK_ID: write-1
TASK_ENVIRONMENT: local
TASK_ARCHIVE_POLICY: controller_after_acceptance
WORKTREE_ROOT: C:\repo\.worktrees
WORKTREE: C:\repo\.worktrees\write-1
BRANCH: codex/write-1
BASE_COMMIT: {FULL_SHA}
OBJECTIVE: implement one isolated change
OWNED_PATHS: src/**; tests/**
DO_NOT_TOUCH: production; deployment
ACCEPTANCE: focused tests pass
REQUIRED_TESTS: python -m unittest
MODEL_POLICY: repo_write_default:gpt-5.6-luna/max
"""

VALID_REVIEW = rf"""
REVIEW_TASK_ID: review-1
TASK_ENVIRONMENT: local
TASK_ARCHIVE_POLICY: controller_after_acceptance
TARGET_MODE: existing_worktree
TARGET_PATH: C:\repo\.worktrees\write-1
TARGET_COMMIT_OR_RANGE: {FULL_SHA}
READ_ONLY: true
ACCEPTANCE_BASELINE: A1 focused behavior; A2 required regression checks
THREAT_MODEL: repository inputs and failures named by A1-A2
NON_GOALS: unrelated hardening and new protocol design
REVIEW_SCOPE: inspect the frozen candidate
ACCEPTANCE: PASS when A1-A2 have no mapped blocker
MODEL_POLICY: app_default
"""

VALID_FINAL = """
TASK_ID: write-1
STATUS: final
SUMMARY: implementation complete
EVIDENCE: tests=PASS; commit=abc
RISKS_OR_LIMITS: local evidence only
PENDING_ITEMS: controller verification
DELIVERY: task_message:controller-1
TARGET_SETTINGS: preserve
NEXT: controller verifies the candidate
"""


class ContractValidationTests(unittest.TestCase):
    def validate(self, kind: str, text: str) -> list[str]:
        return VALIDATOR.validate(kind, VALIDATOR.parse_fields(text))

    def test_valid_packets(self) -> None:
        for kind, packet in (
            ("binding", VALID_BINDING),
            ("write", VALID_WRITE),
            ("review", VALID_REVIEW),
            ("update", VALID_FINAL),
        ):
            with self.subTest(kind=kind):
                self.assertEqual(self.validate(kind, packet), [])

    def test_binding_accepts_windows_extended_root_equivalence(self) -> None:
        packet = VALID_BINDING.replace(
            "ACTUAL_THREAD_CWD: C:\\repo", "ACTUAL_THREAD_CWD: \\\\?\\C:\\repo"
        )
        self.assertEqual(self.validate("binding", packet), [])

    def test_binding_rejects_projectless_foreign_task(self) -> None:
        packet = (
            VALID_BINDING.replace("TASK_PROJECT_ID: saved-project", "TASK_PROJECT_ID: projectless")
            .replace("ACTUAL_THREAD_PROJECT_ID: saved-project", "ACTUAL_THREAD_PROJECT_ID: none")
            .replace("ACTUAL_THREAD_CWD: C:\\repo", "ACTUAL_THREAD_CWD: C:\\Users\\Example")
        )
        errors = "\n".join(self.validate("binding", packet))
        self.assertIn("ACTUAL_THREAD_CWD must equal REPOSITORY_ROOT", errors)
        self.assertIn("TASK_PROJECT_ID must identify", errors)

    def test_binding_rejects_worktree_escape(self) -> None:
        packet = VALID_BINDING.replace(
            "EXECUTION_PATH: C:\\repo\\.worktrees\\write-1",
            "EXECUTION_PATH: C:\\repo\\.worktrees\\child\\..\\..\\outside",
        )
        self.assertIn(
            "EXECUTION_PATH must be below WORKTREE_ROOT",
            self.validate("binding", packet),
        )

    def test_review_root_binding_uses_repository_root(self) -> None:
        packet = (
            VALID_BINDING.replace("TASK_MODE: write", "TASK_MODE: review_root")
            .replace(
                "EXECUTION_PATH: C:\\repo\\.worktrees\\write-1",
                "EXECUTION_PATH: C:\\repo",
            )
        )
        self.assertEqual(self.validate("binding", packet), [])
        invalid = packet.replace("EXECUTION_PATH: C:\\repo", "EXECUTION_PATH: C:\\other")
        self.assertIn(
            "review_root EXECUTION_PATH must equal REPOSITORY_ROOT",
            self.validate("binding", invalid),
        )

    def test_review_worktree_binding_requires_repository_local_tree(self) -> None:
        packet = VALID_BINDING.replace("TASK_MODE: write", "TASK_MODE: review_worktree")
        self.assertEqual(self.validate("binding", packet), [])

    def test_write_requires_explicit_model_and_full_sha(self) -> None:
        invalid = VALID_WRITE.replace(
            "MODEL_POLICY: repo_write_default:gpt-5.6-luna/max",
            "MODEL_POLICY: app_default",
        ).replace(FULL_SHA, "abc123")
        errors = "\n".join(self.validate("write", invalid))
        self.assertIn("must explicitly bind", errors)
        self.assertIn("BASE_COMMIT must be a full", errors)

    def test_write_rejects_external_worktree(self) -> None:
        invalid = VALID_WRITE.replace(
            "WORKTREE: C:\\repo\\.worktrees\\write-1", "WORKTREE: C:\\outside"
        )
        self.assertIn("WORKTREE must be below WORKTREE_ROOT", self.validate("write", invalid))

    def test_dispatch_rejects_app_managed_worktree_environment(self) -> None:
        for kind, packet in (
            ("binding", VALID_BINDING),
            ("write", VALID_WRITE),
            ("review", VALID_REVIEW),
        ):
            with self.subTest(kind=kind):
                invalid = packet.replace(
                    "TASK_ENVIRONMENT: local", "TASK_ENVIRONMENT: worktree"
                )
                self.assertIn(
                    "TASK_ENVIRONMENT must be local; App-managed worktree tasks are forbidden",
                    self.validate(kind, invalid),
                )

    def test_dispatch_requires_controller_owned_archival(self) -> None:
        for kind, packet in (("write", VALID_WRITE), ("review", VALID_REVIEW)):
            with self.subTest(kind=kind):
                invalid = packet.replace(
                    "TASK_ARCHIVE_POLICY: controller_after_acceptance",
                    "TASK_ARCHIVE_POLICY: child_on_final",
                )
                self.assertIn(
                    "TASK_ARCHIVE_POLICY must be controller_after_acceptance",
                    self.validate(kind, invalid),
                )

    def test_review_supports_all_three_target_modes(self) -> None:
        for mode in ("root_readonly", "existing_worktree", "detached_snapshot"):
            with self.subTest(mode=mode):
                packet = VALID_REVIEW.replace("TARGET_MODE: existing_worktree", f"TARGET_MODE: {mode}")
                self.assertEqual(self.validate("review", packet), [])

    def test_review_rejects_ambiguous_history_and_writable_fields(self) -> None:
        invalid = VALID_REVIEW.replace(
            f"TARGET_COMMIT_OR_RANGE: {FULL_SHA}",
            f"TARGET_COMMIT_OR_RANGE: full history through {FULL_SHA}",
        ) + "\nOWNED_PATHS: src/**\n"
        errors = "\n".join(self.validate("review", invalid))
        self.assertIn("must be a full SHA or full-SHA range", errors)
        self.assertIn("must not declare a writable boundary", errors)

    def test_review_requires_frozen_acceptance_boundary(self) -> None:
        for field in ("ACCEPTANCE_BASELINE", "THREAT_MODEL", "NON_GOALS"):
            with self.subTest(field=field):
                invalid = "\n".join(
                    line for line in VALID_REVIEW.splitlines() if not line.startswith(f"{field}:")
                )
                self.assertIn(f"missing field: {field}", self.validate("review", invalid))

    def test_review_boundary_rejects_placeholders(self) -> None:
        invalid = VALID_REVIEW.replace(
            "ACCEPTANCE_BASELINE: A1 focused behavior; A2 required regression checks",
            "ACCEPTANCE_BASELINE: <whatever the reviewer considers important>",
        )
        self.assertIn(
            "ACCEPTANCE_BASELINE must not contain placeholders",
            self.validate("review", invalid),
        )

    def test_final_requires_direct_delivery_and_evidence(self) -> None:
        invalid = VALID_FINAL.replace("DELIVERY: task_message:controller-1", "DELIVERY: local_final_only").replace(
            "EVIDENCE: tests=PASS; commit=abc", "EVIDENCE: none"
        )
        errors = "\n".join(self.validate("update", invalid))
        self.assertIn("DELIVERY must be task_message", errors)
        self.assertIn("final EVIDENCE must include", errors)

    def test_blocked_delivery_failure_is_valid(self) -> None:
        blocked = """
TASK_ID: write-1
STATUS: blocked
SUMMARY: task-message capability unavailable
EVIDENCE: delivery call failed
DELIVERY: blocked:task_message_unavailable
TARGET_SETTINGS: preserve
NEXT: recover on the next real controller wake
"""
        self.assertEqual(self.validate("update", blocked), [])

    def test_report_rejects_controller_model_override(self) -> None:
        invalid = VALID_FINAL.replace(
            "TARGET_SETTINGS: preserve",
            "TARGET_SETTINGS: override:gpt-5.6-luna/max",
        )
        self.assertIn(
            "TARGET_SETTINGS must be preserve; controller-bound reports must omit model and thinking overrides",
            self.validate("update", invalid),
        )

    def test_obsolete_ceremony_fields_are_rejected(self) -> None:
        write = VALID_WRITE + "\nCONTROLLER_AFTER_DISPATCH: event_driven_yield\nNO_REPORT_CHECK_AFTER: current_turn_once\n"
        report = VALID_FINAL + "\nTURN_STATE: ending\nBLOCKER_OR_NEXT: owner=controller\n"
        self.assertTrue(any("obsolete protocol fields" in error for error in self.validate("write", write)))
        self.assertTrue(any("obsolete protocol fields" in error for error in self.validate("update", report)))


if __name__ == "__main__":
    unittest.main()
