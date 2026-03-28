#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据合并 Sub-Agent - 合并已有数据和采集数据
解决"Join LinkedIn"问题，生成完整数据库
"""

import sys
import io
import pandas as pd
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from subagent_base import SubAgentBase
from resource_manager import resource_manager

# ==================== 配置 ====================

# 输入文件
EXISTING_DATA = Path(r"C:\Users\Haide\Desktop\OPENCLAW\LINKEDIN\LINKEDIN Connections_with_posts_FINAL.csv")
COLLECTED_DATA = Path(r"C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\contact_profiles_full.csv")
PRIORITY_DATA = Path(r"C:\Users\Haide\Desktop\LINKEDIN\priority_ranking.csv")

# 输出文件
OUTPUT_DATABASE = Path(r"C:\Users\Haide\Desktop\LINKEDIN\linkedin_master_database.csv")
OUTPUT_LEADS = Path(r"C:\Users\Haide\Desktop\LINKEDIN\linkedin_business_leads.csv")

# ==================== Sub-Agent ====================

class DataMergeSubAgent(SubAgentBase):
    """数据合并 Sub-Agent"""
    
    def __init__(self):
        super().__init__('data_merge')
        self.input_files = {
            'existing': EXISTING_DATA,
            'collected': COLLECTED_DATA,
            'priority': PRIORITY_DATA
        }
        self.output_files = {
            'database': OUTPUT_DATABASE,
            'leads': OUTPUT_LEADS
        }
    
    def execute(self):
        """执行数据合并"""
        self.log("开始加载输入文件...", 'INFO')
        
        # 读取输入文件（带文件锁）
        with resource_manager.acquire_file(str(self.input_files['existing']), self.run_id, timeout=60):
            if self.input_files['existing'].exists():
                existing_data = pd.read_csv(self.input_files['existing'], encoding='utf-8', encoding_errors='replace')
            else:
                self.log("警告：已有数据文件不存在", 'WARNING')
                existing_data = pd.DataFrame()
        
        with resource_manager.acquire_file(str(self.input_files['collected']), self.run_id, timeout=60):
            if self.input_files['collected'].exists():
                collected_data = pd.read_csv(self.input_files['collected'], encoding='utf-8', encoding_errors='replace')
            else:
                self.log("警告：采集数据文件不存在", 'WARNING')
                collected_data = pd.DataFrame()
        
        with resource_manager.acquire_file(str(self.input_files['priority']), self.run_id, timeout=60):
            if self.input_files['priority'].exists():
                priority_data = pd.read_csv(self.input_files['priority'], encoding='utf-8', encoding_errors='replace')
            else:
                self.log("警告：优先级数据文件不存在", 'WARNING')
                priority_data = pd.DataFrame()
        
        self.update_progress(30, 100)
        self.log(f"已加载：已有数据{len(existing_data)}条，采集数据{len(collected_data)}条，优先级{len(priority_data)}条", 'INFO')
        
        # 合并逻辑
        self.log("开始合并数据...", 'INFO')
        
        if not collected_data.empty and not existing_data.empty:
            # 按 URL 合并
            merged = pd.merge(
                existing_data,
                collected_data,
                left_on='URL',
                right_on='contact_id',
                how='left',
                suffixes=('_existing', '_collected')
            )
            
            # 解决"Join LinkedIn"问题 - 优先使用已有数据的姓名/公司/职位
            merged['name'] = merged.apply(
                lambda row: f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip() 
                if pd.isna(row.get('name')) or row.get('name') == 'Join LinkedIn' 
                else row.get('name', ''),
                axis=1
            )
            
            merged['company'] = merged.apply(
                lambda row: row.get('Company', row.get('current_company')) 
                if pd.isna(row.get('Company')) or row.get('Company') == '' 
                else row.get('Company', ''),
                axis=1
            )
            
            merged['position'] = merged.apply(
                lambda row: row.get('Position', row.get('current_title')) 
                if pd.isna(row.get('Position')) or row.get('Position') == '' 
                else row.get('Position', ''),
                axis=1
            )
        else:
            # 如果采集数据为空，直接使用已有数据
            merged = existing_data.copy()
            if not existing_data.empty:
                merged['name'] = merged.apply(
                    lambda row: f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip(),
                    axis=1
                )
        
        self.update_progress(70, 100)
        self.log("数据合并完成", 'INFO')
        
        # 合并优先级数据
        self.log("开始合并优先级数据...", 'INFO')
        
        if not priority_data.empty and not merged.empty:
            final = pd.merge(
                merged,
                priority_data,
                left_on='URL',
                right_on='contact_id',
                how='left'
            )
        else:
            final = merged
        
        self.update_progress(90, 100)
        self.log("优先级数据合并完成", 'INFO')
        
        # 保存输出
        self.log("保存输出文件...", 'INFO')
        
        with resource_manager.acquire_file(str(self.output_files['database']), self.run_id, timeout=60):
            final.to_csv(self.output_files['database'], index=False, encoding='utf-8-sig')
        
        # 生成高意向线索（如果有发帖数据）
        if 'post_content' in final.columns and not final['post_content'].isna().all():
            self.log("生成高意向线索...", 'INFO')
            
            # 业务意图关键词
            buy_keywords = ['wtb', 'want to buy', 'looking for', 'need', 'rfq', 'quote']
            sell_keywords = ['wts', 'for sale', 'available', 'selling', 'offer']
            
            def detect_intent(content):
                if pd.isna(content):
                    return None
                content_lower = str(content).lower()
                if any(kw in content_lower for kw in buy_keywords):
                    return '采购意向'
                if any(kw in content_lower for kw in sell_keywords):
                    return '出售意向'
                return None
            
            final['business_intent'] = final['post_content'].apply(detect_intent)
            
            # 筛选高意向线索
            leads = final[final['business_intent'].notna()].copy()
            
            if not leads.empty:
                with resource_manager.acquire_file(str(self.output_files['leads']), self.run_id, timeout=60):
                    leads.to_csv(self.output_files['leads'], index=False, encoding='utf-8-sig')
                self.log(f"生成{len(leads)}条高意向线索", 'INFO')
        
        self.update_progress(100, 100)
        
        result = {
            'total_contacts': len(final),
            'output_database': str(self.output_files['database']),
            'output_leads': str(self.output_files['leads']) if 'leads' in locals() else None
        }
        
        self.log(f"数据合并完成！总计{len(final)}位联系人", 'INFO')
        
        return result

# ==================== 主程序 ====================

if __name__ == '__main__':
    agent = DataMergeSubAgent()
    
    try:
        result = agent.execute_with_retry()
        print(f"\n✅ 数据合并完成！")
        print(f"总计：{result['total_contacts']}位联系人")
        print(f"数据库：{result['output_database']}")
        if result['output_leads']:
            print(f"高意向线索：{result['output_leads']}")
    except Exception as e:
        print(f"\n❌ 数据合并失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
