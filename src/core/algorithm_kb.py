"""
本科数值分析算法知识库
定义算法体系、适用条件、数据特征要求、决策规则

覆盖范围（本科数值分析课程）：
1. 插值与逼近
2. 数值积分与微分
3. 线性方程组求解
4. 非线性方程求根
5. 矩阵特征值计算
6. 常微分方程数值解
7. 曲线拟合与最小二乘
"""

# ============================================================================
# 算法体系定义
# ============================================================================

ALGORITHM_KB = {
    # ========================================================================
    # 1. 插值与逼近
    # ========================================================================
    "lagrange_interpolation": {
        "name": "拉格朗日插值",
        "category": "插值与逼近",
        "subcategory": "多项式插值",
        "keywords": ["插值", "多项式", "拉格朗日", "通过已知点"],
        "applicable_when": {
            "data_points": "少量（≤20个点）",
            "distribution": "均匀分布最佳",
            "goal": "通过所有已知数据点构造插值函数",
        },
        "contraindications": ["数据点多时龙格现象严重", "数据含噪声"],
        "complexity": "O(n²)",
        "stability": "中等（高阶不稳定）",
        "matlab_function": "polyfit / polyval",
        "related_formulas": [
            r"P(x) = \sum_{i=0}^{n} y_i \prod_{j\neq i} \frac{x-x_j}{x_i-x_j}",
        ],
        "data_features_match": {
            "scale_level": ["small"],
            "is_sparse": False,
            "needs_imputation": False,
            "is_purely_numeric": True,
            "min_rows": 2,
            "max_rows": 30,
            "penalty_weight": 1.0,
        },
    },
    "newton_interpolation": {
        "name": "牛顿插值",
        "category": "插值与逼近",
        "subcategory": "多项式插值",
        "keywords": ["插值", "牛顿", "差商", "逐步添加节点"],
        "applicable_when": {
            "data_points": "中小规模",
            "pattern": "需要动态增加插值节点",
        },
        "contraindications": ["与拉格朗日相同的龙格现象"],
        "complexity": "O(n²)",
        "stability": "中等",
        "matlab_function": "自定义差商表 + polyval",
        "related_formulas": [
            r"P_n(x) = f[x_0] + f[x_0,x_1](x-x_0) + \cdots + f[x_0,\ldots,x_n]\prod_{i=0}^{n-1}(x-x_i)",
        ],
        "data_features_match": {
            "scale_level": ["small", "medium"],
            "is_sparse": False,
            "needs_imputation": False,
            "is_purely_numeric": True,
            "min_rows": 2,
            "max_rows": 50,
        },
    },
    "spline_interpolation": {
        "name": "三次样条插值",
        "category": "插值与逼近",
        "subcategory": "分段插值",
        "keywords": ["样条", "光滑", "分段", "三次"],
        "applicable_when": {
            "data_points": "任意规模",
            "goal": "需要光滑的插值曲线（C²连续）",
            "avoid_runge": True,
        },
        "contraindications": ["数据极度稀疏"],
        "complexity": "O(n)",
        "stability": "高",
        "matlab_function": "spline / interp1('spline')",
        "related_formulas": [
            r"S_i(x) = a_i + b_i(x-x_i) + c_i(x-x_i)^2 + d_i(x-x_i)^3",
        ],
        "data_features_match": {
            "scale_level": ["small", "medium", "large"],
            "is_sparse": False,
            "needs_imputation": False,
            "is_purely_numeric": True,
            "min_rows": 4,
        },
    },
    "least_squares_fit": {
        "name": "最小二乘拟合",
        "category": "曲线拟合",
        "subcategory": "线性拟合",
        "keywords": ["拟合", "最小二乘", "回归", "残差", "超定"],
        "applicable_when": {
            "data_points": "≥ 待定参数个数",
            "has_noise": True,
            "goal": "不要求过点，求最优逼近",
        },
        "contraindications": ["数据含大量离群点（需鲁棒版本）"],
        "complexity": "O(mn²)（m数据点，n参数）",
        "stability": "高（正规方程可能病态）",
        "matlab_function": "polyfit / fitlm / lsqcurvefit",
        "related_formulas": [
            r"\min \sum_{i=1}^{m} (y_i - f(x_i))^2",
            r"\hat{\beta} = (A^T A)^{-1} A^T y",
        ],
        "data_features_match": {
            "scale_level": ["small", "medium", "large"],
            "needs_imputation": False,
            "is_purely_numeric": True,
            "min_rows": 3,
            "needs_scaling": True,
        },
    },

    # ========================================================================
    # 2. 数值积分与微分
    # ========================================================================
    "composite_trapezoidal": {
        "name": "复合梯形公式",
        "category": "数值积分",
        "subcategory": "牛顿-柯特斯",
        "keywords": ["积分", "梯形", "定积分", "复合"],
        "applicable_when": {
            "function_known": "有函数表达式或等距数据",
            "precision": "低到中等精度要求",
        },
        "complexity": "O(n)",
        "stability": "高",
        "error_order": "O(h²)",
        "matlab_function": "trapz",
        "related_formulas": [
            r"\int_a^b f(x)dx \approx h\left[\frac{f(a)+f(b)}{2} + \sum_{i=1}^{n-1} f(x_i)\right]",
        ],
        "data_features_match": {
            "scale_level": ["small", "medium", "large"],
            "is_purely_numeric": True,
        },
    },
    "composite_simpson": {
        "name": "复合辛普森公式",
        "category": "数值积分",
        "subcategory": "牛顿-柯特斯",
        "keywords": ["积分", "辛普森", "抛物线", "高精度"],
        "applicable_when": {
            "function_known": "有函数表达式或等距数据",
            "precision": "中到高精度要求",
            "n_even": "区间数为偶数",
        },
        "complexity": "O(n)",
        "stability": "高",
        "error_order": "O(h⁴)",
        "matlab_function": "simpson（自定义）/ integral",
        "related_formulas": [
            r"\int_a^b f(x)dx \approx \frac{h}{3}\left[f(a)+f(b)+4\sum_{odd}+2\sum_{even}\right]",
        ],
        "data_features_match": {
            "scale_level": ["small", "medium", "large"],
            "is_purely_numeric": True,
        },
    },
    "gauss_quadrature": {
        "name": "高斯求积公式",
        "category": "数值积分",
        "subcategory": "高斯型",
        "keywords": ["积分", "高斯", "节点", "权重", "最高代数精度"],
        "applicable_when": {
            "function_known": "有光滑函数表达式",
            "precision": "高精度要求",
            "n_points": "较少节点即可达到高精度",
        },
        "complexity": "O(n)（节点数少）",
        "stability": "高",
        "error_order": "O(h^{2n})",
        "matlab_function": "integral（自适应）/ 自定义",
        "related_formulas": [
            r"\int_{-1}^{1} f(x)dx \approx \sum_{i=1}^{n} w_i f(x_i)",
        ],
        "data_features_match": {
            "scale_level": ["small", "medium"],
            "is_purely_numeric": True,
        },
    },
    "romberg_integration": {
        "name": "龙贝格积分",
        "category": "数值积分",
        "subcategory": "外推法",
        "keywords": ["积分", "外推", "龙贝格", "自适应"],
        "applicable_when": {
            "function_known": "有函数表达式",
            "precision": "高精度",
            "smooth": "函数充分光滑",
        },
        "complexity": "O(n log n)",
        "stability": "高",
        "matlab_function": "romberg（自定义）/ integral",
        "related_formulas": [
            r"T_{m}^{(k)} = \frac{4^m T_{m-1}^{(k+1)} - T_{m-1}^{(k)}}{4^m - 1}",
        ],
        "data_features_match": {
            "scale_level": ["small", "medium"],
            "is_purely_numeric": True,
        },
    },
    "numerical_differentiation": {
        "name": "数值微分",
        "category": "数值微分",
        "subcategory": "差分法",
        "keywords": ["导数", "差分", "梯度", "微分"],
        "applicable_when": {
            "function_known": "有函数表达式或离散数据",
            "goal": "近似导数/梯度",
        },
        "complexity": "O(1) 每点",
        "stability": "低（对噪声敏感）",
        "matlab_function": "diff / gradient",
        "related_formulas": [
            r"f'(x) \approx \frac{f(x+h)-f(x-h)}{2h}",
            r"f''(x) \approx \frac{f(x+h)-2f(x)+f(x-h)}{h^2}",
        ],
        "data_features_match": {
            "scale_level": ["small", "medium"],
            "needs_imputation": False,
            "is_purely_numeric": True,
        },
    },

    # ========================================================================
    # 3. 线性方程组求解
    # ========================================================================
    "gaussian_elimination": {
        "name": "高斯消元法",
        "category": "线性方程组",
        "subcategory": "直接法",
        "keywords": ["线性方程组", "消元", "三角分解", "回代"],
        "applicable_when": {
            "matrix_type": "稠密矩阵",
            "matrix_size": "中小规模（<1000阶）",
            "matrix_property": "非奇异",
        },
        "contraindications": ["大规模稀疏矩阵", "接近奇异矩阵"],
        "complexity": "O(n³)",
        "stability": "中等（需选主元）",
        "matlab_function": "mldivide (\\ ) / lu",
        "related_formulas": [
            r"Ax = b \quad \Rightarrow \quad PA = LU, \quad LUx = Pb",
        ],
        "data_features_match": {
            "is_sparse": False,
            "scale_level": ["small", "medium"],
        },
    },
    "lu_decomposition": {
        "name": "LU 分解",
        "category": "线性方程组",
        "subcategory": "直接法",
        "keywords": ["LU", "三角分解", "矩阵分解", "多右端"],
        "applicable_when": {
            "matrix_type": "稠密矩阵",
            "matrix_size": "中小规模",
            "multiple_rhs": "多个右端项（复用分解）",
        },
        "complexity": "O(n³) 分解，O(n²) 求解",
        "stability": "中等（需选主元）",
        "matlab_function": "lu / mldivide",
        "related_formulas": [
            r"A = LU, \quad L\text{下三角}, U\text{上三角}",
        ],
        "data_features_match": {
            "is_sparse": False,
            "scale_level": ["small", "medium"],
            "is_purely_numeric": True,
        },
    },
    "cholesky_decomposition": {
        "name": "Cholesky 分解",
        "category": "线性方程组",
        "subcategory": "直接法",
        "keywords": ["对称正定", "Cholesky", "平方根法"],
        "applicable_when": {
            "matrix_type": "对称正定矩阵",
            "matrix_size": "中小规模",
        },
        "complexity": "O(n³/3)（比LU快一倍）",
        "stability": "高（对正定矩阵）",
        "matlab_function": "chol",
        "related_formulas": [
            r"A = LL^T, \quad A\text{对称正定}",
        ],
        "data_features_match": {
            "is_sparse": False,
            "scale_level": ["small", "medium"],
            "is_purely_numeric": True,
        },
    },
    "jacobi_iteration": {
        "name": "雅可比迭代法",
        "category": "线性方程组",
        "subcategory": "迭代法",
        "keywords": ["迭代", "雅可比", "对角占优", "稀疏"],
        "applicable_when": {
            "matrix_type": "稀疏或大型稠密",
            "matrix_size": "大规模（>1000阶）",
            "convergence": "对角占优保证收敛",
        },
        "complexity": "O(n²) 每次迭代",
        "stability": "依赖矩阵条件",
        "matlab_function": "自定义",
        "related_formulas": [
            r"x^{(k+1)} = D^{-1}(b - (L+U)x^{(k)})",
        ],
        "data_features_match": {
            "is_sparse": True,
            "scale_level": ["large", "xlarge"],
        },
    },
    "gauss_seidel": {
        "name": "高斯-赛德尔迭代法",
        "category": "线性方程组",
        "subcategory": "迭代法",
        "keywords": ["迭代", "赛德尔", "收敛", "稀疏"],
        "applicable_when": {
            "matrix_type": "稀疏或大型",
            "matrix_size": "大规模",
            "convergence": "比雅可比快（一般情况）",
        },
        "complexity": "O(n²) 每次迭代",
        "stability": "依赖矩阵条件",
        "matlab_function": "自定义",
        "related_formulas": [
            r"x^{(k+1)} = (D+L)^{-1}(b - Ux^{(k)})",
        ],
        "data_features_match": {
            "is_sparse": True,
            "scale_level": ["large", "xlarge"],
            "is_purely_numeric": True,
        },
    },
    "sor_iteration": {
        "name": "SOR 迭代法",
        "category": "线性方程组",
        "subcategory": "迭代法",
        "keywords": ["松弛", "SOR", "加速", "超松弛"],
        "applicable_when": {
            "matrix_type": "稀疏或大型",
            "need_speedup": "比 GS 更快收敛",
        },
        "complexity": "O(n²) 每次迭代",
        "stability": "依赖松弛因子 ω 选择",
        "matlab_function": "自定义",
        "related_formulas": [
            r"x^{(k+1)} = (1-\omega)x^{(k)} + \omega (D+L)^{-1}(b - Ux^{(k)})",
        ],
        "data_features_match": {
            "is_sparse": True,
            "scale_level": ["large", "xlarge"],
            "is_purely_numeric": True,
        },
    },
    "conjugate_gradient": {
        "name": "共轭梯度法",
        "category": "线性方程组",
        "subcategory": "迭代法",
        "keywords": ["共轭梯度", "CG", "对称正定", "Krylov子空间"],
        "applicable_when": {
            "matrix_type": "对称正定稀疏矩阵",
            "matrix_size": "大规模",
        },
        "complexity": "O(n²) 每次迭代，收敛快",
        "stability": "高（对称正定情况）",
        "matlab_function": "pcg",
        "related_formulas": [
            r"x_{k+1} = x_k + \alpha_k p_k, \quad \alpha_k = \frac{r_k^T r_k}{p_k^T A p_k}",
        ],
        "data_features_match": {
            "is_sparse": True,
            "scale_level": ["large", "xlarge"],
            "is_purely_numeric": True,
        },
    },

    # ========================================================================
    # 4. 非线性方程求根
    # ========================================================================
    "bisection_method": {
        "name": "二分法",
        "category": "非线性方程",
        "subcategory": "区间法",
        "keywords": ["二分", "求根", "有根区间", "稳健"],
        "applicable_when": {
            "root_known_range": "已知有根区间 [a,b]，f(a)f(b)<0",
            "precision": "低到中等精度",
            "robustness_first": "优先保证收敛",
        },
        "complexity": "O(log(1/ε))",
        "stability": "极高（必定收敛）",
        "convergence_rate": "线性收敛",
        "matlab_function": "fzero（结合二分+插值）",
        "related_formulas": [
            r"c = \frac{a+b}{2}, \quad f(a)f(c)<0 \Rightarrow b=c \text{ else } a=c",
        ],
        "data_features_match": {
            "is_purely_numeric": True,
        },
    },
    "newton_method": {
        "name": "牛顿迭代法",
        "category": "非线性方程",
        "subcategory": "迭代法",
        "keywords": ["牛顿", "切线", "快速收敛", "导数"],
        "applicable_when": {
            "derivative_available": "导数可用或可数值近似",
            "initial_guess": "有较好初值",
            "precision": "高精度",
        },
        "contraindications": ["导数接近零（重根/拐点）", "初值远离根"],
        "complexity": "O(n²) 每次（n维），二次收敛",
        "stability": "中等（依赖初值）",
        "convergence_rate": "二次收敛",
        "matlab_function": "fzero / fsolve",
        "related_formulas": [
            r"x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}",
        ],
        "data_features_match": {
            "is_purely_numeric": True,
        },
    },
    "secant_method": {
        "name": "割线法",
        "category": "非线性方程",
        "subcategory": "迭代法",
        "keywords": ["割线", "弦截", "无导数", "超线性"],
        "applicable_when": {
            "no_derivative": "导数不便计算",
            "two_points": "有两个接近根的初始值",
        },
        "complexity": "O(1) 每次迭代",
        "stability": "中等",
        "convergence_rate": "超线性（≈1.618阶）",
        "matlab_function": "自定义",
        "related_formulas": [
            r"x_{n+1} = x_n - f(x_n)\frac{x_n - x_{n-1}}{f(x_n) - f(x_{n-1})}",
        ],
        "data_features_match": {
            "is_purely_numeric": True,
        },
    },
    "fixed_point_iteration": {
        "name": "不动点迭代",
        "category": "非线性方程",
        "subcategory": "迭代法",
        "keywords": ["不动点", "迭代函数", "压缩映射"],
        "applicable_when": {
            "contractive": "迭代函数满足压缩条件 |g'(x)|<1",
        },
        "complexity": "O(1) 每次迭代",
        "stability": "依赖 g(x) 选取",
        "convergence_rate": "线性收敛",
        "matlab_function": "自定义",
        "related_formulas": [
            r"x = g(x), \quad x_{n+1} = g(x_n)",
        ],
        "data_features_match": {
            "is_purely_numeric": True,
        },
    },

    # ========================================================================
    # 5. 矩阵特征值计算
    # ========================================================================
    "power_method": {
        "name": "幂法",
        "category": "特征值问题",
        "subcategory": "主特征值",
        "keywords": ["特征值", "幂法", "主特征值", "迭代"],
        "applicable_when": {
            "goal": "求最大特征值及对应特征向量",
            "matrix_type": "任意方阵",
            "dominant": "存在占优特征值",
        },
        "complexity": "O(n²) 每次迭代",
        "stability": "依赖特征值分离度",
        "matlab_function": "eigs（求几个特征值）",
        "related_formulas": [
            r"v_{k+1} = \frac{Av_k}{\|Av_k\|}, \quad \lambda \approx \frac{v_k^T A v_k}{v_k^T v_k}",
        ],
        "data_features_match": {
            "scale_level": ["large", "xlarge"],
            "is_purely_numeric": True,
        },
    },
    "inverse_power_method": {
        "name": "反幂法",
        "category": "特征值问题",
        "subcategory": "特定特征值",
        "keywords": ["特征值", "反幂法", "最小特征值", "移位"],
        "applicable_when": {
            "goal": "求离某值最近的特征值",
            "shift_available": "已知特征值近似值",
        },
        "complexity": "O(n³) 每次迭代（需解线性方程组）",
        "matlab_function": "eigs + shift",
        "related_formulas": [
            r"(A - \mu I)v_{k+1} = v_k, \quad \lambda \approx \mu + \frac{1}{\tilde{\lambda}}",
        ],
        "data_features_match": {
            "scale_level": ["medium", "large"],
            "is_purely_numeric": True,
        },
    },
    "qr_algorithm": {
        "name": "QR 算法",
        "category": "特征值问题",
        "subcategory": "全部特征值",
        "keywords": ["QR", "全部特征值", "正交", "Schur"],
        "applicable_when": {
            "goal": "求全部特征值",
            "matrix_type": "中小规模稠密矩阵",
        },
        "complexity": "O(n³)",
        "stability": "高",
        "matlab_function": "eig",
        "related_formulas": [
            r"A_k = Q_k R_k, \quad A_{k+1} = R_k Q_k",
        ],
        "data_features_match": {
            "is_sparse": False,
            "scale_level": ["small", "medium"],
            "is_purely_numeric": True,
        },
    },
    "jacobi_eigenvalue": {
        "name": "Jacobi 特征值法",
        "category": "特征值问题",
        "subcategory": "对称矩阵",
        "keywords": ["Jacobi", "对称", "全部特征值", "旋转"],
        "applicable_when": {
            "matrix_type": "实对称矩阵",
            "matrix_size": "中小规模",
        },
        "complexity": "O(n³)",
        "stability": "高",
        "matlab_function": "eig（对称矩阵自动优化）",
        "related_formulas": [
            r"A_{k+1} = J^T A_k J, \quad J\text{为Givens旋转矩阵}",
        ],
        "data_features_match": {
            "scale_level": ["small", "medium"],
            "is_purely_numeric": True,
        },
    },

    # ========================================================================
    # 6. 常微分方程数值解
    # ========================================================================
    "euler_method": {
        "name": "欧拉方法",
        "category": "常微分方程",
        "subcategory": "初值问题",
        "keywords": ["ODE", "欧拉", "一阶", "显式"],
        "applicable_when": {
            "precision": "低精度要求 / 教学演示",
            "problem": "一阶 ODE 初值问题",
        },
        "complexity": "O(n)",
        "stability": "低（条件稳定）",
        "error_order": "O(h)",
        "matlab_function": "自定义 / ode1",
        "related_formulas": [
            r"y_{n+1} = y_n + h f(t_n, y_n)",
        ],
        "data_features_match": {
            "scale_level": ["small"],
            "is_purely_numeric": True,
        },
    },
    "improved_euler": {
        "name": "改进欧拉方法",
        "category": "常微分方程",
        "subcategory": "初值问题",
        "keywords": ["ODE", "改进欧拉", "预测校正", "二阶"],
        "applicable_when": {
            "precision": "中等精度",
            "balance": "精度与计算量平衡",
        },
        "complexity": "O(n)",
        "error_order": "O(h²)",
        "matlab_function": "自定义",
        "related_formulas": [
            r"\tilde{y}_{n+1} = y_n + h f(t_n, y_n)",
            r"y_{n+1} = y_n + \frac{h}{2}[f(t_n,y_n) + f(t_{n+1},\tilde{y}_{n+1})]",
        ],
        "data_features_match": {
            "scale_level": ["small", "medium"],
            "is_purely_numeric": True,
        },
    },
    "runge_kutta_4": {
        "name": "经典四阶龙格-库塔法",
        "category": "常微分方程",
        "subcategory": "初值问题",
        "keywords": ["ODE", "RK4", "四阶", "高精度"],
        "applicable_when": {
            "precision": "高精度要求",
            "problem": "一阶 ODE 或可化为一阶的高阶 ODE",
            "standard_choice": True,
        },
        "complexity": "O(n)，每步4次函数求值",
        "stability": "中等",
        "error_order": "O(h⁴)",
        "matlab_function": "ode45（自适应RK）",
        "related_formulas": [
            r"k_1 = h f(t_n, y_n)",
            r"k_2 = h f(t_n+\frac{h}{2}, y_n+\frac{k_1}{2})",
            r"y_{n+1} = y_n + \frac{1}{6}(k_1+2k_2+2k_3+k_4)",
        ],
        "data_features_match": {
            "scale_level": ["small", "medium", "large"],
            "is_purely_numeric": True,
        },
    },
    "runge_kutta_fehlberg": {
        "name": "Runge-Kutta-Fehlberg (RKF45)",
        "category": "常微分方程",
        "subcategory": "自适应步长",
        "keywords": ["ODE", "自适应", "变步长", "误差控制"],
        "applicable_when": {
            "precision": "需要误差控制",
            "adaptive": "解变化剧烈程度不一",
        },
        "complexity": "自适应，每步6次求值",
        "stability": "高（自动步长控制）",
        "matlab_function": "ode45",
        "related_formulas": [
            r"y_{n+1} = y_n + h\sum b_i k_i, \quad \text{误差} = h\sum (b_i - b_i^*)k_i",
        ],
        "data_features_match": {
            "scale_level": ["small", "medium", "large"],
            "is_purely_numeric": True,
        },
    },
    "linear_multistep": {
        "name": "线性多步法",
        "category": "常微分方程",
        "subcategory": "多步法",
        "keywords": ["ODE", "多步", "Adams", "BDF"],
        "applicable_when": {
            "efficiency": "函数求值昂贵时（复用历史值）",
            "stiff": "刚性方程用 BDF",
        },
        "complexity": "每步 1-2 次函数求值",
        "matlab_function": "ode113 (Adams) / ode15s (BDF)",
        "related_formulas": [
            r"\sum_{j=0}^{k} \alpha_j y_{n+j} = h\sum_{j=0}^{k} \beta_j f_{n+j}",
        ],
        "data_features_match": {
            "scale_level": ["medium", "large"],
            "is_purely_numeric": True,
        },
    },
}


# ============================================================================
# 分类汇总
# ============================================================================

CATEGORIES = {
    "插值与逼近": {
        "icon": "📈",
        "description": "根据离散数据构造连续函数",
        "algorithms": ["lagrange_interpolation", "newton_interpolation", "spline_interpolation"],
    },
    "曲线拟合": {
        "icon": "📉",
        "description": "寻找最佳逼近函数（不一定过点）",
        "algorithms": ["least_squares_fit"],
    },
    "数值积分": {
        "icon": "∫",
        "description": "近似计算定积分值",
        "algorithms": ["composite_trapezoidal", "composite_simpson", "gauss_quadrature", "romberg_integration"],
    },
    "数值微分": {
        "icon": "∂",
        "description": "近似计算导数/梯度",
        "algorithms": ["numerical_differentiation"],
    },
    "线性方程组": {
        "icon": "🔲",
        "description": "求解 Ax = b",
        "algorithms": [
            "gaussian_elimination", "lu_decomposition", "cholesky_decomposition",
            "jacobi_iteration", "gauss_seidel", "sor_iteration", "conjugate_gradient",
        ],
    },
    "非线性方程": {
        "icon": "🎯",
        "description": "求解 f(x) = 0",
        "algorithms": ["bisection_method", "newton_method", "secant_method", "fixed_point_iteration"],
    },
    "特征值问题": {
        "icon": "λ",
        "description": "计算矩阵特征值和特征向量",
        "algorithms": ["power_method", "inverse_power_method", "qr_algorithm", "jacobi_eigenvalue"],
    },
    "常微分方程": {
        "icon": "🔢",
        "description": "数值求解 ODE 初值问题",
        "algorithms": ["euler_method", "improved_euler", "runge_kutta_4", "runge_kutta_fehlberg", "linear_multistep"],
    },
}


# ============================================================================
# 决策规则（关键字 → 候选算法）
# ============================================================================

# 从自然语言关键词到算法候选的映射
KEYWORD_TO_ALGORITHMS = {
    # 插值相关
    "插值": ["lagrange_interpolation", "newton_interpolation", "spline_interpolation"],
    "样条": ["spline_interpolation"],
    "拉格朗日": ["lagrange_interpolation"],
    "牛顿插值": ["newton_interpolation"],
    "龙格": ["spline_interpolation"],  # 避免龙格 → 样条

    # 拟合相关
    "拟合": ["least_squares_fit"],
    "最小二乘": ["least_squares_fit"],
    "回归": ["least_squares_fit"],
    "残差": ["least_squares_fit"],

    # 积分相关
    "积分": ["composite_trapezoidal", "composite_simpson", "gauss_quadrature", "romberg_integration"],
    "梯形": ["composite_trapezoidal"],
    "辛普森": ["composite_simpson"],
    "高斯积分": ["gauss_quadrature"],
    "龙贝格": ["romberg_integration"],
    "求积": ["composite_trapezoidal", "composite_simpson", "gauss_quadrature"],

    # 微分相关
    "导数": ["numerical_differentiation"],
    "微分": ["numerical_differentiation"],
    "梯度": ["numerical_differentiation"],
    "差分": ["numerical_differentiation"],

    # 线性方程组
    "线性方程": ["gaussian_elimination", "lu_decomposition", "cholesky_decomposition",
                  "jacobi_iteration", "gauss_seidel", "sor_iteration", "conjugate_gradient"],
    "方程组": ["gaussian_elimination", "lu_decomposition", "jacobi_iteration", "gauss_seidel", "conjugate_gradient"],
    "高斯消元": ["gaussian_elimination"],
    "LU": ["lu_decomposition"],
    "三角分解": ["lu_decomposition"],
    "Cholesky": ["cholesky_decomposition"],
    "对称正定": ["cholesky_decomposition", "conjugate_gradient"],
    "雅可比": ["jacobi_iteration"],
    "赛德尔": ["gauss_seidel"],
    "SOR": ["sor_iteration"],
    "共轭梯度": ["conjugate_gradient"],
    "迭代法": ["jacobi_iteration", "gauss_seidel", "sor_iteration", "conjugate_gradient"],
    "稀疏": ["jacobi_iteration", "gauss_seidel", "sor_iteration", "conjugate_gradient"],
    "直接法": ["gaussian_elimination", "lu_decomposition", "cholesky_decomposition"],

    # 非线性方程
    "求根": ["bisection_method", "newton_method", "secant_method", "fixed_point_iteration"],
    "二分法": ["bisection_method"],
    "牛顿法": ["newton_method"],
    "割线": ["secant_method"],
    "弦截": ["secant_method"],
    "不动点": ["fixed_point_iteration"],
    "非线性方程": ["bisection_method", "newton_method", "secant_method", "fixed_point_iteration"],
    "f(x)=0": ["bisection_method", "newton_method", "secant_method"],

    # 特征值
    "特征值": ["power_method", "inverse_power_method", "qr_algorithm", "jacobi_eigenvalue"],
    "特征向量": ["power_method", "inverse_power_method", "qr_algorithm"],
    "幂法": ["power_method"],
    "反幂法": ["inverse_power_method"],
    "QR": ["qr_algorithm"],
    "谱": ["power_method", "qr_algorithm"],

    # ODE
    "微分方程": ["euler_method", "improved_euler", "runge_kutta_4", "runge_kutta_fehlberg", "linear_multistep"],
    "ODE": ["euler_method", "improved_euler", "runge_kutta_4", "runge_kutta_fehlberg", "linear_multistep"],
    "常微分": ["euler_method", "improved_euler", "runge_kutta_4", "runge_kutta_fehlberg", "linear_multistep"],
    "初值": ["euler_method", "improved_euler", "runge_kutta_4", "runge_kutta_fehlberg"],
    "欧拉": ["euler_method"],
    "龙格库塔": ["runge_kutta_4"],
    "RK4": ["runge_kutta_4"],
    "变步长": ["runge_kutta_fehlberg"],
    "刚性": ["linear_multistep"],
}


def get_algorithm_info(alg_id: str) -> dict:
    """获取算法详细信息"""
    return ALGORITHM_KB.get(alg_id, {})


def get_category_algorithms(category: str) -> list:
    """获取某分类下的所有算法 ID"""
    cat_info = CATEGORIES.get(category, {})
    return cat_info.get("algorithms", [])


def match_keywords(text: str) -> list:
    """
    从文本中匹配关键词，返回候选算法 ID 列表（去重）

    Args:
        text: 用户问题描述

    Returns:
        list: 匹配到的算法 ID 列表
    """
    text_lower = text.lower()
    matched = []

    for keyword, alg_ids in KEYWORD_TO_ALGORITHMS.items():
        if keyword.lower() in text_lower:
            matched.extend(alg_ids)

    # 去重并保持顺序
    seen = set()
    result = []
    for alg_id in matched:
        if alg_id not in seen:
            seen.add(alg_id)
            result.append(alg_id)

    return result


def get_algorithm_categories() -> dict:
    """获取算法分类体系"""
    return CATEGORIES
