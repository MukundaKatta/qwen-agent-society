"""Tests for the typed primitives: enums, frozen dataclasses, serialization.

Standard-library ``unittest`` only (no third-party deps). Run with::

    python -m unittest discover -s tests
"""

import dataclasses
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qwen_society.types import (  # noqa: E402
    AgentSpec,
    Message,
    MessageKind,
    SocietyResult,
    Subtask,
    Verdict,
)


class EnumTests(unittest.TestCase):
    def test_message_kind_values(self):
        self.assertEqual(MessageKind.PLAN.value, "plan")
        self.assertEqual(MessageKind.PARTIAL.value, "partial")
        self.assertEqual(MessageKind.CRITIQUE.value, "critique")
        self.assertEqual(MessageKind.FINAL.value, "final")

    def test_message_kind_is_a_str_enum(self):
        # str-mixed enum keeps equality with the raw string value.
        self.assertEqual(MessageKind.PLAN, "plan")

    def test_verdict_values(self):
        self.assertEqual(Verdict.APPROVE.value, "approve")
        self.assertEqual(Verdict.REVISE.value, "revise")


class FrozenDataclassTests(unittest.TestCase):
    def test_agent_spec_is_frozen(self):
        spec = AgentSpec("planner", "decompose", "You plan.")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            spec.name = "other"  # type: ignore[misc]

    def test_subtask_is_frozen(self):
        st = Subtask(role="triage", task="assess")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            st.role = "diagnose"  # type: ignore[misc]


class MessageTests(unittest.TestCase):
    def test_to_dict_renders_enum_to_value(self):
        m = Message("planner", MessageKind.PLAN, "plan", "the plan", 0)
        d = m.to_dict()
        self.assertEqual(
            d,
            {
                "author": "planner",
                "kind": "plan",
                "topic": "plan",
                "content": "the plan",
                "round": 0,
            },
        )

    def test_round_defaults_to_zero(self):
        m = Message("a", MessageKind.PARTIAL, "a", "x")
        self.assertEqual(m.round, 0)


class SocietyResultTests(unittest.TestCase):
    def test_transcript_defaults_to_empty_list(self):
        r = SocietyResult(task="t", final="f", rounds=1, approved=True)
        self.assertEqual(r.transcript, [])

    def test_to_dict_contains_all_fields(self):
        r = SocietyResult(
            task="t", final="f", rounds=2, approved=False, transcript=[{"k": 1}]
        )
        self.assertEqual(
            r.to_dict(),
            {
                "task": "t",
                "final": "f",
                "rounds": 2,
                "approved": False,
                "transcript": [{"k": 1}],
            },
        )


if __name__ == "__main__":
    unittest.main()
