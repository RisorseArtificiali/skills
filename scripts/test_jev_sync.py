"""Diff-guard: each consuming skill's jev/ copy must match scripts/jev exactly.

As a unittest: fails on drift. Run `python3 scripts/test_jev_sync.py --fix` to
re-sync every declared copy from the source of truth (the lince
gen_registry/test_registry_sync pattern: edit the source, then regenerate).
"""

import argparse
import filecmp
import shutil
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SOURCE = SCRIPTS / "jev"
# Every skill that consumes the layer must be listed here.
CONSUMERS = ["pr-assessment"]


def copies(repo_root):
    for skill in CONSUMERS:
        yield skill, repo_root / "skills" / skill / "jev"


def drifted(repo_root):
    result = []
    for skill, target in copies(repo_root):
        source_files = sorted(p.relative_to(SOURCE) for p in SOURCE.rglob("*") if p.is_file())
        if not target.is_dir():
            result.append((skill, None))
            continue
        target_files = sorted(p.relative_to(target) for p in target.rglob("*") if p.is_file())
        if source_files != target_files:
            result.append((skill, None))
            continue
        for relative in source_files:
            if not filecmp.cmp(SOURCE / relative, target / relative, shallow=False):
                result.append((skill, relative))
    return result


class JevSyncTests(unittest.TestCase):
    def test_skill_copies_match_the_source(self):
        problems = drifted(SCRIPTS.parent)
        if problems:
            detail = "; ".join(f"{skill}:{path or 'missing or file-set differs'}"
                               for skill, path in problems)
            self.fail(
                f"skills' jev/ copies drifted from scripts/jev: {detail}. "
                f"Run: python3 scripts/test_jev_sync.py --fix")


def fix(repo_root):
    for skill, target in copies(repo_root):
        if target.is_dir():
            shutil.rmtree(target)
        shutil.copytree(SOURCE, target)
        print(f"synced {target}")


if __name__ == "__main__":
    if "--fix" in sys.argv:
        fix(SCRIPTS.parent)
    else:
        unittest.main()
