# -*- coding: utf-8 -*-
"""
合并客户需求清单 CSV 文件
"""

import csv
from datetime import datetime

print("=== 合并客户需求清单 ===")
print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 输入文件
blue_sky_file = r"C:\Users\Haide\Desktop\Blue_Sky_Full_Analysis.csv"
initial_turbo_file = r"C:\Users\Haide\Desktop\Initial_Turbo_Full_Analysis.csv"
output_file = r"C:\Users\Haide\Desktop\客户需求清单.csv"

# 读取 Blue Sky Technics
print("\n[1/3] 读取 Blue Sky Technics 数据...")
blue_sky_rows = []
try:
    with open(blue_sky_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['Customer'] = 'Blue Sky Technics'
            blue_sky_rows.append(row)
    print(f"[OK] 读取 {len(blue_sky_rows)} 条记录")
except Exception as e:
    print(f"[ERROR] 读取失败：{e}")
    blue_sky_rows = []

# 读取 Initial Aviation 和 Turbo Resources
print("\n[2/3] 读取 Initial Aviation 和 Turbo Resources 数据...")
initial_turbo_rows = []
try:
    with open(initial_turbo_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 标准化字段名
            new_row = {
                'Date': row.get('Date', ''),
                'Customer': row.get('Company', ''),
                'From': row.get('From', ''),
                'Subject': row.get('Subject', ''),
                'PartNumber': row.get('PartNumber', ''),
                'Description': row.get('Description', ''),
            }
            initial_turbo_rows.append(new_row)
    print(f"[OK] 读取 {len(initial_turbo_rows)} 条记录")
except Exception as e:
    print(f"[ERROR] 读取失败：{e}")
    initial_turbo_rows = []

# 合并数据
print("\n[3/3] 合并并导出...")
all_rows = blue_sky_rows + initial_turbo_rows

# 统一字段顺序
fieldnames = ['Date', 'Customer', 'From', 'Subject', 'PartNumber', 'Description']

if all_rows:
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"\n[OK] 已导出到：{output_file}")
    print(f"[OK] 总计 {len(all_rows)} 条记录")
    
    # 按客户统计
    customer_stats = {}
    for row in all_rows:
        c = row.get('Customer', 'Unknown')
        customer_stats[c] = customer_stats.get(c, 0) + 1
    
    print("\n=== 按客户统计 ===")
    for customer, count in sorted(customer_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {customer}: {count} 条")
    
    # 打印前 20 条预览
    print("\n=== 前 20 条预览 ===")
    for i, row in enumerate(all_rows[:20], 1):
        pn = row.get('PartNumber', 'N/A')[:20]
        desc = row.get('Description', 'N/A')[:40]
        print(f"{i:3}. {row.get('Date', 'N/A')[:10]:<10} | {row.get('Customer', 'N/A'):<25} | {pn:<20} | {desc}")
    if len(all_rows) > 20:
        print(f"... 还有 {len(all_rows) - 20} 条")
else:
    print("[ERROR] 无数据可导出")

print(f"\n结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=== 任务完成 ===")
