"""
MATLAB 算法智能分析平台 — 主入口
基于 Streamlit 的数学问题分析 Web 应用

功能：
1. 复杂数学公式输入（LaTeX）+ 实时预览
2. 数据文件上传（CSV/Excel/TXT）
3. LLM 决策树算法选择（后续阶段）
4. Python 代码生成 + MATLAB 调用（后续阶段）
5. 结果验证（后续阶段）
"""

import streamlit as st

from src.ui.formula_input import render_formula_input, render_formula_templates, insert_template_to_input
from src.ui.file_upload import render_file_upload
from src.ui.sidebar import render_sidebar, PROBLEM_TYPES


# ============================================================================
# 页面配置
# ============================================================================
st.set_page_config(
    page_title="MATLAB 算法智能分析平台",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# 自定义 CSS 样式
# ============================================================================
def inject_custom_css():
    """注入自定义样式"""
    st.markdown("""
    <style>
        /* --- 全局样式 --- */
        .stApp {
            font-family: 'Inter', 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
        }

        /* --- 主标题 --- */
        .main-header {
            background: linear-gradient(135deg, #1a5276 0%, #2e86c1 50%, #3498db 100%);
            padding: 1.8rem 2rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            color: white;
            box-shadow: 0 4px 20px rgba(26, 82, 118, 0.3);
        }
        .main-header h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
        }
        .main-header p {
            margin: 0.3rem 0 0 0;
            opacity: 0.85;
            font-size: 0.95rem;
        }

        /* --- 区域卡片 --- */
        .section-card {
            background: #ffffff;
            border: 1px solid #e8ecf1;
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }

        /* --- 提交按钮 --- */
        .stButton > button[data-testid="baseButton-secondary"] {
            background: linear-gradient(135deg, #1a5276, #2e86c1) !important;
            color: white !important;
            border: none !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
            padding: 0.7rem 2.5rem !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
        }
        .stButton > button[data-testid="baseButton-secondary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(46, 134, 193, 0.4);
        }

        /* --- 信息卡片 --- */
        .info-card {
            background: #f0f7ff;
            border-left: 4px solid #2e86c1;
            padding: 1rem 1.2rem;
            border-radius: 8px;
            margin: 0.8rem 0;
        }

        /* --- 公式预览区 --- */
        .latex-preview-area {
            background: #fafbfc;
            border: 1px dashed #d0d7de;
            border-radius: 10px;
            padding: 1.2rem;
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* --- 状态徽章 --- */
        .status-badge {
            display: inline-block;
            padding: 0.2rem 0.7rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .status-ready { background: #d4edda; color: #155724; }
        .status-pending { background: #fff3cd; color: #856404; }

        /* --- 页脚 --- */
        .app-footer {
            text-align: center;
            color: #999;
            font-size: 0.8rem;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
        }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# 初始化 Session State
# ============================================================================
def init_session_state():
    """初始化 session state 变量"""
    defaults = {
        "latex_input": "",
        "uploaded_data": None,
        "file_name": None,
        "analysis_submitted": False,
        "analysis_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================================
# 主页面渲染
# ============================================================================
def main():
    """主应用入口"""
    inject_custom_css()
    init_session_state()

    # ---- 侧边栏 ----
    config = render_sidebar()

    # ---- 主内容区 ----
    render_main_header()

    # 标签页：输入界面 | 分析结果（后续）
    tab_input, tab_result = st.tabs(["📝 问题输入", "📊 分析结果"])

    with tab_input:
        render_input_tab(config)

    with tab_result:
        render_result_tab()

    # ---- 页脚 ----
    st.markdown(
        '<div class="app-footer">MATLAB 算法智能分析平台 · Powered by LLM + MATLAB Engine</div>',
        unsafe_allow_html=True,
    )


def render_main_header():
    """渲染主标题"""
    st.markdown("""
    <div class="main-header">
        <h1>🧠 MATLAB 算法智能分析平台</h1>
        <p>基于大语言模型的智能算法选择 · 自动代码生成 · MATLAB 高性能计算</p>
    </div>
    """, unsafe_allow_html=True)


def render_input_tab(config: dict):
    """渲染问题输入标签页"""
    # ---- 问题描述 ----
    st.markdown("### 📝 问题描述")

    problem_description = st.text_area(
        "请用自然语言描述您要解决的数学问题",
        height=100,
        placeholder=(
            "例如：\n"
            "- 对附件中的数据进行线性回归拟合，找出自变量 X 和因变量 Y 之间的关系\n"
            "- 求解以下微分方程，并绘制解的曲线\n"
            "- 对矩阵 A 进行奇异值分解（SVD）\n"
            "- 计算附件数据的傅里叶变换并分析频谱特征"
        ),
        key="problem_description",
        help="描述越详细，LLM 越能准确选择算法并生成正确代码",
    )

    # ---- 公式输入 + 模板 ----
    col_formula, col_templates = st.columns([3, 1])

    with col_formula:
        latex_input = render_formula_input()

    with col_templates:
        st.markdown("### 📚 公式模板")
        selected_template = render_formula_templates()
        if selected_template:
            insert_template_to_input(selected_template)
            st.rerun()

    st.divider()

    # ---- 文件上传 ----
    uploaded_df = render_file_upload()

    st.divider()

    # ---- 提交区域 ----
    render_submit_area(config, problem_description, latex_input, uploaded_df)


def render_submit_area(config: dict, description: str, latex: str, df):
    """渲染提交按钮和状态检查"""
    st.markdown("### 🚀 提交分析")

    # 状态检查
    checks = []
    checks.append(("问题描述", bool(description.strip())))
    checks.append(("数学公式", bool(latex.strip())))
    checks.append(("数据文件", df is not None))
    checks.append(("问题类型", bool(config.get('problem_type'))))

    # 显示状态
    cols = st.columns(len(checks))
    for i, (name, ok) in enumerate(checks):
        with cols[i]:
            if ok:
                st.success(f"✅ {name}")
            else:
                st.info(f"⏳ {name}")

    # 准备就绪判断（至少需要问题描述或公式之一）
    ready = checks[0][1] or checks[1][1]

    # 提交按钮
    col_btn, col_hint = st.columns([1, 3])
    with col_btn:
        submitted = st.button(
            "🚀 提交分析",
            type="secondary",
            disabled=not ready,
            use_container_width=True,
        )

    with col_hint:
        if not ready:
            st.caption("⚠️ 请至少填写问题描述或输入数学公式后再提交")
        else:
            st.caption("✅ 准备就绪，点击按钮开始智能分析")

    if submitted:
        st.session_state["analysis_submitted"] = True
        st.session_state["submission_data"] = {
            "problem_type": config.get('problem_type'),
            "description": description,
            "latex_formula": latex,
            "data_shape": df.shape if df is not None else None,
            "data_columns": df.columns.tolist() if df is not None else None,
            "llm_model": config.get('llm_model'),
        }
        st.success("✅ 分析请求已提交！")

        # 展示提交摘要
        with st.expander("📋 提交摘要", expanded=True):
            st.json(st.session_state["submission_data"])

        st.info(
            "💡 **下一阶段将实现：**\n"
            "1. LLM 决策树分析 → 选择最优算法\n"
            "2. 自动生成 Python 代码\n"
            "3. 调用 MATLAB Engine 执行计算\n"
            "4. 结果验证与可视化展示\n\n"
            "请切换到「📊 分析结果」标签页查看（开发中）"
        )


def render_result_tab():
    """渲染分析结果标签页"""
    if not st.session_state.get("analysis_submitted"):
        st.info("👈 请先在「问题输入」标签页中填写信息并提交分析")
        return

    st.markdown("### 📊 分析结果")

    submission = st.session_state.get("submission_data", {})

    # 展示当前阶段占位
    st.markdown("---")

    # 决策树阶段占位
    with st.expander("🌳 第一步：算法决策树分析", expanded=True):
        st.info("🔜 **开发中** — LLM 将在此处展示决策树推理过程，选择最优算法")

    # 代码生成阶段占位
    with st.expander("💻 第二步：Python 代码生成", expanded=True):
        st.info("🔜 **开发中** — 将在此处展示生成的 Python/MATLAB 代码")

    # MATLAB 执行结果阶段占位
    with st.expander("⚡ 第三步：MATLAB 计算结果", expanded=True):
        st.info("🔜 **开发中** — 将在此处展示 MATLAB Engine 执行结果")

    # 验证阶段占位
    with st.expander("✅ 第四步：结果验证", expanded=True):
        st.info("🔜 **开发中** — 将在此处展示自动验证结果")


# ============================================================================
# 入口
# ============================================================================
if __name__ == "__main__":
    main()
