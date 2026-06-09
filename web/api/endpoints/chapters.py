from fastapi import APIRouter, HTTPException
from typing import Optional
from web.services.qa_service import QAService

router = APIRouter()
qa_service = QAService()

@router.get("/chapters", tags=["chapters"])
async def get_chapters(subject: Optional[str] = None):
    """
    获取所有章节
    
    Args:
        subject: 科目筛选（可选）：math, physics, chemistry, biology, english, chinese
    """
    try:
        qa_system = qa_service.get_qa_system()
        chapters = qa_system.get_chapters(subject=subject)
        return chapters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subjects", tags=["chapters"])
async def get_subjects():
    """获取所有科目列表"""
    try:
        qa_system = qa_service.get_qa_system()
        if hasattr(qa_system, 'get_all_subjects'):
            subjects = qa_system.get_all_subjects()
        else:
            # 默认科目列表
            subjects = ["math", "physics", "chemistry", "biology", "english", "chinese"]
        
        subject_names = {
            "math": "数学",
            "physics": "物理",
            "chemistry": "化学",
            "biology": "生物",
            "english": "英语",
            "chinese": "语文",
            "data_structure": "数据结构"
        }
        
        result = []
        for sub_id in subjects:
            result.append({
                "id": sub_id,
                "name": subject_names.get(sub_id, sub_id)
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 