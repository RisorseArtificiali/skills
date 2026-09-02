#!/usr/bin/env bash
# wire-machine.sh — prepare a machine or a project for the agent toolkit.
#
# Idempotent: safe to re-run. No sudo: everything is user-level or in-repo.
#
# Usage:
#   scripts/wire-machine.sh --check       verify prerequisites and auth
#   scripts/wire-machine.sh --skills      install the skill sets at user level
#   scripts/wire-machine.sh --scaffold    scaffold AGENTS.local.md + .git/info/exclude (inside a repo)
#   scripts/wire-machine.sh --all         check + skills + scaffold
#   scripts/wire-machine.sh --dry-run ... print what would run, change nothing
#
# Environment overrides:
#   AGENT                harness to install for   (default: claude-code)
#   TOOLKIT_REPO         this repo's slug         (default: RisorseArtificiali/skills)
#   SUPERPOWERS_REPO     (default: obra/superpowers)
#   MATTP_SKILLS_REPO    (default: mattpocock/skills)
#   ADDY_SKILLS_REPO     (default: addyosmani/agent-skills)
#   PONYTAIL_REPO        (default: DietrichGebert/ponytail)
#   HUMANIZER_REPO       (default: blader/humanizer)

set -euo pipefail

AGENT="${AGENT:-claude-code}"
TOOLKIT_REPO="${TOOLKIT_REPO:-RisorseArtificiali/skills}"
SUPERPOWERS_REPO="${SUPERPOWERS_REPO:-obra/superpowers}"
MATTP_SKILLS_REPO="${MATTP_SKILLS_REPO:-mattpocock/skills}"
ADDY_SKILLS_REPO="${ADDY_SKILLS_REPO:-addyosmani/agent-skills}"
PONYTAIL_REPO="${PONYTAIL_REPO:-DietrichGebert/ponytail}"
HUMANIZER_REPO="${HUMANIZER_REPO:-blader/humanizer}"

TOOLKIT_SKILLS="adversarial-code-review catch-me-up drink-from-the-firehose issue-triage issue-reply navigating-java plan-walkthrough pr-walkthrough review slides writing-prds grilling handoff subagent-driven-development writing-plans doubt-driven-development"
SUPERPOWERS_SKILLS="brainstorming dispatching-parallel-agents finishing-a-development-branch requesting-code-review systematic-debugging using-git-worktrees"
MATTP_SKILLS="codebase-design diagnosing-bugs domain-modeling grill-with-docs grill-me git-guardrails-claude-code wait-what writing-for-agents"
ADDY_SKILLS="interview-me context-engineering"
PONYTAIL_SKILLS="ponytail-review"
HUMANIZER_SKILLS="humanizer"

DRY_RUN=0
MODES=()

usage() { grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

while [ $# -gt 0 ]; do
  case "$1" in
    --check|--skills|--scaffold|--all) MODES+=("$1"); shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage 0 ;;
    *) echo "unknown option: $1" >&2; usage 1 ;;
  esac
done
[ ${#MODES[@]} -eq 0 ] && usage 1

run() {
  if [ "$DRY_RUN" = 1 ]; then echo "  [dry-run] $*"; else "$@"; fi
}

say() { printf '\n== %s\n' "$*"; }

do_check() {
  say "Prerequisites"
  local missing=0
  for cmd in git gh npx; do
    if command -v "$cmd" >/dev/null 2>&1; then echo "  ok       $cmd"; else echo "  MISSING  $cmd"; missing=1; fi
  done
  # Test what matters — that the API is reachable with the ambient token —
  # rather than `gh auth status`, which fails if any stored account is stale.
  if gh api --silent /user >/dev/null 2>&1; then echo "  ok       gh reaches the GitHub API (ambient auth)"; else echo "  WARN     gh cannot reach the GitHub API — skill installs will fail"; fi
  if [ "$missing" = 1 ]; then echo; echo "Fix the missing tools, then re-run."; exit 1; fi
  say "Harness skills directory (AGENT=$AGENT)"
  local dir="$HOME/.claude/skills"
  if [ -d "$dir" ]; then echo "  ok       $dir ($(ls "$dir" | wc -l) entries)"; else echo "  absent   $dir (created on first install)"; fi
}

do_skills() {
  say "Installing skills at user level (agent: $AGENT)"
  local ok=0 fail=0
  install_one() {
    local repo="$1" skill="$2"
    printf '  %-32s (from %s) ' "$skill" "$repo"
    if [ "$DRY_RUN" = 1 ]; then echo "[dry-run]"; return; fi
    if npx -y skills@latest add "$repo" -g -y --agent "$AGENT" --skill "$skill" >/dev/null 2>&1; then
      echo "ok"; ok=$((ok+1)); else echo "FAILED"; fail=$((fail+1)); fi
  }
  for s in $TOOLKIT_SKILLS;    do install_one "$TOOLKIT_REPO"     "$s"; done
  for s in $SUPERPOWERS_SKILLS; do install_one "$SUPERPOWERS_REPO"  "$s"; done
  for s in $MATTP_SKILLS;       do install_one "$MATTP_SKILLS_REPO" "$s"; done
  for s in $ADDY_SKILLS;        do install_one "$ADDY_SKILLS_REPO"  "$s"; done
  for s in $PONYTAIL_SKILLS;    do install_one "$PONYTAIL_REPO"     "$s"; done
  for s in $HUMANIZER_SKILLS;   do install_one "$HUMANIZER_REPO"    "$s"; done
  say "Done: $ok installed, $fail failed"
  [ "$fail" -eq 0 ] || exit 1
}

do_scaffold() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "run --scaffold inside a repository" >&2; exit 1; }
  say "AGENTS.local.md (untracked machine notes)"
  if [ -f AGENTS.local.md ]; then
    echo "  ok       already present — left untouched"
  elif [ "$DRY_RUN" = 1 ]; then
    echo "  [dry-run] would create AGENTS.local.md from the template"
  else
    run tee AGENTS.local.md >/dev/null <<'TEMPLATE'
# AGENTS.local.md — machine-specific notes (untracked)

Notes that are true on this dev box only. Referenced from AGENTS.md; never commit
this file. Worktrees do not inherit untracked files: symlink it from a worktree
(`ln -s ../../../AGENTS.local.md AGENTS.local.md` under `.claude/worktrees/...`).

## Toolchain
- Installed toolchains and versions; what is read-only or missing (and "do not try to install it").

## Sandbox / filesystem
- Read-only paths; writable paths; what is ephemeral between sessions or reboots.

## Git / GitHub
- How credentials reach git and gh on this box (helper, env vars, explicit refspecs).

## Feature workflow
- Point to the pipeline your project follows (skills installed on this box).
TEMPLATE
    echo "  created  AGENTS.local.md — fill it in, and reference it from AGENTS.md"
  fi
  say ".git/info/exclude (machine-local, never committed)"
  for entry in .reviews/ .serena/ .qmd/; do
    if grep -qxF "$entry" .git/info/exclude 2>/dev/null; then
      echo "  ok       $entry already excluded"
    elif [ "$DRY_RUN" = 1 ]; then
      echo "  [dry-run] would exclude $entry"
    else
      echo "$entry" >> .git/info/exclude
      echo "  excluded $entry"
    fi
  done
  say "Remaining by hand (project-specific)"
  cat <<'NOTES'
  - Register MCP servers workspace-scoped, in-repo (.mcp.json and your other
    agents' equivalents); start servers with an explicit project flag.
  - Replicate the pipeline section of your agents file for this repo.
NOTES
}

for mode in "${MODES[@]}"; do
  case "$mode" in
    --check)    do_check ;;
    --skills)   do_skills ;;
    --scaffold) do_scaffold ;;
    --all)      do_check; do_skills; do_scaffold ;;
  esac
done
