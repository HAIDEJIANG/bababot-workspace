# -*- coding: utf-8 -*-
"""
LinkedIn 数据宽松修复脚本
尽量修复可修复的问题，保留更多数据
"""

import csv
import re
from datetime import datetime, timedelta
from pathlib import Path

# 输入输出文件
INPUT_FILE = r'C:\Users\Haide\Desktop\real business post\LinkedIn_Business_Posts_Master_Table.csv'
OUTPUT_FILE = r'C:\Users\Haide\Desktop\real business post\LinkedIn_Business_Posts_Master_Table_fixed.csv'

# 类别映射 (中文 -> 英文)
CATEGORY_MAP = {
    '航空器': 'aircraft',
    '发动机': 'engine',
    '起落架': 'landing_gear',
    '航材': 'parts',
    '直升机': 'helicopter',
    '维修': 'mro',
    '培训': 'training',
    '市场报告': 'other',
    '新闻': 'news',
    '其他': 'other',
}

# 业务类型映射
BUSINESS_TYPE_MAP = {
    'leasing': 'service',
    'lease': 'service',
    'rental': 'service',
    '出租': 'service',
    '租赁': 'service',
    '出售': 'supply',
    '供应': 'supply',
    '销售': 'supply',
    '求购': 'demand',
    '采购': 'demand',
    '需求': 'demand',
    '服务': 'service',
    '新闻': 'news',
    '资讯': 'news',
}

def normalize_category(value):
    """规范化类别"""
    if not value:
        return 'other'
    
    value = value.strip().lower()
    
    # 检查是否已经是有效值
    valid = ['engine', 'aircraft', 'landing_gear', 'mro', 'parts', 'helicopter', 'service', 'training', 'other', 'news']
    if value in valid:
        return value
    
    # 中文映射
    for cn, en in CATEGORY_MAP.items():
        if cn in value or value in cn:
            return en
    
    # 关键词推断
    if any(kw in value for kw in ['engine', '发动机', 'cfm', 'v2500', 'pw']):
        return 'engine'
    if any(kw in value for kw in ['aircraft', '飞机', 'boeing', 'airbus', 'b737', 'a320']):
        return 'aircraft'
    if any(kw in value for kw in ['landing', 'gear', '起落架']):
        return 'landing_gear'
    if any(kw in value for kw in ['mro', '维修', 'maintenance']):
        return 'mro'
    if any(kw in value for kw in ['parts', '件', '航材']):
        return 'parts'
    if any(kw in value for kw in ['helicopter', '直升机', 'bell', 'robinson']):
        return 'helicopter'
    
    return 'other'

def normalize_business_type(value):
    """规范化业务类型"""
    if not value:
        return 'other'
    
    value = value.strip().lower()
    
    # 检查是否已经是有效值
    valid = ['supply', 'demand', 'service', 'news', 'education', 'other']
    if value in valid:
        return value
    
    # 映射
    for key, mapped in BUSINESS_TYPE_MAP.items():
        if key in value:
            return mapped
    
    return 'other'

def normalize_business_value(value):
    """规范化业务价值"""
    if not value:
        return ''
    
    value = value.strip().lower()
    
    if value in ['high', 'medium', 'low']:
        return value
    
    # 关键词推断
    if any(kw in value for kw in ['urgent', '紧急', '高价值', 'high']):
        return 'high'
    if any(kw in value for kw in ['medium', '中']):
        return 'medium'
    if any(kw in value for kw in ['low', '低']):
        return 'low'
    
    return 'medium'  # 默认中等价值

def fix_post_date(value, collection_date=None):
    """修复日期格式"""
    if not value:
        return ''
    
    value = value.strip()
    
    # 已经是正确格式
    if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
        return value
    
    # 相对日期转换
    now = datetime.now()
    
    if 'd ago' in value.lower() or '天前' in value:
        # 提取天数
        match = re.search(r'(\d+)', value)
        if match:
            days = int(match.group(1))
            fixed_date = now - timedelta(days=days)
            return fixed_date.strftime('%Y-%m-%d')
    
    if 'w ago' in value.lower() or '周前' in value or '星期前' in value:
        match = re.search(r'(\d+)', value)
        if match:
            weeks = int(match.group(1))
            fixed_date = now - timedelta(weeks=weeks)
            return fixed_date.strftime('%Y-%m-%d')
    
    if 'h ago' in value.lower() or '小时前' in value:
        # 今天
        return now.strftime('%Y-%m-%d')
    
    # 如果有 collection_date，使用它
    if collection_date:
        return collection_date
    
    return now.strftime('%Y-%m-%d')  # 默认今天

def fix_source_url(value, post_id=''):
    """修复 source URL"""
    if not value:
        return ''
    
    value = value.strip()
    
    # 已经是有效 URL
    if value.startswith('http://') or value.startswith('https://') or value.startswith('www.'):
        return value
    
    # 格式如 "20260305_2045" - 无法修复，标记为 unknown
    if re.match(r'^\d{8}_\d+$', value):
        return f'https://www.linkedin.com/feed/unknown/{post_id}'
    
    # 其他情况
    return ''

def fix_row(row):
    """修复单行数据"""
    fixed = row.copy()
    
    # 修复 category
    if 'category' in fixed:
        fixed['category'] = normalize_category(fixed.get('category', ''))
    
    # 修复 business_type
    if 'business_type' in fixed:
        fixed['business_type'] = normalize_business_type(fixed.get('business_type', ''))
    
    # 修复 business_value
    if 'business_value' in fixed:
        fixed['business_value'] = normalize_business_value(fixed.get('business_value', ''))
    
    # 修复 post_date
    if 'post_date' in fixed:
        fixed['post_date'] = fix_post_date(fixed.get('post_date', ''), fixed.get('collection_date', ''))
    
    # 修复 source_url (尽量保留，不删除)
    if 'source_url' in fixed:
        original_url = fixed.get('source_url', '')
        fixed['source_url'] = fix_source_url(original_url, fixed.get('post_id', ''))
        # 如果修复后为空，保留原始值
        if not fixed['source_url'] and original_url:
            fixed['source_url'] = original_url
            if 'notes' in fixed:
                fixed['notes'] = (fixed.get('notes', '') + ' [source_url needs verification]').strip()
    
    return fixed

def main():
    print("="*60)
    print("LinkedIn Data Lenient Fixer")
    print("="*60)
    
    # 读取文件
    rows = []
    headers = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for row in reader:
            rows.append(row)
    
    print(f"\nInput file: {Path(INPUT_FILE).name}")
    print(f"Total rows: {len(rows)}")
    
    # 修复每行
    fixed_rows = []
    fix_counts = {
        'category': 0,
        'business_type': 0,
        'business_value': 0,
        'post_date': 0,
        'source_url': 0,
    }
    
    for row in rows:
        fixed = fix_row(row)
        
        # 统计修复次数
        if fixed.get('category') != row.get('category'):
            fix_counts['category'] += 1
        if fixed.get('business_type') != row.get('business_type'):
            fix_counts['business_type'] += 1
        if fixed.get('business_value') != row.get('business_value'):
            fix_counts['business_value'] += 1
        if fixed.get('post_date') != row.get('post_date'):
            fix_counts['post_date'] += 1
        if fixed.get('source_url') != row.get('source_url'):
            fix_counts['source_url'] += 1
        
        fixed_rows.append(fixed)
    
    # 保存修复后的数据
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(fixed_rows)
    
    print(f"\n{'='*60}")
    print("Fix Report")
    print('='*60)
    print(f"Rows processed: {len(fixed_rows)}")
    print(f"Rows retained: {len(fixed_rows)} (100%)")
    print(f"\nFixes applied:")
    print(f"  - category: {fix_counts['category']} rows")
    print(f"  - business_type: {fix_counts['business_type']} rows")
    print(f"  - business_value: {fix_counts['business_value']} rows")
    print(f"  - post_date: {fix_counts['post_date']} rows")
    print(f"  - source_url: {fix_counts['source_url']} rows")
    
    print(f"\nOutput file: {Path(OUTPUT_FILE).name}")
    print(f"Location: {Path(OUTPUT_FILE).parent}")
    
    print("\n" + "="*60)
    print("Fix complete - All data retained!")
    print("="*60)

if __name__ == '__main__':
    main()