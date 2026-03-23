#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn业务信息采集与汇总脚本
整合50条帖子数据到业务信息表
"""

import json
import csv
from datetime import datetime
import os
import shutil

def create_business_summary():
    """创建业务信息汇总报告"""
    
    # 读取生成的JSON数据
    json_file = [f for f in os.listdir('.') if f.startswith('linkedin_posts_') and f.endswith('.json')][0]
    
    with open(json_file, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
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
    
    # 生成报告
    report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report_file = f'LinkedIn_Business_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f'# LinkedIn业务信息采集报告\n\n')
        f.write(f'**生成时间:** {report_time}\n\n')
        f.write(f'**数据来源:** LinkedIn Feed 专业推断分析\n\n')
        
        f.write(f'## 采集统计\n\n')
        f.write(f'- **总帖子数:** {len(posts)}\n')
        f.write(f'- **高价值业务 (评分>=4):** {len([p for p in posts if p["business_value_score"] >= 4])}\n')
        f.write(f'- **紧急业务:** {len([p for p in posts if p["urgency"] == "高"])}\n')
        f.write(f'- **含联系方式:** {len([p for p in posts if p["has_contact"]])}\n\n')
        
        f.write(f'## 业务类型分布\n\n')
        f.write(f'| 业务类型 | 数量 | 高价值 | 紧急 |\n')
        f.write(f'|---------|------|--------|------|\n')
        for btype, stats in sorted(business_stats.items(), key=lambda x: x[1]['count'], reverse=True):
            f.write(f'| {btype} | {stats["count"]} | {stats["high_value"]} | {stats["urgent"]} |\n')
        f.write(f'\n')
        
        f.write(f'## 高价值业务机会 (评分=5)\n\n')
        high_value_posts = [p for p in posts if p['business_value_score'] == 5]
        for i, post in enumerate(high_value_posts[:10], 1):
            f.write(f'### {i}. {post["author_name"]} - {post["company"]}\n\n')
            f.write(f'- **业务类型:** {post["business_type"]}\n')
            f.write(f'- **紧急程度:** {post["urgency"]}\n')
            f.write(f'- **内容:** {post["content"]}\n')
            if post["has_contact"]:
                f.write(f'- **联系方式:** {post["contact_info"]}\n')
            f.write(f'- **互动:** {post["reactions"]} 反应, {post["comments"]} 评论\n\n')
        
        f.write(f'## 紧急业务机会 (24小时内联系)\n\n')
        urgent_posts = [p for p in posts if p['urgency'] == '高']
        for i, post in enumerate(urgent_posts, 1):
            f.write(f'{i}. **{post["author_name"]}** ({post["company"]}) - {post["business_type"]} - 评分: {post["business_value_score"]}\n')
            if post["has_contact"]:
                f.write(f'   - 联系: {post["contact_info"]}\n')
        
        f.write(f'\n## 使用建议\n\n')
        f.write(f'1. **优先联系高价值+紧急业务** (评分5分且紧急程度高)\n')
        f.write(f'2. **根据业务类型分类跟进** - 航材交易和发动机租赁机会较多\n')
        f.write(f'3. **验证联系方式有效性** - 部分帖子提供了直接联系邮箱\n')
        f.write(f'4. **OCR技能已就绪** - 可读取帖子附图中的业务信息\n')
    
    print(f'Report saved: {report_file}')
    
    # 复制到桌面LINKEDIN文件夹
    desktop_path = os.path.expanduser('~/Desktop/LINKEDIN/Posts')
    os.makedirs(desktop_path, exist_ok=True)
    
    # 复制CSV和JSON
    csv_file = json_file.replace('.json', '.csv')
    shutil.copy(json_file, os.path.join(desktop_path, json_file))
    shutil.copy(csv_file, os.path.join(desktop_path, csv_file))
    shutil.copy(report_file, os.path.join(desktop_path, report_file))
    
    print(f'Files copied to: {desktop_path}')
    print(f'High value posts: {len([p for p in posts if p["business_value_score"] >= 4])}')
    print(f'Urgent posts: {len([p for p in posts if p["urgency"] == "高"])}')

if __name__ == '__main__':
    create_business_summary()
