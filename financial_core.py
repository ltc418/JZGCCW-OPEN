from dataclasses import dataclass, field
from typing import List, Dict, Optional
from decimal import Decimal, getcontext, ROUND_HALF_UP
import copy

# 设置Decimal精度，确保小数点后2位精确计算
getcontext().prec = 10
getcontext().rounding = ROUND_HALF_UP


def round_decimal(value: float, decimal_places: int = 2) -> Decimal:
    """将数值四舍五入到指定小数位数"""
    if isinstance(value, Decimal):
        return value.quantize(Decimal('1').scaleb(-decimal_places), rounding=ROUND_HALF_UP)
    return Decimal(str(value)).quantize(Decimal('1').scaleb(-decimal_places), rounding=ROUND_HALF_UP)


@dataclass
class ProjectPeriod:
    """项目期间管理类"""
    construction_period: int = 3  # 建设期（年）
    operation_period: int = 17   # 运营期（年）
    
    @property
    def total_period(self) -> int:
        """计算期（年）"""
        return self.construction_period + self.operation_period
    
    @property
    def operation_start_year(self) -> int:
        """运营期开始年份（第几年）"""
        return self.construction_period + 1
    
    @property
    def years_range(self) -> range:
        """年份范围"""
        return range(1, self.total_period + 1)
    
    @property
    def construction_years_range(self) -> range:
        """建设期年份范围"""
        return range(1, self.construction_period + 1)
    
    @property
    def operation_years_range(self) -> range:
        """运营期年份范围"""
        return range(self.operation_start_year, self.total_period + 1)
    
    def is_construction_year(self, year: int) -> bool:
        """判断是否为建设期年份"""
        return year in self.construction_years_range
    
    def is_operation_year(self, year: int) -> bool:
        """判断是否为运营期年份"""
        return year in self.operation_years_range
    
    def get_year_label(self, year: int) -> str:
        """获取年份标签"""
        return f"第{year}年"
    
    def validate(self) -> bool:
        """验证期间参数是否合法"""
        return (
            1 <= self.construction_period <= 10 and
            1 <= self.operation_period <= 50
        )


@dataclass
class ProjectBasicInfo:
    """项目基本信息"""
    project_name: str = "东兴电子产业园三期项目财务分析"
    construction_period: int = 3
    operation_period: int = 17
    calculation_period: int = 20
    prior_work_years: int = 20


@dataclass
class InvestmentData:
    """项目投资数据"""
    # 工程费
    building_cost: Decimal = Decimal('67062.86')  # 建筑工程费
    equipment_procurement_cost: Decimal = Decimal('2360.38')  # 生产设备购置费
    equipment_installation_cost: Decimal = Decimal('18299.19')  # 生产设备安装费
    public_equipment_procurement_cost: Decimal = Decimal('0')  # 公用设备购置费
    public_equipment_installation_cost: Decimal = Decimal('0')  # 公用设备安装费
    
    # 工程建设其他费
    construction_management_fee: Decimal = Decimal('0')  # 建设单位管理费
    technical_consulting_fee: Decimal = Decimal('6036.83')  # 项目建设技术咨询费
    infrastructure_fee: Decimal = Decimal('1737.79')  # 基础设施建设费
    land_use_fee: Decimal = Decimal('6505.72')  # 土地使用费
    patent_fee: Decimal = Decimal('0')  # 专利及专有技术费
    other_preparation_fee: Decimal = Decimal('323.19')  # 工程准备及其他费
    
    # 预备费
    basic_contingency_reserve: Decimal = Decimal('10532.08')  # 基本预备费
    price_contingency_reserve: Decimal = Decimal('0')  # 涨价预备费
    
    # 建设期利息
    construction_interest: Decimal = Decimal('5721.185772330424')  # 建设期利息
    
    # 流动资金
    working_capital: Decimal = Decimal('90')  # 流动资金


@dataclass
class AssetData:
    """资产数据"""
    fixed_assets_original_value: Decimal = Decimal('0')  # 固定资产原值（不含建设期利息）
    fixed_assets_with_interest: Decimal = Decimal('0')  # 固定资产原值（含建设期利息）
    
    # 折旧参数
    depreciation_years: int = 20  # 折旧年限
    salvage_rate: Decimal = Decimal('0.05')  # 残值率
    
    # 无形资产
    intangible_assets: Decimal = Decimal('0')  # 无形资产原值
    amortization_years: int = 50  # 摊销年限
    
    # 其他资产
    other_assets: Decimal = Decimal('0')  # 其他资产原值
    other_assets_years: int = 5  # 其他资产摊销年限
    
    # 可抵扣进项税
    deductible_tax: Decimal = Decimal('8716.8199')  # 可抵扣建设投资进项税


@dataclass
class RevenueData:
    """收入数据"""
    # 标准厂房收入（按年份）
    factory_building_revenue: Dict[int, Decimal] = field(default_factory=dict)
    # 配套用房招商收入（按年份）
    supporting_facility_revenue: Dict[int, Decimal] = field(default_factory=dict)
    # 物业服务费收入（按年份）
    property_service_revenue: Dict[int, Decimal] = field(default_factory=dict)
    # 车位出租收入（按年份）
    parking_revenue: Dict[int, Decimal] = field(default_factory=dict)
    # 广告栏出租收入（按年份）
    advertising_revenue: Dict[int, Decimal] = field(default_factory=dict)
    # 固定资产销售收入（按年份）
    asset_sale_revenue: Dict[int, Decimal] = field(default_factory=dict)
    
    def get_total_revenue(self, year: int) -> Decimal:
        """获取某年的总收入"""
        return round_decimal(
            self.factory_building_revenue.get(year, Decimal('0')) +
            self.supporting_facility_revenue.get(year, Decimal('0')) +
            self.property_service_revenue.get(year, Decimal('0')) +
            self.parking_revenue.get(year, Decimal('0')) +
            self.advertising_revenue.get(year, Decimal('0')) +
            self.asset_sale_revenue.get(year, Decimal('0'))
        )


@dataclass
class CostData:
    """成本数据"""
    # 外购原材料成本（按年份）
    material_cost: Dict[int, Decimal] = field(default_factory=dict)
    # 外购燃料及动力成本（按年份）
    fuel_power_cost: Dict[int, Decimal] = field(default_factory=dict)
    # 工资福利成本（按年份）
    labor_cost: Dict[int, Decimal] = field(default_factory=dict)
    # 修理费（按年份）
    repair_cost: Dict[int, Decimal] = field(default_factory=dict)
    # 其他费用（按年份）
    other_cost: Dict[int, Decimal] = field(default_factory=dict)
    
    def get_total_cost(self, year: int) -> Decimal:
        """获取某年的总成本"""
        return round_decimal(
            self.material_cost.get(year, Decimal('0')) +
            self.fuel_power_cost.get(year, Decimal('0')) +
            self.labor_cost.get(year, Decimal('0')) +
            self.repair_cost.get(year, Decimal('0')) +
            self.other_cost.get(year, Decimal('0'))
        )


@dataclass
class TaxData:
    """税费数据"""
    # 税率参数
    vat_output_rate: Decimal = Decimal('0.09')  # 销项税率（一般9%）
    vat_input_rate: Decimal = Decimal('0.13')  # 进项税率（一般13%）
    city_maintenance_tax_rate: Decimal = Decimal('0.07')  # 城市维护建设税率（7%）
    education_surtax_rate: Decimal = Decimal('0.05')  # 教育费附加及地方教育费附加率（5%）
    income_tax_rate: Decimal = Decimal('0.25')  # 企业所得税率（25%）
    land_value_tax_rate: Decimal = Decimal('0')  # 土地增值税率
    
    # 补贴收入（按年份）
    subsidy_income: Dict[int, Decimal] = field(default_factory=dict)


@dataclass
class FinancialParameters:
    """财务参数"""
    tax_rate: Decimal = Decimal('0.25')  # 企业所得税税率
    surplus_reserve_rate: Decimal = Decimal('0.1')  # 盈余公积金比率
    discount_rate: Decimal = Decimal('0.06')  # 折现率（内部收益率ic）
    loss_offset_years: int = 5  # 亏损弥补年限


@dataclass
class CalculationResults:
    """计算结果数据"""
    # 期间信息
    construction_period: int = 3
    operation_period: int = 17
    total_period: int = 20
    
    # 投资计算结果
    total_investment: Decimal = Decimal('0')
    fixed_assets_investment: List[Decimal] = field(default_factory=list)  # 各年固定资产投资
    working_capital_investment: List[Decimal] = field(default_factory=list)  # 各年流动资金投资
    
    # 折旧摊销计算结果
    annual_depreciation: List[Decimal] = field(default_factory=list)  # 各年折旧
    annual_amortization: List[Decimal] = field(default_factory=list)  # 各年摊销
    
    # 收入成本计算结果
    annual_revenue: List[Decimal] = field(default_factory=list)  # 各年收入
    annual_cost: List[Decimal] = field(default_factory=list)  # 各年成本
    annual_profit_before_tax: List[Decimal] = field(default_factory=list)  # 各年税前利润
    annual_income_tax: List[Decimal] = field(default_factory=list)  # 各年所得税
    annual_profit_after_tax: List[Decimal] = field(default_factory=list)  # 各年税后利润
    
    # 税费计算结果
    annual_vat_output: List[Decimal] = field(default_factory=list)  # 各年销项税
    annual_vat_input: List[Decimal] = field(default_factory=list)  # 各年进项税
    annual_vat_paid: List[Decimal] = field(default_factory=list)  # 各年实缴增值税
    annual_city_maintenance_tax: List[Decimal] = field(default_factory=list)  # 各年城建税
    annual_education_surtax: List[Decimal] = field(default_factory=list)  # 各年教育费附加
    
    # 现金流量计算结果
    annual_cash_flow_in: List[Decimal] = field(default_factory=list)  # 各年现金流入
    annual_cash_flow_out: List[Decimal] = field(default_factory=list)  # 各年现金流出
    annual_net_cash_flow: List[Decimal] = field(default_factory=list)  # 各年净现金流量
    cumulative_cash_flow: List[Decimal] = field(default_factory=list)  # 累计净现金流量
    
    # 财务指标
    npv: Decimal = Decimal('0')  # 净现值
    irr: Decimal = Decimal('0')  # 内部收益率
    static_payback_period: Optional[float] = None  # 静态投资回收期
    dynamic_payback_period: Optional[float] = None  # 动态投资回收期
    
    def initialize_arrays(self, total_period: int):
        """初始化所有数组"""
        zeros = [Decimal('0')] * total_period
        self.fixed_assets_investment = zeros.copy()
        self.working_capital_investment = zeros.copy()
        self.annual_depreciation = zeros.copy()
        self.annual_amortization = zeros.copy()
        self.annual_revenue = zeros.copy()
        self.annual_cost = zeros.copy()
        self.annual_profit_before_tax = zeros.copy()
        self.annual_income_tax = zeros.copy()
        self.annual_profit_after_tax = zeros.copy()
        self.annual_vat_output = zeros.copy()
        self.annual_vat_input = zeros.copy()
        self.annual_vat_paid = zeros.copy()
        self.annual_city_maintenance_tax = zeros.copy()
        self.annual_education_surtax = zeros.copy()
        self.annual_cash_flow_in = zeros.copy()
        self.annual_cash_flow_out = zeros.copy()
        self.annual_net_cash_flow = zeros.copy()
        self.cumulative_cash_flow = zeros.copy()


@dataclass
class FinancialModel:
    """财务模型数据容器"""
    # 项目期间
    period: ProjectPeriod = field(default_factory=ProjectPeriod)
    
    # 项目基本信息
    basic_info: ProjectBasicInfo = field(default_factory=ProjectBasicInfo)
    
    # 投资数据
    investment: InvestmentData = field(default_factory=InvestmentData)
    
    # 资产数据
    assets: AssetData = field(default_factory=AssetData)
    
    # 收入数据
    revenue: RevenueData = field(default_factory=RevenueData)
    
    # 成本数据
    cost: CostData = field(default_factory=CostData)
    
    # 税费数据
    tax: TaxData = field(default_factory=TaxData)
    
    # 财务参数
    parameters: FinancialParameters = field(default_factory=FinancialParameters)
    
    # 计算结果
    results: CalculationResults = field(default_factory=CalculationResults)
    
    def initialize_results(self):
        """初始化计算结果"""
        self.results.construction_period = self.period.construction_period
        self.results.operation_period = self.period.operation_period
        self.results.total_period = self.period.total_period
        self.results.initialize_arrays(self.period.total_period)
    
    def update_period(self, construction_period: int, operation_period: int):
        """更新项目期间并迁移数据"""
        old_period = copy.deepcopy(self.period)
        
        # 更新期间
        self.period.construction_period = construction_period
        self.period.operation_period = operation_period
        
        # 更新基本信息
        self.basic_info.construction_period = construction_period
        self.basic_info.operation_period = operation_period
        self.basic_info.calculation_period = self.period.total_period
        
        # 迁移年份数据
        self._migrate_year_data(old_period)
        
        # 初始化结果
        self.initialize_results()
    
    def _migrate_year_data(self, old_period: ProjectPeriod):
        """迁移年份数据，保留可用的历史数据"""
        new_total = self.period.total_period
        
        # 迁移收入数据
        for year, value in self.revenue.factory_building_revenue.items():
            if year <= new_total:
                self.revenue.factory_building_revenue[year] = value
            else:
                del self.revenue.factory_building_revenue[year]
        
        for year, value in self.revenue.supporting_facility_revenue.items():
            if year <= new_total:
                self.revenue.supporting_facility_revenue[year] = value
            else:
                del self.revenue.supporting_facility_revenue[year]
        
        # 迁移成本数据
        for year, value in self.cost.material_cost.items():
            if year <= new_total:
                self.cost.material_cost[year] = value
            else:
                del self.cost.material_cost[year]
        
        for year, value in self.cost.labor_cost.items():
            if year <= new_total:
                self.cost.labor_cost[year] = value
            else:
                del self.cost.labor_cost[year]
    
    def to_dict(self) -> Dict:
        """转换为字典，用于保存"""
        return {
            'period': {
                'construction_period': self.period.construction_period,
                'operation_period': self.period.operation_period
            },
            'investment': {
                'building_cost': float(self.investment.building_cost),
                'equipment_procurement_cost': float(self.investment.equipment_procurement_cost),
                'equipment_installation_cost': float(self.investment.equipment_installation_cost),
                'public_equipment_procurement_cost': float(self.investment.public_equipment_procurement_cost),
                'public_equipment_installation_cost': float(self.investment.public_equipment_installation_cost),
                'construction_management_fee': float(self.investment.construction_management_fee),
                'technical_consulting_fee': float(self.investment.technical_consulting_fee),
                'infrastructure_fee': float(self.investment.infrastructure_fee),
                'land_use_fee': float(self.investment.land_use_fee),
                'patent_fee': float(self.investment.patent_fee),
                'other_preparation_fee': float(self.investment.other_preparation_fee),
                'basic_contingency_reserve': float(self.investment.basic_contingency_reserve),
                'price_contingency_reserve': float(self.investment.price_contingency_reserve),
                'construction_interest': float(self.investment.construction_interest),
                'working_capital': float(self.investment.working_capital)
            },
            'revenue': {
                'factory_building_revenue': {k: float(v) for k, v in self.revenue.factory_building_revenue.items()},
                'supporting_facility_revenue': {k: float(v) for k, v in self.revenue.supporting_facility_revenue.items()},
                'property_service_revenue': {k: float(v) for k, v in self.revenue.property_service_revenue.items()},
                'parking_revenue': {k: float(v) for k, v in self.revenue.parking_revenue.items()},
                'advertising_revenue': {k: float(v) for k, v in self.revenue.advertising_revenue.items()},
                'asset_sale_revenue': {k: float(v) for k, v in self.revenue.asset_sale_revenue.items()}
            },
            'cost': {
                'material_cost': {k: float(v) for k, v in self.cost.material_cost.items()},
                'fuel_power_cost': {k: float(v) for k, v in self.cost.fuel_power_cost.items()},
                'labor_cost': {k: float(v) for k, v in self.cost.labor_cost.items()},
                'repair_cost': {k: float(v) for k, v in self.cost.repair_cost.items()},
                'other_cost': {k: float(v) for k, v in self.cost.other_cost.items()}
            },
            'tax': {
                'vat_output_rate': float(self.tax.vat_output_rate),
                'vat_input_rate': float(self.tax.vat_input_rate),
                'city_maintenance_tax_rate': float(self.tax.city_maintenance_tax_rate),
                'education_surtax_rate': float(self.tax.education_surtax_rate),
                'income_tax_rate': float(self.tax.income_tax_rate),
                'subsidy_income': {k: float(v) for k, v in self.tax.subsidy_income.items()}
            },
            'parameters': {
                'tax_rate': float(self.parameters.tax_rate),
                'surplus_reserve_rate': float(self.parameters.surplus_reserve_rate),
                'discount_rate': float(self.parameters.discount_rate),
                'loss_offset_years': self.parameters.loss_offset_years
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FinancialModel':
        """从字典创建模型"""
        model = cls()
        
        # 恢复期间
        if 'period' in data:
            model.period.construction_period = data['period'].get('construction_period', 3)
            model.period.operation_period = data['period'].get('operation_period', 17)
        
        # 恢复投资数据
        if 'investment' in data:
            inv_data = data['investment']
            model.investment.building_cost = Decimal(str(inv_data.get('building_cost', 67062.86)))
            model.investment.equipment_procurement_cost = Decimal(str(inv_data.get('equipment_procurement_cost', 2360.38)))
            model.investment.equipment_installation_cost = Decimal(str(inv_data.get('equipment_installation_cost', 18299.19)))
            model.investment.public_equipment_procurement_cost = Decimal(str(inv_data.get('public_equipment_procurement_cost', 0)))
            model.investment.public_equipment_installation_cost = Decimal(str(inv_data.get('public_equipment_installation_cost', 0)))
            model.investment.construction_management_fee = Decimal(str(inv_data.get('construction_management_fee', 0)))
            model.investment.technical_consulting_fee = Decimal(str(inv_data.get('technical_consulting_fee', 6036.83)))
            model.investment.infrastructure_fee = Decimal(str(inv_data.get('infrastructure_fee', 1737.79)))
            model.investment.land_use_fee = Decimal(str(inv_data.get('land_use_fee', 6505.72)))
            model.investment.patent_fee = Decimal(str(inv_data.get('patent_fee', 0)))
            model.investment.other_preparation_fee = Decimal(str(inv_data.get('other_preparation_fee', 323.19)))
            model.investment.basic_contingency_reserve = Decimal(str(inv_data.get('basic_contingency_reserve', 10532.08)))
            model.investment.price_contingency_reserve = Decimal(str(inv_data.get('price_contingency_reserve', 0)))
            model.investment.construction_interest = Decimal(str(inv_data.get('construction_interest', 5721.185772330424)))
            model.investment.working_capital = Decimal(str(inv_data.get('working_capital', 90)))
        
        # 恢复收入数据
        if 'revenue' in data:
            rev_data = data['revenue']
            model.revenue.factory_building_revenue = {int(k): Decimal(str(v)) for k, v in rev_data.get('factory_building_revenue', {}).items()}
            model.revenue.supporting_facility_revenue = {int(k): Decimal(str(v)) for k, v in rev_data.get('supporting_facility_revenue', {}).items()}
            model.revenue.property_service_revenue = {int(k): Decimal(str(v)) for k, v in rev_data.get('property_service_revenue', {}).items()}
            model.revenue.parking_revenue = {int(k): Decimal(str(v)) for k, v in rev_data.get('parking_revenue', {}).items()}
            model.revenue.advertising_revenue = {int(k): Decimal(str(v)) for k, v in rev_data.get('advertising_revenue', {}).items()}
            model.revenue.asset_sale_revenue = {int(k): Decimal(str(v)) for k, v in rev_data.get('asset_sale_revenue', {}).items()}
        
        # 恢复成本数据
        if 'cost' in data:
            cost_data = data['cost']
            model.cost.material_cost = {int(k): Decimal(str(v)) for k, v in cost_data.get('material_cost', {}).items()}
            model.cost.fuel_power_cost = {int(k): Decimal(str(v)) for k, v in cost_data.get('fuel_power_cost', {}).items()}
            model.cost.labor_cost = {int(k): Decimal(str(v)) for k, v in cost_data.get('labor_cost', {}).items()}
            model.cost.repair_cost = {int(k): Decimal(str(v)) for k, v in cost_data.get('repair_cost', {}).items()}
            model.cost.other_cost = {int(k): Decimal(str(v)) for k, v in cost_data.get('other_cost', {}).items()}
        
        # 恢复税费数据
        if 'tax' in data:
            tax_data = data['tax']
            model.tax.vat_output_rate = Decimal(str(tax_data.get('vat_output_rate', 0.09)))
            model.tax.vat_input_rate = Decimal(str(tax_data.get('vat_input_rate', 0.13)))
            model.tax.city_maintenance_tax_rate = Decimal(str(tax_data.get('city_maintenance_tax_rate', 0.07)))
            model.tax.education_surtax_rate = Decimal(str(tax_data.get('education_surtax_rate', 0.05)))
            model.tax.income_tax_rate = Decimal(str(tax_data.get('income_tax_rate', 0.25)))
            model.tax.subsidy_income = {int(k): Decimal(str(v)) for k, v in tax_data.get('subsidy_income', {}).items()}
        
        # 恢复财务参数
        if 'parameters' in data:
            param_data = data['parameters']
            model.parameters.tax_rate = Decimal(str(param_data.get('tax_rate', 0.25)))
            model.parameters.surplus_reserve_rate = Decimal(str(param_data.get('surplus_reserve_rate', 0.1)))
            model.parameters.discount_rate = Decimal(str(param_data.get('discount_rate', 0.06)))
            model.parameters.loss_offset_years = param_data.get('loss_offset_years', 5)
        
        # 初始化结果
        model.initialize_results()
        
        return model