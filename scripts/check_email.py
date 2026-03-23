#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查邮箱内容和文件夹
"""

import imaplib
import email
from email.header import decode_header

# 邮箱配置
IMAP_HOST = "imaphz.qiye.163.com"
IMAP_PORT = 993
IMAP_USER = "sale@aeroedgeglobal.com"
IMAP_PASS = "A4D8%b3x6FHAH45d"

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

print("连接到 IMAP 服务器...")
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
    
    # 显示最近 10 封邮件的发件人和主题
    print("\n最近 10 封邮件:")
    for msg_id in msg_ids[-10:]:
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

# 搜索所有包含 domas 或 bluesky 的邮件
print("\n=== 全局搜索 DOMAS/BLUESKY ===")
mail.select('INBOX')
for search_term in ['domas', 'bluesky', 'DOMAS', 'BLUESKY']:
    status, messages = mail.search(None, '(BODY "' + search_term + '")')
    if status == 'OK' and messages[0]:
        count = len(messages[0].split())
        print(f"包含 '{search_term}': {count} 封邮件")
    else:
        print(f"包含 '{search_term}': 0 封邮件")

# 搜索所有发件人
print("\n=== 搜索所有发件人包含 @blueskytechnics.com ===")
status, messages = mail.search(None, '(FROM "@blueskytechnics.com")')
if status == 'OK' and messages[0]:
    count = len(messages[0].split())
    print(f"找到 {count} 封邮件")
    
    # 显示前 5 封
    msg_ids = messages[0].split()[:5]
    for msg_id in msg_ids:
        status, msg_data = mail.fetch(msg_id, '(RFC822)')
        if status == 'OK':
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            subject = decode_mime_words(msg.get('Subject', ''))
            from_addr = decode_mime_words(msg.get('From', ''))
            print(f"  From: {from_addr}")
            print(f"  Subject: {subject}")
            print()
else:
    print("没有找到匹配的邮件")

mail.logout()
print("\n完成!")
