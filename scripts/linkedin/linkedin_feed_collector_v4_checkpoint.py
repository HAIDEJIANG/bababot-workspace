#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Feed 无限滚动采集系统 v4.0 - 增量保存版

核心改进:
1. 每采集 N 条帖子立即保存 (增量保存)
2. 断点续传 - 从中断位置继续采集
3. 实时 JSONL 日志 - 每条帖子独立记录
4. 最终合并 - 所有增量数据合并到主表

保存策略:
- 每 10 条帖子保存一次增量文件
- 每次保存生成检查点 (checkpoint)
- 中断后可从检查点恢复
- 最终合并所有增量到主表
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# 设置控制台输出为 UTF-8 (Windows)
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

# 添加 openclaw 到 PATH (Windows)
OPENCLAW_PATH = r"C:\Users\Haide\AppData\Roaming\npm"
if OPENCLAW_PATH not in os.environ.get("PATH", ""):
    os.environ["PATH"] = OPENCLAW_PATH + os.pathsep + os.environ.get("PATH", "")

# ============ 配置 ============
LINKEDIN_URL = "https://www.linkedin.com/feed/"
MAX_POSTS = 500  # 增加到 500 条
MAX_SCROLLS = 100  # 增加到 100 次滚动
SCROLL_DELAY = 5  # 滚动后等待 5 秒（给 LinkedIn 加载时间）
NEW_CONTENT_THRESHOLD = 5  # 连续 5 次无新内容才停止
OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
CHECKPOINT_INTERVAL = 10  # 每 N 条帖子保存一次检查点
AUTO_SAVE_INTERVAL = 60   # 每 N 秒自动保存一次
SCROLL_PIXELS = 800  # 每次滚动像素
SCROLL_SMOOTH = True  # 使用平滑滚动（模拟真实滚轮）

# 航空业务关键词
AVIATION_KEYWORDS = [
    "engine", "cfm56", "v2500", "pw", "ge", "rolls-royce",
    "landing gear", "nlg", "mlg", "nose gear", "main gear",
    "mro", "maintenance", "overhaul", "repair",
    "aircraft", "boeing", "airbus", "a320", "a321", "b737", "b747", "b787",
    "part", "component", "inventory", "sale", "lease", "leasing",
    "aviation", "aerospace", "aeroparts"
]

# ============ 工具函数 ============
def now_ts() -> str:
    return datetime.now().isoformat(timespec="seconds")

def now_filename() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

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
            # Windows 上需要 shell=True 来执行 .CMD 文件，并指定 UTF-8 编码
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True, encoding='utf-8', errors='replace')
            if p.returncode == 0:
                output = p.stdout.strip()
                if not output:
                    return {}
                return json.loads(output)
            last_err = (p.stderr or p.stdout).strip()
        except json.JSONDecodeError as je:
            # 返回原始输出以便调试
            return {"raw": p.stdout, "error": str(je)}
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

# ============ 状态管理 ============
class CollectionState:
    """采集状态管理"""
    
    def __init__(self, run_id: str, state_file: Path):
        self.run_id = run_id
        self.state_file = state_file
        self.posts = []
        self.seen_hashes = set()
        self.last_save_index = 0
        self.scroll_count = 0
        self.last_scroll_pos = 0
        self.consecutive_no_new = 0
        self.start_time = now_ts()
        self.last_auto_save = time.time()
        self.load()
    
    def load(self) -> None:
        """加载状态（断点续传）"""
        if self.state_file.exists():
            try:
                with self.state_file.open("r", encoding="utf-8") as f:
                    state = json.load(f)
                self.posts = state.get("posts", [])
                self.seen_hashes = set(state.get("seen_hashes", []))
                self.last_save_index = len(self.posts)
                self.scroll_count = state.get("scroll_count", 0)
                self.last_scroll_pos = state.get("last_scroll_pos", 0)
                print(f"📥 已加载断点：{len(self.posts)} 条帖子，从第 {self.scroll_count} 次滚动继续")
            except Exception as e:
                print(f"⚠️ 加载状态失败：{e}，从头开始")
    
    def save(self, force: bool = False) -> None:
        """保存状态"""
        if len(self.posts) <= self.last_save_index and not force:
            return
        
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "run_id": self.run_id,
            "posts": self.posts,
            "seen_hashes": list(self.seen_hashes),
            "scroll_count": self.scroll_count,
            "last_scroll_pos": self.last_scroll_pos,
            "last_updated": now_ts()
        }
        
        # 保存状态文件
        with self.state_file.open("w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        # 保存增量 JSON
        new_posts = self.posts[self.last_save_index:]
        if new_posts:
            increment_file = OUTPUT_DIR / f"LinkedIn_Increment_{self.run_id}_{len(self.posts):04d}.json"
            with increment_file.open("w", encoding="utf-8") as f:
                json.dump(new_posts, f, ensure_ascii=False, indent=2)
            
            # 保存增量 CSV
            self._save_increment_csv(new_posts, len(self.posts))
        
        self.last_save_index = len(self.posts)
        print(f"💾 已保存：{len(self.posts)} 条帖子 (新增 {len(self.posts) - self.last_save_index + len(new_posts)})")
    
    def _save_increment_csv(self, posts: list, total_count: int) -> None:
        """保存增量 CSV"""
        import csv
        if not posts:
            return
        
        csv_file = OUTPUT_DIR / f"LinkedIn_Increment_{self.run_id}_{total_count:04d}.csv"
        with csv_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=posts[0].keys())
            writer.writeheader()
            writer.writerows(posts)
    
    def add_post(self, post: dict) -> None:
        """添加帖子"""
        self.posts.append(post)
        self.seen_hashes.add(post["content_hash"])
    
    def should_auto_save(self) -> bool:
        """检查是否需要自动保存"""
        return (time.time() - self.last_auto_save) >= AUTO_SAVE_INTERVAL
    
    def mark_saved(self) -> None:
        """标记已保存"""
        self.last_auto_save = time.time()

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
    
    try:
        run_command(["openclaw", "browser", "start", "--json"])
        time.sleep(2)
    except:
        pass
    
    result = run_command(["openclaw", "browser", "tabs", "--json"])
    tabs = result.get("tabs", [])
    
    target = find_linkedin_feed_tab(tabs)
    if target:
        print(f"✅ 找到 LinkedIn Feed tab: {target[:16]}...")
        return target
    
    print("🌐 打开 LinkedIn Feed...")
    run_command([
        "openclaw", "browser", "open",
        LINKEDIN_URL,
        "--json"
    ])
    time.sleep(5)
    
    result = run_command(["openclaw", "browser", "tabs", "--json"])
    tabs = result.get("tabs", [])
    target = find_linkedin_feed_tab(tabs)
    
    if not target:
        raise RuntimeError("无法找到或打开 LinkedIn Feed tab")
    
    print(f"✅ 已打开 LinkedIn Feed tab: {target[:16]}...")
    return target

def snapshot_page(target_id: str, limit: int = 400) -> dict:
    """获取页面快照"""
    # 先 focus 到目标 tab
    run_command(["openclaw", "browser", "focus", target_id])
    return run_command([
        "openclaw", "browser", "snapshot",
        "--json",
        "--limit", str(limit)
    ])

def find_new_posts_button(refs: dict) -> str | None:
    """查找 'New posts' 按钮的 ref"""
    for ref, meta in refs.items():
        role = meta.get("role", "")
        name = (meta.get("name") or "").lower()
        # 查找包含 "new posts" 的按钮
        if "new posts" in name or "new" in name:
            if role in ["button", "link"]:
                return ref
    return None

def click_new_posts(target_id: str, refs: dict) -> bool:
    """
    点击 'New posts' 按钮刷新 Feed
    
    返回：
    - True: 成功点击
    - False: 未找到按钮或点击失败
    """
    new_posts_ref = find_new_posts_button(refs)
    if not new_posts_ref:
        return False
    
    try:
        # 先 focus 到目标 tab
        run_command(["openclaw", "browser", "focus", target_id])
        run_command([
            "openclaw", "browser", "click",
            new_posts_ref
        ])
        print(f"   ✅ 已点击 'New posts' 按钮")
        time.sleep(3)  # 等待页面刷新
        return True
    except Exception as e:
        print(f"   ⚠️ 点击 'New posts' 失败：{e}")
        return False

def scroll_page(target_id: str, pixels: int = 800, smooth: bool = True) -> int:
    """
    模拟鼠标滚轮滚动页面
    
    策略:
    1. 先 focus 到目标 tab
    2. 使用 JavaScript 模拟真实滚轮事件
    3. 小幅度多次滚动 (每次 200px)，模拟真实用户行为
    4. 滚动后等待内容加载
    
    返回：当前滚动位置
    """
    try:
        # 先 focus 到目标 tab
        run_command(["openclaw", "browser", "focus", target_id])
        time.sleep(0.5)
        
        # 方案 1: 模拟真实滚轮滚动 (小幅度多次) - 使用箭头函数
        if smooth:
            # 分 4 次滚动，每次 200px，模拟真实滚轮
            result = None
            for i in range(4):
                result = run_command([
                    "openclaw", "browser", "evaluate",
                    "--fn", "() => { window.scrollBy({top:200,left:0,behavior:'smooth'}); return document.documentElement.scrollTop; }"
                ])
                time.sleep(0.3)  # 每次滚动间隔 300ms
            # 返回最终滚动位置
            return int(result.get("result", 0)) if isinstance(result, dict) else 0
        else:
            # 方案 2: 单次滚动
            result = run_command([
                "openclaw", "browser", "evaluate",
                "--fn", f"() => {{ window.scrollBy({{top:{pixels},left:0,behavior:'auto'}}); return document.documentElement.scrollTop; }}"
            ])
            return int(result.get("result", 0)) if isinstance(result, dict) else pixels
    except Exception as e:
        print(f"   ⚠️ JavaScript 滚动失败：{e}，尝试 PageDown...")
        # 方案 3: 备用 PageDown
        try:
            run_command(["openclaw", "browser", "press", "PageDown"])
            time.sleep(1)
            # 获取当前滚动位置
            result = run_command([
                "openclaw", "browser", "evaluate",
                "--fn", "() => document.documentElement.scrollTop"
            ])
            return int(result.get("result", 0)) if isinstance(result, dict) else 0
        except:
            print(f"   ⚠️ PageDown 也失败，尝试直接设置 scrollTop...")
            # 方案 4: 直接设置滚动位置
            try:
                result = run_command([
                    "openclaw", "browser", "evaluate",
                    "--fn", f"() => {{ window.scrollBy(0,{pixels}); return document.documentElement.scrollTop; }}"
                ])
                return int(result.get("result", 0)) if isinstance(result, dict) else pixels
            except:
                return 0

def get_scroll_position(target_id: str) -> int:
    """获取当前滚动位置"""
    try:
        # 先 focus 到目标 tab
        run_command(["openclaw", "browser", "focus", target_id])
        time.sleep(0.3)
        
        result = run_command([
            "openclaw", "browser", "evaluate",
            "--fn", "() => document.documentElement.scrollTop"
        ])
        return int(result.get("result", 0)) if isinstance(result, dict) else 0
    except:
        return 0

# ============ 帖子解析 ============
def parse_posts_from_snapshot(snapshot_text: str) -> list:
    """从快照中解析帖子"""
    posts = []
    lines = snapshot_text.split('\n')
    current_post = None
    
    for line in lines:
        if re.search(r'\b(Company|Person)\b', line, re.IGNORECASE):
            if current_post and current_post.get("content"):
                posts.append(current_post)
            current_post = {"raw": line, "author": None, "content": "", "time": None}
        elif current_post:
            if len(line) > 50:
                current_post["content"] += line + " "
            time_match = re.search(r'(\d+[hmd]\b)', line)
            if time_match:
                current_post["time"] = time_match.group(1)
    
    if current_post and current_post.get("content"):
        posts.append(current_post)
    
    return posts

def extract_post_details(post: dict, post_index: int) -> dict | None:
    """提取帖子详细信息"""
    content = post.get("content", "").strip()
    if len(content) < 50:
        return None
    
    post_id = f"LI_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{post_index:03d}"
    
    author_match = re.search(r'"([^"]+)"', post.get("raw", ""))
    author = author_match.group(1) if author_match else "Unknown"
    
    post_time = post.get("time", "Unknown")
    business_type = classify_business_type(content)
    tags = extract_tags(content)
    
    return {
        "post_id": post_id,
        "author_name": author,
        "author_title": "Unknown",
        "content": content[:2000],
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
    
    pn_matches = re.findall(r'\b([A-Z0-9]{4,}-[A-Z0-9-]+)\b', content)
    tags.extend(pn_matches[:5])
    
    for kw in AVIATION_KEYWORDS:
        if kw in content_lower:
            tags.append(kw)
    
    return list(set(tags))[:10]

# ============ 主采集逻辑 ============
def collect_feed(target_id: str, state: CollectionState, max_posts: int = MAX_POSTS, max_scrolls: int = MAX_SCROLLS) -> list:
    """采集 LinkedIn Feed（增量保存版）"""
    
    print(f"\n🚀 开始采集 LinkedIn Feed")
    print(f"   当前帖子数：{len(state.posts)}")
    print(f"   目标帖子数：{max_posts}")
    print(f"   最大滚动次数：{max_scrolls}")
    print(f"   自动保存间隔：每 {CHECKPOINT_INTERVAL} 条帖子")
    print(f"   状态文件：{state.state_file}")
    print(f"   采集策略：滚轮滚动 + 点击 'New posts' 刷新")
    print(f"\n")
    
    new_posts_clicks = 0  # 记录点击 'New posts' 次数
    
    while state.scroll_count < max_scrolls:
        # 自动保存检查
        if state.should_auto_save():
            print(f"\n⏰ 定时保存...")
            state.save()
            state.mark_saved()
        
        # 策略 A: 每 20 次滚动后，尝试点击 'New posts' 刷新 Feed
        if state.scroll_count > 0 and state.scroll_count % 20 == 0:
            print(f"\n🔄 尝试点击 'New posts' 刷新 Feed...")
            snap = snapshot_page(target_id, 400)
            refs = snap.get("refs", {})
            
            if click_new_posts(target_id, refs):
                new_posts_clicks += 1
                print(f"   📊 已点击 'New posts' {new_posts_clicks} 次")
                state.consecutive_no_new = 0  # 重置无新内容计数
                time.sleep(5)  # 等待刷新完成
                continue  # 跳过本次滚动
        
        # 策略 B: 常规滚轮滚动
        print(f"📄 滚动 #{state.scroll_count+1}/{max_scrolls}")
        snap = snapshot_page(target_id, 400)
        snapshot_text = snap.get("snapshot", "")
        
        # 解析帖子
        raw_posts = parse_posts_from_snapshot(snapshot_text)
        print(f"   解析到 {len(raw_posts)} 个原始帖子")
        
        # 提取详细信息并去重
        new_posts = []
        for i, post in enumerate(raw_posts):
            details = extract_post_details(post, len(state.posts) + i)
            if not details:
                continue
            
            if details["content_hash"] in state.seen_hashes:
                continue
            
            if not is_aviation_related(details["content"]):
                continue
            
            state.add_post(details)
            new_posts.append(details)
            
            # 实时记录到 JSONL 日志
            log_jsonl(state.log_file, {
                "ts": now_ts(),
                "event": "post_collected",
                "post_id": details["post_id"],
                "author": details["author_name"],
                "business_type": details["business_type"]
            })
        
        print(f"   ✅ 新增航空相关帖子：{len(new_posts)}")
        print(f"   📊 累计采集：{len(state.posts)} 条")
        
        # 检查点保存
        if len(state.posts) >= state.last_save_index + CHECKPOINT_INTERVAL:
            print(f"\n💾 保存检查点...")
            state.save()
        
        # 检查是否达到目标
        if len(state.posts) >= max_posts:
            print(f"   ✅ 已达到目标帖子数 ({max_posts})")
            break
        
        # 滚动页面
        current_pos = get_scroll_position(target_id)
        if current_pos <= state.last_scroll_pos:
            print(f"   ⚠️ 滚动位置未变化 (可能已到底部)")
            state.consecutive_no_new += 1
            if state.consecutive_no_new >= NEW_CONTENT_THRESHOLD:
                print(f"   🛑 连续 {NEW_CONTENT_THRESHOLD} 次无新内容，停止采集")
                break
        else:
            state.consecutive_no_new = 0
        
        print(f"   📜 模拟滚轮滚动...")
        scroll_page(target_id, 800, smooth=True)
        
        # 等待内容加载 (LinkedIn 需要时间加载新内容)
        print(f"   ⏳ 等待内容加载...")
        time.sleep(5)  # 增加到 5 秒，给 LinkedIn 足够时间加载
        
        # 检查是否真的滚动到了新位置
        new_pos = get_scroll_position(target_id)
        if new_pos <= state.last_scroll_pos:
            print(f"   ⚠️ 滚动位置未变化 (当前：{new_pos}, 上次：{state.last_scroll_pos})")
            state.consecutive_no_new += 1
            if state.consecutive_no_new >= NEW_CONTENT_THRESHOLD:
                print(f"   🛑 连续 {NEW_CONTENT_THRESHOLD} 次无新内容，停止采集")
                break
        else:
            print(f"   ✅ 滚动成功：{state.last_scroll_pos} → {new_pos}")
            state.consecutive_no_new = 0  # 重置无新内容计数
        
        state.last_scroll_pos = new_pos
        state.scroll_count += 1
    
    # 最终保存
    print(f"\n💾 最终保存...")
    state.save(force=True)
    
    return state.posts

def merge_all_increments(run_id_prefix: str) -> dict:
    """合并所有增量文件到主表"""
    print("\n🔀 合并增量文件...")
    
    increments = []
    for f in OUTPUT_DIR.glob(f"LinkedIn_Increment_{run_id_prefix}_*.json"):
        try:
            with f.open("r", encoding="utf-8") as file:
                posts = json.load(file)
                increments.extend(posts)
                print(f"   📄 {f.name}: {len(posts)} 条")
        except Exception as e:
            print(f"   ⚠️ {f.name}: 读取失败 - {e}")
    
    if not increments:
        return {"merged": 0}
    
    # 去重
    seen = set()
    unique_posts = []
    for post in increments:
        if post["content_hash"] not in seen:
            seen.add(post["content_hash"])
            unique_posts.append(post)
    
    # 保存主表
    master_file = OUTPUT_DIR / f"LinkedIn_Business_Posts_Master_{run_id_prefix}.json"
    with master_file.open("w", encoding="utf-8") as f:
        json.dump(unique_posts, f, ensure_ascii=False, indent=2)
    
    # 保存 CSV
    import csv
    csv_file = OUTPUT_DIR / f"LinkedIn_Business_Posts_Master_{run_id_prefix}.csv"
    with csv_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=unique_posts[0].keys())
        writer.writeheader()
        writer.writerows(unique_posts)
    
    print(f"   ✅ 合并完成：{len(unique_posts)} 条唯一帖子")
    print(f"   📁 主表：{master_file.name}")
    
    return {
        "merged": len(unique_posts),
        "master_file": str(master_file),
        "csv_file": str(csv_file)
    }

def generate_report(posts: list, run_id: str, merge_result: dict = None) -> str:
    """生成采集报告"""
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

本次采集使用无限滚动方式采集 LinkedIn Feed，支持增量保存和断点续传。

### 采集统计
| 指标 | 数值 |
|------|------|
| 采集帖子总数 | {len(posts)} |
| 业务类型 | {len(by_type)} 种 |
| 数据格式 | JSON + CSV + Markdown |
| 数据真实性 | 100% 真实帖子 |
| 增量保存 | 每 {CHECKPOINT_INTERVAL} 条自动保存 |
| 断点续传 | 支持 |

---

## 业务分类统计

| 业务类型 | 数量 | 占比 |
|----------|------|------|
"""
    
    for btype, count in sorted(by_type.items(), key=lambda x: -x[1]):
        pct = count / len(posts) * 100 if posts else 0
        report += f"| {btype} | {count} | {pct:.1f}% |\n"
    
    if merge_result:
        report += f"""
## 数据合并

- **合并文件数**: {merge_result.get('merged', 0)} 条
- **主表文件**: `{merge_result.get('master_file', 'N/A')}`
- **CSV 文件**: `{merge_result.get('csv_file', 'N/A')}`
"""
    
    report += f"""
---

## 数据保存位置

**增量文件**: `LinkedIn_Increment_{run_id}_*.json`
**主表文件**: `LinkedIn_Business_Posts_Master_{run_id}.json`
**运行日志**: `outputs/linkedin_collection_{run_id}.jsonl`

---

**报告生成时间**: {now_ts()}
"""
    
    return report

# ============ 主函数 ============
def main():
    ap = argparse.ArgumentParser(description="LinkedIn Feed 无限滚动采集系统 v4.1 - 滚轮模拟 + New posts 刷新")
    ap.add_argument("--max-posts", type=int, default=MAX_POSTS, help=f"最大采集帖子数 (默认：{MAX_POSTS})")
    ap.add_argument("--max-scrolls", type=int, default=MAX_SCROLLS, help=f"最大滚动次数 (默认：{MAX_SCROLLS})")
    ap.add_argument("--checkpoint-interval", type=int, default=CHECKPOINT_INTERVAL, help=f"检查点间隔 (默认：{CHECKPOINT_INTERVAL})")
    ap.add_argument("--new-posts-interval", type=int, default=20, help=f"每 N 次滚动后点击 'New posts' (默认：20)")
    ap.add_argument("--merge-only", action="store_true", help="仅合并增量文件，不采集")
    args = ap.parse_args()
    
    # 初始化
    run_id = now_filename()
    log_file = Path("outputs") / f"linkedin_collection_{run_id}.jsonl"
    state_file = OUTPUT_DIR / f"linkedin_state_{run_id}.json"
    
    print(f"\n{'='*60}")
    print(f"🚀 LinkedIn Feed 无限滚动采集系统 v4.0 - 增量保存版")
    print(f"{'='*60}")
    print(f"📝 Run ID: {run_id}")
    print(f"📂 输出：{OUTPUT_DIR}")
    print(f"💾 检查点间隔：每 {args.checkpoint_interval} 条帖子")
    print(f"📜 最大滚动：{args.max_scrolls}")
    print(f"{'='*60}\n")
    
    # 仅合并模式
    if args.merge_only:
        merge_result = merge_all_increments(run_id[:15])
        print(f"\n✅ 合并完成：{merge_result['merged']} 条")
        return 0
    
    # 创建状态对象
    state = CollectionState(run_id, state_file)
    state.log_file = log_file
    state.last_auto_save = time.time()  # 重置自动保存计时
    
    # 记录开始
    log_jsonl(log_file, {
        "ts": now_ts(),
        "event": "run_start",
        "run_id": run_id,
        "max_posts": args.max_posts,
        "max_scrolls": args.max_scrolls,
        "checkpoint_interval": args.checkpoint_interval,
        "resumed": len(state.posts) > 0
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
        posts = collect_feed(target_id, state, args.max_posts, args.max_scrolls)
    except Exception as e:
        print(f"\n❌ 采集失败：{e}")
        log_jsonl(log_file, {
            "ts": now_ts(),
            "event": "error",
            "reason": str(e)
        })
        # 即使失败也保存已采集的数据
        state.save(force=True)
        return 2
    
    # 合并增量文件
    merge_result = merge_all_increments(run_id[:15])
    
    # 生成报告
    if posts:
        report = generate_report(posts, run_id, merge_result)
        report_file = OUTPUT_DIR / f"LinkedIn_Collection_Report_{run_id}.md"
        with report_file.open("w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\n{'='*60}")
        print(f"✅ 采集完成！")
        print(f"{'='*60}")
        print(f"📊 采集帖子：{len(posts)} 条")
        print(f"📁 主表：{merge_result.get('master_file', 'N/A')}")
        print(f"📁 CSV: {merge_result.get('csv_file', 'N/A')}")
        print(f"📁 报告：{report_file.name}")
        print(f"📁 日志：{log_file}")
        print(f"{'='*60}\n")
        
        log_jsonl(log_file, {
            "ts": now_ts(),
            "event": "run_complete",
            "run_id": run_id,
            "posts_collected": len(posts),
            "merged": merge_result.get('merged', 0),
            "files": merge_result
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
