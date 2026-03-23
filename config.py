# -*- coding: utf-8 -*-
"""
OpenClaw 工作区配置模块
集中管理所有路径和配置设置
"""

import os
from pathlib import Path

# 基础路径
WORKSPACE_ROOT = Path(r"C:\Users\Haide\.openclaw\workspace")

# 默认文件保存路径（桌面/OPENCLAW）
DEFAULT_OUTPUT_DIR = Path(r"C:\Users\Haide\Desktop\OPENCLAW")

# 确保输出目录存在
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# LinkedIn 相关路径
LINKEDIN_DIR = Path(r"C:\Users\Haide\Desktop\LINKEDIN")
LINKEDIN_MASTER_TABLE = DEFAULT_OUTPUT_DIR / "LinkedIn_Business_Posts_Master_Table.csv"

# 邮件相关路径
EMAIL_OUTPUT_DIR = DEFAULT_OUTPUT_DIR
EMAIL_SUMMARY_FILE = DEFAULT_OUTPUT_DIR / "邮箱收件箱汇总_2026-01-01_至今.csv"

# RFQ 相关路径
RFQ_OUTPUT_DIR = DEFAULT_OUTPUT_DIR
RFQ_MATCH_RESULT = RFQ_OUTPUT_DIR / "RFQ 报价匹配分析结果.csv"
RFQ_BEST_QUOTE = RFQ_OUTPUT_DIR / "RFQ 最优报价推荐.csv"

# 客户需求相关路径
CUSTOMER_OUTPUT_DIR = DEFAULT_OUTPUT_DIR
CUSTOMER_REQUIREMENTS_FILE = CUSTOMER_OUTPUT_DIR / "客户需求清单.csv"

# 供应商报价相关路径
SUPPLIER_OUTPUT_DIR = DEFAULT_OUTPUT_DIR
SUPPLIER_QUOTE_FILE = SUPPLIER_OUTPUT_DIR / "航材供应商报价汇总_2026-03-01_至今.csv"

# Blue Sky Technics 相关路径
BLUE_SKY_OUTPUT_DIR = DEFAULT_OUTPUT_DIR
BLUE_SKY_REQUIREMENTS_FILE = BLUE_SKY_OUTPUT_DIR / "Blue_Sky_Technics_Requirements.csv"
BLUE_SKY_FULL_ANALYSIS = BLUE_SKY_OUTPUT_DIR / "Blue_Sky_Full_Analysis.csv"

# Initial/Turbo 相关路径
INITIAL_TURBO_OUTPUT_DIR = DEFAULT_OUTPUT_DIR
INITIAL_TURBO_ANALYSIS_FILE = INITIAL_TURBO_OUTPUT_DIR / "Initial_Turbo_Full_Analysis.csv"
INITIAL_TURBO_SUMMARY_FILE = INITIAL_TURBO_OUTPUT_DIR / "Initial_Turbo_Summary.csv"

# 内存压缩相关路径
MEMORY_DIR = WORKSPACE_ROOT / "memory"
MEMORY_COMPRESSOR_SCRIPT = WORKSPACE_ROOT / "claw-compactor" / "scripts" / "heartbeat_batch.py"

# 脚本路径
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"
LINKEDIN_SCRIPTS_DIR = SCRIPTS_DIR / "linkedin"
RFQ_SCRIPTS_DIR = SCRIPTS_DIR / "rfq_auto"

# 技能路径
SKILLS_DIR = WORKSPACE_ROOT / "skills"

# 模型配置
DEFAULT_MODEL = "bailian/qwen3.5-plus"
FALLBACK_MODELS = [
    "bailian/qwen3-max-2026-01-23",
    "bailian/qwen3-coder-next",
    "bailian/qwen3-coder-plus",
    "bailian/MiniMax-M2.5",
    "bailian/glm-5",
    "bailian/glm-4.7",
    "bailian/kimi-k2.5",
    # OpenRouter 模型
    "openrouter/stepfun/step-3.5-flash:free",
    "openrouter/hunter-alpha"
]

# OpenRouter 配置
OPENROUTER_CONFIG = {
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": "sk-sp-1f8c48b5b0694d2894971833793c5f55",
    "models": {
        "step-3.5-flash": "stepfun/step-3.5-flash:free",
        "hunter-alpha": "hunter-alpha"
    }
}

# IMAP 配置
IMAP_CONFIG = {
    "server": "imaphz.qiye.163.com",
    "port": 993,
    "username": "sale@aeroedgeglobal.com",
    # 密码需要从安全存储获取，不建议硬编码
}

# 输出文件编码
OUTPUT_ENCODING = "utf-8-sig"  # Excel 兼容的 UTF-8


def get_output_path(filename: str, subdir: str = None) -> Path:
    """
    获取输出文件的完整路径
    
    Args:
        filename: 文件名
        subdir: 子目录名（可选）
    
    Returns:
        完整的文件路径
    """
    if subdir:
        output_dir = DEFAULT_OUTPUT_DIR / subdir
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / filename
    return DEFAULT_OUTPUT_DIR / filename


def get_workspace_path(relative_path: str) -> Path:
    """
    获取工作区内文件的完整路径
    
    Args:
        relative_path: 相对于工作区根目录的路径
    
    Returns:
        完整的文件路径
    """
    return WORKSPACE_ROOT / relative_path


# 打印配置信息（调试用）
if __name__ == "__main__":
    print("="*60)
    print("OpenClaw 配置信息")
    print("="*60)
    print(f"工作区根目录：{WORKSPACE_ROOT}")
    print(f"默认输出目录：{DEFAULT_OUTPUT_DIR}")
    print(f"LinkedIn 目录：{LINKEDIN_DIR}")
    print(f"邮件输出目录：{EMAIL_OUTPUT_DIR}")
    print(f"RFQ 输出目录：{RFQ_OUTPUT_DIR}")
    print(f"客户需求输出目录：{CUSTOMER_OUTPUT_DIR}")
    print(f"供应商报价输出目录：{SUPPLIER_OUTPUT_DIR}")
    print(f"Blue Sky 输出目录：{BLUE_SKY_OUTPUT_DIR}")
    print(f"Initial/Turbo 输出目录：{INITIAL_TURBO_OUTPUT_DIR}")
    print(f"内存目录：{MEMORY_DIR}")
    print(f"脚本目录：{SCRIPTS_DIR}")
    print(f"技能目录：{SKILLS_DIR}")
    print(f"默认模型：{DEFAULT_MODEL}")
    print("="*60)
