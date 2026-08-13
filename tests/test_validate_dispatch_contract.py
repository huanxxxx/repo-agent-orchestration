from __future__ import annotations

import importlib.util
import re
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
ORCHESTRATION_MODE: delivery
SOURCE_ROLE: delivery_controller
TARGET_ROLE: peer_writer
REPORT_TO_TASK_ID: controller-1
AUTHORITY_BASELINE: user-approved outcome A1-A2
TASK_ENVIRONMENT: local
TASK_ARCHIVE_POLICY: dispatching_authority_after_acceptance
WORKTREE_ROOT: C:\repo\.worktrees
WORKTREE: C:\repo\.worktrees\write-1
BRANCH: codex/write-1
BASE_COMMIT: {FULL_SHA}
OBJECTIVE: implement one isolated change
OWNED_PATHS: src/**; tests/**
DO_NOT_TOUCH: production; deployment
ACCEPTANCE: focused tests pass
REQUIRED_TESTS: python -m unittest
MODEL_POLICY: app_default
"""

VALID_REVIEW = rf"""
REVIEW_TASK_ID: review-1
ORCHESTRATION_MODE: delivery
REVIEW_CLASS: implementation
SOURCE_ROLE: delivery_controller
TARGET_ROLE: peer_reviewer
REPORT_TO_TASK_ID: controller-1
TASK_ENVIRONMENT: local
TASK_ARCHIVE_POLICY: dispatching_authority_after_acceptance
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
ORCHESTRATION_MODE: delivery
UPDATE_CLASS: implementation
SOURCE_ROLE: peer_writer
TARGET_ROLE: delivery_controller
TARGET_TASK_ID: controller-1
STATUS: final
SUMMARY: implementation complete
EVIDENCE: tests=PASS; commit=abc
RISKS_OR_LIMITS: local evidence only
PENDING_ITEMS: controller verification
DELIVERY: task_message:controller-1
TARGET_SETTINGS: preserve
NEXT: controller verifies the candidate
"""

VALID_DESIGN_HANDOFF = rf"""
DESIGN_TASK_ID: design-1
DELIVERY_TASK_ID: delivery-1
ORCHESTRATION_MODE: architected
SOURCE_ROLE: design_authority
TARGET_ROLE: delivery_controller
REPORT_TO_TASK_ID: design-1
TASK_ENVIRONMENT: local
TASK_ARCHIVE_POLICY: dispatching_authority_after_acceptance
REPOSITORY_ROOT: C:\repo
DESIGN_CHECKPOINT: {FULL_SHA}
DESIGN_REVIEW_STATUS: PASS
DESIGN_REVIEW_EVIDENCE: review-1 PASS against D1-D2
OBJECTIVE: implement the frozen repository architecture
AUTHORITATIVE_INPUTS: repository facts and informed user choices
FROZEN_DECISIONS: D1 identity; D2 balanced entries
NON_GOALS: deployment and production data
ACCEPTANCE_BASELINE: D1-D2
IMPLEMENTATION_BOUNDARY: implement without redesign
EXTERNAL_GATES: merge main; push; deploy
DESIGN_REOPEN_RULE: false assumption or boundary change returns to design-1
MODEL_POLICY: app_default
"""

VALID_DELIVERY_PLAN = rf"""
DELIVERY_TASK_ID: delivery-1
DESIGN_TASK_ID: design-1
ORCHESTRATION_MODE: architected
SOURCE_ROLE: delivery_controller
TARGET_ROLE: design_authority
TARGET_TASK_ID: design-1
UPDATE_TYPE: plan
DESIGN_CHECKPOINT: {FULL_SHA}
SUMMARY: implementation graph and first ready set frozen
DESIGN_ALIGNMENT: all milestones map to D1-D2
EVIDENCE: dependency and ownership checks passed
RISKS_OR_LIMITS: external gates closed
PENDING_ITEMS: implementation and review
READY_SET: ledger; identity
PARALLEL_DISPATCH: writer-ledger; writer-identity
DECISION_REQUIRED: no
DEPENDENCY_GRAPH: ledger and identity precede integration
SHARED_PATH_OWNER: delivery-1
DELIVERY: task_message:design-1
TARGET_SETTINGS: preserve
NEXT: continue authorized delivery
"""

VALID_DELIVERY_MILESTONE = rf"""
DELIVERY_TASK_ID: delivery-1
DESIGN_TASK_ID: design-1
ORCHESTRATION_MODE: architected
SOURCE_ROLE: delivery_controller
TARGET_ROLE: design_authority
TARGET_TASK_ID: design-1
UPDATE_TYPE: milestone
DESIGN_CHECKPOINT: {FULL_SHA}
SUMMARY: S2B-0 reached its frozen checkpoint
DESIGN_ALIGNMENT: the candidate preserves D1-D2
EVIDENCE: checkpoint and focused tests recorded
RISKS_OR_LIMITS: independent review pending
PENDING_ITEMS: independent review
DECISION_REQUIRED: no
MILESTONE: S2B-0 candidate frozen; independent review pending
DELIVERY: task_message:design-1
TARGET_SETTINGS: preserve
NEXT: delivery continues without design action
"""

VALID_DESIGN_REOPEN = rf"""
DELIVERY_TASK_ID: delivery-1
DESIGN_TASK_ID: design-1
ORCHESTRATION_MODE: architected
SOURCE_ROLE: delivery_controller
TARGET_ROLE: design_authority
TARGET_TASK_ID: design-1
DESIGN_CHECKPOINT: {FULL_SHA}
AFFECTED_SCOPE: identity and dependent integration
CONFLICT: verified platform fact contradicts D1
EVIDENCE: stable identity field is unavailable
OPTIONS: revise D1; defer identity
RECOMMENDATION: revise D1 without weakening privacy
PAUSED_SCOPE: identity and dependent integration
UNAFFECTED_WORK: ledger may continue
DELIVERY: task_message:design-1
TARGET_SETTINGS: preserve
NEXT: await design decision for affected scope
"""

VALID_DESIGN_DECISION = rf"""
DESIGN_TASK_ID: design-1
DELIVERY_TASK_ID: delivery-1
ORCHESTRATION_MODE: architected
SOURCE_ROLE: design_authority
TARGET_ROLE: delivery_controller
TARGET_TASK_ID: delivery-1
PRIOR_DESIGN_CHECKPOINT: {FULL_SHA}
DECISION: reopen_rejected
RATIONALE: evidence does not invalidate D1
UPDATED_DESIGN_CHECKPOINT: unchanged
AFFECTED_SCOPE: identity
AUTHORITY_BOUNDARY: gather evidence; no alternate identity path authorized
DELIVERY: task_message:delivery-1
TARGET_SETTINGS: preserve
NEXT: keep affected scope on hold
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
            ("design_handoff", VALID_DESIGN_HANDOFF),
            ("delivery_update", VALID_DELIVERY_PLAN),
            ("design_reopen", VALID_DESIGN_REOPEN),
            ("design_decision", VALID_DESIGN_DECISION),
        ):
            with self.subTest(kind=kind):
                self.assertEqual(self.validate(kind, packet), [])

    def test_delivery_milestone_packet_is_valid(self) -> None:
        self.assertEqual(
            self.validate("delivery_update", VALID_DELIVERY_MILESTONE), []
        )

    def test_delivery_update_variants_reject_cross_type_fields(self) -> None:
        missing_milestone = "\n".join(
            line
            for line in VALID_DELIVERY_MILESTONE.splitlines()
            if not line.startswith("MILESTONE:")
        )
        self.assertIn(
            "delivery milestone missing field: MILESTONE",
            self.validate("delivery_update", missing_milestone),
        )

        plan_with_milestone = (
            VALID_DELIVERY_PLAN
            + "\nMILESTONE: relabelled milestone content\n"
        )
        self.assertIn(
            "delivery plan must not declare MILESTONE",
            self.validate("delivery_update", plan_with_milestone),
        )

        milestone_with_plan_fields = VALID_DELIVERY_MILESTONE.replace(
            "MILESTONE: S2B-0 candidate frozen; independent review pending",
            "MILESTONE: S2B-0 candidate frozen; independent review pending\n"
            "READY_SET: S2B-R",
        )
        self.assertIn(
            "delivery milestone must not declare plan-only fields: READY_SET",
            self.validate("delivery_update", milestone_with_plan_fields),
        )

    def test_schema_fields_do_not_conflict_with_obsolete_fields(self) -> None:
        self.assertEqual(VALIDATOR.schema_integrity_errors(), [])

    def test_binding_accepts_windows_extended_root_equivalence(self) -> None:
        packet = VALID_BINDING.replace(
            "ACTUAL_THREAD_CWD: C:\\repo", "ACTUAL_THREAD_CWD: \\\\?\\C:\\repo"
        )
        self.assertEqual(self.validate("binding", packet), [])

    def test_posix_absolute_paths_are_classified_and_compared_correctly(self) -> None:
        self.assertEqual(VALIDATOR.canonical_path("/tmp/repo")[0], "posix")
        self.assertTrue(
            VALIDATOR.is_descendant_path(
                "/tmp/repo/.worktrees/write-1", "/tmp/repo/.worktrees"
            )
        )
        self.assertFalse(
            VALIDATOR.is_descendant_path(
                "/tmp/repo/.worktrees", "/tmp/repo/.worktrees"
            )
        )
        self.assertEqual(VALIDATOR.normalized_path("/tmp/repo"), "/tmp/repo")

    def test_windows_absolute_paths_are_classified_separately_from_posix(self) -> None:
        self.assertEqual(VALIDATOR.canonical_path("C:\\repo")[0], "windows")
        self.assertEqual(VALIDATOR.canonical_path("/tmp/repo")[0], "posix")
        self.assertNotEqual(
            VALIDATOR.canonical_path("C:\\repo")[0],
            VALIDATOR.canonical_path("/tmp/repo")[0],
        )

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

    def test_write_accepts_explicit_model_and_requires_full_sha(self) -> None:
        explicit = VALID_WRITE.replace(
            "MODEL_POLICY: app_default",
            "MODEL_POLICY: repo_write_default:gpt-5.6-luna/max",
        )
        self.assertEqual(self.validate("write", explicit), [])
        invalid = VALID_WRITE.replace(
            "MODEL_POLICY: app_default",
            "MODEL_POLICY: controller_family_auto",
        ).replace(FULL_SHA, "abc123")
        errors = "\n".join(self.validate("write", invalid))
        self.assertIn("must be app_default", errors)
        self.assertIn("BASE_COMMIT must be a full", errors)

    def test_repository_model_policy_maps_profile_values_to_packets(self) -> None:
        self.assertEqual(
            VALIDATOR.repository_model_policy("write", "app_default"),
            "app_default",
        )
        self.assertEqual(
            VALIDATOR.repository_model_policy("write", "gpt-5.6-luna/max"),
            "repo_write_default:gpt-5.6-luna/max",
        )
        self.assertEqual(
            VALIDATOR.repository_model_policy("review", "gpt-5.6-luna/max"),
            "repo_review_default:gpt-5.6-luna/max",
        )
        self.assertEqual(
            VALIDATOR.repository_model_policy("delivery", "gpt-5.6-sol/high"),
            "repo_delivery_default:gpt-5.6-sol/high",
        )

    def test_repository_model_policy_output_passes_packet_validation(self) -> None:
        write_policy = VALIDATOR.repository_model_policy("write", "gpt-5.6-luna/max")
        review_policy = VALIDATOR.repository_model_policy("review", "gpt-5.6-luna/max")
        self.assertEqual(
            self.validate(
                "write",
                VALID_WRITE.replace("MODEL_POLICY: app_default", f"MODEL_POLICY: {write_policy}"),
            ),
            [],
        )
        self.assertEqual(
            self.validate(
                "review",
                VALID_REVIEW.replace("MODEL_POLICY: app_default", f"MODEL_POLICY: {review_policy}"),
            ),
            [],
        )

    def test_repository_model_policy_rejects_invalid_profile_values(self) -> None:
        for kind in ("write", "review", "delivery"):
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(ValueError, "app_default or <model>/<reasoning>"):
                    VALIDATOR.repository_model_policy(kind, "bad value")

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

    def test_dispatch_requires_dispatching_authority_archival(self) -> None:
        for kind, packet in (("write", VALID_WRITE), ("review", VALID_REVIEW)):
            with self.subTest(kind=kind):
                invalid = packet.replace(
                    "TASK_ARCHIVE_POLICY: dispatching_authority_after_acceptance",
                    "TASK_ARCHIVE_POLICY: peer_self_on_final",
                )
                self.assertIn(
                    "TASK_ARCHIVE_POLICY must be dispatching_authority_after_acceptance",
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
ORCHESTRATION_MODE: delivery
UPDATE_CLASS: implementation
SOURCE_ROLE: peer_writer
TARGET_ROLE: delivery_controller
TARGET_TASK_ID: controller-1
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
            "TARGET_SETTINGS must be preserve; task-message reports must omit model and thinking overrides",
            self.validate("update", invalid),
        )

    def test_architected_packets_enforce_authority_direction(self) -> None:
        invalid_handoff = VALID_DESIGN_HANDOFF.replace(
            "SOURCE_ROLE: design_authority", "SOURCE_ROLE: delivery_controller"
        )
        self.assertIn(
            "design handoff SOURCE_ROLE must be design_authority",
            self.validate("design_handoff", invalid_handoff),
        )
        invalid_update = VALID_DELIVERY_PLAN.replace(
            "TARGET_TASK_ID: design-1", "TARGET_TASK_ID: another-design"
        )
        errors = self.validate("delivery_update", invalid_update)
        self.assertIn("TARGET_TASK_ID must equal DESIGN_TASK_ID", errors)
        self.assertIn("DELIVERY task id must equal TARGET_TASK_ID", errors)

    def test_validator_rejects_unknown_fields_outside_shared_schema(self) -> None:
        errors = self.validate("delivery_update", VALID_DELIVERY_PLAN + "\nOWNER: design-1\n")
        self.assertIn("unknown packet fields: OWNER", errors)

    def test_architected_write_and_review_require_design_checkpoint(self) -> None:
        write = VALID_WRITE.replace(
            "ORCHESTRATION_MODE: delivery", "ORCHESTRATION_MODE: architected"
        )
        review = VALID_REVIEW.replace(
            "ORCHESTRATION_MODE: delivery", "ORCHESTRATION_MODE: architected"
        )
        self.assertIn(
            "architected write requires DESIGN_CHECKPOINT",
            self.validate("write", write),
        )
        self.assertIn(
            "architected review requires DESIGN_CHECKPOINT",
            self.validate("review", review),
        )

        delivery_write = VALID_WRITE + f"\nDESIGN_CHECKPOINT: {FULL_SHA}\n"
        delivery_review = VALID_REVIEW + f"\nDESIGN_CHECKPOINT: {FULL_SHA}\n"
        self.assertIn(
            "delivery write must not declare DESIGN_CHECKPOINT",
            self.validate("write", delivery_write),
        )
        self.assertIn(
            "delivery review must not declare DESIGN_CHECKPOINT",
            self.validate("review", delivery_review),
        )

    def test_design_review_reports_to_design_authority(self) -> None:
        review = (
            VALID_REVIEW.replace(
                "ORCHESTRATION_MODE: delivery", "ORCHESTRATION_MODE: architected"
            )
            .replace("REVIEW_CLASS: implementation", "REVIEW_CLASS: design")
            .replace(
                "SOURCE_ROLE: delivery_controller", "SOURCE_ROLE: design_authority"
            )
            + f"\nDESIGN_CHECKPOINT: {FULL_SHA}\n"
        )
        self.assertEqual(self.validate("review", review), [])

        mismatched = review.replace(
            f"TARGET_COMMIT_OR_RANGE: {FULL_SHA}",
            "TARGET_COMMIT_OR_RANGE: " + ("2" * 40),
        )
        self.assertIn(
            "design review TARGET_COMMIT_OR_RANGE must end at DESIGN_CHECKPOINT",
            self.validate("review", mismatched),
        )

    def test_architected_reports_require_actual_source_task_ids(self) -> None:
        for kind, packet, field in (
            ("delivery_update", VALID_DELIVERY_PLAN, "DELIVERY_TASK_ID"),
            ("design_reopen", VALID_DESIGN_REOPEN, "DELIVERY_TASK_ID"),
            ("design_decision", VALID_DESIGN_DECISION, "DESIGN_TASK_ID"),
            ("update", VALID_FINAL, "TASK_ID"),
        ):
            with self.subTest(kind=kind, field=field):
                invalid = re.sub(rf"(?m)^{field}: .+$", f"{field}: pending", packet)
                self.assertIn(
                    f"{field} must identify an actual task",
                    self.validate(kind, invalid),
                )

    def test_design_reopen_requires_recommendation_and_paused_scope(self) -> None:
        for field in ("RECOMMENDATION", "PAUSED_SCOPE"):
            with self.subTest(field=field):
                invalid = "\n".join(
                    line
                    for line in VALID_DESIGN_REOPEN.splitlines()
                    if not line.startswith(f"{field}:")
                )
                self.assertIn(
                    f"missing field: {field}",
                    self.validate("design_reopen", invalid),
                )

    def test_design_decision_cannot_silently_change_checkpoint(self) -> None:
        changed_without_reopen = VALID_DESIGN_DECISION.replace(
            "UPDATED_DESIGN_CHECKPOINT: unchanged",
            "UPDATED_DESIGN_CHECKPOINT: " + ("2" * 40),
        )
        self.assertIn(
            "only reopen_approved may change UPDATED_DESIGN_CHECKPOINT",
            self.validate("design_decision", changed_without_reopen),
        )

        same_checkpoint_reopen = (
            VALID_DESIGN_DECISION.replace(
                "DECISION: reopen_rejected", "DECISION: reopen_approved"
            ).replace(
                "UPDATED_DESIGN_CHECKPOINT: unchanged",
                f"UPDATED_DESIGN_CHECKPOINT: {FULL_SHA}",
            )
        )
        self.assertIn(
            "reopen_approved requires a new UPDATED_DESIGN_CHECKPOINT",
            self.validate("design_decision", same_checkpoint_reopen),
        )

    def test_obsolete_ceremony_fields_are_rejected(self) -> None:
        write = VALID_WRITE + "\nCONTROLLER_AFTER_DISPATCH: event_driven_yield\nNO_REPORT_CHECK_AFTER: current_turn_once\n"
        report = VALID_FINAL + "\nTURN_STATE: ending\nBLOCKER_OR_NEXT: owner=controller\n"
        self.assertTrue(any("obsolete protocol fields" in error for error in self.validate("write", write)))
        self.assertTrue(any("obsolete protocol fields" in error for error in self.validate("update", report)))


if __name__ == "__main__":
    unittest.main()
