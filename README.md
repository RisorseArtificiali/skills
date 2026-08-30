**English** · [Italiano](README_IT.md)

The skill set we run daily on our coding agent harness: our own skills (`skills/`), forks of
MIT-licensed upstream skills we maintain locally (`forked/`), and the workflow
that chains them. Skills are the unit that makes an agent's *process*
predictable — this repo is ours, opinionated and versioned.

## Built for large projects

This workflow and this skill collection were created for projects with
**10+ active contributors and 50+ people involved in some capacity**. That
does not make them unsuitable for smaller ones — but there they may need
some adaptation. Our advice: try the skills as they are, and adapt the
workflow to your needs as you go. And one principle does not scale with
project size, because it never changes: the role of managing and
orchestrating the agents is, and remains, a human one.

## The workflow

For any non-trivial feature or issue, the pipeline is:

1. **brainstorming** — evaluate the idea/issue, converge on an approved
   design (upstream's "three paths" model: spike / bounded / architectural —
   the ceremony scales with the task, the approval gate never does).
   Falls to **interview-me** *(upstream)* when intent is underspecified.
2. **grilling** *(fork)* — stress-test the decisions one question at a time
   until shared understanding.
3. **writing-prds** — phased PRD with falsifiable acceptance criteria; decompose
   into tasks.
4. **writing-plans** *(fork)* — one implementation plan per task. Fork addition:
   a *Deviation Protocol* — executors stop and report on deviation, never
   improvise a fix.
5. **subagent-driven-development** *(fork)* — execute plans task-by-task with
   fresh subagents. Fork policy: *Model Selection — always inherit* (every
   dispatch runs on the session's model; quality is enforced by the fix loop
   and review gates, not by model tiering) and a Maven test-iteration section.
6. **adversarial-code-review** — mandatory gate before merging any branch: fresh
   reviewer subagents attacking from distinct lenses, then verifiers that must
   reproduce every finding. The PRD's acceptance criteria are the review contract.

Around the pipeline: **doubt-driven-development** *(fork)* for in-flight second
opinions, **review** for on-demand leveled reviews, **plan-walkthrough** /
**pr-walkthrough** to review documents/PRs above the code level with the human
in the loop — each leaves a **visual dossier** (Mermaid diagrams: before/after
architecture, impact map, phase graph, traceability, assumptions) so impacts
and risks are *seen*, not imagined, **issue-triage** as the issue radar,
**git-guardrails-claude-code** as the destructive-git safety net, **handoff**
*(fork)* to pass work between sessions, **catch-me-up** /
**drink-from-the-firehose** to re-enter a project cold. Craft references:
**navigating-java** (symbol-level Java navigation), **slides** (fully-local
reveal.js decks).

### Running a project with it

The catalog above says what exists and how to install it.
[**WORKFLOW.md**](WORKFLOW.md) says how to use it, for the human driving
the agents: the pyramid of roles (who directs, who executes, and why the
strongest model plans), the gates where a human decides, the daily rhythm,
where knowledge lives, and how to wire a new machine or project.
[**SKILLS-CHEATSHEET.md**](SKILLS-CHEATSHEET.md) is the one-glance answer
to "which skill right now?" — in the pipeline and in every other moment of
project life — and `scripts/wire-machine.sh` automates the wiring.

The agents themselves run in [**Lince**](https://lince.sh)
([RisorseArtificiali/lince](https://github.com/RisorseArtificiali/lince)):
every coding agent lives in an isolated sandbox, so even full permissions
cannot damage the machine, and the dashboard drives several agents in
parallel — each on its own task, in its own worktree. Our steady state is
about five agents at a time, across one or two projects. Typing is
optional: voice input via [**VoxCode**](https://github.com/RisorseArtificiali/voxcode)
(Whisper transcription, fully local — no audio leaves the machine) is how
long context gets from your head into the agent.

## Own skills (`skills/`)

| Skill | What it does |
|---|---|
| adversarial-code-review | pre-merge adversarial review: fresh-context reviewers + reproducibility gate |
| review | quick leveled review of a diff/branch/PR on demand |
| writing-prds | phased PRD with falsifiable acceptance criteria, decomposed into tasks |
| plan-walkthrough | logical review of PRDs/plans/design docs as a visual dossier (Mermaid phase graph, traceability matrix, assumption map), human in the loop |
| pr-walkthrough | logical review of a PR above the code level: Mermaid before/after map + impact map, blast radius at a glance |
| issue-triage | periodic GitHub-issue sweep with rolling state |
| navigating-java | structural Java navigation (symbols before grep) |
| slides | presentation as markdown + vendored reveal.js deck |
| catch-me-up | post-absence realignment briefing |
| drink-from-the-firehose | role-aware guided project onboarding |

## Forks (`forked/`)

Pinned snapshots of MIT-licensed upstream skills, some with local
modifications (see [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md) for
sources, base versions and the exact changes, and
[`forked/README.md`](forked/README.md) for the reasons):

| Skill | Upstream | Local delta |
|---|---|---|
| subagent-driven-development | obra/superpowers | + "Model Selection — always inherit" policy, + Maven test-iteration section |
| writing-plans | obra/superpowers | + "Deviation Protocol" section, + per-task Guardrails block |
| doubt-driven-development | addyosmani/agent-skills | none — pinned snapshot; keeps standalone-friendly paths after an upstream restructure |
| grilling | mattpocock/skills | question flow rewritten: one question at a time with recommended answers (upstream asks batched rounds) |
| handoff | mattpocock/skills | storage moved from the OS temp dir into the repo, one file per handoff, pending/done lifecycle |

## Upstream skills we use unmodified

Not vendored here — installed straight from their repos (all MIT), cited as
thanks:

| Skill | Repo |
|---|---|
| interview-me, context-engineering | addyosmani/agent-skills |
| brainstorming, dispatching-parallel-agents, finishing-a-development-branch, requesting-code-review, systematic-debugging, using-git-worktrees | obra/superpowers |
| codebase-design, diagnosing-bugs, domain-modeling, grill-with-docs, grill-me, git-guardrails-claude-code, wait-what, writing-for-agents | mattpocock/skills |
| ponytail-review | DietrichGebert/ponytail |

Install any of them (and anything from this repo) with:

```sh
npx skills add <owner>/<repo> -g -y --agent <your-agent> --skill <skill-name>
# e.g. from this repo, once public:
npx skills add maeste/skills -g -y --agent <your-agent> --skill review
```

## Companion MCP servers

Three MCP servers complete the setup — none required by the skills, all worth citing:

| Server | Repo | Role in the workflow |
|---|---|---|
| Serena | https://github.com/oraios/serena | semantic code retrieval and editing — the backend `navigating-java` drives for symbol-level navigation |
| Backlog.md | https://github.com/MrLesk/Backlog.md | human/agent project collaboration in git — where the `writing-prds` task decomposition lands |
| qmd | https://github.com/tobi/qmd | local mini search engine over markdown — indexes the docs, plans and reviews the pipeline produces |

## Also from us

- [**Lince**](https://lince.sh) — sandbox + dashboard + hooks: the
  multi-agent workstation this toolkit runs in
  ([RisorseArtificiali/lince](https://github.com/RisorseArtificiali/lince)).
- [**VoxCode**](https://github.com/RisorseArtificiali/voxcode) — voice input
  for coding agents: local Whisper transcription, no audio leaves the
  machine; installs with Lince.
- [**RisorseArtificiali**](https://risorseartificiali.com) — the organization
  behind Lince and this skill set.
- [**maeste.it**](https://maeste.it) — Stefano Maestri's site.

## License

MIT — see [`LICENSE`](LICENSE). `forked/` derives from MIT-licensed upstream
work; their notices are retained in
[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).
