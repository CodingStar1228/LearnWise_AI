# EasyEdu

费曼学习法的 AI 辅导系统，做给 IB / AP 国际课程的学生用。

产品叫 **EasyEdu**，团队是 **LearnWise_AI**（也是这个仓库的名字）。参赛方向是 IAIO 的 **AI for Business**——我们想把它做成能真正卖给 IB/AP 培训机构、留学辅导机构的东西，而不只是一个 demo。

## 思路

市面上的 AI 辅导基本都是“学生问、AI 答”。我们反过来：**让学生给 AI 讲题**。

学生讲完，三个智能体接力判断这次讲解到底怎么样，然后决定下一步——是继续追问把他逼深一点，还是直接纠错。这就是费曼学习法那句老话：能讲明白才算真懂。

- **Router** 先评估学生讲得对不对、够不够透。
- 讲对了但浮于表面，交给 **Student**（一个好奇的“同学”）继续追问。
- 讲错了，或者讲完整了，交给 **Teacher** 纠错或总结。

编排用的是 LangGraph。模型这块我们没有用现成的商业 API，而是自己写了一层调用客户端（`src/agents/llm/`），默认连我们自己用 vLLM 部署的模型——成本、数据、可定制都握在自己手里，这也是“for business”的核心卖点。

## 现在做到哪了

能跑的：三智能体工作流、自有模型调用层、Web 应用（浏览题目 / 对话 / 抽认卡）、vLLM 自部署脚本、4090 上的 QLoRA 训练。

还在路上的：AP/IB 题库内容。教材到题库的生成脚本（`scripts/ingest_textbooks.py`）已经写好，但要在模型起来之后跑一遍才会生成内容，所以现在的 demo 还暂时跑在一份旧的数据结构题库上。

## 在 AutoDL 4090 上跑

```bash
cd /root/autodl-tmp
source /etc/network_turbo
git clone https://github.com/CodingStar1228/LearnWise_AI.git
cd LearnWise_AI
bash scripts/setup_autodl.sh        # 装依赖 + 下 Qwen2.5-7B
```

装完，开两个终端，一个跑模型、一个跑网页：

```bash
# 终端 A：起模型
export LEARNWISE_MODEL_PATH=/root/autodl-tmp/models/Qwen2.5-7B-Instruct
./scripts/serve_model_vllm.sh

# 终端 B：起网页
export LEARNWISE_LLM_BACKEND=local_vllm
export LEARNWISE_LLM_BASE_URL=http://127.0.0.1:8000/v1
export LEARNWISE_WEB_PORT=6006
bash run_web.sh
```

网页用 6006 端口，配合 AutoDL 的「自定义服务」就能在浏览器打开（细节见 [`docs/AUTODL.md`](docs/AUTODL.md)）。

生成题库和训练（单卡显存有限，记得先停掉 vLLM 再训练）：

```bash
python scripts/ingest_textbooks.py --course all --max-chunks 10   # 模型在线时
python scripts/build_sft_data.py
bash src/models/rlhf/sft/train.sh
```

## 目录

```
src/         智能体、自有模型层(agents/llm)、QA 系统、训练代码
web/         FastAPI 网页应用
scripts/     部署/数据/训练脚本
data/        运行时数据（courses=AP/IB，ds_data=旧 demo，rlhf_data=训练集）
textbooks/   AP/IB 教材 PDF（数据来源，太大没进 git）
config/      路径和模型配置
docs/        文档
legacy/      旧方向归档，留着备查
```

每个目录的细节在 [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md)。

## 文档

- [`docs/AUTODL.md`](docs/AUTODL.md) — 怎么连上 AutoDL 把它跑起来
- [`docs/MODEL_SERVING.md`](docs/MODEL_SERVING.md) — vLLM 部署
- [`docs/TRAINING.md`](docs/TRAINING.md) — 4090 上的 QLoRA 训练
- [`docs/DATA.md`](docs/DATA.md) — 数据格式和生成管线
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — 架构和数据流
- [`docs/BUSINESS_CASE.md`](docs/BUSINESS_CASE.md) — 商业角度的想法

## 技术栈

FastAPI、LangGraph、自己写的 LLM 客户端（httpx + OpenAI 兼容协议）、vLLM 部署、QLoRA（PEFT + bitsandbytes）、pdfplumber/PyMuPDF，前端是原生 HTML/CSS/JS。
