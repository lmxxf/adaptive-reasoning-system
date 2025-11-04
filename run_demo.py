#!/usr/bin/env python3
"""
一键运行演示 - 使用DeepSeek API
支持环境变量和交互式输入
"""

from config import get_deepseek_api_key, DEEPSEEK_API_KEY
from llm_integration_example import ProductionAdaptiveReasoningSystem


def main():
    print("🤖 自适应推理系统 - DeepSeek API 演示")
    print("=" * 60)
    print()

    # 获取API密钥（自动处理环境变量或交互式输入）
    try:
        # 如果环境变量已设置，直接使用
        if DEEPSEEK_API_KEY:
            api_key = DEEPSEEK_API_KEY
            print(f"✅ API密钥已加载: {api_key[:15]}...")
        else:
            # 没有环境变量，提示用户输入
            api_key = get_deepseek_api_key()
            print(f"✅ API密钥已输入: {api_key[:15]}...")

    except KeyboardInterrupt:
        print("\n\n❌ 用户取消")
        return
    except Exception as e:
        print(f"❌ 获取API密钥失败: {e}")
        return

    print()

    # 初始化系统
    try:
        system = ProductionAdaptiveReasoningSystem(
            api_type="deepseek",
            api_key=api_key
        )
        print("✅ 系统初始化成功")
        print()
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")
        return

    # 测试任务
    demo_tasks = [
        {
            "text": "编写一个Python函数计算两个数的最大公约数",
            "expected": "编程任务 → 非思考模式/简化思考模式"
        },
        {
            "text": "证明：对于任意正整数n，1+2+3+...+n = n(n+1)/2",
            "expected": "数学证明 → 完整思考模式"
        },
        {
            "text": "什么是人工智能？",
            "expected": "简单问答 → 非思考模式"
        },
        {
            "text": "设计一个高并发的微服务架构",
            "expected": "复杂设计 → 完整思考模式/简化思考模式"
        }
    ]

    print("🎯 开始测试 (共4个任务)...")
    print()

    for i, task in enumerate(demo_tasks, 1):
        print("=" * 60)
        print(f"📝 任务 {i}/{len(demo_tasks)}: {task['text']}")
        print(f"💡 预期推理模式: {task['expected']}")
        print()

        try:
            # 处理任务
            result = system.process_task(task["text"], f"demo_{i}")

            print(f"🧠 选择模式: {result.reasoning_mode.value}")
            print(f"📊 复杂度分数: {result.metadata.get('complexity_score', 0):.1f}")
            print(f"✅ 置信度: {result.confidence_score:.1%}")
            print(f"⏱️  执行时间: {result.execution_time:.3f}秒")
            print()
            print("💬 DeepSeek响应:")
            print("-" * 60)
            # 显示前500个字符
            response_preview = result.response[:500] if len(result.response) > 500 else result.response
            print(response_preview)
            if len(result.response) > 500:
                print(f"\n... (还有 {len(result.response) - 500} 个字符)")
            print("-" * 60)

        except Exception as e:
            print(f"❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()

        print()

    # 显示统计
    print("=" * 60)
    print("📊 系统运行统计:")
    print("=" * 60)
    stats = system.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    print("✅ 演示完成！")
    print()
    print("💡 提示:")
    print("  - 设置环境变量避免每次输入: export DEEPSEEK_API_KEY='your-key'")
    print("  - 查看 llm_integration_example.py 了解实现细节")
    print("  - 运行 python3 demo.py 查看更多示例")


if __name__ == "__main__":
    main()
