# ============================================================================
# MathWizard 项目初始化脚本 (Windows PowerShell)
# 用法: 在 c:\ 下运行此脚本
#   PowerShell: .\init_mathwizard.ps1
# ============================================================================

$ProjectRoot = "c:\MathWizard"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MathWizard 项目结构初始化" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查目录是否已存在
if (Test-Path $ProjectRoot) {
    Write-Host "[警告] 目录 $ProjectRoot 已存在" -ForegroundColor Yellow
    $response = Read-Host "是否覆盖？(y/n)"
    if ($response -ne 'y') {
        Write-Host "已取消。"
        exit
    }
    Remove-Item -Path $ProjectRoot -Recurse -Force
}

# 创建目录结构
$directories = @(
    "$ProjectRoot",
    "$ProjectRoot\src",
    "$ProjectRoot\src\ui",
    "$ProjectRoot\src\core",
    "$ProjectRoot\src\utils",
    "$ProjectRoot\data\uploads",
    "$ProjectRoot\output",
    "$ProjectRoot\tests",
    "$ProjectRoot\docs"
)

Write-Host "[1/3] 创建目录结构..." -ForegroundColor Green
foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    Write-Host "  + $dir"
}

# 创建占位文件
$files = @(
    "$ProjectRoot\src\__init__.py",
    "$ProjectRoot\src\ui\__init__.py",
    "$ProjectRoot\src\core\__init__.py",
    "$ProjectRoot\src\core\decision_tree.py",
    "$ProjectRoot\src\core\code_generator.py",
    "$ProjectRoot\src\core\validator.py",
    "$ProjectRoot\src\utils\__init__.py",
    "$ProjectRoot\data\uploads\.gitkeep",
    "$ProjectRoot\output\.gitkeep",
    "$ProjectRoot\tests\__init__.py",
    "$ProjectRoot\docs\.gitkeep"
)

Write-Host ""
Write-Host "[2/3] 创建占位文件..." -ForegroundColor Green
foreach ($file in $files) {
    New-Item -ItemType File -Path $file -Force | Out-Null
    Write-Host "  + $file"
}

Write-Host ""
Write-Host "[3/3] 初始化 Git 仓库..." -ForegroundColor Green
Set-Location $ProjectRoot
git init
Write-Host "  + Git 仓库已初始化"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  初始化完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host "  1. 将沙箱中的文件复制到对应目录"
Write-Host "  2. cd $ProjectRoot"
Write-Host "  3. python -m venv venv"
Write-Host "  4. venv\Scripts\activate"
Write-Host "  5. pip install -r requirements.txt"
Write-Host "  6. streamlit run app.py"
Write-Host ""
