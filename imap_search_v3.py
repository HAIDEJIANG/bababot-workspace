#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMAP 搜索脚本 v3 - 搜索已发送和收件箱中的客户邮件
"""

import imaplib
import email
from email.header import decode_header
import ssl
import os
import re

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

def extract_email_info(msg, folder_name):
    """提取邮件信息"""
    info = {
        'date': '',
        'part_number': '',
        'description': '',
        'quantity': '',
        'condition': '',
        'subject': '',
        'from': '',
        'to': '',
        'folder': folder_name,
        'status': '待处理'
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
    
    # 获取正文
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
    
    text = body + " " + info['subject']
    
    # 提取零件号
    part_patterns = [
        r'P/N[:\s]*([A-Z0-9\-]+)',
        r'PN[:\s]*([A-Z0-9\-]+)',
        r'Part\s*Number[:\s]*([A-Z0-9\-]+)',
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
    
    # 描述
    if info['part_number']:
        info['description'] = f"Part: {info['part_number']}"
    else:
        info['description'] = info['subject'][:80]
    
    # 检查是否已回复（如果是 TO 客户的邮件，说明已回复）
    if folder_name == 'Sent':
        info['status'] = '已回复'
    
    return info

def search_folder(mail, folder, customer_name, search_terms):
    """搜索特定文件夹"""
    results = []
    
    try:
        # 尝试选择文件夹
        status, _ = mail.select(folder)
        if status != 'OK':
            return results
        
        print(f"\n搜索文件夹：{folder}")
        
        # 对每个搜索词进行搜索
        for term in search_terms:
            # FROM 搜索
            status, messages = mail.search(None, f'(FROM "{term}")')
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                print(f"  FROM '{term}': {len(email_ids)} 封")
                
                for email_id in email_ids[:100]:  # 限制每词最多 100 封
                    try:
                        status, msg_data = mail.fetch(email_id, '(RFC822)')
                        if status != 'OK':
                            continue
                        
                        msg = email.message_from_bytes(msg_data[0][1])
                        info = extract_email_info(msg, folder)
                        info['customer'] = customer_name
                        
                        # 检查是否是业务相关
                        full_text = msg.as_string()[:3000].lower()
                        business_keywords = ['rfq', 'quote', 'price', 'avail', 'offer', 'part', 'p/n', 
                                            'condition', 'aircraft', 'engine', 'landing', 'gear', 
                                            'material', 'stock', 'demand', 'requirement', 'need']
                        
                        is_business = any(kw in full_text for kw in business_keywords)
                        
                        if is_business or info['part_number']:
                            # 去重
                            if not any(r['subject'] == info['subject'] and r['date'] == info['date'] for r in results):
                                results.append(info)
                                print(f"    + [{info['date']}] {info['subject'][:60]}")
                    
                    except Exception as e:
                        continue
            
            # TO 搜索（查找我们发给客户的邮件）
            status, messages = mail.search(None, f'(TO "{term}")')
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                print(f"  TO '{term}': {len(email_ids)} 封")
                
                for email_id in email_ids[:50]:
                    try:
                        status, msg_data = mail.fetch(email_id, '(RFC822)')
                        if status != 'OK':
                            continue
                        
                        msg = email.message_from_bytes(msg_data[0][1])
                        info = extract_email_info(msg, folder)
                        info['customer'] = customer_name
                        
                        if info['part_number'] or any(kw in info['subject'].lower() for kw in ['rfq', 'quote', 'price', 'offer']):
                            if not any(r['subject'] == info['subject'] and r['date'] == info['date'] for r in results):
                                results.append(info)
                                print(f"    + [{info['date']}] {info['subject'][:60]}")
                    
                    except:
                        continue
            
            # SUBJECT 搜索
            status, messages = mail.search(None, f'(SUBJECT "{term}")')
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                print(f"  SUBJECT '{term}': {len(email_ids)} 封")
        
        mail.close(folder)
        
    except Exception as e:
        print(f"文件夹 {folder} 搜索失败：{e}")
    
    return results

def generate_report(all_results):
    """生成报告"""
    report = "# 客户历史需求邮件汇总报告\n\n"
    report += f"**生成时间**: 2026-03-16\n"
    report += f"**邮箱**: {USERNAME}\n"
    report += f"**时间范围**: 2026-01-01 至今\n\n"
    report += "---\n\n"
    
    total = 0
    pending = 0
    replied = 0
    
    customers = ['Gabriel Leclair', 'Abraham Siria', 'Domas @ Blue Sky Technics']
    
    for customer in customers:
        customer_results = [r for r in all_results if r['customer'] == customer]
        
        report += f"## {customer}\n\n"
        report += "### 需求清单\n\n"
        
        if not customer_results:
            report += "*未找到相关需求邮件*\n\n"
        else:
            report += "| 日期 | 零件号 | 描述 | 数量 | 条件 | 状态 |\n"
            report += "|------|--------|------|------|------|------|\n"
            
            for r in sorted(customer_results, key=lambda x: x['date'], reverse=True)[:50]:
                desc = r['description'][:40]
                report += f"| {r['date']} | {r['part_number']} | {desc} | {r['quantity']} | {r['condition']} | {r['status']} |\n"
            
            report += "\n"
            
            c_pending = sum(1 for r in customer_results if r['status'] == '待处理')
            c_replied = sum(1 for r in customer_results if r['status'] == '已回复')
            
            report += "### 汇总\n\n"
            report += f"- 总需求数量：{len(customer_results)} 项\n"
            report += f"- 待处理：{c_pending} 项\n"
            report += f"- 已回复：{c_replied} 项\n\n"
            
            total += len(customer_results)
            pending += c_pending
            replied += c_replied
        
        report += "---\n\n"
    
    report += "## 总体汇总\n\n"
    report += f"- **总需求数量**: {total} 项\n"
    report += f"- **待处理**: {pending} 项\n"
    report += f"- **已回复**: {replied} 项\n"
    
    return report

def main():
    print("=" * 60)
    print("IMAP 客户邮件搜索 v3")
    print("=" * 60)
    
    ssl_context = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ssl_context)
    mail.login(USERNAME, AUTH_CODE)
    
    customers = {
        'Gabriel Leclair': ['Gabriel', 'Leclair', 'gabriel'],
        'Abraham Siria': ['Abraham', 'Siria', 'abraham'],
        'Domas @ Blue Sky Technics': ['Domas', 'Blue Sky', 'BlueSky', 'domas']
    }
    
    all_results = []
    
    # 搜索 INBOX 和 Sent
    folders = ['INBOX', 'Sent']
    
    for customer, terms in customers.items():
        print(f"\n{'='*60}")
        print(f"客户：{customer}")
        print(f"{'='*60}")
        
        for folder in folders:
            results = search_folder(mail, folder, customer, terms)
            all_results.extend(results)
        
        print(f"\n该客户总计：{len([r for r in all_results if r['customer'] == customer])} 封邮件")
    
    # 生成报告
    print(f"\n{'='*60}")
    print("生成报告...")
    print(f"{'='*60}")
    
    report = generate_report(all_results)
    
    report_file = "C:\\Users\\Haide\\.openclaw\\workspace\\customer_demands_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存：{report_file}")
    print(f"总计找到：{len(all_results)} 封邮件")
    
    print("\n" + "=" * 60)
    print("报告预览:")
    print("=" * 60 + "\n")
    print(report)
    
    mail.logout()

if __name__ == "__main__":
    main()
