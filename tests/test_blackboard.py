"""Tests for the shared blackboard."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qwen_society import Blackboard  # noqa: E402
from qwen_society.types import Message, MessageKind  # noqa: E402


def test_post_and_latest_partials():
    bb = Blackboard()
    bb.post(Message("a", MessageKind.PARTIAL, "a", "v1", 1))
    bb.post(Message("a", MessageKind.PARTIAL, "a", "v2", 2))
    bb.post(Message("b", MessageKind.PARTIAL, "b", "x", 1))
    lp = bb.latest_partials()
    assert lp["a"] == "v2"  # later round overwrites earlier
    assert lp["b"] == "x"
    assert len(bb) == 3


def test_by_kind():
    bb = Blackboard()
    bb.post(Message("p", MessageKind.PLAN, "plan", "...", 0))
    bb.post(Message("a", MessageKind.PARTIAL, "a", "...", 1))
    assert len(bb.by_kind(MessageKind.PLAN)) == 1
    assert len(bb.by_kind(MessageKind.PARTIAL)) == 1


def test_transcript_is_serializable():
    bb = Blackboard()
    bb.post(Message("p", MessageKind.PLAN, "plan", "x", 0))
    t = bb.transcript()
    assert t[0]["kind"] == "plan"  # enum rendered to its value
    assert t[0]["author"] == "p"
