#!/usr/bin/env python3
import imaplib
import ssl

IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
USERNAME = "jianghaide@aeroedgeglobal.com"
PASSWORD = "arv9KztNY" + chr(36) + "JWaHx3"

print("Connecting...")
ssl_context = ssl.create_default_context()
mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ssl_context)

print("Logging in...")
mail.login(USERNAME, PASSWORD)

print("Selecting INBOX...")
mail.select("INBOX")

print("Searching ALL...")
status, messages = mail.search(None, "ALL")

print(f"Status: {status}")
print(f"Messages: {len(messages[0].split()) if messages[0] else 0}")

mail.close()
mail.logout()
print("Done!")
