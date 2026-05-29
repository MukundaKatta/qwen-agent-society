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
python -m pytest -q     # 9 tests, no deps
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
tests/                     # 9 tests (blackboard + society), zero deps
docs/                      # architecture + Alibaba Cloud deploy guide
server.py                  # FastAPI backend
```

## License

MIT. See [LICENSE](LICENSE).
