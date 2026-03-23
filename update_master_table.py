#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新LinkedIn总表，将分析结果合并到总表中
"""

import csv
import json
from datetime import datetime
import os

def read_analysis_results(json_file):
    """读取分析结果"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_master_csv(csv_file):
    """读取主CSV文件"""
    contacts = []
    with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)
    return contacts, reader.fieldnames

def find_contact_by_name(contacts, first_name, last_name):
    """根据姓名查找联系人"""
    for contact in contacts:
        if (contact.get('First Name', '') == first_name and 
            contact.get('Last Name', '') == last_name):
            return contact
    return None

def update_contact_with_analysis(contact, analysis):
    """用分析结果更新联系人信息"""
    # 更新分析状态
    contact['Analysis Status'] = '已分析'
    
    # 添加分析字段
    contact['业务领域分类'] = analysis.get('业务领域分类', '')
    contact['行业细分'] = analysis.get('行业细分', '')
    contact['数据分析推断'] = analysis.get('数据分析推断', '')
    contact['帖子内容分析'] = analysis.get('帖子内容分析', '')
    contact['工作内容总结'] = analysis.get('工作内容总结', '')
    contact['Recent_Activity_Summary'] = analysis.get('Recent_Activity_Summary', '')
    contact['Business_Focus'] = analysis.get('Business_Focus', '')
    contact['Analysis_Method_Bababot'] = analysis.get('分析方法', '')
    contact['Analysis_Time_Bababot'] = analysis.get('分析时间', '')
    contact['Data_Quality_Bababot'] = analysis.get('数据质量', '')
    contact['Notes_Bababot'] = '基于职位和公司信息的专业推断分析'
    
    # 添加业务画像标签
    tags = analysis.get('业务画像标签', [])
    contact['业务画像标签'] = ';'.join(tags[:5])  # 最多5个标签
    
    return contact

def main():
    """主函数"""
    print("开始更新LinkedIn总表...")
    
    # 文件路径
    analysis_file = r"C:\Users\Haide\Desktop\LINKEDIN\Analysis\linkedin_analysis_batch4_2026-02-23.json"
    master_csv = r"C:\Users\Haide\Desktop\LINKEDIN\Data\LINKEDIN Connections_bababot_style_FINAL.csv"
    backup_csv = r"C:\Users\Haide\Desktop\LINKEDIN\Data\LINKEDIN Connections_bababot_style_FINAL_backup.csv"
    updated_csv = r"C:\Users\Haide\Desktop\LINKEDIN\Data\LINKEDIN Connections_bababot_style_FINAL_updated.csv"
    
    # 读取分析结果
    print(f"读取分析结果: {analysis_file}")
    analyses = read_analysis_results(analysis_file)
    print(f"读取到 {len(analyses)} 个分析结果")
    
    # 读取主CSV文件
    print(f"读取主CSV文件: {master_csv}")
    contacts, fieldnames = read_master_csv(master_csv)
    print(f"读取到 {len(contacts)} 个联系人")
    
    # 创建备份
    print(f"创建备份: {backup_csv}")
    with open(backup_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contacts)
    
    # 更新联系人信息
    updated_count = 0
    for analysis in analyses:
        name_parts = analysis['姓名'].split(' ', 1)
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = name_parts[1]
        else:
            first_name = name_parts[0]
            last_name = ''
        
        # 查找联系人
        contact = find_contact_by_name(contacts, first_name, last_name)
        if contact:
            # 更新联系人
            updated_contact = update_contact_with_analysis(contact, analysis)
            updated_count += 1
            print(f"已更新: {first_name} {last_name}")
        else:
            print(f"未找到: {first_name} {last_name}")
    
    # 扩展字段列表
    new_fields = ['业务领域分类', '行业细分', '数据分析推断', '帖子内容分析', 
                  '工作内容总结', 'Recent_Activity_Summary', 'Business_Focus',
                  'Analysis_Method_Bababot', 'Analysis_Time_Bababot', 
                  'Data_Quality_Bababot', 'Notes_Bababot', '业务画像标签']
    
    # 添加新字段到字段列表
    all_fieldnames = list(fieldnames)
    for field in new_fields:
        if field not in all_fieldnames:
            all_fieldnames.append(field)
    
    # 保存更新后的CSV
    print(f"保存更新后的CSV: {updated_csv}")
    with open(updated_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=all_fieldnames)
        writer.writeheader()
        
        # 确保所有联系人都有新字段
        for contact in contacts:
            for field in new_fields:
                if field not in contact:
                    contact[field] = ''
            writer.writerow(contact)
    
    print(f"\n更新完成!")
    print(f"总共更新了 {updated_count} 个联系人")
    print(f"备份文件: {backup_csv}")
    print(f"更新后的文件: {updated_csv}")
    
    # 生成报告
    generate_report(analyses, updated_csv)

def generate_report(analyses, updated_csv_file):
    """生成分析报告"""
    report_file = r"C:\Users\Haide\Desktop\LINKEDIN\Reports\LinkedIn_Analysis_Batch4_Report_2026-02-23.md"
    
    print(f"\n生成分析报告: {report_file}")
    
    # 统计信息
    domain_counts = {}
    industry_counts = {}
    tag_counts = {}
    
    for analysis in analyses:
        domain = analysis.get('业务领域分类', '未知')
        industry = analysis.get('行业细分', '未知')
        tags = analysis.get('业务画像标签', [])
        
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # 生成报告内容
    report_content = f"""# LinkedIn联系人分析报告 - 批次4

## 报告信息
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **分析批次**: 第4批次
- **分析联系人数量**: {len(analyses)}人
- **分析方法**: 专业推断分析 (基于bababot方法)
- **数据质量**: 基于职位和公司信息的专业推断

## 统计分析

### 业务领域分布
| 业务领域 | 人数 | 百分比 |
|----------|------|--------|
"""
    
    # 添加业务领域分布
    for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(analyses)) * 100
        report_content += f"| {domain} | {count} | {percentage:.1f}% |\n"
    
    report_content += """
### 行业细分分布
| 行业细分 | 人数 | 百分比 |
|----------|------|--------|
"""
    
    # 添加行业细分分布
    for industry, count in sorted(industry_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(analyses)) * 100
        report_content += f"| {industry} | {count} | {percentage:.1f}% |\n"
    
    report_content += """
### 热门业务标签
| 业务标签 | 出现次数 |
|----------|----------|
"""
    
    # 添加热门标签
    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        report_content += f"| {tag} | {count} |\n"
    
    report_content += """
## 详细联系人分析

### 关键联系人识别

#### 1. 航材交易相关联系人
"""
    
    # 识别航材交易相关联系人
    parts_contacts = []
    for analysis in analyses:
        if any(keyword in analysis.get('职位', '').lower() for keyword in ['parts', 'component', 'supply', '部件', '航材']):
            parts_contacts.append(analysis)
    
    for i, contact in enumerate(parts_contacts[:5]):
        report_content += f"{i+1}. **{contact['姓名']}** - {contact['职位']} at {contact['公司']}\n"
        report_content += f"   - **业务领域**: {contact['业务领域分类']}\n"
        report_content += f"   - **行业细分**: {contact['行业细分']}\n"
        report_content += f"   - **Business Focus**: {contact['Business_Focus']}\n"
        report_content += f"   - **LinkedIn**: {contact['LinkedIn链接']}\n\n"
    
    report_content += """
#### 2. 飞机交易相关联系人
"""
    
    # 识别飞机交易相关联系人
    aircraft_contacts = []
    for analysis in analyses:
        if any(keyword in analysis.get('职位', '').lower() for keyword in ['acquisition', 'asset', 'sales', '交易', '收购']):
            aircraft_contacts.append(analysis)
    
    for i, contact in enumerate(aircraft_contacts[:5]):
        report_content += f"{i+1}. **{contact['姓名']}** - {contact['职位']} at {contact['公司']}\n"
        report_content += f"   - **业务领域**: {contact['业务领域分类']}\n"
        report_content += f"   - **行业细分**: {contact['行业细分']}\n"
        report_content += f"   - **Business Focus**: {contact['Business_Focus']}\n"
        report_content += f"   - **LinkedIn**: {contact['LinkedIn链接']}\n\n"
    
    report_content += """
#### 3. 维修服务相关联系人
"""
    
    # 识别维修服务相关联系人
    mro_contacts = []
    for analysis in analyses:
        if any(keyword in analysis.get('职位', '').lower() for keyword in ['mro', 'maintenance', '维修', 'technical']):
            mro_contacts.append(analysis)
    
    for i, contact in enumerate(mro_contacts[:5]):
        report_content += f"{i+1}. **{contact['姓名']}** - {contact['职位']} at {contact['公司']}\n"
        report_content += f"   - **业务领域**: {contact['业务领域分类']}\n"
        report_content += f"   - **行业细分**: {contact['行业细分']}\n"
        report_content += f"   - **Business Focus**: {contact['Business_Focus']}\n"
        report_content += f"   - **LinkedIn**: {contact['LinkedIn链接']}\n\n"
    
    report_content += f"""
## 完整联系人列表

本次分析共处理了 {len(analyses)} 个联系人，详细信息如下：

| 序号 | 姓名 | 职位 | 公司 | 业务领域 | 行业细分 | Business Focus |
|------|------|------|------|----------|----------|----------------|
"""
    
    # 添加完整列表
    for i, analysis in enumerate(analyses, 1):
        report_content += f"| {i} | {analysis['姓名']} | {analysis['职位']} | {analysis['公司']} | {analysis['业务领域分类']} | {analysis['行业细分']} | {analysis['Business_Focus']} |\n"
    
    report_content += f"""
## 数据文件

1. **分析数据文件**: `linkedin_analysis_batch4_2026-02-23.json` - 完整分析数据
2. **CSV格式文件**: `linkedin_analysis_batch4_2026-02-23.csv` - 结构化分析数据
3. **更新后的总表**: `{os.path.basename(updated_csv_file)}` - 包含分析结果的总表

## 后续建议

### 1. 业务应用建议
- **航材交易**: 重点关注 {len(parts_contacts)} 个航材相关联系人
- **飞机交易**: 重点关注 {len(aircraft_contacts)} 个飞机交易相关联系人
- **维修服务**: 重点关注 {len(mro_contacts)} 个维修服务相关联系人

### 2. 联系策略
1. **优先级排序**: 根据业务需求确定联系优先级
2. **个性化消息**: 根据联系人的Business Focus定制联系内容
3. **批量联系**: 可以按业务领域分组联系

### 3. 数据维护
1. **定期更新**: 建议每季度更新一次联系人分析
2. **数据验证**: 通过实际互动验证分析准确性
3. **标签优化**: 根据实际业务需求调整业务标签

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*分析方法: 专业推断分析 (基于bababot方法)*
"""
    
    # 保存报告
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"报告已保存到: {report_file}")

if __name__ == "__main__":
    main()