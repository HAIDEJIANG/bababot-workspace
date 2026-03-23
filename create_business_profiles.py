#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建业务画像报告和更新总表
"""

import json
import csv
from datetime import datetime
import os

def read_analysis_results():
    """读取分析结果"""
    analysis_file = r"C:\Users\Haide\Desktop\LINKEDIN\Analysis\linkedin_analysis_batch4_2026-02-23.json"
    with open(analysis_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_business_profiles_report(analyses):
    """创建业务画像报告"""
    report_file = r"C:\Users\Haide\Desktop\LINKEDIN\Reports\Business_Profiles_Batch4_2026-02-23.md"
    
    # 统计信息
    domain_stats = {}
    industry_stats = {}
    tag_stats = {}
    
    for analysis in analyses:
        domain = analysis.get('业务领域分类', '未知')
        industry = analysis.get('行业细分', '未知')
        tags = analysis.get('业务画像标签', [])
        
        domain_stats[domain] = domain_stats.get(domain, 0) + 1
        industry_stats[industry] = industry_stats.get(industry, 0) + 1
        
        for tag in tags:
            tag_stats[tag] = tag_stats.get(tag, 0) + 1
    
    # 生成报告
    report = f"""# 业务画像分析报告 - 批次4 (20个联系人)

## 📊 分析概览
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **分析数量**: 20个LinkedIn联系人
- **分析方法**: 专业推断分析 (基于bababot方法)
- **数据来源**: 职位信息 + 公司背景 + 航空行业知识

## 📈 统计分析

### 业务领域分布
| 排名 | 业务领域 | 人数 | 占比 | 主要标签 |
|------|----------|------|------|----------|
"""
    
    # 业务领域排名
    for i, (domain, count) in enumerate(sorted(domain_stats.items(), key=lambda x: x[1], reverse=True), 1):
        percentage = (count / len(analyses)) * 100
        # 获取该领域的主要标签
        domain_tags = []
        for analysis in analyses:
            if analysis.get('业务领域分类') == domain:
                domain_tags.extend(analysis.get('业务画像标签', []))
        
        # 统计标签频率
        from collections import Counter
        top_tags = [tag for tag, _ in Counter(domain_tags).most_common(3)]
        
        report += f"| {i} | {domain} | {count} | {percentage:.1f}% | {', '.join(top_tags)} |\n"
    
    report += """
### 行业细分分布
| 排名 | 行业细分 | 人数 | 占比 | 说明 |
|------|----------|------|------|------|
"""
    
    # 行业细分排名
    for i, (industry, count) in enumerate(sorted(industry_stats.items(), key=lambda x: x[1], reverse=True), 1):
        percentage = (count / len(analyses)) * 100
        report += f"| {i} | {industry} | {count} | {percentage:.1f}% | 航空行业相关服务 |\n"
    
    report += """
### 热门业务标签
| 排名 | 业务标签 | 出现次数 | 关联领域 |
|------|----------|----------|----------|
"""
    
    # 热门标签排名
    for i, (tag, count) in enumerate(sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)[:15], 1):
        # 查找标签关联的领域
        associated_domains = set()
        for analysis in analyses:
            if tag in analysis.get('业务画像标签', []):
                associated_domains.add(analysis.get('业务领域分类', ''))
        
        report += f"| {i} | {tag} | {count} | {', '.join(list(associated_domains)[:2])} |\n"
    
    report += """
## 🎯 业务应用指南

### 1. 航材交易相关联系人
**适用场景**: 飞机部件采购、航材供应、库存管理
"""
    
    parts_contacts = [a for a in analyses if any(kw in a.get('职位', '').lower() for kw in ['parts', 'component', 'supply', 'purchasing', 'procurement'])]
    
    for i, contact in enumerate(parts_contacts[:5], 1):
        report += f"""
#### {i}. **{contact['姓名']}** - {contact['职位']}
- **公司**: {contact['公司']}
- **业务领域**: {contact['业务领域分类']}
- **行业细分**: {contact['行业细分']}
- **业务标签**: {', '.join(contact['业务画像标签'][:5])}
- **Business Focus**: {contact['Business_Focus']}
- **联系价值**: {contact.get('工作内容总结', '')}
- **LinkedIn**: {contact['LinkedIn链接']}
"""
    
    report += """
### 2. 飞机交易相关联系人
**适用场景**: 飞机买卖、租赁、资产管理、投资
"""
    
    aircraft_contacts = [a for a in analyses if any(kw in a.get('职位', '').lower() for kw in ['acquisition', 'asset', 'sales', 'leasing', 'finance'])]
    
    for i, contact in enumerate(aircraft_contacts[:5], 1):
        report += f"""
#### {i}. **{contact['姓名']}** - {contact['职位']}
- **公司**: {contact['公司']}
- **业务领域**: {contact['业务领域分类']}
- **行业细分**: {contact['行业细分']}
- **业务标签**: {', '.join(contact['业务画像标签'][:5])}
- **Business Focus**: {contact['Business_Focus']}
- **联系价值**: {contact.get('工作内容总结', '')}
- **LinkedIn**: {contact['LinkedIn链接']}
"""
    
    report += """
### 3. 维修服务相关联系人
**适用场景**: MRO服务、技术支援、工程维修、质量控制
"""
    
    mro_contacts = [a for a in analyses if any(kw in a.get('职位', '').lower() for kw in ['mro', 'maintenance', 'technical', 'engineering', 'repair'])]
    
    for i, contact in enumerate(mro_contacts[:5], 1):
        report += f"""
#### {i}. **{contact['姓名']}** - {contact['职位']}
- **公司**: {contact['公司']}
- **业务领域**: {contact['业务领域分类']}
- **行业细分**: {contact['行业细分']}
- **业务标签**: {', '.join(contact['业务画像标签'][:5])}
- **Business Focus**: {contact['Business_Focus']}
- **联系价值**: {contact.get('工作内容总结', '')}
- **LinkedIn**: {contact['LinkedIn链接']}
"""
    
    report += f"""
## 📋 完整联系人列表 (按业务价值排序)

| 序号 | 姓名 | 职位 | 公司 | 业务领域 | 行业细分 | 业务标签 | Business Focus | 联系价值 |
|------|------|------|------|----------|----------|----------|----------------|----------|
"""
    
    # 按业务价值排序（销售/收购/资产管理优先）
    def contact_value(contact):
        position = contact.get('职位', '').lower()
        if any(kw in position for kw in ['sales', 'acquisition', 'asset', 'business development']):
            return 1
        elif any(kw in position for kw in ['manager', 'director', 'head', 'vp']):
            return 2
        else:
            return 3
    
    sorted_analyses = sorted(analyses, key=contact_value)
    
    for i, analysis in enumerate(sorted_analyses, 1):
        report += f"| {i} | {analysis['姓名']} | {analysis['职位']} | {analysis['公司']} | {analysis['业务领域分类']} | {analysis['行业细分']} | {', '.join(analysis['业务画像标签'][:3])} | {analysis['Business_Focus'][:50]}... | {analysis.get('工作内容总结', '')[:60]}... |\n"
    
    report += f"""
## 🚀 快速查找指南

### 按业务需求查找
1. **航材采购** → 查找标签: 采购专家、供应链管理、航材供应
2. **飞机交易** → 查找标签: 资产管理、投资专家、销售专家
3. **维修服务** → 查找标签: MRO专家、工程技术、质量控制
4. **业务合作** → 查找标签: 业务发展、销售专家、管理领导

### 按公司类型查找
1. **MRO公司** → Skyways Technics, CTS Engines, Moog Aircraft
2. **航空公司** → 相关运营和管理人员
3. **租赁公司** → 金融租赁相关联系人
4. **制造公司** → 部件制造商和供应商

## 💡 使用建议

### 1. 联系策略
- **优先级**: 先联系业务领域匹配度高的联系人
- **个性化**: 根据Business Focus定制联系内容
- **时机**: 工作日工作时间联系效果最佳

### 2. 关系维护
- **定期互动**: 点赞、评论对方的专业内容
- **价值提供**: 分享行业资讯、市场分析
- **专业形象**: 保持专业的沟通风格

### 3. 数据更新
- **定期分析**: 建议每季度更新业务画像
- **实际验证**: 通过互动验证分析准确性
- **标签优化**: 根据实际业务调整标签体系

## 📁 生成文件
1. **业务画像报告**: `Business_Profiles_Batch4_2026-02-23.md` (本文件)
2. **分析数据**: `linkedin_analysis_batch4_2026-02-23.json`
3. **CSV数据**: `linkedin_analysis_batch4_2026-02-23.csv`
4. **联系人总表**: `LINKEDIN_Connections_with_Profiles.csv` (新增)

## 🔄 后续计划
1. **继续分析**: 分析更多批次的联系人
2. **数据整合**: 将所有分析结果整合到统一数据库
3. **智能推荐**: 基于业务需求自动推荐联系人
4. **效果跟踪**: 跟踪联系效果并优化分析模型

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*分析方法: 专业推断分析 + 航空行业知识*
*数据质量: 基于公开信息的专业推断*
"""

    # 保存报告
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"业务画像报告已保存到: {report_file}")
    return report_file

def create_enhanced_csv(analyses):
    """创建增强的CSV文件"""
    csv_file = r"C:\Users\Haide\Desktop\LINKEDIN\Data\LINKEDIN_Connections_with_Profiles.csv"
    
    # 定义字段
    fieldnames = [
        '姓名', '职位', '公司', 'LinkedIn链接', 
        '分析时间', '分析方法', '数据质量',
        '业务领域分类', '行业细分', 
        '业务画像标签', 'Business_Focus',
        'Recent_Activity_Summary', '帖子内容分析',
        '工作内容总结', '数据分析推断',
        '航材交易相关度', '飞机交易相关度', 
        '维修服务相关度', '租赁服务相关度',
        '联系优先级', '联系建议'
    ]
    
    # 计算相关度
    enhanced_analyses = []
    for analysis in analyses:
        enhanced = analysis.copy()
        
        # 计算各项业务相关度 (1-5分)
        position = analysis.get('职位', '').lower()
        tags = analysis.get('业务画像标签', [])
        
        # 航材交易相关度
        parts_score = 1
        if any(kw in position for kw in ['parts', 'component', 'supply', 'purchasing', 'procurement']):
            parts_score = 5
        elif any(kw in position for kw in ['material', 'inventory', 'logistics']):
            parts_score = 4
        elif '采购' in position or '供应' in position:
            parts_score = 4
        enhanced['航材交易相关度'] = parts_score
        
        # 飞机交易相关度
        aircraft_score = 1
        if any(kw in position for kw in ['acquisition', 'asset', 'sales', 'leasing', 'finance']):
            aircraft_score = 5
        elif any(kw in position for kw in ['trading', 'broker', 'deal']):
            aircraft_score = 4
        enhanced['飞机交易相关度'] = aircraft_score
        
        # 维修服务相关度
        mro_score = 1
        if any(kw in position for kw in ['mro', 'maintenance', 'technical', 'engineering', 'repair']):
            mro_score = 5
        elif any(kw in position for kw in ['quality', 'inspection', 'overhaul']):
            mro_score = 4
        enhanced['维修服务相关度'] = mro_score
        
        # 租赁服务相关度
        lease_score = 1
        if any(kw in position for kw in ['leasing', 'rental', 'charter']):
            lease_score = 5
        elif '租赁' in position:
            lease_score = 4
        enhanced['租赁服务相关度'] = lease_score
        
        # 联系优先级 (基于最高相关度)
        max_score = max(parts_score, aircraft_score, mro_score, lease_score)
        enhanced['联系优先级'] = '高' if max_score >= 4 else '中' if max_score >= 3 else '低'
        
        # 联系建议
        suggestions = []
        if parts_score >= 4:
            suggestions.append('航材交易')
        if aircraft_score >= 4:
            suggestions.append('飞机交易')
        if mro_score >= 4:
            suggestions.append('维修服务')
        if lease_score >= 4:
            suggestions.append('租赁服务')
        
        if not suggestions:
            suggestions.append('业务拓展')
        
        enhanced['联系建议'] = '、'.join(suggestions)
        
        # 转换标签为字符串
        enhanced['业务画像标签'] = ';'.join(analysis.get('业务画像标签', []))
        
        enhanced_analyses.append(enhanced)
    
    # 保存CSV
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enhanced_analyses)
    
    print(f"增强的CSV文件已保存到: {csv_file}")
    return csv_file

def main():
    """主函数"""
    print("开始创建业务画像报告...")
    
    # 读取分析结果
    analyses = read_analysis_results()
    print(f"读取到 {len(analyses)} 个分析结果")
    
    # 创建业务画像报告
    report_file = create_business_profiles_report(analyses)
    
    # 创建增强的CSV文件
    csv_file = create_enhanced_csv(analyses)
    
    print(f"\n✅ 任务完成!")
    print(f"📄 业务画像报告: {report_file}")
    print(f"📊 增强数据文件: {csv_file}")
    print(f"👥 分析联系人: {len(analyses)} 个")
    
    # 显示关键联系人
    print(f"\n🎯 关键联系人发现:")
    
    # 航材交易相关
    parts_contacts = [a for a in analyses if any(kw in a.get('职位', '').lower() for kw in ['parts', 'component', 'supply', 'purchasing'])]
    print(f"  航材交易相关: {len(parts_contacts)} 人")
    
    # 飞机交易相关
    aircraft_contacts = [a for a in analyses if any(kw in a.get('职位', '').lower() for kw in ['acquisition', 'asset', 'sales'])]
    print(f"  飞机交易相关: {len(aircraft_contacts)} 人")
    
    # 维修服务相关
    mro_contacts = [a for a in analyses if any(kw in a.get('职位', '').lower() for kw in ['mro', 'maintenance', 'technical'])]
    print(f"  维修服务相关: {len(mro_contacts)} 人")

if __name__ == "__main__":
    main()