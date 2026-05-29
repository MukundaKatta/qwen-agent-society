# Architecture

qwen-agent-society coordinates several Qwen agents through a shared blackboard. No
agent calls another directly; they post to and read from the blackboard, and a
coordinator drives the protocol.

## Protocol

```
   task
    │
    ▼
 Planner ───────────────▶ "role: subtask" lines ──▶ parse_subtasks()
    │ (posts PLAN)
    ▼
 ┌────────────────────────── round loop (<= max_rounds) ──────────────────────────┐
 │  for each subtask:                                                              │
 │     specialist(role).complete(ROLE / SUBTASK / CRITIC_NOTES) ─▶ post PARTIAL    │
 │                                                                                │
 │  Critic.complete(all latest PARTIALS) ─▶ post CRITIQUE                          │
 │     APPROVE  ─▶ break                                                           │
 │     REVISE: notes ─▶ attach notes to every role, run another round             │
 └────────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
 Synthesizer.complete(approved PARTIALS) ─▶ post FINAL ─▶ SocietyResult
```

Every step appends a `Message` (PLAN / PARTIAL / CRITIQUE / FINAL) to the
blackboard, so `result.transcript` is a complete, ordered, replayable record of
who did what in which round.

## Roles

The default roster is an incident-response society, but a role is just an
`AgentSpec(name, capability, system_prompt)`. You pass any `roster` you like. If
the planner names a role that is not in the roster, the coordinator falls back to
a `generic_specialist`, so the planner can invent roles without breaking the run.

## Why the critic matters

A single agent tends to accept its own first answer. The critic is a separate
member with its own prompt whose only job is to gate quality: it reads the
combined partials and either approves or returns concrete revision notes. Those
notes flow back into the next round's specialist prompts (`CRITIC_NOTES: ...`), so
the society improves the work rather than shipping a first draft. The loop is
bounded by `max_rounds`, so it always terminates, approved or not, and
`SocietyResult.approved` records which.

## Determinism and testing

The coordinator is pure orchestration over a `complete(spec, content)` interface,
so the offline `FakeQwenClient` (a role-aware responder) exercises the exact same
code path as the live `QwenClient`. The whole multi-agent loop, including the
revision cycle, is tested with no key and no network.
