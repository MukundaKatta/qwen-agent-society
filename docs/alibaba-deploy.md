# Running on Qwen Cloud + Alibaba Cloud

Two hackathon requirements covered here: the society must call **Qwen models on
Qwen Cloud**, and the backend must **run on Alibaba Cloud** with a short
proof-of-deployment recording.

## 1. Qwen model access (Qwen Cloud / DashScope)

1. Create an Alibaba Cloud account and enable **Model Studio (DashScope)**.
2. Create an API key and export it:

   ```bash
   export DASHSCOPE_API_KEY="sk-..."
   ```

3. `QwenClient` targets the DashScope OpenAI-compatible endpoint
   (`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`), default `qwen-plus`.
   Each society member is one Qwen call; `qwen-max` raises reasoning quality.

```bash
pip install -r requirements-server.txt
```

## 2. Deploy the backend on Alibaba Cloud

This repo ships a `Dockerfile`, `requirements-server.txt`, and a
`deploy/alibaba.sh` helper. The society is stateless, so any compute target works.

```bash
./deploy/alibaba.sh build                            # build the backend image
DASHSCOPE_API_KEY=sk-... ./deploy/alibaba.sh run     # run locally on :8080

# push to Alibaba Cloud Container Registry, then create an FC/SAE app from it:
ACR_REGISTRY=registry.cn-hangzhou.aliyuncs.com ACR_NAMESPACE=<ns> ACR_USERNAME=<user> \
  ./deploy/alibaba.sh push
```

Targets that satisfy "backend runs on Alibaba Cloud": **Function Compute
(container)**, **Serverless App Engine (SAE)**, **ACK**, or **ECS**. Set
`DASHSCOPE_API_KEY`, route to port 8080. Endpoints: `GET /healthz`,
`POST /solve {task, max_rounds}` which returns the final plan plus the full
collaboration transcript.

## 3. Proof-of-deployment recording (required)

Record a short clip showing the Alibaba Cloud console (the FC/SAE/ECS resource
deployed and healthy), then a `curl` to `/solve` returning the final plan and the
multi-round transcript. Upload it alongside the ~3-minute demo video.

## 4. Submission checklist (Qwen Cloud hackathon)

- [x] Public code repo with open-source license — this repo (MIT).
- [x] Architecture diagram — `docs/architecture.md`.
- [x] Text description of features — `README.md`.
- [ ] Uses Qwen models on Qwen Cloud — set `DASHSCOPE_API_KEY`, run `QwenClient`.
- [ ] Proof of Alibaba Cloud deployment recording — section 3 (you record it).
- [ ] ~3-minute demo video on YouTube/Vimeo/Facebook — (you record it).
- [ ] Track: **Agent Society**.
