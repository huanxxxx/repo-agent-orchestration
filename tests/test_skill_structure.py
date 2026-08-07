from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "repo-agent-orchestration"


class SkillStructureTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required = (
            "SKILL.md",
            "agents/openai.yaml",
            "references/controller.md",
            "references/contracts.md",
            "references/recovery.md",
            "scripts/validate_dispatch_contract.py",
        )
        for relative in required:
            self.assertTrue((SKILL / relative).is_file(), relative)

    def test_frontmatter_is_minimal_and_valid(self) -> None:
        content = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        self.assertIsNotNone(match)
        fields = {}
        for line in match.group(1).splitlines():
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
        self.assertEqual(set(fields), {"name", "description"})
        self.assertEqual(fields["name"], "repo-agent-orchestration")
        self.assertTrue(fields["description"])

    def test_default_prompt_names_the_skill(self) -> None:
        metadata = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("$repo-agent-orchestration", metadata)

    def test_installable_skill_has_no_project_docs(self) -> None:
        self.assertFalse((SKILL / "README.md").exists())
        self.assertFalse((SKILL / "LICENSE").exists())

    def test_repository_model_stays_configurable(self) -> None:
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        match = re.search(r"^WRITE_TASK_MODEL: (.+)$", contracts, re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertTrue(match.group(1).startswith("<"))

    def test_skill_uses_repository_host_and_lightweight_route_gate(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        validator = (SKILL / "scripts" / "validate_dispatch_contract.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("Reject projectless", skill)
        self.assertIn("TASK_HOST_POLICY: repository_project_local", contracts)
        self.assertIn('environment: {type: "local"}', contracts)
        self.assertIn("TASK_ENVIRONMENT: local", contracts)
        self.assertIn("App-managed worktree tasks are forbidden", validator)
        self.assertIn("TASK_ARCHIVE_POLICY: controller_after_acceptance", contracts)
        self.assertIn("set_thread_archived", controller)
        self.assertIn("TASK_MODE: write|review_root|review_worktree", contracts)
        self.assertIn("continue in the same turn", contracts)
        self.assertNotIn("BINDING_STATUS", contracts)
        self.assertNotIn("COMMAND_WORKDIR_POLICY", contracts)

    def test_route_cli_uses_live_git_identity_checks(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        validator = (SKILL / "scripts" / "validate_dispatch_contract.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("required paths currently exist", skill)
        self.assertIn("def validate_live_worktree", validator)
        self.assertIn('"worktree", "list", "--porcelain"', validator)
        self.assertIn("must not use detached HEAD", validator)

    def test_controller_waiting_is_event_driven_without_fake_checkpoint(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        validator = (SKILL / "scripts" / "validate_dispatch_contract.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("end the controller turn", skill)
        self.assertIn("Do not call recursive waits", controller)
        self.assertNotIn("CONTROLLER_AFTER_DISPATCH", contracts)
        self.assertNotIn("current_turn_once", contracts)
        self.assertIn("OBSOLETE_DISPATCH_FIELDS", validator)

    def test_review_routing_covers_root_candidate_and_snapshot(self) -> None:
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("root_readonly", contracts)
        self.assertIn("existing_worktree", contracts)
        self.assertIn("detached_snapshot", contracts)

    def test_reports_do_not_duplicate_turn_and_owner_state(self) -> None:
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("STATUS: progress|blocked|final", contracts)
        self.assertNotIn("TURN_STATE:", contracts)
        self.assertNotIn("owner=<controller|task>", contracts)

    def test_controller_reports_preserve_destination_model_settings(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("must omit `model` and `thinking`", skill)
        self.assertIn("TARGET_SETTINGS: preserve", contracts)
        self.assertIn("destination-thread overrides", contracts)
        self.assertIn("controller-model drift", controller)

    def test_readme_documents_demo_compatibility_and_evidence_limits(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Run the local end-to-end demo", readme)
        self.assertIn("## Compatibility and evidence limits", readme)
        self.assertIn("Primary tested surface", readme)
        self.assertIn("does not create Codex tasks", readme)
        self.assertNotIn("saves 80%", readme.casefold())


if __name__ == "__main__":
    unittest.main()
