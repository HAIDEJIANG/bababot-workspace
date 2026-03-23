#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将LinkedIn分析结果合并到总表中的脚本
"""

import csv
import os
from datetime import datetime

def read_csv_file(filepath):
    """读取CSV文件"""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                data.append(row)
        return headers, data
    except Exception as e:
        print(f"读取文件 {filepath} 时出错: {e}")
        return None, None

def write_csv_file(filepath, headers, data):
    """写入CSV文件"""
    try:
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        print(f"成功写入文件: {filepath}")
        return True
    except Exception as e:
        print(f"写入文件 {filepath} 时出错: {e}")
        return False

def merge_analysis():
    """合并分析结果"""
    # 读取现有的业务分析文件
    business_analysis_file = "linkedin_business_analysis.csv"
    new_analysis_file = "linkedin_complete_analysis_2026-02-22.csv"
    output_file = "linkedin_merged_analysis_2026-02-22.csv"
    
    print("开始合并分析结果...")
    
    # 读取现有业务分析文件
    print(f"读取现有业务分析文件: {business_analysis_file}")
    biz_headers, biz_data = read_csv_file(business_analysis_file)
    
    if biz_headers is None:
        print("无法读取现有业务分析文件，使用新分析文件作为基础")
        # 读取新分析文件
        new_headers, new_data = read_csv_file(new_analysis_file)
        if new_headers is None:
            print("无法读取新分析文件")
            return False
        
        # 写入合并后的文件
        success = write_csv_file(output_file, new_headers, new_data)
        if success:
            print(f"已创建新的合并文件: {output_file}")
            print(f"包含 {len(new_data)} 条记录")
        return success
    
    # 读取新分析文件
    print(f"读取新分析文件: {new_analysis_file}")
    new_headers, new_data = read_csv_file(new_analysis_file)
    
    if new_headers is None:
        print("无法读取新分析文件")
        return False
    
    # 检查列结构
    print(f"现有文件列数: {len(biz_headers)}")
    print(f"新文件列数: {len(new_headers)}")
    
    # 合并数据
    merged_data = []
    
    # 首先添加现有数据
    for row in biz_data:
        merged_data.append(row)
    
    # 添加新数据（避免重复）
    existing_names = set(row[0] for row in biz_data if len(row) > 0)
    
    new_count = 0
    for row in new_data:
        if len(row) > 0 and row[0] not in existing_names:
            merged_data.append(row)
            new_count += 1
            existing_names.add(row[0])
    
    # 写入合并后的文件
    success = write_csv_file(output_file, biz_headers, merged_data)
    
    if success:
        print(f"合并完成!")
        print(f"现有记录数: {len(biz_data)}")
        print(f"新增记录数: {new_count}")
        print(f"总记录数: {len(merged_data)}")
        print(f"输出文件: {output_file}")
    
    return success

def create_summary_report():
    """创建汇总报告"""
    input_file = "linkedin_merged_analysis_2026-02-22.csv"
    report_file = "linkedin_analysis_summary_2026-02-22.md"
    
    print(f"\n创建汇总报告...")
    
    headers, data = read_csv_file(input_file)
    if headers is None:
        print("无法读取合并文件")
        return False
    
    # 创建报告内容
    report_content = f"""# LinkedIn联系人分析汇总报告
## 生成日期：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 数据概览
- **总联系人数量：** {len(data)}
- **分析完成时间：** 2026-02-22 23:50
- **数据来源：** LinkedIn连接页面快照 + 行业知识分析

## 分析范围
本次分析涵盖了从LinkedIn连接页面获取的前10个联系人，基于他们的职位信息和公司描述进行工作内容分析。

## 联系人分类统计

### 按职位层级分类
1. **高级管理层 (C-level/VP)：** 3人
   - Sharon Green (CEO)
   - Brianna Jenkins (VP)
   - Wissam Al Mehyou (CEO)

2. **总监级别：** 1人
   - Charles Khoury (Director)

3. **专业顾问：** 3人
   - Sarah MALAKI (业务/财务/销售)
   - Fabrizio Poli (航空企业家/顾问)
   - Zeineb Lassoued (高级顾问)

4. **区域专家：** 2人
   - John Robinson (亚太区)
   - Zeineb Lassoued (非洲-中东)

5. **运营协调：** 1人
   - Ali Negm (销售运营协调)

### 按业务领域分类
1. **航空零部件和供应链：** 1人
2. **飞机维护和技术服务：** 1人
3. **业务开发和综合管理：** 1人
4. **资产收购和投资：** 1人
5. **航空创业和综合服务：** 1人
6. **区域销售和业务发展：** 1人
7. **私人航空服务：** 1人
8. **区域航空咨询：** 1人
9. **销售和运营协调：** 1人
10. **窄体飞机业务：** 1人

## 关键发现
1. **行业集中度高：** 所有联系人都在航空或相关行业工作
2. **职位多样性：** 涵盖了从CEO到专业顾问的不同职位层级
3. **区域覆盖广：** 联系人分布在北美、欧洲、中东、亚太等不同区域
4. **专业领域细分：** 每个联系人都有明确的专业领域和专长

## 数据文件
1. **详细分析数据：** `linkedin_merged_analysis_2026-02-22.csv`
   - 包含所有联系人的详细分析信息
   - 字段：联系人姓名、职位、公司、连接日期、业务领域分类、行业细分、数据分析推断、帖子内容分析、工作内容总结

2. **原始分析文件：** `linkedin_posts_analysis_actual_2026-02-22.md`
   - 基于LinkedIn页面快照的详细分析报告

3. **合并前文件：** `linkedin_business_analysis.csv`
   - 之前的业务分析结果

## 后续建议
1. **深度分析：** 对关键联系人进行更深入的分析，了解他们的专业见解和行业趋势
2. **网络拓展：** 基于这些联系人的专业领域，寻找更多的相关联系人
3. **定期更新：** 定期检查联系人的最新动态和帖子内容
4. **关系维护：** 通过LinkedIn消息与关键联系人保持联系

---
*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"汇总报告已创建: {report_file}")
        return True
    except Exception as e:
        print(f"创建汇总报告时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("LinkedIn分析结果合并工具")
    print("=" * 60)
    
    # 合并分析结果
    if merge_analysis():
        # 创建汇总报告
        create_summary_report()
        
        print("\n" + "=" * 60)
        print("合并完成！")
        print("生成的文件：")
        print("1. linkedin_merged_analysis_2026-02-22.csv - 合并后的分析数据")
        print("2. linkedin_analysis_summary_2026-02-22.md - 汇总报告")
        print("3. linkedin_posts_analysis_actual_2026-02-22.md - 详细分析报告")
        print("=" * 60)
    else:
        print("合并过程中出现错误")

if __name__ == "__main__":
    main()