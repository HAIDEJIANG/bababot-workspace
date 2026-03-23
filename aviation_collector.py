"""
LinkedIn Aviation Data Collector
采集LinkedIn航空相关帖子，自动去重
"""
import json
import csv
import re
from datetime import datetime
from pathlib import Path

class AviationDataCollector:
    def __init__(self):
        self.workspace = Path("C:/Users/Haide/.openclaw/workspace")
        self.output_file = self.workspace / "outputs" / "aviation_linkedin_master_20250301.csv"
        self.state_file = self.workspace / "outputs" / "aviation_linkedin_state.json"
        self.master_file = self.workspace / "Desktop" / "real business post" / "LinkedIn_Business_Posts_Master_Table.csv"
        
        # 去重索引
        self.url_index = set()
        self.content_index = set()
        
        # 统计
        self.stats = {
            "total_new": 0,
            "total_duplicates": 0,
            "by_category": {}
        }
        
        # 航空关键词
        self.high_priority_keywords = [
            'aviation', 'aerospace', 'aircraft', 'airline', 'engine', 'cfm', 'v2500',
            'leap', 'pw', 'boeing', 'airbus', 'a320', 'b737', 'b747', 'mro',
            'maintenance', 'landing gear', 'charter', 'lease', 'acmi', 'sale',
            'part', 'component', 'freighter', 'cargo', 'overhaul', 'repair'
        ]
        
        self.medium_priority_keywords = [
            'flight', 'pilot', 'hangar', 'apron', 'turbine', 'propeller',
            'airport', 'fleet', 'fuselage', 'wing', 'cockpit'
        ]
        
        self.load_existing_data()
    
    def load_existing_data(self):
        """加载现有数据建立去重索引"""
        if self.output_file.exists():
            with open(self.output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # URL去重
                    if row.get('source_url'):
                        self.url_index.add(row['source_url'])
                    # 内容去重 (author + content[:100])
                    key = f"{row.get('author_name','')}_{row.get('post_content','')[:100]}"
                    self.content_index.add(key)
        print(f"[初始化] 已加载 {len(self.url_index)} 条URL索引, {len(self.content_index)} 条内容索引")
    
    def is_aviation_related(self, text):
        """检查是否航空相关"""
        text_lower = text.lower()
        
        # 高优先级关键词
        for kw in self.high_priority_keywords:
            if kw in text_lower:
                return True, 'high'
        
        # 中优先级关键词
        for kw in self.medium_priority_keywords:
            if kw in text_lower:
                return True, 'medium'
        
        return False, None
    
    def is_duplicate(self, author, content, url):
        """检查是否重复"""
        # URL去重
        if url and url in self.url_index:
            return True, 'url'
        
        # 内容去重
        key = f"{author}_{content[:100]}"
        if key in self.content_index:
            return True, 'content'
        
        return False, None
    
    def save_post(self, post_data):
        """保存帖子到CSV"""
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
        
        # 更新索引
        if post_data['source_url']:
            self.url_index.add(post_data['source_url'])
        key = f"{post_data['author_name']}_{post_data['post_content'][:100]}"
        self.content_index.add(key)
    
    def update_state(self, status, progress):
        """更新状态文件"""
        state = {
            "status": status,
            "progress": progress,
            "stats": self.stats,
            "last_updated": datetime.now().isoformat(),
            "total_indexed": len(self.content_index)
        }
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def merge_to_master(self):
        """合并到主表"""
        import shutil
        
        # 确保目录存在
        self.master_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果主表不存在，直接复制
        if not self.master_file.exists():
            shutil.copy(self.output_file, self.master_file)
            print(f"[合并] 主表不存在，已创建: {self.master_file}")
            return
        
        # 读取主表现有内容
        existing_urls = set()
        existing_content = set()
        
        with open(self.master_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('source_url'):
                    existing_urls.add(row['source_url'])
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
                url = row.get('source_url','')
                key = f"{row.get('author_name','')}_{row.get('post_content','')[:100]}"
                
                if url in existing_urls or key in existing_content:
                    continue
                
                writer.writerow([
                    row['timestamp'], row['author_name'], row['author_title'],
                    row['author_company'], row['post_content'], row['hashtags'],
                    row['source_url'], row['post_type'], row['collected_at']
                ])
                new_count += 1
        
        print(f"[合并] 已向主表追加 {new_count} 条新记录")

if __name__ == "__main__":
    collector = AviationDataCollector()
    collector.update_state("ready", "initialized")
    print("采集器初始化完成")
