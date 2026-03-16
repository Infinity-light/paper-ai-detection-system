"""
Distance Learning检测：基于改写距离的AI文本检测

核心原理：
- AI生成的文本在改写后语义距离更小（更稳定）
- 人类文本在改写后语义距离更大（更多样化）

参考论文：
Distance Learning for Detecting LLM-Generated Text
https://arxiv.org/html/2601.21895v2
"""

import os
from typing import Dict, Optional
import requests
import json


class DistanceLearningDetector:
    """基于Distance Learning的AI文本检测器"""

    def __init__(self, api_key: Optional[str] = None, api_base: str = "https://api.deepseek.com"):
        """
        初始化检测器

        Args:
            api_key: Deepseek API密钥（如果不提供，从环境变量读取）
            api_base: API基础URL
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供DEEPSEEK_API_KEY环境变量或api_key参数")

        self.api_base = api_base
        self.model = "deepseek-chat"

    def detect(self, text: str, temperature: float = 0.7) -> Dict:
        """
        检测文本的AI概率

        Args:
            text: 待检测文本（段落）
            temperature: 改写时的温度参数

        Returns:
            {
                "ai_probability": 0-100的AI概率,
                "distance": 语义距离值,
                "rewritten_text": 改写后的文本,
                "confidence": 置信度 (low/medium/high)
            }
        """
        if not text or len(text.strip()) < 20:
            return {
                "ai_probability": 0,
                "distance": 0,
                "rewritten_text": "",
                "confidence": "low",
                "error": "文本过短"
            }

        try:
            # 步骤1：使用LLM改写文本
            rewritten_text = self._rewrite_text(text, temperature)

            # 步骤2：计算语义距离
            distance = self._calculate_semantic_distance(text, rewritten_text)

            # 步骤3：根据距离计算AI概率
            ai_probability = self._distance_to_probability(distance)

            # 步骤4：计算置信度
            confidence = self._calculate_confidence(distance, len(text))

            return {
                "ai_probability": ai_probability,
                "distance": distance,
                "rewritten_text": rewritten_text,
                "confidence": confidence
            }

        except Exception as e:
            return {
                "ai_probability": 0,
                "distance": 0,
                "rewritten_text": "",
                "confidence": "low",
                "error": str(e)
            }

    def _rewrite_text(self, text: str, temperature: float) -> str:
        """
        使用LLM改写文本

        Args:
            text: 原始文本
            temperature: 温度参数（控制随机性）

        Returns:
            改写后的文本
        """
        prompt = f"""请对以下文本进行轻微改写，保持原意不变，但使用不同的表达方式。
只输出改写后的文本，不要添加任何解释或说明。

原文：
{text}

改写："""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": len(text) * 2  # 预留足够空间
        }

        response = requests.post(
            f"{self.api_base}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")

        result = response.json()
        rewritten = result["choices"][0]["message"]["content"].strip()

        return rewritten

    def _calculate_semantic_distance(self, text1: str, text2: str) -> float:
        """
        计算两段文本的语义距离

        简化版实现：使用字符级编辑距离 / 文本长度
        生产环境建议使用embedding向量的余弦距离

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            距离值（0-1之间，越小越相似）
        """
        # 简化版：使用Levenshtein距离
        distance = self._levenshtein_distance(text1, text2)
        max_len = max(len(text1), len(text2))

        # 归一化到0-1
        normalized_distance = distance / max_len if max_len > 0 else 0

        return normalized_distance

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        计算Levenshtein编辑距离

        Args:
            s1: 字符串1
            s2: 字符串2

        Returns:
            编辑距离
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # 插入、删除、替换的代价
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _distance_to_probability(self, distance: float) -> int:
        """
        将语义距离转换为AI概率

        核心逻辑：
        - 距离越小（改写后变化小）→ AI概率越高
        - 距离越大（改写后变化大）→ AI概率越低

        Args:
            distance: 语义距离（0-1）

        Returns:
            AI概率（0-100）
        """
        # 反向映射：距离小 → 概率高
        # 使用sigmoid函数平滑映射
        # 这里的阈值需要根据实际数据调优

        if distance < 0.3:
            # 距离很小，高度疑似AI
            return int(100 - distance * 200)
        elif distance < 0.5:
            # 距离中等，中度疑似
            return int(70 - (distance - 0.3) * 200)
        else:
            # 距离大，低度疑似
            return int(max(0, 30 - (distance - 0.5) * 60))

    def _calculate_confidence(self, distance: float, text_length: int) -> str:
        """
        计算置信度

        Args:
            distance: 语义距离
            text_length: 文本长度

        Returns:
            置信度 (low/medium/high)
        """
        # 文本太短，置信度低
        if text_length < 50:
            return "low"

        # 距离在极端值，置信度高
        if distance < 0.2 or distance > 0.7:
            return "high"
        elif distance < 0.35 or distance > 0.55:
            return "medium"
        else:
            return "low"


# 测试代码
if __name__ == "__main__":
    # 注意：需要设置DEEPSEEK_API_KEY环境变量
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        print("警告：未设置DEEPSEEK_API_KEY环境变量")
        print("请设置后再运行测试")
        print("示例：export DEEPSEEK_API_KEY='your-api-key'")
    else:
        detector = DistanceLearningDetector(api_key=api_key)

        # 测试样本1：AI生成文本
        ai_text = """
        人工智能技术的发展为社会带来了深刻的变革。首先，它提高了生产效率。
        其次，它改善了人们的生活质量。最后，它推动了科技创新的进程。
        """

        print("测试AI生成文本：")
        result = detector.detect(ai_text.strip())
        print(f"AI概率：{result['ai_probability']}%")
        print(f"语义距离：{result['distance']:.3f}")
        print(f"置信度：{result['confidence']}")
        if 'error' in result:
            print(f"错误：{result['error']}")
        print()

        # 测试样本2：人类撰写文本
        human_text = """
        昨天我去了一家新开的咖啡店，环境超级棒！老板是个很有想法的年轻人，
        店里的装修风格特别文艺。我点了一杯拿铁，味道不错，价格也合理。
        下次还想再去试试他们家的甜品。
        """

        print("测试人类撰写文本：")
        result = detector.detect(human_text.strip())
        print(f"AI概率：{result['ai_probability']}%")
        print(f"语义距离：{result['distance']:.3f}")
        print(f"置信度：{result['confidence']}")
        if 'error' in result:
            print(f"错误：{result['error']}")
