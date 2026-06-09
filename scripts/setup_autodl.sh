#!/usr/bin/env bash
# EasyEdu (team LearnWise_AI) — one-shot AutoDL setup.
# Staged install so failures are isolated. Model downloads to the data disk.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODEL_ID="${LEARNWISE_MODEL_ID:-Qwen/Qwen2.5-7B-Instruct}"
MODEL_DIR="${LEARNWISE_MODEL_PATH:-/root/autodl-tmp/models/Qwen2.5-7B-Instruct}"

echo "=== [1/4] AutoDL academic acceleration (best-effort) ==="
source /etc/network_turbo 2>/dev/null || echo "  (network_turbo unavailable, continuing)"
pip install -U pip

echo "=== [2/4] App + agent deps (web, LangGraph, PDF ingest) ==="
pip install \
  fastapi "uvicorn[standard]" python-multipart jinja2 "pydantic>=2" python-dotenv \
  "langchain==0.3.23" "langchain-openai==0.3.12" "langchain-community==0.3.21" "langgraph==0.3.30" \
  tiktoken numpy tqdm requests python-dateutil httpx pdfplumber PyMuPDF modelscope

echo "=== [3/4] GPU stack: vLLM (serving) + QLoRA training ==="
echo "    (vLLM will upgrade torch to a newer CUDA 12.x build — this is expected)"
pip install vllm
pip install peft bitsandbytes accelerate datasets

echo "=== [4/4] Download base model to data disk: ${MODEL_ID} ==="
if [ -d "$MODEL_DIR" ] && [ -n "$(ls -A "$MODEL_DIR" 2>/dev/null)" ]; then
  echo "  Model dir already populated: $MODEL_DIR (skip)"
else
  mkdir -p "$MODEL_DIR"
  modelscope download --model "$MODEL_ID" --local_dir "$MODEL_DIR"
fi

echo ""
echo "=== Done. Next steps ==="
echo "  export LEARNWISE_MODEL_PATH=$MODEL_DIR"
echo "  ./scripts/serve_model_vllm.sh          # terminal A: serve model"
echo "  # terminal B:"
echo "  export LEARNWISE_LLM_BACKEND=local_vllm"
echo "  export LEARNWISE_LLM_BASE_URL=http://127.0.0.1:8000/v1"
echo "  bash run_web.sh"
