@echo off
echo ============================================================
echo             建设项目经济评价系统 - 快速启动
echo ============================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [步骤 1/5] 检查Python环境...
python --version
echo.

REM 检查虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo [步骤 2/5] 检测到虚拟环境，正在激活...
    call .venv\Scripts\activate.bat
    echo ✓ 虚拟环境已激活
    echo.
) else (
    echo [步骤 2/5] 未检测到虚拟环境，跳过
    echo.
)

REM 检查依赖
echo [步骤 3/5] 检查依赖包...
pip show streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo 未检测到依赖包，正在安装...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖包安装失败
        pause
        exit /b 1
    )
    echo.
    echo ✓ 依赖包安装完成
    echo.
) else (
    echo ✓ 依赖包已安装
    echo.
)

REM 创建必要的目录
if not exist ".streamlit" mkdir ".streamlit"
if not exist "outputs" mkdir "outputs"

echo [步骤 4/5] 正在启动应用程序...
echo.

REM 启动Streamlit应用
echo ============================================================
echo 应用程序正在启动中...
echo 访问地址: http://localhost:8501
echo ============================================================
echo.
echo [提示] 按 Ctrl+C 停止应用程序
echo.

streamlit run app.py

REM 如果程序异常退出
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo [错误] 应用程序启动失败
    echo ============================================================
    echo.
    echo 请检查以下问题：
    echo 1. 确保已安装所有依赖包（pip install -r requirements.txt）
    echo 2. 确保端口8501未被占用
    echo 3. 检查Python版本是否符合要求（3.8+）
    echo.
    pause
    exit /b 1
)