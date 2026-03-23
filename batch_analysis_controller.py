#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn批量分析控制器
管理100个联系人一批的分析流程，包括总结、写入总表、备份等全套流程
"""

import os
import pandas as pd
import json
from datetime import datetime
import shutil
import sys

class BatchAnalysisController:
    def __init__(self):
        # 路径配置
        self.base_dir = r"C:\Users\Haide\Desktop\LINKEDIN"
        self.data_dir = os.path.join(self.base_dir, "Data")
        self.analysis_dir = os.path.join(self.base_dir, "Analysis")
        self.reports_dir = os.path.join(self.base_dir, "Reports")
        self.backup_dir = os.path.join(self.base_dir, "Backup")
        self.daily_maintenance_dir = os.path.join(self.base_dir, "日常维护")
        self.integration_dir = os.path.join(self.base_dir, "整合结果")
        
        # 创建必要的目录
        for directory in [self.analysis_dir, self.reports_dir, self.backup_dir, 
                         self.daily_maintenance_dir, self.integration_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # 文件路径
        self.input_file = os.path.join(self.data_dir, "LINKEDIN Connections_with_analysis_COMPLETE.csv")
        self.master_file = os.path.join(self.integration_dir, "LinkedIn_分析结果_完整汇总.xlsx")
        self.daily_file_template = os.path.join(self.daily_maintenance_dir, "LinkedIn分析_每日汇总_{date}.xlsx")
        
        # 分析状态
        self.batch_size = 100
        self.current_batch = 0
        self.total_analyzed = 0
        self.total_contacts = 0
        
    def load_data(self):
        """加载联系人数据"""
        print("加载联系人数据...")
        try:
            # 尝试不同编码
            encodings = ['utf-8', 'gbk', 'latin1', 'cp1252']
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(self.input_file, encoding=encoding)
                    print(f"成功使用编码: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                print("错误: 无法读取联系人数据文件")
                return None
            
            self.total_contacts = len(df)
            print(f"总联系人数量: {self.total_contacts}")
            return df
            
        except Exception as e:
            print(f"加载数据错误: {e}")
            return None
    
    def check_analysis_progress(self):
        """检查分析进度"""
        print("\n检查分析进度...")
        
        # 检查已分析的文件
        analysis_files = []
        if os.path.exists(self.analysis_dir):
            for file in os.listdir(self.analysis_dir):
                if file.startswith("linkedin_analysis_batch") and file.endswith(".csv"):
                    analysis_files.append(file)
        
        if analysis_files:
            print(f"找到 {len(analysis_files)} 个分析文件")
            
            # 找出最新的批次
            batch_numbers = []
            for file in analysis_files:
                try:
                    # 从文件名提取批次号
                    match = re.search(r'batch(\d+)', file)
                    if match:
                        batch_numbers.append(int(match.group(1)))
                except:
                    continue
            
            if batch_numbers:
                self.current_batch = max(batch_numbers)
                print(f"最新批次: 第{self.current_batch}批")
                
                # 计算已分析数量
                total_analyzed = 0
                for batch_num in range(1, self.current_batch + 1):
                    batch_files = [f for f in analysis_files if f"batch{batch_num}" in f]
                    if batch_files:
                        latest_batch = max(batch_files)  # 取最新的文件
                        try:
                            batch_df = pd.read_csv(os.path.join(self.analysis_dir, latest_batch))
                            total_analyzed += len(batch_df)
                        except:
                            continue
                
                self.total_analyzed = total_analyzed
                print(f"已分析联系人: {self.total_analyzed}")
                print(f"分析进度: {self.total_analyzed}/{self.total_contacts} ({self.total_analyzed/self.total_contacts*100:.2f}%)")
            else:
                print("无法从文件名中提取批次号")
                self.current_batch = 0
                self.total_analyzed = 0
        else:
            print("没有找到之前的分析文件")
            self.current_batch = 0
            self.total_analyzed = 0
        
        return self.total_analyzed
    
    def run_batch_analysis(self, batch_number=None):
        """运行一批分析"""
        if batch_number is None:
            batch_number = self.current_batch + 1
        
        print(f"\n{'='*60}")
        print(f"开始第{batch_number}批分析 (每批{self.batch_size}个联系人)")
        print(f"{'='*60}")
        
        # 计算起始位置
        start_index = self.total_analyzed
        
        # 导入分析函数
        sys.path.append('.')
        from analyze_linkedin_batch_100 import analyze_batch
        
        # 运行分析
        result = analyze_batch(
            input_file=self.input_file,
            output_dir=self.analysis_dir,
            batch_size=self.batch_size,
            start_index=start_index
        )
        
        if result is None:
            print("分析失败")
            return False
        
        analysis_df, csv_path, json_path = result
        
        # 更新状态
        self.current_batch = batch_number
        self.total_analyzed += len(analysis_df)
        
        # 生成报告
        self.generate_batch_report(analysis_df, batch_number, csv_path)
        
        # 更新总表
        self.update_master_file(analysis_df, batch_number)
        
        # 更新每日汇总
        self.update_daily_summary(analysis_df, batch_number)
        
        # 备份文件
        self.backup_files(batch_number, csv_path, json_path)
        
        # 记录状态
        self.record_analysis_status(batch_number, len(analysis_df))
        
        return True
    
    def generate_batch_report(self, analysis_df, batch_number, csv_path):
        """生成批次报告"""
        print(f"\n生成第{batch_number}批分析报告...")
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        report_filename = f"LinkedIn_Analysis_Batch{batch_number}_Report_{timestamp}.md"
        report_path = os.path.join(self.reports_dir, report_filename)
        
        # 生成报告内容
        report_content = f"""# LinkedIn联系人业务画像分析报告 - 第{batch_number}批

## 批次信息
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **批次编号**: 第{batch_number}批
- **分析数量**: {len(analysis_df)} 位联系人
- **累计分析**: {self.total_analyzed} 位联系人 ({self.total_analyzed/self.total_contacts*100:.2f}%)
- **剩余待分析**: {self.total_contacts - self.total_analyzed} 位联系人
- **数据文件**: {os.path.basename(csv_path)}

## 关键统计

### 业务领域分布
"""
        
        # 业务领域统计
        business_counts = analysis_df['业务领域分类'].str.split('、').explode().value_counts()
        for business, count in business_counts.items():
            percentage = count / len(analysis_df) * 100
            report_content += f"- **{business}**: {count}人 ({percentage:.1f}%)\n"
        
        report_content += f"""
### 联系优先级
- **高优先级**: {(analysis_df['联系优先级'] == '高').sum()}人 ({(analysis_df['联系优先级'] == '高').sum()/len(analysis_df)*100:.1f}%)
- **中优先级**: {(analysis_df['联系优先级'] == '中').sum()}人 ({(analysis_df['联系优先级'] == '中').sum()/len(analysis_df)*100:.1f}%)
- **低优先级**: {(analysis_df['联系优先级'] == '低').sum()}人 ({(analysis_df['联系优先级'] == '低').sum()/len(analysis_df)*100:.1f}%)

### 业务相关度评分
- **平均评分**: {analysis_df['业务相关度评分'].mean():.2f}/5
- **评分分布**:
  - 5分: {(analysis_df['业务相关度评分'] == 5).sum()}人
  - 4分: {(analysis_df['业务相关度评分'] == 4).sum()}人
  - 3分: {(analysis_df['业务相关度评分'] == 3).sum()}人
  - 2分: {(analysis_df['业务相关度评分'] == 2).sum()}人
  - 1分: {(analysis_df['业务相关度评分'] == 1).sum()}人

## 高价值联系人 (评分≥4)

"""
        
        # 高价值联系人
        high_value = analysis_df[analysis_df['业务相关度评分'] >= 4]
        if len(high_value) > 0:
            for idx, row in high_value.iterrows():
                report_content += f"### {row['姓名']}\n"
                report_content += f"- **公司**: {row['公司']}\n"
                report_content += f"- **职位**: {row['职位']}\n"
                report_content += f"- **业务领域**: {row['业务领域分类']}\n"
                report_content += f"- **评分**: {row['业务相关度评分']}/5\n"
                report_content += f"- **优先级**: {row['联系优先级']}\n"
                report_content += f"- **联系建议**: {row['具体联系建议']}\n"
                report_content += f"- **Business Focus**: {row['Business_Focus']}\n"
                report_content += f"- **Recent Activity**: {row['Recent_Activity_Summary']}\n\n"
        else:
            report_content += "本批次没有高价值联系人。\n\n"
        
        report_content += f"""
## 业务应用重点

### 1. 航材交易机会
"""
        
        material_contacts = analysis_df[analysis_df['业务领域分类'].str.contains('航材供应')]
        if len(material_contacts) > 0:
            for _, row in material_contacts.head(10).iterrows():
                report_content += f"- **{row['姓名']}** - {row['公司']} ({row['职位']}) | 评分: {row['业务相关度评分']}/5\n"
        else:
            report_content += "本批次没有航材交易相关联系人。\n"
        
        report_content += f"""
### 2. 飞机交易机会
"""
        
        aircraft_contacts = analysis_df[analysis_df['业务领域分类'].str.contains('资产管理')]
        if len(aircraft_contacts) > 0:
            for _, row in aircraft_contacts.head(10).iterrows():
                report_content += f"- **{row['姓名']}** - {row['公司']} ({row['职位']}) | 评分: {row['业务相关度评分']}/5\n"
        else:
            report_content += "本批次没有飞机交易相关联系人。\n"
        
        report_content += f"""
### 3. 维修服务机会
"""
        
        maintenance_contacts = analysis_df[analysis_df['业务领域分类'].str.contains('维修服务')]
        if len(maintenance_contacts) > 0:
            for _, row in maintenance_contacts.head(10).iterrows():
                report_content += f"- **{row['姓名']}** - {row['公司']} ({row['职位']}) | 评分: {row['业务相关度评分']}/5\n"
        else:
            report_content += "本批次没有维修服务相关联系人。\n"
        
        report_content += f"""
## 分析说明
- **分析方法**: 专业推断分析（基于职位和公司信息）
- **分析质量**: 应用航空行业专业知识，确保分析准确性
- **使用建议**: 建议在实际联系前进行验证
- **更新频率**: 每批分析完成后自动更新总表和每日汇总

## 下一步计划
1. **继续分析**: 第{batch_number + 1}批 ({self.batch_size}个联系人)
2. **业务联系**: 优先联系高价值联系人
3. **效果跟踪**: 记录联系效果，优化分析模型

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*累计进度: {self.total_analyzed}/{self.total_contacts} ({self.total_analyzed/self.total_contacts*100:.2f}%)*
*下一批预计分析: 第{batch_number + 1}批*
"""
        
        # 保存报告
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"分析报告已保存到: {report_path}")
        return report_path
    
    def update_master_file(self, analysis_df, batch_number):
        """更新主Excel文件"""
        print(f"\n更新主Excel文件...")
        
        try:
            # 检查主文件是否存在
            if os.path.exists(self.master_file):
                # 读取现有数据
                with pd.ExcelFile(self.master_file) as xls:
                    existing_data = {}
                    for sheet_name in xls.sheet_names:
                        existing_data[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
                
                # 更新业务画像汇总表
                if '业务画像汇总' in existing_data:
                    # 添加新批次数据
                    updated_df = pd.concat([existing_data['业务画像汇总'], analysis_df], ignore_index=True)
                    existing_data['业务画像汇总'] = updated_df
                else:
                    existing_data['业务画像汇总'] = analysis_df
                
                # 添加批次分析表
                existing_data[f'批次{batch_number}'] = analysis_df
                
                # 保存更新后的文件
                with pd.ExcelWriter(self.master_file, engine='openpyxl') as writer:
                    for sheet_name, df in existing_data.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                print(f"主文件已更新: {self.master_file}")
                
            else:
                # 创建新的主文件
                with pd.ExcelWriter(self.master_file, engine='openpyxl') as writer:
                    analysis_df.to_excel(writer, sheet_name='业务画像汇总', index=False)
                    analysis_df.to_excel(writer, sheet_name=f'批次{batch_number}', index=False)
                
                print(f"主文件已创建: {self.master_file}")
                
        except Exception as e:
            print(f"更新主文件错误: {e}")
            # 创建备份
            backup_file = self.master_file.replace('.xlsx', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
            try:
                if os.path.exists(self.master_file):
                    shutil.copy2(self.master_file, backup_file)
                    print(f"主文件已备份到: {backup_file}")
            except:
                pass
    
    def update_daily_summary(self, analysis_df, batch_number):
        """更新每日汇总文件"""
        print(f"\n更新每日汇总文件...")
        
        today = datetime.now().strftime('%Y-%m-%d')
        daily_file = self.daily_file_template.format(date=today)
        
        try:
            # 读取或创建每日汇总
            if os.path.exists(daily_file):
                with pd.ExcelFile(daily_file) as xls:
                    daily_data = {}
                    for sheet_name in xls.sheet_names:
                        daily_data[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
            else:
                daily_data = {}
            
            # 更新业务画像表
            if '业务画像' in daily_data:
                updated_df = pd.concat([daily_data['业务画像'], analysis_df], ignore_index=True)
                daily_data['业务画像'] = updated_df
            else:
                daily_data['业务画像'] = analysis_df
            
            # 更新高优先级联系人表
            high_priority = analysis_df[analysis_df['联系优先级'] == '高']
            if '高优先级联系人' in daily_data:
                if len(high_priority) > 0:
                    updated_high = pd.concat([daily_data['高优先级联系人'], high_priority], ignore_index=True)
                    daily_data['高优先级联系人'] = updated_high
            else:
                daily_data['高优先级联系人'] = high_priority if len(high_priority) > 0 else pd.DataFrame()
            
            # 更新分析进度表
            progress_data = {
                '日期': [today],
                '批次': [batch_number],
                '本批分析数量': [len(analysis_df)],
                '累计分析数量': [self.total_analyzed],
                '总联系人数量': [self.total_contacts],
                '完成百分比': [f"{self.total_analyzed/self.total_contacts*100:.2f}%"],
                '剩余数量': [self.total_contacts - self.total_analyzed]
            }
            progress_df = pd.DataFrame(progress_data)
            
            if '分析进度' in daily_data:
                daily_data['分析进度'] = pd.concat([daily_data['分析进度'], progress_df], ignore_index=True)
            else:
                daily_data['分析进度'] = progress_df
            
            # 保存每日汇总
            with pd.ExcelWriter(daily_file, engine='openpyxl') as writer:
                for sheet_name, df in daily_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"每日汇总已更新: {daily_file}")
            
        except Exception as e:
            print(f"更新每日汇总错误: {e}")
    
    def backup_files(self, batch_number, csv_path, json_path):
        """备份分析文件"""
        print(f"\n备份分析文件...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        batch_backup_dir = os.path.join(self.backup_dir, f"batch{batch_number}_{timestamp}")
        os.makedirs(batch_backup_dir, exist_ok=True)
        
        try:
            # 备份CSV文件
            if os.path.exists(csv_path):
                backup_csv = os.path.join(batch_backup_dir, os.path.basename(csv_path))
                shutil.copy2(csv_path, backup_csv)
                print(f"CSV文件已备份到: {backup_csv}")
            
            # 备份JSON文件
            if os.path.exists(json_path):
                backup_json = os.path.join(batch_backup_dir, os.path.basename(json_path))
                shutil.copy2(json_path, backup_json)
                print(f"JSON文件已备份到: {backup_json}")
            
            # 备份报告文件
            report_files = [f for f in os.listdir(self.reports_dir) if f"Batch{batch_number}" in f]
            for report_file in report_files:
                report_path = os.path.join(self.reports_dir, report_file)
                backup_report = os.path.join(batch_backup_dir, report_file)
                shutil.copy2(report_path, backup_report)
                print(f"报告文件已备份: {report_file}")
            
            # 创建备份记录
            backup_record = {
                'batch_number': batch_number,
                'backup_time': datetime.now().isoformat(),
                'files_backed_up': [],
                'analysis_count': self.total_analyzed,
                'total_contacts': self.total_contacts
            }
            
            if os.path.exists(csv_path):
                backup_record['files_backed_up'].append(os.path.basename(csv_path))
            if os.path.exists(json_path):
                backup_record['files_backed_up'].append(os.path.basename(json_path))
            backup_record['files_backed_up'].extend(report_files)
            
            record_path = os.path.join(batch_backup_dir, 'backup_record.json')
            with open(record_path, 'w', encoding='utf-8') as f:
                json.dump(backup_record, f, ensure_ascii=False, indent=2)
            
            print(f"备份记录已保存: {record_path}")
            
        except Exception as e:
            print(f"备份文件错误: {e}")
    
    def record_analysis_status(self, batch_number, batch_count):
        """记录分析状态"""
        status_file = os.path.join(self.base_dir, "analysis_status.json")
        
        status_data = {
            'last_analysis': {
                'batch_number': batch_number,
                'analysis_time': datetime.now().isoformat(),
                'contacts_analyzed': batch_count,
                'total_analyzed': self.total_analyzed,
                'completion_percentage': f"{self.total_analyzed/self.total_contacts*100:.2f}%"
            },
            'overall_progress': {
                'total_contacts': self.total_contacts,
                'analyzed_contacts': self.total_analyzed,
                'remaining_contacts': self.total_contacts - self.total_analyzed,
                'batches_completed': batch_number,
                'last_update': datetime.now().isoformat()
            },
            'next_batch': {
                'batch_number': batch_number + 1,
                'start_index': self.total_analyzed,
                'estimated_contacts': min(self.batch_size, self.total_contacts - self.total_analyzed),
                'suggested_time': (datetime.now().timestamp() + 3600)  # 1小时后
            }
        }
        
        try:
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)
            print(f"分析状态已记录: {status_file}")
        except Exception as e:
            print(f"记录分析状态错误: {e}")
    
    def run_complete_workflow(self, batches_to_run=None):
        """运行完整的分析工作流程"""
        print("=" * 70)
        print("LinkedIn联系人批量分析系统")
        print("=" * 70)
        
        # 加载数据
        df = self.load_data()
        if df is None:
            print("无法加载数据，退出系统")
            return False
        
        # 检查进度
        self.check_analysis_progress()
        
        print(f"\n当前状态:")
        print(f"- 总联系人: {self.total_contacts}")
        print(f"- 已分析: {self.total_analyzed} ({self.total_analyzed/self.total_contacts*100:.2f}%)")
        print(f"- 剩余: {self.total_contacts - self.total_analyzed}")
        print(f"- 已完成批次: {self.current_batch}")
        
        if self.total_analyzed >= self.total_contacts:
            print("\n所有联系人都已分析完成！")
            return True
        
        # 确定要运行的批次数量
        if batches_to_run is None:
            remaining_batches = (self.total_contacts - self.total_analyzed + self.batch_size - 1) // self.batch_size
            print(f"\n剩余批次: {remaining_batches}")
            batches_to_run = min(remaining_batches, 1)  # 默认先运行1批
        
        print(f"\n计划运行 {batches_to_run} 批分析")
        print(f"每批 {self.batch_size} 个联系人")
        
        # 运行批次分析
        success_count = 0
        for i in range(batches_to_run):
            batch_num = self.current_batch + 1
            
            print(f"\n{'='*60}")
            print(f"运行第 {i+1}/{batches_to_run} 批分析 (批次{batch_num})")
            print(f"{'='*60}")
            
            success = self.run_batch_analysis(batch_num)
            if success:
                success_count += 1
            else:
                print(f"第{batch_num}批分析失败，停止后续分析")
                break
            
            # 更新状态
            self.current_batch = batch_num
        
        # 生成最终报告
        if success_count > 0:
            self.generate_final_report(success_count)
        
        return success_count > 0
    
    def generate_final_report(self, batches_completed):
        """生成最终报告"""
        print(f"\n{'='*60}")
        print("生成分析总结报告")
        print(f"{'='*60}")
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        final_report_path = os.path.join(self.reports_dir, f"LinkedIn_Analysis_Summary_{timestamp}.md")
        
        # 读取最新的每日汇总文件
        today = datetime.now().strftime('%Y-%m-%d')
        daily_file = self.daily_file_template.format(date=today)
        
        try:
            if os.path.exists(daily_file):
                with pd.ExcelFile(daily_file) as xls:
                    if '分析进度' in xls.sheet_names:
                        progress_df = pd.read_excel(xls, sheet_name='分析进度')
                    if '业务画像' in xls.sheet_names:
                        profile_df = pd.read_excel(xls, sheet_name='业务画像')
                    if '高优先级联系人' in xls.sheet_names:
                        high_priority_df = pd.read_excel(xls, sheet_name='高优先级联系人')
            else:
                print("每日汇总文件不存在，无法生成详细报告")
                return
                
        except Exception as e:
            print(f"读取每日汇总文件错误: {e}")
            return
        
        # 生成报告内容
        report_content = f"""# LinkedIn联系人分析总结报告

## 分析概况
- **报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **分析周期**: 批量分析工作流程
- **完成批次**: {batches_completed} 批
- **累计分析**: {self.total_analyzed} 位联系人
- **完成进度**: {self.total_analyzed}/{self.total_contacts} ({self.total_analyzed/self.total_contacts*100:.2f}%)
- **剩余分析**: {self.total_contacts - self.total_analyzed} 位联系人

## 批次分析详情
"""
        
        if 'progress_df' in locals() and not progress_df.empty:
            for _, row in progress_df.iterrows():
                report_content += f"- **{row['日期']}** - 批次{row['批次']}: {row['本批分析数量']}人 | 累计: {row['累计分析数量']}人 ({row['完成百分比']})\n"
        
        report_content += f"""
## 关键成果

### 1. 高价值联系人发现
- **高优先级联系人**: {len(high_priority_df) if 'high_priority_df' in locals() and not high_priority_df.empty else 0} 位
- **业务相关度≥4**: {(profile_df['业务相关度评分'] >= 4).sum() if 'profile_df' in locals() and not profile_df.empty else 0} 位

### 2. 业务领域覆盖
"""
        
        if 'profile_df' in locals() and not profile_df.empty:
            business_counts = profile_df['业务领域分类'].str.split('、').explode().value_counts()
            for business, count in business_counts.head(10).items():
                percentage = count / len(profile_df) * 100
                report_content += f"- **{business}**: {count}人 ({percentage:.1f}%)\n"
        
        report_content += f"""
### 3. 系统建设成果
- **主分析文件**: {os.path.basename(self.master_file)}
- **每日汇总文件**: {os.path.basename(daily_file)}
- **分析报告**: {len([f for f in os.listdir(self.reports_dir) if f.endswith('.md')])} 份
- **数据备份**: {len([d for d in os.listdir(self.backup_dir) if os.path.isdir(os.path.join(self.backup_dir, d))])} 个批次备份

## 业务应用价值

### 立即可用的资源
1. **高优先级联系人列表** - 可直接联系的业务伙伴
2. **业务领域分类** - 按需求快速查找相关联系人
3. **详细分析报告** - 了解每个联系人的专业背景

### 长期价值
1. **完整的联系人数据库** - 所有业务画像集中管理
2. **自动化分析系统** - 可持续更新和维护
3. **业务智能基础** - 支持数据驱动的业务决策

## 后续工作计划

### 短期 (1-7天)
1. **继续批量分析** - 完成剩余 {self.total_contacts - self.total_analyzed} 位联系人
2. **实际联系验证** - 开始联系高优先级联系人
3. **系统优化** - 根据使用反馈优化分析模型

### 中期 (1-4周)
1. **完整覆盖** - 完成所有3,185位联系人的分析
2. **效果跟踪** - 建立联系效果跟踪系统
3. **智能推荐** - 基于业务需求智能推荐联系人

### 长期 (1-3个月)
1. **生态系统建设** - 完整的LinkedIn分析和工作流系统
2. **商业价值扩展** - 扩展到更多业务场景
3. **自动化升级** - 实现完全自动化的分析和管理

## 使用指南

### 快速开始
1. 打开每日汇总文件: `{os.path.basename(daily_file)}`
2. 查看"高优先级联系人"工作表
3. 根据业务需求筛选联系人
4. 开始业务联系

### 文件说明
- **主文件**: `{os.path.basename(self.master_file)}` - 完整历史数据
- **每日文件**: `{os.path.basename(daily_file)}` - 最新数据，日常使用
- **分析报告**: `Reports/` 目录 - 详细分析报告
- **原始数据**: `Analysis/` 目录 - 原始分析数据

## 技术支持
- **分析方法**: 专业推断分析 + 航空行业知识
- **系统维护**: 每日自动更新汇总文件
- **数据安全**: 定期备份所有分析数据
- **问题反馈**: 记录在分析状态文件中

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*系统状态: 正常运行*
*建议下一步: 开始使用分析结果进行业务联系*

**记住**: 分析结果基于公开信息的专业推断，建议在实际重要业务决策前进行验证。
"""
        
        # 保存报告
        with open(final_report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"总结报告已生成: {final_report_path}")
        return final_report_path

# 主程序
if __name__ == "__main__":
    import re  # 添加缺失的导入
    
    print("LinkedIn批量分析系统启动...")
    
    controller = BatchAnalysisController()
    
    # 运行完整工作流程
    success = controller.run_complete_workflow(batches_to_run=1)
    
    if success:
        print("\n" + "="*70)
        print("批量分析工作流程完成！")
        print("="*70)
        print(f"累计分析: {controller.total_analyzed} 位联系人")
        print(f"完成进度: {controller.total_analyzed/controller.total_contacts*100:.2f}%")
        print(f"下一批: 第{controller.current_batch + 1}批")
        print("\n所有文件已保存到相应目录:")
        print(f"- 分析数据: {controller.analysis_dir}")
        print(f"- 分析报告: {controller.reports_dir}")
        print(f"- 每日汇总: {controller.daily_maintenance_dir}")
        print(f"- 完整数据: {controller.integration_dir}")
    else:
        print("\n批量分析工作流程失败，请检查错误信息。")
