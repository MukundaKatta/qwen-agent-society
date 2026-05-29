"""qwen-agent-society: a multi-agent collaboration system on Qwen Cloud.

A society of Qwen agents with distinct capabilities (planner, triage, diagnose,
remediate, communicate, critic, synthesizer) collaborate through a shared
blackboard. A coordinator decomposes the task, dispatches subtasks to specialist
roles, runs a critic that can send work back for revision, and synthesizes the
approved results into a final answer.

Built for the Global AI Hackathon Series with Qwen Cloud (Agent Society track).
"""

from .types import MessageKind, Verdict, AgentSpec, Subtask, Message, SocietyResult
from .blackboard import Blackboard
from .roles import default_roster, generic_specialist, PLANNER, CRITIC, SYNTHESIZER
from .qwen_client import QwenClient, FakeQwenClient, demo_responder
from .society import Society, parse_subtasks

__version__ = "0.1.0"

__all__ = [
    "MessageKind",
    "Verdict",
    "AgentSpec",
    "Subtask",
    "Message",
    "SocietyResult",
    "Blackboard",
    "default_roster",
    "generic_specialist",
    "PLANNER",
    "CRITIC",
    "SYNTHESIZER",
    "QwenClient",
    "FakeQwenClient",
    "demo_responder",
    "Society",
    "parse_subtasks",
]
