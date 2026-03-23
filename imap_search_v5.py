#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMAP 搜索脚本 v5 - 高效版本，只搜索最近邮件
"""

import imaplib
import email
from email.header import decode_header
import ssl
import os
import re
from datetime import datetime, timedelta

IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
USERNAME = "jianghaide@aeroedgeglobal.com"
AUTH_CODE = os.environ.get('IMAP_AUTH_CODE', 'arv9KztNY$JWaHx3')

def decode_mime_words(header):
    if not header:
        return ""
    decoded = ""
    for part, encoding in decode_header(header):
        if isinstance(part, bytes):
            try:
                decoded += part.decode(encoding or 'utf-8', errors='ignore')
            except:
                decoded += part.decode('latin-1', errors='ignore')
        else:
            decoded += str(part)
    return decoded

def extract_basic_info(msg):
    """提取基本邮件信息"""
    info = {
        'date': '',
        'subject': '',
        'from': '',
        'to': ''
    }
    
    info['subject'] = decode_mime_words(msg.get('Subject', ''))
    info['from'] = decode_mime_words(msg.get('From', ''))
    info['to'] = decode_mime_words(msg.get('To', ''))
    
    date = msg.get('Date', '')
    try:
        parsed_date = email.utils.parsedate_to_datetime(date)
        info['date'] = parsed_date.strftime('%Y-%m-%d')
    except:
        info['date'] = date[:20] if date else ''
    
    return info

def main():
    print("=" * 60)
    print("IMAP 客户邮件搜索 v5 (高效版)")
    print("=" * 60)
    
    ssl_context = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ssl_context)
    mail.login(USERNAME, AUTH_CODE)
    
    # 目标客户和可能的邮箱地址
    customers = [
        {'name': 'Gabriel Leclair', 'emails': ['gabriel.leclair', 'gabriel@', 'leclair@']},
        {'name': 'Abraham Siria', 'emails': ['abraham.siria', 'abraham@', 'siria@']},
        {'name': 'Domas @ Blue Sky Technics', 'emails': ['domas@', 'info@bluesky', 'contact@bluesky']}
    ]
    
    all_results = []
    
    # 搜索 INBOX
    mail.select('INBOX')
    
    # 获取最近 200 封邮件（避免处理全部 876 封）
    status, messages = mail.search(None, 'ALL')
    if status == 'OK':
        all_ids = messages[0].split()
        recent_ids = all_ids[-200:] if len(all_ids) > 200 else all_ids
        
        print(f"\n检查最近 {len(recent_ids)} 封邮件...")
        
        for email_id in recent_ids:
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822 HEADER.FIELDS FROM TO SUBJECT DATE)')
                if status != 'OK':
                    continue
                
                msg = email.message_from_bytes(msg_data[0][1])
                info = extract_basic_info(msg)
                
                # 检查日期（2026年以后）
                try:
                    parsed_date = email.utils.parsedate_to_datetime(msg.get('Date', ''))
                    if parsed_date.year < 2026:
                        continue
                except:
                    continue
                
                from_lower = info['from'].lower()
                to_lower = info['to'].lower()
                subject_lower = info['subject'].lower()
                
                # 检查是否匹配客户
                for customer in customers:
                    matched = False
                    for email_pattern in customer['emails']:
                        if email_pattern in from_lower or email_pattern in to_lower:
                            matched = True
                            break
                    
                    # 如果没找到邮箱匹配，尝试姓名匹配
                    if not matched:
                        name_parts = customer['name'].split('@')[0].strip().split()
                        if len(name_parts) >= 2:
                            last_name = name_parts[-1].lower()
                            if last_name in from_lower or last_name in to_lower:
                                matched = True
                    
                    if matched:
                        # 快速检查是否是业务邮件
                        business_keywords = ['rfq', 'quote', 'price', 'avail', 'offer', 'part', 'p/n', 
                                           'condition', 'aircraft', 'engine', 'landing', 'gear']
                        
                        is_business = any(kw in subject_lower for kw in business_keywords)
                        
                        if is_business:
                            result = {
                                'customer': customer['name'],
                                'date': info['date'],
                                'subject': info['subject'],
                                'from': info['from'],
                                'to': info['to'],
                                'folder': 'INBOX',
                                'status': '待处理'
                            }
                            all_results.append(result)
                            print(f"[{info['date']}] {customer['name']}: {info['subject'][:60]}")
            
            except Exception as e:
                continue
    
    # 搜索已发送文件夹
    try:
        mail.select('Sent')
        status, messages = mail.search(None, 'ALL')
        if status == 'OK':
            all_ids = messages[0].split()
            recent_ids = all_ids[-100:] if len(all_ids) > 100 else all_ids
            
            print(f"\n检查已发送最近 {len(recent_ids)} 封邮件...")
            
            for email_id in recent_ids:
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822 HEADER.FIELDS FROM TO SUBJECT DATE)')
                    if status != 'OK':
                        continue
                    
                    msg = email.message_from_bytes(msg_data[0][1])
                    info = extract_basic_info(msg)
                    
                    try:
                        parsed_date = email.utils.parsedate_to_datetime(msg.get('Date', ''))
                        if parsed_date.year < 2026:
                            continue
                    except:
                        continue
                    
                    to_lower = info['to'].lower()
                    subject_lower = info['subject'].lower()
                    
                    for customer in customers:
                        matched = False
                        for email_pattern in customer['emails']:
                            if email_pattern in to_lower:
                                matched = True
                                break
                        
                        if not matched:
                            name_parts = customer['name'].split('@')[0].strip().split()
                            if len(name_parts) >= 2:
                                last_name = name_parts[-1].lower()
                                if last_name in to_lower:
                                    matched = True
                        
                        if matched:
                            business_keywords = ['rfq', 'quote', 'price', 'offer', 'part']
                            is_business = any(kw in subject_lower for kw in business_keywords)
                            
                            if is_business:
                                result = {
                                    'customer': customer['name'],
                                    'date': info['date'],
                                    'subject': info['subject'],
                                    'from': info['from'],
                                    'to': info['to'],
                                    'folder': 'Sent',
                                    'status': '已回复'
                                }
                                all_results.append(result)
                                print(f"[{info['date']}] TO {customer['name']}: {info['subject'][:60]}")
                
                except:
                    continue
        
        mail.close()
    except:
        pass
    
    mail.logout()
    
    # 生成简单报告
    print("\n" + "=" * 60)
    print("生成报告...")
    print("=" * 60)
    
    report = "# 客户历史需求邮件汇总报告\n\n"
    report += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"**邮箱**: {USERNAME}\n"
    report += f"**时间范围**: 2026-01-01 至今\n"
    report += f"**搜索范围**: 最近 200 封收件箱邮件 + 最近 100 封已发送邮件\n\n"
    report += "---\n\n"
    
    total = len(all_results)
    pending = sum(1 for r in all_results if r['status'] == '待处理')
    replied = sum(1 for r in all_results if r['status'] == '已回复')
    
    # 按客户分组
    customers_data = {}
    for result in all_results:
        customer = result['customer']
        if customer not in customers_data:
            customers_data[customer] = []
        customers_data[customer].append(result)
    
    for customer in [c['name'] for c in customers]:
        results = customers_data.get(customer, [])
        
        report += f"## {customer}\n\n"
        report += "### 需求清单\n\n"
        
        if not results:
            report += "*未找到相关需求邮件*\n\n"
        else:
            report += "| 日期 | 主题 | 状态 |\n"
            report += "|------|------|------|\n"
            
            for r in sorted(results, key=lambda x: x['date'], reverse=True):
                subject = r['subject'][:60]
                report += f"| {r['date']} | {subject} | {r['status']} |\n"
            
            report += "\n"
            
            c_pending = sum(1 for r in results if r['status'] == '待处理')
            c_replied = sum(1 for r in results if r['status'] == '已回复')
            
            report += "### 汇总\n\n"
            report += f"- 总需求数量：{len(results)} 项\n"
            report += f"- 待处理：{c_pending} 项\n"
            report += f"- 已回复：{c_replied} 项\n\n"
        
        report += "---\n\n"
    
    report += "## 总体汇总\n\n"
    report += f"- **总需求数量**: {total} 项\n"
    report += f"- **待处理**: {pending} 项\n"
    report += f"- **已回复**: {replied} 项\n"
    
    # 保存报告
    report_file = "C:\\Users\\Haide\\.openclaw\\workspace\\customer_demands_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存：{report_file}")
    print(f"\n总计找到：{total} 封邮件")
    
    if total == 0:
        print("\n建议：")
        print("1. 检查客户实际使用的邮箱地址")
        print("2. 扩大时间范围到 2025 年")
        print("3. 手动检查邮箱中的相关邮件")
    
    print("\n" + "=" * 60)
    print("报告预览:")
    print("=" * 60 + "\n")
    print(report)

if __name__ == "__main__":
    main()
