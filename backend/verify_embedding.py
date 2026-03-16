"""
手动验证脚本：SiliconFlow Embedding 集成
用于快速验证 Distance Learning 检测功能
"""

import os
import sys
from app.core.distance_learning import DistanceLearningDetector


def main():
    """主函数"""
    print("=" * 60)
    print("SiliconFlow Embedding 集成验证")
    print("=" * 60)

    # 检查环境变量
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    siliconflow_key = os.getenv("SILICONFLOW_API_KEY")

    if not deepseek_key:
        print("\n❌ 错误：未设置 DEEPSEEK_API_KEY 环境变量")
        print("请设置后再运行：")
        print("  export DEEPSEEK_API_KEY='your-api-key'")
        sys.exit(1)

    if not siliconflow_key:
        print("\n❌ 错误：未设置 SILICONFLOW_API_KEY 环境变量")
        print("请设置后再运行：")
        print("  export SILICONFLOW_API_KEY='your-api-key'")
        sys.exit(1)

    print("\n✓ 环境变量检查通过")

    # 初始化检测器
    try:
        detector = DistanceLearningDetector()
        print("✓ 检测器初始化成功")
    except Exception as e:
        print(f"\n❌ 检测器初始化失败: {e}")
        sys.exit(1)

    # 测试样本
    ai_text = """
    人工智能技术的发展为社会带来了深刻的变革。首先，它提高了生产效率。
    其次，它改善了人们的生活质量。最后，它推动了科技创新的进程。
    总之，人工智能将继续在未来发挥重要作用。
    """

    human_text = """
    昨天我去了一家新开的咖啡店，环境超级棒！老板是个很有想法的年轻人，
    店里的装修风格特别文艺。我点了一杯拿铁，味道不错，价格也合理。
    下次还想再去试试他们家的甜品，听说芝士蛋糕特别好吃。
    """

    print("\n" + "=" * 60)
    print("测试 1: AI 生成风格文本")
    print("=" * 60)
    print(f"文本内容: {ai_text.strip()[:50]}...")

    try:
        result1 = detector.detect(ai_text.strip())
        print(f"\n✓ 检测完成")
        print(f"  AI 概率: {result1['ai_probability']:.1f}%")
        print(f"  语义距离: {result1['distance']:.4f}")
        print(f"  置信度: {result1['confidence']}")

        if 'error' in result1:
            print(f"  ⚠ 警告: {result1['error']}")

        if 'rewritten_text' in result1 and result1['rewritten_text']:
            print(f"  改写文本: {result1['rewritten_text'][:50]}...")

    except Exception as e:
        print(f"\n❌ 检测失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试 2: 人类撰写风格文本")
    print("=" * 60)
    print(f"文本内容: {human_text.strip()[:50]}...")

    try:
        result2 = detector.detect(human_text.strip())
        print(f"\n✓ 检测完成")
        print(f"  AI 概率: {result2['ai_probability']:.1f}%")
        print(f"  语义距离: {result2['distance']:.4f}")
        print(f"  置信度: {result2['confidence']}")

        if 'error' in result2:
            print(f"  ⚠ 警告: {result2['error']}")

        if 'rewritten_text' in result2 and result2['rewritten_text']:
            print(f"  改写文本: {result2['rewritten_text'][:50]}...")

    except Exception as e:
        print(f"\n❌ 检测失败: {e}")
        import traceback
        traceback.print_exc()

    # 结果对比
    print("\n" + "=" * 60)
    print("结果对比")
    print("=" * 60)

    try:
        if 'distance' in result1 and 'distance' in result2:
            print(f"AI 文本距离:   {result1['distance']:.4f}")
            print(f"人类文本距离:  {result2['distance']:.4f}")
            print(f"距离差异:      {abs(result1['distance'] - result2['distance']):.4f}")

            if result1['distance'] < result2['distance']:
                print("\n✓ 符合预期: AI 文本距离 < 人类文本距离")
                print("  (AI 生成文本在改写后更稳定)")
            else:
                print("\n⚠ 不符合预期: AI 文本距离 >= 人类文本距离")
                print("  这可能是由于:")
                print("  - 样本选择不够典型")
                print("  - 改写质量不够好")
                print("  - 需要调整阈值参数")

    except Exception as e:
        print(f"⚠ 无法进行对比: {e}")

    print("\n" + "=" * 60)
    print("验证完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
