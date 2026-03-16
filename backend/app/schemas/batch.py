"""
Batch Schemas

role: 检测批次的Pydantic schemas
depends: []
exports: [BatchCreate, BatchResponse, BatchDetail]
status: PENDING

functions:
- BatchCreate: 创建批次请求schema
- BatchResponse: 批次响应schema
- BatchDetail: 批次详情schema
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class BatchCreate(BaseModel):
    """创建批次请求"""
    user_id: Optional[str] = None


class BatchResponse(BaseModel):
    """批次响应"""
    id: int
    created_at: datetime
    status: str
    total_papers: int
    processed_papers: int
    user_id: Optional[str] = None

    class Config:
        from_attributes = True


class BatchDetail(BatchResponse):
    """批次详情（包含论文列表）"""
    papers: List["PaperResponse"] = []

    class Config:
        from_attributes = True


# 避免循环导入
from app.schemas.paper import PaperResponse
BatchDetail.model_rebuild()
