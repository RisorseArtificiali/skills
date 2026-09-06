**English** · [Italiano](CODEX_IT.md)

# Using the toolkit with Codex

The Codex profile installs 37 skills: the 15 maintained here and 22 selected
upstream skills. The sources, complete commit IDs and skill paths are in
[`compat/codex/upstream.lock.json`](compat/codex/upstream.lock.json).

## Install and update

Requires Python 3.9+ and Git; GitHub workflows also need authenticated `gh`.
Run from this checkout:

```sh
AGENT=codex scripts/wire-machine.sh --dry-run --skills
AGENT=codex scripts/wire-machine.sh --skills
AGENT=codex scripts/wire-machine.sh --check
```

Local skill folders are linked into `~/.agents/skills/`, so edits in this repo
are immediately reflected in the installation. Upstream repositories are fetched
at the locked commits under `${CODEX_HOME:-~/.codex}/toolkit/upstream/`; only the
selected skill folders are exposed. Full repository snapshots preserve licenses,
scripts and references outside individual skill folders. Their code is not run
during installation. An interrupted download does not publish partial skill links.

The installer refuses to overwrite unrelated folders or links and detects
same-name legacy installations under `$CODEX_HOME/skills`. Re-running keeps
unchanged links and updates only managed links. Old upstream snapshots remain
available; remove unused ones manually after checking no links point to them.

Override discovery or storage locations without editing the script:

```sh
python3 scripts/install-codex-skills.py --dest /path/to/.agents/skills --cache /writable/cache
```

Codex supports symlinked skill folders and local discovery. In CLI/IDE prompts,
use `$review`, `$writing-plans`, etc.; use the skill selector in other surfaces.
If the next turn does not see the new skills, restart Codex.
[Official skill documentation](https://learn.chatgpt.com/docs/build-skills).

## What the profile includes

| Source | Selection |
|---|---|
| This repository | All `skills/` and `forked/` entries; our forks take precedence |
| obra/superpowers | The six README entries plus `executing-plans`, `test-driven-development`, `verification-before-completion`, `receiving-code-review` |
| mattpocock/skills | The seven portable README entries |
| addyosmani/agent-skills | `interview-me`, `context-engineering` |
| DietrichGebert/ponytail | `ponytail-review` and the cheatsheet's `ponytail-audit` |
| blader/humanizer | `humanizer` |

`executing-plans` completes the alternate execution path; TDD and completion
verification are dependencies of `systematic-debugging`; receiving review is the
companion for acting on findings. Other skills mentioned only as related reading
are not automatically pulled in as entire frameworks.

`git-guardrails-claude-code` is excluded from this profile: it configures
Claude's `PreToolUse` hooks and cannot enforce Codex permissions. The existing
Claude installation route still includes it. Lince and VoxCode are host applications,
not skill dependencies; this installer does not install or reconfigure them.

## Adaptations maintained here

- Local skill instructions use actual host capabilities, fresh Codex subagents,
  inherited models, supported question widgets and explicit worktree ownership.
- Cross-skill references resolve by installed name; the SDD final reviewer prompt
  is found inside `requesting-code-review`, not through a nonexistent sibling path.
- Doubt review no longer depends on absent `references/` or persona directories.
  Launching Codex from Codex does not by itself count as cross-model review.
- Existing explicit-only invocation flags are preserved, with matching
  `agents/openai.yaml` policies for Codex. Claude frontmatter extensions remain
  in source; the strict OpenAI validator rejects those extra keys even when the
  required metadata and YAML are valid.
- [`skill-header.md`](compat/codex/skill-header.md) is inserted into selected
  upstream entrypoints. It maps host tool names and skill namespaces. The upstream
  Codex tool reference is replaced by this same adapter so model-tier guidance
  cannot silently override the toolkit's inherit policy. Existing upstream
  explicit-only flags gain Codex metadata when it is missing.
- SDD helpers print paths on stdout and diagnostics on stderr. The scaffold uses
  `git rev-parse --git-path info/exclude`, which also works in linked worktrees,
  and excludes its `AGENTS.local.md` file.

No plugin-wide bootstrap or upstream fork with a duplicate name is enabled.
Updating an upstream requires reviewing its changes and modifying the lock file;
changing the adapter creates a new cache entry. Keep all adaptations in these
tracked files, never by editing the cache.

## Optional companion tools

Choose these per target project. Installing skills alone does not connect MCP
servers or create a backlog/search index.

| Tool | Assessment and setup |
|---|---|
| [Serena](https://github.com/oraios/serena#quick-start) | Useful for Java/symbol navigation. Requires its language backend; follow its current Codex client guide. `navigating-java` already has a CLI fallback. |
| [Backlog.md](https://github.com/MrLesk/Backlog.md#mcp-integration-model-context-protocol) | Useful in projects with an initialized backlog. Can run through CLI or `backlog mcp start`; `writing-prds` also supports Markdown task breakdowns. |
| [qmd](https://github.com/tobi/qmd#quick-start) | Useful for large Markdown collections. Install `@tobilu/qmd`, choose collection roots, then index; semantic search adds local model downloads. A small skill catalog does not need an index. |

For project wiring, Codex reads `.codex/config.toml` in trusted projects.
Merge the relevant server tables into the target project's configuration, keeping
that reproducible configuration in that repository; use `cwd` or a server's
project option for explicit scope. Do not copy Claude's `.mcp.json` verbatim.
[Official MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

## Verification

```sh
python3 scripts/test_codex_install.py
bash -n scripts/wire-machine.sh
git diff --check
```

The tests exercise live links, idempotence, collision preservation, legacy
duplicates, a write-free dry run, scaffold behavior in a linked worktree, and
consumable paths from SDD helpers. They do not replace running a skill on a real
project or verifying an optional MCP connection.
