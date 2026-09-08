#!/usr/bin/env python3
"""Install the locked toolkit into Codex discovery using non-destructive links."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def git(directory, *args):
    result = subprocess.run(
        ["git", "-C", str(directory), *args], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return result.stdout.strip()


def skill_name(directory):
    content = (directory / "SKILL.md").read_text()
    if not content.startswith("---\n"):
        raise ValueError(f"Missing skill frontmatter: {directory}")
    front = content.split("---", 2)[1]
    match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", front, re.M)
    if not match or not re.search(r"^description:", front, re.M):
        raise ValueError(f"Invalid skill metadata: {directory}")
    return match[1]


def prepare_source(source, cache, header):
    # The adapter version is part of the cache key: updates never edit a
    # checkout to which an existing installation still points.
    revision = source["ref"]
    key = hashlib.sha256(header.encode() + Path(__file__).read_bytes()
                         + json.dumps(source, sort_keys=True).encode()).hexdigest()[:12]
    destination = cache / source["repo"].replace("/", "--") / f"{revision}-{key}"
    if (destination / ".toolkit-ready").is_file():
        return destination
    if destination.exists():
        raise ValueError(f"Incomplete cache entry: {destination}; inspect and remove it before retrying")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".install-", dir=destination.parent))
    try:
        git(staging, "init", "--quiet")
        git(staging, "remote", "add", "origin", f"https://github.com/{source['repo']}.git")
        git(staging, "fetch", "--quiet", "--depth=1", "origin", revision)
        git(staging, "checkout", "--quiet", "--detach", "FETCH_HEAD")
        if git(staging, "rev-parse", "HEAD") != revision:
            raise ValueError(f"Wrong upstream revision for {source['repo']}")
        for name, relative in source["skills"].items():
            folder = staging / relative
            if skill_name(folder) != name:
                raise ValueError(f"Skill name mismatch: {folder}")
            entry = folder / "SKILL.md"
            original = entry.read_text()
            end = original.index("\n---", 4) + 4
            entry.write_text(original[:end] + "\n\n" + header + original[end:])
            if re.search(r"^disable-model-invocation:\s*true\s*$", original[:end], re.M):
                metadata = folder / "agents/openai.yaml"
                if not metadata.exists():
                    metadata.parent.mkdir(exist_ok=True)
                    metadata.write_text("policy:\n  allow_implicit_invocation: false\n")
        # This upstream reference routes Codex to cheaper model tiers. The
        # toolkit's inherited-model policy is maintained in the tracked adapter.
        host_ref = staging / "skills/using-superpowers/references/codex-tools.md"
        if host_ref.is_file():
            host_ref.write_text(header)
        (staging / ".toolkit-ready").write_text(revision + "\n")
        staging.rename(destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination


def install(args):
    lock = json.loads((ROOT / "compat/codex/upstream.lock.json").read_text())
    header = (ROOT / "compat/codex/skill-header.md").read_text()
    entries = {}
    for parent in (ROOT / "skills", ROOT / "forked"):
        for entry in sorted(parent.glob("*/SKILL.md")):
            name = skill_name(entry.parent)
            if name in entries:
                raise ValueError(f"Duplicate local skill: {name}")
            entries[name] = entry.parent
    for source in lock["sources"]:
        if not re.fullmatch(r"[0-9a-f]{40}", source["ref"]):
            raise ValueError(f"Unpinned source: {source['repo']}")
        for name in source["skills"]:
            if name in entries:
                raise ValueError(f"Duplicate skill in lock: {name}")
            entries[name] = None

    dest = args.dest.expanduser().absolute()
    cache = args.cache.expanduser().absolute()
    # Preflight every destination before downloading or linking anything.
    for name, local in entries.items():
        target = dest / name
        if os.path.lexists(target):
            resolved = target.resolve()
            managed = target.is_symlink() and (resolved == local or resolved.is_relative_to(cache))
            if not managed:
                raise ValueError(f"Refusing to replace existing skill: {target}")
        legacy = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills" / name
        if legacy != target and os.path.lexists(legacy):
            raise ValueError(f"Duplicate legacy skill: {legacy}; resolve it before installing {target}")

    for source in lock["sources"]:
        if args.dry_run:
            print(f"fetch {source['repo']} @ {source['ref']}")
            continue
        print(f"Preparing {source['repo']} @ {source['ref'][:12]}", flush=True)
        checkout = prepare_source(source, cache, header)
        for name, relative in source["skills"].items():
            entries[name] = checkout / relative

    if not args.dry_run:
        for name, source in entries.items():
            if skill_name(source) != name:
                raise ValueError(f"Invalid installed source: {source}")
        dest.mkdir(parents=True, exist_ok=True)
    for name, source in sorted(entries.items()):
        target = dest / name
        if args.dry_run:
            print(f"link {target} -> {source or 'locked upstream skill'}")
            continue
        if target.is_symlink() and target.resolve() == source.resolve():
            continue
        if target.is_symlink():
            target.unlink()
        target.symlink_to(source, target_is_directory=True)
    print(f"{'Would install' if args.dry_run else 'Installed'} {len(entries)} skills in {dest}")
    for skipped in lock["excluded"]:
        print(f"Excluded {skipped['name']}: {skipped['reason']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Show sources and links; no writes or network")
    parser.add_argument("--dest", type=Path, default=Path.home() / ".agents/skills")
    parser.add_argument("--cache", type=Path,
                        default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "toolkit/upstream")
    args = parser.parse_args()
    try:
        install(args)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError):
            print(error.stderr, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
