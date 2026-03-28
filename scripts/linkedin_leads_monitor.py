#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 实时业务线索监控
定期扫描新采集的发帖，识别业务意图并记录
每 10 分钟自动运行一次
"""

import csv
import json
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================

INPUT_POSTS_FILE = Path(r"C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\contact_posts_90days.csv")
OUTPUT_LEADS_FILE = Path(r"C:\Users\Haide\Desktop\LINKEDIN\business_leads_realtime.csv")
PRIORITY_FILE = Path(r"C:\Users\Haide\Desktop\LINKEDIN\priority_ranking.csv")
STATE_FILE = Path(r"C:\Users\Haide\Desktop\LINKEDIN\business_leads_state.json")

# 业务意图关键词（参考领英帖子信息采集工作）
# 广域关键词（航空业务相关）
BROAD_KEYWORDS = [
    'aircraft', 'engine', 'spare parts', 'aviation components',
    'landing gear', 'apu', 'cfm56', 'v2500', 'pw4000',
    'leap', 'trent', 'a320', 'b737', 'b777', 'a350',
    'airframe', 'mro', 'maintenance', 'overhaul',
    'rotable', 'serviceable', 'trace', 'cert'
]

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

# 紧急程度关键词
URGENT_KEYWORDS = [
    'urgent', 'aog', 'immediate', 'asap', 'emergency',
    'rush', 'priority', 'critical', 'time sensitive'
]

# 零件号格式（用于提取 PN）
PN_PATTERNS = [
    r'\b[A-Z0-9]{4,}(?:-[A-Z0-9]+)*\b',  # 标准 PN 格式
    r'\bPN\s*[:#]?\s*[A-Z0-9-]+\b',  # PN: XXXXX 格式
    r'\bPart\s*(?:Number|No\.?)\s*[:#]?\s*[A-Z0-9-]+\b',  # Part Number 格式
]

# ==================== 工具函数 ====================

def load_state():
    """加载已处理的发帖记录"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {'processed_posts': set(data.get('processed_posts', [])), 'last_check': None}
    return {'processed_posts': set(), 'last_check': None}

def save_state(state):
    """保存状态"""
    state['last_check'] = datetime.now().isoformat()
    state['processed_posts'] = list(state['processed_posts'])  # set 转 list
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def analyze_intent(post_content):
    """分析业务意图（参考领英帖子采集关键词）"""
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
    
    # 检查是否包含航空业务关键词（确保相关性）
    has_aviation_context = any(kw in content for kw in BROAD_KEYWORDS)
    
    if intents and has_aviation_context:
        urgency = '🔴 紧急' if is_urgent else '🟢 普通'
        return f"{urgency} - {', '.join(intents)}"
    elif intents:
        # 有业务意图但无航空上下文（可能是通用业务）
        urgency = '🔴 紧急' if is_urgent else '🟡 待确认'
        return f"{urgency} - {', '.join(intents)}"
    
    return None

def extract_pn_numbers(post_content):
    """提取帖子中的零件号（PN）"""
    if not post_content:
        return []
    
    pns = []
    for pattern in PN_PATTERNS:
        matches = re.findall(pattern, str(post_content), re.IGNORECASE)
        pns.extend(matches)
    
    return list(set(pns))[:10]  # 最多 10 个

def extract_business_summary(post_content, intent):
    """提取业务信息概要（参考领英帖子采集）"""
    if not post_content:
        return ''
    
    summary_parts = []
    
    # 提取 PN 号
    pns = extract_pn_numbers(post_content)
    if pns:
        summary_parts.append(f"PN: {', '.join(pns[:5])}")
    
    # 提取业务关键词
    keywords = []
    all_intent_keywords = BUY_KEYWORDS + SELL_KEYWORDS + PARTNERSHIP_KEYWORDS
    for kw in all_intent_keywords:
        if kw in str(post_content).lower():
            keywords.append(kw.upper())
    
    if keywords:
        summary_parts.append(f"关键词：{', '.join(set(keywords)[:5])}")
    
    # 提取航空业务类型
    aviation_types = []
    for kw in BROAD_KEYWORDS:
        if kw in str(post_content).lower():
            aviation_types.append(kw.upper())
    
    if aviation_types:
        summary_parts.append(f"业务类型：{', '.join(set(aviation_types)[:3])}")
    
    # 紧急标记
    if any(kw in str(post_content).lower() for kw in URGENT_KEYWORDS):
        summary_parts.append("⚠️ 紧急需求")
    
    # 如果有 PN 号，优先显示
    if pns:
        return ' | '.join(summary_parts)
    
    # 否则返回帖子前 150 字
    return str(post_content)[:150] + ('...' if len(str(post_content)) > 150 else '')

def get_recommended_action(intent, priority_score):
    """推荐跟进动作（考虑优先级分数）"""
    if not intent:
        return '保持关注'
    
    # 高优先级 + 紧急 = 最高优先级
    if '紧急' in intent and int(priority_score) >= 80:
        return '🔥 最高优先级 - 立即联系（24 小时内）'
    elif '紧急' in intent:
        return '🔥 紧急 - 立即联系（24 小时内）'
    elif '采购意向' in intent and int(priority_score) >= 80:
        return '💰 高优先级采购 - 准备报价（1 天内）'
    elif '采购意向' in intent:
        return '💰 采购意向 - 准备报价（1-2 天）'
    elif '出售意向' in intent and int(priority_score) >= 80:
        return '📦 高优先级供应 - 评估库存（1 天内）'
    elif '出售意向' in intent:
        return '📦 供应意向 - 评估库存（2-3 天）'
    elif '合作意向' in intent:
        return '🤝 合作意向 - 商务洽谈（3-5 天）'
    else:
        return '📅 定期跟进（1 周）'

# ==================== 主程序 ====================

def main():
    print("="*60)
    print("LinkedIn 实时业务线索监控")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 加载状态
    state = load_state()
    processed = set(state.get('processed_posts', []))
    
    # 加载优先级
    priority_map = {}
    if PRIORITY_FILE.exists():
        with open(PRIORITY_FILE, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                priority_map[row.get('contact_id', '')] = row
    
    # 检查发帖文件
    if not INPUT_POSTS_FILE.exists():
        print("发帖文件不存在，等待采集...")
        return
    
    # 读取新发帖
    new_posts = []
    with open(INPUT_POSTS_FILE, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            post_id = f"{row.get('contact_id', '')}_{row.get('post_date', '')}_{row.get('crawl_time', '')}"
            if post_id not in processed:
                new_posts.append(row)
    
    print(f"发现 {len(new_posts)} 条新发帖")
    
    if not new_posts:
        print("无新发帖")
        save_state(state)
        return
    
    # 识别业务线索
    new_leads = []
    cutoff_date = datetime(2026, 1, 1)
    
    for post in new_posts:
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
                'recommended_action': get_recommended_action(intent, contact_info.get('total_score', 0)),
                'discovered_at': datetime.now().isoformat()
            }
            new_leads.append(lead)
            processed.add(f"{contact_id}_{post_date_str}_{post.get('crawl_time', '')}")
    
    print(f"识别到 {len(new_leads)} 条新业务线索")
    
    # 保存线索
    if new_leads:
        is_new_file = not OUTPUT_LEADS_FILE.exists()
        mode = 'a' if not is_new_file else 'w'
        
        with open(OUTPUT_LEADS_FILE, mode, encoding='utf-8', newline='') as f:
            fieldnames = [
                'contact_id', 'name', 'company', 'position',
                'post_date', 'post_content', 'post_url',
                'business_intent', 'business_summary',
                'priority_score', 'priority_level',
                'recommended_action', 'discovered_at'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if is_new_file:
                writer.writeheader()
            writer.writerows(new_leads)
        
        print(f"\n已追加 {len(new_leads)} 条线索到：{OUTPUT_LEADS_FILE}")
        
        # 显示新线索
        print("\n" + "="*80)
        print("新发现的业务线索：")
        print("="*80)
        
        for i, lead in enumerate(new_leads, 1):
            print(f"\n{i}. {lead['name']} - {lead['position']} @ {lead['company']}")
            print(f"   优先级：{lead['priority_level']} ({lead['priority_score']}分)")
            print(f"   发帖日期：{lead['post_date'][:10]}")
            print(f"   业务意图：{lead['business_intent']}")
            print(f"   业务概要：{lead['business_summary']}")
            print(f"   推荐动作：{lead['recommended_action']}")
            if lead.get('post_url'):
                print(f"   帖子链接：{lead['post_url']}")
        
        print("\n" + "="*60)
    
    # 保存状态
    state['processed_posts'] = list(processed)
    save_state(state)
    
    print("="*60)
    print("监控完成！下次检查：10 分钟后")
    print("="*60)

if __name__ == '__main__':
    main()
