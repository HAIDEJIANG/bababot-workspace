#!/usr/bin/env python3
"""
从 sale@aeroedgeglobal.com 邮箱提取 RFQ 报价信息
使用 IMAP 协议读取邮件内容并汇总
"""

import imaplib
import email
from email.header import decode_header
import re
import os
import json
from datetime import datetime

# 邮箱配置
IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
EMAIL_ADDR = "sale@aeroedgeglobal.com"
EMAIL_PASS = "Aa138222"

# 报价提取结果
QUOTES = []

def decode_mime_header(header_val):
    """解码 MIME 邮件头"""
    if not header_val:
        return ""
    parts = decode_header(header_val)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(charset or 'utf-8', errors='replace'))
            except:
                result.append(part.decode('utf-8', errors='replace'))
        else:
            result.append(str(part))
    return " ".join(result)

def get_email_body(msg):
    """提取邮件正文"""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disp = str(part.get("Content-Disposition", ""))
            if content_type == "text/plain" and "attachment" not in content_disp:
                try:
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    body += payload.decode(charset, errors='replace')
                except:
                    pass
            elif content_type == "text/html" and "attachment" not in content_disp and not body:
                try:
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    html = payload.decode(charset, errors='replace')
                    body += re.sub(r'<[^>]+>', ' ', html)
                    body = re.sub(r'\s+', ' ', body).strip()
                except:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or 'utf-8'
            body = payload.decode(charset, errors='replace')
        except:
            pass
    return body

def extract_quote_info(body, subject, from_addr):
    """从邮件正文中提取报价信息"""
    info = {
        "供应商": from_addr.split('<')[0].strip() if '<' in from_addr else from_addr,
        "联系人": "",
        "邮箱": "",
        "件号": "",
        "金额_USD": "",
        "数量": "",
        "状态": "",
        "交期": "",
        "发货地": "",
        "备注": subject[:100],
        "邮件时间": "",
    }
    
    # 提取 PN 号
    pn_patterns = [
        r'\b\d{6,}-\d{2,}\b',
        r'\b[A-Z]{2,}\d{4,}-\d+\b',
        r'\b\d{4,}[A-Z]\d+-\d+\b',
        r'\b\d{3,}-\d{3,}-\d+\b',
    ]
    for p in pn_patterns:
        matches = re.findall(p, body)
        if matches:
            info["件号"] = matches[0]
            break
    
    # 提取价格
    prices = re.findall(r'\$[\d,]+(?:\.\d{2})?', body)
    if prices:
        info["金额_USD"] = prices[0]
    
    # 提取条件
    cond_matches = re.findall(r'\b(FN|NE|NS|OH|SV|RP|AR|TESTED|INSPECTED|NEW|OVERHAULED|SERVICEABLE)\b', body, re.IGNORECASE)
    if cond_matches:
        info["状态"] = cond_matches[0].upper()
    
    # 提取交期
    lt_matches = re.findall(r'\b(\d+)\s*(day|week|month|business day|working day|BD|WD)\b', body, re.IGNORECASE)
    if lt_matches:
        info["交期"] = " ".join(lt_matches[0])
    
    # 提取 STOCK
    if re.search(r'\bSTOCK\b', body, re.IGNORECASE):
        info["交期"] = "STOCK"
    
    # 提取数量
    qty_matches = re.findall(r'\b(\d+)\s*(EA|PCS|pieces|units)\b', body, re.IGNORECASE)
    if qty_matches:
        info["数量"] = qty_matches[0][0] + " " + qty_matches[0][1]
    
    return info

def main():
    print("=" * 60)
    print("RFQ20260324-02 报价提取")
    print("邮箱：sale@aeroedgeglobal.com")
    print("=" * 60)
    
    # 连接 IMAP
    print("\n[1] 连接邮箱...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ADDR, EMAIL_PASS)
        print("  ✅ 登录成功")
    except Exception as e:
        print("  ❌ 登录失败：{}".format(str(e)))
        print("  可能原因：163 企业邮箱需要验证码或授权码")
        return
    
    # 选择收件箱
    mail.select("INBOX")
    
    # 搜索今天的邮件
    since_date = "25-Mar-2026"
    print("\n[2] 搜索 {} 以来的邮件...".format(since_date))
    
    status, messages = mail.search(None, f'(SINCE {since_date})')
    if status != "OK":
        print("  ❌ 搜索失败")
        mail.logout()
        return
    
    msg_ids = messages[0].split()
    print("  📬 找到 {} 封邮件".format(len(msg_ids)))
    
    # 逐封读取
    print("\n[3] 提取报价信息...")
    rfq_keywords = ["RFQ", "quote", "quotation", "price", "offer", "pricing", "AEROEDGE", "Part Number"]
    
    for i, msg_id in enumerate(msg_ids):
        try:
            status, data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue
            
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            subject = decode_mime_header(msg.get("Subject", ""))
            from_addr = decode_mime_header(msg.get("From", ""))
            date_str = decode_mime_header(msg.get("Date", ""))
            
            # 判断是否 RFQ 相关
            combined_text = (subject + " " + from_addr).lower()
            is_rfq = any(kw.lower() in combined_text for kw in rfq_keywords)
            
            # 排除 StockMarket 自动确认
            if "stockmarket" in from_addr.lower() and "confirmation" in subject.lower():
                continue
            
            if is_rfq:
                body = get_email_body(msg)[:2000]
                quote_info = extract_quote_info(body, subject, from_addr)
                quote_info["邮件时间"] = date_str
                QUOTES.append(quote_info)
                
                print("  📧 #{}: {} | {}".format(len(QUOTES), from_addr[:40], subject[:60]))
        
        except Exception as e:
            print("  ⚠️ 邮件 {} 读取失败：{}".format(msg_id.decode(), str(e)[:50]))
            continue
    
    mail.logout()
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📊 结果汇总")
    print("=" * 60)
    print("总计：{} 封报价邮件".format(len(QUOTES)))
    
    if QUOTES:
        # 保存 JSON
        output_dir = os.path.dirname(os.path.dirname(__file__))
        json_path = os.path.join(output_dir, "rfq_quotes_imap.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(QUOTES, f, indent=2, ensure_ascii=False)
        print("\n详细数据已保存：{}".format(json_path))
        
        # 打印表格
        print("\n" + "=" * 100)
        print("{:<4} {:<30} {:<15} {:<12} {:<8} {:<10} {:<20}".format(
            "序号", "供应商", "PN", "金额", "状态", "交期", "联系人"))
        print("=" * 100)
        
        for i, q in enumerate(QUOTES, 1):
            print("{:<4} {:<30} {:<15} {:<12} {:<8} {:<10} {:<20}".format(
                i, q["供应商"][:30], q["件号"], q["金额_USD"], q["状态"], q["交期"], q["联系人"]))
        
        print("=" * 100)
        
        # 生成 CSV
        csv_path = os.path.join(output_dir, "rfq_quotes_summary_imap.csv")
        with open(csv_path, "w", encoding="utf-8-sig") as f:
            headers = ["序号", "供应商", "联系人", "邮箱", "件号", "金额_USD", "数量", "状态", "交期", "发货地", "备注", "邮件时间"]
            f.write(",".join(headers) + "\n")
            for i, q in enumerate(QUOTES, 1):
                row = [str(i), q["供应商"], q["联系人"], q["邮箱"], q["件号"], 
                       q["金额_USD"], q["数量"], q["状态"], q["交期"], q["发货地"], 
                       q["备注"], q["邮件时间"]]
                f.write(",".join(['"{}"'.format(str(x).replace('"', '""')) for x in row]) + "\n")
        
        print("CSV 表格已保存：{}".format(csv_path))

if __name__ == "__main__":
    main()
