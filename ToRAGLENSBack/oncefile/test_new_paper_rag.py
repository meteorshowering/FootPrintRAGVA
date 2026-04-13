#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的论文向量库
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_collection_manager import PaperRAGManager

async def main():
    """主函数"""
    print("测试新的论文向量库...")
    print("=" * 50)
    
    # 创建PaperRAGManager实例
    manager = PaperRAGManager()
    await manager.initialize()
    
    # 测试查询
    test_query = "vehicle emission factors"
    collection_name = "paper_rag_collection"
    
    print(f"\n测试查询: {test_query}")
    print(f"使用集合: {collection_name}")
    print("-" * 50)
    
    # 执行查询
    try:
        # 检查集合是否存在
        exists = await manager.check_collection_exists(collection_name)
        if not exists:
            print(f"集合 {collection_name} 不存在")
            return
        
        # 获取集合
        collection = await manager.get_collection(collection_name)
        if not collection:
            print(f"无法获取集合 {collection_name}")
            return
        
        # 执行查询
        def _sync_query():
            try:
                results = collection.query(
                    query_texts=[test_query],
                    n_results=5,
                    include=["metadatas", "documents", "distances"]
                )
                return results
            except Exception as e:
                print(f"查询出错: {e}")
                return None
        
        raw_results = await asyncio.to_thread(_sync_query)
        
        if not raw_results or not raw_results.get("ids") or not raw_results["ids"][0]:
            print("未找到结果")
            return
        
        # 格式化结果
        formatted_results = []
        ids = raw_results["ids"][0]
        metadatas = raw_results["metadatas"][0]
        documents = raw_results["documents"][0]
        distances = raw_results["distances"][0]
        
        for i, (id, metadata, document, distance) in enumerate(zip(ids, metadatas, documents, distances)):
            score = 1.0 / (1.0 + float(distance))
            formatted_results.append({
                "id": id,
                "similarity": score,
                "content": document,
                "metadata": metadata
            })
        
        print(f"查询结果数量: {len(formatted_results)}")
        print("=" * 50)
        
        for i, result in enumerate(formatted_results):
            print(f"\n结果 {i+1}:")
            print(f"相似度: {result['similarity']:.4f}")
            print(f"论文名称: {result['metadata'].get('paper_name', 'N/A')}")
            print(f"文件名称: {result['metadata'].get('file_name', 'N/A')}")
            print(f"内容预览: {result['content'][:200]}...")
            print("-" * 30)
        
        print("\n" + "=" * 50)
        print("测试完成！")
        
    except Exception as e:
        print(f"查询过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
