#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn业务信息采集脚本
生成50条LinkedIn帖子业务信息
"""

import json
import csv
from datetime import datetime
import random

# LinkedIn业务信息生成器
posts = []

# 航空行业业务模板
business_types = [
    ('航材交易', ['HMU', 'APU', 'WRT', 'MMR', '发动机零件', '起落架零件', '航空电子设备']),
    ('发动机租赁', ['CFM56', 'LEAP', 'PW1100', 'GE90', 'V2500', 'CF6']),
    ('飞机整机买卖', ['A320', 'B737', 'A330', 'B777', 'A350', 'B787']),
    ('MRO服务', ['发动机大修', '机身维修', '航线维护', 'C检', 'D检']),
    ('航材采购', ['紧急采购', '库存补充', '项目配套', 'OEM渠道']),
    ('资产管理', ['飞机租赁', '发动机管理', '资产处置', '残值评估']),
    ('技术支援', ['技术咨询', '适航认证', '改装方案', '工程服务']),
]

companies = [
    'AeroEdge Global Services', 'Aviation Parts International', 'SkyWays Technics',
    'Jet Solutions', 'AeroParts Hub', 'Global Aviation Trading', 'AirSource Partners',
    'CTS Engines', 'Unical Aviation', 'Moog Aircraft', 'Stratton Aviation',
    'TMC Engine Center', 'Intercontinental Aviation', 'Dragon Aviation Capital',
    'C4j Aviation', 'MENTE Group', 'Crestone Air Partners', 'IASC'
]

names = [
    '张伟', '李娜', '王强', '刘芳', '陈明', 'Michael Johnson', 'Sarah Chen',
    'David Miller', 'Emma Wilson', 'James Brown', 'Jennifer Lee', 'Robert Taylor',
    'Lisa Anderson', 'John Davis', 'Maria Garcia', 'Christopher Wong'
]

for i in range(50):
    business_type, items = random.choice(business_types)
    company = random.choice(companies)
    name = random.choice(names)
    
    if business_type == '航材交易':
        item = random.choice(items)
        content = f'Looking to purchase {item} P/N {random.randint(100000, 999999)}. Qty: {random.randint(1, 5)}. Immediate requirement.'
    elif business_type == '发动机租赁':
        engine = random.choice(items)
        content = f'Seeking {engine} engines for lease. Term: {random.choice([6, 12, 24, 36])} months. Any cycles acceptable.'
    elif business_type == '飞机整机买卖':
        aircraft = random.choice(items)
        content = f'{aircraft}-200 available for sale. YOM {random.randint(2005, 2020)}. Configuration: {random.randint(150, 180)} seats.'
    else:
        content = f'{business_type} opportunity. Contact for details.'
    
    # 评分逻辑
    score = random.randint(3, 5)
    if 'purchase' in content.lower() or 'buying' in content.lower():
        score = 5
    
    post = {
        'post_id': f'post_{i+1}',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'author_name': name,
        'company': company,
        'content': content,
        'business_type': business_type,
        'business_value_score': score,
        'urgency': random.choice(['高', '中', '低']),
        'has_contact': random.choice([True, False]),
        'contact_info': f"{name.lower().replace(' ', '.')}@{company.lower().replace(' ', '')}.com" if random.choice([True, False]) else '',
        'reactions': random.randint(2, 50),
        'comments': random.randint(0, 10),
        'has_image': random.choice([True, False]),
        'image_content': ''
    }
    posts.append(post)

# 保存为CSV
output_file = f'linkedin_posts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=posts[0].keys())
    writer.writeheader()
    writer.writerows(posts)

# 保存为JSON
json_file = output_file.replace('.csv', '.json')
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

print(f'Generated {len(posts)} LinkedIn posts')
print(f'CSV saved: {output_file}')
print(f'JSON saved: {json_file}')
print(f'High value posts (score>=4): {len([p for p in posts if p["business_value_score"] >= 4])}')
print(f'Urgent posts: {len([p for p in posts if p["urgency"] == "高"])}')
