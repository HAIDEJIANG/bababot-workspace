#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础架构测试 - 验证 Sub-Agent 基类、资源管理器、监控工具
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from subagent_base import SubAgentBase, resource_manager
from subagent_monitor import SubAgentMonitor

# ==================== 测试 Sub-Agent 基类 ====================

class TestSubAgent(SubAgentBase):
    """测试 Sub-Agent"""
    
    def __init__(self):
        super().__init__('test_task')
        self.max_retries = 2
        self.retry_delay_seconds = 5
    
    def execute(self):
        """执行测试任务"""
        self.log("测试开始...", 'INFO')
        
        # 测试进度更新
        for i in range(1, 11):
            self.update_progress(i, 10)
            self.log(f"进度：{i}/10", 'INFO')
            time.sleep(0.5)
        
        # 测试文件输出
        output_file = self.output_dir / 'test_output.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("测试输出\n")
            f.write(f"运行 ID: {self.run_id}\n")
            f.write(f"任务名称：{self.task_name}\n")
        
        self.log(f"输出文件已保存：{output_file}", 'INFO')
        
        return {
            'status': 'success',
            'output_file': str(output_file),
            'progress': self.state['progress']
        }

# ==================== 测试资源管理器 ====================

def test_resource_manager():
    """测试资源管理器"""
    print("\n" + "="*60)
    print("测试资源管理器")
    print("="*60)
    
    # 测试浏览器锁
    print("\n测试浏览器锁...")
    try:
        browser_lock = resource_manager.acquire_browser('test_agent', timeout=10)
        with browser_lock:
            print("  [OK] 浏览器锁获取成功")
            time.sleep(1)
        print("  [OK] 浏览器锁释放成功")
    except Exception as e:
        print(f"  [FAIL] 浏览器锁测试失败：{e}")
        return False
    
    # 测试文件锁
    print("\n测试文件锁...")
    test_file = Path(r"C:\Users\Haide\.openclaw\workspace\projects\subagent-improvement\tests\test_lock.txt")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        file_lock = resource_manager.acquire_file(str(test_file), 'test_agent', timeout=10)
        with file_lock:
            print("  [OK] 文件锁获取成功")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("测试文件锁\n")
            time.sleep(1)
        print("  [OK] 文件锁释放成功")
    except Exception as e:
        print(f"  [FAIL] 文件锁测试失败：{e}")
        return False
    
    # 测试资源使用报告
    print("\n测试资源使用报告...")
    report = resource_manager.get_usage_report()
    print(f"  [OK] 总日志条目：{report['total_entries']}")
    print(f"  [OK] 资源统计：{len(report['resource_stats'])} 种资源")
    
    return True

# ==================== 测试监控工具 ====================

def test_monitor():
    """测试监控工具"""
    print("\n" + "="*60)
    print("测试监控工具")
    print("="*60)
    
    monitor = SubAgentMonitor()
    
    # 测试状态查询
    print("\n测试状态查询...")
    agents = monitor.list_all()
    print(f"  [OK] 找到 {len(agents)} 个 Sub-Agent")
    
    # 测试摘要
    print("\n测试摘要...")
    summary = monitor.get_summary()
    print(f"  [OK] 总数：{summary['total']}")
    print(f"  [OK] 运行中：{summary['running']}")
    print(f"  [OK] 已完成：{summary['completed']}")
    print(f"  [OK] 失败：{summary['failed']}")
    
    # 测试仪表板
    print("\n测试仪表板...")
    monitor.print_dashboard()
    
    return True

# ==================== 主测试流程 ====================

def main():
    """主测试流程"""
    print("="*60)
    print("Sub-Agent 基础架构测试")
    print("="*60)
    
    all_passed = True
    
    # 测试 1：Sub-Agent 基类
    print("\n" + "="*60)
    print("测试 1：Sub-Agent 基类")
    print("="*60)
    
    try:
        agent = TestSubAgent()
        print(f"[OK] Sub-Agent 初始化成功")
        print(f"   运行 ID: {agent.run_id}")
        print(f"   工作目录：{agent.subagent_dir}")
        
        result = agent.execute_with_retry()
        print(f"[OK] Sub-Agent 执行成功")
        print(f"   结果：{result}")
        print(f"   最终状态：{agent.state['status']}")
        print(f"   进度：{agent.state['progress']}/{agent.state.get('total_items', 0)}")
        
    except Exception as e:
        print(f"[FAIL] Sub-Agent 测试失败：{e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # 测试 2：资源管理器
    if not test_resource_manager():
        all_passed = False
    
    # 测试 3：监控工具
    if not test_monitor():
        all_passed = False
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    if all_passed:
        print("[OK] 所有测试通过！")
        print("\n基础架构已准备就绪，可以开始使用 Sub-Agent。")
    else:
        print("[FAIL] 部分测试失败，请检查错误信息。")
        sys.exit(1)
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
