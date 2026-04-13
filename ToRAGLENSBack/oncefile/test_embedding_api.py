#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试嵌入API配置
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_collection_manager import RAGCollectionManager, PaperRAGManager

async def test_embedding_api():
    """测试嵌入API是否正常工作"""
    print("测试嵌入API配置...")
    print("=" * 50)
    
    # 创建RAGCollectionManager实例
    manager = RAGCollectionManager()
    await manager.initialize()
    
    # 测试获取嵌入向量
    test_text = "这是一段测试文本，用于测试嵌入API是否正常工作。"
    print(f"测试文本: {test_text}")
    print("-" * 30)
    
    embedding = manager.get_embedding_from_api(test_text)
    
    if embedding:
        print(f"✅ 成功获取嵌入向量")
        print(f"向量长度: {len(embedding)}")
        print(f"向量前5个值: {embedding[:5]}")
        print(f"使用的模型: {manager.embedding_api_config['model']}")
        print(f"API URL: {manager.embedding_api_config['url']}")
    else:
        print("❌ 获取嵌入向量失败")
    
    print("=" * 50)

async def test_paper_collection():
    """测试论文集合加载"""
    print("\n测试论文集合加载...")
    print("=" * 50)
    
    # 创建PaperRAGManager实例
    manager = PaperRAGManager()
    await manager.initialize()
    
    # 测试处理单个文件
    test_file = None
    paper_md_path = manager.paper_md_path
    
    # 查找第一个MD文件
    for file in os.listdir(paper_md_path):
        if file.endswith('.md'):
            test_file = os.path.join(paper_md_path, file)
            break
    
    if test_file:
        print(f"测试文件: {os.path.basename(test_file)}")
        print("-" * 30)
        
        # 处理文件
        chunk_data = await manager.process_paper_file(test_file)
        print(f"处理结果: {len(chunk_data)} 个块")
        
        # 测试添加数据
        test_collection = "test_paper_collection"
        print(f"\n测试添加数据到集合: {test_collection}")
        
        # 创建测试集合
        await manager.create_collection(test_collection)
        
        # 添加第一个块
        if chunk_data:
            first_chunk = chunk_data[0]
            success = await manager.add_data_with_custom_embedding(
                test_collection,
                first_chunk["content"],
                first_chunk["metadata"]
            )
            
            if success:
                print("✅ 成功添加数据到集合")
                # 验证数据是否添加成功
                collection = await manager.get_collection(test_collection)
                if collection:
                    count = collection.count()
                    print(f"集合中的数据数量: {count}")
            else:
                print("❌ 添加数据失败")
        
        # 删除测试集合
        await manager.delete_collection(test_collection)
        print(f"✅ 删除测试集合: {test_collection}")
    else:
        print("❌ 未找到测试文件")
    
    print("=" * 50)

async def main():
    """主函数"""
    await test_embedding_api()
    await test_paper_collection()
    print("\n测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
