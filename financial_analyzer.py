import streamlit as st
import pandas as pd
import numpy as np

def initialize_session_state():
    """初始化会话状态变量"""
    # 项目基本信息
    if 'project_name' not in st.session_state:
        st.session_state.project_name = "东兴电子产业园三期项目财务分析"
    if 'construction_period' not in st.session_state:
        st.session_state.construction_period = 3
    if 'operation_period' not in st.session_state:
        st.session_state.operation_period = 17
    if 'total_period' not in st.session_state:
        st.session_state.total_period = st.session_state.construction_period + st.session_state.operation_period

def calculate_financial_model():
    """计算财务模型"""
    # 获取用户输入的数据
    construction_period = st.session_state.get('construction_period', 3)
    operation_period = st.session_state.get('operation_period', 17)
    total_period = construction_period + operation_period
    
    # 项目投资部分 - 需要用户输入的数据
    building_cost = st.session_state.get('building_cost', 67062.86)  # 1.1 建筑工程费
    equipment_procurement_cost = st.session_state.get('equipment_procurement_cost', 0)  # 1.3.1 生产设备购置费
    equipment_installation_cost = st.session_state.get('equipment_installation_cost', 18299.19)  # 1.3.2 生产设备安装费
    other_construction_costs = st.session_state.get('other_construction_costs', 16870.944)  # 工程建设其他费
    contingency_reserve = st.session_state.get('contingency_reserve', 10532.08)  # 预备费
    construction_interest = st.session_state.get('construction_interest', 5721.185772330424)  # 建设期利息
    working_capital = st.session_state.get('working_capital', 90)  # 流动资金
    
    # 各类资产形成计算
    fixed_assets_without_interest = st.session_state.get('fixed_assets_without_interest', 100336.1972)
    fixed_assets_with_interest = fixed_assets_without_interest + construction_interest  # 包含建设期利息的固定资产原值
    land_use_right = st.session_state.get('land_use_right', 6505.72)  # 土地使用权
    patent_right = st.session_state.get('patent_right', 0)  # 专利权
    other_asset = st.session_state.get('other_asset', 294.1029)  # 其他资产
    deductible_tax = st.session_state.get('deductible_tax', 8716.8199)  # 可抵扣建设投资进项税
    
    # 固定资产折旧参数
    depreciation_years_house = st.session_state.get('depreciation_years_house', 20)  # 房屋建筑物折旧年限
    salvage_rate_house = st.session_state.get('salvage_rate_house', 0.05)  # 房屋建筑物残值率
    
    # 固定资产销售计划
    fixed_asset_sale_ratio = st.session_state.get('fixed_asset_sale_ratio', 0.25)  # 用于出售的固定资产占比
    fixed_asset_sale_amount = st.session_state.get('fixed_asset_sale_amount', 26514.34574308261)  # 用于出售的固定资产总额
    
    # 项目资金使用计划
    project_investment_total = building_cost + equipment_procurement_cost + equipment_installation_cost + \
                              other_construction_costs + contingency_reserve + construction_interest + working_capital
    
    # 初始化所有年份的数据
    years = list(range(1, total_period + 1))
    
    # 初始化各年数据数组
    revenue = [0.0] * total_period  # 营业收入
    operating_cost = [0.0] * total_period  # 经营成本
    VAT_output = [0.0] * total_period  # 销项税
    VAT_input = [0.0] * total_period  # 进项税
    VAT_paid = [0.0] * total_period  # 实缴增值税
    VAT_refund = [0.0] * total_period  # 增值税退税
    business_tax = [0.0] * total_period  # 营业税
    city_maintenance_tax = [0.0] * total_period  # 城市维护建设税
    education_surcharge = [0.0] * total_period  # 教育费附加
    local_education_surcharge = [0.0] * total_period  # 地方教育费附加
    land_value_tax = [0.0] * total_period  # 土地增值税
    income_tax = [0.0] * total_period  # 所得税
    profit_before_tax = [0.0] * total_period  # 税前利润
    profit_after_tax = [0.0] * total_period  # 税后利润
    depreciation = [0.0] * total_period  # 折旧
    amortization = [0.0] * total_period  # 摊销
    interest_payment = [0.0] * total_period  # 利息支付
    principal_repayment = [0.0] * total_period  # 本金偿还
    loan_balance = [0.0] * total_period  # 贷款余额
    fixed_asset_investment = [0.0] * total_period  # 固定资产投资
    working_capital_investment = [0.0] * total_period  # 流动资金投资
    cash_flow_in = [0.0] * total_period  # 现金流入
    cash_flow_out = [0.0] * total_period  # 现金流出
    net_cash_flow = [0.0] * total_period  # 净现金流量
    cumulative_cash_flow = [0.0] * total_period  # 累计净现金流量
    
    # 读取用户输入的每年收入数据
    for i in range(construction_period, total_period):
        key = f"income_year_{i+1}"
        revenue[i] = st.session_state.get(key, 0.0)
    
    # 读取用户输入的每年成本数据
    for i in range(construction_period, total_period):
        key = f"cost_year_{i+1}"
        operating_cost[i] = st.session_state.get(key, revenue[i] * 0.1)  # 默认成本为收入的10%
    
    # 计算每年的折旧
    annual_depreciation = fixed_assets_with_interest * (1 - salvage_rate_house) / depreciation_years_house
    for i in range(construction_period, total_period):
        depreciation[i] = annual_depreciation
    
    # 计算每年的现金流
    for i in range(total_period):
        year_idx = i
        
        if year_idx < construction_period:
            # 建设期投资
            if year_idx == 0:
                fixed_asset_investment[year_idx] = project_investment_total * 0.4
            elif year_idx == 1:
                fixed_asset_investment[year_idx] = project_investment_total * 0.3
            else:
                fixed_asset_investment[year_idx] = project_investment_total * 0.3
                
            cash_flow_out[year_idx] = fixed_asset_investment[year_idx]
            net_cash_flow[year_idx] = -cash_flow_out[year_idx]
        else:
            # 运营期
            cash_flow_in[year_idx] = revenue[year_idx]
            
            # 计算税费
            VAT_output[year_idx] = revenue[year_idx] * 0.09 / 1.09  # 9%销项税
            VAT_paid[year_idx] = max(0, VAT_output[year_idx] - VAT_input[year_idx])  # 实际缴纳的增值税
            city_maintenance_tax[year_idx] = VAT_paid[year_idx] * 0.07  # 城建税 7%
            education_surcharge[year_idx] = VAT_paid[year_idx] * 0.03  # 教育费附加 3%
            local_education_surcharge[year_idx] = VAT_paid[year_idx] * 0.02  # 地方教育费附加 2%
            
            # 税前利润
            profit_before_tax[year_idx] = revenue[year_idx] - operating_cost[year_idx] - depreciation[year_idx] - \
                                        city_maintenance_tax[year_idx] - education_surcharge[year_idx] - \
                                        local_education_surcharge[year_idx] - land_value_tax[year_idx]
            
            # 所得税（亏损不交税）
            income_tax[year_idx] = max(0, profit_before_tax[year_idx] * 0.25)
            
            # 现金流出
            cash_flow_out[year_idx] = operating_cost[year_idx] + city_maintenance_tax[year_idx] + \
                                     education_surcharge[year_idx] + local_education_surcharge[year_idx] + \
                                     income_tax[year_idx] + land_value_tax[year_idx]
            
            # 净现金流量
            net_cash_flow[year_idx] = cash_flow_in[year_idx] - cash_flow_out[year_idx]
    
    # 计算累计净现金流量
    for i in range(total_period):
        if i == 0:
            cumulative_cash_flow[i] = net_cash_flow[i]
        else:
            cumulative_cash_flow[i] = cumulative_cash_flow[i-1] + net_cash_flow[i]
    
    # 计算NPV
    discount_rate = st.session_state.get('discount_rate', 0.06)
    npv = sum([net_cash_flow[i] / ((1 + discount_rate) ** i) for i in range(total_period)])
    
    # 计算静态投资回收期
    payback_period = None
    for i in range(1, total_period):
        if cumulative_cash_flow[i] >= 0 and cumulative_cash_flow[i-1] < 0:
            payback_period = i + (abs(cumulative_cash_flow[i-1]) / net_cash_flow[i])
            break
    
    return {
        'years': years,
        'revenue': revenue,
        'operating_cost': operating_cost,
        'depreciation': depreciation,
        'net_cash_flow': net_cash_flow,
        'cumulative_cash_flow': cumulative_cash_flow,
        'construction_period': construction_period,
        'operation_period': operation_period,
        'total_period': total_period,
        'npv': npv,
        'payback_period': payback_period,
        'income_tax': income_tax,
        'city_maintenance_tax': city_maintenance_tax,
        'education_surcharge': education_surcharge,
        'local_education_surcharge': local_education_surcharge
    }

def render_input_form():
    """渲染输入表单"""
    st.title("建设项目经济评价系统")
    st.subheader("建筑工程财务模型参数")
    
    with st.expander("项目基本信息", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("项目名称", value=st.session_state.get('project_name', "东兴电子产业园三期项目财务分析"), key="project_name")
        with col2:
            col_a, col_b = st.columns(2)
            with col_a:
                st.number_input("建设期(年)", min_value=1, max_value=10, value=st.session_state.get('construction_period', 3), key="construction_period")
            with col_b:
                st.number_input("运营期(年)", min_value=1, max_value=50, value=st.session_state.get('operation_period', 17), key="operation_period")
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
            st.number_input("含税投资", value=st.session_state.get('building_cost', 67062.86), 
                           key="building_cost", format="%.2f", help="建筑工程费含税投资")
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
            st.number_input("含税投资", value=st.session_state.get('equipment_cost', 2360.38), 
                           key="equipment_cost", format="%.2f", help="建筑设备费含税投资")
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
            st.number_input("含税投资", value=st.session_state.get('equipment_installation_cost', 18299.19), 
                           key="equipment_installation_cost", format="%.2f", help="建筑设备安装费含税投资")
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
            st.number_input("含税投资", value=st.session_state.get('equipment_procurement_cost', 0.0), 
                           key="equipment_procurement_cost", format="%.2f", help="生产设备购置费含税投资")
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
            st.number_input("含税投资", value=st.session_state.get('production_equipment_installation_cost', 0.0), 
                           key="production_equipment_installation_cost", format="%.2f", help="生产设备安装费含税投资")
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
        st.number_input("工程建设其他费", value=st.session_state.get('other_construction_costs', 16870.944), 
                       key="other_construction_costs", format="%.2f", help="工程建设其他费")
        
        # 预备费
        st.write("3 预备费")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("基本预备费", value=st.session_state.get('contingency_reserve', 10532.08), 
                           key="contingency_reserve", format="%.2f", help="基本预备费")
        with col2:
            st.number_input("涨价预备费", value=st.session_state.get('price_increase_reserve', 0.0), 
                           key="price_increase_reserve", format="%.2f", help="涨价预备费")
        
        # 建设期利息
        st.write("4 建设期利息")
        st.number_input("建设期利息", value=st.session_state.get('construction_interest', 5721.185772330424), 
                       key="construction_interest", format="%.2f", help="建设期利息")
        
        # 流动资金
        st.write("5 流动资金")
        st.number_input("流动资金", value=st.session_state.get('working_capital', 90.0), 
                       key="working_capital", format="%.2f", help="流动资金")
    
    with st.expander("各类资产形成计算", expanded=True):
        st.write("**各类资产形成计算（根据项目投资归类计算）**")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write("序号")
        with col2:
            st.write("项目")
        with col3:
            st.write("合计")
        with col4:
            st.write("折旧、摊销年限")
        with col5:
            st.write("残值率")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write("1")
        with col2:
            st.write("固定资产")
        with col3:
            fixed_assets_without_interest = st.session_state.get('building_cost', 67062.86) + \
                                           st.session_state.get('equipment_cost', 2360.38) + \
                                           st.session_state.get('equipment_installation_cost', 18299.19) + \
                                           st.session_state.get('equipment_procurement_cost', 0) + \
                                           st.session_state.get('production_equipment_installation_cost', 0) + \
                                           st.session_state.get('other_construction_costs', 16870.944) + \
                                           st.session_state.get('contingency_reserve', 10532.08)
            st.number_input("固定资产原值（不含建设期利息）", value=fixed_assets_without_interest, 
                           key="fixed_assets_without_interest", format="%.2f", disabled=True)
        with col4:
            st.number_input("折旧年限", value=st.session_state.get('depreciation_years_house', 20), 
                           key="depreciation_years_house", min_value=1, help="固定资产折旧年限")
        with col5:
            st.number_input("残值率", value=st.session_state.get('salvage_rate_house', 0.05), 
                           key="salvage_rate_house", min_value=0.0, max_value=1.0, step=0.01, help="固定资产残值率")
    
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
                        value=st.session_state.get(key, default_val),
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
                        value=st.session_state.get(key, default_cost),
                        key=key,
                        label_visibility="collapsed",
                        help=f"第{i+1}年外购原材料成本"
                    )
    
    with st.expander("利润相关参数", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("企业所得税税率", value=st.session_state.get('tax_rate', 0.25), 
                           key="tax_rate", step=0.01, min_value=0.0, max_value=1.0, help="企业所得税税率")
            st.number_input("盈余公积金比率", value=st.session_state.get('surplus_reserve_rate', 0.1), 
                           key="surplus_reserve_rate", step=0.01, min_value=0.0, max_value=1.0, help="盈余公积金比率")
        with col2:
            st.number_input("净现值内部收益率ic", value=st.session_state.get('discount_rate', 0.06), 
                           key="discount_rate", step=0.01, help="净现值内部收益率ic")


def display_results(results):
    """显示计算结果"""
    st.subheader("财务分析结果")
    
    # 现金流量表
    st.write("### 项目投资现金流量表")
    df_cf = pd.DataFrame({
        '年份': results['years'],
        '现金流入': [round(cf, 2) for cf in results['revenue']],
        '营业收入': [round(rev, 2) for rev in results['revenue']],
        '现金流出': [round(oc + dt + cm + es + les, 2) for oc, dt, cm, es, les in 
                    zip(results['operating_cost'], 
                        results['income_tax'], 
                        results['city_maintenance_tax'], 
                        results['education_surcharge'], 
                        results['local_education_surcharge'])],
        '经营成本': [round(oc, 2) for oc in results['operating_cost']],
        '所得税': [round(tax, 2) for tax in results['income_tax']],
        '净现金流量': [round(cf, 2) for cf in results['net_cash_flow']],
        '累计净现金流量': [round(cfcf, 2) for cfcf in results['cumulative_cash_flow']]
    })
    
    st.dataframe(df_cf, width=1200)
    
    # 显示关键指标
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("净现值(NPV)", f"{results['npv']:.2f}万元")
    with col2:
        if results['payback_period']:
            st.metric("静态投资回收期", f"{results['payback_period']:.2f}年")
        else:
            st.metric("静态投资回收期", "未回收")
    with col3:
        # 计算IRR（简化的近似算法）
        try:
            cash_flows = results['net_cash_flow']
            # 使用numpy的irr函数计算
            irr = np.irr(cash_flows)
            st.metric("内部收益率(IRR)", f"{irr:.2%}")
        except:
            st.metric("内部收益率(IRR)", "无法计算")


def main():
    """主函数"""
    st.set_page_config(page_title="建设项目经济评价系统", layout="wide")
    
    # 初始化会话状态
    initialize_session_state()
    
    # 渲染输入表单
    render_input_form()
    
    # 计算按钮
    if st.button("计算"):
        with st.spinner("正在计算中..."):
            results = calculate_financial_model()
        display_results(results)

if __name__ == "__main__":
    main()