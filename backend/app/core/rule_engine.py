"""
规则引擎：基于统计特征的AI文本快速筛选

检测特征：
1. 套路短语（"首先"、"其次"、"总而言之"等）
2. 句式工整度（句子长度方差）
3. 词汇多样性（unique ratio）
4. 情感强度（平淡 vs 丰富）
"""

import re
from typing import Dict, List, Tuple
import jieba


class RuleEngine:
    """规则引擎：快速筛选AI文本"""

    # AI常用套路短语
    AI_PHRASES = [
        "首先", "其次", "再次", "最后", "总而言之", "综上所述",
        "值得注意的是", "需要指出的是", "不可否认", "毋庸置疑",
        "从某种意义上说", "在一定程度上", "总的来说", "换句话说",
        "与此同时", "由此可见", "显而易见", "众所周知"
    ]

    def __init__(self):
        """初始化规则引擎"""
        pass

    def detect(self, text: str) -> Dict:
        """
        检测文本的AI概率

        Args:
            text: 待检测文本（段落）

        Returns:
            {
                "score": 0-100的AI概率分数,
                "features": {
                    "phrase_score": 套路短语得分,
                    "uniformity_score": 句式工整度得分,
                    "diversity_score": 词汇多样性得分,
                    "emotion_score": 情感强度得分
                },
                "reasons": ["检测到的具体原因"]
            }
        """
        if not text or len(text.strip()) < 20:
            return {
                "score": 0,
                "features": {},
                "reasons": ["文本过短，无法判断"]
            }

        features = {}
        reasons = []
        total_score = 0

        # 特征1：套路短语检测
        phrase_score, phrase_reasons = self._check_ai_phrases(text)
        features["phrase_score"] = phrase_score
        total_score += phrase_score
        reasons.extend(phrase_reasons)

        # 特征2：句式工整度
        uniformity_score, uniformity_reasons = self._check_sentence_uniformity(text)
        features["uniformity_score"] = uniformity_score
        total_score += uniformity_score
        reasons.extend(uniformity_reasons)

        # 特征3：词汇多样性
        diversity_score, diversity_reasons = self._check_word_diversity(text)
        features["diversity_score"] = diversity_score
        total_score += diversity_score
        reasons.extend(diversity_reasons)

        # 特征4：情感强度（简化版）
        emotion_score, emotion_reasons = self._check_emotion_intensity(text)
        features["emotion_score"] = emotion_score
        total_score += emotion_score
        reasons.extend(emotion_reasons)

        # 总分限制在0-100
        final_score = min(total_score, 100)

        return {
            "score": final_score,
            "features": features,
            "reasons": reasons
        }

    def _check_ai_phrases(self, text: str) -> Tuple[int, List[str]]:
        """
        检测套路短语

        Returns:
            (得分, 原因列表)
        """
        found_phrases = [phrase for phrase in self.AI_PHRASES if phrase in text]
        count = len(found_phrases)

        if count == 0:
            return 0, []
        elif count == 1:
            return 10, [f"使用了套路短语：{found_phrases[0]}"]
        elif count == 2:
            return 20, [f"使用了多个套路短语：{', '.join(found_phrases)}"]
        else:
            return 30, [f"大量使用套路短语（{count}个）：{', '.join(found_phrases[:3])}等"]

    def _check_sentence_uniformity(self, text: str) -> Tuple[int, List[str]]:
        """
        检测句式工整度（句子长度方差）

        AI生成的文本句子长度往往更均匀
        """
        # 按句号、问号、感叹号分句
        sentences = re.split(r'[。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 3:
            return 0, []

        # 计算句子长度
        lengths = [len(s) for s in sentences]
        avg_length = sum(lengths) / len(lengths)

        # 计算方差
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        std_dev = variance ** 0.5

        # 变异系数（标准差/平均值）
        cv = std_dev / avg_length if avg_length > 0 else 0

        # 变异系数越小，句子越工整（越像AI）
        if cv < 0.2:
            return 25, [f"句式过于工整（变异系数={cv:.2f}）"]
        elif cv < 0.3:
            return 15, [f"句式较为工整（变异系数={cv:.2f}）"]
        else:
            return 0, []

    def _check_word_diversity(self, text: str) -> Tuple[int, List[str]]:
        """
        检测词汇多样性

        AI生成的文本词汇重复率往往更高
        """
        # 使用jieba分词
        words = list(jieba.cut(text))
        # 过滤标点和空格
        words = [w for w in words if w.strip() and not re.match(r'^[，。！？、；：""''（）《》\\s]+$', w)]

        if len(words) < 10:
            return 0, []

        # 计算unique ratio
        unique_ratio = len(set(words)) / len(words)

        # unique ratio越低，词汇多样性越差（越像AI）
        if unique_ratio < 0.5:
            return 25, [f"词汇多样性低（重复率={1-unique_ratio:.1%}）"]
        elif unique_ratio < 0.6:
            return 15, [f"词汇多样性较低（重复率={1-unique_ratio:.1%}）"]
        else:
            return 0, []

    def _check_emotion_intensity(self, text: str) -> Tuple[int, List[str]]:
        """
        检测情感强度（简化版）

        AI生成的文本情感表达往往更平淡
        """
        # 情感词（简化版）
        strong_emotion_words = [
            "非常", "特别", "极其", "十分", "相当", "太", "真",
            "超级", "巨", "狂", "疯狂", "爆", "炸裂",
            "爱", "恨", "喜欢", "讨厌", "激动", "兴奋", "愤怒", "悲伤"
        ]

        emotion_count = sum(1 for word in strong_emotion_words if word in text)

        # 情感词密度
        text_length = len(text)
        emotion_density = emotion_count / (text_length / 100) if text_length > 0 else 0

        # 情感密度越低，越像AI
        if emotion_density < 0.5:
            return 20, ["情感表达平淡，缺少个人色彩"]
        elif emotion_density < 1.0:
            return 10, ["情感表达较为平淡"]
        else:
            return 0, []


# 测试代码
if __name__ == "__main__":
    engine = RuleEngine()

    # 测试样本1：明显AI生成
    ai_text = """
    首先，我们需要认识到人工智能的重要性。其次，人工智能在各个领域都有广泛的应用。
    再次，我们应该重视人工智能的发展。最后，总而言之，人工智能是未来的趋势。
    值得注意的是，人工智能技术正在快速发展。需要指出的是，这一趋势不可逆转。
    """

    result = engine.detect(ai_text)
    print("AI生成文本检测结果：")
    print(f"得分：{result['score']}")
    print(f"特征：{result['features']}")
    print(f"原因：{result['reasons']}")
    print()

    # 测试样本2：人类撰写
    human_text = """
    我真的超级喜欢这个想法！昨天晚上想了一夜，越想越兴奋。
    虽然实现起来可能有点难，但我觉得值得一试。
    你觉得呢？咱们要不要先做个小demo看看效果？
    """

    result = engine.detect(human_text)
    print("人类撰写文本检测结果：")
    print(f"得分：{result['score']}")
    print(f"特征：{result['features']}")
    print(f"原因：{result['reasons']}")
