#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
线索筛选 Sub-Agent - 筛选高价值业务线索，生成跟进建议
基于意图分析结果，筛选高优先级线索
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
INPUT_INTENTS = Path(r"C:\Users\Haide\Desktop\LINKEDIN\linkedin_business_intents.csv")
INPUT_PRIORITY = Path(r"C:\Users\Haide\Desktop\LINKEDIN\priority_ranking.csv")

# 输出文件
OUTPUT_LEADS = Path(r"C:\Users\Haide\Desktop\LINKEDIN\linkedin_high_value_leads.csv")
OUTPUT_ACTIONS = Path(r"C:\Users\Haide\Desktop\LINKEDIN\linkedin_recommended_actions.csv")

# 高价值线索筛选标准
MIN_PRIORITY_SCORE = 80  # 最低优先级分数
MIN_COMBINED_SCORE = 90  # 最低综合分数

# ==================== Sub-Agent ====================

class LeadScreeningSubAgent(SubAgentBase):
    """线索筛选 Sub-Agent"""
    
    def __init__(self):
        super().__init__('lead_screening')
        self.input_files = {
            'intents': INPUT_INTENTS,
            'priority': INPUT_PRIORITY
        }
        self.output_files = {
            'leads': OUTPUT_LEADS,
            'actions': OUTPUT_ACTIONS
        }
    
    def get_recommended_action(self, intent, priority_score, combined_score):
        """生成推荐跟进动作"""
        actions = []
        
        # 基于紧急程度
        if '🔴 紧急' in intent:
            actions.append('立即联系（24 小时内）')
        elif priority_score >= 100 or combined_score >= 110:
            actions.append('优先联系（48 小时内）')
        elif priority_score >= 80 or combined_score >= 90:
            actions.append('常规跟进（1 周内）')
        else:
            actions.append('保持关注')
        
        # 基于意图类型
        if '采购意向' in intent:
            actions.append('准备报价方案')
        if '出售意向' in intent:
            actions.append('评估库存匹配')
        if '合作意向' in intent:
            actions.append('安排商务洽谈')
        
        # 基于职位
        if 'CEO' in str(intent) or 'President' in str(intent) or 'Director' in str(intent):
            actions.append('高层对接')
        
        return ' | '.join(actions)
    
    def generate_follow_up_template(self, name, company, intent):
        """生成跟进话术模板"""
        templates = {
            '采购意向': f"""尊敬的{name}先生/女士，

您好！关注到贵司（{company}）有采购需求，我们专业提供航空零部件供应服务。

我们的优势：
- 现货库存充足
- 快速交付（24-48 小时）
- 质量保证（提供证书）
- 有竞争力的价格

如有具体 PN 号需求，请随时告知，我们将立即为您报价。

顺祝商祺！""",
            
            '出售意向': f"""尊敬的{name}先生/女士，

您好！关注到贵司（{company}）有库存出售，我们可能有采购需求。

请告知：
- 具体 PN 号和数量
- 产品条件和证书
- 期望价格

我们会快速评估并给您反馈。

顺祝商祺！""",
            
            '合作意向': f"""尊敬的{name}先生/女士，

您好！关注到贵司（{company}）有合作意向，我们很感兴趣。

我们可以探讨的合作方向：
- 供应链合作
- 库存共享
- 联合开发市场

期待与您进一步沟通。

顺祝商祺！"""
        }
        
        # 选择最匹配的模板
        if '采购意向' in intent:
            return templates['采购意向']
        elif '出售意向' in intent:
            return templates['出售意向']
        elif '合作意向' in intent:
            return templates['合作意向']
        else:
            return templates['采购意向']
    
    def execute(self):
        """执行线索筛选"""
        self.log("开始加载输入文件...", 'INFO')
        
        # 读取意图分析结果
        with resource_manager.acquire_file(str(self.input_files['intents']), self.run_id):
            if self.input_files['intents'].exists():
                intents_df = pd.read_csv(self.input_files['intents'], encoding='utf-8', errors='replace')
            else:
                self.log("警告：意图分析文件不存在", 'WARNING')
                intents_df = pd.DataFrame()
        
        self.update_progress(20, 100)
        self.log(f"已加载：意图数据{len(intents_df)}条", 'INFO')
        
        if intents_df.empty:
            self.log("无意图数据，跳过筛选", 'WARNING')
            return {
                'total_analyzed': 0,
                'high_value_leads': 0,
                'output_file': None
            }
        
        # 筛选高价值线索
        self.log("开始筛选高价值线索...", 'INFO')
        
        # 筛选标准：综合优先级 >= MIN_COMBINED_SCORE
        high_value_leads = intents_df[intents_df['combined_priority_score'] >= MIN_COMBINED_SCORE].copy()
        
        self.update_progress(50, 100)
        self.log(f"筛选出{len(high_value_leads)}条高价值线索", 'INFO')
        
        # 生成推荐动作
        self.log("生成推荐跟进动作...", 'INFO')
        
        high_value_leads['recommended_action'] = high_value_leads.apply(
            lambda row: self.get_recommended_action(
                row['business_intent'],
                row['original_priority_score'],
                row['combined_priority_score']
            ),
            axis=1
        )
        
        # 生成跟进话术模板
        high_value_leads['follow_up_template'] = high_value_leads.apply(
            lambda row: self.generate_follow_up_template(
                row['name'],
                row['company'],
                row['business_intent']
            ),
            axis=1
        )
        
        # 按综合优先级排序
        high_value_leads = high_value_leads.sort_values('combined_priority_score', ascending=False)
        
        self.update_progress(80, 100)
        
        # 保存高价值线索
        self.log("保存高价值线索...", 'INFO')
        
        with resource_manager.acquire_file(str(self.output_files['leads']), self.run_id):
            high_value_leads.to_csv(self.output_files['leads'], index=False, encoding='utf-8-sig')
        
        # 保存推荐动作（简化版）
        actions_df = high_value_leads[[
            'contact_id', 'name', 'company', 'position',
            'business_intent', 'combined_priority_score', 'recommended_action'
        ]].copy()
        
        with resource_manager.acquire_file(str(self.output_files['actions']), self.run_id):
            actions_df.to_csv(self.output_files['actions'], index=False, encoding='utf-8-sig')
        
        self.update_progress(100, 100)
        
        # 统计
        intent_counts = high_value_leads['business_intent'].value_counts()
        self.log("高价值线索分布：", 'INFO')
        for intent, count in intent_counts.items():
            self.log(f"  {intent}: {count}条", 'INFO')
        
        return {
            'total_analyzed': len(intents_df),
            'high_value_leads': len(high_value_leads),
            'output_leads': str(self.output_files['leads']),
            'output_actions': str(self.output_files['actions'])
        }

# ==================== 主程序 ====================

if __name__ == '__main__':
    agent = LeadScreeningSubAgent()
    
    try:
        result = agent.execute_with_retry()
        print(f"\n✅ 线索筛选完成！")
        print(f"分析意图：{result['total_analyzed']}条")
        print(f"高价值线索：{result['high_value_leads']}条")
        if result.get('output_leads'):
            print(f"线索文件：{result['output_leads']}")
            print(f"动作文件：{result['output_actions']}")
    except Exception as e:
        print(f"\n❌ 线索筛选失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
