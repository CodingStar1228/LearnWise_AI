# src/knowledge_qa_system.py (修订版)
import os
import json
from uuid import uuid4
from typing import Dict, List, Optional, Any, Tuple

from langchain_core.messages import HumanMessage

from data.ds_data.data_processing.index_builder import KnowledgeIndexSystem
from data.high_school_data_loader import HighSchoolDataLoader
from src.agents.workflow import create_workflow
from src.agents.llm.env import get_default_model_backend

# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DS_INDICES_PATH = os.path.join(ROOT_DIR, "data", "ds_data", "ds_indices.pkl")
HS_INDICES_PATH = os.path.join(ROOT_DIR, "data", "hs_indices.pkl")

class KnowledgeQASystem:
    """知识问答系统，整合知识点索引和智能体问答功能"""
    
    def __init__(self, 
                 indices_path: str = DS_INDICES_PATH,
                 use_high_school_data: bool = True,
                 router_model_type: Optional[str] = None,
                 teacher_model_type: Optional[str] = None,
                 student_model_type: Optional[str] = None):
        """
        初始化知识问答系统
        
        Args:
            indices_path: 索引文件路径（用于旧数据结构）
            use_high_school_data: 是否使用高中教学系统数据
            router_model_type: 路由模型类型
            teacher_model_type: 教师模型类型
            student_model_type: 学生模型类型
        """
        self.use_high_school_data = use_high_school_data
        
        # 加载数据系统
        if use_high_school_data:
            # 尝试加载高中数据
            if os.path.exists(HS_INDICES_PATH):
                try:
                    self.index_system = HighSchoolDataLoader.load_indices(HS_INDICES_PATH)
                    print("✅ 已加载高中教学系统数据")
                except Exception as e:
                    print(f"⚠️  加载高中数据失败: {e}，尝试重新加载...")
                    self.index_system = HighSchoolDataLoader()
                    self.index_system.load_all_subjects()
                    self.index_system.save_indices(HS_INDICES_PATH)
            else:
                # 首次运行，加载并保存
                self.index_system = HighSchoolDataLoader()
                self.index_system.load_all_subjects()
                self.index_system.save_indices(HS_INDICES_PATH)
        else:
            # 使用原有数据结构
            self.index_system = KnowledgeIndexSystem.load_indices(indices_path)
        
        # 创建智能体工作流（默认 self-hosted local_vllm）
        default_backend = get_default_model_backend()
        self.workflow = create_workflow(
            router_model_type=router_model_type or default_backend,
            teacher_model_type=teacher_model_type or default_backend,
            student_model_type=student_model_type or default_backend,
        )

        self.sessions = {}
        
        
    def get_chapters(self, subject: Optional[str] = None) -> List[Dict]:
        """
        获取所有章节
        
        Args:
            subject: 科目筛选（可选）
        
        Returns:
            章节信息列表
        """
        if self.use_high_school_data and hasattr(self.index_system, 'get_chapters_by_subject'):
            if subject:
                chapters = self.index_system.get_chapters_by_subject(subject)
            else:
                chapters = self.index_system.get_all_chapters()
        else:
            chapters = self.index_system.get_chapter_list()
        
        # 按章节ID排序
        chapters.sort(key=lambda x: x.get("order", 0) if isinstance(x.get("order"), int) else 0)
        return chapters
    
    def chapter_knowledge_points(self) -> Dict[str, List[str]]:
        """
        获取所有章节的知识点
        """
        chapters_knowledge_points = {}
        for chapter_id, chapter_info in self.index_system.chapter_index.items():
            chapters_knowledge_points[chapter_id] = chapter_info['knowledge_points']
        return chapters_knowledge_points
    
    def knowledge_points_summary_by_knowledge_id(self, knowledge_id: str) -> str:
        """
        获取指定知识点对应的总结
        """
        return self.index_system.get_knowledge_point(knowledge_id)['summry']
    
    def get_knowledge_name_by_knowledge_id(self, knowledge_id: str) -> str:
        """
        获取指定知识点对应的名称
        """
        return self.index_system.get_knowledge_point(knowledge_id)['title']
    
    def get_questions_by_chapter(self, chapter_id: str) -> List[Dict]:
        """
        获取指定章节的所有问题
        
        Args:
            chapter_id: 章节ID，例如 "01"
            
        Returns:
            问题列表
        """
        questions = []
        for q in self.index_system.get_questions_by_chapter(chapter_id):
            # 返回精简版的问题列表，只包含必要信息
            questions.append({
                "id": q["id"],
                "title": q["title"],
                "type": q.get("type", "选择题"),
                "difficulty": q.get("difficulty", "中等")
            })
        return questions
    
    def get_question_detail(self, question_id: str) -> Optional[Dict]:
        """
        获取问题详情
        
        Args:
            question_id: 问题ID，例如 "q011002"
            
        Returns:
            问题详情
        """
        return self.index_system.get_question(question_id)
    
    def create_session(self, question_id: str) -> str:
        """
        创建问答会话
        
        Args:
            question_id: 问题ID
            
        Returns:
            会话ID
        """
        # 获取问题详情
        question = self.index_system.get_question(question_id)
        if not question:
            raise ValueError(f"找不到问题: {question_id}")
        
        # 创建会话ID
        session_id = str(uuid4())
        
        # 初始化会话元数据 (不存储消息历史，由LangGraph管理)
        self.sessions[session_id] = {
            "question_id": question_id,
            "question": question,
            "status": "created",
            "last_evaluation": {}  # 最近一次评估结果
        }
        
        return session_id
    
    async def process_answer(self, session_id: str, answer: str):
        """
        处理用户回答
        
        Args:
            session_id: 会话ID
            answer: 用户回答内容
            
        Returns:
            处理结果，包含AI回复和评估结果
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"找不到会话: {session_id}")
        
        # 准备用户消息
        user_message = HumanMessage(content=answer)
        
        # 准备工作流配置 - 使用会话的thread_id
        config = {"configurable": {"thread_id": session_id}}
        
        # 获取当前会话的工作流状态
        inputs = {
            "messages": [user_message],  # 只传递当前消息，历史消息由LangGraph基于thread_id管理
            "question": [session["question"]],
            "evaluation": {},
            "log": ""
        }
        
        print("开始处理回答...")
        async for msg, metadata in self.workflow.astream(inputs, config, stream_mode="messages"):
            yield msg.content, metadata['langgraph_node']
        

    def get_session_info(self, session_id: str) -> Dict:
        """获取会话信息"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"找不到会话: {session_id}")
        
        return {
            "session_id": session_id,
            "question_id": session["question_id"],
            "status": session["status"],
            "last_evaluation": session["last_evaluation"]
            # 注意：我们不再返回历史消息，因为它们由LangGraph管理
        }
    
    def get_related_knowledge_points(self, question_id: str) -> List[Dict]:
        """
        获取问题相关的知识点
        
        Args:
            question_id: 问题ID
            
        Returns:
            相关知识点列表
        """
        question = self.get_question_detail(question_id)
        if not question or "knowledge_points" not in question:
            return []
        
        knowledge_points = []
        for kp_id in question["knowledge_points"]:
            kp = self.index_system.get_knowledge_point(kp_id)
            if kp:
                knowledge_points.append({
                    "id": kp_id,
                    "title": kp.get("title", ""),
                    "summry": kp.get("summry", "")
                })
        
        return knowledge_points
    
    def get_similar_questions(self, question_id: str, limit: int = 5) -> List[Dict]:
        """
        获取与当前问题相似的其他问题
        
        Args:
            question_id: 问题ID
            limit: 返回的问题数量限制
            
        Returns:
            相似问题列表
        """
        question = self.get_question_detail(question_id)
        if not question or "knowledge_points" not in question:
            return []
        
        # 基于共同知识点查找相似题目
        similar_questions = []
        seen_ids = {question_id}  # 排除当前问题
        
        for kp_id in question["knowledge_points"]:
            questions = self.index_system.get_questions_by_knowledge(kp_id)
            for q in questions:
                q_id = q["id"]
                if q_id not in seen_ids:
                    similar_questions.append({
                        "id": q_id,
                        "title": q["title"],
                        "type": q.get("type", "选择题")
                    })
                    seen_ids.add(q_id)
                    
                    if len(similar_questions) >= limit:
                        return similar_questions
        
        return similar_questions
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否删除成功
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    # ========== 新增方法：高中教学系统扩展功能 ==========
    
    def get_questions_by_subject(self, subject: str) -> List[Dict]:
        """
        按科目获取题目
        
        Args:
            subject: 科目 (math, physics, chemistry, biology, english, chinese)
            
        Returns:
            题目列表
        """
        all_questions = []
        # 遍历所有章节获取题目
        chapters = self.get_chapters()
        for chapter in chapters:
            questions = self.index_system.get_questions_by_chapter(chapter["id"])
            for q in questions:
                # 检查科目匹配（如果题目有subject字段）
                if q.get("subject") == subject:
                    all_questions.append({
                        "id": q["id"],
                        "title": q["title"],
                        "type": q.get("type", "选择题"),
                        "difficulty": q.get("difficulty", 3),
                        "subject": q.get("subject", ""),
                        "tags": q.get("tags", [])
                    })
        return all_questions
    
    def get_questions_by_tags(self, tags: List[str], match_all: bool = False) -> List[Dict]:
        """
        按标签获取题目
        
        Args:
            tags: 标签列表
            match_all: 如果为True，题目必须包含所有标签；如果为False，包含任一标签即可
            
        Returns:
            题目列表
        """
        all_questions = []
        chapters = self.get_chapters()
        for chapter in chapters:
            questions = self.index_system.get_questions_by_chapter(chapter["id"])
            for q in questions:
                question_tags = q.get("tags", [])
                if not question_tags:
                    continue
                
                # 检查标签匹配
                if match_all:
                    # 必须包含所有标签
                    if all(tag in question_tags for tag in tags):
                        all_questions.append({
                            "id": q["id"],
                            "title": q["title"],
                            "type": q.get("type", "选择题"),
                            "difficulty": q.get("difficulty", 3),
                            "subject": q.get("subject", ""),
                            "tags": question_tags
                        })
                else:
                    # 包含任一标签即可
                    if any(tag in question_tags for tag in tags):
                        all_questions.append({
                            "id": q["id"],
                            "title": q["title"],
                            "type": q.get("type", "选择题"),
                            "difficulty": q.get("difficulty", 3),
                            "subject": q.get("subject", ""),
                            "tags": question_tags
                        })
        return all_questions
    
    def get_questions_by_subject_and_tags(
        self, 
        subject: Optional[str] = None, 
        tags: Optional[List[str]] = None,
        grade: Optional[str] = None,
        difficulty: Optional[int] = None
    ) -> List[Dict]:
        """
        按多个条件筛选题目
        
        Args:
            subject: 科目
            tags: 标签列表
            grade: 年级
            difficulty: 难度等级
            
        Returns:
            题目列表
        """
        all_questions = []
        chapters = self.get_chapters()
        for chapter in chapters:
            questions = self.index_system.get_questions_by_chapter(chapter["id"])
            for q in questions:
                # 科目筛选
                if subject and q.get("subject") != subject:
                    continue
                
                # 年级筛选
                if grade and q.get("grade") != grade:
                    continue
                
                # 难度筛选
                if difficulty and q.get("difficulty") != difficulty:
                    continue
                
                # 标签筛选
                if tags:
                    question_tags = q.get("tags", [])
                    if not any(tag in question_tags for tag in tags):
                        continue
                
                all_questions.append({
                    "id": q["id"],
                    "title": q["title"],
                    "type": q.get("type", "选择题"),
                    "difficulty": q.get("difficulty", 3),
                    "subject": q.get("subject", ""),
                    "grade": q.get("grade", ""),
                    "tags": q.get("tags", [])
                })
        return all_questions
    
    def add_tags_to_question(self, question_id: str, tags: List[str]) -> bool:
        """
        为题目添加标签
        
        Args:
            question_id: 题目ID
            tags: 要添加的标签列表
            
        Returns:
            是否成功
        """
        question = self.get_question_detail(question_id)
        if not question:
            return False
        
        existing_tags = question.get("tags", [])
        # 合并标签，去重
        new_tags = list(set(existing_tags + tags))
        question["tags"] = new_tags
        
        # 这里需要保存回存储系统（根据实际存储方式实现）
        # 如果是文件存储，需要更新对应的JSON文件
        # 如果是数据库，需要更新数据库记录
        # 暂时返回True，实际实现需要根据存储方式调整
        return True
    
    def remove_tag_from_question(self, question_id: str, tag: str) -> bool:
        """
        从题目中移除标签
        
        Args:
            question_id: 题目ID
            tag: 要移除的标签
            
        Returns:
            是否成功
        """
        question = self.get_question_detail(question_id)
        if not question:
            return False
        
        tags = question.get("tags", [])
        if tag in tags:
            tags.remove(tag)
            question["tags"] = tags
            # 保存更新（需要根据实际存储方式实现）
            return True
        return False
    
    def get_all_subjects(self) -> List[str]:
        """
        获取所有科目列表
        
        Returns:
            科目列表
        """
        if self.use_high_school_data and hasattr(self.index_system, 'subjects'):
            # 从数据加载器获取科目列表
            return self.index_system.subjects
        
        # 兼容旧版本：从章节中提取科目
        subjects = set()
        chapters = self.get_chapters()
        for chapter in chapters:
            subject = chapter.get("subject")
            if subject:
                subjects.add(subject)
        return sorted(list(subjects))
    
    def get_all_tags(self, subject: Optional[str] = None) -> List[str]:
        """
        获取所有标签列表
        
        Args:
            subject: 如果提供，只返回该科目的标签
            
        Returns:
            标签列表
        """
        tags = set()
        chapters = self.get_chapters()
        for chapter in chapters:
            questions = self.index_system.get_questions_by_chapter(chapter["id"])
            for q in questions:
                # 科目筛选
                if subject and q.get("subject") != subject:
                    continue
                
                question_tags = q.get("tags", [])
                tags.update(question_tags)
        return sorted(list(tags))