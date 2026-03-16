"""
AI检测器：整合规则引擎和Distance Learning

三阶段检测流程：
1. 规则引擎快速筛选
2. Distance Learning精准检测
3. 统计验证
"""

from typing import Dict, Optional
from app.core.rule_engine import RuleEngine
from app.core.distance_learning import DistanceLearningDetector


class AIDetector:
    """AI文本检测器（整合版）"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化检测器

        Args:
            api_key: Deepseek API密钥
        """
        self.rule_engine = RuleEngine()
        self.distance_detector = DistanceLearningDetector(api_key) if api_key else None

    def detect(self, text: str, use_distance_learning: bool = True) -> Dict:
        """
        检测文本的AI概率

        Args:
            text: 待检测文本（段落）
            use_distance_learning: 是否使用Distance Learning（需要API调用）

        Returns:
            {
                "final_score": 最终AI概率（0-100）,
                "confidence": 置信度,
                "stage1_rule": 规则引擎结果,
                "stage2_distance": Distance Learning结果（如果启用）,
                "reasons": 检测原因列表
            }
        """
        result = {
            "final_score": 0,
            "confidence": "low",
            "stage1_rule": None,
            "stage2_distance": None,
            "reasons": []
        }

        # 阶段1：规则引擎快速筛选
        rule_result = self.rule_engine.detect(text)
        result["stage1_rule"] = rule_result
        result["reasons"].extend(rule_result["reasons"])

        # 如果规则引擎分数很低，直接返回
        if rule_result["score"] < 30:
            result["final_score"] = rule_result["score"]
            result["confidence"] = "medium" if rule_result["score"] > 0 else "low"
            result["reasons"].append("规则引擎判定为人工撰写，无需进一步检测")
            return result

        # 阶段2：Distance Learning精准检测
        if use_distance_learning and self.distance_detector:
            try:
                distance_result = self.distance_detector.detect(text)
                result["stage2_distance"] = distance_result

                if "error" not in distance_result:
                    # 综合两个阶段的结果
                    # 权重：规则引擎40%，Distance Learning 60%
                    combined_score = (
                        rule_result["score"] * 0.4 +
                        distance_result["ai_probability"] * 0.6
                    )
                    result["final_score"] = int(combined_score)
                    result["confidence"] = distance_result["confidence"]
                    result["reasons"].append(
                        f"Distance Learning检测：语义距离={distance_result['distance']:.2f}"
                    )
                else:
                    # Distance Learning失败，只用规则引擎结果
                    result["final_score"] = rule_result["score"]
                    result["confidence"] = "medium"
                    result["reasons"].append(f"Distance Learning检测失败：{distance_result['error']}")

            except Exception as e:
                # 出错时降级到规则引擎
                result["final_score"] = rule_result["score"]
                result["confidence"] = "medium"
                result["reasons"].append(f"Distance Learning检测异常：{str(e)}")
        else:
            # 未启用Distance Learning，只用规则引擎
            result["final_score"] = rule_result["score"]
            result["confidence"] = "medium"

        return result


# 测试代码
if __name__ == "__main__":
    import os

    # 测试样本
    ai_text = """
    首先，我们需要认识到人工智能的重要性。其次，人工智能在各个领域都有广泛的应用。
    再次，我们应该重视人工智能的发展。最后，总而言之，人工智能是未来的趋势。
    值得注意的是，人工智能技术正在快速发展。需要指出的是，这一趋势不可逆转。
    """

    human_text = """
    我真的超级喜欢这个想法！昨天晚上想了一夜，越想越兴奋。
    虽然实现起来可能有点难，但我觉得值得一试。
    你觉得呢？咱们要不要先做个小demo看看效果？
    """

    # 测试1：仅使用规则引擎
    print("=" * 50)
    print("测试1：仅使用规则引擎")
    print("=" * 50)

    detector = AIDetector()

    print("\nAI生成文本：")
    result = detector.detect(ai_text, use_distance_learning=False)
    print(f"最终得分：{result['final_score']}")
    print(f"置信度：{result['confidence']}")
    print(f"原因：{result['reasons']}")

    print("\n人类撰写文本：")
    result = detector.detect(human_text, use_distance_learning=False)
    print(f"最终得分：{result['final_score']}")
    print(f"置信度：{result['confidence']}")
    print(f"原因：{result['reasons']}")

    # 测试2：使用Distance Learning（需要API密钥）
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        print("\n" + "=" * 50)
        print("测试2：使用Distance Learning")
        print("=" * 50)

        detector_with_dl = AIDetector(api_key=api_key)

        print("\nAI生成文本：")
        result = detector_with_dl.detect(ai_text, use_distance_learning=True)
        print(f"最终得分：{result['final_score']}")
        print(f"置信度：{result['confidence']}")
        print(f"规则引擎得分：{result['stage1_rule']['score']}")
        if result['stage2_distance']:
            print(f"Distance Learning概率：{result['stage2_distance']['ai_probability']}")
            print(f"语义距离：{result['stage2_distance']['distance']:.2f}")
        print(f"原因：{result['reasons']}")
    else:
        print("\n未设置DEEPSEEK_API_KEY环境变量，跳过Distance Learning测试")
