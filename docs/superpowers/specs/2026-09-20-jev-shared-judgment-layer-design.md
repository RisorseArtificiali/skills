# JEV Shared Judgment Layer — Design

**Date:** 2026-09-20
**Status:** Approved design (all six sections) — pending implementation plan
**Branch:** `docs/jev-integration-design`
**First client:** `skills/pr-walkthrough`

## Context

[TypeSafe AI](https://typesafe.ai)'s **Jev** (`jev-1.13.0`, early access) is a "System One
model": it takes a `state` document plus typed questions and returns typed answers with
calibrated probabilities — no text generation. Three primitives: **Choice** (pick + per-option
probabilities + confidence), **Score** (rubric levels + confidence), **Noul** (probability of
yes, 0–1; 0.5 = uncertain). Questions sharing a state are evaluated in parallel in one call
(~$0.042/M input tokens, output free). Known limits: literal reading, no math/date reasoning,
indirection degrades it, context rot on large irrelevant state.

`pr-walkthrough` reviews a PR at logical altitude with the human as reviewer: scan subagents
→ logical-change inventory + 7-dimension traffic light → dossier map → interactive
walkthrough → consolidation. The scan phase already produces exactly the compact state Jev
judges well; the two architectures compose (LLM System 2 reads and compresses, Jev System 1
makes calibrated judgments on the compression).

## Evidence base — the spike (2026-09-20)

Two real, consolidated walkthrough dossiers (lince PR-272, technical; OneRing PR-250,
doc-only) were replayed through Jev batteries with **findings stripped from the state**;
dossier conclusions served as ground truth only post-hoc. Scripts and raw responses:
`temp/jev-spike.py`, `temp/jev-spike-v2.py`, `temp/jev-spike-*.json` (throwaway, git-ignored).

**v1 results (36 questions, 2 calls, ~$0.0002, 623–941 ms):**

- **PR-272:** priority ranking put R5 (hand-written registry artifact vs modified generator)
  at the top — score 1.84, confidence 0.76, highest of the battery — matching the real
  blocking finding, *derived* from normative-source consistency. Dimension risks: tests 0.76,
  ux 0.73, impacts 0.68, architecture 0.67 vs human reds {architecture, impacts, docs, tests} —
  3 of 4 reds in its top four. Walkthrough mode `by_logical_change` at 0.98 = the mode
  actually used.
- **PR-250:** C3 (scope beyond end-user config) correctly ranked most out-of-intent (0.63)
  and highest priority (1.53) — it drove the human Intent yellow. Ambiguous dimensions got
  0.49/0.51 (epistemically honest uncertainty).

**v1 misses → v2 fixes (pre-registered predictions, 6/8 full hits):**

| Miss (v1) | Fix (v2) | Outcome |
|---|---|---|
| Doc-drift blind on both PRs (0.43 / 0.51 vs two reds) | `doc_inventory` added to state; per-doc fan-out with neutral phrasing ("does this doc need an update to stay accurate?") | 272: 0.82–0.93 on all 5 stale docs, ranking sensible. 250: index 0.85 (the red driver), overlap pages 0.33/0.34 (accepted trade-offs) — both drift *shapes* caught |
| Intent yellows escaped the generic risk-noul (0.21 / 0.49) | Atomic decomposition: `intent_linked`, `intent_scope` (choice), `intent_verifiable` | 272: linked 0.09 (zero issues — the actual driver). 250: linked 0.94 (#126), scope `changes_broader` 0.84 — perfect separation |
| Aggregate criteria shape-brittle | A/B'd old-vs-new criteria in one call | State enrichment dominated: with inventory present even old criteria hit 0.89 on 272; new criteria *failed* on 250 (0.29) because it encoded one theory of drift ("existing page goes wrong") while 250 was the other shape ("new overlapping page, unlinked"). **Fan-out + neutral phrasing covers both shapes** |

Controls re-asked v1 questions verbatim: nouls stable within ±0.1 across runs and state
enrichment (tests 0.76→0.75, architecture 0.67→0.69, priority R5 1.84→1.77).

**Spike lessons (load-bearing for this design):**

1. **The state dominates the criteria.** Invest in the state contract, not in criteria
   perfectionism.
2. **Fan-out beats aggregates**: per-doc/per-change granularity with neutral phrasing is
   robust across PR shapes and yields actionable pointers.
3. **Atomic beats generic** on subtle dimensions (intent).
4. Jev answers the question *written* — criteria encode a theory of the judgment; a wrong
   theory returns a confidently literal "no".
5. Caveats: n=2, battery designed by us, states hand-built from dossiers. Findings are
   review prompts, not proof.

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Delivery shape | **Shared layer now** (`scripts/jev/`), pr-walkthrough first client | Other skills (plan-walkthrough, issue-triage) consume it without refactoring |
| Interaction model | **Divergence + gating** | Scanner status × Jev probability: divergence → automatic doubt; convergence-on-green may archive a section — with safeguards (below) |
| Human role | Unchanged: every judgment is the human's; Jev never produces findings or verdicts | Same stance as jev-review ("review prompts, not proof") |

## Architecture

```
scripts/jev/
  jev_call.py                 # neutral runner (stdlib only): state + battery → API → report
  batteries/
    pr-walkthrough.json       # validated battery; questions as human-editable constants
  README.md                   # state contract, how to add a battery, key handling
skills/pr-walkthrough/
  jev/                        # synced copy of scripts/jev/ (install artifact, travels with skill)
  SKILL.md                    # new "Step 1.5 — JEV pass"
scripts/tests/
  test_jev_sync.py            # diff-guard: skill copies cannot drift from the source
```

Source of truth is `scripts/jev/`. The per-skill copy exists because installers link whole
skill directories (codex/bob), and an installed skill must be self-sufficient. The diff-guard
replicates the `gen_registry` / `test_registry_sync` pattern already used in lince. Future
Jev-consuming skills get the same synced copy plus their own battery.

## State contract

Scan subagents add one structured JSON block to their compact notes (prose unchanged):

```json
{
  "pr": {"title": "...", "size": "...", "linked_issues": "...", ...},
  "declared_intent": "...",
  "normative_sources": ["..."],
  "logical_changes": [{"id": "R1", "name": "...", "what": "...", "files": ["..."], "weight": "S|M|L"}],
  "doc_inventory": [{"path": "docs/...", "covers": "what the page covers, scanner-enumerated"}],
  "repo_facts": ["explicit facts a scanner verified, e.g. 'branch is stale vs upstream/main'"],
  "scanner_status": {"intent": "green|yellow|red", "architecture": "...", "...": "..."}
}
```

`doc_inventory` and `repo_facts` are the v2 additions the spike validated as decisive.
The orchestrator merges the three scanners' blocks into
`.reviews/prs/<target>.jev-state.json` (conflicts: keep the worst status, union inventories).

## Battery v1 (`pr-walkthrough.json`) — validated modules only

| Module | Form | Why |
|---|---|---|
| `needs_update_{i}` | Noul fan-out over `doc_inventory`, neutral phrasing | The spike's star: catches both drift shapes, yields per-doc pointers |
| `intent_linked` / `intent_scope` / `intent_verifiable` | Noul / Choice / Noul | Atomic decomposition separated both intent cases perfectly |
| `priority_{id}` | Score per logical change (3-level rubric) | Ranked the blocking finding top with the highest confidence |
| `risk_{dimension}` | Noul ×7 | Secondary signal: feeds divergence detection and the gating conjunction — never sufficient alone (shape-brittle as a standalone) |
| `walkthrough_mode` | Choice | 0.98 match with the mode actually used; cheap second opinion on the skill's own heuristic |

The runner expands fan-out placeholders (`{i}` over `doc_inventory`, `{id}` over
`logical_changes`). Question text is data — edited by humans in one file, never inline in
the skill.

## Policy rules (in `jev_call.py`, thresholds as named constants at top)

- **Divergence → doubt.** `risk_{dimension}` ≥ 0.6 against scanner-green, or ≤ 0.35 against
  scanner-red/yellow → the section opens with an explicit doubt the human triages. Jev never
  emits findings directly.
- **Gating (safeguarded).** A section may be archived without walkthrough **only if**:
  scanner-green **and** `risk` noul ≤ 0.30 **and** no `needs_update` ≥ 0.5 anywhere in the
  report (conservative global conjunct — no per-section relevance computation).
  Additional prohibitions: never gate **Intent**; never gate sections with scanner DOUBTS;
  never green-by-Jev-alone (honesty rule intact). Gated sections stay visible in the dossier
  as a numbered line with the evidence ("🟢∅ archived: scanner green, JEV 0.18") and are
  un-gateable at any time from the navigation menu.
- **Ordering.** Red/yellow sections run in `priority`-desc order; confidence is displayed
  next to the score.

## Fallback, privacy, cost

- No `TYPESAFE_API_KEY` (env var, or a git-ignored file like `temp/.typesafe-key`) or network
  failure → JEV pass is skipped, one line in the dossier header ("JEV pass: skipped (no
  key)"), gating unavailable, skill otherwise identical to today.
- **Privacy:** v1 state carries compact notes and file names, never raw diff hunks —
  minimal third-party surface; declared in `scripts/jev/README.md`.
- **Cost:** ~$0.0002 per review (one batched call), < 1 s.

## SKILL.md changes (`pr-walkthrough`)

1. New **Step 1.5 — JEV pass**: assemble state → run `jev/jev_call.py` with the synced
   battery → apply policy → dossier gains a JEV column next to the traffic light, a gated
   list, and divergence doubts surfaced in the relevant walkthrough sections.
2. Scanner subagent prompt gains the structured-block requirement (`doc_inventory`,
   `repo_facts`).
3. Red Flags gains: "a section was gated that the scanner did not actually examine" and
   "gating applied despite scanner doubts".
4. Interaction-with-other-skills notes that plan-walkthrough / issue-triage may add
   batteries later.

## Testing

- Runner: mocked HTTP (stdlib `unittest.mock`); policy rules: unit tests on synthetic
  answer sets (divergence mapping, gating prohibitions, ordering).
- Battery: pure data; golden fixtures extracted from `temp/jev-spike-*.json` for response
  format regression.
- No live API in tests. `test_jev_sync.py` runs alongside `test_codex_install.py`.

## Out of scope (YAGNI)

Batteries for plan-walkthrough / issue-triage (after the pattern runs in production — no
ground truth today); Nouls on raw diff hunks; auto-verdicts; compiler/static-analysis
integration; the upstream `typesafe-ai/skills` agent skill (kept as reference reading only).
