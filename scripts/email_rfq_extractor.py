# -*- coding: utf-8 -*-
"""
邮箱询价信息提取脚本
从 sale@aeroedgeglobal.com 收件箱提取 2026-03-16 至今的询价/RFQ 邮件
"""

import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta
import csv

# 邮箱配置
IMAP_CONFIGS = [
    {
        'server': 'imap.qiye.163.com',
        'port': 993,
        'username': 'sale@aeroedgeglobal.com',
        'password': 'A4D8%b3x6FHAH45d',
    },
    {
        'server': 'imaphz.qiye.163.com',
        'port': 993,
        'username': 'sale@aeroedgeglobal.com',
        'password': 'A4D8%b3x6FHAH45d',
    },
]

# 输出文件
RFQ_OUTPUT_FILE = r'C:\Users\Haide\Desktop\OPENCLAW\客户询价汇总_2026-03-16_至今.csv'

# 询价/RFQ 关键词
RFQ_KEYWORDS = [
    'rfq', 'inquiry', 'enquiry', 'requirement', 'looking for', 'need', 'want',
    '求购', '需求', '询价', '寻找', '采购', 'buy', 'purchase',
    'quote', 'quotation', 'price', 'offer',  # 这些可能同时出现在询价和报价中
]

# 报价关键词 (用于排除)
QUOTE_KEYWORDS = [
    'thank you for your inquiry', 'please find attached quote', 'our quote',
    'quoted price', 'as per our quote', 'reference to your RFQ',
    'we are pleased to quote', 'attached is our quotation',
]

def decode_mime_words(s):
    """解码 MIME 编码的字符串"""
    if not s:
        return ''
    decoded = []
    for part, encoding in decode_header(s):
        if isinstance(part, bytes):
            try:
                decoded.append(part.decode(encoding or 'utf-8', errors='ignore'))
            except:
                decoded.append(part.decode('latin-1', errors='ignore'))
        else:
            decoded.append(str(part))
    return ''.join(decoded)

def extract_email_body(msg):
    """提取邮件正文"""
    body = ''
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition', ''))
            
            if 'attachment' in content_disposition:
                continue
            
            if content_type == 'text/plain':
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    body += part.get_payload(decode=True).decode(charset, errors='ignore')
                except:
                    pass
            elif content_type == 'text/html':
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    html = part.get_payload(decode=True).decode(charset, errors='ignore')
                    body += re.sub(r'<[^>]+>', ' ', html)
                except:
                    pass
    else:
        try:
            charset = msg.get_content_charset() or 'utf-8'
            body = msg.get_payload(decode=True).decode(charset, errors='ignore')
        except:
            pass
    
    return body

def extract_part_numbers(text):
    """从文本中提取件号"""
    part_numbers = []
    
    patterns = [
        r'\b([A-Z0-9]{4,}-[A-Z0-9]{2,})\b',
        r'\b([A-Z0-9]{6,})\b',
        r'PN[:\s]*([A-Z0-9-]+)',
        r'Part\s*(?:Number)?[:\s]*([A-Z0-9-]+)',
        r'件号 [::\s]*([A-Z0-9-]+)',
        r'P/N[:\s]*([A-Z0-9-]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        part_numbers.extend(matches)
    
    return list(set(part_numbers))[:10]

def extract_condition(text):
    """从文本中提取条件"""
    conditions = ['SV', 'NS', 'NE', 'AR', 'OH', 'FN', 'AS', 'OH', 'SV']
    
    text_upper = text.upper()
    for cond in conditions:
        if re.search(r'\b' + cond + r'\b', text_upper):
            return cond
    
    return ''

def extract_qty(text):
    """从文本中提取数量"""
    patterns = [
        r'qty[:\s]*(\d+)',
        r'quantity[:\s]*(\d+)',
        r'数量 [::\s]*(\d+)',
        r'(\d+)\s*pcs',
        r'(\d+)\s*units',
        r'(\d+)\s*EA',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[0]
    
    return ''

def is_rfq_email(subject, body):
    """判断是否为询价/RFQ 邮件 (非报价邮件)"""
    text = (subject + ' ' + body).lower()
    
    # 检查是否为报价回复 (排除)
    for quote_kw in QUOTE_KEYWORDS:
        if quote_kw.lower() in text:
            return False
    
    # 检查是否包含询价关键词
    rfq_count = sum(1 for keyword in RFQ_KEYWORDS if keyword.lower() in text)
    
    # 特殊模式识别
    rfq_patterns = [
        r'rfq\s*(?:from|number|#|no)',
        r'inquiry\s*(?:for|about)',
        r'looking\s+for',
        r'we\s+(?:are\s+)?(?:looking|need|want)',
        r'求购',
        r'需求',
        r'询价',
    ]
    
    for pattern in rfq_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return rfq_count >= 2

def has_attachment(msg):
    """检查邮件是否有附件"""
    for part in msg.walk():
        if part.get_content_disposition() == 'attachment':
            return True
    return False

def fetch_emails():
    """获取 2026-03-16 至今的邮件"""
    print("Connecting to email: sale@aeroedgeglobal.com")
    
    mail = None
    config = None
    
    for cfg in IMAP_CONFIGS:
        try:
            print(f"  Trying server: {cfg['server']}...")
            mail = imaplib.IMAP4_SSL(cfg['server'], cfg['port'])
            mail.login(cfg['username'], cfg['password'])
            mail.select('INBOX')
            config = cfg
            print(f"  Success!")
            break
        except Exception as e:
            print(f"  Failed: {e}")
            mail = None
            continue
    
    if not mail:
        print("All connection attempts failed")
        return []
    
    try:
        print("Email connected successfully")
        
        # 从 2026-03-16 开始
        since_date = datetime(2026, 3, 16)
        since_str = since_date.strftime('%d-%b-%Y')
        
        print(f"Date range: {since_str} to now")
        
        status, messages = mail.search(None, f'(SINCE "{since_str}")')
        
        if status != 'OK':
            print("Email search failed")
            return []
        
        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} emails")
        
        rfqs = []
        processed = 0
        
        for msg_id in email_ids:
            try:
                status, msg_data = mail.fetch(msg_id, '(RFC822)')
                if status != 'OK':
                    continue
                
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                subject = decode_mime_words(msg.get('Subject', ''))
                from_addr = decode_mime_words(msg.get('From', ''))
                date_str = msg.get('Date', '')
                
                body = extract_email_body(msg)
                
                # 判断是否为询价邮件
                if is_rfq_email(subject, body):
                    part_numbers = extract_part_numbers(body)
                    condition = extract_condition(body)
                    qty = extract_qty(body)
                    has_atta = has_attachment(msg)
                    
                    rfq_info = {
                        'Date': date_str,
                        'From': from_addr,
                        'Subject': subject,
                        'PartNumbers': '; '.join(part_numbers) if part_numbers else '',
                        'Condition': condition,
                        'Qty': qty,
                        'Has_Attachment': 'Yes' if has_atta else 'No',
                        'Summary': body[:500].replace('\n', ' ').replace('\r', ''),
                    }
                    
                    rfqs.append(rfq_info)
                    print(f"  RFQ: {subject[:50]}...")
                
                processed += 1
                if processed % 10 == 0:
                    print(f"  Processed {processed}/{len(email_ids)} emails...")
                
            except Exception as e:
                print(f"  Error: {e}")
                continue
        
        mail.close()
        mail.logout()
        
        return rfqs
        
    except Exception as e:
        print(f"Email error: {e}")
        try:
            mail.close()
            mail.logout()
        except:
            pass
        return []

def save_to_csv(rfqs, output_file):
    """保存询价信息到 CSV"""
    if not rfqs:
        print("No RFQ data to save")
        return
    
    fieldnames = ['Date', 'From', 'Subject', 'PartNumbers', 'Condition', 'Qty', 'Has_Attachment', 'Summary']
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rfqs)
    
    print(f"\nSaved {len(rfqs)} RFQs to: {output_file}")

def main():
    print("="*60)
    print("Email RFQ Extractor")
    print("="*60)
    
    rfqs = fetch_emails()
    
    save_to_csv(rfqs, RFQ_OUTPUT_FILE)
    
    if rfqs:
        print("\n" + "="*60)
        print("RFQ Summary Statistics")
        print("="*60)
        print(f"Total RFQ emails: {len(rfqs)}")
        
        # 按客户统计
        customers = {}
        for r in rfqs:
            customer = r['From'].split('<')[0].strip().strip('"')
            customers[customer] = customers.get(customer, 0) + 1
        
        print("\nCustomer distribution:")
        for customer, count in sorted(customers.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {customer}: {count} RFQs")
        
        # 附件统计
        with_atta = sum(1 for r in rfqs if r['Has_Attachment'] == 'Yes')
        print(f"\nWith attachments: {with_atta}/{len(rfqs)}")
        
        # 件号统计
        with_pn = sum(1 for r in rfqs if r['PartNumbers'])
        print(f"With part numbers: {with_pn}/{len(rfqs)}")
    
    print("\n" + "="*60)
    print("Processing complete")
    print("="*60)

if __name__ == '__main__':
    main()
