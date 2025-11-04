#!/usr/bin/env python3
"""
自适应推理系统测试用例和示例
基于DeepSeek-V3实验数据验证系统性能
"""

import json
import time
from adaptive_reasoning_system import (
    AdaptiveReasoningSystem, ReasoningMode, TaskType
)


def run_deepseek_validation_tests():
    """运行基于DeepSeek-V3数据的验证测试"""

    system = AdaptiveReasoningSystem()

    # 基于论文中的实验数据构造测试用例
    test_cases = [
        # 编程任务（应该优选非思考模式）
        {
            "id": "codeforces_1",
            "text": "编写一个Python函数，实现快速排序算法",
            "expected_mode": ReasoningMode.NON_THINKING,
            "category": "编程-算法实现"
        },
        {
            "id": "codeforces_2",
            "text": "给定一个整数数组，找出其中没有重复元素的最长子数组的长度",
            "expected_mode": ReasoningMode.NON_THINKING,
            "category": "编程-数据结构"
        },
        {
            "id": "codeforces_3",
            "text": "实现一个LRU缓存类，支持get和put操作",
            "expected_mode": ReasoningMode.SIMPLIFIED,  # 稍复杂的设计
            "category": "编程-系统设计"
        },

        # 数学推理任务（应该优选完整思考模式）
        {
            "id": "hmmt_1",
            "text": "证明：对于任意正整数n，1+2+3+...+n = n(n+1)/2",
            "expected_mode": ReasoningMode.FULL_THINKING,
            "category": "数学-证明"
        },
        {
            "id": "hmmt_2",
            "text": "求解方程组：x²+y²=25, x+y=7，并验证所有解",
            "expected_mode": ReasoningMode.FULL_THINKING,
            "category": "数学-方程求解"
        },
        {
            "id": "hmmt_3",
            "text": "计算定积分∫[0,π] sin(x)dx的值",
            "expected_mode": ReasoningMode.SIMPLIFIED,  # 标准积分
            "category": "数学-积分计算"
        },

        # 简单问答（应该使用非思考模式）
        {
            "id": "qa_1",
            "text": "什么是机器学习？",
            "expected_mode": ReasoningMode.NON_THINKING,
            "category": "简单问答"
        },
        {
            "id": "qa_2",
            "text": "请列出Python的基本数据类型",
            "expected_mode": ReasoningMode.NON_THINKING,
            "category": "简单问答"
        },

        # 复杂推理任务
        {
            "id": "complex_1",
            "text": "分析深度学习中梯度消失问题的成因，并提出三种解决方案",
            "expected_mode": ReasoningMode.FULL_THINKING,
            "category": "复杂推理"
        },
        {
            "id": "complex_2",
            "text": "设计一个分布式系统架构来处理每秒100万次请求",
            "expected_mode": ReasoningMode.SIMPLIFIED,
            "category": "系统设计"
        }
    ]

    print("=== DeepSeek-V3 验证测试开始 ===\n")

    correct_predictions = 0
    total_tests = len(test_cases)
    results = []

    for test_case in test_cases:
        result = system.process_task(test_case["text"], test_case["id"])

        # 检查模式预测是否正确
        is_correct = result.reasoning_mode == test_case["expected_mode"]
        if is_correct:
            correct_predictions += 1

        results.append({
            "test_case": test_case,
            "result": result,
            "is_correct": is_correct
        })

        print(f"测试用例: {test_case['id']} ({test_case['category']})")
        print(f"任务: {test_case['text'][:50]}...")
        print(f"期望模式: {test_case['expected_mode'].value}")
        print(f"实际模式: {result.reasoning_mode.value}")
        print(f"预测正确: {'✓' if is_correct else '✗'}")
        print(f"置信度: {result.confidence_score:.3f}")
        print(f"复杂度分数: {result.metadata['complexity_score']:.1f}")
        print("-" * 60)

    accuracy = correct_predictions / total_tests
    print(f"\n=== 验证结果汇总 ===")
    print(f"总测试用例: {total_tests}")
    print(f"预测正确: {correct_predictions}")
    print(f"准确率: {accuracy:.2%}")

    # 按类别统计
    category_stats = {}
    for r in results:
        category = r["test_case"]["category"]
        if category not in category_stats:
            category_stats[category] = {"correct": 0, "total": 0}
        category_stats[category]["total"] += 1
        if r["is_correct"]:
            category_stats[category]["correct"] += 1

    print(f"\n=== 按类别统计 ===")
    for category, stats in category_stats.items():
        acc = stats["correct"] / stats["total"]
        print(f"{category}: {stats['correct']}/{stats['total']} ({acc:.2%})")

    return results


def run_performance_benchmark():
    """运行性能基准测试"""

    system = AdaptiveReasoningSystem()

    # 生成不同复杂度的测试任务
    benchmark_tasks = []

    # 简单任务 (应该用非思考模式，节省时间)
    simple_tasks = [
        "1+1等于多少？",
        "Python中如何创建列表？",
        "什么是HTTP协议？",
        "列出常见的排序算法",
        "解释什么是递归"
    ]

    # 中等任务 (应该用简化模式)
    medium_tasks = [
        "编写冒泡排序算法并分析时间复杂度",
        "设计一个简单的购物车类",
        "计算斐波那契数列的第20项",
        "解释面向对象编程的三大特性",
        "比较BFS和DFS算法的优缺点"
    ]

    # 复杂任务 (应该用完整思考模式)
    complex_tasks = [
        "证明哥德巴赫猜想对于小于100的所有偶数成立",
        "设计一个支持事务的分布式数据库系统",
        "分析Transformer架构的注意力机制原理",
        "推导反向传播算法的数学公式",
        "设计一个大规模推荐系统的完整架构"
    ]

    # 构造基准测试集
    task_id = 1
    for task_list, complexity_label in [
        (simple_tasks, "简单"),
        (medium_tasks, "中等"),
        (complex_tasks, "复杂")
    ]:
        for task_text in task_list:
            benchmark_tasks.append({
                "id": f"benchmark_{task_id}",
                "text": task_text,
                "complexity_label": complexity_label
            })
            task_id += 1

    print("=== 性能基准测试开始 ===\n")

    start_time = time.time()
    results = system.batch_process(benchmark_tasks)
    total_time = time.time() - start_time

    # 统计分析
    mode_usage = {mode.value: 0 for mode in ReasoningMode}
    complexity_stats = {}

    for i, result in enumerate(results):
        mode_usage[result.reasoning_mode.value] += 1

        complexity_label = benchmark_tasks[i]["complexity_label"]
        if complexity_label not in complexity_stats:
            complexity_stats[complexity_label] = {
                "count": 0,
                "avg_time": 0,
                "modes": {mode.value: 0 for mode in ReasoningMode}
            }

        stats = complexity_stats[complexity_label]
        stats["count"] += 1
        stats["avg_time"] = (stats["avg_time"] * (stats["count"] - 1) + result.execution_time) / stats["count"]
        stats["modes"][result.reasoning_mode.value] += 1

    print(f"总耗时: {total_time:.3f}秒")
    print(f"平均每任务: {total_time/len(results):.3f}秒")
    print(f"总任务数: {len(results)}")

    print(f"\n=== 推理模式使用统计 ===")
    for mode, count in mode_usage.items():
        percentage = count / len(results) * 100
        print(f"{mode}: {count} ({percentage:.1f}%)")

    print(f"\n=== 按复杂度统计 ===")
    for complexity, stats in complexity_stats.items():
        print(f"\n{complexity}任务:")
        print(f"  数量: {stats['count']}")
        print(f"  平均耗时: {stats['avg_time']:.3f}秒")
        print(f"  模式分布: ", end="")
        for mode, count in stats['modes'].items():
            if count > 0:
                print(f"{mode}:{count} ", end="")
        print()

    return results


def run_adaptive_optimization_demo():
    """运行自适应优化演示"""

    system = AdaptiveReasoningSystem()

    print("=== 自适应优化演示 ===\n")

    # 演示相同问题在不同表述下的处理差异
    similar_tasks = [
        {
            "text": "写一个排序函数",
            "description": "简单请求 - 应该用非思考模式"
        },
        {
            "text": "请详细分析各种排序算法的时间复杂度和空间复杂度，并给出最优选择建议",
            "description": "复杂分析 - 应该用完整思考模式"
        },
        {
            "text": "实现快速排序并简单说明原理",
            "description": "中等复杂度 - 应该用简化模式"
        }
    ]

    for i, task in enumerate(similar_tasks, 1):
        print(f"示例 {i}: {task['description']}")
        print(f"任务: {task['text']}")

        result = system.process_task(task["text"], f"demo_{i}")

        print(f"选择模式: {result.reasoning_mode.value}")
        print(f"复杂度分数: {result.metadata['complexity_score']:.1f}")
        print(f"置信度: {result.confidence_score:.3f}")
        print(f"执行时间: {result.execution_time:.3f}秒")
        print(f"任务类型: {result.metadata['task_type']}")
        print("-" * 50)

    # 显示系统统计
    stats = system.get_statistics()
    print(f"\n=== 系统运行统计 ===")
    for key, value in stats.items():
        print(f"{key}: {value}")


def export_test_results(results, filename="test_results.json"):
    """导出测试结果到JSON文件"""

    export_data = []
    for result_item in results:
        if isinstance(result_item, dict) and "result" in result_item:
            # 验证测试结果
            export_data.append({
                "test_id": result_item["result"].task_id,
                "category": result_item["test_case"]["category"],
                "task_text": result_item["test_case"]["text"],
                "expected_mode": result_item["test_case"]["expected_mode"].value,
                "actual_mode": result_item["result"].reasoning_mode.value,
                "is_correct": result_item["is_correct"],
                "confidence_score": result_item["result"].confidence_score,
                "execution_time": result_item["result"].execution_time,
                "complexity_score": result_item["result"].metadata["complexity_score"]
            })
        else:
            # 基准测试结果
            export_data.append({
                "test_id": result_item.task_id,
                "reasoning_mode": result_item.reasoning_mode.value,
                "execution_time": result_item.execution_time,
                "confidence_score": result_item.confidence_score,
                "complexity_score": result_item.metadata["complexity_score"],
                "task_type": result_item.metadata["task_type"]
            })

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"测试结果已导出到: {filename}")


if __name__ == "__main__":
    print("自适应推理系统测试套件")
    print("基于《大语言模型的内部推理与外部输出差异性研究》")
    print("=" * 60)

    # 运行所有测试
    print("\n1. 运行DeepSeek-V3验证测试...")
    validation_results = run_deepseek_validation_tests()

    print("\n2. 运行性能基准测试...")
    benchmark_results = run_performance_benchmark()

    print("\n3. 运行自适应优化演示...")
    run_adaptive_optimization_demo()

    # 导出结果
    print("\n4. 导出测试结果...")
    export_test_results(validation_results, "validation_results.json")
    export_test_results(benchmark_results, "benchmark_results.json")

    print("\n测试完成！")