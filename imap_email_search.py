#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMAP 邮件搜索脚本 - 搜集 3 个客户的历史需求邮件（改进版）
"""

import imaplib
import email
from email.header import decode_header
from datetime import datetime
import re
import ssl
import os

# IMAP 配置
IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
USERNAME = "jianghaide@aeroedgeglobal.com"
AUTH_CODE = os.environ.get('IMAP_AUTH_CODE', 'arv9KztNY$JWaHx3')

# 目标客户 - 多种搜索关键词
CUSTOMERS = {
    "Gabriel Leclair": ["Gabriel", "Leclair", "gabriel.leclair", "gabriel@", "LECLAIR"],
    "Abraham Siria": ["Abraham", "Siria", "abraham.siria", "abraham@", "SIRIA"],
    "Domas @ Blue Sky Technics": ["Domas", "Blue Sky", "BlueSky", "domas@", "DOMAS", "BLUE"]
}

# 时间范围：2026-01-01 至今
SINCE_DATE = "01-Jan-2026"

def decode_mime_words(header):
    """解码 MIME 编码的邮件头"""
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
            decoded += part
    return decoded

def extract_email_info(msg):
    """从邮件中提取需求信息"""
    info = {
        'date': '',
        'part_number': '',
        'description': '',
        'quantity': '',
        'condition': '',
        'subject': '',
        'status': '待处理',
        'from': ''
    }
    
    # 获取邮件头信息
    info['subject'] = decode_mime_words(msg.get('Subject', ''))
    info['from'] = decode_mime_words(msg.get('From', ''))
    
    date_str = msg.get('Date', '')
    if date_str:
        try:
            parsed_date = email.utils.parsedate_to_datetime(date_str)
            info['date'] = parsed_date.strftime('%Y-%m-%d')
        except:
            info['date'] = date_str[:20] if date_str else ''
    
    # 获取邮件正文
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    body += part.get_payload(decode=True).decode(charset, errors='ignore')
                except:
                    pass
    else:
        try:
            charset = msg.get_content_charset() or 'utf-8'
            body = msg.get_payload(decode=True).decode(charset, errors='ignore')
        except:
            pass
    
    # 从正文和主题中提取信息
    text_to_search = body + " " + info['subject']
    
    # 提取零件号（多种模式）
    part_patterns = [
        r'P/N[:\s]*([A-Z0-9\-]+)',
        r'PN[:\s]*([A-Z0-9\-]+)',
        r'Part[:\s]*Number[:\s]*([A-Z0-9\-]+)',
        r'零件号 [:\s]*([A-Z0-9\-]+)',
        r'([A-Z]{1,3}\d{4,}[-]?\d*)',
        r'(\d{6,}[-]?\d*)',
    ]
    for pattern in part_patterns:
        match = re.search(pattern, text_to_search, re.IGNORECASE)
        if match:
            info['part_number'] = match.group(1).strip()
            break
    
    # 提取数量
    qty_patterns = [
        r'QTY[:\s]*(\d+)',
        r'Quantity[:\s]*(\d+)',
        r'数量 [:\s]*(\d+)',
        r'(\d+)\s*(EA|PCS|Pieces|个)',
        r'need\s+(\d+)',
        r'looking\s+for\s+(\d+)',
    ]
    for pattern in qty_patterns:
        match = re.search(pattern, text_to_search, re.IGNORECASE)
        if match:
            info['quantity'] = match.group(1)
            break
    
    # 提取条件（SV/NS/NE 等）
    cond_patterns = [
        r'\b(SV|NS|NE|OH|AR|TSO)\b',
        r'Condition[:\s]*(SV|NS|NE|OH|AR)',
        r'条件 [:\s]*(SV|NS|NE|OH|AR)',
    ]
    for pattern in cond_patterns:
        match = re.search(pattern, text_to_search, re.IGNORECASE)
        if match:
            info['condition'] = match.group(1).upper()
            break
    
    # 提取描述
    desc_patterns = [
        r'Description[:\s]*(.+?)(?:\n|$)',
        r'描述 [:\s]*(.+?)(?:\n|$)',
        r'Request[:\s]*(.+?)(?:\n|$)',
        r'需求 [:\s]*(.+?)(?:\n|$)',
    ]
    for pattern in desc_patterns:
        match = re.search(pattern, text_to_search, re.IGNORECASE)
        if match:
            info['description'] = match.group(1).strip()[:100]
            break
    
    # 如果没有提取到描述，使用主题
    if not info['description'] and info['subject']:
        info['description'] = info['subject'][:100]
    
    # 检查是否已回复
    reply_indicators = ['re:', '回复', '回复:', 'answered', 'quoted']
    if any(ind in info['subject'].lower() for ind in reply_indicators):
        info['status'] = '已回复'
    
    return info

def search_customer_emails(customer_name, search_terms):
    """搜索特定客户的邮件"""
    results = []
    
    try:
        ssl_context = ssl.create_default_context()
        
        print(f"正在连接 IMAP 服务器...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ssl_context)
        
        print(f"正在登录...")
        mail.login(USERNAME, AUTH_CODE)
        print(f"登录成功！")
        
        # 列出所有文件夹
        status, folders = mail.list()
        print(f"可用文件夹：{len(folders)} 个")
        
        # 尝试不同的文件夹
        folders_to_check = ['INBOX', 'INBOX.收件箱', '收件箱', 'Sent', 'Sent Items']
        
        for folder in folders_to_check:
            try:
                status, messages = mail.select(folder)
                if status != 'OK':
                    continue
                
                print(f"\n检查文件夹：{folder}")
                
                # 尝试多种搜索方式
                for term in search_terms:
                    # 方式 1: FROM 搜索
                    search_criteria = f'(FROM "{term}" SINCE "{SINCE_DATE}")'
                    status, email_ids = mail.search(None, search_criteria)
                    
                    if status == 'OK' and email_ids[0]:
                        ids = email_ids[0].split()
                        print(f"  FROM '{term}': 找到 {len(ids)} 封邮件")
                        
                        for email_id in ids[:50]:  # 限制每客户最多 50 封
                            try:
                                status, msg_data = mail.fetch(email_id, '(RFC822)')
                                if status != 'OK':
                                    continue
                                
                                raw_email = msg_data[0][1]
                                msg = email.message_from_bytes(raw_email)
                                email_info = extract_email_info(msg)
                                email_info['customer'] = customer_name
                                
                                # 检查是否是业务相关邮件
                                subject_lower = email_info['subject'].lower()
                                body_lower = (msg.as_string()[:2000]).lower()
                                
                                business_keywords = ['rfq', 'quote', 'price', 'avail', 'offer', '需求', '询价', 
                                                     'part', 'p/n', 'condition', 'aircraft', 'engine', 
                                                     'landing', 'gear', 'material', 'stock']
                                
                                is_business = any(kw in subject_lower or kw in body_lower for kw in business_keywords)
                                
                                if is_business or email_info['part_number']:
                                    # 去重
                                    if not any(r['subject'] == email_info['subject'] and r['date'] == email_info['date'] for r in results):
                                        results.append(email_info)
                                        print(f"    + {email_info['date']} | {email_info['part_number']} | {email_info['subject'][:50]}")
                                
                            except Exception as e:
                                continue
                    
                    # 方式 2: SUBJECT 搜索（补充）
                    search_criteria = f'(SUBJECT "{term}" SINCE "{SINCE_DATE}")'
                    status, email_ids = mail.search(None, search_criteria)
                    
                    if status == 'OK' and email_ids[0]:
                        ids = email_ids[0].split()
                        print(f"  SUBJECT '{term}': 找到 {len(ids)} 封邮件")
                        
                        for email_id in ids[:20]:
                            try:
                                status, msg_data = mail.fetch(email_id, '(RFC822)')
                                if status != 'OK':
                                    continue
                                
                                raw_email = msg_data[0][1]
                                msg = email.message_from_bytes(raw_email)
                                email_info = extract_email_info(msg)
                                email_info['customer'] = customer_name
                                
                                # 检查发件人是否匹配其他关键词
                                from_match = any(t.lower() in email_info['from'].lower() for t in search_terms if t != term)
                                
                                if from_match and not any(r['subject'] == email_info['subject'] and r['date'] == email_info['date'] for r in results):
                                    results.append(email_info)
                                    print(f"    + {email_info['date']} | {email_info['subject'][:60]}")
                            
                            except:
                                continue
                
                mail.close()
                
            except Exception as e:
                print(f"文件夹 {folder} 检查失败：{e}")
                continue
        
        mail.logout()
        
    except Exception as e:
        print(f"IMAP 错误：{e}")
    
    return results

def generate_report(all_results):
    """生成 Markdown 格式的报告"""
    report = "# 客户历史需求邮件汇总报告\n\n"
    report += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"**时间范围**: 2026-01-01 至今\n"
    report += f"**邮箱**: {USERNAME}\n\n"
    report += "---\n\n"
    
    total_demands = 0
    total_pending = 0
    total_replied = 0
    
    # 按客户分组
    customers_data = {}
    for result in all_results:
        customer = result['customer']
        if customer not in customers_data:
            customers_data[customer] = []
        customers_data[customer].append(result)
    
    # 为每个客户生成报告
    for customer, demands in customers_data.items():
        report += f"## {customer}\n\n"
        report += "### 需求清单\n\n"
        
        if not demands:
            report += "*没有找到相关需求邮件*\n\n"
        else:
            report += "| 日期 | 零件号 | 描述 | 数量 | 条件 | 状态 |\n"
            report += "|------|--------|------|------|------|------|\n"
            
            for d in sorted(demands, key=lambda x: x['date'], reverse=True):
                desc = d['description'][:40] + "..." if len(d['description']) > 40 else d['description']
                report += f"| {d['date']} | {d['part_number']} | {desc} | {d['quantity']} | {d['condition']} | {d['status']} |\n"
            
            report += "\n"
            
            pending = sum(1 for d in demands if d['status'] == '待处理')
            replied = sum(1 for d in demands if d['status'] == '已回复')
            
            report += "### 汇总\n\n"
            report += f"- 总需求数量：{len(demands)} 项\n"
            report += f"- 待处理：{pending} 项\n"
            report += f"- 已回复：{replied} 项\n\n"
            
            total_demands += len(demands)
            total_pending += pending
            total_replied += replied
        
        report += "---\n\n"
    
    report += "## 总体汇总\n\n"
    report += f"- **总需求数量**: {total_demands} 项\n"
    report += f"- **待处理**: {total_pending} 项\n"
    report += f"- **已回复**: {total_replied} 项\n"
    
    return report

def main():
    print("=" * 60)
    print("客户历史需求邮件搜集（改进版）")
    print("=" * 60)
    
    all_results = []
    
    for customer, terms in CUSTOMERS.items():
        print(f"\n{'='*60}")
        print(f"客户：{customer}")
        print(f"搜索关键词：{', '.join(terms)}")
        print(f"{'='*60}")
        
        results = search_customer_emails(customer, terms)
        all_results.extend(results)
        
        print(f"\n该客户找到 {len(results)} 个需求")
    
    print(f"\n{'='*60}")
    print("生成报告...")
    print(f"{'='*60}")
    
    report = generate_report(all_results)
    
    report_file = "C:\\Users\\Haide\\.openclaw\\workspace\\customer_demands_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存：{report_file}")
    print(f"总计：{len(all_results)} 个客户需求")
    
    # 显示报告内容
    print(f"\n{'='*60}")
    print("报告预览:")
    print(f"{'='*60}\n")
    print(report)
    
    return all_results

if __name__ == "__main__":
    main()
