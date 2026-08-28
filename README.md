
The skill set we run daily on our coding agent harness: our own skills (`skills/`), forks of
MIT-licensed upstream skills we maintain locally (`forked/`), and the workflow
that chains them. Skills are the unit that makes an agent's *process*
predictable — this repo is ours, opinionated and versioned.

## The workflow

For any non-trivial feature or issue, the pipeline is:

1. **brainstorming** *(fork)* — evaluate the idea/issue, converge on an approved
   design. Falls to **interview-me** *(upstream)* when intent is underspecified.
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
in the loop, **issue-triage** as the issue radar, **git-guardrails-claude-code**
*(fork)* as the destructive-git safety net, **handoff** *(fork)* to pass work
between sessions, **catch-me-up** / **drink-from-the-firehose** to re-enter a
project cold. Craft references: **navigating-java** (symbol-level Java
navigation), **slides** (fully-local reveal.js decks).

## Own skills (`skills/`)

| Skill | What it does |
|---|---|
| adversarial-code-review | pre-merge adversarial review: fresh-context reviewers + reproducibility gate |
| review | quick leveled review of a diff/branch/PR on demand |
| writing-prds | phased PRD with falsifiable acceptance criteria, decomposed into tasks |
| plan-walkthrough | logical review of PRDs/plans/design docs, human in the loop |
| pr-walkthrough | logical review of a PR above the code level |
| issue-triage | periodic GitHub-issue sweep with rolling state |
| navigating-java | structural Java navigation (symbols before grep) |
| slides | presentation as markdown + vendored reveal.js deck |
| catch-me-up | post-absence realignment briefing |
| drink-from-the-firehose | role-aware guided project onboarding |

## Forks (`forked/`)

MIT-licensed upstream skills we run with local modifications (see
[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md) for sources, base versions
and the exact changes):

| Skill | Upstream | Local delta |
|---|---|---|
| brainstorming | obra/superpowers | light edits; base snapshot 2026-07-28 |
| subagent-driven-development | obra/superpowers | + "Model Selection — always inherit" policy, + Maven test-iteration section |
| writing-plans | obra/superpowers | + "Deviation Protocol" section |
| doubt-driven-development | addyosmani/agent-skills | path fixes for standalone install |
| grilling | mattpocock/skills | light edits; base snapshot 2026-07-28 |
| grill-me | mattpocock/skills | light edits |
| handoff | mattpocock/skills | light edits |
| git-guardrails-claude-code | mattpocock/skills | light edits |

## Upstream skills we use unmodified

Not vendored here — installed straight from their repos (all MIT), cited as
thanks:

| Skill | Repo |
|---|---|
| interview-me, context-engineering | addyosmani/agent-skills |
| dispatching-parallel-agents, finishing-a-development-branch, requesting-code-review, systematic-debugging, using-git-worktrees | obra/superpowers |
| codebase-design, diagnosing-bugs, domain-modeling, grill-with-docs, wait-what, writing-for-agents | mattpocock/skills |
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

## License

MIT — see [`LICENSE`](LICENSE). `forked/` derives from MIT-licensed upstream
work; their notices are retained in
[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).
