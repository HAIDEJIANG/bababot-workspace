# -*- coding: utf-8 -*-
"""
RFQ 询价单与供应商报价匹配分析
找出每个零件号的最优报价
"""

import csv
import os
from datetime import datetime
from config import (
    SUPPLIER_QUOTE_FILE,
    RFQ_MATCH_RESULT,
    RFQ_BEST_QUOTE,
    OUTPUT_ENCODING,
    DEFAULT_OUTPUT_DIR
)

# RFQ 询价单零件号（从 Excel 文件中提取）
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

# 读取报价汇总文件（使用配置路径）
quote_file = SUPPLIER_QUOTE_FILE
quotes = []

print("="*80)
print("=== RFQ 询价单与供应商报价匹配分析 ===")
print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"输出目录：{DEFAULT_OUTPUT_DIR}")
print("="*80)

# 读取报价数据
if os.path.exists(quote_file):
    print(f"\n[1/4] 读取报价文件：{quote_file}")
    with open(quote_file, 'r', encoding=OUTPUT_ENCODING) as f:
        reader = csv.DictReader(f)
        for row in reader:
            quotes.append(row)
    print(f"[OK] 读取 {len(quotes)} 条报价记录")
else:
    print(f"[ERROR] 报价文件不存在：{quote_file}")
    exit(1)

# 匹配函数
def find_quotes_for_part(part_number, quotes):
    """为零件号找到所有匹配的报价"""
    matches = []
    pn_upper = part_number.upper().strip()
    
    for q in quotes:
        quote_pn = q.get('PartNumber', '').upper().strip()
        quote_desc = q.get('Description', '').upper().strip()
        
        # 精确匹配或部分匹配
        if pn_upper == quote_pn or pn_upper in quote_pn or quote_pn in pn_upper:
            matches.append(q)
        # 也检查描述中是否包含零件号
        elif pn_upper in quote_desc:
            matches.append(q)
    
    return matches

# 为每个 RFQ 零件匹配报价
print("\n[2/4] 匹配 RFQ 零件与报价...")

rfq1_matches = []
rfq2_matches = []

for pn in rfq_20260313_01:
    matches = find_quotes_for_part(pn, quotes)
    rfq1_matches.append({
        'RFQ': 'RFQ20260313-01',
        'PN': pn,
        'MatchCount': len(matches),
        'Quotes': matches
    })

for pn in rfq_20260305_01:
    matches = find_quotes_for_part(pn, quotes)
    rfq2_matches.append({
        'RFQ': 'RFQ20260305-01',
        'PN': pn,
        'MatchCount': len(matches),
        'Quotes': matches
    })

# 统计匹配情况
rfq1_matched = sum(1 for m in rfq1_matches if m['MatchCount'] > 0)
rfq2_matched = sum(1 for m in rfq2_matches if m['MatchCount'] > 0)

print(f"\nRFQ20260313-01: {rfq1_matched}/{len(rfq_20260313_01)} 零件找到报价")
print(f"RFQ20260305-01: {rfq2_matched}/{len(rfq_20260305_01)} 零件找到报价")

# 导出匹配结果
print("\n[3/4] 导出匹配结果...")
output_file = RFQ_MATCH_RESULT  # 使用配置路径

all_results = []
for m in rfq1_matches + rfq2_matches:
    if m['MatchCount'] > 0:
        for q in m['Quotes']:
            all_results.append({
                'RFQ': m['RFQ'],
                'PartNumber': m['PN'],
                'QuoteSupplier': q.get('From', ''),
                'QuotePrice': q.get('Price', ''),
                'QuoteCondition': q.get('Condition', ''),
                'QuoteDate': q.get('Date', ''),
                'QuoteSource': q.get('Source', '')
            })
    else:
        all_results.append({
            'RFQ': m['RFQ'],
            'PartNumber': m['PN'],
            'QuoteSupplier': '待询价',
            'QuotePrice': 'N/A',
            'QuoteCondition': 'N/A',
            'QuoteDate': 'N/A',
            'QuoteSource': 'N/A'
        })

if all_results:
    fieldnames = ['RFQ', 'PartNumber', 'QuoteSupplier', 'QuotePrice', 'QuoteCondition', 'QuoteDate', 'QuoteSource']
    with open(output_file, 'w', newline='', encoding=OUTPUT_ENCODING) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"[OK] 已导出到：{output_file}")
    print(f"[OK] 总计 {len(all_results)} 条匹配记录")

# 生成最优报价推荐
print("\n[4/4] 生成最优报价推荐...")

def get_best_quote(matches):
    """从多个报价中选择最优（简单规则：有价格的优先）"""
    if not matches:
        return None
    
    # 优先返回有明确价格的
    for m in matches:
        price = m.get('Price', '')
        if price and price not in ['N/A', '待报价', '待确认']:
            return m
    
    return matches[0] if matches else None

# 最优报价汇总
best_quotes = []
for m in rfq1_matches + rfq2_matches:
    best = get_best_quote(m['Quotes'])
    best_quotes.append({
        'RFQ': m['RFQ'],
        'PartNumber': m['PN'],
        'BestSupplier': best.get('From', '') if best else '待询价',
        'BestPrice': best.get('Price', '') if best else 'N/A',
        'Condition': best.get('Condition', '') if best else 'N/A',
        'Status': '已匹配' if best and best.get('Price') not in ['', 'N/A', '待报价'] else '待询价'
    })

# 导出最优报价（使用配置路径）
best_output = RFQ_BEST_QUOTE
if best_quotes:
    fieldnames = ['RFQ', 'PartNumber', 'BestSupplier', 'BestPrice', 'Condition', 'Status']
    with open(best_output, 'w', newline='', encoding=OUTPUT_ENCODING) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(best_quotes)
    
    print(f"[OK] 最优报价推荐已导出到：{best_output}")

# 统计摘要
print("\n" + "="*80)
print("=== 匹配统计摘要 ===")
print("="*80)

print(f"\n【RFQ20260313-01】(30 个零件)")
print(f"  找到报价：{rfq1_matched} 个 ({rfq1_matched/len(rfq_20260313_01)*100:.1f}%)")
print(f"  待询价：{len(rfq_20260313_01) - rfq1_matched} 个")

print(f"\n【RFQ20260305-01】(25 个零件)")
print(f"  找到报价：{rfq2_matched} 个 ({rfq2_matched/len(rfq_20260305_01)*100:.1f}%)")
print(f"  待询价：{len(rfq_20260305_01) - rfq2_matched} 个")

# 显示部分匹配结果
print("\n" + "="*80)
print("=== 已匹配报价预览 (前 20 条) ===")
print("="*80)

matched_items = [m for m in rfq1_matches + rfq2_matches if m['MatchCount'] > 0]
for i, m in enumerate(matched_items[:20], 1):
    best = get_best_quote(m['Quotes'])
    price = best.get('Price', 'N/A') if best else 'N/A'
    supplier = best.get('From', 'N/A')[:30] if best else 'N/A'
    print(f"{i:3}. {m['PN']:<25} | {price:<15} | {supplier:<30} | {m['MatchCount']}个报价")

if len(matched_items) > 20:
    print(f"... 还有 {len(matched_items) - 20} 个已匹配零件")

# 显示待询价零件
print("\n" + "="*80)
print("=== 待询价零件清单 ===")
print("="*80)

pending_items = [m for m in rfq1_matches + rfq2_matches if m['MatchCount'] == 0]
if pending_items:
    for i, m in enumerate(pending_items, 1):
        print(f"{i:3}. {m['RFQ']:<18} | {m['PN']}")
    print(f"\n共计 {len(pending_items)} 个零件需要向供应商询价")
else:
    print("所有零件均已获得报价！")

print("\n" + "="*80)
print(f"结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=== 任务完成 ===")
print("="*80)
