"""
文件上传 UI 组件
支持 CSV、Excel、TXT 等格式上传，数据预览、列选择和统计信息展示
"""

from typing import Optional

import pandas as pd
import streamlit as st

from src.utils.data_parser import (
    get_allowed_extensions,
    get_data_preview,
    get_data_summary,
    get_missing_info,
    get_numeric_stats,
    parse_file,
)


def render_file_upload() -> Optional[pd.DataFrame]:
    """
    渲染文件上传区域

    Returns:
        pd.DataFrame | None: 解析后的数据，未上传则返回 None
    """
    st.markdown("### 📂 数据文件上传")

    uploaded_file = st.file_uploader(
        label="上传待分析的数据文件",
        type=get_allowed_extensions(),
        help="支持 CSV、Excel (.xlsx/.xls)、TXT、DAT 格式",
        key="data_file_uploader",
    )

    if uploaded_file is None:
        # 展示上传区域的占位说明
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.info("📄 **CSV**\n逗号分隔值文件")
        with col_b:
            st.info("📊 **Excel**\n.xlsx / .xls 工作簿")
        with col_c:
            st.info("📝 **TXT/DAT**\n文本/数据文件")
        return None

    # 解析文件
    with st.spinner("正在解析文件..."):
        df, error = parse_file(uploaded_file)

    if error:
        st.error(f"❌ {error}")
        return None

    if df is None or df.empty:
        st.warning("⚠️ 文件为空或无法解析")
        return None

    # 保存到 session state
    st.session_state["uploaded_data"] = df
    st.session_state["file_name"] = uploaded_file.name

    # 显示数据信息
    st.success(f"✅ 成功加载: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

    # --- 数据摘要 ---
    summary = get_data_summary(df)
    _render_data_summary(summary)

    # --- 数据预览 ---
    _render_data_preview(df)

    # --- 列选择 ---
    selected_columns = _render_column_selector(df)

    # --- 数值统计 ---
    _render_numeric_stats(df)

    # 返回选中的列数据
    if selected_columns:
        return df[selected_columns]
    return df


def _render_data_summary(summary: dict):
    """渲染数据摘要信息"""
    with st.expander("📋 数据摘要", expanded=True):
        rows, cols = summary['shape']
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("行数", f"{rows:,}")
        c2.metric("列数", cols)
        c3.metric("数值列", len(summary['numeric_columns']))
        c4.metric("缺失率", f"{summary['missing_percent']}%")

        # 列类型
        st.markdown("**列信息**")
        col_info = pd.DataFrame({
            "列名": summary['columns'],
            "类型": [summary['dtypes'].get(c, "unknown") for c in summary['columns']],
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True)

        # 缺失信息
        if summary['missing_count'] > 0:
            st.markdown(f"**缺失值详情**（总计 {summary['missing_count']} 个）")


def _render_data_preview(df: pd.DataFrame):
    """渲染数据预览表格"""
    with st.expander("🔍 数据预览", expanded=True):
        n_rows = st.slider(
            "预览行数", min_value=5, max_value=100, value=10, step=5,
            key="preview_rows",
        )
        preview = get_data_preview(df, n_rows)
        st.dataframe(preview, use_container_width=True)


def _render_column_selector(df: pd.DataFrame) -> list:
    """渲染列选择器"""
    with st.expander("🎯 选择分析列", expanded=False):
        all_columns = df.columns.tolist()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        select_all = st.checkbox("全选", value=True, key="select_all_columns")

        if select_all:
            default_cols = all_columns
        else:
            default_cols = numeric_cols if numeric_cols else all_columns

        selected = st.multiselect(
            "选择要参与计算的列",
            options=all_columns,
            default=default_cols,
            key="selected_columns",
        )

        if not selected:
            st.warning("请至少选择一列数据")
            return all_columns

        return selected


def _render_numeric_stats(df: pd.DataFrame):
    """渲染数值统计信息"""
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    if not numeric_cols:
        return

    with st.expander("📊 数值统计", expanded=False):
        stats_df = get_numeric_stats(df)
        st.dataframe(stats_df, use_container_width=True)

        # 缺失值详情
        missing_df = get_missing_info(df)
        if not missing_df.empty:
            st.markdown("**含缺失值的列**")
            st.dataframe(missing_df, use_container_width=True, hide_index=True)
