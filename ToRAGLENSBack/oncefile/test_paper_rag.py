#!/usr/bin/env python3
"""
【功能】paper_rag_collection 创建、加载与查询示例。
【长期价值】集成测试草稿；可删。
"""

import asyncio
import sys
from rag_collection_manager import get_paper_rag_manager

async def test_paper_rag():
    """测试论文向量库的创建和查询功能"""
    print("=== 测试论文向量库功能 ===\n")
    
    try:
        # 获取论文RAG管理器
        manager = await get_paper_rag_manager()
        print("✅ 成功获取论文RAG管理器实例")
        
        # 论文集合名称
        paper_collection_name = "paper_rag_collection"
        
        # 1. 测试加载论文到集合
        print("\n1. 测试加载论文到集合:")
        print(f"   开始加载论文到集合 '{paper_collection_name}'...")
        chunk_count = await manager.load_papers_to_collection(paper_collection_name, reset_data=True)
        print(f"   加载完成: {chunk_count} 个块")
        assert chunk_count > 0, "应该加载至少一个块"
        
        # 2. 测试检查集合是否存在
        print("\n2. 测试检查集合是否存在:")
        exists = await manager.check_collection_exists(paper_collection_name)
        print(f"   集合 '{paper_collection_name}' 是否存在: {exists}")
        assert exists, "集合应该存在"
        
        # 3. 测试获取集合
        print("\n3. 测试获取集合:")
        collection = await manager.get_collection(paper_collection_name)
        print(f"   获取集合成功: {collection.name}")
        print(f"   集合中的记录数: {collection.count()}")
        assert collection.count() > 0, "集合中应该有记录"
        
        # 4. 测试查询功能
        print("\n4. 测试查询功能:")
        # 创建RAG内存实例
        rag_memory = await manager.create_rag_memory(paper_collection_name)
        
        # 执行语义查询
        query_text = "air pollution"
        print(f"   查询关键词: '{query_text}'")
        
        # 使用集合的query方法
        results = collection.query(
            query_texts=[query_text],
            n_results=3,
            include=["metadatas", "documents", "distances"]
        )
        
        print(f"   查询结果数量: {len(results['ids'][0]) if results['ids'] else 0}")
        
        # 打印查询结果
        if results and results['ids'] and results['ids'][0]:
            print("\n   查询结果示例:")
            for i, (id, doc, meta, dist) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                print(f"\n   结果 {i}:")
                print(f"   ID: {id}")
                print(f"   距离: {dist:.4f}")
                print(f"   论文名称: {meta.get('paper_name', '未知')}")
                print(f"   文件名称: {meta.get('file_name', '未知')}")
                print(f"   块索引: {meta.get('chunk_index', '未知')}/{meta.get('total_chunks', '未知')}")
                print(f"   内容预览: {doc[:200]}...")
        
        # 5. 测试另一个查询
        print("\n5. 测试另一个查询:")
        query_text = "emissions"
        print(f"   查询关键词: '{query_text}'")
        
        results = collection.query(
            query_texts=[query_text],
            n_results=3,
            include=["metadatas", "documents", "distances"]
        )
        
        print(f"   查询结果数量: {len(results['ids'][0]) if results['ids'] else 0}")
        
        # 6. 打印集合统计信息
        print("\n6. 集合统计信息:")
        print(f"   集合名称: {paper_collection_name}")
        print(f"   记录总数: {collection.count()}")
        print(f"   论文块数量: {chunk_count}")
        
        print("\n=== 所有测试通过 ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
if __name__ == "__main__":
    result = asyncio.run(test_paper_rag())
    sys.exit(0 if result else 1)
