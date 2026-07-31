# MathWizard — MATLAB 算法智能分析平台

基于大语言模型（LLM）的智能数学算法选择与代码生成平台，通过决策树确定最优算法，自动生成 Python 代码调用 MATLAB Engine 执行计算，并对结果进行自动验证。

## 功能架构

```
用户输入（公式 + 数据 + 问题描述）
       │
       ▼
┌─────────────────────┐
│  Streamlit 前端界面  │  ← 当前阶段 ✅
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  LLM 决策树引擎      │  ← 开发中 🔜
│  (算法选择与推理)     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Python 代码生成器   │  ← 开发中 🔜
│  (LLM → MATLAB API) │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  MATLAB Engine 执行  │  ← 开发中 🔜
│  (matlab.engine)     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  结果验证与可视化     │  ← 开发中 🔜
└─────────────────────┘
```

## 项目结构

```
MathWizard/
├── .gitignore                  # Git 忽略规则
├── README.md                   # 项目说明（本文件）
├── requirements.txt            # Python 依赖
├── app.py                      # Streamlit 应用主入口
│
├── src/                        # 源代码
│   ├── __init__.py
│   ├── ui/                     # 用户界面组件
│   │   ├── __init__.py
│   │   ├── formula_input.py    # LaTeX 公式输入 + 实时预览
│   │   ├── file_upload.py      # 数据文件上传 + 预览 + 统计
│   │   └── sidebar.py          # 侧边栏（问题类型/LLM配置）
│   ├── core/                   # 核心引擎（后续阶段）
│   │   ├── __init__.py
│   │   ├── decision_tree.py    # LLM 决策树算法选择
│   │   ├── code_generator.py   # LLM → Python 代码生成
│   │   └── validator.py        # 结果自动验证
│   └── utils/                  # 工具模块
│       ├── __init__.py
│       ├── latex_utils.py      # LaTeX 模板库 + 符号表 + 验证
│       └── data_parser.py      # 数据文件解析 + 统计分析
│
├── data/                       # 数据目录
│   └── uploads/                # 用户上传数据（gitignore）
│       └── .gitkeep
│
├── output/                     # 输出结果
│   └── .gitkeep
│
├── tests/                      # 测试
│   └── __init__.py
│
└── docs/                       # 文档
    └── .gitkeep
```

## 快速开始

### 环境要求

- Python 3.10+
- MATLAB R2023b+（需安装 MATLAB Engine API for Python）
- LLM API Key（OpenAI 兼容格式）

### 安装

```bash
# 克隆仓库
git clone <repo-url> MathWizard
cd MathWizard

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 运行

```bash
streamlit run app.py
```

浏览器访问 `http://localhost:8501`

### 安装 MATLAB Engine API（可选）

```bash
cd <MATLAB安装目录>/extern/engines/python
python setup.py install
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | Streamlit |
| 公式渲染 | KaTeX (st.latex / st.markdown) |
| 数据处理 | pandas, numpy, scipy |
| 可视化 | matplotlib |
| LLM 接口 | OpenAI API 兼容格式 |
| MATLAB 桥接 | matlab.engine (MATLAB Engine API for Python) |

## 当前进度

- [x] **阶段一**：Streamlit 输入界面（公式 + 文件上传 + 问题描述）
- [ ] **阶段二**：LLM 决策树算法选择
- [ ] **阶段三**：Python 代码生成 + MATLAB 调用
- [ ] **阶段四**：结果验证与可视化
