# 项目结构说明 / Project Structure

本文件逐目录说明 **每个部分是什么、做什么用、是否被运行时代码引用**，方便快速定位。
标记说明：🟢 运行时核心（动它会影响应用）｜🟡 工具/辅助｜⚪ 数据/资源｜🗄️ 归档（不再使用）。

---

## 顶层 / Top level

| 路径 | 标记 | 说明 |
|------|------|------|
| `src/` | 🟢 | 核心源码：智能体、QA 系统、服务层、模型训练 |
| `web/` | 🟢 | FastAPI Web 应用（API、模板、静态资源） |
| `data/` | ⚪ | 运行时数据与产物 |
| `textbooks/` | ⚪ | AP/IB 教材原始 PDF（新方向的数据来源） |
| `config/` | 🟢 | 路径常量与数据库配置 |
| `docs/` | 🟡 | 项目文档 |
| `legacy/` | 🗄️ | 旧方向归档（不被任何运行时代码引用） |
| `requirements.txt` | 🟢 | Python 依赖 |
| `run_web.sh` / `start_server.py` | 🟢 | 启动脚本 |
| `Dockerfile` | 🟡 | 容器化构建 |

---

## `src/` — 核心源码

| 路径 | 标记 | 说明 |
|------|------|------|
| `src/knowledge_qa_system.py` | 🟢 | **主类 `KnowledgeQASystem`**：加载数据索引 + 创建智能体工作流 + 会话管理。Web 层通过它访问一切 |
| `src/agents/workflow.py` | 🟢 | LangGraph 工作流定义（router→student/teacher 的流转） |
| `src/agents/agents/router.py` | 🟢 | 路由智能体 |
| `src/agents/agents/student.py` | 🟢 | 学生智能体（追问） |
| `src/agents/agents/teacher.py` | 🟢 | 教师智能体（纠错/总结） |
| `src/agents/base.py` | 🟢 | 智能体基类 / 公共逻辑 |
| `src/agents/models.py` | 🟢 | LLM 模型封装与选择（deepseek/tongyi 等） |
| `src/agents/session_manager.py` | 🟢 | 会话状态管理 |
| `src/agents/prompts/*.txt` | 🟢 | **各智能体的系统提示词**。⚠️ 当前内容写死为“数据结构 / 中文”，转向 AP/IB 后需重写 |
| `src/agents/example.py` | 🟡 | 智能体调用示例 |
| `src/agents/agents_jupyter.ipynb` | 🟡 | 智能体调试笔记本 |
| `src/services/file_upload_service.py` | 🟢 | 文件上传 + OCR/PDF 解析 + 题目抽取 |
| `src/services/question_generator.py` | 🟢 | 基于现有题目生成相似题 |
| `src/services/question_exporter.py` | 🟢 | 题目导出（JSON/TXT/MD/Word/Excel/PDF） |
| `src/services/flashcard_service.py` | 🟢 | 抽认卡（SM-2 间隔重复算法） |
| `src/services/video_recommender.py` | 🟢 | 基于知识点的视频推荐 |
| `src/database/schema.py` | 🟢 | 数据模型 / schema 定义 |
| `src/models/rlhf/sft/` | 🧪 | **LoRA SFT 训练代码**（见下方 + `docs/TRAINING.md`） |
| `src/models/vllm/` | 🧪 | vLLM 推理脚本（`run.sh`, `zvllm.ipynb`） |
| `src/.env` | 🔒 | API Key 等密钥（已被 .gitignore 忽略，勿提交） |

### `src/models/rlhf/sft/` — 微调

| 文件 | 说明 |
|------|------|
| `train.py` | 训练主流程（Accelerate + DeepSpeed ZeRO-3 + PEFT LoRA） |
| `train.sh` | 启动脚本。⚠️ 路径写死为旧 autodl 路径（`/root/autodl-tmp/...`）和 GLM-4-9B，需按你的 4090 环境改 |
| `data_preprocess.py` | 数据集与对话模板（system/user/assistant，jsonl 输入） |
| `arguments.py` | Model/Data/Peft 参数定义 |
| `default_config.yaml` / `zero_stage3_config.json` | Accelerate / DeepSpeed 配置 |
| `inference.py` / `evaluate.py` / `utils.py` | 推理 / 评估 / 工具 |

---

## `web/` — Web 应用

| 路径 | 标记 | 说明 |
|------|------|------|
| `web/main.py` | 🟢 | FastAPI 入口，注册路由与页面 |
| `web/core/config.py` | 🟢 | Web 层配置。⚠️ `DATA_DIR` 当前指向 `data/ds_data` |
| `web/services/qa_service.py` | 🟢 | 封装 `KnowledgeQASystem`，被各 API 调用 |
| `web/api/endpoints/*.py` | 🟢 | REST 接口：chapters / questions / sessions / knowledge / upload / tags / videos / flashcards / questions_extended |
| `web/models/schemas.py` | 🟢 | API 请求/响应模型 |
| `web/templates/*.html` | 🟢 | 页面：index / problems / knowledge / chat / flashcards / chapter |
| `web/static/css`,`web/static/js` | 🟢 | 前端样式与脚本 |
| `web/requirements.txt` | 🟡 | Web 子模块依赖（与根 requirements 重叠） |

---

## `data/` — 运行时数据

| 路径 | 标记 | 说明 |
|------|------|------|
| `data/courses/AP`, `data/courses/IB` | ⚪ | **新方向数据目标位置**（当前为空脚手架，结构见 `docs/DATA.md`） |
| `data/ds_data/` | 🟢🗄️ | **旧“数据结构”数据集**，但**当前唯一可运行的 demo 数据**。含真实题目/知识点 + `ds_indices.pkl` + `data_processing/`（PDF 抽取、索引构建）。`src/knowledge_qa_system.py` 会 import 其 `index_builder` |
| `data/hs_indices.pkl` | 🟢 | 高中数据索引缓存，`use_high_school_data=True` 时运行时加载 |
| `data/high_school_data/` | 🗄️ | 旧中国高中方向，题目文件**全为空 `[]`**，仅占位；仅在 `hs_indices.pkl` 缺失时才会被重建读取 |
| `data/high_school_data_loader.py` | 🟢 | 高中数据加载器，被 `knowledge_qa_system` import（暂不可删） |
| `data/samples/` | ⚪ | OCR/上传功能的测试样例图片（原 `homework/`） |
| `data/uploads/` | ⚪ | 用户上传文件落地目录（运行时产物） |
| `data/exports/` | ⚪ | 题目导出产物目录 |

---

## `textbooks/` — 教材原料（新方向数据来源）

见 [`textbooks/README.md`](../textbooks/README.md)。按 `AP/` `IB/` `reference/` 分类的 8 本 PDF。

---

## `config/`

| 文件 | 说明 |
|------|------|
| `config/paths.py` | 全局路径常量（DATA/SRC/AGENTS/PROMPTS/MODELS…）。⚠️ 仍以 `ds_data` 为默认数据 |
| `config/db_config.yaml` | 数据库配置 |

---

## `docs/`

| 文件 | 说明 |
|------|------|
| `PROJECT_STRUCTURE.md` | 本文件 |
| `ARCHITECTURE.md` | 系统架构与数据流 |
| `DATA.md` | 数据格式 + AP/IB 数据组织方案 |
| `TRAINING.md` | 单卡 4090 微调方案 |
| `agents.md` | 智能体设计说明（原 functional_docs） |
| `database_design.md` | 数据库设计（原 functional_docs） |
| `knowledge_graph_user_guide.md` | 知识图谱使用指南 |

---

## `legacy/` — 归档（🗄️ 不再使用，可随时删）

| 路径 | 说明 |
|------|------|
| `legacy/docs/` | 旧的 9 个 markdown（PROJECT_INTRODUCTION、IMPLEMENTATION_*、MODIFICATION_GUIDE、*_SUMMARY、QUICK_START、TROUBLESHOOTING） |
| `legacy/scripts/` | 旧一次性脚本：`create_high_school_data.py`、`migrate_ds_to_hs.py`、`demo.py`、`ztmp.py` |
| `legacy/notebooks/` | `analyze_hs_indices.ipynb` |
| `legacy/misc/` | `README_HIGH_SCHOOL.md`、散落的 `chapter_1.json` |
| `legacy/data/DS2026_extracted/` | 旧数据结构教材抽取出的 120MB 页文本 |

> 这些都已确认**没有被任何运行时代码 import**，纯归档。确定不需要后可整目录删除。
