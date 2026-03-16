"""
Student Info Extractor Tests

role: 学生信息提取器测试
depends: [services/student_info_extractor.py]
exports: []
status: IMPLEMENTED

functions:
- test_extract_from_filename(): 测试从文件名提取
- test_extract_from_content(): 测试从内容提取
- test_parse_student_id(): 测试学号解析
- test_extract_combined(): 测试综合提取
"""

import pytest
from app.services.student_info_extractor import StudentInfoExtractor


class TestStudentInfoExtractor:
    """学生信息提取器测试"""

    def setup_method(self):
        """测试前准备"""
        self.extractor = StudentInfoExtractor()

    def test_extract_from_filename(self):
        """测试从文件名提取学生信息"""
        # 测试标准格式：学号-姓名.docx
        result = self.extractor.extract_from_filename("22042201034-张三.docx")
        assert result["student_id"] == "22042201034"
        assert result["student_name"] == "张三"
        assert result["class_name"] == "2204"

        # 测试只有学号
        result = self.extractor.extract_from_filename("22042201034.docx")
        assert result["student_id"] == "22042201034"
        assert result["class_name"] == "2204"

        # 测试只有姓名
        result = self.extractor.extract_from_filename("张三.docx")
        assert result["student_name"] == "张三"
        assert result["student_id"] is None

        # 测试无信息
        result = self.extractor.extract_from_filename("document.docx")
        assert result["student_id"] is None
        assert result["student_name"] is None

    def test_extract_from_content(self):
        """测试从文档内容提取学生信息"""
        # 测试标准格式
        paragraphs = [
            "学号：22042201034",
            "姓名：张三",
            "论文标题：人工智能研究"
        ]
        result = self.extractor.extract_from_content(paragraphs)
        assert result["student_id"] == "22042201034"
        assert result["student_name"] == "张三"
        assert result["class_name"] == "2204"

        # 测试只有学号
        paragraphs = ["22042201034", "论文内容..."]
        result = self.extractor.extract_from_content(paragraphs)
        assert result["student_id"] == "22042201034"

        # 测试空内容
        result = self.extractor.extract_from_content([])
        assert result["student_id"] is None
        assert result["student_name"] is None

    def test_parse_student_id(self):
        """测试学号解析"""
        # 测试标准学号
        result = self.extractor.parse_student_id("22042201034")
        assert result["grade"] == "22"
        assert result["class_number"] == "04"
        assert result["class_name"] == "2204"

        # 测试无效学号
        result = self.extractor.parse_student_id("123")
        assert result["grade"] is None
        assert result["class_number"] is None
        assert result["class_name"] is None

        # 测试空学号
        result = self.extractor.parse_student_id("")
        assert result["grade"] is None

    def test_extract_combined(self):
        """测试综合提取（文件名+内容）"""
        # 测试文件名和内容都有信息
        filename = "22042201034-张三.docx"
        paragraphs = ["论文标题", "论文内容"]
        result = self.extractor.extract(filename, paragraphs)
        assert result["student_id"] == "22042201034"
        assert result["student_name"] == "张三"
        assert result["class_name"] == "2204"
        assert result["confidence"] == "high"

        # 测试只有文件名有信息
        filename = "22042201034.docx"
        paragraphs = ["论文内容"]
        result = self.extractor.extract(filename, paragraphs)
        assert result["student_id"] == "22042201034"
        assert result["confidence"] in ["medium", "low"]

        # 测试只有内容有信息
        filename = "document.docx"
        paragraphs = ["学号：22042201034", "姓名：张三"]
        result = self.extractor.extract(filename, paragraphs)
        assert result["student_id"] == "22042201034"
        assert result["student_name"] == "张三"

        # 测试都没有信息
        filename = "document.docx"
        paragraphs = ["论文内容"]
        result = self.extractor.extract(filename, paragraphs)
        assert result["confidence"] == "low"
