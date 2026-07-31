"""
LLM 语义分析模块
调用大语言模型解析用户的问题描述，提取数学意图和结构化信息

输出结构化 JSON：
- problem_type: 问题分类
- mathematical_intent: 数学意图
- key_entities: 关键实体（变量、函数、矩阵等）
- constraints: 约束条件
- suggested_category: 建议的算法大类
"""

import json
import os
import re
from typing import Optional

from src.core.algorithm_kb import CATEGORIES, match_keywords, KEYWORD_TO_ALGORITHMS


# ============================================================================
# LLM 调用
# ============================================================================

def _build_system_prompt() -> str:
    """构建系统提示词"""
    categories_desc = "\n".join([
        f"- {info['icon']} {name}: {info['description']}"
        for name, info in CATEGORIES.items()
    ])

    return f"""你是一个数值分析专家系统。分析用户描述的数学问题，输出结构化JSON。

## 可识别的问题类型：
{categories_desc}

## 输出格式（严格JSON，不要markdown包裹）：
{{
    "problem_type": "从上述分类中选择最匹配的一个",
    "mathematical_intent": "一句话概括用户想做什么数学运算",
    "key_entities": {{
        "variables": ["变量名列表"],
        "matrices": ["矩阵名列表"],
        "functions": ["函数名列表"],
        "parameters": ["参数列表"]
    }},
    "constraints": ["约束条件列表"],
    "suggested_category": "建议的算法大类",
    "confidence": 0.0-1.0,
    "reasoning": "简短推理过程"
}}

## 规则：
- 如果用户提到"拟合/回归/最小二乘"→ 曲线拟合
- 如果用户提到"插值/样条/过点"→ 插值与逼近
- 如果用户提到"积分/求积"→ 数值积分
- 如果用户提到"导数/梯度/微分"→ 数值微分
- 如果用户提到"方程组/线性/求解Ax"→ 线性方程组
- 如果用户提到"求根/f(x)=0/二分/牛顿"→ 非线性方程
- 如果用户提到"特征值/特征向量/谱"→ 特征值问题
- 如果用户提到"ODE/微分方程/初值"→ 常微分方程
"""


def _build_user_prompt(description: str, has_data: bool, data_summary: str = "") -> str:
    """构建用户提示词"""
    prompt = f"分析以下数学问题：\n\n{description}"

    if has_data and data_summary:
        prompt += f"\n\n## 上传数据概况\n{data_summary}"

    prompt += "\n\n请输出结构化JSON分析结果。"
    return prompt


def call_llm_for_semantic_analysis(
    description: str,
    has_data: bool = False,
    data_summary: str = "",
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
) -> dict:
    """
    调用 LLM 进行语义分析

    Args:
        description: 用户问题描述
        has_data: 是否有上传数据
        data_summary: 数据摘要文本
        model: 模型名称
        api_key: API Key
        api_base: API Base URL

    Returns:
        dict: 结构化分析结果
    """
    # 优先用参数，其次环境变量
    api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
    api_base = api_base or os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")

    if not api_key:
        # 无 API Key 时回退到关键词规则引擎
        return _fallback_keyword_analysis(description)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key, base_url=api_base)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _build_system_prompt()},
                {"role": "user", "content": _build_user_prompt(description, has_data, data_summary)},
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        content = response.choices[0].message.content.strip()

        # 尝试解析 JSON
        result = _parse_llm_json(content)

        # 合并关键词匹配结果
        keyword_algs = match_keywords(description)
        if keyword_algs:
            result["keyword_matched_algorithms"] = keyword_algs

        result["llm_raw_response"] = content
        result["analysis_method"] = "llm"

        return result

    except Exception as e:
        # LLM 调用失败，回退到规则引擎
        fallback = _fallback_keyword_analysis(description)
        fallback["llm_error"] = str(e)
        fallback["analysis_method"] = "fallback_keyword"
        return fallback


def _parse_llm_json(content: str) -> dict:
    """解析 LLM 返回的 JSON"""
    # 去除可能的 markdown 代码块标记
    content = re.sub(r'^```(?:json)?\s*', '', content.strip())
    content = re.sub(r'\s*```$', '', content.strip())

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # 尝试提取 JSON 子串
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return {
            "problem_type": "未知",
            "mathematical_intent": content[:200],
            "key_entities": {},
            "constraints": [],
            "suggested_category": "未知",
            "confidence": 0.0,
            "reasoning": "LLM 返回格式异常",
            "parse_error": True,
        }


# ============================================================================
# 关键词规则引擎（回退方案）
# ============================================================================

def _fallback_keyword_analysis(description: str) -> dict:
    """
    基于关键词匹配的语义分析（不需要 LLM API）
    作为 LLM 不可用时的回退方案
    """
    text = description.lower()

    # 问题类型判定
    type_scores = {}
    if any(kw in text for kw in ["插值", "样条", "过点", "通过.*点"]):
        type_scores["插值与逼近"] = 3
    if any(kw in text for kw in ["拟合", "最小二乘", "回归", "残差"]):
        type_scores["曲线拟合"] = 3
    if any(kw in text for kw in ["积分", "求积", "辛普森", "梯形"]):
        type_scores["数值积分"] = 3
    if any(kw in text for kw in ["导数", "微分", "梯度"]):
        type_scores["数值微分"] = 2
    if any(kw in text for kw in ["线性方程", "方程组", "Ax", "矩阵求解"]):
        type_scores["线性方程组"] = 3
    if any(kw in text for kw in ["求根", "f(x)=0", "二分", "牛顿", "不动点"]):
        type_scores["非线性方程"] = 3
    if any(kw in text for kw in ["特征值", "特征向量", "谱"]):
        type_scores["特征值问题"] = 3
    if any(kw in text for kw in ["ode", "微分方程", "初值", "龙格库塔"]):
        type_scores["常微分方程"] = 3

    # 选得分最高的
    if type_scores:
        problem_type = max(type_scores, key=type_scores.get)
    else:
        problem_type = "数值计算"

    # 关键词匹配算法
    keyword_algs = match_keywords(description)

    return {
        "problem_type": problem_type,
        "mathematical_intent": f"对问题进行{problem_type}分析",
        "key_entities": {},
        "constraints": [],
        "suggested_category": problem_type,
        "confidence": min(0.7, len(keyword_algs) * 0.1),
        "reasoning": f"基于关键词规则匹配，命中 {len(keyword_algs)} 个算法候选",
        "keyword_matched_algorithms": keyword_algs,
        "analysis_method": "keyword_rules",
    }
