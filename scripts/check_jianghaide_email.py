#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查 jianghaide 邮箱中的 DOMAS 邮件
"""

import imaplib
import email
from email.header import decode_header
import base64

# 邮箱配置 - jianghaide
IMAP_HOST = "imaphz.qiye.163.com"
IMAP_PORT = 993
IMAP_USER = "jianghaide@aeroedgeglobal.com"
# 密码使用 base64 编码避免 shell 解析问题
IMAP_PASS = base64.b64decode('YXJ2OUt6dE5ZJEpXYUh4Mw==').decode()

TARGET_EMAIL = "domas@blueskytechnics.com"

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

print(f"连接到 IMAP 服务器 (jianghaide@aeroedgeglobal.com)...")
mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
mail.login(IMAP_USER, IMAP_PASS)

# 列出所有邮箱
print("\n=== 邮箱文件夹列表 ===")
status, mailboxes = mail.list()
for mbox in mailboxes:
    print(mbox.decode())

# 检查 INBOX
print("\n=== 检查 INBOX ===")
mail.select('INBOX')
status, messages = mail.search(None, 'ALL')
if status == 'OK':
    msg_ids = messages[0].split()
    print(f"INBOX 总邮件数：{len(msg_ids)}")

# 搜索来自 DOMAS 的邮件
print(f"\n=== 搜索来自 {TARGET_EMAIL} 的邮件 ===")
for mbox_code in ['INBOX', '&XfJT0ZAB-', '&g0l6P3ux-']:
    try:
        mail.select(mbox_code)
        
        # 搜索发件人
        status, messages = mail.search(None, f'(FROM "{TARGET_EMAIL}")')
        if status == 'OK' and messages[0]:
            msg_ids = messages[0].split()
            print(f"\n{mbox_code}: 找到 {len(msg_ids)} 封来自 DOMAS 的邮件")
            
            # 显示前 20 封
            for msg_id in msg_ids[:20]:
                status, msg_data = mail.fetch(msg_id, '(RFC822)')
                if status == 'OK':
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    subject = decode_mime_words(msg.get('Subject', ''))
                    from_addr = decode_mime_words(msg.get('From', ''))
                    date = msg.get('Date', '')
                    print(f"  From: {from_addr}")
                    print(f"  Subject: {subject}")
                    print(f"  Date: {date}")
                    print()
        else:
            print(f"{mbox_code}: 没有找到来自 DOMAS 的邮件")
    except Exception as e:
        print(f"{mbox_code}: 错误 - {str(e)}")

# 搜索包含 blueskytechnics 的邮件
print(f"\n=== 搜索包含 blueskytechnics 的邮件 ===")
mail.select('INBOX')
for term in ['blueskytechnics', 'DOMAS', 'domas']:
    status, messages = mail.search(None, f'(BODY "{term}")')
    if status == 'OK' and messages[0]:
        msg_ids = messages[0].split()
        print(f"包含 '{term}': {len(msg_ids)} 封邮件")
        
        # 显示前 5 封
        for msg_id in msg_ids[:5]:
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            if status == 'OK':
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                subject = decode_mime_words(msg.get('Subject', ''))
                from_addr = decode_mime_words(msg.get('From', ''))
                print(f"  From: {from_addr} | Subject: {subject}")
    else:
        print(f"包含 '{term}': 0 封邮件")

mail.logout()
print("\n完成!")
