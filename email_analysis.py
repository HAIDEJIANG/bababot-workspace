#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收件箱邮件分析脚本
分析 2026-01-01 至今的所有邮件
"""

import imaplib
import email
from email.header import decode_header
from datetime import datetime
import csv
import re
from collections import Counter

# IMAP 配置
IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
USERNAME = "jianghaide@aeroedgeglobal.com"

# 从配置文件读取密码（避免 shell 变量注入问题）
with open("C:/Users/Haide/.openclaw/workspace/email_config.txt", "r", encoding="utf-8") as f:
    PASSWORD = f.read().strip()

# 业务分类关键词
BUSINESS_KEYWORDS = {
    "航材交易": ["part", "component", "航材", "零件", "部件", "PN", "P/N", "material", "supply", "采购", "销售", "quote", "quotation", "RFQ", "price", "库存"],
    "发动机相关": ["engine", "发动机", "CFM56", "V2500", "PW", "GE", "Rolls-Royce", "motor", "turbine", "blade", "EGT", "LLP"],
    "起落架相关": ["landing gear", "起落架", "gear", "MLG", "NLG", "strut", "actuator", "wheel", "brake", "tire"],
    "MRO 服务": ["MRO", "maintenance", "repair", "overhaul", "服务", "维修", "保养", "大修", "service", "inspection", "check"],
}

def decode_mime_words(s):
    """解码 MIME 编码的字符串"""
    if not s:
        return ""
    decoded = ""
    for part, encoding in decode_header(s):
        if isinstance(part, bytes):
            try:
                decoded += part.decode(encoding or 'utf-8', errors='ignore')
            except:
                decoded += part.decode('utf-8', errors='ignore')
        else:
            decoded += part
    return decoded

def classify_business(subject, body):
    """根据主题和正文分类业务类型"""
    text = (subject + " " + body).lower()
    
    scores = {}
    for category, keywords in BUSINESS_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        scores[category] = score
    
    if max(scores.values()) == 0:
        return "其他"
    
    return max(scores, key=scores.get)

def get_email_body(msg):
    """提取邮件正文"""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition") or "")
            
            if content_type == "text/plain" and "attachment" not in content_disposition:
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

def parse_date(date_str):
    """解析邮件日期"""
    try:
        # 尝试多种日期格式
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue
        
        # 如果都失败，尝试从 Date 头提取
        match = re.search(r'(\d{1,2})\s+(\w{3})\s+(\d{4})\s+(\d{2}):(\d{2}):(\d{2})', date_str)
        if match:
            day, mon, year, hour, minute, sec = match.groups()
            month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
            month = month_map.get(mon, 1)
            return datetime(int(year), month, int(day), int(hour), int(minute), int(sec))
        
        return datetime.now()
    except:
        return datetime.now()

def main():
    print("正在连接 IMAP 服务器...")
    
    # 连接服务器
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(USERNAME, PASSWORD)
    mail.select("INBOX")
    
    print("正在搜索 2026-01-01 至今的邮件...")
    
    # 搜索 2026-01-01 之后的邮件
    since_date = "01-Jan-2026"
    status, messages = mail.search(None, f'(SINCE "{since_date}")')
    
    if status != "OK":
        print("搜索失败")
        return
    
    email_ids = messages[0].split()
    total_emails = len(email_ids)
    print(f"找到 {total_emails} 封邮件")
    
    emails_data = []
    sender_counter = Counter()
    category_counter = Counter({
        "航材交易": 0,
        "发动机相关": 0,
        "起落架相关": 0,
        "MRO 服务": 0,
        "其他": 0
    })
    
    for i, email_id in enumerate(email_ids, 1):
        try:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # 提取发件人
                    from_header = decode_mime_words(msg.get("From", ""))
                    from_email_match = re.search(r'<([^>]+)>', from_header)
                    from_email = from_email_match.group(1) if from_email_match else from_header
                    
                    # 提取主题
                    subject = decode_mime_words(msg.get("Subject", ""))
                    
                    # 提取日期
                    date_header = msg.get("Date", "")
                    email_date = parse_date(date_header)
                    
                    # 检查是否已读
                    status, flags = mail.fetch(email_id, "(FLAGS)")
                    is_read = b'\\Seen' in flags[0]
                    
                    # 提取正文
                    body = get_email_body(msg)
                    body_summary = body[:200].replace('\n', ' ').strip() if body else ""
                    
                    # 业务分类
                    category = classify_business(subject, body)
                    category_counter[category] += 1
                    
                    # 统计发件人
                    sender_counter[from_email] += 1
                    
                    emails_data.append({
                        "#": i,
                        "发件人": from_header,
                        "主题": subject,
                        "发件时间": email_date.strftime("%Y-%m-%d %H:%M"),
                        "业务分类": category,
                        "摘要": body_summary,
                        "是否已读": "已读" if is_read else "未读"
                    })
                    
                    if i % 50 == 0:
                        print(f"已处理 {i}/{total_emails} 封邮件")
        
        except Exception as e:
            print(f"处理邮件 {i} 时出错：{e}")
            continue
    
    print("\n分析完成！")
    
    # 生成 Markdown 报告
    md_report = f"""## 收件箱邮件汇总（2026-01-01 至今）

### 邮件清单
| # | 发件人 | 主题 | 发件时间 | 业务分类 | 摘要 |
|---|--------|------|----------|----------|------|
"""
    
    for email_info in emails_data:
        md_report += f"| {email_info['#']} | {email_info['发件人'][:30]}... | {email_info['主题'][:30]}... | {email_info['发件时间']} | {email_info['业务分类']} | {email_info['摘要'][:50]}... |\n"
    
    md_report += f"""
### 按业务分类统计
- 航材交易：{category_counter['航材交易']} 封
- 发动机相关：{category_counter['发动机相关']} 封
- 起落架相关：{category_counter['起落架相关']} 封
- MRO 服务：{category_counter['MRO 服务']} 封
- 其他：{category_counter['其他']} 封

### 重点客户/供应商（出现频率 Top 10）
"""
    
    top_10_senders = sender_counter.most_common(10)
    for i, (sender, count) in enumerate(top_10_senders, 1):
        md_report += f"{i}. {sender} - {count} 封\n"
    
    # 保存 Markdown 报告
    with open("C:/Users/Haide/Desktop/邮箱收件箱汇总_2026-01-01_至今.md", "w", encoding="utf-8") as f:
        f.write(md_report)
    
    # 保存 CSV 文件
    with open("C:/Users/Haide/Desktop/邮箱收件箱汇总_2026-01-01_至今.csv", "w", encoding="utf-8-sig", newline="") as f:
        if emails_data:
            writer = csv.DictWriter(f, fieldnames=["#", "发件人", "主题", "发件时间", "业务分类", "摘要", "是否已读"])
            writer.writeheader()
            writer.writerows(emails_data)
    
    print(f"\n报告已保存:")
    print(f"  - Markdown: C:/Users/Haide/Desktop/邮箱收件箱汇总_2026-01-01_至今.md")
    print(f"  - CSV: C:/Users/Haide/Desktop/邮箱收件箱汇总_2026-01-01_至今.csv")
    print(f"\n总计：{total_emails} 封邮件")
    print(f"\n业务分类统计:")
    for cat, count in category_counter.items():
        print(f"  - {cat}: {count} 封")
    
    # 关闭连接
    mail.close()
    mail.logout()

if __name__ == "__main__":
    main()
