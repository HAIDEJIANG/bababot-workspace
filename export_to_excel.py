#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import pandas as pd
from datetime import datetime
import os
import shutil

# 读取数据
json_file = 'linkedin_posts_20260224_173020.json'
with open(json_file, 'r', encoding='utf-8') as f:
    posts = json.load(f)

print('Loaded', len(posts), 'posts')

# 创建DataFrame
df = pd.DataFrame(posts)

# 选择需要的列
df_export = pd.DataFrame({
    '姓名': df['author_name'],
    '公司': df['company'],
    '业务类型': df['business_type'],
    '帖子内容': df['content'],
    '业务价值评分': df['business_value_score'],
    '紧急程度': df['urgency'],
    '联系方式': df['contact_info'],
    '互动数': df['reactions'],
    '评论数': df['comments'],
    '采集时间': df['timestamp'],
    '更新日期': datetime.now().strftime('%Y-%m-%d')
})

# 保存Excel
output_file = 'LinkedIn_Posts_Updated_' + datetime.now().strftime('%Y%m%d') + '.xlsx'
df_export.to_excel(output_file, sheet_name='Posts', index=False)

print('Excel saved:', output_file)

# 复制到桌面
desktop = os.path.expanduser('~/Desktop/LINKEDIN/Posts')
os.makedirs(desktop, exist_ok=True)
shutil.copy(output_file, desktop)
shutil.copy(json_file, desktop)

print('Files copied to:', desktop)
print('High value posts:', len(df[df['business_value_score'] >= 4]))
print('Urgent posts:', len(df[df['urgency'] == '高']))
