#!/usr/bin/env python3
"""
LLM集成示例
展示如何将自适应推理系统与真实的LLM API集成
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any
from adaptive_reasoning_system import (
    AdaptiveReasoningSystem, ReasoningMode, ReasoningExecutor, TaskFeatures
)


class LLMAPIClient:
    """LLM API客户端接口（可适配多种API）"""

    def __init__(self, api_type: str = "openai", api_key: str = None, base_url: str = None):
        self.api_type = api_type
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url
        self.client = self._initialize_client()

    def _initialize_client(self):
        """初始化API客户端"""
        if self.api_type == "openai":
            try:
                import openai
                return openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                print("警告: 未安装openai库，使用模拟响应")
                return None
        elif self.api_type == "deepseek":
            # DeepSeek API客户端
            try:
                import openai  # DeepSeek兼容OpenAI API
                return openai.OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com/v1"
                )
            except ImportError:
                print("警告: 未安装openai库，使用模拟响应")
                return None
        else:
            print(f"警告: 不支持的API类型 {self.api_type}，使用模拟响应")
            return None

    async def generate_response(self, prompt: str, mode: ReasoningMode,
                               temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """生成响应"""
        if self.client is None:
            return self._simulate_response(prompt, mode)

        try:
            # 根据推理模式调整参数
            if mode == ReasoningMode.NON_THINKING:
                temperature = 0.3  # 更确定性的输出
                max_tokens = 1024  # 较短的回答
            elif mode == ReasoningMode.SIMPLIFIED:
                temperature = 0.5
                max_tokens = 1536
            else:  # FULL_THINKING
                temperature = 0.7
                max_tokens = 2048  # 允许更长的详细回答

            # 选择模型
            model = self._get_model_for_mode(mode)

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"API调用失败: {e}")
            return self._simulate_response(prompt, mode)

    def _get_model_for_mode(self, mode: ReasoningMode) -> str:
        """根据推理模式选择合适的模型"""
        if self.api_type == "openai":
            if mode == ReasoningMode.FULL_THINKING:
                return "gpt-4-turbo-preview"  # 更强的推理能力
            else:
                return "gpt-3.5-turbo"  # 更快速的响应
        elif self.api_type == "deepseek":
            return "deepseek-chat"
        else:
            return "default-model"

    def _simulate_response(self, prompt: str, mode: ReasoningMode) -> str:
        """模拟API响应（用于测试）"""
        response_templates = {
            ReasoningMode.NON_THINKING: "基于内部推理，直接回答：{answer}",
            ReasoningMode.SIMPLIFIED: "简化推理过程：\n1. 分析问题\n2. 核心步骤\n3. 得出结论：{answer}",
            ReasoningMode.FULL_THINKING: "详细推理过程：\n1. 问题分析：...\n2. 解决思路：...\n3. 详细步骤：...\n4. 验证检查：...\n5. 最终答案：{answer}"
        }

        template = response_templates.get(mode, "默认回答：{answer}")
        return template.format(answer="[模拟回答内容]")


class EnhancedReasoningExecutor(ReasoningExecutor):
    """增强版推理执行器，支持真实LLM API"""

    def __init__(self, api_client: LLMAPIClient):
        super().__init__()
        self.api_client = api_client

    async def execute_reasoning_async(self, task_text: str, mode: ReasoningMode,
                                     features: TaskFeatures) -> str:
        """异步执行推理"""
        prompt = self.prompts[mode](task_text, features)
        response = await self.api_client.generate_response(prompt, mode)
        return response

    def execute_reasoning(self, task_text: str, mode: ReasoningMode,
                         features: TaskFeatures) -> str:
        """同步执行推理（兼容原接口）"""
        return asyncio.run(self.execute_reasoning_async(task_text, mode, features))


class ProductionAdaptiveReasoningSystem(AdaptiveReasoningSystem):
    """生产环境自适应推理系统"""

    def __init__(self, api_type: str = "openai", api_key: str = None, config: Dict[str, Any] = None):
        super().__init__()

        # 初始化LLM API客户端
        self.api_client = LLMAPIClient(api_type, api_key)

        # 使用增强版推理执行器
        self.reasoning_executor = EnhancedReasoningExecutor(self.api_client)

        # 加载配置
        self.config = config or {}
        self._load_config()

    def _load_config(self):
        """加载配置参数"""
        # 可以从配置文件或环境变量加载阈值等参数
        thresholds = self.config.get("thresholds", {})
        if thresholds:
            self.complexity_evaluator.mode_thresholds.update(thresholds)

    async def process_task_async(self, task_text: str, task_id: Optional[str] = None):
        """异步处理任务"""
        import time

        start_time = time.time()

        if task_id is None:
            task_id = f"task_{int(time.time() * 1000)}"

        # 1. 分析任务特征
        features = self.task_analyzer.analyze_task(task_text)

        # 2. 选择推理模式
        reasoning_mode = self.complexity_evaluator.evaluate_reasoning_mode(features)
        confidence_score = self.complexity_evaluator.get_confidence_score(features, reasoning_mode)

        # 3. 异步执行推理
        response = await self.reasoning_executor.execute_reasoning_async(
            task_text, reasoning_mode, features
        )

        execution_time = time.time() - start_time

        # 4. 更新统计信息
        self._update_stats(features.task_type, reasoning_mode, execution_time)

        # 5. 构造结果
        from adaptive_reasoning_system import ReasoningResult
        result = ReasoningResult(
            task_id=task_id,
            reasoning_mode=reasoning_mode,
            response=response,
            execution_time=execution_time,
            confidence_score=confidence_score,
            metadata={
                'features': features,
                'complexity_score': features.complexity_score,
                'task_type': features.task_type.value
            }
        )

        return result

    async def batch_process_async(self, tasks: list):
        """异步批量处理任务"""
        # 使用asyncio.gather并发处理任务
        coroutines = []

        for i, task_info in enumerate(tasks):
            task_text = task_info.get('text', task_info.get('task', ''))
            task_id = task_info.get('id', f"batch_task_{i}")
            coroutines.append(self.process_task_async(task_text, task_id))

        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                from adaptive_reasoning_system import ReasoningResult
                error_result = ReasoningResult(
                    task_id=tasks[i].get('id', f"batch_task_{i}"),
                    reasoning_mode=ReasoningMode.NON_THINKING,
                    response=f"错误: {str(result)}",
                    execution_time=0.0,
                    confidence_score=0.0,
                    metadata={'error': str(result)}
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)

        return processed_results

    def save_config(self, filename: str = "system_config.json"):
        """保存系统配置"""
        config_data = {
            "api_type": self.api_client.api_type,
            "thresholds": self.complexity_evaluator.mode_thresholds,
            "stats": self.stats
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)

        print(f"配置已保存到: {filename}")

    @classmethod
    def load_from_config(cls, filename: str = "system_config.json"):
        """从配置文件加载系统"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            api_type = config_data.get("api_type", "openai")
            system = cls(api_type=api_type, config=config_data)

            print(f"从配置文件 {filename} 加载系统成功")
            return system

        except FileNotFoundError:
            print(f"配置文件 {filename} 不存在，使用默认配置")
            return cls()
        except Exception as e:
            print(f"加载配置文件失败: {e}，使用默认配置")
            return cls()


async def demo_production_system():
    """演示生产环境系统"""

    print("=== 生产环境自适应推理系统演示 ===\n")

    # 初始化系统（使用模拟API）
    system = ProductionAdaptiveReasoningSystem(api_type="simulation")

    # 测试任务
    demo_tasks = [
        {
            "id": "prod_test_1",
            "text": "请编写一个Python函数计算两个数的最大公约数"
        },
        {
            "id": "prod_test_2",
            "text": "证明：平方根2是无理数，并详细说明证明过程"
        },
        {
            "id": "prod_test_3",
            "text": "什么是递归？"
        }
    ]

    print("单任务处理演示:")
    for task in demo_tasks:
        print(f"\n处理任务: {task['text'][:50]}...")
        result = await system.process_task_async(task['text'], task['id'])
        print(f"推理模式: {result.reasoning_mode.value}")
        print(f"执行时间: {result.execution_time:.3f}秒")
        print(f"响应预览: {result.response[:100]}...")

    print(f"\n" + "="*50)
    print("批量处理演示:")

    batch_tasks = [
        {"id": "batch_1", "text": "1+1=?"},
        {"id": "batch_2", "text": "设计一个高并发的Web服务器架构"},
        {"id": "batch_3", "text": "解释什么是深度学习"},
        {"id": "batch_4", "text": "证明勾股定理"}
    ]

    batch_results = await system.batch_process_async(batch_tasks)

    print(f"批量处理完成，共处理 {len(batch_results)} 个任务")

    for result in batch_results:
        print(f"任务 {result.task_id}: {result.reasoning_mode.value} "
              f"({result.execution_time:.3f}s)")

    # 显示统计信息
    print(f"\n=== 系统统计 ===")
    stats = system.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

    # 保存配置
    system.save_config("demo_config.json")


def create_web_api_example():
    """创建Web API示例"""

    web_api_code = '''
from flask import Flask, request, jsonify
import asyncio
from llm_integration_example import ProductionAdaptiveReasoningSystem

app = Flask(__name__)

# 初始化全局系统实例
reasoning_system = ProductionAdaptiveReasoningSystem.load_from_config()

@app.route('/api/reason', methods=['POST'])
def reason_endpoint():
    """推理API端点"""
    try:
        data = request.get_json()
        task_text = data.get('task', '')
        task_id = data.get('task_id')

        if not task_text:
            return jsonify({"error": "缺少task参数"}), 400

        # 同步处理
        result = reasoning_system.process_task(task_text, task_id)

        return jsonify({
            "task_id": result.task_id,
            "reasoning_mode": result.reasoning_mode.value,
            "response": result.response,
            "execution_time": result.execution_time,
            "confidence_score": result.confidence_score,
            "metadata": result.metadata
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/batch_reason', methods=['POST'])
def batch_reason_endpoint():
    """批量推理API端点"""
    try:
        data = request.get_json()
        tasks = data.get('tasks', [])

        if not tasks:
            return jsonify({"error": "缺少tasks参数"}), 400

        # 异步批量处理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            reasoning_system.batch_process_async(tasks)
        )
        loop.close()

        # 序列化结果
        response_data = []
        for result in results:
            response_data.append({
                "task_id": result.task_id,
                "reasoning_mode": result.reasoning_mode.value,
                "response": result.response,
                "execution_time": result.execution_time,
                "confidence_score": result.confidence_score
            })

        return jsonify({"results": response_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def stats_endpoint():
    """统计信息API端点"""
    stats = reasoning_system.get_statistics()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

    with open("/home/lmxxf/work/web_api_example.py", 'w', encoding='utf-8') as f:
        f.write(web_api_code)

    print("Web API示例已创建: web_api_example.py")

    # 创建API使用说明
    api_docs = '''
# 自适应推理系统 Web API 使用说明

## 启动服务
```bash
python web_api_example.py
```

## API端点

### 1. 单任务推理
**POST** `/api/reason`

请求体:
```json
{
    "task": "请编写一个Python函数计算斐波那契数列",
    "task_id": "optional_task_id"
}
```

响应:
```json
{
    "task_id": "task_12345",
    "reasoning_mode": "non_thinking",
    "response": "生成的回答内容",
    "execution_time": 0.234,
    "confidence_score": 0.85,
    "metadata": {...}
}
```

### 2. 批量任务推理
**POST** `/api/batch_reason`

请求体:
```json
{
    "tasks": [
        {"id": "task1", "text": "什么是机器学习？"},
        {"id": "task2", "text": "证明1+1=2"}
    ]
}
```

### 3. 系统统计
**GET** `/api/stats`

## 使用示例

```bash
# 单任务请求
curl -X POST http://localhost:5000/api/reason \\
  -H "Content-Type: application/json" \\
  -d '{"task": "解释什么是人工智能"}'

# 批量任务请求
curl -X POST http://localhost:5000/api/batch_reason \\
  -H "Content-Type: application/json" \\
  -d '{"tasks": [{"id": "1", "text": "1+1=?"}, {"id": "2", "text": "什么是深度学习？"}]}'

# 获取统计信息
curl http://localhost:5000/api/stats
```
'''

    with open("/home/lmxxf/work/API_USAGE.md", 'w', encoding='utf-8') as f:
        f.write(api_docs)

    print("API使用说明已创建: API_USAGE.md")


if __name__ == "__main__":
    print("LLM集成示例")
    print("展示如何将自适应推理系统与真实LLM API集成")
    print("=" * 60)

    # 运行演示
    asyncio.run(demo_production_system())

    # 创建Web API示例
    print("\n创建Web API示例...")
    create_web_api_example()

    print("\n集成示例创建完成！")
    print("\n下一步:")
    print("1. 安装依赖: pip install openai flask")
    print("2. 设置API密钥: export LLM_API_KEY='your_api_key'")
    print("3. 运行Web API: python web_api_example.py")