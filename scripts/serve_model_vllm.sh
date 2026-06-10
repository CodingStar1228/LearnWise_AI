#!/usr/bin/env bash
# Start self-hosted OpenAI-compatible API via vLLM (AutoDL 4090 / local GPU)
set -euo pipefail

MODEL_PATH="${LEARNWISE_MODEL_PATH:-/root/autodl-tmp/models/Qwen2.5-7B-Instruct}"
HOST="${LEARNWISE_VLLM_HOST:-0.0.0.0}"
PORT="${LEARNWISE_VLLM_PORT:-8000}"
SERVED_NAME="${LEARNWISE_LLM_MODEL:-Qwen2.5-7B-Instruct}"
GPU_MEMORY="${LEARNWISE_VLLM_GPU_MEMORY:-0.90}"
MAX_LEN="${LEARNWISE_VLLM_MAX_LEN:-8192}"

echo "Model path:    $MODEL_PATH"
echo "Listen:        $HOST:$PORT"
echo "Served name:   $SERVED_NAME"
echo "Max model len: $MAX_LEN"

python -m vllm.entrypoints.openai.api_server \
  --model "$MODEL_PATH" \
  --served-model-name "$SERVED_NAME" \
  --host "$HOST" \
  --port "$PORT" \
  --dtype auto \
  --gpu-memory-utilization "$GPU_MEMORY" \
  --max-model-len "$MAX_LEN"
