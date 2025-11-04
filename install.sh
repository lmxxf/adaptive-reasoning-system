#!/bin/bash

# 自适应推理系统安装脚本
# 基于《大语言模型的内部推理与外部输出差异性研究》

echo "🤖 大语言模型自适应推理系统安装脚本"
echo "========================================"
echo "作者：Kien Ngam Ngam"
echo ""

# 检查Python版本
echo "🔍 检查Python环境..."
python_version=$(python3 --version 2>/dev/null | awk '{print $2}')
if [ -z "$python_version" ]; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

echo "✅ Python版本: $python_version"

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: 未找到pip3，请先安装pip"
    exit 1
fi

echo "✅ pip3已安装"

# 创建虚拟环境（可选）
read -p "🤔 是否创建Python虚拟环境? (y/n): " create_venv
if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv

    if [ $? -ne 0 ]; then
        echo "❌ 虚拟环境创建失败"
        echo "💡 在Debian/Ubuntu系统上，请先运行:"
        echo "   sudo apt install python3-venv"
        echo ""
        echo "⚠️  继续使用系统Python环境安装..."
    else
        source venv/bin/activate
        echo "✅ 虚拟环境已激活"
    fi
fi

# 安装依赖
echo "📥 安装项目依赖..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 依赖安装成功"
else
    echo "❌ 依赖安装失败，请检查网络连接"
    exit 1
fi

# 运行演示
echo ""
echo "🎯 安装完成！"
echo ""
echo "📋 下一步操作："
echo "1. 🚀 真实LLM演示: python3 run_demo.py (使用DeepSeek API)"
echo "2. 📖 基础演示: python3 demo.py (模拟模式)"
echo "3. 🧪 完整测试: python3 test_examples.py"
echo "4. ⚙️  系统测试: python3 adaptive_reasoning_system.py"
echo ""

read -p "🚀 是否立即运行真实LLM演示? (y/n): " run_demo
if [ "$run_demo" = "y" ] || [ "$run_demo" = "Y" ]; then
    echo "🎭 运行DeepSeek API演示程序..."
    python3 run_demo.py
fi

echo ""
echo "🎉 安装和设置完成！"
echo "📚 查看 README.md 了解详细使用方法"
echo "🐛 遇到问题请查看GitHub Issues"