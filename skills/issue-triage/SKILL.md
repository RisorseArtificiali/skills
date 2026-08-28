---
name: issue-triage
description: Fast interactive triage of a repository's GitHub issues — sweep what is new, changed, or newly commented since the last check, then walk issue by issue with a brief summary, what changed, and a proposed urgency, letting the user tag on GitHub or mark for deep dive. Keeps a rolling state document with the last-check date so each run picks up where the previous one left off. Use when the user says "triage the issues", "what's new in the issues", "giro sulle issue", "catch me up on the backlog", or returns to a repo after time away. Understanding content and urgency only — never assigning, closing, or commenting on issues.
---

# Issue Triage

## Overview

The radar of the pipeline: a fast pass over the repository's issues to know *what exists, what moved, and what burns* — so the expensive tools (`plan-walkthrough`, the PRD pipeline) get pointed at the right targets. Speed is the point: brief summaries, closed-menu decisions, a rolling state file. The skill proposes urgency; the user disposes. Assigning, closing, and commenting are explicitly out of scope.

Interaction style is the house grammar: closed menu questions wherever possible (harness widget or lettered A/B/C fallback), one issue at a time, never advancing past an unanswered question, session language throughout (the state doc included — it is operational state, not an author-facing deliverable).

## The State Document

`<repo>/.reviews/triage/issues.md` (ensure `.reviews/` is in `.git/info/exclude`, never `.gitignore`). Rolling, single file:

```markdown
# Issue triage — <repo>
Last check: <ISO timestamp of the last sweep's START>

## Needs deep dive
- #N <title> — <one-line why> (added <date>)

## Notes
- #N: <persistent note> (<date>)

## Last run
<the final queue table of the most recent run, with outcomes>
```

The `Last check` timestamp is the **start** of the sweep, not its end — activity that lands while you triage must surface next time, not fall between runs.

## Step 1 — Time Reference and Sweep

1. Read the state doc. If it exists, propose via closed question: since last check (default) / custom date / full sweep of all open issues. First run: ask for the reference date (offer: last 7 days / 30 days / all open).
2. Sweep with `gh` (current repo; honor an explicit `-R owner/repo`):
   - `gh issue list --state open --search "updated:>=<date>" --json number,title,createdAt,updatedAt,labels,author,url --limit 200`
   - Classify each hit: **new** (`createdAt` ≥ reference date) vs **changed** (updated since — comments bump `updatedAt`; if it bumped with no new comments, say "edited/relabeled").
3. Build the queue: for each issue a one-liner and a **proposed urgency** (alta/media/bassa) with a one-word reason — signals: security/data-loss/regression language, "blocks #N" references, milestone proximity, maintainer involvement, long-stale-suddenly-active. More than ~15 issues: delegate the one-liners to a scan subagent and keep only the table in the orchestrator; fewer: inline.

Present the queue table — number | title | new/changed | proposed urgency | one line — sorted by proposed urgency, then recency. Closed question: start the cycle / reorder / drop some / stop here (the table alone is a valid outcome; update the state doc anyway).

## Step 2 — The Cycle, Issue by Issue

For each issue, fetch detail just-in-time (`gh issue view N --comments`) and present ≤10 lines:

1. **What it says** — the issue in two or three plain sentences (its actual content, not its title).
2. **What changed** since the reference date — new comments summarized by author and substance, state/label edits. For a new issue: "new".
3. **Proposed urgency + why** — one line.

Then the action menu (multi-select where the harness allows; combinations are legitimate):

- **Tag on GitHub** → fetch the repo's real labels (`gh label list`) once per run, offer them as a menu, then apply with `gh issue edit N --add-label <chosen>` showing the exact command as you run it. Only labels the user picked — never invent or pre-apply.
- **Segna per approfondimento** → add to the state doc's "Needs deep dive" with a one-line why; suggest `plan-walkthrough` as the follow-up when the list is walked later.
- **Nota** → a persistent one-line note in the state doc.
- **Avanti** — nothing to do, next issue.
- **Stop** — save progress (issues not yet walked stay marked pending in the Last run table).

Urgency disagreements are data: record the user's call, not the proposal.

## Step 3 — Close

1. Update the state doc: new `Last check` (the sweep-start timestamp), the final queue table with per-issue outcomes, deep-dive additions, notes.
2. Report in ≤6 lines: how many new / changed / tagged / marked for deep dive, and the top of the deep-dive list.

## Red Flags

- Applying a label the user didn't pick from the menu, or any label not in `gh label list`
- Deciding urgency instead of proposing it
- Summarizing an issue from its title without reading the body
- Ending a run without updating `Last check` (the next sweep will re-show everything or, worse, miss the gap)
- Commenting on, assigning, or closing an issue — out of scope even if it feels helpful; surface the suggestion to the user instead
- The cycle advancing past an unanswered menu

## Interaction with Other Skills

- **`plan-walkthrough`** — the deep-dive list is its feed: an issue marked for approfondimento gets the full document review there.
- **`pr-walkthrough` / `writing-prds`** — downstream once an issue graduates from triage to work.

## Verification

- [ ] Reference date confirmed via menu; sweep covered new, changed, and commented issues
- [ ] Every walked issue got summary + what-changed + proposed urgency, and its menu was answered
- [ ] Labels applied only from the repo's real label set, only on user selection, command shown
- [ ] State doc updated: sweep-start timestamp, outcomes, deep-dive list
- [ ] No issue was assigned, closed, or commented
