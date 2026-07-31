"""
模拟测试场景定义
每个场景包含：自然语言问题描述、上传数据文件、预期分类、预期算法
"""

TEST_SCENARIOS = [
    {
        "id": "scenario_fit",
        "name": "曲线拟合 — 多项式回归",
        "description": (
            "对附件中的数据 (demo_poly_fit.csv) 进行多项式回归拟合。"
            "数据包含自变量 x 和因变量 y，y 含测量噪声。"
            "请找出 x 和 y 之间的函数关系 y = f(x)，"
            "使用最小二乘法确定多项式系数。"
        ),
        "data_file": "demo_poly_fit.csv",
        "expected_category": "曲线拟合",
        "expected_primary": "least_squares_fit",
        "tags": ["拟合", "最小二乘", "回归", "多项式", "噪声"],
    },
    {
        "id": "scenario_interp",
        "name": "插值与逼近 — 离散数据插值",
        "description": (
            "已知 12 个离散数据点 (demo_interpolation.csv)，"
            "需要构造一条光滑曲线通过所有这些点。"
            "数据点分布不均匀，要求插值曲线具有 C² 连续性。"
            "请推荐最适合的插值算法。"
        ),
        "data_file": "demo_interpolation.csv",
        "expected_category": "插值与逼近",
        "expected_primary": "spline_interpolation",
        "tags": ["插值", "样条", "光滑", "通过已知点", "C²连续"],
    },
    {
        "id": "scenario_linear",
        "name": "线性方程组 — 三对角稀疏矩阵",
        "description": (
            "求解线性方程组 Ax = b，其中 A 是一个 100×100 的三对角稀疏矩阵"
            "（主对角线元素为 2，次对角线元素为 -1），"
            "b 为全 1 向量。矩阵规模中等，具有稀疏结构。"
            "请推荐最合适的求解算法。"
        ),
        "data_file": "demo_linear_system.csv",
        "expected_category": "线性方程组",
        "expected_primary": "jacobi_iteration",  # 对称正定三对角 → 迭代法最优
        "tags": ["线性方程", "方程组", "三对角", "稀疏", "矩阵求解"],
    },
    {
        "id": "scenario_nonlinear",
        "name": "非线性方程 — 求根",
        "description": (
            "求解非线性方程 f(x) = x³ - 2x - 5 = 0 在区间 [1, 4] 内的根。"
            "已知 f(2) = -1 < 0, f(3) = 16 > 0，"
            "函数在区间内连续且单调递增。需要高精度结果。"
            "请推荐最适合的求根算法。"
        ),
        "data_file": "demo_nonlinear_root.csv",
        "expected_category": "非线性方程",
        "expected_primary": "newton_method",
        "tags": ["求根", "牛顿", "f(x)=0", "有根区间", "高精度"],
    },
    {
        "id": "scenario_ode",
        "name": "常微分方程 — 初值问题",
        "description": (
            "求解一阶常微分方程初值问题：dy/dt = -2y + sin(t), y(0) = 1。"
            "数据文件 demo_ode.csv 包含时间序列观测值。"
            "要求在 t ∈ [0, 3] 上以步长 h = 0.1 进行数值求解，"
            "需要高精度和误差控制。请推荐最适合的 ODE 求解算法。"
        ),
        "data_file": "demo_ode.csv",
        "expected_category": "常微分方程",
        "expected_primary": "runge_kutta_fehlberg",  # 需要误差控制 → 自适应RKF
        "tags": ["ODE", "微分方程", "初值", "RK4", "高精度"],
    },
]
