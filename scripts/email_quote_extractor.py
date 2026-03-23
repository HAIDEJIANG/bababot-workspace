# -*- coding: utf-8 -*-
"""
邮箱报价信息提取脚本
从 sale@aeroedgeglobal.com 收件箱提取 2026-03-16 至今的报价邮件
"""

import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta
import csv
import sys

# 邮箱配置 - 尝试多个服务器配置
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
    {
        'server': 'imap.163.com',
        'port': 993,
        'username': 'sale@aeroedgeglobal.com',
        'password': 'A4D8%b3x6FHAH45d',
    },
]

# 输出文件
OUTPUT_FILE = r'C:\Users\Haide\Desktop\OPENCLAW\邮箱报价信息汇总_2026-03-16_至今.csv'

# 邮件报价关键词
QUOTE_KEYWORDS = [
    'quote', 'quotation', 'price', 'offer', '报价', '单价', '价格', 
    'USD', 'EUR', 'CNY', '$', '€', '¥',
    'PN', 'P/N', 'Part Number', '件号',
    'Condition', 'SV', 'NS', 'NE', 'AR', 'OH',
    'Qty', 'Quantity', '数量', '台', '个', '件',
    'Lead Time', '交货期', '货期',
    'Validity', '有效期',
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
            
            # 跳过附件
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
                    # 简单 HTML 清理
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
    
    # 常见件号模式
    patterns = [
        r'\b([A-Z0-9]{4,}-[A-Z0-9]{2,})\b',  # 如 12345-AB
        r'\b([A-Z0-9]{6,})\b',  # 纯数字/字母长串
        r'PN[:\s]*([A-Z0-9-]+)',  # PN: XXX
        r'Part\s*(?:Number)?[:\s]*([A-Z0-9-]+)',  # Part Number: XXX
        r'件号 [::\s]*([A-Z0-9-]+)',  # 件号：XXX
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        part_numbers.extend(matches)
    
    return list(set(part_numbers))[:5]  # 限制最多 5 个

def extract_prices(text):
    """从文本中提取价格信息"""
    prices = []
    
    # 价格模式
    patterns = [
        r'USD\s*[\$]?([\d,]+\.?\d*)',
        r'\$([\d,]+\.?\d*)',
        r'EUR\s*[€]?([\d,]+\.?\d*)',
        r'€([\d,]+\.?\d*)',
        r'单价 [::\s]*[\$€¥]?([\d,]+\.?\d*)',
        r'价格 [::\s]*[\$€¥]?([\d,]+\.?\d*)',
        r'quote[:\s]*[\$€¥]?([\d,]+\.?\d*)',
        r'price[:\s]*[\$€¥]?([\d,]+\.?\d*)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            price_str = match.replace(',', '')
            try:
                prices.append(float(price_str))
            except:
                pass
    
    return prices

def extract_condition(text):
    """从文本中提取条件"""
    conditions = ['SV', 'NS', 'NE', 'AR', 'OH', 'FN', 'AS', 'SV', 'NS', 'NE']
    
    text_upper = text.upper()
    for cond in conditions:
        if cond in text_upper:
            return cond
    
    return ''

def is_quote_email(subject, body):
    """判断是否为报价邮件"""
    text = (subject + ' ' + body).lower()
    
    # 检查是否包含报价相关关键词
    quote_count = sum(1 for keyword in QUOTE_KEYWORDS if keyword.lower() in text)
    
    return quote_count >= 2

def fetch_emails(days=30):
    """获取指定天数内的邮件"""
    print(f"Trying to connect to email: sale@aeroedgeglobal.com")
    
    mail = None
    config = None
    
    # 尝试多个配置
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
        print(f"Email connected successfully")
        
        # 计算日期范围 - 从 2026-03-16 开始
        since_date = datetime(2026, 3, 16)
        since_str = since_date.strftime('%d-%b-%Y')
        
        print(f"Date range: {since_str} to now")
        
        # 搜索邮件
        status, messages = mail.search(None, f'(SINCE "{since_str}")')
        
        if status != 'OK':
            print("Email search failed")
            return []
        
        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} emails")
        
        quotes = []
        processed = 0
        
        for msg_id in email_ids:
            try:
                status, msg_data = mail.fetch(msg_id, '(RFC822)')
                if status != 'OK':
                    continue
                
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # 提取邮件信息
                subject = decode_mime_words(msg.get('Subject', ''))
                from_addr = decode_mime_words(msg.get('From', ''))
                date_str = msg.get('Date', '')
                
                # 提取正文
                body = extract_email_body(msg)
                
                # 判断是否为报价邮件
                if is_quote_email(subject, body):
                    part_numbers = extract_part_numbers(body)
                    prices = extract_prices(body)
                    condition = extract_condition(body)
                    
                    quote_info = {
                        'Date': date_str,
                        'From': from_addr,
                        'Subject': subject,
                        'PartNumbers': '; '.join(part_numbers) if part_numbers else '',
                        'Prices': '; '.join([f"${p:.2f}" for p in prices]) if prices else '',
                        'Condition': condition,
                        'Body_Summary': body[:500].replace('\n', ' ').replace('\r', ''),
                    }
                    
                    quotes.append(quote_info)
                    print(f"  Quote email: {subject[:50]}...")
                
                processed += 1
                if processed % 10 == 0:
                    print(f"  Processed {processed}/{len(email_ids)} emails...")
                
            except Exception as e:
                print(f"  Error processing email: {e}")
                continue
        
        mail.close()
        mail.logout()
        
        return quotes
        
    except Exception as e:
        print(f"Email error: {e}")
        try:
            mail.close()
            mail.logout()
        except:
            pass
        return []

def save_to_csv(quotes, output_file):
    """保存报价信息到 CSV"""
    if not quotes:
        print("No quote data to save")
        return
    
    fieldnames = ['Date', 'From', 'Subject', 'PartNumbers', 'Prices', 'Condition', 'Body_Summary']
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(quotes)
    
    print(f"\nSaved {len(quotes)} quotes to: {output_file}")

def main():
    print("="*60)
    print("Email Quote Extractor")
    print("="*60)
    
    # 获取邮件
    quotes = fetch_emails(days=30)
    
    # 保存到 CSV
    save_to_csv(quotes, OUTPUT_FILE)
    
    # 汇总统计
    if quotes:
        print("\n" + "="*60)
        print("Quote Summary Statistics")
        print("="*60)
        print(f"Total quote emails: {len(quotes)}")
        
        # 按供应商统计
        suppliers = {}
        for q in quotes:
            supplier = q['From'].split('<')[0].strip().strip('"')
            suppliers[supplier] = suppliers.get(supplier, 0) + 1
        
        print("\nSupplier distribution:")
        for supplier, count in sorted(suppliers.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {supplier}: {count} emails")
        
        # 价格统计
        all_prices = []
        for q in quotes:
            if q['Prices']:
                for p in q['Prices'].split(';'):
                    try:
                        price = float(p.replace('$', '').replace(',', ''))
                        all_prices.append(price)
                    except:
                        pass
        
        if all_prices:
            print(f"\nPrice range:")
            print(f"  - Min: ${min(all_prices):.2f}")
            print(f"  - Max: ${max(all_prices):.2f}")
            print(f"  - Avg: ${sum(all_prices)/len(all_prices):.2f}")
    
    print("\n" + "="*60)
    print("Processing complete")
    print("="*60)

if __name__ == '__main__':
    main()
