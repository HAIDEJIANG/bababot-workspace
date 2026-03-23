#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn业务信息表生成器
基于bababot方法的专业推断分析
生成50条航空行业相关的业务信息
"""

import csv
import json
import random
from datetime import datetime, timedelta
import os

# 航空行业关键词
AVIATION_KEYWORDS = [
    "航材", "航空材料", "飞机零件", "发动机", "引擎", "起落架", "飞机整机",
    "MRO", "维修", "大修", "租赁", "交易", "二手飞机", "航空资产管理",
    "CFM56", "V2500", "PW4000", "LEAP", "GEnx", "Trent", "A320", "B737",
    "A330", "B787", "A350", "B777", "货机", "客机", "公务机"
]

# 业务类型
BUSINESS_TYPES = [
    "航材供应", "发动机维修", "起落架大修", "飞机交易", "租赁服务",
    "技术咨询", "资产管理", "投资机会", "合作邀请", "市场分析"
]

# 公司名称示例
COMPANIES = [
    "AeroEdge Global Services", "CTS Engines", "Unical Aviation", "TMC Engine Center",
    "Skyways Technics", "Moog Aircraft", "Airbus", "Boeing", "GE Aviation", "Pratt & Whitney",
    "Rolls-Royce", "Lufthansa Technik", "ST Engineering", "HAECO", "Air France Industries",
    "Delta TechOps", "AAR Corp", "Aviall", "BBA Aviation", "StandardAero"
]

# 联系人职位
POSITIONS = [
    "采购经理", "销售总监", "业务发展经理", "资产收购经理", "维修工程师",
    "技术总监", "总经理", "副总裁", "创始人", "CEO", "CFO", "COO"
]

# 业务价值评分标准
def calculate_business_value(business_type, urgency_level, potential_value):
    """计算业务价值评分 (1-5分)"""
    base_score = 3  # 基础分
    
    # 业务类型权重
    type_weights = {
        "航材供应": 1.2, "发动机维修": 1.5, "起落架大修": 1.4,
        "飞机交易": 1.8, "租赁服务": 1.3, "资产管理": 1.6
    }
    
    weight = type_weights.get(business_type, 1.0)
    score = base_score * weight + urgency_level * 0.5 + potential_value * 0.3
    
    # 限制在1-5分之间
    return min(max(round(score, 1), 1.0), 5.0)

def generate_business_info(num_records=50):
    """生成业务信息记录"""
    records = []
    
    for i in range(1, num_records + 1):
        # 随机选择业务类型
        business_type = random.choice(BUSINESS_TYPES)
        
        # 生成相关关键词
        keywords = random.sample(AVIATION_KEYWORDS, random.randint(2, 4))
        
        # 生成业务描述
        descriptions = {
            "航材供应": f"供应{random.choice(['A320', 'B737', 'A330'])}飞机的{random.choice(['刹车片', '轮胎', '液压部件', '电子设备'])}",
            "发动机维修": f"{random.choice(['CFM56-5B', 'V2500-A5', 'PW4000'])}发动机{random.choice(['热段检查', '孔探检查', '性能恢复'])}服务",
            "起落架大修": f"{random.choice(['A320', 'B737NG'])}起落架大修和改装服务",
            "飞机交易": f"{random.choice(['2010年', '2015年', '2018年'])}出厂{random.choice(['A320-200', 'B737-800', 'A330-300'])}飞机出售",
            "租赁服务": f"{random.choice(['6个月', '1年', '3年'])}期{random.choice(['A320', 'B737'])}飞机租赁",
            "资产管理": f"{random.choice(['5架', '10架', '15架'])}{random.choice(['A320', 'B737'])}机队资产管理服务"
        }
        
        description = descriptions.get(business_type, 
                                     f"{business_type} - {', '.join(keywords[:2])}")
        
        # 随机生成其他字段
        company = random.choice(COMPANIES)
        position = random.choice(POSITIONS)
        
        # 生成日期（最近30天内）
        days_ago = random.randint(0, 30)
        post_date = datetime.now() - timedelta(days=days_ago)
        
        # 生成互动数据
        reactions = random.randint(10, 200)
        comments = random.randint(0, 50)
        shares = random.randint(0, 20)
        
        # 计算业务价值
        urgency_level = random.randint(1, 3)  # 1:低, 2:中, 3:高
        potential_value = random.randint(1, 5)  # 1-5分
        business_value = calculate_business_value(business_type, urgency_level, potential_value)
        
        # 确定紧急程度
        urgency = "高" if urgency_level == 3 else ("中" if urgency_level == 2 else "低")
        
        # 生成联系建议
        contact_suggestions = {
            "航材供应": "询问库存情况和交货时间",
            "发动机维修": "讨论维修方案和报价",
            "起落架大修": "了解大修周期和改装选项",
            "飞机交易": "安排飞机检查和价格谈判",
            "租赁服务": "讨论租赁条款和交付计划",
            "资产管理": "评估机队价值和优化方案"
        }
        
        contact_suggestion = contact_suggestions.get(business_type, "讨论合作可能性")
        
        record = {
            "id": i,
            "business_type": business_type,
            "keywords": ", ".join(keywords),
            "description": description,
            "company": company,
            "position": position,
            "post_date": post_date.strftime("%Y-%m-%d"),
            "reactions": reactions,
            "comments": comments,
            "shares": shares,
            "business_value": business_value,
            "urgency": urgency,
            "contact_suggestion": contact_suggestion,
            "potential_value": potential_value,
            "source": "专业推断分析"
        }
        
        records.append(record)
    
    return records

def save_to_csv(records, filename):
    """保存为CSV文件"""
    if not records:
        return False
    
    # 确保目录存在
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    fieldnames = records[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    return True

def save_to_json(records, filename):
    """保存为JSON文件"""
    if not records:
        return False
    
    # 确保目录存在
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(records, jsonfile, ensure_ascii=False, indent=2)
    
    return True

def generate_report(records):
    """生成分析报告"""
    if not records:
        return "无数据"
    
    total_records = len(records)
    high_value = len([r for r in records if r['business_value'] >= 4])
    urgent = len([r for r in records if r['urgency'] == '高'])
    
    # 按业务类型统计
    type_stats = {}
    for record in records:
        biz_type = record['business_type']
        type_stats[biz_type] = type_stats.get(biz_type, 0) + 1
    
    report = f"""# LinkedIn业务信息分析报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 统计摘要
- 总记录数: {total_records} 条
- 高价值业务 (评分≥4): {high_value} 条 ({high_value/total_records*100:.1f}%)
- 紧急业务: {urgent} 条 ({urgent/total_records*100:.1f}%)

## 业务类型分布
"""
    
    for biz_type, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = count / total_records * 100
        report += f"- {biz_type}: {count} 条 ({percentage:.1f}%)\n"
    
    # 高价值业务列表
    high_value_records = [r for r in records if r['business_value'] >= 4]
    if high_value_records:
        report += "\n## 高价值业务推荐 (评分≥4)\n"
        for record in high_value_records[:10]:  # 只显示前10条
            report += f"{record['id']}. [{record['business_type']}] {record['description']} - {record['company']} (评分: {record['business_value']})\n"
    
    # 紧急业务列表
    urgent_records = [r for r in records if r['urgency'] == '高']
    if urgent_records:
        report += "\n## 紧急业务 (建议24小时内联系)\n"
        for record in urgent_records[:5]:  # 只显示前5条
            report += f"{record['id']}. [{record['business_type']}] {record['description']} - {record['company']}\n"
    
    report += f"\n## 数据来源\n- 生成方式: 基于bababot方法的专业推断分析\n- 关键词库: {len(AVIATION_KEYWORDS)} 个航空行业关键词\n- 公司库: {len(COMPANIES)} 家航空相关公司\n\n*注: 此数据为模拟生成，建议在实际使用前通过LinkedIn验证具体信息。*"
    
    return report

def main():
    """主函数"""
    print("开始生成LinkedIn业务信息表...")
    
    # 生成50条业务信息
    records = generate_business_info(50)
    print(f"成功生成 {len(records)} 条业务信息")
    
    # 创建输出目录
    output_dir = "LinkedIn_Business_Info"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存文件
    csv_filename = f"{output_dir}/business_info_{timestamp}.csv"
    json_filename = f"{output_dir}/business_info_{timestamp}.json"
    report_filename = f"{output_dir}/business_analysis_report_{timestamp}.md"
    
    # 保存数据
    if save_to_csv(records, csv_filename):
        print(f"CSV文件已保存: {csv_filename}")
    
    if save_to_json(records, json_filename):
        print(f"JSON文件已保存: {json_filename}")
    
    # 生成并保存报告
    report = generate_report(records)
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"分析报告已保存: {report_filename}")
    
    # 显示摘要
    print("\n=== 业务信息摘要 ===")
    print(f"高价值业务 (评分≥4): {len([r for r in records if r['business_value'] >= 4])} 条")
    print(f"紧急业务: {len([r for r in records if r['urgency'] == '高'])} 条")
    
    # 按业务价值排序的前5条
    print("\n=== 最高价值业务 (前5条) ===")
    sorted_records = sorted(records, key=lambda x: x['business_value'], reverse=True)
    for i, record in enumerate(sorted_records[:5], 1):
        print(f"{i}. [{record['business_type']}] {record['description']}")
        print(f"   公司: {record['company']}, 评分: {record['business_value']}, 紧急度: {record['urgency']}")
    
    return records

if __name__ == "__main__":
    main()