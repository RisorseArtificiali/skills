---
name: review
description: Quick leveled code review of the current diff, a branch, a PR number, or specific paths — correctness bugs first, plus reuse/simplification/efficiency cleanups. Findings are verified before being reported and ranked most-severe first. Use whenever the user says "review", "review this", "check my diff", "look over this change", "review PR N", or after finishing a piece of work and wanting a fast second opinion. Levels: low/medium (few, high-confidence findings) and high (broader coverage). Lighter than adversarial-code-review — use this on demand and mid-work; use adversarial-code-review as the pre-merge gate.
---

# Review

## Overview

An on-demand review with one promise: **every finding reported has survived verification**. A review's value is not how many findings it produces — it is that each one is worth the author's time. Plausible-but-wrong findings cost an investigation each; unranked lists bury the one critical bug under nine nitpicks. So: verify, rank, and let "no findings" be a real answer.

This is the everyday tool. It has no worktree, no reviewer panel, no fix loop — for the full pre-merge gate, use `adversarial-code-review`.

## Loading Constraints

Orchestrator only. Reviewer subagents receive the verbatim prompt below, never this skill.

## Target Resolution

In order, when no target is given:

1. Uncommitted changes exist → review them (`git diff HEAD --stat`; include untracked files that belong to the change).
2. Otherwise → the branch: `git merge-base HEAD <main>`…`HEAD`.

Explicit targets: a PR number (`gh pr view N` for description, `gh pr diff N`), a branch, a commit range, or paths. For PRs, the description joins the context handed to the reviewer.

Keep only the `--stat` and the contract in your own context — reviewers read the code themselves. If you catch yourself reading the changed files "to get oriented", stop: you are about to become the context-sharing reviewer this skill exists to avoid.

## Levels

Default is **medium**; reuse the level the user last asked for; honor an explicit one.

| Level | Reviewers | Verification | Report |
|---|---|---|---|
| **low / medium** | 1 fresh reviewer | orchestrator re-reads every cited site; findings needing execution to confirm are dropped unless trivially checkable | few findings, high confidence only |
| **high** | 2 reviewers: correctness lens + quality lens (reuse/simplification/efficiency) | one skeptic subagent per finding; reproduce (run the test, trigger the path, run the count) where a command can do it | broader; unreproduced findings included but labeled PLAUSIBLE |

## Process

### 1. Dispatch

Send each reviewer this prompt — fill placeholders, change nothing else. At low/medium the single reviewer covers both correctness and quality; at high, give each reviewer only its lens line.

```
Fresh-context code review — {LENS: correctness bugs | reuse, simplification
and efficiency cleanups}. You know nothing about this change except what is
below. The author is not in the room; do not soften findings for them.

REPO: {path}. Read the change with: {git diff command}. Read surrounding
files whenever the diff alone is not enough to be sure.

CONTEXT (what the change is for):
{contract / PR description / user's one-line description}

Rules:
- Report only findings you would stake a review comment on. When unsure at
  this effort level ({level}), drop it — a missed nitpick costs nothing, a
  false finding costs an investigation.
- Every finding needs a concrete failure scenario (correctness) or a concrete
  before/after benefit (quality). "Could be cleaner" is not a finding.
- Verify every file:line anchor against the actual file before reporting.
- No style commentary unless it hides a bug.
- Finding nothing is a valid result: return exactly "No findings." if so.

Format each finding as:
- FILE:LINE | SEVERITY(critical/major/minor) | CLAIM (one sentence)
  WHY: failure scenario or concrete benefit
  EVIDENCE: what you read or ran
```

### 2. Verify

No finding reaches the user unverified — this step is the product:

- **All levels:** re-read the cited site yourself. Stale anchor, misquoted code, or a guard the reviewer missed upstream → the finding dies. Note the kill count; don't report the corpses individually.
- **High:** dispatch a skeptic per surviving finding (parallel, one message) with the verifier prompt from `adversarial-code-review` Step 4 — refute or reproduce. CONFIRMED needs a command and its output; what can't be executed stays PLAUSIBLE with the reason stated.
- Never assert a number (occurrences, affected call sites) without running the count, and never assert a cause without reproducing it — if a claimed fix wouldn't change observable behavior, the diagnosis is wrong, not the observation.

### 3. Report

Ranked most-severe first, in the final message:

```
Review of <target> (<level>):

1. [critical] file:line — claim.
   Why: failure scenario. (Confirmed: command + result / Plausible: reason)
2. [major] ...
...
(N candidate findings dropped in verification.)
```

- One finding, one numbered entry — claim first, mechanism after.
- If nothing survives: say so plainly, with what was covered. Do not invent minor findings to justify the run.
- If the diff was too large to cover fully, say what was skipped — a silent partial review reads as a clean bill.

## Options

- **`--fix`** — after reporting: apply the confirmed findings to the working tree, smallest change that resolves each, then re-run the tests covering the touched code. Report what was fixed vs. skipped and why. Do not commit unless asked.
- **`--comment`** (PR targets) — draft the inline comments, show the user the exact text, and post only after their approval. Never post review content to any external surface without the text being approved first.

## Escalation

Recommend `adversarial-code-review` instead of running this skill when: the branch is about to merge, the change touches auth/data-migration/concurrency/public API, or a high-level review keeps producing confirmed findings — repeated findings are information about the branch, and the gate exists for exactly that.

## Interaction with Other Skills

- **`adversarial-code-review`** — the heavyweight gate: worktree, lens panel, mandatory reproduction, fix loop. This skill is its everyday sibling; same finding format, so escalation loses nothing.
- **`requesting-code-review`** — the between-tasks habit inside subagent-driven-development; keep using it there. This skill is the on-demand, leveled entry point.
- **`doubt-driven-development`** — in-flight doubt on decisions while working; this skill reviews finished diffs.

## Verification

- [ ] Reviewer was a fresh subagent with the verbatim prompt — never an inline read by the orchestrator
- [ ] Every reported finding was re-verified at its anchor; kills were counted, not reported
- [ ] At high level, CONFIRMED findings carry a reproduction; the rest are labeled PLAUSIBLE
- [ ] Findings ranked most-severe first; "no findings" stated plainly when true
- [ ] Partial coverage was disclosed
- [ ] Nothing posted to a PR without the exact text approved; nothing committed without being asked
