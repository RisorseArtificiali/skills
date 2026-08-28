# Forked skills

This folder contains copies of skills from other repositories. All of them
are MIT-licensed; the upstream sources, base versions and license texts
are recorded in [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md).

We keep local copies for two reasons:

1. **Pinning.** We freeze a version we have tested. Upstream skills evolve
   fast, and sometimes they are redesigned completely. A redesign may be
   great for its author and wrong for us — with a pinned copy, our daily
   workflow cannot change overnight without a decision on our side.
2. **Local improvements.** Some forks carry changes we need and upstream
   does not have: a different interview style, a safer place to store
   handoffs, extra rules for our build tools. Where we changed something,
   this page says exactly what we changed and why.

The table below was checked against upstream `main` on **2026-08-28**.

| Skill | Upstream repo | Base snapshot | Our changes | Upstream since |
|---|---|---|---|---|
| grilling | mattpocock/skills | 2026-07-28 (`4128367`) | question flow rewritten | evolved the batch style further |
| handoff | mattpocock/skills | 2026-07-28 (`4128367`) | storage and lifecycle redesigned | still saves to the OS temp dir |
| writing-plans | obra/superpowers | 2026-07-28 (`44c9b2d`) | + Deviation Protocol, + per-task Guardrails | added a "Spec" header line to the template |
| subagent-driven-development | obra/superpowers | 2026-07-28 (`44c9b2d`) | + always-inherit model policy, + Maven test iteration | active development since |
| doubt-driven-development | addyosmani/agent-skills | 2026-07-26 (`7829ffd`) | none — exact snapshot | repo restructured; our copy keeps standalone-friendly paths |

Skills we used to vendor and now install unmodified from upstream instead:

- `brainstorming` (obra/superpowers) — we evaluated upstream's redesign (the
  "three paths" model: spike / bounded / architectural) and adopted it; once
  adopted there was no local delta left to justify a fork.
- `grill-me` and `git-guardrails-claude-code` (mattpocock/skills) — our
  copies had no local changes, and upstream differs today only by a line of
  wording.

See the main README for the as-is list.

## The forks in detail

### grilling

Stress-tests a plan or decision by interviewing you until you and the
agent share the same understanding. Our version asks **one question at a
time**, and for each question the agent states its recommended answer.
Facts that can be looked up in the repo are looked up, not asked; the real
decisions are always put to you. Nothing is acted on until you confirm the
shared understanding.

**Our changes:** upstream asks questions in batches — it maps a "design
tree" and fires a whole round of numbered questions at once. We rewrote
that flow into the sequential one described above.

**Why:** several questions at once are hard to answer well, and one
answer usually changes the next question worth asking. The recommended
answer keeps you in control: you can accept it with one word or argue
with it.

### handoff

Compresses the current conversation into a handoff document that a fresh
agent session can pick up: the state of the work, what was tried, and
which skills the next agent should use.

**Our changes:** upstream saves the handoff to the operating system's
temporary directory. We save it inside the repo, at
`.reviews/handoffs/<date>-<topic>.md`, kept out of version control
through `.git/info/exclude` (never `.gitignore`). The topic comes from the
command argument or the branch name; one file per handoff, so parallel
sessions never overwrite each other. A consumed handoff is moved to
`handoffs/done/` — and since no skill runs on the receiving side, the
instruction to do that travels inside the handoff document itself.

**Why:** a temp directory can be wiped at any moment, and the handoff must
survive until the next session — possibly days later, on another machine.
With the file next to the repo, the new session finds it where the work
lives.

### writing-plans

Turns one task into an implementation plan for an executor agent that will
never see this conversation: exact files, exact code snippets, verification
steps. The plan is a work order for a stranger.

**Our changes — two additions to the plan template:**

- **Deviation Protocol.** If a step does not produce its stated expected
  result, the executor must stop the task and report — expected vs
  observed, and the smallest question that unblocks it. No adapting the
  plan, no improvised fixes, no skipping ahead.
- **Per-task Guardrails.** Each task carries its repo invariants verbatim:
  architecture rules, module boundaries, forbidden dependencies. The
  executor sees only its own task, so the rules must travel inside it.

**Why:** a fresh executor has no shared context with us, so unplanned
fixes are invisible to everyone. A stopped task costs minutes; an executor
improvising past a deviation compounds a small surprise into rework.

### subagent-driven-development

Executes an implementation plan task by task with fresh subagents: an
implementer writes the code, a task reviewer checks it against the plan,
a fix loop resolves findings, and a final review covers the whole branch.

**Our changes — two policies:**

- **Model Selection — always inherit.** Every dispatch (implementers,
  reviewers, verifiers, final review) runs on the session's model.
  Upstream assigned cheap models to "mechanical" tasks; we removed that
  tiering. If a dispatch is too heavy, the answer is a fresh implementer
  with fuller context — never a silent model bump.
- **Fast, safe test iteration (Maven projects only).** Rules for keeping
  the per-iteration cost low: which plugin runs which test suffix, why
  `-DskipTests` can report a silent false green on integration tests, how
  to run one integration test per module, and why two Maven builds must
  never share a working tree.

**Why:** in practice a task stays "mechanical" only until something
unexpected happens, and the cheapest models respond to the unexpected by
improvising instead of stopping. Quality comes from the fix loop, the
Deviation Protocol and the review gates — not from the model tier. The
Maven rules exist because a false green is worse than a failure: it ends
the loop while the code is still broken.

### doubt-driven-development

Subjects a non-trivial decision to a fresh-context adversarial review
*while the work is happening* — the in-flight complement to
adversarial-code-review, which runs at the end.

**Our changes:** none. This is the exact upstream snapshot.

**Why we fork it:** upstream later restructured its repository, and the
new version refers to its support files with paths that only work inside
that repository layout. Our snapshot keeps the standalone-friendly
relative paths, so the skill remains usable on its own, without adopting
upstream's forced directory structure — install it anywhere and it works.
