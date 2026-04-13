"""
测试单个策略执行API
"""
import asyncio
import json
from single_strategy_api import execute_single_strategy


async def test_semantic_search():
    """测试语义搜索策略"""
    print("=" * 80)
    print("测试1: 语义搜索策略")
    print("=" * 80)
    
    plan_dict = {
        "action": "call_tool",
        "tool_name": "strategy_semantic_search",
        "ParentNode": "0",
        "args": {
            "query_intent": "how to visualize air pollution data in China"
        },
        "reason": "测试语义搜索策略执行"
    }
    
    root_goal = "how to visualize the data of air pollution in China"
    
    print(f"\n📋 输入策略:")
    print(json.dumps(plan_dict, ensure_ascii=False, indent=2))
    print(f"\n🎯 根目标: {root_goal}")
    print("\n⏳ 开始执行...\n")
    
    try:
        result = await execute_single_strategy(plan_dict, root_goal)
        
        print("\n" + "=" * 80)
        print("✅ 执行成功！返回给前端的数据:")
        print("=" * 80)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n" + "=" * 80)
        print("📊 数据摘要:")
        print("=" * 80)
        print(f"工具名称: {result.get('tool_name')}")
        print(f"总结果数: {result.get('total_results')}")
        print(f"重复结果数: {result.get('duplicate_results')}")
        print(f"父节点: {result.get('ParentNode')}")
        print(f"原因: {result.get('reason')}")
        print(f"\n策略总结 (前500字符):")
        summary = result.get('plansummary', '')
        if summary:
            print(summary[:500] + "..." if len(summary) > 500 else summary)
        else:
            print("(无总结)")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_metadata_search():
    """测试元数据搜索策略"""
    print("\n\n" + "=" * 80)
    print("测试2: 元数据搜索策略")
    print("=" * 80)
    
    plan_dict = {
        "action": "call_tool",
        "tool_name": "strategy_metadata_search",
        "ParentNode": "img_001",
        "args": {
            "paper_id": "13"
        },
        "reason": "测试元数据搜索策略执行，深入挖掘论文ID 13的内容"
    }
    
    root_goal = "how to visualize the data of air pollution in China"
    
    print(f"\n📋 输入策略:")
    print(json.dumps(plan_dict, ensure_ascii=False, indent=2))
    print(f"\n🎯 根目标: {root_goal}")
    print("\n⏳ 开始执行...\n")
    
    try:
        result = await execute_single_strategy(plan_dict, root_goal)
        
        print("\n" + "=" * 80)
        print("✅ 执行成功！返回给前端的数据:")
        print("=" * 80)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n" + "=" * 80)
        print("📊 数据摘要:")
        print("=" * 80)
        print(f"工具名称: {result.get('tool_name')}")
        print(f"总结果数: {result.get('total_results')}")
        print(f"重复结果数: {result.get('duplicate_results')}")
        print(f"父节点: {result.get('ParentNode')}")
        print(f"原因: {result.get('reason')}")
        print(f"\n策略总结 (前500字符):")
        summary = result.get('plansummary', '')
        if summary:
            print(summary[:500] + "..." if len(summary) > 500 else summary)
        else:
            print("(无总结)")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主测试函数"""
    print("\n" + "🚀" * 40)
    print("开始测试单个策略执行API")
    print("🚀" * 40)
    
    # 测试1: 语义搜索
    result1 = await test_semantic_search()
    
    # 测试2: 元数据搜索
    result2 = await test_metadata_search()
    
    print("\n\n" + "=" * 80)
    print("📝 测试总结")
    print("=" * 80)
    print(f"测试1 (语义搜索): {'✅ 成功' if result1 else '❌ 失败'}")
    print(f"测试2 (元数据搜索): {'✅ 成功' if result2 else '❌ 失败'}")
    
    if result1:
        print(f"\n测试1返回的数据结构:")
        print(f"  - action: {result1.get('action')}")
        print(f"  - tool_name: {result1.get('tool_name')}")
        print(f"  - args: {result1.get('args')}")
        print(f"  - total_results: {result1.get('total_results')}")
        print(f"  - duplicate_results: {result1.get('duplicate_results')}")
        print(f"  - plansummary: {'有' if result1.get('plansummary') else '无'}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
