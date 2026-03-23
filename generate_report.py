#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from datetime import datetime
import os

json_file = 'linkedin_posts_20260224_173020.json'

with open(json_file, 'r', encoding='utf-8') as f:
    posts = json.load(f)

print('Loaded', len(posts), 'posts')

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
    print(btype + ':', stats['count'], 'posts,', stats['high_value'], 'high value,', stats['urgent'], 'urgent')

# 高价值帖子
high_value = [p for p in posts if p['business_value_score'] >= 4]
urgent = [p for p in posts if p['urgency'] == '高']

print('High value posts:', len(high_value))
print('Urgent posts:', len(urgent))

# 生成简单报告
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
report_file = 'LinkedIn_Business_Report_' + timestamp + '.md'

with open(report_file, 'w', encoding='utf-8') as f:
    f.write('# LinkedIn Business Information Report\n\n')
    f.write('Generated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n\n')
    f.write('Total Posts: ' + str(len(posts)) + '\n')
    f.write('High Value: ' + str(len(high_value)) + '\n')
    f.write('Urgent: ' + str(len(urgent)) + '\n\n')
    
    f.write('## Top Opportunities\n\n')
    for i, post in enumerate([p for p in posts if p['business_value_score'] == 5][:10], 1):
        f.write(str(i) + '. **' + post['author_name'] + '** (' + post['company'] + ') - ' + post['business_type'] + '\n')
        f.write('   Content: ' + post['content'][:100] + '\n')
        if post['has_contact']:
            f.write('   Contact: ' + post['contact_info'] + '\n')
        f.write('\n')

print('Report saved:', report_file)

# 复制到桌面
desktop = os.path.expanduser('~/Desktop/LINKEDIN/Posts')
os.makedirs(desktop, exist_ok=True)

import shutil
shutil.copy(report_file, desktop)
shutil.copy(json_file, desktop)
csv_file = json_file.replace('.json', '.csv')
shutil.copy(csv_file, desktop)

print('Files copied to:', desktop)
