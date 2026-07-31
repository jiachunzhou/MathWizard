"""
MATLAB 算法智能分析平台 — 主入口
基于 Streamlit 的数学问题分析 Web 应用

功能：
1. 复杂数学公式输入（LaTeX）+ 实时预览
2. 数据文件上传（CSV/Excel/TXT）
3. LLM 决策树算法选择 ✅
4. Python 代码生成 + MATLAB 调用（后续阶段）
5. 结果验证（后续阶段）
"""

import streamlit as st

from src.ui.formula_input import render_formula_input, render_formula_templates, insert_template_to_input
from src.ui.file_upload import render_file_upload
from src.ui.sidebar import render_sidebar, PROBLEM_TYPES
from src.ui.decision_display import render_decision_tab
from src.core.pipeline import run_analysis_pipeline


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
        "analysis_completed": False,
        "analysis_result": None,
        "algorithm_confirmed": False,
        "confirmed_algorithm": None,
        "confirmed_decision": None,
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

    # 标签页：输入界面 | 算法决策 | 分析结果
    tab_input, tab_decision, tab_result = st.tabs([
        "📝 问题输入",
        "🌳 算法决策",
        "📊 分析结果",
    ])

    with tab_input:
        render_input_tab(config)

    with tab_decision:
        render_decision_tab()

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
    # ---- 演示按钮 ----
    _render_demo_shortcuts()

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

    # ---- 文件上传（或展示演示数据） ----
    demo_data = st.session_state.get("uploaded_data")
    demo_file = st.session_state.get("file_name", "")
    is_demo = bool(demo_file and st.session_state.get("_demo_data_ok"))

    if is_demo and demo_data is not None:
        st.markdown("### 📂 数据文件（演示模式）")
        st.success(f"✅ 已加载演示数据: **{demo_file}** ({demo_data.shape[0]}行 × {demo_data.shape[1]}列)")
        with st.expander("🔍 数据预览", expanded=True):
            st.dataframe(demo_data.head(10), use_container_width=True)
        uploaded_df = demo_data
    else:
        uploaded_df = render_file_upload()

    st.divider()

    # ---- 提交区域 ----
    render_submit_area(config, problem_description, latex_input, uploaded_df)


def render_submit_area(config: dict, description: str, latex: str, df):
    """渲染提交按钮和状态检查"""
    st.markdown("### 🚀 提交分析")

    # 状态检查（问题类型由 LLM 自动判断，不需要用户填写）
    checks = []
    checks.append(("问题描述", bool(description.strip())))
    checks.append(("数据文件", df is not None))
    checks.append(("问题类型", True))  # 始终通过 — LLM 自动分类

    # 显示状态
    cols = st.columns(len(checks))
    for i, (name, ok) in enumerate(checks):
        with cols[i]:
            if ok:
                if name == "问题类型":
                    st.success(f"🤖 {name}（自动判断）")
                else:
                    st.success(f"✅ {name}")
            else:
                st.info(f"⏳ {name}")

    # 准备就绪判断（只需要问题描述）
    ready = checks[0][1]

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
            st.caption("⚠️ 请至少填写问题描述后再提交")
        else:
            st.caption("✅ 准备就绪 — 系统将自动：分类 → 选算法 → 推荐公式 → 生成代码")

    if submitted:
        st.session_state["analysis_submitted"] = True
        st.session_state["submission_data"] = {
            "problem_type": config.get('problem_type') or "🤖 待 LLM 自动分类",
            "description": description,
            "latex_formula": latex if latex.strip() else "🤖 待 LLM 自动推断",
            "data_shape": df.shape if df is not None else None,
            "data_columns": df.columns.tolist() if df is not None else None,
            "llm_model": config.get('llm_model'),
        }

        # ---- 调用分析流水线 ----
        with st.spinner("🚀 正在执行分析流水线..."):
            try:
                results = run_analysis_pipeline(
                    description=description,
                    df=df,
                    latex_formula=latex,
                    problem_type_override=config.get('problem_type'),
                    llm_model=config.get('llm_model', 'gpt-4o-mini'),
                    llm_api_key=config.get('llm_api_key', ''),
                    llm_api_base=config.get('llm_api_base', ''),
                )
                st.success("✅ 分析完成！")
            except Exception as e:
                st.error(f"❌ 分析过程出错：{str(e)}")
                st.info(
                    "💡 **离线模式提示**：如果未配置 LLM API Key，"
                    "系统会自动使用关键词规则引擎进行语义分析。"
                )

        # 展示提交摘要
        with st.expander("📋 提交摘要", expanded=False):
            st.json(st.session_state["submission_data"])

        st.info(
            "💡 **下一步：**\n\n"
            "1. 🌳 切换到「**算法决策**」标签页 → 查看 LLM 决策树推理过程\n"
            "2. 📊 切换到「**分析结果**」标签页 → 查看生成的代码与验证结果"
        )


def render_result_tab():
    """渲染分析结果标签页 — 代码生成 + 执行结果 + 验证"""
    if not st.session_state.get("analysis_submitted"):
        st.info("👈 请先在「📝 问题输入」中填写问题描述并提交分析")
        return

    st.markdown("## 📊 分析结果")

    submission = st.session_state.get("submission_data", {})

    # ---- 第一步：Python 代码 ----
    _render_code_section(submission)

    st.divider()

    # ---- 第二步：MATLAB 执行结果 ----
    _render_matlab_result_section()

    st.divider()

    # ---- 第三步：结果验证 ----
    _render_validation_section(submission)


def _render_code_section(submission: dict):
    """渲染 Python/MATLAB 代码展示区"""
    st.markdown("### 💻 生成的代码")

    tab_py, tab_matlab = st.tabs(["🐍 Python 代码", "🔧 MATLAB 代码"])

    with tab_py:
        st.caption("LLM 自动生成的 Python 调用代码")
        st.code(
            _get_placeholder_python_code(submission),
            language="python",
            line_numbers=True,
        )

    with tab_matlab:
        st.caption("等效的 MATLAB 原生代码")
        st.code(
            _get_placeholder_matlab_code(submission),
            language="matlab",
            line_numbers=True,
        )

    # 代码说明
    with st.expander("📋 代码说明", expanded=False):
        st.markdown("""
        | 模块 | 说明 |
        |------|------|
        | 数据预处理 | 标准化、缺失值处理、特征选择 |
        | 模型构建 | 根据决策树选择的算法构建模型 |
        | MATLAB 调用 | 通过 `matlab.engine` 桥接 MATLAB 引擎 |
        | 结果回传 | 将 MATLAB 计算结果转换回 Python 数据结构 |
        """)


def _render_matlab_result_section():
    """渲染 MATLAB 执行结果"""
    st.markdown("### ⚡ MATLAB 执行结果")

    col_out, col_viz = st.columns(2)

    with col_out:
        st.markdown("**数值输出**")
        st.info(
            "🔜 此处将展示 MATLAB Engine 的原始输出，包括：\n\n"
            "- 回归系数 / 特征值 / 优化结果\n"
            "- 收敛信息与迭代次数\n"
            "- 执行时间统计"
        )

    with col_viz:
        st.markdown("**可视化结果**")
        st.info(
            "🔜 此处将展示 MATLAB 生成的图表：\n\n"
            "- 拟合曲线 vs 原始数据\n"
            "- 残差分布图\n"
            "- 特征重要性排序"
        )


def _render_validation_section(submission: dict):
    """渲染结果验证区"""
    st.markdown("### ✅ 结果验证")

    # 验证维度
    checks = [
        ("残差正态性检验", "Shapiro-Wilk / Kolmogorov-Smirnov", "验证模型假设"),
        ("多重共线性检验", "VIF（方差膨胀因子）", "检测特征冗余"),
        ("交叉验证", "K-Fold Cross Validation", "评估泛化能力"),
        ("残差异方差检验", "Breusch-Pagan / White", "验证方差齐性"),
        ("影响点诊断", "Cook's Distance", "检测异常影响点"),
        ("预测误差评估", "MAE / RMSE / MAPE", "量化预测精度"),
    ]

    for i, (name, method, purpose) in enumerate(checks):
        status_color = "#ccc"
        status_text = "⏳ 待验证"

        st.markdown(f"""
        <div style="display:flex;align-items:center;margin:6px 0;padding:10px 14px;
                    background:#fafafa;border-radius:8px;border:1px solid #eee;">
            <span style="font-size:1.2rem;margin-right:12px;">{status_text}</span>
            <div>
                <strong>{name}</strong>
                <span style="color:#888;margin-left:8px;font-size:0.85rem;">
                    方法：{method}
                </span>
            </div>
            <span style="margin-left:auto;color:#aaa;font-size:0.8rem;">{purpose}</span>
        </div>
        """, unsafe_allow_html=True)

    st.caption("🔜 提交分析后，验证模块将自动执行以上所有检验并输出结论")


def _get_placeholder_python_code(submission: dict) -> str:
    """生成占位 Python 代码（后续由 LLM 生成）"""
    problem_type = submission.get("problem_type", "待分析")
    has_data = submission.get("data_shape") is not None

    lines = [
        '"""',
        f'MathWizard 自动生成代码',
        f'问题类型: {problem_type}',
        f'数据来源: {"上传文件" if has_data else "示例数据"}',
        f'生成时间: 提交分析后自动生成',
        '"""',
        '',
        'import numpy as np',
        'import pandas as pd',
        'from scipy import stats, optimize, linalg',
        '',
        '',
        '# ============================================================',
        '# 1. 数据加载与预处理',
        '# ============================================================',
        '',
    ]

    if has_data:
        shape = submission.get("data_shape", (0, 0))
        cols = submission.get("data_columns", [])
        lines.extend([
            f'# 加载上传数据: {shape[0]} 行 × {shape[1]} 列',
            f'# 列名: {", ".join(cols[:5])}{"..." if len(cols) > 5 else ""}',
            '# df = pd.read_csv("uploaded_file.csv")',
            '',
            '# 数据预处理',
            '# - 缺失值检测与处理',
            '# - 标准化 / 归一化',
            '# - 特征选择 / 降维',
            '',
        ])
    else:
        lines.extend([
            '# 无上传数据，使用示例数据',
            '# np.random.seed(42)',
            '# X = np.random.randn(100, 5)',
            '# y = 3*X[:,0] + 2*X[:,1] + np.random.randn(100)*0.5',
            '',
        ])

    lines.extend([
        '',
        '# ============================================================',
        '# 2. 算法实现（由 LLM 决策树选择）',
        '# ============================================================',
        '',
        '# 算法选择理由将在此处注释',
        '# 决策树路径: 语义分析 → 数据特征 → 问题分类 → 算法匹配',
        '',
        '',
        '# ============================================================',
        '# 3. 调用 MATLAB Engine',
        '# ============================================================',
        '',
        '# import matlab.engine',
        '# eng = matlab.engine.start_matlab()',
        '#',
        '# # 将数据传入 MATLAB 工作区',
        '# eng.workspace["X"] = matlab.double(X.tolist())',
        '# eng.workspace["y"] = matlab.double(y.tolist())',
        '#',
        '# # 调用 MATLAB 函数',
        '# result = eng.some_matlab_function(nargout=1)',
        '#',
        '# eng.quit()',
        '',
        '',
        '# ============================================================',
        '# 4. 结果处理与可视化',
        '# ============================================================',
        '',
        '# import matplotlib.pyplot as plt',
        '#',
        '# # 绘制结果',
        '# fig, axes = plt.subplots(1, 2, figsize=(12, 5))',
        '# ...',
        '# plt.show()',
    ])

    return '\n'.join(lines)


def _get_placeholder_matlab_code(submission: dict) -> str:
    """生成占位 MATLAB 代码"""
    problem_type = submission.get("problem_type", "待分析")

    return f"""% MathWizard 自动生成 MATLAB 代码
% 问题类型: {problem_type}
% 生成时间: 提交分析后自动生成

% ============================================================
% 1. 数据加载
% ============================================================
% data = readtable('data.csv');
% X = data{{:, 1:end-1}};
% y = data{{:, end}};

% ============================================================
% 2. 核心算法
% ============================================================
% 算法由 LLM 决策树自动选择
% 示例（线性回归）:
%   model = fitlm(X, y);
%   disp(model);

% ============================================================
% 3. 结果可视化
% ============================================================
% figure;
% plot(y, 'b-o'); hold on;
% plot(predict(model, X), 'r--');
% legend('实际值', '预测值');
% title('模型拟合结果');

% ============================================================
% 4. 残差分析
% ============================================================
% residuals = model.Residuals.Raw;
% figure;
% qqplot(residuals);
% title('残差正态性检验');
"""


# ============================================================================
# 演示场景快捷入口
# ============================================================================

import os as _os

DEMO_SCENARIOS = [
    {
        "icon": "📈",
        "name": "曲线拟合 — 多项式回归",
        "description": (
            "对附件中的数据 (demo_poly_fit.csv) 进行多项式回归拟合。"
            "数据包含自变量 x 和因变量 y，y 含测量噪声。"
            "请找出 x 和 y 之间的函数关系 y = f(x)，"
            "使用最小二乘法确定多项式系数。"
        ),
        "data_file": "demo_poly_fit.csv",
        "data_dir": "data/samples",
    },
    {
        "icon": "📐",
        "name": "插值与逼近 — 三次样条插值",
        "description": (
            "已知 12 个离散数据点 (demo_interpolation.csv)，"
            "需要构造一条光滑曲线通过所有这些点。"
            "数据点分布不均匀，要求插值曲线具有 C² 连续性。"
            "请推荐最适合的插值算法。"
        ),
        "data_file": "demo_interpolation.csv",
        "data_dir": "data/samples",
    },
    {
        "icon": "🔲",
        "name": "线性方程组 — 三对角稀疏矩阵",
        "description": (
            "求解线性方程组 Ax = b，其中 A 是一个 100×100 的三对角稀疏矩阵"
            "（主对角线元素为 2，次对角线元素为 -1），"
            "b 为全 1 向量。矩阵规模中等，具有稀疏结构。"
            "请推荐最合适的求解算法。"
        ),
        "data_file": "demo_linear_system.csv",
        "data_dir": "data/samples",
    },
    {
        "icon": "🎯",
        "name": "非线性方程 — 牛顿法求根",
        "description": (
            "求解非线性方程 f(x) = x³ - 2x - 5 = 0 在区间 [1, 4] 内的根。"
            "已知 f(2) = -1 < 0, f(3) = 16 > 0，"
            "函数在区间内连续且单调递增。需要高精度结果。"
        ),
        "data_file": "demo_nonlinear_root.csv",
        "data_dir": "data/samples",
    },
    {
        "icon": "🔢",
        "name": "常微分方程 — RK4 初值问题",
        "description": (
            "求解一阶常微分方程初值问题：dy/dt = -2y + sin(t), y(0) = 1。"
            "要求在 t ∈ [0, 3] 上以步长 h = 0.1 进行数值求解，"
            "需要高精度和误差控制。"
        ),
        "data_file": "demo_ode.csv",
        "data_dir": "data/samples",
    },
]


def _render_demo_shortcuts():
    """渲染演示场景快捷按钮 — 一键填充示例问题和数据"""
    st.markdown("### 🧪 快速演示")

    # 使用多列展示按钮
    cols = st.columns(len(DEMO_SCENARIOS))

    for i, (col, scene) in enumerate(zip(cols, DEMO_SCENARIOS)):
        with col:
            if st.button(
                f"{scene['icon']} {scene['name']}",
                key=f"demo_{i}",
                use_container_width=True,
                help=f"点击自动填充：{scene['name']}",
            ):
                # 填充问题描述
                st.session_state["problem_description"] = scene["description"]

                # 尝试多个路径加载数据文件
                import pandas as pd
                search_paths = [
                    _os.path.join(scene["data_dir"], scene["data_file"]),
                    _os.path.join("data", scene["data_file"]),
                    _os.path.join("data", "samples", scene["data_file"]),
                ]
                df = None
                for data_path in search_paths:
                    if _os.path.isfile(data_path):
                        df = pd.read_csv(data_path)
                        break
                if df is not None:
                    st.session_state["uploaded_data"] = df
                    st.session_state["file_name"] = scene["data_file"]
                    st.session_state["_demo_data_ok"] = True
                else:
                    st.session_state["_demo_data_ok"] = False
                    st.session_state["_demo_data_error"] = (
                        f"⚠️ 未找到 {scene['data_file']}，"
                        "请执行 git pull 获取最新数据文件。"
                    )

                st.rerun()

    # 如果有选中的演示场景，展示加载状态
    demo_name = st.session_state.get("file_name", "")
    if demo_name and st.session_state.get("_demo_data_ok"):
        st.success(f"✅ 已加载演示：{demo_name}")
        if st.button("❌ 清除演示数据", key="clear_demo"):
            for k in ["problem_description", "uploaded_data", "file_name",
                       "_demo_data_ok", "_demo_data_error"]:
                st.session_state.pop(k, None)
            st.rerun()
    elif st.session_state.get("_demo_data_error"):
        st.warning(st.session_state["_demo_data_error"])


# ============================================================================
# 入口
# ============================================================================
if __name__ == "__main__":
    main()
