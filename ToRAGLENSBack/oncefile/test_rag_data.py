#!/usr/bin/env python3
"""
【功能】get_rag_service 后重置并打印 RAG 库数据样例。
【长期价值】调试脚本；可删。
"""

import asyncio
import sys
import json
from rag_service import get_rag_service

async def test_rag_data():
    """测试rag库中的数据"""
    print("=== RAG库数据测试 ===\n")
    
    try:
        # 获取rag服务实例，添加重置数据选项
        service = await get_rag_service()
        
        # 强制重置数据，确保使用新的JSON文件
        print(f"   强制重置数据，确保使用新的JSON文件...")
        # 关闭现有服务
        await service.close()
        # 重新获取服务实例
        service = await get_rag_service()
        # 直接初始化并重置数据
        await service.initialize(reset_data=True)
        
        print("✅ 成功获取RAG服务实例\n")
        
        # 1. 测试语义搜索
        print("1. 测试语义搜索示例:")
        query = "SO2空气污染"
        semantic_results, _trace = await service.query_by_semantic(query_text=query, n_results=3)
        print(f"   搜索关键词: {query}")
        print(f"   搜索结果数量: {len(semantic_results)}")
        
        if semantic_results:
            for i, result in enumerate(semantic_results, 1):
                print(result['metadata'])
                print(f"   \n   示例 {i}:")
                print(f"   ID: {result['id']}")
                print(f"   分数: {result['score']:.4f}")
                print(f"   内容类型: {type(result['content'])}")
                
                # 打印结构化内容
                if isinstance(result['content'], dict):
                    print(f"   结构化内容: {result['content']}")
                    print(f"   标题: {result['content'].get('title', '无标题')[:50]}...")
                    if 'summary' in result['content']:
                        print(f"   摘要: {result['content']['summary'][:100]}...")
                    if 'insight' in result['content']:
                        print(f"   洞察: {result['content']['insight'][:100]}...")
                else:
                    print(f"   内容: {result['content'][:100]}...")
                
                print(f"   元数据: {list(result['metadata'].keys())[:10]}")
                # 检查是否包含full_json
                if 'full_json' in result['metadata']:
                    print(f"   full_json存在，长度: {len(result['metadata']['full_json'])}...")
                else:
                    print(f"   full_json不存在")
        print()
        
        # 2. 测试本地过滤搜索
        print("2. 测试本地过滤搜索示例:")
        keywords = ["PM2.5"]
        local_results = await service.query_by_local_filter(keywords=keywords)
        print(f"   过滤关键词: {keywords}")
        print(f"   搜索结果数量: {len(local_results)}")
        
        if local_results:
            for i, result in enumerate(local_results[:2], 1):
                print(f"   \n   示例 {i}:")
                print(f"   ID: {result['id']}")
                print(f"   分数: {result['score']:.4f}")
                if isinstance(result['content'], dict):
                    print(f"   标题: {result['content'].get('title', '无标题')[:50]}...")
                    print(f"   关键词: {result['content'].get('key_entities', [])[:3]}...")
        print()
        
        # 3. 测试本地缓存数据
        print("3. 本地缓存数据示例:")
        print(f"   本地缓存数据数量: {len(service.local_data_cache)}")
        if service.local_data_cache:
            for i, item in enumerate(service.local_data_cache[:2], 1):
                print(f"   \n   示例 {i}:")
                print(f"   ID: {item.get('id', '无ID')}")
                print(f"   标题: {item.get('title', '无标题')[:50]}...")
                print(f"   类型: {item.get('visual_type', {}).get('main_type', '无类型')}")
                print(f"   保存路径: {item.get('save_path', '无路径')[:60]}...")
        print()
        
        # 4. 测试向量数据库信息
        print("4. 向量数据库信息:")
        print(f"   向量集合名称: {service.collection_name}")
        print(f"   多模态集合名称: {service.multimodal_collection_name}")
        if hasattr(service, 'raw_collection') and service.raw_collection:
            print(f"   向量集合记录数: {service.raw_collection.count()}")
        if hasattr(service, 'multimodal_collection') and service.multimodal_collection:
            print(f"   多模态集合记录数: {service.multimodal_collection.count()}")
        print()
        
        # 5. 打印一条完整的结构化数据
        print("5. 完整结构化数据示例:")
        if service.local_data_cache:
            full_item = service.local_data_cache[0]
            print(json.dumps(full_item, ensure_ascii=False, indent=2)[:1000] + "...")
        
        # 6. 检查数据重复情况
        print("\n6. 数据重复检查:")
        try:
            # 获取向量集合中的所有数据
            all_embeddings = service.raw_collection.get(
                include=["metadatas", "documents"]
            )
            
            if all_embeddings and all_embeddings.get("ids"):
                ids = all_embeddings["ids"]
                metadatas = all_embeddings["metadatas"]
                documents = all_embeddings["documents"]
                
                print(f"   向量集合总记录数: {len(ids)}")
                
                # 检查ID重复情况
                unique_ids = set(ids)
                print(f"   唯一ID数量: {len(unique_ids)}")
                print(f"   ID重复数量: {len(ids) - len(unique_ids)}")
                
                # 检查文档内容重复情况
                unique_documents = set(documents)
                print(f"   唯一文档数量: {len(unique_documents)}")
                print(f"   文档重复数量: {len(documents) - len(unique_documents)}")
                
                # 检查元数据重复情况
                unique_metadatas = set()
                for meta in metadatas:
                    # 将元数据转换为可哈希的字符串，忽略顺序
                    if isinstance(meta, dict):
                        meta_str = json.dumps(meta, sort_keys=True, ensure_ascii=False)
                        unique_metadatas.add(meta_str)
                print(f"   唯一元数据数量: {len(unique_metadatas)}")
                print(f"   元数据重复数量: {len(metadatas) - len(unique_metadatas)}")
                
                # 检查具体哪些ID重复
                if len(ids) > len(unique_ids):
                    print("   重复的ID列表:")
                    id_counts = {}
                    for id in ids:
                        id_counts[id] = id_counts.get(id, 0) + 1
                    
                    for id, count in id_counts.items():
                        if count > 1:
                            print(f"     - {id}: 重复 {count} 次")
            else:
                print("   向量集合中没有数据")
        except Exception as e:
            print(f"   检查数据重复时出错: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await service.close()
    
    print("\n=== 测试完成 ===")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_rag_data())
    sys.exit(0 if result else 1)
