#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 批量采集 - 简化版
直接访问每个公司页面并保存快照
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COMPANIES = [
    {"name": "StandardAero", "url": "https://www.linkedin.com/company/standardaero/posts/"},
    {"name": "GA Telesis", "url": "https://www.linkedin.com/company/gatelesis/posts/"},
    {"name": "Textron Aviation", "url": "https://www.linkedin.com/company/textron-aviation/posts/"},
    {"name": "Lufthansa Technik", "url": "https://www.linkedin.com/company/lufthansa-technik/posts/"},
    {"name": "Rolls-Royce", "url": "https://www.linkedin.com/company/rolls-royce/posts/"},
    {"name": "GE Aerospace", "url": "https://www.linkedin.com/company/ge-aerospace/posts/"},
    {"name": "Honeywell Aerospace", "url": "https://www.linkedin.com/company/honeywell-aerospace/posts/"},
    {"name": "Pratt & Whitney", "url": "https://www.linkedin.com/company/pratt-whitney/posts/"},
    {"name": "Safran", "url": "https://www.linkedin.com/company/safran/posts/"},
    {"name": "Airbus", "url": "https://www.linkedin.com/company/airbus/posts/"},
]

def run_cmd(cmd):
    """执行命令并返回 JSON"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding='utf-8', errors='replace', timeout=90)
        # 尝试从输出中提取 JSON
        output = result.stdout.strip()
        # 查找第一个 { 和最后一个 }
        start = output.find('{')
        end = output.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = output[start:end]
            return json.loads(json_str)
        return {}
    except Exception as e:
        print(f"  命令错误：{e}")
        return {}

def main():
    print("=" * 60)
    print("LinkedIn 批量采集 - 简化版")
    print("=" * 60)
    
    batch_id = datetime.now().strftime("%Y%m%d_%H%M")
    
    for i, company in enumerate(COMPANIES, 1):
        print(f"\n[{i}/{len(COMPANIES)}] {company['name']}")
        
        # 打开页面
        print(f"  打开：{company['url']}")
        result = run_cmd(f'openclaw browser open "{company["url"]}" --json')
        target_id = result.get('targetId')
        
        if not target_id:
            print(f"  [ERR] 无法打开页面")
            continue
        
        # 等待加载
        print("  等待加载...")
        time.sleep(8)
        
        # 获取快照
        print("  获取快照...")
        snapshot_result = run_cmd(f'openclaw browser snapshot --target-id {target_id} --format ai --limit 800 --json')
        snapshot = snapshot_result.get('snapshot', '')
        
        if snapshot:
            # 保存快照
            safe_name = company['name'].replace(' ', '_').replace('&', 'and')
            snapshot_file = OUTPUT_DIR / f"snapshot_{safe_name}_{batch_id}.json"
            
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'company': company['name'],
                    'url': company['url'],
                    'snapshot': snapshot,
                    'timestamp': datetime.now().isoformat()
                }, f, ensure_ascii=False)
            
            print(f"  [OK] 快照已保存：{snapshot_file.name}")
        else:
            print(f"  [WARN] 快照为空")
        
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print("批量采集完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
