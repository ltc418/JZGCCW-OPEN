#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
财务模型测试脚本
用于验证计算逻辑是否正确
"""

from financial_core import FinancialModel
from investment_module import InvestmentModule
from cost_module import CostModule
from revenue_module import RevenueModule
from financial_comprehensive_module import FinancialComprehensiveModule


def test_basic_calculation():
    """测试基本计算功能"""
    print("=" * 60)
    print("财务模型测试")
    print("=" * 60)
    
    # 创建模型
    model = FinancialModel()
    print(f"\n项目名称: {model.basic_info.project_name}")
    print(f"建设期: {model.period.construction_period}年")
    print(f"运营期: {model.period.operation_period}年")
    print(f"计算期: {model.period.total_period}年")
    
    # 设置测试数据
    # 收入数据（运营期第1年）
    model.revenue.factory_building_revenue[4] = 9840.0
    model.revenue.supporting_facility_revenue[4] = 2000.0
    model.revenue.property_service_revenue[4] = 500.0
    
    # 成本数据（运营期第1年）
    model.cost.material_cost[4] = 1000.0
    model.cost.labor_cost[4] = 800.0
    
    # 执行计算
    print("\n正在执行计算...")
    
    # 投资模块
    investment_module = InvestmentModule(model)
    if investment_module.calculate_all():
        print("✓ 投资模块计算完成")
    else:
        print("✗ 投资模块计算失败")
        return False
    
    # 成本模块
    cost_module = CostModule(model)
    if cost_module.calculate_all():
        print("✓ 成本模块计算完成")
    else:
        print("✗ 成本模块计算失败")
        return False
    
    # 收益模块
    revenue_module = RevenueModule(model)
    if revenue_module.calculate_all():
        print("✓ 收益模块计算完成")
    else:
        print("✗ 收益模块计算失败")
        return False
    
    # 财务综合模块
    financial_comprehensive_module = FinancialComprehensiveModule(model)
    if financial_comprehensive_module.calculate_all():
        print("✓ 财务综合模块计算完成")
    else:
        print("✗ 财务综合模块计算失败")
        return False
    
    # 显示关键结果
    print("\n" + "=" * 60)
    print("计算结果")
    print("=" * 60)
    
    results = model.results
    
    # 投资汇总
    print("\n投资汇总:")
    inv_summary = investment_module.get_investment_summary()
    print(f"  工程费: {float(inv_summary['engineering_cost']):,.2f}万元")
    print(f"  工程建设其他费: {float(inv_summary['other_construction_cost']):,.2f}万元")
    print(f"  预备费: {float(inv_summary['contingency_reserve']):,.2f}万元")
    print(f"  建设期利息: {float(inv_summary['construction_interest']):,.2f}万元")
    print(f"  流动资金: {float(inv_summary['working_capital']):,.2f}万元")
    print(f"  项目总投资: {float(inv_summary['total_investment']):,.2f}万元")
    
    # 财务指标
    print("\n财务指标:")
    indicators = financial_comprehensive_module.get_financial_indicators()
    print(f"  净现值(NPV): {indicators['npv']:,.2f}万元")
    print(f"  内部收益率(IRR): {indicators['irr']:.2%}")
    if indicators['static_payback_period'] > 0:
        print(f"  静态投资回收期: {indicators['static_payback_period']:.2f}年")
    else:
        print(f"  静态投资回收期: 未回收")
    
    # 前5年现金流量
    print("\n前5年现金流量:")
    print("  年份  现金流入  现金流出  净现金流量  累计净现金流量")
    for i in range(5):
        year = i + 1
        print(f"  {year:2d}年  {float(results.annual_cash_flow_in[i]):10.2f}  "
              f"{float(results.annual_cash_flow_out[i]):10.2f}  "
              f"{float(results.annual_net_cash_flow[i]):10.2f}  "
              f"{float(results.cumulative_cash_flow[i]):15.2f}")
    
    # 前5年利润
    print("\n前5年利润:")
    print("  年份  营业收入  营业成本  折旧  摊销  税前利润  所得税  税后利润")
    for i in range(5):
        year = i + 1
        print(f"  {year:2d}年  "
              f"{float(results.annual_revenue[i]):8.2f}  "
              f"{float(results.annual_cost[i]):8.2f}  "
              f"{float(results.annual_depreciation[i]):5.2f}  "
              f"{float(results.annual_amortization[i]):5.2f}  "
              f"{float(results.annual_profit_before_tax[i]):8.2f}  "
              f"{float(results.annual_income_tax[i]):6.2f}  "
              f"{float(results.annual_profit_after_tax[i]):8.2f}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    return True


def test_year_adjustment():
    """测试年份数据迁移"""
    print("\n" + "=" * 60)
    print("年份数据迁移测试")
    print("=" * 60)
    
    # 创建模型
    model = FinancialModel()
    
    # 设置一些收入数据
    for year in range(4, 21):
        model.revenue.factory_building_revenue[year] = year * 1000.0
    
    print(f"\n原始设置: 建设期{model.period.construction_period}年，运营期{model.period.operation_period}年")
    print(f"收入数据数量: {len(model.revenue.factory_building_revenue)}")
    
    # 修改期间
    print("\n修改期间: 建设期改为5年，运营期改为15年")
    model.update_period(5, 15)
    
    print(f"新设置: 建设期{model.period.construction_period}年，运营期{model.period.operation_period}年")
    print(f"收入数据数量: {len(model.revenue.factory_building_revenue)}")
    
    # 检查数据迁移
    print("\n检查数据迁移:")
    for year in [6, 10, 15, 16, 20]:
        if year in model.revenue.factory_building_revenue:
            print(f"  第{year}年收入: {float(model.revenue.factory_building_revenue[year]):.2f}万元 ✓")
        else:
            print(f"  第{year}年收入: 不存在（已删除）✓")
    
    print("\n年份数据迁移测试完成！")
    
    return True


def main():
    """主函数"""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  建设项目经济评价系统 - 测试脚本".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print("\n")
    
    # 运行测试
    test_basic_calculation()
    test_year_adjustment()
    
    print("\n")
    print("*" * 60)
    print("所有测试完成！")
    print("*" * 60)
    print("\n")


if __name__ == "__main__":
    main()