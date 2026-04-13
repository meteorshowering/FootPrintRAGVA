import asyncio
from rag_service import get_rag_service

async def test_multimodal_search_simple():
    print("测试简化版多模态检索功能...")
    service = await get_rag_service()
    
    # 测试文本到多模态检索
    print("\n1. 测试文本到多模态检索:")
    try:
        results = await service.query_by_multimodal(query_image_path="allimages/Compass Towards Better Causal Analysis of Urban Time Series/figure_5.jpg")
        print(f"   检索结果数量: {len(results)}")
        if results:
            for i, result in enumerate(results[:3]):
                print(f"   结果 {i+1}: {result['id']} - {result['score']:.2f}")
                # 尝试解析full_json获取标题
                try:
                    full_json = result['metadata'].get('full_json', '')
                    if full_json:
                        import json
                        full_data = json.loads(full_json)
                        title = full_data.get('title', 'No Title')
                        print(f"      标题: {title}")
                except Exception as e:
                    print(f"      无法解析标题: {e}")
    except Exception as e:
        print(f"   检索出错: {e}")
    
    print("\n简化版多模态检索测试完成！")

if __name__ == "__main__":
    asyncio.run(test_multimodal_search_simple())