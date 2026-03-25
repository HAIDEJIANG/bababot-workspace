import imaplib
import email
from email.header import decode_header
import base64
import json

# Gmail IMAP credentials
IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
IMAP_USER = "jianghaide@gmail.com"
IMAP_PASS = "Aa138222"

# Connect to Gmail IMAP
mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
mail.login(IMAP_USER, IMAP_PASS)

# Search for RFQ email from Cynthia Zhang
mail.select("inbox")

# Search for emails from cynthia@haitegroup.com with RFQ20260324-02
status, messages = mail.search(None, '(FROM "cynthia@haitegroup.com" SUBJECT "RFQ20260324-02")')

if status != "OK":
    print("No messages found!")
    exit()

message_ids = messages[0].split()
print(f"Found {len(message_ids)} message(s)")

for msg_id in message_ids[-1:]:  # Get the most recent one
    status, msg_data = mail.fetch(msg_id, "(RFC822)")
    if status != "OK":
        print("Failed to fetch message")
        continue
    
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)
    
    # Print headers
    print("\n=== EMAIL HEADERS ===")
    print(f"From: {msg.get('From')}")
    print(f"To: {msg.get('To')}")
    print(f"Subject: {msg.get('Subject')}")
    print(f"Date: {msg.get('Date')}")
    
    # Get email body
    print("\n=== EMAIL BODY ===")
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    body = part.get_payload(decode=True).decode(charset, errors='ignore')
                    print(body)
                except Exception as e:
                    print(f"Error decoding part: {e}")
            elif content_type == "text/html":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    html_body = part.get_payload(decode=True).decode(charset, errors='ignore')
                    print(f"\n[HTML content available, {len(html_body)} chars]")
                except Exception as e:
                    print(f"Error decoding HTML: {e}")
    else:
        try:
            charset = msg.get_content_charset() or 'utf-8'
            body = msg.get_payload(decode=True).decode(charset, errors='ignore')
            print(body)
        except Exception as e:
            print(f"Error decoding message: {e}")

mail.close()
mail.logout()
