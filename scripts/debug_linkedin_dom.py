#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LinkedIn DOM 结构调试脚本"""

from cdp_client import CDPClient
import json

client = CDPClient(port=9222)
tabs = client.get_browser_tabs()
li_tab = client.find_linkedin_feed()

if not li_tab:
    print("未找到 LinkedIn Feed")
    exit()

print(f"找到 LinkedIn: {li_tab['title']}")
client.connect(li_tab['id'])

# 检查页面中所有包含 data- 属性的元素
print("\n=== 检查 data- 属性 ===")
js = """
(function() {
    var results = [];
    var all = document.querySelectorAll('*[data-id]');
    for (var i = 0; i < Math.min(all.length, 50); i++) {
        var el = all[i];
        results.push({
            tag: el.tagName,
            dataId: el.getAttribute('data-id'),
            text: (el.innerText || '').substring(0, 100)
        });
    }
    return results;
})()
"""
result = client._send_session("Runtime.evaluate", {"expression": js, "returnByValue": True})
data_ids = result.get('result', {}).get('value', [])
print(f"找到 {len(data_ids)} 个包含 data-id 的元素:")
for item in data_ids[:10]:
    print(f"  <{item.get('tag')}> data-id={item.get('dataId', 'N/A')[:50]}")
    print(f"    文本：{item.get('text', 'N/A')[:50]}")

# 检查 aria-label
print("\n=== 检查 aria-label ===")
js = """
(function() {
    var results = [];
    var all = document.querySelectorAll('*[aria-label]');
    for (var i = 0; i < Math.min(all.length, 30); i++) {
        var el = all[i];
        var label = el.getAttribute('aria-label');
        if (label && (label.includes('post') || label.includes('share') || label.includes('activity'))) {
            results.push({
                tag: el.tagName,
                ariaLabel: label,
                text: (el.innerText || '').substring(0, 100)
            });
        }
    }
    return results;
})()
"""
result = client._send_session("Runtime.evaluate", {"expression": js, "returnByValue": True})
aria_items = result.get('result', {}).get('value', [])
print(f"找到 {len(aria_items)} 个可能相关的 aria-label:")
for item in aria_items[:10]:
    print(f"  <{item.get('tag')}> aria-label={item.get('ariaLabel', 'N/A')[:80]}")

# 检查所有 article 标签的完整结构
print("\n=== 检查 article 标签结构 ===")
js = """
(function() {
    var articles = document.querySelectorAll('article');
    var results = [];
    for (var i = 0; i < Math.min(articles.length, 5); i++) {
        var el = articles[i];
        var attrs = {};
        for (var j = 0; j < el.attributes.length; j++) {
            var attr = el.attributes[j];
            if (attr.name.startsWith('data-') || attr.name.startsWith('aria-')) {
                attrs[attr.name] = attr.value;
            }
        }
        results.push({
            tag: 'article',
            attributes: attrs,
            textLen: (el.innerText || '').length,
            firstLine: (el.innerText || '').split('\\n')[0].substring(0, 100)
        });
    }
    return results;
})()
"""
result = client._send_session("Runtime.evaluate", {"expression": js, "returnByValue": True})
articles = result.get('result', {}).get('value', [])
print(f"找到 {len(articles)} 个 article 标签:")
for art in articles:
    print(f"  属性：{json.dumps(art.get('attributes', {}), indent=4)}")
    print(f"  文本长度：{art.get('textLen')}，第一行：{art.get('firstLine')}")

client.disconnect()
print("\n调试完成")
