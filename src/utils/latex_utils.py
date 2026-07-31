"""
LaTeX 公式工具模块
提供公式模板库、LaTeX 验证、渲染辅助等功能
"""

import re
from typing import Optional

# ============================================================================
# 公式模板库
# ============================================================================

# 模板分类结构：{分类名: {模板名: LaTeX源码}}
LATEX_TEMPLATES = {
    "微积分": {
        "定积分": r"\int_{a}^{b} f(x)\,dx",
        "不定积分": r"\int f(x)\,dx",
        "二重积分": r"\iint_{D} f(x,y)\,dx\,dy",
        "三重积分": r"\iiint_{V} f(x,y,z)\,dx\,dy\,dz",
        "一阶导数": r"\frac{d}{dx}f(x)",
        "高阶导数": r"\frac{d^n}{dx^n}f(x)",
        "偏导数": r"\frac{\partial f}{\partial x}",
        "梯度": r"\nabla f(x,y,z)",
        "极限": r"\lim_{x \to a} f(x)",
    },
    "线性代数": {
        "矩阵 2×2": r"\begin{bmatrix} a & b \\ c & d \end{bmatrix}",
        "矩阵 3×3": r"\begin{bmatrix} a_{11} & a_{12} & a_{13} \\ a_{21} & a_{22} & a_{23} \\ a_{31} & a_{32} & a_{33} \end{bmatrix}",
        "行列式": r"\begin{vmatrix} a & b \\ c & d \end{vmatrix}",
        "特征值方程": r"\det(A - \lambda I) = 0",
        "向量": r"\vec{v} = \begin{bmatrix} v_1 \\ v_2 \\ v_3 \end{bmatrix}",
        "内积": r"\langle u, v \rangle",
        "范数": r"\|x\|_p = \left(\sum |x_i|^p\right)^{1/p}",
    },
    "概率统计": {
        "正态分布": r"f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}",
        "期望": r"E[X] = \int_{-\infty}^{\infty} x f(x)\,dx",
        "方差": r"\operatorname{Var}(X) = E[(X-\mu)^2]",
        "贝叶斯定理": r"P(A|B) = \frac{P(B|A)P(A)}{P(B)}",
        "似然函数": r"L(\theta|x) = \prod_{i=1}^{n} f(x_i|\theta)",
    },
    "优化问题": {
        "线性规划": r"\begin{aligned} \min \quad & c^T x \\ \text{s.t.} \quad & Ax \leq b \\ & x \geq 0 \end{aligned}",
        "最小二乘": r"\min_{x} \|Ax - b\|_2^2",
        "拉格朗日乘子": r"\mathcal{L}(x,\lambda) = f(x) + \lambda^T g(x)",
        "梯度下降": r"x_{k+1} = x_k - \alpha \nabla f(x_k)",
    },
    "微分方程": {
        "ODE 一阶": r"\frac{dy}{dt} = f(t, y)",
        "ODE 二阶": r"\frac{d^2y}{dt^2} + a\frac{dy}{dt} + by = 0",
        "PDE 热方程": r"\frac{\partial u}{\partial t} = \alpha \nabla^2 u",
        "PDE 波动方程": r"\frac{\partial^2 u}{\partial t^2} = c^2 \nabla^2 u",
    },
    "数值方法": {
        "牛顿法": r"x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}",
        "梯形法则": r"\int_a^b f(x)dx \approx \frac{h}{2}[f(a)+f(b)] + h\sum_{i=1}^{n-1} f(x_i)",
        "欧拉方法": r"y_{n+1} = y_n + h f(t_n, y_n)",
        "插值多项式": r"P(x) = \sum_{i=0}^{n} y_i \prod_{j\neq i} \frac{x-x_j}{x_i-x_j}",
    },
    "信号处理": {
        "傅里叶变换": r"F(\omega) = \int_{-\infty}^{\infty} f(t) e^{-i\omega t}\,dt",
        "傅里叶逆变换": r"f(t) = \frac{1}{2\pi}\int_{-\infty}^{\infty} F(\omega) e^{i\omega t}\,d\omega",
        "拉普拉斯变换": r"F(s) = \int_{0}^{\infty} f(t) e^{-st}\,dt",
        "卷积": r"(f * g)(t) = \int_{-\infty}^{\infty} f(\tau)g(t-\tau)\,d\tau",
    },
}

# 希腊字母表
GREEK_LETTERS = {
    "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta",
    "ε": r"\epsilon", "ζ": r"\zeta", "η": r"\eta", "θ": r"\theta",
    "λ": r"\lambda", "μ": r"\mu", "ν": r"\nu", "ξ": r"\xi",
    "π": r"\pi", "ρ": r"\rho", "σ": r"\sigma", "τ": r"\tau",
    "φ": r"\phi", "χ": r"\chi", "ψ": r"\psi", "ω": r"\omega",
    "Γ": r"\Gamma", "Δ": r"\Delta", "Θ": r"\Theta", "Λ": r"\Lambda",
    "Ξ": r"\Xi", "Π": r"\Pi", "Σ": r"\Sigma", "Φ": r"\Phi",
    "Ψ": r"\Psi", "Ω": r"\Omega",
}

# 常用数学符号
MATH_SYMBOLS = {
    "±": r"\pm", "∓": r"\mp", "×": r"\times", "÷": r"\div",
    "·": r"\cdot", "∘": r"\circ", "∗": r"\ast", "⋆": r"\star",
    "≤": r"\leq", "≥": r"\geq", "≠": r"\neq", "≈": r"\approx",
    "≡": r"\equiv", "∼": r"\sim", "∝": r"\propto", "∈": r"\in",
    "∀": r"\forall", "∃": r"\exists", "∞": r"\infty", "∂": r"\partial",
    "∇": r"\nabla", "∫": r"\int", "∮": r"\oint", "∑": r"\sum",
    "∏": r"\prod", "√": r"\sqrt{}", "∅": r"\emptyset",
    "⊂": r"\subset", "⊆": r"\subseteq", "∪": r"\cup", "∩": r"\cap",
}


def get_all_categories() -> list:
    """获取所有公式模板分类"""
    return list(LATEX_TEMPLATES.keys())


def get_templates_by_category(category: str) -> dict:
    """获取指定分类下的所有模板"""
    return LATEX_TEMPLATES.get(category, {})


def get_template(category: str, name: str) -> Optional[str]:
    """获取指定模板的 LaTeX 源码"""
    return LATEX_TEMPLATES.get(category, {}).get(name)


def get_greek_letters() -> dict:
    """获取希腊字母表"""
    return GREEK_LETTERS


def get_math_symbols() -> dict:
    """获取常用数学符号表"""
    return MATH_SYMBOLS


def validate_latex(latex_str: str) -> bool:
    """
    基础 LaTeX 语法验证
    检查括号匹配、环境配对等
    """
    if not latex_str or not latex_str.strip():
        return False

    # 检查大括号配对
    brace_depth = 0
    for ch in latex_str:
        if ch == '{':
            brace_depth += 1
        elif ch == '}':
            brace_depth -= 1
            if brace_depth < 0:
                return False

    if brace_depth != 0:
        return False

    # 检查 \begin{} 和 \end{} 配对
    begins = re.findall(r'\\begin\{(\w+)\}', latex_str)
    ends = re.findall(r'\\end\{(\w+)\}', latex_str)

    if sorted(begins) != sorted(ends):
        return False

    return True


def wrap_display_math(latex_str: str) -> str:
    """将公式包装为显示数学模式"""
    latex_str = latex_str.strip()
    if latex_str.startswith(r'\[') or latex_str.startswith('$$'):
        return latex_str
    return r"$$\displaystyle " + latex_str + r" $$"


def wrap_inline_math(latex_str: str) -> str:
    """将公式包装为行内数学模式"""
    latex_str = latex_str.strip()
    if latex_str.startswith(r'\(') or latex_str.startswith('$'):
        return latex_str
    return r"$\displaystyle " + latex_str + r" $"


def extract_formulas_from_text(text: str) -> list:
    """从文本中提取所有 LaTeX 公式（$$...$$ 或 $...$ 包裹的内容）"""
    display_pattern = r'\$\$(.+?)\$\$'
    inline_pattern = r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)'

    formulas = []
    for match in re.finditer(display_pattern, text, re.DOTALL):
        formulas.append({
            'type': 'display',
            'latex': match.group(1).strip(),
            'full_match': match.group(0),
        })

    for match in re.finditer(inline_pattern, text):
        formulas.append({
            'type': 'inline',
            'latex': match.group(1).strip(),
            'full_match': match.group(0),
        })

    return formulas
