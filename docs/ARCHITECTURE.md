# 系统架构 / Architecture

## 分层 / Layers

```
┌───────────────────────────────────────────────┐
│  前端 Web (web/templates + web/static)         │  题目浏览 / 对话 / 抽认卡
├───────────────────────────────────────────────┤
│  FastAPI 后端 (web/main.py + web/api)          │  REST API / 会话 / 上传
├───────────────────────────────────────────────┤
│  核心业务 (src/)                                │
│   ├─ KnowledgeQASystem  数据索引 + 题目查询     │
│   ├─ 多智能体 (LangGraph)  router/student/teacher│
│   └─ 服务层  上传OCR / 生成 / 导出 / 抽认卡 / 推荐 │
├───────────────────────────────────────────────┤
│  数据层  JSON 题库/知识点 + Pickle 索引          │
└───────────────────────────────────────────────┘
```

## 智能体工作流 / Agent workflow

```
学生回答 ──▶ Router 评估
                ├─ 正确但不完整 ──▶ Student 追问 ──┐
                ├─ 不正确       ──▶ Teacher 纠错 ──┤──▶ 继续对话 / 换题
                └─ 正确且完整   ──▶ Teacher 总结 ──┘
```

- 代码：`src/agents/workflow.py`（图定义）+ `src/agents/agents/*.py`（节点）。
- 提示词：`src/agents/prompts/*.txt`（⚠️ 当前为数据结构/中文，转向 AP/IB 需重写）。
- 模型：`src/agents/models.py` 中可切换（deepseek / tongyi 等）。

## 数据索引 / Indexing

为避免每次遍历大量 JSON，系统在首次运行时构建内存索引并落盘为 `.pkl`：

```
首次：读取 JSON → 构建索引 → 保存 *.pkl
之后：直接 load *.pkl（秒级启动）
```

索引结构（见 `data/ds_data/data_processing/index_builder.py`）：
`chapter_index` / `question_index` / `knowledge_index` / `knowledge_question_index`。

> ⚠️ 数据更新后需重建索引，否则读到的是旧缓存。

## 数据流：从教材到题库 / Ingestion

```
textbooks/*.pdf
   │  (pdfplumber / PyMuPDF / PaddleOCR)
   ▼
抽取文本/页面  ──▶  LLM 解析为 题目+知识点(JSON)  ──▶  data/courses/{AP,IB}/...
                                                          │
                                                          ▼  构建索引(.pkl) ──▶ 上线
```

> 此 ingestion 管线目前是“计划中”：原 `data/ds_data/data_processing/` 提供了可复用的 PDF 抽取/索引代码，AP/IB 版本待实现（本次仅整理，未改业务代码）。
