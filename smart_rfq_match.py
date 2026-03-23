# -*- coding: utf-8 -*-
"""
智能 RFQ 匹配脚本
使用模糊匹配和关键词匹配来找到 RFQ 零件的报价
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

# RFQ 零件号列表（包含描述信息）
RFQ_PARTS = {
    # RFQ20260313-01
    "1152466-250": "APU START CONVERTER UNIT",
    "129666-3": "PRECOOLER CONTR",
    "18-1738-12": "TRANSMITTER - FLAP POS",
    "1FA14012-8": "ACTUATOR",
    "2041217-0416": "WX RADAR",
    "2215628-3": "DIFFUSER ASSEMBLY",
    "2215629-1": "PLENUM ASSY, HEAT EXCH, RH",
    "2215629-2": "PLENUM ASSY, HEAT EXCH, RH",
    "2313M-347-4": "DRIVE ASSY-WINDSH.WIPER LH",
    "3214972-1": "VALVE",
    "35000-00-01": "CLOCK",
    "3522W000-001": "OXYGEN SENSOR",
    "4063-19972-01AA": "VALVE",
    "45-0351-1": "LANDING LIGHT",
    "57186-11": "PUMP, HYD, ELEC MOTOR DRIVEN",
    "606802-2": "BLWR, VACUUM",
    "622-5132-109": "R/T RADAR",
    "622-5135-802": "WXR SINGLE ANT PEDESTAL",
    "622-7998-013": "ELEC. DISPLAY UNIT",
    "622814-5": "CABIN TEMP CONTROL",
    "808556-1": "VALVE",
    "822-2532-100": "MULTI MODE RECEIVER",
    "901906": "DETECTOR",
    "902020-01": "FIRE DETECTOR ASSY",
    "BFS24": "BATTERY CHARGER",
    "DMN23-1C": "VHF NAV ANTENNA",
    "G6992-02": "TCAS CONTROL",
    "R15048": "ACTUATOR",
    "R5303M1": "ACTUATOR, ELECTRO-MECH LINEAR",
    "R5303M1-1": "ACTUATOR: DOOR",
    
    # RFQ20260305-01
    "10037-0770": "IND",
    "15800-029-3": "TOILET ASSEMBLY",
    "170089-02-01": "CDU MULTIFUNCTION FMS",
    "2040061-103": "SWITCH - NGS",
    "285W0024-1M": "ATTENDANT HANDSET",
    "312BS101-1": "DEDICATED BATTERY CHARGER",
    "3291828-1": "Ram Air Valve",
    "346A2801-5": "DRAIN AY",
    "473957-4": "FIRE EXT 800 CU IN DUAL",
    "5000-1-01A-2396": "RESTRAINT",
    "5A3307-701": "SLIDE ASSY., ESCAPE",
}


def normalize_for_match(text):
    """
    标准化文本用于匹配
    - 转大写
    - 去除空格和特殊字符
    - 统一分隔符
    """
    if not text:
        return ""
    text = text.upper()
    text = re.sub(r'[\s\-\_\.]', '', text)
    return text


def smart_match(quote_pn, rfq_pn, quote_desc, rfq_desc):
    """
    智能匹配逻辑
    1. 零件号精确匹配
    2. 零件号包含匹配
    3. 描述关键词匹配
    """
    # 标准化
    quote_pn_norm = normalize_for_match(quote_pn)
    rfq_pn_norm = normalize_for_match(rfq_pn)
    quote_desc_norm = normalize_for_match(quote_desc)
    rfq_desc_norm = normalize_for_match(rfq_desc)
    
    # 1. 零件号精确匹配
    if quote_pn_norm == rfq_pn_norm:
        return True, "精确匹配"
    
    # 2. 零件号包含匹配
    if rfq_pn_norm in quote_pn_norm or quote_pn_norm in rfq_pn_norm:
        return True, "包含匹配"
    
    # 3. 描述关键词匹配（提取 RFQ 描述的关键词）
    if rfq_desc:
        # 提取关键词（至少 3 个字符的单词）
        keywords = re.findall(r'[A-Z0-9]{3,}', rfq_desc_norm)
        for keyword in keywords:
            if keyword in quote_desc_norm or keyword in quote_pn_norm:
                return True, f"关键词匹配 ({keyword})"
    
    return False, ""


def get_best_quote(matches):
    """
    从多个报价中选择最优
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
print("=== 智能 RFQ 匹配脚本 ===")
print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"输入文件：{SUPPLIER_QUOTE_FILE}")
print(f"RFQ 零件数：{len(RFQ_PARTS)} 个")
print("="*80)

# 读取报价数据
print("\n[1/4] 读取报价数据...")
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

# 智能匹配
print("\n[2/4] 执行智能匹配...")

all_matches = []
matched_parts = set()

for rfq_pn, rfq_desc in RFQ_PARTS.items():
    for quote in quotes:
        quote_pn = quote.get('PartNumber', '')
        quote_desc = quote.get('Description', '')
        
        is_match, match_type = smart_match(quote_pn, rfq_pn, quote_desc, rfq_desc)
        
        if is_match:
            all_matches.append({
                'RFQ': 'RFQ20260313-01' if rfq_pn in RFQ_20260313_01 else 'RFQ20260305-01',
                'PartNumber': rfq_pn,
                'QuoteSupplier': quote.get('From', ''),
                'QuotePrice': quote.get('Price', ''),
                'QuoteCondition': quote.get('Condition', ''),
                'QuoteDate': quote.get('Date', ''),
                'QuoteSource': quote.get('Source', ''),
                'MatchedPN': quote_pn,
                'MatchType': match_type,
                'Description': rfq_desc
            })
            matched_parts.add(rfq_pn)

print(f"[OK] 找到 {len(all_matches)} 条匹配记录")
print(f"[OK] {len(matched_parts)}/{len(RFQ_PARTS)} 个零件找到报价")

# 生成最优报价推荐
print("\n[3/4] 生成最优报价推荐...")

best_quotes = []
for rfq_pn, rfq_desc in RFQ_PARTS.items():
    # 找到该零件的所有匹配
    part_matches = [m for m in all_matches if m.get('PartNumber') == rfq_pn]
    
    if part_matches:
        best = get_best_quote(part_matches)
        if best:
            best_quotes.append({
                'RFQ': best.get('RFQ', ''),
                'PartNumber': rfq_pn,
                'BestSupplier': best.get('QuoteSupplier', ''),
                'BestPrice': best.get('QuotePrice', ''),
                'Condition': best.get('QuoteCondition', ''),
                'Status': '已匹配' if best.get('QuotePrice', '') not in ['', 'N/A', '待报价'] else '待询价',
                'Description': rfq_desc
            })
    else:
        best_quotes.append({
            'RFQ': 'N/A',
            'PartNumber': rfq_pn,
            'BestSupplier': '待询价',
            'BestPrice': 'N/A',
            'Condition': 'N/A',
            'Status': '待询价',
            'Description': rfq_desc
        })

# 导出结果
print("\n[4/4] 导出结果...")

# 1. 导出匹配结果
match_file = RFQ_MATCH_RESULT
fieldnames_match = ['RFQ', 'PartNumber', 'QuoteSupplier', 'QuotePrice', 'QuoteCondition', 'QuoteDate', 'QuoteSource', 'MatchedPN', 'MatchType', 'Description']
with open(match_file, 'w', newline='', encoding=OUTPUT_ENCODING) as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames_match)
    writer.writeheader()
    writer.writerows(all_matches)
print(f"[OK] 已导出 RFQ 匹配结果：{match_file}")

# 2. 导出最优报价推荐
best_file = RFQ_BEST_QUOTE
fieldnames_best = ['RFQ', 'PartNumber', 'BestSupplier', 'BestPrice', 'Condition', 'Status', 'Description']
with open(best_file, 'w', newline='', encoding=OUTPUT_ENCODING) as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames_best)
    writer.writeheader()
    writer.writerows(best_quotes)
print(f"[OK] 已导出最优报价推荐：{best_file}")

# 统计信息
print("\n" + "="*80)
print("=== 匹配统计 ===")
print("="*80)

print(f"\nRFQ 零件总数：{len(RFQ_PARTS)} 个")
print(f"找到报价：{len(matched_parts)} 个 ({len(matched_parts)/len(RFQ_PARTS)*100:.1f}%)")
print(f"待询价：{len(RFQ_PARTS) - len(matched_parts)} 个")

print(f"\n匹配记录总数：{len(all_matches)} 条")

# 按匹配类型统计
print("\n按匹配类型统计:")
match_type_stats = {}
for m in all_matches:
    match_type = m.get('MatchType', 'Unknown')
    match_type_stats[match_type] = match_type_stats.get(match_type, 0) + 1

for match_type, count in sorted(match_type_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"  {match_type}: {count} 条")

# 按供应商统计（仅匹配到的）
print("\n按供应商统计 (Top 10):")
supplier_stats = {}
for m in all_matches:
    supplier = m.get('QuoteSupplier', '')[:50]
    supplier_stats[supplier] = supplier_stats.get(supplier, 0) + 1

for supplier, count in sorted(supplier_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {supplier}: {count} 条")

# 显示待询价零件
print("\n" + "="*80)
print("=== 待询价零件清单 ===")
print("="*80)

pending_parts = [b for b in best_quotes if b['Status'] == '待询价']
if pending_parts:
    for i, p in enumerate(pending_parts, 1):
        print(f"{i:3}. {p['PartNumber']:<25} | {p['Description'][:40]}")
    print(f"\n共计 {len(pending_parts)} 个零件需要向供应商询价")
else:
    print("所有零件均已获得报价！")

print("\n" + "="*80)
print(f"结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=== 任务完成 ===")
print("="*80)
