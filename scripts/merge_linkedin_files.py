#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并所有 LinkedIn 采集文件到 Master Table
"""

import os
import csv
from pathlib import Path
from datetime import datetime

# 目录配置
DATA_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
MASTER_FILE = DATA_DIR / "LinkedIn_Business_Posts_Master_Table.csv"

def find_linkedin_csv_files():
    """找出所有包含 LinkedIn 数据的 CSV 文件"""
    csv_files = []
    
    for f in DATA_DIR.glob("*.csv"):
        if f.name == MASTER_FILE.name:
            continue  # 跳过 Master Table 本身
        
        # 跳过太小或明显无关的文件
        if f.stat().st_size < 500:
            continue
        
        # 检查文件名关键词
        keywords = ['linkedin', 'LinkedIn', 'Collection', 'Posts', 'business', 'feed']
        if any(kw.lower() in f.name.lower() for kw in keywords):
            csv_files.append(f)
    
    return csv_files

def analyze_csv_file(file_path):
    """分析 CSV 文件结构"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return None
            
            rows = list(reader)
            return {
                'file': file_path,
                'name': file_path.name,
                'header': header,
                'rows': len(rows),
                'size_kb': round(file_path.stat().st_size / 1024, 1)
            }
    except Exception as e:
        print(f"[ERR] {file_path.name}: {e}")
        return None

def extract_posts_from_file(file_path, header):
    """从 CSV 文件提取帖子记录"""
    posts = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # 提取关键字段（根据不同文件格式）
                post = {
                    'author': row.get('author_name') or row.get('author') or row.get('发布者') or 'Unknown',
                    'company': row.get('company') or row.get('公司') or '',
                    'content': row.get('content') or row.get('内容') or row.get('content_summary') or '',
                    'pn': row.get('part_numbers') or row.get('PN') or row.get('零件号') or '',
                    'business_type': row.get('business_type') or row.get('业务类型') or '航材信息',
                    'contact': row.get('contact_info') or row.get('联系方式') or '',
                    'source_url': row.get('source_url') or row.get('链接') or '',
                    'timestamp': row.get('timestamp') or row.get('采集时间') or '',
                }
                
                # 只保留有业务价值的记录
                if post['content'] and len(post['content']) > 20:
                    posts.append(post)
    
    except Exception as e:
        print(f"[ERR] 读取 {file_path.name}: {e}")
    
    return posts

def merge_to_master(posts, master_file):
    """追加记录到 Master Table"""
    if not posts:
        return 0
    
    # 读取现有记录避免重复
    existing_ids = set()
    existing_content_hashes = set()
    
    if master_file.exists():
        try:
            with open(master_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'post_id' in row:
                        existing_ids.add(row['post_id'])
                    # 用内容 hash 去重
                    content = row.get('content', '')[:100] or row.get('content_summary', '')[:100]
                    if content:
                        existing_content_hashes.add(hash(content))
        except Exception as e:
            print(f"[WARN] 读取 Master Table: {e}")
    
    # 追加新记录
    appended = 0
    timestamp_base = datetime.now().strftime('%Y%m%d')
    
    # Master Table 字段列表
    master_fields = [
        'post_id', 'timestamp', 'author_name', 'company', 'position', 'content',
        'business_type', 'business_value_score', 'urgency', 'has_contact', 'contact_info',
        'post_time', 'reactions', 'comments', 'reposts', 'has_image', 'image_content',
        'source_url', 'source_file', 'merge_timestamp', 'batch_id', 'collected_at',
        'author_url', 'posted_time', 'content_summary', 'is_repost', 'original_author',
        'category', 'aircraft_type', 'author_title', 'content_type', 'tags', 'author',
        'likes', 'summary', 'part_numbers', 'condition', 'quantity', 'certification',
        'part_number', 'status', 'notes'
    ]
    
    with open(master_file, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=master_fields, extrasaction='ignore')
        
        for i, post in enumerate(posts, start=1):
            # 生成唯一 ID
            post_id = f"linkedin_merge_{timestamp_base}_{i:03d}"
            
            # 检查重复
            content_hash = hash(post.get('content', '')[:100])
            if post_id in existing_ids or content_hash in existing_content_hashes:
                continue
            
            # 构建完整记录
            full_record = {
                'post_id': post_id,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'author_name': post.get('author', 'Unknown'),
                'company': post.get('company', ''),
                'position': '',
                'content': post.get('content', ''),
                'business_type': post.get('business_type', '航材信息'),
                'business_value_score': '7.0',
                'urgency': '中',
                'has_contact': 'True' if post.get('contact') else 'False',
                'contact_info': post.get('contact', ''),
                'source_url': post.get('source_url', ''),
                'source_file': post.get('source_file', ''),
                'merge_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'collected_at': post.get('timestamp', ''),
                'content_summary': post.get('content', '')[:100],
                'part_numbers': post.get('pn', ''),
                'status': 'active',
                'notes': f"Merged from historical collection"
            }
            
            writer.writerow(full_record)
            appended += 1
    
    return appended

def main():
    print("=" * 60)
    print("LinkedIn 数据文件合并工具")
    print("=" * 60)
    
    # 1. 找出所有 CSV 文件
    print("\n[1] 搜索 LinkedIn 数据文件...")
    csv_files = find_linkedin_csv_files()
    
    if not csv_files:
        print("[WARN] 未找到任何数据文件")
        return
    
    print(f"[OK] 找到 {len(csv_files)} 个文件")
    
    # 2. 分析每个文件
    print("\n[2] 分析文件结构...")
    file_info = []
    for f in csv_files:
        info = analyze_csv_file(f)
        if info and info['rows'] > 0:
            file_info.append(info)
            print(f"  - {info['name']}: {info['rows']} 行, {info['size_kb']} KB")
    
    # 3. 提取并合并记录
    print("\n[3] 提取帖子记录...")
    all_posts = []
    
    for info in file_info:
        posts = extract_posts_from_file(info['file'], info['header'])
        print(f"  - {info['name']}: 提取 {len(posts)} 条")
        all_posts.extend(posts)
    
    print(f"[OK] 总计提取 {len(all_posts)} 条记录")
    
    # 4. 合并到 Master Table
    print("\n[4] 合并到 Master Table...")
    appended = merge_to_master(all_posts, MASTER_FILE)
    
    print(f"[OK] 成功追加 {appended} 条记录")
    
    # 5. 统计最终结果
    print("\n[5] 最终统计...")
    if MASTER_FILE.exists():
        with open(MASTER_FILE, 'r', encoding='utf-8') as f:
            total = sum(1 for _ in f) - 1  # 减去表头
        print(f"[OK] Master Table 当前总记录: {total} 条")
    
    print("\n" + "=" * 60)
    print("合并完成")
    print("=" * 60)

if __name__ == "__main__":
    main()