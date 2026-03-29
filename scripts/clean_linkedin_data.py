#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理 LinkedIn 导出的原始数据（只保留真实字段）
"""

import csv
from pathlib import Path

# 输入输出文件
INPUT_FILE = Path(r"C:\Users\Haide\Desktop\OPENCLAW\LINKEDIN\LINKEDIN Connections_with_posts_FINAL.csv")
OUTPUT_FILE = Path(r"C:\Users\Haide\Desktop\LINKEDIN\linkedin_contacts_cleaned.csv")

def main():
    print("="*60)
    print("整理 LinkedIn 联系人数据（只保留真实字段）")
    print("="*60)
    
    if not INPUT_FILE.exists():
        print(f"输入文件不存在：{INPUT_FILE}")
        return
    
    # 读取数据
    contacts = []
    with open(INPUT_FILE, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 只提取 LinkedIn 导出的真实字段
            contact = {
                'contact_id': row.get('URL', ''),
                'first_name': row.get('First Name', ''),
                'last_name': row.get('Last Name', ''),
                'full_name': f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip(),
                'company': row.get('Company', ''),
                'position': row.get('Position', ''),
                'email': row.get('Email Address', ''),
                'connected_on': row.get('Connected On', '')
            }
            contacts.append(contact)
    
    print(f"读取 {len(contacts)} 位联系人")
    
    # 输出干净的数据
    fieldnames = [
        'contact_id', 'first_name', 'last_name', 'full_name',
        'company', 'position', 'email', 'connected_on'
    ]
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contacts)
    
    print(f"已保存到：{OUTPUT_FILE}")
    print("="*60)
    
    # 统计
    companies = set(c['company'] for c in contacts if c['company'])
    positions = set(c['position'] for c in contacts if c['position'])
    has_email = sum(1 for c in contacts if c['email'])
    
    print(f"公司数量：{len(companies)}")
    print(f"职位类型：{len(positions)}")
    print(f"有邮箱：{has_email} 位")
    print("="*60)
    print("\n✅ 所有数据均来自 LinkedIn 导出，无估计数据")

if __name__ == '__main__':
    main()
