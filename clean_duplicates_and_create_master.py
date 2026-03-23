#!/usr/bin/env python3
"""
清理重复记录并创建唯一总表
目标：合并所有分析文件，去除重复记录，创建唯一联系人总表
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import hashlib

def get_file_hash(filepath):
    """计算文件哈希值用于去重"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def clean_and_merge_analysis_files():
    """清理重复记录并创建唯一总表"""
    
    # 设置文件路径
    analysis_dir = r"C:\Users\Haide\Desktop\LINKEDIN\Analysis"
    output_dir = r"C:\Users\Haide\Desktop\LINKEDIN\Data"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 收集所有CSV文件
    csv_files = []
    for file in os.listdir(analysis_dir):
        if file.endswith('.csv'):
            csv_files.append(os.path.join(analysis_dir, file))
    
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    # 读取并合并所有文件
    all_data = []
    file_hashes = {}
    duplicate_files = []
    
    for filepath in csv_files:
        try:
            # 计算文件哈希
            file_hash = get_file_hash(filepath)
            
            # 检查是否重复
            if file_hash in file_hashes:
                duplicate_files.append((filepath, file_hashes[file_hash]))
                print(f"发现重复文件: {os.path.basename(filepath)}")
                continue
            
            file_hashes[file_hash] = filepath
            
            # 读取CSV文件
            df = pd.read_csv(filepath, encoding='utf-8')
            
            # 添加批次信息
            batch_name = os.path.basename(filepath).replace('.csv', '')
            df['batch_file'] = batch_name
            
            # 添加唯一标识符
            # 检查列名（可能是中文或英文）
            if 'First Name' in df.columns and 'Last Name' in df.columns:
                df['full_name'] = df['First Name'].astype(str) + ' ' + df['Last Name'].astype(str)
            elif '姓名' in df.columns:
                df['full_name'] = df['姓名']
            elif '名字' in df.columns and '姓氏' in df.columns:
                df['full_name'] = df['名字'].astype(str) + ' ' + df['姓氏'].astype(str)
            else:
                # 尝试找到姓名列
                name_cols = [col for col in df.columns if '名' in col or 'Name' in col]
                if len(name_cols) >= 2:
                    df['full_name'] = df[name_cols[0]].astype(str) + ' ' + df[name_cols[1]].astype(str)
                else:
                    df['full_name'] = 'Unknown'
            
            # 生成唯一ID
            df['unique_id'] = df.apply(lambda row: hashlib.md5(
                f"{row['full_name']}_{row.get('Position', '')}_{row.get('Company', '')}".encode('utf-8')
            ).hexdigest()[:12], axis=1)
            
            all_data.append(df)
            print(f"已加载: {os.path.basename(filepath)} - {len(df)} 条记录")
            
        except Exception as e:
            print(f"读取文件 {filepath} 时出错: {e}")
    
    # 合并所有数据
    if not all_data:
        print("没有找到有效数据")
        return
    
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\n合并后总记录数: {len(combined_df)}")
    
    # 去除重复记录（基于唯一ID）
    unique_df = combined_df.drop_duplicates(subset=['unique_id'], keep='first')
    print(f"去重后唯一记录数: {len(unique_df)}")
    print(f"去除重复记录数: {len(combined_df) - len(unique_df)}")
    
    # 数据清理
    # 1. 处理缺失值
    # 检查可能的列名（中文和英文）
    business_focus_cols = [col for col in unique_df.columns if '业务' in col or 'Business' in col or 'Focus' in col]
    activity_cols = [col for col in unique_df.columns if '活动' in col or 'Activity' in col or 'Summary' in col]
    score_cols = [col for col in unique_df.columns if '评分' in col or 'Score' in col or '相关' in col]
    
    # 使用找到的列名
    business_focus_col = business_focus_cols[0] if business_focus_cols else None
    activity_col = activity_cols[0] if activity_cols else None
    score_col = score_cols[0] if score_cols else None
    
    if business_focus_col:
        unique_df[business_focus_col] = unique_df[business_focus_col].fillna('')
    if activity_col:
        unique_df[activity_col] = unique_df[activity_col].fillna('')
    if score_col:
        unique_df[score_col] = unique_df[score_col].fillna('')
    
    # 2. 标准化评分
    if score_col:
        # 确保评分在1-5之间
        unique_df[score_col] = pd.to_numeric(
            unique_df[score_col], errors='coerce'
        ).clip(lower=1, upper=5).fillna(3)
    
    # 3. 添加联系优先级
    def assign_priority(score):
        if pd.isna(score):
            return '低'
        try:
            score_num = float(score)
            if score_num >= 4:
                return '高'
            elif score_num >= 3:
                return '中'
            else:
                return '低'
        except:
            return '低'
    
    if score_col:
        unique_df['联系优先级'] = unique_df[score_col].apply(assign_priority)
    else:
        unique_df['联系优先级'] = '中'
    
    # 4. 添加业务标签
    def assign_business_tags(focus):
        if pd.isna(focus):
            return '其他'
        
        tags = []
        focus_str = str(focus)
        
        # 航材相关
        if any(word in focus_str for word in ['航材', '采购', '供应', 'spare', 'part', 'material']):
            tags.append('航材采购')
        
        # 飞机相关
        if any(word in focus_str for word in ['飞机', 'aircraft', '交易', '租赁', 'lease', 'sale']):
            tags.append('飞机交易')
        
        # 发动机相关
        if any(word in focus_str for word in ['发动机', 'engine', 'mro', '维修', 'maintenance']):
            tags.append('维修服务')
        
        # 业务拓展
        if any(word in focus_str for word in ['业务', '销售', '发展', 'business', 'sales', 'development']):
            tags.append('业务拓展')
        
        # 资产管理
        if any(word in focus_str for word in ['资产', '管理', '投资', 'asset', 'management', 'investment']):
            tags.append('资产管理')
        
        return ', '.join(tags) if tags else '其他'
    
    if business_focus_col:
        unique_df['业务标签'] = unique_df[business_focus_col].apply(assign_business_tags)
    else:
        unique_df['业务标签'] = '其他'
    
    # 5. 添加分析质量指标
    def calculate_quality(row):
        focus_len = len(str(row[business_focus_col])) if business_focus_col else 0
        activity_len = len(str(row[activity_col])) if activity_col else 0
        
        if focus_len > 20 and activity_len > 20:
            return '高'
        elif focus_len > 10 or activity_len > 10:
            return '中'
        else:
            return '低'
    
    unique_df['分析完整性'] = unique_df.apply(calculate_quality, axis=1)
    
    # 保存唯一总表
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    master_file = os.path.join(output_dir, f'LinkedIn_唯一联系人总表_{timestamp}.csv')
    unique_df.to_csv(master_file, index=False, encoding='utf-8-sig')
    
    # 创建统计报告
    stats = {
        '总文件数': len(csv_files),
        '重复文件数': len(duplicate_files),
        '合并记录数': len(combined_df),
        '唯一记录数': len(unique_df),
        '重复记录数': len(combined_df) - len(unique_df),
        '高优先级联系人': len(unique_df[unique_df['联系优先级'] == '高']),
        '中优先级联系人': len(unique_df[unique_df['联系优先级'] == '中']),
        '低优先级联系人': len(unique_df[unique_df['联系优先级'] == '低']),
        '航材采购标签': len(unique_df[unique_df['业务标签'].str.contains('航材采购')]),
        '飞机交易标签': len(unique_df[unique_df['业务标签'].str.contains('飞机交易')]),
        '维修服务标签': len(unique_df[unique_df['业务标签'].str.contains('维修服务')]),
        '业务拓展标签': len(unique_df[unique_df['业务标签'].str.contains('业务拓展')]),
        '资产管理标签': len(unique_df[unique_df['业务标签'].str.contains('资产管理')]),
    }
    
    # 生成统计报告
    stats_file = os.path.join(output_dir, f'数据清理统计报告_{timestamp}.md')
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write(f"# LinkedIn数据清理统计报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 数据清理结果\n")
        for key, value in stats.items():
            f.write(f"- **{key}**: {value}\n")
        
        f.write("\n## 优先级分布\n")
        priority_counts = unique_df['联系优先级'].value_counts()
        for priority, count in priority_counts.items():
            percentage = (count / len(unique_df)) * 100
            f.write(f"- **{priority}优先级**: {count}人 ({percentage:.1f}%)\n")
        
        f.write("\n## 业务标签分布\n")
        # 统计标签分布
        all_tags = []
        for tags in unique_df['业务标签']:
            if tags != '其他':
                all_tags.extend([tag.strip() for tag in tags.split(',')])
        
        from collections import Counter
        tag_counts = Counter(all_tags)
        for tag, count in tag_counts.most_common():
            percentage = (count / len(unique_df)) * 100
            f.write(f"- **{tag}**: {count}人 ({percentage:.1f}%)\n")
        
        f.write("\n## 分析质量\n")
        quality_counts = unique_df['分析完整性'].value_counts()
        for quality, count in quality_counts.items():
            percentage = (count / len(unique_df)) * 100
            f.write(f"- **{quality}质量**: {count}人 ({percentage:.1f}%)\n")
        
        f.write("\n## 重复文件列表\n")
        if duplicate_files:
            for dup_file, orig_file in duplicate_files:
                f.write(f"- {os.path.basename(dup_file)} → 重复于 {os.path.basename(orig_file)}\n")
        else:
            f.write("无重复文件\n")
        
        f.write("\n## 文件信息\n")
        f.write(f"- **唯一总表**: `{os.path.basename(master_file)}`\n")
        f.write(f"- **总联系人**: {len(unique_df)} 位\n")
        f.write(f"- **文件大小**: {os.path.getsize(master_file) / 1024:.1f} KB\n")
    
    print(f"\n[SUCCESS] 数据清理完成！")
    print(f"[FILE] 唯一总表: {master_file}")
    print(f"[REPORT] 统计报告: {stats_file}")
    print(f"[CONTACTS] 唯一联系人: {len(unique_df)} 位")
    print(f"[HIGH PRIORITY] 高优先级联系人: {stats['高优先级联系人']} 位")
    
    return unique_df, stats

def create_daily_summary(unique_df, stats):
    """创建每日汇总文件"""
    
    output_dir = r"C:\Users\Haide\Desktop\LINKEDIN\日常维护"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d')
    
    # 创建Excel文件
    excel_file = os.path.join(output_dir, f'LinkedIn分析_每日汇总_{timestamp}.xlsx')
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # 1. 高优先级联系人
        high_priority = unique_df[unique_df['联系优先级'] == '高'].sort_values(
            'Business Relevance Score', ascending=False
        )
        high_priority.to_excel(writer, sheet_name='高优先级联系人', index=False)
        
        # 2. 按业务标签分类
        for tag in ['航材采购', '飞机交易', '维修服务', '业务拓展', '资产管理']:
            tag_contacts = unique_df[unique_df['业务标签'].str.contains(tag, na=False)]
            if not tag_contacts.empty:
                sheet_name = tag[:31]  # Excel sheet name limit
                tag_contacts.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # 3. 分析进度
        progress_data = {
            '指标': ['总联系人', '已分析', '完成进度', '高优先级', '中优先级', '低优先级'],
            '数量': [
                stats.get('唯一记录数', 0),
                stats.get('唯一记录数', 0),
                '100%',
                stats.get('高优先级联系人', 0),
                stats.get('中优先级联系人', 0),
                stats.get('低优先级联系人', 0)
            ]
        }
        progress_df = pd.DataFrame(progress_data)
        progress_df.to_excel(writer, sheet_name='分析进度', index=False)
        
        # 4. 统计摘要
        summary_data = []
        for key, value in stats.items():
            if key not in ['总文件数', '重复文件数', '合并记录数', '唯一记录数', '重复记录数']:
                summary_data.append({'指标': key, '数值': value})
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='统计摘要', index=False)
    
    print(f"[DAILY] 每日汇总文件: {excel_file}")
    return excel_file

if __name__ == "__main__":
    print("开始清理重复记录并创建唯一总表...")
    print("=" * 60)
    
    try:
        # 执行数据清理
        unique_df, stats = clean_and_merge_analysis_files()
        
        # 创建每日汇总
        if unique_df is not None:
            excel_file = create_daily_summary(unique_df, stats)
            
            print("\n" + "=" * 60)
            print("[SUCCESS] 所有任务完成！")
            print(f"[FILE] 唯一总表已保存")
            print(f"[REPORT] 统计报告已生成")
            print(f"[DAILY] 每日汇总文件已更新")
            print(f"[CONTACTS] 总联系人: {len(unique_df)} 位")
            print(f"[HIGH] 高优先级: {stats.get('高优先级联系人', 0)} 位")
            
    except Exception as e:
        print(f"[ERROR] 执行过程中出错: {e}")
        import traceback
        traceback.print_exc()