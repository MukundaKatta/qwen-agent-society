"""Tests for the society coordinator: plan, dispatch, critic loop, synthesize.

Standard-library ``unittest`` only (no third-party deps). Run with::

    python -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qwen_society import FakeQwenClient, Society, parse_subtasks  # noqa: E402


class ParseSubtasksTests(unittest.TestCase):
    def test_parse_subtasks(self):
        st = parse_subtasks("triage: do x\ndiagnose: do y\n\njunk line without colon")
        self.assertEqual(len(st), 2)
        self.assertEqual(st[0].role, "triage")
        self.assertEqual(st[0].task, "do x")

    def test_parse_subtasks_lowercases_role_and_strips(self):
        st = parse_subtasks("  TRIAGE :  assess impact  ")
        self.assertEqual(len(st), 1)
        self.assertEqual(st[0].role, "triage")
        self.assertEqual(st[0].task, "assess impact")

    def test_parse_subtasks_skips_lines_without_a_task(self):
        # A role with an empty task (just "role:") must not produce a subtask.
        st = parse_subtasks("triage:\nremediate: apply the fix")
        self.assertEqual([s.role for s in st], ["remediate"])

    def test_parse_subtasks_keeps_colons_in_the_task(self):
        st = parse_subtasks("communicate: status: investigating outage")
        self.assertEqual(len(st), 1)
        self.assertEqual(st[0].task, "status: investigating outage")

    def test_parse_subtasks_empty_plan(self):
        self.assertEqual(parse_subtasks(""), [])


class SocietyRunTests(unittest.TestCase):
    def test_society_runs_critic_loop_then_approves(self):
        r = Society(FakeQwenClient(), max_rounds=3).run("checkout 500s")
        self.assertTrue(r.approved)
        self.assertEqual(r.rounds, 2)  # round 1 REVISE (vague fix), round 2 APPROVE (rollback)
        self.assertIn("rollback", r.final.lower())

    def test_result_records_the_original_task(self):
        r = Society(FakeQwenClient(), max_rounds=3).run("checkout 500s")
        self.assertEqual(r.task, "checkout 500s")

    def test_transcript_has_all_kinds(self):
        r = Society(FakeQwenClient(), max_rounds=3).run("checkout 500s")
        kinds = {m["kind"] for m in r.transcript}
        self.assertTrue({"plan", "partial", "critique", "final"} <= kinds)

    def test_transcript_starts_with_plan_and_ends_with_final(self):
        r = Society(FakeQwenClient(), max_rounds=3).run("checkout 500s")
        self.assertEqual(r.transcript[0]["kind"], "plan")
        self.assertEqual(r.transcript[-1]["kind"], "final")

    def test_to_dict_round_trips_the_result(self):
        r = Society(FakeQwenClient(), max_rounds=3).run("checkout 500s")
        d = r.to_dict()
        self.assertEqual(d["task"], r.task)
        self.assertEqual(d["final"], r.final)
        self.assertEqual(d["approved"], r.approved)
        self.assertEqual(d["rounds"], r.rounds)
        self.assertEqual(d["transcript"], r.transcript)

    def test_always_approve_runs_one_round(self):
        def responder(spec, content):
            if spec.name == "planner":
                return "triage: x\nremediate: y"
            if spec.name == "critic":
                return "APPROVE"
            if spec.name == "synthesizer":
                return "final plan"
            return "ok"

        r = Society(FakeQwenClient(responder), max_rounds=3).run("t")
        self.assertEqual(r.rounds, 1)
        self.assertTrue(r.approved)

    def test_never_approve_caps_at_max_rounds(self):
        def responder(spec, content):
            if spec.name == "planner":
                return "triage: x"
            if spec.name == "critic":
                return "REVISE: never satisfied"
            if spec.name == "synthesizer":
                return "final anyway"
            return "ok"

        r = Society(FakeQwenClient(responder), max_rounds=2).run("t")
        self.assertFalse(r.approved)
        self.assertEqual(r.rounds, 2)
        # Even without approval the synthesizer still produces a final answer.
        self.assertEqual(r.final, "final anyway")

    def test_critic_notes_are_passed_back_on_revision(self):
        seen_notes = []

        def responder(spec, content):
            if spec.name == "planner":
                return "remediate: fix it"
            if spec.name == "remediate":
                seen_notes.append("CRITIC_NOTES: NONE" in content)
                return "some remediation"
            if spec.name == "critic":
                # Approve only on the second round so we see one revision.
                return "APPROVE" if len(seen_notes) >= 2 else "REVISE: be concrete"
            if spec.name == "synthesizer":
                return "done"
            return "ok"

        Society(FakeQwenClient(responder), max_rounds=3).run("t")
        # First dispatch has no notes; the revision dispatch carries the critic's note.
        self.assertEqual(seen_notes, [True, False])

    def test_unknown_role_uses_generic_specialist(self):
        def responder(spec, content):
            if spec.name == "planner":
                return "weirdrole: do something special"
            if spec.name == "critic":
                return "APPROVE"
            if spec.name == "synthesizer":
                return "done"
            return f"{spec.name} handled it"

        r = Society(FakeQwenClient(responder), max_rounds=2).run("t")
        partial_authors = {m["author"] for m in r.transcript if m["kind"] == "partial"}
        self.assertIn("weirdrole", partial_authors)
        self.assertTrue(r.approved)


if __name__ == "__main__":
    unittest.main()
