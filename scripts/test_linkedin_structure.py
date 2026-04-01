from cdp_client import CDPClient
import json

c = CDPClient(port=9222)
t = c.find_linkedin_feed()
c.connect(t['id'])

# 获取页面 HTML 结构
print("Getting page structure...\n")
js = """
(function() {
    // 查找所有可能有帖子内容的容器
    var containers = [];
    var all = document.querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
        var el = all[i];
        var text = el.innerText;
        // 查找包含"Start a post"或类似 LinkedIn 特征的容器
        if (text && text.length > 500 && text.length < 5000) {
            var tag = el.tagName;
            var role = el.getAttribute('role') || '';
            var aria = el.getAttribute('aria-label') || '';
            var className = el.className || '';
            if (typeof className === 'string') {
                className = className.substring(0, 100);
            }
            containers.push({
                tag: tag,
                role: role,
                aria: aria.substring(0, 100),
                class: className,
                textLen: text.length,
                firstLine: text.split('\\n')[0].substring(0, 100)
            });
        }
    }
    return containers.slice(0, 30);
})()
"""

r = c.evaluate(js)
containers = r.get('result', {}).get('result', {}).get('value', [])
print(f"Found {len(containers)} potential containers:\n")
for i, c in enumerate(containers[:10]):
    print(f"[{i}] <{c.get('tag')}> role={c.get('role','N/A')[:30]} aria={c.get('aria','N/A')[:30]}")
    print(f"    class={c.get('class','N/A')[:60]}")
    print(f"    textLen={c.get('textLen')}, firstLine: {c.get('firstLine','N/A')[:50]}")
    print()

c.disconnect()
