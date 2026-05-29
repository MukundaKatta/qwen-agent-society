"""The shared blackboard: an append-only message log every agent reads and writes.

Coordination is indirect, through this shared space, rather than agents calling
each other directly. The blackboard IS the audit trail of the collaboration.
"""

from __future__ import annotations

from .types import Message, MessageKind


class Blackboard:
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def post(self, msg: Message) -> Message:
        self._messages.append(msg)
        return msg

    def all(self) -> list[Message]:
        return list(self._messages)

    def by_kind(self, kind: MessageKind) -> list[Message]:
        return [m for m in self._messages if m.kind is kind]

    def latest_partials(self) -> dict[str, str]:
        """Most recent partial result per author (later rounds overwrite earlier)."""
        out: dict[str, str] = {}
        for m in self._messages:
            if m.kind is MessageKind.PARTIAL:
                out[m.author] = m.content
        return out

    def transcript(self) -> list[dict]:
        return [m.to_dict() for m in self._messages]

    def __len__(self) -> int:
        return len(self._messages)
