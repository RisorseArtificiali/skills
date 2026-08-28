# Skills

This folder holds the skills we wrote ourselves. A skill is a written
procedure that a coding agent loads and follows: it teaches the agent how
to do one job, step by step, instead of leaving the method to chance.

Why does this matter to you? An agent without a fixed process is not
consistent. It reviews code differently every time, forgets steps, and
gives you answers you cannot fully trust. A skill makes the process
repeatable: the same quality gates run on every task, and you can open the
`SKILL.md` file and read exactly what the agent is going to do.

Each skill lives in its own folder. This page describes, for humans, what
each skill does and what you get from using it. For how they chain
together in a full workflow, see the [main README](../README.md).

## Plan and specify

### writing-prds

Turns an approved idea or issue into a phased PRD (product requirements
document), and then breaks it into backlog-ready tasks with testable
acceptance criteria. It will not write a PRD from a raw idea — the
decisions must already exist (from brainstorming or a discussed issue).
Phases are ordered by risk, each phase ships something you can verify on
its own, and every acceptance criterion must be falsifiable: there has to
be a concrete check that fails if the work is not done.

**What you get:** a requirements document that an agent who never met you
can execute and review against. Vague wishes ("works well", "is robust")
get rewritten into observable behavior before anyone builds anything —
this is what stops ambiguity from reaching the code.

## Review

### adversarial-code-review

The mandatory review gate before merging a branch or PR. It creates an
isolated copy of the repo (a git worktree), checks that the test suite is
green, then sends a panel of fresh reviewer subagents to attack the change
from different angles: correctness, tests, security, simplification, and
compliance with the spec. Every finding they produce goes to a skeptic
subagent that must reproduce it by actually running code. Only reproduced
findings count as confirmed.

**What you get:** a review without the two classic failure modes. A
reviewer who shares the author's context tends to approve bad code; a
reviewer who only reads code produces findings that sound right but do not
reproduce. This skill blocks both, and its report is honest about what was
confirmed, what is only plausible, and what was not covered.

### review

The quick, everyday version of the review above. One or two fresh reviewer
subagents look at your current diff, a branch, or a PR — correctness bugs
first, plus reuse and simplification cleanups. Every finding is verified
before it reaches you, and the list is ranked most severe first. Levels
control the depth: low/medium gives you few, high-confidence findings;
high casts a wider net and marks what could not be reproduced.

**What you get:** a fast second opinion you can ask for in the middle of
work, with almost no noise. "No findings" is a real answer — the skill
does not invent nitpicks to justify the run.

### plan-walkthrough

A logical review of a *document* — a PRD, an implementation plan, a design
doc, a GitHub issue — with you in the loop. It builds a visual dossier
(phase graph, traceability matrix, assumption map), then walks you through
the document step by step with closed questions, and triages the findings
with you.

**What you get:** the holes in a plan surface before anyone builds it —
unclear goals, missing acceptance criteria, assumptions that do not hold
against the real codebase. Fixing a plan costs minutes; fixing the code
built from it costs days.

### pr-walkthrough

The same idea for a pull request or branch. It produces a map of what
changed, then walks you through the PR above the code level: architecture,
impacts and dependencies, user experience, operations, documentation, and
the test story.

**What you get:** you can actually review a PR that is too large or too
unfamiliar to grasp from the diff alone — as a reviewer, or before your
own merge.

## Navigate the code

### navigating-java

A method for moving around Java codebases with symbol-level tools (find
definition, find callers, find implementations, type hierarchy) instead of
text search — plus the Maven module structure knowledge that goes with it.
It also lists what symbol tools cannot see (reflection, dependency
injection by name, service loaders) and the string search that must back
them up before any rename or deletion.

**What you get:** correct answers to the questions grep answers wrongly in
Java, like "who calls this method?" and "what breaks if I change this
signature?". It also keeps the agent's context small: symbol overviews
instead of whole files read top to bottom.

## Stay oriented

### catch-me-up

After a few days away, it collects everything that happened in the
project: PRs, issues, releases, commits on the main branch, new decisions
and docs — plus the items assigned to you. It sorts the material by
importance and delivers a one-minute summary in chat, then a full HTML
page where every item links to its source.

**What you get:** back in the picture in minutes, with a receipt for every
claim, and your own open work (assigned issues, stalled reviews) listed
first.

### drink-from-the-firehose

A guided, quiz-driven onboarding walkthrough of a project. It scans the
repo, builds a chapter plan (what the project is, the module map, where
decisions live, how to build and test, and so on), then teaches chapter by
chapter. Short quizzes check understanding, and the difficulty adapts to
your answers. You pick a role — developer, PM, designer, user — and the
sources and depth follow it.

**What you get:** structured onboarding instead of random reading, and
every claim backed by a file or document you can open yourself.

### issue-triage

A fast, regular sweep of a repository's GitHub issues. It checks what is
new, changed, or newly commented since the last run (it keeps a small
rolling state document), then walks you through the issues one by one:
short summary, what changed, a proposed urgency. It only reads — it never
closes, assigns, or comments on anything unless you say so.

**What you get:** a quick giro over the backlog whenever you return to a
repo, with zero risk of accidental actions on GitHub.

## Communicate

### slides

Builds a presentation as two artifacts: a markdown file — the source of
truth, with speaker notes — and a reveal.js deck that works fully offline.
The deck's assets are vendored (no CDN), and the theme is generated from
design tokens, so it is consistent and easy to restyle.

**What you get:** presentations you can edit as text, version in git, and
present anywhere — including without internet access.
