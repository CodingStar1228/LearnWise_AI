# 数据说明 / Data Guide

本文件说明数据格式，以及 **AP/IB 新内容应该怎么组织**。

---

## 1. 数据从哪来 / Sources

原始教材 PDF 放在 `textbooks/`（`AP/`、`IB/`、`reference/`），见 `textbooks/README.md`。
这些 PDF 是数据来源，**不直接被应用读取**；需要经 ingestion 管线抽取成结构化 JSON。

---

## 2. 数据格式 / Schema

每个学科/章节由三类 JSON 构成（参考可运行样例 `data/ds_data/`）：

### chapters.json — 章节
```json
{
  "id": "01",
  "title": "章节标题",
  "parent_id": "",
  "order": 1,
  "description": "章节概述...",
  "knowledge_points": ["kc0111", "kc0112"],
  "sub_chapters": []
}
```

### questions/<chapter>.json — 题目（数组）
```json
{
  "id": "q011002",
  "title": "题目短标题",
  "content": "题干，选择题把选项写进来\nA. ...\nB. ...",
  "difficulty": 1,
  "type": "concept",
  "knowledge_points": ["kc0111"],
  "related_questions": [{ "id": "q...", "relation_type": "similar" }],
  "reference_answer": {
    "content": "A",
    "key_points": ["要点1", "要点2"],
    "explanation": "答案解析..."
  },
  "chapter": "01"
}
```

### knowledgepoints/<chapter>.json — 知识点（数组）
```json
{
  "id": "kc0111",
  "title": "知识点名称",
  "chapter_id": "c01",
  "description": "知识点详细说明...",
  "summry": "（教师智能体读取此字段做讲解，注意当前代码里是拼写 summry）"
}
```

> ⚠️ 注意几个**历史坑**：
> - `knowledgepoints` 里教师智能体读取的字段名是 `summry`（拼写错误，但代码依赖它，见 `knowledge_qa_system.py`）。
> - 旧样例里 `order`/`difficulty` 有时被填成字符串 `"integer"` 占位，真实数据应填数字。

---

## 3. 最小 ingestion / Minimal ingest

```bash
python scripts/ingest_textbooks.py
```

从 `textbooks/AP`、`textbooks/IB` 抽取前几页文本，生成 `data/courses/<AP|IB>/<subject>/` 脚手架（chapters、knowledgepoints、questions）。详见 `data/courses/manifest.json`。

---

## 4. AP/IB 数据组织建议 / Proposed layout

沿用三件套结构，按 课程→学科 分目录：

```
data/courses/
├── AP/
│   ├── statistics/      {chapters.json, questions/*.json, knowledgepoints/*.json}
│   ├── physics/
│   ├── cs_principles/
│   └── economics/
└── IB/
    ├── math_aa_hl/
    ├── computer_science/
    └── economics/        # 取决于 Hodder 教材确认结果
```

ID 命名建议（便于去重与跨学科引用）：
- 章节：`<course>_<subject>_c01`（如 `ap_stat_c01`）
- 题目：`<course>_<subject>_q0001`
- 知识点：`<course>_<subject>_kc0001`

---

## 4. 索引 / Index

应用通过 `.pkl` 索引读取数据（见 `docs/ARCHITECTURE.md`）。
**数据变更后必须重建索引**，否则读到旧缓存。索引/抽取的可复用代码在
`data/ds_data/data_processing/`（`pdf_extractor.py`、`index_builder.py`）。

---

## 5. 双语 / Bilingual

AP/IB 教材为英文，产品定位中英双语：题干/解析建议保留英文原文，
可另加中文辅助字段（如 `content_zh`、`explanation_zh`），渲染层按用户语言选择。
（此为数据约定，具体落地待 ingestion 与前端支持。）
