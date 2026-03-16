"""
Batch API Routes

role: 批次管理API路由
depends: [database.py, models/batch.py, schemas/batch.py]
exports: [router]
status: IMPLEMENTED

functions:
- create_batch(batch_data, db): 创建新批次
- get_batch(batch_id, db): 获取批次详情
- list_batches(skip, limit, db): 获取批次列表
- delete_batch(batch_id, db): 删除批次
- get_batch_papers(batch_id, sort_by, db): 获取批次中的论文列表
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.batch import BatchCreate, BatchResponse, BatchDetail
from app.schemas.paper import PaperResponse
from app.models.batch import DetectionBatch, BatchStatus
from app.models.paper import Paper
from app.services.file_storage import FileStorage

router = APIRouter()


@router.post("/batches", response_model=BatchResponse)
async def create_batch(
    batch_data: BatchCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的检测批次

    Args:
        batch_data: 批次创建数据
        db: 数据库会话

    Returns:
        创建的批次信息
    """
    batch = DetectionBatch(
        status=BatchStatus.PENDING,
        total_papers=0,
        processed_papers=0,
        user_id=batch_data.user_id
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@router.get("/batches/{batch_id}", response_model=BatchDetail)
async def get_batch(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    获取批次详情

    Args:
        batch_id: 批次ID
        db: 数据库会话

    Returns:
        批次详情（包含论文列表）
    """
    batch = db.query(DetectionBatch).filter(DetectionBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"批次不存在: {batch_id}")
    return batch


@router.get("/batches", response_model=List[BatchResponse])
async def list_batches(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取批次列表

    Args:
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话

    Returns:
        批次列表
    """
    batches = db.query(DetectionBatch).order_by(
        DetectionBatch.created_at.desc()
    ).offset(skip).limit(limit).all()
    return batches


@router.delete("/batches/{batch_id}")
async def delete_batch(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    删除批次

    Args:
        batch_id: 批次ID
        db: 数据库会话

    Returns:
        删除结果
    """
    batch = db.query(DetectionBatch).filter(DetectionBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"批次不存在: {batch_id}")

    # 删除相关文件
    try:
        storage = FileStorage()
        storage.delete_batch_files(batch_id)
    except Exception as e:
        # 文件删除失败不影响数据库删除
        pass

    # 删除批次（级联删除论文和段落）
    db.delete(batch)
    db.commit()

    return {"message": f"批次 {batch_id} 已删除"}


@router.get("/batches/{batch_id}/papers", response_model=List[PaperResponse])
async def get_batch_papers(
    batch_id: int,
    sort_by: str = Query("ai_score", description="排序字段: ai_score, created_at"),
    order: str = Query("desc", description="排序方向: asc, desc"),
    db: Session = Depends(get_db)
):
    """
    获取批次中的论文列表（支持按AI率排序）

    Args:
        batch_id: 批次ID
        sort_by: 排序字段
        order: 排序方向
        db: 数据库会话

    Returns:
        论文列表
    """
    # 检查批次是否存在
    batch = db.query(DetectionBatch).filter(DetectionBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"批次不存在: {batch_id}")

    # 构建查询
    query = db.query(Paper).filter(Paper.batch_id == batch_id)

    # 排序
    if sort_by == "ai_score":
        if order == "desc":
            query = query.order_by(Paper.ai_score.desc().nullslast())
        else:
            query = query.order_by(Paper.ai_score.asc().nullsfirst())
    elif sort_by == "created_at":
        if order == "desc":
            query = query.order_by(Paper.created_at.desc())
        else:
            query = query.order_by(Paper.created_at.asc())
    else:
        raise HTTPException(status_code=400, detail=f"不支持的排序字段: {sort_by}")

    papers = query.all()
    return papers
