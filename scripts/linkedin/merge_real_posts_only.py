#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并所有真实采集的 LinkedIn 数据
只包含 3 月 5 日和 3 月 6 日的真实采集数据
"""

import csv
import json
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
MASTER_FILE = OUTPUT_DIR / "LinkedIn_Business_Posts_Master_Table_CLEAN.csv"

# 真实数据文件
REAL_DATA_FILES = [
    "LinkedIn_Business_Posts_真实采集_20260305_1653.csv",
    "LinkedIn_Business_Posts_真实采集_20260305_1915.csv",
    "LinkedIn_Business_Posts_真实采集_20260306_135948.csv",
    "LinkedIn_Business_Posts_真实采集_20260306_144941.csv",
]

def load_csv(filepath):
    """加载 CSV 文件"""
    posts = []
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                posts.append(row)
        print(f"  [OK] {filepath.name}: {len(posts)} 条")
    except Exception as e:
        print(f"  [ERR] {filepath.name}: {e}")
    return posts

def main():
    print("=" * 60)
    print("合并真实 LinkedIn 数据")
    print("=" * 60)
    
    all_posts = []
    
    for filename in REAL_DATA_FILES:
        filepath = OUTPUT_DIR / filename
        if filepath.exists():
            posts = load_csv(filepath)
            all_posts.extend(posts)
        else:
            print(f"  [WARN] 未找到：{filename}")
    
    # 去重（基于 post_id）
    seen_ids = set()
    unique_posts = []
    for post in all_posts:
        post_id = post.get('post_id', '')
        if post_id and post_id not in seen_ids:
            seen_ids.add(post_id)
            unique_posts.append(post)
    
    print(f"\n[STATS] 去重后总计：{len(unique_posts)} 条")
    
    # 保存
    if unique_posts:
        # 使用第一个文件的字段
        fieldnames = list(unique_posts[0].keys())
        
        with open(MASTER_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unique_posts)
        
        print(f"\n[OK] 已保存：{MASTER_FILE.name}")
        
        # 统计
        business_types = {}
        for post in unique_posts:
            bt = post.get('business_type', 'Unknown')
            business_types[bt] = business_types.get(bt, 0) + 1
        
        print("\n[STATS] 业务类型分布:")
        for bt, count in sorted(business_types.items(), key=lambda x: -x[1]):
            print(f"  {bt}: {count} 条")
        
        # 质量验证
        unknown_count = sum(1 for p in unique_posts if p.get('author_name') == 'Unknown')
        ui_element_count = sum(1 for p in unique_posts if 'ref=e' in p.get('content', ''))
        
        print(f"\n[QUALITY] 数据质量:")
        print(f"  author_name='Unknown': {unknown_count} 条 ({unknown_count/len(unique_posts)*100:.1f}%)")
        print(f"  包含 UI 元素 (ref=e): {ui_element_count} 条 ({ui_element_count/len(unique_posts)*100:.1f}%)")
    else:
        print("\n❌ 没有数据可保存")

if __name__ == "__main__":
    main()
