#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Cookie 配置
用于绕过验证墙，采集完整 Profile 数据
"""

# LinkedIn Cookie（li_at）
LINKEDIN_COOKIE = "AQEDARmdEkwBQQxYAAABnS2LN4kAAAGdUZe7iVYAejKFkFL3ivg9Un_wDRran8h7YsbTvLSWbRi1bP5M3aE_gRRPyVG7z7dev0ESzYfutbt9dJ10ItAPIDcJ9OLx4AlecngJh5Kz75d1USjCzRTlnBep"

# 请求头配置
HEADERS = {
    'authority': 'www.linkedin.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.5',
    'cookie': f'li_at={LINKEDIN_COOKIE}',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
}

# 验证 Cookie 是否有效
def validate_cookie():
    """验证 Cookie 有效性"""
    import requests
    
    try:
        response = requests.get(
            'https://www.linkedin.com/feed/',
            headers=HEADERS,
            timeout=10,
            allow_redirects=False
        )
        
        # 如果重定向到登录页面，说明 Cookie 无效
        if response.status_code == 302:
            return False, "Cookie 已过期，需要重新导出"
        
        # 如果返回 200，说明 Cookie 有效
        if response.status_code == 200:
            return True, "Cookie 有效"
        
        return False, f"未知状态：{response.status_code}"
    
    except Exception as e:
        return False, f"验证失败：{str(e)}"

if __name__ == '__main__':
    print("正在验证 LinkedIn Cookie...")
    valid, message = validate_cookie()
    
    if valid:
        print(f"[OK] {message}")
    else:
        print(f"[FAIL] {message}")
        print("\n请重新导出 Cookie：")
        print("1. 打开 Chrome 浏览器")
        print("2. 访问 https://www.linkedin.com")
        print("3. 按 F12 打开开发者工具")
        print("4. Application → Cookies → https://www.linkedin.com")
        print("5. 找到 li_at cookie，复制 Value 值")
