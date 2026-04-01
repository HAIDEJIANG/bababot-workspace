#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# 设置 Chrome 选项，连接到现有浏览器
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# 禁用日志
options.add_argument("--log-level=3")
options.add_argument("--silent")

try:
    print("Connecting to Edge...")
    driver = webdriver.Edge(options=options)
    
    print(f"Current URL: {driver.current_url}")
    print(f"Page title: {driver.title}")
    
    # 等待页面加载
    time.sleep(2)
    
    # 获取页面文本
    body_text = driver.find_element(By.TAG_NAME, "body").text
    print(f"\nBody text length: {len(body_text)}")
    print(f"First 300 chars:\n{body_text[:300]}")
    
    # 查找文章元素
    articles = driver.find_elements(By.TAG_NAME, "article")
    print(f"\nFound {len(articles)} article elements")
    
    for i, article in enumerate(articles[:5]):
        text = article.text[:200]
        print(f"  [{i+1}] {text}...")
    
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
