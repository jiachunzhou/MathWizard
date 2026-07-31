"""
公式输入 UI 组件
提供 LaTeX 公式输入、实时预览、模板插入等功能
"""

from typing import Optional

import streamlit as st

from src.utils.latex_utils import (
    LATEX_TEMPLATES,
    GREEK_LETTERS,
    MATH_SYMBOLS,
    get_all_categories,
    get_templates_by_category,
    validate_latex,
    wrap_display_math,
)


def render_formula_input() -> str:
    """
    渲染公式输入区域，返回用户输入的 LaTeX 源码

    Returns:
        str: 用户输入的 LaTeX 公式字符串
    """
    st.markdown("### 📐 数学公式输入")

    # 使用两列布局：左边输入，右边预览
    col_input, col_preview = st.columns([1, 1])

    with col_input:
        # LaTeX 源码输入区
        latex_input = st.text_area(
            label="LaTeX 公式源码",
            value=st.session_state.get("latex_input", ""),
            height=200,
            placeholder=r"在此输入 LaTeX 公式，例如：\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}",
            key="latex_text_area",
            help="支持标准 LaTeX 数学语法。可使用 $$...$$ 或 $...$ 包裹公式。",
        )

        # 保存到 session state
        st.session_state["latex_input"] = latex_input

        # 公式语法验证
        if latex_input.strip():
            is_valid = validate_latex(latex_input)
            if not is_valid:
                st.warning("⚠️ LaTeX 语法可能有误：括号或环境未正确配对，请检查。")

        # 快捷符号栏
        st.markdown("**快捷符号**")
        _render_symbol_shortcuts()

    with col_preview:
        st.markdown("**公式预览**")
        _render_latex_preview(latex_input)

    return latex_input


def render_formula_templates() -> Optional[str]:
    """
    渲染公式模板选择器，返回选中的模板 LaTeX 源码

    Returns:
        str | None: 被选中的模板源码
    """
    st.markdown("**公式模板库**")

    categories = get_all_categories()
    selected_category = st.selectbox(
        "选择分类",
        categories,
        key="template_category",
    )

    if selected_category:
        templates = get_templates_by_category(selected_category)
        template_names = list(templates.keys())

        # 使用列布局展示模板按钮
        cols_per_row = 2
        for i in range(0, len(template_names), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(template_names):
                    name = template_names[idx]
                    latex_src = templates[name]
                    with col:
                        # 显示模板名和预览
                        if st.button(
                            f"📌 {name}",
                            key=f"tpl_{selected_category}_{name}",
                            use_container_width=True,
                            help=f"点击插入: {latex_src}",
                        ):
                            return latex_src

    return None


def _render_latex_preview(latex_input: str):
    """渲染 LaTeX 公式预览"""
    if not latex_input.strip():
        st.info("输入公式后将在此处实时预览")
        return

    # 尝试渲染
    lines = latex_input.strip().split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        try:
            # 如果用户已经包裹了 $$ 或 $，直接渲染
            if line.startswith('$$') and line.endswith('$$'):
                st.latex(line[2:-2])
            elif line.startswith('$') and line.endswith('$'):
                st.latex(line[1:-1])
            elif line.startswith(r'\[') and line.endswith(r'\]'):
                st.latex(line[2:-2])
            elif line.startswith(r'\(') and line.endswith(r'\)'):
                st.latex(line[2:-2])
            else:
                st.latex(line)
        except Exception:
            # LaTeX 渲染失败时显示原始文本
            st.code(line, language="latex")


def _render_symbol_shortcuts():
    """渲染快捷符号按钮"""
    tab_greek, tab_symbol = st.tabs(["希腊字母", "数学符号"])

    with tab_greek:
        _render_symbol_button_grid(GREEK_LETTERS, "greek")

    with tab_symbol:
        _render_symbol_button_grid(MATH_SYMBOLS, "math")


def _render_symbol_button_grid(symbols: dict, prefix: str):
    """渲染符号按钮网格"""
    symbols_list = list(symbols.items())
    cols_per_row = 8

    for i in range(0, len(symbols_list), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(symbols_list):
                symbol, latex_cmd = symbols_list[idx]
                with col:
                    if st.button(
                        symbol,
                        key=f"sym_{prefix}_{idx}",
                        use_container_width=True,
                        help=f"插入: {latex_cmd}",
                    ):
                        # 在光标位置插入 LaTeX 命令
                        current = st.session_state.get("latex_input", "")
                        st.session_state["latex_input"] = current + " " + latex_cmd
                        st.rerun()


def insert_template_to_input(template_latex: str):
    """将模板 LaTeX 插入到输入框"""
    current = st.session_state.get("latex_input", "")
    if current:
        st.session_state["latex_input"] = current + "\n" + template_latex
    else:
        st.session_state["latex_input"] = template_latex
