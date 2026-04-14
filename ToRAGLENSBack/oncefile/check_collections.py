#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【功能】列出 Chroma 中集合名称与条目数，用于运维检查。
【长期价值】运维小工具可保留。
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_collection_manager import RAGCollectionManager

async def main():
    """主函数"""
    print("检查现有向量库集合...")
    print("=" * 50)
    
    # 创建RAGCollectionManager实例
    manager = RAGCollectionManager()
    await manager.initialize()
    
    # 列出所有集合
    collections = manager.chroma_client.list_collections()
    collection_names = [c.name for c in collections]
    print(f"现有集合数量: {len(collection_names)}")
    print(f"集合名称: {collection_names}")
    print("=" * 50)
    
    # 检查每个集合的结构
    for collection_name in collection_names:
        print(f"\n检查集合: {collection_name}")
        print("-" * 30)
        
        try:
            collection = await manager.get_collection(collection_name)
            if not collection:
                print(f"无法获取集合 {collection_name}")
                continue
            
            # 获取集合大小
            count = collection.count()
            print(f"集合大小: {count} 条数据")
            
            # 采样查看前3条数据的结构
            if count > 0:
                sample_results = collection.query(
                    query_texts=["test"],
                    n_results=3,
                    include=["metadatas", "documents"]
                )
                
                if sample_results and sample_results.get("metadatas") and sample_results["metadatas"][0]:
                    print(f"\n第一条数据的metadata结构:")
                    metadata = sample_results["metadatas"][0][0]
                    for key, value in metadata.items():
                        print(f"  {key}: {str(value)[:100]}..." if len(str(value)) > 100 else f"  {key}: {value}")
                    
                    print(f"\n第一条数据的content预览:")
                    content = sample_results["documents"][0][0]
                    print(f"  {content[:200]}..." if len(content) > 200 else f"  {content}")
            
        except Exception as e:
            print(f"检查集合 {collection_name} 时出错: {e}")
    
    print("\n" + "=" * 50)
    print("检查完成！")

if __name__ == "__main__":
    asyncio.run(main())
