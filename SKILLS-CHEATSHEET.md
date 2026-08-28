# SKILLS CHEATSHEET — which skill, when

A lookup table for the human: you feel a need, you find the skill. The
[workflow](WORKFLOW.md) tells the story; this page is the index. If two
rows seem to fit, the "two-second rules" at the bottom break the tie.

## In the pipeline (stage by stage)

| When | Skill | Your part |
|---|---|---|
| An idea, issue or request arrives | `brainstorming` (+ `interview-me` if the intent is unclear) | answer questions; approve the design |
| The design needs stress-testing | `grilling` | one question at a time; your decisions stay yours |
| Shared understanding reached | `writing-prds` | approve the PRD before any task exists |
| PRD or plan is written | `plan-walkthrough` | judge it at the stage-3 gate |
| Tasks are approved | `writing-plans`, then `subagent-driven-development` | answer deviation reports only |
| A branch is done | `adversarial-code-review` | read the verdict; then merge — explicitly |

## Any moment, on demand

| You are thinking... | Skill |
|---|---|
| "I am not sure about this decision we just made" | `doubt-driven-development` |
| "Give this diff a quick look" | `review` (fast second opinion, mid-work) |
| "This is about to merge, or it touches something risky" | `adversarial-code-review` |
| "Help me understand / review this big PR" | `pr-walkthrough` |
| "Is this document (PRD, plan, design, issue) any good?" | `plan-walkthrough` |
| "This test fails / this broke / it got slow" | `systematic-debugging`, `diagnosing-bugs` |
| "Where is this in the Java code? Who calls it?" | `navigating-java` — before any grep |
| "This design area feels tangled" | `codebase-design` |
| "Is this over-engineered?" | `ponytail-review` (a diff), `ponytail-audit` (a whole repo) |
| "These tasks are independent — run them in parallel" | `dispatching-parallel-agents` |
| "This work needs isolation from my workspace" | `using-git-worktrees` |
| "The branch is finished — what now?" | `finishing-a-development-branch` |
| "Write or update docs for agents" | `writing-for-agents` |
| "Agent output is degrading — check the context setup" | `context-engineering` |

## By moment

### Project start
- New to the project (human!) → `drink-from-the-firehose` — role-aware,
  quiz-driven onboarding; every claim carries its source.
- Setting up a new box or repo → the [wiring checklist](WORKFLOW.md#wiring-a-new-machine-or-project)
  and `scripts/wire-machine.sh`.

### Day to day
- Back after a few days → `catch-me-up` — one report, your open work first.
- Session is closing → `handoff` — the next session reads a document, not
  your memory.
- A decision feels shaky while work is in flight → `doubt-driven-development`.

### Periodic
- Weekly, or whenever you return → `issue-triage` — the radar: new,
  changed, and yours.

### Decisions that deserve to leave traces
- The design is worth ADRs and a glossary → `grill-with-docs` instead of
  `grilling` — same interview, but it writes as it goes.
- Domain terms need pinning down → `domain-modeling`.

### Communication
- Something must be presented → `slides` — markdown source + offline deck.
- An explanation did not land → `wait-what` — "re-pitch it, simpler".
- You want the agent to interview *you* → `grilling` (or `/grill-me`).

## Two-second rules

- **Merge-bound or risky?** → `adversarial-code-review`, not `review`.
  `review` is the everyday tool; the gate is the gate.
- **Document or code?** Document → `plan-walkthrough`. Code → `review` /
  `pr-walkthrough` (above the code level) — never line-level nitpicks at a gate.
- **Decision not yet made?** → `doubt-driven-development`. Decision made and
  built? → the review family.
- **How fuzzy is the idea?** Fuzzy → `brainstorming`. Clear idea, contested
  decisions → `grilling`. Shared understanding → `writing-prds`.
- **Java and code structure?** → `navigating-java` first, grep second.
  Strings, configs, resources? → grep is the right tool there.
- **Model older or smaller?** Keep the pipeline anyway — the skills are its
  guardrail, not an optional extra.
