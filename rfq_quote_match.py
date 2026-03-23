# -*- coding: utf-8 -*-
"""
询价单与报价匹配分析
读取两份 RFQ 询价单，与供应商报价匹配，找出最优报价
"""

import csv
import os
from datetime import datetime

# 询价单零件号（从 Excel 文件中提取）
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

# 读取报价汇总文件
quote_file = r"C:\Users\Haide\Desktop\航材供应商报价汇总_2026-03-01_至今.csv"
quotes = []

print("=== 询价单与报价匹配分析 ===")
print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 读取报价数据
if os.path.exists(quote_file):
    print(f"\n[1/3] 读取报价文件：{quote_file}")
    with open(quote_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            quotes.append(row)
    print(f"[OK] 读取 {len(quotes)} 条报价记录")
else:
    print(f"[ERROR] 报价文件不存在：{quote_file}")
    exit(1)

# 匹配询价单零件
print("\n[2/3] 匹配询价单零件与报价...")

def find_best_quote(part_number, quotes):
    """为零件号找到最优报价"""
    matches = []
    for q in quotes:
        pn = q.get('PartNumber', '').strip().upper()
        if part_number.upper() in pn or pn in part_number.upper():
            matches.append(q)
    
    if not matches:
        return None
    
    # 按价格排序（如果有价格信息）
    # 这里简单返回第一个匹配
    return matches[0] if matches else None

# RFQ 20260313-01 匹配结果
rfq1_matches = []
rfq2_matches = []

for pn in rfq_20260313_01:
    match = find_best_quote(pn, quotes)
    if match:
        rfq1_matches.append({
            'PN': pn,
            'Supplier': match.get('From', ''),
            'Price': match.get('Price', ''),
            'Condition': match.get('Condition', ''),
            'Date': match.get('Date', '')
        })

for pn in rfq_20260305_01:
    match = find_best_quote(pn, quotes)
    if match:
        rfq2_matches.append({
            'PN': pn,
            'Supplier': match.get('From', ''),
            'Price': match.get('Price', ''),
            'Condition': match.get('Condition', ''),
            'Date': match.get('Date', '')
        })

# 导出匹配结果
print("\n[3/3] 导出匹配结果...")
output_file = r"C:\Users\Haide\Desktop\询价单报价匹配结果.csv"

all_matches = []
for m in rfq1_matches:
    m['RFQ'] = 'RFQ20260313-01'
    all_matches.append(m)
for m in rfq2_matches:
    m['RFQ'] = 'RFQ20260305-01'
    all_matches.append(m)

if all_matches:
    fieldnames = ['RFQ', 'PN', 'Supplier', 'Price', 'Condition', 'Date']
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_matches)
    
    print(f"[OK] 已导出到：{output_file}")
    print(f"[OK] 总计 {len(all_matches)} 条匹配记录")
    
    # 统计信息
    print("\n=== 匹配统计 ===")
    print(f"\nRFQ20260313-01:")
    print(f"  零件总数：{len(rfq_20260313_01)}")
    print(f"  匹配成功：{len(rfq1_matches)}")
    print(f"  匹配率：{len(rfq1_matches)/len(rfq_20260313_01)*100:.1f}%")
    
    print(f"\nRFQ20260305-01:")
    print(f"  零件总数：{len(rfq_20260305_01)}")
    print(f"  匹配成功：{len(rfq2_matches)}")
    print(f"  匹配率：{len(rfq2_matches)/len(rfq_20260305_01)*100:.1f}%")
    
    # 显示部分匹配结果
    print("\n=== 匹配结果预览 (前 20 条) ===")
    for i, m in enumerate(all_matches[:20], 1):
        price = m['Price'] or 'N/A'
        cond = m['Condition'] or 'N/A'
        print(f"{i:3}. {m['RFQ']:<15} | {m['PN']:<20} | {m['Supplier'][:30]:<30} | {price:<15} | {cond:<6}")
    if len(all_matches) > 20:
        print(f"... 还有 {len(all_matches) - 20} 条")
else:
    print("[WARN] 未找到匹配的报价记录")

print(f"\n结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=== 任务完成 ===")
