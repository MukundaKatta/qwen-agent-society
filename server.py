"""HTTP backend for qwen-agent-society, deployable on Alibaba Cloud.

    pip install -r requirements-server.txt
    export DASHSCOPE_API_KEY=sk-...
    uvicorn server:app --host 0.0.0.0 --port 8080

POST /solve  {"task": "...", "max_rounds": 2}
  -> SocietyResult {task, final, rounds, approved, transcript}
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from qwen_society import QwenClient, Society

app = FastAPI(title="qwen-agent-society", version="0.1.0")


class SolveRequest(BaseModel):
    task: str
    max_rounds: int = 2
    model: str = "qwen-plus"


@app.get("/healthz")
def healthz() -> dict[str, Any]:
    return {"ok": True, "qwen_key_set": bool(os.environ.get("DASHSCOPE_API_KEY"))}


@app.post("/solve")
def solve(req: SolveRequest) -> dict[str, Any]:
    society = Society(QwenClient(model=req.model), max_rounds=req.max_rounds)
    return society.run(req.task).to_dict()
