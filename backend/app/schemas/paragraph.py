"""
Paragraph Schemas

role: 段落的Pydantic schemas
depends: []
exports: [ParagraphResponse]
status: PENDING

functions:
- ParagraphResponse: 段落响应schema
"""

from typing import Optional, List
from pydantic import BaseModel


class ParagraphResponse(BaseModel):
    """段落响应"""
    id: int
    paper_id: int
    paragraph_index: int
    content: str
    ai_score: Optional[float] = None
    confidence: Optional[str] = None
    reasons: Optional[List[str]] = None

    class Config:
        from_attributes = True
