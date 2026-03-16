"""
Detection Batch Model

role: 检测批次数据模型
depends: [database.py]
exports: [DetectionBatch]
status: PENDING

functions:
- DetectionBatch: 检测批次模型类
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class BatchStatus(str, enum.Enum):
    """批次状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DetectionBatch(Base):
    """检测批次模型"""
    __tablename__ = "detection_batches"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Enum(BatchStatus), default=BatchStatus.PENDING, nullable=False)
    total_papers = Column(Integer, default=0, nullable=False)
    processed_papers = Column(Integer, default=0, nullable=False)
    user_id = Column(String(100), nullable=True)  # 可选的用户标识

    # 关系
    papers = relationship("Paper", back_populates="batch", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DetectionBatch(id={self.id}, status={self.status}, total={self.total_papers})>"
