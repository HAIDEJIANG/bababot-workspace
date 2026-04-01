from cdp_client import CDPClient
import time

c = CDPClient(port=9222)
t = c.find_linkedin_feed()
c.connect(t['id'])

print("Page info:", c.get_page_info())

# 滚动几次
print("\nScrolling...")
for i in range(5):
    c.scroll_page(800)
    time.sleep(2)
    info = c.get_page_info()
    print(f"After scroll {i+1}: BodyText={info.get('bodyTextLen', 0)} chars")

# 尝试查找所有有文本的元素
print("\n\nSearching for post containers...")
js = """
(function() {
    var results = [];
    // 尝试查找 LinkedIn 的帖子特征
    var articles = document.querySelectorAll('article, [role="article"], div[data-update-id], div.update-v2, div.feed-update');
    for (var i = 0; i < articles.length; i++) {
        var el = articles[i];
        results.push({
            tag: el.tagName,
            role: el.getAttribute('role'),
            textLen: el.innerText.length
        });
    }
    return results;
})()
"""
r = c.evaluate(js)
posts = r.get('result', {}).get('result', {}).get('value', [])
print(f"Found {len(posts)} potential posts")
for p in posts[:5]:
    print(f"  - {p}")

# 尝试获取所有可见文本
print("\n\nGetting body text...")
js = "document.body.innerText"
r = c.evaluate(js)
text = r.get('result', {}).get('result', {}).get('value', '')
print(f"Body text length: {len(text)}")
print(f"First 500 chars:\n{text[:500]}")

c.disconnect()
