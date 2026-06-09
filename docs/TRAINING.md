# 模型训练（4090 QLoRA）/ Training

LearnWise_AI SFT uses **4-bit QLoRA** on a single RTX 4090 — no DeepSpeed ZeRO-3 required.

## 1. Build training data

```bash
python scripts/build_sft_data.py
# → data/rlhf_data/sft/train.jsonl, val.jsonl
```

Format: `input` = message list, `output` = assistant message (see `src/models/rlhf/sft/data_preprocess.py`).

> `build_sft_data.py` 会**优先读 `data/courses` 的真实 AP/IB 题库**（`ingest_textbooks.py` 生成），没有则回退 `data/ds_data`。采用**混合策略**：同时学教学行为（router/teacher/student）与学科内容（接地解析），准确率优先。

## 2. Train

```bash
export LEARNWISE_MODEL_PATH=/root/autodl-tmp/models/Qwen2.5-7B-Instruct
bash src/models/rlhf/sft/train.sh
```

Or:

```bash
python -m src.models.rlhf.sft.train --help
```

Key env vars:
- `LEARNWISE_MODEL_PATH` — base model
- `LEARNWISE_SFT_TRAIN` / `LEARNWISE_SFT_VAL` — jsonl paths
- `LEARNWISE_SFT_OUTPUT` — checkpoint dir

Defaults: LoRA r=16, accum=16, max_source=1536, Qwen target modules.

## 3. Serve fine-tuned weights

Merge LoRA or point vLLM at adapter output, then:

```bash
export LEARNWISE_MODEL_PATH=/path/to/output/checkpoint
export LEARNWISE_LLM_MODEL=LearnWise-7B-Feynman
./scripts/serve_model_vllm.sh
```

See [`MODEL_SERVING.md`](MODEL_SERVING.md).

## Dependencies (GPU machine)

```bash
pip install torch transformers peft bitsandbytes accelerate
```

Optional: `pip install vllm` for inference server.

## Business angle

Fine-tuned **LearnWise-Feynman** model replaces paid APIs → lower marginal cost and a proprietary asset for B2B deals.
