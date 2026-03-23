#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR技能使用示例
演示如何从图片中提取文字并分析LinkedIn帖子
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_tool import OCRReader, analyze_linkedin_screenshot


def example_basic_ocr():
    """基础OCR使用示例"""
    print("=" * 60)
    print("基础OCR使用示例")
    print("=" * 60)
    
    # 创建OCR阅读器
    ocr = OCRReader()
    
    # 检查OCR是否可用
    if not ocr.ocr_available:
        print("OCR功能不可用，请安装依赖：")
        print("pip install pytesseract pillow")
        print("并安装Tesseract OCR：https://github.com/UB-Mannheim/tesseract/wiki")
        return
    
    print("OCR功能可用，准备测试...")
    
    # 示例：测试图片（如果存在）
    test_images = [
        "example_linkedin_screenshot.png",
        "test_image.jpg",
        "sample.png"
    ]
    
    for image_name in test_images:
        image_path = Path(__file__).parent / image_name
        if image_path.exists():
            print(f"\n测试图片: {image_name}")
            print("-" * 40)
            
            # 提取文字
            result = ocr.extract_text(image_path)
            
            if result['success']:
                print(f"提取成功！字符数: {result['character_count']}")
                print(f"前200字符预览: {result['text'][:200]}...")
                
                # 分析LinkedIn帖子
                analysis = analyze_linkedin_screenshot(result)
                if analysis['success']:
                    print(f"帖子类型: {analysis['post_type']}")
                    print(f"业务机会: {analysis['business_opportunity']}")
            else:
                print(f"提取失败: {result.get('error')}")
            break
    else:
        print("\n未找到测试图片，请将图片放入 skills/ocr-reader/ 目录")
        print("支持的格式: PNG, JPG, JPEG, BMP")


def example_linkedin_analysis():
    """LinkedIn帖子分析示例"""
    print("\n" + "=" * 60)
    print("LinkedIn帖子分析示例")
    print("=" * 60)
    
    # 模拟的LinkedIn帖子文字（来自用户提供的例子）
    sample_text = """AIRCRAFT & ENGINE TRADERS PLATFORM
Abraham San Emeterio • 1st
4d • 4 days ago • Visible to anyone on or off LinkedIn

Good evening,

I am looking to purchase

CFM56-5C2 
Qty: 2

PW121A
Qty: 1

Open to any cycles remaining but the more cycles the better. Please DM if you have any options available.

Thank you,

Abraham
asanem@airsource.us
likeinsightful
6"""
    
    print("模拟LinkedIn帖子分析：")
    print("-" * 40)
    print(sample_text)
    print("-" * 40)
    
    # 创建模拟的OCR结果
    mock_ocr_result = {
        'success': True,
        'text': sample_text,
        'image_path': 'mock_linkedin_screenshot.png',
        'language': 'eng',
        'character_count': len(sample_text)
    }
    
    # 分析帖子
    analysis = analyze_linkedin_screenshot(mock_ocr_result)
    
    if analysis['success']:
        print("\n分析结果：")
        print(f"帖子类型: {analysis['post_type']}")
        print(f"业务机会: {'是' if analysis['business_opportunity'] else '否'}")
        print(f"紧急程度: {analysis['urgency_level']}")
        
        if analysis['contact_info']:
            print(f"联系方式: {analysis['contact_info']}")
        
        if analysis['products_services']:
            print(f"产品/服务: {', '.join(analysis['products_services'])}")
        
        # 业务价值评估
        print("\n业务价值评估：")
        if analysis['business_opportunity']:
            print("✅ 发现业务机会！")
            print("📞 建议立即联系")
            print("📧 联系方式: asanem@airsource.us")
            print("🛠️ 需求产品: CFM56-5C2 (2台), PW121A (1台)")
            print("⏰ 紧急程度: 高（明确采购需求）")
        else:
            print("ℹ️ 未发现明显业务机会")


def example_integration_with_openclaw():
    """与OpenClaw集成示例"""
    print("\n" + "=" * 60)
    print("与OpenClaw集成示例")
    print("=" * 60)
    
    print("在OpenClaw中使用OCR功能的几种方式：")
    print("\n1. 使用内置image工具：")
    print("""
# 读取图片文字
image(prompt="读取图片中的所有文字", image="图片路径或URL")
""")
    
    print("\n2. 创建自定义工具函数：")
    print("""
def read_image_text(image_path):
    \"\"\"读取图片文字工具函数\"\"\"
    ocr = OCRReader()
    result = ocr.extract_text(image_path)
    return result
""")
    
    print("\n3. LinkedIn帖子分析工作流：")
    print("""
def analyze_linkedin_screenshot_workflow(screenshot_path):
    \"\"\"LinkedIn截图分析工作流\"\"\"
    # 1. OCR提取文字
    ocr_result = read_image_text(screenshot_path)
    
    if not ocr_result['success']:
        return {"error": "OCR提取失败"}
    
    # 2. 分析帖子内容
    analysis = analyze_linkedin_screenshot(ocr_result)
    
    # 3. 提取业务机会
    if analysis['business_opportunity']:
        business_info = extract_business_info(ocr_result['text'])
        return {
            'analysis': analysis,
            'business_opportunity': business_info,
            'recommendation': '立即联系'
        }
    
    return {'analysis': analysis, 'business_opportunity': None}
""")


def example_installation_guide():
    """安装指南"""
    print("\n" + "=" * 60)
    print("OCR技能安装指南")
    print("=" * 60)
    
    print("1. 安装Tesseract OCR（Windows）：")
    print("   下载地址：https://github.com/UB-Mannheim/tesseract/wiki")
    print("   安装后添加环境变量：C:\\Program Files\\Tesseract-OCR")
    
    print("\n2. 安装Python依赖：")
    print("   pip install pytesseract pillow")
    
    print("\n3. 安装中文语言包：")
    print("   从 https://github.com/tesseract-ocr/tessdata 下载 chi_sim.traineddata")
    print("   放到 Tesseract-OCR\\tessdata 目录")
    
    print("\n4. 测试安装：")
    print("   python ocr_tool.py --help")


def main():
    """主函数"""
    print("OCR Reader Skill - 使用示例")
    print("=" * 60)
    
    # 运行各个示例
    example_basic_ocr()
    example_linkedin_analysis()
    example_integration_with_openclaw()
    example_installation_guide()
    
    print("\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    print("✅ OCR技能已创建")
    print("✅ 支持中英文图片文字提取")
    print("✅ 特别优化LinkedIn帖子分析")
    print("✅ 提供完整的安装和使用指南")
    print("✅ 可与OpenClaw现有工作流集成")
    
    print("\n下一步：")
    print("1. 安装Tesseract OCR和Python依赖")
    print("2. 测试OCR功能：python ocr_tool.py 图片路径")
    print("3. 集成到LinkedIn分析工作流中")


if __name__ == '__main__':
    main()