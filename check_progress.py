#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import glob
from datetime import datetime

workspace = r'C:\Users\Haide\.openclaw\workspace'
all_posts = []

# 加载所有已保存的JSON文件
json_files = glob.glob(os.path.join(workspace, 'linkedin_real_posts*.json'))
for json_file in json_files:
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
            if isinstance(posts, list):
                all_posts.extend(posts)
    except:
        pass

print(f'已加载 {len(all_posts)} 条历史帖子')

# 添加刚才新采集的2条帖子
new_posts = [
    {
        'post_id': 'linkedin_real_032',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'author_name': 'Avia Solutions Group',
        'company': 'AviaAM Leasing',
        'content': 'AviaAM Leasing has successfully completed the sale of a Boeing 737-400BDSF to ECT Aviation Group. The aircraft was delivered with a CFM56-3C1 engine installed on-wing.',
        'business_type': '飞机销售',
        'business_value_score': 4,
        'urgency': '中',
        'has_contact': False,
        'post_time': '3 hours ago',
        'reactions': 20
    },
    {
        'post_id': 'linkedin_real_033',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'author_name': 'VSE Aviation',
        'company': 'VSE Aviation Inc.',
        'content': 'CF6-80C2 HPT Stage 1 Nozzle Guide Vanes Installation. Our engine experts successfully completed a Stage 1 HPT NVG Installation on the core module of a CF6-80C2.',
        'business_type': '发动机维修',
        'business_value_score': 5,
        'urgency': '高',
        'has_contact': True,
        'contact_info': 'US: support-davie@vseaviation.com | EUR: supprt-ie@vseaviation.com',
        'post_time': '1 hour ago',
        'reactions': 6
    }
]

# 去重并合并
existing_ids = {p['post_id'] for p in all_posts}
for np in new_posts:
    if np['post_id'] not in existing_ids:
        all_posts.append(np)
        print(f'添加新帖子: {np[\"author_name\"]}')

# 业务帖子筛选
business_keywords = ['purchase', 'buying', 'sale', 'selling', 'lease', 'leasing', 'mro', 'maintenance', 'repair', 'overhaul', 'engine', 'parts', 'aircraft', 'landing gear', 'inventory', 'available', 'installation', 'trading']
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
print(f'采集时间: {datetime.now().strftime(\"%Y-%m-%d %H:%M\")}')
print()
print(f'历史帖子总数: {len(all_posts)} 条')
print(f'业务相关帖子: {len(business_posts)} 条')
print()
print('目标: 100条业务帖子')
progress = len(business_posts)
print(f'当前进度: {progress}/100 ({progress}%)')
print(f'还需采集: {100 - progress} 条')
print()
print('按业务类型分布:')
type_counts = {}
for p in business_posts:
    t = p.get('business_type', 'Unknown')
    type_counts[t] = type_counts.get(t, 0) + 1
for t, c in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
    print(f'  - {t}: {c}条')
print()
print(f'高价值帖子 (评分>=4): {len([p for p in business_posts if p.get(\"business_value_score\", 0) >= 4])} 条')
print(f'含联系方式: {len([p for p in business_posts if p.get(\"has_contact\")])} 条')
print('='*60)
