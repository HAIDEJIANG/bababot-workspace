import urllib.request, os, json

# 搜索海特高新的邮件
req = urllib.request.Request('https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?q=from:cynthia@haitegroup.com&maxResults=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
response = json.load(urllib.request.urlopen(req))
print(json.dumps(response, indent=2))