"""
数据解析工具模块
支持 CSV、Excel、TXT 等格式的文件解析、数据预览和统计分析
"""

import io
from typing import Optional, Tuple

import numpy as np
import pandas as pd


# 支持的文件类型
SUPPORTED_EXTENSIONS = {
    "csv": "CSV 文件",
    "xlsx": "Excel 工作簿 (.xlsx)",
    "xls": "Excel 工作簿 (.xls)",
    "txt": "文本文件",
    "dat": "数据文件",
}


def get_supported_formats() -> dict:
    """获取支持的文件格式"""
    return SUPPORTED_EXTENSIONS


def get_allowed_extensions() -> list:
    """获取 st.file_uploader 使用的扩展名列表"""
    return list(SUPPORTED_EXTENSIONS.keys())


def parse_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    根据文件扩展名解析上传的文件，返回 (DataFrame, error_message)
    
    Args:
        uploaded_file: Streamlit UploadedFile 对象
        
    Returns:
        (DataFrame | None, error_message | None)
    """
    if uploaded_file is None:
        return None, "未选择文件"

    file_name = uploaded_file.name.lower()

    try:
        if file_name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            return df, None

        elif file_name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            return df, None

        elif file_name.endswith(('.txt', '.dat')):
            # 尝试自动检测分隔符
            content = uploaded_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            uploaded_file.seek(0)

            # 尝试常见分隔符
            for sep in [',', '\t', ';', r'\s+']:
                try:
                    df = pd.read_csv(uploaded_file, sep=sep)
                    if df.shape[1] > 1:
                        return df, None
                    uploaded_file.seek(0)
                except Exception:
                    uploaded_file.seek(0)
                    continue

            # 默认用逗号
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file)
            return df, None

        else:
            return None, f"不支持的文件格式: {file_name.split('.')[-1]}"

    except UnicodeDecodeError:
        return None, "文件编码错误，请检查文件编码格式（建议使用 UTF-8）"
    except pd.errors.EmptyDataError:
        return None, "文件为空"
    except pd.errors.ParserError as e:
        return None, f"文件解析错误: {str(e)}"
    except Exception as e:
        return None, f"读取文件失败: {str(e)}"


def get_data_preview(df: pd.DataFrame, n_rows: int = 10) -> pd.DataFrame:
    """获取数据预览（前 N 行）"""
    return df.head(n_rows)


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    获取数据摘要统计信息
    
    Returns:
        dict: {
            'shape': (rows, cols),
            'columns': [...],
            'dtypes': {...},
            'numeric_columns': [...],
            'categorical_columns': [...],
            'missing_count': int,
            'missing_percent': float,
        }
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    missing_percent = (missing_cells / total_cells * 100) if total_cells > 0 else 0

    return {
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'numeric_columns': numeric_cols,
        'categorical_columns': categorical_cols,
        'missing_count': int(missing_cells),
        'missing_percent': round(missing_percent, 2),
    }


def get_numeric_stats(df: pd.DataFrame, columns: Optional[list] = None) -> pd.DataFrame:
    """
    获取数值列的描述性统计
    
    Args:
        df: 数据 DataFrame
        columns: 要统计的列名列表，None 表示所有数值列
        
    Returns:
        描述性统计 DataFrame (count, mean, std, min, 25%, 50%, 75%, max)
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    if not columns:
        return pd.DataFrame()

    stats = df[columns].describe()
    return stats


def get_column_unique_values(df: pd.DataFrame, column: str, max_unique: int = 50) -> dict:
    """
    获取某列的唯一值信息
    
    Returns:
        dict: {
            'unique_count': int,
            'values': list (最多 max_unique 个),
            'truncated': bool,
        }
    """
    if column not in df.columns:
        return {'unique_count': 0, 'values': [], 'truncated': False}

    unique_vals = df[column].dropna().unique()
    total_unique = len(unique_vals)

    return {
        'unique_count': total_unique,
        'values': unique_vals[:max_unique].tolist(),
        'truncated': total_unique > max_unique,
    }


def filter_dataframe(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """按列筛选 DataFrame"""
    valid_cols = [c for c in columns if c in df.columns]
    return df[valid_cols] if valid_cols else df


def get_missing_info(df: pd.DataFrame) -> pd.DataFrame:
    """获取每列的缺失值信息"""
    missing = pd.DataFrame({
        '列名': df.columns,
        '缺失数': df.isnull().sum().values,
        '缺失率 (%)': (df.isnull().sum() / len(df) * 100).round(2).values,
        '数据类型': df.dtypes.values,
    })
    missing = missing[missing['缺失数'] > 0].reset_index(drop=True)
    return missing
