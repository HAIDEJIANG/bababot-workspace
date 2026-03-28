#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 实时业务线索识别
在采集过程中识别 2026 年帖子的业务意图，记录高价值线索
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path

# ==================== 配置 ====================

INPUT_POSTS_FILE = Path(r"C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\contact_posts_90days.csv")
OUTPUT_LEADS_FILE = Path(r"C:\Users\Haide\Desktop\LINKEDIN\business_leads_realtime.csv")
PRIORITY_FILE = Path(r"C:\Users\Haide\Desktop\LINKEDIN\priority_ranking.csv")

# 业务意图关键词
BUY_KEYWORDS = [
    'wtb', 'want to buy', 'looking for', 'need', 'rfq', 'quote', 
    'buy', 'purchase', 'procurement', 'sourcing', 'require'
]

SELL_KEYWORDS = [
    'wts', 'for sale', 'available', 'selling', 'offer', 'sell',
    'stock', 'inventory', 'supply', 'provide'
]

PARTNERSHIP_KEYWORDS = [
    'partnership', 'collaboration', 'distributor', 'dealer',
    'agent', 'representative', 'joint venture'
]

URGENT_KEYWORDS = [
    'urgent', 'aog', 'immediate', 'asap', 'emergency'
]

# ==================== 工具函数 ====================

def analyze_intent(post_content):
    """分析发帖内容的业务意图"""
    if not post_content:
        return None
    
    content = str(post_content).lower()
    
    intents = []
    
    # 检查紧急程度
    is_urgent = any(kw in content for kw in URGENT_KEYWORDS)
    
    # 检查业务意图
    if any(kw in content for kw in BUY_KEYWORDS):
        intents.append('采购意向')
    if any(kw in content for kw in SELL_KEYWORDS):
        intents.append('出售意向')
    if any(kw in content for kw in PARTNERSHIP_KEYWORDS):
        intents.append('合作意向')
    
    if intents:
        urgency = '🔴 紧急' if is_urgent else '🟢 普通'
        return f"{urgency} - {', '.join(intents)}"
    
    return None

def extract_business_summary(post_content, intent):
    """提取业务信息概要"""
    if not post_content:
        return ''
    
    # 提取 PN 号
    import re
    pn_pattern = r'\b[A-Z0-9]{4,}(?:-[A-Z0-9]+)*\b'
    pns = re.findall(pn_pattern, str(post_content))
    
    # 提取关键词
    keywords = []
    for kw in BUY_KEYWORDS + SELL_KEYWORDS + PARTNERSHIP_KEYWORDS:
        if kw in str(post_content).lower():
            keywords.append(kw.upper())
    
    summary_parts = []
    if pns:
        summary_parts.append(f"PN: {', '.join(pns[:5])}")
    if keywords:
        summary_parts.append(f"关键词：{', '.join(set(keywords)[:5])}")
    if 'urgent' in str(post_content).lower() or 'aog' in str(post_content).lower():
        summary_parts.append("⚠️ 紧急需求")
    
    return ' | '.join(summary_parts) if summary_parts else post_content[:100]

def get_recommended_action(intent):
    """根据业务意图推荐跟进动作"""
    if not intent:
        return '保持关注'
    
    if '紧急' in intent:
        return '🔥 立即联系（24 小时内）'
    elif '采购意向' in intent:
        return '💰 准备报价（1-2 天）'
    elif '出售意向' in intent:
        return '📦 评估库存（2-3 天）'
    elif '合作意向' in intent:
        return '🤝 商务洽谈（3-5 天）'
    else:
        return '📅 定期跟进（1 周）'

# ==================== 主程序 ====================

def main():
    print("="*60)
    print("LinkedIn 实时业务线索识别")
    print("="*60)
    
    # 加载优先级打分
    priority_map = {}
    if PRIORITY_FILE.exists():
        with open(PRIORITY_FILE, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contact_id = row.get('contact_id', '')
                priority_map[contact_id] = {
                    'name': row.get('name', ''),
                    'company': row.get('company', ''),
                    'position': row.get('position', ''),
                    'total_score': row.get('total_score', ''),
                    'priority_level': row.get('priority_level', '')
                }
        print(f"已加载 {len(priority_map)} 位联系人优先级")
    
    # 检查输入文件
    if not INPUT_POSTS_FILE.exists():
        print(f"错误：输入文件不存在 - {INPUT_POSTS_FILE}")
        return
    
    # 读取发帖数据
    posts = []
    with open(INPUT_POSTS_FILE, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            posts.append(row)
    
    print(f"共读取 {len(posts)} 条发帖")
    
    # 筛选 2026 年发帖并识别业务意图
    print("\n开始识别业务线索...")
    leads = []
    
    cutoff_date = datetime(2026, 1, 1)
    
    for post in posts:
        post_date_str = post.get('post_date', '')
        if not post_date_str:
            continue
        
        try:
            post_date = datetime.fromisoformat(post_date_str.replace('Z', '+00:00'))
            if post_date < cutoff_date:
                continue
        except:
            continue
        
        post_content = post.get('post_content', '')
        intent = analyze_intent(post_content)
        
        if intent:
            contact_id = post.get('contact_id', '')
            contact_info = priority_map.get(contact_id, {})
            
            lead = {
                'contact_id': contact_id,
                'name': contact_info.get('name', post.get('contact_name', '')),
                'company': contact_info.get('company', ''),
                'position': contact_info.get('position', ''),
                'post_date': post_date_str,
                'post_content': post_content[:500],
                'post_url': post.get('post_url', ''),
                'business_intent': intent,
                'business_summary': extract_business_summary(post_content, intent),
                'priority_score': contact_info.get('total_score', ''),
                'priority_level': contact_info.get('priority_level', ''),
                'recommended_action': get_recommended_action(intent),
                'crawl_time': post.get('crawl_time', datetime.now().isoformat())
            }
            leads.append(lead)
    
    print(f"识别到 {len(leads)} 条业务线索")
    
    # 按优先级排序
    leads.sort(key=lambda x: int(x.get('priority_score', 0)), reverse=True)
    
    # 保存结果
    if leads:
        print(f"\n保存结果到：{OUTPUT_LEADS_FILE}")
        
        OUTPUT_LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(OUTPUT_LEADS_FILE, 'w', encoding='utf-8', newline='') as f:
            fieldnames = [
                'contact_id', 'name', 'company', 'position',
                'post_date', 'post_content', 'post_url',
                'business_intent', 'business_summary',
                'priority_score', 'priority_level', 'recommended_action',
                'crawl_time'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(leads)
        
        print(f"成功保存 {len(leads)} 条业务线索")
        
        # 显示前 10 条高价值线索
        print("\n" + "="*80)
        print("前 10 条高价值业务线索：")
        print("="*80)
        
        for i, lead in enumerate(leads[:10], 1):
            print(f"\n{i}. {lead['name']} - {lead['position']} @ {lead['company']}")
            print(f"   优先级：{lead['priority_level']} ({lead['priority_score']}分)")
            print(f"   发帖日期：{lead['post_date'][:10]}")
            print(f"   业务意图：{lead['business_intent']}")
            print(f"   业务概要：{lead['business_summary']}")
            print(f"   推荐动作：{lead['recommended_action']}")
        
        print("\n" + "="*60)
    else:
        print("\n未发现业务线索（可能是发帖内容不包含业务关键词）")
    
    print("="*60)
    print("业务线索识别完成！")
    if leads:
        print(f"输出文件：{OUTPUT_LEADS_FILE}")
    print("="*60)

if __name__ == '__main__':
    main()
