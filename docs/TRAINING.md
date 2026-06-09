# 模型训练（4090 QLoRA）/ Training

LearnWise_AI SFT uses **4-bit QLoRA** on a single RTX 4090 — no DeepSpeed ZeRO-3 required.

## 1. Build training data

```bash
python scripts/build_sft_data.py
# → data/rlhf_data/sft/train.jsonl, val.jsonl
```

Format: `input` = message list, `output` = assistant message (see `src/models/rlhf/sft/data_preprocess.py`).

> 现在 `build_sft_data.py` 用的是旧 `data/ds_data` 占位题；AP/IB 真实数据生成后（`scripts/ingest_textbooks.py`）应改成读 `data/courses`。

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
