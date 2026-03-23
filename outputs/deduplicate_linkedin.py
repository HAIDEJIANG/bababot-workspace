#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deduplication and Merge Script for LinkedIn Collection
Checks new posts against master table and appends unique entries
"""

import pandas as pd
import hashlib
import os
from datetime import datetime

# Paths
MASTER_TABLE = r"C:\Users\Haide\Desktop\real business post\LinkedIn_Business_Posts_Master_Table.csv"
NEW_COLLECTION = r"C:\Users\Haide\.openclaw\workspace\outputs\linkedin_collection_20260302_1452.md"
OUTPUT_DIR = r"C:\Users\Haide\.openclaw\workspace\outputs"

def extract_posts_from_markdown(md_file):
    """Extract posts from markdown collection file"""
    posts = []
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by post sections
    sections = content.split('---')[1:]  # Skip header
    
    for section in sections:
        if not section.strip() or 'Post ' not in section:
            continue
            
        lines = section.strip().split('\n')
        post = {}
        
        for line in lines:
            if line.startswith('## Post '):
                post['post_number'] = line.replace('## Post ', '').split(':')[0]
            elif '**Author:**' in line:
                post['author_name'] = line.split('**Author:**')[1].strip()
            elif '**Author Profile:**' in line:
                post['author_profile'] = line.split('**Author Profile:**')[1].strip()
            elif '**Source URL:**' in line:
                post['source_url'] = line.split('**Source URL:**')[1].strip()
            elif '**Content:**' in line:
                post['content_preview'] = line.split('**Content:**')[1].strip()[:200]
            elif '**Time Posted:**' in line:
                post['time_posted'] = line.split('**Time Posted:**')[1].strip()
        
        if post.get('source_url'):
            posts.append(post)
    
    return posts

def generate_content_hash(post):
    """Generate hash for deduplication based on URL + author + content preview"""
    hash_input = f"{post.get('source_url', '')}|{post.get('author_name', '')}|{post.get('content_preview', '')}"
    return hashlib.md5(hash_input.encode('utf-8')).hexdigest()

def check_duplicates(new_posts, master_df):
    """Check which posts are already in master table"""
    if master_df.empty:
        return new_posts, []
    
    unique_posts = []
    duplicates = []
    
    for post in new_posts:
        post_hash = generate_content_hash(post)
        
        # Check if URL exists in master
        if 'source_url' in master_df.columns:
            url_match = master_df[master_df['source_url'] == post.get('source_url')]
            if not url_match.empty:
                duplicates.append(post)
                continue
        
        unique_posts.append(post)
    
    return unique_posts, duplicates

def main():
    print("=" * 60)
    print("LinkedIn Collection Deduplication")
    print("=" * 60)
    
    # Extract new posts
    print(f"\n[READ] New collection: {NEW_COLLECTION}")
    new_posts = extract_posts_from_markdown(NEW_COLLECTION)
    print(f"[OK] Found {len(new_posts)} posts in new collection")
    
    # Load master table
    print(f"\n[LOAD] Master table: {MASTER_TABLE}")
    try:
        master_df = pd.read_csv(MASTER_TABLE)
        print(f"[OK] Master table loaded: {len(master_df)} existing posts")
    except FileNotFoundError:
        print("[WARN] Master table not found, creating new one")
        master_df = pd.DataFrame()
    
    # Check for duplicates
    print("\n[CHECK] Checking for duplicates...")
    unique_posts, duplicates = check_duplicates(new_posts, master_df)
    
    print(f"\n[RESULTS] Deduplication Results:")
    print(f"  - New posts: {len(new_posts)}")
    print(f"  - Unique posts: {len(unique_posts)}")
    print(f"  - Duplicates: {len(duplicates)}")
    
    if duplicates:
        print("\n[SKIP] Duplicate posts (will be skipped):")
        for post in duplicates:
            print(f"  - {post.get('author_name', 'Unknown')}: {post.get('content_preview', '')[:50]}...")
    
    if unique_posts:
        # Create DataFrame for unique posts
        new_df = pd.DataFrame(unique_posts)
        new_df['collection_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_df['collection_batch'] = '20260302_1452'
        
        # Append to master
        if not master_df.empty:
            updated_df = pd.concat([master_df, new_df], ignore_index=True)
        else:
            updated_df = new_df
        
        # Save backup of master
        backup_path = MASTER_TABLE.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        master_df.to_csv(backup_path, index=False, encoding='utf-8-sig')
        print(f"\n[BACKUP] Master table backup saved: {backup_path}")
        
        # Save updated master
        updated_df.to_csv(MASTER_TABLE, index=False, encoding='utf-8-sig')
        print(f"[OK] Updated master table saved: {len(updated_df)} total posts")
        
        # Save unique posts report
        report_path = os.path.join(OUTPUT_DIR, f"linkedin_unique_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        new_df.to_csv(report_path, index=False, encoding='utf-8-sig')
        print(f"[REPORT] Unique posts report saved: {report_path}")
    else:
        print("\n[WARN] No unique posts to add")
    
    print("\n" + "=" * 60)
    print("Deduplication Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
