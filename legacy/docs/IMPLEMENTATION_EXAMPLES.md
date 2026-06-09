# 实现示例代码

本文档提供关键功能的具体实现代码示例。

## 一、数据库Schema扩展示例

### 1.1 修改后的Question模型

```python
# src/database/schema.py

class Question(BaseModel):
    """问题模型（扩展版）"""
    id: str = Field(..., description="问题唯一标识符")
    title: str = Field(..., description="问题标题")
    content: str = Field(..., description="问题内容")
    difficulty: int = Field(1, description="难度等级 (1-5)")
    type: str = Field(..., description="问题类型 (choice, fill, essay, calculation)")
    
    # 新增字段
    subject: str = Field(..., description="科目 (math, physics, chemistry, biology, english, chinese)")
    grade: str = Field(default="", description="年级 (grade1, grade2, grade3)")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    source: str = Field(default="manual", description="来源 (upload, generate, manual)")
    upload_file_id: Optional[str] = Field(None, description="上传文件ID")
    
    # 原有字段
    knowledge_points: List[str] = Field(default_factory=list, description="相关知识点ID列表")
    related_questions: List[RelatedQuestion] = Field(default_factory=list, description="相关问题")
    reference_answer: ReferenceAnswer = Field(..., description="参考答案")
    
    # 新增：视频推荐
    video_recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="推荐视频")
```

### 1.2 新增模型

```python
# src/database/schema.py

from datetime import datetime
from typing import Optional

class UploadedFile(BaseModel):
    """上传文件模型"""
    id: str = Field(..., description="文件唯一标识符")
    filename: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型 (pdf, image)")
    file_path: str = Field(..., description="文件存储路径")
    upload_time: datetime = Field(default_factory=datetime.now, description="上传时间")
    file_size: int = Field(..., description="文件大小（字节）")
    processed: bool = Field(default=False, description="是否已处理")
    processing_status: str = Field(default="pending", description="处理状态")
    extracted_text: Optional[str] = Field(None, description="提取的文本")
    questions: List[str] = Field(default_factory=list, description="提取的题目ID列表")
    error_message: Optional[str] = Field(None, description="错误信息")

class FlashCard(BaseModel):
    """抽认卡模型"""
    id: str = Field(..., description="抽认卡唯一标识符")
    question_id: str = Field(..., description="关联的题目ID")
    front: str = Field(..., description="正面内容（问题）")
    back: str = Field(..., description="背面内容（答案）")
    subject: str = Field(..., description="科目")
    tags: List[str] = Field(default_factory=list, description="标签")
    difficulty: int = Field(1, description="难度")
    
    # 间隔重复算法相关
    review_count: int = Field(default=0, description="复习次数")
    ease_factor: float = Field(default=2.5, description="易度因子（SM-2算法）")
    interval: int = Field(default=1, description="复习间隔（天）")
    last_review: Optional[datetime] = Field(None, description="上次复习时间")
    next_review: Optional[datetime] = Field(None, description="下次复习时间")
    quality: int = Field(default=0, description="上次复习质量 (0-5)")

class PomodoroSession(BaseModel):
    """番茄钟会话模型"""
    id: str = Field(..., description="会话唯一标识符")
    user_id: str = Field(..., description="用户ID")
    subject: str = Field(..., description="学习科目")
    start_time: datetime = Field(..., description="开始时间")
    duration: int = Field(25, description="时长（分钟）")
    completed: bool = Field(default=False, description="是否完成")
    break_time: int = Field(default=5, description="休息时间（分钟）")
    question_ids: List[str] = Field(default_factory=list, description="学习的题目ID列表")
```

## 二、文件上传服务示例

### 2.1 文件上传服务

```python
# src/services/file_upload_service.py

import os
import uuid
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import asyncio

from data.ds_data.data_processing.pdf_extractor import PDFExtractor
from paddleocr import PaddleOCR
from PIL import Image
import io

class FileUploadService:
    """文件上传和处理服务"""
    
    def __init__(self, upload_dir: str = "data/uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')
        
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> Dict:
        """保存上传的文件"""
        file_id = str(uuid.uuid4())
        file_ext = Path(filename).suffix.lower()
        
        # 确定文件类型
        if file_ext == '.pdf':
            file_type = 'pdf'
        elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            file_type = 'image'
        else:
            raise ValueError(f"不支持的文件类型: {file_ext}")
        
        # 保存文件
        file_path = self.upload_dir / f"{file_id}{file_ext}"
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return {
            "id": file_id,
            "filename": filename,
            "file_type": file_type,
            "file_path": str(file_path),
            "upload_time": datetime.now(),
            "file_size": len(file_content),
            "processed": False,
            "processing_status": "pending"
        }
    
    async def extract_text_from_file(self, file_info: Dict) -> str:
        """从文件中提取文本"""
        file_path = file_info["file_path"]
        file_type = file_info["file_type"]
        
        if file_type == "pdf":
            # 使用PDFExtractor
            output_dir = self.upload_dir / file_info["id"]
            extractor = PDFExtractor(
                file_path, 
                str(output_dir), 
                is_scanned=True,  # 可以根据实际情况判断
                lang='ch'
            )
            extractor.extract_text()
            
            # 读取提取的文本
            text_files = list((output_dir / "text").glob("*.txt"))
            all_text = ""
            for text_file in sorted(text_files):
                with open(text_file, 'r', encoding='utf-8') as f:
                    all_text += f.read() + "\n"
            
            return all_text
        
        elif file_type == "image":
            # 使用OCR识别图片
            result = self.ocr.ocr(file_path)
            text = ""
            if result and result[0]:
                for line in result[0]:
                    text += line[1][0] + "\n"
            return text
        
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
    
    async def extract_questions_from_text(self, text: str, subject: str) -> List[Dict]:
        """从文本中提取题目（使用LLM）"""
        # 这里需要调用LLM API来分析文本并提取题目
        # 示例使用DeepSeek API
        
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY")
        )
        
        prompt = f"""你是一个题目提取专家。请从以下文本中识别并提取所有题目。

要求：
1. 识别题目的类型（选择题、填空题、解答题等）
2. 提取题目的完整内容，包括题目、选项（如果有）、答案
3. 识别题目所属的科目和知识点
4. 为题目添加合适的标签
5. 评估题目难度（1-5）

文本内容：
{text[:5000]}  # 限制长度避免超出token限制

请以JSON格式返回，格式如下：
{{
    "questions": [
        {{
            "title": "题目标题",
            "content": "题目完整内容",
            "type": "choice/fill/essay",
            "options": {{"A": "...", "B": "...", ...}},  # 如果是选择题
            "answer": "答案",
            "explanation": "解析",
            "tags": ["标签1", "标签2"],
            "difficulty": 3,
            "knowledge_points": ["知识点1", "知识点2"]
        }}
    ]
}}
"""
        
        response = await llm.ainvoke(prompt)
        # 解析JSON响应
        import json
        result = json.loads(response.content)
        return result.get("questions", [])
```

### 2.2 文件上传API端点

```python
# web/api/endpoints/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
import os
from src.services.file_upload_service import FileUploadService
from web.models.schemas import UploadedFileInfo, QuestionInfo

router = APIRouter()
upload_service = FileUploadService()

@router.post("/upload/file", response_model=UploadedFileInfo)
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """上传文件"""
    try:
        # 读取文件内容
        content = await file.read()
        
        # 保存文件
        file_info = await upload_service.save_uploaded_file(content, file.filename)
        
        # 异步处理文件
        if background_tasks:
            background_tasks.add_task(process_file_async, file_info["id"])
        
        return file_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_file_async(file_id: str):
    """异步处理文件"""
    # 获取文件信息
    file_info = get_file_info(file_id)  # 需要实现
    file_info["processing_status"] = "processing"
    
    try:
        # 提取文本
        text = await upload_service.extract_text_from_file(file_info)
        file_info["extracted_text"] = text
        
        # 提取题目
        subject = detect_subject(text)  # 需要实现科目检测
        questions = await upload_service.extract_questions_from_text(text, subject)
        
        # 保存题目到数据库
        question_ids = []
        for q in questions:
            question_id = save_question(q)  # 需要实现
            question_ids.append(question_id)
        
        file_info["questions"] = question_ids
        file_info["processed"] = True
        file_info["processing_status"] = "completed"
        
    except Exception as e:
        file_info["processing_status"] = "failed"
        file_info["error_message"] = str(e)
    
    # 更新文件信息
    update_file_info(file_id, file_info)  # 需要实现

@router.get("/upload/files", response_model=List[UploadedFileInfo])
async def get_uploaded_files():
    """获取所有上传的文件"""
    # 实现获取文件列表
    pass

@router.get("/upload/{file_id}/status")
async def get_file_status(file_id: str):
    """获取文件处理状态"""
    # 实现获取状态
    pass
```

## 三、题目生成服务示例

### 3.1 题目生成服务

```python
# src/services/question_generator.py

from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
import json
import os

class QuestionGenerator:
    """题目生成服务"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY")
        )
    
    async def generate_similar_question(
        self, 
        original_question: Dict,
        difficulty: Optional[int] = None,
        variations: int = 1
    ) -> List[Dict]:
        """生成相似题目"""
        
        prompt = f"""基于以下题目，生成{variations}道相似但不同的新题目。

原题目：
标题：{original_question.get('title', '')}
内容：{original_question.get('content', '')}
类型：{original_question.get('type', '')}
难度：{original_question.get('difficulty', 3)}
科目：{original_question.get('subject', '')}
标签：{', '.join(original_question.get('tags', []))}

要求：
1. 保持相同的知识点和难度级别
2. 改变具体数值、场景或表述方式
3. 确保题目逻辑正确，答案准确
4. 如果是选择题，生成完整的选项
5. 提供详细的解析

请以JSON格式返回，格式如下：
{{
    "questions": [
        {{
            "title": "题目标题",
            "content": "题目完整内容",
            "type": "{original_question.get('type', 'choice')}",
            "options": {{"A": "...", "B": "...", ...}},
            "answer": "答案",
            "explanation": "详细解析",
            "difficulty": {difficulty or original_question.get('difficulty', 3)},
            "tags": {json.dumps(original_question.get('tags', []))},
            "subject": "{original_question.get('subject', '')}"
        }}
    ]
}}
"""
        
        response = await self.llm.ainvoke(prompt)
        result = json.loads(response.content)
        return result.get("questions", [])
    
    async def generate_questions_by_topic(
        self,
        topic: str,
        subject: str,
        difficulty: int,
        count: int = 5
    ) -> List[Dict]:
        """根据主题生成题目"""
        
        prompt = f"""请生成{count}道关于"{topic}"的{subject}题目。

要求：
1. 难度级别：{difficulty}（1-5）
2. 题目类型多样化（选择题、填空题、解答题）
3. 每道题都要有完整的答案和解析
4. 题目要符合高中教学大纲

请以JSON格式返回题目列表。
"""
        
        response = await self.llm.ainvoke(prompt)
        result = json.loads(response.content)
        return result.get("questions", [])
```

## 四、抽认卡服务示例

### 4.1 抽认卡服务（包含间隔重复算法）

```python
# src/services/flashcard_service.py

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import math

class FlashCardService:
    """抽认卡服务，实现SM-2间隔重复算法"""
    
    def create_flashcard_from_question(self, question: Dict) -> Dict:
        """从题目创建抽认卡"""
        return {
            "id": f"fc_{question['id']}",
            "question_id": question["id"],
            "front": self._generate_front(question),
            "back": self._generate_back(question),
            "subject": question.get("subject", ""),
            "tags": question.get("tags", []),
            "difficulty": question.get("difficulty", 3),
            "review_count": 0,
            "ease_factor": 2.5,
            "interval": 1,
            "last_review": None,
            "next_review": datetime.now(),
            "quality": 0
        }
    
    def _generate_front(self, question: Dict) -> str:
        """生成抽认卡正面内容"""
        content = question.get("content", "")
        if question.get("type") == "choice" and question.get("options"):
            options_text = "\n".join([f"{k}. {v}" for k, v in question["options"].items()])
            return f"{content}\n\n{options_text}"
        return content
    
    def _generate_back(self, question: Dict) -> str:
        """生成抽认卡背面内容"""
        answer = question.get("reference_answer", {}).get("content", "")
        explanation = question.get("reference_answer", {}).get("explanation", "")
        return f"答案：{answer}\n\n解析：{explanation}"
    
    def review_flashcard(self, card: Dict, quality: int) -> Dict:
        """
        复习抽认卡并更新间隔
        
        quality: 复习质量 (0-5)
        0: 完全忘记
        1: 困难，需要提示
        2: 困难，但能回忆起来
        3: 一般
        4: 容易
        5: 非常简单
        """
        if quality < 0 or quality > 5:
            raise ValueError("quality must be between 0 and 5")
        
        # SM-2算法
        if quality < 3:
            # 回答错误，重置
            card["interval"] = 1
            card["ease_factor"] = max(1.3, card["ease_factor"] - 0.2)
        else:
            # 回答正确
            if card["review_count"] == 0:
                card["interval"] = 1
            elif card["review_count"] == 1:
                card["interval"] = 6
            else:
                card["interval"] = int(card["interval"] * card["ease_factor"])
            
            # 更新易度因子
            card["ease_factor"] = card["ease_factor"] + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            card["ease_factor"] = max(1.3, card["ease_factor"])
        
        # 更新复习信息
        card["review_count"] += 1
        card["quality"] = quality
        card["last_review"] = datetime.now()
        card["next_review"] = datetime.now() + timedelta(days=card["interval"])
        
        return card
    
    def get_due_flashcards(self, flashcards: List[Dict]) -> List[Dict]:
        """获取需要复习的抽认卡"""
        now = datetime.now()
        return [card for card in flashcards if card.get("next_review") and card["next_review"] <= now]
    
    def get_review_statistics(self, flashcards: List[Dict]) -> Dict:
        """获取复习统计"""
        total = len(flashcards)
        due = len(self.get_due_flashcards(flashcards))
        reviewed = sum(1 for card in flashcards if card.get("review_count", 0) > 0)
        
        return {
            "total": total,
            "due": due,
            "reviewed": reviewed,
            "new": total - reviewed,
            "mastered": sum(1 for card in flashcards if card.get("ease_factor", 0) > 2.5 and card.get("review_count", 0) >= 3)
        }
```

## 五、视频推荐服务示例

### 5.1 视频推荐服务

```python
# src/services/video_recommender.py

from typing import List, Dict
import re

class VideoRecommender:
    """视频推荐服务"""
    
    def __init__(self):
        # 可以维护一个视频资源库
        self.video_database = [
            {
                "id": "v001",
                "title": "高中数学：微积分基础",
                "url": "https://www.bilibili.com/video/...",
                "platform": "bilibili",
                "subject": "math",
                "tags": ["微积分", "导数", "积分"],
                "duration": 1800,  # 秒
                "views": 10000,
                "rating": 4.5
            },
            # ... 更多视频
        ]
    
    def recommend_videos_for_question(self, question: Dict, limit: int = 5) -> List[Dict]:
        """为题目推荐视频"""
        subject = question.get("subject", "")
        tags = question.get("tags", [])
        knowledge_points = question.get("knowledge_points", [])
        
        # 匹配视频
        matched_videos = []
        for video in self.video_database:
            score = 0
            
            # 科目匹配
            if video.get("subject") == subject:
                score += 10
            
            # 标签匹配
            video_tags = video.get("tags", [])
            for tag in tags:
                if tag in video_tags:
                    score += 5
            
            # 知识点匹配
            video_knowledge = video.get("knowledge_points", [])
            for kp in knowledge_points:
                if kp in video_knowledge:
                    score += 8
            
            if score > 0:
                matched_videos.append({
                    **video,
                    "match_score": score
                })
        
        # 按分数排序
        matched_videos.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matched_videos[:limit]
    
    def search_videos(self, keyword: str, subject: Optional[str] = None) -> List[Dict]:
        """搜索视频"""
        results = []
        for video in self.video_database:
            if subject and video.get("subject") != subject:
                continue
            
            # 关键词匹配
            if keyword.lower() in video.get("title", "").lower():
                results.append(video)
        
        return results
```

## 六、API端点集成示例

### 6.1 主应用集成

```python
# web/main.py (部分修改)

from web.api.endpoints import (
    chapters, questions, sessions, knowledge,
    upload, tags, videos, pomodoro, flashcards, questions_extended
)

# ... 原有代码 ...

# 注册新路由
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(tags.router, prefix="/api", tags=["tags"])
app.include_router(videos.router, prefix="/api", tags=["videos"])
app.include_router(pomodoro.router, prefix="/api", tags=["pomodoro"])
app.include_router(flashcards.router, prefix="/api", tags=["flashcards"])
app.include_router(questions_extended.router, prefix="/api", tags=["questions_extended"])

# 添加新页面路由
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

## 七、前端JavaScript示例

### 7.1 文件上传前端

```javascript
// web/static/js/upload.js

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload/file', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        // 显示上传成功
        showUploadSuccess(result);
        
        // 开始轮询处理状态
        pollProcessingStatus(result.id);
        
    } catch (error) {
        console.error('上传失败:', error);
        showError('上传失败，请重试');
    }
}

async function pollProcessingStatus(fileId) {
    const interval = setInterval(async () => {
        const response = await fetch(`/api/upload/${fileId}/status`);
        const status = await response.json();
        
        updateProgressBar(status.processing_status);
        
        if (status.processing_status === 'completed') {
            clearInterval(interval);
            showExtractedQuestions(status.questions);
        } else if (status.processing_status === 'failed') {
            clearInterval(interval);
            showError(status.error_message);
        }
    }, 2000); // 每2秒查询一次
}
```

### 7.2 抽认卡前端

```javascript
// web/static/js/flashcards.js

let currentCard = null;
let cards = [];

async function loadFlashcards() {
    const response = await fetch('/api/flashcards/due');
    cards = await response.json();
    
    if (cards.length > 0) {
        showNextCard();
    } else {
        showNoCardsMessage();
    }
}

function showNextCard() {
    if (cards.length === 0) return;
    
    currentCard = cards.shift();
    document.getElementById('card-front').textContent = currentCard.front;
    document.getElementById('card-back').textContent = '';
    document.getElementById('card-container').classList.remove('flipped');
}

function flipCard() {
    document.getElementById('card-container').classList.add('flipped');
    document.getElementById('card-back').textContent = currentCard.back;
}

async function rateCard(quality) {
    // quality: 0-5
    const response = await fetch(`/api/flashcards/${currentCard.id}/review`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({quality: quality})
    });
    
    const updatedCard = await response.json();
    
    // 显示下一个卡片
    showNextCard();
    
    // 更新统计
    updateStatistics();
}
```

这些示例代码展示了关键功能的实现方式。你可以根据实际需求进行调整和扩展。
