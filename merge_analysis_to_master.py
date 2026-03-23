import pandas as pd
import numpy as np
from datetime import datetime

def merge_analysis_to_master():
    """
    将LinkedIn联系人分析结果合并到总表中
    """
    print("开始合并分析结果到总表...")
    
    # 1. 读取总表
    master_file = 'C:/Users/Haide/.openclaw/media/inbound/file_5---52705be1-cb2c-47bb-866a-57c576e59910.csv'
    master_df = pd.read_csv(master_file)
    print(f"总表读取完成: {len(master_df)} 行, {len(master_df.columns)} 列")
    
    # 2. 读取分析结果
    analysis_file = 'C:/Users/Haide/.openclaw/workspace/linkedin_merged_analysis_2026-02-22.csv'
    analysis_df = pd.read_csv(analysis_file)
    print(f"分析结果读取完成: {len(analysis_df)} 行, {len(analysis_df.columns)} 列")
    
    # 3. 准备分析数据映射
    # 根据分析结果文件，我们需要匹配联系人
    # 分析结果中的字段：姓名、职位、公司、连接日期、业务领域分类、行业细分、数据分析推断、帖子内容分析、工作内容总结
    
    # 创建姓名映射字典（全名）
    analysis_dict = {}
    for idx, row in analysis_df.iterrows():
        # 创建全名作为键
        full_name = f"{row['姓名']}".strip()
        analysis_dict[full_name] = {
            '业务领域分类': row.get('业务领域分类', ''),
            '行业细分': row.get('行业细分', ''),
            '数据分析推断': row.get('数据分析推断', ''),
            '帖子内容分析': row.get('帖子内容分析', ''),
            '工作内容总结': row.get('工作内容总结', '')
        }
    
    print(f"创建了 {len(analysis_dict)} 个分析结果映射")
    
    # 4. 在总表中添加分析字段
    # 先添加空列
    analysis_columns = [
        '业务领域分类',
        '行业细分', 
        '数据分析推断',
        '帖子内容分析',
        '工作内容总结',
        '分析状态'
    ]
    
    for col in analysis_columns:
        if col not in master_df.columns:
            master_df[col] = ''
    
    # 5. 匹配并填充分析结果
    matched_count = 0
    for idx, row in master_df.iterrows():
        # 创建全名用于匹配
        first_name = str(row.get('First Name', '')).strip()
        last_name = str(row.get('Last Name', '')).strip()
        full_name = f"{first_name} {last_name}".strip()
        
        # 尝试匹配
        if full_name in analysis_dict:
            analysis_data = analysis_dict[full_name]
            master_df.at[idx, '业务领域分类'] = analysis_data['业务领域分类']
            master_df.at[idx, '行业细分'] = analysis_data['行业细分']
            master_df.at[idx, '数据分析推断'] = analysis_data['数据分析推断']
            master_df.at[idx, '帖子内容分析'] = analysis_data['帖子内容分析']
            master_df.at[idx, '工作内容总结'] = analysis_data['工作内容总结']
            master_df.at[idx, '分析状态'] = '已分析'
            matched_count += 1
        else:
            # 检查是否有部分匹配（只使用姓氏）
            for analysis_name in analysis_dict.keys():
                if last_name and last_name in analysis_name:
                    analysis_data = analysis_dict[analysis_name]
                    master_df.at[idx, '业务领域分类'] = analysis_data['业务领域分类']
                    master_df.at[idx, '行业细分'] = analysis_data['行业细分']
                    master_df.at[idx, '数据分析推断'] = analysis_data['数据分析推断']
                    master_df.at[idx, '帖子内容分析'] = analysis_data['帖子内容分析']
                    master_df.at[idx, '工作内容总结'] = analysis_data['工作内容总结']
                    master_df.at[idx, '分析状态'] = '部分匹配'
                    matched_count += 1
                    break
    
    print(f"成功匹配 {matched_count} 个联系人")
    
    # 6. 保存合并后的文件
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    output_file = f'C:/Users/Haide/.openclaw/workspace/linkedin_master_with_analysis_{timestamp}.csv'
    master_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"合并完成！文件已保存: {output_file}")
    
    # 7. 生成统计报告
    total_contacts = len(master_df)
    analyzed_count = len(master_df[master_df['分析状态'] == '已分析'])
    partial_count = len(master_df[master_df['分析状态'] == '部分匹配'])
    not_analyzed = total_contacts - analyzed_count - partial_count
    
    print("\n=== 合并统计报告 ===")
    print(f"总联系人数量: {total_contacts}")
    print(f"已分析联系人: {analyzed_count}")
    print(f"部分匹配联系人: {partial_count}")
    print(f"未分析联系人: {not_analyzed}")
    print(f"分析覆盖率: {(analyzed_count + partial_count)/total_contacts*100:.1f}%")
    
    # 8. 创建摘要报告
    summary_file = f'C:/Users/Haide/.openclaw/workspace/merge_summary_{timestamp}.md'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"# LinkedIn联系人分析合并报告\n\n")
        f.write(f"**合并时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 统计概览\n\n")
        f.write(f"- **总联系人数量**: {total_contacts}\n")
        f.write(f"- **已分析联系人**: {analyzed_count}\n")
        f.write(f"- **部分匹配联系人**: {partial_count}\n")
        f.write(f"- **未分析联系人**: {not_analyzed}\n")
        f.write(f"- **分析覆盖率**: {(analyzed_count + partial_count)/total_contacts*100:.1f}%\n\n")
        
        f.write(f"## 已分析联系人列表\n\n")
        analyzed_df = master_df[master_df['分析状态'].isin(['已分析', '部分匹配'])]
        for idx, row in analyzed_df.iterrows():
            f.write(f"### {row['First Name']} {row['Last Name']}\n")
            f.write(f"- **职位**: {row.get('Position', '')}\n")
            f.write(f"- **公司**: {row.get('Company', '')}\n")
            f.write(f"- **业务领域**: {row.get('业务领域分类', '')}\n")
            f.write(f"- **行业细分**: {row.get('行业细分', '')}\n")
            f.write(f"- **工作内容总结**: {row.get('工作内容总结', '')[:100]}...\n")
            f.write(f"- **匹配状态**: {row.get('分析状态', '')}\n\n")
    
    print(f"摘要报告已保存: {summary_file}")
    
    return output_file, summary_file

if __name__ == "__main__":
    merge_analysis_to_master()