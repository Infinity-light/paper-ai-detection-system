"""
AI Detector Tests

role: AI检测器测试
depends: [services/ai_detector.py]
exports: []
status: IMPLEMENTED

functions:
- test_detect_paragraph(): 测试段落检测
- test_detect_paper(): 测试论文检测
- test_calculate_paper_score(): 测试总分计算
"""

import pytest
from app.services.ai_detector import AIDetectorService


class TestAIDetector:
    """AI检测器测试"""

    def setup_method(self):
        """测试前准备"""
        self.detector = AIDetectorService()

    def test_detect_paragraph(self):
        """测试段落检测"""
        # 测试AI生成文本（典型特征）
        ai_text = """
        首先，我们需要认识到人工智能的重要性。其次，人工智能在各个领域都有广泛的应用。
        再次，我们应该重视人工智能的发展。最后，总而言之，人工智能是未来的趋势。
        """
        result = self.detector.detect_paragraph(ai_text, use_distance_learning=False)

        assert "ai_score" in result
        assert "confidence" in result
        assert "reasons" in result
        assert isinstance(result["ai_score"], (int, float))
        assert result["ai_score"] >= 0
        assert result["ai_score"] <= 100
        assert result["confidence"] in ["low", "medium", "high"]

        # 测试人类撰写文本
        human_text = "我昨天去了公园，看到很多人在散步。天气很好，心情也不错。"
        result = self.detector.detect_paragraph(human_text, use_distance_learning=False)

        assert result["ai_score"] >= 0
        assert result["ai_score"] <= 100

    def test_detect_paper(self):
        """测试论文检测"""
        # 测试多个段落
        paragraphs = [
            "首先，我们需要认识到人工智能的重要性。",
            "其次，人工智能在各个领域都有广泛的应用。",
            "最后，总而言之，人工智能是未来的趋势。"
        ]

        result = self.detector.detect_paper(paragraphs, use_distance_learning=False)

        assert "paper_score" in result
        assert "paragraph_results" in result
        assert isinstance(result["paper_score"], (int, float))
        assert len(result["paragraph_results"]) == len(paragraphs)

        # 验证每个段落结果
        for i, para_result in enumerate(result["paragraph_results"]):
            assert para_result["index"] == i
            assert "content" in para_result
            assert "ai_score" in para_result
            assert "confidence" in para_result
            assert "reasons" in para_result

        # 测试空段落列表
        result = self.detector.detect_paper([], use_distance_learning=False)
        assert result["paper_score"] == 0.0
        assert len(result["paragraph_results"]) == 0

    def test_calculate_paper_score(self):
        """测试论文总分计算"""
        # 测试正常情况
        scores = [80.0, 90.0, 70.0]
        avg_score = self.detector.calculate_paper_score(scores)
        assert avg_score == 80.0

        # 测试单个分数
        scores = [75.0]
        avg_score = self.detector.calculate_paper_score(scores)
        assert avg_score == 75.0

        # 测试空列表
        scores = []
        avg_score = self.detector.calculate_paper_score(scores)
        assert avg_score == 0.0

        # 测试极端值
        scores = [0.0, 100.0]
        avg_score = self.detector.calculate_paper_score(scores)
        assert avg_score == 50.0
