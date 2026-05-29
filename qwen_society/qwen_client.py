"""Qwen Cloud client plus an offline fake, both exposing `complete(spec, content)`.

The live client runs each society member as a Qwen call (its system prompt + the
coordinator's content) through the DashScope OpenAI-compatible endpoint. The fake
is a deterministic, role-aware responder so the demo and tests run the full
multi-agent collaboration offline with no key.
"""

from __future__ import annotations

import os
from typing import Callable

from .types import AgentSpec

DASHSCOPE_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen-plus"


class QwenClient:
    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None, base_url: str = DASHSCOPE_BASE_URL) -> None:
        from openai import OpenAI  # optional dependency; only for live runs

        key = api_key or os.environ.get("DASHSCOPE_API_KEY")
        if not key:
            raise RuntimeError("set DASHSCOPE_API_KEY or pass api_key to use the live Qwen client")
        self.model = model
        self._client = OpenAI(api_key=key, base_url=base_url)

    def complete(self, spec: AgentSpec, content: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": spec.system_prompt},
                {"role": "user", "content": content},
            ],
        )
        return (resp.choices[0].message.content or "").strip()


def demo_responder(spec: AgentSpec, content: str) -> str:
    """Deterministic stand-in for Qwen that drives a realistic collaboration.

    The remediate role gives a vague answer until the critic pushes back, which
    makes the critic revision loop visibly run twice in the demo.
    """
    role = spec.name
    if role == "planner":
        return (
            "triage: assess severity and impact\n"
            "diagnose: find the root cause\n"
            "remediate: choose and apply the fix\n"
            "communicate: draft a status update"
        )
    if role == "triage":
        return "SEV-1: checkout is down for all users, ~100% 5xx since 08:00"
    if role == "diagnose":
        return "Root cause: deploy v2.4.0 introduced an OOM in CheckoutHandler"
    if role == "remediate":
        if "CRITIC_NOTES: NONE" in content:
            return "Investigate and apply a fix"
        return "Rollback checkout to v2.3.7 (last good deploy), then verify error rate"
    if role == "communicate":
        return "Status: investigating checkout outage; mitigation in progress; next update in 15m"
    if role == "critic":
        return "APPROVE" if "rollback" in content.lower() else "REVISE: remediation must name a concrete, reversible action"
    if role == "synthesizer":
        return (
            "Incident plan: SEV-1 checkout outage caused by v2.4.0 OOM. "
            "Remediation: rollback to v2.3.7 and verify error rate. "
            "Comms: stakeholder update posted on a 15-minute cadence."
        )
    return f"({role}) completed the subtask"


class FakeQwenClient:
    def __init__(self, responder: Callable[[AgentSpec, str], str] | None = None) -> None:
        self.responder = responder or demo_responder

    def complete(self, spec: AgentSpec, content: str) -> str:
        return self.responder(spec, content)
