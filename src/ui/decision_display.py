"""
算法决策展示组件
可视化 LLM 决策树推理过程：自然语言分析 + 数据特征分析 → 算法选择
"""

import streamlit as st


# ============================================================================
# 决策树数据结构（后续由 LLM 填充）
# ============================================================================

def render_decision_tab():
    """渲染「算法决策」标签页的全部内容"""
    st.markdown("## 🌳 算法决策树分析")

    if not st.session_state.get("analysis_submitted"):
        _render_empty_state()
        return

    # 检查是否有分析结果
    analysis_result = st.session_state.get("analysis_result")
    if analysis_result is None:
        _render_pending_state(st.session_state.get("submission_data", {}))
        return

    # 有真实分析结果，展示完整内容
    submission = st.session_state.get("submission_data", {})
    semantic = analysis_result.get("semantic_result", {})
    data_report = analysis_result.get("data_report", {})
    decision = analysis_result.get("decision_result", {})

    # 概览卡片
    _render_overview_cards_live(submission, semantic, decision)

    st.markdown("---")

    # 双维度分析区
    col_nlp, col_data = st.columns(2)

    with col_nlp:
        _render_nlp_analysis_live(semantic)

    with col_data:
        _render_data_analysis_live(data_report)

    st.markdown("---")

    # 决策路径
    _render_decision_path(decision)

    st.markdown("---")

    # 算法推荐结果
    _render_algorithm_recommendation_live(decision)


# ============================================================================
# 空状态 / 等待状态
# ============================================================================

def _render_empty_state():
    """未提交时的空状态"""
    st.info("👈 请先在「📝 问题输入」中填写问题描述并提交分析")
    st.markdown("### 📋 决策流程预览")
    st.markdown("提交分析后，系统将通过以下流程自动选择最优算法：")
    _render_placeholder_flow()


def _render_pending_state(submission: dict):
    """已提交但分析未完成（异常情况）"""
    st.warning("⏳ 分析结果尚未生成，请返回「📝 问题输入」重新提交")
    st.json(submission)


# ============================================================================
# 概览卡片（真实数据版）
# ============================================================================

def _render_overview_cards_live(submission: dict, semantic: dict, decision: dict):
    """使用真实分析结果渲染概览卡片"""
    c1, c2, c3 = st.columns(3)

    with c1:
        category = decision.get("problem_category", semantic.get("suggested_category", "待分析"))
        st.metric(label="📝 问题类型", value=category)

    with c2:
        primary = decision.get("primary_algorithm_info", {})
        alg_name = primary.get("name", decision.get("primary_algorithm", "待定"))
        st.metric(label="🏆 推荐算法", value=alg_name)

    with c3:
        confidence = decision.get("confidence", semantic.get("confidence", 0))
        st.metric(label="🎯 置信度", value=f"{confidence:.0%}")

    # 分析方式标签
    method = semantic.get("analysis_method", "unknown")
    method_labels = {
        "llm": "🤖 LLM 分析",
        "keyword_rules": "📋 关键词规则",
        "fallback_keyword": "📋 关键词规则（LLM不可用）",
    }
    st.caption(f"分析方式：{method_labels.get(method, method)}")


# ============================================================================
# 自然语言分析（真实数据版）
# ============================================================================

def _render_nlp_analysis_live(semantic: dict):
    """使用真实语义分析结果渲染"""
    st.markdown("### 🗣️ 维度一：自然语言分析")

    with st.expander("📋 语义特征提取", expanded=True):
        st.markdown(f"""
        <div style="background:#f0f7ff;padding:1rem;border-radius:8px;border-left:3px solid #2e86c1;margin-bottom:0.8rem;">
            <strong>🧠 数学意图：</strong>{semantic.get('mathematical_intent', '—')}
        </div>
        """, unsafe_allow_html=True)

        # 关键实体
        entities = semantic.get("key_entities", {})
        if entities:
            for entity_type, items in entities.items():
                if items:
                    st.markdown(f"**{entity_type}**：{', '.join(items)}")

        # 约束条件
        constraints = semantic.get("constraints", [])
        if constraints:
            st.markdown("**约束条件**：")
            for c in constraints:
                st.markdown(f"- {c}")

    with st.expander("🔍 关键词匹配", expanded=False):
        keyword_algs = semantic.get("keyword_matched_algorithms", [])
        if keyword_algs:
            st.markdown(f"**命中 {len(keyword_algs)} 个关键词 → 候选算法**：")
            from src.core.algorithm_kb import get_algorithm_info
            for alg_id in keyword_algs[:10]:
                info = get_algorithm_info(alg_id)
                name = info.get("name", alg_id)
                cat = info.get("category", "—")
                st.markdown(f"- **{name}** `{alg_id}` ({cat})")
        else:
            st.caption("无直接关键词命中，使用 LLM 语义理解")

    # 推理过程
    with st.expander("📜 推理过程", expanded=False):
        reasoning = semantic.get("reasoning", "")
        raw = semantic.get("llm_raw_response", "")
        if reasoning:
            st.markdown(reasoning)
        if raw and raw != reasoning:
            st.divider()
            st.caption("LLM 原始输出：")
            st.code(raw[:500], language="text")


# ============================================================================
# 数据分析（真实数据版）
# ============================================================================

def _render_data_analysis_live(data_report: dict):
    """使用真实数据分析报告渲染"""
    st.markdown("### 📊 维度二：数据特征分析")

    if data_report.get("status") == "no_data" or not data_report:
        st.info("无上传数据，跳过数据维度分析")
        return

    with st.expander("📋 数据结构特征", expanded=True):
        scale = data_report.get("scale", {})
        sparsity = data_report.get("sparsity", {})
        quality = data_report.get("quality", {})
        scale_sens = data_report.get("scale_sensitivity", {})

        features = [
            ("数据规模", f"{scale.get('rows', '?')}行 × {scale.get('cols', '?')}列", scale.get("description", "")),
            ("稀疏度", f"{sparsity.get('sparse_ratio', 0):.1%}", sparsity.get("description", "")),
            ("缺失率", f"{quality.get('missing_ratio', 0):.1%}",
             "需要插值" if quality.get("needs_imputation") else "数据完整"),
            ("量纲差异", f"范围比 {scale_sens.get('range_ratio', 'N/A')}",
             scale_sens.get("description", "")),
            ("数值列占比", f"{data_report['structure']['numeric_ratio']:.0%}",
             "全数值" if data_report['structure'].get('is_purely_numeric') else "含非数值列"),
        ]

        for name, value, impact in features:
            st.markdown(f"""
            <div style="display:flex;align-items:center;margin:4px 0;padding:6px 10px;
                        background:#f8f9fa;border-radius:6px;">
                <span style="font-weight:600;min-width:90px;">{name}</span>
                <span style="color:#2e86c1;min-width:160px;">{value}</span>
                <span style="color:#888;font-size:0.85rem;">{impact}</span>
            </div>
            """, unsafe_allow_html=True)

    # 预处理建议
    recs = data_report.get("recommendations", [])
    if recs:
        with st.expander("💡 预处理建议", expanded=False):
            for r in recs:
                st.markdown(f"""
                <div style="background:#fef9e7;padding:8px 12px;border-radius:6px;margin:4px 0;
                            border-left:3px solid #f39c12;">
                    <strong>{r['action']}</strong>：{r['reason']}<br>
                    <small>建议方法：{', '.join(r.get('methods', []))}</small>
                </div>
                """, unsafe_allow_html=True)


# ============================================================================
# 决策路径（真实数据版）
# ============================================================================

def _render_decision_path(decision: dict):
    """渲染决策树推理路径"""
    st.markdown("### 🌲 决策树推理路径")

    path = decision.get("decision_path", [])

    if not path:
        st.info("无决策路径数据")
        return

    # 时间线样式展示
    html_parts = ['<div style="position:relative;padding-left:30px;">']

    for i, step in enumerate(path):
        color = "#2e86c1" if i < len(path) - 1 else "#27ae60"
        html_parts.append(f"""
        <div style="position:relative;margin-bottom:16px;">
            <div style="position:absolute;left:-24px;top:4px;width:12px;height:12px;
                        border-radius:50%;background:{color};border:2px solid #fff;
                        box-shadow:0 0 0 2px {color};"></div>
            <div style="font-weight:600;color:#333;">{step['step']}</div>
            <div style="color:#555;margin:2px 0;">{step['decision']}</div>
            <div style="font-size:0.8rem;color:#999;">来源：{step.get('source', '—')}</div>
        </div>
        """)

    html_parts.append('</div>')
    st.markdown('\n'.join(html_parts), unsafe_allow_html=True)

    # 推理说明
    reasoning = decision.get("reasoning", "")
    if reasoning:
        with st.expander("📜 详细推理说明", expanded=True):
            st.markdown(reasoning)


# ============================================================================
# 算法推荐（真实数据版）
# ============================================================================

def _render_algorithm_recommendation_live(decision: dict):
    """使用真实决策结果渲染算法推荐"""
    st.markdown("### 🎯 算法推荐结果")

    primary_info = decision.get("primary_algorithm_info", {})
    candidates = decision.get("candidates", [])

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**🏆 首选算法**")
        if primary_info:
            st.markdown(f"""
            <div style="background:#d4efdf;padding:1rem;border-radius:10px;
                        border:1px solid #27ae60;">
                <h3 style="margin:0;color:#1e8449;">{primary_info.get('name', '—')}</h3>
                <p style="margin:8px 0 0 0;color:#555;">
                    <b>分类：</b>{primary_info.get('category', '—')}<br>
                    <b>复杂度：</b>{primary_info.get('complexity', '—')}<br>
                    <b>稳定性：</b>{primary_info.get('stability', '—')}<br>
                    <b>MATLAB：</b><code>{primary_info.get('matlab_function', '—')}</code>
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("未找到推荐算法")

    with c2:
        st.markdown("**📊 候选算法对比**")
        if candidates:
            # 构建对比表
            rows = []
            for c in candidates[:5]:
                rows.append({
                    "算法": c.get("name", c.get("algorithm_id", "—")),
                    "分数": f"{c.get('score', 0):.1f}",
                    "复杂度": c.get("complexity", "—"),
                    "稳定性": c.get("stability", "—"),
                })
            import pandas as pd
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.caption("无候选算法")

    # 备选算法
    if len(candidates) > 1:
        with st.expander("📋 全部候选算法详情", expanded=False):
            for c in candidates:
                from src.core.algorithm_kb import get_algorithm_info
                info = get_algorithm_info(c.get("algorithm_id", ""))
                contraindications = info.get("contraindications", [])

                st.markdown(f"""
                <div style="margin:6px 0;padding:10px;background:#fafafa;border-radius:6px;">
                    <strong>{c.get('name', '—')}</strong>
                    <span style="float:right;color:#2e86c1;">{c.get('score', 0):.1f}分</span><br>
                    <small>复杂度: {c.get('complexity', '—')} | 稳定性: {c.get('stability', '—')}</small>
                    {f'<br><small style="color:#c0392b;">⚠️ 不适用: {"; ".join(contraindications)}</small>' if contraindications else ''}
                </div>
                """, unsafe_allow_html=True)


# ============================================================================
# 辅助函数
# ============================================================================

def _render_llm_placeholder(title: str, items: list):
    """渲染 LLM 分析占位区域"""
    st.caption(f"🔜 {title} — 提交后由 LLM 自动分析填充")

    for item in items:
        if isinstance(item, tuple):
            key, value = item
            st.markdown(f"""
            <div style="display:flex;margin:2px 0;padding:4px 8px;
                        background:#fafafa;border-radius:4px;font-size:0.85rem;">
                <span style="font-weight:600;min-width:180px;color:#555;">{key}</span>
                <span style="color:#888;">{value}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="margin:2px 0;padding:4px 8px;color:#999;font-size:0.85rem;">{item}</div>
            """, unsafe_allow_html=True)


def _render_placeholder_flow():
    """展示占位决策流程（未提交时）"""
    st.markdown("""
    <style>
        .placeholder-flow {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 10px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .placeholder-step {
            background: #fff;
            border: 1px dashed #ccc;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
            color: #666;
        }
        .placeholder-arrow { color: #bbb; font-size: 1.2rem; }
    </style>
    <div class="placeholder-flow">
        <span class="placeholder-step">📝 问题描述</span>
        <span class="placeholder-arrow">→</span>
        <span class="placeholder-step">🗣️ 语义分析</span>
        <span class="placeholder-arrow">→</span>
        <span class="placeholder-step">📊 数据特征</span>
        <span class="placeholder-arrow">→</span>
        <span class="placeholder-step">🌲 决策树</span>
        <span class="placeholder-arrow">→</span>
        <span class="placeholder-step">🎯 算法推荐</span>
    </div>
    """, unsafe_allow_html=True)
