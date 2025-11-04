# 🔑 API密钥配置指南

本项目使用**环境变量**方式管理API密钥，更加安全且符合最佳实践。

---

## 🚀 快速开始

### 方法1: 使用便捷脚本（最简单）

```bash
# 1. 在当前终端设置环境变量
source set_api_key.sh

# 2. 运行演示
python3 run_demo.py
```

### 方法2: 手动设置环境变量

```bash
# 临时设置（仅当前终端会话）
export DEEPSEEK_API_KEY='sk-your-api-key-here'

# 运行演示
python3 run_demo.py
```

### 方法3: 永久设置（推荐）

```bash
# 添加到 ~/.bashrc（永久生效）
echo 'export DEEPSEEK_API_KEY="sk-your-api-key-here"' >> ~/.bashrc

# 重新加载配置
source ~/.bashrc

# 现在可以随时运行
python3 run_demo.py
```

### 方法4: 一次性运行

```bash
# 在命令前设置环境变量（仅此次运行有效）
DEEPSEEK_API_KEY='sk-your-api-key-here' python3 run_demo.py
```

### 方法5: 交互式输入

```bash
# 直接运行，程序会提示输入API密钥
python3 run_demo.py

# 输出示例：
# ⚠️  未检测到环境变量 DEEPSEEK_API_KEY
# 💡 提示: 可以通过环境变量设置: export DEEPSEEK_API_KEY='your-key'
# 🔑 DeepSeek API Key: _____
```

---

## 🔒 安全优势

使用环境变量相比硬编码的优势：

✅ **不会被Git追踪** - API密钥不在代码文件中
✅ **更易于管理** - 在一个地方统一配置
✅ **符合12因素应用** - 配置与代码分离
✅ **支持多环境** - 开发/测试/生产环境独立配置
✅ **隐藏输入** - 交互式模式使用 getpass 隐藏密钥输入

---

## 📋 你的API密钥

**DeepSeek API Key**: `sk-your-api-key-here`

> ⚠️ 注意：请将上面的占位符替换为你的真实API密钥

---

## 🧪 验证配置

### 检查环境变量是否设置

```bash
# 查看环境变量
echo $DEEPSEEK_API_KEY

# 或使用配置检查工具
python3 config.py
```

输出示例：

```
🔑 API密钥配置检查
============================================================

📋 环境变量状态:
  DEEPSEEK_API_KEY:   ✅ 已设置
  OPENAI_API_KEY:     ❌ 未设置
  ANTHROPIC_API_KEY:  ❌ 未设置
```

### 测试API密钥获取

```bash
python3 config.py test
```

这会测试获取API密钥的完整流程（包括交互式输入）。

---

## 💻 在代码中使用

### 基础使用

```python
from config import get_deepseek_api_key

# 自动从环境变量获取（如果没有则提示输入）
api_key = get_deepseek_api_key()
print(f"API Key: {api_key[:10]}...")
```

### 集成到应用

```python
from config import get_deepseek_api_key, DEEPSEEK_API_KEY
from llm_integration_example import ProductionAdaptiveReasoningSystem

# 方式1: 如果环境变量已设置，直接使用
if DEEPSEEK_API_KEY:
    api_key = DEEPSEEK_API_KEY
else:
    # 方式2: 没有环境变量，提示用户输入
    api_key = get_deepseek_api_key()

# 初始化系统
system = ProductionAdaptiveReasoningSystem(
    api_type="deepseek",
    api_key=api_key
)

# 使用系统
result = system.process_task("你的问题", "task_1")
```

---

## 🔧 多API支持

### 配置多个API密钥

```bash
# 设置多个API提供商的密钥
export DEEPSEEK_API_KEY='sk-your-deepseek-key'
export OPENAI_API_KEY='sk-your-openai-key'
export ANTHROPIC_API_KEY='sk-ant-your-claude-key'
```

### 在代码中使用

```python
from config import get_openai_api_key, get_anthropic_api_key

# 获取不同提供商的API密钥
openai_key = get_openai_api_key()
claude_key = get_anthropic_api_key()
```

---

## 📝 便捷脚本说明

### `set_api_key.sh`

这个脚本会自动设置你的API密钥环境变量：

```bash
# 使用 source 命令运行（让环境变量在当前shell生效）
source set_api_key.sh

# 或
. set_api_key.sh
```

**注意**: 必须使用 `source` 或 `.` 命令运行，直接 `./set_api_key.sh` 不会生效（环境变量只在子shell中）。

---

## 🌍 不同Shell的配置

### Bash/Zsh

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export DEEPSEEK_API_KEY="sk-your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Fish Shell

```bash
# Fish使用不同的语法
set -Ux DEEPSEEK_API_KEY "sk-your-api-key-here"
```

### Windows (PowerShell)

```powershell
# 临时设置
$env:DEEPSEEK_API_KEY = "sk-your-api-key-here"

# 永久设置（系统环境变量）
[System.Environment]::SetEnvironmentVariable('DEEPSEEK_API_KEY', 'sk-your-api-key-here', 'User')
```

---

## 🐛 常见问题

### Q: 为什么运行时还是提示输入API密钥？

A: 检查以下几点：
1. 环境变量是否正确设置：`echo $DEEPSEEK_API_KEY`
2. 是否使用了 `source` 命令加载脚本
3. 是否在同一个终端会话中运行

### Q: 如何撤销环境变量？

A:
```bash
# 临时撤销（当前会话）
unset DEEPSEEK_API_KEY

# 永久撤销（从配置文件中删除对应行）
nano ~/.bashrc  # 删除 export DEEPSEEK_API_KEY=... 这一行
source ~/.bashrc
```

### Q: 我想用配置文件，不想用环境变量

A: 可以创建一个 `.env` 文件（已添加到 .gitignore）：
```bash
# 创建 .env 文件
echo 'DEEPSEEK_API_KEY=sk-your-api-key-here' > .env

# 安装 python-dotenv
pip install python-dotenv

# 在代码开头加载
from dotenv import load_dotenv
load_dotenv()
```

---

## 📚 相关文档

- **快速开始**: `QUICK_START.md`
- **项目文档**: `README.md`
- **演示脚本**: `run_demo.py`

---

## ✅ 推荐流程

**最佳实践（按推荐顺序）**:

1. 🥇 **永久环境变量** - 添加到 ~/.bashrc
2. 🥈 **临时环境变量** - export 命令
3. 🥉 **交互式输入** - 运行时提示输入

**不推荐**:
- ❌ 硬编码在代码文件中
- ❌ 提交到Git仓库

---

**准备好了吗？** 选择一种方式设置API密钥，然后运行 `python3 run_demo.py` 开始体验！
