"""
Upload API Routes

role: 文件上传API路由
depends: [database.py, models/batch.py, models/paper.py, services/file_storage.py, tasks/detection_tasks.py]
exports: [router]
status: IMPLEMENTED

functions:
- upload_papers(files, batch_id, db): 上传论文文件
- create_batch_and_upload(files, db): 创建批次并上传文件
"""

from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.batch import BatchResponse
from app.schemas.paper import PaperResponse
from app.models.batch import DetectionBatch, BatchStatus
from app.models.paper import Paper, PaperStatus
from app.services.file_storage import FileStorage
from app.tasks.detection_tasks import process_batch

router = APIRouter()


@router.post("/batches/{batch_id}/upload", response_model=List[PaperResponse])
async def upload_papers(
    batch_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    上传论文文件到指定批次

    Args:
        batch_id: 批次ID
        files: 上传的文件列表
        db: 数据库会话

    Returns:
        创建的论文记录列表
    """
    # 检查批次是否存在
    batch = db.query(DetectionBatch).filter(DetectionBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"批次不存在: {batch_id}")

    # 检查文件格式
    allowed_extensions = ['.doc', '.docx']
    for file in files:
        ext = file.filename.lower().split('.')[-1]
        if f'.{ext}' not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file.filename}，仅支持DOC/DOCX"
            )

    # 保存文件并创建论文记录
    storage = FileStorage()
    papers = []

    for file in files:
        try:
            # 保存文件
            file_path = storage.save_upload(file.file, batch_id, file.filename)

            # 创建论文记录
            paper = Paper(
                batch_id=batch_id,
                filename=file.filename,
                file_path=file_path,
                status=PaperStatus.PENDING
            )
            db.add(paper)
            papers.append(paper)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    # 更新批次的论文总数
    batch.total_papers += len(papers)
    db.commit()

    # 刷新论文对象以获取ID
    for paper in papers:
        db.refresh(paper)

    return papers


@router.post("/upload", response_model=BatchResponse)
async def create_batch_and_upload(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    创建新批次并上传论文文件

    Args:
        files: 上传的文件列表
        db: 数据库会话

    Returns:
        创建的批次信息
    """
    if not files:
        raise HTTPException(status_code=400, detail="未上传任何文件")

    # 检查文件格式
    allowed_extensions = ['.doc', '.docx']
    for file in files:
        ext = file.filename.lower().split('.')[-1]
        if f'.{ext}' not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file.filename}，仅支持DOC/DOCX"
            )

    # 创建批次
    batch = DetectionBatch(
        status=BatchStatus.PENDING,
        total_papers=len(files),
        processed_papers=0
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    # 保存文件并创建论文记录
    storage = FileStorage()

    for file in files:
        try:
            # 保存文件
            file_path = storage.save_upload(file.file, batch.id, file.filename)

            # 创建论文记录
            paper = Paper(
                batch_id=batch.id,
                filename=file.filename,
                file_path=file_path,
                status=PaperStatus.PENDING
            )
            db.add(paper)

        except Exception as e:
            # 如果保存失败，删除批次
            db.delete(batch)
            db.commit()
            raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    db.commit()

    # 触发异步处理任务
    try:
        process_batch.delay(batch.id)
    except Exception as e:
        # 任务提交失败，但批次已创建
        batch.status = BatchStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=f"任务提交失败: {str(e)}")

    db.refresh(batch)
    return batch
