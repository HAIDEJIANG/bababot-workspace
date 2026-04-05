#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 采集脚本 v9.0 - CDP 协议版（无需 Playwright）

更新内容：
1. 使用纯 CDP 协议通过 WebSocket 连接浏览器
2. 不依赖 Playwright，使用标准库 + websocket-client
3. 连接 Edge 浏览器的远程调试端口
4. Cookie 自动复用（浏览器已登录状态）

使用前提：
- Edge 浏览器已启动并登录 LinkedIn
- Edge 启动参数包含 --remote-debugging-port=9222
- 或使用 BROWSER_CONFIG.md 中的配置

用法：
  python scripts/linkedin_v9_cdp.py --duration 30
  python scripts/linkedin_v9_cdp.py --port 9224
"""

import sys
import io
import time
import json
import re
import argparse
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 导入 CDP 客户端
from cdp_client import CDPClient, log

# ==================== 配置 ====================

OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)

# 采集配置
DEFAULT_DURATION_MINUTES = 30
SCROLL_PAUSE = 3  # 滚动后等待秒数
SCROLL_PIXELS = 600  # 每次滚动像素
REFRESH_INTERVAL = 5  # 每 5 分钟刷新一次页面
SCROLL_PER_REFRESH = 20  # 每次刷新后滚动 20 次

# PN 号识别正则
PN_PATTERNS = [
    r'\b[0-9]{6,}-[0-9]{2,}\b',
    r'\b[A-Z]{2,}[0-9]{4,}-[0-9]{2,}\b',
    r'\b[0-9]{4,}[A-Z]{1,3}-[0-9]{2,}\b',
    r'\b[A-Z]{1,2}-[0-9]{4,}-[0-9]{2,}\b',
]

# 业务关键词（用于筛选高价值帖子）
BUSINESS_KEYWORDS = [
    'available', 'stock', 'price', 'quote', 'RFQ', 'offer',
    '现货', '价格', '询价', '报价', '出售', '采购',
    'PN', 'P/N', 'Part Number', '件号',
    'CFM56', 'V2500', 'A320', 'B737', 'engine', 'landing gear', 'APU',
]

# ==================== 工具函数 ====================

def extract_pn(text: str) -> list:
    """从文本中提取零件号"""
    pns = []
    for pattern in PN_PATTERNS:
        pns.extend(re.findall(pattern, text, re.IGNORECASE))
    return list(set(pns))

def has_business_intent(text: str) -> bool:
    """判断帖子是否有业务意图"""
    text_lower = text.lower()
    score = 0
    for keyword in BUSINESS_KEYWORDS:
        if keyword.lower() in text_lower:
            score += 1
    return score >= 2

def save_posts(posts: list, output_file: Path):
    """保存帖子到 CSV"""
    if not posts:
        return
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # 表头
        f.write("采集时间，发帖人，发布时间，内容摘要，零件号，业务意图，原始链接\n")
        
        for post in posts:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            author = post.get('author', 'Unknown').replace(',', ' ')
            pub_time = post.get('timestamp', '') or ''
            content = post.get('text', '')[:500].replace(',', ' ').replace('\n', ' ')
            pns = ','.join(post.get('pn', []))
            business = '是' if post.get('business_intent') else '否'
            link = post.get('link', '')
            
            f.write(f"{timestamp},{author},{pub_time},{content},{pns},{business},{link}\n")
    
    log(f"[OK] 已保存 {len(posts)} 条帖子到：{output_file}")

def append_to_master(posts: list, master_file: Path):
    """追加帖子到 Master Table（不覆盖历史数据）"""
    if not posts:
        log("[WARN] 无新帖子需要追加")
        return 0
    
    # 检查 Master Table 是否存在
    if not master_file.exists():
        log(f"[WARN] Master Table 不存在：{master_file}")
        return 0
    
    # 读取现有记录的 ID，避免重复
    import csv
    existing_ids = set()
    try:
        with open(master_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'post_id' in row:
                    existing_ids.add(row['post_id'])
    except Exception as e:
        log(f"[WARN] 读取 Master Table 失败：{e}")
    
    # 追加新记录
    appended = 0
    timestamp_base = datetime.now().strftime('%Y%m%d')
    
    with open(master_file, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        for i, post in enumerate(posts, start=1):
            # 生成唯一 ID
            post_id = f"linkedin_real_{timestamp_base}_{i:03d}"
            if post_id in existing_ids:
                continue
            
            # 写入记录（简化格式，匹配 Master Table 结构）
            author = post.get('author', 'Unknown')
            content = post.get('text', '')[:200]
            pns = post.get('pn', [])
            business = '航材销售' if post.get('business_intent') else '行业资讯'
            contact = ''
            if 'sales@' in content or '@' in content:
                # 提取邮箱
                import re
                emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)
                if emails:
                    contact = emails[0]
            
            # 写入简化行（匹配现有格式）
            row_data = [
                post_id,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                author,
                '',  # company
                '',  # position
                content,
                business,
                '8.0',  # business_value_score
                '中',  # urgency
                'True' if contact else 'False',
                contact,
                '', '', '', '', '', '', '', '', '', '', '', '', '',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                content[:100], '', '', '', '', '', '', '', 'active', '', '', ''
            ]
            writer.writerow(row_data)
            appended += 1
    
    log(f"[OK] 已追加 {appended} 条帖子到 Master Table：{master_file}")
    return appended

def save_raw_posts(posts: list, output_file: Path):
    """保存原始帖子数据（JSON 格式）"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    log(f"[OK] 已保存原始数据到：{output_file}")

# ==================== 主采集流程 ====================

def collect_linkedin_posts(duration_minutes: int, port: int):
    """主采集函数"""
    log("=" * 70)
    log("LinkedIn 采集 v9.0 - CDP 协议版")
    log("=" * 70)
    log(f"采集时长：{duration_minutes} 分钟")
    log(f"CDP 端口：{port}")
    log(f"输出目录：{OUTPUT_DIR}")
    
    # 初始化 CDP 客户端
    client = CDPClient(port=port)
    
    # 检查浏览器连接
    tabs = client.get_browser_tabs()
    if not tabs:
        log("[ERR] 无法连接到浏览器，请确保 Edge 已启动并开启远程调试")
        log("启动命令：msedge --remote-debugging-port=9222")
        return
    
    log(f"[OK] 浏览器已连接，找到 {len(tabs)} 个标签页")
    
    # 查找 LinkedIn Feed 页面
    linkedin_tab = client.find_linkedin_feed()
    if not linkedin_tab:
        log("[ERR] 未找到已登录的 LinkedIn Feed 页面")
        log("请在 Edge 中打开：https://www.linkedin.com/feed")
        log("并确保已登录账号")
        return
    
    log(f"[OK] 找到 LinkedIn Feed: {linkedin_tab.get('title', 'N/A')}")
    
    # 连接到该标签页（使用 Target.attachToTarget 方式）
    if not client.connect(linkedin_tab.get('id')):
        log("[ERR] CDP 连接失败")
        return
    
    # 验证页面信息
    page_info = client.get_page_info()
    log(f"页面信息：Title={page_info.get('title', 'N/A')}, BodyText={page_info.get('bodyTextLen', 0)} chars")
    
    if page_info.get('bodyTextLen', 0) == 0:
        log("[WARN] 页面内容为空，可能需要等待加载")
        time.sleep(3)
    
    # 开始采集
    log("\n" + "=" * 70)
    log("开始采集（支持刷新获取最新内容）...")
    log(f"刷新间隔：每 {REFRESH_INTERVAL} 分钟")
    log(f"每次刷新后滚动：{SCROLL_PER_REFRESH} 次")
    log("=" * 70)
    
    posts_collected = []
    seen_hashes = set()
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    scroll_count = 0
    refresh_count = 0
    last_refresh_time = start_time
    scroll_in_cycle = 0  # 本轮滚动计数
    
    while time.time() < end_time:
        try:
            elapsed_minutes = (time.time() - start_time) / 60
            
            # 检查是否需要刷新页面
            time_since_refresh = (time.time() - last_refresh_time) / 60
            if time_since_refresh >= REFRESH_INTERVAL:
                log(f"\n[REFRESH] 刷新页面获取最新内容 (第 {refresh_count + 1} 次刷新)")
                
                # 执行刷新
                client.evaluate("window.location.reload()")
                time.sleep(8)  # 等待页面重新加载
                
                # 重置滚动计数
                scroll_in_cycle = 0
                
                # 更新刷新时间
                last_refresh_time = time.time()
                refresh_count += 1
                
                log(f"[REFRESH] 页面已刷新，继续采集...")
                
                # 保存进度
                temp_file = OUTPUT_DIR / f"linkedin_posts_temp_{datetime.now().strftime('%H%M')}.json"
                save_raw_posts(posts_collected, temp_file)
            
            # 提取帖子
            posts = client.extract_posts()
            new_count = 0
            
            for post_data in posts:
                post_hash = hash(post_data.get('hash', ''))
                
                if post_hash not in seen_hashes:
                    seen_hashes.add(post_hash)
                    
                    # 提取零件号
                    pns = extract_pn(post_data.get('text', ''))
                    
                    # 判断业务意图
                    business = has_business_intent(post_data.get('text', ''))
                    
                    # 构建帖子记录
                    post_record = {
                        'author': post_data.get('author', 'Unknown'),
                        'text': post_data.get('text', ''),
                        'timestamp': post_data.get('timestamp'),
                        'pn': pns,
                        'business_intent': business,
                        'link': f"https://www.linkedin.com/feed/update/{post_hash}",
                        'collected_at': datetime.now().isoformat()
                    }
                    
                    posts_collected.append(post_record)
                    new_count += 1
                    
                    if business or pns:
                        log(f"[TARGET] 高价值帖子：{post_data.get('author', 'Unknown')[:30]} | PN: {pns if pns else 'N/A'}")
            
            if new_count > 0:
                log(f"[NEW] 新增 {new_count} 条帖子（总计：{len(posts_collected)}）")
            
            # 滚动页面
            scroll_count += 1
            log(f"[SCROLL] 滚动页面 (第 {scroll_count} 次，本轮第 {scroll_in_cycle + 1} 次)")
            client.scroll_page(SCROLL_PIXELS)
            scroll_in_cycle += 1
            time.sleep(SCROLL_PAUSE)
            
            # 如果本轮滚动达到上限，重置计数继续滚动
            if scroll_in_cycle >= SCROLL_PER_REFRESH:
                scroll_in_cycle = 0
                log(f"[INFO] 本轮滚动 {SCROLL_PER_REFRESH} 次完成，重置计数继续采集")
        
        except Exception as e:
            log(f"[WARN] 采集异常：{e}")
            time.sleep(5)
            # 尝试重连
            if not client.connect(linkedin_tab.get('id')):
                log("[ERR] 重连失败，尝试重新查找标签页...")
                linkedin_tab = client.find_linkedin_feed()
                if linkedin_tab:
                    client.disconnect()
                    if not client.connect(linkedin_tab.get('id')):
                        log("[ERR] 无法重新连接")
                        break
    
    # 采集结束
    client.disconnect()
    
    elapsed_minutes = (time.time() - start_time) / 60
    log("\n" + "=" * 70)
    log("采集完成")
    log("=" * 70)
    log(f"运行时长：{elapsed_minutes:.1f} 分钟")
    log(f"采集帖子：{len(posts_collected)} 条")
    log(f"滚动次数：{scroll_count} 次")
    log(f"刷新次数：{refresh_count} 次")
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = OUTPUT_DIR / f"linkedin_posts_{timestamp}.csv"
    json_file = OUTPUT_DIR / f"linkedin_posts_{timestamp}.json"
    
    save_posts(posts_collected, csv_file)
    save_raw_posts(posts_collected, json_file)
    
    # 追加到 Master Table（不覆盖历史数据）
    master_file = OUTPUT_DIR / "LinkedIn_Business_Posts_Master_Table.csv"
    appended = append_to_master(posts_collected, master_file)
    
    # 统计高价值帖子
    high_value = [p for p in posts_collected if p.get('business_intent') or p.get('pn')]
    if high_value:
        log(f"\n[TARGET] 高价值帖子：{len(high_value)} 条")
        for post in high_value[:10]:
            pn_list = post.get('pn', [])
            pn_str = pn_list[0] if pn_list else 'N/A'
            log(f"  - {post.get('author', 'Unknown')[:40]} | PN: {pn_str}")
    
    return len(posts_collected)

# ==================== 命令行入口 ====================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LinkedIn 采集 - CDP 协议版')
    parser.add_argument('--duration', type=int, default=DEFAULT_DURATION_MINUTES,
                        help=f'采集时长（分钟），默认 {DEFAULT_DURATION_MINUTES}')
    parser.add_argument('--port', type=int, default=18800,
                        help='CDP 调试端口，默认 18800（Browser Relay）')
    
    args = parser.parse_args()
    
    try:
        collect_linkedin_posts(args.duration, args.port)
    except KeyboardInterrupt:
        log("\n[WARN] 用户中断")
    except Exception as e:
        log(f"\n[ERR] 程序异常：{e}")
        import traceback
        traceback.print_exc()
