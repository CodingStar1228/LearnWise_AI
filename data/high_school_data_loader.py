"""
高中教学系统数据加载器
支持多科目数据加载
"""

import json
import os
import pickle
from typing import Dict, List, Optional
from pathlib import Path


class HighSchoolDataLoader:
    """高中教学系统数据加载器"""
    
    def __init__(self, data_dir: str = None):
        """
        初始化数据加载器
        
        Args:
            data_dir: 数据目录路径，默认为 high_school_data 目录
        """
        if data_dir is None:
            # 默认使用 high_school_data 目录
            current_file = Path(__file__)
            self.data_dir = current_file.parent / "high_school_data"
        else:
            self.data_dir = Path(data_dir)
        
        # 科目列表
        self.subjects = ["math", "physics", "chemistry", "biology", "english", "chinese", "data_structure"]
        
        # 索引
        self.knowledge_index: Dict[str, dict] = {}
        self.knowledge_question_index: Dict[str, List[str]] = {}
        self.question_index: Dict[str, dict] = {}
        self.chapter_index: Dict[str, dict] = {}
        self.subject_chapters: Dict[str, List[dict]] = {}  # 按科目组织的章节
        
    def load_all_subjects(self):
        """加载所有科目的数据"""
        print("开始加载高中教学系统数据...")
        
        for subject_id in self.subjects:
            subject_dir = self.data_dir / subject_id
            if subject_dir.exists():
                print(f"\n加载 {subject_id} 科目数据...")
                self._load_subject(subject_id)
            else:
                print(f"⚠️  科目 {subject_id} 数据目录不存在，跳过")
        
        print(f"\n✅ 数据加载完成！")
        print(f"   - 章节数: {len(self.chapter_index)}")
        print(f"   - 题目数: {len(self.question_index)}")
        print(f"   - 知识点数: {len(self.knowledge_index)}")
    
    def _load_subject(self, subject_id: str):
        """加载单个科目的数据"""
        subject_dir = self.data_dir / subject_id
        
        # 加载章节
        chapters_file = subject_dir / "chapters" / "chapters.json"
        if chapters_file.exists():
            with open(chapters_file, 'r', encoding='utf-8') as f:
                chapters = json.load(f)
                self.subject_chapters[subject_id] = chapters
                for chapter in chapters:
                    chapter['subject'] = subject_id  # 添加科目信息
                    self.chapter_index[chapter['id']] = chapter
            print(f"  ✅ 加载了 {len(chapters)} 个章节")
        else:
            print(f"  ⚠️  章节文件不存在: {chapters_file}")
        
        # 加载知识点
        kp_dir = subject_dir / "knowledgepoints"
        if kp_dir.exists():
            kp_count = 0
            for kp_file in kp_dir.glob("*.json"):
                with open(kp_file, 'r', encoding='utf-8') as f:
                    knowledge_points = json.load(f)
                    for kp in knowledge_points:
                        kp['subject'] = subject_id  # 添加科目信息
                        self.knowledge_index[kp['id']] = kp
                        if 'questions' in kp:
                            self.knowledge_question_index[kp['id']] = kp['questions']
                        else:
                            self.knowledge_question_index[kp['id']] = []
                        kp_count += 1
            print(f"  ✅ 加载了 {kp_count} 个知识点")
        
        # 加载题目
        q_dir = subject_dir / "questions"
        if q_dir.exists():
            q_count = 0
            for q_file in q_dir.glob("*.json"):
                with open(q_file, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                    for q in questions:
                        # 确保题目有科目信息
                        if 'subject' not in q:
                            q['subject'] = subject_id
                        
                        self.question_index[q['id']] = q
                        
                        # 更新知识点-题目索引
                        if 'knowledge_points' in q:
                            for kp_id in q['knowledge_points']:
                                if kp_id not in self.knowledge_question_index:
                                    self.knowledge_question_index[kp_id] = []
                                if q['id'] not in self.knowledge_question_index[kp_id]:
                                    self.knowledge_question_index[kp_id].append(q['id'])
                        q_count += 1
            print(f"  ✅ 加载了 {q_count} 个题目")
    
    def get_chapters_by_subject(self, subject_id: str) -> List[Dict]:
        """获取指定科目的章节列表"""
        if subject_id in self.subject_chapters:
            return self.subject_chapters[subject_id]
        return []
    
    def get_all_chapters(self) -> List[Dict]:
        """获取所有章节"""
        return list(self.chapter_index.values())
    
    def get_questions_by_chapter(self, chapter_id: str) -> List[Dict]:
        """获取指定章节的题目"""
        questions = []
        for q_id, q in self.question_index.items():
            if q.get('chapter') == chapter_id:
                questions.append(q)
        return questions
    
    def get_questions_by_subject(self, subject_id: str) -> List[Dict]:
        """获取指定科目的题目"""
        questions = []
        for q_id, q in self.question_index.items():
            if q.get('subject') == subject_id:
                questions.append(q)
        return questions
    
    def get_question(self, question_id: str) -> Optional[Dict]:
        """获取题目详情"""
        return self.question_index.get(question_id)
    
    def get_knowledge_point(self, knowledge_id: str) -> Optional[Dict]:
        """获取知识点详情"""
        return self.knowledge_index.get(knowledge_id)
    
    def get_questions_by_knowledge(self, knowledge_id: str) -> List[Dict]:
        """获取指定知识点的题目"""
        question_ids = self.knowledge_question_index.get(knowledge_id, [])
        questions = []
        for q_id in question_ids:
            if q_id in self.question_index:
                questions.append(self.question_index[q_id])
        return questions
    
    def save_indices(self, filepath: str):
        """保存索引到文件"""
        indices = {
            'knowledge_index': self.knowledge_index,
            'knowledge_question_index': self.knowledge_question_index,
            'question_index': self.question_index,
            'chapter_index': self.chapter_index,
            'subject_chapters': self.subject_chapters
        }
        with open(filepath, 'wb') as f:
            pickle.dump(indices, f)
        print(f"✅ 索引已保存到: {filepath}")
    
    @classmethod
    def load_indices(cls, filepath: str):
        """从文件加载索引"""
        with open(filepath, 'rb') as f:
            indices = pickle.load(f)
        
        loader = cls()
        loader.knowledge_index = indices.get('knowledge_index', {})
        loader.knowledge_question_index = indices.get('knowledge_question_index', {})
        loader.question_index = indices.get('question_index', {})
        loader.chapter_index = indices.get('chapter_index', {})
        loader.subject_chapters = indices.get('subject_chapters', {})
        
        print(f"✅ 索引已从 {filepath} 加载")
        return loader


if __name__ == "__main__":
    # 测试数据加载
    loader = HighSchoolDataLoader()
    loader.load_all_subjects()
    
    # 保存索引
    indices_file = loader.data_dir.parent / "hs_indices.pkl"
    loader.save_indices(str(indices_file))
    
    # 测试查询
    print("\n" + "="*50)
    print("测试查询功能")
    print("="*50)
    
    # 获取数学科目的章节
    math_chapters = loader.get_chapters_by_subject("math")
    print(f"\n数学科目章节数: {len(math_chapters)}")
    if math_chapters:
        print(f"第一个章节: {math_chapters[0]['title']}")
