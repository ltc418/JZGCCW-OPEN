import streamlit as st
import pandas as pd
import numpy as np

def calculate_financial_model():
    # 获取用户输入的数据
    construction_period = st.session_state.get('construction_period', 3)
    operation_period = st.session_state.get('operation_period', 17)
    total_period = construction_period + operation_period
    
    # 初始化所有年份的数据
    years = list(range(1, total_period + 1))
    
    # 项目投资部分 - 需要用户输入的数据
    building_cost = st.session_state.get('building_cost', 67062.86)  # 1.1 建筑工程费
    equipment_procurement_cost = st.session_state.get('equipment_procurement_cost', 0)  # 1.3.1 生产设备购置费
    equipment_installation_cost = st.session_state.get('equipment_installation_cost', 18299.19)  # 1.3.2 生产设备安装费
    other_construction_costs = st.session_state.get('other_construction_costs', 16870.944)  # 工程建设其他费
    contingency_reserve = st.session_state.get('contingency_reserve', 10532.08)  # 预备费
    construction_interest = st.session_state.get('construction_interest', 5721.185772330424)  # 建设期利息
    working_capital = st.session_state.get('working_capital', 90)  # 流动资金
    
    # 资产形成计算
    fixed_assets_total = building_cost + equipment_procurement_cost + equipment_installation_cost + other_construction_costs + contingency_reserve + construction_interest
    intangible_assets = st.session_state.get('intangible_assets', 6505.72)  # 无形资产
    other_assets = st.session_state.get('other_assets', 294.1029)  # 其他资产
    deductible_tax = st.session_state.get('deductible_tax', 8716.8199)  # 可抵扣建设投资进项税
    
    # 收入数据 - 按年份输入
    income_years = {}
    for i in range(4, total_period + 1):  # 收入从第4年开始
        key = f"income_year_{i}"
        # 默认值使用原始数据中的值
        if i == 4:
            default_val = 21127.586435770652
        elif i <= 20:
            # 根据运营年份提供不同的默认值
            base_values = [34384.75930731196, 34384.75930731196, 35769.15930731196, 15883.4, 15883.4, 
                          17406.24, 17406.24, 17406.24, 19081.364000000005, 19081.364000000005, 
                          19081.364000000005, 20924.000400000008, 20924.000400000008, 20924.000400000008, 
                          22950.90044000001, 22950.90044000001]
            idx = min(i-5, len(base_values)-1)  # 确保不越界
            default_val = base_values[idx]
        else:
            default_val = 0
        income_years[key] = st.session_state.get(key, default_val)
    
    # 成本数据 - 按年份输入
    cost_years = {}
    for i in range(4, total_period + 1):  # 成本从第4年开始
        key = f"cost_year_{i}"
        # 默认值使用原始数据中的值，这里我们假设成本为收入的一定比例
        if i >= 4:
            default_val = income_years[f"income_year_{i}"] * 0.1  # 假设成本是收入的10%
        else:
            default_val = 0
        cost_years[key] = st.session_state.get(key, default_val)
    
    # 计算现金流
    cash_flow = []
    cumulative_cash_flow = []
    for i in range(total_period):
        year_idx = i + 1
        
        if year_idx <= construction_period:
            # 建设期只有支出，没有收入
            net_cash_flow = -(fixed_assets_total / construction_period)  # 假设投资均匀投入
        else:
            # 运营期
            income_key = f"income_year_{year_idx}"
            cost_key = f"cost_year_{year_idx}"
            income = st.session_state.get(income_key, income_years[income_key])
            cost = st.session_state.get(cost_key, cost_years[cost_key])
            
            # 计算税费
            profit_before_tax = income - cost
            income_tax = max(0, profit_before_tax * 0.25)  # 所得税25%
            
            net_cash_flow = income - cost - income_tax
            
        cash_flow.append(net_cash_flow)
        
        # 累计现金流
        if i == 0:
            cumulative_cash_flow.append(net_cash_flow)
        else:
            cumulative_cash_flow.append(cumulative_cash_flow[-1] + net_cash_flow)
    
    return {
        'years': years,
        'cash_flow': cash_flow,
        'cumulative_cash_flow': cumulative_cash_flow,
        'construction_period': construction_period,
        'operation_period': operation_period,
        'total_period': total_period
    }

def render_input_form():
    st.title("建设项目经济评价系统")
    st.subheader("建筑工程财务模型参数")
    
    with st.expander("项目基本信息", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("项目名称", value="东兴电子产业园三期项目财务分析", key="project_name")
        with col2:
            st.number_input("建设期(年)", min_value=1, max_value=10, value=3, key="construction_period")
            st.number_input("运营期(年)", min_value=1, max_value=50, value=17, key="operation_period")
            calc_period = st.session_state.get('construction_period', 3) + st.session_state.get('operation_period', 17)
            st.number_input("计算期(年)", value=calc_period, key="calculation_period", disabled=True)
    
    with st.expander("项目投资", expanded=True):
        st.write("**项目投资估算汇总(万元)**")
        
        # 工程费
        st.write("1 工程费")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.write("1.1 建筑工程费")
        with col2:
            st.number_input("含税投资", value=67062.86, key="building_cost", format="%.2f", help="建筑工程费含税投资")
        with col3:
            st.write("进项税")
        with col4:
            st.write("不含税投资")
        with col5:
            st.write("进项税率")
        with col6:
            st.write("形成资产")
        
        # 设备费用
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.write("1.2.1 建筑设备费")
        with col2:
            st.number_input("含税投资", value=2360.38, key="equipment_cost", format="%.2f", help="建筑设备费含税投资")
        with col3:
            st.write("进项税")
        with col4:
            st.write("不含税投资")
        with col5:
            st.write("进项税率")
        with col6:
            st.write("固定资产")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.write("1.2.2 建筑设备安装费")
        with col2:
            st.number_input("含税投资", value=18299.19, key="equipment_installation_cost", format="%.2f", help="建筑设备安装费含税投资")
        with col3:
            st.write("进项税")
        with col4:
            st.write("不含税投资")
        with col5:
            st.write("进项税率")
        with col6:
            st.write("固定资产")
        
        # 生产设备
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.write("1.3.1 生产设备购置费")
        with col2:
            st.number_input("含税投资", value=0.0, key="equipment_procurement_cost", format="%.2f", help="生产设备购置费含税投资")
        with col3:
            st.write("进项税")
        with col4:
            st.write("不含税投资")
        with col5:
            st.write("进项税率")
        with col6:
            st.write("固定资产")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.write("1.3.2 生产设备安装费")
        with col2:
            st.number_input("含税投资", value=0.0, key="production_equipment_installation_cost", format="%.2f", help="生产设备安装费含税投资")
        with col3:
            st.write("进项税")
        with col4:
            st.write("不含税投资")
        with col5:
            st.write("进项税率")
        with col6:
            st.write("固定资产")
        
        # 工程建设其他费
        st.write("2 工程建设其他费")
        st.number_input("工程建设其他费", value=16870.944, key="other_construction_costs", format="%.2f", help="工程建设其他费")
        
        # 预备费
        st.write("3 预备费")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("基本预备费", value=10532.08, key="contingency_reserve", format="%.2f", help="基本预备费")
        with col2:
            st.number_input("涨价预备费", value=0.0, key="price_increase_reserve", format="%.2f", help="涨价预备费")
        
        # 建设期利息
        st.write("4 建设期利息")
        st.number_input("建设期利息", value=5721.185772330424, key="construction_interest", format="%.2f", help="建设期利息")
        
        # 流动资金
        st.write("5 流动资金")
        st.number_input("流动资金", value=90.0, key="working_capital", format="%.2f", help="流动资金")
    
    with st.expander("项目经营收入", expanded=True):
        # 获取建设期和运营期
        construction_period = st.session_state.get('construction_period', 3)
        operation_period = st.session_state.get('operation_period', 17)
        total_period = construction_period + operation_period
        
        # 显示年份标题
        cols = st.columns(total_period + 3)  # +3是为了容纳前面的列
        with cols[0]:
            st.write("序号")
        with cols[1]:
            st.write("收入名称")
        with cols[2]:
            st.write("销项税税率")
        
        for i in range(total_period):
            with cols[i + 3]:  # +3是因为前面有3列
                st.write(f"第{i+1}年")
        
        # 标准厂房收入
        cols = st.columns(total_period + 3)
        with cols[0]:
            st.write("1")
        with cols[1]:
            st.write("标准厂房收入（万元）")
        with cols[2]:
            st.write("0.09")
        
        for i in range(total_period):
            with cols[i + 3]:
                if i < construction_period:
                    st.write("0")  # 建设期无收入
                else:
                    # 提供运营期收入输入
                    key = f"income_year_{i+1}"
                    # 设置默认值
                    if i == 3:  # 第4年
                        default_val = 9840
                    elif i == 4:
                        default_val = 9840
                    elif i == 5:
                        default_val = 10824.0
                    elif i < 10:
                        default_val = 10824.0
                    elif i < 15:
                        default_val = 13097.040000000003
                    elif i < 20:
                        default_val = 15847.418400000006
                    else:
                        default_val = 0
                    
                    st.number_input(
                        f"第{i+1}年收入",
                        value=default_val,
                        key=key,
                        label_visibility="collapsed",
                        help=f"第{i+1}年标准厂房收入"
                    )
    
    with st.expander("经营成本", expanded=True):
        # 经营成本输入区域
        cols = st.columns(total_period + 3)
        with cols[0]:
            st.write("序号")
        with cols[1]:
            st.write("成本名称")
        with cols[2]:
            st.write("进项税税率")
        
        for i in range(total_period):
            with cols[i + 3]:
                st.write(f"第{i+1}年")
        
        # 外购原材料成本
        cols = st.columns(total_period + 3)
        with cols[0]:
            st.write("1")
        with cols[1]:
            st.write("外购原材料成本")
        with cols[2]:
            st.write("0.13")
        
        for i in range(total_period):
            with cols[i + 3]:
                if i < construction_period:
                    st.write("0")  # 建设期无成本
                else:
                    key = f"cost_year_{i+1}"
                    # 使用收入的一个百分比作为默认成本
                    income_key = f"income_year_{i+1}"
                    income_val = st.session_state.get(income_key, 0)
                    
                    default_cost = income_val * 0.1  # 默认为收入的10%
                    st.number_input(
                        f"第{i+1}年成本",
                        value=default_cost,
                        key=key,
                        label_visibility="collapsed",
                        help=f"第{i+1}年外购原材料成本"
                    )
    
    with st.expander("利润相关参数", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("企业所得税税率", value=0.25, key="tax_rate", step=0.01, help="企业所得税税率")
            st.number_input("盈余公积金比率", value=0.1, key="surplus_reserve_rate", step=0.01, help="盈余公积金比率")
        with col2:
            st.number_input("净现值内部收益率ic", value=0.06, key="discount_rate", step=0.01, help="净现值内部收益率ic")


def display_results(results):
    st.subheader("财务分析结果")
    
    # 现金流量表
    st.write("### 现金流量表")
    df_cf = pd.DataFrame({
        '年份': results['years'],
        '净现金流量': [round(cf, 2) for cf in results['cash_flow']],
        '累计净现金流量': [round(cfcf, 2) for cfcf in results['cumulative_cash_flow']]
    })
    
    st.dataframe(df_cf, width=1000)
    
    # 计算NPV和IRR
    discount_rate = st.session_state.get('discount_rate', 0.06)
    cash_flows = results['cash_flow']
    
    # 计算NPV
    npv = sum([cf / ((1 + discount_rate) ** i) for i, cf in enumerate(cash_flows, 0)])
    
    # 计算静态投资回收期
    cumulative_cf = results['cumulative_cash_flow']
    payback_period = None
    for i, cum_cf in enumerate(cumulative_cf):
        if cum_cf >= 0 and i > 0:
            # 找到首次转正的年份
            prev_cum_cf = cumulative_cf[i-1] if i > 0 else 0
            if cash_flows[i] != 0:
                payback_period = i + (abs(prev_cum_cf) / abs(cash_flows[i]))
                break
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("净现值(NPV)", f"{npv:.2f}万元")
    with col2:
        if payback_period:
            st.metric("静态投资回收期", f"{payback_period:.2f}年")
        else:
            st.metric("静态投资回收期", "未回收")
    with col3:
        # IRR计算较复杂，这里简化处理或使用近似方法
        st.metric("内部收益率(IRR)", "待计算")


def main():
    st.set_page_config(page_title="建设项目经济评价系统", layout="wide")
    
    # 渲染输入表单
    render_input_form()
    
    # 计算按钮
    if st.button("计算"):
        results = calculate_financial_model()
        display_results(results)

if __name__ == "__main__":
    main()