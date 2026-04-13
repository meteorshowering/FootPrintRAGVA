#!/usr/bin/env python3
"""
测试集合管理功能
"""

import asyncio
import sys
from rag_collection_manager import get_rag_collection_manager

async def test_collection_management():
    """测试集合管理功能"""
    print("=== 测试集合管理功能 ===\n")
    
    try:
        # 获取集合管理器
        manager = await get_rag_collection_manager()
        print("✅ 成功获取集合管理器实例")
        
        # 测试集合名称
        test_collection_name = "test_collection"
        
        # 1. 测试检查集合是否存在
        print("\n1. 测试检查集合是否存在:")
        exists = await manager.check_collection_exists(test_collection_name)
        print(f"   集合 '{test_collection_name}' 是否存在: {exists}")
        
        # 2. 测试创建集合
        print("\n2. 测试创建集合:")
        collection = await manager.create_collection(test_collection_name)
        print(f"   创建集合成功: {collection.name}")
        
        # 3. 测试再次检查集合是否存在
        print("\n3. 测试再次检查集合是否存在:")
        exists = await manager.check_collection_exists(test_collection_name)
        print(f"   集合 '{test_collection_name}' 是否存在: {exists}")
        assert exists, "集合应该存在"
        
        # 4. 测试获取集合
        print("\n4. 测试获取集合:")
        retrieved_collection = await manager.get_collection(test_collection_name)
        print(f"   获取集合成功: {retrieved_collection.name if retrieved_collection else '失败'}")
        assert retrieved_collection, "应该能够获取集合"
        
        # 5. 测试获取或创建集合（使用现有集合）
        print("\n5. 测试获取或创建集合（使用现有集合）:")
        get_or_create_collection = await manager.get_or_create_collection(test_collection_name)
        print(f"   获取或创建集合成功: {get_or_create_collection.name}")
        
        # 6. 测试创建RAG内存
        print("\n6. 测试创建RAG内存:")
        rag_memory = await manager.create_rag_memory(test_collection_name)
        print(f"   创建RAG内存成功")
        
        # 7. 测试添加数据
        print("\n7. 测试添加数据:")
        test_content = "这是测试内容，用于验证数据添加功能"
        test_metadata = {"test_key": "test_value", "test_number": 123}
        success = await manager.add_data_to_collection(rag_memory, test_content, test_metadata)
        print(f"   添加数据成功: {success}")
        assert success, "添加数据应该成功"
        
        # 8. 测试删除集合
        print("\n8. 测试删除集合:")
        delete_success = await manager.delete_collection(test_collection_name)
        print(f"   删除集合成功: {delete_success}")
        assert delete_success, "删除集合应该成功"
        
        # 9. 测试再次检查集合是否存在（应该不存在）
        print("\n9. 测试再次检查集合是否存在（应该不存在）:")
        exists = await manager.check_collection_exists(test_collection_name)
        print(f"   集合 '{test_collection_name}' 是否存在: {exists}")
        assert not exists, "集合应该不存在"
        
        print("\n=== 所有测试通过 ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
if __name__ == "__main__":
    result = asyncio.run(test_collection_management())
    sys.exit(0 if result else 1)
