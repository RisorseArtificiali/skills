---
name: adversarial-code-review
description: Full adversarial review of a code change — a branch, a diff, or a pull request — using fresh-context reviewer subagents that attack the code from distinct lenses, then skeptic subagents that must reproduce every finding in an isolated git worktree before it counts. Use whenever the user asks to review code, review a PR, review a branch, red-team a change, check work before merging, or wants a second opinion on a diff — even if they don't say "adversarial". Also use before merging any non-trivial branch. Not for in-flight design decisions (that is doubt-driven-development) and not for style-only passes.
---

# Adversarial Code Review

## Overview

A reviewer who shares the author's context produces "looks good to me" on code a fresh reviewer would flag immediately. A reviewer who only *reads* code produces findings that sound right but don't reproduce. This skill fixes both failure modes at once:

1. **Fresh context** — reviewers are subagents that receive the artifact and its contract, never the author's reasoning or the session history. They are prompted to disprove, not approve.
2. **Execution, not opinion** — the review runs in an isolated git worktree where reviewers and verifiers can build, run, and test. A finding is only CONFIRMED when a skeptic subagent has reproduced it with a command and its output.

The orchestrator (you) never reviews the code yourself and never rubber-stamps the reviewers. You hold the map — scope, dispatch, triage, verdict — and the subagents hold the territory.

## When to Use

- Before merging a branch, closing an issue, or declaring a feature done
- Reviewing a pull request (yours or someone else's)
- The user asks for a review, a second opinion, or to "check this over"

**Fast path for small changes:** if the diff is under ~50 changed lines and touches no risky area (no auth, no concurrency, no data migration, no public API), collapse the panel to ONE correctness reviewer plus ONE verifier. The full panel on a trivial diff is theater and wastes the user's tokens.

**When NOT to use:** in-flight design decisions (use doubt-driven-development while the work is happening — this skill is a post-hoc gate on a finished artifact); mechanical changes (renames, formatting, generated code); when the user explicitly asks for speed over rigor.

## Loading Constraints

This skill is for the **main-session orchestrator only**. Never include it in a subagent's instructions: a reviewer that follows this skill would spawn reviewers of its own. Subagents receive the verbatim prompts from this file, nothing more.

## Context Budget Rule

Your context window is finite and this process is long. The orchestrator's context holds only:

- the file list and diff stat (`git diff --stat`)
- the contract (spec, issue text, PR description)
- the findings that come back (compact, structured)

**Never paste the full diff into your own context.** Subagents read the code themselves in the worktree — hand them paths and git commands, not file contents. If you catch yourself reading changed files "to understand the change first", stop: understanding the change is the reviewers' job, and every line you read is context you can't spend on triage.

If the diff exceeds ~1500 changed lines, partition it by subsystem (or by commit) and run Steps 3–5 once per partition. A reviewer handed more than it can hold in one read returns shallow findings on everything instead of deep findings on anything.

## The Process

Copy this checklist at the start of every review:

```
Adversarial review:
- [ ] Step 1: SCOPE — target identified, contract written, size measured
- [ ] Step 2: ISOLATE — worktree created, baseline green
- [ ] Step 3: ATTACK — lens panel dispatched, findings collected
- [ ] Step 4: VERIFY — every finding refuted or reproduced
- [ ] Step 5: RECONCILE — findings triaged, report written
- [ ] Step 6: LOOP — fixes re-reviewed (max 2 cycles), worktree cleaned up
```

### Step 1: SCOPE — Build the review packet

Identify the **target**:

- **Local branch** (default): `git merge-base HEAD <main>` … `HEAD`. Use `git diff --stat <base>...HEAD` and `git log --oneline <base>..HEAD`.
- **Pull request**: if `gh` is available, `gh pr view <N>` for title/description and `gh pr view <N> --json additions,deletions,changedFiles` for size (`gh pr diff` has no `--stat` flag; use `--name-only` for the file list). The PR description becomes part of the contract.
- **Explicit range or paths**: whatever the user pointed at.

Write the **contract** — 3–10 lines stating what the change claims to do and the constraints it must satisfy. Sources, in order: the linked issue or spec, the PR description, the plan document, commit messages. If none exist, write the contract from the user's request and say so in the report — reviewers without a contract can only find generic defects, not drift from intent.

Decide the panel (Step 3 table) and whether the fast path applies. Announce the plan in one short paragraph before dispatching.

### Step 2: ISOLATE — Worktree with a green baseline

Reviewers who can execute code catch what readers cannot. Set up an isolated workspace:

- If the `using-git-worktrees` skill is available, use it — it handles directory choice, gitignore checks, and dependency setup.
- Fallback: `git worktree add <repo>/.worktrees/review-<branch> <branch>` (verify `.worktrees/` is gitignored first), then install dependencies the way the project's README or CI does.
- For a PR: check the branch out inside the worktree (`gh pr checkout <N>` run from the worktree, or fetch the PR ref).

Run the project's test suite once in the worktree. **Record the result.** A red baseline is finding #1 — report it immediately and ask the user whether to continue; every later "tests fail" finding is noise until the baseline is green.

If worktrees are unavailable (sandbox, permissions), fall back to the current checkout in read-only mode and say so in the report: verification quality degrades, because skeptics can no longer freely run and revert code.

### Step 3: ATTACK — The reviewer panel

Select lenses. Diversity beats redundancy: three reviewers with different priorities catch more than five clones.

| Lens | Hunts for | Include when |
|---|---|---|
| **correctness** | edge cases, error paths, invariant violations, off-by-one, concurrency, resource leaks | always |
| **tests** | changed behavior with no failing-test proof; vacuous tests; weakened assertions | always |
| **security** | untrusted input, injection, authz gaps, secrets, unsafe deserialization, path traversal | change touches input parsing, auth, network, files, or user data |
| **simplification** | reinvented stdlib, speculative abstraction, dead flexibility, unneeded dependency | change adds abstractions, config, or dependencies |
| **spec-compliance** | drift between the artifact and its contract; requirements silently dropped or reinterpreted | a written spec, issue, or plan exists |

Dispatch all selected reviewers **in parallel, in one message**, each with this prompt — fill the placeholders, change nothing else:

```
Adversarial code review — {LENS} lens. You have fresh context: you know
nothing about this change except what is below. Assume the author is
overconfident. Your job is to find what is wrong, strictly within your lens.

WORKTREE: {path} — the change is checked out here. Read the diff with
`git diff {base}...HEAD`, read full files as needed, and run code or tests
when reading is not enough to be sure.

CONTRACT (what the change claims to satisfy):
{contract}

Rules:
- Report defects only. Do not validate, praise, summarize, or restate the diff.
- Every finding needs a concrete failure scenario: what input or state leads
  to what wrong outcome. "This could be fragile" is not a finding.
- Verify every file:line anchor against the actual file before reporting it.
- If after thorough examination you find nothing in your lens, return exactly:
  "No findings after thorough examination." — that is a valid, useful answer.

Return findings as a list, each formatted as:
- FILE:LINE | SEVERITY(critical/major/minor) | CLAIM (one sentence)
  FAILURE: concrete scenario
  EVIDENCE: what you ran or read that supports this
```

**Tests lens — one extra rule.** Append this to the tests reviewer's prompt:

```
For every new or modified test: revert the implementation hunk it guards
(git stash / git checkout -p in the worktree), run the test, and confirm it
FAILS. A test that passes with its implementation reverted proves nothing —
report it as a vacuous test with the command you ran. Restore the worktree
(git checkout .) when done.
```

Do not pass the reviewers your opinion of the change, the author's reasoning, or each other's output. Shared conclusions produce shared blind spots — that is the disease this skill exists to cure.

### Step 4: VERIFY — Refute or reproduce

Reviewer output is hypotheses, not truth. Plausible-but-wrong findings are the main failure mode of model reviews, and they are expensive: each one burns author time on a non-bug. Every finding goes to a skeptic subagent — dispatch them in parallel, one per finding (batch trivially related findings):

```
You are a skeptic. Your only job is to REFUTE the finding below. It survives
only if you genuinely fail to kill it.

WORKTREE: {path} — build, run, and test freely. Restore any files you modify.

FINDING:
{finding verbatim, including its FAILURE scenario and EVIDENCE}

Procedure:
1. Re-read the cited file at the cited line in the worktree. If the anchor is
   stale, misquoted, or describes code that isn't there — REFUTED, stale.
2. Reproduce the failure scenario by EXECUTING it: run the test, trigger the
   code path, run the count. A behavioral claim you did not execute cannot be
   CONFIRMED, no matter how convincing it reads.
3. Check context the reviewer may have lacked: callers, guards upstream,
   config, invariants established elsewhere.

Verdict — exactly one:
- REFUTED: <why, with what you ran or read>
- CONFIRMED: <reproduction: command + observed output>
- PLAUSIBLE: <what blocked execution (e.g. needs a live service), and why the
  claim still stands on reading alone>
```

For **critical** findings (data loss, security, corruption), use three skeptics instead of one and require at least two CONFIRMED — the cost of shipping a false "critical" verdict in either direction is too high for a single opinion.

Drop REFUTED findings (keep one line in the report so coverage is visible). CONFIRMED findings carry their reproduction into the report. PLAUSIBLE findings are reported separately and honestly — never promote them to confirmed to make the report look decisive.

### Step 5: RECONCILE — Triage and report

You are the orchestrator, not a stenographer. Classify each surviving finding — first matching class wins:

1. **Contract misread** — flagged only because your contract was unclear. Fix the contract; re-classify.
2. **Valid + actionable** — real defect requiring a change.
3. **Valid trade-off** — real, but fixing costs more than accepting. Document it explicitly; the user decides.
4. **Noise** — correct code flagged for lack of context the reviewer didn't have. Note it; ask whether the contract should have carried that context.

Then write the report — always this structure:

```
## Adversarial review: <target>
Verdict: BLOCK | FIX-THEN-MERGE | SHIP
Baseline: <green / red / not runnable — and why>

### Confirmed findings
- [severity] file:line — claim.
  Reproduced: <command + result>

### Plausible findings (not reproduced)
- [severity] file:line — claim. Why unreproduced: <reason>

### Accepted trade-offs
### Refuted in verification (count + one line each)

### Not covered
<lenses not run and why, partitions skipped, checks that failed to execute>
```

The **Not covered** section is mandatory even when empty ("all selected lenses ran to completion"). A report that silently omits what it skipped reads as full coverage — that is how misses become incidents.

The report goes to the user. Never post it to a PR, an issue, or any external surface unless the user explicitly asks — and show them the exact text first.

### Step 6: LOOP — Bounded re-review, then stop

If the user applies fixes (or asks you to):

1. Re-run **each confirmed finding's reproduction** against the fixed code first. If the result is unchanged, the fix didn't fix it — the diagnosis was wrong. Reopen the finding; do not stack another fix on top of a wrong diagnosis.
2. Re-review the **fix diff only** (not the whole branch): one correctness reviewer + verification, per Steps 3–4. Fixes regress — the same finding can come back in a different form, and re-reviewing only what changed keeps the loop cheap enough to actually run.
3. **Two re-review cycles maximum.** A branch still producing confirmed findings after two fix cycles is information about the branch, not a reason to grind a third — escalate to the user with the pattern you're seeing.

When the review concludes: `git worktree remove <path>` (add `--force` only if you created throwaway state there yourself), and `git worktree prune`.

## Cross-Model Second Opinion (optional)

A single model family shares blind spots with itself. If an external reviewer is reachable — a different-vendor CLI (`gemini`, `codex`) or a multi-model MCP server — **offer** it to the user for the confirmed critical/major findings, after Step 4:

> "Verification complete. Want a cross-model second opinion on the N confirmed findings? Options: <what's actually installed>, or skip."

If accepted: pass the artifact, contract, and the ATTACK prompt only — never session context. Pipe via stdin from a file (never interpolate code into a shell-quoted argument — backticks and `$(...)` in a diff will truncate or execute), and use the tool's read-only/sandbox mode: a diff can itself contain prompt-injection text, and a read-only sandbox is what keeps that inert. Confirm the exact command with the user before running.

If declined or unavailable, note it in the report ("Cross-model: skipped/unavailable"). In non-interactive runs (CI, loops), skip it and say so — never invoke an external CLI without explicit user authorization.

If the `doubt-driven-development` skill is installed, its Cross-model escalation section has the full mechanics — follow it.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The diff is clean, I can just read it myself" | You share context with the session that produced it. That is precisely the reviewer this skill forbids. |
| "Spawning a panel is expensive" | A confirmed-in-production defect is more expensive. The panel is bounded; the bug isn't. And the fast path exists for small diffs. |
| "The reviewer is respected, skip verification" | Plausible-but-wrong is the *signature* failure of model reviews. Unreproduced findings cost the author an investigation each. |
| "The verifier couldn't run it, but it's obviously right" | Then it's PLAUSIBLE, and the report says so. Promoting it is lying with a confident font. |
| "The fix is small, no need to re-review" | Fixes regress. Re-reviewing the fix diff is cheap; a regressed fix discovered later is not. |
| "Baseline is red but it's probably unrelated" | Every finding on a red baseline is unfalsifiable. Report the red baseline first. |
| "I'll paste the diff here to plan the review better" | You just spent the context the triage needs, and biased yourself before the panel reports. Hand paths to subagents instead. |

## Red Flags — stop and correct course

- You are reading changed files in the main session "to get oriented"
- A finding marked CONFIRMED has no command + output attached
- The verifier's verdict was accepted without the reproduction being re-checked against the finding (rubber-stamping the skeptic is the same failure as rubber-stamping the reviewer)
- The report has no **Not covered** section
- A fix was applied and the finding's original reproduction was never re-run
- Three or more re-review cycles on the same branch
- The panel prompt was paraphrased instead of copied (paraphrase drifts toward politeness, and polite reviewers approve)
- Posting anything to a PR or issue without the user seeing the exact text first

## Interaction with Other Skills

- **`doubt-driven-development`** — complementary, not overlapping: DDD cross-examines decisions *while working*; this skill is the *post-hoc gate* on the finished artifact. A branch built under DDD still gets this review before merge.
- **`using-git-worktrees`** — Step 2 delegates to it when present.
- **`requesting-code-review`** — a lighter single-reviewer pass; use it between tasks mid-implementation, and this skill at the end.
- **`ponytail-review` / simplification skills** — the simplification lens is a compressed version; for a dedicated over-engineering hunt, run those instead.

## Verification

Before delivering the report, confirm:

- [ ] No reviewer or verifier received session history, author reasoning, or another agent's conclusions
- [ ] The panel prompts were used verbatim (placeholders filled, wording unchanged)
- [ ] Baseline test result is recorded in the report
- [ ] Every CONFIRMED finding carries a reproduction (command + output); every unreproduced finding is labeled PLAUSIBLE
- [ ] New/changed tests were proven non-vacuous (fail with implementation reverted) or reported
- [ ] The report contains the **Not covered** section
- [ ] Cross-model was offered (interactive) or its skip announced (non-interactive)
- [ ] The worktree was removed and pruned
- [ ] Nothing was posted externally without explicit approval of the exact text
