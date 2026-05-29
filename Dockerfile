# Backend image for qwen-agent-society, for Alibaba Cloud Function Compute / SAE /
# ECS / ACK. The core library is stdlib-only; this image adds the FastAPI server.
FROM python:3.12-slim

WORKDIR /app

COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

COPY qwen_society/ ./qwen_society/
COPY server.py .

ENV PORT=8080
EXPOSE 8080

# DASHSCOPE_API_KEY is provided at runtime as a secret/env var, never baked in.
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8080}"]
