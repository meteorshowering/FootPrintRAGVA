import asyncio

from connection import ConnectionManager
from engine import run_rag_workflow


async def main():
    """
    简单测试 InteractionSummaryAgent / 整个 RAG workflow 的脚本。
    直接在本地起一个 ConnectionManager，不连前端 WebSocket，
    主要用于确认整条链路能跑通、不会在 Summary 阶段报错。
    """
    print("开始测试 InteractionSummaryAgent...")

    manager = ConnectionManager()
    query = "What are the main sources of air pollution from industrial production and how can factories reduce their emissions?"

    await run_rag_workflow(query, manager)

    print("测试完成")


if __name__ == "__main__":
    asyncio.run(main())
