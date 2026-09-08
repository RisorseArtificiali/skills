"""Offline installation and worktree regression checks (standard library only)."""

import argparse
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("installer", SCRIPTS / "install-codex-skills.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "toolkit with spaces"
        (self.repo / "skills/local-skill").mkdir(parents=True)
        (self.repo / "forked").mkdir()
        (self.repo / "skills/local-skill/SKILL.md").write_text(
            "---\nname: local-skill\ndescription: A fixture\n---\nOriginal instructions\n")
        (self.repo / "compat/codex").mkdir(parents=True)
        (self.repo / "compat/codex/skill-header.md").write_text("Host mapping\n")
        (self.repo / "compat/codex/upstream.lock.json").write_text(
            json.dumps({"sources": [], "excluded": []}))
        self.args = argparse.Namespace(dest=self.root / "discovery", cache=self.root / "cache", dry_run=False)
        self.addCleanup(patch.stopall)
        patch.object(installer, "ROOT", self.repo).start()
        patch.dict(os.environ, {"CODEX_HOME": str(self.root / "codex")}).start()

    def run_install(self):
        with contextlib.redirect_stdout(io.StringIO()):
            installer.install(self.args)

    def test_local_links_are_live_and_reinstallation_preserves_them(self):
        self.run_install()
        target = self.args.dest / "local-skill"
        self.assertTrue(target.is_symlink())
        before = target.lstat().st_ino
        entry = self.repo / "skills/local-skill/SKILL.md"
        entry.write_text(entry.read_text() + "Updated in repository\n")
        self.run_install()
        self.assertEqual(before, target.lstat().st_ino)
        self.assertIn("Updated in repository", (target / "SKILL.md").read_text())

    def test_conflict_is_preserved_and_no_cache_is_created(self):
        existing = self.args.dest / "local-skill"
        existing.mkdir(parents=True)
        (existing / "keep.txt").write_text("user data")
        with self.assertRaisesRegex(ValueError, "Refusing to replace"):
            self.run_install()
        self.assertEqual((existing / "keep.txt").read_text(), "user data")
        self.assertFalse(self.args.cache.exists())

    def test_foreign_broken_symlink_is_preserved(self):
        self.args.dest.mkdir()
        target = self.args.dest / "local-skill"
        target.symlink_to(self.root / "missing")
        with self.assertRaisesRegex(ValueError, "Refusing to replace"):
            self.run_install()
        self.assertTrue(target.is_symlink())

    def test_dry_run_has_no_writes_or_downloads(self):
        self.args.dry_run = True
        with patch.object(installer, "git", side_effect=AssertionError("network in dry-run")):
            self.run_install()
        self.assertFalse(self.args.dest.exists())
        self.assertFalse(self.args.cache.exists())

    def test_legacy_duplicate_is_detected_before_writes(self):
        (self.root / "codex/skills/local-skill").mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "Duplicate legacy"):
            self.run_install()
        self.assertFalse(self.args.dest.exists())


class WorkflowTests(unittest.TestCase):
    def test_scaffold_and_artifact_paths_in_linked_worktree(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "main"
            repo.mkdir()
            def git(*args, cwd=repo):
                return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()
            git("init", "--quiet")
            git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                "commit", "--quiet", "--allow-empty", "-m", "baseline")
            worktree = root / "linked with spaces"
            git("worktree", "add", "--quiet", "--detach", str(worktree))
            for _ in range(2):
                subprocess.run(["bash", str(SCRIPTS / "wire-machine.sh"), "--scaffold"],
                               cwd=worktree, check=True, stdout=subprocess.DEVNULL)
            exclude = Path(git("rev-parse", "--git-path", "info/exclude", cwd=worktree))
            if not exclude.is_absolute():
                exclude = worktree / exclude
            self.assertEqual(exclude.read_text().splitlines().count("AGENTS.local.md"), 1)
            self.assertEqual(git("status", "--porcelain", cwd=worktree), "")
            plan = worktree / "plan with spaces.md"
            plan.write_text("# Plan\n### Task 1: One\nDo one thing.\n### Task 2: Two\nDo two things.\n")
            helpers = SCRIPTS.parent / "forked/subagent-driven-development/scripts"
            brief = subprocess.check_output([str(helpers / "task-brief"), str(plan), "1"],
                                            cwd=worktree, text=True).strip()
            self.assertIn("Do one thing.", Path(brief).read_text())
            self.assertNotIn("Do two things.", Path(brief).read_text())
            package = subprocess.check_output([str(helpers / "review-package"), str(plan), "HEAD", "HEAD"],
                                              cwd=worktree, text=True).strip()
            self.assertIn("## Diff", Path(package).read_text())


if __name__ == "__main__":
    unittest.main()
