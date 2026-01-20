# 快速启动指南

## 📋 目录
- [Windows用户](#windows用户)
- [Linux/macOS用户](#linuxmacos用户)
- [故障排除](#故障排除)
- [系统要求](#系统要求)

---

## 🪟 Windows用户

### 方法一：双击运行（推荐）

1. 找到 `start.bat` 文件
2. 双击文件即可启动
3. 等待浏览器自动打开

### 方法二：命令行运行

```cmd
# 在项目目录下打开命令提示符
cd H:\GIT\JZGCCW-open

# 运行启动脚本
start.bat
```

### 方法三：手动启动

```cmd
# 1. 激活虚拟环境（如果有）
.venv\Scripts\activate

# 2. 安装依赖（首次运行）
pip install -r requirements.txt

# 3. 启动应用
streamlit run app.py
```

---

## 🐧 Linux/macOS用户

### 方法一：双击运行（需要可执行权限）

```bash
# 给脚本添加可执行权限
chmod +x start.sh

# 双击或运行
./start.sh
```

### 方法二：命令行运行

```bash
# 在项目目录下打开终端
cd /path/to/JZGCCW-OPEN

# 运行启动脚本
bash start.sh
```

### 方法三：手动启动

```bash
# 1. 激活虚拟环境（如果有）
source .venv/bin/activate

# 2. 安装依赖（首次运行）
pip install -r requirements.txt

# 3. 启动应用
streamlit run app.py
```

---

## 🔧 故障排除

### 常见问题

#### 1. 端口被占用

**错误信息**：
```
Address already in use
Port 8501 is already in use
```

**解决方案**：
```bash
# Windows: 查找占用端口的进程
netstat -ano | findstr :8501

# 或使用其他端口启动
streamlit run app.py --server.port 8502

# Linux/macOS: 查找占用端口的进程
lsof -i :8501
```

#### 2. Python版本不匹配

**错误信息**：
```
Python 3.8+ is required
```

**解决方案**：
```bash
# 检查Python版本
python --version  # Windows
python3 --version  # Linux/macOS

# 安装Python 3.8+
# Windows: 从 https://www.python.org/downloads/ 下载
# Linux: sudo apt-get install python3.8
# macOS: brew install python@3.8
```

#### 3. 依赖包安装失败

**错误信息**：
```
ModuleNotFoundError: No module named 'streamlit'
```

**解决方案**：
```bash
# 升级pip
python -m pip install --upgrade pip

# 清理缓存
pip cache purge

# 重新安装依赖
pip install -r requirements.txt

# 如果网络问题，使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 4. 虚拟环境问题

**解决方案**：
```bash
# 创建新的虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

#### 5. 编码错误（Windows）

**错误信息**：
```
UnicodeEncodeError: 'gbk' codec can't encode character
```

**解决方案**：
```cmd
# 设置命令行编码为UTF-8
chcp 65001
```

---

## 💻 系统要求

### 最低要求

- **操作系统**: Windows 10+, macOS 10.14+, Linux（Ubuntu 18.04+）
- **Python**: 3.8 或更高版本
- **内存**: 4GB RAM
- **磁盘空间**: 500MB 可用空间
- **网络**: 需要网络连接（首次运行时下载依赖）

### 推荐配置

- **操作系统**: Windows 11, macOS 12+, Linux（Ubuntu 20.04+）
- **Python**: 3.10 或更高版本
- **内存**: 8GB RAM
- **磁盘空间**: 1GB 可用空间
- **浏览器**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

### Python依赖包

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0
xlrd>=2.0.1
```

---

## 📖 使用指南

### 首次使用

1. **启动应用程序**
   - Windows: 双击 `start.bat`
   - Linux/macOS: 运行 `bash start.sh`

2. **等待浏览器打开**
   - 应用会自动在默认浏览器中打开
   - 访问地址: `http://localhost:8501`

3. **输入项目数据**
   - 在"数据输入"页面填写项目参数
   - 支持建设期（1-10年）和运营期（1-50年）配置

4. **执行计算**
   - 点击"开始计算"按钮
   - 等待计算完成

5. **查看结果**
   - 在"计算结果"页面查看财务分析结果
   - 包含现金流量表、利润表、财务指标等

6. **导出数据**
   - 在"系统设置"页面导出Excel文件
   - 或保存配置文件供后续使用

### 高级功能

#### 敏感性分析

1. 在"计算结果"页面找到敏感性分析选项
2. 选择要分析的因素（收入、成本、投资等）
3. 查看敏感性分析结果和图表

#### 数据导入/导出

1. **导出配置**:
   - 系统设置 → 保存数据
   - 下载JSON配置文件

2. **导入配置**:
   - 系统设置 → 上传配置文件
   - 选择之前保存的JSON文件

#### Excel导出

1. 在"系统设置"页面
2. 点击"导出Excel"
3. 下载完整的财务分析报告

---

## 🎯 快速测试

如果您想快速测试应用程序，可以使用以下方法：

### 测试数据导入

```python
# 创建一个简单的测试配置
{
  "period": {
    "construction_period": 3,
    "operation_period": 17
  },
  "investment": {
    "building_cost": 67062.86,
    "equipment_procurement_cost": 2360.38,
    ...
  }
}
```

### 命令行测试

```bash
# 运行测试脚本
python test_model.py
```

---

## 📞 获取帮助

### 文档

- **GitHub仓库**: https://github.com/ltc418/JZGCCW-OPEN
- **项目文档**: README.md

### 问题反馈

如果您遇到问题：

1. 查看[故障排除](#故障排除)部分
2. 检查GitHub仓库的[Issues](https://github.com/ltc418/JZGCCW-OPEN/issues)
3. 提交新的Issue，包含：
   - 错误信息
   - 操作系统版本
   - Python版本
   - 详细的复现步骤

---

## ✨ 提示和技巧

### 性能优化

1. **使用虚拟环境**: 隔离项目依赖
2. **定期清理缓存**: `pip cache purge`
3. **关闭不必要的应用**: 释放系统资源

### 数据管理

1. **定期保存**: 使用"保存数据"功能
2. **版本控制**: 使用Git管理配置文件
3. **备份重要数据**: 定期备份Excel导出文件

### 浏览器兼容性

推荐使用以下浏览器：
- **Chrome** (最新版) - ✅ 最佳体验
- **Firefox** (最新版) - ✅ 良好支持
- **Edge** (最新版) - ✅ 良好支持
- **Safari** (14+) - ⚠️ 部分功能受限

---

## 📚 相关资源

- [Streamlit文档](https://docs.streamlit.io/)
- [Python文档](https://docs.python.org/3/)
- [pandas文档](https://pandas.pydata.org/docs/)
- [《建设项目经济评价方法与参数(第三版)》](https://www.mohurd.gov.cn/)

---

**祝您使用愉快！** 🎉