#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 联系人优先级打分脚本 v1.0
根据职位、公司、连接数、发帖等维度自动打分
输出：priority_ranking.csv
"""

import csv
import re
from datetime import datetime, timedelta
from pathlib import Path

# ==================== 配置 ====================

INPUT_FILE = Path(r"C:\Users\Haide\Desktop\OPENCLAW\LINKEDIN\LINKEDIN Connections_with_posts_FINAL.csv")
OUTPUT_FILE = Path(r"C:\Users\Haide\Desktop\LINKEDIN\priority_ranking.csv")

# ==================== 打分标准 ====================

# 职位相关性（40 分）- 核心岗位满分
POSITION_KEYWORDS = {
    # 管理层（40 分）
    'ceo': 40, 'coo': 40, 'cfo': 40, 'cto': 40, 'cio': 40,
    'president': 40, 'vp': 40, 'director': 40,
    'general manager': 40, 'managing director': 40,
    'vice president': 40, 'executive director': 40,
    
    # 高级管理人员（40 分）
    'senior vp': 40, 'executive vp': 40, 'senior vice president': 40,
    'head of': 40, 'chief': 40, 'partner': 40, 'founder': 40,
    'co-founder': 40, 'owner': 40, 'principal': 40,
    
    # Business Development（40 分）
    'business development': 40, 'bd': 40,
    'strategic development': 40, 'growth': 40,
    'business manager': 40, 'development manager': 40,
    
    # 采购（40 分）
    'purchasing': 40, 'procurement': 40, 'buyer': 40,
    'sourcing': 40, 'supply chain': 40, 'materials': 40,
    'purchasing manager': 40, 'procurement manager': 40,
    'supply manager': 40, 'logistics manager': 40,
    
    # 销售（40 分）
    'sales': 40, 'account manager': 40,
    'regional sales': 40, 'commercial': 40,
    'sales manager': 40, 'sales director': 40,
    'account executive': 40, 'business manager': 40,
    
    # 工程（40 分）
    'engineer': 40, 'engineering': 40, 'technical': 40,
    'maintenance': 40, 'mro': 40, 'powerplant': 40,
    'engine': 40, 'aircraft': 40, 'avionics': 40,
    'mechanic': 40, 'technician': 40,
    
    # 资产交易（40 分）
    'trading': 40, 'asset trading': 40,
    'engine trading': 40, 'aircraft trading': 40, 'leasing': 40,
    'trader': 40, 'deal': 40, 'broker': 40,
    
    # 资产管理（40 分）
    'asset management': 40, 'fleet management': 40,
    'portfolio management': 40, 'asset manager': 40,
    'fleet manager': 40, 'portfolio manager': 40,
    
    # 中国区域（40 分）
    'china': 40, 'greater china': 40,
    'apac': 40, 'asia pacific': 40, 'asia': 40,
    'regional': 40, 'area manager': 40,
    
    # 其他（30 分）
    'consultant': 30, 'advisor': 30, 'analyst': 30,
    'operations': 30, 'logistics': 30, 'planning': 30,
    'project': 30, 'program': 30,
    
    # 支持岗位（20 分）
    'support': 20, 'admin': 20, 'hr': 20, 'finance': 20,
    'assistant': 20, 'coordinator': 20, 'specialist': 25,
}

# 公司类型（25 分）
COMPANY_KEYWORDS = {
    'airlines': 25, 'airways': 25, 'cargo': 25, 'air': 25,
    'mro': 25, 'maintenance': 25, 'engineering': 25,
    'technics': 25, 'engine center': 25,
    'parts': 23, 'components': 23, 'spares': 23,
    'trading': 23, 'distribution': 23, 'supply': 23,
    'lease': 20, 'capital': 20, 'asset management': 20,
    'consulting': 18, 'advisory': 18, 'services': 18,
    'media': 15, 'association': 15, 'society': 15,
}

# ==================== 工具函数 ====================

def clean_text(text):
    """清理文本，转为小写"""
    if not text:
        return ''
    return str(text).lower().strip()

def calculate_position_score(position, company):
    """计算职位相关性分数（0-40）"""
    position_lower = clean_text(position)
    company_lower = clean_text(company)
    combined = f"{position_lower} {company_lower}"
    
    # 检查是否包含关键词
    for keyword, score in POSITION_KEYWORDS.items():
        if keyword in combined:
            return score
    
    # 默认分数
    return 25

def calculate_company_score(company):
    """计算公司类型分数（0-25）"""
    company_lower = clean_text(company)
    
    for keyword, score in COMPANY_KEYWORDS.items():
        if keyword in company_lower:
            return score
    
    # 默认分数（未知公司类型）
    return 15

def calculate_time_score(connected_on):
    """计算连接时间分数（0-5）"""
    if not connected_on:
        return 3  # 默认中等分数
    
    try:
        # 解析日期（格式：DD-MMM-YY，如 18-Feb-26）
        date_str = clean_text(connected_on)
        # 尝试多种格式
        for fmt in ['%d-%b-%y', '%d %b %y', '%Y-%m-%d']:
            try:
                connected_date = datetime.strptime(date_str, fmt)
                days = (datetime.now() - connected_date).days
                
                if days <= 90: return 5
                elif days <= 180: return 4
                elif days <= 365: return 3
                elif days <= 730: return 2
                else: return 1
            except ValueError:
                continue
        
        return 3  # 无法解析时返回默认值
    except Exception as e:
        return 3

def calculate_connection_score(connections):
    """计算连接数分数（0-25）"""
    if not connections:
        return 15  # 默认中等分数
    
    conn_str = str(connections).lower().strip()
    
    # 处理 "500+" 格式
    if '500+' in conn_str or '500' in conn_str:
        return 25
    
    # 尝试提取数字
    try:
        # 移除非数字字符
        numbers = re.findall(r'\d+', conn_str)
        if numbers:
            count = int(numbers[0])
            if count >= 500: return 25
            elif count >= 200: return 20
            elif count >= 100: return 15
            elif count >= 50: return 10
            else: return 5
    except:
        pass
    
    return 15  # 默认分数

def calculate_post_score(post_count):
    """计算发帖活跃度分数（0-15）"""
    try:
        count = int(post_count) if post_count else 0
        if count >= 10: return 15
        elif count >= 5: return 12
        elif count >= 3: return 10
        elif count >= 1: return 8
        else: return 5
    except:
        return 5

def calculate_business_intent_bonus(post_content):
    """计算业务意图加分（0-5）"""
    if not post_content:
        return 0
    
    content_lower = clean_text(post_content)
    
    # 出售/供应
    if any(kw in content_lower for kw in ['wts', 'for sale', 'available', 'selling', 'offer']):
        return 5
    
    # 采购/询价
    if any(kw in content_lower for kw in ['wtb', 'rfq', 'looking for', 'need', 'want to buy', 'quote']):
        return 5
    
    # 行业洞察
    if any(kw in content_lower for kw in ['industry insights', 'market trends', 'analysis']):
        return 3
    
    # 公司动态
    if any(kw in content_lower for kw in ['company update', 'news', 'announcement']):
        return 2
    
    return 0

def get_priority_level(total_score):
    """根据总分确定优先级等级"""
    if total_score >= 80:
        return '⭐⭐⭐ 高优先级'
    elif total_score >= 60:
        return '⭐⭐ 中优先级'
    else:
        return '⭐ 低优先级'

# ==================== 主程序 ====================

def main():
    print("="*60)
    print("LinkedIn 联系人优先级打分 v1.0")
    print("="*60)
    
    # 检查输入文件
    if not INPUT_FILE.exists():
        print(f"错误：输入文件不存在 - {INPUT_FILE}")
        return
    
    # 读取输入数据
    contacts = []
    print(f"读取输入文件：{INPUT_FILE}")
    
    with open(INPUT_FILE, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)
    
    print(f"共读取 {len(contacts)} 位联系人")
    print()
    
    # 打分
    print("开始打分...")
    results = []
    
    for i, contact in enumerate(contacts):
        # 提取字段
        first_name = contact.get('First Name', '')
        last_name = contact.get('Last Name', '')
        name = f"{first_name} {last_name}".strip()
        company = contact.get('Company', '')
        position = contact.get('Position', '')
        connected_on = contact.get('Connected On', '')
        connections = contact.get('connections', '500+')  # 假设有连接数字段，或使用默认值
        
        # 计算各维度分数
        position_score = calculate_position_score(position, company)
        company_score = calculate_company_score(company)
        time_score = calculate_time_score(connected_on)
        connection_score = calculate_connection_score(connections)
        post_score = 5  # 默认发帖分数（后续可补充真实发帖数据）
        intent_bonus = 0  # 默认无业务意图加分
        
        # 总分
        total_score = position_score + company_score + time_score + connection_score + post_score + intent_bonus
        
        # 优先级等级
        priority_level = get_priority_level(total_score)
        
        # 保存结果
        result = {
            'contact_id': contact.get('URL', ''),
            'name': name,
            'company': company,
            'position': position,
            'connected_on': connected_on,
            'position_score': position_score,
            'company_score': company_score,
            'connection_time_score': time_score,
            'connection_count_score': connection_score,
            'post_activity_score': post_score,
            'business_intent_bonus': intent_bonus,
            'total_score': total_score,
            'priority_level': priority_level,
        }
        results.append(result)
        
        # 进度显示
        if (i + 1) % 500 == 0:
            print(f"  已处理 {i+1}/{len(contacts)} 位联系人")
    
    print(f"打分完成！")
    print()
    
    # 统计分布
    high_priority = sum(1 for r in results if r['total_score'] >= 80)
    medium_priority = sum(1 for r in results if 60 <= r['total_score'] < 80)
    low_priority = sum(1 for r in results if r['total_score'] < 60)
    
    print("优先级分布：")
    print(f"  [HIGH] 高优先级（80-120 分）: {high_priority} 人 ({high_priority/len(results)*100:.1f}%)")
    print(f"  [MED]  中优先级（60-79 分）: {medium_priority} 人 ({medium_priority/len(results)*100:.1f}%)")
    print(f"  [LOW]  低优先级（0-59 分）: {low_priority} 人 ({low_priority/len(results)*100:.1f}%)")
    print()
    
    # 保存结果
    print(f"保存结果到：{OUTPUT_FILE}")
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            'contact_id', 'name', 'company', 'position', 'connected_on',
            'position_score', 'company_score', 'connection_time_score',
            'connection_count_score', 'post_activity_score', 'business_intent_bonus',
            'total_score', 'priority_level'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"成功保存 {len(results)} 条记录")
    print()
    
    # 显示前 10 位高优先级联系人
    print("前 10 位高优先级联系人：")
    print("="*80)
    
    high_priority_contacts = sorted(
        [r for r in results if r['total_score'] >= 80],
        key=lambda x: x['total_score'],
        reverse=True
    )[:10]
    
    for i, contact in enumerate(high_priority_contacts, 1):
        print(f"{i}. {contact['name']} - {contact['position']} @ {contact['company']}")
        print(f"   总分：{contact['total_score']} 分")
        print(f"   细分：职位{contact['position_score']} + 公司{contact['company_score']} + "
              f"时间{contact['connection_time_score']} + 连接{contact['connection_count_score']} + "
              f"发帖{contact['post_activity_score']}")
        print()
    
    print("="*60)
    print("打分完成！")
    print(f"输出文件：{OUTPUT_FILE}")
    print("="*60)

if __name__ == '__main__':
    main()
