#!/usr/bin/env python3
"""
测试论文向量库的读取和检索功能
"""

import asyncio
import sys
from rag_collection_manager import get_paper_rag_manager

async def test_paper_rag_query():
    """测试论文向量库的读取和检索功能"""
    print("=== 测试论文向量库查询功能 ===\n")
    
    try:
        # 获取论文RAG管理器
        manager = await get_paper_rag_manager()
        print("✅ 成功获取论文RAG管理器实例")
        
        # 论文集合名称
        paper_collection_name = "paper_rag_collection"
        
        # 1. 检查集合是否存在
        print("\n1. 检查集合是否存在:")
        exists = await manager.check_collection_exists(paper_collection_name)
        print(f"   集合 '{paper_collection_name}' 是否存在: {exists}")
        
        if not exists:
            print("❌ 集合不存在，请先运行 rag_collection_manager.py 创建集合")
            return False
        
        # 2. 获取集合信息
        print("\n2. 获取集合信息:")
        collection = await manager.get_collection(paper_collection_name)
        print(f"   集合名称: {collection.name}")
        print(f"   集合中的记录数: {collection.count()}")
        
        if collection.count() == 0:
            print("❌ 集合中没有数据，请先运行 rag_collection_manager.py 加载数据")
            return False
        
        # 3. 打印一个示例块
        print("\n3. 打印一个示例块:")
        # 获取集合中的第一条数据
        sample_data = collection.get(
            include=["metadatas", "documents"],
            limit=1
        )
        
        if sample_data and sample_data.get("documents") and sample_data["documents"]:
            sample_doc = sample_data["documents"][0]
            sample_meta = sample_data["metadatas"][0]
            print(f"   示例块内容:")
            print(f"   论文名称: {sample_meta.get('paper_name', '未知')}")
            print(f"   文件名称: {sample_meta.get('file_name', '未知')}")
            print(f"   块索引: {sample_meta.get('chunk_index', '未知')}/{sample_meta.get('total_chunks', '未知')}")
            print(f"   块大小: {sample_meta.get('chunk_size', '未知')} 字符")
            print(f"   内容预览: {sample_doc}...")
        else:
            print("❌ 无法获取示例数据")
        
        # 4. 以"NO污染物"为query进行检索
        print("\n4. 以'NO污染物'为query进行检索:")
        query_text = "NO pollution"
        print(f"   查询关键词: '{query_text}'")
        
        # 执行语义查询
        results = collection.query(
            query_texts=[query_text],
            n_results=5,
            include=["metadatas", "documents", "distances"]
        )
        
        print(f"   查询结果数量: {len(results['ids'][0]) if results['ids'] else 0}")
        
        # 打印检索结果
        if results and results['ids'] and results['ids'][0]:
            print("\n   检索结果:")
            for i, (id, doc, meta, dist) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                print(f"\n   结果 {i}:")
                print(f"   ID: {id}")
                print(f"   相似度: {1.0 / (1.0 + float(dist)):.4f}")
                print(f"   论文名称: {meta.get('paper_name', '未知')}")
                print(f"   文件名称: {meta.get('file_name', '未知')}")
                print(f"   块索引: {meta.get('chunk_index', '未知')}/{meta.get('total_chunks', '未知')}")
                print(f"   内容预览: {doc}")
        else:
            print("❌ 未找到相关结果")
        
        # 5. 以其他关键词进行检索
        print("\n5. 以'air pollution'为query进行检索:")
        query_text = "air pollution"
        print(f"   查询关键词: '{query_text}'")
        
        # 执行语义查询
        results = collection.query(
            query_texts=[query_text],
            n_results=5,
            include=["metadatas", "documents", "distances"]
        )
        
        print(f"   查询结果数量: {len(results['ids'][0]) if results['ids'] else 0}")
        
        if results and results['ids'] and results['ids'][0]:
            print("\n   检索结果:")
            for i, (id, doc, meta, dist) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                print(f"\n   结果 {i}:")
                print(f"   ID: {id}")
                print(f"   相似度: {1.0 / (1.0 + float(dist)):.4f}")
                print(f"   论文名称: {meta.get('paper_name', '未知')}")
                print(f"   文件名称: {meta.get('file_name', '未知')}")
                print(f"   内容预览: {doc[:150]}...")
        
        print("\n=== 测试完成 ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_paper_rag_query())
    sys.exit(0 if result else 1)
