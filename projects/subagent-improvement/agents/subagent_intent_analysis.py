#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务意图分析 Sub-Agent - 分析发帖内容，识别业务意图
识别类型：采购意向、出售意向、合作意向
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from subagent_base import SubAgentBase, resource_manager

# ==================== 配置 ====================

# 输入文件
INPUT_POSTS = Path(r"C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\contact_posts_90days.csv")
INPUT_PRIORITY = Path(r"C:\Users\Haide\Desktop\LINKEDIN\priority_ranking.csv")

# 输出文件
OUTPUT_INTENTS = Path(r"C:\Users\Haide\Desktop\LINKEDIN\linkedin_business_intents.csv")

# 业务意图关键词
BUY_KEYWORDS = [
    'wtb', 'want to buy', 'want to purchase', 'looking for', 'need', 'require',
    'rfq', 'request for quote', 'quote', 'quotation', 'price',
    'buy', 'purchase', 'procurement', 'sourcing', 'buyer',
    'searching for', 'seeking', 'demand', 'interested in'
]

SELL_KEYWORDS = [
    'wts', 'want to sell', 'for sale', 'available', 'selling', 'offer',
    'sell', 'stock', 'inventory', 'supply', 'provide', 'supplier',
    'have', 'own', 'can supply', 'can provide', 'ready to ship',
    'in stock', 'immediate delivery', 'hot sale'
]

PARTNERSHIP_KEYWORDS = [
    'partnership', 'collaboration', 'distributor', 'dealer',
    'agent', 'representative', 'joint venture', 'cooperation',
    'distribute', 'reseller', 'exclusive', 'authorized'
]

URGENT_KEYWORDS = [
    'urgent', 'aog', 'immediate', 'asap', 'emergency',
    'rush', 'priority', 'critical', 'time sensitive'
]

# ==================== Sub-Agent ====================

class IntentAnalysisSubAgent(SubAgentBase):
    """业务意图分析 Sub-Agent"""
    
    def __init__(self):
        super().__init__('intent_analysis')
        self.input_files = {
            'posts': INPUT_POSTS,
            'priority': INPUT_PRIORITY
        }
        self.output_files = {
            'intents': OUTPUT_INTENTS
        }
    
    def detect_intent(self, content):
        """检测业务意图"""
        if pd.isna(content) or not content:
            return None
        
        content_lower = str(content).lower()
        
        # 检查紧急程度
        is_urgent = any(kw in content_lower for kw in URGENT_KEYWORDS)
        
        # 检测意图类型
        intents = []
        
        buy_count = sum(1 for kw in BUY_KEYWORDS if kw in content_lower)
        sell_count = sum(1 for kw in SELL_KEYWORDS if kw in content_lower)
        partnership_count = sum(1 for kw in PARTNERSHIP_KEYWORDS if kw in content_lower)
        
        if buy_count > 0:
            intents.append('采购意向')
        if sell_count > 0:
            intents.append('出售意向')
        if partnership_count > 0:
            intents.append('合作意向')
        
        if not intents:
            return None
        
        # 组合意图和紧急程度
        intent_str = ', '.join(intents)
        if is_urgent:
            intent_str = '🔴 紧急 - ' + intent_str
        
        return intent_str
    
    def calculate_priority_score(self, intent, priority_score):
        """计算优先级分数（结合意图和原有优先级）"""
        base_score = int(priority_score) if priority_score else 0
        
        # 意图加分
        if intent:
            if '🔴 紧急' in intent:
                base_score += 20
            if '采购意向' in intent:
                base_score += 15
            if '出售意向' in intent:
                base_score += 10
            if '合作意向' in intent:
                base_score += 5
        
        return min(base_score, 120)  # 最高 120 分
    
    def execute(self):
        """执行意图分析"""
        self.log("开始加载输入文件...", 'INFO')
        
        # 读取发帖数据
        with resource_manager.acquire_file(str(self.input_files['posts']), self.run_id):
            if self.input_files['posts'].exists():
                posts_df = pd.read_csv(self.input_files['posts'], encoding='utf-8', errors='replace')
            else:
                self.log("警告：发帖数据文件不存在", 'WARNING')
                posts_df = pd.DataFrame()
        
        # 读取优先级数据
        with resource_manager.acquire_file(str(self.input_files['priority']), self.run_id):
            if self.input_files['priority'].exists():
                priority_df = pd.read_csv(self.input_files['priority'], encoding='utf-8', errors='replace')
            else:
                self.log("警告：优先级数据文件不存在", 'WARNING')
                priority_df = pd.DataFrame()
        
        self.update_progress(20, 100)
        self.log(f"已加载：发帖数据{len(posts_df)}条，优先级数据{len(priority_df)}条", 'INFO')
        
        # 意图分析
        self.log("开始业务意图分析...", 'INFO')
        
        results = []
        
        for idx, row in posts_df.iterrows():
            contact_id = row.get('contact_id', '')
            post_content = row.get('post_content', '')
            post_date = row.get('post_date', '')
            
            # 检测意图
            intent = self.detect_intent(post_content)
            
            if intent:
                # 查找联系人优先级
                priority_row = priority_df[priority_df['contact_id'] == contact_id]
                priority_score = priority_row['total_score'].values[0] if not priority_row.empty else 0
                priority_level = priority_row['priority_level'].values[0] if not priority_row.empty else ''
                name = priority_row['name'].values[0] if not priority_row.empty else ''
                company = priority_row['company'].values[0] if not priority_row.empty else ''
                position = priority_row['position'].values[0] if not priority_row.empty else ''
                
                # 计算综合优先级
                combined_score = self.calculate_priority_score(intent, priority_score)
                
                result = {
                    'contact_id': contact_id,
                    'name': name,
                    'company': company,
                    'position': position,
                    'post_date': post_date,
                    'post_content': post_content[:500] if post_content else '',
                    'business_intent': intent,
                    'original_priority_score': priority_score,
                    'combined_priority_score': combined_score,
                    'priority_level': priority_level,
                    'analyzed_at': datetime.now().isoformat()
                }
                results.append(result)
            
            # 更新进度
            if (idx + 1) % 100 == 0:
                progress = min(20 + (idx / len(posts_df) * 80), 100)
                self.update_progress(int(progress), 100)
        
        self.update_progress(100, 100)
        
        # 保存结果
        self.log("保存意图分析结果...", 'INFO')
        
        if results:
            results_df = pd.DataFrame(results)
            
            # 按综合优先级排序
            results_df = results_df.sort_values('combined_priority_score', ascending=False)
            
            with resource_manager.acquire_file(str(self.output_files['intents']), self.run_id):
                results_df.to_csv(self.output_files['intents'], index=False, encoding='utf-8-sig')
            
            self.log(f"分析完成！识别到{len(results)}条业务意图", 'INFO')
            
            # 统计
            intent_counts = results_df['business_intent'].value_counts()
            self.log("意图分布：", 'INFO')
            for intent, count in intent_counts.items():
                self.log(f"  {intent}: {count}条", 'INFO')
        else:
            self.log("未识别到业务意图", 'WARNING')
        
        return {
            'total_analyzed': len(posts_df),
            'intents_found': len(results),
            'output_file': str(self.output_files['intents'])
        }

# ==================== 主程序 ====================

if __name__ == '__main__':
    agent = IntentAnalysisSubAgent()
    
    try:
        result = agent.execute_with_retry()
        print(f"\n✅ 业务意图分析完成！")
        print(f"分析发帖：{result['total_analyzed']}条")
        print(f"识别意图：{result['intents_found']}条")
        print(f"输出文件：{result['output_file']}")
    except Exception as e:
        print(f"\n❌ 业务意图分析失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
