# Model serving / 模型自部署

EasyEdu defaults to **self-hosted** inference via an OpenAI-compatible API (`local_vllm`).

## Quick start (AutoDL 4090)

```bash
# 1. Install vLLM on GPU machine
pip install vllm

# 2. Set model path (download Qwen2.5-7B-Instruct to this path)
export EASYEDU_MODEL_PATH=/root/autodl-fs/Qwen/Qwen2.5-7B-Instruct

# 3. Start server
chmod +x scripts/serve_model_vllm.sh
./scripts/serve_model_vllm.sh
```

Server listens at `http://0.0.0.0:8000/v1`.

## Connect EasyEdu Web / agents

On the machine running FastAPI (same host or remote):

```bash
export EASYEDU_LLM_BACKEND=local_vllm
export EASYEDU_LLM_BASE_URL=http://127.0.0.1:8000/v1
export EASYEDU_LLM_MODEL=Qwen2.5-7B-Instruct
export EASYEDU_LLM_API_KEY=EMPTY

bash run_web.sh
```

## After fine-tuning (EasyEdu LoRA)

Merge LoRA into base weights or point vLLM at merged checkpoint:

```bash
export EASYEDU_MODEL_PATH=/path/to/easyedu-merged
export EASYEDU_LLM_MODEL=EasyEdu-7B-Feynman
./scripts/serve_model_vllm.sh
```

## Fallback (dev only)

```bash
export EASYEDU_LLM_BACKEND=deepseek
export DEEPSEEK_API_KEY=sk-...
```

Commercial APIs are fallbacks; competition demo should use `local_vllm`.

## Health check

```bash
curl -s "$EASYEDU_LLM_BASE_URL/models" | head
```
