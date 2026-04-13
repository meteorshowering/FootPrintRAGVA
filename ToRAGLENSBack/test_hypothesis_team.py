"""
测试 HypothesisGeneratorAgent Team 的脚本
从 experiment_results JSON 文件解析数据，测试报告生成
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List

# 导入必要的模块
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo
from protocols import ResearchGraph, GraphNode, ItemEvaluation, ExperimentResult, TaskComplete, IterationResult, QueryResult, OrchestratorPlan
from engine import HypothesisGeneratorAgent
from autogen_core import CancellationToken


def load_experiment_results(json_path: str) -> Dict[str, Any]:
    """从 JSON 文件加载实验结果"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_research_graph_from_experiment(experiment_data: Dict[str, Any]) -> ResearchGraph:
    """从实验结果构建 ResearchGraph"""
    root_goal = experiment_data.get("root_goal", "")
    nodes: Dict[str, GraphNode] = {}
    
    # 遍历所有 iterations 和 query_results，构建节点
    node_id_counter = 1
    for iteration in experiment_data.get("iterations", []):
        for query_result in iteration.get("query_results", []):
            plan = query_result.get("orchestrator_plan", {})
            plan_id = str(node_id_counter)
            node_id_counter += 1
            
            # 创建计划节点（如果有）
            if plan:
                plan_node = GraphNode(
                    id=plan_id,
                    type="PLAN",
                    status="ACTIVE",
                    content={"tool_name": plan.get("tool_name", ""), "args": plan.get("args", {})},
                    metadata={},
                    ParentNode=plan.get("ParentNode", "0"),
                    source_tool=plan.get("tool_name", ""),
                    source_args=plan.get("args", {}),
                    source_reason=plan.get("reason", ""),
                    created_at_round=iteration.get("round_number", 0)
                )
                nodes[plan_id] = plan_node
            
            # 创建证据节点
            for rag_result in query_result.get("rag_results", []):
                retrieval = rag_result.get("retrieval_result", {})
                evaluation = rag_result.get("evaluation")
                
                evidence_id = retrieval.get("id", f"evidence_{node_id_counter}")
                node_id_counter += 1
                
                # 构建评估信息
                eval_obj = None
                if evaluation:
                    eval_obj = ItemEvaluation(
                        target_evidence_id=evaluation.get("target_evidence_id", evidence_id),
                        branch_action=evaluation.get("branch_action", "KEEP"),
                        extracted_insight=evaluation.get("extracted_insight", ""),
                        scores=evaluation.get("scores", {}),
                        reason=evaluation.get("reason", ""),
                        suggested_keywords=evaluation.get("suggested_keywords", [])
                    )
                
                # 构建节点内容
                content = retrieval.get("content", {})
                if isinstance(content, dict):
                    # 如果 content 是字典，提取 text 字段
                    text_content = content.get("text", "")
                    title = content.get("title", "")
                    summary = content.get("summary", "")
                    insight = content.get("insight", "")
                else:
                    text_content = str(content)
                    title = ""
                    summary = ""
                    insight = ""
                
                node_content = {
                    "title": title or text_content[:100] if text_content else "",
                    "summary": summary or text_content[:500] if text_content else "",
                    "insight": insight or "",
                    "text": text_content
                }
                
                # 构建元数据
                metadata = retrieval.get("metadata", {})
                node_metadata = {
                    "paper_id": metadata.get("paperid") or metadata.get("paper_id", ""),
                    "key_entities": metadata.get("key_entities", []),
                    "figure_type": metadata.get("type", ""),
                    "chunkid": metadata.get("chunkid", "")
                }
                
                # 创建证据节点
                evidence_node = GraphNode(
                    id=evidence_id,
                    type="EVIDENCE",
                    status="ACTIVE" if eval_obj and eval_obj.branch_action != "PRUNE" else "PRUNED",
                    content=node_content,
                    metadata=node_metadata,
                    ParentNode=plan_id if plan else "0",
                    source_tool=retrieval.get("source_tool", ""),
                    source_args=retrieval.get("source_args", {}),
                    created_at_round=iteration.get("round_number", 0),
                    evaluation=eval_obj
                )
                nodes[evidence_id] = evidence_node
                
                # 更新父节点的 children_ids
                if plan_id in nodes:
                    nodes[plan_id].children_ids.append(evidence_id)
    
    # 构建 ResearchGraph
    graph = ResearchGraph(root_goal=root_goal, nodes=nodes)
    
    return graph


def build_experiment_result_from_json(experiment_data: Dict[str, Any]) -> ExperimentResult:
    """从 JSON 数据构建 ExperimentResult 对象"""
    from protocols import IterationResult, QueryResult, OrchestratorPlan, RagResult
    
    root_goal = experiment_data.get("root_goal", "")
    iterations = []
    
    for iter_data in experiment_data.get("iterations", []):
        round_number = iter_data.get("round_number", 0)
        query_results = []
        
        for qr_data in iter_data.get("query_results", []):
            # 构建 OrchestratorPlan
            plan_data = qr_data.get("orchestrator_plan", {})
            orchestrator_plan = None
            if plan_data:
                orchestrator_plan = OrchestratorPlan(
                    action=plan_data.get("action", ""),
                    tool_name=plan_data.get("tool_name"),
                    ParentNode=plan_data.get("ParentNode"),
                    args=plan_data.get("args", {}),
                    reason=plan_data.get("reason", ""),
                    total_results=plan_data.get("total_results", 0),
                    duplicate_results=plan_data.get("duplicate_results", 0),
                    plansummary=plan_data.get("plansummary")
                )
            
            # 构建 rag_results（保持原始格式，因为后续需要访问 node_id）
            rag_results = []
            for rag_data in qr_data.get("rag_results", []):
                # 保持原始字典格式，方便后续访问
                rag_results.append(rag_data)
            
            # 构建 QueryResult
            query_result = QueryResult(
                orchestrator_plan=orchestrator_plan,
                rag_results=rag_results  # 保持原始格式，后续会转换为字典访问
            )
            query_results.append(query_result)
        
        iteration = IterationResult(
            round_number=round_number,
            query_results=query_results
        )
        iterations.append(iteration)
    
    experiment_result = ExperimentResult(
        root_goal=root_goal,
        iterations=iterations,
        summary=None  # 可以后续添加
    )
    
    return experiment_result


async def test_hypothesis_team(json_path: str):
    """测试 HypothesisGeneratorAgent Team"""
    print(f"[INFO] 加载实验结果: {json_path}")
    experiment_data = load_experiment_results(json_path)
    
    print(f"[INFO] 构建 ResearchGraph...")
    graph = build_research_graph_from_experiment(experiment_data)
    print(f"   - 根目标: {graph.root_goal}")
    print(f"   - 节点总数: {len(graph.nodes)}")
    
    active_nodes = [nid for nid, node in graph.nodes.items() if node.status == "ACTIVE" and node.type == "EVIDENCE"]
    print(f"   - 活跃证据节点: {len(active_nodes)}")
    
    # 构建 ExperimentResult
    print(f"[INFO] 构建 ExperimentResult...")
    experiment_result = build_experiment_result_from_json(experiment_data)
    print(f"   - 迭代轮数: {len(experiment_result.iterations)}")
    
    # 统计 plan summaries
    plan_summary_count = 0
    for iteration in experiment_result.iterations:
        for qr in iteration.query_results:
            if qr.orchestrator_plan and qr.orchestrator_plan.plansummary:
                plan_summary_count += 1
    print(f"   - Plan summaries 数量: {plan_summary_count}")
    
    # 初始化模型客户端
    print(f"[INFO] 初始化模型客户端...")
    model_client = OpenAIChatCompletionClient(
        model="deepseek-r1:671b-0528",
        base_url="https://uni-api.cstcloud.cn/v1",
        api_key="f24a9af08a33a9649b3f149706c8c45e8602a884b8beab6abae0d608226477f8",
        model_info=ModelInfo(
            vision=False,
            structured_output=False,
            function_calling=True,
            streaming=True,
            json_output=False,
            family="deepseek",
            context_length=65536,
        )
    )
    
    # 创建 HypothesisGeneratorAgent（作为协调者）
    print(f"[INFO] 创建 HypothesisGeneratorAgent...")
    hypothesis_agent = HypothesisGeneratorAgent(model_client, None)
    
    # 创建 TaskComplete 消息（包含 experiment_result）
    task_complete = TaskComplete(graph_snapshot=graph, experiment_result=experiment_result)
    
    # 创建消息上下文（简化版）
    # MessageContext 通常由 runtime 自动创建，这里创建一个简单的 mock
    class MockMessageContext:
        def __init__(self):
            self.cancellation_token = CancellationToken()
            self.agent_id = "test"
        
        async def publish_message(self, message, topic_id):
            # Mock 方法，不做实际操作
            pass
    
    ctx = MockMessageContext()
    
    # 调用 handle_task_complete
    print(f"[INFO] 开始生成报告...")
    print("=" * 80)
    await hypothesis_agent.handle_task_complete(task_complete, ctx)
    print("=" * 80)
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "logs"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"hypothesis_report_{timestamp}.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Hypothesis Generator Team 测试报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"源文件: {json_path}\n")
        f.write(f"根目标: {graph.root_goal}\n")
        f.write(f"活跃节点数: {len(active_nodes)}\n\n")
        f.write("=" * 80 + "\n\n")
        f.write(hypothesis_agent.report_content)
    
    print(f"\n[SUCCESS] 报告已保存到: {output_file}")
    print(f"\n[INFO] 报告预览（前500字符）:")
    print("-" * 80)
    print(hypothesis_agent.report_content[:500])
    print("-" * 80)
    
    return hypothesis_agent.report_content


async def main():
    """主函数"""
    # 使用提供的 JSON 文件路径
    json_path = r"mapdesignpre/mapfront/mapfront/public/experiment_results_20260211_151405.json"
    
    # 如果文件不存在，尝试其他路径
    if not os.path.exists(json_path):
        json_path = r"logs/experiment_results_20260211_151405.json"
    
    if not os.path.exists(json_path):
        print(f"[ERROR] 找不到文件: {json_path}")
        print("请确保文件存在，或修改 json_path 变量")
        return
    
    try:
        report = await test_hypothesis_team(json_path)
        print("\n[SUCCESS] 测试完成！")
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
