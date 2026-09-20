"""JEV runner and policy checks (standard library only, no live API)."""

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("jev_call", SCRIPTS / "jev" / "jev_call.py")
jev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jev)

FIXTURES = SCRIPTS / "fixtures" / "jev"
BATTERY = SCRIPTS / "jev" / "batteries" / "pr-assessment.json"

STATE = {
    "pr": {"title": "t", "size": "s", "linked_issues": "none"},
    "declared_intent": "do the thing",
    "normative_sources": ["AGENTS.md"],
    "logical_changes": [
        {"id": "R1", "name": "first", "what": "adds A", "files": ["a.py"], "weight": "S"},
        {"id": "R2", "name": "second", "what": "adds B", "files": ["b.py"], "weight": "M"},
    ],
    "doc_inventory": [
        {"path": "docs/x.md", "covers": "lists the things"},
        {"path": "docs/y.md", "covers": "explains the flags"},
    ],
    "repo_facts": [],
    "scanner_status": {"intent": "green", "architecture": "green", "impacts": "red",
                       "ux": "green", "ops": "green", "docs": "yellow", "tests": "green"},
}


class ExpansionTests(unittest.TestCase):
    def setUp(self):
        self.battery = jev.load_battery(BATTERY)

    def test_fanout_over_docs_and_changes(self):
        questions = jev.expand_battery(self.battery, STATE)
        self.assertIn("needs_update_0", questions)
        self.assertIn("needs_update_1", questions)
        self.assertIn("priority_R1", questions)
        self.assertIn("priority_R2", questions)
        self.assertIn("risk_intent", questions)
        self.assertEqual(len(questions), 2 + 2 + 3 + 7 + 1)  # docs + changes + intent + risks + mode

    def test_instructions_interpolate_entry_fields(self):
        questions = jev.expand_battery(self.battery, STATE)
        self.assertIn("docs/x.md", questions["needs_update_0"]["instructions"])
        self.assertIn("lists the things", questions["needs_update_0"]["instructions"])
        self.assertIn("'first'", questions["priority_R1"]["instructions"])

    def test_empty_collections_shrink_fanout(self):
        questions = jev.expand_battery(self.battery, {"doc_inventory": [], "logical_changes": []})
        self.assertNotIn("needs_update_0", questions)
        self.assertNotIn("priority_R1", questions)
        self.assertIn("risk_intent", questions)

    def test_literal_braces_in_battery_survive_when_not_placeholders(self):
        # The mode question and criteria contain no placeholders: verbatim passthrough.
        questions = jev.expand_battery(self.battery, STATE)
        self.assertEqual(questions["walkthrough_mode"],
                         self.battery["questions"]["walkthrough_mode"])


def answers(default_risk=0.5, **overrides):
    """0.5 fires no policy rule against any scanner status — the silent baseline."""
    base = {}
    for dim in ("intent", "architecture", "impacts", "ux", "ops", "docs", "tests"):
        base[f"risk_{dim}"] = {"type": "noul", "noul": default_risk}
    for i in range(2):
        base[f"needs_update_{i}"] = {"type": "noul", "noul": 0.1}
    for cid in ("R1", "R2"):
        base[f"priority_{cid}"] = {"type": "score", "score": 1.0, "confidence": 0.5}
    base["intent_linked"] = {"type": "noul", "noul": 0.9}
    base["intent_scope"] = {"type": "choice", "choice": "changes_within_intent",
                            "probabilities": {}, "confidence": 0.9}
    base["intent_verifiable"] = {"type": "noul", "noul": 0.8}
    base.update(overrides)
    return base


class PolicyTests(unittest.TestCase):
    def test_divergence_above_green(self):
        derived = jev.apply_policy(answers(risk_tests={"type": "noul", "noul": 0.60}),
                                   STATE)
        kinds = [(d["dimension"], d["kind"]) for d in derived["doubts"]]
        self.assertIn(("tests", "jev_above_green"), kinds)

    def test_no_divergence_below_threshold(self):
        derived = jev.apply_policy(answers(risk_tests={"type": "noul", "noul": 0.59}),
                                   STATE)
        self.assertFalse(derived["doubts"])

    def test_divergence_below_red(self):
        derived = jev.apply_policy(answers(risk_impacts={"type": "noul", "noul": 0.35}),
                                   STATE)
        kinds = [(d["dimension"], d["kind"]) for d in derived["doubts"]]
        self.assertIn(("impacts", "jev_below_flag"), kinds)

    def test_green_with_middling_noul_is_silent(self):
        # 0.4 against green: neither divergence rule fires — no noise.
        derived = jev.apply_policy(answers(risk_tests={"type": "noul", "noul": 0.40}),
                                   STATE)
        self.assertFalse(derived["doubts"])

    def test_doc_flag_threshold_and_low_attention_veto(self):
        derived = jev.apply_policy(
            answers(default_risk=0.2, needs_update_0={"type": "noul", "noul": 0.50}), STATE)
        self.assertEqual([f["path"] for f in derived["doc_flags"]], ["docs/x.md"])
        # A doc flag vetoes low-attention marks entirely.
        self.assertFalse(derived["low_attention"])

    def test_low_attention_requires_green_low_noul_and_no_doc_flags(self):
        derived = jev.apply_policy(answers(default_risk=0.2), STATE)
        marked = {m["dimension"] for m in derived["low_attention"]}
        # green + noul 0.2: architecture, ux, ops, tests qualify; intent never; docs is yellow.
        self.assertEqual(marked, {"architecture", "ux", "ops", "tests"})

    def test_intent_never_low_attention_even_when_green_and_low(self):
        derived = jev.apply_policy(
            answers(risk_intent={"type": "noul", "noul": 0.05}), STATE)
        self.assertFalse(any(m["dimension"] == "intent" for m in derived["low_attention"]))

    def test_priorities_sorted_desc(self):
        derived = jev.apply_policy(
            answers(priority_R1={"type": "score", "score": 1.8, "confidence": 0.7},
                     priority_R2={"type": "score", "score": 0.9, "confidence": 0.4}),
            STATE)
        self.assertEqual([p["id"] for p in derived["priorities"]], ["R1", "R2"])

    def test_intent_flags(self):
        derived = jev.apply_policy(
            answers(intent_linked={"type": "noul", "noul": 0.09},
                    intent_scope={"type": "choice", "choice": "changes_broader",
                                  "probabilities": {}, "confidence": 0.84},
                    intent_verifiable={"type": "noul", "noul": 0.30}),
            STATE)
        flags = {f["flag"] for f in derived["intent_flags"]}
        self.assertEqual(flags, {"no_linked_spec", "changes_broader", "intent_not_verifiable"})

    def test_missing_scanner_status_noted(self):
        state = dict(STATE, scanner_status={})
        derived = jev.apply_policy(answers(), state)
        self.assertTrue(any("scanner_status" in n for n in derived["notes"]))
        self.assertFalse(derived["doubts"])


class GoldenResponseTests(unittest.TestCase):
    """The parser and policy must keep handling real API responses from the spike."""

    def test_pr272_fixture(self):
        data = json.loads((FIXTURES / "api-response-pr272-v2.json").read_text())
        state = dict(STATE, doc_inventory=[{"path": f"docs/d{i}.md", "covers": "c"} for i in range(5)])
        derived = jev.apply_policy(data["answers"], state)
        self.assertEqual([f["path"] for f in derived["doc_flags"]],
                         ["docs/d0.md", "docs/d1.md", "docs/d2.md", "docs/d3.md", "docs/d4.md"])
        self.assertTrue(any("no linked issue/spec" in f["say"] for f in derived["intent_flags"]))

    def test_pr250_fixture(self):
        data = json.loads((FIXTURES / "api-response-pr250-v2.json").read_text())
        state = dict(STATE, doc_inventory=[{"path": "docs/user/index.md", "covers": "index"},
                                           {"path": "docs/user/installation.md", "covers": "install"},
                                           {"path": "docs/user/agent-configuration.md", "covers": "config"}])
        derived = jev.apply_policy(data["answers"], state)
        # index.md at 0.85 flags; the two overlap pages (0.33/0.34) stay below 0.50.
        self.assertEqual([f["path"] for f in derived["doc_flags"]], ["docs/user/index.md"])


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.state_path = self.dir / "state.json"
        self.state_path.write_text(json.dumps(STATE))
        self.out_path = self.dir / "report.json"
        self.fixture = json.loads((FIXTURES / "api-response-pr272-v2.json").read_text())

    def run_main(self, *extra):
        argv = ["--state", str(self.state_path), "--battery", str(BATTERY),
                "--out", str(self.out_path), *extra]
        with redirect_stdout(io.StringIO()) as stdout:
            code = jev.main(argv)
        return code, stdout.getvalue()

    def test_end_to_end_with_mocked_api(self):
        response = json.dumps(dict(self.fixture)).encode()
        with patch.object(jev.urllib.request, "urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value.read.return_value = response
            with patch.dict("os.environ", {"TYPESAFE_API_KEY": "test-key"}):
                code, output = self.run_main()
        self.assertEqual(code, 0)
        report = json.loads(self.out_path.read_text())
        self.assertIn("derived", report)
        self.assertEqual(report["battery"]["name"], "pr-assessment")
        # The pr272 golden response carries needs_update + intent answers: those surface.
        self.assertIn("DOC    docs/x.md", output)
        self.assertIn("INTENT no linked issue/spec", output)

    def test_missing_key_exits_2(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit) as ctx:
                self.run_main()
            self.assertEqual(ctx.exception.code, 2)

    def test_api_error_after_retries_exits_3(self):
        import urllib.error
        with patch.object(jev.urllib.request, "urlopen",
                          side_effect=urllib.error.HTTPError(
                              "url", 500, "boom", {}, io.BytesIO(b"oops"))), \
             patch.object(jev.time, "sleep"), \
             patch.dict("os.environ", {"TYPESAFE_API_KEY": "test-key"}):
            with self.assertRaises(SystemExit) as ctx:
                self.run_main()
            self.assertEqual(ctx.exception.code, 3)


if __name__ == "__main__":
    unittest.main()
