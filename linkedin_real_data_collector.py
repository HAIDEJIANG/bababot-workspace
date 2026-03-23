# LinkedIn真实帖子采集脚本
# 使用OpenClaw browser工具直接浏览LinkedIn采集真实数据

import json
import time
from datetime import datetime
import pandas as pd
import os

class LinkedInRealDataCollector:
    """LinkedIn真实数据采集器 - 使用浏览器自动化"""
    
    def __init__(self):
        self.collected_posts = []
        self.batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def collect_from_browser(self):
        """通过浏览器采集真实LinkedIn帖子"""
        print("开始通过浏览器采集真实LinkedIn帖子...")
        
        # 这里应该使用OpenClaw browser工具
        # 由于当前环境限制，这里提供采集框架
        
        # 实际采集流程：
        # 1. 启动浏览器并登录LinkedIn
        # 2. 导航到航空业务相关群组或搜索页面
        # 3. 滚动页面加载帖子
        # 4. 提取帖子数据
        # 5. 验证数据真实性
        
        print("注意: 需要实际运行OpenClaw browser工具进行采集")
        print("当前提供采集框架和验证逻辑")
        
        # 模拟采集流程（实际应替换为真实浏览器操作）
        self._simulate_collection_process()
        
    def _simulate_collection_process(self):
        """模拟采集流程 - 实际应使用browser工具"""
        print("\n采集流程说明:")
        print("1. 使用 browser action=open 打开 LinkedIn Feed")
        print("2. 使用 browser action=snapshot 获取页面结构")
        print("3. 使用 browser action=evaluate 执行JavaScript提取帖子数据")
        print("4. 验证每个帖子的 source_url 真实性")
        print("5. 保存到CSV文件")
        
        # 这里应该调用实际的browser工具命令
        # 例如:
        # browser action=open targetUrl="https://www.linkedin.com/feed/"
        # browser action=snapshot
        # browser action=evaluate script="提取帖子的JavaScript代码"
        
    def validate_post_data(self, post_data):
        """验证帖子数据真实性"""
        required_fields = ['source_url', 'content', 'author_name']
        
        # 检查必需字段
        for field in required_fields:
            if field not in post_data or not post_data[field]:
                return False, f"缺少必需字段: {field}"
        
        # 验证source_url格式
        source_url = post_data.get('source_url', '')
        if not source_url.startswith('https://www.linkedin.com/'):
            return False, f"无效的LinkedIn URL: {source_url}"
        
        # 验证内容非空
        if not post_data.get('content', '').strip():
            return False, "帖子内容为空"
        
        return True, "验证通过"
    
    def format_post_data(self, raw_post):
        """格式化帖子数据为标准格式"""
        return {
            "post_id": f"LI_REAL_{datetime.now().strftime('%Y%m%d')}_{len(self.collected_posts)+1:03d}",
            "timestamp": datetime.now().isoformat(),
            "author_name": raw_post.get('author', 'Unknown'),
            "company": raw_post.get('company', ''),
            "position": raw_post.get('position', ''),
            "content": raw_post.get('content', ''),
            "business_type": self._classify_business_type(raw_post.get('content', '')),
            "business_value_score": self._calculate_business_score(raw_post.get('content', '')),
            "urgency": self._determine_urgency(raw_post.get('content', '')),
            "has_contact": self._has_contact_info(raw_post.get('content', '')),
            "contact_info": self._extract_contact_info(raw_post.get('content', '')),
            "post_time": raw_post.get('time', ''),
            "reactions": raw_post.get('reactions', 0),
            "comments": raw_post.get('comments', 0),
            "reposts": raw_post.get('reposts', 0),
            "has_image": raw_post.get('has_image', False),
            "image_content": raw_post.get('image_content', ''),
            "source_url": raw_post.get('url', ''),
            "_source_file": f"linkedin_real_collection_{self.batch_id}.csv",
            "author_url": raw_post.get('author_url', ''),
            "posted_time": raw_post.get('posted_time', ''),
            "content_summary": raw_post.get('content', '')[:200],
            "is_repost": raw_post.get('is_repost', False),
            "original_author": raw_post.get('original_author', ''),
            "category": "航空",
            "aircraft_type": self._extract_aircraft_type(raw_post.get('content', '')),
            "batch_id": self.batch_id,
            "author_title": raw_post.get('author_title', ''),
            "content_type": "LinkedIn Post",
            "tags": self._extract_tags(raw_post.get('content', '')),
            "post_number": len(self.collected_posts) + 1,
            "author_profile": raw_post.get('author_url', ''),
            "time_posted": raw_post.get('posted_time', ''),
            "content_preview": raw_post.get('content', '')[:100],
            "collection_date": datetime.now().strftime('%Y-%m-%d'),
            "collection_batch": self.batch_id
        }
    
    def _classify_business_type(self, content):
        """根据内容分类业务类型"""
        content_lower = content.lower()
        
        business_keywords = {
            '发动机销售/采购': ['cfm56', 'engine', 'motor', 'pw', 'v2500', 'apu'],
            '起落架销售/租赁': ['landing gear', 'landing-gear', 'nlg', 'mlg'],
            '航材销售': ['parts', 'component', 'spare', 'pn ', 'part number'],
            'MRO服务': ['mro', 'maintenance', 'overhaul', 'repair', '检查', '维修'],
            '飞机租赁': ['lease', 'leasing', 'rental', 'charter'],
            '飞机销售': ['sale', 'for sale', 'available', '出售']
        }
        
        for biz_type, keywords in business_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return biz_type
        
        return '航空业务'
    
    def _calculate_business_score(self, content):
        """计算业务价值评分"""
        score = 5  # 基础分
        
        # 根据关键词加分
        high_value_terms = ['cfm56', 'urgent', 'immediate', 'available now', 'for sale']
        medium_value_terms = ['looking for', 'need', 'required', 'searching']
        
        content_lower = content.lower()
        
        for term in high_value_terms:
            if term in content_lower:
                score += 2
        
        for term in medium_value_terms:
            if term in content_lower:
                score += 1
        
        return min(score, 10)  # 最高10分
    
    def _determine_urgency(self, content):
        """确定紧急程度"""
        content_lower = content.lower()
        
        if any(term in content_lower for term in ['urgent', 'immediate', 'asap', '紧急', '急需']):
            return 'High'
        elif any(term in content_lower for term in ['looking for', 'need', 'required']):
            return 'Medium'
        else:
            return 'Low'
    
    def _has_contact_info(self, content):
        """检查是否有联系信息"""
        content_lower = content.lower()
        contact_indicators = ['contact', 'email', 'dm', 'message', 'call', 'whatsapp', 'wechat']
        return any(indicator in content_lower for indicator in contact_indicators)
    
    def _extract_contact_info(self, content):
        """提取联系信息"""
        import re
        
        # 提取邮箱
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)
        if emails:
            return emails[0]
        
        # 检查是否有DM指示
        if any(term in content.lower() for term in ['dm me', 'send dm', 'direct message']):
            return 'DM on LinkedIn'
        
        return ''
    
    def _extract_aircraft_type(self, content):
        """提取飞机类型"""
        content_lower = content.lower()
        
        aircraft_types = {
            'A320': ['a320', 'a321', 'a319'],
            'B737': ['737', 'b737'],
            'B747': ['747', 'b747'],
            'B777': ['777', 'b777'],
            'B787': ['787', 'b787'],
            'ATR': ['atr'],
            'Embraer': ['embraer', 'e-jets']
        }
        
        for aircraft, keywords in aircraft_types.items():
            if any(keyword in content_lower for keyword in keywords):
                return aircraft
        
        return ''
    
    def _extract_tags(self, content):
        """提取标签"""
        tags = []
        content_lower = content.lower()
        
        if 'cfm56' in content_lower:
            tags.append('CFM56')
        if 'engine' in content_lower:
            tags.append('Engine')
        if 'parts' in content_lower:
            tags.append('Parts')
        if 'mro' in content_lower:
            tags.append('MRO')
        
        return ', '.join(tags)
    
    def save_to_csv(self, filename):
        """保存到CSV文件"""
        if not self.collected_posts:
            print("没有采集到数据，无法保存")
            return
        
        df = pd.DataFrame(self.collected_posts)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"已保存 {len(self.collected_posts)} 条真实数据到: {filename}")
        return df
    
    def merge_to_master_table(self, new_data_df):
        """合并到主表"""
        master_table_path = "C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv"
        
        if not os.path.exists(master_table_path):
            print(f"主表不存在: {master_table_path}")
            return False
        
        try:
            # 读取主表
            master_df = pd.read_csv(master_table_path, encoding='utf-8-sig')
            
            # 确保列名一致
            for col in new_data_df.columns:
                if col not in master_df.columns:
                    master_df[col] = None
            
            # 合并数据
            combined_df = pd.concat([master_df, new_data_df], ignore_index=True)
            
            # 创建备份
            backup_path = master_table_path.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
            master_df.to_csv(backup_path, index=False, encoding='utf-8-sig')
            
            # 保存合并后的主表
            combined_df.to_csv(master_table_path, index=False, encoding='utf-8-sig')
            
            print(f"成功合并到主表")
            print(f"合并前: {len(master_df)} 条记录")
            print(f"新增: {len(new_data_df)} 条记录")
            print(f"合并后: {len(combined_df)} 条记录")
            print(f"备份文件: {backup_path}")
            
            return True
            
        except Exception as e:
            print(f"合并到主表时出错: {str(e)}")
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("LinkedIn真实数据采集系统")
    print("=" * 60)
    
    collector = LinkedInRealDataCollector()
    
    # 采集数据
    collector.collect_from_browser()
    
    # 注意: 这里需要实际运行browser工具来采集真实数据
    # 以下为示例说明
    
    print("\n" + "=" * 60)
    print("实际采集步骤:")
    print("1. 运行以下命令启动浏览器:")
    print('   browser action=open profile=chrome targetUrl="https://www.linkedin.com/feed/"')
    print("\n2. 登录LinkedIn（如果未登录）")
    print("\n3. 搜索航空业务关键词，例如:")
    print('   browser action=act kind=type text="CFM56 engine sale"')
    print("\n4. 提取帖子数据")
    print("\n5. 验证并保存真实数据")
    print("=" * 60)
    
    # 如果采集到真实数据，可以调用:
    # collector.save_to_csv("linkedin_real_posts.csv")
    # collector.merge_to_master_table(df)

if __name__ == "__main__":
    main()
