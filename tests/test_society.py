"""Tests for the society coordinator: plan, dispatch, critic loop, synthesize."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qwen_society import FakeQwenClient, Society, parse_subtasks  # noqa: E402


def test_parse_subtasks():
    st = parse_subtasks("triage: do x\ndiagnose: do y\n\njunk line without colon")
    assert len(st) == 2
    assert st[0].role == "triage" and st[0].task == "do x"


def test_society_runs_critic_loop_then_approves():
    r = Society(FakeQwenClient(), max_rounds=3).run("checkout 500s")
    assert r.approved is True
    assert r.rounds == 2  # round 1 REVISE (vague fix), round 2 APPROVE (rollback)
    assert "rollback" in r.final.lower()


def test_transcript_has_all_kinds():
    r = Society(FakeQwenClient(), max_rounds=3).run("checkout 500s")
    kinds = {m["kind"] for m in r.transcript}
    assert {"plan", "partial", "critique", "final"} <= kinds


def test_always_approve_runs_one_round():
    def responder(spec, content):
        if spec.name == "planner":
            return "triage: x\nremediate: y"
        if spec.name == "critic":
            return "APPROVE"
        if spec.name == "synthesizer":
            return "final plan"
        return "ok"

    r = Society(FakeQwenClient(responder), max_rounds=3).run("t")
    assert r.rounds == 1 and r.approved is True


def test_never_approve_caps_at_max_rounds():
    def responder(spec, content):
        if spec.name == "planner":
            return "triage: x"
        if spec.name == "critic":
            return "REVISE: never satisfied"
        if spec.name == "synthesizer":
            return "final anyway"
        return "ok"

    r = Society(FakeQwenClient(responder), max_rounds=2).run("t")
    assert r.approved is False
    assert r.rounds == 2


def test_unknown_role_uses_generic_specialist():
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
    assert "weirdrole" in partial_authors
    assert r.approved is True
