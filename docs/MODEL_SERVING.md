# Model serving / 模型自部署

LearnWise_AI defaults to **self-hosted** inference via an OpenAI-compatible API (`local_vllm`).

## Quick start (AutoDL 4090)

```bash
# 1. Install vLLM on GPU machine
pip install vllm

# 2. Set model path (download Qwen2.5-7B-Instruct to this path)
export LEARNWISE_MODEL_PATH=/root/autodl-tmp/models/Qwen2.5-7B-Instruct

# 3. Start server
chmod +x scripts/serve_model_vllm.sh
./scripts/serve_model_vllm.sh
```

Server listens at `http://0.0.0.0:8000/v1`.

## Connect LearnWise_AI Web / agents

On the machine running FastAPI (same host or remote):

```bash
export LEARNWISE_LLM_BACKEND=local_vllm
export LEARNWISE_LLM_BASE_URL=http://127.0.0.1:8000/v1
export LEARNWISE_LLM_MODEL=Qwen2.5-7B-Instruct
export LEARNWISE_LLM_API_KEY=EMPTY

bash run_web.sh
```

## After fine-tuning (LearnWise LoRA)

Merge LoRA into base weights or point vLLM at merged checkpoint:

```bash
export LEARNWISE_MODEL_PATH=/root/autodl-tmp/LearnWise_AI/output/learnwise-merged
export LEARNWISE_LLM_MODEL=LearnWise-7B-Feynman
./scripts/serve_model_vllm.sh
```

## Fallback (dev only)

```bash
export LEARNWISE_LLM_BACKEND=deepseek
export DEEPSEEK_API_KEY=sk-...
```

Commercial APIs are fallbacks; competition demo should use `local_vllm`.

## Health check

```bash
curl -s "$LEARNWISE_LLM_BASE_URL/models" | head
```
