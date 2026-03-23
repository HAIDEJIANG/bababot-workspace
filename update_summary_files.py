#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新LinkedIn分析汇总文件
将新的分析结果整合到总表和每日汇总中
"""

import pandas as pd
import os
from datetime import datetime
import glob

def update_master_file():
    """更新主Excel文件"""
    
    base_dir = r"C:\Users\Haide\Desktop\LINKEDIN"
    analysis_dir = os.path.join(base_dir, "Analysis")
    integration_dir = os.path.join(base_dir, "整合结果")
    daily_dir = os.path.join(base_dir, "日常维护")
    
    # 创建目录
    os.makedirs(integration_dir, exist_ok=True)
    os.makedirs(daily_dir, exist_ok=True)
    
    # 主文件路径
    master_file = os.path.join(integration_dir, "LinkedIn_分析结果_完整汇总.xlsx")
    
    # 查找最新的分析文件
    analysis_files = glob.glob(os.path.join(analysis_dir, "linkedin_analysis_batch*.csv"))
    if not analysis_files:
        print("没有找到分析文件")
        return
    
    # 按修改时间排序，获取最新的文件
    latest_file = max(analysis_files, key=os.path.getmtime)
    print(f"找到最新分析文件: {os.path.basename(latest_file)}")
    
    # 读取分析数据
    try:
        new_data = pd.read_csv(latest_file, encoding='utf-8-sig')
        print(f"读取分析数据: {len(new_data)} 条记录")
    except Exception as e:
        print(f"读取分析文件错误: {e}")
        return
    
    # 检查主文件是否存在
    if os.path.exists(master_file):
        print("更新现有主文件...")
        try:
            # 读取现有数据
            with pd.ExcelFile(master_file) as xls:
                existing_data = {}
                for sheet_name in xls.sheet_names:
                    existing_data[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
            
            # 更新业务画像汇总表
            if '业务画像汇总' in existing_data:
                # 检查是否有重复数据
                existing_names = set(existing_data['业务画像汇总']['姓名'].astype(str))
                new_names = set(new_data['姓名'].astype(str))
                
                # 只添加新数据
                new_rows = new_data[~new_data['姓名'].isin(existing_names)]
                if len(new_rows) > 0:
                    updated_df = pd.concat([existing_data['业务画像汇总'], new_rows], ignore_index=True)
                    existing_data['业务画像汇总'] = updated_df
                    print(f"添加了 {len(new_rows)} 条新记录到业务画像汇总")
                else:
                    print("没有新记录需要添加")
            else:
                existing_data['业务画像汇总'] = new_data
                print("创建新的业务画像汇总表")
            
            # 获取批次号
            batch_match = os.path.basename(latest_file).split('_')[2]  # batchX
            batch_number = batch_match.replace('batch', '')
            
            # 添加批次分析表
            sheet_name = f'批次{batch_number}'
            existing_data[sheet_name] = new_data
            print(f"添加批次分析表: {sheet_name}")
            
            # 保存更新后的文件
            with pd.ExcelWriter(master_file, engine='openpyxl') as writer:
                for sheet_name, df in existing_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"主文件已更新: {master_file}")
            
        except Exception as e:
            print(f"更新主文件错误: {e}")
            # 创建新的主文件
            create_new_master_file(master_file, new_data, latest_file)
    else:
        print("创建新的主文件...")
        create_new_master_file(master_file, new_data, latest_file)
    
    # 更新每日汇总文件
    update_daily_summary(new_data, daily_dir, latest_file)

def create_new_master_file(master_file, new_data, latest_file):
    """创建新的主文件"""
    try:
        # 获取批次号
        batch_match = os.path.basename(latest_file).split('_')[2]
        batch_number = batch_match.replace('batch', '')
        
        with pd.ExcelWriter(master_file, engine='openpyxl') as writer:
            # 业务画像汇总表
            new_data.to_excel(writer, sheet_name='业务画像汇总', index=False)
            
            # 批次分析表
            new_data.to_excel(writer, sheet_name=f'批次{batch_number}', index=False)
            
            # 统计分析表
            create_statistics_sheet(new_data, writer)
            
            # 联系人索引表
            create_index_sheet(new_data, writer)
        
        print(f"新的主文件已创建: {master_file}")
    except Exception as e:
        print(f"创建主文件错误: {e}")

def create_statistics_sheet(data, writer):
    """创建统计分析表"""
    stats_data = {
        '统计项目': [
            '总联系人数量',
            '高优先级联系人',
            '中优先级联系人',
            '低优先级联系人',
            '平均业务相关度评分',
            '航材供应相关',
            '业务发展相关',
            '资产管理相关',
            '维修服务相关',
            '管理领导相关',
            '航空专业服务'
        ],
        '数量': [
            len(data),
            (data['联系优先级'] == '高').sum(),
            (data['联系优先级'] == '中').sum(),
            (data['联系优先级'] == '低').sum(),
            f"{data['业务相关度评分'].mean():.2f}",
            data['业务领域分类'].str.contains('航材供应').sum(),
            data['业务领域分类'].str.contains('业务发展').sum(),
            data['业务领域分类'].str.contains('资产管理').sum(),
            data['业务领域分类'].str.contains('维修服务').sum(),
            data['业务领域分类'].str.contains('管理领导').sum(),
            data['业务领域分类'].str.contains('航空专业服务').sum()
        ]
    }
    
    stats_df = pd.DataFrame(stats_data)
    stats_df.to_excel(writer, sheet_name='统计分析', index=False)

def create_index_sheet(data, writer):
    """创建联系人索引表"""
    index_data = data[['姓名', '公司', '职位', '业务领域分类', '联系优先级', '业务相关度评分']].copy()
    index_data = index_data.sort_values(['联系优先级', '业务相关度评分'], ascending=[False, False])
    index_data.to_excel(writer, sheet_name='联系人索引', index=False)

def update_daily_summary(new_data, daily_dir, latest_file):
    """更新每日汇总文件"""
    
    today = datetime.now().strftime('%Y-%m-%d')
    daily_file = os.path.join(daily_dir, f"LinkedIn分析_每日汇总_{today}.xlsx")
    
    print(f"\n更新每日汇总文件: {os.path.basename(daily_file)}")
    
    try:
        if os.path.exists(daily_file):
            print("更新现有每日汇总文件...")
            with pd.ExcelFile(daily_file) as xls:
                daily_data = {}
                for sheet_name in xls.sheet_names:
                    daily_data[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
        else:
            print("创建新的每日汇总文件...")
            daily_data = {}
        
        # 更新业务画像表
        if '业务画像' in daily_data:
            # 检查重复
            existing_names = set(daily_data['业务画像']['姓名'].astype(str))
            new_names = set(new_data['姓名'].astype(str))
            
            new_rows = new_data[~new_data['姓名'].isin(existing_names)]
            if len(new_rows) > 0:
                updated_df = pd.concat([daily_data['业务画像'], new_rows], ignore_index=True)
                daily_data['业务画像'] = updated_df
                print(f"添加了 {len(new_rows)} 条新记录到业务画像")
            else:
                print("没有新记录需要添加")
        else:
            daily_data['业务画像'] = new_data
            print("创建新的业务画像表")
        
        # 更新高优先级联系人表
        high_priority = new_data[new_data['联系优先级'] == '高']
        if len(high_priority) > 0:
            if '高优先级联系人' in daily_data:
                # 检查重复
                existing_high_names = set(daily_data['高优先级联系人']['姓名'].astype(str))
                new_high_names = set(high_priority['姓名'].astype(str))
                
                new_high_rows = high_priority[~high_priority['姓名'].isin(existing_high_names)]
                if len(new_high_rows) > 0:
                    updated_high = pd.concat([daily_data['高优先级联系人'], new_high_rows], ignore_index=True)
                    daily_data['高优先级联系人'] = updated_high
                    print(f"添加了 {len(new_high_rows)} 条新记录到高优先级联系人")
                else:
                    print("没有新的高优先级联系人")
            else:
                daily_data['高优先级联系人'] = high_priority
                print("创建新的高优先级联系人表")
        
        # 更新分析进度表
        batch_match = os.path.basename(latest_file).split('_')[2]
        batch_number = batch_match.replace('batch', '')
        
        progress_data = {
            '日期': [today],
            '批次': [batch_number],
            '本批分析数量': [len(new_data)],
            '高优先级数量': [len(high_priority)],
            '平均业务相关度': [f"{new_data['业务相关度评分'].mean():.2f}"],
            '分析时间': [datetime.now().strftime('%H:%M:%S')]
        }
        progress_df = pd.DataFrame(progress_data)
        
        if '分析进度' in daily_data:
            daily_data['分析进度'] = pd.concat([daily_data['分析进度'], progress_df], ignore_index=True)
        else:
            daily_data['分析进度'] = progress_df
        print("更新分析进度表")
        
        # 更新业务应用指南表
        update_business_guide(daily_data, new_data)
        
        # 保存每日汇总文件
        with pd.ExcelWriter(daily_file, engine='openpyxl') as writer:
            for sheet_name, df in daily_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"每日汇总文件已更新: {daily_file}")
        
        # 生成每日报告
        generate_daily_report(daily_data, daily_dir, today, batch_number, len(new_data))
        
    except Exception as e:
        print(f"更新每日汇总文件错误: {e}")

def update_business_guide(daily_data, new_data):
    """更新业务应用指南表"""
    
    # 按业务领域分类
    business_areas = {
        '航材供应': new_data[new_data['业务领域分类'].str.contains('航材供应')],
        '飞机交易': new_data[new_data['业务领域分类'].str.contains('资产管理')],
        '维修服务': new_data[new_data['业务领域分类'].str.contains('维修服务')],
        '业务发展': new_data[new_data['业务领域分类'].str.contains('业务发展')]
    }
    
    guide_data = []
    for area, df in business_areas.items():
        if len(df) > 0:
            # 取评分最高的3个联系人
            top_contacts = df.nlargest(3, '业务相关度评分')
            for _, contact in top_contacts.iterrows():
                guide_data.append({
                    '业务领域': area,
                    '姓名': contact['姓名'],
                    '公司': contact['公司'],
                    '职位': contact['职位'],
                    '业务相关度': contact['业务相关度评分'],
                    '联系优先级': contact['联系优先级'],
                    '联系建议': contact['具体联系建议']
                })
    
    if guide_data:
        guide_df = pd.DataFrame(guide_data)
        daily_data['业务应用指南'] = guide_df
        print(f"更新业务应用指南表: {len(guide_data)} 条记录")

def generate_daily_report(daily_data, daily_dir, today, batch_number, batch_count):
    """生成每日报告"""
    
    report_file = os.path.join(daily_dir, f"LinkedIn分析_每日报告_{today}.md")
    
    report_content = f"""# LinkedIn分析每日报告 - {today}

## 今日分析总结

### 批次信息
- **分析批次**: 第{batch_number}批
- **分析数量**: {batch_count} 位联系人
- **分析时间**: {datetime.now().strftime('%H:%M:%S')}
- **分析方法**: 专业推断分析

### 关键成果
"""
    
    if '业务画像' in daily_data:
        total_contacts = len(daily_data['业务画像'])
        high_priority = len(daily_data['高优先级联系人']) if '高优先级联系人' in daily_data else 0
        avg_score = daily_data['业务画像']['业务相关度评分'].mean()
        
        report_content += f"""
- **累计分析**: {total_contacts} 位联系人
- **高优先级联系人**: {high_priority} 位
- **平均业务相关度**: {avg_score:.2f}/5
"""
    
    report_content += f"""
### 业务领域分布
"""
    
    if '业务画像' in daily_data:
        business_counts = daily_data['业务画像']['业务领域分类'].str.split('、').explode().value_counts()
        for business, count in business_counts.items():
            percentage = count / len(daily_data['业务画像']) * 100
            report_content += f"- **{business}**: {count}人 ({percentage:.1f}%)\n"
    
    report_content += f"""
## 今日高价值联系人

### 推荐优先联系
"""
    
    if '高优先级联系人' in daily_data and len(daily_data['高优先级联系人']) > 0:
        high_priority_df = daily_data['高优先级联系人']
        # 取评分最高的5个
        top_5 = high_priority_df.nlargest(5, '业务相关度评分')
        
        for idx, contact in top_5.iterrows():
            report_content += f"""
#### {contact['姓名']}
- **公司**: {contact['公司']}
- **职位**: {contact['职位']}
- **业务领域**: {contact['业务领域分类']}
- **评分**: {contact['业务相关度评分']}/5
- **联系建议**: {contact['具体联系建议']}
"""
    else:
        report_content += "今日没有高优先级联系人。\n"
    
    report_content += f"""
## 业务机会发现

### 1. 航材交易机会
"""
    
    if '业务应用指南' in daily_data:
        material_contacts = daily_data['业务应用指南'][daily_data['业务应用指南']['业务领域'] == '航材供应']
        if len(material_contacts) > 0:
            for _, contact in material_contacts.iterrows():
                report_content += f"- **{contact['姓名']}** - {contact['公司']} ({contact['职位']}) | 评分: {contact['业务相关度']}/5\n"
        else:
            report_content += "今日没有发现航材交易机会。\n"
    
    report_content += f"""
### 2. 飞机交易机会
"""
    
    if '业务应用指南' in daily_data:
        aircraft_contacts = daily_data['业务应用指南'][daily_data['业务应用指南']['业务领域'] == '飞机交易']
        if len(aircraft_contacts) > 0:
            for _, contact in aircraft_contacts.iterrows():
                report_content += f"- **{contact['姓名']}** - {contact['公司']} ({contact['职位']}) | 评分: {contact['业务相关度']}/5\n"
        else:
            report_content += "今日没有发现飞机交易机会。\n"
    
    report_content += f"""
## 使用建议

### 立即行动
1. **查看每日汇总文件**: `LinkedIn分析_每日汇总_{today}.xlsx`
2. **优先联系高优先级联系人**
3. **根据业务需求筛选相关领域的联系人**

### 文件说明
- **业务画像工作表**: 所有分析过的联系人
- **高优先级联系人工作表**: 推荐优先联系的联系人
- **分析进度工作表**: 分析历史记录
- **业务应用指南工作表**: 按业务领域分类的推荐联系人

## 明日计划
1. **继续分析下一批联系人**
2. **跟踪已联系联系人的反馈**
3. **优化分析模型**

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*系统状态: 正常运行*
*建议: 开始使用今日的分析结果进行业务联系*
"""
    
    # 保存报告
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"每日报告已生成: {report_file}")
    return report_file

def main():
    """主函数"""
    print("开始更新LinkedIn分析汇总文件...")
    print("=" * 60)
    
    update_master_file()
    
    print("\n" + "=" * 60)
    print("汇总文件更新完成!")
    print("=" * 60)
    
    # 显示文件位置
    base_dir = r"C:\Users\Haide\Desktop\LINKEDIN"
    print(f"\n文件位置:")
    print(f"- 分析数据: {os.path.join(base_dir, 'Analysis')}")
    print(f"- 完整汇总: {os.path.join(base_dir, '整合结果')}")
    print(f"- 每日汇总: {os.path.join(base_dir, '日常维护')}")
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n今日文件:")
    print(f"- 每日汇总: LinkedIn分析_每日汇总_{today}.xlsx")
    print(f"- 每日报告: LinkedIn分析_每日报告_{today}.md")
    
    print(f"\n建议:")
    print("1. 打开每日汇总文件查看最新分析结果")
    print("2. 优先联系高优先级联系人")
    print("3. 根据业务需求筛选相关领域的联系人")
    print("4. 记录联系反馈以优化分析模型")

if __name__ == "__main__":
    main()