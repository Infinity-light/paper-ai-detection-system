"""
AI Detector Service

role: AI检测服务，整合规则引擎和Distance Learning
depends: [core/ai_detector.py]
exports: [AIDetectorService]
status: IMPLEMENTED

functions:
- AIDetectorService.detect_paragraph(text): 检测单个段落
- AIDetectorService.detect_paper(paragraphs): 检测整篇论文
- AIDetectorService.calculate_paper_score(paragraph_scores): 计算论文总分
"""

from typing import Dict, List
from app.core.ai_detector import AIDetector


class AIDetectorService:
    """AI检测服务"""

    def __init__(self, api_key: str = None):
        """
        初始化检测服务

        Args:
            api_key: Deepseek API密钥
        """
        self.detector = AIDetector(api_key=api_key)

    def detect_paragraph(self, text: str, use_distance_learning: bool = True) -> Dict:
        """
        检测单个段落

        Args:
            text: 段落文本
            use_distance_learning: 是否使用Distance Learning

        Returns:
            {
                "ai_score": AI概率分数,
                "confidence": 置信度,
                "reasons": 检测原因列表
            }
        """
        # 调用核心检测器
        result = self.detector.detect(text, use_distance_learning=use_distance_learning)

        # 转换为服务层格式
        return {
            "ai_score": result["final_score"],
            "confidence": result["confidence"],
            "reasons": result["reasons"]
        }

    def detect_paper(self, paragraphs: List[str], use_distance_learning: bool = True) -> Dict:
        """
        检测整篇论文

        Args:
            paragraphs: 段落列表
            use_distance_learning: 是否使用Distance Learning

        Returns:
            {
                "paper_score": 论文总分,
                "paragraph_results": 段落检测结果列表
            }
        """
        paragraph_results = []

        # 检测每个段落
        for index, paragraph in enumerate(paragraphs):
            try:
                result = self.detect_paragraph(paragraph, use_distance_learning)
                paragraph_results.append({
                    "index": index,
                    "content": paragraph,
                    "ai_score": result["ai_score"],
                    "confidence": result["confidence"],
                    "reasons": result["reasons"]
                })
            except Exception as e:
                # 如果某个段落检测失败，记录错误但继续
                paragraph_results.append({
                    "index": index,
                    "content": paragraph,
                    "ai_score": 0,
                    "confidence": "low",
                    "reasons": [f"检测失败: {str(e)}"]
                })

        # 计算论文总分
        paragraph_scores = [p["ai_score"] for p in paragraph_results]
        paper_score = self.calculate_paper_score(paragraph_scores)

        return {
            "paper_score": paper_score,
            "paragraph_results": paragraph_results
        }

    def calculate_paper_score(self, paragraph_scores: List[float]) -> float:
        """
        计算论文总分（加权平均）

        Args:
            paragraph_scores: 段落分数列表

        Returns:
            论文总分
        """
        if not paragraph_scores:
            return 0.0

        # 使用简单平均
        total_score = sum(paragraph_scores)
        avg_score = total_score / len(paragraph_scores)

        return round(avg_score, 2)
