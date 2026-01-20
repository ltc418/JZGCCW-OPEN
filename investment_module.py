from decimal import Decimal
from typing import List, Dict
from financial_core import FinancialModel, round_decimal, ProjectPeriod
from financial_calculator import FinancialCalculatorBase


class InvestmentPlanCalculator(FinancialCalculatorBase):
    """投资计划计算器 - 对应工作表3"""
    
    def calculate(self) -> bool:
        """计算投资资金使用计划"""
        try:
            inv = self.model.investment
            assets = self.model.assets
            results = self.model.results
            
            # 计算总投资构成
            investment_summary = self._calculate_total_investment()
            
            # 按年度分配投资（建设期）
            construction_years = self.period.construction_period
            investment_schedule = self._create_investment_schedule(investment_summary, construction_years)
            
            # 更新固定资产投资数据
            for year_idx in range(construction_years):
                results.fixed_assets_investment[year_idx] = round_decimal(
                    investment_schedule['fixed_assets'][year_idx]
                )
            
            # 更新流动资金投资数据
            operation_start = self.period.operation_start_year - 1
            if operation_start < len(results.working_capital_investment):
                results.working_capital_investment[operation_start] = round_decimal(
                    investment_schedule['working_capital']
                )
            
            return True
            
        except Exception as e:
            import traceback
            print(f"投资计划计算错误: {e}")
            traceback.print_exc()
            return False
    
    def _calculate_total_investment(self) -> Dict[str, Decimal]:
        """计算总投资构成"""
        inv = self.model.investment
        assets = self.model.assets
        
        # 固定资产投资
        fixed_assets = assets.fixed_assets_with_interest
        
        # 无形资产
        intangible_assets = assets.intangible_assets
        
        # 其他资产
        other_assets = assets.other_assets
        
        # 流动资金
        working_capital = inv.working_capital
        
        # 总投资
        total = round_decimal(fixed_assets + intangible_assets + other_assets + working_capital)
        
        return {
            'fixed_assets': fixed_assets,
            'intangible_assets': intangible_assets,
            'other_assets': other_assets,
            'working_capital': working_capital,
            'total': total
        }
    
    def _create_investment_schedule(self, investment: Dict[str, Decimal], 
                                     construction_years: int) -> Dict[str, List[Decimal]]:
        """创建年度投资计划"""
        # 固定资产投资按建设期分配
        fixed_assets = investment['fixed_assets']
        if construction_years >= 3:
            # 40%, 30%, 30%
            fixed_assets_schedule = [
                round_decimal(fixed_assets * Decimal('0.4')),
                round_decimal(fixed_assets * Decimal('0.3')),
                round_decimal(fixed_assets * Decimal('0.3'))
            ]
            if construction_years > 3:
                # 超过3年的部分平均分配
                remaining_years = construction_years - 3
                if remaining_years > 0:
                    avg_investment = round_decimal(fixed_assets * Decimal('0.3') / Decimal(remaining_years))
                    fixed_assets_schedule.extend([avg_investment] * remaining_years)
        else:
            # 建设期少于3年，平均分配
            avg_investment = round_decimal(fixed_assets / Decimal(construction_years))
            fixed_assets_schedule = [avg_investment] * construction_years
        
        return {
            'fixed_assets': fixed_assets_schedule[:construction_years],
            'working_capital': investment['working_capital']
        }


class LoanRepaymentCalculator(FinancialCalculatorBase):
    """借款偿还计算器 - 对应工作表4"""
    
    def calculate(self) -> bool:
        """计算借款偿还及利息"""
        try:
            inv = self.model.investment
            results = self.model.results
            
            # 简化版本：假设建设期利息已计算，运营期无新增借款
            # 这里主要计算建设期利息的确认
            
            # 验证建设期利息
            construction_interest = inv.construction_interest
            
            # 将建设期利息计入固定资产
            # 这个已经在InvestmentCalculator中处理
            
            return True
            
        except Exception as e:
            print(f"借款偿还计算错误: {e}")
            return False


class WorkingCapitalCalculator(FinancialCalculatorBase):
    """流动资金计算器 - 对应工作表2"""
    
    def calculate(self) -> bool:
        """计算流动资金需求"""
        try:
            inv = self.model.investment
            cost_data = self.model.cost
            results = self.model.results
            
            # 简化版本：流动资金按运营期需求的固定比例
            # 在实际应用中，流动资金应按详细计算
            
            # 这里直接使用用户输入的流动资金
            working_capital = inv.working_capital
            
            # 流动资金在运营期开始时投入
            operation_start = self.period.operation_start_year - 1
            if operation_start < len(results.working_capital_investment):
                results.working_capital_investment[operation_start] = round_decimal(working_capital)
            
            return True
            
        except Exception as e:
            print(f"流动资金计算错误: {e}")
            return False


class ProjectInvestmentSummaryCalculator(FinancialCalculatorBase):
    """项目投资汇总计算器 - 对应工作表1"""
    
    def calculate(self) -> bool:
        """计算项目投资汇总"""
        try:
            inv = self.model.investment
            assets = self.model.assets
            results = self.model.results
            
            # 1. 工程费
            engineering_cost = round_decimal(
                inv.building_cost +
                inv.equipment_procurement_cost +
                inv.equipment_installation_cost +
                inv.public_equipment_procurement_cost +
                inv.public_equipment_installation_cost
            )
            
            # 2. 工程建设其他费
            other_construction_cost = round_decimal(
                inv.construction_management_fee +
                inv.technical_consulting_fee +
                inv.infrastructure_fee +
                inv.land_use_fee +
                inv.patent_fee +
                inv.other_preparation_fee
            )
            
            # 3. 预备费
            contingency_reserve = round_decimal(
                inv.basic_contingency_reserve +
                inv.price_contingency_reserve
            )
            
            # 4. 建设期利息
            construction_interest = inv.construction_interest
            
            # 5. 流动资金
            working_capital = inv.working_capital
            
            # 项目总投资
            total_project_investment = round_decimal(
                engineering_cost +
                other_construction_cost +
                contingency_reserve +
                construction_interest +
                working_capital
            )
            
            # 更新结果
            results.total_investment = total_project_investment
            
            return True
            
        except Exception as e:
            print(f"项目投资汇总计算错误: {e}")
            return False


class InvestmentModule:
    """投资模块 - 整合工作表1-4"""
    
    def __init__(self, model: FinancialModel):
        self.model = model
        self.calculators = {
            'summary': ProjectInvestmentSummaryCalculator(model),
            'working_capital': WorkingCapitalCalculator(model),
            'investment_plan': InvestmentPlanCalculator(model),
            'loan_repayment': LoanRepaymentCalculator(model)
        }
    
    def calculate_all(self) -> bool:
        """执行投资模块所有计算"""
        try:
            # 先初始化模型结果
            self.model.initialize_results()
            
            # 按顺序执行计算
            calculation_order = [
                'summary',
                'working_capital',
                'investment_plan',
                'loan_repayment'
            ]
            
            for calc_name in calculation_order:
                calculator = self.calculators[calc_name]
                if not calculator.calculate():
                    print(f"投资模块 {calc_name} 计算失败")
                    return False
            
            return True
            
        except Exception as e:
            import traceback
            print(f"投资模块计算错误: {e}")
            traceback.print_exc()
            return False
    
    def get_investment_summary(self) -> Dict[str, Decimal]:
        """获取投资汇总数据"""
        inv = self.model.investment
        assets = self.model.assets
        
        return {
            'engineering_cost': round_decimal(
                inv.building_cost +
                inv.equipment_procurement_cost +
                inv.equipment_installation_cost +
                inv.public_equipment_procurement_cost +
                inv.public_equipment_installation_cost
            ),
            'other_construction_cost': round_decimal(
                inv.construction_management_fee +
                inv.technical_consulting_fee +
                inv.infrastructure_fee +
                inv.land_use_fee +
                inv.patent_fee +
                inv.other_preparation_fee
            ),
            'contingency_reserve': round_decimal(
                inv.basic_contingency_reserve +
                inv.price_contingency_reserve
            ),
            'construction_interest': inv.construction_interest,
            'working_capital': inv.working_capital,
            'fixed_assets_original_value': assets.fixed_assets_original_value,
            'fixed_assets_with_interest': assets.fixed_assets_with_interest,
            'total_investment': self.model.results.total_investment
        }