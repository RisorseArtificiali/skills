#!/usr/bin/env python3
"""Neutral JEV runner: state + battery -> TypeSafe API -> assessment report.

Standard library only. The battery (questions) lives in a JSON data file so
humans review and edit it without touching code. This runner owns the policy:
divergence doubts, doc flags, priorities, low-attention marks. Thresholds are
named constants below — tune them here, nowhere else.

Exit codes: 0 ok; 2 configuration/key error; 3 API error after retries.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
DEFAULT_MODEL = "jev-latest"
RETRYABLE_STATUS = {429, 529}
RETRY_ATTEMPTS = 4
RETRY_BACKOFF_S = 2.0

# --- policy thresholds (spike-validated; see docs/superpowers/specs/2026-09-20-*.md) ---
DIVERGE_HIGH = 0.60   # risk noul >= this against scanner-green -> doubt
DIVERGE_LOW = 0.35    # risk noul <= this against scanner-red/yellow -> doubt
DOC_FLAG = 0.50       # needs_update noul >= this -> doc flag (veto for low-attention)
LOW_ATT_MAX = 0.30    # risk noul <= this (with scanner green, no doc flags) -> low attention
INTENT_NEVER_LOW = True  # Intent is never marked low-attention, whatever the numbers say


class _EntryDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def load_battery(path):
    battery = json.loads(Path(path).read_text())
    if not isinstance(battery.get("questions"), dict) or not battery["questions"]:
        raise ValueError(f"Battery {path} has no questions")
    return battery


def expand_battery(battery, state):
    """Expand question-id templates over the state's fan-out collections.

    Ids containing "{i}" fan out over state["doc_inventory"]; ids containing
    "{id}" over state["logical_changes"]. Inside `instructions`, the same
    placeholders plus each entry's fields ({path}, {covers}, {name}, {what})
    are interpolated. Questions without placeholders pass through unchanged.
    """
    docs = state.get("doc_inventory", [])
    changes = state.get("logical_changes", [])
    questions = {}
    for qid, question in battery["questions"].items():
        if "{i}" in qid:
            for i, doc in enumerate(docs):
                questions[qid.format(i=i)] = _render(question, _EntryDict(i=i, **doc))
        elif "{id}" in qid:
            for change in changes:
                questions[qid.format(id=change["id"])] = _render(question, _EntryDict(**change))
        else:
            questions[qid] = question
    return questions


def _render(question, fields):
    rendered = dict(question)
    rendered["instructions"] = question["instructions"].format_map(fields)
    return rendered


def load_key(key_file):
    import os
    key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if key:
        return key
    if key_file:
        path = Path(key_file)
        if path.is_file():
            key = path.read_text().strip()
            if key:
                return key
    sys.stderr.write(
        "No API key: set TYPESAFE_API_KEY or pass --key-file (see scripts/jev/README.md)\n")
    raise SystemExit(2)


def call_api(state, questions, key, model=DEFAULT_MODEL, endpoint=API_ENDPOINT):
    payload = json.dumps({"state": state, "model": model, "questions": questions}).encode()
    last_error = None
    for attempt in range(RETRY_ATTEMPTS):
        request = urllib.request.Request(
            endpoint, data=payload, method="POST",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read())
            data["elapsed_ms"] = round((time.perf_counter() - started) * 1000)
            return data
        except urllib.error.HTTPError as error:
            body = error.read().decode(errors="replace")[:300]
            last_error = f"HTTP {error.code}: {body}"
            if error.code in RETRYABLE_STATUS and attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_BACKOFF_S * (2 ** attempt))
                continue
            break
        except (urllib.error.URLError, TimeoutError) as error:
            last_error = f"network: {error}"
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_BACKOFF_S * (2 ** attempt))
                continue
            break
    sys.stderr.write(f"API error after retries: {last_error}\n")
    raise SystemExit(3)


def apply_policy(answers, state):
    """Derive the assessment flags from raw answers. Pure function, no I/O."""
    derived = {"doubts": [], "doc_flags": [], "low_attention": [], "intent_flags": [],
               "priorities": [], "notes": []}
    status = state.get("scanner_status") or {}
    if not status:
        derived["notes"].append("no scanner_status in state: divergence checks skipped")

    for dim, scanner in sorted(status.items()):
        answer = answers.get(f"risk_{dim}")
        if not answer or answer.get("type") != "noul":
            continue
        p = answer["noul"]
        if scanner == "green" and p >= DIVERGE_HIGH:
            derived["doubts"].append(
                {"kind": "jev_above_green", "dimension": dim, "noul": p,
                 "say": f"scanner green but JEV risk {p:.2f}: worth a look"})
        if scanner in ("yellow", "red") and p <= DIVERGE_LOW:
            derived["doubts"].append(
                {"kind": "jev_below_flag", "dimension": dim, "noul": p,
                 "say": f"scanner {scanner} but JEV risk {p:.2f}: verify the scanner's claim"})

    for qid, answer in sorted(answers.items()):
        if qid.startswith("needs_update_") and answer.get("type") == "noul" \
                and answer["noul"] >= DOC_FLAG:
            index = qid.rsplit("_", 1)[-1]
            docs = state.get("doc_inventory", [])
            path = docs[int(index)]["path"] if index.isdigit() and int(index) < len(docs) else qid
            derived["doc_flags"].append({"path": path, "noul": answer["noul"]})

    for change in state.get("logical_changes", []):
        answer = answers.get(f"priority_{change['id']}")
        if answer and answer.get("type") == "score":
            derived["priorities"].append(
                {"id": change["id"], "name": change.get("name", change["id"]),
                 "score": answer["score"], "confidence": answer.get("confidence")})
    derived["priorities"].sort(key=lambda entry: entry["score"], reverse=True)

    linked = answers.get("intent_linked", {})
    if linked.get("type") == "noul" and linked["noul"] <= DIVERGE_LOW:
        derived["intent_flags"].append(
            {"flag": "no_linked_spec", "noul": linked["noul"],
             "say": "no linked issue/spec behind the change (JEV)"})
    scope = answers.get("intent_scope", {})
    if scope.get("type") == "choice" and scope.get("choice") not in (None, "changes_within_intent"):
        derived["intent_flags"].append(
            {"flag": scope["choice"], "confidence": scope.get("confidence"),
             "say": f"scope: {scope['choice']} (JEV)"})
    verifiable = answers.get("intent_verifiable", {})
    if verifiable.get("type") == "noul" and verifiable["noul"] <= 0.40:
        derived["intent_flags"].append(
            {"flag": "intent_not_verifiable", "noul": verifiable["noul"],
             "say": "declared intent too vague to verify scope against (JEV)"})

    doc_veto = bool(derived["doc_flags"])
    for dim, scanner in sorted(status.items()):
        if INTENT_NEVER_LOW and dim == "intent":
            continue
        answer = answers.get(f"risk_{dim}")
        if scanner == "green" and answer and answer.get("type") == "noul" \
                and answer["noul"] <= LOW_ATT_MAX and not doc_veto:
            derived["low_attention"].append(
                {"dimension": dim, "noul": answer["noul"],
                 "say": f"scanner green + JEV {answer['noul']:.2f} + no doc flags: low attention"})
    return derived


def summarize(report):
    lines = [f"model {report.get('model')} | {report.get('elapsed_ms')} ms | "
             f"usage {report.get('usage')}"]
    derived = report["derived"]
    for doubt in derived["doubts"]:
        lines.append(f"  DOUBT  {doubt['say']}")
    for flag in derived["doc_flags"]:
        lines.append(f"  DOC    {flag['path']} (noul {flag['noul']:.2f})")
    for flag in derived["intent_flags"]:
        lines.append(f"  INTENT {flag['say']}")
    for entry in derived["priorities"]:
        conf = f" conf {entry['confidence']:.2f}" if entry.get("confidence") is not None else ""
        lines.append(f"  PRIO   {entry['id']} {entry['name']}: {entry['score']:.2f}{conf}")
    for mark in derived["low_attention"]:
        lines.append(f"  LOW    {mark['say']}")
    for note in derived["notes"]:
        lines.append(f"  NOTE   {note}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, help="state JSON file (see README.md)")
    parser.add_argument("--battery", required=True, help="battery JSON file")
    parser.add_argument("--out", help="report JSON file (default: next to the state)")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--key-file", help="file holding the API key (env TYPESAFE_API_KEY wins)")
    parser.add_argument("--endpoint", default=API_ENDPOINT)
    args = parser.parse_args(argv)

    state = json.loads(Path(args.state).read_text())
    battery = load_battery(args.battery)
    questions = expand_battery(battery, state)
    if not questions:
        sys.stderr.write("Battery expanded to zero questions: state lacks doc_inventory/"
                         "logical_changes?\n")
        raise SystemExit(2)
    key = load_key(args.key_file)
    response = call_api(state, questions, key, model=args.model, endpoint=args.endpoint)
    response["derived"] = apply_policy(response.get("answers", {}), state)
    response["battery"] = {"name": battery.get("name"), "version": battery.get("version")}

    out = Path(args.out) if args.out else Path(args.state).with_suffix(".jev-report.json")
    out.write_text(json.dumps(response, indent=2))
    print(summarize(response))
    print(f"report -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
