#!/usr/bin/env python3
"""
检查 sale@aeroedgeglobal.com 邮箱中与 RFQ20260324-02 相关的报价回复
通过 IMAP 连接 163 企业邮箱
"""

import imaplib
import email
from email.header import decode_header
import sys
import json
import os
import re
import base64
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 邮箱配置
IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
EMAIL_ADDR = "sale@aeroedgeglobal.com"
EMAIL_PASS = "Aa138222"

# 搜索配置
RFQ_REF = "RFQ20260324-02"
SEARCH_DAYS = 3  # 搜索最近3天的邮件
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..")

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
                    # 简单去 HTML 标签
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
    return body[:5000]  # 限制长度

def get_attachments(msg):
    """提取附件信息"""
    attachments = []
    if msg.is_multipart():
        for part in msg.walk():
            content_disp = str(part.get("Content-Disposition", ""))
            if "attachment" in content_disp:
                filename = part.get_filename()
                if filename:
                    filename = decode_mime_header(filename)
                    size = len(part.get_payload(decode=True) or b"")
                    attachments.append({
                        "filename": filename,
                        "size_bytes": size,
                        "content_type": part.get_content_type()
                    })
    return attachments

def extract_quote_info(body, subject):
    """从邮件正文中提取报价信息"""
    info = {
        "pn_numbers": [],
        "prices": [],
        "conditions": [],
        "lead_times": [],
        "quantities": [],
    }
    
    # PN 号提取
    pn_patterns = [
        r'\b\d{6,}-\d{2,}\b',
        r'\b[A-Z]{2,}\d{4,}-\d+\b',
        r'\b\d{4,}[A-Z]\d+-\d+\b',
    ]
    for p in pn_patterns:
        info["pn_numbers"].extend(re.findall(p, body))
    info["pn_numbers"] = list(set(info["pn_numbers"]))
    
    # 价格提取
    prices = re.findall(r'\$[\d,]+(?:\.\d{2})?', body)
    prices += re.findall(r'USD\s*[\d,]+(?:\.\d{2})?', body, re.IGNORECASE)
    info["prices"] = list(set(prices))
    
    # 条件提取
    cond_matches = re.findall(r'\b(FN|NE|NS|OH|SV|RP|AR|TESTED|INSPECTED|NEW|OVERHAULED|SERVICEABLE)\b', body, re.IGNORECASE)
    info["conditions"] = list(set([c.upper() for c in cond_matches]))
    
    # 交期提取
    lt_matches = re.findall(r'\b(\d+)\s*(day|week|month|business day|working day|BD|WD)\b', body, re.IGNORECASE)
    info["lead_times"] = [f"{n} {u}" for n, u in lt_matches]
    
    return info

def main():
    print("=" * 60)
    print("检查 sale@aeroedgeglobal.com 邮箱报价")
    print("搜索范围: 最近 %d 天" % SEARCH_DAYS)
    print("关联 RFQ: %s" % RFQ_REF)
    print("=" * 60)
    
    # 连接 IMAP
    print("\n[1] 连接邮箱...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ADDR, EMAIL_PASS)
        print("  ✅ 登录成功")
    except Exception as e:
        print("  ❌ 登录失败: %s" % str(e))
        return
    
    # 选择收件箱
    mail.select("INBOX")
    
    # 搜索最近几天的邮件
    since_date = (datetime.now() - timedelta(days=SEARCH_DAYS)).strftime("%d-%b-%Y")
    print("\n[2] 搜索自 %s 以来的邮件..." % since_date)
    
    # 搜索所有最近的邮件
    status, messages = mail.search(None, f'(SINCE {since_date})')
    if status != "OK":
        print("  ❌ 搜索失败")
        mail.logout()
        return
    
    msg_ids = messages[0].split()
    print("  📬 找到 %d 封邮件" % len(msg_ids))
    
    # 逐封读取
    quotes = []
    rfq_related = []
    
    print("\n[3] 分析邮件内容...")
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
            to_addr = decode_mime_header(msg.get("To", ""))
            
            body = get_email_body(msg)
            attachments = get_attachments(msg)
            
            # 判断是否与 RFQ 相关 (检查主题和正文)
            is_rfq_related = False
            rfq_keywords = [RFQ_REF, "RFQ", "quote", "quotation", "price", "offer", 
                           "pricing", "bid", "proposal", "availability",
                           "stockmarket", "StockMarket"]
            
            combined_text = (subject + " " + body).lower()
            for kw in rfq_keywords:
                if kw.lower() in combined_text:
                    is_rfq_related = True
                    break
            
            # 也检查附件名
            for att in attachments:
                if any(kw.lower() in att["filename"].lower() for kw in ["quote", "rfq", "price", "offer"]):
                    is_rfq_related = True
                    break
            
            if is_rfq_related:
                quote_info = extract_quote_info(body, subject)
                
                entry = {
                    "msg_id": msg_id.decode(),
                    "from": from_addr,
                    "to": to_addr,
                    "subject": subject,
                    "date": date_str,
                    "body_preview": body[:1000],
                    "attachments": attachments,
                    "extracted_info": quote_info,
                }
                rfq_related.append(entry)
                
                att_info = f" + {len(attachments)} 附件" if attachments else ""
                print("  📧 [%d] %s | %s%s" % (len(rfq_related), from_addr[:50], subject[:60], att_info))
        
        except Exception as e:
            print("  ⚠️ 邮件 %s 读取失败: %s" % (msg_id.decode(), str(e)[:50]))
            continue
    
    mail.logout()
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📊 结果汇总")
    print("=" * 60)
    print("总邮件数: %d" % len(msg_ids))
    print("RFQ 相关: %d" % len(rfq_related))
    
    if rfq_related:
        # 保存 JSON
        output_path = os.path.join(OUTPUT_DIR, "sale_email_quotes.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(rfq_related, f, indent=2, ensure_ascii=False)
        print("\n详细数据已保存: %s" % output_path)
        
        # 打印详细信息
        print("\n" + "-" * 60)
        for i, entry in enumerate(rfq_related, 1):
            print("\n📧 邮件 #%d" % i)
            print("  发件人: %s" % entry["from"])
            print("  主题: %s" % entry["subject"])
            print("  日期: %s" % entry["date"])
            if entry["attachments"]:
                for att in entry["attachments"]:
                    print("  📎 附件: %s (%s, %d bytes)" % (att["filename"], att["content_type"], att["size_bytes"]))
            if entry["extracted_info"]["prices"]:
                print("  💰 价格: %s" % ", ".join(entry["extracted_info"]["prices"]))
            if entry["extracted_info"]["pn_numbers"]:
                print("  🔧 PN: %s" % ", ".join(entry["extracted_info"]["pn_numbers"]))
            if entry["extracted_info"]["conditions"]:
                print("  📋 条件: %s" % ", ".join(entry["extracted_info"]["conditions"]))
            if entry["extracted_info"]["lead_times"]:
                print("  🚚 交期: %s" % ", ".join(entry["extracted_info"]["lead_times"]))
            print("  正文预览: %s..." % entry["body_preview"][:200])
    else:
        print("\n⚠️ 未找到与 RFQ 相关的报价邮件")
        print("可能原因:")
        print("  - RFQ 刚发送不久，供应商尚未回复")
        print("  - 报价可能在其他邮箱 (jianghaide@gmail.com)")
        print("  - 需要等待更长时间")

if __name__ == "__main__":
    main()
