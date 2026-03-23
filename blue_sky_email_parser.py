#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blue Sky Technics 需求汇总脚本
从 IMAP 邮箱提取 Blue Sky Technics 相关邮件需求
"""

import imaplib
import email
from email.header import decode_header
from datetime import datetime
import csv
import re
import ssl

# IMAP 配置
IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
USERNAME = "jianghaide@aeroedgeglobal.com"
PASSWORD = "arv9KztNY$JWaHx3"

def decode_mime_words(s):
    """解码 MIME 编码的字符串"""
    if not s:
        return ""
    decoded = []
    for word, encoding in decode_header(s):
        if isinstance(word, bytes):
            try:
                decoded.append(word.decode(encoding or 'utf-8', errors='ignore'))
            except:
                decoded.append(word.decode('utf-8', errors='ignore'))
        else:
            decoded.append(word)
    return ''.join(decoded)

def extract_email_body(msg):
    """提取邮件正文内容"""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
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
    return body

def is_blue_sky_email(raw_from, decoded_from, subject):
    """检查邮件是否来自 Blue Sky Technics"""
    check_text = f"{raw_from} {decoded_from} {subject}".lower()
    return "blue sky" in check_text or "bluesky" in check_text or "domas" in check_text

def parse_requirements(body, subject, date, sender_name, sender_email):
    """从邮件内容中提取需求信息"""
    requirements = []
    
    content = f"{subject}\n{body}".upper()
    content_lower = f"{subject}\n{body}"
    
    # 提取零件号
    pn_patterns = [
        r'PN[:\s]*([A-Z0-9\-]+)',
        r'PART[:\s]*NUMBER[:\s]*([A-Z0-9\-]+)',
        r'PART[:\s]*NO[:\s]*([A-Z0-9\-]+)',
        r'P/N[:\s]*([A-Z0-9\-]+)',
        r'([A-Z]{1,3}\d{4,}[-]?\d*)',
        r'(\d{6,}[-]?\d*)',
    ]
    
    # 提取数量
    qty_patterns = [
        r'QTY[:\s]*(\d+)',
        r'QUANTITY[:\s]*(\d+)',
        r'数量[:\s]*(\d+)',
        r'(\d+)\s*(PCS|PIECES|EA|个)',
    ]
    
    # 提取条件
    condition_patterns = [
        r'CONDITION[:\s]*(SV|NS|NE|OH|TS|AR|FN|AS)',
        r'条件[:\s]*(SV|NS|NE|OH|TS|AR|FN|AS)',
        r'\b(SV|NS|NE|OH|TS|AR|FN|AS)\b',
    ]
    
    # 提取目标价格
    price_patterns = [
        r'TARGET[:\s]*PRICE[:\s]*\$?([\d,\.]+)',
        r'目标价[:\s]*\$?([\d,\.]+)',
        r'USD[:\s]*([\d,\.]+)',
        r'\$([\d,\.]+)',
    ]
    
    # 提取产品描述
    desc_patterns = [
        r'DESCRIPTION[:\s]*(.+?)(?:\n|$)',
        r'产品[:\s]*(.+?)(?:\n|$)',
        r'ITEM[:\s]*(.+?)(?:\n|$)',
        r'REQUIREMENT[:\s]*(.+?)(?:\n|$)',
        r'NEED[:\s]*(.+?)(?:\n|$)',
        r'LOOKING FOR[:\s]*(.+?)(?:\n|$)',
        r'WANTED[:\s]*(.+?)(?:\n|$)',
    ]
    
    # 尝试提取零件号
    pn = ""
    for pattern in pn_patterns:
        match = re.search(pattern, content_lower, re.IGNORECASE)
        if match:
            pn = match.group(1).strip()
            break
    
    # 尝试提取数量
    qty = ""
    for pattern in qty_patterns:
        match = re.search(pattern, content_lower, re.IGNORECASE)
        if match:
            qty = match.group(1).strip()
            break
    
    # 尝试提取条件
    condition = ""
    for pattern in condition_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            condition = match.group(1).strip().upper()
            break
    
    # 尝试提取目标价格
    target_price = ""
    for pattern in price_patterns:
        match = re.search(pattern, content_lower, re.IGNORECASE)
        if match:
            target_price = match.group(1).strip()
            break
    
    # 尝试提取产品描述
    description = ""
    for pattern in desc_patterns:
        match = re.search(pattern, content_lower, re.IGNORECASE)
        if match:
            description = match.group(1).strip()[:100]
            break
    
    if not description and subject:
        description = subject[:100]
    
    # 判断状态
    status = "待报价"
    status_lower = content_lower.lower()
    if any(kw in status_lower for kw in ['quoted', '报价', 'quote sent']):
        status = "已报价"
    elif any(kw in status_lower for kw in ['sold', '成交', 'closed', 'deal']):
        status = "已成交"
    elif any(kw in status_lower for kw in ['cancelled', '取消', 'closed', '关闭']):
        status = "已关闭"
    
    # 分类
    category = "其他"
    if any(kw in content_lower for kw in ['electronic', '电子', 'avionics', 'computer', 'indicator', 'sensor', 'control']):
        category = "电子类"
    elif any(kw in content_lower for kw in ['mechanical', '机械', 'gear', 'bearing', 'shaft', 'valve']):
        category = "机械类"
    elif any(kw in content_lower for kw in ['material', '航材', 'aircraft', 'engine', 'landing', 'part']):
        category = "航材类"
    
    requirements.append({
        '日期': date,
        '发件人': f"{sender_name} <{sender_email}>",
        '主题': subject,
        '零件号': pn,
        '产品描述': description,
        '数量': qty,
        '条件': condition,
        '目标价': target_price,
        '状态': status,
        '类别': category,
        '备注': ""
    })
    
    return requirements

def connect_imap():
    """连接 IMAP 服务器"""
    print(f"Connecting to IMAP: {IMAP_SERVER}:{IMAP_PORT}")
    ssl_context = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ssl_context)
    print(f"Login: {USERNAME}")
    mail.login(USERNAME, PASSWORD)
    mail.select("INBOX")
    print("Selected INBOX")
    return mail

def search_emails(mail):
    """搜索 Blue Sky Technics 相关邮件"""
    print("Searching for Blue Sky Technics emails...")
    
    status, messages = mail.search(None, "ALL")
    if status != "OK":
        print("Search failed")
        return []
    
    all_email_ids = messages[0].split()
    print(f"Total emails in INBOX: {len(all_email_ids)}")
    
    blue_sky_ids = []
    
    for i, email_id in enumerate(all_email_ids, 1):
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(all_email_ids)}")
        
        try:
            status, msg_data = mail.fetch(email_id, "(RFC822 HEADER.FIELDS (FROM SUBJECT))")
            if status != "OK":
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    raw_from = msg.get("From", "")
                    decoded_from = decode_mime_words(raw_from)
                    subject = decode_mime_words(msg.get("Subject", ""))
                    
                    if is_blue_sky_email(raw_from, decoded_from, subject):
                        blue_sky_ids.append(email_id)
                        print(f"  [FOUND] {decoded_from[:60]} - {subject[:40]}")
        except Exception as e:
            continue
    
    print(f"\nTotal Blue Sky emails found: {len(blue_sky_ids)}")
    return blue_sky_ids

def fetch_and_parse_emails(mail, email_ids):
    """获取并解析邮件"""
    all_requirements = []
    
    for i, email_id in enumerate(email_ids, 1):
        print(f"\nProcessing email {i}/{len(email_ids)}...")
        
        try:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    sender = decode_mime_words(msg.get("From", ""))
                    sender_email = ""
                    sender_name = ""
                    
                    if "<" in sender and ">" in sender:
                        match = re.match(r'(.+?)\s*<(.+?)>', sender)
                        if match:
                            sender_name = match.group(1).strip()
                            sender_email = match.group(2).strip()
                    else:
                        sender_email = sender
                    
                    subject = decode_mime_words(msg.get("Subject", ""))
                    
                    date_str = msg.get("Date", "")
                    try:
                        date_obj = email.utils.parsedate_to_datetime(date_str)
                        date = date_obj.strftime("%Y-%m-%d")
                    except:
                        date = date_str[:10] if date_str else "未知"
                    
                    body = extract_email_body(msg)
                    
                    print(f"  From: {sender[:60]}")
                    print(f"  Subject: {subject[:60]}")
                    print(f"  Date: {date}")
                    print(f"  Body preview: {body[:200]}...")
                    
                    requirements = parse_requirements(body, subject, date, sender_name, sender_email)
                    all_requirements.extend(requirements)
                    
        except Exception as e:
            print(f"Error processing email: {e}")
            continue
    
    return all_requirements

def generate_report(requirements):
    """生成汇总报告"""
    print("\n" + "="*80)
    print("Blue Sky Technics 需求汇总 (2026-01-01 至今)")
    print("="*80)
    
    print("\n### 需求清单")
    print("| # | 日期 | 零件号 | 产品描述 | 数量 | 条件 | 目标价 | 状态 | 备注 |")
    print("|---|------|--------|----------|------|------|--------|------|------|")
    
    for i, req in enumerate(requirements, 1):
        desc = req['产品描述'][:20] if req['产品描述'] else ""
        print(f"| {i} | {req['日期']} | {req['零件号']} | {desc} | {req['数量']} | {req['条件']} | {req['目标价']} | {req['状态']} | {req['备注']} |")
    
    print("\n### 按状态统计")
    status_count = {}
    for req in requirements:
        status = req['状态']
        status_count[status] = status_count.get(status, 0) + 1
    
    for status, count in status_count.items():
        print(f"- {status}: {count} 项")
    
    print("\n### 按产品类别统计")
    category_count = {}
    for req in requirements:
        category = req['类别']
        category_count[category] = category_count.get(category, 0) + 1
    
    for category, count in category_count.items():
        print(f"- {category}: {count} 项")
    
    print("\n### 重点推荐报价项目")
    pending_quotes = [r for r in requirements if r['状态'] == '待报价' and r['零件号']]
    if pending_quotes:
        for req in pending_quotes[:5]:
            print(f"- {req['零件号']}: {req['产品描述']} (数量：{req['数量']}, 条件：{req['条件']})")
    else:
        print("暂无待报价项目")
    
    return status_count, category_count

def save_to_csv(requirements, filepath):
    """保存为 CSV 文件"""
    print(f"\nSaving CSV: {filepath}")
    
    fieldnames = ['日期', '发件人', '主题', '零件号', '产品描述', '数量', '条件', '目标价', '状态', '类别', '备注']
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(requirements)
    
    print(f"Saved {len(requirements)} records to CSV")

def main():
    """主函数"""
    print("="*80)
    print("Blue Sky Technics Requirements Summary Tool")
    print("="*80)
    
    mail = connect_imap()
    email_ids = search_emails(mail)
    
    if not email_ids:
        print("No related emails found")
        mail.close()
        mail.logout()
        return
    
    requirements = fetch_and_parse_emails(mail, email_ids)
    
    mail.close()
    mail.logout()
    
    if not requirements:
        print("No valid requirements extracted")
        return
    
    generate_report(requirements)
    
    csv_path = "C:/Users/Haide/Desktop/Blue_Sky_Technics_需求汇总_2026-01-01_至今.csv"
    save_to_csv(requirements, csv_path)
    
    print("\n" + "="*80)
    print("Processing Complete!")
    print("="*80)

if __name__ == "__main__":
    main()
