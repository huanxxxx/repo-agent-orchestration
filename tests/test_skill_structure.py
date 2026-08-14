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
            "references/architected.md",
            "references/contracts.md",
            "references/continuity.md",
            "references/recovery.md",
            "scripts/validate_dispatch_contract.py",
            "scripts/packet_schema.py",
            "scripts/construct_packet.py",
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

    def test_architected_mode_separates_design_and_delivery_authority(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        architected = (SKILL / "references" / "architected.md").read_text(
            encoding="utf-8"
        )
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("`direct`", skill)
        self.assertIn("`delivery`", skill)
        self.assertIn("`architected`", skill)
        self.assertIn("Treat a proposed solution as input, not proof", architected)
        self.assertIn("recommend a preferred option", architected)
        self.assertIn("Do not manufacture objections", architected)
        self.assertIn("independent design-review PASS", architected)
        self.assertIn("single repository-root write lease", architected)
        self.assertIn("Never write the root concurrently", architected)
        self.assertIn("Do not absorb the design-authority role", controller)

    def test_delivery_controller_proactively_dispatches_ready_work(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        architected = (SKILL / "references" / "architected.md").read_text(
            encoding="utf-8"
        )
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("dispatch all ready, non-conflicting peer tasks", skill)
        self.assertIn("without waiting for a separate user instruction", architected)
        self.assertIn("does not require a separate user request to parallelize", controller)
        self.assertIn("Never create duplicate tasks", architected)

    def test_architected_report_chain_is_bidirectional_and_event_driven(self) -> None:
        architected = (SKILL / "references" / "architected.md").read_text(
            encoding="utf-8"
        )
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("delivery controller --DELIVERY_UPDATE", architected)
        self.assertIn("design authority --DESIGN_HANDOFF", architected)
        self.assertIn("design authority --DESIGN_DECISION", architected)
        self.assertIn("DESIGN_REOPEN_REQUEST", contracts)
        self.assertIn("DECISION_REQUIRED: yes|no", contracts)
        self.assertIn("does not pause authorized work", contracts)
        self.assertIn("without waking it merely to acknowledge acceptance", architected)

    def test_packet_constructor_shares_schema_and_stays_pure(self) -> None:
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        validator = (SKILL / "scripts" / "validate_dispatch_contract.py").read_text(
            encoding="utf-8"
        )
        constructor = (SKILL / "scripts" / "construct_packet.py").read_text(
            encoding="utf-8"
        )
        schema = (SKILL / "scripts" / "packet_schema.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("from packet_schema import REQUIRED", validator)
        self.assertIn("from packet_schema import PACKET_SCHEMAS", constructor)
        self.assertIn('"design_handoff"', schema)
        self.assertIn('"delivery_update"', schema)
        self.assertIn('"design_reopen"', schema)
        self.assertIn('"design_decision"', schema)
        self.assertIn("It never creates tasks, touches Git", contracts)

    def test_hot_path_is_bounded_and_markdown_has_a_size_budget(self) -> None:
        skill_path = SKILL / "SKILL.md"
        markdown = (skill_path,) + tuple((SKILL / "references").glob("*.md"))
        skill = skill_path.read_text(encoding="utf-8")
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        constructor = (SKILL / "scripts" / "construct_packet.py").read_text(
            encoding="utf-8"
        )
        validator = (
            SKILL / "scripts" / "validate_dispatch_contract.py"
        ).read_text(encoding="utf-8")

        self.assertLessEqual(skill_path.stat().st_size, 8_200)
        self.assertLessEqual(sum(path.stat().st_size for path in markdown), 42_000)
        self.assertIn("once per task/runtime binding", skill)
        self.assertIn("Do not reload the Skill bundle", skill)
        self.assertIn("Do not create temporary packet files", skill)
        self.assertIn("Do not reread the full Skill/reference bundle", controller)
        self.assertIn("executor-only domain Skills", controller)
        self.assertIn('"--live"', constructor)
        self.assertIn('args.contract == "-"', validator)

    def test_installable_skill_has_no_project_docs(self) -> None:
        self.assertFalse((SKILL / "README.md").exists())
        self.assertFalse((SKILL / "LICENSE").exists())

    def test_repository_model_stays_configurable(self) -> None:
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        match = re.search(r"^WRITE_TASK_MODEL: (.+)$", contracts, re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "app_default|<explicit model/reasoning>")

    def test_write_model_defaults_to_host_compatible_and_keeps_explicit_binding(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("For `app_default`, omit `model` and `thinking`", skill)
        self.assertIn("MODEL_POLICY: app_default|repo_write_default", contracts)
        self.assertIn("host's advertised model catalog", controller)
        self.assertIn("instead of guessing from the controller model name", controller)

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
        self.assertIn(
            "TASK_ARCHIVE_POLICY: dispatching_authority_after_acceptance",
            contracts,
        )
        self.assertIn("set_thread_archived", controller)
        self.assertIn(
            "TASK_MODE: delivery_controller|write|review_root|review_worktree",
            contracts,
        )
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

    def test_post_pass_continuity_closeout_does_not_reopen_review(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        continuity = (SKILL / "references" / "continuity.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("do not reopen review merely because", skill)
        self.assertIn("reviewed checkpoint distinct from the later continuity checkpoint", skill)
        self.assertIn("sole detailed hot-state surface", continuity)
        self.assertIn("does not invalidate the prior PASS", continuity)
        self.assertIn("Do not dispatch a peer reviewer", continuity)
        self.assertIn("invent new acceptance criteria", continuity)
        self.assertIn("classify any proposed closeout diff", controller)
        self.assertIn("Never dispatch a docs-only reviewer", controller)

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

    def test_authorities_yield_after_events_and_fail_closed_on_protocol_errors(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        architected = (SKILL / "references" / "architected.md").read_text(
            encoding="utf-8"
        )
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("one bounded event batch", skill)
        self.assertIn("PROTOCOL_BLOCKED", skill)
        self.assertIn("End the design-authority turn", architected)
        self.assertIn("must not inspect, wait on, or monitor", architected)
        self.assertIn("End the controller turn", controller)
        self.assertIn("Do not relabel the same content", contracts)

    def test_peer_creation_is_single_attempt_and_unknown_receipts_are_reconciled(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("one creation call per logical dispatch", skill)
        self.assertIn("never authorizes an immediate second creation call", skill)
        self.assertIn("Make exactly one creation call", controller)
        self.assertIn("creation outcome unknown", controller)
        self.assertIn("list tasks and reconcile", controller)

    def test_scope_reopen_and_active_peer_turns_fail_closed(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("only the design authority may change the design baseline", skill)
        self.assertIn("DESIGN_REOPEN_REQUEST", skill)
        self.assertIn("it may not authorize itself", controller)
        self.assertIn(
            "When the task is `active`, do not send another continuation or correction",
            skill,
        )
        self.assertIn(
            "If the task is `active`, do not send a plain `continue`", controller
        )
        self.assertIn(
            "current active-turn evidence identifies more than one live turn",
            controller,
        )

    def test_live_turn_gate_uses_runtime_status_not_stale_history(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        recovery = (SKILL / "references" / "recovery.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("current top-level runtime status", skill)
        self.assertIn("`idle` or `notLoaded` means no live turn", skill)
        self.assertIn(
            "persisted historical turn rows are not a live-turn inventory", controller
        )
        self.assertIn(
            "do not block, archive/restore, interrupt, or ask the user", controller
        )
        self.assertIn("do not override it by paging persisted historical turns", recovery)
        self.assertNotIn("while any turn is `inProgress`", skill)

    def test_app_tasks_are_peers_not_internal_subagents(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        controller = (SKILL / "references" / "controller.md").read_text(
            encoding="utf-8"
        )
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        demo = (ROOT / "examples" / "demo" / "CODEX_DESKTOP_RUNBOOK.md").read_text(
            encoding="utf-8"
        )
        published = "\n".join((skill, controller, contracts, readme, demo)).casefold()
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
