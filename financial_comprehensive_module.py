from decimal import Decimal
from typing import Dict, List, Optional
from financial_core import FinancialModel, round_decimal, ProjectPeriod
from financial_calculator import FinancialCalculatorBase


def to_decimal(value) -> Decimal:
    """将各种类型转换为Decimal"""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


class CashFlowStatementCalculator(FinancialCalculatorBase):
    """现金流量表计算器 - 对应工作表8的核心部分"""
    
    def calculate(self) -> bool:
        """计算现金流量表"""
        try:
            results = self.model.results
            revenue_data = self.model.revenue
            tax_data = self.model.tax
            
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_construction_year(year):
                    # 建设期现金流量
                    # 现金流入=0
                    cash_flow_in = Decimal('0')
                    results.annual_cash_flow_in[year_idx] = cash_flow_in
                    
                    # 现金流出=固定资产投资
                    cash_flow_out = results.fixed_assets_investment[year_idx]
                    results.annual_cash_flow_out[year_idx] = cash_flow_out
                    
                    # 净现金流量
                    net_cash_flow = round_decimal(float(cash_flow_in - cash_flow_out))
                    results.annual_net_cash_flow[year_idx] = net_cash_flow
                    
                elif self.period.is_operation_year(year):
                    # 运营期现金流量
                    # 现金流入=营业收入+固定资产销售收入+回收流动资金+回收固定资产余值
                    cash_flow_in = round_decimal(float(
                        results.annual_revenue[year_idx] +
                        to_decimal(revenue_data.asset_sale_revenue.get(year, Decimal('0')))
                    ))
                    results.annual_cash_flow_in[year_idx] = cash_flow_in
                    
                    # 现金流出=经营成本+所得税+附加税费+流动资金投资
                    # 经营成本=总成本-折旧-摊销
                    operating_cost = round_decimal(float(
                        results.annual_cost[year_idx] -
                        results.annual_depreciation[year_idx] -
                        results.annual_amortization[year_idx]
                    ))
                    
                    cash_flow_out = round_decimal(float(
                        operating_cost +
                        results.annual_income_tax[year_idx] +
                        results.annual_city_maintenance_tax[year_idx] +
                        results.annual_education_surtax[year_idx] +
                        results.working_capital_investment[year_idx]
                    ))
                    results.annual_cash_flow_out[year_idx] = cash_flow_out
                    
                    # 净现金流量
                    net_cash_flow = round_decimal(float(cash_flow_in - cash_flow_out))
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
                results.cumulative_cash_flow[year_idx] = round_decimal(float(cumulative))
            
            return True
            
        except Exception as e:
            print(f"现金流量表计算错误: {e}")
            return False


class FinancialIndicatorsCalculator(FinancialCalculatorBase):
    """财务指标计算器"""
    
    def calculate_irr(self, cash_flows):
        """使用二分法计算IRR"""
        lower_rate = -0.9  # 下限
        upper_rate = 1.0   # 上限
        tolerance = 0.0001  # 容差
        max_iterations = 1000
        
        mid_rate = 0.0
        
        for _ in range(max_iterations):
            mid_rate = (lower_rate + upper_rate) / 2
            npv_mid = sum(cf / ((1 + mid_rate) ** i) for i, cf in enumerate(cash_flows))
            
            if abs(npv_mid) < tolerance:
                return mid_rate
            
            if npv_mid > 0:
                lower_rate = mid_rate
            else:
                upper_rate = mid_rate
        
        return mid_rate
    
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
                    npv += round_decimal(float(cash_flow * discount_factor))
            results.npv = round_decimal(float(npv))
            
            # 计算内部收益率(IRR)
            try:
                float_cash_flows = [float(cf) for cf in net_cash_flows]
                irr_value = self.calculate_irr(float_cash_flows)
                results.irr = round_decimal(float(irr_value))
            except Exception as e:
                print(f"IRR计算错误: {e}")
                results.irr = Decimal('0')
            
            # 计算静态投资回收期
            cumulative = results.cumulative_cash_flow
            static_payback = None
            for year_idx in range(1, len(cumulative)):
                if cumulative[year_idx] >= 0 and cumulative[year_idx - 1] < 0:
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
                if cash_flow != 0:
                    discount_factor = Decimal('1') / (Decimal('1') + discount_rate) ** year_idx
                    discounted_cf = round_decimal(float(cash_flow * discount_factor))
                else:
                    discounted_cf = Decimal('0')
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


class FinancialComprehensiveModule:
    """财务综合模块 - 整合工作表8"""
    
    def __init__(self, model: FinancialModel):
        self.model = model
        self.period = model.period
        self.calculators = {
            'cash_flow': CashFlowStatementCalculator(model),
            'indicators': FinancialIndicatorsCalculator(model)
        }
    
    def calculate_all(self) -> bool:
        """执行财务综合模块所有计算"""
        try:
            # 按顺序执行计算
            calculation_order = [
                'cash_flow',
                'indicators'
            ]
            
            for calc_name in calculation_order:
                calculator = self.calculators[calc_name]
                if not calculator.calculate():
                    print(f"财务综合模块 {calc_name} 计算失败")
                    return False
            
            return True
            
        except Exception as e:
            print(f"财务综合模块计算错误: {e}")
            return False
    
    def get_cash_flow_statement(self) -> Dict[str, List]:
        """获取现金流量表数据"""
        results = self.model.results
        
        return {
            'years': list(range(1, self.period.total_period + 1)),
            'cash_flow_in': results.annual_cash_flow_in,
            'cash_flow_out': results.annual_cash_flow_out,
            'net_cash_flow': results.annual_net_cash_flow,
            'cumulative_cash_flow': results.cumulative_cash_flow
        }
    
    def get_financial_indicators(self) -> Dict[str, float]:
        """获取财务指标数据"""
        results = self.model.results
        
        return {
            'npv': float(results.npv),
            'irr': float(results.irr),
            'static_payback_period': results.static_payback_period if results.static_payback_period else 0.0,
            'dynamic_payback_period': results.dynamic_payback_period if results.dynamic_payback_period else 0.0
        }
    
    def get_profitability_analysis(self) -> Dict[str, Dict]:
        """获取盈利能力分析"""
        results = self.model.results
        
        # 计算累计税后利润
        total_profit_after_tax = sum(results.annual_profit_after_tax)
        
        # 计算累计所得税
        total_income_tax = sum(results.annual_income_tax)
        
        # 计算平均投资回报率
        operation_years = sum(1 for i in range(self.period.total_period) 
                              if self.period.is_operation_year(i + 1))
        
        if operation_years > 0:
            avg_profit_after_tax = total_profit_after_tax / Decimal(operation_years)
            avg_income_tax = total_income_tax / Decimal(operation_years)
        else:
            avg_profit_after_tax = Decimal('0')
            avg_income_tax = Decimal('0')
        
        return {
            'total_profit_after_tax': {
                'value': float(total_profit_after_tax),
                'unit': '万元'
            },
            'total_income_tax': {
                'value': float(total_income_tax),
                'unit': '万元'
            },
            'avg_profit_after_tax': {
                'value': float(avg_profit_after_tax),
                'unit': '万元/年'
            },
            'avg_income_tax': {
                'value': float(avg_income_tax),
                'unit': '万元/年'
            },
            'total_investment': {
                'value': float(results.total_investment),
                'unit': '万元'
            }
        }
    
    def get_solvency_analysis(self) -> Dict[str, Dict]:
        """获取偿债能力分析"""
        results = self.model.results
        
        # 计算资产负债率（简化）
        # 假设借款占总投资的70%
        total_debt = round_decimal(float(results.total_investment * Decimal('0.7')))
        debt_ratio = round_decimal(float(total_debt / results.total_investment * Decimal('100')))
        
        return {
            'total_debt': {
                'value': float(total_debt),
                'unit': '万元'
            },
            'debt_ratio': {
                'value': float(debt_ratio),
                'unit': '%'
            }
        }