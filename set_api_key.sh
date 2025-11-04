#!/bin/bash
# 快速设置API密钥环境变量的脚本

echo "🔑 设置DeepSeek API密钥"
echo "=" * 60

# 你的API密钥 - 请替换为你的真实API密钥
API_KEY="sk-your-api-key-here"

# 设置环境变量
export DEEPSEEK_API_KEY="$API_KEY"

echo "✅ 环境变量已设置: DEEPSEEK_API_KEY"
echo "   密钥: ${API_KEY:0:15}..."
echo ""
echo "💡 提示: 此设置仅在当前终端会话有效"
echo ""
echo "如需永久设置，请运行:"
echo "  echo 'export DEEPSEEK_API_KEY=\"$API_KEY\"' >> ~/.bashrc"
echo "  source ~/.bashrc"
echo ""
echo "现在可以运行:"
echo "  python3 run_demo.py"
