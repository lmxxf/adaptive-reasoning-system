#!/usr/bin/env python3
"""
大语言模型自适应推理系统
基于《大语言模型的内部推理与外部输出差异性研究》论文实现

核心理论：
- 内部推理过程 ≠ 外部输出内容
- 内部推理：基于Transformer并行计算，是"并行的、瞬间的"
- 外部输出：基于串行token生成，是"串行的、逐步的"
- 思维链是"事后构造"的解释性叙述，而非真实推理过程

作者：Research Team
单位：AI Research Institute
"""

import re
import json
import time
import logging
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ReasoningMode(Enum):
    """推理模式枚举"""
    NON_THINKING = "non_thinking"      # 非思考模式
    SIMPLIFIED = "simplified"          # 简化思考模式
    FULL_THINKING = "full_thinking"    # 完整思考模式


class TaskType(Enum):
    """任务类型枚举"""
    PROGRAMMING = "programming"        # 编程任务
    MATH_REASONING = "math_reasoning"  # 数学推理
    SIMPLE_QA = "simple_qa"           # 简单问答
    COMPLEX_REASONING = "complex_reasoning"  # 复杂推理
    ALGORITHM_DESIGN = "algorithm_design"    # 算法设计
    UNKNOWN = "unknown"               # 未知类型


@dataclass
class TaskFeatures:
    """任务特征"""
    contains_code: bool = False        # 是否包含代码
    contains_math: bool = False        # 是否包含数学符号
    complexity_score: float = 0.0     # 复杂度分数 (0-100)
    requires_verification: bool = False # 是否需要逐步验证
    task_type: TaskType = TaskType.UNKNOWN
    keywords_count: Dict[str, int] = None

    def __post_init__(self):
        if self.keywords_count is None:
            self.keywords_count = {}


@dataclass
class ReasoningResult:
    """推理结果"""
    task_id: str
    reasoning_mode: ReasoningMode
    response: str
    execution_time: float
    confidence_score: float
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TaskAnalyzer:
    """任务特征分析器"""

    def __init__(self):
        # 编程相关关键词
        self.programming_keywords = {
            'function', 'class', 'def', 'import', 'return', 'if', 'else', 'for', 'while',
            'try', 'except', 'print', 'input', 'list', 'dict', 'array', 'variable',
            'algorithm', 'code', 'program', 'script', 'debug', 'compile', 'execute',
            '函数', '类', '变量', '算法', '代码', '程序', '脚本', '调试', '编译', '执行'
        }

        # 数学相关关键词
        self.math_keywords = {
            'equation', 'formula', 'calculate', 'solve', 'proof', 'theorem', 'derivative',
            'integral', 'matrix', 'vector', 'probability', 'statistics', 'geometry',
            '方程', '公式', '计算', '求解', '证明', '定理', '导数', '积分', '矩阵', '向量',
            '概率', '统计', '几何'
        }

        # 需要验证的关键词
        self.verification_keywords = {
            'prove', 'verify', 'check', 'validate', 'confirm', 'ensure', 'step by step',
            'reasoning', 'logic', 'analysis', 'derivation',
            '证明', '验证', '检查', '确认', '逐步', '推理', '逻辑', '分析', '推导'
        }

    def analyze_task(self, task_text: str) -> TaskFeatures:
        """分析任务特征"""
        task_text_lower = task_text.lower()

        # 检测是否包含代码
        contains_code = self._detect_code(task_text)

        # 检测是否包含数学符号
        contains_math = self._detect_math(task_text)

        # 统计关键词
        programming_count = sum(1 for keyword in self.programming_keywords
                               if keyword in task_text_lower)
        math_count = sum(1 for keyword in self.math_keywords
                        if keyword in task_text_lower)
        verification_count = sum(1 for keyword in self.verification_keywords
                               if keyword in task_text_lower)

        # 计算复杂度分数
        complexity_score = self._calculate_complexity(
            task_text, programming_count, math_count, verification_count
        )

        # 判断是否需要验证
        requires_verification = (verification_count > 0 or
                               math_count > programming_count or
                               '步骤' in task_text or 'step' in task_text_lower)

        # 确定任务类型
        task_type = self._determine_task_type(
            programming_count, math_count, verification_count, contains_code
        )

        return TaskFeatures(
            contains_code=contains_code,
            contains_math=contains_math,
            complexity_score=complexity_score,
            requires_verification=requires_verification,
            task_type=task_type,
            keywords_count={
                'programming': programming_count,
                'math': math_count,
                'verification': verification_count
            }
        )

    def _detect_code(self, text: str) -> bool:
        """检测是否包含代码"""
        code_patterns = [
            r'```[\s\S]*?```',  # 代码块
            r'`[^`]+`',         # 内联代码
            r'def\s+\w+\s*\(',  # Python函数定义
            r'function\s+\w+',  # JavaScript函数
            r'class\s+\w+',     # 类定义
            r'#include\s*<',    # C/C++头文件
            r'import\s+\w+',    # import语句
        ]

        for pattern in code_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _detect_math(self, text: str) -> bool:
        """检测是否包含数学符号"""
        math_patterns = [
            r'\$.*?\$',         # LaTeX数学公式
            r'\\[a-zA-Z]+',     # LaTeX命令
            r'[∑∏∫∆∇]',        # 数学符号
            r'\b\d+\s*[+\-*/]\s*\d+',  # 算术表达式
            r'[=<>≤≥≠]',       # 比较符号
            r'[∈∉⊂⊃∩∪]',      # 集合符号
        ]

        for pattern in math_patterns:
            if re.search(pattern, text):
                return True
        return False

    def _calculate_complexity(self, text: str, prog_count: int,
                            math_count: int, verif_count: int) -> float:
        """计算任务复杂度分数 (0-100)"""
        base_score = min(len(text) / 50, 50)  # 基于文本长度，最高50分

        # 关键词加权
        keyword_score = (prog_count * 2 + math_count * 3 + verif_count * 4)
        keyword_score = min(keyword_score, 30)  # 最高30分

        # 特殊模式加权
        special_score = 0
        if '证明' in text or 'prove' in text.lower():
            special_score += 15
        if '算法' in text or 'algorithm' in text.lower():
            special_score += 10
        if '优化' in text or 'optimize' in text.lower():
            special_score += 10

        special_score = min(special_score, 20)  # 最高20分

        total_score = base_score + keyword_score + special_score
        return min(total_score, 100)

    def _determine_task_type(self, prog_count: int, math_count: int,
                           verif_count: int, contains_code: bool) -> TaskType:
        """确定任务类型"""
        if contains_code or prog_count > math_count + verif_count:
            if prog_count > 3 or '算法' in str(prog_count):
                return TaskType.ALGORITHM_DESIGN
            return TaskType.PROGRAMMING

        if math_count > 0 and verif_count > 0:
            return TaskType.MATH_REASONING

        if verif_count > 2 or math_count > 3:
            return TaskType.COMPLEX_REASONING

        if prog_count + math_count + verif_count <= 2:
            return TaskType.SIMPLE_QA

        return TaskType.UNKNOWN


class ComplexityEvaluator:
    """复杂度评估模块"""

    def __init__(self):
        # 基于DeepSeek-V3实验数据的权重配置
        self.mode_thresholds = {
            'non_thinking_max': 30,      # 非思考模式最大复杂度
            'simplified_min': 25,        # 简化模式最小复杂度
            'simplified_max': 70,        # 简化模式最大复杂度
            'full_thinking_min': 65      # 完整思考模式最小复杂度
        }

    def evaluate_reasoning_mode(self, features: TaskFeatures) -> ReasoningMode:
        """基于任务特征评估推理模式"""
        complexity = features.complexity_score

        # 特殊规则：基于论文发现
        if features.task_type == TaskType.PROGRAMMING:
            # 编程任务：内部推理足够强，避免思维链干扰
            if complexity <= 40:
                return ReasoningMode.NON_THINKING
            else:
                return ReasoningMode.SIMPLIFIED

        if features.task_type == TaskType.MATH_REASONING:
            # 数学推理：需要逐步验证，保留思维链
            if complexity >= 50:
                return ReasoningMode.FULL_THINKING
            else:
                return ReasoningMode.SIMPLIFIED

        # 基于复杂度的通用规则
        if complexity <= self.mode_thresholds['non_thinking_max']:
            return ReasoningMode.NON_THINKING
        elif complexity <= self.mode_thresholds['simplified_max']:
            return ReasoningMode.SIMPLIFIED
        else:
            return ReasoningMode.FULL_THINKING

    def get_confidence_score(self, features: TaskFeatures,
                           selected_mode: ReasoningMode) -> float:
        """计算选择模式的置信度分数"""
        complexity = features.complexity_score
        base_confidence = 0.7

        # 基于任务类型的置信度调整
        if features.task_type == TaskType.PROGRAMMING and selected_mode == ReasoningMode.NON_THINKING:
            base_confidence += 0.2
        elif features.task_type == TaskType.MATH_REASONING and selected_mode == ReasoningMode.FULL_THINKING:
            base_confidence += 0.2
        elif features.task_type == TaskType.SIMPLE_QA and selected_mode == ReasoningMode.NON_THINKING:
            base_confidence += 0.15

        # 基于复杂度的置信度调整
        if selected_mode == ReasoningMode.NON_THINKING and complexity > 40:
            base_confidence -= 0.1
        elif selected_mode == ReasoningMode.FULL_THINKING and complexity < 30:
            base_confidence -= 0.1

        return min(max(base_confidence, 0.1), 1.0)


class ReasoningExecutor:
    """推理执行引擎"""

    def __init__(self):
        self.prompts = {
            ReasoningMode.NON_THINKING: self._get_non_thinking_prompt,
            ReasoningMode.SIMPLIFIED: self._get_simplified_prompt,
            ReasoningMode.FULL_THINKING: self._get_full_thinking_prompt
        }

    def execute_reasoning(self, task_text: str, mode: ReasoningMode,
                         features: TaskFeatures) -> str:
        """执行推理"""
        prompt_generator = self.prompts[mode]
        prompt = prompt_generator(task_text, features)

        # 这里应该调用实际的LLM API
        # 为了演示，我们返回模拟响应
        return self._simulate_llm_response(prompt, mode, features)

    def _get_non_thinking_prompt(self, task_text: str, features: TaskFeatures) -> str:
        """非思考模式提示词"""
        return f"""请直接回答以下问题，不需要展示思考过程：

{task_text}

请直接给出答案："""

    def _get_simplified_prompt(self, task_text: str, features: TaskFeatures) -> str:
        """简化思考模式提示词"""
        return f"""请回答以下问题，只需要展示关键步骤：

{task_text}

请按以下格式回答：
关键步骤：[列出2-3个关键步骤]
答案：[最终答案]"""

    def _get_full_thinking_prompt(self, task_text: str, features: TaskFeatures) -> str:
        """完整思考模式提示词"""
        return f"""请详细回答以下问题，展示完整的思考过程：

{task_text}

请按以下格式回答：
1. 问题分析：[分析问题的要求和约束]
2. 解决思路：[详细的解决方案思路]
3. 详细步骤：[逐步的解决过程]
4. 验证检查：[检查答案的正确性]
5. 最终答案：[给出最终答案]"""

    def _simulate_llm_response(self, prompt: str, mode: ReasoningMode,
                              features: TaskFeatures) -> str:
        """模拟LLM响应（实际应用中应调用真实的LLM API）"""
        task_type = features.task_type.value
        complexity = features.complexity_score

        responses = {
            ReasoningMode.NON_THINKING: f"基于内部推理，针对{task_type}任务（复杂度:{complexity:.1f}），直接给出答案：[模拟答案]",
            ReasoningMode.SIMPLIFIED: f"针对{task_type}任务（复杂度:{complexity:.1f}）的简化推理：\n关键步骤：1) 分析 2) 计算 3) 验证\n答案：[模拟答案]",
            ReasoningMode.FULL_THINKING: f"针对{task_type}任务（复杂度:{complexity:.1f}）的完整推理：\n1. 问题分析：...\n2. 解决思路：...\n3. 详细步骤：...\n4. 验证检查：...\n5. 最终答案：[模拟答案]"
        }

        return responses[mode]


class AdaptiveReasoningSystem:
    """自适应推理系统主类"""

    def __init__(self):
        self.task_analyzer = TaskAnalyzer()
        self.complexity_evaluator = ComplexityEvaluator()
        self.reasoning_executor = ReasoningExecutor()
        self.stats = {
            'total_tasks': 0,
            'mode_usage': {mode.value: 0 for mode in ReasoningMode},
            'avg_execution_time': 0.0,
            'task_types': {task_type.value: 0 for task_type in TaskType}
        }

    def process_task(self, task_text: str, task_id: Optional[str] = None) -> ReasoningResult:
        """处理单个任务"""
        start_time = time.time()

        if task_id is None:
            task_id = f"task_{int(time.time() * 1000)}"

        logger.info(f"开始处理任务 {task_id}")

        # 1. 分析任务特征
        features = self.task_analyzer.analyze_task(task_text)
        logger.info(f"任务特征分析完成: {features.task_type.value}, 复杂度: {features.complexity_score:.1f}")

        # 2. 选择推理模式
        reasoning_mode = self.complexity_evaluator.evaluate_reasoning_mode(features)
        confidence_score = self.complexity_evaluator.get_confidence_score(features, reasoning_mode)
        logger.info(f"选择推理模式: {reasoning_mode.value}, 置信度: {confidence_score:.3f}")

        # 3. 执行推理
        response = self.reasoning_executor.execute_reasoning(task_text, reasoning_mode, features)

        execution_time = time.time() - start_time

        # 4. 更新统计信息
        self._update_stats(features.task_type, reasoning_mode, execution_time)

        # 5. 构造结果
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

        logger.info(f"任务 {task_id} 处理完成，耗时: {execution_time:.3f}秒")

        return result

    def batch_process(self, tasks: List[Dict[str, str]]) -> List[ReasoningResult]:
        """批量处理任务"""
        results = []

        logger.info(f"开始批量处理 {len(tasks)} 个任务")

        for i, task_info in enumerate(tasks):
            task_text = task_info.get('text', task_info.get('task', ''))
            task_id = task_info.get('id', f"batch_task_{i}")

            try:
                result = self.process_task(task_text, task_id)
                results.append(result)
            except Exception as e:
                logger.error(f"处理任务 {task_id} 时发生错误: {e}")
                # 创建错误结果
                error_result = ReasoningResult(
                    task_id=task_id,
                    reasoning_mode=ReasoningMode.NON_THINKING,
                    response=f"错误: {str(e)}",
                    execution_time=0.0,
                    confidence_score=0.0,
                    metadata={'error': str(e)}
                )
                results.append(error_result)

        logger.info(f"批量处理完成，成功处理 {len([r for r in results if 'error' not in r.metadata])} 个任务")

        return results

    def _update_stats(self, task_type: TaskType, reasoning_mode: ReasoningMode,
                     execution_time: float):
        """更新统计信息"""
        self.stats['total_tasks'] += 1
        self.stats['mode_usage'][reasoning_mode.value] += 1
        self.stats['task_types'][task_type.value] += 1

        # 更新平均执行时间
        total_time = self.stats['avg_execution_time'] * (self.stats['total_tasks'] - 1)
        self.stats['avg_execution_time'] = (total_time + execution_time) / self.stats['total_tasks']

    def get_statistics(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        if self.stats['total_tasks'] == 0:
            return {"message": "暂无统计数据"}

        return {
            "总任务数": self.stats['total_tasks'],
            "平均执行时间": f"{self.stats['avg_execution_time']:.3f}秒",
            "推理模式使用情况": {
                mode: f"{count} ({count/self.stats['total_tasks']*100:.1f}%)"
                for mode, count in self.stats['mode_usage'].items()
            },
            "任务类型分布": {
                task_type: f"{count} ({count/self.stats['total_tasks']*100:.1f}%)"
                for task_type, count in self.stats['task_types'].items()
                if count > 0
            }
        }

    def optimize_thresholds(self, feedback_data: List[Dict[str, Any]]):
        """基于反馈数据优化阈值（预留接口）"""
        # 这里可以实现基于历史表现数据的阈值优化算法
        logger.info("阈值优化功能待实现")
        pass


if __name__ == "__main__":
    # 系统测试
    system = AdaptiveReasoningSystem()

    # 测试用例
    test_cases = [
        {"id": "test_1", "text": "请编写一个Python函数，计算斐波那契数列的第n项"},
        {"id": "test_2", "text": "证明当n≥3时，费马小定理成立"},
        {"id": "test_3", "text": "什么是人工智能？"},
        {"id": "test_4", "text": "设计一个高效的排序算法，并分析其时间复杂度"},
        {"id": "test_5", "text": "求解方程组：x + y = 5, 2x - y = 1，并验证解的正确性"}
    ]

    print("=== 自适应推理系统测试 ===\n")

    # 批量处理测试
    results = system.batch_process(test_cases)

    # 显示结果
    for result in results:
        print(f"任务ID: {result.task_id}")
        print(f"推理模式: {result.reasoning_mode.value}")
        print(f"执行时间: {result.execution_time:.3f}秒")
        print(f"置信度: {result.confidence_score:.3f}")
        print(f"响应: {result.response}")
        print("-" * 50)

    # 显示统计信息
    print("\n=== 系统统计信息 ===")
    stats = system.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")