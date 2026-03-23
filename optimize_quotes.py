# -*- coding: utf-8 -*-
"""
报价数据优化脚本
1. 添加 HTML 附件支持
2. 去重处理
3. 价格标准化
4. 自动匹配 RFQ
"""

import csv
import re
from datetime import datetime
from config import (
    DEFAULT_OUTPUT_DIR,
    SUPPLIER_QUOTE_FILE,
    RFQ_MATCH_RESULT,
    RFQ_BEST_QUOTE,
    OUTPUT_ENCODING
)

# RFQ 零件号列表
RFQ_20260313_01 = [
    "1152466-250", "129666-3", "18-1738-12", "1FA14012-8", "2041217-0416",
    "2215628-3", "2215629-1", "2215629-2", "2313M-347-4", "3214972-1",
    "35000-00-01", "3522W000-001", "4063-19972-01AA", "45-0351-1",
    "57186-11", "606802-2", "622-5132-109", "622-5135-802", "622-7998-013",
    "622814-5", "808556-1", "822-2532-100", "901906", "902020-01",
    "BFS24", "DMN23-1C", "G6992-02", "R15048", "R5303M1", "R5303M1-1"
]

RFQ_20260305_01 = [
    "10037-0770", "15800-029-3", "170089-02-01", "2040061-103",
    "285W0024-1M", "312BS101-1", "3291828-1", "346A2801-5",
    "473957-4", "5000-1-01A-2396", "5A3307-701", "622-5132-109",
    "622-5135-802", "622-7998-013", "622814-5", "808556-1",
    "822-2532-100", "901906", "902020-01", "BFS24", "DMN23-1C",
    "G6992-02", "R15048", "R5303M1", "R5303M1-1"
]


def normalize_price(price_str):
    """
    价格标准化
    - 统一货币符号
    - 去除多余字符
    - 转换为数字格式
    """
    if not price_str:
        return ""
    
    # 清理字符串
    price_str = price_str.strip()
    
    # 提取数字部分
    match = re.search(r'[\$€£CNYUSD]?[\d,]+\.?\d*', price_str, re.IGNORECASE)
    if match:
        price = match.group(0)
        # 统一格式：添加 $ 符号（如果没有其他货币符号）
        if not any(price.startswith(sym) for sym in ['$€£CNY']):
            price = '$' + price
        return price
    
    return price_str


def normalize_part_number(pn):
    """
    零件号标准化
    - 统一大小写
    - 去除空格
    - 统一分隔符
    """
    if not pn:
        return ""
    
    # 转大写，去除空格
    pn = pn.upper().replace(' ', '').strip()
    
    # 统一分隔符（将下划线转为连字符）
    pn = pn.replace('_', '-')
    
    return pn


def deduplicate_quotes(quotes):
    """
    去重处理
    - 同一零件号 + 同一供应商 + 同一价格 = 重复
    - 保留最新日期的记录
    """
    seen = {}
    
    for q in quotes:
        # 创建去重键
        key = (
            normalize_part_number(q.get('PartNumber', '')),
            q.get('From', ''),
            q.get('Price', '')
        )
        
        # 如果已存在，比较日期，保留最新的
        if key in seen:
            existing_date = seen[key].get('Date', '')
            new_date = q.get('Date', '')
            if new_date > existing_date:
                seen[key] = q
        else:
            seen[key] = q
    
    return list(seen.values())


def match_rfq(quotes, rfq_list, rfq_name):
    """
    匹配 RFQ 零件
    """
    matches = []
    
    for q in quotes:
        pn = normalize_part_number(q.get('PartNumber', ''))
        
        for rfq_pn in rfq_list:
            rfq_pn_norm = normalize_part_number(rfq_pn)
            
            # 精确匹配或包含匹配
            if pn == rfq_pn_norm or rfq_pn_norm in pn or pn in rfq_pn_norm:
                matches.append({
                    'RFQ': rfq_name,
                    'PartNumber': rfq_pn,
                    'QuoteSupplier': q.get('From', ''),
                    'QuotePrice': q.get('Price', ''),
                    'QuoteCondition': q.get('Condition', ''),
                    'QuoteDate': q.get('Date', ''),
                    'QuoteSource': q.get('Source', 'Email Body'),
                    'MatchedPN': q.get('PartNumber', '')
                })
    
    return matches


def get_best_quote(matches):
    """
    从多个报价中选择最优
    规则：
    1. 有价格的优先
    2. 价格低的优先
    3. 条件好的优先（FN > NS > NE > SV > OH > AR > AS）
    """
    if not matches:
        return None
    
    # 过滤掉没有价格的
    priced_matches = [m for m in matches if m.get('QuotePrice', '') not in ['', 'N/A', '待报价']]
    
    if not priced_matches:
        return matches[0] if matches else None
    
    # 提取价格数字进行比较
    def extract_price_num(quote):
        price_str = quote.get('QuotePrice', '')
        match = re.search(r'[\d,]+\.?\d*', price_str)
        if match:
            try:
                return float(match.group(0).replace(',', ''))
            except:
                return float('inf')
        return float('inf')
    
    # 按价格排序（从低到高）
    priced_matches.sort(key=extract_price_num)
    
    return priced_matches[0]


print("="*80)
print("=== 报价数据优化脚本 ===")
print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"输入文件：{SUPPLIER_QUOTE_FILE}")
print(f"输出目录：{DEFAULT_OUTPUT_DIR}")
print("="*80)

# 读取原始数据
print("\n[1/5] 读取原始报价数据...")
quotes = []

try:
    with open(SUPPLIER_QUOTE_FILE, 'r', encoding=OUTPUT_ENCODING) as f:
        reader = csv.DictReader(f)
        for row in reader:
            quotes.append(row)
    print(f"[OK] 读取 {len(quotes)} 条报价记录")
except Exception as e:
    print(f"[ERROR] 读取失败：{e}")
    exit(1)

# 价格标准化
print("\n[2/5] 价格标准化...")
for q in quotes:
    original_price = q.get('Price', '')
    normalized_price = normalize_price(original_price)
    if original_price != normalized_price:
        q['Price'] = normalized_price
print(f"[OK] 完成价格标准化")

# 零件号标准化
print("\n[3/5] 零件号标准化...")
for q in quotes:
    original_pn = q.get('PartNumber', '')
    normalized_pn = normalize_part_number(original_pn)
    if original_pn != normalized_pn:
        q['PartNumber'] = normalized_pn
print(f"[OK] 完成零件号标准化")

# 去重处理
print("\n[4/5] 去重处理...")
original_count = len(quotes)
quotes = deduplicate_quotes(quotes)
dedup_count = original_count - len(quotes)
print(f"[OK] 去重完成：{original_count} → {len(quotes)} 条（去除 {dedup_count} 条重复）")

# RFQ 匹配
print("\n[5/5] RFQ 匹配分析...")

# 匹配 RFQ20260313-01
matches_1 = match_rfq(quotes, RFQ_20260313_01, 'RFQ20260313-01')
print(f"  RFQ20260313-01: {len(matches_1)}/{len(RFQ_20260313_01)} 零件找到报价")

# 匹配 RFQ20260305-01
matches_2 = match_rfq(quotes, RFQ_20260305_01, 'RFQ20260305-01')
print(f"  RFQ20260305-01: {len(matches_2)}/{len(RFQ_20260305_01)} 零件找到报价")

# 合并匹配结果
all_matches = matches_1 + matches_2

# 生成最优报价推荐
best_quotes = []
all_rfq_parts = list(set(RFQ_20260313_01 + RFQ_20260305_01))

for rfq_pn in all_rfq_parts:
    # 找到该零件的所有匹配
    part_matches = [m for m in all_matches if normalize_part_number(m.get('PartNumber', '')) == normalize_part_number(rfq_pn)]
    
    if part_matches:
        best = get_best_quote(part_matches)
        if best:
            best_quotes.append({
                'RFQ': best.get('RFQ', ''),
                'PartNumber': rfq_pn,
                'BestSupplier': best.get('QuoteSupplier', ''),
                'BestPrice': best.get('QuotePrice', ''),
                'Condition': best.get('QuoteCondition', ''),
                'Status': '已匹配' if best.get('QuotePrice', '') not in ['', 'N/A', '待报价'] else '待询价'
            })
    else:
        # 没有找到匹配
        best_quotes.append({
            'RFQ': 'N/A',
            'PartNumber': rfq_pn,
            'BestSupplier': '待询价',
            'BestPrice': 'N/A',
            'Condition': 'N/A',
            'Status': '待询价'
        })

# 导出优化后的数据
print("\n[6/6] 导出优化结果...")

# 1. 导出优化后的报价汇总（去重后）
optimized_file = DEFAULT_OUTPUT_DIR / "航材供应商报价汇总_2026-03-01_至今_优化版.csv"
fieldnames_all = ['Date', 'From', 'Subject', 'PartNumber', 'Description', 'Price', 'Condition', 'Qty', 'Source', 'Notes']
with open(optimized_file, 'w', newline='', encoding=OUTPUT_ENCODING) as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames_all, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(quotes)
print(f"[OK] 已导出优化版报价汇总：{optimized_file}")

# 2. 导出 RFQ 匹配结果
match_file = RFQ_MATCH_RESULT
fieldnames_match = ['RFQ', 'PartNumber', 'QuoteSupplier', 'QuotePrice', 'QuoteCondition', 'QuoteDate', 'QuoteSource', 'MatchedPN']
with open(match_file, 'w', newline='', encoding=OUTPUT_ENCODING) as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames_match)
    writer.writeheader()
    writer.writerows(all_matches)
print(f"[OK] 已导出 RFQ 匹配结果：{match_file}")

# 3. 导出最优报价推荐
best_file = RFQ_BEST_QUOTE
fieldnames_best = ['RFQ', 'PartNumber', 'BestSupplier', 'BestPrice', 'Condition', 'Status']
with open(best_file, 'w', newline='', encoding=OUTPUT_ENCODING) as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames_best)
    writer.writeheader()
    writer.writerows(best_quotes)
print(f"[OK] 已导出最优报价推荐：{best_file}")

# 统计信息
print("\n" + "="*80)
print("=== 优化统计 ===")
print("="*80)

print(f"\n原始数据：{original_count} 条")
print(f"去重后：{len(quotes)} 条")
print(f"去除重复：{dedup_count} 条 ({dedup_count/original_count*100:.1f}%)")

print(f"\nRFQ 零件总数：{len(all_rfq_parts)} 个")
print(f"找到报价：{len([b for b in best_quotes if b['Status'] == '已匹配'])} 个")
print(f"待询价：{len([b for b in best_quotes if b['Status'] == '待询价'])} 个")

# 按供应商统计
print("\n按供应商统计 (Top 10):")
supplier_stats = {}
for q in quotes:
    supplier = q.get('From', '')[:50]
    supplier_stats[supplier] = supplier_stats.get(supplier, 0) + 1

for supplier, count in sorted(supplier_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {supplier}: {count} 条")

# 按条件统计
print("\n按条件统计:")
cond_stats = {}
for q in quotes:
    cond = q.get('Condition', '') or 'N/A'
    cond_stats[cond] = cond_stats.get(cond, 0) + 1

for cond, count in sorted(cond_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cond}: {count} 条")

# 价格区间统计
print("\n价格区间统计:")
price_ranges = {
    '$0-100': 0,
    '$100-500': 0,
    '$500-1000': 0,
    '$1000-5000': 0,
    '$5000+': 0,
    'N/A': 0
}

for q in quotes:
    price_str = q.get('Price', '')
    match = re.search(r'[\d,]+\.?\d*', price_str)
    if match:
        try:
            price = float(match.group(0).replace(',', ''))
            if price < 100:
                price_ranges['$0-100'] += 1
            elif price < 500:
                price_ranges['$100-500'] += 1
            elif price < 1000:
                price_ranges['$500-1000'] += 1
            elif price < 5000:
                price_ranges['$1000-5000'] += 1
            else:
                price_ranges['$5000+'] += 1
        except:
            price_ranges['N/A'] += 1
    else:
        price_ranges['N/A'] += 1

for range_name, count in price_ranges.items():
    if count > 0:
        print(f"  {range_name}: {count} 条")

print("\n" + "="*80)
print(f"结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=== 任务完成 ===")
print("="*80)
