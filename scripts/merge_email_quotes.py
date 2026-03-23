# -*- coding: utf-8 -*-
"""合并邮箱报价数据到总表"""

import csv

# 读取新数据
new_quotes = []
with open(r'C:\Users\Haide\Desktop\OPENCLAW\邮箱报价信息汇总_2026-03-16_至今.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        new_quotes.append(row)

# 读取现有数据
existing_quotes = []
try:
    with open(r'C:\Users\Haide\Desktop\OPENCLAW\航材供应商报价汇总_2026-03-01_至今.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_quotes.append(row)
except:
    pass

print(f'New quotes: {len(new_quotes)}')
print(f'Existing quotes: {len(existing_quotes)}')

# 合并数据 (去重)
existing_subjects = set(q['Subject'] for q in existing_quotes)
merged = existing_quotes.copy()

for quote in new_quotes:
    if quote['Subject'] not in existing_subjects:
        # 转换格式
        new_row = {
            'Date': quote['Date'],
            'From': quote['From'],
            'Subject': quote['Subject'],
            'PartNumber': quote['PartNumbers'].split(';')[0] if quote['PartNumbers'] else '',
            'Description': quote['Body_Summary'][:200] if quote['Body_Summary'] else '',
            'Price': quote['Prices'].split(';')[0] if quote['Prices'] else '',
            'Condition': quote['Condition'],
            'Qty': '',
            'Source': 'Email',
            'Notes': '',
        }
        merged.append(new_row)
        print(f'  + Added: {quote["Subject"][:50]}...')

# 保存合并后的数据
fieldnames = ['Date', 'From', 'Subject', 'PartNumber', 'Description', 'Price', 'Condition', 'Qty', 'Source', 'Notes']
with open(r'C:\Users\Haide\Desktop\OPENCLAW\航材供应商报价汇总_2026-03-01_至今.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(merged)

print(f'\nMerged total: {len(merged)} records')
print(f'New added: {len(merged) - len(existing_quotes)} records')
print(f'Output: C:/Users/Haide/Desktop/OPENCLAW/航材供应商报价汇总_2026-03-01_至今.csv')
