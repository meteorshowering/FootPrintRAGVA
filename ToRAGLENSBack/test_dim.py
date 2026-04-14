"""
【功能】打印 multimodal2text 集合中一条记录的 embedding 维度（调试用）。
【长期价值】一次性调试脚本；可删。
"""
import os
import sys
import asyncio
from rag_collection_manager import MultimodalRAGManager

async def test_dim():
    manager = MultimodalRAGManager()
    await manager.initialize()
    col = manager.chroma_client.get_collection("multimodal2text")
    res = col.get(limit=1, include=["embeddings"])
    try:
        print("Dim:", len(res["embeddings"][0]))
    except Exception as e:
        print(e)

asyncio.run(test_dim())
