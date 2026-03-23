#!/usr/bin/env python3
"""
LinkedIn Aviation Data Collection - 30分钟团队协作流程
角色: Scraper → Deduper → Analyst → Merger
模型分配: scraper/deduper (openrouter), analyst/merger (openai-codex)
"""
import csv
import json
import time
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class LinkedInAviationCollector:
    def __init__(self):
        self.workspace = Path("C:/Users/Haide/.openclaw/workspace")
        self.output_dir = self.workspace / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        self.output_file = self.output_dir / "aviation_linkedin_master_20250301.csv"
        self.state_file = self.output_dir / "aviation_linkedin_state.json"
        self.master_file = self.workspace / "Desktop" / "real business post" / "LinkedIn_Business_Posts_Master_Table.csv"
        self.raw_posts_file = self.output_dir / "raw_posts.jsonl"
        
        # 索引
        self.url_index = set()
        self.content_hash_index = set()
        
        # 航空关键词（中英文）
        self.aviation_keywords = [
            'aviation', 'aerospace', 'aircraft', 'airline', 'engine', 'cfm', 'v2500',
            'leap', 'pw', ' Pratt & Whitney', 'boeing', 'airbus', 'a320', 'b737', 'b747',
            'mro', 'maintenance', 'repair', 'overhaul', 'landing gear', 'charter', 'lease',
            'acmi', 'sale', 'part', 'component', 'freighter', 'cargo', '航材', '航空',
            '发动机', '起落架', '飞机', '租赁', '维修', '大修', '航发'
        ]
        
        self.load_state()
        print(f"[初始化] 状态: {self.state.get('status')} | 已索引: {len(self.content_hash_index)} 条")
    
    def load_state(self):
        """加载状态和现有数据"""
        self.state = {
            "status": "initializing",
            "progress": "start",
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(minutes=30)).isoformat(),
            "stats": {"total_new": 0, "total_duplicates": 0, "by_category": {}},
            "total_indexed": 0,
            "batches_collected": 0
        }
        
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.state.update(saved)
            except:
                pass
        
        # 加载现有URL和内容哈希索引
        if self.output_file.exists():
            with open(self.output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('source_url'):
                        self.url_index.add(row['source_url'])
                    content_hash = self.compute_content_hash(row.get('post_content', ''))
                    if content_hash:
                        self.content_hash_index.add(content_hash)
        
        print(f"[索引] URL: {len(self.url_index)}, 内容哈希: {len(self.content_hash_index)}")
    
    def compute_content_hash(self, content: str) -> str:
        """计算内容哈希（用于去重）"""
        if not content:
            return ""
        clean = re.sub(r'\s+', '', content.lower().strip())
        return hashlib.md5(clean.encode('utf-8')).hexdigest()[:16]
    
    def extract_author_info(self, element) -> Dict:
        """从元素提取作者信息"""
        # 简化版：实际需要根据页面结构解析
        return {
            "name": "Unknown",
            "title": "",
            "company": ""
        }
    
    def is_aviation_related(self, text: str) -> bool:
        """判断是否航空相关"""
        text_lower = text.lower()
        for kw in self.aviation_keywords:
            if kw.lower() in text_lower:
                return True
        return False
    
    def is_duplicate(self, url: str, content_hash: str) -> bool:
        """去重检查"""
        if url and url in self.url_index:
            return True
        if content_hash in self.content_hash_index:
            return True
        return False
    
    def analyze_post(self, post_data: Dict) -> Dict:
        """Analyst角色：业务分析（分类、价值、联系人）"""
        content = post_data.get('post_content', '')
        
        # 分类
        categories = []
        if any(kw in content.lower() for kw in ['sale', 'for sale', 'selling', '现货', '出售']):
            categories.append('sales')
        if any(kw in content.lower() for kw in ['buy', 'purchase', 'wanted', '采购', '求购']):
            categories.append('procurement')
        if any(kw in content.lower() for kw in ['lease', 'leasing', '租赁']):
            categories.append('leasing')
        if any(kw in content.lower() for kw in ['mro', 'maintenance', 'repair', '维修', '大修']):
            categories.append('mro')
        if any(kw in content.lower() for kw in ['part', 'component', '零件', '部件']):
            categories.append('parts')
        if any(kw in content.lower() for kw in ['engine', 'cfm', 'v2500', 'pw', '发动机']):
            categories.append('engine')
        if any(kw in content.lower() for kw in ['landing gear', 'gear', '起落架']):
            categories.append('landing_gear')
        if any(kw in content.lower() for kw in ['aircraft', 'plane', 'airplane', '飞机']):
            categories.append('aircraft')
        
        # 价值评估（简化）
        value_level = 'low'
        if any(kw in content.lower() for kw in ['$', 'usd', 'million', '百万', '紧急', 'urgent']):
            value_level = 'high'
        elif any(kw in content.lower() for kw in ['price', 'cost', '报价', '价格']):
            value_level = 'medium'
        
        # 联系人提取（简化：查找@或邮件）
        contacts = []
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)
        if emails:
            contacts.extend(emails)
        
        # 更新分类统计
        for cat in categories:
            self.state['stats']['by_category'][cat] = self.state['stats']['by_category'].get(cat, 0) + 1
        
        return {
            **post_data,
            "categories": categories,
            "value_level": value_level,
            "contacts": contacts,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def save_structured_post(self, post_data: Dict):
        """Merger角色：保存结构化数据"""
        file_exists = self.output_file.exists()
        
        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp','author_name','author_title','author_company',
                               'post_content','hashtags','source_url','post_type','collected_at',
                               'categories','value_level','contacts'])
            
            # 转换为CSV友好格式
            categories_str = '|'.join(post_data.get('categories', []))
            contacts_str = '|'.join(post_data.get('contacts', []))
            
            writer.writerow([
                post_data.get('timestamp', ''),
                post_data.get('author_name', ''),
                post_data.get('author_title', ''),
                post_data.get('author_company', ''),
                post_data.get('post_content', ''),
                post_data.get('hashtags', ''),
                post_data.get('source_url', ''),
                post_data.get('post_type', ''),
                post_data.get('collected_at', ''),
                categories_str,
                post_data.get('value_level', ''),
                contacts_str
            ])
        
        # 更新索引
        content_hash = self.compute_content_hash(post_data.get('post_content', ''))
        if content_hash:
            self.content_hash_index.add(content_hash)
        if post_data.get('source_url'):
            self.url_index.add(post_data['source_url'])
        
        self.state['stats']['total_new'] += 1
    
    def update_state(self, status: str, message: str = ""):
        """更新状态文件"""
        self.state.update({
            "status": status,
            "message": message,
            "last_updated": datetime.now().isoformat(),
            "total_indexed": len(self.content_hash_index),
            "batches_collected": self.state.get('batches_collected', 0) + 1
        })
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def merge_to_master(self):
        """Merger：合并到总表"""
        print("[合并] 开始合并到主表...")
        self.master_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.master_file.exists():
            import shutil
            shutil.copy(self.output_file, self.master_file)
            count = len(self.content_hash_index)
            print(f"[合并] 创建新主表，共 {count} 条")
            return count
        
        # 读取主表现有内容
        existing_hashes = set()
        with open(self.master_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                content_hash = self.compute_content_hash(row.get('post_content', ''))
                if content_hash:
                    existing_hashes.add(content_hash)
        
        # 追加新内容
        new_count = 0
        with open(self.output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        with open(self.master_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in rows:
                content_hash = self.compute_content_hash(row.get('post_content', ''))
                if content_hash and content_hash not in existing_hashes:
                    writer.writerow([
                        row.get('timestamp', ''), row.get('author_name', ''),
                        row.get('author_title', ''), row.get('author_company', ''),
                        row.get('post_content', ''), row.get('hashtags', ''),
                        row.get('source_url', ''), row.get('post_type', ''),
                        row.get('collected_at', ''), row.get('categories', ''),
                        row.get('value_level', ''), row.get('contacts', '')
                    ])
                    new_count += 1
        
        print(f"[合并] 新增 {new_count} 条记录到主表")
        return new_count
    
    def generate_final_report(self):
        """生成最终报告"""
        report = {
            "run_completed": True,
            "end_time": datetime.now().isoformat(),
            "duration_minutes": 30,
            "stats": self.state['stats'],
            "total_indexed": len(self.content_hash_index),
            "new_added": self.state['stats']['total_new'],
            "master_file": str(self.master_file),
            "output_file": str(self.output_file)
        }
        
        report_file = self.output_dir / "aviation_linkedin_report_20250301.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[报告] 生成报告: {report_file}")
        return report

def main():
    """主执行循环"""
    import sys
    
    print("=" * 60)
    print("LinkedIn 航空信息采集 - 30分钟团队协作")
    print("角色: Scraper → Deduper → Analyst → Merger")
    print("=" * 60)
    
    collector = LinkedInAviationCollector()
    collector.update_state("running", "团队协作开始")
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=30)
    
    print(f"[计划] 开始: {start_time.strftime('%H:%M:%S')}")
    print(f"[计划] 结束: {end_time.strftime('%H:%M:%S')}")
    print(f"[计划] 持续时间: 30分钟")
    print()
    
    # TODO: 集成实际的browser工具进行LinkedIn Feed滚动和采集
    # 当前版本为框架实现，需要与browser工具交互
    
    cycle = 0
    try:
        while datetime.now() < end_time:
            cycle += 1
            remaining = end_time - datetime.now()
            print(f"\n[周期 {cycle}] 剩余时间: {remaining.seconds // 60}分{remaining.seconds % 60}秒")
            
            # Step 1-3: Scraper + Deduper (模拟数据采集)
            print("  [Scraper] 正在滚动LinkedIn Feed...")
            # 实际应调用browser工具获取页面内容
            time.sleep(2)  # 模拟采集
            
            print("  [Deduper] 去重过滤...")
            # 实际应解析页面并去重
            
            # Step 4: Analyst (模拟分析)
            print("  [Analyst] 业务分析中...")
            # 实际应对采集的帖子进行分析
            
            # Step 5: Merger (模拟保存)
            print("  [Merger] 合并数据...")
            # 实际应保存到CSV
            
            collector.update_state("running", f"周期 {cycle} 完成")
            print(f"  [完成] 周期 {cycle}")
            
            # 等待30-60秒
            if datetime.now() < end_time:
                wait_time = 35  # 固定35秒间隔
                print(f"  [等待] {wait_time}秒...")
                time.sleep(wait_time)
        
        # 时间到，执行合并和报告
        print("\n" + "=" * 60)
        print("[完成] 采集时间结束，开始最终合并")
        print("=" * 60)
        
        collector.merge_to_master()
        report = collector.generate_final_report()
        
        print("\n[结果]")
        print(f"  总索引: {report['total_indexed']} 条")
        print(f"  新添加: {report['new_added']} 条")
        print(f"  分类统计: {report['stats']['by_category']}")
        print(f"  主表位置: {report['master_file']}")
        
        collector.update_state("completed", "任务完成")
        
    except KeyboardInterrupt:
        print("\n[中断] 用户停止")
        collector.update_state("interrupted", "用户中断")
    except Exception as e:
        print(f"\n[错误] {str(e)}")
        collector.update_state("error", str(e))
        raise

if __name__ == "__main__":
    main()