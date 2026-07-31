"""
分析流水线编排器
「提交分析」后的总调度器：串联语义分析 → 数据特征 → 决策树 → 结果汇总

将所有结果写入 st.session_state，供前端三个标签页消费
"""

import time
from typing import Optional

import pandas as pd
import streamlit as st

from src.core.semantic_analyzer import call_llm_for_semantic_analysis
from src.core.data_analyzer import analyze_data
from src.core.decision_engine import run_decision_tree
from src.core.algorithm_kb import CATEGORIES


def run_analysis_pipeline(
    description: str,
    df: Optional[pd.DataFrame] = None,
    latex_formula: str = "",
    problem_type_override: Optional[str] = None,
    llm_model: str = "gpt-4o-mini",
    llm_api_key: str = "",
    llm_api_base: str = "",
) -> dict:
    """
    执行完整的分析流水线

    Args:
        description: 用户问题描述
        df: 上传的数据 DataFrame
        latex_formula: 用户输入的 LaTeX 公式
        problem_type_override: 用户手动选择的问题类型（覆盖自动分类）
        llm_model: LLM 模型
        llm_api_key: API Key
        llm_api_base: API Base

    Returns:
        dict: 完整分析结果，写入 session_state
    """
    perf_stats = {}
    t_start = time.time()

    # 初始化进度
    progress = st.progress(0, "开始分析...")
    status = st.empty()

    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "description": description,
        "latex_formula": latex_formula,
        "has_data": df is not None and not df.empty,
    }

    # ---- 阶段 1：数据特征分析（本地计算，不依赖 LLM） ----
    status.text("📊 正在分析数据特征...")
    progress.progress(10)

    t1 = time.time()
    data_report = None
    if df is not None and not df.empty:
        data_report = analyze_data(df)
        results["data_report"] = data_report
        results["data_features"] = data_report  # 前端展示用
    perf_stats["data_analysis_ms"] = int((time.time() - t1) * 1000)

    progress.progress(30)

    # ---- 阶段 2：语义分析（LLM 调用） ----
    status.text("🧠 LLM 正在分析问题描述...")
    progress.progress(40)

    data_summary = ""
    if data_report:
        data_summary = (
            f"数据规模: {data_report['rows']}行×{data_report['cols']}列, "
            f"数值列: {data_report['structure']['numeric_count']}个, "
            f"稀疏度: {data_report['sparsity']['sparse_ratio']:.1%}, "
            f"缺失率: {data_report['quality']['missing_ratio']:.1%}"
        )

    t2 = time.time()
    semantic_result = call_llm_for_semantic_analysis(
        description=description,
        has_data=results["has_data"],
        data_summary=data_summary,
        latex_formula=latex_formula,
        model=llm_model,
        api_key=llm_api_key,
        api_base=llm_api_base,
    )
    perf_stats["semantic_analysis_ms"] = int((time.time() - t2) * 1000)

    # 验证语义分析结果
    semantic_result = _validate_semantic_result(semantic_result)
    results["semantic_result"] = semantic_result

    # 用户手动覆盖问题类型
    if problem_type_override:
        if problem_type_override in CATEGORIES:
            semantic_result["problem_type"] = problem_type_override
            semantic_result["suggested_category"] = problem_type_override
            semantic_result["user_overrode"] = True
            semantic_result["confidence"] = max(semantic_result.get("confidence", 0.5), 0.8)
            results["user_overrode_type"] = True
        else:
            results["override_warning"] = (
                f"手动选择的类型「{problem_type_override}」不在知识库中，"
                f"将使用 LLM 自动分类结果"
            )

    progress.progress(60)

    # ---- 阶段 3：决策树推理 ----
    status.text("🌳 决策树正在推理最优算法...")
    progress.progress(70)

    t3 = time.time()
    decision_result = run_decision_tree(
        semantic_result=semantic_result,
        data_report=data_report,
    )
    perf_stats["decision_tree_ms"] = int((time.time() - t3) * 1000)

    # 验证决策结果
    decision_result = _validate_decision_result(decision_result)
    results["decision_result"] = decision_result

    progress.progress(90)

    # ---- 阶段 4：写入 session_state ----
    status.text("📋 正在汇总结果...")

    perf_stats["total_ms"] = int((time.time() - t_start) * 1000)
    results["perf_stats"] = perf_stats

    st.session_state["analysis_result"] = results
    st.session_state["analysis_completed"] = True

    progress.progress(100)
    status.text(f"✅ 分析完成！（耗时 {perf_stats['total_ms']}ms）")
    time.sleep(0.5)
    status.empty()
    progress.empty()

    return results


def _validate_semantic_result(result: dict) -> dict:
    """验证语义分析结果的必要字段"""
    required_fields = {
        "problem_type": "数值计算",
        "mathematical_intent": "未能解析数学意图",
        "suggested_category": "数值计算",
        "confidence": 0.0,
        "constraints": [],
        "key_entities": {},
        "keyword_matched_algorithms": [],
    }
    for field, default in required_fields.items():
        if field not in result:
            result[field] = default
    # 确保 confidence 在 0-1 范围内
    result["confidence"] = max(0.0, min(1.0, float(result.get("confidence", 0.5))))
    return result


def _validate_decision_result(result: dict) -> dict:
    """验证决策结果的必要字段"""
    if not result.get("decision_path"):
        result["decision_path"] = [{
            "step": "错误",
            "decision": "决策路径生成失败，请检查输入",
            "source": "系统",
        }]
    if not result.get("candidates"):
        result["confidence"] = 0.0
    if not result.get("problem_category"):
        result["problem_category"] = "未知"
    return result
