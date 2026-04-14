#!/usr/bin/env python3
"""
【功能】构造模拟 raw_results，调试 RAGService._format_results。
【长期价值】单元调试片段；可删。
"""

import json
import sys
from rag_service import RAGService

async def debug_format_results():
    """调试_format_results方法"""
    print("=== 调试_format_results方法 ===\n")
    
    try:
        # 创建RAGService实例
        service = RAGService()
        
        # 模拟raw_results数据
        raw_results = {
            "ids": [["img_95"]],
            "metadatas": [[{
                "id": "img_95",
                "paper_id": "unknown",
                "savepath": "test.jpg",
                "image_path": "test.jpg",
                "keywords": "test",
                "full_json": json.dumps({
                    "id": "img_95",
                    "title": "Test Title",
                    "summary": "Test Summary",
                    "insight": "Test Insight",
                    "key_entities": ["test1", "test2"]
                })
            }]],
            "documents": [["Title: Test Title\nSummary: Test Summary\nInsight: Test Insight"]],
            "distances": [[0.2]]
        }
        
        print("1. 原始数据:")
        print(f"   IDs: {raw_results['ids']}")
        print(f"   Metadata keys: {list(raw_results['metadatas'][0][0].keys())}")
        print(f"   Document: {raw_results['documents'][0][0][:50]}...")
        print(f"   Distance: {raw_results['distances'][0][0]}")
        print()
        
        # 调用_format_results方法
        formatted = service._format_results(raw_results, is_semantic=True)
        
        print("2. 格式化结果:")
        print(f"   结果数量: {len(formatted)}")
        if formatted:
            result = formatted[0]
            print(f"   ID: {result['id']}")
            print(f"   分数: {result['score']:.4f}")
            print(f"   内容类型: {type(result['content'])}")
            print(f"   内容: {result['content']}")
            print(f"   元数据: {list(result['metadata'].keys())}")
        print()
        
        # 测试直接解析full_json
        print("3. 直接解析full_json测试:")
        full_json = raw_results['metadatas'][0][0]['full_json']
        print(f"   full_json: {full_json[:100]}...")
        
        try:
            parsed = json.loads(full_json)
            print(f"   解析成功，类型: {type(parsed)}")
            print(f"   解析内容: {parsed}")
        except Exception as e:
            print(f"   解析失败: {e}")
        print()
        
        print("=== 调试完成 ===")
        return True
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(debug_format_results())
    sys.exit(0 if result else 1)
