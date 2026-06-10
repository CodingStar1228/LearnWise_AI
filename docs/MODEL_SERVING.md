# 模型部署

EasyEdu 默认连一个我们自己用 vLLM 起的、兼容 OpenAI 协议的模型服务（`local_vllm`），不走商业 API。

## 起服务（AutoDL 4090）

```bash
pip install vllm
export LEARNWISE_MODEL_PATH=/root/autodl-tmp/models/Qwen2.5-7B-Instruct
./scripts/serve_model_vllm.sh
```

起来后监听在 `http://0.0.0.0:8000/v1`。

## 让网页/智能体连上它

在跑 FastAPI 的那台机器上（本机或远程都行）设好这几个变量再起网页：

```bash
export LEARNWISE_LLM_BACKEND=local_vllm
export LEARNWISE_LLM_BASE_URL=http://127.0.0.1:8000/v1
export LEARNWISE_LLM_MODEL=Qwen2.5-7B-Instruct
export LEARNWISE_LLM_API_KEY=EMPTY
bash run_web.sh
```

## 换成微调后的模型

把 LoRA 合并进基座，或者直接让 vLLM 指向训练产物，然后改一下模型路径重启：

```bash
export LEARNWISE_MODEL_PATH=/root/autodl-tmp/LearnWise_AI/output/learnwise-merged
export LEARNWISE_LLM_MODEL=LearnWise-7B-Feynman
./scripts/serve_model_vllm.sh
```

## 兜底：开发期可以临时用商业 API

本地没显卡、只想调代码的时候，可以临时切到商业 API：

```bash
export LEARNWISE_LLM_BACKEND=deepseek
export DEEPSEEK_API_KEY=sk-...
```

但比赛 demo 一定要用 `local_vllm`，跑自己的模型才是重点。

## 检查服务活没活

```bash
curl -s "$LEARNWISE_LLM_BASE_URL/models" | head
```
