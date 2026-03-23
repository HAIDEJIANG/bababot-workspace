#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMAP 邮箱探索脚本
查看文件夹结构和邮件内容
"""

import imaplib
import email
from email.header import decode_header
import ssl

# IMAP 配置
IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
USERNAME = "jianghaide@aeroedgeglobal.com"
PASSWORD = "arv9KztNY$JWaHx3"

def decode_mime_words(s):
    """解码 MIME 编码的字符串"""
    if not s:
        return ""
    decoded = []
    for word, encoding in decode_header(s):
        if isinstance(word, bytes):
            try:
                decoded.append(word.decode(encoding or 'utf-8', errors='ignore'))
            except:
                decoded.append(word.decode('utf-8', errors='ignore'))
        else:
            decoded.append(word)
    return ''.join(decoded)

def connect_imap():
    """连接 IMAP 服务器"""
    print(f"正在连接 IMAP 服务器：{IMAP_SERVER}:{IMAP_PORT}")
    ssl_context = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ssl_context)
    print(f"正在登录：{USERNAME}")
    mail.login(USERNAME, PASSWORD)
    return mail

def list_folders(mail):
    """列出所有文件夹"""
    status, folders = mail.list()
    if status == "OK":
        print("\n=== 邮箱文件夹 ===")
        for folder in folders:
            print(f"  {folder.decode('utf-8')}")
    return folders

def check_folder(mail, folder_name, limit=20):
    """检查指定文件夹的邮件"""
    print(f"\n=== 检查文件夹：{folder_name} ===")
    
    status, messages = mail.select(folder_name)
    if status != "OK":
        print(f"  无法选择文件夹：{folder_name}")
        return
    
    status, email_ids = mail.search(None, "ALL")
    if status != "OK":
        print("  搜索失败")
        return
    
    email_list = email_ids[0].split()
    total = len(email_list)
    print(f"  总邮件数：{total}")
    
    if total == 0:
        return
    
    # 获取最近的邮件
    recent_ids = email_list[-limit:] if len(email_list) > limit else email_list
    
    print(f"\n  最近 {len(recent_ids)} 封邮件的发件人:")
    senders = {}
    
    for email_id in recent_ids:
        try:
            status, msg_data = mail.fetch(email_id, "(RFC822 BODY[HEADER.FIELDS (FROM SUBJECT DATE)])")
            if status == "OK":
                msg = email.message_from_bytes(msg_data[0][1])
                sender = decode_mime_words(msg.get("From", ""))
                subject = decode_mime_words(msg.get("Subject", ""))
                date = msg.get("Date", "")[:20]
                
                # 统计发件人
                senders[sender] = senders.get(sender, 0) + 1
                
                print(f"    [{date}] {sender[:60]}")
                print(f"           主题：{subject[:50]}")
        except Exception as e:
            print(f"    错误：{e}")
    
    print(f"\n  发件人统计 (前 10):")
    sorted_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)[:10]
    for sender, count in sorted_senders:
        print(f"    {count} 封 - {sender[:50]}")

def search_all_mail(mail, search_term):
    """在所有文件夹中搜索"""
    print(f"\n=== 全局搜索：{search_term} ===")
    
    status, folders = mail.list()
    if status != "OK":
        return
    
    total_found = 0
    
    for folder_item in folders:
        folder_name = folder_item.decode('utf-8').split('"')[-2] if '"' in folder_item.decode('utf-8') else folder_item.decode('utf-8').split()[-1]
        
        # 跳过特殊文件夹
        if '\\Trash' in folder_item.decode('utf-8') or '\\Spam' in folder_item.decode('utf-8'):
            continue
        
        try:
            mail.select(folder_name)
            
            # 尝试多种搜索
            for query in [f'FROM "{search_term}"', f'SUBJECT "{search_term}"', f'BODY "{search_term}"']:
                status, email_ids = mail.search(None, query)
                if status == "OK" and email_ids[0]:
                    count = len(email_ids[0].split())
                    if count > 0:
                        print(f"  {folder_name}: {query} -> {count} 封")
                        total_found += count
        except:
            pass
    
    print(f"  总计找到：{total_found} 封")

def main():
    """主函数"""
    print("="*60)
    print("IMAP 邮箱探索工具")
    print("="*60)
    
    mail = connect_imap()
    
    # 列出所有文件夹
    folders = list_folders(mail)
    
    # 检查常见文件夹
    common_folders = ["INBOX", "收件箱", "Sent", "已发送", "Drafts", "草稿箱", "Archive", "归档"]
    for folder in common_folders:
        check_folder(mail, folder)
    
    # 全局搜索 Blue Sky
    search_all_mail(mail, "Blue Sky")
    search_all_mail(mail, "Domas")
    
    mail.close()
    mail.logout()
    
    print("\n" + "="*60)
    print("探索完成!")
    print("="*60)

if __name__ == "__main__":
    main()
