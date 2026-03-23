#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Browser Config - 浏览器连接配置模块
供 LinkedIn 和 RFQ 脚本使用
"""

import json
from pathlib import Path

WEBTOP_STATE_FILE = Path(__file__).parent / "webtop" / "webtop-state.json"

def get_browser_config():
    """
    获取浏览器连接配置
    
    返回:
        dict: 浏览器配置
            - cdp_endpoint: CDP 连接端点
            - user_data_dir: 用户数据目录
            - is_running: 浏览器是否运行中
    """
    default_config = {
        "cdp_endpoint": "http://localhost:9222",
        "user_data_dir": r"C:\Users\Haide\AppData\Local\OpenClaw\BrowserData",
        "is_running": False,
        "headless": False
    }
    
    if WEBTOP_STATE_FILE.exists():
        try:
            with open(WEBTOP_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            if state.get("status") == "running":
                default_config["is_running"] = True
                default_config["last_check"] = state.get("last_check")
                default_config["started_at"] = state.get("started_at")
        except Exception as e:
            print(f"⚠️ 读取浏览器状态失败：{e}")
    
    return default_config

def create_browser_context(playwright):
    """
    创建浏览器上下文（连接到持久化浏览器）
    
    用法:
        with sync_playwright() as p:
            browser = create_browser_context(p)
            # 使用 browser...
    
    参数:
        playwright: Playwright 实例
    
    返回:
        Browser: 浏览器实例
    """
    config = get_browser_config()
    
    if config["is_running"]:
        # 连接到现有浏览器
        try:
            browser = playwright.chromium.connect_over_cdp(
                config["cdp_endpoint"],
                timeout=10000
            )
            print(f"✅ 已连接到持久化浏览器 (CDP: {config['cdp_endpoint']})")
            return browser
        except Exception as e:
            print(f"⚠️ 连接持久化浏览器失败：{e}")
            print("📝 将使用临时浏览器...")
    
    # 启动新浏览器（带持久化数据目录）
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=config["user_data_dir"],
        headless=config["headless"],
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ],
        timeout=30000
    )
    print(f"✅ 已启动新浏览器（持久化数据：{config['user_data_dir']}）")
    return browser

if __name__ == "__main__":
    # 测试配置
    config = get_browser_config()
    print("浏览器配置:")
    print(json.dumps(config, indent=2, ensure_ascii=False))
