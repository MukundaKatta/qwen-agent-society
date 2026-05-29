"""Typed primitives for the agent society. Closed enums + dataclasses."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class MessageKind(str, Enum):
    PLAN = "plan"
    PARTIAL = "partial"
    CRITIQUE = "critique"
    FINAL = "final"


class Verdict(str, Enum):
    APPROVE = "approve"
    REVISE = "revise"


@dataclass(frozen=True)
class AgentSpec:
    """A society member: a name, what it is good at, and its system prompt."""

    name: str
    capability: str
    system_prompt: str


@dataclass(frozen=True)
class Subtask:
    role: str
    task: str


@dataclass
class Message:
    """One entry on the shared blackboard. The whole run is an ordered list of these."""

    author: str
    kind: MessageKind
    topic: str
    content: str
    round: int = 0

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["kind"] = self.kind.value
        return d


@dataclass
class SocietyResult:
    task: str
    final: str
    rounds: int
    approved: bool
    transcript: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "final": self.final,
            "rounds": self.rounds,
            "approved": self.approved,
            "transcript": self.transcript,
        }
