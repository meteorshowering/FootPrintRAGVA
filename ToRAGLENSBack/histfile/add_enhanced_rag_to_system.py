#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【功能】从 enhanced_rag_data.json 导入增强 RAG 条目，写入 Chroma 集合（content + metadata）。
【长期价值】histfile 历史脚本；若当前流程已不用该 JSON，可归档或删除。
"""

import json
import os
import asyncio
from typing import List, Dict, Any
from pathlib import Path

# 导入RAG系统相关模块
try:
    from rag_collection_manager import RAGCollectionManager
    from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig
    from autogen_core.memory import MemoryContent, MemoryMimeType
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"RAG系统导入失败: {e}")
    RAG_AVAILABLE = False


class EnhancedRAGDataImporter:
    """增强版RAG数据导入器"""
    
    def __init__(self, 
                 enhanced_rag_data_path: str = "enhanced_rag_output/enhanced_rag_data.json",
                 collection_name: str = "enhanced_rag_collection",
                 db_persistence_path: str = ".chromadb_autogen"):
        """
        初始化增强版RAG数据导入器
        
        Args:
            enhanced_rag_data_path: 增强版RAG数据文件路径
            collection_name: RAG集合名称
            db_persistence_path: 数据库持久化路径
        """
        self.enhanced_rag_data_path = enhanced_rag_data_path
        self.collection_name = collection_name
        self.db_persistence_path = db_persistence_path
        
        # 数据存储
        self.enhanced_rag_data = []
        self.rag_manager = None
        self.rag_memory = None
        
        # 统计信息
        self.stats = {
            "total_items": 0,
            "successful_adds": 0,
            "failed_adds": 0,
            "text_items": 0,
            "picture_items": 0
        }
    
    def load_enhanced_rag_data(self) -> List[Dict]:
        """加载增强版RAG数据"""
        print("正在加载增强版RAG数据...")
        
        if not os.path.exists(self.enhanced_rag_data_path):
            print(f"增强版RAG数据文件不存在: {self.enhanced_rag_data_path}")
            return []
        
        try:
            with open(self.enhanced_rag_data_path, 'r', encoding='utf-8') as f:
                self.enhanced_rag_data = json.load(f)
            
            self.stats["total_items"] = len(self.enhanced_rag_data)
            self.stats["text_items"] = len([item for item in self.enhanced_rag_data if item.get("type") == "texture"])
            self.stats["picture_items"] = len([item for item in self.enhanced_rag_data if item.get("type") == "picture"])
            
            print(f"成功加载 {len(self.enhanced_rag_data)} 条增强版RAG数据")
            print(f"文本数据: {self.stats['text_items']} 条")
            print(f"图片数据: {self.stats['picture_items']} 条")
            
            return self.enhanced_rag_data
            
        except Exception as e:
            print(f"加载增强版RAG数据失败: {e}")
            return []
    
    async def initialize_rag_system(self) -> bool:
        """初始化RAG系统"""
        if not RAG_AVAILABLE:
            print("RAG系统不可用，无法继续")
            return False
        
        print("正在初始化RAG系统...")
        
        try:
            # 初始化RAG管理器
            self.rag_manager = RAGCollectionManager(self.db_persistence_path)
            await self.rag_manager.initialize()
            
            # 创建或获取集合
            collection = await self.rag_manager.get_collection(self.collection_name)
            if not collection:
                print(f"集合 {self.collection_name} 不存在，创建新集合")
                collection = await self.rag_manager.create_collection(self.collection_name)
            else:
                print(f"集合 {self.collection_name} 已存在，将添加新数据")
            
            # 创建RAG内存实例
            config = PersistentChromaDBVectorMemoryConfig(
                collection_name=self.collection_name,
                persist_directory=self.db_persistence_path
            )
            self.rag_memory = ChromaDBVectorMemory(config)
            
            print("RAG系统初始化完成")
            return True
            
        except Exception as e:
            print(f"RAG系统初始化失败: {e}")
            return False
    
    def prepare_metadata(self, item: Dict) -> Dict[str, Any]:
        """准备RAG metadata，包含所有enhanced_rag_data的字段（除了content）"""
        metadata = {}
        
        # 添加所有enhanced_rag_data的字段到metadata
        for key, value in item.items():
            if key != "content":  # 排除content字段，因为它将作为检索内容
                # 处理特殊类型的值
                if isinstance(value, (dict, list)):
                    # 将复杂类型转换为JSON字符串
                    metadata[key] = json.dumps(value, ensure_ascii=False)
                else:
                    metadata[key] = value
        
        # 确保必要的字段存在
        if "chunkid" not in metadata:
            metadata["chunkid"] = "unknown"
        if "paperid" not in metadata:
            metadata["paperid"] = "unknown"
        if "type" not in metadata:
            metadata["type"] = "unknown"
        
        return metadata
    
    async def add_item_to_rag(self, item: Dict) -> bool:
        """将单个数据项添加到RAG系统"""
        if not self.rag_memory:
            print("RAG系统未初始化，无法添加数据")
            return False
        
        try:
            # 获取content作为检索内容
            content = item.get("content", "")
            if not content:
                print(f"数据项 {item.get('chunkid', 'unknown')} 缺少content字段，跳过")
                return False
            
            # 准备metadata
            metadata = self.prepare_metadata(item)
            
            # 添加到RAG系统
            success = await self.rag_manager.add_data_to_collection(
                self.rag_memory, content, metadata
            )
            
            if success:
                self.stats["successful_adds"] += 1
                return True
            else:
                self.stats["failed_adds"] += 1
                return False
                
        except Exception as e:
            print(f"添加数据项 {item.get('chunkid', 'unknown')} 失败: {e}")
            self.stats["failed_adds"] += 1
            return False
    
    async def add_all_data_to_rag(self, batch_size: int = 100) -> bool:
        """将所有数据添加到RAG系统"""
        if not self.enhanced_rag_data:
            print("没有数据可添加")
            return False
        
        print(f"开始将 {len(self.enhanced_rag_data)} 条数据添加到RAG系统...")
        
        total_items = len(self.enhanced_rag_data)
        
        for i in range(0, total_items, batch_size):
            batch = self.enhanced_rag_data[i:i + batch_size]
            batch_number = (i // batch_size) + 1
            total_batches = (total_items + batch_size - 1) // batch_size
            
            print(f"处理批次 {batch_number}/{total_batches} ({len(batch)} 条数据)...")
            
            # 并发处理批次
            tasks = [self.add_item_to_rag(item) for item in batch]
            results = await asyncio.gather(*tasks)
            
            successful_in_batch = sum(results)
            print(f"批次 {batch_number} 完成: {successful_in_batch}/{len(batch)} 成功")
        
        print("所有数据添加完成")
        return True
    
    def print_statistics(self):
        """打印统计信息"""
        print("\n=== 数据添加统计 ===")
        print(f"总数据项数: {self.stats['total_items']}")
        print(f"文本数据项: {self.stats['text_items']}")
        print(f"图片数据项: {self.stats['picture_items']}")
        print(f"成功添加: {self.stats['successful_adds']}")
        print(f"添加失败: {self.stats['failed_adds']}")
        
        success_rate = (self.stats['successful_adds'] / self.stats['total_items'] * 100) if self.stats['total_items'] > 0 else 0
        print(f"成功率: {success_rate:.2f}%")
    
    async def run(self):
        """运行完整的导入流程"""
        print("开始将增强版RAG数据添加到系统...")
        
        # 1. 加载数据
        self.load_enhanced_rag_data()
        
        if not self.enhanced_rag_data:
            print("数据加载失败，无法继续")
            return
        
        # 2. 初始化RAG系统
        if not await self.initialize_rag_system():
            print("RAG系统初始化失败，无法继续")
            return
        
        # 3. 添加数据到RAG系统
        await self.add_all_data_to_rag()
        
        # 4. 打印统计信息
        self.print_statistics()
        
        print("\n增强版RAG数据添加完成！")
        print(f"集合名称: {self.collection_name}")
        print(f"数据库路径: {self.db_persistence_path}")


async def main():
    """主函数"""
    # 创建增强版RAG数据导入器
    importer = EnhancedRAGDataImporter(
        enhanced_rag_data_path="enhanced_rag_output/enhanced_rag_data.json",
        collection_name="enhanced_rag_collection",
        db_persistence_path=".chromadb_autogen"
    )
    
    # 运行导入流程
    await importer.run()


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())