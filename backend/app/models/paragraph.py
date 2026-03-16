"""
Paragraph Model

role: 段落数据模型
depends: [database.py, models/paper.py]
exports: [Paragraph]
status: PENDING

functions:
- Paragraph: 段落模型类
"""

from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Paragraph(Base):
    """段落模型"""
    __tablename__ = "paragraphs"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, index=True)
    paragraph_index = Column(Integer, nullable=False)  # 段落序号（从0开始）
    content = Column(Text, nullable=False)  # 段落内容
    ai_score = Column(Float, nullable=True)  # AI检测得分 0-100
    confidence = Column(String(20), nullable=True)  # 置信度: low/medium/high
    reasons = Column(JSON, nullable=True)  # 检测原因列表

    # 关系
    paper = relationship("Paper", back_populates="paragraphs")

    def __repr__(self):
        return f"<Paragraph(id={self.id}, paper_id={self.paper_id}, index={self.paragraph_index}, score={self.ai_score})>"
