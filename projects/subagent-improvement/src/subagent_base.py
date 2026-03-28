#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sub-Agent 基类 - 提供独立稳定运行的基础功能
特性：
- 独立工作目录
- 资源锁管理
- 错误自动重试
- 状态追踪
- 日志隔离
"""

import os
import sys
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# ==================== 配置 ====================

WORKSPACE = Path(r"C:\Users\Haide\.openclaw\workspace")
SUBAGENTS_DIR = WORKSPACE / 'subagents'

# ==================== 资源管理器 ====================

class ResourceManager:
    """全局资源管理器 - 避免多个 Sub-Agent 资源冲突"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        import threading
        
        # 资源锁
        self.browser_lock = threading.Lock()
        self.gmail_lock = threading.Lock()
        self.linkedin_lock = threading.Lock()
        self.file_locks = {}
        self.file_locks_lock = threading.Lock()
        
        # 使用日志
        self.usage_log = []
        self._initialized = True
    
    def acquire_browser(self, subagent_id: str, timeout: int = 300):
        """获取浏览器资源（带超时）"""
        import threading
        
        start_time = time.time()
        acquired = self.browser_lock.acquire(timeout=timeout)
        
        if not acquired:
            raise TimeoutError(f"Sub-Agent {subagent_id} 等待浏览器超时（{timeout}秒）")
        
        wait_time = time.time() - start_time
        self._log_usage(subagent_id, 'browser', 'acquired', wait_time)
        
        try:
            yield 'browser_session'
        finally:
            self.browser_lock.release()
            self._log_usage(subagent_id, 'browser', 'released')
    
    def acquire_file(self, filepath: str, subagent_id: str, timeout: int = 60):
        """获取文件锁（避免读写冲突）"""
        import threading
        
        filepath = str(filepath)
        
        with self.file_locks_lock:
            if filepath not in self.file_locks:
                self.file_locks[filepath] = threading.Lock()
        
        acquired = self.file_locks[filepath].acquire(timeout=timeout)
        if not acquired:
            raise TimeoutError(f"Sub-Agent {subagent_id} 等待文件锁超时：{filepath}")
        
        try:
            yield filepath
        finally:
            self.file_locks[filepath].release()
    
    def _log_usage(self, subagent_id: str, resource: str, action: str, duration: float = None):
        """记录资源使用日志"""
        entry = {
            'subagent_id': subagent_id,
            'resource': resource,
            'action': action,
            'timestamp': time.time(),
            'duration': duration
        }
        self.usage_log.append(entry)
        
        # 保留最近 1000 条
        if len(self.usage_log) > 1000:
            self.usage_log = self.usage_log[-1000:]
    
    def get_usage_report(self) -> Dict[str, Any]:
        """获取资源使用报告"""
        return {
            'total_entries': len(self.usage_log),
            'recent_usage': self.usage_log[-100:]
        }

# 全局资源管理器实例
resource_manager = ResourceManager()

# ==================== Sub-Agent 基类 ====================

class SubAgentBase:
    """Sub-Agent 基类 - 所有 Sub-Agent 继承此类"""
    
    def __init__(self, task_name: str, run_id: str = None):
        """
        初始化 Sub-Agent
        
        Args:
            task_name: 任务名称（用于创建独立工作目录）
            run_id: 运行 ID（默认使用时间戳）
        """
        self.task_name = task_name
        self.run_id = run_id or datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 创建独立工作目录
        self.subagent_dir = SUBAGENTS_DIR / f"run_{self.run_id}_{task_name}"
        self.input_dir = self.subagent_dir / 'input'
        self.output_dir = self.subagent_dir / 'output'
        self.logs_dir = self.subagent_dir / 'logs'
        
        # 确保目录存在
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化状态
        self.state = {
            'run_id': self.run_id,
            'task_name': task_name,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'status': 'initializing',  # initializing, running, completed, failed
            'progress': 0,
            'total_items': 0,
            'errors': [],
            'result': None
        }
        
        # 错误处理配置
        self.max_retries = 3
        self.retry_delay_seconds = 30
        self.timeout_minutes = 120
        
        # 保存初始状态
        self.save_state()
        self.log("Sub-Agent 初始化完成", 'INFO')
    
    # ==================== 状态管理 ====================
    
    def save_state(self):
        """保存运行状态到文件"""
        state_file = self.subagent_dir / 'state.json'
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def load_state(self) -> Dict[str, Any]:
        """加载运行状态"""
        state_file = self.subagent_dir / 'state.json'
        if not state_file.exists():
            return {}
        
        with open(state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_progress(self, current: int, total: int = None):
        """更新进度"""
        self.state['progress'] = current
        if total is not None:
            self.state['total_items'] = total
        self.save_state()
    
    def set_status(self, status: str, result: Any = None):
        """设置状态"""
        self.state['status'] = status
        self.state['end_time'] = datetime.now().isoformat()
        if result is not None:
            self.state['result'] = result
        self.save_state()
    
    # ==================== 日志管理 ====================
    
    def log(self, message: str, level: str = 'INFO'):
        """记录日志到独立日志文件"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] {message}"
        
        # 写入独立日志文件
        log_file = self.logs_dir / f"{self.run_id}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
        
        # 同时输出到控制台
        print(log_line)
    
    def get_logs(self, lines: int = 100) -> list:
        """获取最近日志"""
        log_file = self.logs_dir / f"{self.run_id}.log"
        if not log_file.exists():
            return []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:]
    
    # ==================== 错误处理 ====================
    
    def execute_with_retry(self):
        """带重试的执行"""
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                self.state['status'] = 'running'
                self.state['attempt'] = attempt + 1
                self.save_state()
                
                self.log(f"开始执行（第{attempt + 1}次尝试）", 'INFO')
                result = self.execute()
                
                self.state['status'] = 'completed'
                self.state['result'] = result
                self.save_state()
                
                self.log("执行成功", 'INFO')
                return result
                
            except Exception as e:
                attempt += 1
                last_error = e
                
                error_info = {
                    'attempt': attempt,
                    'error': str(e),
                    'traceback': traceback.format_exc(),
                    'time': datetime.now().isoformat()
                }
                self.state['errors'].append(error_info)
                self.save_state()
                
                self.log(f"执行失败（第{attempt}次）: {e}", 'ERROR')
                
                if attempt < self.max_retries:
                    self.log(f"等待{self.retry_delay_seconds}秒后重试...", 'INFO')
                    time.sleep(self.retry_delay_seconds)
        
        # 所有重试失败
        self.state['status'] = 'failed'
        self.state['last_error'] = str(last_error)
        self.save_state()
        
        self.log(f"所有重试失败（{self.max_retries}次）", 'ERROR')
        raise last_error
    
    def execute(self):
        """
        执行任务（子类必须实现）
        
        Returns:
            执行结果
        """
        raise NotImplementedError("Sub-Agent 必须实现 execute() 方法")
    
    # ==================== 清理 ====================
    
    def cleanup(self, keep_logs: bool = True, keep_output: bool = True):
        """
        清理工作目录
        
        Args:
            keep_logs: 是否保留日志
            keep_output: 是否保留输出
        """
        try:
            for item in self.subagent_dir.iterdir():
                if keep_logs and item.name == 'logs':
                    continue
                if keep_output and item.name == 'output':
                    continue
                
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    import shutil
                    shutil.rmtree(item)
            
            self.log("工作目录清理完成", 'INFO')
        except Exception as e:
            self.log(f"清理失败：{e}", 'ERROR')
    
    # ==================== 状态查询 ====================
    
    def get_status(self) -> Dict[str, Any]:
        """获取运行状态"""
        return {
            'run_id': self.state['run_id'],
            'task_name': self.state['task_name'],
            'status': self.state['status'],
            'progress': self.state['progress'],
            'total_items': self.state.get('total_items', 0),
            'attempts': self.state.get('attempt', 0),
            'errors_count': len(self.state.get('errors', [])),
            'start_time': self.state['start_time'],
            'end_time': self.state.get('end_time')
        }
    
    def is_completed(self) -> bool:
        """检查是否已完成"""
        return self.state['status'] == 'completed'
    
    def is_failed(self) -> bool:
        """检查是否已失败"""
        return self.state['status'] == 'failed'
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.state['status'] == 'running'
