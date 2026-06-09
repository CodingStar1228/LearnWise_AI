# EasyEdu

> 基于费曼学习法的 AI 教学系统 · 面向 IB / AP 国际课程
> A Feynman-method AI tutoring system for IB / AP curricula
>
> **Product**: EasyEdu · **Team / Repo**: LearnWise_AI

**赛事定位 / Competition track**: IAIO — **AI for Business** 赛道。
EasyEdu 把“讲题式学习”包装成一个可面向 K12 国际教育机构（IB/AP 培训学校、留学辅导机构）落地的 B2B 教学产品，核心卖点是**自有模型 + 可私有化部署**。

---

## 1. 这是什么 / What it is

传统 AI 辅导是“学生提问、AI 回答”。EasyEdu 反过来：**让学生给 AI 讲题**，由三个智能体协作判断讲解的对错与深浅，并动态决定下一步该“追问”还是“纠错”。这就是费曼学习法（“能教会别人，才算真懂”）的产品化。

Instead of "student asks, AI answers", EasyEdu makes the **student explain the problem to the AI**. Three agents collaborate to judge correctness/depth and decide whether to probe deeper or correct — the Feynman technique, productized.

**三智能体 / Three agents**
- **Router（路由）** — 评估学生回答，决定下一步走向。
- **Student（学生）** — 回答正确但不完整时追问，逼出更深理解。
- **Teacher（教师）** — 纠错引导 / 知识点追问 / 总结强化。

> 编排基于 **LangGraph**；模型走**自有 LLM 客户端**（`src/agents/llm/`），默认连自部署 vLLM，不依赖商业 API。

---

## 2. 当前状态 / Current status

| 模块 | 状态 | 说明 |
|------|------|------|
| 三智能体工作流 | ✅ | `src/agents/`，LangGraph + 自有 LLM 客户端 |
| 自有模型调用层 | ✅ | `src/agents/llm/`，OpenAI 兼容，默认 `local_vllm` |
| Web 应用 | ✅ | `web/`，题目浏览 / 对话 / 抽认卡 |
| 模型自部署 | ✅ | `scripts/serve_model_vllm.sh`（vLLM） |
| 4090 QLoRA 训练 | ✅ | `src/models/rlhf/sft/` |
| AP/IB 数据管线 | ✅ 脚本就绪 | `scripts/ingest_textbooks.py`（需模型在线时运行） |
| AP/IB 题库内容 | ⏳ 待生成 | 运行管线后产出到 `data/courses/`；demo 暂用 `data/ds_data/` |

---

## 3. 在 AutoDL 4090 上运行 / Run on AutoDL

```bash
# 0. 克隆 + 装依赖
cd /root/autodl-tmp
source /etc/network_turbo
git clone https://github.com/CodingStar1228/LearnWise_AI.git
cd LearnWise_AI
bash scripts/setup_autodl.sh        # 装依赖 + 下载 Qwen2.5-7B

# 1. 起自有模型服务（终端A）
export LEARNWISE_MODEL_PATH=/root/autodl-tmp/models/Qwen2.5-7B-Instruct
./scripts/serve_model_vllm.sh

# 2. 启动 Web（终端B）
export LEARNWISE_LLM_BACKEND=local_vllm
export LEARNWISE_LLM_BASE_URL=http://127.0.0.1:8000/v1
export LEARNWISE_WEB_PORT=6006
bash run_web.sh
```

> AutoDL 看网页：把 Web 跑在 **6006** 端口，用控制台「自定义服务」；或本地 `ssh -L` 端口转发。详见 `docs/AUTODL.md`。

生成 AP/IB 数据 / 训练自有模型：

```bash
# 生成题库（模型在线时）
python scripts/ingest_textbooks.py --course all --max-chunks 10

# 训练（先 Ctrl+C 停 vLLM 腾显存）
python scripts/build_sft_data.py
bash src/models/rlhf/sft/train.sh
```

---

## 4. 目录速览 / Repo layout

```
LearnWise_AI/
├── src/            核心：智能体(agents/llm 自有模型层)、QA 系统、服务、训练
├── web/            FastAPI Web 应用
├── scripts/        部署/数据/训练脚本（serve, ingest, build_sft, setup_autodl）
├── data/           运行时数据（courses=AP/IB，ds_data=旧 demo，rlhf_data=训练集）
├── textbooks/      AP/IB 教材 PDF（数据来源，gitignored）
├── config/         路径与模型配置
├── docs/           文档
├── legacy/         旧方向归档
└── requirements.txt
```

> 详细用途见 **[`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md)**。

---

## 5. 文档导航 / Docs

- [`docs/AUTODL.md`](docs/AUTODL.md) — AutoDL 连接与运行手把手
- [`docs/MODEL_SERVING.md`](docs/MODEL_SERVING.md) — vLLM 自部署
- [`docs/TRAINING.md`](docs/TRAINING.md) — 单卡 4090 QLoRA 训练
- [`docs/DATA.md`](docs/DATA.md) — 数据格式 & 生成管线
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — 系统架构与数据流
- [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) — 每个目录/文件用途
- [`docs/BUSINESS_CASE.md`](docs/BUSINESS_CASE.md) — IAIO for business 商业叙事

---

## 6. 技术栈 / Stack

FastAPI · LangGraph · 自有 LLM 客户端(httpx, OpenAI 兼容) · vLLM 自部署 ·
PEFT QLoRA + bitsandbytes（单卡 4090 训练）· pdfplumber/PyMuPDF · 前端 HTML/CSS/JS
