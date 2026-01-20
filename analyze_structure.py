import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel('JZGCCW01.xls', sheet_name='1 建筑工程财务模型参数', header=None)

print("=== 年份列布局分析 ===")
# 查看第1-10行，重点关注哪些列包含年份
for i in range(30):
    row_str = f"行{i:3d}: "
    for j in range(37):
        val = df.iloc[i, j]
        if pd.notna(val) and val != '':
            if isinstance(val, (int, float)) and val == int(val):
                if val in range(2000, 2100) or val in range(1, 21):
                    row_str += f"[{j}:{val:.0f}] "
            elif isinstance(val, str) and ('年' in val or '月' in val or '期' in val):
                row_str += f"[{j}:{val}] "
    if '[11:' in row_str or '[12:' in row_str or '[13:' in row_str:
        print(row_str)

print("\n\n=== 关键参数提取 ===")
print(f"建设期: {df.iloc[1, 4]}")
print(f"运营期: {df.iloc[2, 4]}")
print(f"计算期: {df.iloc[2, 7]}")
print(f"项目名称: {df.iloc[0, 4]}")

print("\n\n=== 查找所有含有'年'的列 ===")
year_cols = set()
for i in range(len(df)):
    for j in range(len(df.columns)):
        val = df.iloc[i, j]
        if pd.notna(val) and isinstance(val, str):
            if '年' in val and ('第' in val or '运营' in val or '建设' in val):
                year_cols.add(j)

print(f"可能包含年份的列: {sorted(year_cols)}")

# 查看第10-20行前15列
print("\n\n=== 第10-30行，列4-15 ===")
for i in range(10, 35):
    row_vals = []
    for j in range(4, 15):
        val = df.iloc[i, j]
        if pd.notna(val) and val != '':
            row_vals.append(f"{j}:{val}")
    if row_vals:
        print(f"行{i:3d}: {', '.join(row_vals)}")
