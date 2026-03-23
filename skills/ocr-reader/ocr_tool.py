#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR工具 - 图片文字提取工具
支持从图片中提取中英文文字
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("警告：OCR依赖未安装，请运行：pip install pytesseract pillow")


class OCRReader:
    """OCR阅读器类"""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        初始化OCR阅读器
        
        Args:
            tesseract_path: Tesseract OCR可执行文件路径
        """
        self.ocr_available = OCR_AVAILABLE
        
        if self.ocr_available:
            # 设置Tesseract路径（Windows系统）
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            elif sys.platform == 'win32':
                # Windows默认路径
                default_paths = [
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
                ]
                for path in default_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        break
    
    def extract_text(self, image_path: Union[str, Path], 
                    language: str = 'chi_sim+eng',
                    preprocess: bool = True) -> Dict:
        """
        从图片中提取文字
        
        Args:
            image_path: 图片文件路径
            language: 语言设置（默认中英文）
            preprocess: 是否进行图片预处理
        
        Returns:
            包含提取文字和元数据的字典
        """
        if not self.ocr_available:
            return {
                'success': False,
                'error': 'OCR依赖未安装',
                'suggestion': '请运行: pip install pytesseract pillow'
            }
        
        try:
            # 检查文件是否存在
            image_path = Path(image_path)
            if not image_path.exists():
                return {
                    'success': False,
                    'error': f'文件不存在: {image_path}',
                    'image_path': str(image_path)
                }
            
            # 打开图片
            img = Image.open(image_path)
            
            # 图片预处理（可选）
            if preprocess:
                img = self._preprocess_image(img)
            
            # 提取文字
            text = pytesseract.image_to_string(img, lang=language)
            
            # 清理文字
            text = text.strip()
            
            # 获取图片信息
            img_info = {
                'format': img.format,
                'size': img.size,
                'mode': img.mode
            }
            
            return {
                'success': True,
                'text': text,
                'image_path': str(image_path),
                'image_info': img_info,
                'language': language,
                'character_count': len(text),
                'line_count': len(text.splitlines())
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'image_path': str(image_path),
                'language': language
            }
    
    def _preprocess_image(self, img: Image.Image) -> Image.Image:
        """
        图片预处理
        
        Args:
            img: PIL图片对象
        
        Returns:
            预处理后的图片
        """
        # 转换为灰度图
        if img.mode != 'L':
            img = img.convert('L')
        
        # 这里可以添加更多预处理步骤
        # 如：对比度增强、二值化、去噪等
        
        return img
    
    def batch_extract(self, image_paths: List[Union[str, Path]], 
                     language: str = 'chi_sim+eng',
                     preprocess: bool = True) -> List[Dict]:
        """
        批量提取图片文字
        
        Args:
            image_paths: 图片路径列表
            language: 语言设置
            preprocess: 是否预处理
        
        Returns:
            提取结果列表
        """
        results = []
        for image_path in image_paths:
            result = self.extract_text(image_path, language, preprocess)
            results.append(result)
        return results
    
    def extract_with_cache(self, image_path: Union[str, Path],
                          cache_dir: Union[str, Path] = 'ocr_cache',
                          language: str = 'chi_sim+eng') -> Dict:
        """
        带缓存的文字提取
        
        Args:
            image_path: 图片路径
            cache_dir: 缓存目录
            language: 语言设置
        
        Returns:
            提取结果
        """
        image_path = Path(image_path)
        cache_dir = Path(cache_dir)
        
        # 创建缓存目录
        cache_dir.mkdir(exist_ok=True)
        
        # 计算图片哈希值
        with open(image_path, 'rb') as f:
            image_hash = hashlib.md5(f.read()).hexdigest()
        
        cache_file = cache_dir / f"{image_hash}_{language}.json"
        
        # 检查缓存
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_result = json.load(f)
                
                # 验证缓存有效性（检查文件修改时间）
                image_mtime = image_path.stat().st_mtime
                cache_mtime = cache_file.stat().st_mtime
                
                if cache_mtime > image_mtime:
                    cached_result['cached'] = True
                    return cached_result
            except:
                pass  # 缓存读取失败，重新提取
        
        # 执行OCR提取
        result = self.extract_text(image_path, language)
        
        # 保存缓存
        if result['success']:
            result['cached'] = False
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result


def analyze_linkedin_screenshot(ocr_result: Dict) -> Dict:
    """
    分析LinkedIn截图提取的文字
    
    Args:
        ocr_result: OCR提取结果
    
    Returns:
        分析结果
    """
    if not ocr_result.get('success'):
        return {
            'success': False,
            'error': 'OCR提取失败',
            'ocr_error': ocr_result.get('error')
        }
    
    text = ocr_result['text']
    
    # 提取关键信息
    analysis = {
        'success': True,
        'post_type': 'unknown',
        'business_opportunity': False,
        'contact_info': {},
        'products_services': [],
        'urgency_level': 'low'
    }
    
    # 检查是否是LinkedIn帖子
    linkedin_keywords = ['LinkedIn', 'like', 'comment', 'share', 'follow', 'connection']
    if any(keyword.lower() in text.lower() for keyword in linkedin_keywords):
        analysis['post_type'] = 'linkedin'
    
    # 检查业务机会关键词
    business_keywords = ['purchase', 'buy', 'sell', 'supply', 'available', 'looking for',
                        '需要', '采购', '销售', '供应', '寻找']
    if any(keyword.lower() in text.lower() for keyword in business_keywords):
        analysis['business_opportunity'] = True
    
    # 提取联系方式
    import re
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    if emails:
        analysis['contact_info']['emails'] = emails
    
    phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    phones = re.findall(phone_pattern, text)
    if phones:
        analysis['contact_info']['phones'] = phones
    
    # 提取产品/服务信息
    aviation_keywords = ['CFM56', 'PW', '发动机', '引擎', 'aircraft', 'engine',
                        '航材', '起落架', '维修', '租赁']
    products = []
    for keyword in aviation_keywords:
        if keyword.lower() in text.lower():
            products.append(keyword)
    
    if products:
        analysis['products_services'] = products
    
    # 评估紧急程度
    urgency_keywords = ['urgent', 'immediate', 'asap', '紧急', '立即', '尽快']
    if any(keyword.lower() in text.lower() for keyword in urgency_keywords):
        analysis['urgency_level'] = 'high'
    
    return analysis


def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OCR图片文字提取工具')
    parser.add_argument('image_path', help='图片文件路径')
    parser.add_argument('--language', default='chi_sim+eng', 
                       help='OCR语言设置（默认：chi_sim+eng）')
    parser.add_argument('--no-preprocess', action='store_true',
                       help='禁用图片预处理')
    parser.add_argument('--cache-dir', default='ocr_cache',
                       help='缓存目录（默认：ocr_cache）')
    parser.add_argument('--analyze', action='store_true',
                       help='分析提取的文字（特别针对LinkedIn）')
    
    args = parser.parse_args()
    
    # 创建OCR阅读器
    ocr = OCRReader()
    
    # 提取文字
    if args.cache_dir:
        result = ocr.extract_with_cache(args.image_path, args.cache_dir, args.language)
    else:
        result = ocr.extract_text(args.image_path, args.language, not args.no_preprocess)
    
    # 输出结果
    if result['success']:
        print("=" * 60)
        print("OCR提取结果：")
        print("=" * 60)
        print(f"图片: {result['image_path']}")
        print(f"语言: {result['language']}")
        print(f"字符数: {result['character_count']}")
        print(f"行数: {result['line_count']}")
        print("-" * 60)
        print("提取的文字内容：")
        print("-" * 60)
        print(result['text'])
        print("=" * 60)
        
        # 分析文字
        if args.analyze:
            analysis = analyze_linkedin_screenshot(result)
            if analysis['success']:
                print("\n分析结果：")
                print(f"帖子类型: {analysis['post_type']}")
                print(f"业务机会: {'是' if analysis['business_opportunity'] else '否'}")
                print(f"紧急程度: {analysis['urgency_level']}")
                if analysis['contact_info']:
                    print(f"联系方式: {analysis['contact_info']}")
                if analysis['products_services']:
                    print(f"产品/服务: {', '.join(analysis['products_services'])}")
    else:
        print(f"OCR提取失败: {result.get('error', '未知错误')}")
        if 'suggestion' in result:
            print(f"建议: {result['suggestion']}")
    
    return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())