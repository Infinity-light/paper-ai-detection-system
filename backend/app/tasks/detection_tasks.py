"""
Detection Tasks

role: Celery异步检测任务
depends: [config.py, database.py, models/batch.py, models/paper.py, models/paragraph.py, services/document_parser.py, services/student_info_extractor.py, services/ai_detector.py]
exports: [celery_app, process_batch, process_paper]
status: IMPLEMENTED

functions:
- celery_app: Celery应用实例
- process_batch(batch_id): 处理整个批次
- process_paper(paper_id): 处理单篇论文
"""

from celery import Celery
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import SessionLocal
from app.models.batch import DetectionBatch, BatchStatus
from app.models.paper import Paper, PaperStatus
from app.models.paragraph import Paragraph
from app.services.document_parser import DocumentParser
from app.services.student_info_extractor import StudentInfoExtractor
from app.services.ai_detector import AIDetectorService

settings = get_settings()

# 创建Celery应用
celery_app = Celery(
    "paper_detection",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(bind=True)
def process_batch(self, batch_id: int):
    """
    处理整个批次的论文检测

    Args:
        batch_id: 批次ID

    Returns:
        处理结果
    """
    db = SessionLocal()
    try:
        # 获取批次
        batch = db.query(DetectionBatch).filter(DetectionBatch.id == batch_id).first()
        if not batch:
            return {"error": f"批次不存在: {batch_id}"}

        # 更新批次状态为处理中
        batch.status = BatchStatus.PROCESSING
        db.commit()

        # 获取批次中的所有论文
        papers = db.query(Paper).filter(Paper.batch_id == batch_id).all()

        # 处理每篇论文
        for paper in papers:
            try:
                process_paper.delay(paper.id)
            except Exception as e:
                paper.status = PaperStatus.FAILED
                paper.error_message = f"任务提交失败: {str(e)}"
                db.commit()

        return {"batch_id": batch_id, "total_papers": len(papers)}

    except Exception as e:
        # 更新批次状态为失败
        batch = db.query(DetectionBatch).filter(DetectionBatch.id == batch_id).first()
        if batch:
            batch.status = BatchStatus.FAILED
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
def process_paper(self, paper_id: int):
    """
    处理单篇论文的检测

    Args:
        paper_id: 论文ID

    Returns:
        处理结果
    """
    db = SessionLocal()
    try:
        # 获取论文
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            return {"error": f"论文不存在: {paper_id}"}

        # 更新论文状态为处理中
        paper.status = PaperStatus.PROCESSING
        db.commit()

        # 1. 解析文档
        parser = DocumentParser()
        paragraphs = parser.parse(paper.file_path)

        if not paragraphs:
            paper.status = PaperStatus.FAILED
            paper.error_message = "文档解析失败：未提取到段落"
            db.commit()
            return {"error": "未提取到段落"}

        # 2. 提取学生信息
        extractor = StudentInfoExtractor()
        student_info = extractor.extract(paper.filename, paragraphs)

        paper.student_id = student_info.get("student_id")
        paper.student_name = student_info.get("student_name")
        paper.class_name = student_info.get("class_name")
        db.commit()

        # 3. AI检测
        detector = AIDetectorService(api_key=settings.deepseek_api_key)
        detection_result = detector.detect_paper(paragraphs, use_distance_learning=True)

        # 4. 保存检测结果
        paper.ai_score = detection_result["paper_score"]

        # 保存段落检测结果
        for para_result in detection_result["paragraph_results"]:
            paragraph = Paragraph(
                paper_id=paper.id,
                paragraph_index=para_result["index"],
                content=para_result["content"],
                ai_score=para_result["ai_score"],
                confidence=para_result["confidence"],
                reasons=para_result["reasons"]
            )
            db.add(paragraph)

        # 更新论文状态为完成
        paper.status = PaperStatus.COMPLETED
        db.commit()

        # 5. 更新批次进度
        batch = db.query(DetectionBatch).filter(DetectionBatch.id == paper.batch_id).first()
        if batch:
            completed_count = db.query(Paper).filter(
                Paper.batch_id == batch.id,
                Paper.status == PaperStatus.COMPLETED
            ).count()
            batch.processed_papers = completed_count

            # 检查是否所有论文都已处理完成
            if completed_count == batch.total_papers:
                batch.status = BatchStatus.COMPLETED

            db.commit()

        return {
            "paper_id": paper.id,
            "ai_score": paper.ai_score,
            "student_info": student_info
        }

    except Exception as e:
        # 更新论文状态为失败
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if paper:
            paper.status = PaperStatus.FAILED
            paper.error_message = str(e)
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()
