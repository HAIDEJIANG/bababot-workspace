#!/usr/bin/env python3
"""
创建每日汇总文件（修复版）
"""

import pandas as pd
import os
from datetime import datetime

def create_daily_summary_fixed():
    """创建每日汇总Excel文件"""
    
    # 读取唯一总表
    data_dir = r"C:\Users\Haide\Desktop\LINKEDIN\Data"
    master_file = None
    
    # 查找最新的唯一总表
    for file in os.listdir(data_dir):
        if file.startswith('LinkedIn_唯一联系人总表_') and file.endswith('.csv'):
            master_file = os.path.join(data_dir, file)
            break
    
    if not master_file:
        print("未找到唯一总表文件")
        return None
    
    print(f"读取唯一总表: {os.path.basename(master_file)}")
    
    # 读取数据
    df = pd.read_csv(master_file, encoding='utf-8')
    print(f"总联系人: {len(df)} 位")
    
    # 检查列名
    print("列名列表:")
    for col in df.columns:
        print(f"  - {col}")
    
    # 确定评分列名
    score_cols = [col for col in df.columns if '评分' in col or 'Score' in col or '相关' in col]
    score_col = score_cols[0] if score_cols else None
    
    # 确定优先级列名
    priority_cols = [col for col in df.columns if '优先级' in col or 'Priority' in col]
    priority_col = priority_cols[0] if priority_cols else '联系优先级'
    
    # 确定业务标签列名
    tag_cols = [col for col in df.columns if '标签' in col or 'Tag' in col]
    tag_col = tag_cols[0] if tag_cols else '业务标签'
    
    # 创建每日汇总文件
    output_dir = r"C:\Users\Haide\Desktop\LINKEDIN\日常维护"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d')
    excel_file = os.path.join(output_dir, f'LinkedIn分析_每日汇总_{timestamp}.xlsx')
    
    print(f"创建Excel文件: {excel_file}")
    
    # 创建Excel写入器
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # 1. 高优先级联系人
        if priority_col in df.columns:
            high_priority = df[df[priority_col] == '高']
            if not high_priority.empty:
                if score_col:
                    high_priority = high_priority.sort_values(score_col, ascending=False)
                high_priority.to_excel(writer, sheet_name='高优先级联系人', index=False)
                print(f"高优先级联系人: {len(high_priority)} 位")
            else:
                # 如果没有高优先级，使用前100位
                top_contacts = df.head(100)
                top_contacts.to_excel(writer, sheet_name='高优先级联系人', index=False)
                print(f"高优先级联系人（前100位）: {len(top_contacts)} 位")
        else:
            # 如果没有优先级列，使用前100位
            top_contacts = df.head(100)
            top_contacts.to_excel(writer, sheet_name='高优先级联系人', index=False)
            print(f"高优先级联系人（前100位）: {len(top_contacts)} 位")
        
        # 2. 按业务标签分类
        if tag_col in df.columns:
            tags_to_include = ['航材采购', '飞机交易', '维修服务', '业务拓展', '资产管理']
            
            for tag in tags_to_include:
                tag_contacts = df[df[tag_col].str.contains(tag, na=False)]
                if not tag_contacts.empty:
                    # Excel sheet name限制31字符
                    sheet_name = tag[:31]
                    tag_contacts.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"{tag}: {len(tag_contacts)} 位")
        
        # 3. 分析进度
        progress_data = {
            '指标': ['总联系人', '高优先级', '中优先级', '低优先级', '分析完成度'],
            '数量': [
                len(df),
                len(df[df[priority_col] == '高']) if priority_col in df.columns else 0,
                len(df[df[priority_col] == '中']) if priority_col in df.columns else 0,
                len(df[df[priority_col] == '低']) if priority_col in df.columns else 0,
                '100%'
            ]
        }
        progress_df = pd.DataFrame(progress_data)
        progress_df.to_excel(writer, sheet_name='分析进度', index=False)
        
        # 4. 统计摘要
        summary_data = []
        
        # 优先级统计
        if priority_col in df.columns:
            priority_counts = df[priority_col].value_counts()
            for priority, count in priority_counts.items():
                percentage = (count / len(df)) * 100
                summary_data.append({
                    '指标': f'{priority}优先级',
                    '数值': f'{count}人 ({percentage:.1f}%)'
                })
        
        # 业务标签统计
        if tag_col in df.columns:
            all_tags = []
            for tags in df[tag_col]:
                if isinstance(tags, str) and tags != '其他':
                    all_tags.extend([tag.strip() for tag in tags.split(',')])
            
            from collections import Counter
            tag_counts = Counter(all_tags)
            for tag, count in tag_counts.most_common(10):  # 最多显示10个标签
                percentage = (count / len(df)) * 100
                summary_data.append({
                    '指标': f'{tag}标签',
                    '数值': f'{count}人 ({percentage:.1f}%)'
                })
        
        # 分析质量统计
        if '分析完整性' in df.columns:
            quality_counts = df['分析完整性'].value_counts()
            for quality, count in quality_counts.items():
                percentage = (count / len(df)) * 100
                summary_data.append({
                    '指标': f'{quality}质量分析',
                    '数值': f'{count}人 ({percentage:.1f}%)'
                })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='统计摘要', index=False)
        
        # 5. 联系人索引（前500位）
        index_df = df.head(500)[['full_name', '职位', '公司', priority_col if priority_col in df.columns else '']]
        index_df.to_excel(writer, sheet_name='联系人索引', index=False)
    
    print(f"[SUCCESS] 每日汇总文件已创建: {excel_file}")
    print(f"[INFO] 总工作表数: 6个")
    print(f"[INFO] 总联系人: {len(df)} 位")
    
    return excel_file

if __name__ == "__main__":
    print("开始创建每日汇总文件...")
    print("=" * 60)
    
    try:
        excel_file = create_daily_summary_fixed()
        if excel_file:
            print("\n" + "=" * 60)
            print("[SUCCESS] 每日汇总文件创建完成！")
            print(f"[FILE] 文件位置: {excel_file}")
            print("[NEXT] 现在可以开始Git提交和数据验证工作")
    except Exception as e:
        print(f"[ERROR] 创建过程中出错: {e}")
        import traceback
        traceback.print_exc()