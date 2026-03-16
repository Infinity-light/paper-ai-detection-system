"""
Paper API Routes

role: 论文管理API路由
depends: [database.py, models/paper.py, schemas/paper.py]
exports: [router]
status: IMPLEMENTED

functions:
- get_paper(paper_id, db): 获取论文详情
- list_papers(batch_id, skip, limit, db): 获取论文列表
- download_result(paper_id, db): 下载检测结果
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import get_db
from app.schemas.paper import PaperResponse, PaperDetail
from app.models.paper import Paper

router = APIRouter()


@router.get("/papers/{paper_id}", response_model=PaperDetail)
async def get_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):
    """
    获取论文详情

    Args:
        paper_id: 论文ID
        db: 数据库会话

    Returns:
        论文详情（包含段落列表）
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail=f"论文不存在: {paper_id}")
    return paper


@router.get("/papers", response_model=List[PaperResponse])
async def list_papers(
    batch_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取论文列表

    Args:
        batch_id: 批次ID（可选，用于过滤）
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话

    Returns:
        论文列表
    """
    query = db.query(Paper)

    # 如果指定了批次ID，进行过滤
    if batch_id is not None:
        query = query.filter(Paper.batch_id == batch_id)

    # 按创建时间倒序排列
    papers = query.order_by(Paper.created_at.desc()).offset(skip).limit(limit).all()
    return papers


@router.get("/papers/{paper_id}/result")
async def download_result(
    paper_id: int,
    db: Session = Depends(get_db)
):
    """
    下载论文检测结果

    Args:
        paper_id: 论文ID
        db: 数据库会话

    Returns:
        检测结果文件
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail=f"论文不存在: {paper_id}")

    # 检查结果文件是否存在
    if not paper.result_path:
        raise HTTPException(status_code=404, detail="检测结果尚未生成")

    result_path = Path(paper.result_path)
    if not result_path.exists():
        raise HTTPException(status_code=404, detail="结果文件不存在")

    # 返回文件
    return FileResponse(
        path=str(result_path),
        filename=f"{paper.filename}_result.txt",
        media_type="text/plain"
    )
