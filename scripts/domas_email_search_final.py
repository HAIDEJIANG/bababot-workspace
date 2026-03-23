#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOMAS 邮件搜索 - 最终执行脚本
搜索所有邮箱，提取器材需求，更新 Excel 和报告
"""

import imaplib
import email
from email.header import decode_header
import pandas as pd
from datetime import datetime
import re
import base64

# 邮箱配置
EMAIL_ACCOUNTS = [
    {
        'name': 'sale',
        'email': 'sale@aeroedgeglobal.com',
        'host': 'imaphz.qiye.163.com',
        'port': 993,
        'pass': base64.b64decode('QTREOCViM3g2RkhBSDQ1ZA==').decode()
    },
    {
        'name': 'jianghaide',
        'email': 'jianghaide@aeroedgeglobal.com',
        'host': 'imaphz.qiye.163.com',
        'port': 993,
        'pass': base64.b64decode('YXJ2OUt6dE5ZJEpXYUh4Mw==').decode()
    }
]

TARGET_EMAIL = "domas@blueskytechnics.com"
EXCEL_PATH = "C:/Users/Haide/Desktop/OPENCLAW/DOMAS_Requirements_Summary.xlsx"
REPORT_PATH = "C:/Users/Haide/.openclaw/workspace/DOMAS_Email_Search_Report.md"

def decode_mime_words(s):
    if not s:
        return ""
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

def extract_email_content(msg):
    content = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition") or "")
            if "attachment" in content_disposition.lower():
                continue
            if content_type == "text/plain":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    if payload:
                        content += payload.decode(charset, errors='ignore') + "\n"
                except:
                    pass
    else:
        try:
            charset = msg.get_content_charset() or 'utf-8'
            payload = msg.get_payload(decode=True)
            if payload:
                content = payload.decode(charset, errors='ignore')
        except:
            pass
    return content

def extract_part_info(content, subject):
    parts_info = []
    text = f"{subject}\n{content}"
    
    part_patterns = [
        r'P/N[:\s]*([A-Z0-9\-]+)',
        r'Part Number[:\s]*([A-Z0-9\-]+)',
        r'件号[:\s]*([A-Z0-9\-]+)',
        r'PART NO[:\s]*([A-Z0-9\-]+)',
        r'PN[:\s]*([A-Z0-9\-]+)',
        r'[A-Z]{2,}[0-9]{3,}[\-][0-9]+',
        r'[0-9]{6,}[\-][0-9]+',
    ]
    
    qty_patterns = [
        r'QTY[:\s]*(\d+)',
        r'Quantity[:\s]*(\d+)',
        r'数量[:\s]*(\d+)',
        r'(\d+)\s+PCS',
        r'(\d+)\s+EA',
    ]
    
    part_numbers = []
    for pattern in part_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        part_numbers.extend(matches)
    
    quantities = []
    for pattern in qty_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        quantities.extend(matches)
    
    if part_numbers:
        for i, pn in enumerate(part_numbers[:5]):
            qty = quantities[i] if i < len(quantities) else (quantities[0] if quantities else "1")
            parts_info.append({
                'part_number': pn.strip(),
                'quantity': str(qty).strip(),
                'description': subject[:100]
            })
    
    return parts_info

def search_account(account_config):
    results = []
    stats = {'from': 0, 'to': 0, 'body': 0}
    
    print(f"\n连接邮箱：{account_config['email']}")
    try:
        mail = imaplib.IMAP4_SSL(account_config['host'], account_config['port'])
        mail.login(account_config['email'], account_config['pass'])
        
        # 获取所有邮箱
        status, mailboxes = mail.list()
        
        for mbox in mailboxes:
            mbox_name = mbox.decode().split(' "')[-1].strip('"')
            try:
                mail.select(mbox_name)
                
                # 策略 1: 发件人匹配
                status, messages = mail.search(None, f'(FROM "{TARGET_EMAIL}")')
                if status == 'OK' and messages[0]:
                    msg_ids = messages[0].split()
                    stats['from'] += len(msg_ids)
                    
                    for msg_id in msg_ids[:50]:
                        status, msg_data = mail.fetch(msg_id, '(RFC822)')
                        if status == 'OK':
                            raw_email = msg_data[0][1]
                            msg = email.message_from_bytes(raw_email)
                            subject = decode_mime_words(msg.get('Subject', ''))
                            from_addr = decode_mime_words(msg.get('From', ''))
                            content = extract_email_content(msg)
                            parts_info = extract_part_info(content, subject)
                            
                            for part in parts_info:
                                results.append({
                                    '发件人': from_addr,
                                    '收件日期': datetime.now().strftime('%Y-%m-%d'),
                                    '邮件主题': subject[:50],
                                    '邮件内容摘要': content[:100].replace('\n', ' '),
                                    '件号/Part Number': part['part_number'],
                                    '数量': part['quantity'],
                                    '描述': part['description'],
                                    '优先级': '中',
                                    '备注': f'{account_config["name"]}-{mbox_name}'
                                })
                
                # 策略 2: 正文包含关键词
                if mbox_name == 'INBOX':
                    for term in ['blueskytechnics', 'DOMAS']:
                        status, messages = mail.search(None, f'(BODY "{term}")')
                        if status == 'OK' and messages[0]:
                            msg_ids = messages[0].split()
                            stats['body'] += len(msg_ids)
            except:
                continue
        
        mail.logout()
    except Exception as e:
        print(f"  错误：{str(e)}")
    
    return results, stats

def main():
    print("=" * 70)
    print("DOMAS 邮件搜索 - 器材需求提取")
    print("=" * 70)
    print(f"目标邮箱：{TARGET_EMAIL}")
    print(f"搜索时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    total_stats = {'from': 0, 'to': 0, 'body': 0}
    
    for account in EMAIL_ACCOUNTS:
        results, stats = search_account(account)
        all_results.extend(results)
        for k in total_stats:
            total_stats[k] += stats[k]
    
    # 更新 Excel
    print(f"\n更新 Excel 文件：{EXCEL_PATH}")
    try:
        existing_df = pd.read_excel(EXCEL_PATH)
        print(f"  现有记录：{len(existing_df)} 条")
    except:
        existing_df = pd.DataFrame(columns=[
            '发件人', '收件日期', '邮件主题', '邮件内容摘要',
            '件号/Part Number', '数量', '描述', '优先级', '备注'
        ])
    
    if all_results:
        new_df = pd.DataFrame(all_results)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['件号/Part Number', '发件人'], keep='last')
        combined_df.to_excel(EXCEL_PATH, index=False)
        print(f"  更新后总计：{len(combined_df)} 条")
        total_records = len(combined_df)
    else:
        print("  无新数据")
        total_records = len(existing_df)
    
    # 生成报告
    report = f"""# DOMAS 邮件搜索报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**目标邮箱**: {TARGET_EMAIL}
**搜索账号**: 
- sale@aeroedgeglobal.com
- jianghaide@aeroedgeglobal.com

## 搜索结果

| 搜索类型 | 匹配数量 |
|---------|---------|
| 发件人匹配 (FROM) | {total_stats['from']} |
| 正文内容匹配 | {total_stats['body']} |
| **新增需求记录** | {len(all_results)} |
| **Excel 总记录** | {total_records} |

## 搜索说明

### 搜索策略
1. **发件人精确匹配**: FROM:"{TARGET_EMAIL}"
2. **正文关键词**: BODY:"blueskytechnics" 或 BODY:"DOMAS"
3. **搜索范围**: INBOX 及所有文件夹

### 当前状态
{'✅ 找到 ' + str(len(all_results)) + ' 条器材需求记录' if all_results else '⚠️ 暂未找到来自 DOMAS 的邮件'}

## 后续建议

1. **定期检查**: 建议每日执行搜索，及时捕获新需求
2. **扩展关键词**: 可根据实际业务添加更多关键词
3. **人工补充**: 如有已知 DOMAS 邮件，可手动添加到 Excel

## 文件位置

- **Excel 汇总表**: `{EXCEL_PATH}`
- **本报告**: `{REPORT_PATH}`

---
*报告由 OpenClaw DOMAS 邮件搜索脚本自动生成*
"""
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存：{REPORT_PATH}")
    print("\n" + "=" * 70)
    print("任务完成!")
    print(f"  搜索邮箱数：{len(EMAIL_ACCOUNTS)}")
    print(f"  找到需求记录：{len(all_results)} 条")
    print(f"  Excel 总记录：{total_records} 条")
    print("=" * 70)

if __name__ == "__main__":
    main()
