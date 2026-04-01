from cdp_client import CDPClient
import json

c = CDPClient(port=9222)
t = c.find_linkedin_feed()
print('Found:', t['title'] if t else None)

if c.connect(t['id']):
    print("\nSending evaluate...")
    r = c.evaluate('document.title')
    print(f"Full response:\n{json.dumps(r, indent=2)}")
    
    c.disconnect()
