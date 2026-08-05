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

    def test_skill_uses_repository_host_and_execution_worktree(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        contracts = (SKILL / "references" / "contracts.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Separate task hosting from task execution", skill)
        self.assertIn("Reject `projectless`", contracts)
        self.assertIn("TASK_HOST_POLICY: repository_project_local", contracts)
        self.assertIn("COMMAND_WORKDIR_POLICY: exact_execution_worktree", contracts)
        self.assertIn("--kind binding", contracts)
        self.assertIn("dot segments lexically", contracts)
        self.assertIn("not filesystem evidence", contracts)

    def test_readme_documents_demo_compatibility_and_evidence_limits(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Run the local end-to-end demo", readme)
        self.assertIn("## Compatibility and evidence limits", readme)
        self.assertIn("Primary tested surface", readme)
        self.assertIn("does not create Codex tasks", readme)
        self.assertNotIn("saves 80%", readme.casefold())


if __name__ == "__main__":
    unittest.main()
