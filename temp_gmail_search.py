import urllib.request, os, json, base64, urllib.parse

MATON_API_KEY = os.environ.get("MATON_API_KEY", "")
if not MATON_API_KEY:
    print("MATON_API_KEY not found")
    exit(1)

# Search for RFQ email from Cynthia Zhang
query = "from:cynthia@haitegroup.com RFQ20260324-02"
req = urllib.request.Request(f'https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?q={urllib.parse.quote(query)}&maxResults=5')
req.add_header('Authorization', f'Bearer {MATON_API_KEY}')

try:
    response = json.load(urllib.request.urlopen(req))
    print(json.dumps(response, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
