#!/usr/bin/env python3
"""
Create DOMAS Requirements Summary Excel file
"""

import pandas as pd
from datetime import datetime
import os

def main():
    output_dir = 'C:/Users/Haide/Desktop/OPENCLAW'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'DOMAS_Requirements_Summary.xlsx')
    
    # Create DataFrame with headers only (no data since no DOMAS emails found)
    df = pd.DataFrame(columns=[
        '日期',
        '发件人邮箱',
        '邮件主题',
        '器材名称',
        '型号/件号 (Part Number)',
        '数量',
        '需求描述',
        '优先级',
        '备注'
    ])
    
    # Create Excel writer with multiple sheets
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Requirements (empty)
        df.to_excel(writer, index=False, sheet_name='DOMAS Requirements')
        
        # Sheet 2: Search Summary
        summary_data = {
            '项目': [
                '搜索执行时间',
                '检查的邮箱账号',
                'sale 邮箱状态',
                'jianghaide 邮箱状态',
                '检查的邮件总数',
                '发现的 DOMAS 邮件',
                '提取的器材需求',
                '搜索结果'
            ],
            '结果': [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '2 (sale@aeroedgeglobal.com, jianghaide@aeroedgeglobal.com)',
                '✅ 成功连接 (IMAP: imaphz.qiye.163.com:993)',
                '❌ 登录失败 (错误：ERR.LOGIN.REQCODE - 需要验证码)',
                '2,159 封 (仅 sale 邮箱)',
                '0 封',
                '0 条',
                '未在任何文件夹中找到包含"DOMAS"的邮件'
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, index=False, sheet_name='搜索摘要')
        
        # Sheet 3: Instructions
        instructions_data = {
            '后续操作建议': [
                '1. 确认 DOMAS 是否确实向这两个邮箱发送过邮件',
                '2. 检查 jianghaide 邮箱是否需要网页端验证码',
                '3. 确认 DOMAS 使用的发件人邮箱地址',
                '4. 检查邮件是否被删除或归档到其他位置',
                '5. 考虑搜索其他关键词（客户名称、项目名称等）'
            ],
            '说明': [
                'sale 邮箱已检查所有 6 个文件夹（收件箱、已发送、草稿箱等）',
                'jianghaide 邮箱因验证码问题无法访问',
                '搜索条件：FROM:"DOMAS" OR SUBJECT:"DOMAS" OR BODY:"DOMAS"',
                '如需重新执行搜索，请解决验证码问题后运行脚本',
                ''
            ]
        }
        df_instructions = pd.DataFrame(instructions_data)
        df_instructions.to_excel(writer, index=False, sheet_name='操作建议')
    
    print(f"[OK] Excel file created: {output_file}")
    print(f"\nFile contains 3 sheets:")
    print(f"  1. DOMAS Requirements - Equipment requirements (empty)")
    print(f"  2. Search Summary - Search statistics")
    print(f"  3. Instructions - Next steps")
    
    # Also create a text summary
    report_file = os.path.join(output_dir, 'DOMAS_Search_Summary.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("DOMAS 邮件搜索总结报告\n")
        f.write("="*60 + "\n\n")
        f.write(f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("邮箱检查结果:\n")
        f.write("  sale@aeroedgeglobal.com:\n")
        f.write("    - 连接状态：成功\n")
        f.write("    - 邮件总数：2,159 封\n")
        f.write("    - DOMAS 邮件：0 封\n\n")
        f.write("  jianghaide@aeroedgeglobal.com:\n")
        f.write("    - 连接状态：失败 (需要验证码)\n")
        f.write("    - DOMAS 邮件：无法检查\n\n")
        f.write("搜索结果:\n")
        f.write("  - 检查的文件夹：6 个 (INBOX, Sent, Drafts, Trash, Junk, 其他)\n")
        f.write("  - 搜索条件：FROM:\"DOMAS\" OR SUBJECT:\"DOMAS\" OR BODY:\"DOMAS\"\n")
        f.write("  - 发现的 DOMAS 邮件：0 封\n")
        f.write("  - 提取的器材需求：0 条\n\n")
        f.write("输出文件:\n")
        f.write(f"  - Excel: {output_file}\n")
        f.write(f"  - 报告：C:/Users/Haide/.openclaw/workspace/DOMAS_Email_Search_Report.md\n\n")
        f.write("建议:\n")
        f.write("  1. 确认 DOMAS 是否确实向这两个邮箱发送过邮件\n")
        f.write("  2. 解决 jianghaide 邮箱的验证码问题\n")
        f.write("  3. 检查其他邮箱账号或文件夹\n")
    
    print(f"[OK] Text summary created: {report_file}")

if __name__ == '__main__':
    main()
