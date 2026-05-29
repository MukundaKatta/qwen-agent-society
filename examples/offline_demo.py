"""Offline, credential-free demo of qwen-agent-society.

Runs the REAL multi-agent coordinator against a deterministic, role-aware fake
Qwen client. No API key, no network.

    python examples/offline_demo.py

It shows a society resolving an incident: the planner decomposes the task, the
specialists work on the shared blackboard, the critic sends the remediation back
for a concrete action (round 1), the specialist revises (round 2), the critic
approves, and the synthesizer produces the final plan.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qwen_society import FakeQwenClient, Society  # noqa: E402


def main() -> None:
    society = Society(FakeQwenClient(), max_rounds=3)
    result = society.run("checkout is throwing 500s for all users since 08:00")

    print("=" * 68)
    print(f"TASK: {result.task}")
    print("=" * 68)
    for m in result.transcript:
        tag = f"[r{m['round']}] {m['author']}/{m['kind']}"
        print(f"\n{tag}:")
        for line in m["content"].splitlines():
            print(f"    {line}")

    print("\n" + "=" * 68)
    print(f"rounds: {result.rounds}   approved: {result.approved}")
    print(f"FINAL: {result.final}")
    print("=" * 68)
    print("\nNote: the critic gated the remediation until it named a concrete,")
    print("reversible action; the society revised and converged, all on the blackboard.")


if __name__ == "__main__":
    main()
