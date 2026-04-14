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
        # 角色定义
        你是团队中的【验证人员】（实验室研究生），你们团队正在进行针对某个问题的科学文献调研。
        你们的首席科学家会制定调研的方向，根据那个方向已经搜索出了许多证据，你的任务是对搜索出来的每一条证据进行【单点评估】。
        你的证据会被提交给首席科学家，首席科学家会根据你的评估结果，进行下一步的决策。如果做的好，首席科学家会给你涨工资，你要好好工作。
        
        # 评估逻辑
        请仔细阅读证据的标题、总结和洞察，**如果有图片，请务必结合图片内容进行视觉判断**。
        
        1. **判定动作 (branch_action)**:
           - **GROW**: 高价值证据。与问题强相关，且包含进一步深挖的线索（如具体的 Paper ID，关联表格，或者图表展示了极具价值的数据趋势）。
           - **KEEP**: 中等价值。与问题相关，但可能只是背景介绍，或者没有明显的深挖路径。保留作为上下文。
           - **PRUNE**: 低价值。与问题无关，或者信息过于模糊/重复/低质。直接剪除。
        
        2. **信息提取 (extracted_insight)**:
           - 不要只说"这张图很好"。要说"这张图展示了 PM2.5 在冬季与呼吸道疾病发病率呈正相关"。
        
        3. **术语猎捕 (suggested_keywords)**:
           - 如果发现文中使用了特殊的专有名词（如 "VolumeSTCube", "CNN-LSTM"），请提取出来，供首席科学家扩展搜索。
        
        # 输出格式 (JSON List)
        必须返回一个 JSON 列表，包含所有传入证据的评估结果。不要包含 Markdown 标记。
        
        [
          {
            "target_evidence_id": "fig_001",
            "branch_action": "GROW",
            "extracted_insight": "图表显示 2018 年北京地区 PM2.5 浓度峰值对应哮喘急诊人数峰值。",
            "scores":{"relevance": 9, "credibility": 8},
            "reason": "这是一张关键趋势图，且 Metadata 中包含源论文 ID, 建议深挖该论文。",
            "suggested_keywords": ["Time-series analysis", "Asthma emergency visits"]
          }
        ]
        """)
        
        # 总结器的系统消息
        self.summary_system_message = SystemMessage(content="""
        # 角色定义
        你是【总结专家】，负责对整个问答过程进行系统性总结与深度分析。
        你的任务是从复杂的实验结果中提取关键信息，生成清晰、准确的总结报告。
        
        # 核心职责
        1. 过程分析与总结：对问答过程中产生的问题及搜索到的内容进行系统性总结与深度分析
        2. 内容可视化支持：为问题的所有结果生成词云数据，直观展示关键主题与高频词汇
        3. 检索质量评估：评估问题提出的积极意义和价值，分析其对知识获取的贡献度
        
        # 输出要求
        - 生成简洁的过程总结，准确反映问答交互中产生的关键问题
        - 确保总结内容逻辑清晰、重点突出，便于用户快速掌握问答核心
        - 提供详细的检索质量评估，包括相关性、准确性、权威性和完整性等维度
        - 生成高质量的词云数据，便于前端可视化展示
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
                root_goal=root_goal or plan.reason or "单策略检索",
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
            plan.plansummary = f"执行失败: {str(e)}"
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
        prompt_text = "请对以下新检索到的证据进行单点评估（JSON List 格式）：\n"
        
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
            return "本次检索未产生任何结果。"
        
        # 构建总结提示
        summary_parts = []
        summary_parts.append(f"# 检索过程总结\n")
        summary_parts.append(f"**根目标**: {experiment_result.root_goal}\n")
        summary_parts.append(f"**检索轮次**: {len(experiment_result.iterations)}\n\n")
        
        # 分析策略和结果
        if experiment_result.iterations:
            latest_iteration = experiment_result.iterations[-1]
            summary_parts.append(f"## 策略执行总结\n")
            
            for j, query_result in enumerate(latest_iteration.query_results):
                plan = query_result.orchestrator_plan
                summary_parts.append(f"- **策略**: {plan.tool_name}\n")
                summary_parts.append(f"  - **参数**: {plan.args}\n")
                summary_parts.append(f"  - **原因**: {plan.reason}\n")
                summary_parts.append(f"  - **结果**: 找到 {len(query_result.rag_results)} 条\n")
                
                # 统计评估结果
                grow_count = sum(1 for r in query_result.rag_results 
                               if r.evaluation and r.evaluation.branch_action == "GROW")
                keep_count = sum(1 for r in query_result.rag_results 
                               if r.evaluation and r.evaluation.branch_action == "KEEP")
                prune_count = sum(1 for r in query_result.rag_results 
                                if r.evaluation and r.evaluation.branch_action == "PRUNE")
                
                summary_parts.append(f"  - **评估**: 高价值 {grow_count} 条，中等价值 {keep_count} 条，低价值 {prune_count} 条\n")
        
        # 提取关键洞察
        summary_parts.append("\n## 关键洞察\n")
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
        prompt = f"# 检索过程总结任务\n\n"
        prompt += f"## 输入信息\n"
        prompt += f"**根目标**: {experiment_result.root_goal}\n"
        prompt += f"**检索轮次**: {len(experiment_result.iterations)}\n\n"
        
        # 添加策略和结果信息
        if experiment_result.iterations:
            latest_iteration = experiment_result.iterations[-1]
            prompt += f"## 策略执行信息\n"
            for j, query_result in enumerate(latest_iteration.query_results):
                plan = query_result.orchestrator_plan
                prompt += f"- **策略**: {plan.tool_name}\n"
                prompt += f"  - **参数**: {plan.args}\n"
                prompt += f"  - **原因**: {plan.reason}\n"
                prompt += f"  - **结果数量**: {len(query_result.rag_results)} 条\n"
                
                # 添加前3个结果的详细信息
                if query_result.rag_results:
                    prompt += f"  - **详细结果**:\n"
                    for k, rag_result in enumerate(query_result.rag_results[:3]):
                        content = rag_result.retrieval_result.content
                        content_str = str(content) if content else "无内容"
                        prompt += f"    - **结果 {k+1}**: {content_str[:100]}...\n"
                        if rag_result.evaluation:
                            prompt += f"      - **评估**: {rag_result.evaluation.branch_action}\n"
                            prompt += f"      - **分数**: {rag_result.evaluation.scores}\n"
                            insight = rag_result.evaluation.extracted_insight
                            insight_str = str(insight) if insight else "无洞察"
                            prompt += f"      - **洞察**: {insight_str[:150]}...\n"
        
        # 添加关键洞察
        prompt += "\n## 关键洞察\n"
        for insight in unique_insights:
            prompt += f"- {insight}\n"
        
        prompt += "\n## 任务要求\n"
        prompt += "1. 基于以上信息，生成一个全面、连贯的检索过程总结\n"
        prompt += "2. 总结应包括策略信息、检索结果、评估分析和关键洞察\n"
        prompt += "3. 总结应逻辑清晰、重点突出，便于用户快速掌握核心内容\n"
        prompt += "4. 使用自然、流畅的语言，避免过于技术性的表达\n"
        prompt += "5. 总结长度适中，控制在500-1000字左右\n"
        
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
