#!/bin/bash

# 建设项目经济评价系统 - 快速启动脚本
# 适用于 Linux 和 macOS

echo "============================================================"
echo "           建设项目经济评价系统 - 快速启动"
echo "============================================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python 3.8+"
    echo "下载地址: https://www.python.org/downloads/"
    exit 1
fi

echo "[步骤 1/5] 检查Python环境..."
python3 --version
echo ""

# 检查虚拟环境
if [ -d ".venv" ]; then
    echo "[步骤 2/5] 检测到虚拟环境，正在激活..."
    source .venv/bin/activate
    echo "✓ 虚拟环境已激活"
    echo ""
else
    echo "[步骤 2/5] 未检测到虚拟环境，跳过"
    echo ""
fi

# 检查pip
if ! command -v pip &> /dev/null; then
    echo "[错误] 未检测到pip，请先安装pip"
    exit 1
fi

# 检查依赖
echo "[步骤 3/5] 检查依赖包..."
if ! pip show streamlit &> /dev/null; then
    echo "未检测到依赖包，正在安装..."
    echo ""
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖包安装失败"
        exit 1
    fi
    echo ""
    echo "✓ 依赖包安装完成"
    echo ""
else
    echo "✓ 依赖包已安装"
    echo ""
fi

# 创建必要的目录
echo "[步骤 4/5] 创建必要目录..."
mkdir -p .streamlit
mkdir -p outputs
echo "✓ 目录创建完成"
echo ""

# 启动Streamlit应用
echo "[步骤 5/5] 正在启动应用程序..."
echo ""

echo "============================================================"
echo "应用程序正在启动中..."
echo "访问地址: http://localhost:8501"
echo "============================================================"
echo ""
echo "[提示] 按 Ctrl+C 停止应用程序"
echo ""

# 启动应用
streamlit run app.py

# 检查是否成功启动
if [ $? -ne 0 ]; then
    echo ""
    echo "============================================================"
    echo "[错误] 应用程序启动失败"
    echo "============================================================"
    echo ""
    echo "请检查以下问题："
    echo "1. 确保已安装所有依赖包（pip install -r requirements.txt）"
    echo "2. 确保端口8501未被占用"
    echo "3. 检查Python版本是否符合要求（3.8+）"
    echo ""
    exit 1
fi