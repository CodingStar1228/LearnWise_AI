# courses/ — AP/IB 结构化题库（新方向）

应用运行时读取的 **AP/IB 题库目标位置**，当前为空脚手架。
数据格式与组织方式见 [`docs/DATA.md`](../../docs/DATA.md)。

```
courses/
├── AP/   # ap 各学科：每科一个 {chapters.json, questions/, knowledgepoints/}
└── IB/   # ib 各学科：同上
```

> 这些内容需由 ingestion 管线从 `textbooks/` 抽取生成（管线待实现）。
> 在 AP/IB 数据就绪前，可运行的 demo 仍使用 `data/ds_data/`（旧数据结构数据）。
