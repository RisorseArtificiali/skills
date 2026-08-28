---
name: catch-me-up
description: Post-absence realignment briefing — everything that happened in the project while you were away, in one shot.
disable-model-invocation: true
---

One question, then the report. The anti-Socratic sibling of drink-from-the-firehose: no
chapters, no quizzes — everything together, deep where it matters, in the user's language.

## 1 — Kickoff

Ask one question: how many days back (menu: 7 / 14 / 30, plus free text). The answer
opens **the window**.

## 2 — Gather the window

Pick the remote: `upstream` if configured, else `origin` — the canonical project remote;
your fork's own activity is your work, not what happened. Resolve its slug for `gh`;
if `gh` is missing or unauthenticated, stop with a clear message — no invented report.

From the window, collect:

- PRs: opened, merged, closed; review activity.
- Issues: new, closed, reopened; threads with substance.
- Direct commits on the default branch.
- Releases and tags.
- Discussions, if the repo uses them.
- Decisions and conventions: new ADRs, changed architecture docs, convention shifts.
- **Your triage**, via the authenticated gh user: assigned issues, requested reviews,
  mentions and CCs, your PRs stalled or with changes requested.

**Done when:** every source above was queried, or noted absent.

## 3 — Tier by significance

Items earn a **deep dive** by significance: a large diff, substantive discussion,
decision content, or a breaking change gets its diff and conversation read, summarized
as what + why + implications. Chores, typos, CI-only and dependency bumps stay
one-liners. The report states the promotion rule and which items it promoted.

## 4 — Deliver

**Chat — the executive.** "Needs your action" first (the triage, with links), then the
period's big themes with links. Scannable in a minute.

**Artifact — the catch-up.** One self-contained HTML page: the digest organized by
recurring **themes** (the thematic grouping is your reading — labelled as such; the
linked items are the facts), a pure chronological timeline alongside, every item with
state, author and link, deep dives inline, type filters.

Every claim carries its **receipt**: the PR, issue, commit or doc it comes from.
Synthesis is labelled as synthesis.

**Done when:** the chat executive stands alone, and the artifact renders without the
chat open.

## 5 — Hand back

Invite the drill-down: any item can be opened further in chat ("tell me more about
#123"). The session continues from there.
