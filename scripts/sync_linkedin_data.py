#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 数据同步脚本
将各采集脚本的输出汇总到主表 (LinkedIn_Business_Posts_Master_Table.csv)

修复 (2026-03-29): 解决数据流断裂问题
"""

import csv
import json
from datetime import datetime
from pathlib import Path
import hashlib

# ==================== 配置 ====================

MASTER_TABLE = Path(r"C:\Users\Haide\Desktop\real business post\LinkedIn_Business_Posts_Master_Table.csv")
OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
LINKEDIN_ANALYSIS_DIR = Path(r"C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326")

# 数据源文件（按优先级排序）
# 修复 (2026-03-29): 使用通配符匹配动态文件名的采集输出
DATA_SOURCES = [
    # v8 增强版输出 (动态文件名，查找最新的)
    # 1 小时采集输出
    OUTPUT_DIR / "linkedin_1hour_final.csv",
    OUTPUT_DIR / "linkedin_1hour_collection.csv",
    # 批量采集输出
    OUTPUT_DIR / "linkedin_collection_batch.csv",
    # 联系人发帖
    LINKEDIN_ANALYSIS_DIR / "contact_posts_90days.csv",
]

def find_latest_file(pattern_prefix, output_dir):
    """查找指定前缀的最新文件"""
    import glob
    files = glob.glob(str(output_dir / f"{pattern_prefix}*.csv"))
    if not files:
        return None
    return max(files, key=lambda x: Path(x).stat().st_mtime)

# 主表字段
MASTER_FIELDS = [
    "post_id", "timestamp", "author_name", "company", "position", "content",
    "business_type", "business_value_score", "urgency", "has_contact", "contact_info",
    "post_time", "reactions", "comments", "reposts", "has_image", "image_content",
    "source_url", "source_file", "merge_timestamp", "batch_id", "collected_at",
    "author_url", "posted_time", "content_summary", "is_repost", "original_author",
    "category", "aircraft_type", "author_title", "content_type", "tags", "author",
    "likes", "summary", "part_numbers", "condition", "quantity", "certification",
    "part_number", "status", "notes"
]

def generate_post_id(content, author, timestamp):
    """生成唯一帖子 ID"""
    text = f"{content}_{author}_{timestamp}"
    return f"linkedin_sync_{hashlib.md5(text.encode()).hexdigest()[:12]}"

def load_existing_posts():
    """加载主表已有帖子（用于去重）"""
    existing = set()
    if MASTER_TABLE.exists():
        with open(MASTER_TABLE, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 使用 content + author 作为去重键
                content_hash = hashlib.md5(row.get('content', '')[:200].encode()).hexdigest()
                existing.add(content_hash)
    return existing

def normalize_post(row, source_file):
    """将不同格式的帖子标准化为主表格式"""
    timestamp = datetime.now().isoformat()
    
    # 尝试多种字段名映射
    content = (row.get('content') or row.get('text') or row.get('post_content') or 
               row.get('content_summary') or '')
    author = (row.get('author_name') or row.get('author') or row.get('contact_name') or 
              row.get('name') or 'Unknown')
    company = row.get('company', '')
    position = (row.get('position') or row.get('author_title') or row.get('title') or '')
    
    # 生成唯一 ID
    post_id = row.get('post_id') or generate_post_id(content, author, timestamp)
    
    # 业务类型判断
    business_type = row.get('business_type', '')
    if not business_type:
        content_lower = content.lower()
        if any(kw in content_lower for kw in ['for sale', 'available', 'stock']):
            business_type = '航材交易 - 出售'
        elif any(kw in content_lower for kw in ['want', 'need', 'looking for', 'rfq']):
            business_type = '航材交易 - 采购'
        else:
            business_type = '其他'
    
    # 价值评分
    value_score = row.get('business_value_score') or row.get('value_score') or '0'
    
    # 联系方式
    contact_info = row.get('contact_info') or row.get('contacts', '')
    has_contact = 'True' if contact_info else 'False'
    
    # 来源 URL
    source_url = (row.get('source_url') or row.get('post_url') or row.get('url') or 
                  'https://www.linkedin.com/feed')
    
    # 标准化记录
    normalized = {
        'post_id': post_id,
        'timestamp': timestamp,
        'author_name': author,
        'company': company,
        'position': position,
        'content': content[:2000] if content else '',
        'business_type': business_type,
        'business_value_score': value_score,
        'urgency': 'False',
        'has_contact': has_contact,
        'contact_info': str(contact_info)[:200],
        'post_time': row.get('post_time') or row.get('posted_time') or '',
        'reactions': row.get('reactions') or row.get('likes') or '0',
        'comments': row.get('comments', '0'),
        'reposts': row.get('reposts', '0'),
        'has_image': 'True' if row.get('has_image') or row.get('image_content') else 'False',
        'image_content': row.get('image_content', ''),
        'source_url': source_url,
        'source_file': str(source_file),
        'merge_timestamp': timestamp,
        'batch_id': f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'collected_at': timestamp,
        'author_url': row.get('author_url', ''),
        'posted_time': row.get('posted_time') or row.get('post_time', ''),
        'content_summary': content[:200] if content else '',
        'is_repost': 'False',
        'original_author': '',
        'category': '航材交易' if business_type.startswith('航材') else '其他',
        'aircraft_type': '',
        'author_title': position,
        'content_type': 'text',
        'tags': '',
        'author': author,
        'likes': row.get('likes') or row.get('reactions') or '0',
        'summary': content[:150] if content else '',
        'part_numbers': row.get('part_numbers') or row.get('pn_numbers', ''),
        'condition': row.get('condition', ''),
        'quantity': row.get('quantity', ''),
        'certification': row.get('certification', ''),
        'part_number': row.get('part_number') or row.get('pn', ''),
        'status': 'active',
        'notes': f"同步自：{source_file}"
    }
    
    return normalized

def sync_data():
    """执行数据同步"""
    print("=" * 70)
    print("LinkedIn Data Sync")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 加载已有帖子（去重）
    existing = load_existing_posts()
    print(f"[EXISTING] 主表已有帖子哈希数：{len(existing)}")
    
    # 构建实际的数据源列表（处理动态文件名）
    actual_sources = []
    
    # 查找 v8 增强版最新文件
    v8_latest = find_latest_file("linkedin_enhanced_", OUTPUT_DIR)
    if v8_latest:
        actual_sources.append(Path(v8_latest))
        print(f"[FOUND] v8 增强版最新：{Path(v8_latest).name}")
    
    # 添加固定文件名的数据源
    for src in DATA_SOURCES:
        if src.exists():
            actual_sources.append(src)
            print(f"[FOUND] {src.name}")
    
    # 收集新帖子
    new_posts = []
    seen_hashes = set(existing)
    
    for source_file in actual_sources:
        print(f"\n[PROCESS] {source_file.name}")
        
        try:
            with open(source_file, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    content = row.get('content') or row.get('text') or row.get('post_content', '')
                    content_hash = hashlib.md5(content[:200].encode()).hexdigest()
                    
                    if content_hash not in seen_hashes:
                        seen_hashes.add(content_hash)
                        normalized = normalize_post(row, source_file.name)
                        new_posts.append(normalized)
                        count += 1
                
                print(f"  [NEW] {count} 条")
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    print(f"\n[TOTAL] 新增：{len(new_posts)} 条")
    
    # 写入主表
    if new_posts:
        mode = 'a' if MASTER_TABLE.exists() else 'w'
        
        with open(MASTER_TABLE, mode, encoding='utf-8', newline='') as f:
            if mode == 'w':
                writer = csv.DictWriter(f, fieldnames=MASTER_FIELDS)
                writer.writeheader()
            else:
                writer = csv.DictWriter(f, fieldnames=MASTER_FIELDS)
            
            for post in new_posts:
                writer.writerow(post)
        
        print(f"\n[SUCCESS] 已同步到主表：{MASTER_TABLE}")
        print(f"   主表当前总记录数：{len(seen_hashes)}")
    else:
        print("\n[INFO] 无新数据需要同步")
    
    print("=" * 70)
    return len(new_posts)

if __name__ == "__main__":
    try:
        sync_data()
    except Exception as e:
        print(f"\n[ERROR] 同步失败：{e}")
        import traceback
        traceback.print_exc()
