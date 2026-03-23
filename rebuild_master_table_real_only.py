#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重建LinkedIn帖子信息总表 - 只包含真实数据
删除所有模拟生成的数据，只保留2026-02-24的真实采集数据
"""

import pandas as pd
import os
from datetime import datetime

# 设置路径
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "real business post")
output_file = os.path.join(desktop_path, "LinkedIn_Business_Posts_Master_Table.csv")

print("开始重建总表 - 只包含真实数据...")

# 只读取2026-02-24的真实数据文件
real_data_files = [
    "LinkedIn_Business_Posts_ALL_20260224_221252.csv",
    "LinkedIn_Business_Posts_ALL_20260224_221331.csv",
    "LinkedIn_Business_Posts_ALL_20260224_235254.csv"
]

all_data = []

for filename in real_data_files:
    file_path = os.path.join(desktop_path, filename)
    if os.path.exists(file_path):
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # 添加来源标记
            df['data_source'] = 'real_linkedin_posts'
            df['collection_date'] = '2026-02-24'
            
            all_data.append(df)
            print(f"✓ 已读取真实数据: {filename} ({len(df)} 条记录)")
        except Exception as e:
            print(f"✗ 读取失败 {filename}: {str(e)}")

if not all_data:
    print("错误: 未找到真实数据文件")
    exit(1)

# 合并所有真实数据
master_df = pd.concat(all_data, ignore_index=True)

# 去除重复行
initial_count = len(master_df)
master_df = master_df.drop_duplicates(subset=['post_id', 'content', 'source_url'], keep='first')
duplicate_count = initial_count - len(master_df)

print(f"\n数据合并完成:")
print(f"- 初始记录数: {initial_count}")
print(f"- 去重后记录数: {len(master_df)}")
print(f"- 去除重复: {duplicate_count}")

# 保存新的总表
master_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n✅ 总表重建完成!")
print(f"- 总记录数: {len(master_df)} 条真实数据")
print(f"- 输出文件: {output_file}")
print(f"- 数据来源: 2026-02-24 LinkedIn真实帖子")

# 生成清理报告
report = f"""# LinkedIn数据清理报告

## 清理时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 清理操作
- **删除模拟数据文件**: 5个文件
  - LinkedIn_Business_Posts_新增_20260225_2247.csv
  - LinkedIn_Business_Posts_新增_20260226_0122.csv
  - LinkedIn_Business_Posts_新增_20260226_0150.csv
  - LinkedIn_Business_Posts_新增_20260226_0212.csv
  - LinkedIn_Business_Posts_新增_20260226_0220.csv

- **保留真实数据文件**: 3个文件
  - LinkedIn_Business_Posts_ALL_20260224_221252.csv
  - LinkedIn_Business_Posts_ALL_20260224_221331.csv
  - LinkedIn_Business_Posts_ALL_20260224_235254.csv

## 重建后的总表
- **总记录数**: {len(master_df)} 条
- **数据来源**: 2026-02-24 LinkedIn真实帖子
- **数据质量**: 100%真实采集数据
- **去重处理**: 去除 {duplicate_count} 条重复记录

## 备份位置
模拟数据已备份至: `{desktop_path}\模拟数据备份\`

## 后续建议
1. 只使用Browser Relay采集真实LinkedIn数据
2. 建立数据真实性验证机制
3. 定期清理非真实数据

---
*数据清理完成 - 只保留真实LinkedIn帖子数据*
"""

report_file = os.path.join(desktop_path, "数据清理报告.md")
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n清理报告已生成: {report_file}")