#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从正确位置开始分析LinkedIn联系人
"""

import pandas as pd
import os
from datetime import datetime
import json

def analyze_contacts(start_index, batch_size=100):
    """从指定位置开始分析一批联系人"""
    
    # 读取原始数据
    data_path = r"C:\Users\Haide\Desktop\LINKEDIN\Data\LINKEDIN Connections_with_analysis_COMPLETE.csv"
    
    try:
        df = pd.read_csv(data_path, encoding='utf-8')
        total_contacts = len(df)
        
        print(f"总联系人: {total_contacts}")
        print(f"开始位置: {start_index}")
        print(f"批次大小: {batch_size}")
        
        # 计算结束位置
        end_index = min(start_index + batch_size, total_contacts)
        
        if start_index >= total_contacts:
            print("所有联系人都已分析完成!")
            return None
        
        # 提取本批联系人
        batch_df = df.iloc[start_index:end_index].copy()
        
        print(f"分析范围: {start_index} 到 {end_index}")
        print(f"本批联系人数量: {len(batch_df)}")
        
        # 分析每个联系人
        analyzed_contacts = []
        
        for idx, row in batch_df.iterrows():
            contact_info = {
                '序号': idx + 1,
                '姓名': str(str(row.get('First Name', '')) + ' ' + str(row.get('Last Name', ''))).strip(),
                '职位': str(row.get('Position', '')).strip(),
                '公司': str(row.get('Company', '')).strip(),
                '分析时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '分析方法': '专业推断分析'
            }
            
            # 基于职位和公司进行专业推断
            position = contact_info['职位'].lower()
            company = contact_info['公司'].lower()
            
            # 业务领域分类
            business_areas = []
            
            # 航材相关
            if any(word in position for word in ['purchasing', 'procurement', 'supply', 'buyer', '采购']):
                business_areas.append('航材供应')
            
            # 飞机交易相关
            if any(word in position for word in ['sales', 'business development', 'commercial', 'account', '销售', '业务发展']):
                business_areas.append('业务发展')
            
            # 维修服务相关
            if any(word in position for word in ['engineer', 'technical', 'maintenance', 'mro', '维修', '工程']):
                business_areas.append('维修服务')
            
            # 资产管理相关
            if any(word in position for word in ['asset', 'portfolio', 'investment', '资产', '投资']):
                business_areas.append('资产管理')
            
            # 如果没有匹配，使用默认分类
            if not business_areas:
                business_areas.append('业务发展')
            
            contact_info['业务领域分类'] = ', '.join(business_areas)
            
            # 业务相关度评分 (1-5)
            # 基于职位相关性和公司相关性
            score = 3  # 默认中等
            
            # 职位相关性加分
            if any(word in position for word in ['director', 'manager', 'head', 'lead', '总监', '经理', '主管']):
                score += 1
            
            # 公司相关性加分
            aviation_keywords = ['aircraft', 'aviation', 'aerospace', '航空', '飞机', '航材']
            if any(keyword in company for keyword in aviation_keywords):
                score += 1
            
            # 确保分数在1-5之间
            contact_info['业务相关度评分'] = min(max(score, 1), 5)
            
            # 联系优先级
            if contact_info['业务相关度评分'] >= 4:
                contact_info['联系优先级'] = '高'
            elif contact_info['业务相关度评分'] >= 3:
                contact_info['联系优先级'] = '中'
            else:
                contact_info['联系优先级'] = '低'
            
            # 具体联系建议
            if '航材供应' in business_areas:
                contact_info['具体联系建议'] = '航材交易'
            elif '资产管理' in business_areas:
                contact_info['具体联系建议'] = '飞机交易'
            elif '维修服务' in business_areas:
                contact_info['具体联系建议'] = '维修服务'
            else:
                contact_info['具体联系建议'] = '业务拓展'
            
            analyzed_contacts.append(contact_info)
        
        return analyzed_contacts, start_index, end_index, total_contacts
        
    except Exception as e:
        print(f"读取数据错误: {str(e)}")
        return None

def save_analysis_results(analyzed_contacts, batch_num, start_index, end_index, total_contacts):
    """保存分析结果"""
    
    # 创建DataFrame
    df = pd.DataFrame(analyzed_contacts)
    
    # 保存CSV
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    csv_filename = f"linkedin_analysis_batch{batch_num}_{timestamp}.csv"
    csv_path = os.path.join(r"C:\Users\Haide\Desktop\LINKEDIN\Analysis", csv_filename)
    
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"CSV文件已保存: {csv_path}")
    
    # 保存JSON
    json_filename = f"linkedin_analysis_batch{batch_num}_{timestamp}.json"
    json_path = os.path.join(r"C:\Users\Haide\Desktop\LINKEDIN\Analysis", json_filename)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analyzed_contacts, f, ensure_ascii=False, indent=2)
    print(f"JSON文件已保存: {json_path}")
    
    # 生成报告
    generate_report(df, batch_num, start_index, end_index, total_contacts)
    
    return len(df)

def generate_report(df, batch_num, start_index, end_index, total_contacts):
    """生成分析报告"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = f"""# LinkedIn联系人分析报告 - 批次{batch_num}

## 分析概况
- **分析时间**: {timestamp}
- **分析范围**: 联系人 {start_index} 到 {end_index}
- **本批数量**: {len(df)} 位联系人
- **累计分析**: {end_index}/{total_contacts} ({end_index/total_contacts*100:.1f}%)
- **分析方法**: 专业推断分析（基于职位和公司信息）

## 业务领域分布
"""
    
    # 统计业务领域
    business_counts = {}
    for areas in df['业务领域分类']:
        for area in areas.split(', '):
            business_counts[area] = business_counts.get(area, 0) + 1
    
    for area, count in business_counts.items():
        percentage = (count / len(df)) * 100
        report += f"- **{area}**: {count}人 ({percentage:.1f}%)\n"
    
    report += f"""
## 优先级分布
"""
    
    # 统计优先级
    priority_counts = df['联系优先级'].value_counts()
    for priority, count in priority_counts.items():
        percentage = (count / len(df)) * 100
        report += f"- **{priority}优先级**: {count}人 ({percentage:.1f}%)\n"
    
    report += f"""
## 高优先级联系人 (评分≥4)
"""
    
    high_priority = df[df['业务相关度评分'] >= 4]
    if len(high_priority) > 0:
        for _, row in high_priority.head(10).iterrows():
            report += f"- **{row['姓名']}** ({row['公司']}) - {row['职位']} | 评分: {row['业务相关度评分']}/5 | 建议: {row['具体联系建议']}\n"
    else:
        report += "本批次没有高优先级联系人。\n"
    
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
*报告生成时间: {timestamp}*
*累计分析进度: {end_index}/{total_contacts}*
"""
    
    # 保存报告
    report_filename = f"LinkedIn_Analysis_Batch{batch_num}_Report_{datetime.now().strftime('%Y-%m-%d_%H%M')}.md"
    report_path = os.path.join(r"C:\Users\Haide\Desktop\LINKEDIN\Reports", report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告已保存: {report_path}")
    
    return report

def main():
    print("LinkedIn联系人分析 - 从正确位置开始")
    print("=" * 60)
    
    # 检查当前分析进度
    analysis_dir = r"C:\Users\Haide\Desktop\LINKEDIN\Analysis"
    
    if os.path.exists(analysis_dir):
        files = os.listdir(analysis_dir)
        csv_files = [f for f in files if f.endswith('.csv') and 'batch' in f]
        
        total_analyzed = 0
        for csv_file in csv_files:
            try:
                df = pd.read_csv(os.path.join(analysis_dir, csv_file), encoding='utf-8')
                total_analyzed += len(df)
            except:
                pass
        
        print(f"当前已分析: {total_analyzed} 位联系人")
    else:
        total_analyzed = 0
        print("没有找到之前的分析文件，从第0位开始")
    
    # 计算批次号
    batch_size = 100
    batch_num = (total_analyzed // batch_size) + 1
    start_index = total_analyzed
    
    print(f"下一个批次: 批次{batch_num}")
    print(f"开始位置: 第{start_index}位联系人")
    
    # 运行分析
    result = analyze_contacts(start_index, batch_size)
    
    if result is None:
        print("分析完成或出错")
        return
    
    analyzed_contacts, start_idx, end_idx, total_contacts = result
    
    # 保存结果
    count = save_analysis_results(analyzed_contacts, batch_num, start_idx, end_idx, total_contacts)
    
    print(f"\n{'='*60}")
    print(f"分析完成!")
    print(f"批次: {batch_num}")
    print(f"分析数量: {count} 位联系人")
    print(f"累计分析: {end_idx}/{total_contacts} ({end_idx/total_contacts*100:.1f}%)")
    print(f"剩余联系人: {total_contacts - end_idx} 位")
    print("=" * 60)
    
    # 询问是否继续
    print(f"\n是否继续分析下一个批次? (批次{batch_num + 1})")
    print("输入 'y' 继续，其他键退出")
    
    # 在自动化环境中，我们默认继续
    continue_analysis = 'y'  # 默认继续
    
    if continue_analysis.lower() == 'y':
        # 递归调用继续分析
        print(f"\n继续分析批次{batch_num + 1}...")
        # 这里可以添加递归调用或循环
        print("要分析更多批次，请再次运行此脚本")

if __name__ == '__main__':
    main()