"""Built-in society roles. Each is a Qwen agent with a distinct capability.

The default roster is an incident-response society, but any roster of AgentSpecs
works; the coordinator dispatches subtasks to roles by name and falls back to a
generic specialist for roles the planner invents.
"""

from __future__ import annotations

from .types import AgentSpec

PLANNER = AgentSpec(
    name="planner",
    capability="decompose a task into role-tagged subtasks",
    system_prompt=(
        "You are the Planner in a multi-agent society. Decompose the task into 2-4 subtasks. "
        "Output one per line as 'role: subtask', using the team's roles "
        "(triage, diagnose, remediate, communicate). Be concise."
    ),
)

CRITIC = AgentSpec(
    name="critic",
    capability="review partial results and approve or request revision",
    system_prompt=(
        "You are the Critic. Review the partial results from the team. If they are complete and "
        "the remediation names a concrete, reversible action, reply exactly 'APPROVE'. Otherwise "
        "reply 'REVISE: <what to fix>'."
    ),
)

SYNTHESIZER = AgentSpec(
    name="synthesizer",
    capability="combine approved partials into one final answer",
    system_prompt="You are the Synthesizer. Combine the approved partial results into one concise final plan.",
)

TRIAGE = AgentSpec(
    "triage",
    "assess severity and impact",
    "You assess incident severity and user impact. One or two lines.",
)
DIAGNOSE = AgentSpec(
    "diagnose",
    "find the root cause",
    "You find the root cause from symptoms and recent changes. One or two lines.",
)
REMEDIATE = AgentSpec(
    "remediate",
    "choose the fix",
    "You choose the smallest concrete, reversible remediation and name the exact action.",
)
COMMUNICATE = AgentSpec(
    "communicate",
    "draft a status update",
    "You draft a short stakeholder status update.",
)

_BUILTINS = (PLANNER, CRITIC, SYNTHESIZER, TRIAGE, DIAGNOSE, REMEDIATE, COMMUNICATE)


def default_roster() -> dict[str, AgentSpec]:
    return {a.name: a for a in _BUILTINS}


def generic_specialist(role: str) -> AgentSpec:
    return AgentSpec(
        name=role,
        capability=f"handle {role} subtasks",
        system_prompt=f"You are the {role} specialist. Complete the subtask concisely.",
    )
