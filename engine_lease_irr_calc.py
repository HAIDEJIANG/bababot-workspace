# -*- coding: utf-8 -*-
"""
发动机租赁 IRR 计算和现金流表生成
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# IRR计算函数（numpy.irr在新版本中已移除）
def calculate_irr(cash_flows, guess=0.1):
    """使用二分法计算IRR"""
    def npv(rate):
        return sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
    
    # 二分法
    low, high = -0.99, 10.0
    for _ in range(1000):
        mid = (low + high) / 2
        npv_mid = npv(mid)
        if abs(npv_mid) < 1e-6:
            return mid
        if npv_mid > 0:
            low = mid
        else:
            high = mid
    return mid

# ==================== 参数设置 ====================
# 发动机购买成本
PURCHASE_COST_USD = 9_000_000  # 900万美元

# 残值
RESIDUAL_VALUE_USD = 2_000_000  # 200万美元

# 汇率
EXCHANGE_RATE = 6.9  # 人民币/美元

# 转换为人民币
PURCHASE_COST_RMB = PURCHASE_COST_USD * EXCHANGE_RATE  # 6210万人民币
RESIDUAL_VALUE_RMB = RESIDUAL_VALUE_USD * EXCHANGE_RATE  # 1380万人民币

# 融资参数
FINANCING_RATIO = 0.90  # 90%融资
FINANCING_AMOUNT = PURCHASE_COST_RMB * FINANCING_RATIO  # 5589万人民币
FINANCING_RATE = 0.05  # 5%年利率

# 还款方式：80%等额本息 + 20%期末一次还清
AMORTIZED_PORTION = FINANCING_AMOUNT * 0.80  # 4471.2万人民币
BALLOON_PORTION = FINANCING_AMOUNT * 0.20  # 1117.8万人民币

# ==================== 从报价表提取的租金数据 ====================
# 2026年：9个月，月租金约1,744,350元
# 2027年：12个月，月租金约2,388,449元
# 2028年：12个月，月租金约2,455,113元
# 2029年：12个月，月租金约2,526,090元
# 总租期：45个月

rental_schedule = [
    # (年份, 月数, 月租金人民币)
    (2026, 9, 1_744_350),
    (2027, 12, 2_388_448.6),
    (2028, 12, 2_455_112.65),
    (2029, 12, 2_526_089.82),
]

# ==================== 计算租赁现金流 ====================
def calculate_lease_cash_flows():
    """计算租赁业务现金流"""
    cash_flows = []
    period = 0
    total_rent = 0
    
    # 起始日期
    start_date = datetime(2026, 4, 1)
    
    # 初始投资（购买发动机）
    cash_flows.append({
        '期数': 0,
        '日期': start_date.strftime('%Y-%m-%d'),
        '项目': '初始投资',
        '租金收入': 0,
        '融资流入': FINANCING_AMOUNT,
        '融资还款': 0,
        '残值回收': 0,
        '净现金流': -PURCHASE_COST_RMB + FINANCING_AMOUNT,
        '备注': f'购买发动机: -{PURCHASE_COST_RMB:,.0f}, 融资: +{FINANCING_AMOUNT:,.0f}'
    })
    
    current_date = start_date
    
    for year, months, monthly_rent in rental_schedule:
        for m in range(months):
            period += 1
            current_date = current_date + relativedelta(months=1)
            total_rent += monthly_rent
            
            cash_flows.append({
                '期数': period,
                '日期': current_date.strftime('%Y-%m-%d'),
                '项目': f'{year}年{m+1}月租金',
                '租金收入': monthly_rent,
                '融资流入': 0,
                '融资还款': 0,
                '残值回收': 0,
                '净现金流': monthly_rent,
                '备注': ''
            })
    
    # 期末残值回收
    cash_flows.append({
        '期数': period + 1,
        '日期': (current_date + relativedelta(months=1)).strftime('%Y-%m-%d'),
        '项目': '残值回收',
        '租金收入': 0,
        '融资流入': 0,
        '融资还款': -BALLOON_PORTION,
        '残值回收': RESIDUAL_VALUE_RMB,
        '净现金流': RESIDUAL_VALUE_RMB - BALLOON_PORTION,
        '备注': f'残值: +{RESIDUAL_VALUE_RMB:,.0f}, 尾款偿还: -{BALLOON_PORTION:,.0f}'
    })
    
    return cash_flows, total_rent

# ==================== 计算融资还款现金流 ====================
def calculate_financing_cash_flows():
    """计算融资租赁还款现金流"""
    cash_flows = []
    
    # 融资参数
    total_periods = 45  # 45个月
    monthly_rate = FINANCING_RATE / 12  # 月利率
    
    # 等额本息部分
    amortized_principal = AMORTIZED_PORTION
    monthly_payment = amortized_principal * (monthly_rate * (1 + monthly_rate)**total_periods) / ((1 + monthly_rate)**total_periods - 1)
    
    # 计算每月还款明细
    remaining_principal = amortized_principal
    
    for period in range(1, total_periods + 1):
        interest_payment = remaining_principal * monthly_rate
        principal_payment = monthly_payment - interest_payment
        remaining_principal -= principal_payment
        
        cash_flows.append({
            '期数': period,
            '月还款额': monthly_payment,
            '本金': principal_payment,
            '利息': interest_payment,
            '剩余本金': max(0, remaining_principal)
        })
    
    return cash_flows, monthly_payment

# ==================== 计算IRR ====================
def compute_irr_from_cf(cash_flows_list):
    """计算内部收益率"""
    # 月度IRR
    monthly_irr = calculate_irr(cash_flows_list)
    
    # 年化IRR
    annual_irr = (1 + monthly_irr) ** 12 - 1
    
    return monthly_irr, annual_irr

# ==================== 生成综合现金流表 ====================
def generate_comprehensive_cashflow():
    """生成综合现金流表"""
    
    # 租赁现金流
    lease_cf, total_rent = calculate_lease_cash_flows()
    
    # 融资还款现金流
    financing_cf, monthly_payment = calculate_financing_cash_flows()
    
    # 合并现金流表
    combined = []
    
    # 初始投资
    combined.append({
        '期数': 0,
        '日期': '2026-04-01',
        '项目': '初始投资',
        '租金收入(人民币)': 0,
        '融资流入(人民币)': FINANCING_AMOUNT,
        '等额本息还款(人民币)': 0,
        '期末尾款(人民币)': 0,
        '残值回收(人民币)': 0,
        '净现金流(人民币)': -PURCHASE_COST_RMB + FINANCING_AMOUNT,
        '备注': f'购买发动机{PURCHASE_COST_USD}万美元×{EXCHANGE_RATE}={PURCHASE_COST_RMB:,.0f}元'
    })
    
    # 每月现金流
    period = 0
    for year, months, monthly_rent in rental_schedule:
        for m in range(months):
            period += 1
            fin = financing_cf[period - 1] if period <= len(financing_cf) else {'月还款额': 0, '利息': 0, '本金': 0}
            
            combined.append({
                '期数': period,
                '日期': f'{year}-{(m+1):02d}',
                '项目': f'{year}年{m+1}月',
                '租金收入(人民币)': monthly_rent,
                '融资流入(人民币)': 0,
                '等额本息还款(人民币)': -fin['月还款额'],
                '期末尾款(人民币)': 0,
                '残值回收(人民币)': 0,
                '净现金流(人民币)': monthly_rent - fin['月还款额'],
                '备注': f'利息:{fin["利息"]:,.0f}, 本金:{fin["本金"]:,.0f}'
            })
    
    # 期末现金流
    combined.append({
        '期数': period + 1,
        '日期': '2029-10',
        '项目': '期末结算',
        '租金收入(人民币)': 0,
        '融资流入(人民币)': 0,
        '等额本息还款(人民币)': 0,
        '期末尾款(人民币)': -BALLOON_PORTION,
        '残值回收(人民币)': RESIDUAL_VALUE_RMB,
        '净现金流(人民币)': RESIDUAL_VALUE_RMB - BALLOON_PORTION,
        '备注': f'残值{RESIDUAL_VALUE_USD}万美元×{EXCHANGE_RATE}={RESIDUAL_VALUE_RMB:,.0f}元, 尾款偿还{BALLOON_PORTION:,.0f}元'
    })
    
    # 计算IRR
    net_cf = [row['净现金流(人民币)'] for row in combined]
    monthly_irr = calculate_irr(net_cf)
    annual_irr = (1 + monthly_irr) ** 12 - 1
    
    return combined, total_rent, monthly_irr, annual_irr, monthly_payment

# ==================== 主程序 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("发动机租赁 IRR 计算")
    print("=" * 60)
    
    # 显示参数
    print(f"\n【基本参数】")
    print(f"发动机购买成本: {PURCHASE_COST_USD:,} 美元 = {PURCHASE_COST_RMB:,.0f} 人民币")
    print(f"残值: {RESIDUAL_VALUE_USD:,} 美元 = {RESIDUAL_VALUE_RMB:,.0f} 人民币")
    print(f"汇率: {EXCHANGE_RATE} 人民币/美元")
    
    print(f"\n【融资参数】")
    print(f"融资金额: {FINANCING_AMOUNT:,.0f} 人民币 (购买成本的{FINANCING_RATIO*100:.0f}%)")
    print(f"融资利率: {FINANCING_RATE*100:.0f}% 年利率")
    print(f"等额本息部分: {AMORTIZED_PORTION:,.0f} 人民币 ({FINANCING_AMOUNT*0.8:,.0f})")
    print(f"期末尾款: {BALLOON_PORTION:,.0f} 人民币 ({FINANCING_AMOUNT*0.2:,.0f})")
    
    # 生成现金流表
    combined, total_rent, monthly_irr, annual_irr, monthly_payment = generate_comprehensive_cashflow()
    
    print(f"\n【租金收入】")
    for year, months, monthly_rent in rental_schedule:
        print(f"{year}年: {months}个月 × {monthly_rent:,.0f} = {months * monthly_rent:,.0f} 人民币")
    print(f"总租金收入: {total_rent:,.0f} 人民币")
    
    print(f"\n【还款计划】")
    print(f"月还款额 (等额本息): {monthly_payment:,.0f} 人民币")
    print(f"期末尾款: {BALLOON_PORTION:,.0f} 人民币")
    
    print(f"\n【IRR计算结果】")
    print(f"月度IRR: {monthly_irr*100:.4f}%")
    print(f"年化IRR: {annual_irr*100:.4f}%")
    
    # 导出Excel
    df = pd.DataFrame(combined)
    output_path = r'C:\Users\Haide\.openclaw\workspace\发动机租赁现金流表.xlsx'
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='综合现金流表', index=False)
        
        # 添加汇总信息sheet
        summary_data = {
            '项目': ['发动机购买成本(美元)', '发动机购买成本(人民币)', '残值(美元)', '残值(人民币)', 
                    '汇率', '融资金额', '融资利率', '等额本息部分', '期末尾款',
                    '月还款额', '总租金收入', '月度IRR', '年化IRR'],
            '数值': [f'{PURCHASE_COST_USD:,}', f'{PURCHASE_COST_RMB:,.0f}', 
                    f'{RESIDUAL_VALUE_USD:,}', f'{RESIDUAL_VALUE_RMB:,.0f}',
                    EXCHANGE_RATE, f'{FINANCING_AMOUNT:,.0f}', f'{FINANCING_RATE*100:.0f}%',
                    f'{AMORTIZED_PORTION:,.0f}', f'{BALLOON_PORTION:,.0f}',
                    f'{monthly_payment:,.0f}', f'{total_rent:,.0f}',
                    f'{monthly_irr*100:.4f}%', f'{annual_irr*100:.4f}%']
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='汇总信息', index=False)
        
        # 融资还款明细sheet
        financing_cf, _ = calculate_financing_cash_flows()
        pd.DataFrame(financing_cf).to_excel(writer, sheet_name='融资还款明细', index=False)
    
    print(f"\n[OK] 现金流表已生成: {output_path}")