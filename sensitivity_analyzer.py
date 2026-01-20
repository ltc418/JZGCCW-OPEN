from decimal import Decimal
from typing import Dict, List, Tuple
import pandas as pd
from financial_core import FinancialModel, round_decimal
from investment_module import InvestmentModule
from cost_module import CostModule
from revenue_module import RevenueModule
from financial_comprehensive_module import FinancialComprehensiveModule


class SensitivityAnalyzer:
    """敏感性分析器"""
    
    def __init__(self, model: FinancialModel):
        self.model = model
        self.base_results = None
    
    def _calculate_model(self, modified_model: FinancialModel) -> Dict:
        """计算修改后的模型"""
        # 初始化结果
        modified_model.initialize_results()
        
        # 执行投资模块计算
        investment_module = InvestmentModule(modified_model)
        investment_module.calculate_all()
        
        # 执行成本模块计算
        cost_module = CostModule(modified_model)
        cost_module.calculate_all()
        
        # 执行收益模块计算
        revenue_module = RevenueModule(modified_model)
        revenue_module.calculate_all()
        
        # 执行财务综合模块计算
        financial_comprehensive_module = FinancialComprehensiveModule(modified_model)
        financial_comprehensive_module.calculate_all()
        
        return {
            'npv': float(modified_model.results.npv),
            'irr': float(modified_model.results.irr),
            'static_payback_period': modified_model.results.static_payback_period if modified_model.results.static_payback_period else 0.0
        }
    
    def calculate_base_case(self) -> Dict:
        """计算基准情况"""
        self.base_results = self._calculate_model(self.model)
        return self.base_results
    
    def single_factor_analysis(self, factor: str, 
                              percentage_changes: List[float] = None) -> Dict:
        """
        单因素敏感性分析
        
        Args:
            factor: 影响因子 ('revenue', 'cost', 'investment', 'discount_rate')
            percentage_changes: 百分比变化列表，如[-20%, -10%, -5%, 0%, 5%, 10%, 20%]
        
        Returns:
            敏感性分析结果
        """
        if percentage_changes is None:
            percentage_changes = [-20, -10, -5, 0, 5, 10, 20]
        
        if self.base_results is None:
            self.calculate_base_case()
        
        results = []
        base_npv = self.base_results['npv']
        base_irr = self.base_results['irr']
        
        for change in percentage_changes:
            # 创建模型的深拷贝
            import copy
            test_model = copy.deepcopy(self.model)
            
            # 应用变化
            if factor == 'revenue':
                self._apply_revenue_change(test_model, change)
            elif factor == 'cost':
                self._apply_cost_change(test_model, change)
            elif factor == 'investment':
                self._apply_investment_change(test_model, change)
            elif factor == 'discount_rate':
                self._apply_discount_rate_change(test_model, change)
            else:
                continue
            
            # 计算结果
            result = self._calculate_model(test_model)
            result['change_percentage'] = change
            result['npv_change'] = result['npv'] - base_npv
            result['npv_change_percentage'] = (result['npv'] - base_npv) / abs(base_npv) * 100 if base_npv != 0 else 0
            result['irr_change'] = result['irr'] - base_irr
            results.append(result)
        
        return {
            'factor': factor,
            'base_case': self.base_results,
            'sensitivity_analysis': results
        }
    
    def _apply_revenue_change(self, model: FinancialModel, percentage: float):
        """应用收入变化"""
        multiplier = 1 + percentage / 100
        for year in model.revenue.factory_building_revenue:
            model.revenue.factory_building_revenue[year] = round_decimal(
                float(model.revenue.factory_building_revenue[year] * multiplier)
            )
        
        for year in model.revenue.supporting_facility_revenue:
            model.revenue.supporting_facility_revenue[year] = round_decimal(
                float(model.revenue.supporting_facility_revenue[year] * multiplier)
            )
        
        for year in model.revenue.property_service_revenue:
            model.revenue.property_service_revenue[year] = round_decimal(
                float(model.revenue.property_service_revenue[year] * multiplier)
            )
        
        for year in model.revenue.parking_revenue:
            model.revenue.parking_revenue[year] = round_decimal(
                float(model.revenue.parking_revenue[year] * multiplier)
            )
        
        for year in model.revenue.advertising_revenue:
            model.revenue.advertising_revenue[year] = round_decimal(
                float(model.revenue.advertising_revenue[year] * multiplier)
            )
    
    def _apply_cost_change(self, model: FinancialModel, percentage: float):
        """应用成本变化"""
        multiplier = 1 + percentage / 100
        for year in model.cost.material_cost:
            model.cost.material_cost[year] = round_decimal(
                float(model.cost.material_cost[year] * multiplier)
            )
        
        for year in model.cost.fuel_power_cost:
            model.cost.fuel_power_cost[year] = round_decimal(
                float(model.cost.fuel_power_cost[year] * multiplier)
            )
        
        for year in model.cost.labor_cost:
            model.cost.labor_cost[year] = round_decimal(
                float(model.cost.labor_cost[year] * multiplier)
            )
        
        for year in model.cost.other_cost:
            model.cost.other_cost[year] = round_decimal(
                float(model.cost.other_cost[year] * multiplier)
            )
    
    def _apply_investment_change(self, model: FinancialModel, percentage: float):
        """应用投资变化"""
        multiplier = 1 + percentage / 100
        model.investment.building_cost = round_decimal(
            float(model.investment.building_cost * multiplier)
        )
        model.investment.equipment_procurement_cost = round_decimal(
            float(model.investment.equipment_procurement_cost * multiplier)
        )
        model.investment.equipment_installation_cost = round_decimal(
            float(model.investment.equipment_installation_cost * multiplier)
        )
        model.investment.public_equipment_procurement_cost = round_decimal(
            float(model.investment.public_equipment_procurement_cost * multiplier)
        )
        model.investment.public_equipment_installation_cost = round_decimal(
            float(model.investment.public_equipment_installation_cost * multiplier)
        )
        model.investment.construction_management_fee = round_decimal(
            float(model.investment.construction_management_fee * multiplier)
        )
        model.investment.technical_consulting_fee = round_decimal(
            float(model.investment.technical_consulting_fee * multiplier)
        )
        model.investment.infrastructure_fee = round_decimal(
            float(model.investment.infrastructure_fee * multiplier)
        )
        model.investment.basic_contingency_reserve = round_decimal(
            float(model.investment.basic_contingency_reserve * multiplier)
        )
        model.investment.price_contingency_reserve = round_decimal(
            float(model.investment.price_contingency_reserve * multiplier)
        )
    
    def _apply_discount_rate_change(self, model: FinancialModel, percentage: float):
        """应用折现率变化"""
        multiplier = 1 + percentage / 100
        model.parameters.discount_rate = round_decimal(
            float(model.parameters.discount_rate * multiplier)
        )
    
    def multi_factor_analysis(self, 
                             factors: List[str] = None,
                             percentage_changes: List[float] = None) -> Dict:
        """
        多因素敏感性分析
        
        Args:
            factors: 影响因子列表
            percentage_changes: 百分比变化列表
        
        Returns:
            多因素敏感性分析结果
        """
        if factors is None:
            factors = ['revenue', 'cost', 'investment']
        
        if percentage_changes is None:
            percentage_changes = [-10, 0, 10]
        
        results = []
        
        for factor in factors:
            single_result = self.single_factor_analysis(factor, percentage_changes)
            results.append(single_result)
        
        return {
            'factors': factors,
            'multi_factor_analysis': results
        }
    
    def generate_sensitivity_report(self) -> str:
        """生成敏感性分析报告"""
        if self.base_results is None:
            self.calculate_base_case()
        
        report = []
        report.append("=" * 60)
        report.append("敏感性分析报告")
        report.append("=" * 60)
        report.append("")
        
        report.append("基准情况:")
        report.append(f"  净现值(NPV): {self.base_results['npv']:,.2f}万元")
        report.append(f"  内部收益率(IRR): {self.base_results['irr']:.2%}")
        if self.base_results['static_payback_period'] > 0:
            report.append(f"  静态投资回收期: {self.base_results['static_payback_period']:.2f}年")
        report.append("")
        
        # 单因素敏感性分析
        factors = ['revenue', 'cost', 'investment']
        factor_names = {'revenue': '营业收入', 'cost': '经营成本', 'investment': '项目投资'}
        
        for factor in factors:
            report.append(f"{factor_names[factor]}敏感性分析:")
            result = self.single_factor_analysis(factor, [-10, -5, 0, 5, 10])
            
            for item in result['sensitivity_analysis']:
                change = item['change_percentage']
                npv = item['npv']
                irr = item['irr']
                npv_change = item['npv_change_percentage']
                
                if change == 0:
                    report.append(f"  基准情况: NPV={npv:,.2f}万元, IRR={irr:.2%}")
                else:
                    sign = '+' if change > 0 else ''
                    report.append(f"  变化{sign}{change}%: NPV={npv:,.2f}万元, IRR={irr:.2%} (NPV变化{npv_change:+.2f}%)")
            
            report.append("")
        
        return "\n".join(report)
    
    def get_sensitivity_dataframe(self, factor: str = 'revenue') -> pd.DataFrame:
        """获取敏感性分析数据框"""
        result = self.single_factor_analysis(factor)
        data = []
        
        for item in result['sensitivity_analysis']:
            data.append({
                '变化百分比': item['change_percentage'],
                '净现值(万元)': item['npv'],
                '净现值变化(万元)': item['npv_change'],
                '净现值变化(%)': item['npv_change_percentage'],
                '内部收益率(%)': item['irr'] * 100,
                '内部收益率变化(%)': item['irr_change'] * 100
            })
        
        return pd.DataFrame(data)