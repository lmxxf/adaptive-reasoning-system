#!/usr/bin/env python3
"""
API密钥配置文件
优先使用环境变量，没有则提示用户输入
"""

import os
import getpass


def get_api_key(provider: str = "deepseek", env_var: str = None, prompt: str = None) -> str:
    """
    获取API密钥（支持环境变量和交互式输入）

    Args:
        provider: API提供商名称（用于提示信息）
        env_var: 环境变量名
        prompt: 交互式提示文本

    Returns:
        API密钥
    """
    # 1. 首先尝试从环境变量读取
    if env_var:
        api_key = os.getenv(env_var)
        if api_key:
            print(f"✅ 从环境变量 {env_var} 加载 {provider} API密钥")
            return api_key

    # 2. 没有环境变量，提示用户输入
    print(f"⚠️  未检测到环境变量 {env_var}")
    print()

    if prompt:
        print(prompt)
    else:
        print(f"请输入 {provider} API密钥:")

    # 使用 getpass 隐藏输入（更安全）
    api_key = getpass.getpass(f"🔑 {provider} API Key: ")

    if not api_key or api_key.strip() == "":
        raise ValueError(f"API密钥不能为空")

    return api_key.strip()


# =============================================================================
# API密钥配置 - 优先使用环境变量
# =============================================================================

def get_deepseek_api_key() -> str:
    """获取DeepSeek API密钥"""
    return get_api_key(
        provider="DeepSeek",
        env_var="DEEPSEEK_API_KEY",
        prompt="💡 提示: 可以通过环境变量设置: export DEEPSEEK_API_KEY='your-key'"
    )


def get_openai_api_key() -> str:
    """获取OpenAI API密钥"""
    return get_api_key(
        provider="OpenAI",
        env_var="OPENAI_API_KEY",
        prompt="💡 提示: 可以通过环境变量设置: export OPENAI_API_KEY='your-key'"
    )


def get_anthropic_api_key() -> str:
    """获取Anthropic/Claude API密钥"""
    return get_api_key(
        provider="Anthropic",
        env_var="ANTHROPIC_API_KEY",
        prompt="💡 提示: 可以通过环境变量设置: export ANTHROPIC_API_KEY='your-key'"
    )


# =============================================================================
# 向后兼容 - 直接变量方式（仅在明确设置环境变量时可用）
# =============================================================================

# 尝试从环境变量加载（如果没有，这些变量将为None）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


# =============================================================================
# 使用示例和测试
# =============================================================================

if __name__ == "__main__":
    print("🔑 API密钥配置检查")
    print("=" * 60)

    # 检查环境变量
    print("\n📋 环境变量状态:")
    print(f"  DEEPSEEK_API_KEY:   {'✅ 已设置' if DEEPSEEK_API_KEY else '❌ 未设置'}")
    print(f"  OPENAI_API_KEY:     {'✅ 已设置' if OPENAI_API_KEY else '❌ 未设置'}")
    print(f"  ANTHROPIC_API_KEY:  {'✅ 已设置' if ANTHROPIC_API_KEY else '❌ 未设置'}")

    print("\n" + "=" * 60)
    print("💡 推荐配置方式:")
    print()
    print("1. 设置环境变量（推荐）:")
    print("   export DEEPSEEK_API_KEY='sk-your-api-key'")
    print()
    print("2. 或在 ~/.bashrc 中添加:")
    print("   echo 'export DEEPSEEK_API_KEY=\"sk-your-api-key\"' >> ~/.bashrc")
    print("   source ~/.bashrc")
    print()
    print("3. 临时设置（仅当前会话）:")
    print("   DEEPSEEK_API_KEY='sk-your-api-key' python3 run_demo.py")
    print()
    print("=" * 60)

    # 测试获取API密钥（如果用户想测试）
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("\n🧪 测试获取API密钥...")
        try:
            key = get_deepseek_api_key()
            print(f"✅ API密钥获取成功: {key[:10]}...{key[-4:]}")
        except KeyboardInterrupt:
            print("\n\n❌ 用户取消")
        except Exception as e:
            print(f"\n❌ 错误: {e}")
