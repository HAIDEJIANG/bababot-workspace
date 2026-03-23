#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMAP 邮箱诊断脚本 v2 - 改进编码处理
"""

import imaplib
import email
from email.header import decode_header
import ssl
import os

IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
USERNAME = "jianghaide@aeroedgeglobal.com"
AUTH_CODE = os.environ.get('IMAP_AUTH_CODE', 'arv9KztNY$JWaHx3')

def decode_mime_words(header):
    if not header:
        return ""
    decoded = ""
    for part, encoding in decode_header(header):
        if isinstance(part, bytes):
            try:
                decoded += part.decode(encoding or 'utf-8', errors='ignore')
            except:
                decoded += part.decode('latin-1', errors='ignore')
        else:
            decoded += str(part)
    return decoded

def main():
    print("=" * 60)
    print("IMAP 邮箱诊断 v2")
    print("=" * 60)
    
    ssl_context = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ssl_context)
    mail.login(USERNAME, AUTH_CODE)
    
    # 列出所有文件夹
    status, folders = mail.list()
    print(f"\n可用文件夹:")
    for f in folders:
        # 解码文件夹名称
        try:
            decoded = f.decode('utf-8')
        except:
            decoded = str(f)
        print(f"  {decoded}")
    
    # 检查 INBOX
    mail.select('INBOX')
    
    # 获取邮箱状态
    status, count = mail.status('INBOX', '(MESSAGES RECENT UNSEEN)')
    print(f"\nINBOX: {count[0].decode('utf-8', errors='ignore')}")
    
    # 搜索所有邮件
    status, messages = mail.search(None, 'ALL')
    if status == 'OK':
        all_emails = messages[0].split()
        print(f"\nINBOX 总邮件数：{len(all_emails)}")
        
        # 查看最近 30 封邮件
        print(f"\n最近 30 封邮件预览:")
        print("-" * 90)
        
        for i, email_id in enumerate(reversed(all_emails[-30:])):
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822 HEADER.FIELDS.FROM SUBJECT DATE)')
                if status != 'OK':
                    continue
                
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                from_addr = decode_mime_words(msg.get('From', ''))
                subject = decode_mime_words(msg.get('Subject', ''))
                date = msg.get('Date', '')
                
                try:
                    parsed_date = email.utils.parsedate_to_datetime(date)
                    date_str = parsed_date.strftime('%Y-%m-%d %H:%M')
                except:
                    date_str = date[:20] if date else 'Unknown'
                
                # 清理输出
                from_clean = from_addr.replace('\n', ' ')[:50]
                subject_clean = subject.replace('\n', ' ')[:60]
                
                print(f"{i+1:2}. [{date_str}]")
                print(f"    From: {from_clean}")
                print(f"    Subj: {subject_clean}")
                print()
                
            except Exception as e:
                print(f"  邮件 {email_id} 处理失败：{e}")
                continue
    
    # 搜索目标客户
    print("\n" + "=" * 60)
    print("搜索目标客户相关邮件:")
    print("=" * 60)
    
    customers = {
        'Gabriel Leclair': ['Gabriel', 'Leclair'],
        'Abraham Siria': ['Abraham', 'Siria'],
        'Domas @ Blue Sky': ['Domas', 'Blue Sky', 'BlueSky']
    }
    
    for customer, terms in customers.items():
        print(f"\n{customer}:")
        total_found = 0
        
        for term in terms:
            try:
                # FROM 搜索
                status, messages = mail.search(None, f'(FROM "{term}")')
                if status == 'OK' and messages[0]:
                    count = len(messages[0].split())
                    if count > 0:
                        print(f"  FROM '{term}': {count} 封")
                        total_found += count
                
                # SUBJECT 搜索
                status, messages = mail.search(None, f'(SUBJECT "{term}")')
                if status == 'OK' and messages[0]:
                    count = len(messages[0].split())
                    if count > 0:
                        print(f"  SUBJECT '{term}': {count} 封")
                
                # BODY 搜索
                status, messages = mail.search(None, f'(BODY "{term}")')
                if status == 'OK' and messages[0]:
                    count = len(messages[0].split())
                    if count > 0:
                        print(f"  BODY '{term}': {count} 封")
                
            except Exception as e:
                print(f"  搜索 '{term}' 错误：{e}")
        
        if total_found == 0:
            print(f"  (未找到 FROM 匹配)")
    
    # 检查已发送文件夹
    print("\n" + "=" * 60)
    print("检查已发送文件夹:")
    print("=" * 60)
    
    try:
        # 尝试不同的已发送文件夹名称
        sent_folders = ['"&XfJT0ZAB-"', 'Sent', 'Sent Items', '已发送']
        
        for folder in sent_folders:
            try:
                status, messages = mail.select(folder)
                if status == 'OK':
                    status, count = mail.status(folder, '(MESSAGES)')
                    print(f"  {folder}: {count[0].decode('utf-8', errors='ignore')}")
                    
                    # 查看几封邮件
                    status, messages = mail.search(None, 'ALL')
                    if status == 'OK' and messages[0]:
                        emails = messages[0].split()[-5:]  # 最后 5 封
                        for email_id in emails:
                            status, msg_data = mail.fetch(email_id, '(HEADER.FIELDS.FROM SUBJECT DATE)')
                            if status == 'OK':
                                msg = email.message_from_bytes(msg_data[0][1])
                                subject = decode_mime_words(msg.get('Subject', ''))
                                date = msg.get('Date', '')
                                try:
                                    parsed_date = email.utils.parsedate_to_datetime(date)
                                    date_str = parsed_date.strftime('%Y-%m-%d')
                                except:
                                    date_str = ''
                                print(f"    [{date_str}] {subject[:50]}")
                    
                    mail.close(folder)
                    break
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"检查已发送失败：{e}")
    
    mail.logout()
    print("\n诊断完成!")

if __name__ == "__main__":
    main()
