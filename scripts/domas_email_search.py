#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOMAS 邮件搜索脚本
搜索来自 domas@blueskytechnics.com 的邮件，提取器材需求信息
"""

import imaplib
import email
from email.header import decode_header
import pandas as pd
from datetime import datetime
import re
import os

# 邮箱配置
IMAP_HOST = "imaphz.qiye.163.com"
IMAP_PORT = 993
IMAP_USER = "sale@aeroedgeglobal.com"
IMAP_PASS = "A4D8%b3x6FHAH45d"

# 目标邮箱
TARGET_EMAIL = "domas@blueskytechnics.com"

# 输出文件
EXCEL_PATH = "C:/Users/Haide/Desktop/OPENCLAW/DOMAS_Requirements_Summary.xlsx"
REPORT_PATH = "C:/Users/Haide/.openclaw/workspace/DOMAS_Email_Search_Report.md"

def decode_mime_words(s):
    """解码 MIME 编码的字符串"""
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
    """提取邮件正文内容"""
    content = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition") or "")
            
            # 跳过附件
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
            elif content_type == "text/html":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    if payload:
                        # 简单去除 HTML 标签
                        html_content = payload.decode(charset, errors='ignore')
                        content += re.sub(r'<[^>]+>', '', html_content) + "\n"
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
    """从邮件内容中提取器材需求信息"""
    parts_info = []
    
    # 合并主题和内容进行搜索
    text = f"{subject}\n{content}"
    
    # 常见的件号模式
    part_patterns = [
        r'P/N[:\s]*([A-Z0-9\-]+)',
        r'Part Number[:\s]*([A-Z0-9\-]+)',
        r'件号[:\s]*([A-Z0-9\-]+)',
        r'PART NO[:\s]*([A-Z0-9\-]+)',
        r'PN[:\s]*([A-Z0-9\-]+)',
        r'[A-Z]{2,}[0-9]{3,}[\-][0-9]+',  # 如 ABC123-456
        r'[0-9]{6,}[\-][0-9]+',  # 如 123456-789
    ]
    
    # 数量模式
    qty_patterns = [
        r'QTY[:\s]*(\d+)',
        r'Quantity[:\s]*(\d+)',
        r'数量[:\s]*(\d+)',
        r'(\d+)\s+PCS',
        r'(\d+)\s+EA',
        r'(\d+)\s+个',
        r'(\d+)\s+件',
    ]
    
    # 描述模式
    desc_patterns = [
        r'Description[:\s]*([^\n]+)',
        r'描述[:\s]*([^\n]+)',
        r'Requirement[:\s]*([^\n]+)',
        r'需求[:\s]*([^\n]+)',
    ]
    
    # 提取件号
    part_numbers = []
    for pattern in part_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        part_numbers.extend(matches)
    
    # 提取数量
    quantities = []
    for pattern in qty_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        quantities.extend(matches)
    
    # 提取描述
    descriptions = []
    for pattern in desc_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        descriptions.extend(matches)
    
    # 如果找到件号，创建记录
    if part_numbers:
        for i, pn in enumerate(part_numbers[:5]):  # 限制每封邮件最多 5 个件号
            qty = quantities[i] if i < len(quantities) else (quantities[0] if quantities else "1")
            desc = descriptions[i] if i < len(descriptions) else (descriptions[0] if descriptions else "")
            
            parts_info.append({
                'part_number': pn.strip(),
                'quantity': str(qty).strip(),
                'description': desc.strip()[:100] if desc else ""
            })
    else:
        # 如果没有找到明确的件号，但邮件内容包含需求信息
        if len(text.strip()) > 50:
            parts_info.append({
                'part_number': '需人工识别',
                'quantity': '-',
                'description': text.strip()[:200]
            })
    
    return parts_info

def search_emails():
    """搜索并处理邮件"""
    print(f"连接到 IMAP 服务器：{IMAP_HOST}")
    
    # 连接 IMAP
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(IMAP_USER, IMAP_PASS)
    
    # 获取所有邮箱
    status, mailboxes = mail.list()
    print(f"找到 {len(mailboxes)} 个邮箱文件夹")
    
    all_results = []
    search_stats = {
        'total_searched': 0,
        'from_target': 0,
        'to_target': 0,
        'content_match': 0
    }
    
    # 搜索策略 1: 发件人匹配
    print(f"\n搜索策略 1: 发件人包含 {TARGET_EMAIL}")
    for mailbox in mailboxes:
        try:
            mbox_name = mailbox.decode().split(' "')[-1].strip('"')
            mail.select(mbox_name)
            
            # 搜索发件人
            status, messages = mail.search(None, f'(FROM "{TARGET_EMAIL}")')
            if status == 'OK' and messages[0]:
                msg_ids = messages[0].split()
                search_stats['from_target'] += len(msg_ids)
                
                for msg_id in msg_ids[:50]:  # 限制每个文件夹最多处理 50 封
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        
                        subject = decode_mime_words(msg.get('Subject', ''))
                        from_addr = decode_mime_words(msg.get('From', ''))
                        date_str = msg.get('Date', '')
                        
                        content = extract_email_content(msg)
                        parts_info = extract_part_info(content, subject)
                        
                        if parts_info:
                            for part in parts_info:
                                all_results.append({
                                    '发件人': from_addr,
                                    '收件日期': datetime.now().strftime('%Y-%m-%d'),
                                    '邮件主题': subject[:50],
                                    '邮件内容摘要': content[:100].replace('\n', ' '),
                                    '件号/Part Number': part['part_number'],
                                    '数量': part['quantity'],
                                    '描述': part['description'],
                                    '优先级': '中',
                                    '备注': f'来自 {mbox_name}'
                                })
                        search_stats['total_searched'] += 1
        except Exception as e:
            print(f"  邮箱 {mbox_name} 处理失败：{str(e)}")
            continue
    
    # 搜索策略 2: 收件人包含目标邮箱
    print(f"\n搜索策略 2: 收件人包含 {TARGET_EMAIL}")
    for mailbox in mailboxes:
        try:
            mbox_name = mailbox.decode().split(' "')[-1].strip('"')
            mail.select(mbox_name)
            
            status, messages = mail.search(None, f'(TO "{TARGET_EMAIL}")')
            if status == 'OK' and messages[0]:
                msg_ids = messages[0].split()
                search_stats['to_target'] += len(msg_ids)
                
                for msg_id in msg_ids[:20]:
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        
                        subject = decode_mime_words(msg.get('Subject', ''))
                        from_addr = decode_mime_words(msg.get('From', ''))
                        
                        # 只处理来自 DOMAS 相关域名的邮件
                        if 'blueskytechnics' in from_addr.lower() or 'domas' in from_addr.lower():
                            content = extract_email_content(msg)
                            parts_info = extract_part_info(content, subject)
                            
                            if parts_info:
                                for part in parts_info:
                                    all_results.append({
                                        '发件人': from_addr,
                                        '收件日期': datetime.now().strftime('%Y-%m-%d'),
                                        '邮件主题': subject[:50],
                                        '邮件内容摘要': content[:100].replace('\n', ' '),
                                        '件号/Part Number': part['part_number'],
                                        '数量': part['quantity'],
                                        '描述': part['description'],
                                        '优先级': '中',
                                        '备注': f'收件人匹配 - {mbox_name}'
                                    })
        except Exception as e:
            continue
    
    # 搜索策略 3: 正文包含关键词
    print(f"\n搜索策略 3: 正文包含 blueskytechnics 或 DOMAS")
    for mailbox in ['INBOX', '收件箱']:
        try:
            mail.select(mailbox)
            
            # 搜索正文包含关键词
            status, messages = mail.search(None, '(BODY "blueskytechnics")')
            if status == 'OK' and messages[0]:
                msg_ids = messages[0].split()
                search_stats['content_match'] += len(msg_ids)
                
                for msg_id in msg_ids[:20]:
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        
                        subject = decode_mime_words(msg.get('Subject', ''))
                        from_addr = decode_mime_words(msg.get('From', ''))
                        
                        # 只处理来自 DOMAS 相关域名的邮件
                        if 'blueskytechnics' in from_addr.lower() or 'domas' in from_addr.lower():
                            content = extract_email_content(msg)
                            parts_info = extract_part_info(content, subject)
                            
                            if parts_info:
                                for part in parts_info:
                                    all_results.append({
                                        '发件人': from_addr,
                                        '收件日期': datetime.now().strftime('%Y-%m-%d'),
                                        '邮件主题': subject[:50],
                                        '邮件内容摘要': content[:100].replace('\n', ' '),
                                        '件号/Part Number': part['part_number'],
                                        '数量': part['quantity'],
                                        '描述': part['description'],
                                        '优先级': '中',
                                        '备注': f'正文匹配 - {mailbox}'
                                    })
        except Exception as e:
            continue
    
    mail.logout()
    
    return all_results, search_stats

def update_excel(results):
    """更新 Excel 文件"""
    print(f"\n更新 Excel 文件：{EXCEL_PATH}")
    
    # 读取现有数据
    try:
        existing_df = pd.read_excel(EXCEL_PATH)
        print(f"  现有记录数：{len(existing_df)}")
    except:
        existing_df = pd.DataFrame(columns=[
            '发件人', '收件日期', '邮件主题', '邮件内容摘要',
            '件号/Part Number', '数量', '描述', '优先级', '备注'
        ])
        print("  创建新文件")
    
    # 添加新数据
    if results:
        new_df = pd.DataFrame(results)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # 去重（基于件号和发件人）
        combined_df = combined_df.drop_duplicates(subset=['件号/Part Number', '发件人'], keep='last')
        
        # 保存
        combined_df.to_excel(EXCEL_PATH, index=False)
        print(f"  更新后总记录数：{len(combined_df)}")
        return len(combined_df)
    else:
        print("  没有新数据")
        return len(existing_df)

def generate_report(results, stats, total_records):
    """生成 Markdown 报告"""
    report = f"""# DOMAS 邮件搜索报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**目标邮箱**: {TARGET_EMAIL}
**搜索邮箱**: {IMAP_USER}

## 搜索统计

| 搜索策略 | 匹配邮件数 |
|---------|-----------|
| 发件人匹配 (FROM) | {stats['from_target']} |
| 收件人匹配 (TO) | {stats['to_target']} |
| 正文内容匹配 | {stats['content_match']} |
| **总计搜索** | {stats['total_searched']} |

## 提取结果

- **新增需求记录**: {len(results)} 条
- **Excel 总记录数**: {total_records} 条

## 新增需求详情

"""
    
    if results:
        for i, item in enumerate(results[:20], 1):  # 只显示前 20 条
            report += f"""
### {i}. {item['件号/Part Number']}
- **发件人**: {item['发件人']}
- **邮件主题**: {item['邮件主题']}
- **数量**: {item['数量']}
- **描述**: {item['描述']}
- **备注**: {item['备注']}

---
"""
    else:
        report += "\n*本次搜索未找到新的器材需求信息*\n"
    
    report += f"""
## 文件位置

- **Excel 汇总表**: `{EXCEL_PATH}`
- **本报告**: `{REPORT_PATH}`

## 下次搜索建议

1. 定期检查新邮件（建议每日）
2. 对于"需人工识别"的记录，建议手动补充件号信息
3. 可根据业务优先级调整筛选条件

---
*报告由 OpenClaw DOMAS 邮件搜索脚本自动生成*
"""
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告已保存：{REPORT_PATH}")

def main():
    print("=" * 60)
    print("DOMAS 邮件搜索 - 器材需求提取")
    print("=" * 60)
    
    # 搜索邮件
    results, stats = search_emails()
    
    # 更新 Excel
    total_records = update_excel(results)
    
    # 生成报告
    generate_report(results, stats, total_records)
    
    print("\n" + "=" * 60)
    print("任务完成!")
    print(f"  - 找到 {len(results)} 条器材需求记录")
    print(f"  - Excel 总记录：{total_records} 条")
    print("=" * 60)

if __name__ == "__main__":
    main()
