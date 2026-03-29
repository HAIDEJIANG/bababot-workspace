#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 数据采集进度检查工具 - 从实际数据文件读取准确进度
"""

import csv
from pathlib import Path
from datetime import datetime

# 数据目录
DATA_DIR = Path(r"C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326")

def count_unique_contacts(csv_file: Path, url_column: str = 0) -> int:
    """统计 CSV 文件中排重后的联系人数量"""
    if not csv_file.exists():
        return 0
    
    unique_urls = set()
    
    try:
        with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and len(row) > url_column:
                    # 提取 profile URL
                    url = row[url_column]
                    if url.startswith('https://www.linkedin.com/in/'):
                        unique_urls.add(url)
    except Exception as e:
        print(f"读取 {csv_file} 失败：{e}")
        return 0
    
    return len(unique_urls)

def count_posts(csv_file: Path) -> int:
    """统计发帖记录数（排重）"""
    if not csv_file.exists():
        return 0
    
    unique_posts = set()
    
    try:
        with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 按 contact_id + post_date 排重
                key = f"{row.get('contact_id', '')}_{row.get('post_date', '')}"
                if key:
                    unique_posts.add(key)
    except Exception as e:
        print(f"读取 {csv_file} 失败：{e}")
        return 0
    
    return len(unique_posts)

def count_leads(csv_file: Path) -> int:
    """统计高意向线索数"""
    if not csv_file.exists():
        return 0
    
    unique_leads = set()
    
    try:
        with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contact_id = row.get('contact_id', '')
                if contact_id:
                    unique_leads.add(contact_id)
    except Exception as e:
        print(f"读取 {csv_file} 失败：{e}")
        return 0
    
    return len(unique_leads)

def get_accurate_progress():
    """获取准确的采集进度"""
    print("="*60)
    print("LinkedIn 数据采集进度检查（从实际数据文件读取）")
    print("="*60)
    print(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查各个数据文件
    profile_count = count_unique_contacts(
        DATA_DIR / "contact_profiles_full.csv",
        url_column=0  # 第一列是 URL
    )
    
    posts_count = count_posts(
        DATA_DIR / "contact_posts_90days.csv"
    )
    
    leads_count = count_leads(
        DATA_DIR / "business_leads.csv"
    )
    
    # 总联系人
    TOTAL_CONTACTS = 3185
    
    # 输出结果
    print("[DATA] 准确数据（来自实际数据文件）：")
    print("-"*60)
    print(f"Total contacts:     {TOTAL_CONTACTS:,}")
    print(f"Collected profiles: {profile_count:,}")
    print(f"Post records:       {posts_count:,}")
    print(f"High-value leads:   {leads_count:,}")
    print()
    print("[PROGRESS] 进度统计：")
    print("-"*60)
    print(f"Progress:     {profile_count/TOTAL_CONTACTS*100:.2f}% ({profile_count:,}/{TOTAL_CONTACTS:,})")
    print(f"Remaining:    {TOTAL_CONTACTS - profile_count:,}")
    print()
    print("[NOTE] 注意：")
    print("-"*60)
    print("- Data from actual CSV files (most accurate)")
    print("- progress.json counter may be inaccurate")
    print("="*60)
    
    return {
        'total_contacts': TOTAL_CONTACTS,
        'profile_count': profile_count,
        'posts_count': posts_count,
        'leads_count': leads_count,
        'progress_percent': profile_count/TOTAL_CONTACTS*100,
        'remaining': TOTAL_CONTACTS - profile_count,
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    get_accurate_progress()
