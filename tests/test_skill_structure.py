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
            "references/continuity.md",
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

    def test_worktrees_belong_to_independent_tasks_not_subagents(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("More agents alone never justify more worktrees", skill)
        self.assertIn("Different peer write tasks never share", skill)
        self.assertIn("Agent count alone is not a task boundary", controller)
        self.assertIn("EXECUTION_PATH: inherit_current", contracts)
        self.assertIn("must not create another branch or worktree", controller)

    def test_continuity_package_and_snapshot_boundaries_are_lightweight(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        continuity = (SKILL / "references" / "continuity.md").read_text(
            encoding="utf-8"
        )
        recovery = (SKILL / "references" / "recovery.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("references/continuity.md", skill)
        self.assertIn("App task owns", continuity)
        self.assertIn("Git worktree owns", continuity)
        self.assertIn("not an authorization token", continuity)
        self.assertIn("Do not create a package for short work", continuity)
        self.assertIn("HEAD of a clean task worktree", recovery)
        self.assertIn("user explicitly requests one", recovery)

    def test_focused_evidence_cannot_claim_full_or_production_proof(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("focused checks do not prove the full repository", skill)
        self.assertIn("or production behavior", skill)

    def test_task_output_is_checkpointed_before_crossing_boundaries(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        recovery = (SKILL / "references" / "recovery.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("cross-turn pause, ownership handoff, formal review, or `final`", skill)
        self.assertIn("that task verifies and commits the combined checkpoint", skill)
        self.assertIn("Do not strand completed work only in a dirty worktree", controller)
        self.assertIn("write-task `final`", contracts)
        self.assertIn("exact dirty paths", contracts)
        self.assertIn("prechange snapshot from a checkpoint commit", recovery)

    def test_write_tasks_stop_at_acceptance_without_scope_expansion(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("smallest change that satisfies", skill)
        self.assertIn("Every changed path must have a concrete acceptance justification", skill)
        self.assertIn("Once the required acceptance and tests pass, stop implementation", skill)
        self.assertIn("OWNED_PATHS` says where a task may write", controller)
        self.assertIn("mapping from each acceptance condition", controller)
        self.assertIn("Passing acceptance is the stop condition", contracts)
        self.assertIn("map each acceptance condition to its changed paths", contracts)

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
        self.assertIn("startup wait at most once", skill)
        self.assertIn("must not trigger a second wait", controller)
        self.assertIn("Do not call recursive waits", controller)
        self.assertNotIn("CONTROLLER_AFTER_DISPATCH", contracts)
        self.assertNotIn("current_turn_once", contracts)
        self.assertIn("OBSOLETE_DISPATCH_FIELDS", validator)

    def test_app_tasks_are_peers_not_internal_subagents(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        published = "\n".join((skill, controller, contracts, readme)).casefold()
        self.assertIn("app-created user-visible task is a peer task", published)
        self.assertIn("controller is a coordination role", published)
        self.assertIn("actual creation capability", published)
        self.assertIn("same-task parent/subagent relationship", published)
        self.assertIn("queued worktree setup", published)
        self.assertIn("phantom task", published)
        self.assertNotIn("child task", published)
        self.assertNotIn("child final", published)
        self.assertNotIn("child packet", published)
        self.assertNotIn("child local final", published)

    def test_review_routing_covers_root_candidate_and_snapshot(self) -> None:
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("root_readonly", contracts)
        self.assertIn("existing_worktree", contracts)
        self.assertIn("detached_snapshot", contracts)

    def test_review_contract_freezes_acceptance_and_stops_scope_drift(self) -> None:
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
        self.assertIn("Freeze the acceptance baseline", skill)
        self.assertIn("ACCEPTANCE_BASELINE:", contracts)
        self.assertIn("THREAT_MODEL:", contracts)
        self.assertIn("NON_GOALS:", contracts)
        self.assertIn("Severity alone never grants scope", controller)
        self.assertIn("scope-drift audit", controller)
        self.assertIn('"ACCEPTANCE_BASELINE"', validator)

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
