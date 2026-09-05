from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "repo-agent-orchestration" / "scripts"
CONSTRUCTOR_PATH = SCRIPTS / "construct_packet.py"
SPEC = importlib.util.spec_from_file_location("packet_constructor", CONSTRUCTOR_PATH)
assert SPEC and SPEC.loader
CONSTRUCTOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CONSTRUCTOR
SPEC.loader.exec_module(CONSTRUCTOR)

FULL_SHA = "0123456789abcdef0123456789abcdef01234567"


def delivery_plan_fields() -> dict[str, str]:
    return {
        "DELIVERY_TASK_ID": "delivery-1",
        "DESIGN_TASK_ID": "design-1",
        "ORCHESTRATION_MODE": "architected",
        "SOURCE_ROLE": "delivery_controller",
        "TARGET_ROLE": "design_authority",
        "TARGET_TASK_ID": "design-1",
        "DESIGN_CHECKPOINT": FULL_SHA,
        "SUMMARY": "plan frozen",
        "DESIGN_ALIGNMENT": "milestones map to D1-D2",
        "EVIDENCE": "dependency graph checked",
        "RISKS_OR_LIMITS": "external gates closed",
        "PENDING_ITEMS": "implementation",
        "READY_SET": "ledger; identity",
        "PARALLEL_DISPATCH": "writer-ledger; writer-identity",
        "DECISION_REQUIRED": "no",
        "DELIVERY": "task_message:design-1",
        "TARGET_SETTINGS": "preserve",
        "NEXT": "continue delivery",
        "DEPENDENCY_GRAPH": "ledger and identity precede integration",
        "SHARED_PATH_OWNER": "delivery-1",
    }


def delivery_milestone_fields() -> dict[str, str]:
    fields = delivery_plan_fields()
    for name in (
        "READY_SET",
        "PARALLEL_DISPATCH",
        "DEPENDENCY_GRAPH",
        "SHARED_PATH_OWNER",
    ):
        fields.pop(name)
    fields["SUMMARY"] = "S2B-0 reached its frozen checkpoint"
    fields["MILESTONE"] = "S2B-0 candidate frozen; independent review pending"
    return fields


def write_launch_fields() -> dict[str, str]:
    return {
        "REPORT_TO": "controller-1",
        "AUTHORITY_BASELINE": "A1-A2",
        "WORKTREE_ROOT": r"C:\repo\.worktrees",
        "WORKTREE": r"C:\repo\.worktrees\writer-1",
        "BRANCH": "codex/writer-1",
        "BASE_COMMIT": FULL_SHA,
        "OBJECTIVE": "implement one bounded change",
        "OWNED_PATHS": "src/**; tests/**",
        "DO_NOT_TOUCH": "deployment; production",
        "ACCEPTANCE": "A1-A2 pass",
        "REQUIRED_TESTS": "python -m unittest",
    }


class PacketConstructorTests(unittest.TestCase):
    def test_design_review_choice_is_explicit_and_round_trips_without_model_override(self) -> None:
        fields = {
            "DESIGN_TASK_ID": "design-1",
            "DELIVERY_TASK_ID": "delivery-1",
            "PRIOR_DESIGN_CHECKPOINT": FULL_SHA,
            "DECISION": "reopen_approved",
            "RATIONALE": "bounded reversible contract adjustment",
            "UPDATED_DESIGN_CHECKPOINT": "2" * 40,
            "AFFECTED_SCOPE": "two design clauses",
            "AUTHORITY_BOUNDARY": "design-owner decision only; no release",
            "NEXT": "continue authorized delivery",
            "DESIGN_REVIEW_STATUS": "not_required",
            "DESIGN_REVIEW_EVIDENCE": "no mandated independent review; owner checked unchanged interfaces",
        }
        arguments = CONSTRUCTOR.task_message_args(
            "design_decision", target_task_id="delivery-1", **fields
        )
        self.assertEqual(set(arguments), {"threadId", "prompt"})
        from validate_dispatch_contract import parse_fields, validate

        packet = parse_fields(arguments["prompt"])
        self.assertEqual(validate("design_decision", packet), [])
        self.assertEqual(packet["DESIGN_REVIEW_STATUS"], "not_required")
        self.assertEqual(packet["TARGET_SETTINGS"], "preserve")
        self.assertEqual(packet["DESIGN_REVIEW_EVIDENCE"], fields["DESIGN_REVIEW_EVIDENCE"])

        fields.pop("DESIGN_REVIEW_STATUS")
        with self.assertRaisesRegex(ValueError, "must record PASS"):
            CONSTRUCTOR.task_message_args("design_decision", target_task_id="delivery-1", **fields)

    def test_launch_prompt_is_complete_before_task_creation(self) -> None:
        prompt = CONSTRUCTOR.launch_prompt("write", **write_launch_fields())

        self.assertTrue(prompt.startswith("PEER_WRITE_DISPATCH\n"))
        self.assertNotRegex(prompt, r"(?m)^TASK_ID:")
        self.assertIn("ORCHESTRATION_MODE: delivery", prompt)
        self.assertIn("SOURCE_ROLE: delivery_controller", prompt)
        self.assertIn("TARGET_ROLE: peer_writer", prompt)
        self.assertIn("TASK_ENVIRONMENT: local", prompt)
        self.assertIn("REPORT_TO_TASK_ID: controller-1", prompt)
        self.assertNotIn("AWAIT_FORMAL_DISPATCH", prompt)

    def test_launch_rejects_a_preassigned_runtime_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "assigned by create_thread"):
            CONSTRUCTOR.launch_prompt(
                "write", TASK_ID="guessed-writer-id", **write_launch_fields()
            )

    def test_minimal_design_review_report_derives_mechanics_and_aliases(self) -> None:
        arguments = CONSTRUCTOR.task_message_args(
            "update",
            target_task_id="design-1",
            UPDATE_CLASS="design_review",
            STATUS="final",
            VERDICT="HOLD",
            FINDINGS="D1 conflicts with the verified runtime boundary",
            DESIGN_CHECKPOINT=FULL_SHA,
        )

        self.assertEqual(arguments["threadId"], "design-1")
        prompt = arguments["prompt"]
        self.assertNotRegex(prompt, r"(?m)^TASK_ID:")
        self.assertIn("ORCHESTRATION_MODE: architected", prompt)
        self.assertIn("SOURCE_ROLE: peer_reviewer", prompt)
        self.assertIn("TARGET_ROLE: design_authority", prompt)
        self.assertIn("SUMMARY: HOLD", prompt)
        self.assertIn("EVIDENCE: D1 conflicts", prompt)
        self.assertIn("DELIVERY: task_message:design-1", prompt)
        self.assertIn("TARGET_SETTINGS: preserve", prompt)
        self.assertIn("NEXT: authority_acceptance", prompt)
        self.assertNotIn("RISKS_OR_LIMITS", prompt)
        self.assertNotIn("PENDING_ITEMS", prompt)

    def test_delivery_plan_injects_type_and_uses_schema_order(self) -> None:
        packet = CONSTRUCTOR.delivery_plan_packet(**delivery_plan_fields())
        self.assertEqual(packet["UPDATE_TYPE"], "plan")
        self.assertEqual(list(packet)[0], "DELIVERY_TASK_ID")
        self.assertLess(
            list(packet).index("READY_SET"), list(packet).index("DEPENDENCY_GRAPH")
        )

    def test_serialization_has_header_and_round_trips_validator(self) -> None:
        fields = delivery_plan_fields()
        fields["UPDATE_TYPE"] = "plan"
        text = CONSTRUCTOR.serialize_packet("delivery_update", fields)
        self.assertTrue(text.startswith("DELIVERY_UPDATE\n"))
        parsed = CONSTRUCTOR.build_packet("delivery_update", **fields)
        self.assertEqual(parsed["TARGET_TASK_ID"], "design-1")

    def test_delivery_milestone_is_constructible_and_valid(self) -> None:
        packet = CONSTRUCTOR.delivery_milestone_packet(
            **delivery_milestone_fields()
        )

        self.assertEqual(packet["UPDATE_TYPE"], "milestone")
        self.assertEqual(
            packet["MILESTONE"],
            "S2B-0 candidate frozen; independent review pending",
        )
        self.assertNotIn("READY_SET", packet)

    def test_delivery_final_omits_plan_only_fields(self) -> None:
        fields = delivery_plan_fields()
        for name in (
            "READY_SET",
            "PARALLEL_DISPATCH",
            "DEPENDENCY_GRAPH",
            "SHARED_PATH_OWNER",
        ):
            fields.pop(name)
        fields["DECISION_REQUIRED"] = "yes"

        packet = CONSTRUCTOR.delivery_final_packet(**fields)

        self.assertEqual(packet["UPDATE_TYPE"], "final")
        self.assertNotIn("READY_SET", packet)
        self.assertNotIn("DEPENDENCY_GRAPH", packet)

    def test_constructor_rejects_missing_and_unknown_fields(self) -> None:
        missing = delivery_plan_fields()
        missing.pop("DESIGN_CHECKPOINT")
        with self.assertRaisesRegex(ValueError, "missing packet fields"):
            CONSTRUCTOR.delivery_plan_packet(**missing)
        unknown = delivery_plan_fields()
        unknown["CREATE_TASK"] = "yes"
        with self.assertRaisesRegex(ValueError, "unknown packet fields"):
            CONSTRUCTOR.delivery_plan_packet(**unknown)

    def test_constructor_enforces_authority_routing(self) -> None:
        invalid = delivery_plan_fields()
        invalid["TARGET_ROLE"] = "peer_writer"
        with self.assertRaisesRegex(ValueError, "TARGET_ROLE must be design_authority"):
            CONSTRUCTOR.delivery_plan_packet(**invalid)

    def test_task_message_args_use_raw_packet_and_exact_target(self) -> None:
        fields = delivery_plan_fields()
        fields["UPDATE_TYPE"] = "plan"

        arguments = CONSTRUCTOR.task_message_args("delivery_update", **fields)

        self.assertEqual(set(arguments), {"threadId", "prompt"})
        self.assertEqual(arguments["threadId"], "design-1")
        self.assertTrue(arguments["prompt"].startswith("DELIVERY_UPDATE\n"))
        self.assertNotIn("codex_delegation", arguments["prompt"])
        self.assertNotIn("source_thread_id", arguments["prompt"])

    def test_task_message_target_map_covers_only_outgoing_packet_kinds(self) -> None:
        self.assertEqual(
            CONSTRUCTOR.TASK_MESSAGE_TARGET_FIELDS,
            {
                "write": "TASK_ID",
                "review": "REVIEW_TASK_ID",
                "update": "TARGET_TASK_ID",
                "design_handoff": "DELIVERY_TASK_ID",
                "delivery_update": "TARGET_TASK_ID",
                "design_reopen": "TARGET_TASK_ID",
                "design_decision": "TARGET_TASK_ID",
            },
        )
        with self.assertRaisesRegex(ValueError, "not sent through task-message"):
            CONSTRUCTOR.task_message_args("binding")

    def test_task_message_args_reject_delegation_framing_in_fields(self) -> None:
        fields = delivery_plan_fields()
        fields["UPDATE_TYPE"] = "plan"
        fields["SUMMARY"] = "<codex_delegation>wrapped</codex_delegation>"

        with self.assertRaisesRegex(ValueError, "App-managed delegation framing"):
            CONSTRUCTOR.task_message_args("delivery_update", **fields)

    def test_module_has_no_workflow_side_effect_api(self) -> None:
        forbidden = {
            "create_task",
            "send_message",
            "git_commit",
            "wait_task",
            "archive_task",
        }
        self.assertTrue(forbidden.isdisjoint(vars(CONSTRUCTOR)))

    def test_cli_streams_json_through_static_and_live_validation(self) -> None:
        fields = delivery_plan_fields()
        fields["UPDATE_TYPE"] = "plan"
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(CONSTRUCTOR_PATH),
                "--kind",
                "delivery_update",
                "--live",
                "-",
            ],
            input=json.dumps(fields),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("DELIVERY_UPDATE\n"))
        self.assertIn("UPDATE_TYPE: plan", result.stdout)

    def test_cli_emits_exact_task_message_arguments(self) -> None:
        fields = delivery_plan_fields()
        fields["UPDATE_TYPE"] = "plan"
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(CONSTRUCTOR_PATH),
                "--kind",
                "delivery_update",
                "--live",
                "--task-message",
                "-",
            ],
            input=json.dumps(fields),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        arguments = json.loads(result.stdout)
        self.assertEqual(arguments["threadId"], "design-1")
        self.assertTrue(arguments["prompt"].startswith("DELIVERY_UPDATE\n"))
        self.assertNotIn("codex_delegation", arguments["prompt"])

    def test_cli_launch_and_explicit_task_message_target(self) -> None:
        launch = subprocess.run(
            [
                sys.executable,
                "-B",
                str(CONSTRUCTOR_PATH),
                "--kind",
                "write",
                "--launch",
                "-",
            ],
            input=json.dumps(write_launch_fields()),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(launch.returncode, 0, launch.stderr)
        self.assertNotRegex(launch.stdout, r"(?m)^TASK_ID:")

        report = subprocess.run(
            [
                sys.executable,
                "-B",
                str(CONSTRUCTOR_PATH),
                "--kind",
                "update",
                "--task-message-to",
                "design-1",
                "-",
            ],
            input=json.dumps(
                {
                    "UPDATE_CLASS": "design_review",
                    "STATUS": "final",
                    "VERDICT": "PASS",
                    "FINDINGS": "D1-D2 have no mapped blocker",
                    "DESIGN_CHECKPOINT": FULL_SHA,
                }
            ),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(report.returncode, 0, report.stderr)
        arguments = json.loads(report.stdout)
        self.assertEqual(arguments["threadId"], "design-1")
        self.assertIn("SUMMARY: PASS", arguments["prompt"])

    def test_cli_live_validation_fails_closed(self) -> None:
        fields = {
            "TASK_ID": "writer-1",
            "TASK_MODE": "write",
            "TASK_ENVIRONMENT": "local",
            "REPOSITORY_ROOT": r"C:\repo",
            "WORKTREE_ROOT": r"C:\repo\.worktrees",
            "EXECUTION_PATH": r"C:\repo\.worktrees\missing",
            "TASK_PROJECT_ID": "project-1",
            "ACTUAL_THREAD_CWD": r"C:\repo",
            "ACTUAL_THREAD_PROJECT_ID": "project-1",
        }
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(CONSTRUCTOR_PATH),
                "--kind",
                "binding",
                "--live",
                "-",
            ],
            input=json.dumps(fields),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("INVALID live binding packet", result.stderr)
        self.assertIn("REPOSITORY_ROOT does not exist", result.stderr)


if __name__ == "__main__":
    unittest.main()
