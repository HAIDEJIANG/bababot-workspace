# LinkedIn 6 小时采集监控脚本
# 功能：监控采集任务状态，失败时自动重启
# 用法：python .\scripts\linkedin-6h-monitor.py

import subprocess
import time
import json
from datetime import datetime, timedelta
import os

CONFIG = {
    "duration_hours": 6,
    "check_interval_minutes": 5,
    "max_failures": 3,
    "log_file": "C:/Users/Haide/Desktop/real business post/linkedin-6h-monitor.log",
    "master_table": "C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv",
    "cron_job": "linkedin-auto-collection"
}

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(CONFIG["log_file"], "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

def check_browser_relay():
    """检查 Browser Relay 是否运行"""
    try:
        result = subprocess.run(
            ["openclaw", "browser", "status"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="C:/Users/Haide/.openclaw/workspace"
        )
        if "running\": true" in result.stdout or "running": true" in result.stdout:
            return True
        return False
    except Exception as e:
        log(f"Browser Relay 检查失败：{e}")
        return False

def check_gateway():
    """检查 Gateway 是否运行"""
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="C:/Users/Haide/.openclaw/workspace"
        )
        if "Listening:" in result.stdout or "RPC probe: ok" in result.stdout:
            return True
        return False
    except Exception as e:
        log(f"Gateway 检查失败：{e}")
        return False

def check_recent_collection():
    """检查最近是否有采集记录"""
    try:
        if not os.path.exists(CONFIG["master_table"]):
            return False
        
        # 检查文件最后修改时间
        mtime = os.path.getmtime(CONFIG["master_table"])
        last_modified = datetime.fromtimestamp(mtime)
        now = datetime.now()
        
        # 如果 40 分钟内没有更新，可能任务卡住了
        if now - last_modified > timedelta(minutes=40):
            return False
        
        return True
    except Exception as e:
        log(f"采集记录检查失败：{e}")
        return False

def restart_browser_relay():
    """重启 Browser Relay"""
    log("尝试重启 Browser Relay...")
    try:
        subprocess.run(
            ["openclaw", "browser", "start", "--profile", "openclaw"],
            timeout=60,
            cwd="C:/Users/Haide/.openclaw/workspace"
        )
        log("Browser Relay 重启完成")
        time.sleep(10)  # 等待启动
        return True
    except Exception as e:
        log(f"Browser Relay 重启失败：{e}")
        return False

def main():
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=CONFIG["duration_hours"])
    failure_count = 0
    
    log("=" * 60)
    log(f"LinkedIn 6 小时采集监控启动")
    log(f"开始时间：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"预计结束：{end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)
    
    while datetime.now() < end_time:
        try:
            remaining = end_time - datetime.now()
            log(f"运行中... 剩余时间：{remaining.seconds // 3600}小时 {(remaining.seconds % 3600) // 60}分钟")
            
            # 检查系统状态
            browser_ok = check_browser_relay()
            gateway_ok = check_gateway()
            collection_ok = check_recent_collection()
            
            log(f"状态检查 - Browser: {'✅' if browser_ok else '❌'}, Gateway: {'✅' if gateway_ok else '❌'}, 采集：{'✅' if collection_ok else '⏳'}")
            
            # 如果关键服务失败，尝试恢复
            if not gateway_ok:
                log("⚠️ Gateway 失败！尝试重启...")
                failure_count += 1
                if failure_count >= CONFIG["max_failures"]:
                    log("❌ 失败次数过多，停止监控")
                    break
            
            if not browser_ok:
                log("⚠️ Browser Relay 失败！尝试重启...")
                restart_browser_relay()
                failure_count += 1
                if failure_count >= CONFIG["max_failures"]:
                    log("❌ 失败次数过多，停止监控")
                    break
            
            # 重置失败计数（如果一切正常）
            if browser_ok and gateway_ok:
                failure_count = 0
            
            # 等待下次检查
            log(f"等待 {CONFIG['check_interval_minutes']} 分钟后再次检查...")
            time.sleep(CONFIG["check_interval_minutes"] * 60)
            
        except KeyboardInterrupt:
            log("用户中断监控")
            break
        except Exception as e:
            log(f"监控循环错误：{e}")
            time.sleep(60)
    
    log("=" * 60)
    log("6 小时采集监控结束")
    log(f"结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)

if __name__ == "__main__":
    main()
