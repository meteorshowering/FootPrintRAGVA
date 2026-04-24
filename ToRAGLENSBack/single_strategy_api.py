"""
【功能】单个策略执行 API：复刻 engine 中单轮检索/评估/总结，供独立调用或前端实验；定义 SingleStrategyExecutor。
【长期价值】辅助长期维护（与主流程 engine 重复度高）；若只保留一种入口可合并或仅保留测试。
"""
import asyncio
import json
import traceback
import datetime
from typing import List, Dict, Any, Optional

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import SystemMessage, UserMessage
from autogen_core.models import ModelInfo

from scientific_tools import ALL_TOOLS_MAP
from protocols import (
    OrchestratorPlan, RawEvidenceItem, ItemEvaluation,
    RagResult, QueryResult, IterationResult, ExperimentResult,
    WordCloudData, RetrievalQualityEvaluation, SummaryResponse
)
from rag_service import get_rag_service


class SingleStrategyExecutor:
    """单个策略执行器，复刻engine中的检索、评估和总结流程"""
    
    def __init__(self):
        """初始化执行器"""
        # 初始化模型客户端
        self.model_client = OpenAIChatCompletionClient(
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
        
        # 评估器的系统消息
        self.evaluator_system_message = SystemMessage(content="""
        # Role
        You are the **Evaluator** on a scientific literature investigation team.
        The lead scientist sets retrieval directions; many evidence items have already been retrieved.
        Your job is to **evaluate each evidence item independently** and return structured feedback for planning.

        # Evaluation logic
        Read title, summary, and insight carefully. **If an image is available, incorporate visual judgment.**

        1. **branch_action**
           - **GROW**: high-value, strongly relevant, with clear follow-up clues (paper IDs, linked tables, or charts showing important trends).
           - **KEEP**: medium-value, relevant but limited expansion value; keep as context.
           - **PRUNE**: low-value, irrelevant, vague, duplicated, or noisy—drop.

        2. **extracted_insight**
           - Give a concrete scientific observation (not generic praise).

        3. **suggested_keywords**
           - Extract useful technical terms for follow-up search (e.g., model names, methods).

        # Output format (JSON list only, no Markdown)
        Return one JSON list covering all provided items.

        [
          {
            "target_evidence_id": "fig_001",
            "branch_action": "GROW",
            "extracted_insight": "The chart links winter PM2.5 peaks with asthma emergency-visit peaks.",
            "scores":{"relevance": 9, "credibility": 8},
            "reason": "High-value trend evidence with traceable paper metadata.",
            "suggested_keywords": ["time-series analysis", "asthma emergency visits"]
          }
        ]

        # Language
        - Write **all** narrative string fields in **English**.
        """)
        
        # 总结器的系统消息
        self.summary_system_message = SystemMessage(content="""
        # Role
        You are a **Summary Specialist** for a retrieval-driven Q&A workflow.
        Extract the key information from the experiment trace and write a clear, accurate narrative summary.

        # Responsibilities
        1. Process analysis: what was asked, how it was searched, and what was found.
        2. (Optional context) Support visualization with keyword-oriented takeaways when relevant.
        3. Briefly comment on retrieval quality dimensions (relevance, accuracy, authority, completeness) when evidence allows.

        # Output requirements
        - Concise but informative; highlight the main findings and limitations.
        - Logical flow; avoid mechanical bullet dumps unless helpful.
        - Write the final summary in **English**, even if the user question is in another language.
        """)
    
    async def execute_strategy(self, plan: OrchestratorPlan, root_goal: str = "") -> OrchestratorPlan:
        """
        执行单个策略的完整流程：检索 -> 评估 -> 总结
        
        参数:
            plan: 要执行的策略计划
            root_goal: 根目标（用于总结生成）
        
        返回:
            更新后的OrchestratorPlan，包含执行结果和总结
        """
        print(f"\n🔹 [SingleStrategyExecutor] 开始执行策略: {plan.tool_name}, 参数: {plan.args}")

        try:
            # 1. 执行工具检索
            raw_items = await self._execute_tool(plan)
            print(f"   ✅ 检索完成，找到 {len(raw_items)} 条结果")

            # 2. 评估检索结果
            evaluations = await self._evaluate_items(raw_items)
            print(f"   ✅ 评估完成，生成 {len(evaluations)} 条评估报告")
            
            # 3. 构建RagResult列表
            rag_results = []
            evaluation_map = {eval.target_evidence_id: eval for eval in evaluations}
            
            for item in raw_items:
                evaluation = evaluation_map.get(item.id)
                rag_results.append(RagResult(
                    retrieval_result=item,
                    evaluation=evaluation
                ))
            
            # 4. 构建ExperimentResult用于总结生成
            query_result = QueryResult(
                orchestrator_plan=plan,
                rag_results=rag_results
            )
            
            iteration_result = IterationResult(
                round_number=0,
                query_results=[query_result]
            )
            
            experiment_result = ExperimentResult(
                root_goal=root_goal or plan.reason or "Single-strategy retrieval",
                iterations=[iteration_result]
            )
            
            # 5. 生成总结
            summary = await self._generate_summary(experiment_result, raw_items)
            print(f"   ✅ 总结生成完成")
            
            # 6. 更新plan的统计信息
            plan.total_results = len(raw_items)
            plan.duplicate_results = 0  # 单策略执行不考虑重复
            plan.plansummary = summary
            
            return plan
            
        except Exception as e:
            print(f"   ❌ 执行策略时出错: {e}")
            print(traceback.format_exc())
            # 返回带有错误信息的plan
            plan.total_results = 0
            plan.duplicate_results = 0
            plan.plansummary = f"Execution failed: {str(e)}"
            return plan
    
    async def _execute_tool(self, plan: OrchestratorPlan) -> List[RawEvidenceItem]:
        """执行工具检索（复刻ToolExecutorAgent的逻辑）"""
        tool_func = ALL_TOOLS_MAP.get(plan.tool_name)
        
        if not tool_func:
            raise ValueError(f"工具未找到: {plan.tool_name}")
        
        try:
            items: List[RawEvidenceItem] = await tool_func(**plan.args)
            return items
        except Exception as e:
            print(f"   ❌ 工具执行失败: {e}")
            raise
    
    async def _evaluate_items(self, items: List[RawEvidenceItem]) -> List[ItemEvaluation]:
        """评估检索结果（复刻EvaluatorAgent的逻辑）"""
        if not items:
            return []
        
        # 构建评估提示
        prompt_text = "Please evaluate the following newly retrieved evidence items (JSON list format):\n"
        
        for item in items:
            meta_preview = {k: v for k, v in item.metadata.items() if k not in ['full_json', 'embedding']}
            item_desc = f"""
            --- Evidence Item ---
            ID: {item.id}
            Source Tool: {item.source_tool}
            Metadata: {json.dumps(meta_preview, ensure_ascii=False)}
            Content: {json.dumps(item.content, ensure_ascii=False)}
            """
            prompt_text += item_desc + "\n"
        
        # 调用LLM进行评估
        try:
            response = await self.model_client.create(
                messages=[
                    self.evaluator_system_message,
                    UserMessage(content=prompt_text, source="user")
                ],
                cancellation_token=None
            )
            
            # 解析结果
            raw_content = response.content
            cleaned = raw_content.replace("```json", "").replace("```", "").strip()
            
            eval_list_data = json.loads(cleaned)
            
            # 转换为ItemEvaluation对象列表
            evaluations = []
            for d in eval_list_data:
                if "target_evidence_id" not in d:
                    continue
                evaluations.append(ItemEvaluation(**d))
            
            return evaluations
            
        except Exception as e:
            print(f"   ⚠️ 评估过程出错: {e}")
            print(traceback.format_exc())
            # 返回空评估列表
            return []
    
    async def _generate_summary(self, experiment_result: ExperimentResult, evidence_data: List[RawEvidenceItem]) -> str:
        """生成策略总结（复刻InteractionSummaryAgent的逻辑）"""
        if not experiment_result.iterations:
            return "This retrieval returned no results."
        
        # 构建总结提示
        summary_parts = []
        summary_parts.append("# Retrieval process summary\n")
        summary_parts.append(f"**Root goal**: {experiment_result.root_goal}\n")
        summary_parts.append(f"**Iterations**: {len(experiment_result.iterations)}\n\n")
        
        # 分析策略和结果
        if experiment_result.iterations:
            latest_iteration = experiment_result.iterations[-1]
            summary_parts.append("## Strategy execution\n")

            for j, query_result in enumerate(latest_iteration.query_results):
                plan = query_result.orchestrator_plan
                summary_parts.append(f"- **Strategy**: {plan.tool_name}\n")
                summary_parts.append(f"  - **Args**: {plan.args}\n")
                summary_parts.append(f"  - **Reason**: {plan.reason}\n")
                summary_parts.append(f"  - **Hits**: {len(query_result.rag_results)}\n")
                
                # 统计评估结果
                grow_count = sum(1 for r in query_result.rag_results 
                               if r.evaluation and r.evaluation.branch_action == "GROW")
                keep_count = sum(1 for r in query_result.rag_results 
                               if r.evaluation and r.evaluation.branch_action == "KEEP")
                prune_count = sum(1 for r in query_result.rag_results 
                                if r.evaluation and r.evaluation.branch_action == "PRUNE")
                
                summary_parts.append(
                    f"  - **Eval counts**: GROW={grow_count}, KEEP={keep_count}, PRUNE={prune_count}\n"
                )

        summary_parts.append("\n## Key insights\n")
        key_insights = []
        
        for iteration in experiment_result.iterations:
            for query_result in iteration.query_results:
                for rag_result in query_result.rag_results:
                    if rag_result.evaluation and rag_result.evaluation.extracted_insight:
                        key_insights.append(rag_result.evaluation.extracted_insight)
        
        # 去重并取前5个关键洞察
        unique_insights = list(set(key_insights))[:5]
        for i, insight in enumerate(unique_insights):
            summary_parts.append(f"{i+1}. {insight}\n")
        
        # 构建大模型提示
        prompt = "# Retrieval process summary task\n\n"
        prompt += "## Input\n"
        prompt += f"**Root goal**: {experiment_result.root_goal}\n"
        prompt += f"**Iterations**: {len(experiment_result.iterations)}\n\n"
        
        # 添加策略和结果信息
        if experiment_result.iterations:
            latest_iteration = experiment_result.iterations[-1]
            prompt += "## Strategy execution\n"
            for j, query_result in enumerate(latest_iteration.query_results):
                plan = query_result.orchestrator_plan
                prompt += f"- **Strategy**: {plan.tool_name}\n"
                prompt += f"  - **Args**: {plan.args}\n"
                prompt += f"  - **Reason**: {plan.reason}\n"
                prompt += f"  - **Hit count**: {len(query_result.rag_results)}\n"

                if query_result.rag_results:
                    prompt += "  - **Sample results**:\n"
                    for k, rag_result in enumerate(query_result.rag_results[:3]):
                        content = rag_result.retrieval_result.content
                        content_str = str(content) if content else "(no content)"
                        prompt += f"    - **Result {k + 1}**: {content_str[:100]}...\n"
                        if rag_result.evaluation:
                            prompt += f"      - **Evaluation**: {rag_result.evaluation.branch_action}\n"
                            prompt += f"      - **Scores**: {rag_result.evaluation.scores}\n"
                            insight = rag_result.evaluation.extracted_insight
                            insight_str = str(insight) if insight else "(no insight)"
                            prompt += f"      - **Insight**: {insight_str[:150]}...\n"

        prompt += "\n## Key insights\n"
        for insight in unique_insights:
            prompt += f"- {insight}\n"

        prompt += "\n## Task requirements\n"
        prompt += "1. Produce a coherent end-to-end retrieval summary from the information above.\n"
        prompt += "2. Cover strategies, retrieval outcomes, evaluation mix, and key insights.\n"
        prompt += "3. Keep logic clear and emphasize what matters for the root goal.\n"
        prompt += "4. Use fluent **English** even if the root goal is not in English.\n"
        prompt += "5. Target about 500–900 English words.\n"
        
        # 调用大模型生成总结
        try:
            response = await self.model_client.create(
                messages=[self.summary_system_message, UserMessage(content=prompt, source="user")],
                cancellation_token=None
            )
            return response.content
        except Exception as e:
            print(f"   ⚠️ 生成总结时出错: {e}")
            # 返回手动生成的总结
            return "".join(summary_parts)


# 全局执行器实例
_executor_instance: Optional[SingleStrategyExecutor] = None


async def get_executor() -> SingleStrategyExecutor:
    """获取执行器实例（单例模式）"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = SingleStrategyExecutor()
    return _executor_instance


async def execute_single_strategy(plan_dict: Dict[str, Any], root_goal: str = "") -> Dict[str, Any]:
    """
    执行单个策略的API接口
    
    参数:
        plan_dict: 策略字典，包含action, tool_name, args, reason, ParentNode等字段
        root_goal: 根目标（可选）
    
    返回:
        更新后的策略字典，包含total_results, duplicate_results, plansummary等字段
    """
    # 确保RAG服务已初始化
    await get_rag_service(
        collection_name="multimodal2text",
        multimodal_collection_name="scientific_rag_multimodal_collection_new",
    )
    
    # 将字典转换为OrchestratorPlan对象
    plan = OrchestratorPlan(**plan_dict)
    
    # 获取执行器并执行策略
    executor = await get_executor()
    result_plan = await executor.execute_strategy(plan, root_goal)
    
    # 将结果转换回字典
    return result_plan.model_dump()


# 测试代码
if __name__ == "__main__":
    async def test():
        test_plan = {
            "action": "call_tool",
            "tool_name": "strategy_semantic_search",
            "ParentNode": "0",
            "args": {"query_intent": "how to visualize air pollution data in China"},
            "reason": "测试策略执行"
        }
        
        result = await execute_single_strategy(test_plan, "测试根目标")
        print("\n" + "="*50)
        print("执行结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    asyncio.run(test())
