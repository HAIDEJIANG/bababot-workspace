#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能优先级打分 Sub-Agent - 根据职位/公司/行业打分，筛选高价值联系人
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from subagent_base import SubAgentBase, resource_manager

# ==================== 配置 ====================

# 输入文件
INPUT_FILE = Path(r"C:\Users\Haide\Desktop\OPENCLAW\LINKEDIN\LINKEDIN Connections_with_posts_FINAL.csv")

# 输出文件
HIGH_PRIORITY_OUTPUT = Path(r"C:\Users\Haide\Desktop\LINKEDIN\high_priority_contacts.csv")
PRIORITY_RANKING_OUTPUT = Path(r"C:\Users\Haide\Desktop\LINKEDIN\priority_ranking.csv")

# 优先级打分标准
PRIORITY_SCORES = {
    # 高优先级（100+ 分）
    'high': {
        'titles': [
            'CEO', 'COO', 'CFO', 'CTO', 'President', 'Vice President',
            'VP', 'Director', 'Managing Director', 'General Manager',
            'President', 'Owner', 'Founder', 'Chairman', 'Chief'
        ],
        'weight': 100
    },
    
    # 中高优先级（80-99 分）
    'medium_high': {
        'titles': [
            'Purchasing', 'Procurement', 'Buyer', 'Sourcing', 'Sourcing Manager',
            'Buyer', 'Procurement Manager', 'Supply Chain', 'Materials Manager',
            'Sales', 'Business Development', 'Account Manager', 'Sales Manager',
            'Business Manager', 'Sales Director', 'BD Manager'
        ],
        'weight': 80
    },
    
    # 中优先级（60-79 分）
    'medium': {
        'titles': [
            'Manager', 'Supervisor', 'Team Leader', 'Operations',
            'Engineer', 'Technical', 'Maintenance', 'MRO',
            'Aircraft', 'Engine', 'Powerplant', 'Aviation'
        ],
        'weight': 60
    },
    
    # 低优先级（40-59 分）
    'low': {
        'titles': [
            'Specialist', 'Analyst', 'Coordinator', 'Assistant',
            'Technician', 'Inspector', 'Support', 'Admin'
        ],
        'weight': 40
    }
}

# 公司类型加分
COMPANY_BONUS = {
    'airlines': 20,
    'mro': 15,
    'engine': 15,
    'spare parts': 15,
    'aviation': 10,
    'aero': 10,
    'aerospace': 10,
    'trading': 10,
    'leasing': 10,
    'broker': 8,
    'consulting': 5
}

# ==================== Sub-Agent ====================

class PriorityRankingSubAgent(SubAgentBase):
    """智能优先级打分 Sub-Agent"""
    
    def __init__(self):
        super().__init__('priority_ranking')
        self.input_file = INPUT_FILE
        self.output_files = {
            'high_priority': HIGH_PRIORITY_OUTPUT,
            'ranking': PRIORITY_RANKING_OUTPUT
        }
    
    def calculate_priority_score(self, title: str, company: str, connections: str) -> tuple:
        """
        计算优先级分数
        Returns: (score, level)
        """
        if pd.isna(title):
            title = ''
        if pd.isna(company):
            company = ''
        if pd.isna(connections):
            connections = ''
        
        title_lower = title.lower()
        company_lower = company.lower()
        connections_str = str(connections).lower()
        
        # 职位分数
        score = 0
        level = 'low'
        
        for level_name, level_config in PRIORITY_SCORES.items():
            for title_keyword in level_config['titles']:
                if title_keyword.lower() in title_lower:
                    score = level_config['weight']
                    level = level_name.split('_')[0]  # high, medium_high, medium, low
                    break
        
        # 公司加分
        for company_type, bonus in COMPANY_BONUS.items():
            if company_type in company_lower:
                score += bonus
        
        # 连接数加分
        if '500+' in connections_str:
            score += 10
        elif '100' in connections_str:
            score += 5
        elif '50' in connections_str:
            score += 3
        
        # 行业加分
        aviation_industries = [
            'aviation', 'aerospace', 'airline', 'aircraft', 'engine',
            'mro', 'maintenance', 'overhaul', 'spare parts', 'aero'
        ]
        if any(industry in company_lower for industry in aviation_industries):
            score += 5
        
        # 调整等级
        if score >= 100:
            level = 'high'
        elif score >= 80:
            level = 'medium_high'
        elif score >= 60:
            level = 'medium'
        else:
            level = 'low'
        
        return score, level
    
    def execute(self):
        """执行优先级打分"""
        self.log("开始加载联系人数据...", 'INFO')
        
        # 读取输入文件
        with resource_manager.acquire_file(str(self.input_file), self.run_id):
            df = pd.read_csv(self.input_file, encoding='utf-8', errors='replace')
        
        self.update_progress(10, 100)
        self.log(f"已加载 {len(df)} 位联系人数据", 'INFO')
        
        # 计算优先级分数
        self.log("开始计算优先级分数...", 'INFO')
        
        scores = []
        high_priority_contacts = []
        
        for idx, row in df.iterrows():
            title = row.get('Position', row.get('title', ''))
            company = row.get('Company', row.get('company', ''))
            connections = row.get('connections', '500+')
            
            score, level = self.calculate_priority_score(title, company, connections)
            
            contact_info = {
                'contact_id': row.get('URL', ''),
                'name': f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip(),
                'company': company,
                'position': title,
                'connections': connections,
                'priority_score': score,
                'priority_level': level,
                'calculate_time': datetime.now().isoformat()
            }
            scores.append(contact_info)
            
            # 筛选高优先级联系人
            if score >= 80:
                high_priority_contacts.append(row)
        
        self.update_progress(80, 100)
        
        # 保存优先级排名
        self.log("保存优先级排名...", 'INFO')
        
        ranking_df = pd.DataFrame(scores)
        ranking_df = ranking_df.sort_values('priority_score', ascending=False)
        
        with resource_manager.acquire_file(str(self.output_files['ranking']), self.run_id):
            ranking_df.to_csv(self.output_files['ranking'], index=False, encoding='utf-8-sig')
        
        # 保存高优先级联系人
        self.log("保存高优先级联系人...", 'INFO')
        
        if high_priority_contacts:
            high_priority_df = pd.DataFrame(high_priority_contacts)
            with resource_manager.acquire_file(str(self.output_files['high_priority']), self.run_id):
                high_priority_df.to_csv(self.output_files['high_priority'], index=False, encoding='utf-8-sig')
        
        self.update_progress(100, 100)
        
        # 统计
        high_count = len([s for s in scores if s['priority_score'] >= 80])
        medium_count = len([s for s in scores if 60 <= s['priority_score'] < 80])
        low_count = len([s for s in scores if s['priority_score'] < 60])
        
        self.log(f"优先级统计：", 'INFO')
        self.log(f"  高优先级（≥80分）：{high_count} 位", 'INFO')
        self.log(f"  中优先级（60-79分）：{medium_count} 位", 'INFO')
        self.log(f"  低优先级（<60分）：{low_count} 位", 'INFO')
        
        return {
            'total_contacts': len(df),
            'high_priority_contacts': high_count,
            'medium_priority_contacts': medium_count,
            'low_priority_contacts': low_count,
            'output_ranking': str(self.output_files['ranking']),
            'output_high_priority': str(self.output_files['high_priority'])
        }

# ==================== 主程序 ====================

if __name__ == '__main__':
    agent = PriorityRankingSubAgent()
    
    try:
        result = agent.execute_with_retry()
        print(f"\n✅ 智能优先级打分完成！")
        print(f"总联系人：{result['total_contacts']} 位")
        print(f"高优先级：{result['high_priority_contacts']} 位")
        print(f"中优先级：{result['medium_priority_contacts']} 位")
        print(f"低优先级：{result['low_priority_contacts']} 位")
        print(f"排名文件：{result['output_ranking']}")
        print(f"高优先级文件：{result['output_high_priority']}")
    except Exception as e:
        print(f"\n❌ 智能优先级打分失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
