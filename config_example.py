#!/usr/bin/env python3
"""
API Key 配置示例
请复制此文件为 config.py 并填入您的API密钥
"""

# =============================================================================
# API 配置 - 请填入您的真实API密钥
# =============================================================================

# OpenAI API配置
OPENAI_API_KEY = "sk-xxx..."  # 在这里填入您的OpenAI API Key

# DeepSeek API配置
DEEPSEEK_API_KEY = "sk-xxx..."  # 在这里填入您的DeepSeek API Key

# 其他API配置
ANTHROPIC_API_KEY = "sk-ant-xxx..."  # Claude API Key

# =============================================================================
# 使用示例
# =============================================================================

def get_real_demo():
    """运行真实LLM的演示"""
    from llm_integration_example import ProductionAdaptiveReasoningSystem

    # 使用OpenAI API
    system_openai = ProductionAdaptiveReasoningSystem(
        api_type="openai",
        api_key=OPENAI_API_KEY
    )

    # 使用DeepSeek API
    system_deepseek = ProductionAdaptiveReasoningSystem(
        api_type="deepseek",
        api_key=DEEPSEEK_API_KEY
    )

    # 测试任务
    test_tasks = [
        "编写一个Python函数计算斐波那契数列的第n项",
        "证明：对于任意正整数n，1+2+3+...+n = n(n+1)/2",
        "什么是人工智能？",
        "设计一个高并发的微服务架构"
    ]

    print("🚀 真实LLM自适应推理演示")
    print("=" * 50)

    for i, task in enumerate(test_tasks, 1):
        print(f"\n任务 {i}: {task}")

        # 使用自适应系统处理
        result = system_openai.process_task(task, f"real_test_{i}")

        print(f"推理模式: {result.reasoning_mode.value}")
        print(f"复杂度: {result.metadata['complexity_score']:.1f}")
        print(f"置信度: {result.confidence_score:.1%}")
        print(f"执行时间: {result.execution_time:.3f}秒")
        print("响应内容:")
        print(result.response)
        print("-" * 50)


if __name__ == "__main__":
    # 检查API密钥是否已配置
    if OPENAI_API_KEY == "sk-xxx..." and DEEPSEEK_API_KEY == "sk-xxx...":
        print("❌ 请先在 config.py 中配置您的API密钥")
        print("📝 步骤:")
        print("1. 复制 config_example.py 为 config.py")
        print("2. 在 config.py 中填入真实的API密钥")
        print("3. 运行 python config.py")
    else:
        # 安装依赖提醒
        try:
            import openai
            get_real_demo()
        except ImportError:
            print("❌ 请先安装openai库:")
            print("pip install openai")