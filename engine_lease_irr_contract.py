# -*- coding: utf-8 -*-
"""
发动机租赁 IRR 计算 - 基于租赁合同实际条款
"""
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

# ==================== 参数设置 ====================
# 发动机购买成本
PURCHASE_COST_USD = 9_000_000  # 900万美元

# 残值
RESIDUAL_VALUE_USD = 2_000_000  # 200万美元

# 汇率
EXCHANGE_RATE = 6.9  # 人民币/美元

# 转换为人民币
PURCHASE_COST_RMB = PURCHASE_COST_USD * EXCHANGE_RATE
RESIDUAL_VALUE_RMB = RESIDUAL_VALUE_USD * EXCHANGE_RATE

# 融资参数
FINANCING_RATIO = 0.90  # 90%融资
FINANCING_AMOUNT = PURCHASE_COST_RMB * FINANCING_RATIO
FINANCING_RATE = 0.05  # 5%年利率

# 还款方式：80%等额本息 + 20%期末一次还清
AMORTIZED_PORTION = FINANCING_AMOUNT * 0.80
BALLOON_PORTION = FINANCING_AMOUNT * 0.20

# ==================== 租赁合同参数 ====================
# 月租金（美元）
MONTHLY_RENT_USD = 95_000  # $95,000/月

# 租期（月）
LEASE_TERM_MONTHS = 36  # 36个月

# 押金（美元）
DEPOSIT_USD = 285_000

# 约定金额（用于计算终止损失）
STIPULATED_AMOUNT_USD = 7_970_000

# 转换为人民币
MONTHLY_RENT_RMB = MONTHLY_RENT_USD * EXCHANGE_RATE
DEPOSIT_RMB = DEPOSIT_USD * EXCHANGE_RATE

# ==================== IRR计算函数 ====================
def calculate_irr(cash_flows, guess=0.1):
    """使用二分法计算IRR"""
    def npv(rate):
        return sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
    
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

# ==================== 计算等额本息还款 ====================
def calculate_monthly_payment(principal, annual_rate, periods):
    """计算等额本息月还款额"""
    monthly_rate = annual_rate / 12
    payment = principal * (monthly_rate * (1 + monthly_rate)**periods) / ((1 + monthly_rate)**periods - 1)
    return payment

monthly_payment = calculate_monthly_payment(AMORTIZED_PORTION, FINANCING_RATE, LEASE_TERM_MONTHS)

# ==================== 生成现金流表 ====================
def generate_cashflow():
    cash_flows = []
    
    # 起始日期
    start_date = datetime(2026, 1, 1)
    
    # 期初：购买发动机 + 融资流入
    cash_flows.append({
        '期数': 0,
        '日期': start_date.strftime('%Y-%m-%d'),
        '项目': '期初',
        '租金收入(美元)': 0,
        '租金收入(人民币)': 0,
        '融资流入(人民币)': FINANCING_AMOUNT,
        '还款支出(人民币)': 0,
        '残值回收(人民币)': 0,
        '净现金流(人民币)': -PURCHASE_COST_RMB + FINANCING_AMOUNT,
        '备注': f'购买发动机: -{PURCHASE_COST_RMB:,.0f}元, 融资: +{FINANCING_AMOUNT:,.0f}元'
    })
    
    # 每月现金流
    for month in range(1, LEASE_TERM_MONTHS + 1):
        current_date = start_date + relativedelta(months=month)
        
        # 租金收入（美元转人民币）
        rent_usd = MONTHLY_RENT_USD
        rent_rmb = rent_usd * EXCHANGE_RATE
        
        # 融资还款（等额本息部分）
        repayment = monthly_payment if month <= LEASE_TERM_MONTHS else 0
        
        # 期末尾款
        balloon = BALLOON_PORTION if month == LEASE_TERM_MONTHS else 0
        
        # 残值回收
        residual = RESIDUAL_VALUE_RMB if month == LEASE_TERM_MONTHS else 0
        
        # 净现金流
        net_cf = rent_rmb - repayment - balloon + residual
        
        cash_flows.append({
            '期数': month,
            '日期': current_date.strftime('%Y-%m'),
            '项目': f'第{month}月',
            '租金收入(美元)': rent_usd,
            '租金收入(人民币)': rent_rmb,
            '融资流入(人民币)': 0,
            '还款支出(人民币)': -repayment,
            '残值回收(人民币)': residual if residual > 0 else 0,
            '净现金流(人民币)': net_cf,
            '备注': f'月租${rent_usd:,}×{EXCHANGE_RATE}={rent_rmb:,.0f}元' + (f', 尾款-{balloon:,.0f}, 残值+{residual:,.0f}' if month == LEASE_TERM_MONTHS else '')
        })
    
    return cash_flows

# ==================== 主程序 ====================
if __name__ == '__main__':
    print("=" * 70)
    print("发动机租赁 IRR 计算（基于租赁合同实际条款）")
    print("=" * 70)
    
    print(f"\n【基本参数】")
    print(f"发动机购买成本: ${PURCHASE_COST_USD:,} = {PURCHASE_COST_RMB:,.0f} 人民币")
    print(f"残值: ${RESIDUAL_VALUE_USD:,} = {RESIDUAL_VALUE_RMB:,.0f} 人民币")
    print(f"汇率: {EXCHANGE_RATE} 人民币/美元")
    
    print(f"\n【租赁合同条款】")
    print(f"月租金: ${MONTHLY_RENT_USD:,} = {MONTHLY_RENT_RMB:,.0f} 人民币")
    print(f"租期: {LEASE_TERM_MONTHS} 个月")
    print(f"押金: ${DEPOSIT_USD:,} (银行保函)")
    print(f"总租金收入: ${MONTHLY_RENT_USD * LEASE_TERM_MONTHS:,} = {MONTHLY_RENT_RMB * LEASE_TERM_MONTHS:,.0f} 人民币")
    
    print(f"\n【融资参数】")
    print(f"融资金额: {FINANCING_AMOUNT:,.0f} 人民币 (购买成本的{FINANCING_RATIO*100:.0f}%)")
    print(f"融资利率: {FINANCING_RATE*100:.0f}% 年利率")
    print(f"等额本息部分: {AMORTIZED_PORTION:,.0f} 人民币 (80%)")
    print(f"期末尾款: {BALLOON_PORTION:,.0f} 人民币 (20%)")
    print(f"月还款额: {monthly_payment:,.0f} 人民币")
    
    # 生成现金流
    cash_flows = generate_cashflow()
    
    # 计算IRR
    net_cf_list = [cf['净现金流(人民币)'] for cf in cash_flows]
    monthly_irr = calculate_irr(net_cf_list)
    annual_irr = (1 + monthly_irr) ** 12 - 1
    
    print(f"\n【IRR计算结果】")
    print(f"月度IRR: {monthly_irr*100:.4f}%")
    print(f"年化IRR: {annual_irr*100:.2f}%")
    
    # 计算NPV@5%
    discount_rate = 0.05 / 12
    npv_5 = sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(net_cf_list))
    print(f"NPV(折现率5%): {npv_5:,.0f} 人民币")
    
    # 导出Excel
    df = pd.DataFrame(cash_flows)
    output_path = r'C:\Users\Haide\.openclaw\workspace\发动机租赁现金流表_合同版.xlsx'
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='现金流表', index=False)
        
        # 汇总信息
        summary = pd.DataFrame({
            '项目': ['发动机购买成本(美元)', '发动机购买成本(人民币)', '残值(美元)', '残值(人民币)',
                    '汇率', '月租金(美元)', '月租金(人民币)', '租期(月)', '总租金收入(人民币)',
                    '融资金额', '融资利率', '等额本息部分', '期末尾款', '月还款额',
                    '月度IRR', '年化IRR', 'NPV(5%)'],
            '数值': [f'${PURCHASE_COST_USD:,}', f'{PURCHASE_COST_RMB:,.0f}',
                    f'${RESIDUAL_VALUE_USD:,}', f'{RESIDUAL_VALUE_RMB:,.0f}',
                    EXCHANGE_RATE, f'${MONTHLY_RENT_USD:,}', f'{MONTHLY_RENT_RMB:,.0f}',
                    LEASE_TERM_MONTHS, f'{MONTHLY_RENT_RMB * LEASE_TERM_MONTHS:,.0f}',
                    f'{FINANCING_AMOUNT:,.0f}', f'{FINANCING_RATE*100:.0f}%',
                    f'{AMORTIZED_PORTION:,.0f}', f'{BALLOON_PORTION:,.0f}',
                    f'{monthly_payment:,.0f}',
                    f'{monthly_irr*100:.4f}%', f'{annual_irr*100:.2f}%',
                    f'{npv_5:,.0f}']
        })
        summary.to_excel(writer, sheet_name='汇总信息', index=False)
    
    print(f"\n[OK] 现金流表已生成: {output_path}")