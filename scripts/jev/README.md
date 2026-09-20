# JEV shared judgment layer

A neutral runner that turns a *state* plus a *battery* of typed questions into a
calibrated assessment via TypeSafe's Jev (`api.typesafe.ai/v1/systemone`,
[System One models](https://docs.typesafe.ai/)). Orchestration and policy stay in
code; the model makes bounded, atomic judgments. Skills consume this layer; they
never talk to the API directly.

Design and evidence: `docs/superpowers/specs/2026-09-20-jev-shared-judgment-layer-design.md`.

## Layout

```
scripts/jev/jev_call.py              runner + policy (thresholds as constants at top)
scripts/jev/batteries/<skill>.json   question batteries — constants, human-editable
skills/<skill>/jev/                  synced copy per consuming skill (install artifact)
scripts/tests/test_jev_sync.py       diff-guard: copies must not drift (run with --fix to sync)
```

## State contract

One JSON file per target, assembled by the consuming skill (merge rule for
multiple scanners: worst status wins, inventories union):

```json
{
  "pr": {"title": "...", "size": "+226/-3, 11 files", "linked_issues": "none"},
  "declared_intent": "short verbatim summary of what the PR says it does",
  "normative_sources": ["contract/yardstick docs, with what each establishes"],
  "logical_changes": [
    {"id": "R1", "name": "...", "what": "neutral scanner-level description",
     "files": ["..."], "weight": "S|M|L"}
  ],
  "doc_inventory": [{"path": "docs/...", "covers": "what the page covers"}],
  "repo_facts": ["explicit facts a scanner verified, e.g. 'branch stale vs upstream/main'"],
  "scanner_status": {"intent": "green|yellow|red", "architecture": "...", "impacts": "...",
                      "ux": "...", "ops": "...", "docs": "...", "tests": "..."}
}
```

`doc_inventory` and `repo_facts` are not optional decoration — the field spike
showed the state dominates the criteria: the same questions went from blind to
sharp when the doc inventory entered the state.

## Battery authoring — the rules the spike paid for

1. **State beats criteria.** When a judgment is weak, enrich the state first;
   polish question text second.
2. **Fan-out beats aggregates.** Per-item questions (`needs_update_{i}` over
   `doc_inventory`, `priority_{id}` over `logical_changes`) with *neutral*
   phrasing are robust across target shapes and yield actionable pointers.
   Aggregate dimension questions are shape-brittle: they encode one theory of
   the judgment and Jev answers the question *written*.
3. **Atomic beats generic.** Decompose subtle dimensions (intent) into single-
   fact questions rather than one umbrella risk question.
4. Ids containing `{i}` fan out over `doc_inventory`; `{id}` over
   `logical_changes`; inside `instructions` the entry fields interpolate
   (`{path}`, `{covers}`, `{name}`, `{what}`, `{i}`, `{id}`).
5. Noul criteria carry `true`/`false` with a `what` (and optionally `examples`);
   Score criteria are 2–10 ordered level descriptions; Choice criteria map
   option → description.

## Policy (in the runner)

- **Divergence → doubt:** risk noul ≥ 0.60 against a scanner-green dimension,
  or ≤ 0.35 against scanner-red/yellow, becomes an explicit doubt for the human.
- **Doc flags:** any `needs_update` noul ≥ 0.50 (also vetoes low-attention marks).
- **Low attention:** scanner-green **and** noul ≤ 0.30 **and** no doc flags —
  and never for `intent`.
- **Priorities:** logical changes sorted by priority score desc, confidence shown.
- Jev never produces findings or verdicts. Doubts are triaged by a human.

## Keys, privacy, cost

- Key resolution: `TYPESAFE_API_KEY` env var, else `--key-file`. Never commit a
  key; a git-ignored file (e.g. `temp/.typesafe-key`) works for local runs.
- The state carries compact notes and file names — **never raw diff hunks**.
  Keep it that way unless a battery is redesigned around it, and say so in the
  battery's `notes` when you do.
- ~$0.042 per million input tokens, output free: a typical assessment is a
  single batched call, well under $0.001, in under a second.

## Exit codes

`0` assessment written · `2` configuration/key/state error · `3` API error after
retries (429/529 use exponential backoff per the API docs).
