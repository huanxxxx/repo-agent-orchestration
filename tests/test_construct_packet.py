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


class PacketConstructorTests(unittest.TestCase):
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
