# EasyEdu 高中教学智能系统 - 项目介绍

## 📚 项目概述

**EasyEdu** 是一款基于**费曼学习法**的高中教学智能系统，通过AI多智能体协同教学，帮助学生通过"主动讲解"的方式深入学习高中各科目知识。

### 核心理念

**费曼学习法**：最好的学习方式就是教授他人。系统引导学生主动讲解题目，AI智能体根据学生的表现动态调整教学策略，形成"讲解-反馈-修正-强化"的学习闭环。

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────┐
│              前端界面 (Web)                      │
│  - HTML/CSS/JavaScript                          │
│  - 科目选择、题目浏览、对话界面                 │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│            FastAPI 后端服务                     │
│  - RESTful API                                  │
│  - 文件上传、题目管理、会话管理                 │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│        核心业务逻辑层                            │
│  ┌──────────────────────────────────────────┐  │
│  │  知识问答系统 (KnowledgeQASystem)        │  │
│  │  - 数据加载和索引                        │  │
│  │  - 题目查询和管理                        │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  多智能体系统 (LangGraph)                │  │
│  │  - 路由Agent: 评估学生回答               │  │
│  │  - 学生Agent: 知识点追问                │  │
│  │  - 教师Agent: 纠错和总结                │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  扩展功能服务                            │  │
│  │  - 文件上传和OCR                         │  │
│  │  - 题目生成                              │  │
│  │  - 题目导出                              │  │
│  │  - 抽认卡服务                            │  │
│  │  - 视频推荐                              │  │
│  └──────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│           数据存储层                             │
│  - JSON文件存储（章节、题目、知识点）          │
│  - Pickle索引文件（快速加载）                  │
│  - 文件上传存储                                │
└─────────────────────────────────────────────────┘
```

## 🔧 核心技术实现

### 1. 多智能体协同教学系统

#### 实现原理

使用 **LangGraph** 构建工作流，实现三个智能体的协同：

```python
# 工作流程
用户回答 → 路由Agent评估 → 选择下一步
                    ├─ 回答正确但不完整 → 学生Agent追问
                    ├─ 回答不正确 → 教师Agent纠错
                    └─ 回答正确且完整 → 教师Agent总结
```

#### 关键代码位置
- `src/agents/workflow.py` - 工作流定义
- `src/agents/agents/router.py` - 路由智能体
- `src/agents/agents/student.py` - 学生智能体
- `src/agents/agents/teacher.py` - 教师智能体

### 2. 数据索引系统

#### 实现原理

**问题**：直接读取JSON文件太慢（需要遍历所有文件）

**解决方案**：构建内存索引，保存为Pickle文件

```python
# 索引结构
{
    'chapter_index': {chapter_id: chapter_object},      # 章节索引
    'question_index': {question_id: question_object},  # 题目索引
    'knowledge_index': {kp_id: kp_object},              # 知识点索引
    'knowledge_question_index': {kp_id: [q_ids]}       # 关联索引
}
```

#### 工作流程

1. **首次运行**：
   ```
   读取JSON文件 → 构建内存索引 → 保存为.pkl文件
   ```

2. **后续运行**：
   ```
   直接加载.pkl文件 → 快速启动
   ```

#### 关键代码位置
- `data/high_school_data_loader.py` - 高中数据加载器
- `data/ds_data/data_processing/index_builder.py` - 索引构建器

### 3. 文件上传和OCR处理

#### 实现流程

```
用户上传文件 (PDF/图片)
    ↓
保存文件到服务器
    ↓
提取文本 (PDF提取器 或 OCR识别)
    ↓
调用LLM分析文本
    ↓
识别和提取题目
    ↓
保存题目到JSON文件
    ↓
更新索引
```

#### 关键技术
- **PDF处理**：`pdfplumber`、`PyMuPDF`
- **OCR识别**：`PaddleOCR`
- **题目提取**：使用LLM（DeepSeek/OpenAI）分析文本

#### 关键代码位置
- `src/services/file_upload_service.py` - 文件上传服务
- `data/ds_data/data_processing/pdf_extractor.py` - PDF提取器

### 4. 题目生成系统

#### 实现原理

使用LLM基于现有题目生成相似题目：

```python
# 生成流程
原题目 + 生成要求 → LLM分析 → 生成新题目
```

#### 生成策略
- **相似题目**：保持知识点和难度，改变数值和场景
- **主题生成**：根据知识点和主题生成新题目

#### 关键代码位置
- `src/services/question_generator.py` - 题目生成服务

### 5. 抽认卡系统（间隔重复算法）

#### 实现原理

使用 **SM-2算法**（SuperMemo 2）实现间隔重复：

```python
# SM-2算法核心
if 回答正确:
    间隔 = 间隔 × 易度因子
    易度因子 += 调整值
else:
    间隔 = 1  # 重置
    易度因子 -= 0.2
```

#### 算法特点
- 根据复习质量调整下次复习时间
- 正确回答：延长间隔
- 错误回答：缩短间隔，增加复习频率

#### 关键代码位置
- `src/services/flashcard_service.py` - 抽认卡服务

### 6. 题目导出系统

#### 支持格式
- **JSON**：结构化数据，便于程序处理
- **TXT**：纯文本，通用格式
- **Markdown**：便于阅读和编辑
- **Word**：使用 `python-docx`
- **Excel**：使用 `openpyxl`
- **PDF**：使用 `reportlab`

#### 关键代码位置
- `src/services/question_exporter.py` - 题目导出服务

## 📊 数据流程

### 数据存储结构

```
data/
├── high_school_data/          # 高中教学数据
│   ├── math/                  # 数学
│   │   ├── chapters/
│   │   │   └── chapters.json
│   │   ├── questions/
│   │   │   ├── m01.json
│   │   │   └── ...
│   │   └── knowledgepoints/
│   │       ├── m01.json
│   │       └── ...
│   ├── physics/               # 物理
│   └── ...
├── hs_indices.pkl             # 索引文件（快速加载）
└── ds_data/                   # 原有数据结构数据
```

### 数据加载流程

```
系统启动
    ↓
检查索引文件是否存在
    ├─ 存在 → 直接加载索引（快速）
    └─ 不存在 → 读取JSON文件 → 构建索引 → 保存
    ↓
系统就绪，可以处理请求
```

## 🛠️ 技术栈

### 后端
- **FastAPI** - Web框架
- **LangChain** - LLM集成
- **LangGraph** - 多智能体工作流
- **Pydantic** - 数据验证

### 数据处理
- **PaddleOCR** - OCR识别
- **pdfplumber** - PDF处理
- **python-docx** - Word导出
- **openpyxl** - Excel导出
- **reportlab** - PDF生成

### 前端
- **HTML/CSS/JavaScript** - 基础前端
- **Marked.js** - Markdown渲染
- **Tailwind CSS** - 样式框架（部分页面）

### AI模型
- **DeepSeek-V3** - 主要LLM（可配置）
- **Qwen2.5** - 备选LLM（可配置）

## 🔄 核心工作流程

### 1. 学习流程

```
学生选择题目
    ↓
查看题目详情
    ↓
尝试讲解解题思路
    ↓
系统评估回答
    ↓
根据评估结果选择智能体
    ├─ 学生Agent追问 → 深入理解
    ├─ 教师Agent纠错 → 纠正错误
    └─ 教师Agent总结 → 强化记忆
    ↓
继续对话或选择新题目
```

### 2. 题目管理流程

```
上传文件 (PDF/图片)
    ↓
OCR/文本提取
    ↓
LLM分析文本
    ↓
识别和提取题目
    ↓
自动分类和打标签
    ↓
保存到对应科目和章节
    ↓
更新索引
```

### 3. 数据查询流程

```
用户请求（如：获取数学章节）
    ↓
API接收请求
    ↓
KnowledgeQASystem查询
    ↓
从索引中快速查找
    ↓
返回结果
```

## 💡 设计亮点

### 1. 多智能体协同
- 不是简单的问答，而是根据学生表现动态调整策略
- 模拟真实教学场景（有提问的同学，有纠错的老师）

### 2. 性能优化
- 使用索引文件加速数据加载
- 避免每次启动都读取大量JSON文件

### 3. 扩展性强
- 支持多科目（数学、物理、化学等）
- 模块化设计，易于添加新功能

### 4. 数据格式灵活
- 支持JSON文件存储
- 易于手动编辑和批量导入

## 📁 关键文件说明

### 核心系统文件
- `src/knowledge_qa_system.py` - 知识问答系统主类
- `src/agents/workflow.py` - 多智能体工作流
- `web/main.py` - FastAPI应用入口

### 数据相关
- `data/high_school_data_loader.py` - 高中数据加载器
- `data/create_high_school_data.py` - 数据结构创建脚本
- `data/hs_indices.pkl` - 索引文件（自动生成）

### 服务层
- `src/services/file_upload_service.py` - 文件上传服务
- `src/services/question_generator.py` - 题目生成服务
- `src/services/question_exporter.py` - 题目导出服务
- `src/services/flashcard_service.py` - 抽认卡服务
- `src/services/video_recommender.py` - 视频推荐服务

### API端点
- `web/api/endpoints/chapters.py` - 章节API
- `web/api/endpoints/questions.py` - 题目API
- `web/api/endpoints/sessions.py` - 会话API
- `web/api/endpoints/upload.py` - 上传API
- `web/api/endpoints/tags.py` - 标签API
- `web/api/endpoints/questions_extended.py` - 题目扩展API

## 🚀 运行流程

### 1. 系统启动

```bash
# 启动Web服务器
bash run_web.sh

# 或
python -m uvicorn web.main:app --host 0.0.0.0 --port 3003
```

### 2. 数据加载

```
系统启动 → 检查索引文件
    ├─ 存在 → 加载索引（秒级）
    └─ 不存在 → 读取JSON → 构建索引 → 保存（首次较慢）
```

### 3. 用户使用

```
访问 http://localhost:3003
    ↓
选择科目和章节
    ↓
查看题目列表
    ↓
选择题目开始学习
    ↓
与AI智能体对话
```

## 🔍 技术细节

### 1. 为什么使用Pickle索引？

**优势**：
- 快速加载（秒级 vs 分钟级）
- 保持内存结构
- Python原生支持

**缺点**：
- 仅Python可用
- 数据更新需重建索引

### 2. 为什么使用LangGraph？

**优势**：
- 灵活的工作流定义
- 状态管理
- 支持复杂决策逻辑
- 易于扩展

### 3. 数据存储为什么用JSON？

**优势**：
- 人类可读
- 易于编辑
- 版本控制友好
- 跨平台兼容

**未来可扩展**：
- 可迁移到数据库（MongoDB/SQLite）
- 当前JSON格式兼容数据库schema

## 📈 系统特点总结

1. **智能教学**：多智能体协同，动态调整教学策略
2. **高效查询**：索引系统，快速数据访问
3. **易于扩展**：模块化设计，支持多科目
4. **功能丰富**：文件上传、题目生成、导出、抽认卡等
5. **用户友好**：清晰的界面，流畅的交互

---

**项目状态**：核心功能已完成，可以开始使用和测试！
