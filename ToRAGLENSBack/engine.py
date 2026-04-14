"""
【功能】多智能体编排核心：Orchestrator / 检索与评估 / 总结与 Hypothesis 生成、交互式暂停、实验结果落盘；与 scientific_tools、protocols、connection 协同。
【长期价值】核心长期维护（体量最大，业务逻辑主战场）。
"""
import asyncio
import json
import traceback
import os
import datetime
from typing import List, Dict, Any, Optional

# -----------------------------------------------------------------
# 1. 导入模块
# -----------------------------------------------------------------
try:
    from rag_service import get_rag_service, rag_service
    from scientific_tools import ALL_TOOLS_MAP, set_active_collection_name
    from protocols import (
        UserRequest, OrchestratorPlan, OrchestratorPlanBatch, SingleToolOutput, ToolOutputBatchMessage,
        EvaluationRequest, EvaluationReportMessage, TaskComplete, ExpandSearchRequest, FollowUpRequest,
        HypothesisStep, HypothesisData,
        RawEvidenceItem, ItemEvaluation, ResearchGraph, GraphNode, ActionTrace, NodeSearchRecord,
        SummaryRequest, SummaryResponse, WordCloudData, RetrievalQualityEvaluation,
        ExperimentResult, IterationSummary,
        OutlineRequest, OutlineResponse, SubTopic, SectionRequest, SectionResponse, SynthesisRequest,
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
from autogen_core.models import ModelInfo
from connection import ConnectionManager
from openai import OpenAI
client = OpenAI(
    base_url = "https://uni-api.cstcloud.cn/v1//chat/completions",
    api_key="f24a9af08a33a9649b3f149706c8c45e8602a884b8beab6abae0d608226477f8"
)
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
        try:
            print(f"📄 [System] 日志文件: {self.filename}")
        except UnicodeEncodeError:
            print(f"[System] 日志文件: {self.filename}")

    def log(self, source: str, summary: str, type: str = "INFO", detail_data: str = None):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        try:
            print(f"\n🔹 [{timestamp}] **{source}** ({type}): {summary[:100]}...")
        except UnicodeEncodeError:
            print(f"\n[{timestamp}] **{source}** ({type}): {summary[:100]}...")
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(f"## [{timestamp}] {source}: {type}\n**Summary**: {summary}\n\n")
            if detail_data:
                f.write(f"```json\n{detail_data}\n```\n\n")
            f.write("---\n")
    
    def log_llm_interaction(self, source: str, prompt: str, response: str, system_message: str = None):
        """记录 LLM 交互：输入 prompt 和输出 response"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(f"### [{timestamp}] {source}: LLM Interaction\n\n")
            
            if system_message:
                f.write(f"**System Message**:\n```\n{system_message}\n```\n\n")
            
            f.write(f"**User Prompt**:\n```\n{prompt}\n```\n\n")
            
            f.write(f"**LLM Response**:\n```\n{response}\n```\n\n")
            
            f.write("---\n")
    
    def log_prompt(self, round_number: int, prompt: str, response: str = None):
        """
        专门记录每次plan时的完整prompt和响应
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"\n📝 [{timestamp}] **Orchestrator** (PROMPT): 记录第 {round_number} 轮策略生成的完整prompt")
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(f"## [{timestamp}] Orchestrator: PROMPT (第 {round_number} 轮)\n")
            f.write("### 📋 完整Prompt内容\n")
            f.write(f"```\n{prompt}\n```\n\n")
            
            if response:
                f.write("### 🤖 LLM响应内容\n")
                f.write(f"```\n{response}\n```\n\n")
            
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
TOPIC_SUMMARY = "InteractionSummaryAgent"
TOPIC_HYPOTHESIS_COORDINATOR = "HypothesisCoordinator"
TOPIC_HYPOTHESIS_SECTION = "HypothesisSection"
TOPIC_HYPOTHESIS_SYNTHESIZER = "HypothesisSynthesizer"

class InteractivePauseGate:
    def __init__(self):
        self._futures: Dict[str, asyncio.Future] = {}
        
    def create_checkpoint(self, checkpoint_id: str) -> asyncio.Future:
        future = asyncio.Future()
        self._futures[checkpoint_id] = future
        return future
        
    def resolve_checkpoint(self, checkpoint_id: str, decision_data: dict):
        if checkpoint_id in self._futures:
            future = self._futures[checkpoint_id]
            if not future.done():
                future.set_result(decision_data)
            del self._futures[checkpoint_id]
            
    async def wait(self, checkpoint_id: str) -> dict:
        future = self.create_checkpoint(checkpoint_id)
        return await future

# -----------------------------------------------------------------
# 4. 智能体定义
# -----------------------------------------------------------------

# --- A. 首席科学家 (Orchestrator) ---
@type_subscription(topic_type=TOPIC_ORCHESTRATOR)
class OrchestratorAgent(RoutedAgent):
    def __init__(self, model_client: OpenAIChatCompletionClient, websocket_manager, is_follow_up_mode: bool = False, pause_gate = None, interactive_mode: bool = False, run_id: str = None) -> None:
        super().__init__("Orchestrator")
        self.model_client = model_client
        self.ws_manager = websocket_manager
        self.is_follow_up_mode = is_follow_up_mode
        self.pause_gate = pause_gate
        self.interactive_mode = interactive_mode
        self.run_id = run_id
        
        self.graph = ResearchGraph(root_goal="")
        self.round_count = 0
        self.pending_tasks = 0
        self.max_rounds = 7
        self.last_round_stats = {}
        self.current_evaluate = []
        self.report_content = ""
        self.current_round_ids: set[str] = set()
        
        # 原始数据存储属性
        from protocols import ExperimentResult, IterationResult, QueryResult, OrchestratorPlan
        self.experiment_result = ExperimentResult(root_goal="")
        self._experiment_save_path: Optional[str] = None  # 本次运行的保存路径，多保存点复用
        self.current_iteration: Optional[IterationResult] = None
        self.current_query_results: Dict[str, QueryResult] = {}  # key: plan_id (使用JSON序列化的策略作为唯一标识)
        
        # ⚡️ 优化：历史策略记录 (使用OrchestratorPlan)
        self.history_strategies: List[OrchestratorPlan] = []  # 存储所有历史策略
        # 每个检索策略（plan）希望返回的结果数量（由前端传入）
        self.rag_result_per_plan: int = 10
        
        # ⚡️ 核心修改：Prompt 强制要求并发和混合策略
        self.strategyhis = ""
        self.searchpro = ""
        self.system_message = SystemMessage(content="""
        # Mission Overview
        You are the **Chief Scientist** in a scientific discovery team.
        Your team's goal is to investigate literature deeply and broadly, starting from the user's question, and discover new, valuable, and verifiable scientific knowledge.
        You are building a **research evidence tree** from retrieved and reviewed papers.

        # Team Roles
        You lead the direction of retrieval.
        Evaluators execute your retrieval plans, inspect text and figures, summarize findings, and assess whether each result should be expanded.
        Thinkers later synthesize validated evidence into a final scientific report.

        # Your Core Responsibilities
        1. **Initial planning**: for a new user question, propose multiple (3-5) search angles.
        2. **Dynamic decisions**: adapt based on evaluator feedback.
        3. **Direction control**: balance **breadth** (new directions) and **depth** (evidence-chain validation).

        # Decision Rules
        - When continuing retrieval, output a JSON list of strategy objects.
        - Each strategy object must have:
          - `action`: fixed as `call_tool`
          - `ParentNode`: evidence node ID (e.g., `chunk_xxx`) or `"0"` for global planning
          - `tool_name`: usually `strategy_semantic_search`, `strategy_metadata_search` or `strategy_exact_search`
          - `args`: tool arguments
          - `reason`: concise rationale

        ## Strategy Types
        1. **ParentNode Selection**:
           - Set to `"0"` for **BROADER (Exploration)**: discovering new directions when results are repetitive or sparse.
           - Set to a specific node ID (e.g., `"chunk_xxx"`) for **DEEPER (Exploitation)**: following up on a promising node to build an evidence chain.

        2. **Search Methods**:
           - `strategy_semantic_search`: Used for semantic similarity retrieval. Parameter: `query_intent` (a natural language phrase or sentence describing what you are looking for).
           - `strategy_metadata_search`: Used for retrieving a specific paper to explore its context. Parameter: `paper_id` (the ID of the paper).
           - `strategy_exact_search`: Used for exact text matching in the database. Parameter: `query_intent`. **IMPORTANT**: For exact search, you MUST use ONLY one or two specific proper nouns (e.g. "PM2.5" or "CNN-LSTM") rather than long phrases or sentences to prevent getting zero results. You should heavily refer to the `suggested_keywords` provided in the evaluation feedback.

        Before outputting each strategy, internally check:
        - Relevance to the original user question (0-10)
        - Novelty vs historical strategies (0-10)
        Only output if both are >= 7.

        # Historical Strategies
        Use historical strategies to avoid duplication and to improve novelty.
        """)
        self.outputregulate = '''
        In this round, you must output about __PLANS_PER_ROUND__ distinct retrieval strategies.
        Except for `finish`, every item must be an `action: "call_tool"` strategy.
        Output JSON ONLY. Do not output any extra commentary.
        For retrieval volume control: only `strategy_semantic_search` and `strategy_exact_search` should target about __RAG_RESULT_PER_PLAN__ results via `n_results`.
        Metadata/multimodal tools are not constrained by this hyperparameter.
        Stay strictly within scientific research scope (avoid unrelated policy/public-health narratives unless directly required by the query).
        **Output format (must be JSON LIST)**:
        [
            {
                "action": "call_tool",
                "ParentNode": "0",
                "tool_name": "strategy_semantic_search", 
                "args": { "query_intent": "PM2.5 chemical composition and source analysis" },
                "reason": "我查看了当前的检索结果，发现已有研究关注PM2.5的浓度变化，但对其化学组成和具体来源的研究还不够深入。我认为有必要探索其他关于PM2.5化学组成分析和来源解析的研究，以获得更全面的理解。"
            },
            {
                "action": "call_tool",
                "ParentNode": "chunk_003329",
                "tool_name": "strategy_metadata_search", 
                "args": { "paper_id": "3" },
                "reason": "这个结果详细讨论了大气污染物的监测方法，评估者对其高度评价。我认为有必要深入查看这篇论文的完整内容，了解其研究方法和具体发现，以便进一步验证和扩展相关研究。"
            },
            {
                "action": "call_tool",
                "ParentNode": "0",
                "tool_name": "strategy_exact_search", 
                "args": { "query_intent": "VOC" },
                "reason": "需要精确查找文献中明确提到'VOC'的段落，不希望引入过于宽泛的语义结果，因此采用精确文本匹配检索。"
            },
            {
                "action": "call_tool",
                "ParentNode": "chunk_002431",
                "tool_name": "strategy_semantic_search", 
                "args": { "query_intent": "大气扩散模型的改进与应用研究" },
                "reason": "当前结果中提到了大气污染物的扩散，但对扩散模型的具体应用和改进研究还不够深入。我认为探索大气扩散模型的最新改进和应用，对提高污染物预测的准确性非常重要。"
            }
        ]
        Or when evidence is already sufficient:
        [ { "action": "finish", "reason": "Evidence is sufficient to answer the user question, so retrieval can stop." } ]
        '''
        # 保留模板，避免 handle_user 多次运行时重复 replace 造成占位符丢失
        self.outputregulate_template = self.outputregulate
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

    async def push_update(self):
        """主动调用 WebSocket 推送当前 Graph 和 ExperimentResult（包含 plansummary）"""
        if self.ws_manager:
            # 注意：确保你的 connection.py / main.py 里的 manager 有 broadcast_graph 方法
            await self.ws_manager.broadcast_graph(self.graph)
            # 同时发送 experiment_result，以便前端获取 plansummary
            if self.experiment_result and self.experiment_result.iterations:
                await self.ws_manager.broadcast_experiment_result(self.experiment_result)

    @message_handler
    async def handle_user(self, message: UserRequest, ctx: MessageContext) -> None:
        logger.log("Orchestrator", f"收到目标: {message.query}", "START")
        # 控制每轮 orchestrator_plan 输出多少个策略（call_tool）
        plans_per_round = getattr(message, "plans_per_round", 3)
        try:
            plans_per_round = int(plans_per_round)
        except Exception:
            plans_per_round = 3
        plans_per_round = max(1, min(plans_per_round, 10))

        # 控制每个策略希望返回多少条检索结果（由工具入参 n_results 控制）
        rag_result_per_plan = getattr(message, "rag_result_per_plan", 10)
        try:
            rag_result_per_plan = int(rag_result_per_plan)
        except Exception:
            rag_result_per_plan = 10
        rag_result_per_plan = max(1, min(rag_result_per_plan, 20))
        self.rag_result_per_plan = rag_result_per_plan

        # 控制最大轮次
        max_rounds = getattr(message, "max_rounds", 7)
        try:
            max_rounds = int(max_rounds)
        except Exception:
            max_rounds = 7
        self.max_rounds = max(1, min(max_rounds, 10))

        # 使用模板渲染，避免多次运行时占位符被 replace 掉
        self.outputregulate = self.outputregulate_template.replace("__PLANS_PER_ROUND__", str(plans_per_round)).replace(
            "__RAG_RESULT_PER_PLAN__", str(rag_result_per_plan)
        )

        self.graph.root_goal = message.query
        self.experiment_result.root_goal = message.query
        self._experiment_save_path = None  # 新查询使用新文件
        self.graph.nodes["0"] = GraphNode(id="0", type="ROOT", status="ACTIVE", content={"goal": message.query})
        await self.push_update()
        # 保存点1：用户提问后立即保存初始状态
        self._save_experiment_results_impl()
        
        # ⚡️ 修改：先使用用户问题本身进行检索，而不是直接让LLM自由生成策略
        await self._execute_initial_search(message.query, ctx)

    async def _execute_initial_search(self, query: str, ctx: MessageContext):
        """
        执行初始搜索：使用用户问题本身作为检索条件，并由大模型发散出两个新问题
        """
        logger.log("Orchestrator", "执行初始搜索：使用用户问题及大模型发散查询", "INITIAL_SEARCH")
        
        # 1. 尝试使用大模型生成两个相关的发散问题
        rewrite_prompt = f"""
        用户提出了一个科学问题："{query}"
        请你基于这个问题，生成另外2个不同的、发散的搜索查询短语（query intent），用于文献的语义检索。
        这些查询短语应该探索问题的不同侧面或相关概念。
        请仅返回一个包含这两个查询短语的JSON数组，格式如下：
        [
            "查询短语1",
            "查询短语2"
        ]
        不要输出任何其他解释性文字。
        """
        
        rewritten_queries = []
        try:
            from autogen_core.models import UserMessage
            response = await self.model_client.create(
                messages=[UserMessage(content=rewrite_prompt, source="user")],
                cancellation_token=ctx.cancellation_token
            )
            cleaned = response.content.replace("```json", "").replace("```", "").strip()
            import json
            parsed_queries = json.loads(cleaned)
            if isinstance(parsed_queries, list):
                rewritten_queries = [str(q) for q in parsed_queries[:2]]
        except Exception as e:
            logger.log("Orchestrator", f"初始问题改写失败，仅使用原问题: {e}", "WARN")
            
        # 2. 创建所有的搜索策略
        plans = []
        # 原问题策略
        plans.append(OrchestratorPlan(
            action="call_tool",
            tool_name="strategy_semantic_search",
            ParentNode="0",
            args={"query_intent": query, "n_results": self.rag_result_per_plan},
            reason="使用用户原始问题作为初始检索条件，获取相关文献基础"
        ))
        
        # 改写问题策略
        for i, rw_query in enumerate(rewritten_queries):
            plans.append(OrchestratorPlan(
                action="call_tool",
                tool_name="strategy_semantic_search",
                ParentNode="0",
                args={"query_intent": rw_query, "n_results": self.rag_result_per_plan},
                reason=f"大模型发散的扩展搜索角度 {i+1}"
            ))

        # 3. 准备迭代结果
        from protocols import IterationResult, QueryResult
        self.current_iteration = IterationResult(round_number=self.round_count)
        self.current_query_results.clear()
        
        # -----------------------------------------------------------------
        # ⚡️ 核心交互点：初始轮次的策略审查
        # -----------------------------------------------------------------
        if self.interactive_mode and self.pause_gate is not None:
            logger.log("Orchestrator", "开启了交互模式，暂停并等待用户审批初始发散计划...", "WAITING_USER")
            # 通知前端当前计划
            plan_dicts = [p.dict() for p in plans]
            import uuid
            checkpoint_id = str(uuid.uuid4())
            await self.ws_manager.broadcast_json({
                "type": "awaiting_user_plan",
                "run_id": self.run_id,
                "checkpoint_id": checkpoint_id,
                "round_number": self.round_count,
                "plans": plan_dicts
            })
            
            # 挂起协程，等待用户指令
            user_response = await self.pause_gate.wait(checkpoint_id)
            
            decision = user_response.get("decision", "abort")
            if decision == "abort":
                logger.log("Orchestrator", "用户选择了终止初始任务", "ABORT")
                await self._finish_task(ctx)
                return
            elif decision == "replace" or decision == "approve":
                user_plans = user_response.get("plans", [])
                new_plans = []
                for up in user_plans:
                    new_plan = OrchestratorPlan(**up)
                    new_plans.append(new_plan)
                plans = new_plans
                
                if len(plans) == 0:
                    logger.log("Orchestrator", "用户清空了所有初始任务，流程结束", "STOP")
                    await self._finish_task(ctx)
                    return
                logger.log("Orchestrator", f"用户审批完成，最终下发 {len(plans)} 个初始任务", "USER_APPROVED")

        for plan in plans:
            # 创建QueryResult并保存原始策略信息
            query_result = QueryResult(orchestrator_plan=plan)
            plan_id = json.dumps({
                'ParentNode': plan.ParentNode,
                'tool_name': plan.tool_name,
                'args': plan.args,
                'reason': plan.reason
            }, sort_keys=True)
            
            self.current_query_results[plan_id] = query_result
            self.current_iteration.query_results.append(query_result)
            
            # ⚡️ 推送策略计划创建消息（前端先画空框）
            if self.ws_manager:
                await self.ws_manager.broadcast_plan_created({
                    "round_number": self.round_count,
                    "plan_id": plan_id,
                    "orchestrator_plan": plan.model_dump(mode="json") if hasattr(plan, 'model_dump') else {
                        "action": plan.action,
                        "tool_name": plan.tool_name,
                        "ParentNode": plan.ParentNode,
                        "args": plan.args,
                        "reason": plan.reason
                    }
                })
            
            # 记录历史策略
            self.history_strategies.append(plan)
            
        # 4. 设置pending_tasks计数器
        self.pending_tasks = len(plans)
        
        # 5. 分发任务
        from protocols import OrchestratorPlanBatch
        await self.publish_message(OrchestratorPlanBatch(plans=plans), topic_id=TopicId(TOPIC_TOOL, source=self.id.key))
        
        logger.log("Orchestrator", f"初始搜索已启动，共 {len(plans)} 个策略，等待工具执行结果...", "INITIAL_SEARCH_STARTED")

    @message_handler
    async def handle_tool_batch(self, message: ToolOutputBatchMessage, ctx: MessageContext) -> None:
        total_result = sum(len(out.raw_items) for out in message.outputs)
        self.current_evaluate = []
        logger.log("ToolExecutor", f"执行: {len(message.outputs)} 条任务，返回 {total_result} 条数据", "BATCH_RECEIVE")
        new_items_buffer = [] #暂存区，放新的
        # duplicate_count = 0 # 重复计数
        #检索的结果先入库
        from protocols import RagResult
        
        for output in message.outputs:
            # [关键点 1] 获取并清洗 ParentNode
            # 确保它是字符串 "ROOT" 或者具体的 ID，防止 None 或数字 0 导致断链
            raw_parent = output.original_plan.ParentNode
            current_tool = output.original_plan.tool_name
            current_reason = output.original_plan.reason
            current_args = output.original_plan.args

            if raw_parent is None or str(raw_parent).strip() == "" or str(raw_parent) == "0":
                ParentNode = "0"
            else:
                ParentNode = str(raw_parent)
                
            # 查找对应的QueryResult
            plan_id = json.dumps({
                'ParentNode': output.original_plan.ParentNode,
                'tool_name': output.original_plan.tool_name,
                'args': output.original_plan.args,
                'reason': output.original_plan.reason
            }, sort_keys=True)
            
            search_record = NodeSearchRecord(
                round_index=self.round_count,
                source_tool=current_tool,
                source_args=current_args,
                parent_id=ParentNode
            )
            
            # ⚡️ 新增：策略统计变量
            total_items = len(output.raw_items)
            duplicate_items = 0
            current_new_ids = []
            
            for item in output.raw_items:
                # 保存原始检索数据到RagResult
                if plan_id in self.current_query_results:
                    rag_result = RagResult(retrieval_result=item)
                    self.current_query_results[plan_id].rag_results.append(rag_result)
                
                current_new_ids.append(item.id)
                self.current_round_ids.add(item.id)

                if item.id in self.graph.nodes:      #重复点
                    duplicate_items += 1
                    # 如果是根节点，不要修改它的属性
                    if item.id == "0" and self.graph.nodes[item.id].type == "ROOT":
                        continue
                    self.graph.nodes[item.id].hit_count += 1
                    self.graph.nodes[item.id].search_history.append(search_record)
                    # self.current_evaluate.append(self.graph.nodes[item.id])    # 重复点不用评估，但是要反馈给orchestra
                else:
                    # 如果item.id是"0"，并且根节点已经存在，给它分配一个新的ID
                    if item.id == "0" and "0" in self.graph.nodes:
                        # 生成一个新的ID
                        new_id = str(len(self.graph.nodes))
                        item.id = new_id

                    # -----------------------------------------------------------------
                    # 关键修复：统一 paper_id 字段，避免被误当成 chunkid
                    # -----------------------------------------------------------------
                    # 目前不同数据源的 metadata 里可能同时存在 paperid / paper_id 等字段。
                    # Orchestrator 后续在 prompt 和可视化里主要读取 paper_id，
                    # 若该字段缺失会导致 LLM 在 deeper 策略里把 chunkid 误填到 paper_id。
                    meta = item.metadata if isinstance(getattr(item, "metadata", None), dict) else {}
                    if meta:
                        # 优先补齐 paper_id
                        if not meta.get("paper_id"):
                            if meta.get("paperid"):
                                meta["paper_id"] = meta.get("paperid")
                        # 兼容某些数据源把 paper_id 放在 paperid 里（或反过来）
                        if not meta.get("paperid") and meta.get("paper_id"):
                            meta["paperid"] = meta.get("paper_id")
                        # 若 chunkid 缺失，用 node id 兜底（常见 chunk_xxxxxx）
                        if not meta.get("chunkid") and isinstance(item.id, str) and item.id.startswith("chunk_"):
                            meta["chunkid"] = item.id
                        # 写回 item，保证 ExperimentResult 中也被规范化
                        item.metadata = meta
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
                    elif ParentNode == "ROOT":
                        # 如果ParentNode是"ROOT"，添加到根节点"0"的children_ids中
                        self.graph.nodes["0"].children_ids.append(item.id)
                    new_items_buffer.append(item)
                    # 不在循环中推送，等所有节点添加完再推送
            
            # ⚡️ 推送检索完成消息（前端画灰色点）
            # 先推送 graph 更新（包含节点数据），再推送 retrieval_complete
            if self.ws_manager and current_new_ids:
                await self.push_update()  # 确保所有新节点数据已发送
                await self.ws_manager.broadcast_retrieval_complete(plan_id, current_new_ids)
            
            # ⚡️ 新增：更新策略统计信息
            # 更新当前查询结果的策略统计
            if plan_id in self.current_query_results:
                output.original_plan.total_results = total_items
                output.original_plan.duplicate_results = duplicate_items
                self.current_query_results[plan_id].orchestrator_plan = output.original_plan
            
            # 更新历史策略中的对应策略统计
            for i, strategy in enumerate(self.history_strategies):
                if (strategy.ParentNode == output.original_plan.ParentNode and
                    strategy.tool_name == output.original_plan.tool_name and
                    strategy.args == output.original_plan.args and
                    strategy.reason == output.original_plan.reason):
                    strategy.total_results = total_items
                    strategy.duplicate_results = duplicate_items
                    break
            
            logger.log("Orchestrator", f"策略统计: 工具={current_tool}, 总结果={total_items}, 重复={duplicate_items}", "STRATEGY_STATS")

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
        
        # ⚡️ 修复：工具执行完成后，递减pending_tasks计数器
        # 这样系统才知道当前轮次的任务已经完成，可以等待评估结果
        self.pending_tasks -= 1
        logger.log("Orchestrator", f"工具执行完成，剩余待处理任务: {self.pending_tasks}", "TOOL_COMPLETE")
        
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
                
                # ⚡️ 推送评估完成消息（前端给点上色）
                if self.ws_manager:
                    await self.ws_manager.broadcast_evaluation_complete(
                        nid,
                        eval_res.model_dump(mode="json") if hasattr(eval_res, 'model_dump') else {
                            "target_evidence_id": eval_res.target_evidence_id,
                            "branch_action": eval_res.branch_action,
                            "extracted_insight": eval_res.extracted_insight,
                            "scores": eval_res.scores,
                            "reason": eval_res.reason
                        }
                    )
                
                await self.push_update()
            
            # 将评估信息保存到对应的RagResult中
            if self.current_iteration:
                for query_result in self.current_iteration.query_results:
                    for rag_result in query_result.rag_results:
                        if rag_result.retrieval_result.id == nid:
                            rag_result.evaluation = eval_res
                            break

        # 4. 批处理计数器递减 (核心循环控制)
        self.pending_eval_batches -= 1
        logger.log("Orchestrator", f"评估包处理完毕。剩余待处理包数: {self.pending_eval_batches}", "BATCH_PROGRESS")

        # 5. 检查本轮是否完全结束
        if self.pending_eval_batches <= 0:
            # 保险归零，防止负数
            self.pending_eval_batches = 0
            
            # 将当前迭代结果添加到实验结果中
            if self.current_iteration:
                self.experiment_result.iterations.append(self.current_iteration)
            
            # 推进轮次
            self.round_count += 1
            logger.log("Orchestrator", f"=== 第 {self.round_count-1} 轮全部分支已闭环 ===", "ROUND_DONE")
            # 保存点2：每轮结束后立即保存（含本轮迭代数据）
            self._save_experiment_results_impl()
            
            # 如果是追问模式，执行完本轮就直接停止
            if self.is_follow_up_mode:
                logger.log("Orchestrator", "追问模式：完成单次检索和评估，流程结束。", "FOLLOW_UP_DONE")
                # 可选地，直接发送实验数据给前端（利用现有的机制）
                return

            # 收集当前轮次的证据数据
            current_evidence_data = []
            for nid in self.current_round_ids:
                if nid in self.graph.nodes:
                    node = self.graph.nodes[nid]
                    # 从节点创建RawEvidenceItem
                    evidence_item = RawEvidenceItem(
                        id=node.id,
                        source_tool=node.source_tool,
                        content=node.content,
                        metadata=node.metadata,
                        score=0.0,
                        source_args=node.source_args
                    )
                    current_evidence_data.append(evidence_item)
            
            # 在节点评估完成之后、下一轮新策略生成之前运行InteractionSummaryAgent
            logger.log("Orchestrator", "调用InteractionSummaryAgent进行本轮综合总结", "SUMMARY_CALL")
            await self.publish_message(
                SummaryRequest(
                    experiment_result=self.experiment_result,
                    current_evidence_data=current_evidence_data,
                    current_question=self.graph.root_goal,
                    user_original_input=self.graph.root_goal
                ),
                topic_id=TopicId(TOPIC_SUMMARY, source=self.id.key)
            )
            
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
        # 构建历史策略信息
        history_strategies_text = ""
        if self.history_strategies:
            history_strategies_text = "\n\n## 📋 历史策略回顾 (避免重复，参考创新)，不要生成重复的策略。\n"
            for i, strategy in enumerate(self.history_strategies, 1):
                # 使用OrchestratorPlan的属性
                history_strategies_text += f"{i}. 父节点: {strategy.ParentNode or '0'}, 工具: {strategy.tool_name or 'unknown'}, 参数: {strategy.args}\n"
                history_strategies_text += f" (搜到: {strategy.total_results}条, 重复: {strategy.duplicate_results}条)" if strategy.total_results > 0 else ""
        
        # ⚡️ 修改：处理初始搜索的特殊情况
        if self.round_count == 0 and len(self.current_round_ids) == 0:
            # 第一次调用，还没有任何评估结果，使用用户问题本身作为基础
            self.strategyhis = f'''User question: {self.graph.root_goal}. Every strategy must directly serve this question and avoid irrelevant drift.
            Current state: this is the first planning step after initial semantic retrieval, and the system has {len(self.graph.nodes) - 1} relevant evidence nodes.

            Plan the next retrieval strategies based on these initial results. You may consider:
            1. Deeper follow-up on specific promising nodes
            2. Broader semantic expansion using discovered keywords
            3. Exploration of related multimodal evidence

            {history_strategies_text}'''
        else:
            # 正常情况：有评估结果
            self.strategyhis = f'''User question: {self.graph.root_goal}. Every strategy must directly serve this question and avoid irrelevant drift.
            Current interaction rounds: {self.round_count}. Current evidence nodes: {len(self.graph.nodes)}.
            {history_strategies_text}'''
            self.searchpro = "Below are evaluator-reviewed retrieval results. Use them to decide whether to expand along current evidence chains or explore new directions."
            if self.current_round_ids:
                logger.log("Orchestrator", f"当前评估节点{len(self.current_round_ids)}个:", "PLANNING")
                for nid in self.current_round_ids:
                    node = self.graph.nodes[nid]

                    id = node.id
                    content = node.content
                    print(node)
                    paperid = node.metadata.get("paper_id") if node.metadata else None
                    keywords = node.metadata.get("key_entities") if node.metadata else None
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
                        self.searchpro += f'''Evidence node ID: {id}. Retrieved via tool(s): {source_tool}. Args: {source_args}.
                        This is hit #{hitcount}. Evaluator result: score={evaluation.scores}, action=[{evaluation.branch_action}].
                        Evaluator insight: {evaluation.extracted_insight}. Reason: {evaluation.reason}. Suggested keywords: {evaluation.suggested_keywords}.
                        Node content: {content}. Paper ID: {paperid}. Keywords: {keywords}\n
                        --------------------------------------------------\n'''
                    
                    else:
                        # ✅ 情况 B: 无评估结果 (重复命中)
                        # 使用简化版 Prompt，避免调用 evaluation.scores
                        self.searchpro += f'''Evidence node ID: {id}. Retrieved via tool(s): {source_tool}. Args: {source_args}.
                This is hit #{hitcount} (duplicate hit).
                Status: ⏳ [PENDING/DUPLICATE] (no fresh detailed evaluation in this cycle; refer to historical info/metadata).
                Node content: {content}. Paper ID: {paperid}. Keywords: {keywords}\n
--------------------------------------------------\n'''
                self.current_round_ids.clear()
                # prompt += f'''证据节点ID: {id}, 选择了{source_tool}工具, 工具参数为{source_args}。
                # 本次是第{hitcount}次检索到, 评估人员已评估，评估分数为{evaluation.scores},认为其内容值得{evaluation.branch_action}。
                # 具体而言评估人员总结条目内容为{evaluation.extracted_insight},理由是{evaluation.reason},他抽取处理一些关键词推荐给你{evaluation.suggested_keywords}。
                # 这个条目的具体内容是: {content}, 来自论文ID: {paperid}, 关键词: {keywords}\n'''
        # 生成规范
        prompt =""
        prompt += self.strategyhis
        prompt += self.searchpro
        prompt += self.outputregulate        
        
        # ⚡️ 新增：记录完整的prompt内容
        # logger.log_prompt(self.round_count, prompt)
        
        logger.log("Orchestrator", "思考并发策略...", "PLANNING")
        response = await self.model_client.create(
            messages=[self.system_message, UserMessage(content=prompt, source="user")],
            cancellation_token=ctx.cancellation_token
        )
        # 记录 LLM 交互
        logger.log_llm_interaction(
            source="Orchestrator",
            prompt=prompt,
            response=response.content,
            system_message=self.system_message.content if self.system_message else None
        )
        logger.log_prompt(self.round_count, prompt, response.content)
        
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

            # 为当前轮次创建IterationResult
            from protocols import IterationResult, QueryResult
            self.current_iteration = IterationResult(round_number=self.round_count)
            self.current_query_results.clear()
        
            #分发消息
            plans = []
            for decision in valid_tasks:
                tool_name = decision.get('tool_name', 'unknown')
                args = decision.get('args', {}) # 确保是字典
                reason = decision.get('reason', '')
                ParentNode = decision.get('ParentNode', '0')
                
                # 只让语义检索和精确检索受 n_results 超参数控制
                if not isinstance(args, dict):
                    args = {}
                if tool_name in ["strategy_semantic_search", "strategy_exact_search"]:
                    args["n_results"] = self.rag_result_per_plan
                else:
                    # metadata/多模态不受该超参数控制：移除 LLM 里可能带的 n_results
                    if "n_results" in args:
                        del args["n_results"]
                if ParentNode is None or str(ParentNode).strip() == "" or str(ParentNode) == "0":
                    ParentNode = "0"
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

            # -----------------------------------------------------------------
            # ⚡️ 核心交互点：如果是互动模式，且有暂停门，则暂停等待用户审批
            # -----------------------------------------------------------------
            if self.interactive_mode and self.pause_gate is not None:
                logger.log("Orchestrator", "开启了交互模式，暂停并等待用户审批计划...", "WAITING_USER")
                # 通知前端当前计划
                plan_dicts = [p.dict() for p in plans]
                import uuid
                checkpoint_id = str(uuid.uuid4())
                await self.ws_manager.broadcast_json({
                    "type": "awaiting_user_plan",
                    "run_id": self.run_id,
                    "checkpoint_id": checkpoint_id,
                    "round_number": self.round_count,
                    "plans": plan_dicts
                })
                
                # 挂起协程，等待用户指令（通过 pause_gate）
                # wait() 方法应返回用户修改后的 decision (e.g. {"decision": "approve", "plans": [...]})
                user_response = await self.pause_gate.wait(checkpoint_id)
                
                decision = user_response.get("decision", "abort")
                if decision == "abort":
                    logger.log("Orchestrator", "用户选择了终止任务", "ABORT")
                    await self._finish_task(ctx)
                    return
                elif decision == "replace" or decision == "approve":
                    # 无论是原样批准还是修改，我们都直接采用前端回传的 plans 作为最终执行计划
                    user_plans = user_response.get("plans", [])
                    new_plans = []
                    for up in user_plans:
                        new_plan = OrchestratorPlan(**up)
                        new_plans.append(new_plan)
                    plans = new_plans
                    self.pending_tasks = len(plans)
                    
                    if self.pending_tasks == 0:
                        logger.log("Orchestrator", "用户清空了所有任务，流程结束", "STOP")
                        await self._finish_task(ctx)
                        return
                    logger.log("Orchestrator", f"用户审批完成，最终下发 {self.pending_tasks} 个有效任务", "USER_APPROVED")
                
            for plan in plans:
                # ⚡️ 优化：记录历史策略 (使用OrchestratorPlan)
                # 直接使用plan对象，它已经包含了所有必要信息
                self.history_strategies.append(plan)
                
                # 创建QueryResult并保存原始策略信息
                query_result = QueryResult(orchestrator_plan=plan)
                # 使用JSON序列化的策略作为唯一标识
                plan_id = json.dumps({
                    'ParentNode': plan.ParentNode,
                    'tool_name': plan.tool_name,
                    'args': plan.args,
                    'reason': plan.reason
                }, sort_keys=True)
                self.current_query_results[plan_id] = query_result
                self.current_iteration.query_results.append(query_result)

            # 记录本轮策略生成日志
            logger.log("Orchestrator", f"本轮生成 {len(valid_tasks)} 个策略，历史策略总数: {len(self.history_strategies)}", "STRATEGY_HISTORY")
            
            await self.publish_message(OrchestratorPlanBatch(plans=plans), topic_id=TopicId(TOPIC_TOOL, source=self.id.key))                
        except Exception as e:
            logger.log("Orchestrator", f"决策解析失败: {e}", "ERROR", detail_data=response.content)
            self.pending_tasks = 0
            await self._finish_task(ctx)

    def save_raw_round_results(self, round_number):
        """保存每一轮的原始结果"""
        # 查找当前轮次的迭代结果
        current_round_iteration = None
        for iteration in self.experiment_result.iterations:
            if iteration.round_number == round_number:
                current_round_iteration = iteration
                break
        
        if not current_round_iteration:
            logger.log("Orchestrator", f"未找到第 {round_number} 轮的迭代结果", "WARN")
            return
        
        # 保存到JSON文件
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def save_experiment_results(self) -> Optional[str]:
        """保存整个实验的所有原始结果。若为首次保存则创建新文件，否则覆盖已有文件。返回保存路径。"""
        return self._save_experiment_results_impl()

    def _save_experiment_results_with_path(self) -> Optional[str]:
        """与 save_experiment_results 相同，返回保存路径供 Hypothesis 追加使用。"""
        return self._save_experiment_results_impl()

    def _save_experiment_results_impl(self) -> Optional[str]:
        """内部实现：多保存点复用同一文件，首次创建后续覆盖。"""
        # 确保root_goal已设置
        if not self.experiment_result.root_goal and self.graph.root_goal:
            self.experiment_result.root_goal = self.graph.root_goal
        
        import os
        if not os.path.isdir("logs"):
            os.makedirs("logs", exist_ok=True)
        
        # 首次保存：创建新文件并记录路径；后续保存：覆盖同一文件
        if self._experiment_save_path is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self._experiment_save_path = f"logs/experiment_results_{timestamp}.json"
        
        try:
            with open(self._experiment_save_path, "w", encoding="utf-8") as f:
                f.write(self.experiment_result.model_dump_json(indent=2, ensure_ascii=False))
            logger.log("Orchestrator", f"实验结果已保存到: {self._experiment_save_path}", "SAVE")
            print(f"\n💾 [System] 实验结果已保存: {self._experiment_save_path}")
            return self._experiment_save_path
        except Exception as e:
            logger.log("Orchestrator", f"保存实验结果失败: {e}", "ERROR")
            print(f"\n❌ [System] 保存实验结果失败: {e}")
            return None
    
    async def _finish_task(self, ctx):
        logger.log("Orchestrator", "发送最终图谱给总结者", "HANDOFF")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存整个实验的原始结果，并记录路径供 Hypothesis 完成后追加保存
        save_path = self._save_experiment_results_with_path()
        
        # 保存可视化数据和图谱状态
        vis_data = self.generate_vis_data()
        
        # 发送任务完成消息给HypothesisGeneratorAgent，传入保存路径以便 Hypothesis 完成后覆盖保存
        await self.publish_message(
            TaskComplete(
                graph_snapshot=self.graph,
                experiment_result=self.experiment_result,
                experiment_save_path=save_path
            ),
            topic_id=TopicId(TOPIC_HYPOTHESIS, source=self.id.key)
        ) 
    
    @message_handler
    async def handle_expand_search(self, message: ExpandSearchRequest, ctx: MessageContext) -> None:
        """处理卡片扩展检索请求"""
        logger.log("Orchestrator", f"收到卡片扩展检索请求: 父节点={message.parent_node_id}, 类型={message.search_type}, 查询={message.search_query}", "EXPAND_SEARCH")
        
        # 根据检索类型生成检索策略
        if message.search_type == "semantic":
            # 语义检索策略
            plan = OrchestratorPlan(
                action="call_tool",
                ParentNode=message.parent_node_id,
                tool_name="strategy_semantic_search",
                args={"query_intent": message.search_query, "n_results": self.rag_result_per_plan},
                reason=message.reason
            )
        elif message.search_type == "metadata":
            # 元数据检索策略
            plan = OrchestratorPlan(
                action="call_tool",
                ParentNode=message.parent_node_id,
                tool_name="strategy_metadata_search",
                args={"paper_id": message.search_query},
                reason=message.reason
            )
        else:
            logger.log("Orchestrator", f"无效的检索类型: {message.search_type}", "ERROR")
            return
        
        # 生成单个任务的批次
        batch = OrchestratorPlanBatch(plans=[plan])
        
        # 发送到 ToolExecutor
        await self.publish_message(batch, topic_id=TopicId(TOPIC_TOOL, source=self.id.key))
        
        # 设置为处理中状态
        self.pending_tasks = 1

    @message_handler
    async def handle_follow_up(self, message: FollowUpRequest, ctx: MessageContext) -> None:
        """
        处理追问：只做一次检索 + 评估。
        关键：round_number 由前端指定，用于把小矩形放到最后一轮 iteration 中。
        """
        query = (message.query or "").strip()
        if not query:
            return

        # 把 round_count 强制设置为前端指定轮次，保证 created_at_round 和 plan_created 的 round_number 对齐
        try:
            self.round_count = int(message.round_number)
        except Exception:
            self.round_count = 0

        try:
            self.rag_result_per_plan = int(message.rag_result_per_plan)
        except Exception:
            pass

        parent_id = (message.parent_node_id or "0")

        logger.log("Orchestrator", f"收到追问请求: round={self.round_count}, parent={parent_id}, query={query}", "FOLLOW_UP")

        # 构造单条精确文本检索 plan
        follow_plan = OrchestratorPlan(
            action="call_tool",
            tool_name="strategy_semantic_search",  # 恢复追问为语义检索
            ParentNode=parent_id,
            args={"query_intent": query, "n_results": self.rag_result_per_plan},
            reason="用户追问：直接检索并评估（跳过规划）"
        )

        # 创建 iteration/query_result 结构（让 experiment_result/前端小矩形逻辑一致）
        from protocols import IterationResult, QueryResult, OrchestratorPlanBatch
        self.current_iteration = IterationResult(round_number=self.round_count)
        self.current_query_results.clear()

        query_result = QueryResult(orchestrator_plan=follow_plan)
        plan_id = json.dumps({
            'ParentNode': follow_plan.ParentNode,
            'tool_name': follow_plan.tool_name,
            'args': follow_plan.args,
            'reason': follow_plan.reason
        }, sort_keys=True)
        self.current_query_results[plan_id] = query_result
        self.current_iteration.query_results.append(query_result)

        # 推送 plan_created：前端先画小矩形
        if self.ws_manager:
            await self.ws_manager.broadcast_plan_created({
                "round_number": self.round_count,
                "plan_id": plan_id,
                "orchestrator_plan": follow_plan.model_dump(mode="json") if hasattr(follow_plan, 'model_dump') else {
                    "action": follow_plan.action,
                    "tool_name": follow_plan.tool_name,
                    "ParentNode": follow_plan.ParentNode,
                    "args": follow_plan.args,
                    "reason": follow_plan.reason
                }
            })

        # 分发任务并等待 tool/eval 回流（复用现有 handle_tool_batch / evaluator 流程）
        self.pending_tasks = 1
        await self.publish_message(OrchestratorPlanBatch(plans=[follow_plan]), topic_id=TopicId(TOPIC_TOOL, source=self.id.key))


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
        # Role
        You are an **Evaluator** in a scientific literature investigation team.
        Your task is to evaluate each retrieved evidence item independently and provide structured feedback for planning.

        # Evaluation Logic
        Read title, summary, and insight carefully.
        If an image is available, include visual judgment.

        1. **branch_action**
           - **GROW**: high-value evidence, strongly relevant, with clear follow-up clues.
           - **KEEP**: medium-value evidence, relevant but limited expansion value.
           - **PRUNE**: low-value evidence, irrelevant/noisy/redundant.

        2. **extracted_insight**
           - Provide a concrete scientific observation, not generic praise.

        3. **suggested_keywords**
           - Extract potentially useful technical terms for follow-up search.

        # Output Format (JSON List)
        Return a JSON list only (no Markdown).
        [
          {
            "target_evidence_id": "fig_001",
            "branch_action": "GROW",
            "extracted_insight": "The figure shows a positive correlation between winter PM2.5 peaks and respiratory emergency visits.",
            "scores":{"relevance": 9, "credibility": 8},
            "reason": "High-value trend evidence with follow-up paper-level traceability.",
            "suggested_keywords": ["time-series analysis", "respiratory emergency visits"]
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
        prompt_text = "Please evaluate the following newly retrieved evidence items (JSON list format):\n"
        
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
            # 记录 LLM 交互
            logger.log_llm_interaction(
                source="Evaluator",
                prompt=prompt_text,
                response=response.content,
                system_message=self.system_message.content if self.system_message else None
            )
            
            # 4. 解析结果
            raw_content = response.content
            # 清洗 Markdown
            cleaned = raw_content.replace("```json", "").replace("```", "").strip()
            
            eval_list_data = json.loads(cleaned)
            
            # 转换为 Pydantic 对象列表
            evaluations = []
            skipped_count = 0
            for d in eval_list_data:
                # 容错处理：确保 target_evidence_id 存在
                if "target_evidence_id" not in d:
                    skipped_count += 1
                    logger.log("Evaluator", f"⚠️ 跳过缺少 target_evidence_id 的评估条目: {d}", "WARN")
                    continue 
                try:
                    evaluations.append(ItemEvaluation(**d))
                except Exception as e:
                    skipped_count += 1
                    logger.log("Evaluator", f"⚠️ 评估条目解析失败: {e}, 条目: {d}", "WARN")
            
            if len(evaluations) == 0 and len(message.new_items) > 0:
                logger.log("Evaluator", f"❌ 警告：评估了 {len(message.new_items)} 条证据，但最终生成 0 条报告（跳过 {skipped_count} 条）", "ERROR", detail_data={"raw_response": raw_content[:500], "cleaned": cleaned[:500]})
            
            logger.log("Evaluator", f"评估完成，生成 {len(evaluations)} 条报告（跳过 {skipped_count} 条）", "REPORT", detail_data=cleaned)
            
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


# --- D. 总结智能体 (InteractionSummaryAgent) ---
@type_subscription(topic_type=TOPIC_SUMMARY)
class InteractionSummaryAgent(RoutedAgent):
    def __init__(self, model_client: OpenAIChatCompletionClient, websocket_manager=None) -> None:
        super().__init__("InteractionSummaryAgent")
        self.model_client = model_client
        self.ws_manager = websocket_manager
        self.system_message = SystemMessage(content="""
        # Role
        You are a **Summary Specialist**.
        You produce structured and reliable summaries of the retrieval process.

        # Responsibilities
        1. Process summary: synthesize what was asked, searched, and found.
        2. Visualization support: provide keyword-oriented data for word-cloud style views.
        3. Retrieval quality assessment: evaluate relevance, accuracy, authority, and completeness.

        # Output Requirements
        - Be concise but informative.
        - Keep logic clear and highlight key findings.
        - Provide actionable quality assessment dimensions.
        """)
    @message_handler 
    async def handle_summary_request(self, message: SummaryRequest, ctx: MessageContext) -> None:
        """
        处理总结请求，生成过程总结、词云数据和检索质量评估
        """
        logger.log("InteractionSummaryAgent", "收到总结请求，开始分析实验结果...", "SUMMARY_START")
        
        try:
            # 1. 生成过程总结（使用当前轮次的证据数据、当前小问题和用户原始输入）
            process_summary = await self.generate_process_summary(
                message.experiment_result,
                message.current_evidence_data,
                message.current_question,
                message.user_original_input
            )
            
            # 2. 生成词云数据
            word_cloud_data = await self.generate_word_cloud(
                message.experiment_result,
                message.current_evidence_data
            )
            
            # 3. 评估检索质量
            quality_evaluation = await self.evaluate_retrieval_quality(message.experiment_result)
            
            # 4. 生成时间戳
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 5. 构建响应消息（按 iteration 粒度的整体总结）
            summary_response = SummaryResponse(
                process_summary=process_summary,
                word_cloud_data=word_cloud_data,
                quality_evaluation=quality_evaluation,
                timestamp=timestamp
            )
            
            # 6. 保存「整轮」总结结果到实验结果中：
            #    - summary: 作为整个实验的“最新/最终总结”（保持原语义）
            #    - latest_iteration.iteration_summary: 紧跟在该轮 round_number 后面的本轮总结
            message.experiment_result.summary = summary_response
            try:
                # 推断当前轮次（优先使用最新 Iteration 的 round_number）
                if message.experiment_result.iterations:
                    latest_iteration = message.experiment_result.iterations[-1]
                    current_round = latest_iteration.round_number
                    latest_iteration.iteration_summary = IterationSummary(
                        round_number=current_round,
                        process_summary=process_summary,
                        timestamp=timestamp,
                    )
            except Exception as e:
                # 记录但不中断主流程；即使写入 iteration_summary 失败，也至少保留 summary
                logger.log(
                    "InteractionSummaryAgent",
                    f"写入iteration_summary时出错: {e}",
                    "ERROR"
                )
            
            # 7. 为当前轮次的每个策略生成「按策略粒度」的单独总结
            #    不再把整轮的 process_summary 直接复制给每个 plan，
            #    而是根据各自的检索结果、参数等信息生成更贴近该策略本身的 summary。
            if message.experiment_result.iterations:
                latest_iteration = message.experiment_result.iterations[-1]
                for query_result in latest_iteration.query_results:
                    if not query_result.orchestrator_plan:
                        continue
                    try:
                        plan_summary = await self.generate_plan_summary(
                            experiment_result=message.experiment_result,
                            query_result=query_result,
                            current_question=message.current_question,
                            user_original_input=message.user_original_input,
                        )
                        query_result.orchestrator_plan.plansummary = plan_summary
                    except Exception as e:
                        logger.log(
                            "InteractionSummaryAgent",
                            f"生成单个策略总结时出错: {e}",
                            "ERROR"
                        )
                        # 失败时不影响整体流程
            
            # 8. 实时保存总结结果到系统日志中
            logger.log("InteractionSummaryAgent", f"本轮总结: {process_summary}...", "SUMMARY_LOG")
            
            # 9. 完整记录summary_response到日志
            logger.log("InteractionSummaryAgent", f"总结响应详情: {summary_response.model_dump_json()}", "SUMMARY_DETAIL")
            
            # 10. 记录日志
            logger.log("InteractionSummaryAgent", "总结生成完成", "SUMMARY_COMPLETE")
            
            # 10.5 保存点：总结完成后立即保存 experiment（含 plansummary）到 JSON
            import glob
            import os
            logs_dir = "logs"
            if os.path.isdir(logs_dir):
                files = glob.glob(os.path.join(logs_dir, "experiment_results_*.json"))
                if files:
                    latest_file = max(files, key=os.path.getmtime)
                    try:
                        with open(latest_file, "w", encoding="utf-8") as f:
                            f.write(message.experiment_result.model_dump_json(indent=2, ensure_ascii=False))
                        logger.log("InteractionSummaryAgent", f"已更新 experiment JSON（含 plansummary）: {latest_file}", "SAVE")
                        print(f"\n💾 [InteractionSummaryAgent] 已保存 experiment 到: {latest_file}")
                    except Exception as save_err:
                        logger.log("InteractionSummaryAgent", f"保存 experiment 失败: {save_err}", "ERROR")
            
            # 11. 不发送响应消息（根据需求，此agent不主动发布信息）
            # 仅保存结果和记录日志
            
            # 11. 通过WebSocket返回结果
            # #region agent log
            try:
                import json as json_lib
                with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json_lib.dumps({"id":"log_summary_before_broadcast","timestamp":datetime.datetime.now().timestamp()*1000,"location":"engine.py:1108","message":"准备通过WebSocket发送总结","data":{"ws_manager_exists":self.ws_manager is not None},"sessionId":"debug-session","runId":"run1","hypothesisId":"D"})+"\n")
            except: pass
            # #endregion
            if self.ws_manager:
                await self.ws_manager.broadcast_summary(summary_response)
            else:
                # #region agent log
                try:
                    import json as json_lib
                    with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json_lib.dumps({"id":"log_summary_no_ws_manager","timestamp":datetime.datetime.now().timestamp()*1000,"location":"engine.py:1110","message":"ws_manager为None，跳过WebSocket发送","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+"\n")
                except: pass
                # #endregion
                
        except Exception as e:
            # #region agent log
            try:
                import json as json_lib
                with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json_lib.dumps({"id":"log_summary_exception","timestamp":datetime.datetime.now().timestamp()*1000,"location":"engine.py:1112","message":"InteractionSummaryAgent异常","data":{"error":str(e),"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+"\n")
            except: pass
            # #endregion
            logger.log("InteractionSummaryAgent", f"生成总结时出错: {e}", "ERROR", detail_data=traceback.format_exc())

     
    async def generate_plan_summary(
        self,
        experiment_result: ExperimentResult,
        query_result,
        current_question: str | None = None,
        user_original_input: str | None = None,
    ) -> str:
        """
        为单个 OrchestratorPlan 生成粒度为“策略级别”的总结。
        
        设计思路：
        - 以该 plan 对应的问题 / args 为核心，聚焦“这一条策略检索到了什么内容”；
        - 主要做内容层面的归纳总结，而不是再评价整轮检索流程；
        - 上下文尽量精简，只提供该策略相关的 rag_results 及其评估信息。
        """
        root_goal = experiment_result.root_goal
        plan = query_result.orchestrator_plan
        rag_results = query_result.rag_results or []

        total_results = getattr(plan, "total_results", len(rag_results))
        duplicate_results = getattr(plan, "duplicate_results", 0)

        prompt_lines = []
        prompt_lines.append("# Single Strategy Summary Task\n")
        prompt_lines.append("You are a summary specialist. Focus only on the single strategy below.")
        prompt_lines.append("Write a concise and focused content summary of what this strategy retrieved.")
        prompt_lines.append("Do not summarize the whole system and do not comment on other strategies.\n")

        prompt_lines.append("## Context\n")
        prompt_lines.append(f"- Original user question: {user_original_input or root_goal}\n")
        prompt_lines.append(f"- Current sub-question: {current_question or root_goal}\n")

        prompt_lines.append("## Strategy Information\n")
        prompt_lines.append(f"- Tool: {plan.tool_name}\n")
        prompt_lines.append(f"- Args: {plan.args}\n")
        prompt_lines.append(f"- Strategy rationale: {plan.reason}\n")
        prompt_lines.append(f"- Result stats: total {total_results}, duplicates {duplicate_results}\n\n")

        prompt_lines.append("## Retrieved Results for This Strategy\n")
        if not rag_results:
            prompt_lines.append("- No results were retrieved for this strategy. Briefly explain possible reasons.\n")
        else:
            result_idx = 0
            for rag_result in rag_results:
                rr = rag_result.retrieval_result
                ev = rag_result.evaluation

                content = rr.content or {}
                meta = rr.metadata or {}
                # 从 content 和 metadata 多种可能字段读取，兼容不同数据源
                title = (
                    content.get("title") or meta.get("title") or meta.get("paper_name") or ""
                )
                if isinstance(title, list):
                    title = " ".join(str(x) for x in title) if title else ""
                else:
                    title = str(title) if title else ""

                summary = content.get("summary") or meta.get("concise_summary") or meta.get("summary") or content.get("text") or ""
                if isinstance(summary, list):
                    summary = " ".join(str(x) for x in summary) if summary else ""
                else:
                    summary = str(summary) if summary else ""

                insight = content.get("insight") or meta.get("inferred_insight") or meta.get("insight") or ""
                if isinstance(insight, list):
                    insight = " ".join(str(x) for x in insight) if insight else ""
                else:
                    insight = str(insight) if insight else ""

                paper_id = meta.get("paper_id") or meta.get("paper_name") or meta.get("file_name") or ""
                key_entities = meta.get("key_entities") or meta.get("keywords") or []
                if not isinstance(key_entities, list):
                    key_entities = [key_entities] if key_entities else []

                # 若 content/metadata 为空，用评估的 extracted_insight 作为核心内容
                if not title and not summary and not insight and ev and ev.extracted_insight:
                    insight = ev.extracted_insight

                # 跳过完全空的结果
                has_content = bool(title or summary or insight or (ev and (ev.branch_action or ev.extracted_insight)))
                if not has_content:
                    continue

                result_idx += 1
                prompt_lines.append(f"- Result {result_idx} (ID: {rr.id}):\n")
                if title:
                    prompt_lines.append(f"  - Title: {title}\n")
                if summary:
                    prompt_lines.append(f"  - Summary/Content: {summary}\n")
                if insight:
                    prompt_lines.append(f"  - Insight: {insight}\n")
                if paper_id:
                    prompt_lines.append(f"  - Linked paper/source: {paper_id}\n")
                if key_entities:
                    ent_str = ", ".join(str(e) for e in key_entities)
                    prompt_lines.append(f"  - Keywords/Entities: {ent_str}\n")

                if ev:
                    prompt_lines.append(f"  - Eval action: {ev.branch_action}\n")
                    if ev.extracted_insight:
                        prompt_lines.append(f"  - Eval insight: {ev.extracted_insight}\n")
                    if ev.reason:
                        prompt_lines.append(f"  - Eval reason: {ev.reason}\n")
                prompt_lines.append("")

        prompt_lines.append("## Output Requirements\n")
        prompt_lines.append("1. Summarize only this strategy; do not discuss the overall system.")
        prompt_lines.append("2. Center on what problem this strategy targets and what types of evidence it retrieved.")
        prompt_lines.append("3. Highlight shared themes, critical information, and high-value leads from title/summary/insight.")
        prompt_lines.append("4. Use 1-2 natural paragraphs, concise and clear (not bullet lists).")
        prompt_lines.append("5. Output natural language only. No JSON or list schema.\n")

        prompt = "\n".join(prompt_lines)

        logger.log(
            "InteractionSummaryAgent",
            f"为单个策略生成总结时使用的提示: {prompt[:800]}...",
            "PLAN_SUMMARY_DEBUG"
        )

        try:
            response = await self.model_client.create(
                messages=[self.system_message, UserMessage(content=prompt, source="user")],
                cancellation_token=None
            )
            # 记录 LLM 交互
            logger.log_llm_interaction(
                source="InteractionSummaryAgent (Plan Summary)",
                prompt=prompt,
                response=response.content,
                system_message=self.system_message.content if self.system_message else None
            )
            return response.content
        except Exception as e:
            logger.log(
                "InteractionSummaryAgent",
                f"调用大模型生成单个策略总结时出错: {e}",
                "ERROR"
            )
            return "Failed to generate a detailed strategy summary. Only raw statistics/results are retained for later analysis."

    async def generate_process_summary(self, experiment_result: ExperimentResult, current_evidence_data=None, current_question=None, user_original_input=None) -> str:
        """
        生成过程总结
        """
        if not experiment_result.iterations:
            return "No retrieval results were produced in this run."
        
        summary_parts = []
        summary_parts.append(f"# Retrieval Process Summary\n")
        summary_parts.append(f"**Original user input**: {user_original_input or experiment_result.root_goal}\n")
        summary_parts.append(f"**Current sub-question**: {current_question or experiment_result.root_goal}\n")
        summary_parts.append(f"**Retrieval rounds**: {len(experiment_result.iterations)}\n\n")
        
        # 分析最新一轮迭代（每轮结束时进行综合总结）
        if experiment_result.iterations:
            latest_iteration = experiment_result.iterations[-1]
            summary_parts.append(f"## 第 {len(experiment_result.iterations)} 轮检索总结\n")
            
            # 分析本轮的查询策略
            for j, query_result in enumerate(latest_iteration.query_results):
                plan = query_result.orchestrator_plan
                summary_parts.append(f"- **策略 {j+1}**: {plan.tool_name}\n")
                summary_parts.append(f"  - **参数**: {plan.args}\n")
                summary_parts.append(f"  - **原因**: {plan.reason}\n")
                summary_parts.append(f"  - **结果**: 找到 {plan.total_results} 条，重复 {plan.duplicate_results} 条\n")
            
            # 分析本轮检索结果
            total_rag_results = sum(len(qr.rag_results) for qr in latest_iteration.query_results)
            summary_parts.append(f"- **本轮总结果**: {total_rag_results} 条\n\n")
        
        # 分析当前轮次的证据数据
        if current_evidence_data:
            summary_parts.append("## 当前轮次证据分析\n")
            summary_parts.append(f"- **证据数量**: {len(current_evidence_data)} 条\n")
            
            # 提取当前轮次的关键洞察
            current_insights = []
            for evidence in current_evidence_data:
                # 从证据中提取洞察
                if evidence.metadata and evidence.metadata.get('key_entities'):
                    current_insights.extend(evidence.metadata['key_entities'])
            
            # 去重并展示
            unique_current_insights = list(set(current_insights))[:10]
            if unique_current_insights:
                summary_parts.append(f"- **关键实体**: {', '.join(unique_current_insights)}\n\n")
        
        # 分析评估结果
        summary_parts.append("## 评估分析\n")
        
        # 统计各类型评估结果
        grow_count = 0
        keep_count = 0
        prune_count = 0
        
        for iteration in experiment_result.iterations:
            for query_result in iteration.query_results:
                for rag_result in query_result.rag_results:
                    if rag_result.evaluation:
                        if rag_result.evaluation.branch_action == "GROW":
                            grow_count += 1
                        elif rag_result.evaluation.branch_action == "KEEP":
                            keep_count += 1
                        elif rag_result.evaluation.branch_action == "PRUNE":
                            prune_count += 1
        
        summary_parts.append(f"- **高价值结果**: {grow_count} 条\n")
        summary_parts.append(f"- **中等价值结果**: {keep_count} 条\n")
        summary_parts.append(f"- **低价值结果**: {prune_count} 条\n\n")
        
        # 提取关键洞察
        summary_parts.append("## 关键洞察\n")
        key_insights = []
        
        for iteration in experiment_result.iterations:
            for query_result in iteration.query_results:
                for rag_result in query_result.rag_results:
                    if rag_result.evaluation and rag_result.evaluation.extracted_insight:
                        key_insights.append(rag_result.evaluation.extracted_insight)
        
        # 去重并取前5个关键洞察
        unique_insights = list(set(key_insights))[:5]
        for i, insight in enumerate(unique_insights):
            summary_parts.append(f"- {insight}\n")
        
        # 构建大模型提示
        prompt = f"# Retrieval Process Summary Task\n\n"
        prompt += f"## Input Context\n"
        prompt += f"**Original user input**: {user_original_input or experiment_result.root_goal}\n"
        prompt += f"**Current sub-question**: {current_question or experiment_result.root_goal}\n"
        prompt += f"**Retrieval rounds**: {len(experiment_result.iterations)}\n\n"
        
        # 添加检索信息
        if experiment_result.iterations:
            latest_iteration = experiment_result.iterations[-1]
            prompt += f"## Round {len(experiment_result.iterations)} Retrieval Details\n"
            for j, query_result in enumerate(latest_iteration.query_results):
                plan = query_result.orchestrator_plan
                prompt += f"- **Strategy {j+1}**: {plan.tool_name}\n"
                prompt += f"  - **Args**: {plan.args}\n"
                prompt += f"  - **Reason**: {plan.reason}\n"
                prompt += f"  - **Results**: {plan.total_results} found, {plan.duplicate_results} duplicates\n"
                
                # 添加每个rag结果的详细信息
                if query_result.rag_results:
                    prompt += f"  - **Detailed Results**:\n"
                    for k, rag_result in enumerate(query_result.rag_results[:3]):  # 限制前3个结果以避免提示过长
                        # 安全获取content
                        content = rag_result.retrieval_result.content
                        content_str = str(content) if content else "无内容"
                        prompt += f"    - **Result {k+1}**: {content_str[:100]}...\n"
                        if rag_result.evaluation:
                            prompt += f"      - **Evaluation**: {rag_result.evaluation.branch_action}\n"
                            prompt += f"      - **Scores**: {rag_result.evaluation.scores}\n"
                            # 安全获取extracted_insight
                            insight = rag_result.evaluation.extracted_insight
                            insight_str = str(insight) if insight else "无洞察"
                            prompt += f"      - **Insight**: {insight_str[:150]}...\n"
            total_rag_results = sum(len(qr.rag_results) for qr in latest_iteration.query_results)
            prompt += f"- **Total results this round**: {total_rag_results}\n\n"
        
        # 添加评估信息
        prompt += "## Evaluation Analysis\n"
        prompt += f"- **High-value results**: {grow_count}\n"
        prompt += f"- **Medium-value results**: {keep_count}\n"
        prompt += f"- **Low-value results**: {prune_count}\n\n"
        
        # 添加关键洞察
        prompt += "## Key Insights\n"
        for insight in unique_insights:
            prompt += f"- {insight}\n"
        
        prompt += "\n## Task Requirements\n"
        prompt += "1. Generate a coherent end-to-end retrieval summary based on the information above.\n"
        prompt += "2. Cover user question, strategy choices, retrieval outcomes, evaluation analysis, and key insights.\n"
        prompt += "3. Keep the logic clear and emphasize important findings.\n"
        prompt += "4. Use natural, fluent language and avoid unnecessary jargon.\n"
        prompt += "5. Keep the length moderate.\n"
        
        logger.log("InteractionSummaryAgent", f"调用大模型生成总结时的提示: {prompt}", "DEBUG")
        # 调用大模型生成总结
        try:
            response = await self.model_client.create(
                messages=[self.system_message, UserMessage(content=prompt, source="user")],
                cancellation_token=None
            )
            # 记录 LLM 交互
            logger.log_llm_interaction(
                source="InteractionSummaryAgent (Plan Summary)",
                prompt=prompt,
                response=response.content,
                system_message=self.system_message.content if self.system_message else None
            )
            return response.content
        except Exception as e:
            logger.log("InteractionSummaryAgent", f"调用大模型生成总结时出错: {e}", "ERROR")
            #  fallback to manual summary if LLM fails
            return "".join(summary_parts)
    
    async def generate_word_cloud(self, experiment_result: ExperimentResult, current_evidence_data=None) -> WordCloudData:
        """
        生成词云数据
        """
        word_freq = {}
        
        # 统计关键词频率
        for iteration in experiment_result.iterations:
            for query_result in iteration.query_results:
                # 统计查询参数中的关键词
                if query_result.orchestrator_plan.args:
                    if "query_intent" in query_result.orchestrator_plan.args:
                        query_text = query_result.orchestrator_plan.args["query_intent"]
                        # 简单分词
                        words = query_text.split()
                        for word in words:
                            word = word.lower().strip()
                            if word and len(word) > 1:
                                word_freq[word] = word_freq.get(word, 0) + 1
                
                # 统计检索结果中的关键词
                for rag_result in query_result.rag_results:
                    # 统计评估中的建议关键词
                    if rag_result.evaluation and rag_result.evaluation.suggested_keywords:
                        for keyword in rag_result.evaluation.suggested_keywords:
                            keyword = keyword.lower().strip()
                            if keyword and len(keyword) > 1:
                                word_freq[keyword] = word_freq.get(keyword, 0) + 2  # 给予更高权重
                    
                    # 统计元数据中的关键词
                    if rag_result.retrieval_result.metadata and "key_entities" in rag_result.retrieval_result.metadata:
                        key_entities = rag_result.retrieval_result.metadata["key_entities"]
                        if isinstance(key_entities, list):
                            for entity in key_entities:
                                entity = entity.lower().strip()
                                if entity and len(entity) > 1:
                                    word_freq[entity] = word_freq.get(entity, 0) + 1
        
        # 统计当前轮次证据数据中的关键词（给予最高权重）
        if current_evidence_data:
            for evidence in current_evidence_data:
                if evidence.metadata and "key_entities" in evidence.metadata:
                    key_entities = evidence.metadata["key_entities"]
                    if isinstance(key_entities, list):
                        for entity in key_entities:
                            entity = entity.lower().strip()
                            if entity and len(entity) > 1:
                                word_freq[entity] = word_freq.get(entity, 0) + 3  # 给予最高权重
        
        # 构建词云数据
        words = []
        for word, freq in word_freq.items():
            words.append({"text": word, "value": freq})
        
        # 按频率排序
        words.sort(key=lambda x: x["value"], reverse=True)
        
        # 提取前10个关键词
        top_keywords = [word["text"] for word in words[:10]]
        
        return WordCloudData(
            words=words,
            total_words=len(words),
            top_keywords=top_keywords
        )
    
    async def evaluate_retrieval_quality(self, experiment_result: ExperimentResult) -> RetrievalQualityEvaluation:
        """
        评估检索质量
        """
        if not experiment_result.iterations:
            return RetrievalQualityEvaluation(
                relevance_score=0.0,
                accuracy_score=0.0,
                authority_score=0.0,
                completeness_score=0.0,
                overall_score=0.0,
                positive_meaning="无检索结果",
                contribution_to_knowledge="无贡献",
                strengths=[],
                weaknesses=["未执行任何检索"],
                suggestions=["重新执行检索"]
            )
        
        # 计算各项评分
        total_evaluations = 0
        total_relevance = 0
        total_accuracy = 0
        total_authority = 0
        total_completeness = 0
        
        for iteration in experiment_result.iterations:
            for query_result in iteration.query_results:
                for rag_result in query_result.rag_results:
                    if rag_result.evaluation and rag_result.evaluation.scores:
                        total_evaluations += 1
                        total_relevance += rag_result.evaluation.scores.get("relevance", 0)
                        total_accuracy += rag_result.evaluation.scores.get("accuracy", 0)
                        total_authority += rag_result.evaluation.scores.get("authority", 0)
                        total_completeness += rag_result.evaluation.scores.get("completeness", 0)
        
        # 计算平均评分
        relevance_score = total_relevance / total_evaluations if total_evaluations > 0 else 0.0
        accuracy_score = total_accuracy / total_evaluations if total_evaluations > 0 else 0.0
        authority_score = total_authority / total_evaluations if total_evaluations > 0 else 0.0
        completeness_score = total_completeness / total_evaluations if total_evaluations > 0 else 0.0
        overall_score = (relevance_score + accuracy_score + authority_score + completeness_score) / 4
        
        # 分析问题的积极意义和价值
        positive_meaning = f"该问题针对 '{experiment_result.root_goal}' 进行了深入研究，通过多轮检索获取了相关信息。"
        contribution_to_knowledge = "通过系统性的检索策略，获取了多方面的相关信息，对该领域的知识有一定贡献。"
        
        # 分析检索过程的优势和不足
        strengths = ["采用了多轮检索策略", "综合使用了多种检索工具", "对检索结果进行了评估和筛选"]
        weaknesses = []
        suggestions = []
        
        # 根据评估结果分析不足和建议
        if relevance_score < 0.6:
            weaknesses.append("检索结果与问题的相关性较低")
            suggestions.append("优化检索关键词，提高相关性")
        
        if accuracy_score < 0.6:
            weaknesses.append("检索结果的准确性有待提高")
            suggestions.append("增加权威数据源，提高结果准确性")
        
        if authority_score < 0.6:
            weaknesses.append("检索结果的权威性不足")
            suggestions.append("优先选择权威期刊和来源的信息")
        
        if completeness_score < 0.6:
            weaknesses.append("检索结果的完整性不够")
            suggestions.append("扩展检索范围，获取更全面的信息")
        
        if not weaknesses:
            weaknesses.append("未发现明显不足")
            suggestions.append("继续保持当前的检索策略")
        
        return RetrievalQualityEvaluation(
            relevance_score=relevance_score,
            accuracy_score=accuracy_score,
            authority_score=authority_score,
            completeness_score=completeness_score,
            overall_score=overall_score,
            positive_meaning=positive_meaning,
            contribution_to_knowledge=contribution_to_knowledge,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions
        )
        


# --- D.1. 大纲生成者 (Hypothesis Coordinator) ---
@type_subscription(topic_type=TOPIC_HYPOTHESIS_COORDINATOR)
class HypothesisCoordinatorAgent(RoutedAgent):
    def __init__(self, model_client: OpenAIChatCompletionClient) -> None:
        super().__init__("HypothesisCoordinator")
        self.model_client = model_client
        self.system_message = SystemMessage(content="""
        You are an **Outline Generation Specialist**.
        Generate a structured report outline from high-level retrieval strategy summaries.

        # Tasks
        1. Analyze all plan summaries to understand macro intent and findings.
        2. Identify major themes and progressive sub-questions.
        3. Produce an outline with one core-hypothesis preview and 3-5 subtopics.
        4. Each subtopic should include 2-4 concrete sub-questions.

        # Output Requirements
        Output strict JSON:
        {
            "core_hypothesis_preview": "one-sentence preview",
            "subtopics": [
                {
                    "topic_name": "name",
                    "description": "description",
                    "sub_questions": ["q1", "q2", "..."],
                    "assigned_plan_ids": ["plan_id1", "plan_id2"],
                    "keywords": ["kw1", "kw2"]
                }
            ]
        }

        Notes:
        - sub_questions should progress from abstract to concrete.
        - assigned_plan_ids should match relevant plan summaries.
        """)
    
    @message_handler
    async def handle_outline_request(self, message: OutlineRequest, ctx: MessageContext) -> None:
        """处理大纲生成请求 - 基于 plan summaries（抽象层面）"""
        logger.log("HypothesisCoordinator", "开始生成大纲（基于 plan summaries）...", "OUTLINE_START")
        
        try:
            graph = message.graph_snapshot
            
            # 使用 plan_summaries 而不是具体的节点信息
            plan_summaries = message.plan_summaries
            if not plan_summaries:
                logger.log("HypothesisCoordinator", "没有 plan summaries，无法生成大纲", "WARNING")
                return
            
            # 构建prompt - 基于 plan summaries（宏观抽象）
            prompt = f"""# Outline Generation Task (From Plan Summaries)

## Original User Question
{graph.root_goal}

## Retrieval Strategy Summaries (total: {len(plan_summaries)})
"""
            for idx, plan_summary in enumerate(plan_summaries, 1):
                plan_id = plan_summary.get("plan_id", f"plan_{idx}")
                plansummary_text = plan_summary.get("plansummary", "")
                tool_name = plan_summary.get("tool_name", "")
                args = plan_summary.get("args", {})
                reason = plan_summary.get("reason", "")
                
                prompt += f"""
                    ### Strategy {idx} (ID: {plan_id})
                    - Tool: {tool_name}
                    - Args: {args}
                    - Reason: {reason}
                    - **Plan Summary**: {plansummary_text}
                    """
            
            if message.experiment_result and message.experiment_result.summary:
                prompt += f"""
                ## Overall Experiment Summary
                {message.experiment_result.summary.process_summary[:500]}
                """
            
            prompt += """
## Task Requirements
1. Analyze each plan summary: what problem it targets and what evidence types it retrieved.
2. Identify 3-5 major subtopics from relevance/similarity.
3. Generate 2-4 progressive sub-questions per subtopic (abstract -> concrete).
4. Assign relevant plan IDs to each subtopic.
5. Produce one-sentence core hypothesis preview.
6. Extract concise keywords for each subtopic.

## Output Format
Return strict JSON:
{
    "core_hypothesis_preview": "one-sentence preview",
    "subtopics": [
        {
            "topic_name": "subtopic name",
            "description": "subtopic description",
            "sub_questions": ["abstract sub-question", "more concrete sub-question", "most concrete sub-question"],
            "assigned_plan_ids": ["plan_id1", "plan_id2"],
            "keywords": ["keyword1", "keyword2"]
        },
        ...
    ]
}

Output JSON only. No extra text.
"""
            
            response = await self.model_client.create(
                messages=[self.system_message, UserMessage(content=prompt, source="user")],
                cancellation_token=ctx.cancellation_token
            )
            # 记录 LLM 交互
            logger.log_llm_interaction(
                source="HypothesisCoordinator",
                prompt=prompt,
                response=response.content,
                system_message=self.system_message.content if self.system_message else None
            )
            
            # 立即保存到 experiment_result（如果存在）
            if message.experiment_result:
                from protocols import HypothesisStep, HypothesisData
                import datetime
                import glob
                import os
                
                outline_step = HypothesisStep(
                    step_name="outline",
                    agent_name="HypothesisCoordinator",
                    prompt=prompt,
                    response=response.content,
                    system_message=self.system_message.content if self.system_message else None,
                    timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                
                # 初始化或更新 hypothesis 数据
                if not message.experiment_result.hypothesis:
                    message.experiment_result.hypothesis = HypothesisData(
                        outline=outline_step,
                        sections=[],
                        synthesis=None,
                        final_report=None
                    )
                else:
                    message.experiment_result.hypothesis.outline = outline_step
                
                logger.log("HypothesisCoordinator", "大纲生成内容已保存到 experiment_result.hypothesis", "SAVE")
                
                # 立即保存到 JSON 文件
                logs_dir = "logs"
                if os.path.isdir(logs_dir):
                    files = glob.glob(os.path.join(logs_dir, "experiment_results_*.json"))
                    if files:
                        latest_file = max(files, key=os.path.getmtime)
                        with open(latest_file, "w", encoding="utf-8") as f:
                            f.write(message.experiment_result.model_dump_json(indent=2, ensure_ascii=False))
                        logger.log("HypothesisCoordinator", f"已更新 JSON 文件: {latest_file}", "SAVE")
                        print(f"\n💾 [HypothesisCoordinator] 已保存大纲生成内容到: {latest_file}")
            
            # 解析JSON响应
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                outline_data = json.loads(json_match.group())
                outline_response = OutlineResponse(
                    core_hypothesis_preview=outline_data.get("core_hypothesis_preview", ""),
                    subtopics=[
                        SubTopic(**st) for st in outline_data.get("subtopics", [])
                    ]
                )
                logger.log("HypothesisCoordinator", f"大纲生成完成，共{len(outline_response.subtopics)}个子主题", "OUTLINE_COMPLETE")
                # 发布大纲响应（使用字符串作为 source，因为可能没有通过 runtime 注册）
                try:
                    source = self.id.key
                except AttributeError:
                    source = "HypothesisCoordinator"
                await self.publish_message(
                    outline_response,
                    topic_id=TopicId(TOPIC_HYPOTHESIS, source=source)
                )
            else:
                logger.log("HypothesisCoordinator", "无法解析JSON响应", "ERROR")
                
        except Exception as e:
            logger.log("HypothesisCoordinator", f"生成大纲时出错: {e}", "ERROR", detail_data=traceback.format_exc())


# --- D.2. 子主题撰写者 (Hypothesis Section) ---
@type_subscription(topic_type=TOPIC_HYPOTHESIS_SECTION)
class HypothesisSectionAgent(RoutedAgent):
    def __init__(self, model_client: OpenAIChatCompletionClient) -> None:
        super().__init__("HypothesisSection")
        self.model_client = model_client
        self.system_message = SystemMessage(content="""
        You are a **Section Writing Specialist**.
        Write a detailed section for each sub-question using the corresponding RAG evidence.

        # Tasks
        1. Analyze the sub-question and evidence deeply.
        2. Connect evidence into coherent reasoning.
        3. Write a focused paragraph (about 200-400 Chinese chars equivalent; keep concise if writing in English).
        4. Cite evidence inline using `[Evidence: node_id]`.

        # Writing Requirements
        1. Synthesize evidence instead of listing fragments.
        2. Every key claim must be evidence-backed.
        3. Keep structure and logic clear.
        4. Use natural academic writing style.
        """)
    
    @message_handler
    async def handle_section_request(self, message: SectionRequest, ctx: MessageContext) -> None:
        """处理子主题撰写请求 - 基于子问题和 RAG 结果（具体层面）"""
        logger.log("HypothesisSection", f"开始撰写子主题: {message.subtopic.topic_name}, 子问题: {message.sub_question}", "SECTION_START")
        
        try:
            prompt = f"""# Section Writing Task (From Sub-question + RAG Results)

## Original User Question
{message.root_goal}

## Subtopic Information
- Topic: {message.subtopic.topic_name}
- Description: {message.subtopic.description}
- Keywords: {message.subtopic.keywords}

## Current Sub-question
{message.sub_question}

## RAG Evidence (total: {len(message.rag_results)})
"""
            for idx, rag_result in enumerate(message.rag_results, 1):
                node_id = rag_result.get('node_id', f'node_{idx}')
                prompt += f"""
### Evidence {idx} (Node ID: {node_id})
- Title: {rag_result.get('title', '')}
- Summary: {rag_result.get('summary', '')}
- Content: {rag_result.get('content', '')[:500]}...
- Evaluation:
  - Action: {rag_result.get('branch_action', '')}
  - Scores: {rag_result.get('scores', {})}
  - Reason: {rag_result.get('reason', '')}
  - Extracted insight: {rag_result.get('extracted_insight', '')}
- Metadata:
  - Paper ID: {rag_result.get('paper_id', '')}
  - Key entities: {rag_result.get('key_entities', [])}
  - Figure type: {rag_result.get('figure_type', '')}
- Source:
  - Tool: {rag_result.get('tool', '')}
  - Args: {rag_result.get('args', {})}
"""
            
            prompt += f"""
## Requirements
1. Focus strictly on the current sub-question.
2. Synthesize multiple evidence items into coherent reasoning.
3. Use `[Evidence: node_id]` citations for every key claim.
4. Use fluent academic writing style.
5. Output paragraph content only (no extra headers or JSON).
"""
            
            response = await self.model_client.create(
                messages=[self.system_message, UserMessage(content=prompt, source="user")],
                cancellation_token=ctx.cancellation_token
            )
            # 记录 LLM 交互
            logger.log_llm_interaction(
                source=f"HypothesisSection ({message.subtopic.topic_name})",
                prompt=prompt,
                response=response.content,
                system_message=self.system_message.content if self.system_message else None
            )
            
            # 立即保存到 experiment_result（如果存在）
            if message.experiment_result:
                from protocols import HypothesisStep, HypothesisData
                import datetime
                import glob
                import os
                
                section_step = HypothesisStep(
                    step_name=f"section_{message.subtopic.topic_name}_{message.sub_question}",
                    agent_name="HypothesisSection",
                    prompt=prompt,
                    response=response.content,
                    system_message=self.system_message.content if self.system_message else None,
                    timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                
                # 初始化或更新 hypothesis 数据
                if not message.experiment_result.hypothesis:
                    message.experiment_result.hypothesis = HypothesisData(
                        outline=None,
                        sections=[section_step],
                        synthesis=None,
                        final_report=None
                    )
                else:
                    if not message.experiment_result.hypothesis.sections:
                        message.experiment_result.hypothesis.sections = []
                    message.experiment_result.hypothesis.sections.append(section_step)
                
                logger.log("HypothesisSection", f"子主题撰写内容已保存到 experiment_result.hypothesis (主题: {message.subtopic.topic_name})", "SAVE")
                
                # 立即保存到 JSON 文件
                logs_dir = "logs"
                if os.path.isdir(logs_dir):
                    files = glob.glob(os.path.join(logs_dir, "experiment_results_*.json"))
                    if files:
                        latest_file = max(files, key=os.path.getmtime)
                        with open(latest_file, "w", encoding="utf-8") as f:
                            f.write(message.experiment_result.model_dump_json(indent=2, ensure_ascii=False))
                        logger.log("HypothesisSection", f"已更新 JSON 文件: {latest_file}", "SAVE")
                        print(f"\n💾 [HypothesisSection] 已保存子主题内容到: {latest_file} (主题: {message.subtopic.topic_name})")
            
            # 提取引用的节点ID
            import re
            cited_nodes = re.findall(r'\[Evidence:\s*([^\]]+)\]', response.content)
            cited_nodes = [nid.strip() for node_group in cited_nodes for nid in node_group.split(',')]
            
            section_response = SectionResponse(
                subtopic_name=message.subtopic.topic_name,
                content=response.content,
                cited_nodes=list(set(cited_nodes))  # 去重
            )
            
            logger.log("HypothesisSection", f"子主题撰写完成: {message.subtopic.topic_name}", "SECTION_COMPLETE")
            # 发布子主题响应（使用字符串作为 source，因为可能没有通过 runtime 注册）
            try:
                source = self.id.key
            except AttributeError:
                source = "HypothesisSection"
            await self.publish_message(
                section_response,
                topic_id=TopicId(TOPIC_HYPOTHESIS, source=source)
            )
            
        except Exception as e:
            logger.log("HypothesisSection", f"撰写子主题时出错: {e}", "ERROR", detail_data=traceback.format_exc())


# --- D.3. 报告整合者 (Hypothesis Synthesizer) ---
@type_subscription(topic_type=TOPIC_HYPOTHESIS_SYNTHESIZER)
class HypothesisSynthesizerAgent(RoutedAgent):
    def __init__(self, model_client: OpenAIChatCompletionClient) -> None:
        super().__init__("HypothesisSynthesizer")
        self.model_client = model_client
        self.system_message = SystemMessage(content="""
        You are a **Report Synthesis Specialist**.
        Integrate all section drafts into a final structured scientific report.

        # Tasks
        1. Merge section content into a coherent whole.
        2. Produce core hypothesis and final conclusions.
        3. Optionally include a brief research-process narrative.

        # Required Structure
        ## 1. Core Hypothesis
        ## 2. Evidence Analysis
        ### 2.1 [Subtopic 1]
        ### 2.2 [Subtopic 2]
        ## 3. Research Process (optional)
        ## 4. Critical Gaps and Future Directions
        ## 5. Conclusion

        # Writing Requirements
        1. Keep citation format `[Evidence: node_id]`.
        2. Ensure strong logical flow and natural transitions.
        3. Target medium length (about 500-1000 English words).
        4. Use fluent academic style.
        """)
    
    @message_handler
    async def handle_synthesis_request(self, message: SynthesisRequest, ctx: MessageContext) -> None:
        """处理报告整合请求"""
        logger.log("HypothesisSynthesizer", "开始整合报告...", "SYNTHESIS_START")
        
        try:
            prompt = f"""# Report Synthesis Task

## Original User Question
{message.root_goal}

## Core Hypothesis Preview
{message.outline.core_hypothesis_preview}

## Section Drafts
"""
            for idx, section in enumerate(message.section_contents, 1):
                prompt += f"""
### Subtopic {idx}: {section.subtopic_name}
{section.content}

Cited nodes: {section.cited_nodes}
"""
            
            prompt += f"""
## Graph Structure Overview
{message.graph_structure_summary}
"""
            
            if message.experiment_summary:
                prompt += f"""
## Experiment Summary
{message.experiment_summary[:500]}
"""
            
            prompt += """
## Requirements
1. Integrate all section drafts into one final structured report.
2. Follow the required report structure strictly.
3. Keep citation format `[Evidence: node_id]`.
4. Ensure coherent logic and smooth transitions.
5. Keep the report length around 500-1000 English words.

Output the full report directly.
"""
            
            response = await self.model_client.create(
                messages=[self.system_message, UserMessage(content=prompt, source="user")],
                cancellation_token=ctx.cancellation_token
            )
            # 记录 LLM 交互
            logger.log_llm_interaction(
                source="HypothesisSynthesizer",
                prompt=prompt,
                response=response.content,
                system_message=self.system_message.content if self.system_message else None
            )
            
            # 立即保存到 experiment_result（如果存在）
            if message.experiment_result:
                from protocols import HypothesisStep, HypothesisData
                import datetime
                import glob
                import os
                
                synthesis_step = HypothesisStep(
                    step_name="synthesis",
                    agent_name="HypothesisSynthesizer",
                    prompt=prompt,
                    response=response.content,
                    system_message=self.system_message.content if self.system_message else None,
                    timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                
                # 初始化或更新 hypothesis 数据
                if not message.experiment_result.hypothesis:
                    message.experiment_result.hypothesis = HypothesisData(
                        outline=None,
                        sections=[],
                        synthesis=synthesis_step,
                        final_report=response.content
                    )
                else:
                    message.experiment_result.hypothesis.synthesis = synthesis_step
                    message.experiment_result.hypothesis.final_report = response.content
                
                logger.log("HypothesisSynthesizer", "报告整合内容已保存到 experiment_result.hypothesis", "SAVE")
                
                # 立即保存到 JSON 文件
                logs_dir = "logs"
                if os.path.isdir(logs_dir):
                    files = glob.glob(os.path.join(logs_dir, "experiment_results_*.json"))
                    if files:
                        latest_file = max(files, key=os.path.getmtime)
                        with open(latest_file, "w", encoding="utf-8") as f:
                            f.write(message.experiment_result.model_dump_json(indent=2, ensure_ascii=False))
                        logger.log("HypothesisSynthesizer", f"已更新 JSON 文件: {latest_file}", "SAVE")
                        print(f"\n💾 [HypothesisSynthesizer] 已保存报告整合内容到: {latest_file}")
            
            logger.log("HypothesisSynthesizer", "报告整合完成", "SYNTHESIS_COMPLETE")
            # 发布最终报告（使用字符串作为 source，因为可能没有通过 runtime 注册）
            try:
                source = self.id.key
            except AttributeError:
                source = "HypothesisSynthesizer"
            await self.publish_message(
                response.content,
                topic_id=TopicId(TOPIC_HYPOTHESIS, source=source)
            )
            
        except Exception as e:
            logger.log("HypothesisSynthesizer", f"整合报告时出错: {e}", "ERROR", detail_data=traceback.format_exc())


# --- D. 总结者 (Hypothesis) ---
@type_subscription(topic_type=TOPIC_HYPOTHESIS)
class HypothesisGeneratorAgent(RoutedAgent):
    def __init__(self, model_client: OpenAIChatCompletionClient, websocket_manager) -> None:
        super().__init__("Hypothesis")
        self.model_client = model_client
        self.ws_manager = websocket_manager
        self.report_content = ""
        self.system_message = SystemMessage(content="""
        You are a strict peer reviewer and scientific writer.
        Evaluate each evidence item and decide whether it should be expanded (GROW) or pruned (PRUNE).
        If an image is available, include visual judgment.

        Output format (JSON List):
        [{"target_evidence_id": "...", "branch_action": "GROW", "extracted_insight": "...", "scores": {...}, "reasoning": "..."}]

        You also act as a synthesis writer after retrieval ends.
        Integrate active evidence nodes into a high-quality scientific report.

        Writing principles:
        1. Synthesize, do not list evidence mechanically.
        2. Every key claim must cite evidence IDs (e.g., `Evidence: fig_10`).
        3. Explicitly state limitations when evidence is missing.

        Report structure:
        1. Core Hypothesis
        2. Evidence Analysis
        3. Critical Gaps and Future Directions
        4. Conclusion
        """)
    async def push_summary(self):
        """主动调用 WebSocket 推送当前 Summary"""
        if self.ws_manager:
            # 注意：确保你的 connection.py / main.py 里的 manager 有 broadcast_summary 方法
            await self.ws_manager.broadcast_summary(self.report_content)

    def __init__(self, model_client: OpenAIChatCompletionClient, websocket_manager) -> None:
        super().__init__("Hypothesis")
        self.model_client = model_client
        self.ws_manager = websocket_manager
        self.report_content = ""
        self.outline_response: Optional[OutlineResponse] = None
        self.section_responses: List[SectionResponse] = []
        # 存储 Hypothesis 生成过程的 prompt 和 response
        self.hypothesis_steps = {
            "outline": None,
            "sections": [],
            "synthesis": None
        }
        self.system_message = SystemMessage(content="""
        You are the **Report Coordinator**.
        Your job is to orchestrate three stages: outline generation, section writing, and final synthesis.
        """)
    
    @message_handler
    async def handle_task_complete(self, message: TaskComplete, ctx: MessageContext) -> None:
        """处理任务完成，协调整个报告生成流程（从抽象到具体）"""
        logger.log("Hypothesis", "开始协调报告生成流程（从抽象到具体）...", "FINAL")
        
        try:
            graph = message.graph_snapshot
            experiment_result = message.experiment_result
            
            # 提取 plan_summaries（抽象层面）
            plan_summaries = []
            if experiment_result and experiment_result.iterations:
                for iteration in experiment_result.iterations:
                    for query_result in iteration.query_results:
                        if query_result.orchestrator_plan and query_result.orchestrator_plan.plansummary:
                            plan_id = f"plan_{iteration.round_number}_{len(plan_summaries)}"
                            plan_summaries.append({
                                "plan_id": plan_id,
                                "plansummary": query_result.orchestrator_plan.plansummary,
                                "tool_name": query_result.orchestrator_plan.tool_name or "",
                                "args": query_result.orchestrator_plan.args,
                                "reason": query_result.orchestrator_plan.reason,
                                "query_result": query_result  # 保存引用以便后续查找 RAG 结果
                            })
            
            if not plan_summaries:
                logger.log("Hypothesis", "没有 plan summaries，无法生成报告", "WARNING")
                self.report_content = "No plan summaries found. Unable to generate report."
                await self.push_summary()
                return
            
            # 阶段1: 生成大纲（基于 plan summaries，抽象层面）
            logger.log("Hypothesis", "阶段1: 基于 plan summaries 生成大纲...", "PHASE1")
            coordinator = HypothesisCoordinatorAgent(self.model_client)
            outline_request = OutlineRequest(
                graph_snapshot=graph,
                experiment_result=experiment_result,
                plan_summaries=plan_summaries
            )
            await coordinator.handle_outline_request(outline_request, ctx)
            
            # 等待并获取大纲响应（简化处理：直接调用方法）
            await asyncio.sleep(0.5)
            
            # 重新调用以获取结果（实际应该通过消息订阅）
            # 为了简化，我们直接在这里调用生成大纲的逻辑
            coordinator_prompt = self._build_coordinator_prompt_from_plans(graph.root_goal, plan_summaries, experiment_result)
            coordinator_response = await self.model_client.create(
                messages=[coordinator.system_message, UserMessage(content=coordinator_prompt, source="user")],
                cancellation_token=ctx.cancellation_token
            )
            logger.log_llm_interaction(
                source="HypothesisCoordinator (via HypothesisGenerator)",
                prompt=coordinator_prompt,
                response=coordinator_response.content,
                system_message=coordinator.system_message.content if coordinator.system_message else None
            )
            
            # 保存 outline 步骤的 prompt 和 response
            from protocols import HypothesisStep, HypothesisData
            import datetime
            self.hypothesis_steps["outline"] = HypothesisStep(
                step_name="outline",
                agent_name="HypothesisCoordinator",
                prompt=coordinator_prompt,
                response=coordinator_response.content,
                system_message=coordinator.system_message.content if coordinator.system_message else None,
                timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # 解析大纲
            import re
            json_match = re.search(r'\{.*\}', coordinator_response.content, re.DOTALL)
            if json_match:
                outline_data = json.loads(json_match.group())
                self.outline_response = OutlineResponse(
                    core_hypothesis_preview=outline_data.get("core_hypothesis_preview", ""),
                    subtopics=[SubTopic(**st) for st in outline_data.get("subtopics", [])]
                )
            else:
                logger.log("Hypothesis", "无法解析大纲 JSON，使用默认大纲", "WARNING")
                self.outline_response = OutlineResponse(
                    core_hypothesis_preview=graph.root_goal,
                    subtopics=[SubTopic(
                        topic_name=f"主题{i+1}",
                        description="",
                        sub_questions=[f"子问题{i+1}"],
                        assigned_plan_ids=[],
                        keywords=[]
                    ) for i in range(min(3, len(plan_summaries)))]
                )
            
            logger.log("Hypothesis", f"大纲生成完成，共{len(self.outline_response.subtopics)}个子主题", "PHASE1_DONE")
            
            # 阶段2: 为每个子问题的每个子问题生成内容（基于 RAG 结果，具体层面）
            logger.log("Hypothesis", "阶段2: 基于子问题和 RAG 结果生成内容...", "PHASE2")
            section_agent = HypothesisSectionAgent(self.model_client)
            self.section_responses = []
            
            # 构建 plan_id 到 RAG 结果的映射
            plan_id_to_rag_results = {}
            for plan_summary in plan_summaries:
                plan_id = plan_summary["plan_id"]
                query_result = plan_summary.get("query_result")
                if query_result and query_result.rag_results:
                    # 将 RAG 结果转换为字典格式
                    rag_results = []
                    for rag_item in query_result.rag_results:
                        # rag_item 可能是 RagResult 对象或字典
                        if hasattr(rag_item, 'retrieval_result'):
                            # 是 RagResult 对象
                            retrieval = rag_item.retrieval_result
                            evaluation = rag_item.evaluation
                            node_id = retrieval.id if hasattr(retrieval, 'id') else (retrieval.get("id", "") if isinstance(retrieval, dict) else "")
                        elif isinstance(rag_item, dict):
                            # 是字典格式（从 JSON 加载的）
                            retrieval = rag_item.get("retrieval_result", {})
                            evaluation = rag_item.get("evaluation", {})
                            # 从 retrieval_result 中提取 id
                            node_id = retrieval.get("id", "") if isinstance(retrieval, dict) else ""
                        else:
                            continue
                        
                        if not node_id:
                            continue  # 跳过没有 node_id 的项目
                        
                        # 找到对应的节点
                        node = graph.nodes.get(node_id) if node_id else None
                        
                        # 提取内容
                        if isinstance(retrieval, dict):
                            content = retrieval.get("content", {})
                            if isinstance(content, dict):
                                title = content.get("title", "")
                                summary = content.get("summary", "")
                                text_content = content.get("text", "")
                            else:
                                title = ""
                                summary = ""
                                text_content = str(content)
                        else:
                            content = retrieval.content if hasattr(retrieval, 'content') else {}
                            title = content.get("title", "") if isinstance(content, dict) else ""
                            summary = content.get("summary", "") if isinstance(content, dict) else ""
                            text_content = content.get("text", "") if isinstance(content, dict) else str(content)
                        
                        # 提取评估信息
                        if evaluation:
                            if isinstance(evaluation, dict):
                                branch_action = evaluation.get("branch_action", "")
                                scores = evaluation.get("scores", {})
                                reason = evaluation.get("reason", "")
                                extracted_insight = evaluation.get("extracted_insight", "")
                            else:
                                branch_action = evaluation.branch_action if hasattr(evaluation, 'branch_action') else ""
                                scores = evaluation.scores if hasattr(evaluation, 'scores') else {}
                                reason = evaluation.reason if hasattr(evaluation, 'reason') else ""
                                extracted_insight = evaluation.extracted_insight if hasattr(evaluation, 'extracted_insight') else ""
                        else:
                            branch_action = node.evaluation.branch_action if node and node.evaluation else ""
                            scores = node.evaluation.scores if node and node.evaluation else {}
                            reason = node.evaluation.reason if node and node.evaluation else ""
                            extracted_insight = node.evaluation.extracted_insight if node and node.evaluation else ""
                        
                        # 提取元数据
                        if isinstance(retrieval, dict):
                            metadata = retrieval.get("metadata", {})
                            paper_id = metadata.get("paperid") or metadata.get("paper_id", "")
                            key_entities = metadata.get("key_entities", [])
                            figure_type = metadata.get("type", "")
                        else:
                            metadata = retrieval.metadata if hasattr(retrieval, 'metadata') else {}
                            paper_id = metadata.get("paperid") or metadata.get("paper_id", "") if isinstance(metadata, dict) else ""
                            key_entities = metadata.get("key_entities", []) if isinstance(metadata, dict) else []
                            figure_type = metadata.get("type", "") if isinstance(metadata, dict) else ""
                        
                        rag_results.append({
                            "node_id": node_id,
                            "title": title or text_content[:100] if text_content else "",
                            "summary": summary or text_content[:500] if text_content else "",
                            "content": text_content,
                            "branch_action": branch_action,
                            "scores": scores,
                            "reason": reason,
                            "extracted_insight": extracted_insight,
                            "paper_id": paper_id,
                            "key_entities": key_entities,
                            "figure_type": figure_type,
                            "tool": query_result.orchestrator_plan.tool_name if query_result.orchestrator_plan else "",
                            "args": query_result.orchestrator_plan.args if query_result.orchestrator_plan else {}
                        })
                    plan_id_to_rag_results[plan_id] = rag_results
            
            # 为每个子主题的每个子问题生成内容
            for subtopic in self.outline_response.subtopics:
                for sub_question in subtopic.sub_questions:
                    # 找到该子问题对应的 RAG 结果（基于 assigned_plan_ids）
                    rag_results_for_question = []
                    for plan_id in subtopic.assigned_plan_ids:
                        if plan_id in plan_id_to_rag_results:
                            rag_results_for_question.extend(plan_id_to_rag_results[plan_id])
                    
                    if not rag_results_for_question:
                        logger.log("Hypothesis", f"子问题 '{sub_question}' 没有对应的 RAG 结果，跳过", "WARNING")
                        continue
                    
                    # 生成子问题内容
                    section_request = SectionRequest(
                        subtopic=subtopic,
                        sub_question=sub_question,
                        rag_results=rag_results_for_question,
                        root_goal=graph.root_goal,
                        experiment_result=experiment_result  # 传递 experiment_result 以便保存
                    )
                    
                    section_prompt = self._build_section_prompt_from_rag(section_request)
                    section_response_content = await self.model_client.create(
                        messages=[section_agent.system_message, UserMessage(content=section_prompt, source="user")],
                        cancellation_token=ctx.cancellation_token
                    )
                    logger.log_llm_interaction(
                        source=f"HypothesisSection ({subtopic.topic_name} - {sub_question})",
                        prompt=section_prompt,
                        response=section_response_content.content,
                        system_message=section_agent.system_message.content if section_agent.system_message else None
                    )
                    
                    # 保存 section 步骤的 prompt 和 response
                    from protocols import HypothesisStep
                    import datetime
                    section_step = HypothesisStep(
                        step_name=f"section_{subtopic.topic_name}_{sub_question}",
                        agent_name="HypothesisSection",
                        prompt=section_prompt,
                        response=section_response_content.content,
                        system_message=section_agent.system_message.content if section_agent.system_message else None,
                        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    self.hypothesis_steps["sections"].append(section_step)
                    
                    # 提取引用的节点ID
                    cited_nodes = re.findall(r'\[Evidence:\s*([^\]]+)\]', section_response_content.content)
                    cited_nodes = [nid.strip() for node_group in cited_nodes for nid in node_group.split(',')]
                    
                    section_response = SectionResponse(
                        subtopic_name=f"{subtopic.topic_name}: {sub_question}",
                        content=section_response_content.content,
                        cited_nodes=list(set(cited_nodes))
                    )
                    self.section_responses.append(section_response)
            
            logger.log("Hypothesis", f"所有子问题内容生成完成，共{len(self.section_responses)}个段落", "PHASE2_DONE")
            
            # 阶段3: 整合最终报告
            logger.log("Hypothesis", "阶段3: 整合最终报告...", "PHASE3")
            synthesizer_agent = HypothesisSynthesizerAgent(self.model_client)
            
            graph_structure_summary = self._build_graph_structure_summary(graph)
            
            synthesis_request = SynthesisRequest(
                root_goal=graph.root_goal,
                outline=self.outline_response,
                section_contents=self.section_responses,
                graph_structure_summary=graph_structure_summary,
                experiment_summary=experiment_result.summary.process_summary if experiment_result and experiment_result.summary else None,
                experiment_result=experiment_result  # 传递 experiment_result 以便保存
            )
            
            synthesis_prompt = self._build_synthesis_prompt(synthesis_request)
            final_response = await self.model_client.create(
                messages=[synthesizer_agent.system_message, UserMessage(content=synthesis_prompt, source="user")],
                cancellation_token=ctx.cancellation_token
            )
            logger.log_llm_interaction(
                source="HypothesisSynthesizer (via HypothesisGenerator)",
                prompt=synthesis_prompt,
                response=final_response.content,
                system_message=synthesizer_agent.system_message.content if synthesizer_agent.system_message else None
            )
            
            # 保存 synthesis 步骤的 prompt 和 response
            from protocols import HypothesisStep, HypothesisData
            import datetime
            self.hypothesis_steps["synthesis"] = HypothesisStep(
                step_name="synthesis",
                agent_name="HypothesisSynthesizer",
                prompt=synthesis_prompt,
                response=final_response.content,
                system_message=synthesizer_agent.system_message.content if synthesizer_agent.system_message else None,
                timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            self.report_content = final_response.content
            
            # 保存 Hypothesis 数据到 experiment_result
            if experiment_result:
                hypothesis_data = HypothesisData(
                    outline=self.hypothesis_steps["outline"],
                    sections=self.hypothesis_steps["sections"],
                    synthesis=self.hypothesis_steps["synthesis"],
                    final_report=self.report_content
                )
                experiment_result.hypothesis = hypothesis_data
                logger.log("Hypothesis", "Hypothesis 数据已保存到 experiment_result", "SAVE")
                # 再次保存到 JSON 文件（Orchestrator 保存时 hypothesis 尚未生成，此处补充保存）
                import glob
                import os
                save_file = getattr(message, "experiment_save_path", None)
                if not save_file or not os.path.isfile(save_file):
                    logs_dir = "logs"
                    if os.path.isdir(logs_dir):
                        files = glob.glob(os.path.join(logs_dir, "experiment_results_*.json"))
                        if files:
                            save_file = max(files, key=os.path.getmtime)
                if save_file:
                    try:
                        with open(save_file, "w", encoding="utf-8") as f:
                            f.write(experiment_result.model_dump_json(indent=2, ensure_ascii=False))
                        logger.log("Hypothesis", f"已更新 JSON 文件: {save_file}", "SAVE")
                        print(f"\n💾 [Hypothesis] 已更新 experiment_result（含 hypothesis）到: {save_file}")
                    except Exception as save_err:
                        logger.log("Hypothesis", f"保存失败: {save_err}", "ERROR")
            
            await self.push_summary()
            logger.log("Hypothesis", "报告生成完成", "DONE")
            logger.log("Hypothesis [Final Report]:", self.report_content, "REPORT")
            
        except Exception as e:
            logger.log("Hypothesis", f"生成报告时出错: {e}", "ERROR", detail_data=traceback.format_exc())
            self.report_content = f"报告生成过程中出现错误: {str(e)}"
            await self.push_summary()
    
    def _build_coordinator_prompt_from_plans(self, root_goal: str, plan_summaries: List[Dict], experiment_result: Optional[ExperimentResult]) -> str:
        """基于 plan summaries 构建 Coordinator 的 prompt"""
        prompt = f"""# Outline Generation Task (From Plan Summaries)

## Original User Question
{root_goal}

## Retrieval Strategy Summaries (total: {len(plan_summaries)})
"""
        for idx, plan_summary in enumerate(plan_summaries, 1):
            plan_id = plan_summary.get("plan_id", f"plan_{idx}")
            plansummary_text = plan_summary.get("plansummary", "")
            tool_name = plan_summary.get("tool_name", "")
            args = plan_summary.get("args", {})
            reason = plan_summary.get("reason", "")
            
            prompt += f"""
### Strategy {idx} (ID: {plan_id})
- Tool: {tool_name}
- Args: {args}
- Reason: {reason}
- **Plan Summary**: {plansummary_text}
"""
        
        if experiment_result and experiment_result.summary:
            prompt += f"""
## Overall Experiment Summary
{experiment_result.summary.process_summary[:500]}
"""
        
        prompt += """
## Task Requirements
1. Analyze each plan summary and identify intended problem/evidence type.
2. Identify 3-5 major subtopics by relevance and similarity.
3. Generate 2-4 progressive sub-questions for each subtopic.
4. Assign related plan IDs to each subtopic.
5. Produce one-sentence core hypothesis preview.
6. Extract concise keywords for each subtopic.

## Output Format
Return strict JSON:
{
    "core_hypothesis_preview": "one-sentence preview",
    "subtopics": [
        {
            "topic_name": "subtopic name",
            "description": "subtopic description",
            "sub_questions": ["abstract question", "more concrete question", "most concrete question"],
            "assigned_plan_ids": ["plan_id1", "plan_id2"],
            "keywords": ["keyword1", "keyword2"]
        },
        ...
    ]
}

Output JSON only. No extra text.
"""
        return prompt
    
    def _build_section_prompt_from_rag(self, section_request: SectionRequest) -> str:
        """基于子问题和 RAG 结果构建 Section 的 prompt"""
        prompt = f"""# Section Writing Task (From Sub-question + RAG Results)

## Original User Question
{section_request.root_goal}

## Subtopic Information
- Topic: {section_request.subtopic.topic_name}
- Description: {section_request.subtopic.description}
- Keywords: {section_request.subtopic.keywords}

## Current Sub-question
{section_request.sub_question}

## RAG Evidence (total: {len(section_request.rag_results)})
"""
        for idx, rag_result in enumerate(section_request.rag_results, 1):
            node_id = rag_result.get('node_id', f'node_{idx}')
            prompt += f"""
### Evidence {idx} (Node ID: {node_id})
- Title: {rag_result.get('title', '')}
- Summary: {rag_result.get('summary', '')}
- Content: {rag_result.get('content', '')[:500]}...
- Evaluation:
  - Action: {rag_result.get('branch_action', '')}
  - Scores: {rag_result.get('scores', {})}
  - Reason: {rag_result.get('reason', '')}
  - Insight: {rag_result.get('extracted_insight', '')}
- Metadata:
  - Paper ID: {rag_result.get('paper_id', '')}
  - Key entities: {rag_result.get('key_entities', [])}
  - Figure type: {rag_result.get('figure_type', '')}
- Source:
  - Tool: {rag_result.get('tool', '')}
  - Args: {rag_result.get('args', {})}
"""
        
        prompt += f"""
## Requirements
1. Focus on the current sub-question and write a detailed paragraph.
2. Synthesize evidence into coherent reasoning.
3. Use `[Evidence: node_id]` for key claims.
4. Use fluent academic writing style.
5. Output paragraph content only.
"""
        return prompt
    
    def _build_coordinator_prompt(self, root_goal: str, nodes_summary: List[Dict]) -> str:
        """构建 Coordinator 的 prompt"""
        prompt = f"""# Outline Generation Task

## Original User Question
{root_goal}

## Active Node Information (total: {len(nodes_summary)})
"""
        for idx, node_info in enumerate(nodes_summary, 1):
            prompt += f"""
Node {idx}:
- ID: {node_info['id']}
- Title: {node_info['title']}
- Insight preview: {node_info['insight_preview']}
- Key entities: {node_info['key_entities']}
- Eval action: {node_info['branch_action']}
"""
        prompt += """
## Requirements
1. Analyze nodes and identify 3-5 major subtopics.
2. Assign relevant node IDs to each subtopic (prioritize GROW nodes).
3. Generate one-sentence core hypothesis preview.
4. Extract keywords for each subtopic.

Output strict JSON only.
"""
        return prompt
    
    def _build_section_prompt(self, request: SectionRequest) -> str:
        """构建 Section Agent 的 prompt"""
        prompt = f"""# Section Writing Task

## Original User Question
{request.root_goal}

## Subtopic Information
- Topic: {request.subtopic.topic_name}
- Description: {request.subtopic.description}
- Keywords: {request.subtopic.keywords}

## Assigned Node Details
"""
        for idx, node_data in enumerate(request.detailed_nodes, 1):
            prompt += f"""
### Node {idx} (ID: {node_data.get('id', 'unknown')})
- Title: {node_data.get('title', '')}
- Summary: {node_data.get('summary', '')}
- Insight: {node_data.get('insight', '')}
- Evaluation:
  - Action: {node_data.get('evaluation', {}).get('branch_action', '')}
  - Scores: {node_data.get('evaluation', {}).get('scores', {})}
  - Extracted insight: {node_data.get('evaluation', {}).get('extracted_insight', '')}
- Metadata:
  - Paper ID: {node_data.get('metadata', {}).get('paper_id', '')}
  - Key entities: {node_data.get('metadata', {}).get('key_entities', [])}
"""
        prompt += """
## Requirements
1. Write a detailed paragraph based on the node information above.
2. Use citation format `[Evidence: node_id]` where relevant.
3. Use natural, fluent academic writing style.

Output paragraph content only.
"""
        return prompt
    
    def _build_synthesis_prompt(self, request: SynthesisRequest) -> str:
        """构建 Synthesizer Agent 的 prompt"""
        prompt = f"""# Report Synthesis Task

## Original User Question
{request.root_goal}

## Core Hypothesis Preview
{request.outline.core_hypothesis_preview}

## Section Drafts
"""
        for idx, section in enumerate(request.section_contents, 1):
            prompt += f"""
### Subtopic {idx}: {section.subtopic_name}
{section.content}

Cited nodes: {section.cited_nodes}
"""
        prompt += f"""
## Graph Structure Overview
{request.graph_structure_summary}
"""
        prompt += """
## Requirements
1. Integrate all section drafts into one structured final report.
2. Follow the required structure strictly.
3. Keep citation format `[Evidence: node_id]`.
4. Target around 500-1000 English words.

Output the full report directly.
"""
        return prompt
    
    def _build_graph_structure_summary(self, graph: ResearchGraph) -> str:
        """构建图谱结构概览"""
        active_nodes = [
            (nid, node) for nid, node in graph.nodes.items()
            if node.status == "ACTIVE" and node.type == "EVIDENCE"
        ]
        summary = f"共{len(active_nodes)}个活跃证据节点。"
        if graph.action_history:
            summary += f" 检索轮次: {len(set(a.round_index for a in graph.action_history))}轮。"
        return summary

        


# --- Main ---
async def main():
    """
    仅用于脚本入口的占位函数（静态检查用）。
    实际运行请通过 `server.py` 触发 `run_rag_workflow(...)`。
    """
    print("engine.py: 请通过 server.py 使用 run_rag_workflow 来启动流程。")

async def run_rag_workflow(
    query: str,
    manager: ConnectionManager,
    collection_name: str = "multimodal2text",
    plans_per_round: int = 3,
    rag_result_per_plan: int = 10,
    max_rounds: int = 7,
    interactive_mode: bool = False,
    run_id: str = None,
    pause_gate = None
):
    set_active_collection_name(collection_name)
    # #region agent log
    try:
        import json as json_lib
        with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
            f.write(json_lib.dumps({"id":"log_workflow_entry","timestamp":datetime.datetime.now().timestamp()*1000,"location":"engine.py:1486","message":"run_rag_workflow开始","data":{"query":query,"manager_connections":len(manager.active_connections)},"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+"\n")
    except: pass
    # #endregion
    print("--- [System] 初始化数据层 ---")
    # #region agent log
    try:
        import json as json_lib
        with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
            f.write(json_lib.dumps({"id":"log_workflow_before_rag","timestamp":datetime.datetime.now().timestamp()*1000,"location":"engine.py:1488","message":"准备初始化RAG服务","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+"\n")
    except: pass
    # #endregion
    rag = await get_rag_service(
        collection_name=collection_name,
        multimodal_collection_name="scientific_rag_multimodal_collection_new",
    )
    # #region agent log
    try:
        import json as json_lib
        with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
            f.write(json_lib.dumps({"id":"log_workflow_rag_ready","timestamp":datetime.datetime.now().timestamp()*1000,"location":"engine.py:1492","message":"RAG服务初始化完成","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+"\n")
    except: pass
    # #endregion
    
    try:
        # model_client = OpenAIChatCompletionClient(
        #     model="gpt-4o",
        #     base_url="http://38.147.105.35:3030/v1",
        #     api_key="sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
        # )
        model_client = OpenAIChatCompletionClient(
            model="deepseek-r1:671b-0528",
            base_url="https://uni-api.cstcloud.cn/v1",
            api_key="f24a9af08a33a9649b3f149706c8c45e8602a884b8beab6abae0d608226477f8",
            model_info=ModelInfo(
                vision=False,                  # 根据实际情况
                structured_output=False,
                function_calling=True,         # 大多数支持工具调用的模型设 True
                streaming=True,
                json_output=False,
                family="deepseek",
                context_length=65536,          # 64k
                # max_output_tokens=8192       # 可选
            )
        )

        runtime = SingleThreadedAgentRuntime()
        
        await OrchestratorAgent.register(runtime, type=TOPIC_ORCHESTRATOR, factory=lambda: OrchestratorAgent(model_client, manager, pause_gate=pause_gate, interactive_mode=interactive_mode, run_id=run_id))
        await ToolExecutorAgent.register(runtime, type=TOPIC_TOOL, factory=lambda: ToolExecutorAgent())
        await EvaluatorAgent.register(runtime, type=TOPIC_EVALUATOR, factory=lambda: EvaluatorAgent(model_client))
        await HypothesisGeneratorAgent.register(runtime, type=TOPIC_HYPOTHESIS, factory=lambda: HypothesisGeneratorAgent(model_client, manager))
        await InteractionSummaryAgent.register(runtime, type=TOPIC_SUMMARY, factory=lambda: InteractionSummaryAgent(model_client, manager))

        runtime.start()
        
        # 使用传入的查询参数，而不是硬编码的内容
        await runtime.publish_message(
            UserRequest(
                query=query,
                plans_per_round=plans_per_round,
                rag_result_per_plan=rag_result_per_plan,
                max_rounds=max_rounds,
                interactive=interactive_mode
            ),
            topic_id=TopicId(TOPIC_ORCHESTRATOR, source="User")
        )
        
        await runtime.stop_when_idle()

    except KeyboardInterrupt:
        print("User Interrupted.")
    finally:
        await rag.close()

async def run_rag_workflow_expand(
    parent_node_id: str,
    search_type: str,
    search_query: str,
    manager: ConnectionManager,
    collection_name: str = "multimodal2text",
):
    set_active_collection_name(collection_name)
    """处理卡片扩展检索请求的工作流"""
    print(f"--- [System] 初始化扩展检索数据层 ---")
    # rag = await get_rag_service(
    #     collection_name="scientific_rag_collection_new",
    #     multimodal_collection_name="scientific_rag_multimodal_collection_new",
    # )
    
    try:
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
            ),
        )

        runtime = SingleThreadedAgentRuntime()
        await OrchestratorAgent.register(
            runtime, type=TOPIC_ORCHESTRATOR, factory=lambda: OrchestratorAgent(model_client, manager)
        )
        await ToolExecutorAgent.register(runtime, type=TOPIC_TOOL, factory=lambda: ToolExecutorAgent())
        await EvaluatorAgent.register(runtime, type=TOPIC_EVALUATOR, factory=lambda: EvaluatorAgent(model_client))
        await HypothesisGeneratorAgent.register(
            runtime, type=TOPIC_HYPOTHESIS, factory=lambda: HypothesisGeneratorAgent(model_client, manager)
        )
        await InteractionSummaryAgent.register(
            runtime, type=TOPIC_SUMMARY, factory=lambda: InteractionSummaryAgent(model_client, manager)
        )

        runtime.start()
        await runtime.publish_message(
            ExpandSearchRequest(
                parent_node_id=parent_node_id,
                search_type=search_type,
                search_query=search_query,
            ),
            topic_id=TopicId(TOPIC_ORCHESTRATOR, source="User"),
        )
        await runtime.stop_when_idle()
    except KeyboardInterrupt:
        print("User Interrupted.")


async def run_rag_workflow_follow_up(
    query: str,
    manager: ConnectionManager,
    collection_name: str = "multimodal2text",
    parent_node_id: str = "0",
    round_number: int = 0,
    rag_result_per_plan: int = 10,
):
    set_active_collection_name(collection_name)
    """
    追问工作流：只做一次检索 + 评估（不走多轮规划）。
    round_number 用于前端把小矩形放到“最后一轮 iteration”。
    """
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
        )
    )

    runtime = SingleThreadedAgentRuntime()
    await OrchestratorAgent.register(runtime, type=TOPIC_ORCHESTRATOR, factory=lambda: OrchestratorAgent(model_client, manager, is_follow_up_mode=True))
    await ToolExecutorAgent.register(runtime, type=TOPIC_TOOL, factory=lambda: ToolExecutorAgent())
    await EvaluatorAgent.register(runtime, type=TOPIC_EVALUATOR, factory=lambda: EvaluatorAgent(model_client))
    await HypothesisGeneratorAgent.register(runtime, type=TOPIC_HYPOTHESIS, factory=lambda: HypothesisGeneratorAgent(model_client, manager))
    await InteractionSummaryAgent.register(runtime, type=TOPIC_SUMMARY, factory=lambda: InteractionSummaryAgent(model_client, manager))

    runtime.start()
    await runtime.publish_message(
        FollowUpRequest(
            query=query,
            parent_node_id=parent_node_id,
            round_number=round_number,
            rag_result_per_plan=rag_result_per_plan,
        ),
        topic_id=TopicId(TOPIC_ORCHESTRATOR, source="User"),
    )
    await runtime.stop_when_idle()

if __name__ == "__main__":
    asyncio.run(main())