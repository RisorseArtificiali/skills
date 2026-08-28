---
name: writing-prds
description: Write a phased PRD (product requirements document) from an evaluated idea or issue, and decompose it into backlog-ready tasks with testable acceptance criteria. Use after brainstorming and grilling have produced a shared understanding, whenever the user says "write the PRD", "requirements doc", "spec this out in phases", "break this into tasks", or wants to turn an approved design or issue into a structured, phased plan of record — even if they don't say "PRD". Not for implementation plans (that is writing-plans) and not for exploring an idea that is still fuzzy (that is brainstorming/grilling first).
---

# Writing PRDs

## Overview

A PRD is the plan of record between "we agree on what to build" and "someone builds it". It lives at a specific altitude: **what must be true and why, phase by phase** — above the implementation plan (which says how, file by file) and below the brainstorm (which explored whether and what).

The PRD's real consumers are agents and reviewers who were not in the room. Every future task will be executed by a fresh session with no memory of the conversations that produced this document. A PRD that says "as discussed" or "the usual approach" is broken for its actual audience. Write it as a work order for strangers.

## Position in the Pipeline

```
issue/idea → brainstorming (+ interview-me) → grilling → PRD (this skill)
          → task decomposition (Backlog.md or markdown) → writing-plans per task
          → implementation → adversarial-code-review before merge
```

**Prerequisite gate:** do not write a PRD from a raw idea. Required inputs:

1. A validated understanding of the problem — a design doc from `brainstorming`, an evaluated issue, or an equivalent written source.
2. The decisions from `grilling` (or an explicit user statement that grilling is skipped).

If these don't exist yet, invoke `brainstorming` and/or `grilling` first — writing a PRD on unexamined requirements just launders ambiguity into official-looking text. If the input is a GitHub issue, read it (`gh issue view <N> --comments`) and treat unresolved discussion threads as grilling questions still to ask.

## The PRD Document

Save to `docs/prd/YYYY-MM-DD-<topic>.md` (user preferences for location override this). Always use this structure — and cut any section that would be empty filler rather than padding it:

```markdown
# PRD: <name>

**Problem:** <2-4 sentences: what hurts today, for whom, why now>
**Goal:** <one sentence: the outcome when this ships>
**Non-goals:** <explicit list of things this deliberately does NOT do>
**Success criteria:** <how we'll know it worked — observable, not aspirational>

## Decisions
<One line per decision made during brainstorming/grilling: the decision and
its why. This section exists so no future agent relitigates a closed question.>
- <decision> — because <rationale>

## Phase 1: <name>
**Goal:** <what this phase proves or delivers, one sentence>
**Scope:** <what's in>
**Out of scope for this phase:** <what's deliberately deferred, and to where>
**Depends on:** <nothing | phase N | external factor>

**Acceptance criteria:**
- [ ] <atomic, testable statement>
- [ ] <negative/edge case where relevant>
- [ ] <testing expectation for this phase>
- [ ] <documentation expectation for this phase>

## Phase 2: ...

## Open questions
<Questions that remain genuinely open, each with who decides and by when it
blocks. This is the ONLY place uncertainty may live — a "TBD" inside a
requirement is a defect; move it here or resolve it.>

## Out of scope (whole PRD)
<What this PRD deliberately does not cover, so its absence reads as a
decision, not an oversight.>
```

### Phase design rules

Phases are the load-bearing structure — they become the task breakdown, so their boundaries matter more than their prose:

- **Each phase ships something verifiable on its own.** The test: if the project were cancelled after phase N, would phases 1..N still be worth having merged? If a phase only "prepares" for the next one, fold it into the phase that needs it.
- **Order by risk, not by architecture.** The phase that proves the riskiest assumption comes first, while course-correction is cheap. "Set up scaffolding" is almost never phase 1.
- **Size for one agent, one review.** A phase should be implementable by a single fresh agent session and reviewable in one sitting. When in doubt, smaller — a context-bounded implementer handed an oversized phase produces shallow work on everything instead of solid work on something.
- **Dependencies are stated, not implied.** If phase 3 consumes something phase 1 produces, name the artifact (schema, endpoint, function) — the phase-3 implementer won't have read phase 1's code yet.

### Acceptance criteria rules

Acceptance criteria are the contract every downstream review will check against, so their quality bounds the quality of everything after:

- **Falsifiable, not aspirational.** For each criterion ask: what concrete check would FAIL if this weren't done? If you can't name one, the criterion is a wish ("works well", "is robust", "handles errors appropriately") — rewrite it around the observable behavior ("returns 422 with a field-level message when the payload fails validation").
- **Atomic.** One verifiable fact per checkbox. A criterion with "and" in it usually hides two.
- **WHAT, not HOW.** No implementation details — file names, function names, and library choices belong in the implementation plan. A criterion that prescribes the how can't survive a legitimate change of approach.
- **Edge and negative cases included** where behavior at the boundary matters — the happy path is what authors test anyway; the criteria earn their keep at the edges.
- **Tests and docs are in-phase criteria, never deferred.** "Add tests in a follow-up" is how features ship untested. Every phase's criteria include its testing and documentation expectations.

## Self-Review

After writing, re-read the document with fresh eyes and check — fix inline, no re-review loop:

1. **Ambiguity:** could any requirement be read two ways? Pick one, make it explicit.
2. **Placeholders:** any TBD/TODO outside the Open questions section? Resolve or move it there.
3. **Falsifiability:** for every acceptance criterion, can you name the check that would fail? Rewrite the ones where you can't.
4. **Phase independence:** does every phase pass the cancellation test? Are all cross-phase dependencies named?
5. **Traceability:** is every grilling decision reflected? Is every requirement covered by some phase's criteria? Anything in the goal with no criterion anywhere is unbuilt by definition.
6. **Length:** every section earns its place — a PRD padded with boilerplate trains readers to skim, and skimmed requirements might as well not exist.

Then show the PRD to the user and get approval **before** decomposing into tasks. Task creation is a commitment; the document it derives from must be agreed first.

## Decomposing into Tasks

After the user approves the PRD:

**If a Backlog.md MCP is available** (`task_create` etc.): follow its task-creation guide. The mapping is mechanical by design:

- One task per phase by default. Split a phase into subtasks only if its criteria span clearly separable deliverables that could be reviewed independently.
- Task description = the phase's Goal + the PRD's Problem context, restated so the task stands alone (the executing agent will not read this conversation — restate, don't reference).
- Acceptance criteria = the phase's criteria, copied verbatim.
- Record dependencies between tasks matching the PRD's "Depends on" lines.
- Use the task's references/documentation fields to link the PRD file and the design doc.
- Leave Definition of Done to project defaults — DoD is completion hygiene, acceptance criteria are scope; don't duplicate one into the other.
- Report every created task (ID, title, criteria) back to the user.

**If no backlog tool is available:** append a `## Task breakdown` section to the PRD itself with the same schema (title, description, criteria, dependencies per task), so the decomposition ports to any tracker later without rework.

Either way: create all tasks in one session — batch-created tasks stay consistent with each other; stragglers added later drift.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The idea is clear enough, skip grilling and write the PRD" | Unexamined requirements don't disappear in a PRD — they get laundered into confident text and surface as rework. |
| "This criterion is obvious, no need to make it testable" | Obvious to you, now. The executing agent meets it cold, and an unfalsifiable criterion is unreviewable. |
| "Phase 1: setup and scaffolding" | Setup proves nothing and ships nothing. Fold it into the first phase that delivers verifiable behavior. |
| "I'll note the file names in the criteria to help the implementer" | That help expires with the first design change. The implementation plan is downstream; keep the PRD at its altitude. |
| "Tests and docs get their own phase at the end" | A final "quality phase" is the first thing cut under pressure. In-phase criteria are the only ones that survive. |
| "TBD here, we'll figure it out during implementation" | Then it's an Open question with an owner — or the phase isn't ready to be committed as a task. |

## Interaction with Other Skills

- **`brainstorming` / `interview-me` / `grilling`** — upstream; they produce this skill's required inputs.
- **`writing-plans`** — downstream; each task from this PRD becomes one implementation plan. The PRD is what lets that plan be written by an agent that never saw this conversation.
- **`subagent-driven-development`** — executes those plans task by task.
- **`adversarial-code-review`** — the phase's acceptance criteria become the review CONTRACT; a PRD with falsifiable criteria is what makes that review sharp.

## Verification

- [ ] Inputs existed (design/issue + grilling decisions) or upstream skills were run first
- [ ] Every phase passes the cancellation test and has named dependencies
- [ ] Every acceptance criterion is falsifiable, atomic, and implementation-free
- [ ] Testing and documentation expectations appear inside each phase's criteria
- [ ] No TBD outside Open questions; non-goals and out-of-scope are explicit
- [ ] User approved the PRD before any task was created
- [ ] Tasks (backlog or markdown) restate context, copy criteria verbatim, and record dependencies
