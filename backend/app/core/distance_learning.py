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
from app.config import get_settings


class EmbeddingAPIError(Exception):
    """Embedding API 调用失败异常"""
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(self.message)


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

        # 从配置读取 SiliconFlow 配置
        settings = get_settings()
        self.siliconflow_api_key = settings.siliconflow_api_key
        self.siliconflow_api_base = settings.siliconflow_api_base
        self.siliconflow_model = settings.siliconflow_model

        if not self.siliconflow_api_key:
            raise ValueError("需要在配置中提供 siliconflow_api_key")

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

    def _get_embedding(self, text: str) -> list:
        """
        调用 SiliconFlow API 获取文本的 Embedding 向量

        Args:
            text: 输入文本

        Returns:
            Embedding 向量（list of float）

        Raises:
            EmbeddingAPIError: API 调用失败
        """
        url = f"{self.siliconflow_api_base}/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.siliconflow_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.siliconflow_model,
            "input": text
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=(5, 10)
            )

            if response.status_code != 200:
                raise EmbeddingAPIError(
                    f"SiliconFlow API 调用失败",
                    status_code=response.status_code,
                    response_text=response.text
                )

            result = response.json()

            # 提取 embedding 向量
            if "data" in result and len(result["data"]) > 0:
                embedding = result["data"][0].get("embedding")
                if embedding:
                    return embedding

            raise EmbeddingAPIError(
                "API 响应格式错误：未找到 embedding 数据",
                response_text=response.text
            )

        except EmbeddingAPIError:
            # 重新抛出我们自己的异常
            raise
        except requests.exceptions.Timeout:
            raise EmbeddingAPIError("API 请求超时")
        except requests.exceptions.RequestException as e:
            raise EmbeddingAPIError(f"API 请求失败: {str(e)}")
        except json.JSONDecodeError:
            raise EmbeddingAPIError("API 响应解析失败", response_text=response.text)
        except Exception as e:
            raise EmbeddingAPIError(f"未知错误: {str(e)}")

    def _cosine_similarity(self, vec1: list, vec2: list) -> float:
        """
        计算两个向量的余弦相似度（手写实现，不使用 numpy）

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            余弦相似度（0-1之间）
        """
        # 计算点积
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # 计算模长
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        # 返回余弦相似度
        return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0

    def _calculate_semantic_distance(self, text1: str, text2: str) -> float:
        """
        计算两段文本的语义距离（使用 Embedding 向量的余弦距离）

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            距离值（0-1之间，越小越相似）
        """
        try:
            # 获取两个文本的 Embedding
            embedding1 = self._get_embedding(text1)
            embedding2 = self._get_embedding(text2)

            # 计算余弦相似度
            similarity = self._cosine_similarity(embedding1, embedding2)

            # 转换为距离（1 - 相似度）
            distance = 1.0 - similarity

            return distance
        except EmbeddingAPIError as e:
            # 抛出异常，不降级
            raise

    # ==================== 原有 Levenshtein 实现（已废弃，保留作为参考） ====================
    # def _calculate_semantic_distance(self, text1: str, text2: str) -> float:
    #     """
    #     计算两段文本的语义距离
    #
    #     简化版实现：使用字符级编辑距离 / 文本长度
    #     生产环境建议使用embedding向量的余弦距离
    #
    #     Args:
    #         text1: 文本1
    #         text2: 文本2
    #
    #     Returns:
    #         距离值（0-1之间，越小越相似）
    #     """
    #     # 简化版：使用Levenshtein距离
    #     distance = self._levenshtein_distance(text1, text2)
    #     max_len = max(len(text1), len(text2))
    #
    #     # 归一化到0-1
    #     normalized_distance = distance / max_len if max_len > 0 else 0
    #
    #     return normalized_distance
    #
    # def _levenshtein_distance(self, s1: str, s2: str) -> int:
    #     """
    #     计算Levenshtein编辑距离
    #
    #     Args:
    #         s1: 字符串1
    #         s2: 字符串2
    #
    #     Returns:
    #         编辑距离
    #     """
    #     if len(s1) < len(s2):
    #         return self._levenshtein_distance(s2, s1)
    #
    #     if len(s2) == 0:
    #         return len(s1)
    #
    #     previous_row = range(len(s2) + 1)
    #     for i, c1 in enumerate(s1):
    #         current_row = [i + 1]
    #         for j, c2 in enumerate(s2):
    #             # 插入、删除、替换的代价
    #             insertions = previous_row[j + 1] + 1
    #             deletions = current_row[j] + 1
    #             substitutions = previous_row[j] + (c1 != c2)
    #             current_row.append(min(insertions, deletions, substitutions))
    #         previous_row = current_row
    #
    #     return previous_row[-1]
    # ==================== 原有实现结束 ====================

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
