#!/usr/bin/env python3
"""
将原有数据结构数据迁移到高中教学系统
作为"数据结构"科目的示例题目
"""

import json
import os
from pathlib import Path
from typing import Dict, List

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
DS_DATA_DIR = ROOT_DIR / "data" / "ds_data"
HS_DATA_DIR = ROOT_DIR / "data" / "high_school_data"

# 创建"数据结构"科目（作为示例）
DS_SUBJECT_ID = "data_structure"
DS_SUBJECT_NAME = "数据结构"


def migrate_chapters():
    """迁移章节数据"""
    chapters_file = DS_DATA_DIR / "chapters.json"
    if not chapters_file.exists():
        print("⚠️  未找到原有章节文件")
        return
    
    with open(chapters_file, 'r', encoding='utf-8') as f:
        ds_chapters = json.load(f)
    
    # 创建数据结构科目目录
    subject_dir = HS_DATA_DIR / DS_SUBJECT_ID
    (subject_dir / "chapters").mkdir(parents=True, exist_ok=True)
    (subject_dir / "questions").mkdir(parents=True, exist_ok=True)
    (subject_dir / "knowledgepoints").mkdir(parents=True, exist_ok=True)
    
    # 转换章节格式
    hs_chapters = []
    for chapter in ds_chapters:
        hs_chapter = {
            "id": f"ds_{chapter['id']}",  # 添加ds_前缀避免冲突
            "title": chapter['title'],
            "parent_id": "",
            "order": int(chapter['id']) if chapter['id'].isdigit() else 0,
            "description": chapter.get('description', ''),
            "knowledge_points": chapter.get('knowledge_points', []),
            "sub_chapters": []
        }
        hs_chapters.append(hs_chapter)
    
    # 保存章节
    chapters_output = subject_dir / "chapters" / "chapters.json"
    with open(chapters_output, 'w', encoding='utf-8') as f:
        json.dump(hs_chapters, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 已迁移 {len(hs_chapters)} 个章节")
    return hs_chapters


def migrate_questions():
    """迁移题目数据"""
    questions_dir = DS_DATA_DIR / "questions"
    if not questions_dir.exists():
        print("⚠️  未找到题目目录")
        return
    
    subject_dir = HS_DATA_DIR / DS_SUBJECT_ID
    questions_output_dir = subject_dir / "questions"
    
    total_questions = 0
    
    # 遍历所有章节的题目文件
    for chapter_file in sorted(questions_dir.glob("chapter_*.json")):
        with open(chapter_file, 'r', encoding='utf-8') as f:
            ds_questions = json.load(f)
        
        # 转换题目格式
        hs_questions = []
        for q in ds_questions:
            # 转换难度
            difficulty = q.get('difficulty', 3)
            if isinstance(difficulty, str):
                # 如果是字符串，转换为数字
                if difficulty == '简单' or difficulty == 'easy':
                    difficulty = 2
                elif difficulty == '困难' or difficulty == 'hard':
                    difficulty = 4
                else:
                    difficulty = 3
            elif not isinstance(difficulty, int):
                difficulty = 3
            
            # 转换题目类型
            q_type = q.get('type', 'choice')
            if q_type == 'concept':
                q_type = 'choice'
            elif q_type == 'calculation':
                q_type = 'calculation'
            else:
                q_type = 'choice'
            
            # 提取选项（如果有）
            options = None
            content = q.get('content', '')
            if 'A.' in content or 'A ' in content:
                # 尝试从内容中提取选项
                lines = content.split('\n')
                options_dict = {}
                for line in lines:
                    line = line.strip()
                    if line.startswith(('A.', 'A ', 'B.', 'B ', 'C.', 'C ', 'D.', 'D ')):
                        key = line[0]
                        value = line[2:].strip() if len(line) > 2 else line[1:].strip()
                        options_dict[key] = value
                if options_dict:
                    options = options_dict
            
            hs_question = {
                "id": f"ds_{q['id']}",  # 添加ds_前缀
                "title": q.get('title', ''),
                "content": content,
                "difficulty": difficulty,
                "type": q_type,
                "subject": DS_SUBJECT_ID,
                "grade": "",  # 数据结构不区分年级
                "tags": ["数据结构", "计算机科学"],  # 添加标签
                "source": "migrated",  # 标记为迁移的数据
                "upload_file_id": None,
                "options": options,
                "knowledge_points": [f"ds_{kp}" for kp in q.get('knowledge_points', [])],  # 添加前缀
                "related_questions": [],
                "reference_answer": {
                    "content": q.get('reference_answer', {}).get('content', ''),
                    "key_points": q.get('reference_answer', {}).get('key_points', []),
                    "explanation": q.get('reference_answer', {}).get('explanation', '')
                },
                "chapter": f"ds_{q.get('chapter', '01')}",  # 添加前缀
                "video_recommendations": []
            }
            hs_questions.append(hs_question)
            total_questions += 1
        
        # 保存到对应的章节文件
        chapter_id = chapter_file.stem.replace('chapter_', '')
        output_file = questions_output_dir / f"ds_{chapter_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(hs_questions, f, ensure_ascii=False, indent=4)
        
        print(f"✅ 已迁移章节 {chapter_id} 的 {len(hs_questions)} 个题目")
    
    print(f"✅ 总共迁移了 {total_questions} 个题目")
    return total_questions


def migrate_knowledge_points():
    """迁移知识点数据"""
    kp_dir = DS_DATA_DIR / "knowledgepoints"
    if not kp_dir.exists():
        print("⚠️  未找到知识点目录")
        return
    
    subject_dir = HS_DATA_DIR / DS_SUBJECT_ID
    kp_output_dir = subject_dir / "knowledgepoints"
    
    total_kps = 0
    
    # 遍历所有章节的知识点文件
    for kp_file in sorted(kp_dir.glob("chapter_*.json")):
        with open(kp_file, 'r', encoding='utf-8') as f:
            ds_kps = json.load(f)
        
        # 转换知识点格式
        hs_kps = []
        for kp in ds_kps:
            hs_kp = {
                "id": f"ds_{kp['id']}",  # 添加ds_前缀
                "title": kp.get('title', ''),
                "chapter_id": f"ds_{kp.get('chapter_id', '').replace('c', '')}",  # 转换章节ID
                "description": kp.get('description', ''),
                "related_points": [],
                "questions": [f"ds_{q}" for q in kp.get('questions', [])]  # 添加前缀
            }
            hs_kps.append(hs_kp)
            total_kps += len(hs_kps)
        
        # 保存到对应的章节文件
        chapter_id = kp_file.stem.replace('chapter_', '')
        output_file = kp_output_dir / f"ds_{chapter_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(hs_kps, f, ensure_ascii=False, indent=4)
        
        print(f"✅ 已迁移章节 {chapter_id} 的 {len(hs_kps)} 个知识点")
    
    print(f"✅ 总共迁移了 {total_kps} 个知识点")
    return total_kps


def update_high_school_loader():
    """更新高中数据加载器，添加数据结构科目"""
    loader_file = ROOT_DIR / "data" / "high_school_data_loader.py"
    
    if loader_file.exists():
        with open(loader_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已包含data_structure
        if 'data_structure' not in content:
            # 在subjects列表中添加
            content = content.replace(
                'self.subjects = ["math", "physics", "chemistry", "biology", "english", "chinese"]',
                'self.subjects = ["math", "physics", "chemistry", "biology", "english", "chinese", "data_structure"]'
            )
            
            with open(loader_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ 已更新数据加载器，添加数据结构科目")


def main():
    """主函数"""
    print("=" * 60)
    print("将原有数据结构数据迁移到高中教学系统")
    print("=" * 60)
    print()
    
    if not DS_DATA_DIR.exists():
        print("❌ 未找到原有数据结构数据目录")
        return
    
    # 迁移章节
    print("1. 迁移章节...")
    chapters = migrate_chapters()
    print()
    
    # 迁移题目
    print("2. 迁移题目...")
    questions_count = migrate_questions()
    print()
    
    # 迁移知识点
    print("3. 迁移知识点...")
    kps_count = migrate_knowledge_points()
    print()
    
    # 更新数据加载器
    print("4. 更新数据加载器...")
    update_high_school_loader()
    print()
    
    print("=" * 60)
    print("✅ 数据迁移完成！")
    print("=" * 60)
    print()
    print("📊 迁移统计：")
    print(f"   - 章节数: {len(chapters) if chapters else 0}")
    print(f"   - 题目数: {questions_count}")
    print(f"   - 知识点数: {kps_count}")
    print()
    print("📝 下一步：")
    print("   1. 重新运行数据加载器更新索引")
    print("   2. 在前端选择'数据结构'科目查看题目")
    print()


if __name__ == "__main__":
    main()
