#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单分析后续20个LinkedIn联系人的业务画像
不使用pandas，纯Python实现
"""

import csv
import json
from datetime import datetime
import os

def read_csv_contacts(file_path):
    """读取CSV文件中的联系人"""
    contacts = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contacts.append(row)
        print(f"成功读取 {len(contacts)} 个联系人")
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        # 尝试其他编码
        try:
            with open(file_path, 'r', encoding='gbk', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    contacts.append(row)
            print(f"使用GBK编码成功读取 {len(contacts)} 个联系人")
        except Exception as e2:
            print(f"使用GBK编码也失败: {e2}")
    
    return contacts

def analyze_contact(contact):
    """分析单个联系人的业务画像"""
    # 基本信息
    first_name = contact.get('First Name', '') or contact.get('First Name', '')
    last_name = contact.get('Last Name', '') or contact.get('Last Name', '')
    position = contact.get('Position', '') or contact.get('Position', '')
    company = contact.get('Company', '') or contact.get('Company', '')
    url = contact.get('URL', '') or contact.get('URL', '')
    
    # 清理数据
    first_name = str(first_name).strip()
    last_name = str(last_name).strip()
    position = str(position).strip()
    company = str(company).strip()
    url = str(url).strip()
    
    # 基于职位和公司信息的专业推断分析
    analysis = {
        '姓名': f"{first_name} {last_name}".strip(),
        '职位': position,
        '公司': company,
        'LinkedIn链接': url,
        '分析时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '分析方法': '专业推断分析 (基于bababot方法)',
        '数据质量': '基于职位和公司信息的专业推断',
        '业务领域分类': '',
        '行业细分': '',
        '数据分析推断': '',
        '帖子内容分析': '',
        '工作内容总结': '',
        'Recent_Activity_Summary': '',
        'Business_Focus': '',
        '业务画像标签': []
    }
    
    # 基于航空行业知识的专业推断
    analysis.update(infer_business_profile(position, company))
    
    return analysis

def infer_business_profile(position, company):
    """基于职位和公司信息推断业务画像"""
    result = {
        '业务领域分类': '',
        '行业细分': '',
        '数据分析推断': '',
        '帖子内容分析': '',
        '工作内容总结': '',
        'Recent_Activity_Summary': '',
        'Business_Focus': '',
        '业务画像标签': []
    }
    
    # 职位关键词分析
    position_lower = str(position).lower()
    company_lower = str(company).lower()
    
    # 业务领域分类
    if any(keyword in position_lower for keyword in ['sales', 'business development', 'bd', 'commercial', '销售', '业务发展']):
        result['业务领域分类'] = '销售与业务发展'
        result['业务画像标签'].append('销售专家')
        result['业务画像标签'].append('业务发展')
    elif any(keyword in position_lower for keyword in ['acquisition', 'asset management', 'investment', 'finance', '收购', '资产', '投资', '金融']):
        result['业务领域分类'] = '收购与资产管理'
        result['业务画像标签'].append('资产管理')
        result['业务画像标签'].append('投资专家')
    elif any(keyword in position_lower for keyword in ['maintenance', 'mro', 'engineering', 'technical', '维修', '工程', '技术']):
        result['业务领域分类'] = '维修与工程技术'
        result['业务画像标签'].append('MRO专家')
        result['业务画像标签'].append('工程技术')
    elif any(keyword in position_lower for keyword in ['procurement', 'supply chain', 'logistics', 'material', '采购', '供应链', '物流', '材料']):
        result['业务领域分类'] = '采购与供应链'
        result['业务画像标签'].append('采购专家')
        result['业务画像标签'].append('供应链管理')
    elif any(keyword in position_lower for keyword in ['ceo', 'director', 'vp', 'head of', 'manager', '总裁', '总监', '经理', '负责人']):
        result['业务领域分类'] = '管理与领导'
        result['业务画像标签'].append('管理领导')
        result['业务画像标签'].append('战略规划')
    else:
        result['业务领域分类'] = '航空专业服务'
        result['业务画像标签'].append('航空专家')
    
    # 行业细分
    if any(keyword in company_lower for keyword in ['airline', '航空', '航空公司', 'airlines']):
        result['行业细分'] = '航空公司运营'
        result['业务画像标签'].append('航空公司')
    elif any(keyword in company_lower for keyword in ['mro', 'maintenance', '维修', 'technic', 'technical']):
        result['行业细分'] = '飞机维修服务'
        result['业务画像标签'].append('MRO服务')
    elif any(keyword in company_lower for keyword in ['leasing', 'finance', 'capital', '租赁', '金融']):
        result['行业细分'] = '航空金融租赁'
        result['业务画像标签'].append('金融租赁')
    elif any(keyword in company_lower for keyword in ['parts', 'component', 'supply', '部件', '航材']):
        result['行业细分'] = '航材供应'
        result['业务画像标签'].append('航材供应')
    elif any(keyword in company_lower for keyword in ['consulting', 'consultant', '咨询']):
        result['行业细分'] = '航空咨询'
        result['业务画像标签'].append('咨询顾问')
    else:
        result['行业细分'] = '航空综合服务'
    
    # 数据分析推断
    result['数据分析推断'] = f"基于{position}职位和{company}公司背景的专业分析"
    
    # 帖子内容分析推断
    if '销售' in result['业务领域分类']:
        result['帖子内容分析'] = '预计分享市场趋势、客户案例、产品更新、行业动态等内容'
        result['Recent_Activity_Summary'] = '市场趋势分析 | 客户成功案例 | 产品技术更新 | 行业网络建设'
    elif '资产管理' in result['业务领域分类']:
        result['帖子内容分析'] = '预计分享投资机会、市场分析、交易案例、风险管理等内容'
        result['Recent_Activity_Summary'] = '投资机会分析 | 市场风险评估 | 交易案例分享 | 资产优化策略'
    elif '维修' in result['业务领域分类']:
        result['帖子内容分析'] = '预计分享技术更新、维修案例、安全标准、质量控制等内容'
        result['Recent_Activity_Summary'] = '技术标准更新 | 维修案例分享 | 安全合规讨论 | 质量控制实践'
    elif '采购' in result['业务领域分类']:
        result['帖子内容分析'] = '预计分享供应链优化、成本控制、供应商管理、物流效率等内容'
        result['Recent_Activity_Summary'] = '供应链优化 | 成本控制策略 | 供应商关系 | 物流效率提升'
    else:
        result['帖子内容分析'] = '预计分享行业洞察、领导力思考、战略规划、团队管理等内容'
        result['Recent_Activity_Summary'] = '行业趋势洞察 | 领导力发展 | 战略规划思考 | 团队管理经验'
    
    # 工作内容总结
    result['工作内容总结'] = f"在{company}担任{position}，专注于{result['业务领域分类']}领域的{result['行业细分']}工作"
    
    # Business Focus
    result['Business_Focus'] = f"{result['业务领域分类']} | {result['行业细分']} | " + " | ".join(result['业务画像标签'][:3])
    
    return result

def main():
    """主函数"""
    print("开始分析后续20个LinkedIn联系人...")
    
    # 文件路径
    csv_file = r"C:\Users\Haide\Desktop\LINKEDIN\Data\LINKEDIN Connections_bababot_style_FINAL.csv"
    output_dir = r"C:\Users\Haide\Desktop\LINKEDIN\Analysis"
    output_csv = os.path.join(output_dir, "linkedin_analysis_batch4_2026-02-23.csv")
    output_json = os.path.join(output_dir, "linkedin_analysis_batch4_2026-02-23.json")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取联系人
    contacts = read_csv_contacts(csv_file)
    
    if not contacts:
        print("没有读取到联系人数据")
        return
    
    # 分析后续20个联系人（从第35个开始）
    start_index = 35  # 从第35个联系人开始（0-based索引）
    end_index = min(start_index + 20, len(contacts))
    
    print(f"分析联系人 {start_index+1} 到 {end_index} (共{end_index-start_index}个)")
    
    analyses = []
    for i in range(start_index, end_index):
        contact = contacts[i]
        first_name = str(contact.get('First Name', '')).strip()
        last_name = str(contact.get('Last Name', '')).strip()
        name = f"{first_name} {last_name}".strip()
        
        # 安全地打印，避免编码问题
        try:
            print(f"分析联系人 {i+1}/{len(contacts)}: {name}")
        except:
            print(f"分析联系人 {i+1}/{len(contacts)}: [姓名包含特殊字符]")
        
        analysis = analyze_contact(contact)
        analyses.append(analysis)
    
    # 保存为CSV
    if analyses:
        print(f"\n保存分析结果到: {output_csv}")
        
        # 获取所有可能的字段
        all_fields = set()
        for analysis in analyses:
            all_fields.update(analysis.keys())
        
        fieldnames = sorted(all_fields)
        
        with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(analyses)
        
        print(f"成功保存 {len(analyses)} 个联系人的分析结果到CSV")
        
        # 保存为JSON
        print(f"保存JSON格式到: {output_json}")
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(analyses, f, ensure_ascii=False, indent=2)
        
        # 打印摘要报告
        print_summary(analyses)
    
    print("\n分析完成!")

def print_summary(analyses):
    """打印分析摘要"""
    print("\n" + "="*80)
    print("分析摘要报告")
    print("="*80)
    
    # 统计业务领域分布
    domain_counts = {}
    industry_counts = {}
    
    for analysis in analyses:
        domain = analysis['业务领域分类']
        industry = analysis['行业细分']
        
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        industry_counts[industry] = industry_counts.get(industry, 0) + 1
    
    print(f"\n分析联系人总数: {len(analyses)}")
    
    print("\n业务领域分布:")
    for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(analyses)) * 100
        print(f"  {domain}: {count}人 ({percentage:.1f}%)")
    
    print("\n行业细分分布:")
    for industry, count in sorted(industry_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(analyses)) * 100
        print(f"  {industry}: {count}人 ({percentage:.1f}%)")
    
    # 显示前5个联系人的详细信息
    print("\n前5个联系人的详细分析:")
    print("-"*80)
    
    for i, analysis in enumerate(analyses[:5]):
        print(f"\n{i+1}. {analysis['姓名']}")
        print(f"   职位: {analysis['职位']}")
        print(f"   公司: {analysis['公司']}")
        print(f"   业务领域: {analysis['业务领域分类']}")
        print(f"   行业细分: {analysis['行业细分']}")
        print(f"   Business Focus: {analysis['Business_Focus']}")
        print(f"   业务标签: {', '.join(analysis['业务画像标签'][:5])}")
    
    if len(analyses) > 5:
        print(f"\n... 还有 {len(analyses)-5} 个联系人的分析结果")

if __name__ == "__main__":
    main()