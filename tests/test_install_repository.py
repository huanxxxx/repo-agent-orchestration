from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER_PATH = ROOT / "scripts" / "install_repository.py"
SPEC = importlib.util.spec_from_file_location("repository_installer", INSTALLER_PATH)
assert SPEC and SPEC.loader
INSTALLER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = INSTALLER
SPEC.loader.exec_module(INSTALLER)


class RepositoryInstallerTests(unittest.TestCase):
    def make_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        repo = Path(temporary.name).resolve()
        subprocess.run(
            ["git", "init", "-b", "main", str(repo)],
            check=True,
            capture_output=True,
        )
        return temporary, repo

    def commit_baseline(self, repo: Path, branch: str | None = None) -> None:
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.name", "Test"], check=True
        )
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.email", "test@example.invalid"],
            check=True,
        )
        if branch:
            subprocess.run(["git", "-C", str(repo), "checkout", "-b", branch], check=True)
        (repo / "README.md").write_text("# test\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-m", "baseline"], check=True
        )

    def settings(self, repo: Path, model: str = "app_default"):
        return INSTALLER.Settings(
            main_branch="main",
            worktree_root=repo / ".worktrees",
            write_task_model=model,
        )

    def test_detect_main_branch_prefers_remote_origin_head(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)
        self.commit_baseline(repo)
        head = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip()
        subprocess.run(
            ["git", "-C", str(repo), "update-ref", "refs/remotes/origin/main", head],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "symbolic-ref",
                "refs/remotes/origin/HEAD",
                "refs/remotes/origin/main",
            ],
            check=True,
        )

        self.assertEqual(INSTALLER.detect_main_branch(repo), "main")

    def test_detect_main_branch_uses_standard_candidate(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)
        self.commit_baseline(repo)

        self.assertEqual(INSTALLER.detect_main_branch(repo), "main")

    def test_detect_main_branch_falls_back_to_current_branch(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)
        self.commit_baseline(repo, "feature-x")

        self.assertEqual(INSTALLER.detect_main_branch(repo), "feature-x")

    def test_installs_skill_and_creates_minimal_agents_file(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)

        result = INSTALLER.install_repository(repo, self.settings(repo))

        self.assertTrue(result["agents_created"])
        self.assertTrue(
            (repo / ".agents" / "skills" / "repo-agent-orchestration" / "SKILL.md").is_file()
        )
        agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("ORCHESTRATION_SKILL: $repo-agent-orchestration", agents)
        self.assertIn("TASK_HOST_POLICY: repository_project_local", agents)
        self.assertIn(f"WORKTREE_ROOT: {repo / '.worktrees'}", agents)
        self.assertIn("WRITE_TASK_MODEL: app_default", agents)
        self.assertIn("CONTINUITY_POLICY: none", agents)
        self.assertIn(
            "Use the repository-local `$repo-agent-orchestration` Skill", agents
        )
        self.assertIn("independent task ownership", agents)
        self.assertIn("do not collapse it into current-task execution", agents)

    def test_preserves_existing_agents_content_and_updates_only_managed_block(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)
        agents_path = repo / "AGENTS.md"
        agents_path.write_text("# Existing rules\n\nKeep this sentence.\n", encoding="utf-8")

        INSTALLER.install_repository(repo, self.settings(repo))
        first = agents_path.read_text(encoding="utf-8")
        INSTALLER.install_repository(repo, self.settings(repo, "executor/medium"))
        second = agents_path.read_text(encoding="utf-8")

        self.assertIn("# Existing rules\n\nKeep this sentence.\n", second)
        self.assertEqual(second.count(INSTALLER.BEGIN_MARKER), 1)
        self.assertEqual(second.count(INSTALLER.END_MARKER), 1)
        self.assertIn("WRITE_TASK_MODEL: executor/medium", second)
        self.assertIn(
            "Use the repository-local `$repo-agent-orchestration` Skill", second
        )
        self.assertNotEqual(first, second)
        third = INSTALLER.install_repository(repo, self.settings(repo, "executor/medium"))
        self.assertFalse(third["agents_changed"])
        self.assertEqual(third["changed_skill_files"], 0)
        self.assertTrue(third["up_to_date"])

    def test_cli_upgrade_without_overrides_preserves_managed_profile(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)
        custom = INSTALLER.Settings(
            main_branch="main",
            worktree_root=repo / ".worktrees",
            write_task_model="custom-executor/high",
            review_task_model="custom-review/medium",
            shared_integration_paths="docs/status.md",
            continuity_policy="repository_defined:docs/status.md",
        )
        INSTALLER.install_repository(repo, custom)
        before = (repo / "AGENTS.md").read_text(encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-B", str(INSTALLER_PATH), "--repo", str(repo)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), before)
        self.assertIn("CONTINUITY_POLICY: repository_defined:docs/status.md", before)

    def test_cli_upgrade_migrates_legacy_luna_default_to_app_default(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)
        legacy = INSTALLER.Settings(
            main_branch="main",
            worktree_root=repo / ".worktrees",
            write_task_model="gpt-5.6-luna/max",
        )
        INSTALLER.install_repository(repo, legacy)

        result = subprocess.run(
            [sys.executable, "-B", str(INSTALLER_PATH), "--repo", str(repo)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("WRITE_TASK_MODEL: app_default", agents)
        self.assertNotIn("WRITE_TASK_MODEL: gpt-5.6-luna/max", agents)

    def test_explicit_cli_can_still_bind_legacy_luna_model(self) -> None:
        self.assertEqual(
            INSTALLER.resolve_write_task_model(
                "gpt-5.6-luna/max", "gpt-5.6-luna/max"
            ),
            "gpt-5.6-luna/max",
        )

    def test_invalid_write_task_model_is_rejected_at_install(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)

        with self.assertRaisesRegex(ValueError, "write task model must be"):
            INSTALLER.install_repository(repo, self.settings(repo, "executor"))

    def test_invalid_review_task_model_is_rejected_at_install(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)
        settings = INSTALLER.Settings(
            main_branch="main",
            worktree_root=repo / ".worktrees",
            review_task_model="<placeholder>/high",
        )

        with self.assertRaisesRegex(ValueError, "review task model must be"):
            INSTALLER.install_repository(repo, settings)

    def test_valid_profile_model_with_slash_is_accepted_at_install(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)

        result = INSTALLER.install_repository(
            repo, self.settings(repo, "gpt-5.6-luna/max")
        )

        agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("WRITE_TASK_MODEL: gpt-5.6-luna/max", agents)
        self.assertTrue(result["agents_changed"])

    def test_check_reports_drift_without_writing(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)

        before = subprocess.run(
            [sys.executable, "-B", str(INSTALLER_PATH), "--repo", str(repo), "--check"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(before.returncode, 1)
        self.assertFalse((repo / ".agents").exists())

        INSTALLER.install_repository(repo, self.settings(repo))
        after = subprocess.run(
            [sys.executable, "-B", str(INSTALLER_PATH), "--repo", str(repo), "--check"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(after.returncode, 0, after.stderr or after.stdout)

    def test_installs_from_linked_worktree_with_primary_repo_worktree_root(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.email", "test@example.invalid"],
            check=True,
        )
        (repo / "README.md").write_text("# test\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-m", "baseline"], check=True)
        linked = repo / "linked-install"
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", "-b", "install-test", str(linked)],
            check=True,
            capture_output=True,
        )

        result = INSTALLER.install_repository(linked, self.settings(repo))

        self.assertEqual(INSTALLER.primary_worktree_root(linked), repo)
        self.assertEqual(result["repository"], str(linked.resolve()))
        self.assertTrue(
            (linked / ".agents" / "skills" / "repo-agent-orchestration" / "SKILL.md").is_file()
        )
        agents = (linked / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn(f"WORKTREE_ROOT: {repo / '.worktrees'}", agents)

    def test_preserves_legacy_profile_values_and_only_adds_missing_parameters(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)
        agents_path = repo / "AGENTS.md"
        agents_path.write_text(
            "# Existing rules\n\n"
            "MAIN_BRANCH: trunk\n"
            "WORKTREE_ROOT: D:\\custom\\trees\n"
            "WRITE_TASK_MODEL: custom-executor/high\n",
            encoding="utf-8",
        )

        INSTALLER.install_repository(repo, self.settings(repo))
        agents = agents_path.read_text(encoding="utf-8")

        self.assertEqual(agents.count("MAIN_BRANCH:"), 1)
        self.assertEqual(agents.count("WORKTREE_ROOT:"), 1)
        self.assertEqual(agents.count("WRITE_TASK_MODEL:"), 1)
        self.assertIn("MAIN_BRANCH: trunk", agents)
        self.assertIn("WORKTREE_ROOT: D:\\custom\\trees", agents)
        self.assertIn("WRITE_TASK_MODEL: custom-executor/high", agents)
        self.assertIn("ORCHESTRATION_SKILL: $repo-agent-orchestration", agents)
        self.assertIn("TASK_HOST_POLICY: repository_project_local", agents)

    def test_dry_run_does_not_write(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)

        result = INSTALLER.install_repository(repo, self.settings(repo), dry_run=True)

        self.assertTrue(result["agents_created"])
        self.assertFalse((repo / "AGENTS.md").exists())
        self.assertFalse((repo / ".agents").exists())

    def test_rejects_a_subdirectory_instead_of_exact_repository_root(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)
        child = repo / "child"
        child.mkdir()

        with self.assertRaisesRegex(ValueError, "exact Git repository root"):
            INSTALLER.install_repository(child, self.settings(repo))

    def test_rejects_a_worktree_root_outside_the_repository(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)
        outside = repo.parent / "outside-worktrees"
        settings = INSTALLER.Settings(main_branch="main", worktree_root=outside)

        with self.assertRaisesRegex(ValueError, "inside the target repository"):
            INSTALLER.install_repository(repo, settings)

    def test_check_reports_unmanaged_skill_files_as_json_error(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)
        INSTALLER.install_repository(repo, self.settings(repo))
        extra = (
            repo
            / ".agents"
            / "skills"
            / "repo-agent-orchestration"
            / "unmanaged.txt"
        )
        extra.write_text("unmanaged\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-B", str(INSTALLER_PATH), "--repo", str(repo), "--check"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("unmanaged files", result.stderr)
        self.assertIn("unmanaged.txt", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_rejects_invalid_model_without_traceback(self) -> None:
        temporary, repo = self.make_repo()
        self.addCleanup(temporary.cleanup)

        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(INSTALLER_PATH),
                "--repo",
                str(repo),
                "--write-task-model",
                "bad value",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("write task model must be", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse((repo / "AGENTS.md").exists())

    def test_package_files_excludes_python_cache_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / "scripts").mkdir()
            (source / "scripts" / "tool.py").write_text("pass\n", encoding="utf-8")
            (source / "scripts" / "__pycache__").mkdir()
            (source / "scripts" / "__pycache__" / "tool.cpython-313.pyc").write_bytes(
                b"cache"
            )
            (source / "loose.pyc").write_bytes(b"cache")

            files = INSTALLER.package_files(source)

            self.assertEqual(files, [Path("scripts/tool.py")])

    def test_text_package_payload_is_stable_across_checkout_line_endings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "contract.md"
            source.write_bytes(b"first\r\nsecond\rthird\n")

            self.assertEqual(
                INSTALLER.package_payload(source), b"first\nsecond\nthird\n"
            )

    def test_binary_package_payload_is_byte_exact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "asset.bin"
            source.write_bytes(b"first\r\nsecond")

            self.assertEqual(INSTALLER.package_payload(source), b"first\r\nsecond")


if __name__ == "__main__":
    unittest.main()
