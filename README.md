# EasyEdu

> 基于费曼学习法的 AI 教学系统 · 面向 IB / AP 国际课程
> A Feynman-method AI tutoring system for IB / AP curricula

**赛事定位 / Competition track**: IAIO — **AI for Business** 赛道。
EasyEdu 把“讲题式学习”包装成一个可面向 K12 国际教育机构（IB/AP 培训学校、留学辅导机构）落地的 B2B 教学产品。

---

## 1. 这是什么 / What it is

传统 AI 辅导是“学生提问、AI 回答”。EasyEdu 反过来：**让学生给 AI 讲题**，由三个智能体协作判断讲解的对错与深浅，并动态决定下一步该“追问”还是“纠错”。这就是费曼学习法（“能教会别人，才算真懂”）的产品化。

Instead of "student asks, AI answers", EasyEdu makes the **student explain the problem to the AI**. Three agents collaborate to judge correctness/depth and dynamically decide whether to probe deeper or correct mistakes — the Feynman technique, productized.

**三智能体 / Three agents**
- **Router（路由）** — 评估学生回答，决定下一步走向。
- **Student（学生）** — 回答正确但不完整时追问，逼出更深理解。
- **Teacher（教师）** — 三种模式：纠错引导 / 知识点追问 / 总结强化。

> 实现基于 **LangGraph** 工作流，见 `src/agents/`。

---

## 2. 当前状态 / Current status

| 模块 | 状态 | 说明 |
|------|------|------|
| 三智能体工作流 | ✅ 可运行 | `src/agents/`，基于 LangGraph |
| Web 应用（FastAPI + 前端） | ✅ 可运行 | `web/`，题目浏览 / 对话 / 抽认卡等 |
| 数据集 | ⚠️ 过渡中 | 当前 demo 仍跑在**旧的“数据结构”数据集**上（`data/ds_data/`）；**AP/IB 内容尚待构建**（`data/courses/`） |
| AP/IB 教材原料 | ✅ 已收录 | 8 本 PDF，见 `textbooks/` |
| 模型微调（LoRA SFT） | 🧪 脚手架 | `src/models/rlhf/sft/`，路径写死、训练数据待生成，方案见 `docs/TRAINING.md` |

> ⚠️ 旧的中国高中方向（`data/high_school_data/`）只是空壳占位，已不再作为主线；数据结构方向作为当前唯一可运行的 demo 数据保留。详见 `docs/PROJECT_STRUCTURE.md`。

---

## 3. 快速开始 / Quick start

```bash
# 1. 安装依赖 (Python 3.11)
pip install -r requirements.txt

# 2. 配置环境变量（API Key 等）：编辑 src/.env

# 3. 启动 Web 服务
bash run_web.sh
# 等价于：
python -m uvicorn web.main:app --host 0.0.0.0 --port 3003 --workers 1
```

浏览器访问 `http://localhost:3003`（不要用 `0.0.0.0` 直接访问）。

---

## 4. 目录速览 / Repo layout

```
EasyEdu/
├── src/            核心：智能体、QA 系统、服务层、训练代码
├── web/            FastAPI Web 应用（API + 模板 + 静态资源）
├── data/           运行时数据（courses=新 AP/IB，ds_data=旧 demo）
├── textbooks/      AP/IB 教材原料 PDF（数据来源）
├── config/         路径与数据库配置
├── docs/           文档（架构 / 结构 / 数据 / 训练）
├── legacy/         旧方向归档（脚本、旧文档、旧抽取数据）
├── requirements.txt
└── run_web.sh
```

> 每个目录/文件的详细用途见 **[`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md)**。

---

## 5. 文档导航 / Docs

- [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) — 每个目录/文件是什么、有没有被运行时引用
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — 系统架构与数据流
- [`docs/DATA.md`](docs/DATA.md) — 数据格式 & AP/IB 数据该怎么放
- [`docs/TRAINING.md`](docs/TRAINING.md) — 单卡 4090 QLoRA 训练
- [`docs/MODEL_SERVING.md`](docs/MODEL_SERVING.md) — vLLM 自部署
- [`docs/BUSINESS_CASE.md`](docs/BUSINESS_CASE.md) — IAIO for business 商业叙事
- [`textbooks/README.md`](textbooks/README.md) — 教材清单（含待人工确认项）

---

## 6. 技术栈 / Stack

FastAPI · LangChain · LangGraph · Pydantic · pdfplumber/PyMuPDF · PaddleOCR ·
PEFT(LoRA) + Accelerate/DeepSpeed（训练）· 前端 HTML/CSS/JS + Marked.js
