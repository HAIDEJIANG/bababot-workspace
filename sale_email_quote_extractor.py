# -*- coding: utf-8 -*-
"""
销售邮箱报价信息提取
登录 sale@aeroedgeglobal.com，提取 2026-03-01 以来的航材供应商报价邮件
"""

import imaplib
import email
from email.header import decode_header
import sys
import re
from datetime import datetime
import csv
from config import (
    IMAP_CONFIG, 
    DEFAULT_OUTPUT_DIR, 
    SUPPLIER_QUOTE_FILE,
    OUTPUT_ENCODING
)

sys.stdout.reconfigure(encoding='utf-8')

# IMAP 配置（从 config 模块导入）
IMAP_SERVER = IMAP_CONFIG["server"]
IMAP_PORT = IMAP_CONFIG["port"]
USERNAME = IMAP_CONFIG["username"]
# 注意：密码应从安全存储获取，此处为示例
AUTH_CODE = "A4D8%b3x6FHAH45d"

# 输出文件路径（使用配置的默认路径）
OUTPUT_FILE = SUPPLIER_QUOTE_FILE

def decode_mime_words(s):
    if not s:
        return ""
    decoded = decode_header(s)
    return ''.join(
        part.decode(encoding or 'utf-8', errors='ignore') if isinstance(part, bytes) else part
        for part, encoding in decoded
    )

def parse_price(text):
    """从文本中提取价格信息"""
    if not text:
        return None
    # 价格模式：$XXX, XXX.XX 或 USD XXX 或 EUR XXX
    patterns = [
        r'\$[\d,]+\.?\d*',
        r'USD\s*[\d,]+\.?\d*',
        r'EUR\s*[\d,]+\.?\d*',
        r'price[:\s]*\$?[\d,]+\.?\d*',
        r'unit\s*price[:\s]*\$?[\d,]+\.?\d*',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None

def parse_condition(text):
    """从文本中提取条件"""
    if not text:
        return ""
    conditions = ['SV', 'NS', 'NE', 'OH', 'AR', 'FN', 'AS', 'DIST']
    text_upper = text.upper()
    for cond in conditions:
        if re.search(rf'\b{cond}\b', text_upper):
            return cond
    return ""

def extract_quote_info(body, subject):
    """从邮件中提取报价信息"""
    quotes = []
    lines = body.split('\n')
    
    current_pn = None
    current_desc = None
    current_price = None
    current_condition = None
    current_qty = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 零件号模式
        pn_match = re.match(r'^([A-Z0-9\-]+)\s*(?:[:\s]|$)', line, re.IGNORECASE)
        if pn_match and len(pn_match.group(1)) >= 5:
            # 保存之前的记录
            if current_pn:
                quotes.append({
                    'PN': current_pn,
                    'Desc': current_desc or '',
                    'Price': current_price or '',
                    'Condition': current_condition or '',
                    'Qty': current_qty or ''
                })
            
            current_pn = pn_match.group(1)
            current_desc = line.replace(current_pn, '').strip()
            current_price = None
            current_condition = None
            current_qty = None
        
        # 价格信息
        if current_pn and not current_price:
            price = parse_price(line)
            if price:
                current_price = price
        
        # 条件信息
        if current_pn and not current_condition:
            cond = parse_condition(line)
            if cond:
                current_condition = cond
        
        # 数量信息
        if current_pn and not current_qty:
            qty_match = re.search(r'(\d+)\s*(?:pcs?|units?|qty|quantity)', line, re.IGNORECASE)
            if qty_match:
                current_qty = qty_match.group(1)
    
    # 保存最后一个记录
    if current_pn:
        quotes.append({
            'PN': current_pn,
            'Desc': current_desc or '',
            'Price': current_price or '',
            'Condition': current_condition or '',
            'Qty': current_qty or ''
        })
    
    return quotes

print("=== 销售邮箱报价信息提取 ===")
print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"邮箱：{USERNAME}")
print(f"时间范围：2026-03-01 至今")

# 连接 IMAP 服务器
print("\n[1/4] 连接 IMAP 服务器...")
try:
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(USERNAME, AUTH_CODE)
    print("[OK] 登录成功")
except Exception as e:
    print(f"[ERROR] 登录失败：{e}")
    sys.exit(1)

# 选择收件箱
print("\n[2/4] 选择收件箱...")
mail.select("INBOX")

# 搜索 2026-03-01 以来的邮件
print("\n[3/4] 搜索 2026-03-01 以来的邮件...")
status, messages = mail.search(None, '(SINCE "01-Mar-2026")')

if status != "OK":
    print("[ERROR] 搜索失败")
    sys.exit(1)

email_ids = messages[0].split()
print(f"[OK] 找到 {len(email_ids)} 封邮件")

# 提取报价信息
print("\n[4/4] 提取报价信息...")
all_quotes = []
email_count = 0

# 关键词过滤（航材供应商相关）
keywords = ['quote', 'quotation', 'price', 'offer', 'rfq', 'PN', 'part number', 'aviation', 'aircraft']

for i, eid in enumerate(email_ids, 1):
    status, msg_data = mail.fetch(eid, "(RFC822)")
    if status != "OK":
        continue
    
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            
            subject = decode_mime_words(msg.get("Subject", ""))
            from_ = decode_mime_words(msg.get("From", ""))
            date_str = msg.get("Date", "")
            
            try:
                date_obj = email.utils.parsedate_to_datetime(date_str)
                formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
            except:
                formatted_date = date_str
            
            # 检查是否包含报价相关关键词
            subject_lower = subject.lower()
            if not any(kw in subject_lower for kw in keywords):
                continue
            
            # 提取正文
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get("Content-Disposition"))
                    if ctype == "text/plain" and "attachment" not in cdispo:
                        try:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            pass
                        break
            else:
                try:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    pass
            
            # 提取报价
            quotes = extract_quote_info(body, subject)
            
            if quotes:
                email_count += 1
                print(f"\n{'='*80}")
                print(f"邮件 {email_count}: {subject}")
                print(f"发件人：{from_}")
                print(f"日期：{formatted_date}")
                print(f"报价数量：{len(quotes)}")
                
                for q in quotes:
                    print(f"  {q['PN']}: {q['Desc'][:40]} | {q['Price']} | {q['Condition']}")
                    
                    all_quotes.append({
                        'Date': formatted_date,
                        'From': from_[:50],
                        'Subject': subject[:50],
                        'PartNumber': q['PN'],
                        'Description': q['Desc'],
                        'Price': q['Price'],
                        'Condition': q['Condition'],
                        'Qty': q['Qty'],
                        'Notes': ''
                    })

print(f"\n\n总计：{email_count} 封报价邮件，{len(all_quotes)} 条报价记录")

# 导出 CSV（使用配置路径）
print("\n导出到 CSV...")
output_file = SUPPLIER_QUOTE_FILE

if all_quotes:
    fieldnames = ['Date', 'From', 'Subject', 'PartNumber', 'Description', 'Price', 'Condition', 'Qty', 'Notes']
    with open(output_file, 'w', newline='', encoding=OUTPUT_ENCODING) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_quotes)
    
    print(f"[OK] 已导出到：{output_file}")
    
    # 统计信息
    print("\n=== 报价统计 ===")
    
    # 按供应商统计
    supplier_stats = {}
    for q in all_quotes:
        supplier = q['From'].split('<')[-1].split('>')[0] if '<' in q['From'] else q['From']
        supplier_stats[supplier] = supplier_stats.get(supplier, 0) + 1
    
    print("\n按供应商统计:")
    for supplier, count in sorted(supplier_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {supplier}: {count} 条")
    
    # 按条件统计
    cond_stats = {}
    for q in all_quotes:
        cond = q['Condition'] or 'N/A'
        cond_stats[cond] = cond_stats.get(cond, 0) + 1
    
    print("\n按条件统计:")
    for cond, count in sorted(cond_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cond}: {count} 条")
else:
    print("[WARN] 未找到报价记录")

mail.close()
mail.logout()

print(f"\n结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=== 任务完成 ===")
