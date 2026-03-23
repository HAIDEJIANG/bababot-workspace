#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合所有LinkedIn业务帖子到"real business post"文件夹
过滤掉行业新闻、招聘信息等非直接业务内容
"""

import json
import csv
import pandas as pd
from datetime import datetime
import os
import shutil
import glob

# 定义业务相关关键词
BUSINESS_KEYWORDS = [
    '采购', 'purchase', 'buying', '求购', 'looking for',
    '销售', 'sale', 'selling', 'available', 'forsale',
    '租赁', 'lease', 'leasing', '出租',
    '维修', 'MRO', 'maintenance', 'repair', 'overhaul',
    '发动机', 'engine', 'CFM', 'PW', 'LEAP', 'GE',
    '航材', 'parts', 'component', 'inventory',
    '飞机', 'aircraft', 'A320', 'B737', 'A330', 'B777',
    '起落架', 'landing gear',
    'APU', '起落架', 'avionics', '电子设备',
    '机库', 'hangar', 'tool', '设备', 'stand'
]

# 排除的关键词（非直接业务）
EXCLUDE_KEYWORDS = [
    'hiring', '招聘', 'job', '职位', 'career',
    'news', '新闻', 'report', '报道',
    'conference', '会议', 'event', '活动',
    'analysis', '分析', 'market', '市场分析',
    ' sentenced ', ' prison ', ' court '  # 法律新闻
]

def is_business_post(post):
    """判断是否为业务相关帖子"""
    content = post.get('content', '').lower()
    business_type = post.get('business_type', '').lower()
    
    # 检查是否为排除类型
    for keyword in EXCLUDE_KEYWORDS:
        if keyword.lower() in content or keyword.lower() in business_type:
            return False
    
    # 检查是否包含业务关键词
    for keyword in BUSINESS_KEYWORDS:
        if keyword.lower() in content or keyword.lower() in business_type:
            return True
    
    # 默认包含评分>=4的帖子
    if post.get('business_value_score', 0) >= 4:
        return True
    
    return False

def load_all_posts():
    """加载所有批次的JSON文件"""
    all_posts = []
    workspace = r'C:\Users\Haide\.openclaw\workspace'
    
    # 查找所有JSON文件
    json_files = glob.glob(os.path.join(workspace, 'linkedin_real_posts*.json'))
    
    print(f"Found {len(json_files)} JSON files")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                posts = json.load(f)
                if isinstance(posts, list):
                    all_posts.extend(posts)
                    print(f"  Loaded {len(posts)} posts from {os.path.basename(json_file)}")
        except Exception as e:
            print(f"  Error loading {json_file}: {e}")
    
    return all_posts

def main():
    # 创建目标文件夹
    desktop = os.path.expanduser('~/Desktop')
    target_folder = os.path.join(desktop, 'real business post')
    os.makedirs(target_folder, exist_ok=True)
    
    print("="*70)
    print("LinkedIn业务帖子整合工具")
    print("="*70)
    print()
    
    # 加载所有帖子
    print("Step 1: 加载所有采集的帖子...")
    all_posts = load_all_posts()
    print(f"总计加载: {len(all_posts)} 条帖子")
    print()
    
    # 过滤业务帖子
    print("Step 2: 筛选业务相关帖子...")
    business_posts = [p for p in all_posts if is_business_post(p)]
    non_business_posts = [p for p in all_posts if not is_business_post(p)]
    
    print(f"业务相关帖子: {len(business_posts)} 条")
    print(f"非业务帖子: {len(non_business_posts)} 条 (已过滤)")
    print()
    
    # 按评分排序
    business_posts.sort(key=lambda x: x.get('business_value_score', 0), reverse=True)
    
    # 显示过滤掉的帖子类型
    print("已过滤的非业务类型:")
    filtered_types = {}
    for p in non_business_posts:
        btype = p.get('business_type', 'Unknown')
        filtered_types[btype] = filtered_types.get(btype, 0) + 1
    for btype, count in sorted(filtered_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {btype}: {count} 条")
    print()
    
    # 保存整合后的业务帖子
    print("Step 3: 保存整合文件...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # JSON
    json_file = os.path.join(target_folder, f'LinkedIn_Business_Posts_ALL_{timestamp}.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(business_posts, f, ensure_ascii=False, indent=2)
    
    # CSV
    csv_file = os.path.join(target_folder, f'LinkedIn_Business_Posts_ALL_{timestamp}.csv')
    if business_posts:
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=business_posts[0].keys())
            writer.writeheader()
            writer.writerows(business_posts)
    
    # Excel (多个工作表)
    excel_file = os.path.join(target_folder, f'LinkedIn_Business_Posts_ALL_{timestamp}.xlsx')
    df = pd.DataFrame(business_posts)
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # 全部业务帖子
        df.to_excel(writer, sheet_name='全部业务帖子', index=False)
        
        # 高价值业务 (评分>=4)
        high_value = df[df['business_value_score'] >= 4]
        high_value.to_excel(writer, sheet_name='高价值业务', index=False)
        
        # 紧急业务
        urgent = df[df['urgency'] == '高']
        urgent.to_excel(writer, sheet_name='紧急业务', index=False)
        
        # 按业务类型分组
        for btype in df['business_type'].unique():
            if pd.notna(btype):
                type_df = df[df['business_type'] == btype]
                # Excel工作表名称限制31字符，且不能包含特殊字符
                sheet_name = btype[:31].replace('/', '-').replace('\\', '-').replace(':', '-').replace('*', '').replace('?', '').replace('[', '').replace(']', '')
                if sheet_name:  # 确保不为空
                    type_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # 含联系方式的
        with_contact = df[df['has_contact'] == True]
        with_contact.to_excel(writer, sheet_name='含联系方式', index=False)
    
    print(f"JSON: {os.path.basename(json_file)}")
    print(f"CSV: {os.path.basename(csv_file)}")
    print(f"Excel: {os.path.basename(excel_file)}")
    print()
    
    # 生成汇总报告
    print("Step 4: 生成汇总报告...")
    report_file = os.path.join(target_folder, f'业务帖子汇总报告_{timestamp}.md')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('# LinkedIn业务帖子汇总报告\n\n')
        f.write(f'**生成时间:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        f.write(f'**数据来源:** LinkedIn Feed 实时采集\n\n')
        f.write(f'**帖子总数:** {len(business_posts)} 条业务相关帖子\n\n')
        
        f.write('## 统计概览\n\n')
        f.write(f'- **高价值业务 (评分=5):** {len([p for p in business_posts if p.get("business_value_score") == 5])} 条\n')
        f.write(f'- **中高价值业务 (评分=4):** {len([p for p in business_posts if p.get("business_value_score") == 4])} 条\n')
        f.write(f'- **含联系方式:** {len([p for p in business_posts if p.get("has_contact")])} 条\n')
        f.write(f'- **紧急程度-高:** {len([p for p in business_posts if p.get("urgency") == "高"])} 条\n\n')
        
        f.write('## 业务类型分布\n\n')
        type_counts = {}
        for p in business_posts:
            btype = p.get('business_type', 'Unknown')
            type_counts[btype] = type_counts.get(btype, 0) + 1
        for btype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f'- **{btype}:** {count} 条\n')
        f.write('\n')
        
        f.write('## 高价值业务机会 (评分=5)\n\n')
        for i, p in enumerate([p for p in business_posts if p.get('business_value_score') == 5], 1):
            f.write(f"### {i}. {p.get('author_name', 'N/A')}\n\n")
            f.write(f"- **公司:** {p.get('company', 'N/A')}\n")
            f.write(f"- **业务类型:** {p.get('business_type', 'N/A')}\n")
            f.write(f"- **内容:** {p.get('content', 'N/A')[:150]}...\n")
            if p.get('has_contact'):
                f.write(f"- **联系方式:** {p.get('contact_info', 'N/A')}\n")
            f.write(f"- **评分:** {p.get('business_value_score', 0)}/5\n\n")
        
        f.write('## 全部业务帖子清单\n\n')
        f.write('| 序号 | 作者 | 公司 | 业务类型 | 评分 | 联系方式 |\n')
        f.write('|------|------|------|---------|------|---------|\n')
        for i, p in enumerate(business_posts, 1):
            contact = '有' if p.get('has_contact') else '无'
            f.write(f"| {i} | {p.get('author_name', 'N/A')[:15]} | {p.get('company', 'N/A')[:20]} | {p.get('business_type', 'N/A')[:15]} | {p.get('business_value_score', 0)} | {contact} |\n")
    
    print(f"报告: {os.path.basename(report_file)}")
    print()
    
    # 复制原始文件到备份文件夹
    print("Step 5: 备份原始采集文件...")
    backup_folder = os.path.join(target_folder, '原始采集文件')
    os.makedirs(backup_folder, exist_ok=True)
    
    for json_file_src in glob.glob(os.path.join(r'C:\Users\Haide\.openclaw\workspace', 'linkedin_real_posts*.json')):
        shutil.copy2(json_file_src, backup_folder)
    
    print(f"已备份到: {backup_folder}")
    print()
    
    # 汇总
    print("="*70)
    print("整合完成!")
    print("="*70)
    print(f"目标文件夹: {target_folder}")
    print(f"业务帖子总数: {len(business_posts)} 条")
    print()
    print("文件清单:")
    for f in os.listdir(target_folder):
        if os.path.isfile(os.path.join(target_folder, f)):
            print(f"  - {f}")
    print()
    print("建议行动:")
    print(f"  1. 立即联系 {len([p for p in business_posts if p.get('urgency') == '高' and p.get('has_contact')])} 个紧急业务")
    print(f"  2. 优先跟进 {len([p for p in business_posts if p.get('business_value_score') >= 4 and p.get('has_contact')])} 个高价值且有联系方式的帖子")
    print("="*70)

if __name__ == '__main__':
    main()
