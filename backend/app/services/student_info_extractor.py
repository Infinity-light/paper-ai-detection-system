"""
Student Information Extractor Service

role: 从文件名和文档内容提取学生信息（学号、姓名、班级）
depends: []
exports: [StudentInfoExtractor]
status: IMPLEMENTED

functions:
- StudentInfoExtractor.extract_from_filename(filename): 从文件名提取信息
- StudentInfoExtractor.extract_from_content(paragraphs): 从文档前几行提取信息
- StudentInfoExtractor.parse_student_id(student_id): 解析学号获取年级和班级
- StudentInfoExtractor.extract(filename, paragraphs): 综合提取学生信息
"""

from typing import Dict, Optional, List
import re


class StudentInfoExtractor:
    """学生信息提取器"""

    def __init__(self):
        """初始化提取器"""
        # 学号格式：22042201034（22=年级，04=班级序号，22=专业代码，01034=学生序号）
        self.student_id_pattern = re.compile(r'\b\d{11}\b')
        # 中文姓名格式：2-4个中文字符
        self.name_pattern = re.compile(r'[\u4e00-\u9fa5]{2,4}')

    def extract_from_filename(self, filename: str) -> Dict[str, Optional[str]]:
        """
        从文件名提取学生信息

        Args:
            filename: 文件名

        Returns:
            {
                "student_id": 学号,
                "student_name": 姓名,
                "class_name": 班级
            }
        """
        result = {
            "student_id": None,
            "student_name": None,
            "class_name": None
        }

        # 去除文件扩展名
        name_without_ext = filename.rsplit('.', 1)[0]

        # 尝试匹配学号
        student_id_match = self.student_id_pattern.search(name_without_ext)
        if student_id_match:
            result["student_id"] = student_id_match.group()
            # 解析学号获取班级信息
            parsed = self.parse_student_id(result["student_id"])
            result["class_name"] = parsed.get("class_name")

        # 尝试匹配姓名（中文字符）
        name_matches = self.name_pattern.findall(name_without_ext)
        if name_matches:
            # 取第一个匹配的中文名
            result["student_name"] = name_matches[0]

        return result

    def extract_from_content(self, paragraphs: List[str]) -> Dict[str, Optional[str]]:
        """
        从文档前几行提取学生信息

        Args:
            paragraphs: 段落列表

        Returns:
            {
                "student_id": 学号,
                "student_name": 姓名,
                "class_name": 班级
            }
        """
        result = {
            "student_id": None,
            "student_name": None,
            "class_name": None
        }

        # 只检查前5个段落
        search_paragraphs = paragraphs[:5] if len(paragraphs) >= 5 else paragraphs

        for para in search_paragraphs:
            # 尝试匹配学号
            if not result["student_id"]:
                student_id_match = self.student_id_pattern.search(para)
                if student_id_match:
                    result["student_id"] = student_id_match.group()
                    # 解析学号获取班级信息
                    parsed = self.parse_student_id(result["student_id"])
                    result["class_name"] = parsed.get("class_name")

            # 尝试匹配姓名
            if not result["student_name"]:
                # 查找"姓名："或"学生："后面的中文名
                name_match = re.search(r'(?:姓名|学生)[：:]\s*([\u4e00-\u9fa5]{2,4})', para)
                if name_match:
                    result["student_name"] = name_match.group(1)
                else:
                    # 如果没有明确标识，尝试匹配独立的中文名
                    name_matches = self.name_pattern.findall(para)
                    if name_matches:
                        result["student_name"] = name_matches[0]

            # 如果都找到了，提前退出
            if result["student_id"] and result["student_name"]:
                break

        return result

    def parse_student_id(self, student_id: str) -> Dict[str, Optional[str]]:
        """
        解析学号获取年级和班级信息

        Args:
            student_id: 学号（如：22042201034）

        Returns:
            {
                "grade": 年级（如：22）,
                "class_number": 班级序号（如：04）,
                "class_name": 班级名称（如：2204）
            }
        """
        result = {
            "grade": None,
            "class_number": None,
            "class_name": None
        }

        if not student_id or len(student_id) != 11:
            return result

        try:
            # 提取年级（前2位）
            grade = student_id[:2]
            result["grade"] = grade

            # 提取班级序号（第3-4位）
            class_number = student_id[2:4]
            result["class_number"] = class_number

            # 组合班级名称
            result["class_name"] = f"{grade}{class_number}"

        except (IndexError, ValueError):
            pass

        return result

    def extract(self, filename: str, paragraphs: List[str]) -> Dict[str, Optional[str]]:
        """
        综合提取学生信息（优先从文件名，其次从内容）

        Args:
            filename: 文件名
            paragraphs: 段落列表

        Returns:
            {
                "student_id": 学号,
                "student_name": 姓名,
                "class_name": 班级,
                "confidence": 置信度（high/medium/low）
            }
        """
        # 从文件名提取
        filename_info = self.extract_from_filename(filename)

        # 从内容提取
        content_info = self.extract_from_content(paragraphs)

        # 合并结果（优先使用文件名中的信息）
        result = {
            "student_id": filename_info["student_id"] or content_info["student_id"],
            "student_name": filename_info["student_name"] or content_info["student_name"],
            "class_name": filename_info["class_name"] or content_info["class_name"],
            "confidence": "low"
        }

        # 评估置信度
        found_count = sum([
            1 if result["student_id"] else 0,
            1 if result["student_name"] else 0,
            1 if result["class_name"] else 0
        ])

        if found_count == 3:
            result["confidence"] = "high"
        elif found_count == 2:
            result["confidence"] = "medium"
        else:
            result["confidence"] = "low"

        return result
