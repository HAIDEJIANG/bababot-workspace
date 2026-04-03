#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取最新供应商报价 v5 - 从邮件正文提取准确数据
"""

import pandas as pd
import os
from datetime import datetime

MASTER_TABLE = r"C:\Users\Haide\Desktop\Quotes_Master_Table.csv"

# 从邮件正文手动提取的报价数据（最准确）
NEW_QUOTES = [
    # 邮件 1720726318 - Michael Pavia / JMF Global
    {
        '需求编号': 'RFQ20260401-01',
        '序号': '',
        '供应商': 'JMF Global, Inc.',
        '联系人': 'Michael Pavia',
        '邮箱': 'pavia@jmfglobal.com',
        '件号': '711002-5',
        '描述': 'CONTROL PANEL',
        '条件': 'OH',
        '数量 (需求)': '1',
        '数量 (可供)': '1',
        '单价 USD': 5000.00,
        '总价 USD': 5000.00,
        '交期': 'STOCK',
        '发货地': '',
        'S/N': 'AD2871',
        'Trace To': 'CANADIAN NORTH',
        'Tag Type': '',
        '报价日期': '2026-04-02',
        '备注': 'RFQ #SYS10550020, 30 天保修'
    },
    # 邮件 1720726315 - Michelle Smith / Tiger Enterprises (从 PDF 提取)
    {
        '需求编号': 'RFQ20260401-01',
        '序号': '',
        '供应商': 'Tiger Enterprises',
        '联系人': 'Michelle Smith',
        '邮箱': '',
        '件号': '9DX404700-01',
        '描述': 'FLASH TUBE',
        '条件': 'NE',
        '数量 (需求)': '3',
        '数量 (可供)': '3',
        '单价 USD': 1100.00,
        '总价 USD': 3300.00,
        '交期': 'IN STOCK',
        '发货地': 'Pelzer, SC',
        'S/N': '',
        'Trace To': 'GOODRICH',
        'Tag Type': '',
        '报价日期': '2026-04-01',
        '备注': 'Quote Q381377'
    },
    # 邮件 1720726223 - Pacific Aerospace (QU-3825291)
    {
        '需求编号': 'RFQ20260401-01',
        '序号': '',
        '供应商': 'Pacific Aerospace',
        '联系人': '',
        '邮箱': 'aq@sales.pac-air.com',
        '件号': 'Y580-02133-01-3',
        '描述': 'MODIFICATION KIT',
        '条件': 'NS',
        '数量 (需求)': '',
        '数量 (可供)': '',
        '单价 USD': 9650.00,
        '总价 USD': 9650.00,
        '交期': '',
        '发货地': '',
        'S/N': '',
        'Trace To': '',
        'Tag Type': '',
        '报价日期': '2026-04-01',
        '备注': 'QU-3825291'
    },
    # 邮件 1720726221 - Hubert JUBAULT
    {
        '需求编号': 'RFQ20260401-01',
        '序号': '',
        '供应商': 'Unknown',
        '联系人': 'Hubert JUBAULT',
        '邮箱': '',
        '件号': 'Y580-02133-01-3',
        '描述': '',
        '条件': 'NE',
        '数量 (需求)': '',
        '数量 (可供)': '',
        '单价 USD': '',
        '总价 USD': '',
        '交期': '',
        '发货地': '',
        'S/N': 'MS0055449',
        'Trace To': '',
        'Tag Type': '',
        '报价日期': '2026-04-01',
        '备注': 'Quote C10232278'
    },
    # 邮件 1720726138 - Fleur Woodage
    {
        '需求编号': 'RFQ20260401-01',
        '序号': '',
        '供应商': 'Unknown',
        '联系人': 'Fleur Woodage',
        '邮箱': '',
        '件号': '2G916-1039',
        '描述': '',
        '条件': 'NE',
        '数量 (需求)': '',
        '数量 (可供)': '',
        '单价 USD': '',
        '总价 USD': '',
        '交期': '',
        '发货地': '',
        'S/N': '',
        'Trace To': '',
        'Tag Type': '',
        '报价日期': '2026-04-01',
        '备注': 'Quote 622648'
    },
]

def main():
    print("Starting quote extraction v5...")
    print(f"New quotes to add: {len(NEW_QUOTES)}")
    
    # 读取现有总表
    if os.path.exists(MASTER_TABLE):
        df_existing = pd.read_csv(MASTER_TABLE)
        print(f"Existing records: {len(df_existing)}")
        
        df_new = pd.DataFrame(NEW_QUOTES)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        
        # 去重（基于件号 + 供应商）
        df_combined = df_combined.drop_duplicates(subset=['件号', '供应商'], keep='last')
        
        print(f"Combined records: {len(df_combined)}")
        
        df_combined.to_csv(MASTER_TABLE, index=False, encoding='utf-8-sig')
        print(f"\n[OK] Updated master table: {MASTER_TABLE}")
    else:
        df_new = pd.DataFrame(NEW_QUOTES)
        df_new.to_csv(MASTER_TABLE, index=False, encoding='utf-8-sig')
        print(f"\n[OK] Created master table: {MASTER_TABLE}")
    
    # 汇总统计
    print("\n" + "="*70)
    print("SUMMARY - New Quotes Added:")
    print("="*70)
    for q in NEW_QUOTES:
        price_str = f"${q['单价 USD']:,.2f}" if q['单价 USD'] else "TBD"
        print(f"PN: {q['件号']} | Supplier: {q['供应商']} | Price: {price_str} | Cond: {q['条件']}")
    
    print("\n[OK] Done!")

if __name__ == "__main__":
    main()
