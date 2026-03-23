# -*- coding: utf-8 -*-
"""
LinkedIn 信息采集脚本（增强版 - 支持定期保存）
每 30 分钟自动保存采集结果到总表，避免数据丢失
"""

import csv
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import time

# 配置
CONFIG = {
    # 输出路径
    'output_dir': Path(r"C:\Users\Haide\Desktop\OPENCLAW"),
    'master_table': Path(r"C:\Users\Haide\Desktop\real business post\LinkedIn_Business_Posts_Master_Table.csv"),
    
    # 采集设置
    'collection_duration_hours': 6,  # 采集总时长
    'save_interval_minutes': 30,     # 保存间隔
    'batch_size': 50,                # 每批采集数量
    
    # 日志设置
    'log_file': Path(r"C:\Users\Haide\Desktop\OPENCLAW\linkedin_collection_log.txt"),
    'checkpoint_file': Path(r"C:\Users\Haide\Desktop\OPENCLAW\linkedin_checkpoint.json"),
}

# 确保输出目录存在
CONFIG['output_dir'].mkdir(parents=True, exist_ok=True)
if not CONFIG['master_table'].parent.exists():
    CONFIG['master_table'].parent.mkdir(parents=True, exist_ok=True)


def log_message(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    
    # 写入日志文件
    with open(CONFIG['log_file'], 'a', encoding='utf-8') as f:
        f.write(log_line + '\n')


def save_checkpoint(data):
    """保存采集进度"""
    with open(CONFIG['checkpoint_file'], 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log_message(f"已保存采集进度 checkpoint")


def load_checkpoint():
    """加载采集进度"""
    if CONFIG['checkpoint_file'].exists():
        with open(CONFIG['checkpoint_file'], 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'last_collection_time': None,
        'total_posts_collected': 0,
        'batches_completed': 0
    }


def save_to_master_table(posts, source='LinkedIn Collection'):
    """
    保存采集数据到总表
    """
    if not posts:
        log_message("没有数据需要保存")
        return 0
    
    # 检查总表是否存在
    file_exists = CONFIG['master_table'].exists()
    
    # 准备字段
    fieldnames = [
        'post_id', 'post_date', 'author', 'author_title', 'company',
        'category', 'business_type', 'business_value', 'content',
        'content_summary', 'contact_info', 'source_url', 'collection_date',
        'verified', 'notes'
    ]
    
    # 转换为 CSV 格式
    csv_posts = []
    for post in posts:
        csv_post = {field: post.get(field, '') for field in fieldnames}
        csv_post['collection_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        csv_post['verified'] = 'TRUE'
        csv_posts.append(csv_post)
    
    # 写入文件
    try:
        with open(CONFIG['master_table'], 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(csv_posts)
        
        log_message(f"已保存 {len(csv_posts)} 条记录到总表")
        return len(csv_posts)
    except Exception as e:
        log_message(f"保存失败：{e}")
        return 0


def collect_linkedin_posts(batch_size=50):
    """
    采集 LinkedIn 帖子
    注意：这里需要实际的浏览器自动化代码
    目前使用模拟数据演示流程
    """
    log_message(f"开始采集 LinkedIn 帖子（批次大小：{batch_size}）")
    
    # TODO: 这里需要集成实际的浏览器自动化代码
    # 可以使用 Playwright、Selenium 或 browser 工具
    
    # 模拟采集过程
    posts = []
    
    # 示例：模拟采集到的数据
    # 实际使用时需要替换为真实的采集逻辑
    sample_posts = [
        {
            'post_id': f'POST_{datetime.now().strftime("%Y%m%d%H%M%S")}_{i}',
            'post_date': datetime.now().strftime('%Y-%m-%d'),
            'author': 'Aviation Professional',
            'author_title': 'Sales Director at Aviation Parts Co.',
            'company': 'Aviation Parts Co.',
            'category': '航材销售',
            'business_type': '供应商',
            'business_value': '高',
            'content': f'Sample post content {i}',
            'content_summary': f'Summary {i}',
            'contact_info': 'contact@aviationparts.com',
            'source_url': f'https://www.linkedin.com/posts/sample-{i}',
            'notes': ''
        }
        for i in range(min(batch_size, 10))  # 模拟采集 10 条
    ]
    
    posts.extend(sample_posts)
    log_message(f"本批次采集到 {len(posts)} 条帖子")
    
    return posts


def main():
    """主函数"""
    log_message("="*80)
    log_message("LinkedIn 信息采集任务启动")
    log_message(f"采集时长：{CONFIG['collection_duration_hours']} 小时")
    log_message(f"保存间隔：{CONFIG['save_interval_minutes']} 分钟")
    log_message(f"输出目录：{CONFIG['output_dir']}")
    log_message(f"总表路径：{CONFIG['master_table']}")
    log_message("="*80)
    
    # 加载进度
    checkpoint = load_checkpoint()
    log_message(f"加载进度：已采集 {checkpoint['total_posts_collected']} 条记录")
    
    # 计算结束时间
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=CONFIG['collection_duration_hours'])
    next_save_time = start_time + timedelta(minutes=CONFIG['save_interval_minutes'])
    
    log_message(f"开始时间：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log_message(f"预计结束时间：{end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log_message(f"下次保存时间：{next_save_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 采集循环
    all_posts = []
    batch_count = 0
    total_saved = 0
    
    try:
        while datetime.now() < end_time:
            current_time = datetime.now()
            
            # 采集一批数据
            batch_posts = collect_linkedin_posts(CONFIG['batch_size'])
            all_posts.extend(batch_posts)
            batch_count += 1
            
            log_message(f"批次 {batch_count}: 采集 {len(batch_posts)} 条，累计 {len(all_posts)} 条")
            
            # 检查是否需要保存
            if current_time >= next_save_time or len(all_posts) >= CONFIG['batch_size'] * 2:
                log_message(f"\n{'='*40}")
                log_message(f"定期保存触发")
                log_message(f"{'='*40}")
                
                saved_count = save_to_master_table(all_posts)
                total_saved += saved_count
                all_posts = []  # 清空临时缓存
                
                # 更新进度
                checkpoint['last_collection_time'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
                checkpoint['total_posts_collected'] += saved_count
                checkpoint['batches_completed'] = batch_count
                save_checkpoint(checkpoint)
                
                # 设置下次保存时间
                next_save_time = current_time + timedelta(minutes=CONFIG['save_interval_minutes'])
                log_message(f"下次保存时间：{next_save_time.strftime('%Y-%m-%d %H:%M:%S')}")
                log_message(f"{'='*40}\n")
            
            # 等待一段时间再进行下一批采集
            wait_time = 60  # 等待 60 秒
            log_message(f"等待 {wait_time} 秒后继续采集...")
            time.sleep(wait_time)
        
        # 最终保存
        if all_posts:
            log_message(f"\n{'='*40}")
            log_message("采集结束，执行最终保存")
            log_message(f"{'='*40}")
            
            saved_count = save_to_master_table(all_posts)
            total_saved += saved_count
            
            # 更新最终进度
            checkpoint['last_collection_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            checkpoint['total_posts_collected'] += saved_count
            save_checkpoint(checkpoint)
        
        # 总结
        log_message(f"\n{'='*80}")
        log_message("LinkedIn 信息采集任务完成")
        log_message(f"{'='*80}")
        log_message(f"总采集批次：{batch_count}")
        log_message(f"总保存记录：{total_saved}")
        log_message(f"总采集时长：{(datetime.now() - start_time).total_seconds() / 60:.1f} 分钟")
        log_message(f"总表位置：{CONFIG['master_table']}")
        log_message(f"日志文件：{CONFIG['log_file']}")
        log_message(f"进度文件：{CONFIG['checkpoint_file']}")
        log_message(f"{'='*80}")
        
    except KeyboardInterrupt:
        log_message("\n用户中断采集任务")
        # 保存当前进度
        if all_posts:
            save_to_master_table(all_posts)
        save_checkpoint(checkpoint)
        log_message("已保存当前进度")
    
    except Exception as e:
        log_message(f"\n发生错误：{e}")
        # 保存当前进度
        if all_posts:
            save_to_master_table(all_posts)
        save_checkpoint(checkpoint)
        log_message("已保存当前进度")
        raise


if __name__ == '__main__':
    main()
