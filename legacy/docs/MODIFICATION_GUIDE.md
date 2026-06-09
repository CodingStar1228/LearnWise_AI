# 高中教学系统改造指南

本文档详细说明如何将现有的改造为基于费曼学习法的高中教学系统。

## 一、系统改造概述

### 1.1 核心变化
- **目标用户**：从考研学生 → 高中生
- **学科范围**：从单一数据结构 → 全高中科目（数学、物理、化学、生物、英语、语文等）
- **功能扩展**：添加题目上传、生成、导出、分类、视频推荐、番茄钟、抽认卡等功能

### 1.2 保留的核心功能
- 费曼学习法的多智能体协同教学
- LangGraph工作流
- 知识点索引系统
- 交互式问答会话

## 二、需要修改的核心文件

### 2.1 数据库Schema修改

**文件**: `src/database/schema.py`

需要添加的字段：

```python
# Question模型需要添加：
- subject: str  # 科目（数学、物理、化学、生物、英语、语文等）
- tags: List[str]  # 标签列表（微积分、力学、有机化学等）
- grade: str  # 年级（高一、高二、高三）
- source: str  # 题目来源（上传、生成、导入）
- upload_file_id: Optional[str]  # 如果是上传的，关联文件ID
- video_recommendations: List[Dict]  # 推荐视频列表

# 新增模型：
class UploadedFile(BaseModel):
    """上传文件模型"""
    id: str
    filename: str
    file_type: str  # pdf, image
    upload_time: datetime
    processed: bool
    extracted_text: Optional[str]
    questions: List[str]  # 从文件中提取的题目ID列表

class FlashCard(BaseModel):
    """抽认卡模型"""
    id: str
    question_id: str
    front: str  # 正面内容
    back: str  # 背面内容（答案）
    subject: str
    tags: List[str]
    difficulty: int
    review_count: int
    last_review: Optional[datetime]
    next_review: Optional[datetime]

class PomodoroSession(BaseModel):
    """番茄钟会话模型"""
    id: str
    user_id: str
    start_time: datetime
    duration: int  # 分钟数
    subject: str
    completed: bool
    break_time: int
```

### 2.2 文件上传和OCR处理

**新增文件**: `src/services/file_upload_service.py`

功能：
- 支持PDF和图片上传
- 调用OCR API进行文本提取
- 使用LLM从提取的文本中识别和提取题目
- 自动分类和打标签

**新增文件**: `web/api/endpoints/upload.py`

API端点：
- `POST /api/upload/file` - 上传文件
- `GET /api/upload/files` - 获取上传文件列表
- `POST /api/upload/{file_id}/extract` - 从文件中提取题目
- `GET /api/upload/{file_id}/status` - 获取处理状态

### 2.3 题目生成和导出

**新增文件**: `src/services/question_generator.py`

功能：
- 基于现有题目生成相似题目
- 支持批量生成
- 支持不同难度级别

**新增文件**: `src/services/question_exporter.py`

功能：
- 导出题目为Word/PDF格式
- 支持按科目、标签、难度筛选
- 支持自定义格式

**新增文件**: `web/api/endpoints/questions_extended.py`

API端点：
- `POST /api/questions/generate` - 生成相似题目
- `POST /api/questions/export` - 导出题目
- `GET /api/questions/export/formats` - 获取支持的导出格式

### 2.4 分类和标签系统

**修改文件**: `src/knowledge_qa_system.py`

添加方法：
- `get_questions_by_subject(subject: str)` - 按科目获取题目
- `get_questions_by_tags(tags: List[str])` - 按标签获取题目
- `add_tags_to_question(question_id: str, tags: List[str])` - 添加标签
- `get_all_subjects()` - 获取所有科目
- `get_all_tags()` - 获取所有标签

**新增文件**: `web/api/endpoints/tags.py`

API端点：
- `GET /api/tags` - 获取所有标签
- `GET /api/tags/{tag}/questions` - 获取带特定标签的题目
- `POST /api/questions/{question_id}/tags` - 为题目添加标签
- `DELETE /api/questions/{question_id}/tags/{tag}` - 删除标签

### 2.5 视频推荐功能

**新增文件**: `src/services/video_recommender.py`

功能：
- 基于题目知识点推荐相关视频
- 支持多个视频平台（B站、YouTube等）
- 视频评分和排序

**新增文件**: `web/api/endpoints/videos.py`

API端点：
- `GET /api/questions/{question_id}/videos` - 获取题目推荐视频
- `POST /api/videos` - 添加视频资源
- `GET /api/videos/search` - 搜索视频

### 2.6 番茄钟功能

**新增文件**: `src/services/pomodoro_service.py`

功能：
- 创建和管理番茄钟会话
- 记录学习时长
- 统计学习数据

**新增文件**: `web/api/endpoints/pomodoro.py`

API端点：
- `POST /api/pomodoro/start` - 开始番茄钟
- `POST /api/pomodoro/{session_id}/stop` - 停止番茄钟
- `GET /api/pomodoro/sessions` - 获取历史会话
- `GET /api/pomodoro/statistics` - 获取学习统计

**新增文件**: `web/templates/pomodoro.html`
**新增文件**: `web/static/js/pomodoro.js`

### 2.7 抽认卡功能

**新增文件**: `src/services/flashcard_service.py`

功能：
- 从题目生成抽认卡
- 间隔重复算法（Spaced Repetition）
- 复习提醒

**新增文件**: `web/api/endpoints/flashcards.py`

API端点：
- `POST /api/flashcards` - 创建抽认卡
- `GET /api/flashcards` - 获取抽认卡列表
- `POST /api/flashcards/{card_id}/review` - 复习抽认卡
- `GET /api/flashcards/due` - 获取需要复习的抽认卡

**新增文件**: `web/templates/flashcards.html`
**新增文件**: `web/static/js/flashcards.js`

### 2.8 智能体Prompt修改

**修改文件**: `src/agents/prompts/teacher_agent_prompt.txt`
**修改文件**: `src/agents/prompts/student_agent_prompt.txt`
**修改文件**: `src/agents/prompts/router_agent_prompt.txt`

需要修改：
- 将"数据结构"改为"高中各科目"
- 添加科目相关的上下文
- 调整难度和深度以适应高中生水平

### 2.9 Web界面修改

**修改文件**: `web/templates/index.html`
- 添加科目选择器
- 添加文件上传入口
- 添加功能导航（番茄钟、抽认卡等）

**修改文件**: `web/templates/problems.html`
- 添加科目和标签筛选
- 添加题目导出按钮
- 添加生成相似题目按钮

**修改文件**: `web/templates/chat.html`
- 添加视频推荐显示
- 优化界面以适应多科目

**新增文件**: `web/templates/upload.html`
- 文件上传界面
- 处理进度显示
- 提取结果展示

**新增文件**: `web/templates/pomodoro.html`
- 番茄钟界面
- 计时器显示
- 统计图表

**新增文件**: `web/templates/flashcards.html`
- 抽认卡学习界面
- 翻转动画
- 复习进度

### 2.10 主应用修改

**修改文件**: `web/main.py`

添加新的路由：
```python
from web.api.endpoints import upload, tags, videos, pomodoro, flashcards, questions_extended

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(tags.router, prefix="/api", tags=["tags"])
app.include_router(videos.router, prefix="/api", tags=["videos"])
app.include_router(pomodoro.router, prefix="/api", tags=["pomodoro"])
app.include_router(flashcards.router, prefix="/api", tags=["flashcards"])
app.include_router(questions_extended.router, prefix="/api", tags=["questions_extended"])
```

添加新的页面路由：
```python
@app.get("/upload")
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/pomodoro")
async def pomodoro_page(request: Request):
    return templates.TemplateResponse("pomodoro.html", {"request": request})

@app.get("/flashcards")
async def flashcards_page(request: Request):
    return templates.TemplateResponse("flashcards.html", {"request": request})
```

## 三、具体实现步骤

### 步骤1: 数据库Schema扩展
1. 修改 `src/database/schema.py`，添加新字段和模型
2. 创建数据库迁移脚本（如果需要）

### 步骤2: 文件上传服务
1. 创建 `src/services/file_upload_service.py`
2. 集成OCR API（可以使用现有的PaddleOCR或调用在线API）
3. 使用LLM提取题目（调用大模型API分析文本，识别题目）
4. 创建上传API端点

### 步骤3: 题目生成和导出
1. 创建题目生成服务，使用LLM基于现有题目生成相似题目
2. 创建导出服务，支持Word/PDF格式
3. 创建相关API端点

### 步骤4: 分类标签系统
1. 修改 `src/knowledge_qa_system.py`，添加分类和标签相关方法
2. 创建标签管理API
3. 在前端添加标签选择和管理界面

### 步骤5: 视频推荐
1. 创建视频推荐服务
2. 可以集成B站API或其他视频平台API
3. 基于知识点匹配推荐视频

### 步骤6: 番茄钟功能
1. 创建番茄钟服务
2. 实现计时和统计功能
3. 创建前端界面

### 步骤7: 抽认卡功能
1. 创建抽认卡服务
2. 实现间隔重复算法
3. 创建前端学习界面

### 步骤8: 智能体Prompt调整
1. 修改所有智能体的prompt，适应高中教学场景
2. 测试和优化

### 步骤9: 前端界面更新
1. 更新现有页面
2. 创建新功能页面
3. 优化用户体验

## 四、技术实现细节

### 4.1 OCR和文本提取
- 使用现有的 `PDFExtractor` 类作为基础
- 对于图片上传，使用PaddleOCR或调用在线OCR API
- 提取文本后，使用LLM（如DeepSeek-V3）分析文本，识别题目结构

### 4.2 题目提取Prompt示例
```
你是一个题目提取专家。请从以下文本中识别并提取所有题目。

要求：
1. 识别题目的类型（选择题、填空题、解答题等）
2. 提取题目的完整内容
3. 识别题目所属的科目和知识点
4. 为题目添加合适的标签

文本内容：
{extracted_text}
```

### 4.3 题目生成Prompt示例
```
基于以下题目，生成一道相似但不同的新题目。

原题目：
{original_question}

要求：
1. 保持相同的知识点和难度
2. 改变具体数值和场景
3. 确保题目逻辑正确
4. 生成完整的题目内容，包括选项（如果是选择题）
```

### 4.4 视频推荐实现
- 可以维护一个视频资源库（手动添加或爬取）
- 基于题目的知识点和标签匹配相关视频
- 可以使用向量数据库存储视频描述，进行语义搜索

### 4.5 间隔重复算法
使用SM-2算法或类似的间隔重复算法：
- 根据复习表现调整下次复习时间
- 正确回答：延长间隔
- 错误回答：缩短间隔

## 五、依赖项更新

需要在 `requirements.txt` 中添加：

```txt
# 文件处理
python-multipart>=0.0.5  # 文件上传
openpyxl>=3.0.0  # Excel导出
python-docx>=0.8.11  # Word导出
reportlab>=3.6.0  # PDF生成

# OCR（如果使用本地OCR）
paddleocr>=2.6.0
pdf2image>=1.16.0

# 视频处理（如果需要）
yt-dlp>=2023.0.0

# 其他
python-dateutil>=2.8.0
```

## 六、配置文件修改

**修改文件**: `config/db_config.yaml` 或相关配置

可能需要添加：
- OCR API配置
- 视频平台API配置
- 文件存储路径配置

## 七、测试建议

1. **单元测试**：为每个新服务创建单元测试
2. **集成测试**：测试文件上传到题目提取的完整流程
3. **端到端测试**：测试从上传到学习的完整用户流程

## 八、注意事项

1. **数据迁移**：如果现有数据需要保留，需要编写迁移脚本
2. **性能优化**：文件上传和OCR处理可能较慢，考虑异步处理和进度反馈
3. **错误处理**：OCR可能失败，需要完善的错误处理机制
4. **安全性**：文件上传需要验证文件类型和大小
5. **用户体验**：添加加载状态、进度条等反馈

## 九、优先级建议

**高优先级**（核心功能）：
1. 数据库Schema扩展
2. 文件上传和题目提取
3. 分类标签系统
4. 智能体Prompt调整

**中优先级**（重要功能）：
5. 题目生成和导出
6. 视频推荐
7. 抽认卡功能

**低优先级**（辅助功能）：
8. 番茄钟功能
9. 界面优化

---

**下一步**：根据这个指南，可以逐步实现各个功能模块。建议先从数据库Schema和文件上传功能开始。
