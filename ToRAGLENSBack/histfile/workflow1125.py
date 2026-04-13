import asyncio
import json
import traceback
import os
import datetime
from typing import List, Dict, Any

# -----------------------------------------------------------------
# 1. 导入模块
# -----------------------------------------------------------------
try:
    from rag_service import get_rag_service, rag_service
    from scientific_tools import ALL_TOOLS_MAP
    from protocols import (
        UserRequest, OrchestratorPlan, OrchestratorPlanBatch, SingleToolOutput, ToolOutputBatchMessage, 
        EvaluationRequest, EvaluationReportMessage, TaskComplete,
        RawEvidenceItem, ItemEvaluation, ResearchGraph, GraphNode,ActionTrace,NodeSearchRecord
    )
except ImportError as e:
    print(f"Error importing project modules: {e}")
    exit()
from autogen_core import (
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    TypeSubscription,
    message_handler,
    type_subscription,
)
from autogen_core.models import SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

# -----------------------------------------------------------------
# 2. 日志系统
# -----------------------------------------------------------------
class WorkflowLogger:
    def __init__(self):
        if not os.path.exists("logs"): os.makedirs("logs")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"logs/run_{timestamp}.md"
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(f"# Workflow Execution Log\nStart Time: {timestamp}\n\n---\n")
        print(f"📄 [System] 日志文件: {self.filename}")

    def log(self, source: str, summary: str, type: str = "INFO", detail_data: str = None):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"\n🔹 [{timestamp}] **{source}** ({type}): {summary[:100]}...")
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(f"## [{timestamp}] {source}: {type}\n**Summary**: {summary}\n\n")
            if detail_data:
                f.write(f"```json\n{detail_data}\n```\n\n")
            f.write("---\n")

logger = WorkflowLogger()

# -----------------------------------------------------------------
# 3. 主题定义
# -----------------------------------------------------------------
TOPIC_USER = "User"
TOPIC_ORCHESTRATOR = "Orchestrator"
TOPIC_TOOL = "ToolExecutor"
TOPIC_EVALUATOR = "Evaluator"
TOPIC_HYPOTHESIS = "HypothesisGenerator"

# -----------------------------------------------------------------
# 4. 智能体定义
# -----------------------------------------------------------------

# --- A. 首席科学家 (Orchestrator) ---
@type_subscription(topic_type=TOPIC_ORCHESTRATOR)
class OrchestratorAgent(RoutedAgent):
    def __init__(self, model_client: OpenAIChatCompletionClient) -> None:
        super().__init__("Orchestrator")
        self.model_client = model_client
        self.graph = ResearchGraph(root_goal="")
        self.round_count = 0
        self.pending_tasks = 0
        self.max_rounds = 5
        self.last_round_stats = {}
        self.current_evaluate = []
        self.current_round_ids: set[str] = set()
        # ⚡️ 核心修改：Prompt 强制要求并发和混合策略
        self.system_message = SystemMessage(content="""
        # 任务整体介绍
        你是【首席科学家】，你处在一个科学知识发现团队中，你们团队的目标是以用户输入的初始问题为目标，深度并且广泛地进行论文调研，发现新的、有价值的、可验证的科学知识。
        为了进行科学知识发现，你和你的团队根据已经搜索并且阅读的论文信息正在构建一棵【科研证据树】。
        # 团队整体介绍
        你所处的科学知识发现团队中，你是首席科学家，即实验室领导的身份。通过输出的检索任务，你负责把握整个团队进行论文文献调研的方向，你的作用非常重要。
        你的团队中有许多验证人员，即实验室研究生的身份。他们会根据你的检索策略去检索论文数据，阅读检索到的图片和文本，进行初步的总结，评估检索到的内容是否符合预期，对每一个结果是否应该进行扩展阅读提出建议，并且将结果反馈给你。
        你的团队中有若干思考人员，即实验室小导师的身份。他们是一个小团队，会负责根据验证人员的反馈，对检索到的内容进行深度思考，挖掘知识之间的关联，发现新的、有价值的、可验证的科学知识，形成最终的科学回答报告。
        # 你的核心职责
        作为团队大脑，你不直接阅读原文，你的工作是**把握方向**：
        1.  **初始规划**：面对用户的新问题，你需要构思 3-5 个不同维度的切入点。
        2.  **动态决策**：根据【验证人员】（Evaluator）反馈的评估报告，决定这棵树该怎么长。
        3.  **方向把控**：你需要平衡【广度】（寻找新灵感）和【深度】（验证证据链）。

        # 决策逻辑：
        1. 继续检索时，你需要输出一系列策略的列表。每一个元素是一个策略，以字典的形式输出。
        2. 每个策略字典中，它首先有action固定为call_tool。
            ParentNode：int类型，你的决策可以来源于某一个搜索策略对应的节点，也可以来源于你综合所有结果进行的思考。这个属性命名为”ParentNode“，如果来源于节点，你应该将这个节点的ID作为ParentNode，如果是综合的结果，你将属性设置为"ROOT"。
            tool_name：str类型。根据你选择的策略决定，是strategy_semantic_search还是strategy_metadata_search。
            args：dict类型。调用检索工具时需要的参数。根据你选择的策略决定，按照下面两种策略的要求去添加args具体的内容。
            reason：str类型。你选择这个策略的原因，不要太长。
        可选策略：
        1. 深度挖掘 (DEEPER - Exploitation)
        * 触发条件：验证人员报告某个节点是【DEEPER】（高价值），你查看验证人员的汇报，发现确实有所帮助，决定在这个论文的基础上进行进一步探索。深度挖掘策略时，策略的ParentNode必须是一个节点的ID。
        * 操作：返回给你的数据中包含 `paper_id`（论文ID）、`keywords`（关键词），你可以选择paper_id或者关键词去进行查询同一篇论文或者其他关键词的论文。在深度挖掘中你要严格使用你认为的ParentNode的信息，不能随意生成新的关键词。
        * 目的：将孤立的线索变成完整的证据链。
        * 参数：如果选择deeper策略，你的返回中tool_name为strategy_metadata_search，args中包含paper_id或者keywords。
        2. 广度扩展 (BROADER - Exploration)**
        * 触发条件：
            1. 当前返回了大量被重复搜索的论文，说明该方向已经几乎彻底研究透彻，需要寻找新的可能的领域。 此时触发，ParentNode应该设置为"ROOT"。
            2. 当前返回的论文数量过少，说明对应的搜索策略不能在数据库中找到支持的论文，或者是找到的论文与用户问题相关性太低。需要寻找新的可能的搜索条件。此时触发，ParentNode应该设置为"ROOT"。
            3. 针对某一条返回的检索和评估结果，验证人员提出了使用新的专业名词的建议，或者你查看后认为可以提炼出一个新的关键词进行检索。此时触发，ParentNode应该设置为对应节点的ID。
        * 操作：根据验证人员的建议或者你自己的判断，你可以选择使用新的专业名词或者新的关键词进行检索。
        * 目的：扩展搜索范围，寻找新的、有价值的、可验证的科学知识。
        * 参数：如果选择broader策略，你的返回中tool_name为strategy_semantic_search，query_intent是你决定的下一步用于检索的文本词句。
        """)
        self.outputregulate = '''
        你可以根据当前的状态自由选择生成1-5个不同的检索策略。除了工具信息的json之外，不要输出任何其他的内容！！！不要输出除了json格式之外的任何其他内容！
        **输出格式 (必须是 JSON LIST)**:
        [
            {
                "action": "call_tool",
                "ParentNode": "0",
                "tool_name": "strategy_semantic_search", 
                "args": { "query_intent": "基于地图的可视化" },
                "reason": "我查看了新的检索和评估结果，发现许多重复的空气污染的可视化，空气污染的可视化研究的比较全面了。它们很多以地图为基础，展示了不同区域的污染情况。我认为查看其他领域基于地图的可视化方法，可能会有所启发。"
            },
            {
                "action": "call_tool",
                "ParentNode": "5",
                "tool_name": "strategy_metadata_search", 
                "args": { "paper_id": "5" },
                "reason": "这个结果和问题高度相关，且评估者对他高度评价，我认为有必要详细查看这篇论文。"
            },
            {
                "action": "call_tool",
                "ParentNode": "6",
                "tool_name": "strategy_semantic_search", 
                "args": { "query_intent": "时空序列的研究与可视化" },
                "reason": "这个结果中说到这个空气污染是一个时空序列，我认为这个关键词的可视化也可以作为扩展方向，对目标研究内容有所帮助"
            }
        ]
        或者当证据已经非常充分时：
        [ { "action": "finish", "reason": "我认为当前已经获得很多的证据，可以停止回答。" } ]
        '''
    def generate_vis_data(self) -> Dict[str, Any]:
        """
        [核心功能] 将 GraphNode 转换为可视化 JSON
        逻辑简化：只要有爹，且爹在图里，就连线。
        """
        vis_nodes = []
        vis_links = []
        
        # 1. 遍历所有节点
        for nid, node in self.graph.nodes.items():
            # --- A. 构建节点 (保持不变) ---
            label = "ROOT"
            if node.type == "EVIDENCE":
                title = node.content.get('title', 'No Title')
                label = title[:20] + "..." if len(title) > 20 else title
            elif node.type == "ROOT":
                label = "🎯 " + self.graph.root_goal[:15] + "..."

            eval_info = {}
            if node.evaluation:
                eval_info = {
                    "score": node.evaluation.scores,
                    "reason": node.evaluation.reason,
                    "insight": node.evaluation.extracted_insight
                }

            vis_node = {
                "id": node.id,
                "label": label,
                "full_title": node.content.get('title', '') if node.content else "",
                "type": node.type,       
                "status": node.status,   
                "round": node.created_at_round,
                "value": node.hit_count, 
                "data": {
                    "paper_id": node.metadata.get('paper_id') if node.metadata else None,
                    "keywords": node.metadata.get('keywords') if node.metadata else None,
                    "evaluation": eval_info
                }
            }
            vis_nodes.append(vis_node)

            # --- B. 构建连线 (逻辑修正) ---
            # 只要 ParentNode 有值，且在当前图中能找到这个父节点，就画线
            if node.ParentNode and node.ParentNode in self.graph.nodes:
                
                # 1. 判定类型：爹是 ROOT 吗？
                if node.ParentNode == "ROOT":
                    link_type = "BROADER" # 根节点发出 = 广度
                else:
                    link_type = "DEEPER"  # 普通节点发出 = 深度
                
                # 2. 准备标签
                tool_short = node.source_tool.replace("strategy_", "").replace("_search", "")
                args_short = str(node.source_args).replace("{", "").replace("}", "").replace("'", "")
                
                vis_link = {
                    "source": node.ParentNode,
                    "target": node.id,
                    "type": link_type,
                    "label": tool_short, 
                    "detail": f"Args: {args_short}\nReason: {node.source_reason}"
                }
                vis_links.append(vis_link)

        return {
            "meta": {
                "root_goal": self.graph.root_goal,
                "total_rounds": self.round_count
            },
            "nodes": vis_nodes,
            "links": vis_links
        }
    @message_handler
    async def handle_user(self, message: UserRequest, ctx: MessageContext) -> None:
        logger.log("Orchestrator", f"收到目标: {message.query}", "START")
        self.graph.root_goal = message.query
        self.graph.nodes["0"] = GraphNode(id="0", type="ROOT", status="ACTIVE", content={"goal": message.query})
        await self._plan_next_move(ctx)

    @message_handler
    async def handle_tool_batch(self, message: ToolOutputBatchMessage, ctx: MessageContext) -> None:
        total_result = sum(len(out.raw_items) for out in message.outputs)
        self.current_evaluate = []
        logger.log("ToolExecutor", f"执行: {len(message.outputs)} 条任务，返回 {total_result} 条数据", "BATCH_RECEIVE")
        new_items_buffer = [] #暂存区，放新的
        # duplicate_count = 0 # 重复计数
        #检索的结果先入库
        for output in message.outputs:
            # [关键点 1] 获取并清洗 ParentNode
            # 确保它是字符串 "ROOT" 或者具体的 ID，防止 None 或数字 0 导致断链
            raw_parent = output.original_plan.ParentNode
            current_tool = output.original_plan.tool_name
            current_reason = output.original_plan.reason
            current_args = output.original_plan.args

            if raw_parent is None or str(raw_parent).strip() == "" or str(raw_parent) == "0":
                ParentNode = "ROOT"
            else:
                ParentNode = str(raw_parent)
            search_record = NodeSearchRecord(
                round_index=self.round_count,
                source_tool=current_tool,
                source_args=current_args,
                parent_id=ParentNode
            )    
            current_new_ids = []
            for item in output.raw_items:
                current_new_ids.append(item.id)
                self.current_round_ids.add(item.id)

                if item.id in self.graph.nodes:      #重复点
                    self.graph.nodes[item.id].hit_count += 1
                    self.graph.nodes[item.id].search_history.append(search_record)
                    # self.current_evaluate.append(self.graph.nodes[item.id])    # 重复点不用评估，但是要反馈给orchestra
                else:
                    node = GraphNode(
                        id=item.id,
                        type="EVIDENCE",
                        status="PENDING", 
                        content=item.content,
                        metadata=item.metadata,
                        ParentNode=ParentNode,
                        created_at_round=self.round_count,
                        source_tool=current_tool,
                        source_reason=current_reason,
                        source_args=current_args,
                        search_history=[search_record]
                    )   
                    self.graph.nodes[item.id] = node
                    if ParentNode in self.graph.nodes:
                        self.graph.nodes[ParentNode].children_ids.append(item.id)
                    elif "ROOT" in self.graph.nodes:
                         self.graph.nodes["ROOT"].children_ids.append(item.id)
                    new_items_buffer.append(item)
        # trace = ActionTrace(
        #     round_index=self.round_count,
        #     tool_name=current_tool,
        #     tool_args=current_args, # 记录当时的搜索词
        #     ParentNode=ParentNode,
        # )
        # self.graph.action_history.append(trace)

        # --- 分批评估 ---
        if not new_items_buffer:
            logger.log("Orchestrator", "本轮无新数据，直接进入下一轮", "SKIP_EVAL")
            self.pending_eval_batches = 1
            await self.handle_eval(EvaluationReportMessage(evaluations=[], global_suggestion="无需评估"), ctx)
            return

        BATCH_SIZE = 5
        chunks = [new_items_buffer[i:i + BATCH_SIZE] for i in range(0, len(new_items_buffer), BATCH_SIZE)]
        
        self.pending_eval_batches = len(chunks)
        logger.log("Orchestrator", f"有{len(new_items_buffer)}条新数据，生成 {len(chunks)} 个评估包发送给 Evaluator", "DISPATCH_EVAL")
        
        for chunk in chunks:
            await self.publish_message(
                EvaluationRequest(new_items=chunk),
                topic_id=TopicId(TOPIC_EVALUATOR, source=self.id.key)
            )
        # self.last_round_stats = {
        #     "tool": message.original_plan.tool_name,
        #     "total": len(message.raw_items),
        #     "new": len(new_items_to_eval),
        #     "dup": duplicate_count
        # }

    @message_handler
    async def handle_eval(self, message: EvaluationReportMessage, ctx: MessageContext) -> None:
        logger.log("Orchestrator", f"收到 {len(message.evaluations)} 条评估，更新图谱...", "UPDATE",detail_data=message.evaluations)
        #这里是正确的
        # 更新状态
        for eval_res in message.evaluations:
            nid = eval_res.target_evidence_id
            if nid in self.graph.nodes:
                node = self.graph.nodes[nid]
                node.evaluation = eval_res
                if eval_res.branch_action in ["GROW", "KEEP"]:
                    node.status = "ACTIVE"
                elif eval_res.branch_action == "PRUNE":
                    node.status = "PRUNED"
                # 新入库的加入库中，之后加入准备orchestra的队列
                # self.current_evaluate.append(node)
                self.current_round_ids.add(nid)

            # 4. 批处理计数器递减 (核心循环控制)
        self.pending_eval_batches -= 1
        logger.log("Orchestrator", f"评估包处理完毕。剩余待处理包数: {self.pending_eval_batches}", "BATCH_PROGRESS")

        # 5. 检查本轮是否完全结束
        if self.pending_eval_batches <= 0:
            # 保险归零，防止负数
            self.pending_eval_batches = 0
            
            # 推进轮次
            self.round_count += 1
            logger.log("Orchestrator", f"=== 第 {self.round_count-1} 轮全部分支已闭环 ===", "ROUND_DONE")
            
            # 决策：继续还是停止
            if self.round_count >= self.max_rounds:
                logger.log("Orchestrator", "达到最大轮次限制，准备生成报告。", "STOP")
                await self._finish_task(ctx)
            else:
                # 立即规划下一轮
                await self._plan_next_move(ctx)
        else:
            # 还有其他分块的评估在路上，原地等待
            pass

    async def _plan_next_move(self, ctx: MessageContext):
        '''
        checked!
        [核心规划逻辑] 基于科研图谱状态和反馈循环，规划下一轮的并行检索任务。

        主要步骤：
        1. **上下文构建 (Context)**：
           - 获取当前图谱中的【活跃节点】(Active Nodes) 作为深挖的潜在父节点。
           - 注入【上一轮战况】(Last Round Stats)，特别是重复率数据，以触发 LLM 的反思机制（高重复率 -> 强制 Broader）。
        
        2. **LLM 决策 (Decision)**：
           - 调用模型生成 JSON 格式的任务列表，决定是继续深挖 (Deeper) 还是横向扩展 (Broader)。
        
        3. **批处理初始化 (Batch Setup)**：
           - 计算有效任务数量并设置 `self.pending_tasks` 计数器，用于控制异步流的批处理闭环。
           - 处理边界情况（如无任务或 LLM 决定结束）。
        
        4. **参数清洗与分发 (Dispatch)**：
           - 强制类型转换：确保 `ParentNode` 为安全的字符串 ID (0/None -> "ROOT")。
           - 封装为 `OrchestratorPlan` 消息，并行广播给 ToolExecutor。
        '''
        prompt = f'''用户提问: {self.graph.root_goal}。当前系统已交互次数: {self.round_count}，一共获得了{len(self.graph.nodes)}个证据节点。'''
        logger.log("Orchestrator", f"当前评估节点{len(self.current_round_ids)}个:", "PLANNING",detail_data = prompt)
        if not self.current_round_ids:
            pass
        else:
            for nid in self.current_round_ids:
                node = self.graph.nodes[nid]

                id = node.id
                content = node.content
                paperid = node.metadata.get("paper_id") if node.metadata else None
                keywords = node.metadata.get("keywords") if node.metadata else None
                hitcount = node.hit_count
                source_tool = node.source_tool
                source_args = node.source_args
                # evaluation = node.evaluation
                this_round_accesses = [
                    acc for acc in node.search_history 
                    if acc.round_index == self.round_count
                ]
                
                # 为了填入你的 Prompt，我们将多个来源合并显示
                if this_round_accesses:
                    source_tool = " & ".join([acc.source_tool for acc in this_round_accesses])
                    source_args = " & ".join([str(acc.source_args) for acc in this_round_accesses])
                else:
                    # 如果是旧节点复用，回退到出生来源
                    source_tool = node.source_tool
                    source_args = str(node.source_args)

                evaluation = node.evaluation
                
                # --- 核心分支：防止 None 报错 ---
                if evaluation:
                    # ✅ 情况 A: 有评估结果 (应用你写的 Prompt)
                    prompt += f'''证据节点ID: {id}, 选择了{source_tool}工具, 工具参数为{source_args}。
                    本次是第{hitcount}次检索到, 评估人员已评估，评估分数为{evaluation.scores},认为其内容值得[{evaluation.branch_action}]。
                    具体而言评估人员总结条目内容为{evaluation.extracted_insight},理由是{evaluation.reason},他抽取处理一些关键词推荐给你{evaluation.suggested_keywords}。
                    这个条目的具体内容是: {content}, 来自论文ID: {paperid}, 关键词: {keywords}\n
                    --------------------------------------------------\n'''
                
                else:
                    # ✅ 情况 B: 无评估结果 (重复命中)
                    # 使用简化版 Prompt，避免调用 evaluation.scores
                    prompt += f'''证据节点ID: {id}, 选择了{source_tool}工具, 工具参数为{source_args}。
            本次是第{hitcount}次检索到 (重复命中)。
            状态: ⏳ [PENDING/DUPLICATE] (本次未进行新一轮详细评估，建议参考历史信息或Metadata)。
            这个条目的具体内容是: {content}, 来自论文ID: {paperid}, 关键词: {keywords}\n
--------------------------------------------------\n'''
        self.current_round_ids.clear()
                # prompt += f'''证据节点ID: {id}, 选择了{source_tool}工具, 工具参数为{source_args}。
                # 本次是第{hitcount}次检索到, 评估人员已评估，评估分数为{evaluation.scores},认为其内容值得{evaluation.branch_action}。
                # 具体而言评估人员总结条目内容为{evaluation.extracted_insight},理由是{evaluation.reason},他抽取处理一些关键词推荐给你{evaluation.suggested_keywords}。
                # 这个条目的具体内容是: {content}, 来自论文ID: {paperid}, 关键词: {keywords}\n'''
        prompt += self.outputregulate        
        logger.log("Orchestrator", "思考并发策略...", "PLANNING")
        response = await self.model_client.create(
            messages=[self.system_message, UserMessage(content=prompt, source="user")],
            cancellation_token=ctx.cancellation_token
        )    
        try:
            cleaned = response.content.replace("```json", "").replace("```", "").strip()
            decision_list = json.loads(cleaned)
            
            # 兼容性处理：如果 LLM 还是只返回了一个对象，把它包进 List
            if isinstance(decision_list, dict):
                decision_list = [decision_list]
            #本轮有多少子任务，要有效的才计数。
            valid_tasks = [d for d in decision_list if d.get("action") == "call_tool"]
            self.pending_tasks = len(valid_tasks)

            #处理没有有效任务的情况。
            if self.pending_tasks ==0:
                is_finish = any(d.get("action") == "finish" for d in decision_list)
                if is_finish:
                    logger.log("Orchestrator", "LLM决定结束任务", "STOP")
                    await self._finish_task(ctx)
                    return      #主动返回了结束任务
                else:
                    logger.log("Orchestrator", "未生成有效任务，流程结束", "WARN")
                    await self._finish_task(ctx)
                    return      #解析不成功，任务被迫停止
            logger.log("Orchestrator", f"本轮次共生成 {self.pending_tasks} 个有效任务", "BATCH_START")

            #分发消息
            plans = []
            for decision in valid_tasks:
                tool_name = decision.get('tool_name', 'unknown')
                args = decision.get('args', {}) # 确保是字典
                reason = decision.get('reason', '')
                ParentNode = decision.get('ParentNode', 'ROOT')
                if ParentNode is None or str(ParentNode).strip() == "" or str(ParentNode) == "0":
                    ParentNode = "ROOT"
                else:
                    ParentNode = str(ParentNode) # 确保是字符串 ID
                logger.log("Orchestrator", f"父节点: {ParentNode}，工具: {tool_name}，参数: {args}，原因: {reason}", "PLAN")    
                plan = OrchestratorPlan(
                    action="call_tool",
                    tool_name=tool_name,
                    args=args,
                    reason=reason,
                    ParentNode=ParentNode,
                )
                plans.append(plan)

            await self.publish_message(OrchestratorPlanBatch(plans=plans), topic_id=TopicId(TOPIC_TOOL, source=self.id.key))                
        except Exception as e:
            logger.log("Orchestrator", f"决策解析失败: {e}", "ERROR", detail_data=response.content)
            self.pending_tasks = 0
            await self._finish_task(ctx)

    async def _finish_task(self, ctx):
        logger.log("Orchestrator", "发送最终图谱给总结者", "HANDOFF")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # trace_filename = f"logs/trace_{timestamp}.json"
        
        # 我们保存整个 ResearchGraph，因为它包含了 nodes (数据) 和 action_history (操作)
        # with open(trace_filename, "w", encoding="utf-8") as f:
        #     # Pydantic 的 model_dump_json 方法非常好用
        #     f.write(self.graph.model_dump_json(indent=2))
        vis_data = self.generate_vis_data()
        vis_filename = f"logs/vis_data_{timestamp}.json"
        graph_state_file = f"logs/graph_state_{timestamp}.json"
        with open(graph_state_file, "w", encoding="utf-8") as f:
            # model_dump_json 是 Pydantic 的神技，完美序列化所有嵌套对象
            f.write(self.graph.model_dump_json(indent=2))
            
        with open(vis_filename, "w", encoding="utf-8") as f:
            json.dump(vis_data, f, indent=2, ensure_ascii=False)
            
        print(f"\n📊 [System] 可视化数据已保存: {vis_filename}")
        await self.publish_message(
            TaskComplete(graph_snapshot=self.graph),
            topic_id=TopicId(TOPIC_HYPOTHESIS, source=self.id.key)
        )


# --- B. 工具执行者 (ToolExecutor) ---
@type_subscription(topic_type=TOPIC_TOOL)
class ToolExecutorAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("ToolExecutor")

    @message_handler
    async def handle_plan(self, message: OrchestratorPlanBatch, ctx: MessageContext) -> None:
        '''
        根据生成的一批任务，并发执行工具函数。
        '''
        logger.log("ToolExecutor", f"执行: {len(message.plans)} 条任务", "EXEC")
        async def run_single_task(plan: OrchestratorPlan) -> SingleToolOutput:
            tool_func = ALL_TOOLS_MAP.get(plan.tool_name)
            try:
                if tool_func:
                    items: List[RawEvidenceItem] = await tool_func(**plan.args)
                    logger.log("ToolExecutor", f"返回 {len(items)} 条数据", "RESULT")
                    return SingleToolOutput(original_plan=plan, raw_items=items)
                else:
                    logger.log("ToolExecutor", f"工具未找到: {plan.tool_name}", "ERROR")
                    return SingleToolOutput(original_plan=plan, raw_items=[], error=f"Tool {plan.tool_name} not found")
            except Exception as e:
                logger.log("ToolExecutor", f"执行崩溃: {e}", "ERROR", detail_data=traceback.format_exc())
                return SingleToolOutput(original_plan=plan, raw_items=[], error=str(e))

        # 并发
        tasks = [run_single_task(plan) for plan in message.plans]
        results = await asyncio.gather(*tasks)
        
        # 汇总结果
        success_count = sum(1 for r in results if not r.error)
        logger.log("ToolExecutor", f"执行完毕: 成功 {success_count}/{len(results)}", "BATCH_DONE")
        
        # 打包发回 Orchestrator
        response = ToolOutputBatchMessage(outputs=results)
        await self.publish_message(response, topic_id=TopicId(TOPIC_ORCHESTRATOR, source=self.id.key))        


# --- C. 评估员 (Evaluator) ---
@type_subscription(topic_type=TOPIC_EVALUATOR)
class EvaluatorAgent(RoutedAgent):
    def __init__(self, model_client: OpenAIChatCompletionClient) -> None:
        super().__init__("Evaluator")
        self.model_client = model_client
        self.system_message = SystemMessage(content="""
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
           - 不要只说“这张图很好”。要说“这张图展示了 PM2.5 在冬季与呼吸道疾病发病率呈正相关”。
        
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
    @message_handler 
    async def handle_request(self,message:EvaluationRequest,ctx: MessageContext) -> None:
        if not message.new_items: return
        logger.log("Evaluator", f"正在评估 {len(message.new_items)} 条【新】证据...", "EVAL")
        
        # 2. 构建多模态 Prompt (User Message Content Parts)
        # 这是一个 List，可以包含文本块和图片块
        # user_content_parts = []
        prompt_text = "请对以下新检索到的证据进行单点评估（JSON List 格式）：\n"
        for item in message.new_items:
            # A. 准备文本描述
            # 尽量把 metadata 里有用的东西都展示给 LLM
            meta_preview = {k: v for k, v in item.metadata.items() if k not in ['full_json', 'embedding']}
            item_desc = f"""
            --- Evidence Item ---
            ID: {item.id}
            Source Tool: {item.source_tool}
            Metadata: {json.dumps(meta_preview, ensure_ascii=False)}
            Content: {json.dumps(item.content, ensure_ascii=False)}
            """
            prompt_text += item_desc + "\n"            
            # # B. 准备图片 (VLM 核心)
            # if item.image_path:
            #     # 使用 utils 里的函数转 Base64
            #     b64_img = encode_image_to_base64(item.image_path)
            #     if b64_img:
            #         logger.log("Evaluator", f"👀 加载图片: {item.image_path}", "VLM_LOAD")
            #         user_content_parts.append({
            #             "type": "image_url",
            #             "image_url": {
            #                 "url": f"data:image/jpeg;base64,{b64_img}"
            #             }
            #         })
            #     else:
            #         logger.log("Evaluator", f"⚠️ 图片加载失败: {item.image_path}", "WARN")
# 3. 调用 LLM (GPT-4o)
        try:
            response = await self.model_client.create(
                messages=[
                    self.system_message, 
                    UserMessage(content=prompt_text, source="user")
                ],
                cancellation_token=ctx.cancellation_token
            )
            
            # 4. 解析结果
            raw_content = response.content
            # 清洗 Markdown
            cleaned = raw_content.replace("```json", "").replace("```", "").strip()
            
            eval_list_data = json.loads(cleaned)
            
            # 转换为 Pydantic 对象列表
            evaluations = []
            for d in eval_list_data:
                # 容错处理：确保 target_evidence_id 存在
                if "target_evidence_id" not in d:
                    continue 
                evaluations.append(ItemEvaluation(**d))
            
            logger.log("Evaluator", f"评估完成，生成 {len(evaluations)} 条报告", "REPORT", detail_data=cleaned)
            
            # 5. 发回 Orchestrator
            await self.publish_message(
                EvaluationReportMessage(evaluations=evaluations, global_suggestion=""),
                topic_id=TopicId(TOPIC_ORCHESTRATOR, source=self.id.key)
            )
            
        except Exception as e:
            # 错误处理：必须发回一条空消息或错误消息，否则 Orchestrator 的计数器会卡死
            error_trace = traceback.format_exc()
            logger.log("Evaluator", f"评估解析失败: {e}", "ERROR", detail_data=error_trace)
            
            await self.publish_message(
                EvaluationReportMessage(evaluations=[], global_suggestion="Evaluator Process Error"),
                topic_id=TopicId(TOPIC_ORCHESTRATOR, source=self.id.key)
            )
        


# --- D. 总结者 (Hypothesis) ---
@type_subscription(topic_type=TOPIC_HYPOTHESIS)
class HypothesisGeneratorAgent(RoutedAgent):
    def __init__(self, model_client: OpenAIChatCompletionClient, websocket_manager=None) -> None:
        super().__init__("Hypothesis")
        self.model_client = model_client
        self.ws_manager = websocket_manager
        self.system_message = SystemMessage(content="""
        你是严格的同行评审员。
        你需要对每条证据进行【单点评估】，判断其是否值得保留 (GROW) 或剪枝 (PRUNE)。
        如果有图片，请结合视觉信息判断。
        
        输出格式 (JSON List): 
        [{"target_evidence_id": "...", "branch_action": "GROW", "extracted_insight": "...", "scores": {...}, "reasoning": "..."}]
        # 角色定义
        你是团队中的【思考人员】（实验室小导师/论文第一作者）。
        首席科学家已经宣布调研结束，并把整理好的【科研证据树】（只包含 ACTIVE 节点）交给了你。

        # 你的任务
        你需要综合所有碎片化的证据，进行深度思考，撰写一份高质量的**科学回答报告**。

        # 写作原则
        1.  **拒绝堆砌**：不要像记流水账一样列出发现了什么。你需要**综合 (Synthesize)**，发现知识之间的隐形关联。
        2.  **言必有据**：你的每一个论点，都必须引用具体的证据 ID。例如：“根据 WRF-Chem 模型的预测结果 (Evidence: fig_10)...”。
        3.  **诚实面对缺口**：如果证据链断了（例如没找到基因数据），请在“局限性”章节明确指出，而不要编造。

        # 报告结构
        ## 1. 核心科学假设 (Core Hypothesis)
        (用一句话提炼出的核心观点)

        ## 2. 证据链分析 (Evidence Analysis)
        ### 2.1 [子主题 1，例如：时空分布特征]
        (结合图表进行论证)
        ### 2.2 [子主题 2，例如：定量数据支持]
        (结合表格数据进行论证)

        ## 3. 关键缺口与未来方向 (Critical Gaps)
        (基于本次调研的未尽之处，提出建议)

        ## 4. 结论 (Conclusion)
        """)

    @message_handler
    async def handle_task_complete(self, message: TaskComplete, ctx: MessageContext) -> None:
        logger.log("Hypothesis", "生成最终报告...", "FINAL")
        active_evidence = message.graph_snapshot.get_active_nodes_summary()
        prompt = f"基于以下科研树筛选出的【高质量证据链】:\n{active_evidence}\n\n请生成最终科学报告(核心假设/证据链/结论)。"
        response = await self.model_client.create(messages=[UserMessage(content=prompt, source="user")], cancellation_token=ctx.cancellation_token)
        print(f"\n\n>>> [Final Report]:\n{response.content}")
        logger.log("Hypothesis", "报告已生成", "DONE")
        logger.log("Hypothesis [Final Report]:", response.content, "REPORT")
        
        # 通过WebSocket发送总结报告到前端
        if hasattr(self, 'ws_manager') and self.ws_manager:
            try:
                report_content = response.content
                await self.ws_manager.broadcast_json({
                    "type": "summary",
                    "content": report_content
                })
                logger.log("Hypothesis", "总结报告已发送到前端", "INFO")
            except Exception as e:
                logger.log("Hypothesis", f"发送总结报告失败: {str(e)}", "ERROR")


# --- Main ---
async def main():
    print("--- [System] 初始化数据层 ---")
    rag = await get_rag_service()
    
    try:
        model_client = OpenAIChatCompletionClient(
            model="gpt-4o",
            base_url="http://38.147.105.35:3030/v1",
            api_key="sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
        )
        runtime = SingleThreadedAgentRuntime()
        
        await OrchestratorAgent.register(runtime, type=TOPIC_ORCHESTRATOR, factory=lambda: OrchestratorAgent(model_client))
        await ToolExecutorAgent.register(runtime, type=TOPIC_TOOL, factory=lambda: ToolExecutorAgent())
        await EvaluatorAgent.register(runtime, type=TOPIC_EVALUATOR, factory=lambda: EvaluatorAgent(model_client))
        await HypothesisGeneratorAgent.register(runtime, type=TOPIC_HYPOTHESIS, factory=lambda: HypothesisGeneratorAgent(model_client, None))

        runtime.start()
        
        query = "空气污染能够如何通过可视化方便分析和理解？"
        
        await runtime.publish_message(
            UserRequest(query=query),
            topic_id=TopicId(TOPIC_ORCHESTRATOR, source="User")
        )
        
        await runtime.stop_when_idle()

    except KeyboardInterrupt:
        print("User Interrupted.")
    finally:
        await rag.close()

if __name__ == "__main__":
    asyncio.run(main())