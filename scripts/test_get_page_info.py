from cdp_client import CDPClient
import json

c = CDPClient(port=9222)
t = c.find_linkedin_feed()
c.connect(t['id'])

# 测试每个 evaluate
print("Testing document.title...")
r = c.evaluate("document.title")
print(f"  Result: {json.dumps(r, indent=2)}")
print(f"  Value: {r.get('result', {}).get('value', 'N/A')}")

print("\nTesting window.location.href...")
r = c.evaluate("window.location.href")
print(f"  Result: {json.dumps(r, indent=2)[:200]}")
print(f"  Value: {r.get('result', {}).get('value', 'N/A')}")

print("\nTesting document.body.innerText.length...")
r = c.evaluate("document.body.innerText.length")
print(f"  Result: {json.dumps(r, indent=2)}")
print(f"  Value: {r.get('result', {}).get('value', 0)}")

print("\nget_page_info:")
info = c.get_page_info()
print(f"  {info}")

c.disconnect()
