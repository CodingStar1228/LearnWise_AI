# 快速开始 - 改造检查清单

## 📋 改造概览

将****改造为**高中全科目教学系统**，需要修改以下核心部分：

## 🎯 核心修改点

### 1. 数据库Schema扩展 ⭐⭐⭐
**文件**: `src/database/schema.py`
- [ ] 在`Question`模型中添加：`subject`（科目）、`tags`（标签）、`grade`（年级）
- [ ] 创建`UploadedFile`模型（文件上传）
- [ ] 创建`FlashCard`模型（抽认卡）
- [ ] 创建`PomodoroSession`模型（番茄钟）

### 2. 文件上传和OCR处理 ⭐⭐⭐
**新增文件**: 
- [ ] `src/services/file_upload_service.py` - 文件上传服务
- [ ] `web/api/endpoints/upload.py` - 上传API端点
- [ ] `web/templates/upload.html` - 上传页面
- [ ] `web/static/js/upload.js` - 上传前端逻辑

**功能**:
- 支持PDF和图片上传
- OCR文本提取
- LLM题目识别和提取

### 3. 题目生成和导出 ⭐⭐
**新增文件**:
- [ ] `src/services/question_generator.py` - 题目生成服务
- [ ] `src/services/question_exporter.py` - 题目导出服务
- [ ] `web/api/endpoints/questions_extended.py` - 扩展题目API

**功能**:
- 基于现有题目生成相似题目
- 导出为Word/PDF格式

### 4. 分类标签系统 ⭐⭐⭐
**修改文件**: `src/knowledge_qa_system.py`
- [ ] 添加`get_questions_by_subject()`方法
- [ ] 添加`get_questions_by_tags()`方法
- [ ] 添加标签管理方法

**新增文件**:
- [ ] `web/api/endpoints/tags.py` - 标签API

### 5. 视频推荐 ⭐⭐
**新增文件**:
- [ ] `src/services/video_recommender.py` - 视频推荐服务
- [ ] `web/api/endpoints/videos.py` - 视频API

### 6. 抽认卡功能 ⭐⭐
**新增文件**:
- [ ] `src/services/flashcard_service.py` - 抽认卡服务（含SM-2算法）
- [ ] `web/api/endpoints/flashcards.py` - 抽认卡API
- [ ] `web/templates/flashcards.html` - 抽认卡页面
- [ ] `web/static/js/flashcards.js` - 抽认卡前端

### 7. 番茄钟功能 ⭐
**新增文件**:
- [ ] `src/services/pomodoro_service.py` - 番茄钟服务
- [ ] `web/api/endpoints/pomodoro.py` - 番茄钟API
- [ ] `web/templates/pomodoro.html` - 番茄钟页面
- [ ] `web/static/js/pomodoro.js` - 番茄钟前端

### 8. 智能体Prompt调整 ⭐⭐⭐
**修改文件**:
- [ ] `src/agents/prompts/teacher_agent_prompt.txt`
- [ ] `src/agents/prompts/student_agent_prompt.txt`
- [ ] `src/agents/prompts/router_agent_prompt.txt`

**修改内容**:
- 将"数据结构"改为"高中各科目"
- 调整难度和深度适应高中生

### 9. Web界面更新 ⭐⭐
**修改文件**:
- [ ] `web/templates/index.html` - 添加科目选择、功能导航
- [ ] `web/templates/problems.html` - 添加筛选、导出功能
- [ ] `web/templates/chat.html` - 添加视频推荐显示

**新增文件**:
- [ ] `web/templates/upload.html`
- [ ] `web/templates/pomodoro.html`
- [ ] `web/templates/flashcards.html`

### 10. 主应用集成 ⭐⭐
**修改文件**: `web/main.py`
- [ ] 注册新的API路由
- [ ] 添加新的页面路由

## 📦 依赖项更新

**修改文件**: `requirements.txt`
- [ ] 添加 `python-multipart` (文件上传)
- [ ] 添加 `openpyxl` (Excel导出)
- [ ] 添加 `python-docx` (Word导出)
- [ ] 添加 `reportlab` (PDF生成)
- [ ] 添加 `paddleocr` (OCR，如果使用本地)
- [ ] 添加 `pdf2image` (PDF转图片)

## 🔄 实施顺序建议

### 第一阶段：核心功能（必须）
1. 数据库Schema扩展
2. 文件上传和OCR处理
3. 分类标签系统
4. 智能体Prompt调整

### 第二阶段：重要功能
5. 题目生成和导出
6. 视频推荐
7. 抽认卡功能

### 第三阶段：辅助功能
8. 番茄钟功能
9. 界面优化

## 📚 参考文档

- **详细指南**: `MODIFICATION_GUIDE.md` - 完整的修改说明
- **代码示例**: `IMPLEMENTATION_EXAMPLES.md` - 具体实现代码

## ⚠️ 注意事项

1. **数据迁移**: 如果现有数据需要保留，需要编写迁移脚本
2. **性能优化**: 文件上传和OCR处理较慢，考虑异步处理
3. **错误处理**: OCR可能失败，需要完善的错误处理
4. **安全性**: 文件上传需要验证文件类型和大小
5. **用户体验**: 添加加载状态、进度条等反馈

## 🚀 开始改造

1. 阅读 `MODIFICATION_GUIDE.md` 了解详细要求
2. 查看 `IMPLEMENTATION_EXAMPLES.md` 获取代码示例
3. 按照本清单逐步实施
4. 测试每个功能模块
5. 优化用户体验

---

**提示**: 建议先从数据库Schema和文件上传功能开始，这是其他功能的基础。
