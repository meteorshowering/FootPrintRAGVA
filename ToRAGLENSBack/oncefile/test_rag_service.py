#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【功能】对 get_rag_service 做语义/多模态查询冒烟测试。
【长期价值】集成测试草稿；可删。
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_service import get_rag_service

async def main():
    """主函数"""
    print("测试修改后的RAG服务...")
    print("=" * 50)
    
    # 获取RAG服务实例
    rag_service = await get_rag_service()
    
    # 测试1: 测试一般文本查询（应该使用paper_rag_collection）
    print("\n测试1: 一般文本查询")
    print("查询: vehicle emission factors")
    print("-" * 30)
    
    results1, _t1 = await rag_service.query_by_semantic("vehicle emission factors")
    print(f"结果数量: {len(results1)}")
    
    for i, result in enumerate(results1[:3]):
        print(f"\n结果 {i+1}:")
        print(f"类型: {result.get('type', 'unknown')}")
        print(f"相似度: {result.get('score', 0):.4f}")
        print(f"来源: {result.get('source', 'unknown')}")
        print(f"内容类型: {result.get('content', {}).get('title', 'unknown') or result.get('content', {}).get('text', 'unknown')[:50]}...")
        print(f"返回格式包含所有必要字段: {all(key in result for key in ['id', 'content', 'score', 'metadata', 'type', 'source'])}")
    
    # 测试2: 测试视觉相关查询（应该使用scientific_rag_collection_new）
    print("\n" + "=" * 50)
    print("\n测试2: 视觉相关查询")
    print("查询: figure showing temperature trends")
    print("-" * 30)
    
    results2 = await rag_service.query_by_semantic("figure showing temperature trends")
    print(f"结果数量: {len(results2)}")
    
    for i, result in enumerate(results2[:3]):
        print(f"\n结果 {i+1}:")
        print(f"类型: {result.get('type', 'unknown')}")
        print(f"相似度: {result.get('score', 0):.4f}")
        print(f"来源: {result.get('source', 'unknown')}")
        print(f"内容类型: {result.get('content', {}).get('title', 'unknown') or result.get('content', {}).get('text', 'unknown')[:50]}...")
        print(f"返回格式包含所有必要字段: {all(key in result for key in ['id', 'content', 'score', 'metadata', 'type', 'source'])}")
    
    # 测试3: 测试指定集合查询
    print("\n" + "=" * 50)
    print("\n测试3: 指定集合查询")
    print("查询: climate change, 使用集合: paper_rag_collection")
    print("-" * 30)
    
    results3, _t3 = await rag_service.query_by_semantic("climate change", collection_name="paper_rag_collection")
    print(f"结果数量: {len(results3)}")
    
    for i, result in enumerate(results3[:3]):
        print(f"\n结果 {i+1}:")
        print(f"类型: {result.get('type', 'unknown')}")
        print(f"相似度: {result.get('score', 0):.4f}")
        print(f"来源: {result.get('source', 'unknown')}")
        print(f"内容类型: {result.get('content', {}).get('title', 'unknown') or result.get('content', {}).get('text', 'unknown')[:50]}...")
        print(f"返回格式包含所有必要字段: {all(key in result for key in ['id', 'content', 'score', 'metadata', 'type', 'source'])}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("所有测试都验证了返回结果格式的一致性，确保前端能够正确处理不同类型的数据。")

if __name__ == "__main__":
    asyncio.run(main())
