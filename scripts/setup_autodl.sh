#!/usr/bin/env bash
# LearnWise_AI — one-shot AutoDL setup: deps + base model download.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODEL_ID="${LEARNWISE_MODEL_ID:-Qwen/Qwen2.5-7B-Instruct}"
MODEL_DIR="${LEARNWISE_MODEL_PATH:-/root/autodl-tmp/models/Qwen2.5-7B-Instruct}"

echo "=== [1/3] AutoDL academic acceleration (best-effort) ==="
source /etc/network_turbo 2>/dev/null || echo "  (network_turbo not available, skipping)"

echo "=== [2/3] Installing Python dependencies ==="
pip install -r requirements.txt
# GPU stack for serving + QLoRA training
pip install vllm transformers peft bitsandbytes accelerate datasets modelscope

echo "=== [3/3] Downloading base model: ${MODEL_ID} ==="
if [ -d "$MODEL_DIR" ] && [ -n "$(ls -A "$MODEL_DIR" 2>/dev/null)" ]; then
  echo "  Model dir already populated: $MODEL_DIR (skip)"
else
  mkdir -p "$MODEL_DIR"
  modelscope download --model "$MODEL_ID" --local_dir "$MODEL_DIR"
fi

echo ""
echo "=== Done. Next steps ==="
echo "  export LEARNWISE_MODEL_PATH=$MODEL_DIR"
echo "  ./scripts/serve_model_vllm.sh        # terminal A (serve model)"
echo "  # terminal B:"
echo "  export LEARNWISE_LLM_BACKEND=local_vllm"
echo "  export LEARNWISE_LLM_BASE_URL=http://127.0.0.1:8000/v1"
echo "  bash run_web.sh"
