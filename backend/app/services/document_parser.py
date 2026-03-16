"""
Document Parser Service

role: 解析DOC/DOCX文档，提取段落内容
depends: []
exports: [DocumentParser]
status: IMPLEMENTED

functions:
- DocumentParser.parse(file_path): 解析文档并返回段落列表
- DocumentParser.extract_paragraphs(doc): 从Document对象提取段落
- DocumentParser.clean_paragraph(text): 清理段落文本
"""

from typing import List
from pathlib import Path
from docx import Document


class DocumentParser:
    """文档解析器"""

    def __init__(self):
        """初始化解析器"""
        self.min_paragraph_length = 10  # 最小段落长度

    def parse(self, file_path: str) -> List[str]:
        """
        解析文档并提取段落

        Args:
            file_path: 文档文件路径

        Returns:
            段落文本列表

        Raises:
            ValueError: 文件格式不支持
            FileNotFoundError: 文件不存在
        """
        path = Path(file_path)

        # 检查文件是否存在
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 检查文件格式
        if path.suffix.lower() not in ['.doc', '.docx']:
            raise ValueError(f"不支持的文件格式: {path.suffix}，仅支持DOC/DOCX")

        try:
            # 解析文档
            doc = Document(file_path)
            paragraphs = self.extract_paragraphs(doc)
            return paragraphs
        except Exception as e:
            raise ValueError(f"文档解析失败: {str(e)}")

    def extract_paragraphs(self, doc: Document) -> List[str]:
        """
        从Document对象提取段落

        Args:
            doc: python-docx Document对象

        Returns:
            段落文本列表
        """
        paragraphs = []

        for para in doc.paragraphs:
            # 清理段落文本
            cleaned_text = self.clean_paragraph(para.text)

            # 过滤掉太短的段落
            if len(cleaned_text) >= self.min_paragraph_length:
                paragraphs.append(cleaned_text)

        return paragraphs

    def clean_paragraph(self, text: str) -> str:
        """
        清理段落文本

        Args:
            text: 原始段落文本

        Returns:
            清理后的文本
        """
        if not text:
            return ""

        # 去除首尾空白
        text = text.strip()

        # 替换多个空格为单个空格
        import re
        text = re.sub(r'\s+', ' ', text)

        # 去除特殊控制字符
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)

        return text
