from decimal import Decimal
from typing import Dict, List, Union
from financial_core import FinancialModel, round_decimal, ProjectPeriod
from financial_calculator import FinancialCalculatorBase


def to_decimal(value: Union[float, str, int, Decimal]) -> Decimal:
    """将各种类型转换为Decimal"""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


class RevenueTaxCalculator(FinancialCalculatorBase):
    """营业收入及税金计算器 - 对应工作表6"""
    
    def calculate(self) -> bool:
        """计算营业收入及税金"""
        try:
            revenue_data = self.model.revenue
            tax_data = self.model.tax
            results = self.model.results
            
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_operation_year(year):
                    # 计算各项收入
                    factory_building = to_decimal(revenue_data.factory_building_revenue.get(year, Decimal('0')))
                    supporting_facility = to_decimal(revenue_data.supporting_facility_revenue.get(year, Decimal('0')))
                    property_service = to_decimal(revenue_data.property_service_revenue.get(year, Decimal('0')))
                    parking = to_decimal(revenue_data.parking_revenue.get(year, Decimal('0')))
                    advertising = to_decimal(revenue_data.advertising_revenue.get(year, Decimal('0')))
                    asset_sale = to_decimal(revenue_data.asset_sale_revenue.get(year, Decimal('0')))
                    
                    # 计算总收入
                    total_revenue = round_decimal(float(
                        factory_building + supporting_facility + 
                        property_service + parking + advertising + asset_sale
                    ))
                    results.annual_revenue[year_idx] = total_revenue
                    
                    # 计算销项税（根据不同税率）
                    # 假设：厂房、配套用房、车位、广告、资产销售税率9%，物业费税率6%
                    vat_output_9 = round_decimal(float(
                        (factory_building + supporting_facility + parking + advertising + asset_sale) * 
                        Decimal('0.09') / Decimal('1.09')
                    ))
                    vat_output_6 = round_decimal(float(
                        property_service * Decimal('0.06') / Decimal('1.06')
                    ))
                    
                    total_vat_output = round_decimal(float(vat_output_9 + vat_output_6))
                    results.annual_vat_output[year_idx] = total_vat_output
                else:
                    # 建设期无收入
                    results.annual_revenue[year_idx] = Decimal('0')
                    results.annual_vat_output[year_idx] = Decimal('0')
            
            return True
            
        except Exception as e:
            print(f"营业收入计算错误: {e}")
            return False


class ProfitCalculator(FinancialCalculatorBase):
    """利润计算器 - 对应工作表7"""
    
    def calculate(self) -> bool:
        """计算利润与利润分配"""
        try:
            results = self.model.results
            tax_data = self.model.tax
            parameters = self.model.parameters
            revenue_data = self.model.revenue
            
            cumulative_loss = Decimal('0')  # 累计亏损
            loss_history = []  # 亏损历史记录
            loss_offset_years = parameters.loss_offset_years
            
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_operation_year(year):
                    # 计算补贴收入
                    subsidy = to_decimal(tax_data.subsidy_income.get(year, Decimal('0')))
                    
                    # 计算税前利润
                    profit_before_tax = round_decimal(float(
                        results.annual_revenue[year_idx] +
                        subsidy -
                        results.annual_cost[year_idx] -
                        results.annual_depreciation[year_idx] -
                        results.annual_amortization[year_idx] -
                        results.annual_city_maintenance_tax[year_idx] -
                        results.annual_education_surtax[year_idx]
                    ))
                    
                    results.annual_profit_before_tax[year_idx] = profit_before_tax
                    
                    # 亏损弥补逻辑
                    if profit_before_tax >= 0:
                        # 有盈利，先弥补以前年度亏损
                        remaining_profit = profit_before_tax
                        
                        # 按时间顺序弥补亏损
                        if loss_history:
                            for i, loss in enumerate(loss_history[:loss_offset_years]):
                                if remaining_profit > 0:
                                    if loss <= remaining_profit:
                                        remaining_profit -= loss
                                        loss_history[i] = Decimal('0')
                                    else:
                                        loss_history[i] -= remaining_profit
                                        remaining_profit = Decimal('0')
                            
                            # 移除已完全弥补的亏损
                            loss_history = [loss for loss in loss_history if loss > 0]
                        
                        # 计算所得税
                        income_tax = round_decimal(float(remaining_profit * tax_data.income_tax_rate))
                    else:
                        # 当年亏损，加入亏损历史
                        loss_history.append(abs(profit_before_tax))
                        if len(loss_history) > loss_offset_years:
                            loss_history.pop(0)
                        income_tax = Decimal('0')
                    
                    results.annual_income_tax[year_idx] = income_tax
                    
                    # 计算税后利润
                    profit_after_tax = round_decimal(float(profit_before_tax - income_tax))
                    results.annual_profit_after_tax[year_idx] = profit_after_tax
                    
                    # 计算盈余公积金（税后利润的10%）
                    surplus_reserve = round_decimal(float(
                        profit_after_tax * parameters.surplus_reserve_rate
                    ))
                    
                    # 计算应付利润（税后利润 - 盈余公积金）
                    distributable_profit = round_decimal(float(profit_after_tax - surplus_reserve))
                else:
                    # 建设期无利润
                    results.annual_profit_before_tax[year_idx] = Decimal('0')
                    results.annual_income_tax[year_idx] = Decimal('0')
                    results.annual_profit_after_tax[year_idx] = Decimal('0')
            
            return True
            
        except Exception as e:
            print(f"利润计算错误: {e}")
            return False


class RevenueModule:
    """收益模块 - 整合工作表6-7"""
    
    def __init__(self, model: FinancialModel):
        self.model = model
        self.period = model.period
        self.calculators = {
            'revenue_tax': RevenueTaxCalculator(model),
            'profit': ProfitCalculator(model)
        }
    
    def calculate_all(self) -> bool:
        """执行收益模块所有计算"""
        try:
            # 按顺序执行计算
            calculation_order = [
                'revenue_tax',
                'profit'
            ]
            
            for calc_name in calculation_order:
                calculator = self.calculators[calc_name]
                if not calculator.calculate():
                    print(f"收益模块 {calc_name} 计算失败")
                    return False
            
            return True
            
        except Exception as e:
            print(f"收益模块计算错误: {e}")
            return False
    
    def get_revenue_summary(self) -> Dict[str, List[Decimal]]:
        """获取收入汇总数据"""
        revenue_data = self.model.revenue
        results = self.model.results
        
        return {
            'factory_building_revenue': [
                to_decimal(revenue_data.factory_building_revenue.get(year, Decimal('0'))) 
                for year in range(1, self.period.total_period + 1)
            ],
            'supporting_facility_revenue': [
                to_decimal(revenue_data.supporting_facility_revenue.get(year, Decimal('0'))) 
                for year in range(1, self.period.total_period + 1)
            ],
            'property_service_revenue': [
                to_decimal(revenue_data.property_service_revenue.get(year, Decimal('0'))) 
                for year in range(1, self.period.total_period + 1)
            ],
            'parking_revenue': [
                to_decimal(revenue_data.parking_revenue.get(year, Decimal('0'))) 
                for year in range(1, self.period.total_period + 1)
            ],
            'advertising_revenue': [
                to_decimal(revenue_data.advertising_revenue.get(year, Decimal('0'))) 
                for year in range(1, self.period.total_period + 1)
            ],
            'asset_sale_revenue': [
                to_decimal(revenue_data.asset_sale_revenue.get(year, Decimal('0'))) 
                for year in range(1, self.period.total_period + 1)
            ],
            'total_revenue': results.annual_revenue,
            'vat_output': results.annual_vat_output
        }
    
    def get_profit_summary(self) -> Dict[str, List[Decimal]]:
        """获取利润汇总数据"""
        results = self.model.results
        
        return {
            'profit_before_tax': results.annual_profit_before_tax,
            'income_tax': results.annual_income_tax,
            'profit_after_tax': results.annual_profit_after_tax
        }