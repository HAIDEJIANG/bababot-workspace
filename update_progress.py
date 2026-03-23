#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import glob
from datetime import datetime

workspace = r'C:\Users\Haide\.openclaw\workspace'
all_posts = []

# 加载所有历史帖子
json_files = glob.glob(os.path.join(workspace, 'linkedin_real_posts*.json'))
for json_file in json_files:
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
            if isinstance(posts, list):
                all_posts.extend(posts)
    except:
        pass

print(f'已加载历史帖子: {len(all_posts)} 条')

# 新采集的帖子
new_posts = [
    {
        'post_id': 'linkedin_real_034',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'author_name': 'AerFin',
        'company': 'AerFin Limited',
        'content': 'Early aircraft retirements are not always a sign of weakness - in todays market, they can be a strategic choice. CEO Simon Goodson explains how mid-life teardowns are helping owners unlock value, support active fleets and navigate ongoing supply chain constraints.',
        'business_type': '飞机拆解-资产管理',
        'business_value_score': 4,
        'urgency': '中',
        'has_contact': False,
        'post_time': '6 hours ago',
        'reactions': 12
    },
    {
        'post_id': 'linkedin_real_035',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'author_name': 'LS Technics',
        'company': 'LS Technics',
        'content': 'Expanded Part-145 certificate with new capabilities for the Airbus family. First MRO in Poland with broad scope of approvals for the Airbus A220 and its engines. Certification includes line maintenance for Airbus A220 (BD-500) with PW1500G engines, as well as maintenance capability for PW1500G and PW1900G engines.',
        'business_type': 'MRO服务',
        'business_value_score': 4,
        'urgency': '中',
        'has_contact': False,
        'post_time': '4 hours ago',
        'reactions': 101
    }
]

# 去重并合并
existing_ids = {p['post_id'] for p in all_posts}
added_count = 0
for np in new_posts:
    if np['post_id'] not in existing_ids:
        all_posts.append(np)
        added_count += 1

print(f'新增帖子: {added_count} 条')

# 业务帖子筛选
business_keywords = ['purchase', 'buying', 'sale', 'selling', 'lease', 'leasing', 'mro', 'maintenance', 'repair', 'overhaul', 
                    'engine', 'parts', 'aircraft', 'landing gear', 'inventory', 'available', 'installation', 'trading', 
                    'teardown', '拆解', '资产管理']
exclude_keywords = ['hiring', 'job', 'career', 'news', 'conference', 'event', 'analysis', 'report']

business_posts = []
for p in all_posts:
    content = p.get('content', '').lower()
    btype = p.get('business_type', '').lower()
    
    is_exclude = any(k in content or k in btype for k in exclude_keywords)
    if is_exclude and p.get('business_value_score', 0) < 4:
        continue
    
    is_business = any(k in content or k in btype for k in business_keywords) or p.get('business_value_score', 0) >= 4
    if is_business:
        business_posts.append(p)

print()
print('='*60)
print('LinkedIn业务帖子采集进度')
print('='*60)
print(f'采集时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
print()
print(f'累计帖子: {len(all_posts)} 条')
print(f'业务帖子: {len(business_posts)} 条')
print()
print('目标: 100条业务帖子')
progress = len(business_posts)
print(f'当前进度: {progress}/100 ({progress}%)')
print(f'还需采集: {100 - progress} 条')
print()
print('业务类型分布:')
type_counts = {}
for p in business_posts:
    t = p.get('business_type', 'Unknown')
    type_counts[t] = type_counts.get(t, 0) + 1
for t, c in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f'  - {t}: {c}条')
print()
print(f'高价值帖子 (评分>=4): {len([p for p in business_posts if p.get("business_value_score", 0) >= 4])} 条')
print(f'含联系方式: {len([p for p in business_posts if p.get("has_contact")])} 条')
print('='*60)
