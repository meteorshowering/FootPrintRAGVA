#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【功能】使用新的分块逻辑重建 paper_rag_collection：删除旧集合并通过 PaperRAGManager 重新加载。
【长期价值】运维脚本可保留；论文库升级时运行。
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_collection_manager import PaperRAGManager

async def main():
    """主函数"""
    print("开始更新论文向量库...")
    print("=" * 50)
    
    # 创建PaperRAGManager实例
    manager = PaperRAGManager()
    
    # 重新加载论文到集合
    collection_name = "paper_rag_collection"
    
    try:
        # 初始化管理器
        await manager.initialize()
        
        # 删除旧的集合（如果存在）
        if await manager.check_collection_exists(collection_name):
            print(f"删除旧的集合: {collection_name}")
            await manager.delete_collection(collection_name)
        
        # 加载论文到新集合
        await manager.load_papers_to_collection(collection_name)
        
        print("\n" + "=" * 50)
        print("论文向量库更新完成！")
        
    except Exception as e:
        print(f"更新过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
