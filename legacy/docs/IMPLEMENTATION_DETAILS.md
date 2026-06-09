# 实现细节说明

## 🎯 项目核心实现

### 一、费曼学习法的实现

#### 1.1 核心理念
费曼学习法强调"通过教授来学习"。系统通过以下方式实现：

1. **引导学生主动讲解**：不是直接给答案，而是让学生先尝试讲解
2. **智能评估**：AI评估学生讲解的正确性和完整性
3. **动态反馈**：根据评估结果选择不同的教学策略

#### 1.2 多智能体协同

```
用户回答
    ↓
路由Agent评估
    ├─ 正确但不完整 → 学生Agent追问
    ├─ 不正确 → 教师Agent纠错
    └─ 正确且完整 → 教师Agent总结
```

**实现位置**：`src/agents/workflow.py`

### 二、数据管理系统

#### 2.1 为什么使用索引文件？

**问题**：
- 直接读取JSON文件需要遍历所有文件
- 每次启动都要读取大量数据
- 查询效率低

**解决方案**：
- 构建内存索引
- 保存为Pickle文件
- 启动时直接加载索引

**性能对比**：
- 直接读取JSON：~10-30秒
- 加载索引文件：~1-2秒

#### 2.2 索引结构

```python
{
    'chapter_index': {
        'm01': {'id': 'm01', 'title': '函数与方程', ...},
        'm02': {'id': 'm02', 'title': '三角函数', ...},
        ...
    },
    'question_index': {
        'q_m01_001': {'id': 'q_m01_001', 'title': '...', ...},
        ...
    },
    'knowledge_index': {
        'kc_m01_001': {'id': 'kc_m01_001', 'title': '...', ...},
        ...
    },
    'knowledge_question_index': {
        'kc_m01_001': ['q_m01_001', 'q_m01_002', ...],
        ...
    }
}
```

**实现位置**：`data/high_school_data_loader.py`

### 三、文件上传和OCR

#### 3.1 处理流程

```
上传文件
    ↓
判断文件类型（PDF/图片）
    ↓
PDF → PDFExtractor提取文本
图片 → PaddleOCR识别
    ↓
提取的文本
    ↓
调用LLM分析
    ↓
识别题目结构
    ↓
提取题目信息
    ↓
保存到JSON文件
```

#### 3.2 题目提取Prompt

系统使用精心设计的Prompt让LLM识别题目：

```
你是一个题目提取专家。请从以下文本中识别并提取所有题目。

要求：
1. 识别题目的类型（选择题、填空题、解答题等）
2. 提取题目的完整内容
3. 识别题目所属的科目和知识点
4. 为题目添加合适的标签
5. 评估题目难度

文本内容：{extracted_text}
```

**实现位置**：`src/services/file_upload_service.py`

### 四、题目生成系统

#### 4.1 生成策略

**相似题目生成**：
- 保持相同的知识点和难度
- 改变具体数值和场景
- 确保逻辑正确

**主题生成**：
- 根据知识点和主题生成
- 支持指定难度和数量

#### 4.2 生成流程

```
原题目 + 生成要求
    ↓
构建Prompt
    ↓
调用LLM生成
    ↓
解析JSON响应
    ↓
验证和格式化
    ↓
返回生成的题目
```

**实现位置**：`src/services/question_generator.py`

### 五、抽认卡系统（SM-2算法）

#### 5.1 SM-2算法原理

**间隔重复算法**：根据复习表现调整下次复习时间

```python
# 算法核心
if quality >= 3:  # 回答正确
    if review_count == 0:
        interval = 1
    elif review_count == 1:
        interval = 6
    else:
        interval = interval * ease_factor
    
    ease_factor += (0.1 - (5 - quality) * ...)
else:  # 回答错误
    interval = 1
    ease_factor -= 0.2
```

**质量评分**：
- 0: 完全忘记
- 1: 困难，需要提示
- 2: 困难，但能回忆
- 3: 一般
- 4: 容易
- 5: 非常简单

**实现位置**：`src/services/flashcard_service.py`

### 六、Web API设计

#### 6.1 RESTful API设计

```
GET  /api/chapters              # 获取章节列表
GET  /api/chapters?subject=math # 按科目筛选
GET  /api/subjects              # 获取科目列表
GET  /api/chapters/{id}/questions # 获取章节题目
GET  /api/questions/{id}         # 获取题目详情
POST /api/sessions              # 创建会话
POST /api/sessions/{id}/message  # 发送消息
POST /api/upload/file            # 上传文件
POST /api/questions/generate     # 生成题目
POST /api/questions/export       # 导出题目
GET  /api/flashcards/due        # 获取需要复习的抽认卡
POST /api/flashcards/{id}/review # 复习抽认卡
```

#### 6.2 流式响应

对话使用流式响应，实时显示AI回复：

```python
async for chunk, node in qa_system.process_answer(session_id, answer):
    yield chunk  # 实时返回文本块
```

**实现位置**：`web/api/endpoints/sessions.py`

### 七、前端实现

#### 7.1 科目选择

```javascript
// 加载科目列表
const subjects = await fetch('/api/subjects');

// 选择科目后加载章节
const chapters = await fetch(`/api/chapters?subject=${subjectId}`);
```

#### 7.2 实时对话

```javascript
// 使用Server-Sent Events或流式响应
const response = await fetch('/api/sessions/{id}/message', {
    method: 'POST',
    body: JSON.stringify({content: answer})
});

// 处理流式响应
const reader = response.body.getReader();
while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    // 显示文本块
}
```

**实现位置**：`web/static/js/chat.js`

## 🔧 关键技术决策

### 1. 为什么选择LangGraph？

**优势**：
- 灵活的工作流定义
- 内置状态管理
- 支持复杂决策逻辑
- 易于调试和扩展

**替代方案**：
- 纯LangChain：工作流定义不够灵活
- 自定义状态机：需要大量代码

### 2. 为什么使用JSON存储？

**优势**：
- 人类可读，易于编辑
- 版本控制友好
- 无需数据库服务器
- 易于迁移

**未来扩展**：
- 可以迁移到MongoDB
- 当前JSON格式兼容数据库schema

### 3. 为什么使用Pickle索引？

**优势**：
- Python原生支持
- 保持完整对象结构
- 加载速度快

**缺点**：
- 仅Python可用
- 数据更新需重建

**替代方案**：
- SQLite：需要定义schema
- Redis：需要额外服务

## 📊 性能优化

### 1. 索引缓存
- 首次加载：读取JSON → 构建索引 → 保存
- 后续加载：直接加载索引文件

### 2. 异步处理
- 文件上传：后台异步处理
- 题目提取：不阻塞用户请求

### 3. 流式响应
- 对话响应：实时返回，不等待完整响应

## 🚀 扩展性设计

### 1. 模块化架构
- 每个功能独立服务
- 易于添加新功能
- 易于替换实现

### 2. 配置化
- 模型可配置（DeepSeek/Qwen等）
- 数据路径可配置
- API密钥环境变量管理

### 3. 数据格式兼容
- 向后兼容原有数据结构
- 支持新旧数据共存

## 🔐 安全性考虑

### 1. 文件上传
- 文件类型验证
- 文件大小限制
- 路径安全检查

### 2. API安全
- 输入验证（Pydantic）
- 错误处理
- 异常捕获

## 📈 未来改进方向

1. **数据库迁移**：从JSON迁移到MongoDB/SQLite
2. **用户系统**：添加用户登录和个人数据
3. **学习分析**：统计学习进度和效果
4. **移动端**：开发移动应用
5. **离线支持**：支持本地模型运行

---

**详细实现代码请参考**：
- `PROJECT_INTRODUCTION.md` - 项目详细介绍
- 源代码注释 - 各模块的详细实现
