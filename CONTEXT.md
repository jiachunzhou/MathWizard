# MathWizard 项目上下文

## 项目定位
基于大语言模型（LLM）的智能数学算法选择与代码生成平台。
通过决策树确定最优算法，自动生成 Python 代码调用 MATLAB Engine 执行计算，并对结果进行自动验证。

## 技术栈
- 前端：Streamlit（三栏标签页布局 + 自定义 CSS）
- 数据处理：pandas, numpy, scipy
- LLM：OpenAI 兼容 API（支持关键词规则引擎回退）
- MATLAB 桥接：matlab.engine（MATLAB Engine API for Python）

## Git 仓库
https://github.com/jiachunzhou/MathWizard

## 项目结构
```
MathWizard/
├── app.py                        # Streamlit 主入口
├── requirements.txt
├── .gitignore
├── README.md
├── src/
│   ├── ui/
│   │   ├── formula_input.py      # LaTeX 公式输入 + 实时预览 + 40+ 模板
│   │   ├── file_upload.py        # 数据文件上传 + 预览 + 统计
│   │   ├── sidebar.py            # 侧边栏（问题类型默认自动判断/LLM配置）
│   │   └── decision_display.py   # 决策树可视化（双维度分析+路径时间线）
│   ├── core/
│   │   ├── data_analyzer.py      # 数据特征自动分析（6维度）
│   │   ├── algorithm_kb.py       # 数值分析算法知识库（29种算法）
│   │   ├── semantic_analyzer.py  # LLM 语义分析（API + 关键词回退）
│   │   ├── decision_engine.py    # 决策树推理引擎（4步流程）
│   │   └── pipeline.py           # 分析流水线编排器
│   └── utils/
│       ├── latex_utils.py        # LaTeX 模板库 + 符号表 + 验证
│       └── data_parser.py        # 数据文件解析 + 统计分析
├── data/samples/                 # 演示数据集
│   └── demo_house_price.csv      # 100条房价多元回归数据
├── tests/
└── docs/
```

## 当前进度

### ✅ 第一阶段：Streamlit 输入界面
- LaTeX 公式输入 + 实时预览（7大分类40+模板）
- 文件上传（CSV/Excel/TXT）+ 数据预览 + 统计摘要
- 侧边栏（问题类型默认「🤖 自动判断」+ LLM 配置）
- 三栏标签页：📝 问题输入 | 🌳 算法决策 | 📊 分析结果
- 代码展示区（Python/MATLAB 代码骨架 + 行号高亮）
- 结果验证区（6 项检验占位）

### ✅ 第二阶段：LLM 决策树后端引擎
- **data_analyzer.py**：6大维度（规模/稀疏性/质量/结构/数值分布/量纲）
- **algorithm_kb.py**：29种算法（插值/拟合/积分/微分/线性方程组/非线性/特征值/ODE）
  - 56个关键词 → 111条映射
  - 每种算法含：适用条件、禁忌、复杂度、稳定性、MATLAB函数
- **semantic_analyzer.py**：LLM API 调用 + 关键词规则引擎回退
- **decision_engine.py**：4步推理（分类→候选→数据约束→排序）
- **pipeline.py**：总调度器，结果写入 session_state

### 🔜 第三阶段：待定（代码生成 / MATLAB集成 / 结果验证）

## 关键设计决策
1. 问题类型默认「自动判断」，用户可手动覆盖
2. 公式输入可选，留空时 LLM 从描述推断
3. 决策树双维度：自然语言 + 数据特征
4. 支持无 API Key 离线运行（关键词规则引擎）
5. 算法范围限定本科数值分析课程（暂不扩展到全部 MATLAB 算法）

## 交互流程
```
用户输入（自然语言 + 可选公式 + 可选数据）
  → 点击「提交分析」
  → pipeline.py 串联执行：
    1. 数据特征分析（本地计算）
    2. 语义分析（LLM 或关键词回退）
    3. 决策树推理（双维度整合）
  → 结果写入 session_state
  → 🌳 算法决策标签页展示推理过程
  → 📊 分析结果标签页展示代码/验证（占位）
```

## 对新会话的提示
- 继续开发前，先 `git pull` 确保代码最新
- 当前阶段：第二阶段已完成，等待开启第三阶段
- 第三阶段方向：Python 代码生成（LLM → MATLAB 调用代码）、MATLAB Engine 实际集成、结果验证逻辑实现
- 所有 LLM 调用都通过 OpenAI 兼容 API，API Key 可从侧边栏配置或环境变量 OPENAI_API_KEY
- 项目运行方式：`streamlit run app.py`
- 演示数据：`data/samples/demo_house_price.csv`（100条房价回归数据）
