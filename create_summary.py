#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from datetime import datetime

json_file = 'linkedin_posts_20260224_173020.json'

with open(json_file, 'r', encoding='utf-8') as f:
    posts = json.load(f)

print(f'Loaded {len(posts)} posts')

# 业务统计
business_stats = {}
for post in posts:
    btype = post['business_type']
    if btype not in business_stats:
        business_stats[btype] = {'count': 0, 'high_value': 0, 'urgent': 0}
    business_stats[btype]['count'] += 1
    if post['business_value_score'] >= 4:
        business_stats[btype]['high_value'] += 1
    if post['urgency'] == '高':
        business_stats[btype]['urgent'] += 1

print('Business type stats:')
for btype, stats in sorted(business_stats.items(), key=lambda x: x[1]['count'], reverse=True):
    print(f"{btype}: {stats['count']} posts, {stats['high_value']} high value, {stats['urgent']} urgent")

# 生成报告
report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
report_file = f'LinkedIn_Business_Report_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.md'

with open(report_file, 'w', encoding='utf-8') as f:
    f.write(f'# LinkedIn Business Information Collection Report\n\n')
    f.write(f'**Generated:** {report_time}\n\n')
    f.write(f'**Total Posts:** {len(posts)}\n')
    f.write(f'**High Value (Score>=4):** {len([p for p in posts if p[\"business_value_score\"] >= 4])}\n')
    f.write(f'**Urgent:** {len([p for p in posts if p[\"urgency\"] == \"高\"])}\n\n')
    
    f.write('## High Value Opportunities (Score=5)\n\n')
    for i, post in enumerate([p for p in posts if p['business_value_score'] == 5][:10], 1):
        f.write(f"{i}. **{post['author_name']}** ({post['company']}) - {post['business_type']}\n")
        f.write(f"   Content: {post['content']}\n")
        if post['has_contact']:
            f.write(f"   Contact: {post['contact_info']}\n")
        f.write(f"\n")

print(f'Report saved: {report_file}')
print(f'High value posts: {len([p for p in posts if p[\"business_value_score\"] >= 4])}')
print(f'Urgent posts: {len([p for p in posts if p[\"urgency\"] == \"高\"])}')
