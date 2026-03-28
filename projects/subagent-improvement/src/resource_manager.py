#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源管理器 - 管理 Sub-Agent 之间的资源共享和锁机制
避免多个 Sub-Agent 同时访问同一资源导致冲突
"""

import time
import threading
from typing import Dict, Any
from datetime import datetime

# ==================== 锁上下文管理器 ====================

class LockContext:
    """通用的锁上下文管理器"""
    
    def __init__(self, lock, resource_manager, subagent_id, resource):
        self.lock = lock
        self.resource_manager = resource_manager
        self.subagent_id = subagent_id
        self.resource = resource
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()
        self.resource_manager._log_usage(self.subagent_id, self.resource, 'released')
        return False

# ==================== 资源管理器 ====================

class ResourceManager:
    """全局资源管理器 - 单例模式"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 资源锁
        self.browser_lock = threading.Lock()
        self.gmail_lock = threading.Lock()
        self.linkedin_lock = threading.Lock()
        self.stockmarket_lock = threading.Lock()
        
        # 文件锁字典
        self.file_locks = {}
        self.file_locks_lock = threading.Lock()
        
        # 使用日志
        self.usage_log = []
        self.max_log_entries = 1000
        
        self._initialized = True
        print("[ResourceManager] 初始化完成")
    
    # ==================== 浏览器资源 ====================
    
    def acquire_browser(self, subagent_id: str, timeout: int = 300):
        """
        获取浏览器资源（带超时）
        
        Args:
            subagent_id: Sub-Agent ID
            timeout: 超时时间（秒）
        
        Returns:
            LockContext 对象（支持 with 语句）
        
        Raises:
            TimeoutError: 等待超时
        """
        start_time = time.time()
        acquired = self.browser_lock.acquire(timeout=timeout)
        
        if not acquired:
            wait_time = time.time() - start_time
            self._log_usage(subagent_id, 'browser', 'timeout', wait_time)
            raise TimeoutError(f"Sub-Agent {subagent_id} 等待浏览器超时（{timeout}秒）")
        
        wait_time = time.time() - start_time
        self._log_usage(subagent_id, 'browser', 'acquired', wait_time)
        
        return LockContext(self.browser_lock, self, subagent_id, 'browser')
    
    # ==================== Gmail 资源 ====================
    
    def acquire_gmail(self, subagent_id: str, timeout: int = 60):
        """获取 Gmail 资源"""
        start_time = time.time()
        acquired = self.gmail_lock.acquire(timeout=timeout)
        
        if not acquired:
            raise TimeoutError(f"Sub-Agent {subagent_id} 等待 Gmail 资源超时")
        
        self._log_usage(subagent_id, 'gmail', 'acquired', time.time() - start_time)
        return LockContext(self.gmail_lock, self, subagent_id, 'gmail')
    
    # ==================== LinkedIn 资源 ====================
    
    def acquire_linkedin(self, subagent_id: str, timeout: int = 60):
        """获取 LinkedIn 资源"""
        start_time = time.time()
        acquired = self.linkedin_lock.acquire(timeout=timeout)
        
        if not acquired:
            raise TimeoutError(f"Sub-Agent {subagent_id} 等待 LinkedIn 资源超时")
        
        self._log_usage(subagent_id, 'linkedin', 'acquired', time.time() - start_time)
        return LockContext(self.linkedin_lock, self, subagent_id, 'linkedin')
    
    # ==================== StockMarket 资源 ====================
    
    def acquire_stockmarket(self, subagent_id: str, timeout: int = 60):
        """获取 StockMarket 资源"""
        start_time = time.time()
        acquired = self.stockmarket_lock.acquire(timeout=timeout)
        
        if not acquired:
            raise TimeoutError(f"Sub-Agent {subagent_id} 等待 StockMarket 资源超时")
        
        self._log_usage(subagent_id, 'stockmarket', 'acquired', time.time() - start_time)
        return LockContext(self.stockmarket_lock, self, subagent_id, 'stockmarket')
    
    # ==================== 文件锁 ====================
    
    def acquire_file(self, filepath: str, subagent_id: str, timeout: int = 60):
        """
        获取文件锁（避免读写冲突）
        
        Args:
            filepath: 文件路径
            subagent_id: Sub-Agent ID
            timeout: 超时时间（秒）
        
        Returns:
            LockContext 对象（支持 with 语句）
        
        Raises:
            TimeoutError: 等待超时
        """
        filepath = str(filepath)
        
        # 创建文件锁（如果不存在）
        with self.file_locks_lock:
            if filepath not in self.file_locks:
                self.file_locks[filepath] = threading.Lock()
        
        # 获取锁
        acquired = self.file_locks[filepath].acquire(timeout=timeout)
        if not acquired:
            raise TimeoutError(f"Sub-Agent {subagent_id} 等待文件锁超时：{filepath}")
        
        return LockContext(self.file_locks[filepath], self, subagent_id, f'file:{filepath}')
    
    # ==================== 使用日志 ====================
    
    def _log_usage(self, subagent_id: str, resource: str, action: str, duration: float = None):
        """记录资源使用日志"""
        entry = {
            'subagent_id': subagent_id,
            'resource': resource,
            'action': action,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'duration': duration
        }
        self.usage_log.append(entry)
        
        # 限制日志数量
        if len(self.usage_log) > self.max_log_entries:
            self.usage_log = self.usage_log[-self.max_log_entries:]
    
    def get_usage_report(self) -> Dict[str, Any]:
        """获取资源使用报告"""
        # 按资源统计
        resource_stats = {}
        for entry in self.usage_log:
            resource = entry['resource']
            if resource not in resource_stats:
                resource_stats[resource] = {
                    'acquired': 0,
                    'released': 0,
                    'timeout': 0,
                    'total_wait_time': 0
                }
            
            action = entry['action']
            if action in resource_stats[resource]:
                resource_stats[resource][action] += 1
            
            if entry['duration'] is not None:
                resource_stats[resource]['total_wait_time'] += entry['duration']
        
        return {
            'total_entries': len(self.usage_log),
            'resource_stats': resource_stats,
            'recent_usage': self.usage_log[-100:]
        }
    
    def clear_usage_log(self):
        """清空使用日志"""
        self.usage_log = []

# ==================== 全局实例 ====================

# 全局资源管理器实例
resource_manager = ResourceManager()

# ==================== 便捷函数 ====================

def acquire_browser(subagent_id: str, timeout: int = 300):
    """便捷函数：获取浏览器资源"""
    return resource_manager.acquire_browser(subagent_id, timeout)

def acquire_gmail(subagent_id: str, timeout: int = 60):
    """便捷函数：获取 Gmail 资源"""
    return resource_manager.acquire_gmail(subagent_id, timeout)

def acquire_linkedin(subagent_id: str, timeout: int = 60):
    """便捷函数：获取 LinkedIn 资源"""
    return resource_manager.acquire_linkedin(subagent_id, timeout)

def acquire_stockmarket(subagent_id: str, timeout: int = 60):
    """便捷函数：获取 StockMarket 资源"""
    return resource_manager.acquire_stockmarket(subagent_id, timeout)

def acquire_file(filepath: str, subagent_id: str, timeout: int = 60):
    """便捷函数：获取文件锁"""
    return resource_manager.acquire_file(filepath, subagent_id, timeout)

def get_resource_report() -> Dict[str, Any]:
    """便捷函数：获取资源使用报告"""
    return resource_manager.get_usage_report()
