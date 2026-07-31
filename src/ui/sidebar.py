"""
侧边栏 UI 组件
提供问题类型选择、LLM 设置、历史记录等功能
"""

import os

import streamlit as st
from dotenv import load_dotenv

# 自动加载 .env
_load_dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(_load_dotenv_path)

_LLM_DEFAULT_API_KEY = os.environ.get("LLM_API_KEY", "")
_LLM_DEFAULT_API_BASE = os.environ.get("LLM_API_BASE", "https://api.openai.com/v1")
_LLM_DEFAULT_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

# 问题类型定义
PROBLEM_TYPES = {
    "分类问题": {
        "icon": "🏷️",
        "description": "将数据点划分到预定义的类别中",
        "algorithms": ["决策树", "SVM", "KNN", "逻辑回归", "随机森林", "神经网络"],
    },
    "回归问题": {
        "icon": "📈",
        "description": "预测连续的数值输出",
        "algorithms": ["线性回归", "多项式回归", "岭回归", "SVR", "高斯过程"],
    },
    "优化问题": {
        "icon": "🎯",
        "description": "在约束条件下寻找最优解",
        "algorithms": ["梯度下降", "牛顿法", "线性规划", "遗传算法", "模拟退火"],
    },
    "微分方程": {
        "icon": "🔢",
        "description": "求解常微分方程或偏微分方程",
        "algorithms": ["欧拉法", "龙格-库塔法", "有限差分法", "有限元法", "谱方法"],
    },
    "统计分析": {
        "icon": "📊",
        "description": "数据分布的统计推断和假设检验",
        "algorithms": ["t检验", "卡方检验", "ANOVA", "贝叶斯推断", "主成分分析"],
    },
    "信号处理": {
        "icon": "〰️",
        "description": "信号的变换、滤波和频谱分析",
        "algorithms": ["FFT", "小波变换", "滤波设计", "卷积", "希尔伯特变换"],
    },
    "数值计算": {
        "icon": "🧮",
        "description": "数值积分、微分、插值等通用计算",
        "algorithms": ["数值积分", "数值微分", "插值", "拟合", "求根"],
    },
    "矩阵运算": {
        "icon": "🔲",
        "description": "矩阵分解、特征值、线性方程组等",
        "algorithms": ["LU分解", "QR分解", "SVD", "特征值", "迭代求解"],
    },
}


def render_sidebar() -> dict:
    """
    渲染整个侧边栏，返回用户配置

    Returns:
        dict: {
            'problem_type': str,
            'problem_description': str,
            'llm_model': str,
            'llm_api_key': str,
            'matlab_available': bool,
        }
    """
    config = {}

    with st.sidebar:
        st.markdown("# ⚙️ 配置面板")

        # --- 问题类型 ---
        config['problem_type'] = _render_problem_type()

        st.divider()

        # --- LLM 设置 ---
        llm_settings = _render_llm_settings()
        config.update(llm_settings)

        st.divider()

        # --- MATLAB 状态 ---
        config['matlab_available'] = _render_matlab_status()

        st.divider()

        # --- 使用帮助 ---
        _render_help()

        st.divider()

        # --- 页脚 ---
        st.markdown(
            "<small style='color: #888;'>MATLAB 算法智能分析平台 v1.0<br>"
            "Powered by LLM + MATLAB Engine</small>",
            unsafe_allow_html=True,
        )

    return config


def _render_problem_type() -> str:
    """渲染问题类型选择器 — 默认自动判断，用户可手动覆盖"""
    st.markdown("### 🎯 问题类型")

    # 构建选项列表：「自动判断」排在第一位
    problem_types = list(PROBLEM_TYPES.keys())
    options = ["🤖 自动判断（推荐）"] + problem_types

    selected = st.selectbox(
        "问题类型（可留空，由LLM自动分类）",
        options=options,
        format_func=lambda x: (
            x if x.startswith("🤖") else f"{PROBLEM_TYPES[x]['icon']} {x}"
        ),
        key="problem_type_select",
    )

    # 用户手动选择了具体类型
    if selected in PROBLEM_TYPES:
        info = PROBLEM_TYPES[selected]
        st.caption(f"📌 已手动指定：{info['description']}")

        with st.expander("📋 该类型候选算法", expanded=False):
            st.caption("提交后 LLM 决策树将从以下算法中择优：")
            for algo in info['algorithms']:
                st.markdown(f"- {algo}")
        return selected

    # 选择了「自动判断」
    st.caption("🧠 系统将通过决策树自动分析问题描述并分类")
    st.caption("覆盖范围：全部 8 个领域、50+ 种算法")

    with st.expander("📋 系统可识别的全部算法", expanded=False):
        for ptype, info in PROBLEM_TYPES.items():
            st.markdown(f"**{info['icon']} {ptype}** — {info['description']}")
            st.caption("  " + " · ".join(info['algorithms']))

    return None  # None 表示「待 LLM 自动判断」


def _render_llm_settings() -> dict:
    """渲染 LLM 配置区域"""
    st.markdown("### 🤖 LLM 设置")

    model = st.selectbox(
        "模型选择",
        options=["deepseek-chat", "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "claude-3.5-sonnet"],
        index=0 if _LLM_DEFAULT_MODEL == "deepseek-chat" else 2,
        key="llm_model",
        help="选择用于决策树推理和代码生成的大语言模型",
    )

    api_key = st.text_input(
        "API Key",
        type="password",
        value=_LLM_DEFAULT_API_KEY,
        key="llm_api_key",
        placeholder="sk-...（已从 .env 自动加载）",
        help="LLM 服务的 API Key。已从 .env 文件自动读取，无需手动填写。",
    )

    api_base = st.text_input(
        "API Base URL（可选）",
        value=_LLM_DEFAULT_API_BASE,
        key="llm_api_base",
        placeholder="https://api.openai.com/v1",
        help="自定义 API 端点。已从 .env 文件自动读取。",
    )

    return {
        'llm_model': model,
        'llm_api_key': api_key,
        'llm_api_base': api_base,
    }


def _render_matlab_status() -> bool:
    """渲染 MATLAB 连接状态"""
    st.markdown("### 🔌 MATLAB 状态")

    try:
        import matlab.engine
        # 尝试检查是否可用（不实际启动引擎以节省时间）
        st.success("✅ MATLAB Engine 已安装")
        return True
    except ImportError:
        st.warning("⚠️ MATLAB Engine 未安装")
        st.caption("Python 代码将生成但无法直接调用 MATLAB。")
        st.caption("安装方法：`pip install matlabengine`")
        return False


def _render_help():
    """渲染使用帮助"""
    st.markdown("### ❓ 使用帮助")

    with st.expander("如何使用", expanded=False):
        st.markdown("""
        **步骤：**
        1. 在主区域用自然语言描述您的问题
        2. 上传待分析的数据文件（可选）
        3. （可选）手动输入公式或选择问题类型来引导 LLM
        4. 点击「提交分析」按钮
        
        **系统将自动完成：**
        - 🌳 决策树分析 → 问题类型分类
        - 🔍 算法推荐 → 匹配最优算法
        - 📐 公式推荐 → 匹配数学表达式
        - 💻 代码生成 → Python + MATLAB 脚本
        
        **手动引导（可选）：**
        - 左侧选择问题类型 → 缩小算法搜索范围
        - 输入 LaTeX 公式 → 提高代码生成精度
        """)

    with st.expander("快捷键", expanded=False):
        st.markdown("""
        - `Ctrl+Enter`：提交分析
        - 点击符号按钮：快速插入 LaTeX 命令
        - 点击模板：插入预设公式
        """)
