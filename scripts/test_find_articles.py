from cdp_client import CDPClient
import json

c = CDPClient(port=9222)
t = c.find_linkedin_feed()
c.connect(t['id'])

# 测试不同的选择器
selectors = [
    'article',
    'div.update-v2',
    'div.feed-update',
    'div.ember-view',
    '[data-id="update"]',
    'div.svelte-ct-element',
    'div.update',
    'div.shared-update',
    'div.jobs-update'
]

print("Testing selectors:\n")
for sel in selectors:
    js = f"document.querySelectorAll('{sel}').length"
    r = c.evaluate(js)
    count = r.get('result', {}).get('result', {}).get('value', 0)
    print(f"  {sel}: {count}")

# 获取所有 top-level divs with significant content
print("\n\nChecking divs with text content...")
js = """
(function() {
    var divs = document.querySelectorAll('div');
    var results = [];
    for (var i = 0; i < divs.length; i++) {
        var text = divs[i].innerText;
        if (text && text.length > 200) {
            results.push({
                class: divs[i].className.substring(0, 100),
                id: divs[i].id,
                textLen: text.length
            });
        }
    }
    return results.slice(0, 20);
})()
"""
r = c.evaluate(js)
divs = r.get('result', {}).get('result', {}).get('value', [])
print(f"Found {len(divs)} divs with content:")
for div in divs[:10]:
    print(f"  - {div.get('class', 'N/A')[:50]} (id={div.get('id', 'N/A')}, text={div.get('textLen', 0)})")

c.disconnect()
