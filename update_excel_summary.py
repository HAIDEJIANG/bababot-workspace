#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新LinkedIn主汇总表
将新生成的50条帖子数据整合到Excel
"""

import json
import pandas as pd
from datetime import datetime
import os

# 读取生成的JSON数据
json_file = 'linkedin_posts_20260224_173020.json'
with open(json_file, 'r', encoding='utf-8') as f:
    posts = json.load(f)

print(f'Loaded {len(posts)} posts from {json_file}')

# 转换为DataFrame
df_new = pd.DataFrame(posts)

# 重命名列以匹配主表格式
df_new = df_new.rename(columns={
    'author_name': '姓名',
    'company': '公司',
    'business_type': '业务类型',
    'content': '帖子内容',
    'business_value_score': '业务价值评分',
    'urgency': '紧急程度',
    'contact_info': '联系方式',
    'reactions': '互动数',
    'timestamp': '采集时间'
})

# 添加新列
df_new['数据来源'] = 'LinkedIn Feed'
df_new['更新日期'] = datetime.now().strftime('%Y-%m-%d')
df_new['联系优先级'] = df_new['业务价值评分'].apply(lambda x: '高' if x >= 4 else '中' if x >= 3 else '低')

# 读取现有主表（如果存在）
main_excel = os.path.expanduser('~/Desktop/LINKEDIN/整合结果/LinkedIn_分析结果_完整汇总.xlsx')

if os.path.exists(main_excel):
    df_existing = pd.read_excel(main_excel, sheet_name='实际帖子分析')
    print(f'Existing data: {len(df_existing)} rows')
    
    # 合并数据
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    print(f'Combined data: {len(df_combined)} rows')
else:
    df_combined = df_new
    print(f'Creating new file with {len(df_combined)} rows')

# 保存到Excel
output_file = 'LinkedIn_Posts_Updated_' + datetime.now().strftime('%Y%m%d') + '.xlsx'
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    df_combined.to_excel(writer, sheet_name='实际帖子分析', index=False)
    
    # 创建摘要sheet
    summary = df_combined.groupby('业务类型').agg({
        '业务价值评分': 'count',
        '联系优先级': lambda x: (x == '高').sum()
    }).rename(columns={'业务价值评分': '帖子数', '联系优先级': '高优先级数'})
    summary.to_excel(writer, sheet_name='业务类型统计')

print(f'Excel saved: {output_file}')

# 复制到桌面
import shutil
desktop_path = os.path.expanduser('~/Desktop/LINKEDIN/整合结果')
os.makedirs(desktop_path, exist_ok=True)
shutil.copy(output_file, desktop_path)
print(f'Copied to: {desktop_path}')

# 打印统计
print(f'\\n统计信息:')
print(f'- 总帖子数: {len(df_combined)}')
print(f'- 本次新增: {len(df_new)}')
print(f'- 高价值帖子: {len(df_combined[df_combined[\"业务价值评分\"] >= 4])}')
print(f'- 紧急帖子: {len(df_combined[df_combined[\"紧急程度\"] == \"高\"])}')
