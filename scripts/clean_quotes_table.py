#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理报价总表 - 删除错误提取的垃圾数据
"""

import pandas as pd

MASTER_TABLE = r"C:\Users\Haide\Desktop\Quotes_Master_Table.csv"

def main():
    df = pd.read_csv(MASTER_TABLE)
    print(f"Before cleanup: {len(df)} records")
    
    # 删除明显错误的记录（件号是英文单词而不是 PN 格式）
    # 有效 PN 格式：包含数字和连字符，如 711002-5, 9DX404700-01
    valid_mask = df['件号'].str.contains(r'\d', na=False)  # 至少包含一个数字
    
    df_clean = df[valid_mask].copy()
    
    # 进一步筛选：删除明显是文本的 PN（如 "Description", "Minimum", "Quotes" 等）
    invalid_keywords = ['DESCRIPTION', 'MINIMUM', 'QUOTES', 'ENTERPRISES', 'AGREES', 'RETURNS', 
                        'CANNOT', 'DEPENDING', 'MICHELLE', 'AEROEDGE', 'EXPIRATION', 'CASHIER',
                        'CREDIT', 'PREPAID', 'EMAIL', 'UNLESS', 'SUPPLY', 'TRANSFER', 'BARCLAYS',
                        'ALEXANDRA', 'PACIFIC', 'QUESTIONS', 'RETURNED', 'NOTIFIED', 'MASTER',
                        'AVIATION', 'HIGGINS', 'BUSINESS', 'LEAD-TIME', 'WITHOUT', 'FACTORS',
                        'EFFORT', 'HANDLING', 'SUBJECT', 'FACTORY', 'RE-CERTIFIED', 'COMPANY',
                        'PRESTON', 'ACCEPTING', 'CONFIRM', 'EUROPEAN', 'UNITED', 'CONDITIONS',
                        'PLEASE', 'GOODRICH', 'PRICES', 'SHOWN', 'PICTURES', 'DEFECTIVE', 
                        'ABSOLUTELY']
    
    for keyword in invalid_keywords:
        df_clean = df_clean[~df_clean['件号'].str.contains(keyword, na=False, case=False)]
    
    print(f"After cleanup: {len(df_clean)} records")
    print(f"Removed: {len(df) - len(df_clean)} invalid records")
    
    # 保存
    df_clean.to_csv(MASTER_TABLE, index=False, encoding='utf-8-sig')
    print(f"\n[OK] Cleaned table saved to: {MASTER_TABLE}")
    
    # 显示有效报价
    print("\n" + "="*70)
    print("VALID QUOTES IN MASTER TABLE:")
    print("="*70)
    
    # 按件号分组显示
    for pn in df_clean['件号'].unique():
        quotes = df_clean[df_clean['件号'] == pn]
        print(f"\nPN: {pn}")
        for _, q in quotes.iterrows():
            price_str = f"${q['单价 USD']:,.2f}" if pd.notna(q['单价 USD']) and q['单价 USD'] else "TBD"
            print(f"  - {q['供应商']} | {price_str} | {q['条件']} | {q['报价日期']}")

if __name__ == "__main__":
    main()
