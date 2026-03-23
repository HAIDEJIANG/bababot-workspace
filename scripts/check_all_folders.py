#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查所有邮箱文件夹的邮件
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

# 邮箱文件夹映射
mailbox_names = [
    ('INBOX', '收件箱'),
    ('&g0l6P3ux-', '草稿箱'),
    ('&XfJT0ZAB-', '已发送'),
    ('&XfJSIJZk-', '已删除'),
    ('&V4NXPpCuTvY-', '垃圾邮件'),
    ('&Xn9USpCuTvY-', '其他')
]

print("\n=== 检查所有文件夹 ===")
for mbox_code, mbox_name in mailbox_names:
    try:
        mail.select(mbox_code)
        status, messages = mail.search(None, 'ALL')
        if status == 'OK':
            count = len(messages[0].split()) if messages[0] else 0
            print(f"{mbox_name} ({mbox_code}): {count} 封邮件")
            
            # 搜索 domas/bluesky
            for term in ['domas', 'bluesky', 'DOMAS', 'BLUESKY', 'domas@blueskytechnics.com']:
                status, msgs = mail.search(None, f'(BODY "{term}")')
                if status == 'OK' and msgs[0]:
                    match_count = len(msgs[0].split())
                    if match_count > 0:
                        print(f"  ✓ 包含 '{term}': {match_count} 封")
    except Exception as e:
        print(f"{mbox_name}: 错误 - {str(e)}")

# 检查已发送文件夹
print("\n=== 检查已发送文件夹 ===")
mail.select('&XfJT0ZAB-')  # 已发送
status, messages = mail.search(None, '(TO "domas@blueskytechnics.com")')
if status == 'OK' and messages[0]:
    msg_ids = messages[0].split()
    print(f"找到 {len(msg_ids)} 封发送给 DOMAS 的邮件")
    
    # 显示前 10 封
    for msg_id in msg_ids[:10]:
        status, msg_data = mail.fetch(msg_id, '(RFC822)')
        if status == 'OK':
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            subject = decode_mime_words(msg.get('Subject', ''))
            to_addr = decode_mime_words(msg.get('To', ''))
            date = msg.get('Date', '')
            print(f"  To: {to_addr}")
            print(f"  Subject: {subject}")
            print(f"  Date: {date}")
            print()
else:
    print("没有找到发送给 DOMAS 的邮件")

mail.logout()
print("\n完成!")
