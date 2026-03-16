"""
Paper Model

role: 论文数据模型
depends: [database.py, models/batch.py]
exports: [Paper]
status: IMPLEMENTED

functions:
- Paper: 论文模型类
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class PaperStatus(str, enum.Enum):
    """论文处理状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Paper(Base):
    """论文模型"""
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("detection_batches.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    student_id = Column(String(50), nullable=True)  # 学号
    student_name = Column(String(100), nullable=True)  # 姓名
    class_name = Column(String(100), nullable=True)  # 班级
    ai_score = Column(Float, nullable=True, index=True)  # AI检测得分 0-100
    status = Column(Enum(PaperStatus), default=PaperStatus.PENDING, nullable=False)
    file_path = Column(String(500), nullable=False)  # 原始文件路径
    result_path = Column(String(500), nullable=True)  # 结果文件路径
    error_message = Column(String(1000), nullable=True)  # 错误信息
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    batch = relationship("DetectionBatch", back_populates="papers")
    paragraphs = relationship("Paragraph", back_populates="paper", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Paper(id={self.id}, filename={self.filename}, ai_score={self.ai_score})>"
