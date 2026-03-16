"""
Paper Schemas

role: 论文的Pydantic schemas
depends: []
exports: [PaperResponse, PaperDetail]
status: PENDING

functions:
- PaperResponse: 论文响应schema
- PaperDetail: 论文详情schema（包含段落）
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class PaperResponse(BaseModel):
    """论文响应"""
    id: int
    batch_id: int
    filename: str
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    class_name: Optional[str] = None
    ai_score: Optional[float] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaperDetail(PaperResponse):
    """论文详情（包含段落列表）"""
    paragraphs: List["ParagraphResponse"] = []

    class Config:
        from_attributes = True


# 避免循环导入
from app.schemas.paragraph import ParagraphResponse
PaperDetail.model_rebuild()
