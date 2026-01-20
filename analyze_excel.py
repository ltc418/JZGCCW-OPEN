import pandas as pd
import xlrd
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 读取Excel文件
wb = xlrd.open_workbook('JZGCCW01.xls', formatting_info=True)
ws = wb.sheet_by_name('1 建筑工程财务模型参数')

print(f"工作表尺寸: 最大行: {ws.nrows}, 最大列: {ws.ncols}")
print("\n")

# 读取数据到pandas DataFrame
df = pd.read_excel('JZGCCW01.xls', sheet_name='1 建筑工程财务模型参数', header=None)

print("=== 前30行数据 ===")
for i in range(min(30, len(df))):
    row_data = df.iloc[i]
    # 只显示非空的前10列
    non_null = row_data[:10].dropna()
    if not non_null.empty:
        print(f"行{i}: {non_null.to_dict()}")

print("\n\n=== 年份列分析（第2-5行） ===")
for i in range(1, 5):
    row_data = df.iloc[i]
    print(f"行{i}: {df.iloc[i, :20].tolist()}")
