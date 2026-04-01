from cdp_client import CDPClient
import time

c = CDPClient(port=9222)
t = c.find_linkedin_feed()
c.connect(t['id'])

print("Before activation:")
info = c.get_page_info()
print(f"  BodyText: {info.get('bodyTextLen', 0)} chars")

# 尝试激活页面
print("\nActivating page...")
c._send_session("Page.bringToFront")
time.sleep(2)

print("\nAfter bringToFront:")
info = c.get_page_info()
print(f"  BodyText: {info.get('bodyTextLen', 0)} chars")

# 尝试导航到同一页面（强制刷新）
print("\nNavigating to same URL...")
c._send_session("Page.navigate", {"url": "https://www.linkedin.com/feed/"})
time.sleep(5)

print("\nAfter navigate:")
info = c.get_page_info()
print(f"  BodyText: {info.get('bodyTextLen', 0)} chars")

# 提取帖子
print("\nExtracting posts...")
posts = c.extract_posts()
print(f"Posts found: {len(posts)}")

c.disconnect()
