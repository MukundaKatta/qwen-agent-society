"""Tests for the shared blackboard.

Standard-library ``unittest`` only (no third-party deps). Run with::

    python -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qwen_society import Blackboard  # noqa: E402
from qwen_society.types import Message, MessageKind  # noqa: E402


class BlackboardTests(unittest.TestCase):
    def test_post_returns_the_message(self):
        bb = Blackboard()
        msg = Message("a", MessageKind.PARTIAL, "a", "v1", 1)
        self.assertIs(bb.post(msg), msg)
        self.assertEqual(len(bb), 1)

    def test_post_and_latest_partials(self):
        bb = Blackboard()
        bb.post(Message("a", MessageKind.PARTIAL, "a", "v1", 1))
        bb.post(Message("a", MessageKind.PARTIAL, "a", "v2", 2))
        bb.post(Message("b", MessageKind.PARTIAL, "b", "x", 1))
        lp = bb.latest_partials()
        self.assertEqual(lp["a"], "v2")  # later round overwrites earlier
        self.assertEqual(lp["b"], "x")
        self.assertEqual(len(bb), 3)

    def test_latest_partials_ignores_non_partial_kinds(self):
        bb = Blackboard()
        bb.post(Message("p", MessageKind.PLAN, "plan", "the plan", 0))
        bb.post(Message("c", MessageKind.CRITIQUE, "critique", "REVISE", 1))
        self.assertEqual(bb.latest_partials(), {})

    def test_by_kind(self):
        bb = Blackboard()
        bb.post(Message("p", MessageKind.PLAN, "plan", "...", 0))
        bb.post(Message("a", MessageKind.PARTIAL, "a", "...", 1))
        self.assertEqual(len(bb.by_kind(MessageKind.PLAN)), 1)
        self.assertEqual(len(bb.by_kind(MessageKind.PARTIAL)), 1)
        self.assertEqual(len(bb.by_kind(MessageKind.FINAL)), 0)

    def test_all_returns_a_copy(self):
        bb = Blackboard()
        bb.post(Message("p", MessageKind.PLAN, "plan", "x", 0))
        snapshot = bb.all()
        snapshot.clear()
        # Mutating the returned list must not affect the blackboard.
        self.assertEqual(len(bb), 1)

    def test_transcript_is_serializable(self):
        bb = Blackboard()
        bb.post(Message("p", MessageKind.PLAN, "plan", "x", 0))
        t = bb.transcript()
        self.assertEqual(t[0]["kind"], "plan")  # enum rendered to its value
        self.assertEqual(t[0]["author"], "p")
        self.assertEqual(t[0]["round"], 0)


if __name__ == "__main__":
    unittest.main()
