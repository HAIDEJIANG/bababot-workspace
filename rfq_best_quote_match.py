# -*- coding: utf-8 -*-
"""
询价单最优报价匹配分析（优化版）
基于邮件原文中实际提取的报价信息进行匹配
"""

import csv
import os
from datetime import datetime

# 询价单零件号
rfq_20260313_01 = [
    "1152466-250", "129666-3", "18-1738-12", "1FA14012-8", "2041217-0416",
    "2215628-3", "2215629-1", "2215629-2", "2313M-347-4", "3214972-1",
    "35000-00-01", "3522W000-001", "4063-19972-01AA", "45-0351-1",
    "57186-11", "606802-2", "622-5132-109", "622-5135-802", "622-7998-013",
    "622814-5", "808556-1", "822-2532-100", "901906", "902020-01",
    "BFS24", "DMN23-1C", "G6992-02", "R15048", "R5303M1", "R5303M1-1"
]

rfq_20260305_01 = [
    "10037-0770", "15800-029-3", "170089-02-01", "2040061-103",
    "285W0024-1M", "312BS101-1", "3291828-1", "346A2801-5",
    "473957-4", "5000-1-01A-2396", "5A3307-701", "622-5132-109",
    "622-5135-802", "622-7998-013", "622814-5", "808556-1",
    "822-2532-100", "901906", "902020-01", "BFS24", "DMN23-1C",
    "G6992-02", "R15048", "R5303M1", "R5303M1-1"
]

# 已知报价数据（从邮件中提取的实际报价）
known_quotes = [
    # Aeroned 报价 (2026-03-09)
    {"PN": "3075663-01", "Price": "$23,764", "Condition": "NE", "Supplier": "Aeroned (supapitch@aeroned.com)"},
    {"PN": "65B40435-13", "Price": "$42,007.00", "Condition": "NE", "Supplier": "Aeroned (sales@aeroned.com)"},
    
    # Avsource 报价 (2026-03-09)
    {"PN": "SYS10486194", "Price": "$45.00", "Condition": "NS", "Supplier": "Avsource via Rotabull"},
    
    # L.J. Walch 报价 (2026-03-09)
    {"PN": "1N1184AR", "Price": "$30.00", "Condition": "NS", "Supplier": "L.J. Walch (jessica@ljwalch.com)"},
    {"PN": "1N1184A", "Price": "$30.00", "Condition": "NS", "Supplier": "L.J. Walch (jessica@ljwalch.com)"},
    
    # Brooks & Maldini 报价 (2026-03-10)
    {"PN": "MS90451-7152", "Price": "$301.75", "Condition": "NE", "Supplier": "Brooks & Maldini"},
    
    # 从 Blue Sky Technics 邮件中提取的零件（2026-02-23）
    {"PN": "1152466-250", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "129666-3", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "18-1738-12", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "1FA14012-8", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "2041217-0416", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "2215628-3", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "2215629-1", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "2215629-2", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "2313M-347-4", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "3214972-1", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "35000-00-01", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "3522W000-001", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "4063-19972-01AA", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "45-0351-1", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "57186-11", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "606802-2", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "622-5132-109", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "622-5135-802", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "622-7998-013", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "622814-5", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "808556-1", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "822-2532-100", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "901906", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "902020-01", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "BFS24", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "DMN23-1C", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "G6992-02", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "R15048", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "R5303M1", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "R5303M1-1", "Price": "待报价", "Condition": "SV", "Supplier": "Blue Sky Technics (RFQ)"},
    
    # 从 RFQ 邮件中提取的其他零件
    {"PN": "10037-0770", "Price": "~$6,000", "Condition": "待确认", "Supplier": "市场价参考"},
    {"PN": "15800-029-3", "Price": "待报价", "Condition": "待确认", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "170089-02-01", "Price": "待报价", "Condition": "待确认", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "2040061-103", "Price": "待报价", "Condition": "待确认", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "285W0024-1M", "Price": "待报价", "Condition": "待确认", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "312BS101-1", "Price": "待报价", "Condition": "待确认", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "3291828-1", "Price": "待报价", "Condition": "待确认", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "346A2801-5", "Price": "待报价", "Condition": "待确认", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "473957-4", "Price": "待报价", "Condition": "待确认", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "5000-1-01A-2396", "Price": "待报价", "Condition": "待确认", "Supplier": "Blue Sky Technics (RFQ)"},
    {"PN": "5A3307-701", "Price": "待报价", "Condition": "待确认", "Supplier": "Blue Sky Technics (RFQ)"},
]

print("=== 询价单最优报价匹配分析 ===")
print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 匹配函数
def find_best_quote(part_number, quotes):
    """为零件号找到最优报价"""
    matches = []
    pn_upper = part_number.upper().strip()
    
    for q in quotes:
        quote_pn = q.get('PN', '').upper().strip()
        # 精确匹配或部分匹配
        if pn_upper == quote_pn or pn_upper in quote_pn or quote_pn in pn_upper:
            matches.append(q)
    
    if not matches:
        return None
    
    # 优先返回有价格的
    for m in matches:
        if m.get('Price') and m['Price'] not in ['待报价', '待确认']:
            return m
    
    return matches[0] if matches else None

# 匹配 RFQ 20260313-01
print("\n[1/3] 匹配 RFQ20260313-01...")
rfq1_results = []
for pn in rfq_20260313_01:
    match = find_best_quote(pn, known_quotes)
    rfq1_results.append({
        'RFQ': 'RFQ20260313-01',
        'PN': pn,
        'Supplier': match['Supplier'] if match else '未找到报价',
        'Price': match['Price'] if match else 'N/A',
        'Condition': match['Condition'] if match else 'N/A',
        'Status': '已匹配' if match else '待询价'
    })

# 匹配 RFQ 20260305-01
print("[2/3] 匹配 RFQ20260305-01...")
rfq2_results = []
for pn in rfq_20260305_01:
    match = find_best_quote(pn, known_quotes)
    rfq2_results.append({
        'RFQ': 'RFQ20260305-01',
        'PN': pn,
        'Supplier': match['Supplier'] if match else '未找到报价',
        'Price': match['Price'] if match else 'N/A',
        'Condition': match['Condition'] if match else 'N/A',
        'Status': '已匹配' if match else '待询价'
    })

# 导出结果
print("[3/3] 导出匹配结果...")
output_file = r"C:\Users\Haide\Desktop\询价单最优报价匹配结果.csv"

all_results = rfq1_results + rfq2_results

if all_results:
    fieldnames = ['RFQ', 'PN', 'Supplier', 'Price', 'Condition', 'Status']
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"\n[OK] 已导出到：{output_file}")
    
    # 统计信息
    print("\n" + "="*80)
    print("=== 匹配统计 ===")
    print("="*80)
    
    rfq1_matched = sum(1 for r in rfq1_results if r['Status'] == '已匹配')
    rfq2_matched = sum(1 for r in rfq2_results if r['Status'] == '已匹配')
    
    print(f"\n【RFQ20260313-01】")
    print(f"  零件总数：{len(rfq_20260313_01)}")
    print(f"  已匹配：{rfq1_matched} ({rfq1_matched/len(rfq_20260313_01)*100:.1f}%)")
    print(f"  待询价：{len(rfq_20260313_01) - rfq1_matched}")
    
    print(f"\n【RFQ20260305-01】")
    print(f"  零件总数：{len(rfq_20260305_01)}")
    print(f"  已匹配：{rfq2_matched} ({rfq2_matched/len(rfq_20260305_01)*100:.1f}%)")
    print(f"  待询价：{len(rfq_20260305_01) - rfq2_matched}")
    
    # 显示有价格的匹配结果
    print("\n" + "="*80)
    print("=== 已获报价的零件 (最优报价) ===")
    print("="*80)
    
    priced_items = [r for r in all_results if r['Price'] not in ['N/A', '待报价', '待确认']]
    if priced_items:
        for i, r in enumerate(priced_items, 1):
            print(f"{i:3}. {r['PN']:<25} | {r['Price']:<15} | {r['Condition']:<10} | {r['Supplier'][:40]}")
    else:
        print("暂无具体价格报价")
    
    # 显示待询价的零件
    print("\n" + "="*80)
    print("=== 待询价零件清单 ===")
    print("="*80)
    
    pending_items = [r for r in all_results if r['Status'] == '待询价']
    if pending_items:
        for i, r in enumerate(pending_items, 1):
            print(f"{i:3}. {r['PN']:<25} | {r['RFQ']}")
        print(f"\n共计 {len(pending_items)} 个零件需要向供应商询价")
    else:
        print("所有零件均已获得报价")

else:
    print("[WARN] 无匹配结果")

print(f"\n结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=== 任务完成 ===")
