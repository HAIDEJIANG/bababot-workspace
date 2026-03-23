#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版LinkedIn批量分析器
每批分析100个联系人
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import re

def analyze_contact_simple(row):
    """简化版联系人分析"""
    
    # 提取基本信息（处理可能的NaN值）
    first_name = row.get('First Name', '')
    last_name = row.get('Last Name', '')
    
    # 处理NaN值
    if pd.isna(first_name):
        first_name = ''
    if pd.isna(last_name):
        last_name = ''
    
    name = str(first_name) + ' ' + str(last_name)
    name = name.strip()
    
    position = row.get('Position', '')
    if pd.isna(position):
        position = ''
    position = str(position).strip()
    
    company = row.get('Company', '')
    if pd.isna(company):
        company = ''
    company = str(company).strip()
    
    # 初始化分析结果
    analysis = {
        '姓名': name,
        '职位': position,
        '公司': company,
        '分析时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '业务领域分类': '',
        '行业细分': '',
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
    
    # 联系优先级
    if analysis['业务相关度评分'] >= 4:
        analysis['联系优先级'] = '高'
    elif analysis['业务相关度评分'] >= 3:
        analysis['联系优先级'] = '中'
    
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

def analyze_batch_simple(input_file, output_dir, batch_size=100, start_index=0, batch_number=1):
    """简化版批量分析"""
    
    print(f"读取数据文件: {input_file}")
    
    # 读取数据
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
    except:
        try:
            df = pd.read_csv(input_file, encoding='gbk')
        except:
            print("错误: 无法读取文件")
            return None
    
    print(f"总联系人数量: {len(df)}")
    print(f"本次分析范围: {start_index} 到 {min(start_index + batch_size, len(df))}")
    
    # 确定分析范围
    end_index = min(start_index + batch_size, len(df))
    batch_df = df.iloc[start_index:end_index].copy()
    
    print(f"开始分析 {len(batch_df)} 个联系人...")
    
    # 分析每个联系人
    analyses = []
    for idx, row in batch_df.iterrows():
        try:
            analysis = analyze_contact_simple(row)
            analyses.append(analysis)
            
            # 每20个联系人显示进度
            if (idx - start_index + 1) % 20 == 0:
                print(f"  已分析 {idx - start_index + 1}/{len(batch_df)} 个联系人")
                
        except Exception as e:
            print(f"分析联系人 {idx} 时出错: {e}")
            # 添加错误记录
            first_name = row.get('First Name', '')
            last_name = row.get('Last Name', '')
            position = row.get('Position', '')
            company = row.get('Company', '')
            
            # 处理NaN值
            if pd.isna(first_name):
                first_name = ''
            if pd.isna(last_name):
                last_name = ''
            if pd.isna(position):
                position = ''
            if pd.isna(company):
                company = ''
            
            error_analysis = {
                '姓名': str(first_name) + ' ' + str(last_name),
                '职位': str(position).strip(),
                '公司': str(company).strip(),
                '分析时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '业务领域分类': '分析错误',
                '行业细分': '分析错误',
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
    
    # CSV文件
    csv_filename = f"linkedin_analysis_batch{batch_number}_{timestamp}.csv"
    csv_path = os.path.join(output_dir, csv_filename)
    analysis_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"分析结果已保存到: {csv_path}")
    
    # 生成简单报告
    generate_simple_report(analysis_df, output_dir, batch_number, timestamp, start_index, end_index, len(df))
    
    return analysis_df, csv_path

def generate_simple_report(analysis_df, output_dir, batch_number, timestamp, start_index, end_index, total_contacts):
    """生成简化报告"""
    
    report_content = f"""# LinkedIn联系人业务画像分析报告 - 批次{batch_number}

## 分析概况
- 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 分析批次: 第{batch_number}批
- 分析范围: 联系人 {start_index + 1} 到 {end_index}
- 分析数量: {len(analysis_df)} 位联系人
- 累计分析: {end_index} 位联系人 ({end_index/total_contacts*100:.2f}%)
- 剩余待分析: {total_contacts - end_index} 位联系人

## 统计分析

### 业务领域分布
"""
    
    # 业务领域统计
    business_counts = analysis_df['业务领域分类'].str.split('、').explode().value_counts()
    for business, count in business_counts.items():
        percentage = count / len(analysis_df) * 100
        report_content += f"- {business}: {count}人 ({percentage:.1f}%)\n"
    
    report_content += f"""
### 联系优先级分布
"""
    
    # 优先级统计
    priority_counts = analysis_df['联系优先级'].value_counts()
    for priority, count in priority_counts.items():
        percentage = count / len(analysis_df) * 100
        report_content += f"- {priority}优先级: {count}人 ({percentage:.1f}%)\n"
    
    report_content += f"""
### 业务相关度评分
- 平均评分: {analysis_df['业务相关度评分'].mean():.2f}
- 最高评分: {analysis_df['业务相关度评分'].max()}
- 最低评分: {analysis_df['业务相关度评分'].min()}
- 评分≥4 (高相关): {(analysis_df['业务相关度评分'] >= 4).sum()}人 ({(analysis_df['业务相关度评分'] >= 4).sum()/len(analysis_df)*100:.1f}%)

## 高优先级联系人 (评分≥4)
"""
    
    # 高优先级联系人
    high_priority = analysis_df[analysis_df['业务相关度评分'] >= 4]
    if len(high_priority) > 0:
        for idx, row in high_priority.iterrows():
            report_content += f"""
### {row['姓名']}
- 职位: {row['职位']}
- 公司: {row['公司']}
- 业务领域: {row['业务领域分类']}
- 业务相关度: {row['业务相关度评分']}/5
- 联系优先级: {row['联系优先级']}
- 联系建议: {row['具体联系建议']}
"""
    else:
        report_content += "本批次没有高优先级联系人。\n"
    
    report_content += f"""
## 业务应用指南

### 1. 航材交易相关联系人
"""
    
    material_contacts = analysis_df[analysis_df['业务领域分类'].str.contains('航材供应')]
    if len(material_contacts) > 0:
        for _, row in material_contacts.head(5).iterrows():
            report_content += f"- {row['姓名']} ({row['公司']}) - {row['职位']} | 评分: {row['业务相关度评分']}/5\n"
    else:
        report_content += "本批次没有航材交易相关联系人。\n"
    
    report_content += f"""
### 2. 飞机交易相关联系人
"""
    
    aircraft_contacts = analysis_df[analysis_df['业务领域分类'].str.contains('资产管理')]
    if len(aircraft_contacts) > 0:
        for _, row in aircraft_contacts.head(5).iterrows():
            report_content += f"- {row['姓名']} ({row['公司']}) - {row['职位']} | 评分: {row['业务相关度评分']}/5\n"
    else:
        report_content += "本批次没有飞机交易相关联系人。\n"
    
    report_content += f"""
### 3. 维修服务相关联系人
"""
    
    maintenance_contacts = analysis_df[analysis_df['业务领域分类'].str.contains('维修服务')]
    if len(maintenance_contacts) > 0:
        for _, row in maintenance_contacts.head(5).iterrows():
            report_content += f"- {row['姓名']} ({row['公司']}) - {row['职位']} | 评分: {row['业务相关度评分']}/5\n"
    else:
        report_content += "本批次没有维修服务相关联系人。\n"
    
    report_content += f"""
## 分析说明
- 分析方法: 专业推断分析（基于职位和公司信息）
- 分析类型: 所有联系人都使用专业推断方法
- 数据来源: LinkedIn联系人导出数据
- 行业知识: 应用航空行业专业知识进行分析
- 准确性说明: 基于公开信息的专业推断，建议在实际联系前进行验证

## 下一步建议
1. 优先联系: 高优先级联系人（评分≥4）
2. 业务匹配: 根据具体业务需求选择相关领域的联系人
3. 验证分析: 通过实际联系验证分析结果的准确性
4. 继续分析: 继续分析下一批联系人

---
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
累计分析进度: {end_index}/{total_contacts}
"""
    
    # 保存报告
    report_filename = f"LinkedIn_Analysis_Batch{batch_number}_Report_{timestamp}.md"
    report_path = os.path.join(output_dir, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"分析报告已保存到: {report_path}")
    return report_path

def main():
    """主函数"""
    print("LinkedIn批量分析器启动")
    
    # 配置路径
    base_dir = r"C:\Users\Haide\Desktop\LINKEDIN"
    data_dir = os.path.join(base_dir, "Data")
    analysis_dir = os.path.join(base_dir, "Analysis")
    reports_dir = os.path.join(base_dir, "Reports")
    
    # 创建目录
    for directory in [analysis_dir, reports_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # 输入文件
    input_file = os.path.join(data_dir, "LINKEDIN Connections_with_analysis_COMPLETE.csv")
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 输入文件不存在: {input_file}")
        return
    
    # 读取数据获取总数
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
    except:
        try:
            df = pd.read_csv(input_file, encoding='gbk')
        except:
            print("错误: 无法读取文件")
            return
    
    total_contacts = len(df)
    print(f"总联系人数量: {total_contacts}")
    
    # 检查已有分析进度
    analysis_files = [f for f in os.listdir(analysis_dir) if f.startswith("linkedin_analysis_batch") and f.endswith(".csv")]
    
    if analysis_files:
        # 找出最大批次号
        batch_numbers = []
        for file in analysis_files:
            match = re.search(r'batch(\d+)', file)
            if match:
                batch_numbers.append(int(match.group(1)))
        
        if batch_numbers:
            current_batch = max(batch_numbers)
            print(f"已有分析批次: 第{current_batch}批")
            
            # 计算已分析数量
            total_analyzed = 0
            for batch_num in range(1, current_batch + 1):
                batch_files = [f for f in analysis_files if f"batch{batch_num}" in f]
                if batch_files:
                    latest_batch = max(batch_files)
                    try:
                        batch_df = pd.read_csv(os.path.join(analysis_dir, latest_batch))
                        total_analyzed += len(batch_df)
                    except:
                        continue
            
            print(f"已分析联系人: {total_analyzed} ({total_analyzed/total_contacts*100:.2f}%)")
            start_index = total_analyzed
            next_batch = current_batch + 1
        else:
            start_index = 0
            next_batch = 1
    else:
        start_index = 0
        next_batch = 1
    
    print(f"\n开始第{next_batch}批分析")
    print(f"起始位置: {start_index}")
    print(f"批量大小: 100个联系人")
    
    # 运行分析
    result = analyze_batch_simple(
        input_file=input_file,
        output_dir=analysis_dir,
        batch_size=100,
        start_index=start_index,
        batch_number=next_batch
    )
    
    if result:
        analysis_df, csv_path = result
        print(f"\n分析完成!")
        print(f"分析数量: {len(analysis_df)} 个联系人")
        print(f"文件保存位置: {csv_path}")
        
        # 显示统计信息
        print(f"\n统计信息:")
        print(f"- 高优先级联系人: {(analysis_df['联系优先级'] == '高').sum()}")
        print(f"- 平均业务相关度: {analysis_df['业务相关度评分'].mean():.2f}/5")
        
        # 业务领域分布
        business_counts = analysis_df['业务领域分类'].str.split('、').explode().value_counts()
        print(f"\n业务领域分布:")
        for business, count in business_counts.head(5).items():
            percentage = count / len(analysis_df) * 100
            print(f"  {business}: {count}人 ({percentage:.1f}%)")
        
        # 计算累计进度
        total_analyzed_now = start_index + len(analysis_df)
        print(f"\n累计进度: {total_analyzed_now}/{total_contacts} ({total_analyzed_now/total_contacts*100:.2f}%)")
        print(f"剩余分析: {total_contacts - total_analyzed_now} 个联系人")
        
        # 建议下一批
        if total_analyzed_now < total_contacts:
            next_start = total_analyzed_now
            next_batch_num = next_batch + 1
            next_batch_size = min(100, total_contacts - total_analyzed_now)
            print(f"\n建议下一批:")
            print(f"- 批次: 第{next_batch_num}批")
            print(f"- 起始位置: {next_start}")
            print(f"- 分析数量: {next_batch_size}个联系人")
    else:
        print("分析失败")

if __name__ == "__main__":
    main()