"""
【功能】针对 paper_rag 检索结果做回归打印（多场景标题与摘要）。
【长期价值】调试脚本；可删。
"""
import asyncio
from rag_service import get_rag_service

def print_result_summary(title: str, results: list):
    """打印结果摘要"""
    print(f"\n{'='*60}")
    print(f"🧪 测试场景: {title}")
    print(f"{'-'*60}")
    print(f"📊 结果数量: {len(results)}")
    
    if not results:
        print("⚠️ 未找到结果")
        return

    print(f"🔎 前 3 条详情:")
    for i, result in enumerate(results[:3], 1):
        print(f"\n   结果 {i}:")
        print(f"   - ID: {result.get('id')}")
        print(f"   - Score: {result.get('score'):.4f}")
        
        # 检查关键字段是否存在
        meta = result.get('metadata', {})
        content = result.get('content', {})
        
        print(f"   - 论文名称: {meta.get('paper_name', 'N/A')}")
        print(f"   - 文件名称: {meta.get('file_name', 'N/A')}")
        
        # 获取内容预览
        content_text = ""
        if isinstance(content, dict):
            # 如果是字典，尝试获取文本内容
            if content.get('text'):
                content_text = content.get('text')
            else:
                # 尝试拼接其他字段
                text_parts = []
                for key, value in content.items():
                    if isinstance(value, str) and value:
                        text_parts.append(value)
                content_text = " ".join(text_parts)
        elif isinstance(content, str):
            content_text = content
        
        # 打印内容预览，限制长度
        preview_length = 150
        if content_text:
            preview = content_text[:preview_length]
            # 检查是否以完整句子开头
            first_char = preview[0] if preview else ''
            print(f"   - 内容预览: {preview}...")
            print(f"   - 首字符: '{first_char}' (是否大写: {first_char.isupper() if first_char else False})")
            
            # 检查是否以句子开头
            if first_char and first_char.isupper():
                print(f"   - ✅ 内容以大写字母开头，可能是完整句子")
            else:
                print(f"   - ⚠️ 内容不以大写字母开头，可能不是完整句子")

async def test_paper_rag_query():
    """测试论文RAG查询"""
    print("=== 测试论文RAG查询 ===")
    
    # 获取RAG服务实例，使用论文集合
    service = await get_rag_service(collection_name="paper_rag_collection")
    print("✅ RAG服务初始化完成")
    
    # 测试查询
    test_queries = [
        "vehicle emission factors",
        "air pollution control",
        "biogenic volatile organic"
    ]
    
    for query in test_queries:
        print(f"\n📝 查询: '{query}'")
        results, _trace = await service.query_by_semantic(
            query_text=query,
            n_results=5,
            score_threshold=0.4
        )
        
        print_result_summary(f"查询: '{query}'", results)

if __name__ == "__main__":
    try:
        asyncio.run(test_paper_rag_query())
    except KeyboardInterrupt:
        print("\n测试被中断")
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()
