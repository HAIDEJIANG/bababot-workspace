#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMAP 搜索脚本 v4 - 修复 bug 并改进搜索
"""

import imaplib
import email
from email.header import decode_header
import ssl
import os
import re
from datetime import datetime

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

def get_email_body(msg):
    """获取邮件正文"""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode(charset, errors='ignore')
                except:
                    pass
    else:
        try:
            charset = msg.get_content_charset() or 'utf-8'
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(charset, errors='ignore')
        except:
            pass
    return body

def extract_email_info(msg, folder_name):
    """提取邮件信息"""
    info = {
        'date': '',
        'part_number': '',
        'quantity': '',
        'condition': '',
        'subject': '',
        'from': '',
        'to': '',
        'folder': folder_name,
        'status': '待处理',
        'body_preview': ''
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
    
    body = get_email_body(msg)
    info['body_preview'] = body[:200]
    
    text = body + " " + info['subject']
    
    # 提取零件号
    part_patterns = [
        r'P/N[:\s]*([A-Z0-9\-]+)',
        r'PN[:\s]*([A-Z0-9\-]+)',
        r'Part\s*#[:\s]*([A-Z0-9\-]+)',
        r'([A-Z]{2,4}\d{4,}[-]?\d*)',
        r'(\d{6,}[-]\d+)',
    ]
    for pattern in part_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['part_number'] = match.group(1).strip()
            break
    
    # 提取数量
    qty_patterns = [
        r'QTY[:\s]*(\d+)',
        r'Quantity[:\s]*(\d+)',
        r'(\d+)\s*(EA|PCS|Pieces)',
    ]
    for pattern in qty_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['quantity'] = match.group(1)
            break
    
    # 提取条件
    cond_match = re.search(r'\b(SV|NS|NE|OH|AR|TSO)\b', text, re.IGNORECASE)
    if cond_match:
        info['condition'] = cond_match.group(1).upper()
    
    # 状态判断
    if folder_name in ['Sent', '&XfJT0ZAB-']:
        info['status'] = '已回复'
    
    return info

def main():
    print("=" * 60)
    print("IMAP 客户邮件搜索 v4")
    print("=" * 60)
    
    ssl_context = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ssl_context)
    mail.login(USERNAME, AUTH_CODE)
    
    # 选择 INBOX
    mail.select('INBOX')
    
    # 获取所有邮件
    status, messages = mail.search(None, 'ALL')
    if status != 'OK':
        print("搜索失败")
        return
    
    all_emails = messages[0].split()
    print(f"\nINBOX 总邮件数：{len(all_emails)}")
    
    # 目标客户关键词
    customer_keywords = {
        'Gabriel Leclair': ['gabriel', 'leclair', 'g.leclair'],
        'Abraham Siria': ['abraham', 'siria', 'a.siria'],
        'Domas @ Blue Sky Technics': ['domas', 'blue sky', 'bluesky', 'blue']
    }
    
    results = {customer: [] for customer in customer_keywords}
    
    print("\n开始扫描邮件...")
    
    # 扫描所有邮件
    for i, email_id in enumerate(all_emails):
        try:
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if status != 'OK':
                continue
            
            msg = email.message_from_bytes(msg_data[0][1])
            
            from_addr = decode_mime_words(msg.get('From', '')).lower()
            to_addr = decode_mime_words(msg.get('To', '')).lower()
            subject = decode_mime_words(msg.get('Subject', '')).lower()
            date = msg.get('Date', '')
            
            try:
                parsed_date = email.utils.parsedate_to_datetime(date)
                date_str = parsed_date.strftime('%Y-%m-%d')
                # 只处理 2026 年以后的邮件
                if parsed_date.year < 2026:
                    continue
            except:
                date_str = ''
            
            # 检查是否匹配目标客户
            matched_customer = None
            for customer, keywords in customer_keywords.items():
                for kw in keywords:
                    if kw in from_addr or kw in to_addr or kw in subject:
                        matched_customer = customer
                        break
                if matched_customer:
                    break
            
            if matched_customer:
                info = extract_email_info(msg, 'INBOX')
                info['customer'] = matched_customer
                
                # 检查是否是业务相关邮件
                full_text = (msg.as_string()[:3000] + subject).lower()
                business_keywords = ['rfq', 'quote', 'price', 'avail', 'offer', 'part', 'p/n', 
                                    'condition', 'aircraft', 'engine', 'landing', 'gear', 
                                    'material', 'stock', 'demand', 'requirement', 'need',
                                    'looking for', 'want', 'require']
                
                is_business = any(kw in full_text for kw in business_keywords)
                
                if is_business or info['part_number']:
                    # 去重
                    exists = any(r['subject'] == info['subject'] and r['date'] == info['date'] 
                                for r in results[matched_customer])
                    if not exists:
                        results[matched_customer].append(info)
                        print(f"[{date_str}] {matched_customer}: {info['subject'][:60]}")
        
        except Exception as e:
            continue
    
    # 检查已发送文件夹
    print("\n检查已发送文件夹...")
    try:
        mail.select('Sent')
        status, messages = mail.search(None, 'ALL')
        if status == 'OK':
            sent_emails = messages[0].split()
            print(f"已发送邮件数：{len(sent_emails)}")
            
            for email_id in sent_emails:
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    to_addr = decode_mime_words(msg.get('To', '')).lower()
                    subject = decode_mime_words(msg.get('Subject', '')).lower()
                    date = msg.get('Date', '')
                    
                    try:
                        parsed_date = email.utils.parsedate_to_datetime(date)
                        date_str = parsed_date.strftime('%Y-%m-%d')
                        if parsed_date.year < 2026:
                            continue
                    except:
                        date_str = ''
                    
                    # 检查是否发送给目标客户
                    matched_customer = None
                    for customer, keywords in customer_keywords.items():
                        for kw in keywords:
                            if kw in to_addr or kw in subject:
                                matched_customer = customer
                                break
                        if matched_customer:
                            break
                    
                    if matched_customer:
                        info = extract_email_info(msg, 'Sent')
                        info['customer'] = matched_customer
                        
                        exists = any(r['subject'] == info['subject'] and r['date'] == info['date'] 
                                    for r in results[matched_customer])
                        if not exists:
                            results[matched_customer].append(info)
                            print(f"[{date_str}] TO {matched_customer}: {info['subject'][:60]}")
                
                except:
                    continue
        
        mail.close()
    except Exception as e:
        print(f"已发送文件夹检查失败：{e}")
    
    mail.logout()
    
    # 生成报告
    print("\n" + "=" * 60)
    print("生成报告...")
    print("=" * 60)
    
    report = "# 客户历史需求邮件汇总报告\n\n"
    report += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"**邮箱**: {USERNAME}\n"
    report += f"**时间范围**: 2026-01-01 至今\n\n"
    report += "---\n\n"
    
    total = 0
    total_pending = 0
    total_replied = 0
    
    for customer, customer_results in results.items():
        report += f"## {customer}\n\n"
        report += "### 需求清单\n\n"
        
        if not customer_results:
            report += "*未找到相关需求邮件*\n\n"
        else:
            report += "| 日期 | 零件号 | 描述 | 数量 | 条件 | 状态 |\n"
            report += "|------|--------|------|------|------|------|\n"
            
            for r in sorted(customer_results, key=lambda x: x['date'], reverse=True):
                desc = r['subject'][:40] if not r['part_number'] else f"Part: {r['part_number']}"
                report += f"| {r['date']} | {r['part_number']} | {desc} | {r['quantity']} | {r['condition']} | {r['status']} |\n"
            
            report += "\n"
            
            c_pending = sum(1 for r in customer_results if r['status'] == '待处理')
            c_replied = sum(1 for r in customer_results if r['status'] == '已回复')
            
            report += "### 汇总\n\n"
            report += f"- 总需求数量：{len(customer_results)} 项\n"
            report += f"- 待处理：{c_pending} 项\n"
            report += f"- 已回复：{c_replied} 项\n\n"
            
            total += len(customer_results)
            total_pending += c_pending
            total_replied += c_replied
        
        report += "---\n\n"
    
    report += "## 总体汇总\n\n"
    report += f"- **总需求数量**: {total} 项\n"
    report += f"- **待处理**: {total_pending} 项\n"
    report += f"- **已回复**: {total_replied} 项\n"
    
    # 保存报告
    report_file = "C:\\Users\\Haide\\.openclaw\\workspace\\customer_demands_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存：{report_file}")
    print(f"\n总计找到：{total} 封邮件")
    
    print("\n" + "=" * 60)
    print("报告预览:")
    print("=" * 60 + "\n")
    print(report)

if __name__ == "__main__":
    main()
