#!/usr/bin/env python3
"""
快速开始：真实LLM演示
展示自适应推理系统与真实LLM的集成效果
"""

import os
from llm_integration_example import ProductionAdaptiveReasoningSystem


def main():
    print("🤖 自适应推理系统 - 真实LLM演示")
    print("=" * 50)

    # 检查API密钥
    openai_key = os.getenv("OPENAI_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")

    if not openai_key and not deepseek_key:
        print("❌ 未检测到API密钥")
        print()
        print("📝 配置方法:")
        print("方法1 - 环境变量:")
        print("  export OPENAI_API_KEY='your_openai_key'")
        print("  export DEEPSEEK_API_KEY='your_deepseek_key'")
        print()
        print("方法2 - 直接传入:")
        print("  system = ProductionAdaptiveReasoningSystem(")
        print("      api_type='openai',")
        print("      api_key='your_api_key'")
        print("  )")
        print()
        print("方法3 - 配置文件:")
        print("  1. 复制 config_example.py 为 config.py")
        print("  2. 填入API密钥")
        print("  3. 运行 python config.py")
        return

    # 选择API
    if openai_key:
        api_type = "openai"
        api_key = openai_key
        print(f"✅ 使用 OpenAI API")
    else:
        api_type = "deepseek"
        api_key = deepseek_key
        print(f"✅ 使用 DeepSeek API")

    print(f"🔑 API Key: {api_key[:8]}...")
    print()

    # 初始化系统
    try:
        system = ProductionAdaptiveReasoningSystem(
            api_type=api_type,
            api_key=api_key
        )
        print("✅ 系统初始化成功")
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")
        return

    # 测试任务
    demo_tasks = [
        {
            "text": "编写一个Python函数计算斐波那契数列",
            "expected": "编程任务 → 应该选择非思考模式"
        },
        {
            "text": "证明勾股定理：a² + b² = c²",
            "expected": "数学证明 → 应该选择完整思考模式"
        },
        {
            "text": "什么是深度学习？",
            "expected": "简单问答 → 应该选择非思考模式"
        }
    ]

    print("🎯 开始测试...")
    print()

    for i, task in enumerate(demo_tasks, 1):
        print(f"📝 任务 {i}: {task['text']}")
        print(f"💡 预期: {task['expected']}")

        try:
            # 处理任务
            result = system.process_task(task["text"], f"demo_{i}")

            print(f"🎯 实际选择: {result.reasoning_mode.value}")
            print(f"📊 复杂度分数: {result.metadata['complexity_score']:.1f}")
            print(f"🎯 置信度: {result.confidence_score:.1%}")
            print(f"⏱️ 执行时间: {result.execution_time:.3f}秒")
            print("📄 LLM响应:")
            print(result.response[:200] + "..." if len(result.response) > 200 else result.response)

        except Exception as e:
            print(f"❌ 处理失败: {e}")

        print("=" * 60)

    # 显示统计
    stats = system.get_statistics()
    print("📊 系统统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()