"""Tests for the Qwen client key-guard and the planner-output parser.

These cover public behavior that the offline suite otherwise leaves untested:
the live client refusing to start without credentials, and parse_subtasks
edge cases (whitespace, blank role/task, multiple colons).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qwen_society import QwenClient, parse_subtasks  # noqa: E402


def test_qwen_client_requires_key(monkeypatch):
    # The key check must run before the optional openai import, so this raises a
    # clear RuntimeError even with no API key and no openai installed.
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="DASHSCOPE_API_KEY"):
        QwenClient()


def test_parse_subtasks_strips_and_lowercases_role():
    st = parse_subtasks("  TRIAGE :  assess the impact  ")
    assert len(st) == 1
    assert st[0].role == "triage"
    assert st[0].task == "assess the impact"


def test_parse_subtasks_keeps_colons_in_task():
    st = parse_subtasks("remediate: rollback: to v2.3.7")
    assert len(st) == 1
    assert st[0].role == "remediate"
    assert st[0].task == "rollback: to v2.3.7"


def test_parse_subtasks_skips_blank_role_or_task():
    st = parse_subtasks(": orphan task\nremediate:\n\ntriage: ok")
    assert [(s.role, s.task) for s in st] == [("triage", "ok")]


def test_parse_subtasks_empty_plan_yields_nothing():
    assert parse_subtasks("") == []
    assert parse_subtasks("no colons here\nstill none") == []
