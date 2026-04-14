"""
【功能】测试 strategy_multimodal_search；内含硬编码 chdir 到旧 ToRAGLENS 路径，易失效。
【长期价值】历史调试脚本；可删或改为相对路径/环境变量。
"""
import asyncio
import os

# 设置当前工作目录为项目根目录
os.chdir("c:\liuxingyu\multisubspace-data\ToRAGLENS\ToRAGLENSBack")

async def test_multimodal_agent():
    print("测试多智能体系统的多模态检索功能...")
    
    # 导入模块
    try:
        from scientific_tools import strategy_multimodal_search
        print("✅ 成功导入strategy_multimodal_search函数")
    except Exception as e:
        print(f"❌ 导入strategy_multimodal_search函数失败: {e}")
        return
    
    # 测试strategy_multimodal_search函数
    try:
        # 测试1: 使用有效的图片路径
        print("\n1. 测试使用有效的图片路径:")
        results = await strategy_multimodal_search(
            query_image_path="allimages/Compass Towards Better Causal Analysis of Urban Time Series/figure_6.jpg"
        )
        print(f"   检索结果数量: {len(results)}")
        if results:
            print(f"   成功获取结果")
        
        # 测试2: 不提供图片路径
        print("\n2. 测试不提供图片路径:")
        results = await strategy_multimodal_search()
        print(f"   检索结果数量: {len(results)}")
        
        # 测试3: 尝试使用query_text参数（应该失败）
        print("\n3. 测试使用query_text参数（应该失败）:")
        try:
            results = await strategy_multimodal_search(query_text="时空数据")
            print(f"   检索结果数量: {len(results)}")
        except TypeError as e:
            print(f"   预期的错误: {e}")
            print(f"   ✅ 正确拒绝了query_text参数")
        
        print("\n✅ 多智能体系统的多模态检索功能测试完成！")
        
    except Exception as e:
        print(f"❌ 测试strategy_multimodal_search函数失败: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    asyncio.run(test_multimodal_agent())