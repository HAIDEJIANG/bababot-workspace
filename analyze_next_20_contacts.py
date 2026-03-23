#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析后续20个LinkedIn联系人的业务画像
基于bababot方法，使用专业推断分析
"""

import pandas as pd
import csv
from datetime import datetime
import json
import os

def read_csv_file(file_path):
    """读取CSV文件，处理编码问题"""
    try:
        # 尝试不同的编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"成功使用 {encoding} 编码读取文件")
                return df
            except UnicodeDecodeError:
                continue
        
        # 如果所有编码都失败，使用错误处理
        df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
        print("使用错误忽略模式读取文件")
        return df
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None

def analyze_contact(contact):
    """分析单个联系人的业务画像"""
    # 基本信息
    first_name = contact.get('First Name', '')
    last_name = contact.get('Last Name', '')
    position = contact.get('Position', '')
    company = contact.get('Company', '')
    url = contact.get('URL', '')
    
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
    position_lower = position.lower()
    
    # 业务领域分类
    if any(keyword in position_lower for keyword in ['sales', 'business development', 'bd', 'commercial']):
        result['业务领域分类'] = '销售与业务发展'
        result['业务画像标签'].append('销售专家')
        result['业务画像标签'].append('业务发展')
    elif any(keyword in position_lower for keyword in ['acquisition', 'asset management', 'investment', 'finance']):
        result['业务领域分类'] = '收购与资产管理'
        result['业务画像标签'].append('资产管理')
        result['业务画像标签'].append('投资专家')
    elif any(keyword in position_lower for keyword in ['maintenance', 'mro', 'engineering', 'technical']):
        result['业务领域分类'] = '维修与工程技术'
        result['业务画像标签'].append('MRO专家')
        result['业务画像标签'].append('工程技术')
    elif any(keyword in position_lower for keyword in ['procurement', 'supply chain', 'logistics', 'material']):
        result['业务领域分类'] = '采购与供应链'
        result['业务画像标签'].append('采购专家')
        result['业务画像标签'].append('供应链管理')
    elif any(keyword in position_lower for keyword in ['ceo', 'director', 'vp', 'head of', 'manager']):
        result['业务领域分类'] = '管理与领导'
        result['业务画像标签'].append('管理领导')
        result['业务画像标签'].append('战略规划')
    else:
        result['业务领域分类'] = '航空专业服务'
        result['业务画像标签'].append('航空专家')
    
    # 行业细分
    company_lower = str(company).lower()
    if any(keyword in company_lower for keyword in ['airline', '航空', '航空公司']):
        result['行业细分'] = '航空公司运营'
        result['业务画像标签'].append('航空公司')
    elif any(keyword in company_lower for keyword in ['mro', 'maintenance', '维修', 'technic']):
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
    output_file = r"C:\Users\Haide\Desktop\LINKEDIN\Analysis\linkedin_analysis_batch4_2026-02-23.csv"
    
    # 读取CSV文件
    print(f"读取文件: {csv_file}")
    df = read_csv_file(csv_file)
    
    if df is None:
        print("无法读取CSV文件")
        return
    
    print(f"总联系人数量: {len(df)}")
    
    # 查找未分析的联系人
    # 假设"Analysis Status"列包含分析状态
    if 'Analysis Status' in df.columns:
        unanalyzed = df[df['Analysis Status'].str.contains('未分析|������', na=False)]
    else:
        # 如果没有分析状态列，从第35行开始（跳过已分析的）
        unanalyzed = df.iloc[35:55]  # 取20个联系人
    
    print(f"找到 {len(unanalyzed)} 个未分析的联系人")
    
    if len(unanalyzed) == 0:
        print("没有找到未分析的联系人")
        return
    
    # 分析联系人
    analyses = []
    for idx, contact in unanalyzed.iterrows():
        print(f"分析联系人 {idx+1}/{len(unanalyzed)}: {contact.get('First Name', '')} {contact.get('Last Name', '')}")
        
        analysis = analyze_contact(contact)
        analyses.append(analysis)
    
    # 保存分析结果
    print(f"保存分析结果到: {output_file}")
    
    # 创建输出目录
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 保存为CSV
    if analyses:
        df_output = pd.DataFrame(analyses)
        df_output.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"成功保存 {len(analyses)} 个联系人的分析结果")
        
        # 同时保存为JSON格式便于查看
        json_file = output_file.replace('.csv', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analyses, f, ensure_ascii=False, indent=2)
        print(f"同时保存为JSON格式: {json_file}")
        
        # 打印摘要
        print("\n分析摘要:")
        print("=" * 80)
        for i, analysis in enumerate(analyses[:5]):  # 只显示前5个
            print(f"{i+1}. {analysis['姓名']}")
            print(f"   职位: {analysis['职位']}")
            print(f"   公司: {analysis['公司']}")
            print(f"   业务领域: {analysis['业务领域分类']}")
            print(f"   行业细分: {analysis['行业细分']}")
            print(f"   业务标签: {', '.join(analysis['业务画像标签'][:3])}")
            print()
        
        if len(analyses) > 5:
            print(f"... 还有 {len(analyses)-5} 个联系人的分析结果")
    
    print("\n分析完成!")

if __name__ == "__main__":
    main()