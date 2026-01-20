from abc import ABC, abstractmethod
from typing import Dict, Optional
from decimal import Decimal
import numpy as np
from financial_core import (
    FinancialModel, ProjectPeriod, round_decimal, 
    InvestmentData, AssetData, RevenueData, CostData, 
    TaxData, CalculationResults
)


class FinancialCalculatorBase(ABC):
    """财务计算基类"""
    
    def __init__(self, model: FinancialModel):
        self.model = model
        self.period = model.period
    
    @abstractmethod
    def calculate(self) -> bool:
        """执行计算，返回是否成功"""
        pass
    
    def validate_inputs(self) -> bool:
        """验证输入数据"""
        return self.period.validate()


class InvestmentCalculator(FinancialCalculatorBase):
    """投资计算器"""
    
    def calculate(self) -> bool:
        """计算项目投资"""
        try:
            inv = self.model.investment
            assets = self.model.assets
            results = self.model.results
            
            # 计算固定资产原值（不含建设期利息）
            assets.fixed_assets_original_value = round_decimal(
                inv.building_cost +
                inv.equipment_procurement_cost +
                inv.equipment_installation_cost +
                inv.public_equipment_procurement_cost +
                inv.public_equipment_installation_cost +
                inv.construction_management_fee +
                inv.technical_consulting_fee +
                inv.infrastructure_fee +
                inv.patent_fee +
                inv.other_preparation_fee +
                inv.basic_contingency_reserve +
                inv.price_contingency_reserve
            )
            
            # 计算固定资产原值（含建设期利息）
            assets.fixed_assets_with_interest = round_decimal(
                assets.fixed_assets_original_value + inv.construction_interest
            )
            
            # 计算无形资产
            assets.intangible_assets = round_decimal(
                inv.land_use_fee + inv.patent_fee
            )
            
            # 计算其他资产
            assets.other_assets = round_decimal(
                inv.other_preparation_fee * 0.5  # 假设50%为其他资产
            )
            
            # 计算可抵扣进项税（简化计算）
            assets.deductible_tax = round_decimal(
                (inv.building_cost +
                 inv.equipment_procurement_cost +
                 inv.equipment_installation_cost +
                 inv.public_equipment_procurement_cost +
                 inv.public_equipment_installation_cost) * Decimal('0.09') / Decimal('1.09')
            )
            
            # 计算总投资
            total_investment = (
                assets.fixed_assets_with_interest +
                assets.intangible_assets +
                assets.other_assets +
                inv.working_capital
            )
            results.total_investment = round_decimal(total_investment)
            
            # 计算固定资产投资（按建设期分配）
            construction_period = self.period.construction_period
            total_fixed_assets = assets.fixed_assets_with_interest + assets.intangible_assets + assets.other_assets
            
            # 按建设期分配：40%, 30%, 30%
            if construction_period >= 3:
                results.fixed_assets_investment[0] = round_decimal(total_fixed_assets * Decimal('0.4'))
                results.fixed_assets_investment[1] = round_decimal(total_fixed_assets * Decimal('0.3'))
                results.fixed_assets_investment[2] = round_decimal(total_fixed_assets * Decimal('0.3'))
            else:
                # 如果建设期少于3年，平均分配
                investment_per_year = round_decimal(total_fixed_assets / Decimal(construction_period))
                for i in range(construction_period):
                    results.fixed_assets_investment[i] = investment_per_year
            
            # 计算流动资金投资（在运营期开始时投入）
            operation_start = self.period.operation_start_year - 1  # 转换为0-based索引
            if operation_start < len(results.working_capital_investment):
                results.working_capital_investment[operation_start] = round_decimal(inv.working_capital)
            
            return True
            
        except Exception as e:
            print(f"投资计算错误: {e}")
            return False


class DepreciationCalculator(FinancialCalculatorBase):
    """折旧摊销计算器"""
    
    def calculate(self) -> bool:
        """计算折旧和摊销"""
        try:
            assets = self.model.assets
            results = self.model.results
            
            # 计算年折旧额
            if assets.depreciation_years > 0:
                annual_depreciation = round_decimal(
                    assets.fixed_assets_with_interest * (Decimal('1') - assets.salvage_rate) / 
                    Decimal(assets.depreciation_years)
                )
            else:
                annual_depreciation = Decimal('0')
            
            # 计算年摊销额
            if assets.amortization_years > 0:
                annual_amortization = round_decimal(
                    assets.intangible_assets / Decimal(assets.amortization_years)
                )
            else:
                annual_amortization = Decimal('0')
            
            # 计算其他资产年摊销额
            if assets.other_assets_years > 0:
                annual_other_amortization = round_decimal(
                    assets.other_assets / Decimal(assets.other_assets_years)
                )
            else:
                annual_other_amortization = Decimal('0')
            
            # 填充各年折旧摊销数据
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_operation_year(year):
                    # 运营期计算折旧摊销
                    results.annual_depreciation[year_idx] = annual_depreciation
                    results.annual_amortization[year_idx] = round_decimal(annual_amortization + annual_other_amortization)
                else:
                    # 建设期无折旧摊销
                    results.annual_depreciation[year_idx] = Decimal('0')
                    results.annual_amortization[year_idx] = Decimal('0')
            
            return True
            
        except Exception as e:
            print(f"折旧摊销计算错误: {e}")
            return False


class RevenueCalculator(FinancialCalculatorBase):
    """收入计算器"""
    
    def calculate(self) -> bool:
        """计算收入和销项税"""
        try:
            revenue_data = self.model.revenue
            tax_data = self.model.tax
            results = self.model.results
            
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_operation_year(year):
                    # 计算总收入
                    total_revenue = revenue_data.get_total_revenue(year)
                    results.annual_revenue[year_idx] = total_revenue
                    
                    # 计算销项税（简化：假设总收入都适用9%税率）
                    if tax_data.vat_output_rate > 0:
                        vat_output = round_decimal(
                            total_revenue * tax_data.vat_output_rate / (Decimal('1') + tax_data.vat_output_rate)
                        )
                    else:
                        vat_output = Decimal('0')
                    
                    results.annual_vat_output[year_idx] = vat_output
                else:
                    # 建设期无收入
                    results.annual_revenue[year_idx] = Decimal('0')
                    results.annual_vat_output[year_idx] = Decimal('0')
            
            return True
            
        except Exception as e:
            print(f"收入计算错误: {e}")
            return False


class CostCalculator(FinancialCalculatorBase):
    """成本计算器"""
    
    def calculate(self) -> bool:
        """计算成本和进项税"""
        try:
            cost_data = self.model.cost
            tax_data = self.model.tax
            assets = self.model.assets
            results = self.model.results
            
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_operation_year(year):
                    # 计算总成本
                    total_cost = cost_data.get_total_cost(year)
                    
                    # 添加修理费（固定资产原值的0.5%）
                    repair_fee = round_decimal(assets.fixed_assets_with_interest * Decimal('0.005'))
                    total_cost = round_decimal(total_cost + repair_fee)
                    
                    results.annual_cost[year_idx] = total_cost
                    
                    # 计算进项税（简化：假设成本都适用13%税率）
                    if tax_data.vat_input_rate > 0:
                        vat_input = round_decimal(
                            total_cost * tax_data.vat_input_rate / (Decimal('1') + tax_data.vat_input_rate)
                        )
                    else:
                        vat_input = Decimal('0')
                    
                    results.annual_vat_input[year_idx] = vat_input
                else:
                    # 建设期无成本
                    results.annual_cost[year_idx] = Decimal('0')
                    results.annual_vat_input[year_idx] = Decimal('0')
            
            return True
            
        except Exception as e:
            print(f"成本计算错误: {e}")
            return False


class TaxCalculator(FinancialCalculatorBase):
    """税费计算器"""
    
    def calculate(self) -> bool:
        """计算税费"""
        try:
            tax_data = self.model.tax
            results = self.model.results
            
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                # 计算实缴增值税
                vat_output = results.annual_vat_output[year_idx]
                vat_input = results.annual_vat_input[year_idx]
                vat_paid = round_decimal(max(vat_output - vat_input, Decimal('0')))
                
                results.annual_vat_paid[year_idx] = vat_paid
                
                # 计算城市维护建设税
                city_maintenance_tax = round_decimal(vat_paid * tax_data.city_maintenance_tax_rate)
                results.annual_city_maintenance_tax[year_idx] = city_maintenance_tax
                
                # 计算教育费附加
                education_surtax = round_decimal(vat_paid * tax_data.education_surtax_rate)
                results.annual_education_surtax[year_idx] = education_surtax
            
            return True
            
        except Exception as e:
            print(f"税费计算错误: {e}")
            return False


class ProfitCalculator(FinancialCalculatorBase):
    """利润计算器"""
    
    def calculate(self) -> bool:
        """计算利润和所得税"""
        try:
            tax_data = self.model.tax
            parameters = self.model.parameters
            results = self.model.results
            
            cumulative_loss = Decimal('0')  # 累计亏损（用于亏损弥补）
            loss_offset_years = parameters.loss_offset_years
            loss_history = []  # 亏损历史记录
            
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_operation_year(year):
                    # 计算税前利润
                    profit_before_tax = round_decimal(
                        results.annual_revenue[year_idx] -
                        results.annual_cost[year_idx] -
                        results.annual_depreciation[year_idx] -
                        results.annual_amortization[year_idx] -
                        results.annual_city_maintenance_tax[year_idx] -
                        results.annual_education_surtax[year_idx]
                    )
                    
                    results.annual_profit_before_tax[year_idx] = profit_before_tax
                    
                    # 亏损弥补逻辑
                    if profit_before_tax >= 0:
                        # 有盈利，先弥补以前年度亏损
                        remaining_loss = Decimal('0')
                        if loss_history:
                            # 按时间顺序弥补亏损
                            for i, loss in enumerate(loss_history):
                                if remaining_loss <= 0 and i < loss_offset_years:
                                    remaining_loss = max(loss - profit_before_tax, Decimal('0'))
                                    profit_before_tax = max(profit_before_tax - loss, Decimal('0'))
                                    loss_history[i] = remaining_loss
                            loss_history = [loss for loss in loss_history if loss > 0]
                        
                        # 计算所得税
                        income_tax = round_decimal(profit_before_tax * tax_data.income_tax_rate)
                    else:
                        # 当年亏损，加入亏损历史
                        loss_history.append(abs(profit_before_tax))
                        if len(loss_history) > loss_offset_years:
                            loss_history.pop(0)  # 移除超过弥补期的亏损
                        income_tax = Decimal('0')
                    
                    results.annual_income_tax[year_idx] = income_tax
                    
                    # 计算税后利润
                    profit_after_tax = round_decimal(profit_before_tax - income_tax)
                    results.annual_profit_after_tax[year_idx] = profit_after_tax
                else:
                    # 建设期无利润
                    results.annual_profit_before_tax[year_idx] = Decimal('0')
                    results.annual_income_tax[year_idx] = Decimal('0')
                    results.annual_profit_after_tax[year_idx] = Decimal('0')
            
            return True
            
        except Exception as e:
            print(f"利润计算错误: {e}")
            return False


class CashFlowCalculator(FinancialCalculatorBase):
    """现金流量计算器"""
    
    def calculate(self) -> bool:
        """计算现金流量"""
        try:
            results = self.model.results
            
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_construction_year(year):
                    # 建设期：现金流入=0，现金流出=固定资产投资
                    cash_flow_in = Decimal('0')
                    cash_flow_out = results.fixed_assets_investment[year_idx]
                    
                    results.annual_cash_flow_in[year_idx] = cash_flow_in
                    results.annual_cash_flow_out[year_idx] = cash_flow_out
                    
                    # 净现金流量
                    net_cash_flow = round_decimal(cash_flow_in - cash_flow_out)
                    results.annual_net_cash_flow[year_idx] = net_cash_flow
                    
                elif self.period.is_operation_year(year):
                    # 运营期：现金流入=营业收入+固定资产销售收入，现金流出=经营成本+税费+流动资金投入
                    
                    # 现金流入
                    cash_flow_in = round_decimal(
                        results.annual_revenue[year_idx] +
                        self.model.revenue.asset_sale_revenue.get(year, Decimal('0'))
                    )
                    
                    # 现金流出
                    cash_flow_out = round_decimal(
                        results.annual_cost[year_idx] +
                        results.annual_income_tax[year_idx] +
                        results.annual_city_maintenance_tax[year_idx] +
                        results.annual_education_surtax[year_idx] +
                        results.working_capital_investment[year_idx]
                    )
                    
                    results.annual_cash_flow_in[year_idx] = cash_flow_in
                    results.annual_cash_flow_out[year_idx] = cash_flow_out
                    
                    # 净现金流量
                    net_cash_flow = round_decimal(cash_flow_in - cash_flow_out)
                    results.annual_net_cash_flow[year_idx] = net_cash_flow
                else:
                    # 其他年份
                    results.annual_cash_flow_in[year_idx] = Decimal('0')
                    results.annual_cash_flow_out[year_idx] = Decimal('0')
                    results.annual_net_cash_flow[year_idx] = Decimal('0')
            
            # 计算累计净现金流量
            cumulative = Decimal('0')
            for year_idx in range(self.period.total_period):
                cumulative += results.annual_net_cash_flow[year_idx]
                results.cumulative_cash_flow[year_idx] = round_decimal(cumulative)
            
            return True
            
        except Exception as e:
            print(f"现金流量计算错误: {e}")
            return False


class FinancialIndicatorsCalculator(FinancialCalculatorBase):
    """财务指标计算器"""
    
    def calculate(self) -> bool:
        """计算财务指标"""
        try:
            parameters = self.model.parameters
            results = self.model.results
            net_cash_flows = results.annual_net_cash_flow
            
            # 计算净现值(NPV)
            discount_rate = parameters.discount_rate
            npv = Decimal('0')
            for year_idx, cash_flow in enumerate(net_cash_flows):
                if cash_flow != 0:
                    discount_factor = Decimal('1') / (Decimal('1') + discount_rate) ** year_idx
                    npv += round_decimal(cash_flow * discount_factor)
            results.npv = round_decimal(npv)
            
            # 计算内部收益率(IRR)
            # 使用numpy的irr函数，转换为float进行计算
            try:
                float_cash_flows = [float(cf) for cf in net_cash_flows]
                irr_value = np.irr(float_cash_flows)
                results.irr = round_decimal(Decimal(str(irr_value)))
            except:
                results.irr = Decimal('0')
            
            # 计算静态投资回收期
            cumulative = results.cumulative_cash_flow
            static_payback = None
            for year_idx, cum_cf in enumerate(cumulative):
                if cum_cf >= 0 and year_idx > 0:
                    prev_cum_cf = cumulative[year_idx - 1]
                    cash_flow = net_cash_flows[year_idx]
                    if cash_flow != 0:
                        payback = year_idx + (abs(prev_cum_cf) / abs(cash_flow))
                        static_payback = float(payback)
                        break
            results.static_payback_period = static_payback
            
            # 计算动态投资回收期
            dynamic_payback = None
            cumulative_pv = Decimal('0')
            for year_idx, cash_flow in enumerate(net_cash_flows):
                discount_factor = Decimal('1') / (Decimal('1') + discount_rate) ** year_idx
                discounted_cf = round_decimal(cash_flow * discount_factor)
                cumulative_pv += discounted_cf
                
                if cumulative_pv >= 0 and year_idx > 0:
                    prev_cum_pv = cumulative_pv - discounted_cf
                    if discounted_cf != 0:
                        dynamic_payback = year_idx + (abs(prev_cum_pv) / abs(discounted_cf))
                        dynamic_payback = float(dynamic_payback)
                        break
            results.dynamic_payback_period = dynamic_payback
            
            return True
            
        except Exception as e:
            print(f"财务指标计算错误: {e}")
            return False


class FinancialCalculator:
    """综合财务计算引擎"""
    
    def __init__(self, model: FinancialModel):
        self.model = model
        self.calculators = {
            'investment': InvestmentCalculator(model),
            'depreciation': DepreciationCalculator(model),
            'revenue': RevenueCalculator(model),
            'cost': CostCalculator(model),
            'tax': TaxCalculator(model),
            'profit': ProfitCalculator(model),
            'cashflow': CashFlowCalculator(model),
            'indicators': FinancialIndicatorsCalculator(model)
        }
    
    def calculate_all(self) -> bool:
        """执行所有计算"""
        try:
            # 初始化结果
            self.model.initialize_results()
            
            # 按顺序执行计算
            calculation_order = [
                'investment',
                'depreciation',
                'revenue',
                'cost',
                'tax',
                'profit',
                'cashflow',
                'indicators'
            ]
            
            for calc_name in calculation_order:
                calculator = self.calculators[calc_name]
                if not calculator.calculate():
                    print(f"{calc_name} 计算失败")
                    return False
            
            return True
            
        except Exception as e:
            print(f"综合计算错误: {e}")
            return False
    
    def calculate_single(self, calculator_name: str) -> bool:
        """执行单个计算器"""
        if calculator_name in self.calculators:
            return self.calculators[calculator_name].calculate()
        else:
            print(f"未找到计算器: {calculator_name}")
            return False