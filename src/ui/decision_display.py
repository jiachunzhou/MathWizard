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

    submission = st.session_state.get("submission_data", {})

    # 概览卡片
    _render_overview_cards(submission)

    st.markdown("---")

    # 双维度分析区
    col_nlp, col_data = st.columns(2)

    with col_nlp:
        _render_nlp_analysis(submission)

    with col_data:
        _render_data_analysis(submission)

    st.markdown("---")

    # 决策树流程图
    _render_decision_tree_flow(submission)

    st.markdown("---")

    # 算法推荐结果
    _render_algorithm_recommendation(submission)


# ============================================================================
# 空状态
# ============================================================================

def _render_empty_state():
    """未提交时的空状态"""
    st.info("👈 请先在「📝 问题输入」中填写问题描述并提交分析")

    # 展示决策流程示意
    st.markdown("### 📋 决策流程预览")
    st.markdown("""
    提交分析后，系统将通过以下流程自动选择最优算法：
    """)

    _render_placeholder_flow()


# ============================================================================
# 概览卡片
# ============================================================================

def _render_overview_cards(submission: dict):
    """顶部概览卡片"""
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            label="📝 问题类型",
            value=submission.get("problem_type", "待分析"),
        )

    with c2:
        shape = submission.get("data_shape")
        value = f"{shape[0]}行 × {shape[1]}列" if shape else "无数据"
        st.metric(label="📊 数据规模", value=value)

    with c3:
        st.metric(
            label="🎯 分析状态",
            value="🔜 待 LLM 推理",
        )


# ============================================================================
# 自然语言分析维度
# ============================================================================

def _render_nlp_analysis(submission: dict):
    """自然语言分析 — 从问题描述提取意图"""
    st.markdown("### 🗣️ 维度一：自然语言分析")
    st.caption("LLM 从问题描述中提取语义特征")

    description = submission.get("description", "")

    with st.expander("📋 语义特征提取", expanded=True):
        if description:
            st.markdown(f"""
            <div style="background:#f8f9fa;padding:1rem;border-radius:8px;border-left:3px solid #2e86c1;">
            <strong>原始输入：</strong><br>
            {description[:200]}{'...' if len(description) > 200 else ''}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("无问题描述")

        # 占位：后续 LLM 填充
        _render_llm_placeholder("语义分析", [
            ("关键词提取", "识别数学概念（如：回归、拟合、分解、求解）"),
            ("意图分类", "映射到 8 大问题类型之一"),
            ("约束识别", "提取精度要求、性能约束、输出格式等"),
        ])

    with st.expander("🔍 关键词匹配", expanded=False):
        _render_llm_placeholder("关键词→领域映射", [
            ("回归/预测/拟合", "→ 回归问题"),
            ("分类/识别/判别", "→ 分类问题"),
            ("最小/最大/最优", "→ 优化问题"),
            ("积分/微分/方程", "→ 微分方程 / 数值计算"),
            ("分解/特征值/奇异值", "→ 矩阵运算"),
            ("频率/频谱/滤波", "→ 信号处理"),
            ("检验/分布/假设", "→ 统计分析"),
        ])


# ============================================================================
# 数据分析维度
# ============================================================================

def _render_data_analysis(submission: dict):
    """数据分析 — 从数据结构推断算法约束"""
    st.markdown("### 📊 维度二：数据特征分析")
    st.caption("从上传数据中提取结构特征")

    shape = submission.get("data_shape")
    columns = submission.get("data_columns", [])

    if shape is None:
        st.info("🔜 无上传数据，将仅基于自然语言进行分析")
        with st.expander("📋 无数据时的分析策略", expanded=False):
            st.markdown("""
            系统将：
            1. 仅从问题描述中提取数学意图
            2. 选择通用算法（不针对特定数据规模优化）
            3. 生成使用示例数据的演示代码
            """)
        return

    # 数据特征占位区
    with st.expander("📋 数据结构特征", expanded=True):
        rows, cols = shape

        # 特征表格
        features = [
            ("数据规模", f"{rows} 行 × {cols} 列", "影响算法复杂度选择"),
            ("稀疏性", "🔜 待分析", "决定使用稀疏还是稠密算法"),
            ("数值列数", f"🔜 待分析（共 {cols} 列）", "影响特征工程策略"),
            ("缺失率", "🔜 待分析", "决定是否需要插值预处理"),
            ("量纲差异", "🔜 待分析", "决定是否需要标准化"),
            ("异常值", "🔜 待分析", "影响鲁棒算法选择"),
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

    with st.expander("🧮 数据驱动决策规则", expanded=False):
        _render_llm_placeholder("数据→算法约束", [
            ("稀疏矩阵 (稀疏度>80%)", "→ 优先迭代法（共轭梯度、GMRES）"),
            ("稠密矩阵 + 中小规模 (<1000×1000)", "→ 直接法（LU、QR、SVD）"),
            ("稠密矩阵 + 大规模 (>1000×1000)", "→ 随机化算法 / 分块计算"),
            ("高维特征 (>100列)", "→ 正则化回归（Lasso、Ridge）"),
            ("缺失值 > 5%", "→ 先插值预处理（KNN插值、多重插补）"),
            ("类别特征为主", "→ 决策树、随机森林系列"),
            ("数值特征为主 + 连续目标", "→ 线性回归、SVR、高斯过程"),
        ])


# ============================================================================
# 决策树流程图
# ============================================================================

def _render_decision_tree_flow(submission: dict):
    """决策树可视化流程图"""
    st.markdown("### 🌲 决策树推理路径")

    # 用 HTML/CSS 绘制决策树
    tree_html = _build_decision_tree_html(submission)
    st.markdown(tree_html, unsafe_allow_html=True)

    # LLM 推理日志占位
    with st.expander("📜 LLM 推理日志", expanded=False):
        st.info(
            "🔜 提交分析后，此处将实时展示 LLM 的完整推理过程，包括：\n\n"
            "1. 读取问题描述 → 提取关键语义\n"
            "2. 分析数据结构 → 评估特征矩阵\n"
            "3. 遍历决策树节点 → 逐步缩小候选算法集\n"
            "4. 输出最终推荐 → 附带置信度和理由"
        )


def _build_decision_tree_html(submission: dict) -> str:
    """构建决策树 HTML"""
    shape = submission.get("data_shape")
    has_data = shape is not None

    return f"""
    <style>
        .dt-container {{
            background: #ffffff;
            border: 1px solid #e0e4e8;
            border-radius: 12px;
            padding: 1.5rem;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            overflow-x: auto;
        }}
        .dt-node {{
            background: #f0f7ff;
            border: 2px solid #2e86c1;
            border-radius: 8px;
            padding: 0.6rem 1rem;
            margin: 0.3rem;
            text-align: center;
            display: inline-block;
            min-width: 140px;
            font-weight: 600;
            color: #1a5276;
        }}
        .dt-node.root {{
            background: linear-gradient(135deg, #1a5276, #2e86c1);
            color: white;
            border-color: #1a5276;
            font-size: 1rem;
            padding: 0.8rem 1.5rem;
        }}
        .dt-node.leaf {{
            background: #d4efdf;
            border-color: #27ae60;
            color: #1e8449;
        }}
        .dt-node.pending {{
            background: #fef9e7;
            border-color: #f39c12;
            color: #7d6608;
            border-style: dashed;
        }}
        .dt-arrow {{
            color: #888;
            font-size: 1.2rem;
            margin: 0 0.5rem;
        }}
        .dt-line {{
            text-align: center;
            color: #aaa;
            margin: 0.2rem 0;
        }}
        .dt-branch {{
            display: inline-block;
            margin: 0.3rem 1rem;
            text-align: center;
            vertical-align: top;
        }}
        .dt-label {{
            font-size: 0.75rem;
            color: #888;
            margin-bottom: 0.2rem;
            font-style: italic;
        }}
    </style>
    <div class="dt-container">
        <div style="text-align:center;">
            <div class="dt-branch">
                <div class="dt-node root">🎯 用户输入</div>
            </div>
        </div>
        <div class="dt-line">│</div>
        <div style="text-align:center;">
            <div style="display:flex;justify-content:center;gap:2rem;">
                <div class="dt-branch">
                    <div class="dt-label">← 维度一</div>
                    <div class="dt-node pending">🗣️ 语义分析</div>
                    <div class="dt-label">自然语言理解</div>
                </div>
                <div class="dt-branch">
                    <div class="dt-label">维度二 →</div>
                    <div class="dt-node pending">{'📊 数据特征' if has_data else '📊 无数据'}</div>
                    <div class="dt-label">{'稀疏性/规模/分布' if has_data else '跳过数据分支'}</div>
                </div>
            </div>
        </div>
        <div class="dt-line">│</div>
        <div style="text-align:center;">
            <div class="dt-branch">
                <div class="dt-node pending">🔍 问题类型分类</div>
                <div class="dt-label">8 领域匹配</div>
            </div>
        </div>
        <div class="dt-line">│</div>
        <div style="text-align:center;">
            <div class="dt-branch">
                <div class="dt-node pending">📐 公式模板匹配</div>
                <div class="dt-label">从 40+ 模板中选择</div>
            </div>
        </div>
        <div class="dt-line">│</div>
        <div style="text-align:center;">
            <div style="display:flex;justify-content:center;gap:1rem;">
                <div class="dt-branch">
                    <div class="dt-node pending">⚙️ 候选算法集</div>
                    <div class="dt-label">按置信度排序</div>
                </div>
                <div class="dt-arrow">→</div>
                <div class="dt-branch">
                    <div class="dt-node leaf">✅ 最优算法</div>
                    <div class="dt-label">推荐 + 理由</div>
                </div>
            </div>
        </div>
    </div>
    """


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


# ============================================================================
# 算法推荐结果
# ============================================================================

def _render_algorithm_recommendation(submission: dict):
    """算法推荐结果展示"""
    st.markdown("### 🎯 算法推荐结果")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**🏆 首选算法**")
        st.info(
            "🔜 提交分析后，此处将显示 LLM 推荐的首选算法，"
            "包含算法名称、适用场景和推荐理由。"
        )

    with c2:
        st.markdown("**📊 置信度评估**")
        st.info(
            "🔜 展示各候选算法的置信度评分和排序，"
            "帮助用户理解决策依据。"
        )

    # 候选算法列表占位
    with st.expander("📋 候选算法对比", expanded=False):
        _render_llm_placeholder("候选算法排序", [
            ("算法名称", "置信度 | 适用场景 | 计算复杂度 | 前提假设"),
            ("——", "提交分析后由 LLM 自动填充 ——"),
        ])


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
