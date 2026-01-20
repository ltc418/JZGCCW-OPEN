#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
依赖检查脚本
验证所有依赖包是否正确安装
"""

import sys

def check_dependencies():
    """检查所有依赖包"""
    print("=" * 60)
    print("Checking Dependencies")
    print("=" * 60)
    print()
    
    dependencies = [
        ('streamlit', '>=1.28.0'),
        ('pandas', '>=2.0.0'),
        ('numpy', '>=1.24.0'),
        ('openpyxl', '>=3.1.0'),
        ('xlrd', '>=2.0.1')
    ]
    
    all_ok = True
    
    for package, version_req in dependencies:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'Unknown')
            print(f"[OK] {package:20s} {version:10s} (required: {version_req})")
        except ImportError as e:
            print(f"[FAIL] {package:20s} NOT INSTALLED (required: {version_req})")
            all_ok = False
        except Exception as e:
            print(f"[ERROR] {package:20s} Error: {e}")
            all_ok = False
    
    print()
    print("=" * 60)
    
    if all_ok:
        print("All dependencies are installed correctly!")
        print("=" * 60)
        return 0
    else:
        print("Some dependencies are missing!")
        print("=" * 60)
        print("\nPlease run: pip install -r requirements.txt")
        return 1


def check_python_version():
    """检查Python版本"""
    print("Python Version Check")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"Python Path: {sys.executable}")
    print("=" * 60)
    print()
    
    # 检查Python版本是否符合要求
    if sys.version_info >= (3, 8):
        print("[OK] Python version 3.8+ is satisfied")
        return True
    else:
        print("[FAIL] Python version 3.8+ is required")
        return False


def check_app_imports():
    """检查应用程序导入"""
    print("Application Imports Check")
    print("=" * 60)
    print()
    
    app_modules = [
        'financial_core',
        'financial_calculator',
        'investment_module',
        'cost_module',
        'revenue_module',
        'financial_comprehensive_module',
        'sensitivity_analyzer',
        'excel_exporter'
    ]
    
    all_ok = True
    
    for module_name in app_modules:
        try:
            __import__(module_name)
            print(f"[OK] {module_name}")
        except ImportError as e:
            print(f"[FAIL] {module_name} - {e}")
            all_ok = False
        except Exception as e:
            print(f"[ERROR] {module_name} - {e}")
            all_ok = False
    
    print()
    print("=" * 60)
    
    if all_ok:
        print("All application modules can be imported!")
        print("=" * 60)
        return 0
    else:
        print("Some application modules failed to import!")
        print("=" * 60)
        return 1


def main():
    """主函数"""
    print()
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  Financial Analysis System - Dependency Check".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print()
    
    # 检查Python版本
    python_ok = check_python_version()
    print()
    
    # 检查依赖包
    deps_ok = check_dependencies() == 0
    print()
    
    # 检查应用程序导入
    imports_ok = check_app_imports() == 0
    print()
    
    # 总结
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Python Version: {'[OK]' if python_ok else '[FAIL]'}")
    print(f"Dependencies:  {'[OK]' if deps_ok else '[FAIL]'}")
    print(f"App Modules:   {'[OK]' if imports_ok else '[FAIL]'}")
    print("=" * 60)
    print()
    
    if python_ok and deps_ok and imports_ok:
        print("System is ready to run!")
        print("Please run: streamlit run app.py")
        print("Or double-click: start.bat (Windows) or ./start.sh (Linux/macOS)")
        print()
        return 0
    else:
        print("System needs fixes before running!")
        print()
        if not python_ok:
            print("- Please install Python 3.8 or higher")
        if not deps_ok:
            print("- Please install dependencies: pip install -r requirements.txt")
        if not imports_ok:
            print("- Please check application module files")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())