# qwen-agent-society

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776ab.svg)](https://www.python.org)
[![Hackathon: Qwen Cloud](https://img.shields.io/badge/Hackathon-Qwen%20Cloud%20%C2%B7%20Agent%20Society-615ced.svg)](https://qwencloud-hackathon.devpost.com/)

A multi-agent collaboration system on **Qwen Cloud**. A society of Qwen agents
with distinct capabilities (planner, triage, diagnose, remediate, communicate,
critic, synthesizer) work a problem together on a shared blackboard. A coordinator
decomposes the task, dispatches subtasks to specialists, runs a critic that can
send work back for revision, and synthesizes the approved results.

Built for the **Global AI Hackathon Series with Qwen Cloud**, Agent Society track
(multiple agents with distinct capabilities working together).

## Why this is different

A single agent has one perspective and no check on itself. A society adds two
things a solo agent lacks:

- **Division of labor** — each subtask goes to the role best suited for it, with its own focused system prompt.
- **A critic gate** — partial results are reviewed before they ship; if the remediation is vague, the critic sends it back with notes and the specialist revises. The society converges instead of accepting the first draft.

Coordination is indirect: agents never call each other, they read and write a
shared **blackboard**, which doubles as a complete, replayable transcript of the
collaboration.

## Architecture

```
task ─▶ Planner ─▶ subtasks (role: subtask)
                        │
              ┌─────────┴───────── dispatch to specialists ─────────┐
              ▼              ▼              ▼               ▼
           triage        diagnose       remediate      communicate     ── post partials ──▶ ┌────────────┐
                                                                                              │ Blackboard │
                                              ┌───────────── read partials ──────────────────│ (shared    │
                                              ▼                                                │  log)      │
                                           Critic ── APPROVE? ── no ──▶ revise w/ notes ──────▶│            │
                                              │ yes                          (loop, bounded)   └────────────┘
                                              ▼
                                         Synthesizer ─▶ final plan
```

Details in [docs/architecture.md](docs/architecture.md).

## See it work with no credentials

```bash
python examples/offline_demo.py
```

A society resolves an incident: the critic rejects a vague remediation in round 1,
the specialist revises to a concrete rollback in round 2, the critic approves, and
the synthesizer produces the final plan. The whole transcript prints, grouped by
round.

```bash
python -m unittest discover -s tests    # 29 tests, standard library only
```

## Use it from code

```python
from qwen_society import Society, QwenClient

society = Society(QwenClient(model="qwen-plus"), max_rounds=2)
result = society.run("checkout is throwing 500s for all users since 08:00")

print(result.final)            # synthesized plan
print(result.approved, result.rounds)
for m in result.transcript:    # full collaboration log
    print(m["round"], m["author"], m["kind"], m["content"])
```

Pass your own `roster={name: AgentSpec}` to define a different society;
`QwenClient` reads `DASHSCOPE_API_KEY` and calls Qwen through the DashScope
OpenAI-compatible endpoint.

### Running fully offline

Swap the live client for `FakeQwenClient`, a deterministic, role-aware responder
that drives the complete collaboration (including the critic revision loop) with
no API key and no network:

```python
from qwen_society import Society, FakeQwenClient

result = Society(FakeQwenClient(), max_rounds=3).run("checkout 500s")
print(result.final)
```

You can also supply your own `responder(spec, content) -> str` to script any
behavior: `FakeQwenClient(my_responder)`.

## API reference

The public surface is re-exported from the top-level `qwen_society` package.

| Symbol | Kind | Purpose |
| --- | --- | --- |
| `Society(client, roster=None, max_rounds=2)` | class | Coordinator. `run(task) -> SocietyResult` plans, dispatches, runs the critic loop, then synthesizes. |
| `QwenClient(model="qwen-plus", api_key=None, base_url=...)` | class | Live client. `complete(spec, content) -> str` via the DashScope OpenAI-compatible endpoint. Needs `openai` and `DASHSCOPE_API_KEY`. |
| `FakeQwenClient(responder=None)` | class | Offline client with the same `complete(spec, content)` interface; defaults to `demo_responder`. |
| `demo_responder(spec, content) -> str` | function | Deterministic stand-in that makes the critic reject a vague fix once, then approve the revision. |
| `parse_subtasks(plan) -> list[Subtask]` | function | Parse the planner's `role: subtask` lines; blank lines and lines without a task are skipped. |
| `default_roster() -> dict[str, AgentSpec]` | function | The built-in incident-response society. |
| `generic_specialist(role) -> AgentSpec` | function | Fallback spec for roles the planner invents that aren't in the roster. |
| `Blackboard()` | class | Append-only shared log: `post`, `all`, `by_kind`, `latest_partials`, `transcript`. |
| `AgentSpec`, `Subtask`, `Message`, `SocietyResult` | dataclasses | Typed primitives; `Message` and `SocietyResult` expose `to_dict()`. |
| `MessageKind`, `Verdict` | enums | Closed sets of message kinds and critic verdicts. |
| `PLANNER`, `CRITIC`, `SYNTHESIZER` | `AgentSpec` | The coordinator roles used by `Society`. |

A client is anything with a `complete(spec: AgentSpec, content: str) -> str`
method, so you can plug in any backend without subclassing.

`SocietyResult` fields: `task`, `final` (synthesized answer), `rounds` (critic
rounds run), `approved` (whether the critic approved before `max_rounds`), and
`transcript` (the full blackboard as a list of dicts).

## Running on Qwen Cloud + Alibaba Cloud

`server.py` exposes `POST /solve`. Deploy guide is in
[docs/alibaba-deploy.md](docs/alibaba-deploy.md); the helper is
`./deploy/alibaba.sh build|run|push`.

## Layout

```
qwen_society/
  types.py        # AgentSpec, Subtask, Message, SocietyResult, enums
  blackboard.py   # shared append-only message log
  roles.py        # built-in roles (planner/critic/synthesizer + specialists)
  qwen_client.py  # live Qwen Cloud client + offline role-aware fake
  society.py      # coordinator: plan -> dispatch -> critique -> synthesize
examples/offline_demo.py   # credential-free; shows the critic revision loop
tests/                     # 29 stdlib unittest tests (types + blackboard + society), zero deps
docs/                      # architecture + Alibaba Cloud deploy guide
server.py                  # FastAPI backend
```

## License

MIT. See [LICENSE](LICENSE).
