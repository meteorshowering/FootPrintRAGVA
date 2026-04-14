#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【功能】实例化 PaperRAGManager 并调用内部分块逻辑做长段落测试。
【长期价值】回归片段；可删。
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_collection_manager import PaperRAGManager

def test_chunking_logic():
    """测试分块逻辑"""
    print("测试分块逻辑...")
    
    # 创建测试文本
    long_text = "这是第四段，非常长的一段文本，我们需要测试当单个段落超过chunk大小时的情况。" + " 测试" * 200
    test_text = f"""这是第一段文本。\n\n这是第二段文本，比第一段稍长一些。\n\n这是第三段文本，我们将测试多个段落合并的情况。\n\n{long_text}\n\n这是第五段，正常长度的段落。"""
    
    print("测试文本长度:", len(test_text))
    print("\n测试文本内容:")
    print(test_text)
    print("\n" + "="*50)
    
    # 创建PaperRAGManager实例
    manager = PaperRAGManager()
    
    # 测试分块
    chunks = manager._split_into_chunks(test_text, chunk_size=200)
    
    print("\n分块结果:")
    print(f"生成的块数量: {len(chunks)}")
    print("="*50)
    
    for i, chunk in enumerate(chunks):
        print(f"\n块 {i+1}:")
        print(f"长度: {len(chunk)}")
        print("内容:")
        print(chunk)
        print("-"*30)

if __name__ == "__main__":
    test_chunking_logic()
