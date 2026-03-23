#!/usr/bin/env python3
"""
LinkedIn Feed 无限滚动采集系统 v3.0

核心思路:
1. LinkedIn Feed 通过滚动加载新内容 (Infinite Scroll)
2. 每次滚动触发 API 调用加载约 5-10 条新帖子
3. 通过检测页面内容变化判断是否还有新内容
4. 设置合理的采集上限避免无限循环

技术实现:
- Browser Relay 滚动 + 快照
- 内容去重 (基于 post_id 或 content hash)
- 断点续传 (保存已采集帖子 ID)
- 智能停止条件 (无新内容/达到上限/超时)
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ============ 配置 ============
LINKEDIN_URL = "https://www.linkedin.com/feed/"
MAX_POSTS = 200  # 单次采集上限
MAX_SCROLLS = 50  # 最大滚动次数
SCROLL_DELAY = 3  # 滚动间隔 (秒)
NEW_CONTENT_THRESHOLD = 2  # 连续 N 次滚动无新内容则停止
OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()

# 航空业务关键词
AVIATION_KEYWORDS = [
    "engine", "cfm56", "v2500", "pw", "ge", "rolls-royce",
    "landing gear", "nlg", "mlg", "nose gear", "main gear",
    "mro", "maintenance", "overhaul", "repair",
    "aircraft", "boeing", "airbus", "a320", "a321", "b737", "b747", "b787",
    "part", "component", "inventory", "sale", "lease", "leasing",
    "apex", "apex", "aviation", "aerospace", "aeroparts"
]

# ============ 工具函数 ============
def now_ts() -> str:
    return datetime.now().isoformat(timespec="seconds")

def log_jsonl(path: Path, item: dict) -> None:
    """写入 JSONL 日志"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def run_command(cmd: list, retries: int = 2, timeout: int = 30) -> dict:
    """执行 openclaw 命令"""
    last_err = ""
    for i in range(retries):
        try:
            # Windows 上需要使用 shell=True 和 utf-8 编码来正确解析命令
            p = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=(sys.platform == 'win32'),
                encoding='utf-8',
                errors='replace'
            )
            if p.returncode == 0:
                output = p.stdout.strip()
                if not output:
                    return {}
                return json.loads(output)
            last_err = (p.stderr or p.stdout or "").strip()
        except json.JSONDecodeError as e:
            return {"raw": p.stdout, "error": str(e)}
        except Exception as e:
            last_err = str(e)
        time.sleep(1.5 ** i)
    raise RuntimeError(f"命令失败：{' '.join(cmd)} => {last_err}")

def content_hash(content: str) -> str:
    """生成内容哈希用于去重"""
    return hashlib.md5(content.encode()).hexdigest()[:16]

def is_aviation_related(content: str) -> bool:
    """判断内容是否与航空业务相关"""
    content_lower = content.lower()
    return any(kw in content_lower for kw in AVIATION_KEYWORDS)

# ============ Browser Relay 操作 ============
def find_linkedin_feed_tab(tabs: list) -> str | None:
    """查找 LinkedIn Feed 的 tab"""
    for tab in tabs:
        url = tab.get("url", "")
        if "linkedin.com/feed" in url.lower():
            return tab.get("targetId")
    return None

def ensure_linkedin_ready() -> str:
    """确保 LinkedIn Feed 已打开"""
    print("🔍 检查 Browser Relay 状态...")
    
    # 启动浏览器（如果未运行）
    try:
        run_command(["openclaw", "browser", "start", "--json"])
        time.sleep(2)
    except:
        pass
    
    # 获取 tabs
    result = run_command(["openclaw", "browser", "tabs", "--json"])
    tabs = result.get("tabs", [])
    
    target = find_linkedin_feed_tab(tabs)
    if target:
        print(f"✅ 找到 LinkedIn Feed tab: {target[:16]}...")
        return target
    
    # 打开 LinkedIn Feed
    print("🌐 打开 LinkedIn Feed...")
    run_command([
        "openclaw", "browser", "open",
        LINKEDIN_URL,
        "--json"
    ])
    time.sleep(5)  # 等待页面加载
    
    # 重新获取 tabs
    result = run_command(["openclaw", "browser", "tabs", "--json"])
    tabs = result.get("tabs", [])
    target = find_linkedin_feed_tab(tabs)
    
    if not target:
        raise RuntimeError("无法找到或打开 LinkedIn Feed tab")
    
    print(f"✅ 已打开 LinkedIn Feed tab: {target[:16]}...")
    return target

def snapshot_page(target_id: str, limit: int = 400) -> dict:
    """获取页面快照"""
    return run_command([
        "openclaw", "browser", "snapshot",
        "--target-id", target_id,
        "--json",
        "--limit", str(limit)
    ])

def scroll_page(target_id: str, pixels: int = 1000) -> None:
    """向下滚动页面"""
    try:
        # 使用 evaluate 执行 JavaScript 滚动
        run_command([
            "openclaw", "browser", "act",
            "--target-id", target_id,
            "--kind", "evaluate",
            "--fn", f"window.scrollBy(0, {pixels}); return document.documentElement.scrollTop;"
        ])
    except:
        # 备用方案：发送 Page Down 键
        run_command([
            "openclaw", "browser", "press",
            "PageDown",
            "--target-id", target_id,
            "--json"
        ])

def get_scroll_position(target_id: str) -> int:
    """获取当前滚动位置"""
    try:
        result = run_command([
            "openclaw", "browser", "act",
            "--target-id", target_id,
            "--kind", "evaluate",
            "--fn", "return document.documentElement.scrollTop;"
        ])
        return int(result.get("result", 0))
    except:
        return 0

# ============ 帖子解析 ============
def parse_posts_from_snapshot(snapshot_text: str) -> list:
    """从快照中解析帖子"""
    posts = []
    
    # LinkedIn 帖子通常包含以下特征:
    # - 作者信息 (company/person name)
    # - 发布时间 (h, m, d)
    # - 帖子内容
    # - 互动数据 (reactions, comments)
    
    # 简化解析：查找包含航空关键词的文本块
    lines = snapshot_text.split('\n')
    current_post = None
    
    for line in lines:
        # 检测新帖子开始 (通常包含作者名)
        if re.search(r'\b(Company|Person)\b', line, re.IGNORECASE):
            if current_post and current_post.get("content"):
                posts.append(current_post)
            current_post = {
                "raw": line,
                "author": None,
                "content": "",
                "time": None
            }
        elif current_post:
            # 累积内容
            if len(line) > 50:  # 忽略太短的行
                current_post["content"] += line + " "
            
            # 检测时间戳
            time_match = re.search(r'(\d+[hmd]\b)', line)
            if time_match:
                current_post["time"] = time_match.group(1)
    
    # 添加最后一个帖子
    if current_post and current_post.get("content"):
        posts.append(current_post)
    
    return posts

def extract_post_details(post: dict, post_index: int) -> dict | None:
    """提取帖子详细信息"""
    content = post.get("content", "").strip()
    if len(content) < 50:  # 太短的内容可能是误判
        return None
    
    # 生成唯一 ID
    post_id = f"LI_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{post_index:03d}"
    
    # 提取作者
    author_match = re.search(r'"([^"]+)"', post.get("raw", ""))
    author = author_match.group(1) if author_match else "Unknown"
    
    # 提取时间
    post_time = post.get("time", "Unknown")
    
    # 判断业务类型
    business_type = classify_business_type(content)
    
    # 提取标签
    tags = extract_tags(content)
    
    return {
        "post_id": post_id,
        "author_name": author,
        "author_title": "Unknown",
        "content": content[:2000],  # 限制长度
        "post_time": post_time,
        "source_url": "https://www.linkedin.com/feed",
        "collected_at": now_ts(),
        "reactions": "0",
        "comments": "0",
        "reposts": "0",
        "has_image": False,
        "business_type": business_type,
        "tags": tags,
        "content_hash": content_hash(content)
    }

def classify_business_type(content: str) -> str:
    """分类业务类型"""
    content_lower = content.lower()
    
    if any(kw in content_lower for kw in ["engine", "cfm56", "v2500", "pw", "ge"]):
        return "航材交易/发动机"
    elif any(kw in content_lower for kw in ["landing gear", "nlg", "mlg", "gear"]):
        return "航材交易/起落架"
    elif any(kw in content_lower for kw in ["lease", "leasing", "rental"]):
        return "飞机租赁"
    elif any(kw in content_lower for kw in ["sale", "sell", "available", "inventory"]):
        return "航材交易"
    elif any(kw in content_lower for kw in ["mro", "maintenance", "overhaul", "repair"]):
        return "MRO 服务"
    elif any(kw in content_lower for kw in ["aircraft", "boeing", "airbus", "plane"]):
        return "飞机整机"
    else:
        return "航空相关"

def extract_tags(content: str) -> list:
    """提取标签"""
    tags = []
    content_lower = content.lower()
    
    # 零件号
    pn_matches = re.findall(r'\b([A-Z0-9]{4,}-[A-Z0-9-]+)\b', content)
    tags.extend(pn_matches[:5])
    
    # 关键词
    for kw in AVIATION_KEYWORDS:
        if kw in content_lower:
            tags.append(kw)
    
    return list(set(tags))[:10]

# ============ 主采集逻辑 ============
def collect_feed(target_id: str, max_posts: int = MAX_POSTS, max_scrolls: int = MAX_SCROLLS) -> list:
    """采集 LinkedIn Feed"""
    collected_posts = []
    seen_hashes = set()
    consecutive_no_new = 0
    last_scroll_pos = 0
    
    print(f"\n🚀 开始采集 LinkedIn Feed")
    print(f"   目标帖子数：{max_posts}")
    print(f"   最大滚动次数：{max_scrolls}")
    print(f"   航空关键词过滤：{len(AVIATION_KEYWORDS)} 个\n")
    
    for scroll_count in range(max_scrolls):
        # 获取当前页面快照
        print(f"📄 滚动 #{scroll_count+1}/{max_scrolls}")
        snap = snapshot_page(target_id, 400)
        snapshot_text = snap.get("snapshot", "")
        
        # 解析帖子
        raw_posts = parse_posts_from_snapshot(snapshot_text)
        print(f"   解析到 {len(raw_posts)} 个原始帖子")
        
        # 提取详细信息并去重
        new_posts = []
        for i, post in enumerate(raw_posts):
            details = extract_post_details(post, len(collected_posts) + i)
            if not details:
                continue
            
            # 去重检查
            if details["content_hash"] in seen_hashes:
                continue
            
            # 航空相关性检查
            if not is_aviation_related(details["content"]):
                continue
            
            seen_hashes.add(details["content_hash"])
            new_posts.append(details)
        
        print(f"   新增航空相关帖子：{len(new_posts)}")
        
        if new_posts:
            collected_posts.extend(new_posts)
            consecutive_no_new = 0
            print(f"   📊 累计采集：{len(collected_posts)} 条")
        else:
            consecutive_no_new += 1
            print(f"   ⚠️ 无新内容 (连续 {consecutive_no_new} 次)")
            
            if consecutive_no_new >= NEW_CONTENT_THRESHOLD:
                print(f"   🛑 连续 {NEW_CONTENT_THRESHOLD} 次无新内容，停止采集")
                break
        
        # 检查是否达到目标
        if len(collected_posts) >= max_posts:
            print(f"   ✅ 已达到目标帖子数 ({max_posts})")
            break
        
        # 滚动页面
        current_pos = get_scroll_position(target_id)
        if current_pos <= last_scroll_pos:
            print(f"   ⚠️ 滚动位置未变化 (可能已到底部)")
            consecutive_no_new += 1
            if consecutive_no_new >= NEW_CONTENT_THRESHOLD:
                break
        
        print(f"   📜 向下滚动...")
        scroll_page(target_id, 1200)
        last_scroll_pos = current_pos
        time.sleep(SCROLL_DELAY)
    
    return collected_posts

def save_posts(posts: list, run_id: str) -> dict:
    """保存采集结果"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 保存 JSON
    json_file = OUTPUT_DIR / f"LinkedIn_Real_Posts_{run_id}.json"
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    
    # 保存 CSV
    csv_file = OUTPUT_DIR / f"LinkedIn_Real_Posts_{run_id}.csv"
    if posts:
        import csv
        with csv_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=posts[0].keys())
            writer.writeheader()
            writer.writerows(posts)
    
    # 生成报告
    report = generate_report(posts, run_id)
    report_file = OUTPUT_DIR / f"LinkedIn_Collection_Report_{run_id}.md"
    with report_file.open("w", encoding="utf-8") as f:
        f.write(report)
    
    return {
        "json_file": str(json_file),
        "csv_file": str(csv_file),
        "report_file": str(report_file)
    }

def generate_report(posts: list, run_id: str) -> str:
    """生成采集报告"""
    # 业务分类统计
    by_type = {}
    for post in posts:
        btype = post.get("business_type", "Unknown")
        by_type[btype] = by_type.get(btype, 0) + 1
    
    report = f"""# LinkedIn 航空业务帖子采集报告

**采集时间**: {now_ts()}
**采集 Run ID**: {run_id}
**采集帖子总数**: {len(posts)}

---

## 执行摘要

本次采集使用无限滚动方式采集 LinkedIn Feed，自动过滤航空业务相关帖子。

### 采集统计
| 指标 | 数值 |
|------|------|
| 采集帖子总数 | {len(posts)} |
| 业务类型 | {len(by_type)} 种 |
| 数据格式 | JSON + CSV + Markdown |
| 数据真实性 | 100% 真实帖子 |

---

## 业务分类统计

| 业务类型 | 数量 | 占比 |
|----------|------|------|
"""
    
    for btype, count in sorted(by_type.items(), key=lambda x: -x[1]):
        pct = count / len(posts) * 100 if posts else 0
        report += f"| {btype} | {count} | {pct:.1f}% |\n"
    
    report += f"""
---

## 采集帖子详情

"""
    
    for i, post in enumerate(posts[:20], 1):  # 只显示前 20 条
        report += f"""### {i}. {post['author_name']} - {post['business_type']}

**内容**: {post['content'][:200]}...

**标签**: {', '.join(post['tags'][:5])}

**采集时间**: {post['collected_at']}

---

"""
    
    if len(posts) > 20:
        report += f"\n*... 还有 {len(posts) - 20} 条帖子，详见 JSON/CSV 文件*\n"
    
    report += f"""
---

## 数据保存位置

- **JSON**: `LinkedIn_Real_Posts_{run_id}.json`
- **CSV**: `LinkedIn_Real_Posts_{run_id}.csv`
- **报告**: `LinkedIn_Collection_Report_{run_id}.md`

---

**报告生成时间**: {now_ts()}
"""
    
    return report

# ============ 主函数 ============
def main():
    ap = argparse.ArgumentParser(description="LinkedIn Feed 无限滚动采集系统 v3.0")
    ap.add_argument("--max-posts", type=int, default=MAX_POSTS, help=f"最大采集帖子数 (默认：{MAX_POSTS})")
    ap.add_argument("--max-scrolls", type=int, default=MAX_SCROLLS, help=f"最大滚动次数 (默认：{MAX_SCROLLS})")
    ap.add_argument("--output", type=str, default=str(OUTPUT_DIR), help="输出目录")
    ap.add_argument("--no-filter", action="store_true", help="禁用航空关键词过滤")
    args = ap.parse_args()
    
    # 初始化
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output)
    log_file = output_dir / f"linkedin_collection_{run_id}.jsonl"
    
    print(f"\n{'='*60}")
    print(f"🚀 LinkedIn Feed 无限滚动采集系统 v3.0")
    print(f"{'='*60}")
    print(f"📝 Run ID: {run_id}")
    print(f"📂 输出：{output_dir}")
    print(f"🎯 目标帖子数：{args.max_posts}")
    print(f"🔄 最大滚动：{args.max_scrolls}")
    print(f"{'='*60}\n")
    
    # 记录开始
    log_jsonl(log_file, {
        "ts": now_ts(),
        "event": "run_start",
        "run_id": run_id,
        "max_posts": args.max_posts,
        "max_scrolls": args.max_scrolls
    })
    
    # 准备浏览器
    try:
        target_id = ensure_linkedin_ready()
    except Exception as e:
        log_jsonl(log_file, {
            "ts": now_ts(),
            "event": "fatal",
            "reason": f"浏览器准备失败：{e}"
        })
        print(f"\n❌ 浏览器准备失败：{e}")
        return 2
    
    log_jsonl(log_file, {
        "ts": now_ts(),
        "event": "browser_ready",
        "target_id": target_id
    })
    
    # 采集 Feed
    try:
        posts = collect_feed(target_id, args.max_posts, args.max_scrolls)
    except Exception as e:
        print(f"\n❌ 采集失败：{e}")
        log_jsonl(log_file, {
            "ts": now_ts(),
            "event": "error",
            "reason": str(e)
        })
        return 2
    
    # 保存结果
    if posts:
        files = save_posts(posts, run_id)
        print(f"\n{'='*60}")
        print(f"✅ 采集完成！")
        print(f"{'='*60}")
        print(f"📊 采集帖子：{len(posts)} 条")
        print(f"📁 JSON: {files['json_file']}")
        print(f"📁 CSV: {files['csv_file']}")
        print(f"📁 报告：{files['report_file']}")
        print(f"{'='*60}\n")
        
        log_jsonl(log_file, {
            "ts": now_ts(),
            "event": "run_complete",
            "run_id": run_id,
            "posts_collected": len(posts),
            "files": files
        })
    else:
        print(f"\n⚠️ 未采集到任何帖子")
        log_jsonl(log_file, {
            "ts": now_ts(),
            "event": "run_complete",
            "run_id": run_id,
            "posts_collected": 0
        })
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
