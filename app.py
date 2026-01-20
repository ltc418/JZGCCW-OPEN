import streamlit as st
import pandas as pd
import json
import io
from decimal import Decimal
from financial_core import FinancialModel, round_decimal
from investment_module import InvestmentModule
from cost_module import CostModule
from revenue_module import RevenueModule
from financial_comprehensive_module import FinancialComprehensiveModule
from financial_calculator import FinancialCalculator
from excel_exporter import ExcelExporter


# 设置页面配置
st.set_page_config(
    page_title="建设项目经济评价系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_model():
    """初始化财务模型"""
    if 'model' not in st.session_state:
        st.session_state.model = FinancialModel()
        st.session_state.model.initialize_results()
    
    return st.session_state.model


def render_period_settings(model):
    """渲染项目期间设置"""
    st.subheader("项目期间设置")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        construction_period = st.number_input(
            "建设期（年）",
            min_value=1,
            max_value=10,
            value=model.period.construction_period,
            key="construction_period_input"
        )
    
    with col2:
        operation_period = st.number_input(
            "运营期（年）",
            min_value=1,
            max_value=50,
            value=model.period.operation_period,
            key="operation_period_input"
        )
    
    with col3:
        total_period = construction_period + operation_period
        st.number_input(
            "计算期（年）",
            value=total_period,
            disabled=True,
            key="total_period_display"
        )
    
    # 如果期间发生变化，更新模型
    if (construction_period != model.period.construction_period or 
        operation_period != model.period.operation_period):
        with st.spinner("正在更新期间配置..."):
            model.update_period(construction_period, operation_period)
        st.success("期间配置已更新！")
        st.rerun()


def render_project_basic_info(model):
    """渲染项目基本信息"""
    with st.expander("项目基本信息", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            model.basic_info.project_name = st.text_input(
                "项目名称",
                value=model.basic_info.project_name,
                key="project_name_input"
            )
        
        with col2:
            model.basic_info.prior_work_years = st.number_input(
                "前期工作年限（年）",
                min_value=1,
                max_value=30,
                value=model.basic_info.prior_work_years,
                key="prior_work_years_input"
            )


def render_investment_inputs(model):
    """渲染投资输入"""
    with st.expander("项目投资", expanded=True):
        st.write("### 工程费")
        col1, col2 = st.columns(2)
        
        with col1:
            model.investment.building_cost = Decimal(str(st.number_input(
                "1.1 建筑工程费（万元）",
                value=float(model.investment.building_cost),
                format="%.2f",
                key="building_cost_input"
            )))
            
            model.investment.equipment_procurement_cost = Decimal(str(st.number_input(
                "1.2.1 生产设备购置费（万元）",
                value=float(model.investment.equipment_procurement_cost),
                format="%.2f",
                key="equipment_procurement_cost_input"
            )))
            
            model.investment.equipment_installation_cost = Decimal(str(st.number_input(
                "1.2.2 生产设备安装费（万元）",
                value=float(model.investment.equipment_installation_cost),
                format="%.2f",
                key="equipment_installation_cost_input"
            )))
        
        with col2:
            model.investment.public_equipment_procurement_cost = Decimal(str(st.number_input(
                "1.3.1 公用设备购置费（万元）",
                value=float(model.investment.public_equipment_procurement_cost),
                format="%.2f",
                key="public_equipment_procurement_cost_input"
            )))
            
            model.investment.public_equipment_installation_cost = Decimal(str(st.number_input(
                "1.3.2 公用设备安装费（万元）",
                value=float(model.investment.public_equipment_installation_cost),
                format="%.2f",
                key="public_equipment_installation_cost_input"
            )))
        
        st.write("### 工程建设其他费")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            model.investment.construction_management_fee = Decimal(str(st.number_input(
                "2.1.1 建设单位管理费（万元）",
                value=float(model.investment.construction_management_fee),
                format="%.2f",
                key="construction_management_fee_input"
            )))
            
            model.investment.technical_consulting_fee = Decimal(str(st.number_input(
                "2.2 项目建设技术咨询费（万元）",
                value=float(model.investment.technical_consulting_fee),
                format="%.2f",
                key="technical_consulting_fee_input"
            )))
        
        with col2:
            model.investment.infrastructure_fee = Decimal(str(st.number_input(
                "2.3 基础设施建设费（万元）",
                value=float(model.investment.infrastructure_fee),
                format="%.2f",
                key="infrastructure_fee_input"
            )))
            
            model.investment.land_use_fee = Decimal(str(st.number_input(
                "2.4 土地使用费（万元）",
                value=float(model.investment.land_use_fee),
                format="%.2f",
                key="land_use_fee_input"
            )))
        
        with col3:
            model.investment.patent_fee = Decimal(str(st.number_input(
                "2.5 专利及专有技术费（万元）",
                value=float(model.investment.patent_fee),
                format="%.2f",
                key="patent_fee_input"
            )))
            
            model.investment.other_preparation_fee = Decimal(str(st.number_input(
                "2.6 工程准备及其他费（万元）",
                value=float(model.investment.other_preparation_fee),
                format="%.2f",
                key="other_preparation_fee_input"
            )))
        
        st.write("### 预备费")
        col1, col2 = st.columns(2)
        
        with col1:
            model.investment.basic_contingency_reserve = Decimal(str(st.number_input(
                "3.1 基本预备费（万元）",
                value=float(model.investment.basic_contingency_reserve),
                format="%.2f",
                key="basic_contingency_reserve_input"
            )))
        
        with col2:
            model.investment.price_contingency_reserve = Decimal(str(st.number_input(
                "3.2 涨价预备费（万元）",
                value=float(model.investment.price_contingency_reserve),
                format="%.2f",
                key="price_contingency_reserve_input"
            )))
        
        st.write("### 建设期利息与流动资金")
        col1, col2 = st.columns(2)
        
        with col1:
            model.investment.construction_interest = Decimal(str(st.number_input(
                "4. 建设期利息（万元）",
                value=float(model.investment.construction_interest),
                format="%.2f",
                key="construction_interest_input"
            )))
        
        with col2:
            model.investment.working_capital = Decimal(str(st.number_input(
                "5. 流动资金（万元）",
                value=float(model.investment.working_capital),
                format="%.2f",
                key="working_capital_input"
            )))


def render_revenue_inputs(model):
    """渲染收入输入"""
    with st.expander("项目经营收入", expanded=False):
        st.write("### 年度收入输入")
        st.write(f"年份范围：第{model.period.operation_start_year}年至第{model.period.total_period}年（运营期）")
        
        # 标准厂房收入
        st.write("#### 1. 标准厂房收入（销项税率9%）")
        cols = st.columns(5)
        for i, year in enumerate(model.period.operation_years_range[:5]):
            with cols[i]:
                default_value = float(model.revenue.factory_building_revenue.get(year, 0.0))
                value = st.number_input(
                    f"第{year}年",
                    value=default_value,
                    format="%.2f",
                    key=f"factory_building_revenue_{year}"
                )
                model.revenue.factory_building_revenue[year] = Decimal(str(value))
        
        # 配套用房收入
        st.write("#### 2. 配套用房招商收入（销项税率9%）")
        cols = st.columns(5)
        for i, year in enumerate(model.period.operation_years_range[:5]):
            with cols[i]:
                default_value = float(model.revenue.supporting_facility_revenue.get(year, 0.0))
                value = st.number_input(
                    f"第{year}年",
                    value=default_value,
                    format="%.2f",
                    key=f"supporting_facility_revenue_{year}"
                )
                model.revenue.supporting_facility_revenue[year] = Decimal(str(value))
        
        # 物业服务费收入
        st.write("#### 3. 物业服务费收入（销项税率6%）")
        cols = st.columns(5)
        for i, year in enumerate(model.period.operation_years_range[:5]):
            with cols[i]:
                default_value = float(model.revenue.property_service_revenue.get(year, 0.0))
                value = st.number_input(
                    f"第{year}年",
                    value=default_value,
                    format="%.2f",
                    key=f"property_service_revenue_{year}"
                )
                model.revenue.property_service_revenue[year] = Decimal(str(value))
        
        # 车位出租收入
        st.write("#### 4. 车位出租收入（销项税率9%）")
        cols = st.columns(5)
        for i, year in enumerate(model.period.operation_years_range[:5]):
            with cols[i]:
                default_value = float(model.revenue.parking_revenue.get(year, 0.0))
                value = st.number_input(
                    f"第{year}年",
                    value=default_value,
                    format="%.2f",
                    key=f"parking_revenue_{year}"
                )
                model.revenue.parking_revenue[year] = Decimal(str(value))
        
        # 广告栏出租收入
        st.write("#### 5. 广告栏出租收入（销项税率9%）")
        cols = st.columns(5)
        for i, year in enumerate(model.period.operation_years_range[:5]):
            with cols[i]:
                default_value = float(model.revenue.advertising_revenue.get(year, 0.0))
                value = st.number_input(
                    f"第{year}年",
                    value=default_value,
                    format="%.2f",
                    key=f"advertising_revenue_{year}"
                )
                model.revenue.advertising_revenue[year] = Decimal(str(value))
        
        # 固定资产销售收入
        st.write("#### 6. 固定资产销售收入（销项税率9%）")
        cols = st.columns(5)
        for i, year in enumerate(model.period.operation_years_range[:5]):
            with cols[i]:
                default_value = float(model.revenue.asset_sale_revenue.get(year, 0.0))
                value = st.number_input(
                    f"第{year}年",
                    value=default_value,
                    format="%.2f",
                    key=f"asset_sale_revenue_{year}"
                )
                model.revenue.asset_sale_revenue[year] = Decimal(str(value))


def render_cost_inputs(model):
    """渲染成本输入"""
    with st.expander("经营成本", expanded=False):
        st.write("### 年度成本输入")
        st.write(f"年份范围：第{model.period.operation_start_year}年至第{model.period.total_period}年（运营期）")
        
        # 外购原材料成本
        st.write("#### 1. 外购原材料成本（进项税率13%）")
        cols = st.columns(5)
        for i, year in enumerate(model.period.operation_years_range[:5]):
            with cols[i]:
                default_value = float(model.cost.material_cost.get(year, 0.0))
                value = st.number_input(
                    f"第{year}年",
                    value=default_value,
                    format="%.2f",
                    key=f"material_cost_{year}"
                )
                model.cost.material_cost[year] = Decimal(str(value))
        
        # 外购燃料及动力成本
        st.write("#### 2. 外购燃料及动力成本（进项税率9%）")
        cols = st.columns(5)
        for i, year in enumerate(model.period.operation_years_range[:5]):
            with cols[i]:
                default_value = float(model.cost.fuel_power_cost.get(year, 0.0))
                value = st.number_input(
                    f"第{year}年",
                    value=default_value,
                    format="%.2f",
                    key=f"fuel_power_cost_{year}"
                )
                model.cost.fuel_power_cost[year] = Decimal(str(value))
        
        # 工资福利成本
        st.write("#### 3. 工资福利成本")
        cols = st.columns(5)
        for i, year in enumerate(model.period.operation_years_range[:5]):
            with cols[i]:
                default_value = float(model.cost.labor_cost.get(year, 0.0))
                value = st.number_input(
                    f"第{year}年",
                    value=default_value,
                    format="%.2f",
                    key=f"labor_cost_{year}"
                )
                model.cost.labor_cost[year] = Decimal(str(value))
        
        # 其他费用
        st.write("#### 4. 其他费用")
        cols = st.columns(5)
        for i, year in enumerate(model.period.operation_years_range[:5]):
            with cols[i]:
                default_value = float(model.cost.other_cost.get(year, 0.0))
                value = st.number_input(
                    f"第{year}年",
                    value=default_value,
                    format="%.2f",
                    key=f"other_cost_{year}"
                )
                model.cost.other_cost[year] = Decimal(str(value))


def render_tax_parameters(model):
    """渲染税费参数"""
    with st.expander("税费参数", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            model.tax.vat_output_rate = Decimal(str(st.number_input(
                "销项税率",
                value=float(model.tax.vat_output_rate),
                format="%.2f",
                step=0.01,
                key="vat_output_rate_input"
            )))
            
            model.tax.vat_input_rate = Decimal(str(st.number_input(
                "进项税率",
                value=float(model.tax.vat_input_rate),
                format="%.2f",
                step=0.01,
                key="vat_input_rate_input"
            )))
        
        with col2:
            model.tax.city_maintenance_tax_rate = Decimal(str(st.number_input(
                "城市维护建设税率",
                value=float(model.tax.city_maintenance_tax_rate),
                format="%.2f",
                step=0.01,
                key="city_maintenance_tax_rate_input"
            )))
            
            model.tax.education_surtax_rate = Decimal(str(st.number_input(
                "教育费附加及地方教育费附加率",
                value=float(model.tax.education_surtax_rate),
                format="%.2f",
                step=0.01,
                key="education_surtax_rate_input"
            )))
        
        with col3:
            model.tax.income_tax_rate = Decimal(str(st.number_input(
                "企业所得税税率",
                value=float(model.tax.income_tax_rate),
                format="%.2f",
                step=0.01,
                key="income_tax_rate_input"
            )))
            
            model.parameters.surplus_reserve_rate = Decimal(str(st.number_input(
                "盈余公积金比率",
                value=float(model.parameters.surplus_reserve_rate),
                format="%.2f",
                step=0.01,
                key="surplus_reserve_rate_input"
            )))
        
        st.write("#### 财务参数")
        col1, col2 = st.columns(2)
        
        with col1:
            model.parameters.discount_rate = Decimal(str(st.number_input(
                "折现率（内部收益率ic）",
                value=float(model.parameters.discount_rate),
                format="%.2f",
                step=0.01,
                key="discount_rate_input"
            )))
        
        with col2:
            model.parameters.loss_offset_years = st.number_input(
                "亏损弥补年限（年）",
                min_value=1,
                max_value=10,
                value=model.parameters.loss_offset_years,
                key="loss_offset_years_input"
            )


def render_asset_parameters(model):
    """渲染资产参数"""
    with st.expander("资产参数", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            model.assets.depreciation_years = st.number_input(
                "固定资产折旧年限（年）",
                min_value=1,
                max_value=50,
                value=model.assets.depreciation_years,
                key="depreciation_years_input"
            )
        
        with col2:
            model.assets.salvage_rate = Decimal(str(st.number_input(
                "固定资产残值率",
                value=float(model.assets.salvage_rate),
                format="%.2f",
                step=0.01,
                key="salvage_rate_input"
            )))
        
        with col3:
            model.assets.amortization_years = st.number_input(
                "无形资产摊销年限（年）",
                min_value=1,
                max_value=100,
                value=model.assets.amortization_years,
                key="amortization_years_input"
            )


def calculate_all(model):
    """执行所有计算"""
    with st.spinner("正在进行财务计算..."):
        # 初始化结果
        model.initialize_results()
        
        # 执行投资模块计算
        investment_module = InvestmentModule(model)
        investment_module.calculate_all()
        
        # 执行成本模块计算
        cost_module = CostModule(model)
        cost_module.calculate_all()
        
        # 执行收益模块计算
        revenue_module = RevenueModule(model)
        revenue_module.calculate_all()
        
        # 执行财务综合模块计算
        financial_comprehensive_module = FinancialComprehensiveModule(model)
        financial_comprehensive_module.calculate_all()
    
    return True


def display_results(model):
    """显示计算结果"""
    st.subheader("📊 财务分析结果")
    
    # 显示关键指标
    st.write("### 关键财务指标")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "净现值(NPV)",
            f"{float(model.results.npv):,.2f}万元"
        )
    
    with col2:
        st.metric(
            "内部收益率(IRR)",
            f"{float(model.results.irr):.2%}"
        )
    
    with col3:
        if model.results.static_payback_period:
            st.metric(
                "静态投资回收期",
                f"{model.results.static_payback_period:.2f}年"
            )
        else:
            st.metric(
                "静态投资回收期",
                "未回收"
            )
    
    with col4:
        if model.results.dynamic_payback_period:
            st.metric(
                "动态投资回收期",
                f"{model.results.dynamic_payback_period:.2f}年"
            )
        else:
            st.metric(
                "动态投资回收期",
                "未回收"
            )
    
    with col5:
        st.metric(
            "项目总投资",
            f"{float(model.results.total_investment):,.2f}万元"
        )
    
    # 显示现金流量表
    st.write("### 项目投资现金流量表")
    cf_data = {
        '年份': list(range(1, model.period.total_period + 1)),
        '现金流入': [round(float(cf), 2) for cf in model.results.annual_cash_flow_in],
        '现金流出': [round(float(cf), 2) for cf in model.results.annual_cash_flow_out],
        '净现金流量': [round(float(cf), 2) for cf in model.results.annual_net_cash_flow],
        '累计净现金流量': [round(float(cf), 2) for cf in model.results.cumulative_cash_flow]
    }
    
    df_cf = pd.DataFrame(cf_data)
    st.dataframe(df_cf, width=1200, height=400)
    
    # 显示利润表
    st.write("### 利润表")
    profit_data = {
        '年份': list(range(1, model.period.total_period + 1)),
        '营业收入': [round(float(r), 2) for r in model.results.annual_revenue],
        '营业成本': [round(float(c), 2) for c in model.results.annual_cost],
        '折旧': [round(float(d), 2) for d in model.results.annual_depreciation],
        '摊销': [round(float(a), 2) for a in model.results.annual_amortization],
        '税前利润': [round(float(p), 2) for p in model.results.annual_profit_before_tax],
        '所得税': [round(float(t), 2) for t in model.results.annual_income_tax],
        '税后利润': [round(float(p), 2) for p in model.results.annual_profit_after_tax]
    }
    
    df_profit = pd.DataFrame(profit_data)
    st.dataframe(df_profit, width=1200, height=400)
    
    # 显示投资汇总
    st.write("### 投资汇总")
    investment_module = InvestmentModule(model)
    investment_summary = investment_module.get_investment_summary()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### 投资构成")
        inv_data = {
            '项目': ['工程费', '工程建设其他费', '预备费', '建设期利息', '流动资金'],
            '金额（万元）': [
                round(float(investment_summary['engineering_cost']), 2),
                round(float(investment_summary['other_construction_cost']), 2),
                round(float(investment_summary['contingency_reserve']), 2),
                round(float(investment_summary['construction_interest']), 2),
                round(float(investment_summary['working_capital']), 2)
            ]
        }
        df_inv = pd.DataFrame(inv_data)
        st.dataframe(df_inv)
    
    with col2:
        st.write("#### 资产形成")
        asset_data = {
            '资产类型': ['固定资产原值（不含利息）', '固定资产原值（含利息）', '无形资产', '总投资'],
            '金额（万元）': [
                round(float(investment_summary['fixed_assets_original_value']), 2),
                round(float(investment_summary['fixed_assets_with_interest']), 2),
                round(float(model.assets.intangible_assets), 2),
                round(float(investment_summary['total_investment']), 2)
            ]
        }
        df_asset = pd.DataFrame(asset_data)
        st.dataframe(df_asset)


def main():
    """主函数"""
    st.title("🏗️ 建设项目经济评价系统")
    st.markdown("---")
    
    # 初始化模型
    model = initialize_model()
    
    # 侧边栏
    with st.sidebar:
        st.header("导航")
        page = st.radio(
            "选择页面",
            ["数据输入", "计算结果", "系统设置"]
        )
    
    if page == "数据输入":
        # 渲染输入界面
        render_period_settings(model)
        render_project_basic_info(model)
        render_investment_inputs(model)
        render_revenue_inputs(model)
        render_cost_inputs(model)
        render_tax_parameters(model)
        render_asset_parameters(model)
        
        # 计算按钮
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🧮 开始计算", use_container_width=True, type="primary"):
                if calculate_all(model):
                    st.success("✅ 计算完成！")
                    st.rerun()
                else:
                    st.error("❌ 计算失败，请检查输入数据！")
    
    elif page == "计算结果":
        # 显示计算结果
        if model.results.npv != 0 or model.results.irr != 0:
            display_results(model)
        else:
            st.warning("⚠️ 还没有计算结果，请先在\"数据输入\"页面进行计算！")
    
    elif page == "系统设置":
        st.subheader("🔧 系统设置")
        
        # 数据保存/加载
        st.write("### 数据管理")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 保存数据"):
                data = model.to_dict()
                st.download_button(
                    label="下载配置文件",
                    data=json.dumps(data, indent=2, ensure_ascii=False),
                    file_name="financial_model_config.json",
                    mime="application/json"
                )
            
            if st.button("📊 导出Excel"):
                try:
                    exporter = ExcelExporter(model)
                    output = io.BytesIO()
                    
                    # 创建临时工作簿
                    import openpyxl
                    wb = openpyxl.Workbook()
                    # 获取默认工作表并删除
                    default_sheet = wb.active
                    if default_sheet:
                        wb.remove(default_sheet)
                    
                    # 创建各个工作表
                    exporter._create_cash_flow_sheet(wb)
                    exporter._create_profit_sheet(wb)
                    exporter._create_investment_sheet(wb)
                    exporter._create_summary_sheet(wb)
                    
                    # 保存到内存
                    wb.save(output)
                    output.seek(0)
                    
                    # 提供下载
                    st.download_button(
                        label="下载Excel文件",
                        data=output,
                        file_name="财务分析结果.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"导出失败: {e}")
        
        with col2:
            uploaded_file = st.file_uploader("上传配置文件", type=['json'])
            if uploaded_file is not None:
                data = json.load(uploaded_file)
                model = FinancialModel.from_dict(data)
                st.session_state.model = model
                st.success("✅ 配置文件加载成功！")
                st.rerun()
        
        # 系统信息
        st.write("### 系统信息")
        st.write(f"- 项目名称：{model.basic_info.project_name}")
        st.write(f"- 建设期：{model.period.construction_period}年")
        st.write(f"- 运营期：{model.period.operation_period}年")
        st.write(f"- 计算期：{model.period.total_period}年")
        st.write(f"- 数据精度：小数点后2位")
        st.write(f"- Python版本：3.x")
        st.write(f"- Streamlit版本：最新版")


if __name__ == "__main__":
    main()