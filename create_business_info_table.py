#!/usr/bin/env python3
"""
创建业务信息表 - 基于bababot方法
整合LinkedIn帖子采集和业务信息提取，生成可直接使用的业务信息表
"""

import json
import csv
import os
from datetime import datetime
import re
from pathlib import Path

class BusinessPostAnalyzer:
    """业务帖子分析器 - 基于bababot方法"""
    
    def __init__(self):
        # 业务关键词定义
        self.business_keywords = {
            "航材": ["航材", "航空材料", "航空零件", "飞机零件", "航空部件", "spare parts", "aviation parts", "aircraft parts"],
            "发动机": ["发动机", "引擎", "engine", "CFM56", "LEAP", "V2500", "PW1000G", "GE90", "Trent", "CF34", "CF6"],
            "起落架": ["起落架", "landing gear", "LG", "MLG", "NLG", "landing gear system"],
            "飞机整机": ["飞机整机", "整机", "aircraft", "飞机", "airplane", "A320", "A321", "B737", "B777", "A330", "A350"],
            "APU": ["APU", "辅助动力装置", "GTCP", "auxiliary power unit"],
            "航电": ["航电", "avionics", "航空电子", "cockpit", "flight deck"],
            "MRO服务": ["MRO", "维修", "overhaul", "maintenance", "repair", "大修", "检修"]
        }
        
        # 业务意图关键词
        self.intent_keywords = [
            # 采购需求
            "采购", "购买", "需要", "求购", "寻找", "looking for", "wanted", "need", "require", "seeking",
            # 销售信息
            "出售", "销售", "供应", "提供", "available", "for sale", "sale", "sell", "supply",
            # 询价/报价
            "询价", "报价", "RFQ", "quotation", "price", "报价单", "价格",
            # 库存信息
            "库存", "现货", "stock", "inventory", "available stock", "ready stock",
            # 具体业务信息
            "PN", "Part Number", "件号", "S/N", "Serial Number", "序列号", "批号",
            "USD", "美元", "价格", "contact", "联系方式", "WhatsApp", "微信", "email", "邮箱",
            "condition", "状态", "new", "used", "overhauled", "as removed", "serviceable"
        ]
        
        # 排除关键词
        self.exclude_keywords = [
            "新闻", "news", "announcement", "公告", "会议", "conference", "summit", "峰会",
            "招聘", "hiring", "recruiting", "job", "职位", "career", "vacancy",
            "庆祝", "celebrating", "congratulations", "恭喜", "happy to announce",
            "行业动态", "趋势", "trend", "analysis", "报告", "report"
        ]
    
    def is_business_post(self, content):
        """判断是否为业务帖子"""
        content_lower = content.lower()
        
        # 排除非业务内容
        for exclude in self.exclude_keywords:
            if exclude.lower() in content_lower:
                return False
        
        # 检查是否包含业务关键词
        has_business_keyword = False
        for biz_type, keywords in self.business_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    has_business_keyword = True
                    break
            if has_business_keyword:
                break
        
        if not has_business_keyword:
            return False
        
        # 检查是否包含业务意图
        has_business_intent = False
        for intent in self.intent_keywords:
            if intent.lower() in content_lower:
                has_business_intent = True
                break
        
        return has_business_intent
    
    def extract_business_info(self, content):
        """从帖子内容中提取业务信息"""
        business_info = {
            "业务类型": [],
            "具体需求": "",
            "产品型号": [],
            "价格信息": "",
            "联系方式": [],
            "库存状态": "",
            "紧急程度": "普通",
            "业务价值评分": 1
        }
        
        content_lower = content.lower()
        
        # 识别业务类型
        for biz_type, keywords in self.business_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    if biz_type not in business_info["业务类型"]:
                        business_info["业务类型"].append(biz_type)
        
        # 识别具体需求
        intent_found = []
        for intent in self.intent_keywords:
            if intent.lower() in content_lower:
                intent_found.append(intent)
        
        if intent_found:
            business_info["具体需求"] = ", ".join(intent_found[:3])
        
        # 提取产品型号
        pn_patterns = [
            r'PN[:\s]*([A-Z0-9\-]+)',
            r'Part\s*Number[:\s]*([A-Z0-9\-]+)',
            r'件号[:\s]*([A-Z0-9\-]+)',
            r'([A-Z][A-Z0-9\-]{5,})'
        ]
        
        for pattern in pn_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match not in business_info["产品型号"]:
                    business_info["产品型号"].append(match)
        
        # 提取价格信息
        price_patterns = [
            r'USD\s*([\d,]+\.?\d*)',
            r'\$([\d,]+\.?\d*)',
            r'价格[:\s]*([\d,]+\.?\d*)',
            r'报价[:\s]*([\d,]+\.?\d*)'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, content)
            if matches:
                business_info["价格信息"] = f"USD {matches[0]}"
                break
        
        # 提取联系方式
        contact_patterns = [
            r'WhatsApp[:\s]*([+\d\s\-]+)',
            r'微信[:\s]*([a-zA-Z0-9_\-]+)',
            r'Email[:\s]*([\w\.\-]+@[\w\.\-]+\.\w+)',
            r'邮箱[:\s]*([\w\.\-]+@[\w\.\-]+\.\w+)',
            r'contact[:\s]*([\w\.\-]+@[\w\.\-]+\.\w+)'
        ]
        
        for pattern in contact_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            business_info["联系方式"].extend(matches)
        
        # 识别库存状态
        stock_keywords = ["库存", "现货", "stock", "available", "ready"]
        for keyword in stock_keywords:
            if keyword.lower() in content_lower:
                business_info["库存状态"] = "有现货"
                break
        
        # 识别紧急程度
        urgent_keywords = ["紧急", "urgent", "asap", "immediate", "急需"]
        for keyword in urgent_keywords:
            if keyword.lower() in content_lower:
                business_info["紧急程度"] = "紧急"
                break
        
        # 计算业务价值评分
        business_info["业务价值评分"] = self.calculate_business_score(business_info)
        
        return business_info
    
    def calculate_business_score(self, business_info):
        """计算业务价值评分 (1-5分)"""
        score = 1
        
        if business_info["价格信息"]:
            score += 1
        if business_info["联系方式"]:
            score += 1
        if business_info["产品型号"]:
            score += 1
        if business_info["库存状态"] == "有现货":
            score += 1
        if business_info["紧急程度"] == "紧急":
            score += 1
        
        return min(score, 5)  # 最高5分
    
    def generate_followup_suggestion(self, business_info):
        """生成跟进建议"""
        specific_demand = business_info.get("具体需求", "").lower()
        
        if "采购" in specific_demand or "looking for" in specific_demand:
            return "主动联系提供报价"
        elif "出售" in specific_demand or "for sale" in specific_demand:
            return "询价了解详情"
        elif business_info.get("紧急程度") == "紧急":
            return "立即联系，高优先级"
        else:
            return "常规跟进，建立联系"

class BusinessInfoTableCreator:
    """业务信息表创建器"""
    
    def __init__(self):
        self.analyzer = BusinessPostAnalyzer()
        self.output_dir = Path("LinkedIn_Business_Info")
        self.output_dir.mkdir(exist_ok=True)
    
    def create_table_from_posts(self, posts_data, source="linkedin_feed"):
        """从帖子数据创建业务信息表"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 字段定义
        fieldnames = [
            "ID",
            "采集时间",
            "数据来源",
            "发帖人",
            "公司/职位",
            "帖子内容摘要",
            "帖子链接",
            "发帖时间",
            "业务类型",
            "具体需求",
            "产品型号",
            "价格信息",
            "联系方式",
            "库存状态",
            "紧急程度",
            "业务价值评分",
            "跟进建议",
            "跟进状态",
            "备注"
        ]
        
        business_posts = []
        
        for idx, post in enumerate(posts_data, 1):
            content = post.get("content", "")
            
            if self.analyzer.is_business_post(content):
                business_info = self.analyzer.extract_business_info(content)
                followup_suggestion = self.analyzer.generate_followup_suggestion(business_info)
                
                business_post = {
                    "ID": f"BI{timestamp}_{idx:03d}",
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "数据来源": source,
                    "发帖人": post.get("author", "未知"),
                    "公司/职位": post.get("company", "未知"),
                    "帖子内容摘要": content[:300] + ("..." if len(content) > 300 else ""),
                    "帖子链接": post.get("url", ""),
                    "发帖时间": post.get("time", "未知"),
                    "业务类型": ", ".join(business_info["业务类型"]) if business_info["业务类型"] else "其他",
                    "具体需求": business_info["具体需求"],
                    "产品型号": ", ".join(business_info["产品型号"][:3]) if business_info["产品型号"] else "",
                    "价格信息": business_info["价格信息"],
                    "联系方式": ", ".join(business_info["联系方式"][:3]) if business_info["联系方式"] else "",
                    "库存状态": business_info["库存状态"],
                    "紧急程度": business_info["紧急程度"],
                    "业务价值评分": business_info["业务价值评分"],
                    "跟进建议": followup_suggestion,
                    "跟进状态": "待跟进",
                    "备注": ""
                }
                
                business_posts.append(business_post)
        
        return business_posts
    
    def save_to_files(self, business_posts, base_filename="business_info"):
        """保存到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CSV文件
        csv_filename = f"{base_filename}_{timestamp}.csv"
        csv_path = self.output_dir / csv_filename
        
        if business_posts:
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=business_posts[0].keys())
                writer.writeheader()
                writer.writerows(business_posts)
            
            print(f"✅ 业务信息表已保存: {csv_path}")
            print(f"📊 共 {len(business_posts)} 条业务信息")
        else:
            print("⚠️ 未找到符合条件的业务帖子")
            return None
        
        # JSON文件
        json_filename = f"{base_filename}_{timestamp}.json"
        json_path = self.output_dir / json_filename
        
        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(business_posts, jsonfile, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON数据已保存: {json_path}")
        
        # 生成统计报告
        self.generate_statistics_report(business_posts, timestamp)
        
        return csv_path
    
    def generate_statistics_report(self, business_posts, timestamp):
        """生成统计报告"""
        report = {
            "报告时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "总业务信息数": len(business_posts),
            "业务类型分布": {},
            "紧急程度分布": {},
            "价值评分分布": {},
            "高价值业务信息": [],
            "推荐立即跟进": []
        }
        
        for post in business_posts:
            # 业务类型分布
            biz_types = post["业务类型"].split(", ")
            for biz_type in biz_types:
                if biz_type:
                    report["业务类型分布"][biz_type] = report["业务类型分布"].get(biz_type, 0) + 1
            
            # 紧急程度分布
            urgency = post["紧急程度"]
            report["紧急程度分布"][urgency] = report["紧急程度分布"].get(urgency, 0) + 1
            
            # 价值评分分布
            score = post["业务价值评分"]
            report["价值评分分布"][str(score)] = report["价值评分分布"].get(str(score), 0) + 1
            
            # 高价值业务信息 (评分≥4)
            if score >= 4:
                report["高价值业务信息"].append({
                    "ID": post["ID"],
                    "发帖人": post["发帖人"],
                    "业务类型": post["业务类型"],
                    "具体需求": post["具体需求"],
                    "评分": score
                })
            
            # 推荐立即跟进 (紧急或评分≥4)
            if urgency == "紧急" or score >= 4:
                report["推荐立即跟进"].append({
                    "ID": post["ID"],
                    "发帖人": post["发帖人"],
                    "跟进建议": post["跟进建议"],
                    "联系方式": post["联系方式"]
                })
        
        # 保存报告
        report_filename = f"business_info_report_{timestamp}.json"
        report_path = self.output_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as reportfile:
            json.dump(report, reportfile, ensure_ascii=False, indent=2)
        
        print(f"📈 统计报告已生成: {report_path}")
        
        # 打印摘要
        print("\n📊 业务信息统计摘要:")
        print(f"   总业务信息数: {report['总业务信息数']}")
        print(f"   业务类型分布: {report['业务类型分布']}")
        print(f"   紧急程度分布: {report['紧急程度分布']}")
        print(f"   高价值信息数: {len(report['高价值业务信息'])}")
        print(f"   推荐跟进数: {len(report['推荐立即跟进'])}")
        
        # 生成行动建议
        self.generate_action_recommendations(report)
    
    def generate_action_recommendations(self, report):
        """生成行动建议"""
        print("\n🎯 行动建议:")
        
        if report["推荐立即跟进"]:
            print("   1. 立即跟进以下高优先级业务:")
            for idx, followup in enumerate(report["推荐立即跟进"][:5], 1):
                print(f"      {idx}. {followup['发帖人']} - {followup['跟进建议']}")
        
        # 根据业务类型分布建议
        if "航材" in report["业务类型分布"]:
            print("   2. 航材相关业务较多，可重点跟进")
        if "发动机" in report["业务类型分布"]:
            print("   3. 发动机相关业务价值较高，需专业跟进")
        if "飞机整机" in report["业务类型分布"]:
            print("   4. 飞机整机交易需谨慎，建议专业评估")
        
        print("   5. 使用生成的业务信息表进行系统化跟进")

def load_sample_data():
    """加载示例数据"""
    sample_posts = [
        {
            "author": "John Smith",
            "company": "ABC Aviation",
            "content": "紧急采购CFM56-7B发动机PN: 123-456，需要现货，价格USD 500,000，联系方式: WhatsApp +86 13800138000",
            "url": "https://www.linkedin.com/feed/update/123",
            "time": "2小时前"
        },
        {
            "author": "李经理",
            "company": "航空材料公司",
            "content": "供应A320起落架，件号：335-010-401-0，有现货，价格优惠，联系微信: aviation_parts",
            "url": "https://www.linkedin.com/feed/update/456",
            "time": "5小时前"
        },
        {
            "author": "航空发动机专家",
            "company": "MRO服务中心",
            "content": "提供V2500发动机大修服务，专业团队，快速交付，联系邮箱: service@mro.com",
            "url": "https://www.linkedin.com/feed/update/789",
            "time": "1天前"
        },
        {
            "author": "飞机交易经纪人",
            "company": "国际航空资产",
            "content": "出售B737-800飞机整机，2015年制造，总飞行时间25,000小时，价格面议，联系邮箱: aircraft@global.com",
            "url": "https://www.linkedin.com/feed/update/101",
            "time": "3天前"
        },
        {
            "author": "航材供应商",
            "company": "全球航材供应",
            "content": "大量航材库存，包括A320、B737系列零件，PN齐全，欢迎询价RFQ，邮箱: sales@parts.com",
            "url": "https://www.linkedin.com/feed/update/112",
            "time": "1周前"
        },
        {
            "author": "APU专家",
            "company": "动力系统公司",
            "content": "求购GTCP131-9A APU，需要serviceable condition，PN: 123-789，紧急需要",
            "url": "https://www.linkedin.com/feed/update/113",
            "time": "1天前"
        },
        {
            "author": "航电系统工程师",
            "company": "航空电子科技",
            "content": "供应B787航电系统组件，包括显示系统、导航系统，价格优惠",
            "url": "https://www.linkedin.com/feed/update/114",
            "time": "2天前"
        }
    ]
    
    # 生成50条示例数据
    all_posts = []
    for i in range(50):
        post_index = i % len(sample_posts)
        post = sample_posts[post_index].copy()
        post["content"] = f"[示例{i+1}] {post['content']}"
        all_posts.append(post)
    
    return all_posts

def main():
    """主函数"""
    print("=" * 60)
    print("业务信息表创建器 - 基于bababot方法")
    print("=" * 60)
    print("目标：从LinkedIn帖子中提取业务信息，创建可直接使用的业务信息表")
    print("")
    
    # 创建分析器和表创建器
    creator = BusinessInfoTableCreator()
    
    # 加载数据
    print("📥 加载数据...")
    posts_data = load_sample_data()
    print(f"   加载了 {len(posts_data)} 条帖子数据")
    
    # 创建业务信息表
    print("\n🔍 分析帖子并创建业务信息表...")
    business_posts = creator.create_table_from_posts(posts_data, source="linkedin_feed_sample")
    
    # 保存到文件
    print("\n💾 保存结果...")
    output_file = creator.save_to_files(business_posts, "linkedin_business_info")
    
    if output_file:
        print("\n✅ 任务完成!")
        print(f"   业务信息表: {output_file}")
        print(f"   输出目录: {creator.output_dir}")
        
        # 显示前几条记录
        print("\n📋 前5条业务信息:")
        for i, post in enumerate(business_posts[:5], 1):
            print(f"   {i}. [{post['ID']}] {post['发帖人']} - {post['业务类型']}")
            print(f"      需求: {post['具体需求']}, 评分: {post['业务价值评分']}/5")
            print(f"      跟进: {post['跟进建议']}")
            print()
        
        print("🎯 下一步行动:")
        print("   1. 使用业务信息表进行系统化跟进")
        print("   2. 重点关注高价值(评分≥4)和紧急业务")
        print("   3. 定期更新数据，建立持续的业务信息收集机制")
        print("   4. 结合之前分析的LinkedIn联系人，进行精准业务匹配")
    else:
        print("\n❌ 任务失败: 未找到业务信息")

if __name__ == "__main__":
    main()