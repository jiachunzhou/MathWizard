"""
数据特征自动分析引擎
从上传的数据中自动提取结构化特征，为决策树提供数据维度输入

分析维度：
- 规模特征：行列数、数据密度
- 稀疏性：零值/空值占比
- 分布特征：数值列的偏度、峰度、正态性
- 质量特征：缺失率、重复率
- 结构特征：数值列占比、类别列基数
- 量纲特征：数值范围差异（是否需要标准化）
"""

from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats


def analyze_data(df: pd.DataFrame) -> dict:
    """
    对 DataFrame 进行全面特征分析

    Args:
        df: 输入数据

    Returns:
        dict: 结构化分析报告
    """
    if df is None or df.empty:
        return {"status": "no_data", "message": "无上传数据"}

    report = {
        "status": "ok",
        "shape": df.shape,
        "rows": df.shape[0],
        "cols": df.shape[1],
        # 规模
        "scale": _analyze_scale(df),
        # 稀疏性
        "sparsity": _analyze_sparsity(df),
        # 质量
        "quality": _analyze_quality(df),
        # 结构
        "structure": _analyze_structure(df),
        # 数值特征
        "numeric_profile": _analyze_numeric_profile(df),
        # 量纲
        "scale_sensitivity": _analyze_scale_sensitivity(df),
        # 汇总建议
        "recommendations": [],
    }

    # 生成预处理建议
    report["recommendations"] = _generate_recommendations(report)

    return report


# ============================================================================
# 各维度分析
# ============================================================================

def _analyze_scale(df: pd.DataFrame) -> dict:
    """规模分析"""
    rows, cols = df.shape
    total_cells = rows * cols

    if rows < 50:
        level = "small"
        desc = "小规模数据（<50行）"
    elif rows < 1000:
        level = "medium"
        desc = "中等规模数据（50-1000行）"
    elif rows < 10000:
        level = "large"
        desc = "大规模数据（1000-10000行）"
    else:
        level = "xlarge"
        desc = "超大规模数据（>10000行）"

    return {
        "rows": rows,
        "cols": cols,
        "total_cells": total_cells,
        "level": level,
        "description": desc,
    }


def _analyze_sparsity(df: pd.DataFrame) -> dict:
    """稀疏性分析"""
    total = df.size

    # 零值比例（仅数值列）
    numeric = df.select_dtypes(include=[np.number])
    zero_count = (numeric == 0).sum().sum() if not numeric.empty else 0
    numeric_total = numeric.size if not numeric.empty else 1
    zero_ratio = round(zero_count / numeric_total, 4)

    # 空值比例
    null_count = df.isnull().sum().sum()
    null_ratio = round(null_count / total, 4) if total > 0 else 0

    # 综合稀疏度
    sparse_ratio = zero_ratio + null_ratio

    if sparse_ratio < 0.1:
        level = "dense"
    elif sparse_ratio < 0.5:
        level = "moderate"
    else:
        level = "sparse"

    return {
        "zero_ratio": zero_ratio,
        "null_ratio": null_ratio,
        "sparse_ratio": round(sparse_ratio, 4),
        "level": level,
        "is_sparse": level == "sparse",
        "description": (
            f"稠密矩阵" if level == "dense"
            else f"中等稀疏度（{sparse_ratio:.1%}）" if level == "moderate"
            else f"稀疏矩阵（{sparse_ratio:.1%}零值/空值）"
        ),
    }


def _analyze_quality(df: pd.DataFrame) -> dict:
    """数据质量分析"""
    total = df.size
    null_count = df.isnull().sum().sum()
    null_ratio = round(null_count / total, 4) if total > 0 else 0

    # 重复行
    dup_count = df.duplicated().sum()

    # 常数列
    constant_cols = []
    for col in df.columns:
        if df[col].nunique(dropna=True) <= 1:
            constant_cols.append(col)

    return {
        "missing_count": int(null_count),
        "missing_ratio": null_ratio,
        "needs_imputation": null_ratio > 0.05,
        "duplicate_rows": int(dup_count),
        "constant_columns": constant_cols,
        "is_clean": null_ratio == 0 and dup_count == 0 and len(constant_cols) == 0,
    }


def _analyze_structure(df: pd.DataFrame) -> dict:
    """数据结构分析"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    other_cols = [c for c in df.columns if c not in numeric_cols and c not in cat_cols]

    return {
        "numeric_count": len(numeric_cols),
        "categorical_count": len(cat_cols),
        "other_count": len(other_cols),
        "numeric_ratio": round(len(numeric_cols) / df.shape[1], 2),
        "numeric_columns": numeric_cols,
        "categorical_columns": cat_cols,
        "is_purely_numeric": len(numeric_cols) == df.shape[1],
    }


def _analyze_numeric_profile(df: pd.DataFrame) -> dict:
    """数值列分布特征分析"""
    numeric = df.select_dtypes(include=[np.number])

    if numeric.empty:
        return {"available": False}

    profiles = {}
    for col in numeric.columns:
        col_data = numeric[col].dropna()
        if len(col_data) < 3:
            continue

        skew = scipy_stats.skew(col_data)
        kurtosis = scipy_stats.kurtosis(col_data)

        # 正态性检验（Shapiro-Wilk，样本量大时用 KS）
        if len(col_data) <= 5000:
            stat, p_value = scipy_stats.shapiro(col_data)
            normality = "normal" if p_value > 0.05 else "non_normal"
        else:
            stat, p_value = scipy_stats.kstest(
                col_data, 'norm', args=(col_data.mean(), col_data.std())
            )
            normality = "normal" if p_value > 0.05 else "non_normal"

        profiles[col] = {
            "mean": round(float(col_data.mean()), 4),
            "std": round(float(col_data.std()), 4),
            "min": round(float(col_data.min()), 4),
            "max": round(float(col_data.max()), 4),
            "skewness": round(float(skew), 4),
            "kurtosis": round(float(kurtosis), 4),
            "normality": normality,
            "normality_pvalue": round(float(p_value), 4),
        }

    return {
        "available": True,
        "columns": profiles,
        "has_skewed": any(abs(p["skewness"]) > 1 for p in profiles.values()),
        "has_non_normal": any(p["normality"] == "non_normal" for p in profiles.values()),
    }


def _analyze_scale_sensitivity(df: pd.DataFrame) -> dict:
    """量纲敏感性分析 — 判断是否需要标准化"""
    numeric = df.select_dtypes(include=[np.number])

    if numeric.empty or numeric.shape[1] < 2:
        return {"needs_scaling": False, "reason": "数值列不足2列，无需标准化"}

    ranges = {}
    for col in numeric.columns:
        col_data = numeric[col].dropna()
        if len(col_data) < 2:
            continue
        col_range = col_data.max() - col_data.min()
        if col_range > 0:
            ranges[col] = col_range

    if len(ranges) < 2:
        return {"needs_scaling": False, "reason": "有效数值列不足"}

    max_range = max(ranges.values())
    min_range = min(ranges.values())

    # 范围比 > 100 认为存在量纲差异
    range_ratio = max_range / min_range if min_range > 0 else float('inf')

    return {
        "needs_scaling": range_ratio > 100,
        "range_ratio": round(range_ratio, 2) if range_ratio != float('inf') else "inf",
        "max_range": round(max_range, 4),
        "min_range": round(min_range, 4),
        "description": (
            f"量纲差异大（范围比 {range_ratio:.0f}:1），建议标准化"
            if range_ratio > 100
            else "量纲差异在可接受范围内"
        ),
    }


# ============================================================================
# 推荐生成
# ============================================================================

def _generate_recommendations(report: dict) -> list:
    """基于分析结果生成预处理建议"""
    recs = []

    quality = report.get("quality", {})
    sparsity = report.get("sparsity", {})
    scale_sens = report.get("scale_sensitivity", {})
    numeric_profile = report.get("numeric_profile", {})
    scale = report.get("scale", {})

    # 缺失值
    if quality.get("needs_imputation"):
        recs.append({
            "type": "preprocessing",
            "action": "impute_missing",
            "reason": f"缺失率 {quality['missing_ratio']:.1%}，建议插值处理",
            "methods": ["KNN插值", "均值/中位数填充", "多重插补"],
        })

    # 量纲
    if scale_sens.get("needs_scaling"):
        recs.append({
            "type": "preprocessing",
            "action": "standardize",
            "reason": scale_sens.get("description", "量纲差异大"),
            "methods": ["Z-score标准化", "Min-Max归一化"],
        })

    # 稀疏矩阵
    if sparsity.get("is_sparse"):
        recs.append({
            "type": "algorithm_constraint",
            "action": "use_sparse_methods",
            "reason": f"稀疏度 {sparsity['sparse_ratio']:.1%}，优先使用迭代法",
            "methods": ["共轭梯度法", "GMRES", "稀疏LU"],
        })

    # 非正态分布
    if numeric_profile.get("has_non_normal"):
        recs.append({
            "type": "algorithm_constraint",
            "action": "use_robust_methods",
            "reason": "数据存在非正态分布特征，建议使用鲁棒方法",
            "methods": ["鲁棒回归", "分位数回归", "Box-Cox变换"],
        })

    # 大规模
    if scale.get("level") in ("large", "xlarge"):
        recs.append({
            "type": "performance",
            "action": "use_iterative_or_randomized",
            "reason": f"数据规模较大（{scale['rows']}行），直接法可能效率低",
            "methods": ["随机化SVD", "分块计算", "迭代求解器"],
        })

    return recs


# ============================================================================
# 供决策树使用的摘要
# ============================================================================

def get_decision_features(report: dict) -> dict:
    """
    从分析报告中提取决策树所需的关键特征
    返回一个扁平的 dict，可直接喂给决策规则引擎
    """
    if report.get("status") == "no_data":
        return {"has_data": False}

    return {
        "has_data": True,
        "rows": report["rows"],
        "cols": report["cols"],
        "scale_level": report["scale"]["level"],
        "is_sparse": report["sparsity"]["is_sparse"],
        "sparse_ratio": report["sparsity"]["sparse_ratio"],
        "needs_imputation": report["quality"]["needs_imputation"],
        "needs_scaling": report["scale_sensitivity"]["needs_scaling"],
        "is_purely_numeric": report["structure"]["is_purely_numeric"],
        "numeric_ratio": report["structure"]["numeric_ratio"],
        "has_non_normal": report["numeric_profile"].get("has_non_normal", False),
        "has_skewed": report["numeric_profile"].get("has_skewed", False),
        "n_recommendations": len(report["recommendations"]),
    }
