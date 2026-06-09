#!/usr/bin/env python3
"""
创建高中教学系统数据结构
将现有的数据结构题目扩展为高中各科目题目
"""

import json
import os
from pathlib import Path
from typing import Dict, List

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
HS_DATA_DIR = DATA_DIR / "high_school_data"  # 高中数据目录

# 高中科目配置
SUBJECTS = {
    "math": {
        "name": "数学",
        "chapters": [
            {"id": "m01", "title": "函数与方程", "order": 1},
            {"id": "m02", "title": "三角函数", "order": 2},
            {"id": "m03", "title": "数列", "order": 3},
            {"id": "m04", "title": "立体几何", "order": 4},
            {"id": "m05", "title": "解析几何", "order": 5},
            {"id": "m06", "title": "概率统计", "order": 6},
            {"id": "m07", "title": "导数与微积分", "order": 7},
            {"id": "m08", "title": "复数", "order": 8},
        ]
    },
    "physics": {
        "name": "物理",
        "chapters": [
            {"id": "p01", "title": "力学基础", "order": 1},
            {"id": "p02", "title": "运动学", "order": 2},
            {"id": "p03", "title": "动力学", "order": 3},
            {"id": "p04", "title": "能量与动量", "order": 4},
            {"id": "p05", "title": "电学基础", "order": 5},
            {"id": "p06", "title": "磁场", "order": 6},
            {"id": "p07", "title": "电磁感应", "order": 7},
            {"id": "p08", "title": "光学", "order": 8},
        ]
    },
    "chemistry": {
        "name": "化学",
        "chapters": [
            {"id": "c01", "title": "化学基础", "order": 1},
            {"id": "c02", "title": "元素周期表", "order": 2},
            {"id": "c03", "title": "化学键", "order": 3},
            {"id": "c04", "title": "化学反应", "order": 4},
            {"id": "c05", "title": "有机化学", "order": 5},
            {"id": "c06", "title": "化学平衡", "order": 6},
            {"id": "c07", "title": "电化学", "order": 7},
            {"id": "c08", "title": "实验化学", "order": 8},
        ]
    },
    "biology": {
        "name": "生物",
        "chapters": [
            {"id": "b01", "title": "细胞生物学", "order": 1},
            {"id": "b02", "title": "遗传学", "order": 2},
            {"id": "b03", "title": "进化论", "order": 3},
            {"id": "b04", "title": "生态学", "order": 4},
            {"id": "b05", "title": "植物学", "order": 5},
            {"id": "b06", "title": "动物学", "order": 6},
            {"id": "b07", "title": "人体生理", "order": 7},
            {"id": "b08", "title": "生物技术", "order": 8},
        ]
    },
    "english": {
        "name": "英语",
        "chapters": [
            {"id": "e01", "title": "语法基础", "order": 1},
            {"id": "e02", "title": "时态语态", "order": 2},
            {"id": "e03", "title": "从句", "order": 3},
            {"id": "e04", "title": "词汇", "order": 4},
            {"id": "e05", "title": "阅读理解", "order": 5},
            {"id": "e06", "title": "完形填空", "order": 6},
            {"id": "e07", "title": "写作", "order": 7},
            {"id": "e08", "title": "听力", "order": 8},
        ]
    },
    "chinese": {
        "name": "语文",
        "chapters": [
            {"id": "h01", "title": "古代文学", "order": 1},
            {"id": "h02", "title": "现代文学", "order": 2},
            {"id": "h03", "title": "文言文", "order": 3},
            {"id": "h04", "title": "古诗词", "order": 4},
            {"id": "h05", "title": "现代文阅读", "order": 5},
            {"id": "h06", "title": "作文", "order": 6},
            {"id": "h07", "title": "语言文字运用", "order": 7},
            {"id": "h08", "title": "文学常识", "order": 8},
        ]
    }
}


def create_directory_structure():
    """创建目录结构"""
    for subject_id in SUBJECTS.keys():
        subject_dir = HS_DATA_DIR / subject_id
        (subject_dir / "chapters").mkdir(parents=True, exist_ok=True)
        (subject_dir / "questions").mkdir(parents=True, exist_ok=True)
        (subject_dir / "knowledgepoints").mkdir(parents=True, exist_ok=True)
    print("✅ 目录结构创建完成")


def create_chapters_file(subject_id: str, subject_info: Dict):
    """创建章节文件"""
    chapters = []
    for chapter in subject_info["chapters"]:
        chapters.append({
            "id": chapter["id"],
            "title": chapter["title"],
            "parent_id": "",
            "order": chapter["order"],
            "description": f"{subject_info['name']} - {chapter['title']}章节内容",
            "knowledge_points": [],  # 将在创建知识点时填充
            "sub_chapters": []
        })
    
    chapters_file = HS_DATA_DIR / subject_id / "chapters" / "chapters.json"
    with open(chapters_file, 'w', encoding='utf-8') as f:
        json.dump(chapters, f, ensure_ascii=False, indent=4)
    print(f"✅ 创建 {subject_info['name']} 章节文件")


def create_empty_questions_file(subject_id: str, chapter_id: str):
    """创建空的题目文件（模板）"""
    questions_file = HS_DATA_DIR / subject_id / "questions" / f"{chapter_id}.json"
    with open(questions_file, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=4)


def create_empty_knowledgepoints_file(subject_id: str, chapter_id: str):
    """创建空的知识点文件（模板）"""
    knowledgepoints_file = HS_DATA_DIR / subject_id / "knowledgepoints" / f"{chapter_id}.json"
    with open(knowledgepoints_file, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=4)


def create_question_template():
    """创建题目模板文件"""
    template = {
        "id": "q_m01_001",  # 格式：q_{章节ID}_{序号}
        "title": "题目标题",
        "content": "题目内容（可以包含选项）",
        "difficulty": 3,  # 1-5，1最简单，5最难
        "type": "choice",  # choice(选择题), fill(填空题), essay(解答题), calculation(计算题)
        "subject": "math",  # math, physics, chemistry, biology, english, chinese
        "grade": "grade2",  # grade1(高一), grade2(高二), grade3(高三), ""(通用)
        "tags": ["函数", "方程"],  # 标签列表
        "source": "manual",  # manual(手动), upload(上传), generate(生成)
        "upload_file_id": None,
        "options": {  # 如果是选择题
            "A": "选项A",
            "B": "选项B",
            "C": "选项C",
            "D": "选项D"
        },
        "knowledge_points": ["kc_m01_001"],  # 知识点ID列表
        "related_questions": [],
        "reference_answer": {
            "content": "答案",
            "key_points": ["关键点1", "关键点2"],
            "explanation": "详细解析"
        },
        "chapter": "m01",
        "video_recommendations": []
    }
    
    template_file = HS_DATA_DIR / "question_template.json"
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=4)
    print("✅ 创建题目模板文件: question_template.json")


def create_knowledgepoint_template():
    """创建知识点模板文件"""
    template = {
        "id": "kc_m01_001",  # 格式：kc_{章节ID}_{序号}
        "title": "知识点标题",
        "chapter_id": "m01",
        "description": "知识点的详细描述",
        "related_points": [],
        "questions": ["q_m01_001"]  # 相关题目ID列表
    }
    
    template_file = HS_DATA_DIR / "knowledgepoint_template.json"
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=4)
    print("✅ 创建知识点模板文件: knowledgepoint_template.json")


def migrate_existing_data():
    """迁移现有数据结构数据（作为示例）"""
    ds_data_dir = DATA_DIR / "ds_data"
    if not ds_data_dir.exists():
        print("⚠️  未找到原有数据结构数据，跳过迁移")
        return
    
    # 创建数据结构示例目录
    example_dir = HS_DATA_DIR / "examples" / "data_structure"
    example_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制原有数据作为示例
    import shutil
    if (ds_data_dir / "chapters.json").exists():
        shutil.copy(ds_data_dir / "chapters.json", example_dir / "chapters.json")
    if (ds_data_dir / "questions").exists():
        shutil.copytree(ds_data_dir / "questions", example_dir / "questions", dirs_exist_ok=True)
    if (ds_data_dir / "knowledgepoints").exists():
        shutil.copytree(ds_data_dir / "knowledgepoints", example_dir / "knowledgepoints", dirs_exist_ok=True)
    
    print("✅ 已迁移原有数据结构数据到 examples/data_structure 作为参考")


def main():
    """主函数"""
    print("=" * 60)
    print("创建高中教学系统数据结构")
    print("=" * 60)
    print()
    
    # 创建目录结构
    create_directory_structure()
    print()
    
    # 为每个科目创建章节
    print("创建章节文件...")
    for subject_id, subject_info in SUBJECTS.items():
        create_chapters_file(subject_id, subject_info)
        
        # 为每个章节创建空的题目和知识点文件
        for chapter in subject_info["chapters"]:
            create_empty_questions_file(subject_id, chapter["id"])
            create_empty_knowledgepoints_file(subject_id, chapter["id"])
    print()
    
    # 创建模板文件
    print("创建模板文件...")
    create_question_template()
    create_knowledgepoint_template()
    print()
    
    # 迁移原有数据
    print("迁移原有数据...")
    migrate_existing_data()
    print()
    
    print("=" * 60)
    print("✅ 数据结构创建完成！")
    print("=" * 60)
    print()
    print("📁 数据目录结构：")
    print(f"   {HS_DATA_DIR}")
    print()
    print("📝 下一步：")
    print("   1. 查看模板文件了解数据格式")
    print("   2. 使用文件上传功能上传PDF/图片自动提取题目")
    print("   3. 使用题目生成功能基于现有题目生成新题目")
    print("   4. 手动编辑JSON文件添加题目和知识点")
    print()


if __name__ == "__main__":
    main()
