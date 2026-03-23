# -*- coding: utf-8 -*-
"""
LinkedIn 航空业务帖子采集脚本
持续采集至少 30 分钟，保存真实帖子数据
"""

import json
import csv
import time
from datetime import datetime
from pathlib import Path

# 输出目录
OUTPUT_DIR = Path.home() / "Desktop" / "real business post"
OUTPUT_DIR.mkdir(exist_ok=True)

# 采集的数据存储
collected_posts = []

def save_to_csv(posts, batch_name):
    """保存帖子到 CSV 文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = OUTPUT_DIR / f"LinkedIn_Real_Posts_{batch_name}_{timestamp}.csv"
    
    fieldnames = [
        'author_name', 'content', 'source_url', 'collected_at',
        'post_time', 'business_type', 'author_title', 'company',
        'reactions', 'comments', 'reposts', 'has_image', 'tags'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for post in posts:
            writer.writerow(post)
    
    print(f"✓ 已保存 {len(posts)} 条帖子到 {filename}")
    return filename

def save_to_json(posts, batch_name):
    """保存帖子到 JSON 文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = OUTPUT_DIR / f"LinkedIn_Real_Posts_{batch_name}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已保存 JSON 到 {filename}")
    return filename

def append_to_master(posts):
    """追加到主表"""
    master_file = OUTPUT_DIR / "LinkedIn_Business_Posts_Master_Table.csv"
    
    fieldnames = [
        'author_name', 'content', 'source_url', 'collected_at',
        'post_time', 'business_type', 'author_title', 'company',
        'reactions', 'comments', 'reposts', 'has_image', 'tags'
    ]
    
    file_exists = master_file.exists()
    
    with open(master_file, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for post in posts:
            writer.writerow(post)
    
    print(f"✓ 已追加 {len(posts)} 条帖子到主表")

def classify_business_type(content):
    """根据内容分类业务类型"""
    content_lower = content.lower()
    
    if any(kw in content_lower for kw in ['engine', 'cfm', 'leap', 'v2500', 'pw4000', 'ge90', 'gTF', 'fan cowl']):
        return '发动机相关'
    elif any(kw in content_lower for kw in ['landing gear', 'gear', 'NLG', 'MLG', '起落架']):
        return '起落架相关'
    elif any(kw in content_lower for kw in ['aircraft', 'A320', 'A321', 'A330', 'B737', 'B787', 'Boeing', 'Airbus', 'plane', 'fleet', 'MSN']):
        return '飞机整机'
    elif any(kw in content_lower for kw in ['MRO', 'maintenance', 'repair', 'overhaul', 'service', 'slot']):
        return 'MRO 服务'
    elif any(kw in content_lower for kw in ['part', 'component', 'spare', 'AOG', 'in stock', 'available', 'sale', '交易']):
        return '航材交易'
    elif any(kw in content_lower for kw in ['charter', 'lease', 'leasing', 'rental', '租赁', '包机']):
        return '租赁/包机'
    elif any(kw in content_lower for kw in ['hiring', 'job', 'career', 'position', 'recruiting']):
        return '行业招聘'
    else:
        return '航空行业其他'

def extract_post_data(post_element):
    """从帖子元素提取数据"""
    try:
        # 这里需要根据实际的浏览器自动化接口来提取数据
        # 由于我们使用 browser 工具，需要通过 snapshot 和 act 来提取
        pass
    except Exception as e:
        print(f"提取帖子数据失败：{e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("LinkedIn 航空业务帖子采集脚本")
    print("=" * 60)
    print(f"输出目录：{OUTPUT_DIR}")
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
