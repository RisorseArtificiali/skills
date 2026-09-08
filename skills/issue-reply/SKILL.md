---
name: issue-reply
description: Reply to GitHub issue discussions as the maintainer — fetch the issue and its thread, brief the user on the discussion and the open questions, verify technical claims against the code before endorsing them, draft the reply, and publish only after explicit approval. Use when the user says "rispondi alle issue", "respond to the issues", "guardiamo la #N", "reply to the comments", or hands over a list of issues to answer. The commenting counterpart of issue-triage, which stays read-only.
---

# Issue Reply

## Overview

The response half of the issue pipeline: `issue-triage` is the read-only radar, this skill holds the conversation — understand an issue's thread, decide the maintainer's answer, publish it. One issue at a time: fetch, brief, resolve, publish, then the next. The user disposes on every gate; nothing reaches GitHub unapproved.

## Step 1 — Fetch

`gh issue view N` twice: once with `--json title,state,author,labels,createdAt,body`, once with `--comments`. Read the body and every comment before briefing — a summary from the title alone is the classic miss.

## Step 2 — Brief the user

In the session language, a readable brief (plain prose, no AI bloat):

1. **The issue** — what it actually asks, two or three sentences.
2. **The discussion** — who said what, by substance, in thread order.
3. **The open questions** — only those awaiting the maintainer, numbered.

When a question is technical, add your **code-side analysis**: verify claims against the real code and artifacts before endorsing them (`javap`, read the class, count the call sites). An external finding is a hypothesis until reproduced locally.

Completion: the user knows what the thread wants from them and answers with a decision.

## Step 3 — Draft and gate

Draft the reply in plain English (GitHub's lingua franca) at B2 level: short sentences, plain vocabulary, numbered decisions, one direct answer per open question. No idioms, no AI-bloat, no attribution footers — unless the project's convention says otherwise. Show the draft; the **approval gate** is explicit — publish only after an OK, and redraft until one arrives. Offer follow-ups (labels, body edits, memory notes) as separate questions; apply a label only when the user picked it.

## Step 4 — Publish and hand off

Post with `gh issue comment N --body-file <file>` and report the link. Then the **handoff**: record the outcome (decision taken, who owns the follow-up, anything pending such as a meeting) in the agent's persistent memory; if the thread surfaced during a triage sweep, note it in the triage state doc (`.reviews/triage/issues.md`) too.

## Side artifacts

Meeting notes spun off an issue (a design sync, an incident review): plain English, in the repo's gitignored working-notes directory (ask which one if none is established), shown to the user before writing. Implementation plans go to `.reviews/plans/`, never a tracked path.

## Red flags

- Posting before the approval gate, or applying a label the user didn't pick
- Endorsing an external finding without reproducing it against the code
- Meeting notes or drafts landing in tracked paths
- Moving to the next issue while one is still unanswered

## With other skills

- **issue-triage** — the radar; its triage questions and "needs deep dive" list feed this one.
