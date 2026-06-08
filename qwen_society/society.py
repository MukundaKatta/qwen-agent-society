"""The coordinator: plan -> dispatch to specialists -> critique -> (revise) -> synthesize.

Agents never call each other directly; they collaborate through the shared
blackboard. The critic gates progress: while it asks for revision (and rounds
remain), the flagged work is redone with the critic's notes. Bounded by
max_rounds so the society always terminates.
"""

from __future__ import annotations

from typing import Optional, Protocol

from .blackboard import Blackboard
from .roles import CRITIC, PLANNER, SYNTHESIZER, default_roster, generic_specialist
from .types import AgentSpec, Message, MessageKind, SocietyResult, Subtask


class _Client(Protocol):
    def complete(self, spec: AgentSpec, content: str) -> str: ...


def parse_subtasks(plan: str) -> list[Subtask]:
    """Parse the planner's 'role: subtask' lines into Subtasks."""
    out: list[Subtask] = []
    for line in plan.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        role, task = line.split(":", 1)
        role, task = role.strip().lower(), task.strip()
        if role and task:
            out.append(Subtask(role=role, task=task))
    return out


class Society:
    def __init__(
        self,
        client: _Client,
        roster: Optional[dict[str, AgentSpec]] = None,
        max_rounds: int = 2,
    ) -> None:
        self.client = client
        self.roster = roster or default_roster()
        self.max_rounds = max_rounds

    def _spec(self, role: str) -> AgentSpec:
        return self.roster.get(role) or generic_specialist(role)

    def run(self, task: str) -> SocietyResult:
        bb = Blackboard()

        plan_out = self.client.complete(
            self.roster.get("planner", PLANNER), f"TASK: {task}"
        )
        bb.post(Message("planner", MessageKind.PLAN, "plan", plan_out, 0))
        subtasks = parse_subtasks(plan_out)

        critic_notes: dict[str, str] = {}
        approved = False
        rounds = 0

        for rnd in range(1, self.max_rounds + 1):
            rounds = rnd
            for st in subtasks:
                notes = critic_notes.get(st.role, "NONE")
                content = f"ROLE: {st.role}\nSUBTASK: {st.task}\nCRITIC_NOTES: {notes}"
                out = self.client.complete(self._spec(st.role), content)
                bb.post(Message(st.role, MessageKind.PARTIAL, st.role, out, rnd))

            partials = bb.latest_partials()
            crit_content = "PARTIALS:\n" + "\n".join(
                f"{r}: {c}" for r, c in partials.items()
            )
            crit_out = self.client.complete(
                self.roster.get("critic", CRITIC), crit_content
            )
            bb.post(Message("critic", MessageKind.CRITIQUE, "critique", crit_out, rnd))

            if crit_out.strip().upper().startswith("APPROVE"):
                approved = True
                break
            note = (
                crit_out.split(":", 1)[1].strip()
                if ":" in crit_out
                else crit_out.strip()
            )
            critic_notes = {st.role: note for st in subtasks}

        partials = bb.latest_partials()
        syn_content = "APPROVED PARTIALS:\n" + "\n".join(
            f"{r}: {c}" for r, c in partials.items()
        )
        final = self.client.complete(
            self.roster.get("synthesizer", SYNTHESIZER), syn_content
        )
        bb.post(Message("synthesizer", MessageKind.FINAL, "final", final, rounds))

        return SocietyResult(
            task=task,
            final=final,
            rounds=rounds,
            approved=approved,
            transcript=bb.transcript(),
        )
