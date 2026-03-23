#!/usr/bin/env python3
"""
LinkedIn Aviation Data Collection - Main Loop
持续采集2小时，每20分钟报告一次进度
"""
import csv
import json
import time
import re
from datetime import datetime
from pathlib import Path

class LinkedInCollector:
    def __init__(self):
        self.workspace = Path("C:/Users/Haide/.openclaw/workspace")
        self.output_file = self.workspace / "outputs" / "aviation_linkedin_master_20250301.csv"
        self.state_file = self.workspace / "outputs" / "aviation_linkedin_state.json"
        self.master_file = self.workspace / "Desktop" / "real business post" / "LinkedIn_Business_Posts_Master_Table.csv"
        
        self.url_index = set()
        self.content_index = set()
        self.stats = {
            "total_new": 0,
            "total_duplicates": 0,
            "by_category": {}
        }
        
        self.keywords = [
            'aviation', 'aerospace', 'aircraft', 'airline', 'engine', 'cfm', 'v2500',
            'leap', 'pw', 'boeing', 'airbus', 'a320', 'b737', 'b747', 'mro',
            'maintenance', 'landing gear', 'charter', 'lease', 'acmi', 'sale',
            'part', 'component', 'freighter', 'cargo', 'overhaul', 'repair'
        ]
        
        self.load_existing_data()
    
    def load_existing_data(self):
        """加载现有数据"""
        if self.output_file.exists():
            with open(self.output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('source_url'):
                        self.url_index.add(row['source_url'])
                    key = f"{row.get('author_name','')}_{row.get('post_content','')[:100]}"
                    self.content_index.add(key)
        print(f"[初始化] URL索引: {len(self.url_index)}, 内容索引: {len(self.content_index)}")
    
    def is_aviation_related(self, text):
        """检查是否航空相关"""
        text_lower = text.lower()
        for kw in self.keywords:
            if kw in text_lower:
                return True
        return False
    
    def is_duplicate(self, author, content):
        """检查是否重复"""
        key = f"{author}_{content[:100]}"
        return key in self.content_index
    
    def save_post(self, post_data):
        """保存帖子"""
        file_exists = self.output_file.exists()
        
        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp','author_name','author_title','author_company',
                               'post_content','hashtags','source_url','post_type','collected_at'])
            writer.writerow([
                post_data['timestamp'],
                post_data['author_name'],
                post_data['author_title'],
                post_data['author_company'],
                post_data['post_content'],
                post_data['hashtags'],
                post_data['source_url'],
                post_data['post_type'],
                post_data['collected_at']
            ])
        
        key = f"{post_data['author_name']}_{post_data['post_content'][:100]}"
        self.content_index.add(key)
        if post_data['source_url']:
            self.url_index.add(post_data['source_url'])
    
    def update_state(self, status, message=""):
        """更新状态"""
        state = {
            "status": status,
            "message": message,
            "stats": self.stats,
            "last_updated": datetime.now().isoformat(),
            "total_indexed": len(self.content_index)
        }
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def merge_to_master(self):
        """合并到主表"""
        import shutil
        
        self.master_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.master_file.exists():
            shutil.copy(self.output_file, self.master_file)
            return len(self.content_index)
        
        # 读取主表现有内容
        existing_content = set()
        with open(self.master_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = f"{row.get('author_name','')}_{row.get('post_content','')[:100]}"
                existing_content.add(key)
        
        # 追加新内容
        new_count = 0
        with open(self.output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        with open(self.master_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in rows:
                key = f"{row.get('author_name','')}_{row.get('post_content','')[:100]}"
                if key not in existing_content:
                    writer.writerow([
                        row['timestamp'], row['author_name'], row['author_title'],
                        row['author_company'], row['post_content'], row['hashtags'],
                        row['source_url'], row['post_type'], row['collected_at']
                    ])
                    new_count += 1
        
        return new_count

if __name__ == "__main__":
    collector = LinkedInCollector()
    collector.update_state("ready", "初始化完成")
    print("采集器就绪")
    print(f"当前索引: {len(collector.content_index)} 条")
