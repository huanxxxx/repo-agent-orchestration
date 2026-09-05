from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "repo-agent-orchestration"


class SkillStructureTests(unittest.TestCase):
    """Packaging checks only; model behavior is evaluated with realistic cases."""

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

    def test_frontmatter_is_valid(self) -> None:
        content = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        self.assertIsNotNone(match)
        fields = {}
        for line in match.group(1).splitlines():
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
        self.assertEqual(fields["name"], "repo-agent-orchestration")
        self.assertTrue(fields["description"])
        self.assertLessEqual(len(fields["description"]), 1024)

    def test_metadata_has_discoverable_name_and_prompt(self) -> None:
        metadata = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        fields = dict(re.findall(r'^\s+(\w+): "([^"]+)"$', metadata, re.MULTILINE))
        self.assertTrue(fields["display_name"])
        self.assertTrue(25 <= len(fields["short_description"]) <= 64)
        self.assertIn("$repo-agent-orchestration", fields["default_prompt"])

    def test_local_markdown_links_resolve_and_references_are_reachable(self) -> None:
        entry = SKILL / "SKILL.md"
        seen: set[Path] = set()
        pending = [entry]
        while pending:
            source = pending.pop().resolve()
            if source in seen:
                continue
            seen.add(source)
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", source.read_text(encoding="utf-8")):
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", link) or link.startswith("#"):
                    continue
                target = (source.parent / link.split("#", 1)[0]).resolve()
                self.assertTrue(target.is_relative_to(SKILL.resolve()), link)
                self.assertTrue(target.is_file(), f"{source.name}: {link}")
                if target.suffix == ".md":
                    pending.append(target)
        references = {path.resolve() for path in (SKILL / "references").glob("*.md")}
        self.assertTrue(references.issubset(seen), references - seen)

    def test_context_size_budget(self) -> None:
        entry = SKILL / "SKILL.md"
        markdown = (entry,) + tuple((SKILL / "references").glob("*.md"))
        self.assertLessEqual(entry.stat().st_size, 9_300)
        self.assertLessEqual(sum(path.stat().st_size for path in markdown), 49_000)

    def test_installable_skill_has_no_project_docs(self) -> None:
        self.assertFalse((SKILL / "README.md").exists())
        self.assertFalse((SKILL / "LICENSE").exists())

    def test_behavioral_inputs_are_replayable_without_the_rubric(self) -> None:
        cases = json.loads((ROOT / "examples" / "behavioral" / "cases.json").read_text(encoding="utf-8"))
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        self.assertTrue(cases)
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["input"]["request"])
                self.assertTrue(case["input"]["facts"])
                self.assertTrue(case["expected_outcomes"])
                self.assertNotIn("expected_outcomes", case["input"])


if __name__ == "__main__":
    unittest.main()
