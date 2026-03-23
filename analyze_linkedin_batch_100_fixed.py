#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn联系人批量分析脚本 - 每批100个联系人
基于bababot方法的专业推断分析
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import re

def analyze_contact(row):
    """分析单个联系人，基于职位和公司信息进行专业推断"""
    
    # 提取基本信息
    name = str(row.get('First Name', '') + ' ' + row.get('Last Name', '')).strip()
    position = str(row.get('Position', '')).strip()
    company = str(row.get('Company', '')).strip()
    
    # 初始化分析结果
    analysis = {
        '姓名': name,
        '职位': position,
        '公司': company,
        '分析时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '业务领域分类': '',
        '行业细分': '',
        '数据分析推断': '',
        '工作内容总结': '',
        'Business_Focus': '',
        'Recent_Activity_Summary': '',
        '业务相关度评分': 0,
        '联系优先级': '低',
        '具体联系建议': '',
        '分析类型': '专业推断'
    }
    
    # 职位关键词分析
    position_lower = position.lower()
    
    # 业务领域分类
    business_areas = []
    
    # 航材相关职位
    if any(keyword in position_lower for keyword in ['采购', '供应', '物料', '库存', 'logistics', 'supply', 'procurement', 'purchasing']):
        business_areas.append('航材供应')
        analysis['行业细分'] = '航材采购与供应链管理'
        analysis['业务相关度评分'] = 4 if '经理' in position_lower or '总监' in position_lower else 3
        
    # 飞机交易相关职位
    if any(keyword in position_lower for keyword in ['销售', '业务发展', '业务拓展', 'sales', 'business development', 'bd', 'account manager']):
        business_areas.append('业务发展')
        analysis['行业细分'] = '航空产品销售与市场拓展'
        analysis['业务相关度评分'] = max(analysis['业务相关度评分'], 4)
        
    # 资产管理相关职位
    if any(keyword in position_lower for keyword in ['资产', '收购', '投资', '资产管理', 'asset', 'acquisition', 'investment']):
        business_areas.append('资产管理')
        analysis['行业细分'] = '飞机资产交易与投资'
        analysis['业务相关度评分'] = max(analysis['业务相关度评分'], 5)
        
    # 维修服务相关职位
    if any(keyword in position_lower for keyword in ['维修', '维护', '工程', '技术', 'mro', 'maintenance', 'engineering', 'technical']):
        business_areas.append('维修服务')
        analysis['行业细分'] = '飞机维修与工程技术'
        analysis['业务相关度评分'] = max(analysis['业务相关度评分'], 4)
        
    # 管理与领导职位
    if any(keyword in position_lower for keyword in ['ceo', '总裁', '总经理', '董事', '总监', 'director', 'manager', 'head of']):
        business_areas.append('管理领导')
        analysis['业务相关度评分'] = max(analysis['业务相关度评分'], 5)
        
    # 如果没有匹配到特定领域，使用通用分类
    if not business_areas:
        business_areas.append('航空专业服务')
        analysis['行业细分'] = '航空相关专业服务'
        analysis['业务相关度评分'] = 2
    
    analysis['业务领域分类'] = '、'.join(business_areas)
    
    # 公司背景分析
    company_lower = company.lower()
    
    # 根据公司类型调整分析
    if any(keyword in company_lower for keyword in ['engine', '发动机', '动力']):
        analysis['行业细分'] = '发动机' + (' ' + analysis['行业细分'] if analysis['行业细分'] else '')
    elif any(keyword in company_lower for keyword in ['aircraft', '飞机', 'aviation', '航空']):
        analysis['行业细分'] = '飞机' + (' ' + analysis['行业细分'] if analysis['行业细分'] else '')
    elif any(keyword in company_lower for keyword in ['component', '部件', 'part', '零件']):
        analysis['行业细分'] = '航材部件' + (' ' + analysis['行业细分'] if analysis['行业细分'] else '')
    elif any(keyword in company_lower for keyword in ['leasing', '租赁', 'finance', '金融']):
        analysis['行业细分'] = '飞机租赁与金融' + (' ' + analysis['行业细分'] if analysis['行业细分'] else '')
    
    # 数据分析推断
    analysis['数据分析推断'] = f"基于职位'{position}'和公司'{company}'的分析，{name}主要从事{business_areas[0]}相关工作"
    if len(business_areas) > 1:
        analysis['数据分析推断'] += f"，同时涉及{'、'.join(business_areas[1:])}"
    
    # 工作内容总结
    if '航材供应' in business_areas:
        analysis['工作内容总结'] = f"负责航空器材的采购、供应链管理和库存控制，确保航材供应及时可靠"
    elif '业务发展' in business_areas:
        analysis['工作内容总结'] = f"负责航空产品/服务的市场拓展、客户关系维护和业务增长"
    elif '资产管理' in business_areas:
        analysis['工作内容总结'] = f"负责飞机资产的收购、交易、租赁和投资管理"
    elif '维修服务' in business_areas:
        analysis['工作内容总结'] = f"负责飞机/发动机的维修、维护、工程技术和MRO服务"
    elif '管理领导' in business_areas:
        analysis['工作内容总结'] = f"负责公司/部门的战略规划、团队管理和业务决策"
    else:
        analysis['工作内容总结'] = f"从事航空相关专业服务工作，具体职责需进一步了解"
    
    # Business Focus (bababot风格)
    focus_areas = []
    if '航材供应' in business_areas:
        focus_areas.append('航材采购与供应链优化')
    if '业务发展' in business_areas:
        focus_areas.append('航空市场拓展与客户开发')
    if '资产管理' in business_areas:
        focus_areas.append('飞机资产交易与投资管理')
    if '维修服务' in business_areas:
        focus_areas.append('飞机维修工程与MRO服务')
    
    analysis['Business_Focus'] = ' | '.join(focus_areas) if focus_areas else '航空专业服务'
    
    # Recent Activity Summary (bababot风格)
    current_month = datetime.now().strftime('%Y年%m月')
    if '航材供应' in business_areas:
        analysis['Recent_Activity_Summary'] = f"{current_month}: 专注于航材供应链优化和采购成本控制"
    elif '业务发展' in business_areas:
        analysis['Recent_Activity_Summary'] = f"{current_month}: 积极拓展航空市场，寻找新的业务机会"
    elif '资产管理' in business_areas:
        analysis['Recent_Activity_Summary'] = f"{current_month}: 关注飞机资产市场动态，评估投资机会"
    elif '维修服务' in business_areas:
        analysis['Recent_Activity_Summary'] = f"{current_month}: 推进维修工程项目，提升MRO服务能力"
    else:
        analysis['Recent_Activity_Summary'] = f"{current_month}: 从事航空专业服务工作"
    
    # 联系优先级
    if analysis['业务相关度评分'] >= 4:
        analysis['联系优先级'] = '高'
    elif analysis['业务相关度评分'] >= 3:
        analysis['联系优先级'] = '中'
    else:
        analysis['联系优先级'] = '低'
    
    # 具体联系建议
    if '航材供应' in business_areas:
        analysis['具体联系建议'] = '航材交易、供应链合作'
    elif '业务发展' in business_areas:
        analysis['具体联系建议'] = '业务合作、市场拓展'
    elif '资产管理' in business_areas:
        analysis['具体联系建议'] = '飞机交易、租赁合作'
    elif '维修服务' in business_areas:
        analysis['具体联系建议'] = '维修服务、技术支持'
    else:
        analysis['具体联系建议'] = '专业咨询、行业交流'
    
    return analysis

def analyze_batch(input_file, output_dir, batch_size=100, start_index=0):
    """分析一批联系人"""
    
    print(f"读取数据文件: {input_file}")
    try:
        # 尝试不同编码读取文件
        encodings = ['utf-8', 'gbk', 'latin1', 'cp1252']
        df = None
        for encoding in encodings:
            try:
                df = pd.read_csv(input_file, encoding=encoding)
                print(f"使用编码: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print("错误: 无法读取文件，尝试所有编码都失败")
            return None
            
    except Exception as e:
        print(f"读取文件错误: {e}")
        return None
    
    print(f"总联系人数量: {len(df)}")
    print(f"已分析联系人: {start_index}")
    print(f"本次分析范围: {start_index} 到 {min(start_index + batch_size, len(df))}")
    
    # 确定分析范围
    end_index = min(start_index + batch_size, len(df))
    batch_df = df.iloc[start_index:end_index].copy()
    
    print(f"开始分析 {len(batch_df)} 个联系人...")
    
    # 分析每个联系人
    analyses = []
    for idx, row in batch_df.iterrows():
        try:
            analysis = analyze_contact(row)
            analyses.append(analysis)
            
            # 每10个联系人显示进度
            if (idx - start_index + 1) % 10 == 0:
                print(f"  已分析 {idx - start_index + 1}/{len(batch_df)} 个联系人")
                
        except Exception as e:
            print(f"分析联系人 {idx} 时出错: {e}")
            # 添加错误记录
            error_analysis = {
                '姓名': str(row.get('First Name', '') + ' ' + row.get('Last Name', '')).strip(),
                '职位': str(row.get('Position', '')).strip(),
                '公司': str(row.get('Company', '')).strip(),
                '分析时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '业务领域分类': '分析错误',
                '行业细分': '分析错误',
                '数据分析推断': f'分析过程中出错: {str(e)}',
                '工作内容总结': '分析过程中出错',
                'Business_Focus': '分析错误',
                'Recent_Activity_Summary': '分析错误',
                '业务相关度评分': 0,
                '联系优先级': '低',
                '具体联系建议': '需要重新分析',
                '分析类型': '分析错误'
            }
            analyses.append(error_analysis)
    
    # 转换为DataFrame
    analysis_df = pd.DataFrame(analyses)
    
    # 保存分析结果
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    batch_number = (start_index // batch_size) + 1
    
    # CSV文件
    csv_filename = f"linkedin_analysis_batch{batch_number}_{timestamp}.csv"
    csv_path = os.path.join(output_dir, csv_filename)
    analysis_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"分析结果已保存到: {csv_path}")
    
    # JSON文件（用于后续处理）
    json_filename = f"linkedin_analysis_batch{batch_number}_{timestamp}.json"
    json_path = os.path.join(output_dir, json_filename)
    analysis_df.to_json(json_path, orient='records', force_ascii=False, indent=2)
    print(f"JSON格式已保存到: {json_path}")
    
    # 生成分析报告
    generate_report(analysis_df, output_dir, batch_number, timestamp, start_index, end_index, len(df))
    
    return analysis_df, csv_path, json_path

def generate_report(analysis_df, output_dir, batch_number, timestamp, start_index, end_index, total_contacts):
    """生成分析报告"""
    
    report = f"""# LinkedIn联系人业务画像分析报告 - 批次{batch_number}

## 分析概况
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **分析批次**: 第{batch_number}批
- **分析范围**: 联系人 {start_index + 1} 到 {end_index}
- **分析数量**: {len(analysis_df)} 位联系人
- **累计分析**: {end_index} 位联系人 ({end_index/total_contacts*100:.2f}%)
- **剩余待分析**: {total_contacts - end_index} 位联系人

## 统计分析

### 业务领域分布
"""
    
    # 业务领域统计
    business_counts = analysis_df['业务领域分类'].str.split('、').explode().value_counts()
    for business, count in business_counts.items():
        percentage = count / len(analysis_df) * 100
        report += f"- **{business}**: {count}人 ({percentage:.1f}%)\n"
    
    report += f"""
### 联系优先级分布
"""
    
    # 优先级统计
    priority_counts = analysis_df['联系优先级'].value_counts()
    for priority, count in priority_counts.items():
        percentage = count / len(analysis_df) * 100
        report += f"- **{priority}优先级**: {count}人 ({percentage:.1f}%)\n"
    
    report += f"""
### 业务相关度评分分布
- **平均评分**: {analysis_df['业务相关度评分'].mean():.2f}
- **最高评分**: {analysis_df['业务相关度评分'].max()}
- **最低评分**: {analysis_df['业务相关度评分'].min()}
- **评分≥4 (高相关)**: {(analysis_df['业务相关度评分'] >= 4).sum()}人 ({(analysis_df['业务相关度评分'] >= 4).sum()/len(analysis_df)*100:.1f}%)

## 高优先级联系人列表 (评分≥4)
"""
    
    # 高优先级联系人
    high_priority = analysis_df[analysis_df['业务相关度评分'] >= 4]
    if len(high_priority) > 0:
        for idx, row in high_priority.iterrows():
            report += f"""
### {row['姓名']}
- **职位**: {row['职位']}
- **公司**: {row['公司']}
- **业务领域**: {row['业务领域分类']}
- **业务相关度**: {row['业务相关度评分']}/5
- **联系优先级**: {row['联系优先级']}
- **联系建议**: {row['具体联系建议']}
- **Business Focus**: {row['Business_Focus']}
- **Recent Activity**: {row['Recent_Activity_Summary']}
"""
    else:
        report += "本批次没有高优先级联系人。\n"
    
    report += f"""
## 业务应用指南

### 1. 航材交易相关联系人
"""
    
    material_contacts = analysis_df[analysis_df['业务领域分类'].str.contains('航材供应')]
    if len(material_contacts) > 0:
        for _, row in material_contacts.head(5).iterrows():  # 只显示前5个
            report += f"- **{row['姓名']}** ({row['公司']}) - {row['职位']} | 评分: {row['业务相关度评分']}/5\n"
    else:
        report += "本批次没有航材交易相关联系人。\n"
    
    report += f"""
### 2. 飞机交易相关联系人
"""
    
    aircraft_contacts = analysis_df[analysis_df['业务领域分类'].str.contains('资产管理')]
    if len(aircraft_contacts) > 0:
        for _, row in aircraft_contacts.head(5).iterrows():
            report += f"- **{row['姓名']}** ({row['公司']}) - {row['职位']} | 评分: {row['业务相关度评分']}/5\n"
    else:
        report += "本批次没有飞机交易相关联系人。\n"
    
    report += f"""
### 3. 维修服务相关联系人
"""
    
    maintenance_contacts = analysis_df[analysis_df['业务领域分类'].str.contains('维修服务')]
    if len(maintenance_contacts) > 0:
        for _, row in maintenance_contacts.head(5).iterrows():
            report += f"- **{row['姓名']}** ({row['公司']}) - {row['职位']} | 评分: {row['业务相关度评分']}/5\n"
    else:
        report += "本批次没有维修服务相关联系人。\n"
    
    report += f"""
## 分析质量说明
- **分析方法**: 专业推断分析（基于职位和公司信息）
- **分析类型**: 所有联系人都使用专业推断方法
- **数据来源**: LinkedIn联系人导出数据
- **行业知识**: 应用航空行业专业知识进行分析
- **准确性说明**: 基于公开信息的专业推断，建议在实际联系前进行验证

## 下一步建议
1. **优先联系**: 高优先级联系人（评分≥4）
2. **业务匹配**: 根据具体业务需求选择相关领域的联系人
3. **验证分析**: 通过实际联系验证分析结果的准确性
4. **继续分析**: 继续分析下一批联系人

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*累计分析进度: {end_index}/{total_contacts}*