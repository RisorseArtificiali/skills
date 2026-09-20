---
name: pr-assessment
description: "Fast calibrated pre-review of a pull request or branch: a light scan builds a structured state, then a batched battery of typed JEV questions (TypeSafe System One model) returns calibrated probabilities — per-dimension risk, per-doc drift flags, atomic intent checks, per-change review priority. Divergences between the scanner's traffic light and the JEV probabilities become doubts the human triages. Use when the user wants a quick assessment before (or instead of) a full walkthrough: \"assess this PR\", \"PR assessment\", \"quick JEV pass\", \"calibrated pre-review\", \"valuta questa PR\", or before deciding whether a walkthrough is worth it. Not a walkthrough (that is pr-walkthrough), not line-level code review (that is review / adversarial-code-review)."
---

# PR Assessment

## Host tools

In Codex, dispatch the scan subagent with `spawn_agent` and `fork_turns: "none"`
when supported; omit model/effort overrides. If fresh subagents are
unavailable, run the scan inline and disclose that the scan is not
fresh-context. The JEV pass itself is a local script — no subagent needed.

## Overview

A reviewer's first question is usually "where should I look?" This skill
answers it in minutes and cents: a light scan compresses the PR into a
structured state, one batched call to JEV ([System One
model](https://docs.typesafe.ai/) — typed questions in, calibrated
probabilities out, no text generation) judges it, and the report shows where
scanner judgment and calibrated probability agree or diverge. Every doubt goes
to the human; nothing is posted anywhere.

Posture (load-bearing):

- **JEV never produces findings or verdicts.** Its output enters the report as
  doubts and probabilities the human triages. Findings are review prompts, not
  proof of a defect.
- **Divergence is the product.** Scanner-green + JEV-high, or scanner-red +
  JEV-low: both are doubts worth a human's second. Agreement is confidence to
  move on.
- **State over criteria.** Weak judgment means the state is missing something
  (doc inventory, repo facts) — enrich the state, don't polish question text.
  The battery is constants in `jev/batteries/pr-assessment.json`; edit it
  deliberately, never inline in a prompt.

This is the light sibling of `pr-walkthrough`: no Mermaid map, no interactive
walkthrough, no consolidation into author questions. It tells you where the
risk sits and whether a full walkthrough is worth it.

## Step 0 — Target and Setup

- **Target:** a PR number (`gh pr view N --json title,body,additions,deletions,changedFiles`,
  `gh pr diff N --name-only`) or a local branch (`git merge-base HEAD <main>`…`HEAD`).
- **Home:** `<repo>/.reviews/assessments/`. Create it if missing and ensure
  `.reviews/` is in `.git/info/exclude` (never touch `.gitignore`). Files:
  `PR-<n>.jev-state.json`, `PR-<n>.jev-report.json`, `PR-<n>.md` (dossier).
- **Resume:** if a report for the target exists, offer via closed question:
  reuse it, or re-run (only if new commits landed).

## Step 1 — Scan for State (one subagent)

Dispatch ONE scan subagent (inline scan is acceptable for PRs under ~10 files,
with disclosure). The prompt must require the structured state contract
(`jev/README.md`): `pr` facts, `declared_intent` (verbatim), `normative_sources`
with what each establishes, `logical_changes` (3–8, NEUTRAL descriptions —
never bake a conclusion into a description), `doc_inventory` (enumerate the
docs that touch what the PR touches, with what each covers), `repo_facts`
(explicit verified facts), `scanner_status` for the seven dimensions
(intent, architecture, impacts, ux, ops, docs, tests).

Scan honesty rule: an unexamined dimension is a DOUBT in the notes, never a
green. The state never contains raw diff hunks — compact notes and file names
only.

## Step 2 — The JEV Pass

Run the runner (repo checkout: `scripts/jev/jev_call.py`; installed skill:
`jev/jev_call.py` next to this file):

```
python3 <jev>/jev_call.py --state <dossier>.jev-state.json --battery <jev>/batteries/pr-assessment.json
```

Key resolution: `TYPESAFE_API_KEY` env var, or `--key-file`. If no key (or the
API is unreachable), ask via closed question: **proceed scan-only** (report the
scanner traffic light alone, marked "JEV pass: skipped") or **stop**. The
skill degrades gracefully; it never blocks on the key.

The runner prints DOUBT / DOC / INTENT / PRIO / LOW lines and writes the full
report next to the state file.

## Step 3 — The Report

Write the dossier (`PR-<n>.md`), then present it in ≤15 lines:

1. **Header** — PR facts, declared intent (1–2 lines), JEV pass status
   (model, ms, cost ≈ $0.001).
2. **Dimension table** — scanner status × JEV risk noul, diverging cells marked ⚠.
3. **Doubts** — every divergence and doc/intent flag, one line each.
4. **Priorities** — logical changes by review priority, confidence shown.
5. **Low attention** — green + noul ≤ 0.30 + no doc flags (never intent),
   numbers visible so a wrong low can be challenged.
6. **Suggested mode** — by dimension vs by logical change (for the follow-up
   walkthrough, if any).

Then one closed question: **triage the doubts?** (recommended when doubts
exist) / **hand off to pr-walkthrough** / **stop here, the report is the
deliverable**. Doubt triage menu (one closed question per doubt):

- **Real problem** → author-question list in the dossier
- **Accepted trade-off** → recorded with rationale
- **False alarm** → dropped, one-line why
- **Needs walkthrough** → park for the hand-off

Offer the English version (`PR-<n>.en.md`) via closed question if the session
language isn't English.

## Red Flags — stop and correct course

- JEV numbers presented as verdicts, or a doubt hidden because "JEV said low"
- The state contains raw diff hunks (privacy contract broken)
- A big PR scanned inline without disclosure, or scanner_status greens on
  dimensions nothing examined
- Question text edited inline in a prompt instead of in the battery file
- Anything posted to the PR — this skill never posts; hand-off drafts go
  through pr-walkthrough's approval gate

## Interaction with Other Skills

- **`pr-walkthrough`** — the deep sibling. Hand-off: the assessment dossier
  seeds Step 0/1 (declared intent, inventory, doubts as pre-seeded findings).
  The "needs walkthrough" list is its input.
- **`review` / `adversarial-code-review`** — code-level; an assessment doubt
  about line-level correctness belongs there.
- **`plan-walkthrough`** — same shape for documents; a plan battery can be
  added to `jev/batteries/` when a ground-truth validation exists.

## Verification

- [ ] State written under `.reviews/assessments/`, contract-complete, no raw hunks
- [ ] Report shows scanner × JEV side by side; every divergence surfaced as a doubt
- [ ] Every doubt triaged by the user through the menu — none resolved unilaterally
- [ ] Low-attention marks carry their numbers; none on intent; none when doc flags exist
- [ ] No-key path offered as a closed question, not an error
- [ ] Nothing posted anywhere; battery edited only in its JSON file
