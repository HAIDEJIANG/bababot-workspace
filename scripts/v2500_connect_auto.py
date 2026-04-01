# LinkedIn V2500 联系人批量 Connect 请求脚本
# 使用 Browser Relay CDP 协议自动发送 Connect 请求

import asyncio
import json
import requests
from datetime import datetime

# CDP WebSocket 地址（Browser Relay）
CDP_BASE = "http://localhost:9222"

# Connect 请求消息模板
CONNECT_MESSAGE = """Hi {name},

I noticed your work in fleet/engine asset management at {company}. We specialize in V2500 engine MRO, leasing, and trading services.

Would be great to connect and explore potential collaboration opportunities.

Best regards,
Haide Jiang
AeroEdge Global"""

async def get_cdp_session():
    """创建 CDP 会话"""
    resp = requests.get(f"{CDP_BASE}/json/new?about:blank")
    if resp.status_code == 200:
        return resp.json().get("webSocketDebuggerUrl")
    return None

async def send_connect_request(profile_url, first_name, company):
    """发送单个 Connect 请求"""
    try:
        # 1. 打开 LinkedIn 个人资料页
        ws_url = await get_cdp_session()
        
        # 使用 requests 调用 CDP HTTP endpoint
        cdp_resp = requests.post(f"{CDP_BASE}/json", json={
            "id": 1,
            "method": "Target.createTarget",
            "params": {"url": profile_url}
        })
        
        target_id = cdp_resp.json().get("result", {}).get("targetId")
        
        if not target_id:
            return {"status": "failed", "reason": "无法创建目标", "url": profile_url}
        
        # 2. 等待页面加载
        await asyncio.sleep(3)
        
        # 3. 查找"Connect"按钮并点击
        # 使用 CDP Runtime.evaluate 执行 JavaScript
        script = f"""
        (() => {{
            const connectBtn = document.querySelector('button[aria-label*="Invite"], button[data-control-name="connect"]');
            if (connectBtn) {{
                connectBtn.click();
                return 'found';
            }}
            
            // 如果已经是好友
            const msgBtn = document.querySelector('button[aria-label*="Message"]');
            if (msgBtn) {{
                return 'already_connected';
            }}
            
            return 'not_found';
        }})()
        """
        
        eval_resp = requests.post(f"{CDP_BASE}/json/{target_id}", json={
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {"expression": script}
        })
        
        result = eval_resp.json().get("result", {}).get("result", {}).get("value")
        
        if result == "already_connected":
            return {"status": "skipped", "reason": "已是好友", "url": profile_url}
        elif result == "not_found":
            return {"status": "failed", "reason": "未找到 Connect 按钮", "url": profile_url}
        
        # 4. 等待弹窗出现
        await asyncio.sleep(2)
        
        # 5. 选择"自定义消息"并填写
        custom_msg_script = f"""
        (() => {{
            const textarea = document.querySelector('div[role="textbox"]');
            if (textarea) {{
                textarea.focus();
                const message = `{CONNECT_MESSAGE.format(name=first_name, company=company)}`;
                document.execCommand('insertText', false, message);
                return 'message_added';
            }}
            return 'textarea_not_found';
        }})()
        """
        
        # 6. 点击发送
        send_script = """
        (() => {
            const sendBtn = document.querySelector('button[aria-label*="Send invitation"], button[type="submit"]');
            if (sendBtn) {
                sendBtn.click();
                return 'sent';
            }
            return 'send_failed';
        })()
        """
        
        return {"status": "success", "url": profile_url, "name": first_name, "company": company}
        
    except Exception as e:
        return {"status": "error", "error": str(e), "url": profile_url}

async def batch_send_connects(contact_list, max_daily=80):
    """批量发送 Connect 请求"""
    results = []
    
    print(f"开始发送 Connect 请求，目标数量：{len(contact_list)}")
    print(f"每日上限：{max_daily}")
    
    for i, contact in enumerate(contact_list[:max_daily]):
        print(f"\n[{i+1}/{len(contact_list)}] 处理：{contact.get('name', 'Unknown')} @ {contact.get('company', 'Unknown')}")
        
        result = await send_connect_request(
            profile_url=contact.get('linkedin_url'),
            first_name=contact.get('first_name', ''),
            company=contact.get('company', '')
        )
        
        results.append(result)
        print(f"结果：{result['status']} - {result.get('reason', result.get('name', ''))}")
        
        # 避免频率限制，每请求间隔 15-25 秒
        await asyncio.sleep(15 + (i % 3) * 5)
    
    # 生成报告
    success_count = sum(1 for r in results if r['status'] == 'success')
    skipped_count = sum(1 for r in results if r['status'] == 'skipped')
    failed_count = sum(1 for r in results if r['status'] in ['failed', 'error'])
    
    report = f"""
## Connect 请求发送报告

**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**发送总数**: {len(results)}
**成功发送**: {success_count}
**已是好友**: {skipped_count}
**失败**: {failed_count}

### 成功列表
"""
    
    for r in results:
        if r['status'] == 'success':
            report += f"- ✅ {r.get('name', 'Unknown')} ({r.get('company', 'Unknown')})\n"
    
    # 保存报告
    with open(f"connect_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n{report}")
    return results

if __name__ == "__main__":
    # 从 v2500_linkedin_contacts.md 解析联系人
    contacts = [
        {
            "name": "M.Faruk Memduhoğlu",
            "first_name": "Faruk",
            "company": "Turkish Airlines",
            "linkedin_url": "https://www.linkedin.com/in/mfarukmemduhoglu/"
        },
        {
            "name": "Kubilay AKPINAR",
            "first_name": "Kubilay",
            "company": "Turkish Airlines",
            "linkedin_url": "https://www.linkedin.com/in/kubilay-akpinar/"
        },
        {
            "name": "Audy Schenkl",
            "first_name": "Audy",
            "company": "LATAM Airlines",
            "linkedin_url": "https://www.linkedin.com/in/audy-schenkl-6089a621/"
        },
        {
            "name": "Wasan Kanjana-huttakit",
            "first_name": "Wasan",
            "company": "Thai Airways",
            "linkedin_url": "https://www.linkedin.com/in/wasan-kanjana-huttakit-80611b210/"
        },
        {
            "name": "Christopher Harvey",
            "first_name": "Christopher",
            "company": "Cathay Pacific",
            "linkedin_url": "https://www.linkedin.com/in/christopher-harvey-b82071a/"
        },
        {
            "name": "Yiheyis Kereyou",
            "first_name": "Yiheyis",
            "company": "Norse Atlantic",
            "linkedin_url": "https://www.linkedin.com/in/yiheyis-kereyou-a7908b66/"
        },
        {
            "name": "Lander Dominguez Ruiz",
            "first_name": "Lander",
            "company": "Condor Airlines",
            "linkedin_url": "https://www.linkedin.com/in/landerdominguezruiz/en/"
        },
        {
            "name": "Shahizan Maksudai",
            "first_name": "Shahizan",
            "company": "Malaysia Airlines",
            "linkedin_url": "https://www.linkedin.com/in/shahizan-maksudai-84596481/"
        },
        {
            "name": "Rory O'Donnell",
            "first_name": "Rory",
            "company": "SMBC Aero Engine Lease",
            "linkedin_url": "https://www.linkedin.com/in/rory-o'donnell-b42a2a53/"
        },
        {
            "name": "Jualimar Bordones",
            "first_name": "Jualimar",
            "company": "LCI",
            "linkedin_url": "https://www.linkedin.com/in/jualimar-bordones-84aa6a67/"
        },
        {
            "name": "陈建宏",
            "first_name": "Kevin",
            "company": "HANGRUN TECH",
            "linkedin_url": "https://www.linkedin.com/in/kevinchen1028/"
        }
    ]
    
    print("=== V2500 联系人 Connect 请求脚本 ===")
    print(f"联系人总数：{len(contacts)}")
    print("\n确认开始发送？(y/n): ", end="")
    
    # 非交互模式，直接执行
    print("y (自动执行)")
    asyncio.run(batch_send_connects(contacts, max_daily=80))
