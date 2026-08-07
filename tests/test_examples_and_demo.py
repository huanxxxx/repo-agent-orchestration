from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublishedExamplesTests(unittest.TestCase):
    def run_json_script(self, relative: str) -> dict[str, object]:
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / relative)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        return json.loads(result.stdout)

    def test_published_contract_examples_match_their_expected_result(self) -> None:
        result = self.run_json_script("scripts/validate_examples.py")
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["cases"]), 11)

    def test_local_demo_proves_isolation_and_rejects_invalid_binding(self) -> None:
        result = self.run_json_script("scripts/run_local_demo.py")
        self.assertTrue(result["passed"])
        self.assertTrue(result["writers_isolated"])
        self.assertTrue(result["invalid_binding_rejected"])
        self.assertTrue(result["missing_worktree_rejected"])
        self.assertTrue(result["root_clean"])
        self.assertIn("no Codex task", result["evidence_limit"])

    def test_direct_cli_fails_closed_for_a_missing_example_worktree(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(
                    ROOT
                    / "skill"
                    / "repo-agent-orchestration"
                    / "scripts"
                    / "validate_dispatch_contract.py"
                ),
                "--kind",
                "write",
                str(ROOT / "examples" / "contracts" / "valid-write-luna-max.txt"),
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("WORKTREE_ROOT does not exist", result.stdout)
        self.assertIn("WORKTREE does not exist", result.stdout)


if __name__ == "__main__":
    unittest.main()
