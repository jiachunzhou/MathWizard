"""
决策树推理引擎
整合语义分析 + 数据特征分析，按决策树规则推理最优算法

决策树结构（本科数值分析版）：
                        用户输入
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
           语义分析              数据特征分析
          (LLM+关键词)          (data_analyzer)
                │                   │
                └─────────┬─────────┘
                          ▼
                    问题类型判定
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
          插值/拟合   线性方程组   微分方程  ...
              │           │           │
              ▼           ▼           ▼
          候选算法集   候选算法集   候选算法集
              │           │           │
              └───────────┼───────────┘
                          ▼
                  数据特征约束过滤
                          │
                          ▼
                    最终算法推荐
"""

from typing import Optional

from src.core.algorithm_kb import (
    ALGORITHM_KB,
    CATEGORIES,
    get_algorithm_info,
    get_category_algorithms,
)
from src.core.data_analyzer import get_decision_features


def run_decision_tree(
    semantic_result: dict,
    data_report: Optional[dict] = None,
) -> dict:
    """
    执行决策树推理

    Args:
        semantic_result: 语义分析结果（来自 semantic_analyzer）
        data_report: 数据分析报告（来自 data_analyzer），可为 None

    Returns:
        dict: {
            "problem_category": str,       # 最终问题分类
            "primary_algorithm": str,      # 首选算法 ID
            "primary_algorithm_info": dict,# 首选算法详情
            "candidates": list,            # 候选算法列表（含分数）
            "decision_path": list,         # 决策路径（每步的推理）
            "confidence": float,           # 综合置信度
            "reasoning": str,              # 推理说明
        }
    """
    decision_path = []
    data_features = get_decision_features(data_report) if data_report else {"has_data": False}

    # ---- 第1步：确定问题分类 ----
    category = _decide_category(semantic_result, decision_path)

    # ---- 第2步：收集候选算法 ----
    candidates = _collect_candidates(category, semantic_result, decision_path)

    # ---- 第3步：数据特征约束过滤 ----
    candidates = _apply_data_constraints(candidates, data_features, decision_path)

    # ---- 第4步：排序与选择 ----
    primary, candidates = _rank_and_select(candidates, decision_path)

    # ---- 构建结果 ----
    return {
        "problem_category": category,
        "category_info": CATEGORIES.get(category, {}),
        "primary_algorithm": primary,
        "primary_algorithm_info": get_algorithm_info(primary) if primary else {},
        "candidates": candidates,
        "decision_path": decision_path,
        "confidence": _compute_confidence(candidates, semantic_result, data_features),
        "reasoning": _build_reasoning(category, primary, candidates, decision_path),
        "semantic_result": semantic_result,
        "data_features": data_features,
    }


# ============================================================================
# 第1步：问题分类
# ============================================================================

def _decide_category(semantic: dict, path: list) -> str:
    """确定问题分类（支持 LLM 返回的非标准分类名模糊匹配）"""
    suggested = semantic.get("suggested_category", "")
    problem_type = semantic.get("problem_type", "")

    # 构建标准分类名列表
    cat_names = list(CATEGORIES.keys())
    # 构建别名映射（LLM 可能返回的非标准名称）
    cat_aliases = {
        "曲线拟合": ["拟合", "回归", "最小二乘拟合", "多项式回归"],
        "插值与逼近": ["插值", "样条插值", "逼近", "三次样条"],
        "数值积分": ["积分", "求积", "数值积分计算"],
        "数值微分": ["微分", "导数", "数值导数"],
        "线性方程组": ["线性方程", "直接法", "迭代法", "方程组求解", "矩阵求解"],
        "非线性方程": ["求根", "非线性方程求根", "方程求解"],
        "特征值问题": ["特征值", "特征向量", "谱分解"],
        "常微分方程": ["ODE", "微分方程", "初值问题", "Runge-Kutta"],
    }

    # 1. 精确匹配
    for cat in cat_names:
        if cat in suggested or cat in problem_type:
            path.append({
                "step": "问题分类",
                "decision": f"语义分析 → {cat}（精确匹配）",
                "source": "LLM 语义分析",
                "confidence": semantic.get("confidence", 0.7),
            })
            return cat

    # 2. 别名模糊匹配
    for cat, aliases in cat_aliases.items():
        for alias in aliases:
            if alias in suggested or alias in problem_type:
                path.append({
                    "step": "问题分类",
                    "decision": f"语义分析 → {cat}（别名匹配: 「{alias}」）",
                    "source": "LLM 语义分析 + 别名映射",
                    "confidence": semantic.get("confidence", 0.7),
                })
                return cat

    # 3. 回退：从关键词算法反推分类
    keyword_algs = semantic.get("keyword_matched_algorithms", [])
    if keyword_algs:
        for cat, info in CATEGORIES.items():
            cat_algs = info["algorithms"]
            overlap = set(keyword_algs) & set(cat_algs)
            if overlap:
                path.append({
                    "step": "问题分类",
                    "decision": f"关键词匹配 → {cat}（{len(overlap)}个算法命中）",
                    "source": "关键词规则",
                    "confidence": 0.6,
                })
                return cat

    path.append({
        "step": "问题分类",
        "decision": "无法明确分类 → 数值计算（通用）",
        "source": "默认回退",
        "confidence": 0.3,
    })
    return "数值计算"


# ============================================================================
# 第2步：收集候选算法
# ============================================================================

def _collect_candidates(category: str, semantic: dict, path: list) -> list:
    """收集候选算法并打初始分（多维度加权评分）"""
    # 从知识库获取该分类所有算法
    cat_algs = get_category_algorithms(category)

    # 如果分类不在知识库中，返回空
    if not cat_algs:
        path.append({
            "step": "候选收集",
            "decision": f"分类「{category}」不在知识库中",
            "source": "知识库查询",
        })
        return []

    # 关键词命中计数（多次命中累积加分）
    keyword_algs = semantic.get("keyword_matched_algorithms", [])
    from collections import Counter
    keyword_hit_count = Counter(keyword_algs)

    mathematical_intent = semantic.get("mathematical_intent", "")
    problem_type = semantic.get("problem_type", "")

    candidates = []

    for alg_id in cat_algs:
        info = get_algorithm_info(alg_id)
        score = 5.0  # 基础分

        # ---- 1. 关键词命中计数加权 ----
        hit_count = keyword_hit_count.get(alg_id, 0)
        if hit_count > 0:
            score += min(15.0, hit_count * 3.0)

        # ---- 2. 算法名称分词匹配 ----
        name = info.get("name", "")
        name_parts = name.replace("（", " ").replace("）", " ").replace("(", " ").replace(")", " ").split()
        for part in name_parts:
            if len(part) >= 2 and part in mathematical_intent:
                score += 4.0
                break  # 只加一次

        # ---- 3. 子类别匹配 ----
        subcategory = info.get("subcategory", "")
        if subcategory and subcategory in problem_type:
            score += 3.0

        # ---- 4. 关键词特异性加分 ----
        specific_keywords = info.get("keywords", [])
        for kw in specific_keywords:
            if len(kw) >= 3 and kw in mathematical_intent:
                specificity_bonus = min(5.0, len(kw) * 0.5)
                score += specificity_bonus

        # ---- 5. 算法收敛速度加分 ----
        convergence = info.get("convergence_rate", "")
        if "二次" in convergence or "超线性" in convergence:
            score += 1.0  # 更快的收敛速度有小幅加分

        # ---- 6. 数值稳定性加分 ----
        stability = info.get("stability", "")
        if stability == "高":
            score += 0.5

        candidates.append({
            "algorithm_id": alg_id,
            "name": info.get("name", alg_id),
            "category": info.get("category", category),
            "score": score,
            "complexity": info.get("complexity", "未知"),
            "stability": info.get("stability", "未知"),
            "matlab_function": info.get("matlab_function", ""),
        })

    path.append({
        "step": "候选收集",
        "decision": f"从「{category}」分类收集 {len(candidates)} 个候选算法（多维度加权评分）",
        "source": "知识库查询 + 关键词加权",
        "detail": [f"{c['name']}: {c['score']:.1f}分" for c in candidates],
    })

    return candidates


# ============================================================================
# 第3步：数据特征约束过滤
# ============================================================================

def _apply_data_constraints(candidates: list, data_features: dict, path: list) -> list:
    """基于数据特征调整候选算法分数（7 个维度）"""
    if not data_features.get("has_data"):
        path.append({
            "step": "数据约束",
            "decision": "无上传数据，跳过数据特征过滤",
            "source": "数据检查",
        })
        return candidates

    adjustments = []

    for c in candidates:
        alg_id = c["algorithm_id"]
        info = get_algorithm_info(alg_id)
        match_rules = info.get("data_features_match", {})

        # ---- 1. 稀疏性检查 ----
        if data_features.get("is_sparse"):
            sparse_match = match_rules.get("is_sparse")
            if sparse_match is True:
                c["score"] += 8.0
                adjustments.append(f"{c['name']}: 稀疏矩阵 → 迭代法加分")
            elif sparse_match is False:
                c["score"] -= 5.0
                adjustments.append(f"{c['name']}: 稀疏矩阵 → 直接法降分")

        # ---- 2. 数据规模检查 ----
        scale = data_features.get("scale_level", "small")
        allowed_scales = match_rules.get("scale_level", [])
        if allowed_scales:
            if scale not in allowed_scales:
                c["score"] -= 3.0
                adjustments.append(f"{c['name']}: 数据规模 {scale} 不匹配 → 降分")
            else:
                c["score"] += 3.0
                adjustments.append(f"{c['name']}: 数据规模 {scale} 匹配 → 加分")

        # ---- 3. 缺失值检查 ----
        if data_features.get("needs_imputation"):
            imp_match = match_rules.get("needs_imputation")
            if imp_match is False:
                c["score"] -= 6.0
                adjustments.append(f"{c['name']}: 数据有缺失 → 需先插值处理")
            elif imp_match is True:
                c["score"] += 4.0
                adjustments.append(f"{c['name']}: 可处理缺失数据 → 加分")

        # ---- 4. 量纲/标准化检查 ----
        if data_features.get("needs_scaling"):
            scale_match = match_rules.get("needs_scaling")
            if scale_match is False:
                c["score"] -= 4.0
                adjustments.append(f"{c['name']}: 量纲差异大 → 需先标准化")
            elif scale_match is True:
                c["score"] += 3.0
                adjustments.append(f"{c['name']}: 可处理不同量纲 → 加分")

        # ---- 5. 数值列占比检查 ----
        numeric_ratio = data_features.get("numeric_ratio", 1.0)
        min_ratio = match_rules.get("numeric_ratio_min", 0.0)
        if numeric_ratio < min_ratio:
            c["score"] -= 5.0
            adjustments.append(
                f"{c['name']}: 数值列占比不足 ({numeric_ratio:.0%} < {min_ratio:.0%}) → 降分"
            )

        # ---- 6. 分布特征检查（非正态） ----
        if data_features.get("has_non_normal"):
            nn_match = match_rules.get("has_non_normal")
            if nn_match is False:
                c["score"] -= 3.0
                adjustments.append(f"{c['name']}: 数据非正态分布 → 降分")

        # 偏态检查
        if data_features.get("has_skewed"):
            skew_match = match_rules.get("has_skewed")
            if skew_match is False:
                c["score"] -= 2.0
                adjustments.append(f"{c['name']}: 数据偏态分布 → 降分")

        # ---- 7. 行数范围检查 ----
        rows = data_features.get("rows", 0)
        min_rows = match_rules.get("min_rows", 0)
        max_rows = match_rules.get("max_rows", float("inf"))
        if rows < min_rows:
            c["score"] -= 5.0
            adjustments.append(f"{c['name']}: 行数不足 ({rows} < {min_rows}) → 降分")
        if rows > max_rows:
            penalty = match_rules.get("penalty_weight", 1.0)
            c["score"] -= 4.0 * penalty
            adjustments.append(f"{c['name']}: 行数超出推荐范围 ({rows} > {max_rows}) → 降分")

        # ---- 8. 纯数值检查 ----
        if not data_features.get("is_purely_numeric", True):
            if match_rules.get("is_purely_numeric") is True:
                c["score"] -= 4.0
                adjustments.append(f"{c['name']}: 数据含非数值列 → 降分")

    if adjustments:
        path.append({
            "step": "数据约束",
            "decision": f"基于 {len(adjustments)} 项数据特征调整候选算法分数",
            "source": "数据特征分析",
            "detail": adjustments,
        })
    else:
        path.append({
            "step": "数据约束",
            "decision": "数据特征与所有候选算法匹配良好",
            "source": "数据特征分析",
        })

    return candidates


# ============================================================================
# 第4步：排序与选择
# ============================================================================

def _rank_and_select(candidates: list, path: list) -> tuple:
    """排序候选算法，选出首选"""
    if not candidates:
        path.append({"step": "算法选择", "decision": "无可用候选算法", "source": "排序"})
        return None, []

    # 按分数降序
    candidates.sort(key=lambda x: x["score"], reverse=True)
    primary = candidates[0]["algorithm_id"]

    # 归一化分数到 0-1
    max_score = candidates[0]["score"]
    min_score = candidates[-1]["score"] if len(candidates) > 1 else max_score
    score_range = max_score - min_score or 1

    for c in candidates:
        c["normalized_score"] = round((c["score"] - min_score) / score_range, 2)

    path.append({
        "step": "算法选择",
        "decision": f"首选: {candidates[0]['name']}（分数: {candidates[0]['score']:.1f}）",
        "source": "评分排序",
        "detail": [f"{c['name']}: {c['score']:.1f}分" for c in candidates[:5]],
    })

    return primary, candidates


# ============================================================================
# 辅助
# ============================================================================

def _compute_confidence(candidates: list, semantic: dict, data_features: dict) -> float:
    """计算综合置信度（梯度加分）"""
    if not candidates:
        return 0.0

    # 基础：语义分析置信度
    base = semantic.get("confidence", 0.5)

    # ---- 数据匹配度动态加分 ----
    if data_features.get("has_data") and len(candidates) > 0:
        # 首选分数越高说明越匹配
        top_score = candidates[0].get("score", 0)
        if top_score >= 20:
            base = min(1.0, base + 0.12)
        elif top_score >= 15:
            base = min(1.0, base + 0.08)
        elif top_score >= 10:
            base = min(1.0, base + 0.05)
        else:
            base = min(1.0, base + 0.03)

    # ---- 首选与第二名的分数差距（梯度加分） ----
    if len(candidates) >= 2:
        gap = candidates[0]["score"] - candidates[1]["score"]
        if gap > 2:
            base = min(1.0, base + 0.04)
        if gap > 5:
            base = min(1.0, base + 0.04)
        if gap > 10:
            base = min(1.0, base + 0.04)

    # ---- 关键词命中数量加分 ----
    keyword_hits = len(semantic.get("keyword_matched_algorithms", []))
    if keyword_hits >= 3:
        base = min(1.0, base + 0.04)
    if keyword_hits >= 5:
        base = min(1.0, base + 0.04)

    # ---- LLM 分析方法加分 ----
    if semantic.get("analysis_method") == "llm":
        base = min(1.0, base + 0.05)

    return round(base, 2)


def _build_reasoning(category: str, primary: str, candidates: list, path: list) -> str:
    """生成可读的推理说明"""
    if not primary:
        return "未能确定合适算法，请提供更多信息。"

    info = get_algorithm_info(primary)
    name = info.get("name", primary)
    complexity = info.get("complexity", "未知")
    stability = info.get("stability", "未知")
    matlab_func = info.get("matlab_function", "自定义")

    lines = [
        f"## 推荐算法：{name}",
        "",
        f"**问题分类**：{category}",
        f"**计算复杂度**：{complexity}",
        f"**数值稳定性**：{stability}",
        f"**MATLAB 函数**：`{matlab_func}`",
        "",
        "**推理过程**：",
    ]

    for step in path:
        lines.append(f"- [{step['step']}] {step['decision']}")

    if len(candidates) > 1:
        lines.append("")
        lines.append("**备选算法**：")
        for c in candidates[1:4]:
            lines.append(f"- {c['name']}（{c['score']:.1f}分）")

    return "\n".join(lines)
