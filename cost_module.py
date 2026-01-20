from decimal import Decimal
from typing import Dict, List
from financial_core import FinancialModel, round_decimal, ProjectPeriod
from financial_calculator import FinancialCalculatorBase


class MaterialCostCalculator(FinancialCalculatorBase):
    """外购原材料费用计算器 - 对应工作表5-1"""
    
    def calculate(self) -> bool:
        """计算外购原材料费用"""
        try:
            cost_data = self.model.cost
            results = self.model.results
            
            # 简化版本：使用用户输入的材料成本
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_operation_year(year):
                    # 获取用户输入的材料成本
                    material_cost = cost_data.material_cost.get(year, Decimal('0'))
                    
                    # 计算进项税（假设税率13%）
                    vat_input = round_decimal(
                        material_cost * Decimal('0.13') / Decimal('1.13')
                    )
                    
                    # 更新结果（这里简化处理，不单独存储材料成本）
                    pass
                else:
                    pass
            
            return True
            
        except Exception as e:
            print(f"材料成本计算错误: {e}")
            return False


class FuelPowerCostCalculator(FinancialCalculatorBase):
    """外购燃料动力费计算器 - 对应工作表5-2"""
    
    def calculate(self) -> bool:
        """计算外购燃料动力费"""
        try:
            cost_data = self.model.cost
            results = self.model.results
            
            # 简化版本：使用用户输入的燃料动力成本
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_operation_year(year):
                    # 获取用户输入的燃料动力成本
                    fuel_power_cost = cost_data.fuel_power_cost.get(year, Decimal('0'))
                    
                    # 计算进项税（假设税率9%）
                    vat_input = round_decimal(
                        fuel_power_cost * Decimal('0.09') / Decimal('1.09')
                    )
                    
                    # 更新结果
                    pass
                else:
                    pass
            
            return True
            
        except Exception as e:
            print(f"燃料动力成本计算错误: {e}")
            return False


class LaborCostCalculator(FinancialCalculatorBase):
    """工资及福利费计算器 - 对应工作表5-3"""
    
    def calculate(self) -> bool:
        """计算工资及福利费"""
        try:
            cost_data = self.model.cost
            results = self.model.results
            
            # 简化版本：使用用户输入的工资成本
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_operation_year(year):
                    # 获取用户输入的工资成本
                    labor_cost = cost_data.labor_cost.get(year, Decimal('0'))
                    
                    # 更新结果
                    pass
                else:
                    pass
            
            return True
            
        except Exception as e:
            print(f"工资成本计算错误: {e}")
            return False


class RepairCostCalculator(FinancialCalculatorBase):
    """修理费计算器 - 对应工作表5-4的一部分"""
    
    def calculate(self) -> bool:
        """计算修理费"""
        try:
            assets = self.model.assets
            cost_data = self.model.cost
            results = self.model.results
            
            # 修理费按固定资产原值的0.5%计算
            repair_rate = Decimal('0.005')
            annual_repair_fee = round_decimal(
                assets.fixed_assets_with_interest * repair_rate
            )
            
            # 填充各年修理费数据
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_operation_year(year):
                    # 运营期计算修理费
                    cost_data.repair_cost[year] = annual_repair_fee
                else:
                    # 建设期无修理费
                    cost_data.repair_cost[year] = Decimal('0')
            
            return True
            
        except Exception as e:
            print(f"修理费计算错误: {e}")
            return False


class DepreciationCostCalculator(FinancialCalculatorBase):
    """固定资产折旧费计算器 - 对应工作表5-4"""
    
    def calculate(self) -> bool:
        """计算固定资产折旧费"""
        try:
            assets = self.model.assets
            results = self.model.results
            
            # 计算年折旧额
            if assets.depreciation_years > 0:
                annual_depreciation = round_decimal(
                    assets.fixed_assets_with_interest * 
                    (Decimal('1') - assets.salvage_rate) / 
                    Decimal(assets.depreciation_years)
                )
            else:
                annual_depreciation = Decimal('0')
            
            # 填充各年折旧数据
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_operation_year(year):
                    # 运营期计算折旧
                    results.annual_depreciation[year_idx] = annual_depreciation
                else:
                    # 建设期无折旧
                    results.annual_depreciation[year_idx] = Decimal('0')
            
            return True
            
        except Exception as e:
            print(f"折旧费计算错误: {e}")
            return False


class AmortizationCostCalculator(FinancialCalculatorBase):
    """无形资产摊销费计算器 - 对应工作表5-5"""
    
    def calculate(self) -> bool:
        """计算无形资产摊销费"""
        try:
            assets = self.model.assets
            results = self.model.results
            
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
            
            # 填充各年摊销数据
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_operation_year(year):
                    # 运营期计算摊销
                    results.annual_amortization[year_idx] = round_decimal(
                        annual_amortization + annual_other_amortization
                    )
                else:
                    # 建设期无摊销
                    results.annual_amortization[year_idx] = Decimal('0')
            
            return True
            
        except Exception as e:
            print(f"摊销费计算错误: {e}")
            return False


class TotalCostCalculator(FinancialCalculatorBase):
    """总成本费用汇总计算器 - 对应工作表5"""
    
    def calculate(self) -> bool:
        """计算总成本费用"""
        try:
            cost_data = self.model.cost
            results = self.model.results
            
            for year_idx in range(self.period.total_period):
                year = year_idx + 1
                
                if self.period.is_operation_year(year):
                    # 计算总成本
                    total_cost = round_decimal(
                        cost_data.material_cost.get(year, Decimal('0')) +
                        cost_data.fuel_power_cost.get(year, Decimal('0')) +
                        cost_data.labor_cost.get(year, Decimal('0')) +
                        cost_data.repair_cost.get(year, Decimal('0')) +
                        cost_data.other_cost.get(year, Decimal('0'))
                    )
                    
                    results.annual_cost[year_idx] = total_cost
                else:
                    # 建设期无成本
                    results.annual_cost[year_idx] = Decimal('0')
            
            return True
            
        except Exception as e:
            print(f"总成本计算错误: {e}")
            return False


class CostModule:
    """成本模块 - 整合工作表5-1到5-5"""
    
    def __init__(self, model: FinancialModel):
        self.model = model
        self.calculators = {
            'material': MaterialCostCalculator(model),
            'fuel_power': FuelPowerCostCalculator(model),
            'labor': LaborCostCalculator(model),
            'repair': RepairCostCalculator(model),
            'depreciation': DepreciationCostCalculator(model),
            'amortization': AmortizationCostCalculator(model),
            'total': TotalCostCalculator(model)
        }
    
    def calculate_all(self) -> bool:
        """执行成本模块所有计算"""
        try:
            # 按顺序执行计算
            calculation_order = [
                'material',
                'fuel_power',
                'labor',
                'repair',
                'depreciation',
                'amortization',
                'total'
            ]
            
            for calc_name in calculation_order:
                calculator = self.calculators[calc_name]
                if not calculator.calculate():
                    print(f"成本模块 {calc_name} 计算失败")
                    return False
            
            return True
            
        except Exception as e:
            print(f"成本模块计算错误: {e}")
            return False
    
    def get_cost_summary(self) -> Dict[str, List[Decimal]]:
        """获取成本汇总数据"""
        results = self.model.results
        
        return {
            'material_cost': [
                self.model.cost.material_cost.get(year, Decimal('0')) 
                for year in range(1, self.period.total_period + 1)
            ],
            'fuel_power_cost': [
                self.model.cost.fuel_power_cost.get(year, Decimal('0')) 
                for year in range(1, self.period.total_period + 1)
            ],
            'labor_cost': [
                self.model.cost.labor_cost.get(year, Decimal('0')) 
                for year in range(1, self.period.total_period + 1)
            ],
            'repair_cost': [
                self.model.cost.repair_cost.get(year, Decimal('0')) 
                for year in range(1, self.period.total_period + 1)
            ],
            'other_cost': [
                self.model.cost.other_cost.get(year, Decimal('0')) 
                for year in range(1, self.period.total_period + 1)
            ],
            'depreciation': results.annual_depreciation,
            'amortization': results.annual_amortization,
            'total_cost': results.annual_cost
        }