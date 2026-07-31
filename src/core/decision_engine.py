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
    """确定问题分类"""
    suggested = semantic.get("suggested_category", "")
    problem_type = semantic.get("problem_type", "")

    # 语义分析直接给出的分类
    for cat in CATEGORIES:
        if cat in suggested or cat in problem_type:
            path.append({
                "step": "问题分类",
                "decision": f"语义分析 → {cat}",
                "source": "LLM 语义分析",
                "confidence": semantic.get("confidence", 0.7),
            })
            return cat

    # 回退：从关键词算法反推分类
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
    """收集候选算法并打初始分"""
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

    # 关键词命中的算法加分
    keyword_algs = set(semantic.get("keyword_matched_algorithms", []))
    candidates = []

    for alg_id in cat_algs:
        info = get_algorithm_info(alg_id)
        score = 5.0  # 基础分

        # 关键词命中加分
        if alg_id in keyword_algs:
            score += 10.0

        # 关键词中算法名命中再加分
        name = info.get("name", "")
        if any(kw in semantic.get("mathematical_intent", "") for kw in name.split()):
            score += 5.0

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
        "decision": f"从「{category}」分类收集 {len(candidates)} 个候选算法",
        "source": "知识库查询",
        "detail": [c["name"] for c in candidates],
    })

    return candidates


# ============================================================================
# 第3步：数据特征约束过滤
# ============================================================================

def _apply_data_constraints(candidates: list, data_features: dict, path: list) -> list:
    """基于数据特征调整候选算法分数"""
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

        # 稀疏性检查
        if data_features.get("is_sparse"):
            if match_rules.get("is_sparse") is True:
                c["score"] += 8.0  # 稀疏矩阵 + 迭代法 = 好匹配
                adjustments.append(f"{c['name']}: 稀疏矩阵 → 迭代法加分")
            elif match_rules.get("is_sparse") is False:
                c["score"] -= 5.0  # 稀疏矩阵 + 直接法 = 不太合适
                adjustments.append(f"{c['name']}: 稀疏矩阵 → 直接法降分")

        # 规模检查
        scale = data_features.get("scale_level", "small")
        allowed_scales = match_rules.get("scale_level", [])
        if allowed_scales:
            if scale not in allowed_scales:
                c["score"] -= 3.0
                adjustments.append(f"{c['name']}: 数据规模 {scale} 不匹配 → 降分")
            else:
                c["score"] += 3.0
                adjustments.append(f"{c['name']}: 数据规模 {scale} 匹配 → 加分")

    if adjustments:
        path.append({
            "step": "数据约束",
            "decision": f"基于数据特征调整 {len(adjustments)} 项分数",
            "source": "数据特征分析",
            "detail": adjustments,
        })
    else:
        path.append({
            "step": "数据约束",
            "decision": "数据特征无明显约束影响",
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
    """计算综合置信度"""
    if not candidates:
        return 0.0

    # 基础：语义分析置信度
    base = semantic.get("confidence", 0.5)

    # 有数据时，数据匹配度加分
    if data_features.get("has_data"):
        base = min(1.0, base + 0.1)

    # 首选与第二名的分数差距
    if len(candidates) >= 2:
        gap = candidates[0]["score"] - candidates[1]["score"]
        if gap > 5:
            base = min(1.0, base + 0.1)

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
