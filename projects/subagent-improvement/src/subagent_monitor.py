#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sub-Agent 监控工具 - 查询和管理 Sub-Agent 状态
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# ==================== 配置 ====================

WORKSPACE = Path(r"C:\Users\Haide\.openclaw\workspace")
SUBAGENTS_DIR = WORKSPACE / 'subagents'

# ==================== 监控器 ====================

class SubAgentMonitor:
    """Sub-Agent 监控器"""
    
    def __init__(self):
        self.subagents_dir = SUBAGENTS_DIR
    
    def list_all(self, status_filter: str = None) -> List[Dict[str, Any]]:
        """
        列出所有 Sub-Agent
        
        Args:
            status_filter: 状态过滤（running, completed, failed）
        
        Returns:
            Sub-Agent 状态列表
        """
        if not self.subagents_dir.exists():
            return []
        
        agents = []
        
        for run_dir in self.subagents_dir.iterdir():
            if not run_dir.is_dir():
                continue
            
            state_file = run_dir / 'state.json'
            if not state_file.exists():
                continue
            
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # 状态过滤
            if status_filter and state.get('status') != status_filter:
                continue
            
            # 计算运行时长
            start_time = datetime.fromisoformat(state['start_time'])
            end_time_str = state.get('end_time')
            end_time = datetime.fromisoformat(end_time_str) if end_time_str else datetime.now()
            duration = end_time - start_time
            
            agents.append({
                'run_id': state['run_id'],
                'task_name': state['task_name'],
                'status': state['status'],
                'progress': state.get('progress', 0),
                'total_items': state.get('total_items', 0),
                'attempts': state.get('attempt', 0),
                'errors_count': len(state.get('errors', [])),
                'start_time': state['start_time'],
                'end_time': state.get('end_time'),
                'duration_seconds': duration.total_seconds(),
                'log_file': str(run_dir / 'logs' / f"{state['run_id']}.log"),
                'output_dir': str(run_dir / 'output')
            })
        
        # 按开始时间排序（最新的在前）
        agents.sort(key=lambda x: x['start_time'], reverse=True)
        
        return agents
    
    def list_running(self) -> List[Dict[str, Any]]:
        """列出运行中的 Sub-Agent"""
        return self.list_all(status_filter='running')
    
    def list_completed(self) -> List[Dict[str, Any]]:
        """列出已完成的 Sub-Agent"""
        return self.list_all(status_filter='completed')
    
    def list_failed(self) -> List[Dict[str, Any]]:
        """列出已失败的 Sub-Agent"""
        return self.list_all(status_filter='failed')
    
    def get_status(self, run_id: str) -> Dict[str, Any]:
        """
        获取指定 Sub-Agent 状态
        
        Args:
            run_id: 运行 ID
        
        Returns:
            Sub-Agent 状态，不存在返回 None
        """
        agents = self.list_all()
        for agent in agents:
            if agent['run_id'] == run_id:
                return agent
        return None
    
    def get_summary(self) -> Dict[str, Any]:
        """获取 Sub-Agent 运行摘要"""
        all_agents = self.list_all()
        running = self.list_running()
        completed = self.list_completed()
        failed = self.list_failed()
        
        return {
            'total': len(all_agents),
            'running': len(running),
            'completed': len(completed),
            'failed': len(failed),
            'total_errors': sum(a['errors_count'] for a in all_agents),
            'by_status': {
                'running': len(running),
                'completed': len(completed),
                'failed': len(failed),
                'initializing': sum(1 for a in all_agents if a['status'] == 'initializing')
            },
            'recent_agents': all_agents[:10]  # 最近 10 个
        }
    
    def get_logs(self, run_id: str, lines: int = 100) -> List[str]:
        """
        获取指定 Sub-Agent 日志
        
        Args:
            run_id: 运行 ID
            lines: 行数
        
        Returns:
            日志行列表
        """
        agent = self.get_status(run_id)
        if not agent:
            return []
        
        log_file = Path(agent['log_file'])
        if not log_file.exists():
            return []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:]
    
    def get_output_files(self, run_id: str) -> List[str]:
        """
        获取指定 Sub-Agent 输出文件列表
        
        Args:
            run_id: 运行 ID
        
        Returns:
            输出文件路径列表
        """
        agent = self.get_status(run_id)
        if not agent:
            return []
        
        output_dir = Path(agent['output_dir'])
        if not output_dir.exists():
            return []
        
        return [str(f) for f in output_dir.iterdir() if f.is_file()]
    
    def print_dashboard(self):
        """打印监控仪表板"""
        summary = self.get_summary()
        
        print("="*60)
        print("Sub-Agent 监控仪表板")
        print("="*60)
        print(f"总数：{summary['total']}")
        print(f"运行中：{summary['running']}")
        print(f"已完成：{summary['completed']}")
        print(f"失败：{summary['failed']}")
        print(f"总错误数：{summary['total_errors']}")
        print()
        
        if summary['running']:
            print("运行中的 Sub-Agent:")
            print("-"*60)
            for agent in self.list_running():
                progress_pct = (agent['progress'] / max(agent['total_items'], 1)) * 100
                print(f"  {agent['task_name']} ({agent['run_id']})")
                print(f"    进度：{agent['progress']}/{agent['total_items']} ({progress_pct:.1f}%)")
                print(f"    运行时长：{agent['duration_seconds']:.0f}秒")
                print(f"    错误数：{agent['errors_count']}")
                print()
        
        if summary['failed']:
            print("失败的 Sub-Agent:")
            print("-"*60)
            for agent in self.list_failed():
                print(f"  {agent['task_name']} ({agent['run_id']})")
                print(f"    错误数：{agent['errors_count']}")
                print(f"    失败时间：{agent['end_time']}")
                print()
        
        print("="*60)

# ==================== 命令行接口 ====================

def main():
    """命令行接口"""
    import sys
    
    monitor = SubAgentMonitor()
    
    if len(sys.argv) < 2:
        monitor.print_dashboard()
        return
    
    command = sys.argv[1]
    
    if command == 'list':
        status_filter = sys.argv[2] if len(sys.argv) > 2 else None
        agents = monitor.list_all(status_filter)
        for agent in agents:
            print(f"{agent['run_id']} | {agent['task_name']} | {agent['status']} | {agent['progress']}/{agent['total_items']}")
    
    elif command == 'status':
        if len(sys.argv) < 3:
            print("用法：python subagent_monitor.py status <run_id>")
            return
        run_id = sys.argv[2]
        status = monitor.get_status(run_id)
        if status:
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            print(f"未找到 Sub-Agent: {run_id}")
    
    elif command == 'logs':
        if len(sys.argv) < 3:
            print("用法：python subagent_monitor.py logs <run_id> [lines]")
            return
        run_id = sys.argv[2]
        lines = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        logs = monitor.get_logs(run_id, lines)
        for line in logs:
            print(line, end='')
    
    elif command == 'summary':
        summary = monitor.get_summary()
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    else:
        print(f"未知命令：{command}")
        print("可用命令：list, status, logs, summary")

if __name__ == '__main__':
    main()
