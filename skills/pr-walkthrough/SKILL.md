---
name: pr-walkthrough
description: Logical review of a pull request or branch with the human reviewer in the loop — what the change does to the project's architecture, impacts and dependencies, user experience, operations, documentation and test story — as a visual dossier (Mermaid map) followed by an interactive step-by-step walkthrough with closed-menu questions and finding triage. Use whenever the user wants to understand or review a PR above the code level: "walk me through this PR", "logical review", "what does this PR really change", "help me review PR N", or when they must review a change too large or unfamiliar to grasp by reading the diff. Not for line-level code review (that is review / adversarial-code-review).
---

# PR Walkthrough

## Overview

A diff shows edits; a reviewer needs to understand *what the change does to the project*. This skill is the analyst at the reviewer's side: it builds a visual map of the pull request's logical content, then walks the reviewer through it in small, concentrated sections — raising doubts, asking closed questions, and triaging findings together. The human is the reviewer and makes every judgment; the skill prepares evidence, keeps the altitude high, and records the outcomes in a dossier that survives the session.

This is explicitly NOT code review. Line-level correctness, style, and test quality belong to `review` and `adversarial-code-review`. When a code-level issue surfaces here anyway, park it in one line in the dossier's "parked for code review" list and move on — chasing it would pull the walkthrough down from the altitude that is its whole point.

## The Seven Dimensions

| # | Dimension | The question it answers |
|---|---|---|
| 1 | **Intent** | Does the PR do what its issue/description promise — and only that? Scope creep; silent reinterpretation; drift from normative sources (ADRs, PRD, use cases) where they exist. |
| 2 | **Architecture** | What changes structurally: modules, boundaries, new/removed dependency edges, patterns broken or introduced. |
| 3 | **Impacts & dependencies** | Blast radius: what else is affected, which contracts/API surfaces change, what breaks for consumers. |
| 4 | **User experience** | How usage changes: commands, flags, config, output, workflows, defaults. |
| 5 | **Operational impact** | What happens to whoever deploys: migrations, new/changed config, upgrade compatibility, rollback. |
| 6 | **Documentation drift** | Which docs the PR updated — and which docs it *should* have updated and didn't. |
| 7 | **Test story** | Not test quality: does every claimed behavior change have coverage somewhere? Do the tests tell the same story as the PR description? |

## Interaction Style (load-bearing)

- **Closed questions with menus wherever possible.** Use the harness's question widget (e.g. AskUserQuestion) when available; otherwise plain-text lettered options (A/B/C…) with a recommended default marked. Open questions only where options genuinely can't be enumerated.
- **One step at a time.** Never answer your own questions; never continue past a question without the user's reply.
- **Small sections.** At most ~15 lines of concentrated text before the next interaction. If a section wants to be longer, it is two sections.
- **Language:** the conversation and the live dossier follow the session language. The English version of the dossier is produced at consolidation (Step 4).

## Step 0 — Target and Setup

- **Target:** a PR number (`gh pr view N --comments` for description + discussion; for size `gh pr view N --json additions,deletions,changedFiles` and `gh pr diff N --name-only` for the file list — `gh pr diff` has no `--stat` flag) or a local branch (`git merge-base HEAD <main>`…`HEAD`). The PR description, linked issues, and unresolved review threads form the **declared intent**.
- **Dossier home:** `<repo>/.reviews/prs/` (shared home with `plan-walkthrough`, which uses `.reviews/plans/`). Create it if missing and ensure `.reviews/` is listed in `.git/info/exclude` (never touch `.gitignore` — the dossier is personal, the repo is shared). File name: `PR-<n>.md` or `<branch-slug>.md`.
- **Resume:** if a dossier for this target already exists, offer via closed question: resume from it (re-scan only what the new commits touched) or start fresh.
- **Normative sources:** locate the project's yardsticks — AGENTS.md/CLAUDE.md and what they point to (ADRs, PRD, use cases, design docs, user guides). These are what Intent and Architecture drift are measured *against*. If none exist, the declared intent is the only yardstick; say so in the dossier.

**Context budget rule (orchestrator):** you read PR metadata, `--stat`, the linked issue, and the normative index — never the full diff. Subagents read code and return compact notes. The dossier file is your working state: if the session dies, the next one resumes from it.

## Step 1 — Light Scan (parallel subagents)

Dispatch three scan subagents **in parallel, in one message** — (a) intent + architecture, (b) impacts + UX + operational, (c) docs + tests. Fill the placeholders; keep the prompt otherwise verbatim:

```
Light logical scan of a change — dimensions: {DIMENSIONS}. Fresh context:
you know only what is below. You are scanning for a REVIEWER's overview,
not doing code review: stay at the level of what the change does to the
project, not how lines are written.

REPO: {path}. Change: {git/gh diff command}. Read the diff and only the
surrounding files needed to classify it. Do not deep-dive.

DECLARED INTENT: {PR description / issue summary}
NORMATIVE SOURCES (yardsticks for drift): {list of docs, or "none"}

Return, compactly:
1. LOGICAL CHANGES: the 3–8 logical changes this diff contains (not files —
   changes a reviewer would name), each: short name | what it does | files
   involved | weight (S/M/L).
2. Per dimension in {DIMENSIONS}: STATUS green|yellow|red | one-line reason |
   POINTERS: files/symbols worth a later deep dive | DOUBTS: anything you
   could not determine at scan depth.
Green = nothing a reviewer must look at. Yellow = worth a look. Red = must
be discussed. Be honest about scan depth: an unexamined area is a DOUBT,
not a green.
```

Merge the three inventories into one (dedupe; 3–8 entries total). Conflicting statuses for the same dimension: keep the worst.

## Step 2 — The Map

Write the dossier's first half, in this order, then present it:

1. **Header** — PR facts, declared intent (2–3 lines), size, date, commit range scanned.
2. **Logical-change inventory** — the merged 3–8 entries. This is the backbone: everything else references these by name.
3. **Architecture before/after** — one Mermaid `flowchart LR` of the *touched subgraph only*: solid = unchanged, green = added, red dashed = removed, thick = modified. Label the edges. If the PR changes no structure, one line saying so beats an empty diagram.
4. **Impact map** — Mermaid `mindmap` (or flowchart): the PR at the center, radiating to affected surfaces (consumers, UX surfaces, ops concerns, docs). The blast radius at a glance.
5. **Traffic light** — the 7 dimensions: 🟢/🟡/🔴 | one-line summary | link to its walkthrough section (filled as sections complete).

Mermaid discipline: relevant subgraph only, never the whole system; every node a real module/component name from the repo; `classDef added`/`removed` for the before/after coloring.

**If artifact publishing is available** (Claude Code): publish the dossier as an artifact too — markdown renders Mermaid natively — and hand over the link. The file remains the source of truth; republish after consolidation.

Present the map with ≤10 lines of narration, then a closed question: **walkthrough mode** — recommend *by dimension* when the inventory has ≤4 entries, *by logical change* above that; the user can override, drop dimensions, or stop at the map (the map alone is a valid deliverable).

## Step 3 — The Walkthrough

**Mode A — by dimension:** one section per non-green dimension, reds first, then yellows. Greens are dismissed in one line each at the end (visible, so a wrong green can be challenged).

**Mode B — by logical change:** one section per inventory entry, examined across the dimensions it touches; close with a per-dimension rollup revisiting the traffic light.

Section contract (both modes):

1. **Zoom just-in-time.** Dispatch one zoom subagent with the scan's POINTERS and DOUBTS for this section (prompt below). Small, already-clear sections may skip the zoom — say so.
2. **The concentrated text** (≤15 lines): what this section shows, in plain reviewer language, citing files/symbols by name — never pasting diff hunks unless a single hunk *is* the point.
3. **The findings ("pulci"),** one closed question each, always the same triage menu:
   - **Real problem** → goes on the author list (as a question or change request)
   - **Accepted trade-off** → recorded with its rationale
   - **False alarm** → dropped, one-line note of why
   - **Deep-dive now** → zoom further, present, re-triage
4. **Comprehension doubts count as findings.** Where the PR is ambiguous ("the description says X, the code seems to do Y"), ask the user via menu how to read it — and if the answer is "unclear", that *is* an author question. The walkthrough exists to make the reviewer understand, not only to critique.
5. **Navigation close** (closed question): next section / jump to `<list>` / zoom on something in this one / stop and consolidate.
6. **Update the dossier** after every section: section text, triage outcomes, traffic-light row. The dossier is always current — never batch the writing to the end.

Zoom subagent prompt:

```
Deep dive for a logical PR review — section: {SECTION}. Fresh context.
REPO: {path}. Change: {diff command}. Start from POINTERS: {pointers};
address DOUBTS: {doubts}. Stay at reviewer altitude: what this means for
the project, not line-level correctness.
Return ≤30 lines: the mechanism as it actually is (read the code, don't
guess), what confirms or kills each doubt, and any NEW doubt a reviewer
should raise with the author. Cite file:symbol for every claim.
```

## Step 4 — Consolidation

When the walkthrough ends (or the user stops early — consolidate what exists and mark the rest "not walked"):

1. Finish the dossier: **verdict** (approve / request changes / needs discussion — the *user* picks it from a closed question, the skill proposes), per-dimension one-liners (final traffic light), **author questions** (real problems + unclear items, phrased as questions where possible — questions land better than verdicts), **accepted trade-offs** with rationales, **doc-drift list** (updated vs missing, each missing item naming the doc that should change), **parked for code review**, **not covered**.
2. **English version:** write `<name>.en.md` next to the live dossier — full translation, same structure. If the session language is English, the single file already is it.
3. Offer via closed question: **draft the GitHub comment?** If yes: compose in English from the author questions + real problems, show the exact text, and post with `gh pr comment` only after the user approves that exact text. Never post anything otherwise; approving the draft concept is not approving the text.

## Red Flags — stop and correct course

- The orchestrator is reading the full diff "for context" — that is the scanners' job
- A section ran past ~15 lines of prose, or answered its own triage question
- Code-level findings being debated instead of parked
- The traffic light says green for a dimension no scanner actually examined (scan honesty rule)
- The dossier lags behind the walkthrough (it must be current after every section)
- The map skipped because "the PR is small" — a small PR gets a small map, not no map
- A comment posted, or any text shown to the author, without the user approving the exact wording
- The walkthrough marching on past a question the user hasn't answered

## Interaction with Other Skills

- **`review` / `adversarial-code-review`** — the code-level siblings. The "parked for code review" list is their input; run them separately (typically after the walkthrough, before merge).
- **`navigating-java`** (and structural-navigation tooling generally) — how scan and zoom subagents should gather evidence in Java repos: symbol queries, not grep.
- **`grilling` / `brainstorming`** — the interaction pattern this skill replicates on a PR: one focused step at a time, closed questions, the human owns every decision.

## Verification

- [ ] Dossier exists in `.reviews/prs/` (excluded via `.git/info/exclude`), map before walkthrough, current after every section
- [ ] Traffic light reflects only what was actually examined; unexamined = doubt, never green
- [ ] Every finding was triaged by the user through the menu — none resolved unilaterally
- [ ] Code-level findings were parked, not debated
- [ ] Walkthrough mode was proposed and confirmed; every section ended with navigation
- [ ] English dossier version produced at consolidation
- [ ] Any author-facing text was approved verbatim by the user before posting
