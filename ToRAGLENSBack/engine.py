"""
【功能】多智能体编排核心：Orchestrator / 检索与评估 / 总结与 Hypothesis 生成、交互式暂停、实验结果落盘；与 scientific_tools、protocols、connection 协同。
【长期价值】核心长期维护（体量最大，业务逻辑主战场）。
"""
import asyncio
import copy
import glob
import json
import re
import traceback
import os
import datetime
from typing import List, Dict, Any, Optional, Tuple

# -----------------------------------------------------------------
# 1. 导入模块
# -----------------------------------------------------------------
try:
    from rag_service import get_rag_service, rag_service, consume_semantic_pipeline_trace
    from scientific_tools import ALL_TOOLS_MAP, set_active_collection_name, set_rag_allowed_chunk_ids
    from protocols import (
        UserRequest, OrchestratorPlan, OrchestratorPlanBatch, SingleToolOutput, ToolOutputBatchMessage,
        EvaluationRequest, EvaluationReportMessage, TaskComplete, ExpandSearchRequest, FollowUpRequest,
        HypothesisStep, HypothesisData,
        RawEvidenceItem, ItemEvaluation, ResearchGraph, GraphNode, ActionTrace, NodeSearchRecord,
        SummaryRequest, SummaryResponse, WordCloudData, RetrievalQualityEvaluation,
        ExperimentResult, ExperimentRoundParameters,
        OutlineRequest, OutlineResponse, SubTopic, SectionRequest, SectionResponse, SynthesisRequest,
    )
except ImportError as e:
    print(f"Error importing project modules: {e}")
    exit()


def apply_rag_result_per_plan_to_plans(
    plans: List[OrchestratorPlan], rag_result_per_plan: int
) -> List[OrchestratorPlan]:
    """每条工具计划在执行前强制对齐 n_results：交互审批回传的 plans 常丢失该字段，会回落到 LLM 自带的 3 等小值。"""
    try:
        n = int(rag_result_per_plan)
    except (TypeError, ValueError):
        n = 10
    n = max(1, min(n, 20))
    out: List[OrchestratorPlan] = []
    for plan in plans:
        args = dict(plan.args) if isinstance(plan.args, dict) else {}
        tn = plan.tool_name or ""
        if tn in ("strategy_semantic_search", "strategy_exact_search"):
            args["n_results"] = n
        else:
            args.pop("n_results", None)
        out.append(plan.model_copy(update={"args": args}))
    return out


def _normalize_plan_summary_llm_output(raw: str) -> str:
    """将 Plan Summary 模型输出规范为 JSON 字符串：{\"answer\": str, \"suggestion\": str}。"""
    text = (raw or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I | re.MULTILINE)
    text = re.sub(r"\s*```\s*$", "", text)
    text = text.strip()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            ans = obj.get("answer", "")
            sug = obj.get("suggestion", "")
            if not isinstance(ans, str):
                ans = json.dumps(ans, ensure_ascii=False) if ans is not None else ""
            if not isinstance(sug, str):
                sug = json.dumps(sug, ensure_ascii=False) if sug is not None else ""
            return json.dumps({"answer": ans, "suggestion": sug}, ensure_ascii=False)
    except Exception:
        pass
    raw_stripped = (raw or "").strip()
    return json.dumps(
        {
            "answer": raw_stripped[:12000] if raw_stripped else "",
            "suggestion": "The model did not return parseable JSON; the answer field contains an excerpt of the raw output.",
        },
        ensure_ascii=False,
    )


def _plan_summary_rag_id_and_content_text(rr: Any) -> Tuple[str, str]:
    """
    plansummary 输入里每条 RAG 只保留 id + 一段正文：
    - 优先 content-text：content 中的 text / content_text / markdown / body 等；
    - 若无正文（如多模态图片块），用 content-title 与 content-summary 合并（兼容 title/summary、concise_summary 及 metadata 兜底）。
    """
    rid = str(getattr(rr, "id", "") or "").strip()
    raw_c = getattr(rr, "content", None)
    c: Dict[str, Any] = raw_c if isinstance(raw_c, dict) else {}

    def _norm(v: Any) -> str:
        if v is None:
            return ""
        if isinstance(v, list):
            return " ".join(str(x) for x in v).strip()
        return str(v).strip()

    for key in ("text", "content_text", "content-text", "markdown", "body"):
        t = _norm(c.get(key))
        if t:
            return rid, t

    title = _norm(
        c.get("title")
        or c.get("content_title")
        or c.get("content-title")
    )
    summary = _norm(
        c.get("summary")
        or c.get("content_summary")
        or c.get("content-summary")
        or c.get("concise_summary")
    )

    meta = getattr(rr, "metadata", None)
    md: Dict[str, Any] = meta if isinstance(meta, dict) else {}
    if not title:
        title = _norm(md.get("title") or md.get("paper_name"))
    if not summary:
        summary = _norm(md.get("summary") or md.get("concise_summary"))

    if title and summary:
        return rid, f"{title}\n{summary}"
    if title:
        return rid, title
    if summary:
        return rid, summary
    return rid, ""


def normalize_map_box_rect_2d(raw: Any) -> Optional[List[List[float]]]:
    """将前端传来的框选矩形规范为 [[xmin, ymin], [xmax, ymax]]，无效则返回 None。"""
    if raw is None:
        return None
    if not isinstance(raw, list) or len(raw) != 2:
        return None
    try:
        a, b = raw[0], raw[1]
        if not isinstance(a, (list, tuple)) or not isinstance(b, (list, tuple)):
            return None
        if len(a) < 2 or len(b) < 2:
            return None
        x1, y1 = float(a[0]), float(a[1])
        x2, y2 = float(b[0]), float(b[1])
        return [[min(x1, x2), min(y1, y2)], [max(x1, x2), max(y1, y2)]]
    except (TypeError, ValueError):
        return None


def _sessions_list_from_experiment_root(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(raw.get("sessions"), list):
        return [x for x in raw["sessions"] if isinstance(x, dict)]
    if raw.get("iterations") is not None or raw.get("root_goal") is not None:
        return [raw] if isinstance(raw, dict) else []
    return []


def _plan_key_for_session_merge(qr: Any) -> str:
    if not isinstance(qr, dict):
        return ""
    p = qr.get("orchestrator_plan")
    if not isinstance(p, dict):
        return ""
    try:
        return f'{p.get("tool_name")}|{json.dumps(p.get("args") or {}, sort_keys=True, ensure_ascii=False)}'
    except Exception:
        return str(p.get("tool_name") or "")


def _merge_orchestrator_plans_disk(prev_p: Any, inc_p: Any) -> Dict[str, Any]:
    """磁盘合并 query_results 时：在保留 rag_results 较多一侧的同时，从另一侧补全 HyDE / rerank / plansummary 等。"""
    out = copy.deepcopy(prev_p) if isinstance(prev_p, dict) else {}
    if not isinstance(inc_p, dict):
        return out
    for key in ("hyde_hypothetical_paragraph_full_text",):
        v = inc_p.get(key)
        if v is None:
            continue
        s = str(v).strip()
        if not s:
            continue
        cur = out.get(key)
        if cur is None or str(cur).strip() == "":
            out[key] = v
    ps = inc_p.get("plansummary")
    if ps is not None and ps != "" and (out.get("plansummary") in (None, "")):
        out["plansummary"] = ps
    try:
        ti = int(inc_p.get("total_results") or 0)
        tp = int(out.get("total_results") or 0)
        if ti > tp:
            out["total_results"] = ti
    except Exception:
        pass
    for key in ("rerank_before_ids", "rerank_after_ids"):
        v = inc_p.get(key)
        if not isinstance(v, list) or len(v) == 0:
            continue
        cur = out.get(key)
        if not isinstance(cur, list) or len(cur) == 0:
            out[key] = copy.deepcopy(v)
    return out


def _merge_query_results_lists_for_save(existing: List[Any], incoming: List[Any]) -> List[Any]:
    """同轮次内按策略键合并 query_results，避免追问追加时重复键。"""
    m: Dict[str, Any] = {}
    for qr in existing or []:
        if isinstance(qr, dict):
            k = _plan_key_for_session_merge(qr)
            if k:
                m[k] = copy.deepcopy(qr)
    for qr in incoming or []:
        if not isinstance(qr, dict):
            continue
        k = _plan_key_for_session_merge(qr)
        if not k:
            m[f"__anon_{len(m)}"] = copy.deepcopy(qr)
            continue
        prev = m.get(k)
        if not prev:
            m[k] = copy.deepcopy(qr)
        else:
            pr = len(prev.get("rag_results") or [])
            ir = len(qr.get("rag_results") or [])
            if ir >= pr:
                chosen = copy.deepcopy(qr)
                pp = chosen.get("orchestrator_plan") if isinstance(chosen.get("orchestrator_plan"), dict) else {}
                ip = prev.get("orchestrator_plan") if isinstance(prev.get("orchestrator_plan"), dict) else {}
                chosen["orchestrator_plan"] = _merge_orchestrator_plans_disk(pp, ip)
                m[k] = chosen
            else:
                chosen = copy.deepcopy(prev)
                pp = chosen.get("orchestrator_plan") if isinstance(chosen.get("orchestrator_plan"), dict) else {}
                ip = qr.get("orchestrator_plan") if isinstance(qr.get("orchestrator_plan"), dict) else {}
                chosen["orchestrator_plan"] = _merge_orchestrator_plans_disk(pp, ip)
                m[k] = chosen
    return list(m.values())


def _merge_iteration_lists_for_save(existing: List[Any], incoming: List[Any]) -> List[Any]:
    """按 round_number 合并迭代；追问运行时 incoming 往往只有新轮，必须与磁盘已有轮次合并。"""
    by_rn: Dict[Any, Dict[str, Any]] = {}
    for it in existing or []:
        if not isinstance(it, dict) or it.get("round_number") is None:
            continue
        by_rn[it["round_number"]] = copy.deepcopy(it)
    for it in incoming or []:
        if not isinstance(it, dict) or it.get("round_number") is None:
            continue
        rn = it["round_number"]
        if rn not in by_rn:
            by_rn[rn] = copy.deepcopy(it)
        else:
            cur = by_rn[rn]
            cur["query_results"] = _merge_query_results_lists_for_save(
                cur.get("query_results") or [], it.get("query_results") or []
            )
    def _rk(x: Any) -> tuple:
        if x is None:
            return (1, 0)
        try:
            return (0, int(x))
        except Exception:
            return (0, 0)

    return [by_rn[k] for k in sorted(by_rn.keys(), key=_rk)]


def _merge_session_dict_on_disk(existing: Optional[Dict[str, Any]], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """
    将本次运行产生的 session 快照合并进磁盘已有项。
    小追问 / 单轮保存时内存里常只有新增迭代，整段替换会丢掉原 JSON 中的历史轮次，故必须合并。
    """
    if not existing or not isinstance(existing, dict):
        return copy.deepcopy(incoming)
    out = copy.deepcopy(existing)
    in_sid = (incoming.get("session_id") or "").strip()
    if in_sid:
        out["session_id"] = in_sid
    ig = (incoming.get("root_goal") or "").strip()
    eg = (out.get("root_goal") or "").strip()
    if len(ig) > len(eg):
        out["root_goal"] = incoming.get("root_goal")
    elif ig and not eg:
        out["root_goal"] = incoming.get("root_goal")
    out["iterations"] = _merge_iteration_lists_for_save(
        out.get("iterations") or [], incoming.get("iterations") or []
    )
    ep: List[Any] = list(out.get("parameters") or [])
    seen_rn = {p.get("round_number") for p in ep if isinstance(p, dict)}
    for p in incoming.get("parameters") or []:
        if isinstance(p, dict):
            rn = p.get("round_number")
            if rn not in seen_rn:
                ep.append(copy.deepcopy(p))
                seen_rn.add(rn)
    out["parameters"] = ep
    if incoming.get("summary") is not None:
        out["summary"] = copy.deepcopy(incoming.get("summary"))
    if incoming.get("hypothesis") is not None:
        out["hypothesis"] = copy.deepcopy(incoming.get("hypothesis"))
    for k in ("use_multi_agent_rewrite_streams", "rewrite_variant_count"):
        if k in incoming:
            out[k] = copy.deepcopy(incoming[k])
    return out


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
    base_url="http://38.147.105.35:3030/v1",
    api_key="sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5",
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


def _is_retryable_llm_transport_error(exc: BaseException) -> bool:
    """网关 502/503、限流、超时等可重试；4xx 客户端错误不重试。"""
    code = getattr(exc, "status_code", None)
    if code is None:
        code = getattr(exc, "code", None)
    if isinstance(code, int):
        if code == 429:
            return True
        if code >= 500:
            return True
        return False
    name = type(exc).__name__
    if name in (
        "InternalServerError",
        "APIConnectionError",
        "APITimeoutError",
        "RateLimitError",
        "ServiceUnavailableError",
    ):
        return True
    s = str(exc).lower()
    if "502" in s or "503" in s or "504" in s or "500" in s or "timeout" in s or "connection" in s:
        return True
    return False


async def model_create_with_retry(
    model_client,
    *,
    messages,
    cancellation_token,
    source: str = "Orchestrator",
    max_retries: int = 5,
    base_delay: float = 1.8,
):
    """对 OpenAI 兼容网关的瞬时 5xx/429 做退避重试（与 autogen OpenAIChatCompletionClient.create 签名一致）。"""
    last_exc: Optional[BaseException] = None
    for attempt in range(max_retries):
        try:
            return await model_client.create(
                messages=messages,
                cancellation_token=cancellation_token,
            )
        except BaseException as e:
            last_exc = e
            if attempt >= max_retries - 1 or not _is_retryable_llm_transport_error(e):
                raise
            delay = min(48.0, base_delay * (2**attempt))
            logger.log(
                source,
                f"LLM 调用失败（{type(e).__name__}），{delay:.1f}s 后重试 ({attempt + 2}/{max_retries}）",
                "RETRY",
                detail_data=str(e)[:1200],
            )
            await asyncio.sleep(delay)
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("model_create_with_retry: no attempt executed")


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
    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        websocket_manager,
        is_follow_up_mode: bool = False,
        pause_gate=None,
        interactive_mode: bool = False,
        run_id: str = None,
        experiment_save_path: Optional[str] = None,
    ) -> None:
        super().__init__("Orchestrator")
        self.model_client = model_client
        self.ws_manager = websocket_manager
        self.is_follow_up_mode = is_follow_up_mode
        self.pause_gate = pause_gate
        self.interactive_mode = interactive_mode
        self.run_id = run_id
        # server 启动时确定的唯一文件；未传时由首次保存生成时间戳文件名（脚本/测试）
        self._server_experiment_save_path = experiment_save_path
        
        self.graph = ResearchGraph(root_goal="")
        self.round_count = 0
        self.pending_tasks = 0
        self.max_rounds = 3
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
        self.plans_per_round: int = 2
        self.collection_name: str = "multimodal2text"
        self.map_box_rect_2d: Optional[List[List[float]]] = None
        self.rag_allowed_chunk_ids: Optional[List[str]] = None
        self.session_id: str = ""
        self.batch_id: str = ""
        # True：不调用 Evaluator LLM，检索后对每条证据自动写入 KEEP 占位评估
        self.skip_evaluation: bool = False
        
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
        2. **Dynamic decisions**: adapt using **prior rounds' strategies and plan summaries** (`answer` / `suggestion` per plan). Do not rely on raw evidence text in the prompt.
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
           - `strategy_exact_search`: Used for exact text matching in the database. Parameter: `query_intent`. **IMPORTANT**: For exact search, you MUST use ONLY one or two specific proper nouns (e.g. "PM2.5" or "CNN-LSTM") rather than long phrases or sentences to prevent getting zero results. Prefer terms implied by prior `plansummary.answer` / `plansummary.suggestion` or plan `args`, not raw evidence text.

        Before outputting each strategy, internally check:
        - Relevance to the original user question (0-10)
        - Novelty vs historical strategies (0-10)
        Only output if both are >= 7.

        # Prior rounds (structured)
        The user message will include completed iterations: each plan's tool/args/reason plus `plansummary.answer` and `plansummary.suggestion`. Use them to avoid repeating failed angles and to pursue under-covered directions.

        # Language
        - Write every natural-language field **you output** (especially each strategy's `reason`) in **English**, even if the user's question is in another language.
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
                "reason": "Prior work already covers PM2.5 concentration trends, but chemical composition and sources are under-explored; we should retrieve studies on PM2.5 composition apportionment and source analysis for a fuller picture."
            },
            {
                "action": "call_tool",
                "ParentNode": "chunk_003329",
                "tool_name": "strategy_metadata_search", 
                "args": { "paper_id": "3" },
                "reason": "This hit discusses air-pollutant monitoring methods and was rated highly by the evaluator; opening the full paper should clarify methods and findings for follow-up validation."
            },
            {
                "action": "call_tool",
                "ParentNode": "0",
                "tool_name": "strategy_exact_search", 
                "args": { "query_intent": "VOC" },
                "reason": "We need passages that explicitly mention VOC; exact match avoids overly broad semantic noise."
            },
            {
                "action": "call_tool",
                "ParentNode": "chunk_002431",
                "tool_name": "strategy_semantic_search", 
                "args": { "query_intent": "Atmospheric dispersion model improvements and applications" },
                "reason": "Results mention pollutant dispersion but not model advances; retrieving dispersion-model improvements should strengthen prediction-oriented evidence."
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

    def _build_orchestrator_prior_rounds_context(self, max_answer_chars: int = 3500, max_suggestion_chars: int = 2000) -> str:
        """
        为下一轮规划构造上下文：仅包含已结束轮次中每条策略的元信息 + plansummary 的 answer/suggestion，
        不再注入证据节点全文（避免低质量噪声）。
        """
        lines: List[str] = []
        lines.append("\n## Prior completed rounds: strategies + plan summaries\n")
        lines.append(
            "Below lists each **executed** retrieval plan from finished iterations. "
            "For each plan, `answer` is the data-grounded response to what that strategy found; "
            "`suggestion` critiques whether that strategy angle was good. "
            "Use this (not raw passages) to decide broader vs deeper next steps. "
            "Do **not** repeat identical tool+args combinations unless you have a clearly new rationale.\n"
        )
        iters = getattr(self.experiment_result, "iterations", None) or []
        if not iters:
            lines.append("(No completed iterations recorded yet.)\n")
            return "".join(lines)
        for it in iters:
            rn = getattr(it, "round_number", "?")
            lines.append(f"\n### Iteration round_number={rn}\n")
            qrs = it.query_results or []
            if not qrs:
                lines.append("(No query_results in this iteration.)\n")
                continue
            for qi, qr in enumerate(qrs):
                op = qr.orchestrator_plan
                if not op:
                    continue
                ps = op.plansummary
                ps_str = ps.strip() if isinstance(ps, str) else ""
                answer_txt, suggestion_txt = "", ""
                if ps_str.startswith("{"):
                    try:
                        obj = json.loads(ps_str)
                        if isinstance(obj, dict):
                            a = obj.get("answer", "")
                            s = obj.get("suggestion", "")
                            answer_txt = str(a) if a is not None else ""
                            suggestion_txt = str(s) if s is not None else ""
                    except Exception:
                        answer_txt = ps_str[:max_answer_chars]
                        suggestion_txt = "(plansummary JSON parse failed; truncated raw in answer.)"
                elif ps_str:
                    answer_txt = ps_str[:max_answer_chars]
                    suggestion_txt = "(legacy free-text plansummary; no separate suggestion field.)"
                if len(answer_txt) > max_answer_chars:
                    answer_txt = answer_txt[:max_answer_chars] + "\n…(truncated)"
                if len(suggestion_txt) > max_suggestion_chars:
                    suggestion_txt = suggestion_txt[:max_suggestion_chars] + "\n…(truncated)"
                lines.append(f"- Plan index {qi + 1} in this iteration:\n")
                lines.append(
                    f"  - ParentNode: {op.ParentNode or '0'}, tool_name: {op.tool_name!r}, "
                    f"total_results: {op.total_results}, duplicate_results: {op.duplicate_results}\n"
                )
                lines.append(f"  - args: {json.dumps(op.args, ensure_ascii=False)}\n")
                lines.append(f"  - reason: {op.reason}\n")
                if answer_txt or suggestion_txt:
                    lines.append(f"  - plansummary.answer: {answer_txt or '(empty)'}\n")
                    lines.append(f"  - plansummary.suggestion: {suggestion_txt or '(empty)'}\n")
                else:
                    lines.append("  - plansummary: (not available yet for this plan)\n")
        return "".join(lines)

    async def push_update(self):
        """主动调用 WebSocket 推送当前 Graph 和 ExperimentResult（包含 plansummary）"""
        if self.ws_manager:
            # 注意：确保你的 connection.py / main.py 里的 manager 有 broadcast_graph 方法
            await self.ws_manager.broadcast_graph(
                self.graph,
                session_id=(self.session_id or None),
                follow_up=bool(self.is_follow_up_mode),
            )
            # 同时发送 experiment_result，以便前端获取 plansummary
            if self.experiment_result and self.experiment_result.iterations:
                await self.ws_manager.broadcast_experiment_result(
                    self.experiment_result,
                    session_id=self.session_id or None,
                    batch_id=self.batch_id or None,
                    follow_up=bool(self.is_follow_up_mode),
                )

    @message_handler
    async def handle_user(self, message: UserRequest, ctx: MessageContext) -> None:
        logger.log("Orchestrator", f"收到目标: {message.query}", "START")
        # 控制每轮 orchestrator_plan 输出多少个策略（call_tool）
        plans_per_round = getattr(message, "plans_per_round", 2)
        try:
            plans_per_round = int(plans_per_round)
        except Exception:
            plans_per_round = 2
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
        max_rounds = getattr(message, "max_rounds", 3)
        try:
            max_rounds = int(max_rounds)
        except Exception:
            max_rounds = 3
        self.max_rounds = max(1, min(max_rounds, 10))
        self.plans_per_round = plans_per_round
        self.collection_name = (getattr(message, "collection_name", None) or "").strip() or "multimodal2text"
        self.map_box_rect_2d = normalize_map_box_rect_2d(getattr(message, "map_box_rect_2d", None))
        _ids = getattr(message, "rag_allowed_chunk_ids", None)
        self.rag_allowed_chunk_ids = list(_ids) if _ids else None
        self.session_id = (getattr(message, "session_id", None) or "").strip()
        self.batch_id = (getattr(message, "batch_id", None) or "").strip()
        if self.batch_id and not self.session_id:
            import uuid
            self.session_id = str(uuid.uuid4())

        self.skip_evaluation = bool(getattr(message, "skip_evaluation", False))

        # 新用户问题：必须清空上一轮图与实验状态，否则旧证据仍留在 graph.nodes 里，
        # 前端 graphToRoundsData 会把多轮/多问题的策略挤进同一 round、纵向堆叠，并重复显示上一题内容。
        self.graph.root_goal = message.query
        self.graph.nodes = {
            "0": GraphNode(id="0", type="ROOT", status="ACTIVE", content={"goal": message.query})
        }
        self.graph.action_history = []
        self.graph.evidence_fingerprints = set()
        self.round_count = 0
        self.pending_tasks = 0
        self.current_iteration = None
        self.current_query_results.clear()
        self.history_strategies.clear()
        self.current_round_ids.clear()
        self.last_round_stats = {}
        _multi = bool(getattr(message, "use_multi_agent_rewrite_streams", False))
        _rvc = getattr(message, "rewrite_variant_count", None)
        try:
            _rvc_i = int(_rvc) if _rvc is not None else int(plans_per_round)
        except Exception:
            _rvc_i = int(plans_per_round)
        _rvc_i = max(1, min(10, _rvc_i))
        self.experiment_result = ExperimentResult(
            root_goal=message.query,
            session_id=self.session_id,
            use_multi_agent_rewrite_streams=_multi,
            rewrite_variant_count=_rvc_i,
        )

        # 使用模板渲染，避免多次运行时占位符被 replace 掉
        self.outputregulate = self.outputregulate_template.replace("__PLANS_PER_ROUND__", str(plans_per_round)).replace(
            "__RAG_RESULT_PER_PLAN__", str(rag_result_per_plan)
        )

        # 与 server 约定：进程内唯一 experiment_results_*.json；无 server 时首次保存再生成时间戳文件
        if self._server_experiment_save_path:
            self._experiment_save_path = self._server_experiment_save_path
        else:
            self._experiment_save_path = None
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
The user asked this scientific question (verbatim; language may vary):
"{query}"

Produce **two additional** distinct, diverse **query intents** (short phrases or sentences) for semantic literature retrieval.
Each intent should explore a **different** angle or related concept.

Return **only** a JSON array of exactly two strings, for example:
[
  "first query intent",
  "second query intent"
]

No markdown fences, no explanations, no extra keys—only the JSON array.
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
            reason="Initial retrieval using the user's original question to establish a baseline evidence set."
        ))
        
        # 改写问题策略
        for i, rw_query in enumerate(rewritten_queries):
            plans.append(OrchestratorPlan(
                action="call_tool",
                tool_name="strategy_semantic_search",
                ParentNode="0",
                args={"query_intent": rw_query, "n_results": self.rag_result_per_plan},
                reason=f"LLM-diverged exploratory search angle {i + 1}"
            ))

        # 3. 准备迭代结果
        from protocols import IterationResult, QueryResult
        self.current_iteration = IterationResult(round_number=self.round_count)
        self.current_query_results.clear()
        self._record_round_parameters_snapshot()
        
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

        plans = apply_rag_result_per_plan_to_plans(plans, self.rag_result_per_plan)
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
                    "session_id": self.session_id,
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
            await self.handle_eval(EvaluationReportMessage(evaluations=[], global_suggestion="No evaluation needed."), ctx)
            return

        if self.skip_evaluation:
            self.pending_eval_batches = 1
            synth = []
            for item in new_items_buffer:
                synth.append(
                    ItemEvaluation(
                        target_evidence_id=str(item.id),
                        branch_action="KEEP",
                        extracted_insight="(evaluation skipped)",
                        scores={"relevance": 8, "credibility": 8},
                        reason="skip_evaluation enabled; default KEEP without Evaluator LLM",
                        suggested_keywords=[],
                    )
                )
            await self.handle_eval(EvaluationReportMessage(evaluations=synth, global_suggestion=""), ctx)
            self.pending_tasks -= 1
            logger.log(
                "Orchestrator",
                f"已跳过评估器，直接为 {len(synth)} 条证据写入占位 KEEP",
                "SKIP_EVAL_APPLIED",
            )
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

            # 收集当前轮次的证据数据；内联 await InteractionSummaryAgent 直至所有 plansummary 完成后再进入下一轮规划
            current_evidence_data = []
            for nid in self.current_round_ids:
                if nid in self.graph.nodes:
                    node = self.graph.nodes[nid]
                    evidence_item = RawEvidenceItem(
                        id=node.id,
                        source_tool=node.source_tool,
                        content=node.content,
                        metadata=node.metadata,
                        score=0.0,
                        source_args=node.source_args,
                    )
                    current_evidence_data.append(evidence_item)

            logger.log(
                "Orchestrator",
                "内联调用 InteractionSummaryAgent（仅 per-plan plansummary；完成后才进入下一轮规划）",
                "SUMMARY_CALL",
            )
            # 必须 await 在本协程内跑完：保证本轮所有 plansummary 写完后再 _plan_next_move；勿用 publish_message 以免与 runtime 顺序不确定
            _summary_agent = InteractionSummaryAgent(self.model_client, self.ws_manager)
            await _summary_agent.handle_summary_request(
                SummaryRequest(
                    experiment_result=self.experiment_result,
                    current_evidence_data=current_evidence_data,
                    current_question=self.graph.root_goal,
                    user_original_input=self.experiment_result.root_goal or self.graph.root_goal,
                ),
                ctx,
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
           - 从 `experiment_result.iterations` 注入【已完成轮次】中每条策略的 tool/args/reason 及 **plansummary** 的 `answer`（数据侧归纳）与 `suggestion`（策略评价）；**不再**注入证据节点全文。
           - 结合图谱规模（节点数）与已完成的规划轮次，决定广度/深度。
        
        2. **LLM 决策 (Decision)**：
           - 调用模型生成 JSON 格式的任务列表，决定是继续深挖 (Deeper) 还是横向扩展 (Broader)。
        
        3. **批处理初始化 (Batch Setup)**：
           - 计算有效任务数量并设置 `self.pending_tasks` 计数器，用于控制异步流的批处理闭环。
           - 处理边界情况（如无任务或 LLM 决定结束）。
        
        4. **参数清洗与分发 (Dispatch)**：
           - 强制类型转换：确保 `ParentNode` 为安全的字符串 ID (0/None -> "ROOT")。
           - 封装为 `OrchestratorPlan` 消息，并行广播给 ToolExecutor。
        '''
        # 规划阶段不再把当前轮证据节点的全文塞进 prompt；清空 id 集合（摘要阶段已消费过）
        self.current_round_ids.clear()

        # ⚡️ 修改：处理初始搜索的特殊情况
        if self.round_count == 0 and len(self.graph.nodes) <= 1:
            # 尚无图谱证据节点时的兜底（极少触发）
            self.strategyhis = f'''User question: {self.graph.root_goal}. Every strategy must directly serve this question and avoid irrelevant drift.
            Current state: planning with little or no evidence graph yet (nodes: {len(self.graph.nodes)}).
            Propose the next retrieval strategies using only the structured prior-round summaries below (may be empty on the very first continuation).'''
        else:
            self.strategyhis = f'''User question: {self.graph.root_goal}. Every strategy must directly serve this question and avoid irrelevant drift.
            Completed planner-evaluation cycles so far: {self.round_count}. Evidence graph nodes (including ROOT): {len(self.graph.nodes)}.
            The next section summarizes **finished iterations only**: each plan's tool/args/reason and its plan-summary **answer** (what the data supported) and **suggestion** (how good the strategy was).'''

        self.searchpro = self._build_orchestrator_prior_rounds_context()
        # 生成规范
        prompt =""
        prompt += self.strategyhis
        prompt += self.searchpro
        prompt += self.outputregulate        
        
        # ⚡️ 新增：记录完整的prompt内容
        # logger.log_prompt(self.round_count, prompt)
        
        logger.log("Orchestrator", "思考并发策略...", "PLANNING")
        response = await model_create_with_retry(
            self.model_client,
            messages=[self.system_message, UserMessage(content=prompt, source="user")],
            cancellation_token=ctx.cancellation_token,
            source="Orchestrator",
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
            self._record_round_parameters_snapshot()
        
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

            plans = apply_rag_result_per_plan_to_plans(plans, self.rag_result_per_plan)
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

    def _record_round_parameters_snapshot(self) -> None:
        """每轮开始时追加一条 parameters 快照（与 root_goal 同文件），并立即保存。"""
        rn = self.current_iteration.round_number if self.current_iteration is not None else self.round_count
        allowed = self.rag_allowed_chunk_ids
        if allowed is not None:
            allowed = list(allowed)
        snap = ExperimentRoundParameters(
            round_number=rn,
            max_rounds=self.max_rounds,
            plans_per_round=self.plans_per_round,
            rag_result_per_plan=self.rag_result_per_plan,
            collection_name=self.collection_name or "multimodal2text",
            interactive=self.interactive_mode,
            rag_allowed_chunk_ids=allowed,
            map_box_rect_2d=self.map_box_rect_2d,
            skip_evaluation=bool(self.skip_evaluation),
        )
        self.experiment_result.parameters.append(snap)
        self._save_experiment_results_impl()

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
        """
        统一落盘为 experiment_results_*.json，根结构为 { "sessions": [ ... ], "batch_id"?: str }。
        按 session_id 合并/更新对应项，保留文件中其它会话（读-合并-写，避免整文件被单次会话覆盖）。
        """
        # 确保root_goal已设置
        if not self.experiment_result.root_goal and self.graph.root_goal:
            self.experiment_result.root_goal = self.graph.root_goal

        import os
        if not os.path.isdir("logs"):
            os.makedirs("logs", exist_ok=True)

        if self._experiment_save_path is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self._experiment_save_path = f"logs/experiment_results_{timestamp}.json"

        try:
            payload = json.loads(self.experiment_result.model_dump_json())
            sid = (self.session_id or payload.get("session_id") or "").strip()

            doc: Dict[str, Any] = {"sessions": []}
            if os.path.exists(self._experiment_save_path):
                with open(self._experiment_save_path, "r", encoding="utf-8") as rf:
                    raw = json.load(rf)
                if isinstance(raw, dict):
                    for k, v in raw.items():
                        if k == "sessions":
                            continue
                        doc[k] = v
                    doc["sessions"] = _sessions_list_from_experiment_root(raw)

            if self.batch_id:
                doc["batch_id"] = self.batch_id

            idx = next(
                (
                    i
                    for i, s in enumerate(doc["sessions"])
                    if isinstance(s, dict) and (s.get("session_id") or "") == sid
                ),
                None,
            )
            if idx is None:
                doc["sessions"].append(payload)
            else:
                doc["sessions"][idx] = _merge_session_dict_on_disk(doc["sessions"][idx], payload)

            with open(self._experiment_save_path, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)

            logger.log("Orchestrator", f"实验结果已保存（sessions 合并）: {self._experiment_save_path}", "SAVE")
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
        
        # [暂时关闭 Hypothesis：不向 Hypothesis 主题发送 TaskComplete；恢复时取消注释]
        # await self.publish_message(
        #     TaskComplete(
        #         graph_snapshot=self.graph,
        #         experiment_result=self.experiment_result,
        #         experiment_save_path=save_path
        #     ),
        #     topic_id=TopicId(TOPIC_HYPOTHESIS, source=self.id.key)
        # )
    
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
        round_number 由前端指定为「新一行」的迭代编号（通常为当前最大 round + 1）。
        追问使用独立 runtime，图谱仅含本轮新证据；前端需合并历史小矩形，见 WS follow_up 标记。
        """
        query = (message.query or "").strip()
        if not query:
            return

        self.session_id = (getattr(message, "session_id", None) or "").strip()
        self.batch_id = (getattr(message, "batch_id", None) or "").strip()
        if self._server_experiment_save_path:
            self._experiment_save_path = self._server_experiment_save_path
        else:
            self._experiment_save_path = None
        root_goal = (getattr(message, "root_goal", None) or "").strip()
        self.graph.root_goal = root_goal or query
        if "0" not in self.graph.nodes:
            self.graph.nodes["0"] = GraphNode(
                id="0", type="ROOT", status="ACTIVE", content={"goal": self.graph.root_goal}
            )
        else:
            try:
                if self.graph.nodes["0"].type == "ROOT":
                    self.graph.nodes["0"].content = {"goal": self.graph.root_goal}
            except Exception:
                pass
        self.experiment_result.root_goal = self.graph.root_goal
        self.experiment_result.session_id = self.session_id

        # 把 round_count 强制设置为前端指定轮次，保证 created_at_round 和 plan_created 的 round_number 对齐
        try:
            self.round_count = int(message.round_number)
        except Exception:
            self.round_count = 0

        try:
            self.rag_result_per_plan = int(message.rag_result_per_plan)
        except Exception:
            pass

        self.collection_name = (getattr(message, "collection_name", None) or "").strip() or "multimodal2text"
        self.map_box_rect_2d = normalize_map_box_rect_2d(getattr(message, "map_box_rect_2d", None))
        _fu_ids = getattr(message, "rag_allowed_chunk_ids", None)
        self.rag_allowed_chunk_ids = list(_fu_ids) if _fu_ids else None
        self.plans_per_round = 1
        self.max_rounds = 1

        parent_id = (message.parent_node_id or "0")

        self.skip_evaluation = bool(getattr(message, "skip_evaluation", False))

        logger.log("Orchestrator", f"收到追问请求: round={self.round_count}, parent={parent_id}, query={query}", "FOLLOW_UP")

        fu_tool = (getattr(message, "follow_up_tool", None) or "strategy_semantic_search").strip()
        allowed_fu = {
            "strategy_semantic_search",
            "strategy_exact_search",
            "strategy_metadata_search",
        }
        if fu_tool not in allowed_fu:
            fu_tool = "strategy_semantic_search"

        if fu_tool in ("strategy_semantic_search", "strategy_exact_search"):
            follow_plan = OrchestratorPlan(
                action="call_tool",
                tool_name=fu_tool,
                ParentNode=parent_id,
                args={"query_intent": query, "n_results": self.rag_result_per_plan},
                reason=f"Follow-up ({fu_tool}): user-specified retrieval and evaluation.",
            )
        else:
            # metadata：paper_id 形如 paper_*，否则按逗号拆 keywords，否则整句作为单关键词
            meta_args: Dict[str, Any] = {"keywords": None, "paper_id": None, "figure_type": None}
            if re.match(r"^paper_\w+", query, re.IGNORECASE):
                meta_args["paper_id"] = query.strip()
            else:
                parts = [p.strip() for p in query.split(",") if p.strip()]
                meta_args["keywords"] = parts if parts else [query.strip()]
            follow_plan = OrchestratorPlan(
                action="call_tool",
                tool_name="strategy_metadata_search",
                ParentNode=parent_id,
                args=meta_args,
                reason="Follow-up (strategy_metadata_search): user-specified metadata filter.",
            )

        # 创建 iteration/query_result 结构（让 experiment_result/前端小矩形逻辑一致）
        from protocols import IterationResult, QueryResult, OrchestratorPlanBatch
        self.current_iteration = IterationResult(round_number=self.round_count)
        self.current_query_results.clear()
        self._record_round_parameters_snapshot()

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
                "session_id": self.session_id,
                "follow_up": True,
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
                    out_plan = plan
                    if plan.tool_name == "strategy_semantic_search":
                        trace = consume_semantic_pipeline_trace()
                        if trace is not None:
                            out_plan = plan.model_copy(
                                update={
                                    "hyde_hypothetical_paragraph_full_text": trace.get(
                                        "hyde_hypothetical_paragraph_full_text"
                                    ),
                                    "rerank_before_ids": trace.get("rerank_before_ids"),
                                    "rerank_after_ids": trace.get("rerank_after_ids"),
                                }
                            )
                    return SingleToolOutput(original_plan=out_plan, raw_items=items)
                else:
                    logger.log("ToolExecutor", f"工具未找到: {plan.tool_name}", "ERROR")
                    return SingleToolOutput(original_plan=plan, raw_items=[], error=f"Tool {plan.tool_name} not found")
            except Exception as e:
                if plan.tool_name == "strategy_semantic_search":
                    consume_semantic_pipeline_trace()
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

        # Language
        - Write **all** human-readable string fields (`extracted_insight`, `reason`, `suggested_keywords` entries) in **English**, even if evidence titles/snippets are in another language.
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
# 由 Orchestrator 在每轮评估结束后内联 await handle_summary_request；不再向 runtime 注册本类。
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
        - Write all narrative output in **English**.
        """)
        # 单策略 plansummary：与整轮总结 system_message 分离，避免输出格式冲突
        self.plan_summary_system_message = SystemMessage(
            content="""You are the **per-plan Plan Summary** agent.

## Role
From the user message you receive: the user question, the current strategy (tool / args / reason), retrieved hits with per-item evaluations, and optionally an iteration-level retrieval-quality note, you must do exactly two things and output **only** the specified JSON:
1. **answer**: Grounded in retrieved content (titles, summaries, insights, etc.), explain **what the evidence supports under this strategy's intent**; stay tied to the user question and sub-question; avoid vague repetition.
2. **suggestion**: Critique whether this strategy was a good choice (tool type, query parameters, search direction), including strengths, risks, or improvements; if evidence is thin or evaluations are mostly PRUNE, say so honestly.

## Output format (strict)
Output a **single** JSON object only. No Markdown code fences, no preamble or postfix.
Keys must be lowercase ASCII and both must exist:
- "answer": string
- "suggestion": string

Both values are plain text; use \\n inside strings for line breaks if needed.

## Language
- Write **answer** and **suggestion** in **English**, even when the user question or corpus snippets are in another language.
"""
        )
    @message_handler 
    async def handle_summary_request(self, message: SummaryRequest, ctx: MessageContext) -> None:
        """
        处理总结请求：已关闭整轮过程总结、词云、检索质量评估 LLM/计算；
        仅顺序生成每条 plan 的 plansummary。
        """
        logger.log("InteractionSummaryAgent", "收到总结请求，开始分析实验结果...", "SUMMARY_START")
        
        try:
            # 1. 整轮过程总结（generate_process_summary）— 按需求关闭，不再调用 LLM、不写入 iteration_summary
            # process_summary = await self.generate_process_summary(
            #     message.experiment_result,
            #     message.current_evidence_data,
            #     message.current_question,
            #     message.user_original_input,
            # )
            process_summary = ""

            # 2. 词云（generate_word_cloud）— 已关闭，仅占位
            # word_cloud_data = await self.generate_word_cloud(...)
            word_cloud_data = WordCloudData(words=[], total_words=0, top_keywords=[])

            # 3. 检索质量评估（evaluate_retrieval_quality）— 已关闭，仅占位
            # quality_evaluation = await self.evaluate_retrieval_quality(...)
            quality_evaluation = RetrievalQualityEvaluation(
                relevance_score=0.0,
                accuracy_score=0.0,
                authority_score=0.0,
                completeness_score=0.0,
                overall_score=0.0,
                positive_meaning="(disabled: iteration-level retrieval quality LLM not run)",
                contribution_to_knowledge="(disabled)",
                strengths=[],
                weaknesses=[],
                suggestions=[],
            )

            # 4. 生成时间戳
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 5. 构建响应消息（按 iteration 粒度的整体总结）
            summary_response = SummaryResponse(
                process_summary=process_summary,
                word_cloud_data=word_cloud_data,
                quality_evaluation=quality_evaluation,
                timestamp=timestamp
            )
            
            # 6. 保存 SummaryResponse（process_summary 已为空）；不再写入 iteration_summary（整轮文字总结已停用）
            message.experiment_result.summary = summary_response
            if message.experiment_result.iterations:
                message.experiment_result.iterations[-1].iteration_summary = None

            # 7. 为当前轮次的每个策略顺序生成 plansummary（全部 await 完成后本函数才返回 → Orchestrator 再规划下一轮）
            # 不再向单策略总结注入「整轮检索质量评估」JSON（该评估已关闭）
            qe_for_plan = ""
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
                            iteration_quality_json=qe_for_plan,
                        )
                        query_result.orchestrator_plan.plansummary = plan_summary
                    except Exception as e:
                        logger.log(
                            "InteractionSummaryAgent",
                            f"生成单个策略总结时出错: {e}",
                            "ERROR",
                        )

            # 8. 实时保存总结结果到系统日志中
            logger.log(
                "InteractionSummaryAgent",
                "本轮 per-plan plansummary 已完成（整轮过程总结 / 词云 / 检索质量评估均已关闭）",
                "SUMMARY_LOG",
            )
            
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
        iteration_quality_json: str | None = None,
    ) -> str:
        """
        为单个 OrchestratorPlan 生成策略级总结，落盘字段 `plansummary` 为 JSON 字符串：
        {\"answer\": \"...\", \"suggestion\": \"...\"}。
        """
        root_goal = experiment_result.root_goal
        plan = query_result.orchestrator_plan
        rag_results = query_result.rag_results or []

        total_results = getattr(plan, "total_results", len(rag_results))
        duplicate_results = getattr(plan, "duplicate_results", 0)

        prompt_lines = []
        prompt_lines.append("# Input instructions\n")
        prompt_lines.append(
            "Below is one retrieval strategy with its evidence rows and evaluations. "
            "Follow the system role and output **only** the required JSON.\n"
        )

        prompt_lines.append("## User question\n")
        prompt_lines.append(f"- Original user input: {user_original_input or root_goal}\n")
        prompt_lines.append(f"- Current sub-question / planning context: {current_question or root_goal}\n")

        prompt_lines.append("\n## Current plan (strategy)\n")
        prompt_lines.append(f"- tool_name: {plan.tool_name}\n")
        prompt_lines.append(f"- args: {json.dumps(plan.args, ensure_ascii=False)}\n")
        prompt_lines.append(f"- reason: {plan.reason}\n")
        prompt_lines.append(f"- stats: total retrieved {total_results}, duplicates {duplicate_results}\n")

        if iteration_quality_json and str(iteration_quality_json).strip():
            prompt_lines.append("\n## Optional: iteration-level retrieval quality note\n")
            prompt_lines.append(str(iteration_quality_json).strip() + "\n")

        prompt_lines.append(
            "\n## Retrieved rows and per-item evaluations\n"
            "Each evidence row provides **id** and **content-text** (body text preferred; "
            "if missing, title+summary are joined, common for figures/multimodal).\n"
        )
        if not rag_results:
            prompt_lines.append(
                "- This strategy returned no rows. In **answer**, explain likely causes; "
                "in **suggestion**, judge whether the strategy should be kept or revised.\n"
            )
        else:
            result_idx = 0
            for rag_result in rag_results:
                rr = rag_result.retrieval_result
                ev = rag_result.evaluation

                eid, content_text = _plan_summary_rag_id_and_content_text(rr)
                rid = (eid or str(getattr(rr, "id", "") or "")).strip()
                has_content = bool(
                    rid
                    and (
                        content_text
                        or (ev and (ev.branch_action or ev.extracted_insight or ev.reason))
                    )
                )
                if not has_content:
                    continue

                result_idx += 1
                prompt_lines.append(f"### Row {result_idx}\n")
                prompt_lines.append(f"- id: {rid}\n")
                prompt_lines.append(f"- content-text: {content_text if content_text else '(empty)'}\n")

                if ev:
                    prompt_lines.append(f"- evaluation branch_action: {ev.branch_action}\n")
                    if ev.extracted_insight:
                        prompt_lines.append(f"- evaluation extracted_insight: {ev.extracted_insight}\n")
                    if ev.reason:
                        prompt_lines.append(f"- evaluation reason: {ev.reason}\n")
                    if getattr(ev, "scores", None) is not None:
                        try:
                            prompt_lines.append(f"- evaluation scores: {json.dumps(ev.scores, ensure_ascii=False)}\n")
                        except Exception:
                            prompt_lines.append(f"- evaluation scores: {ev.scores}\n")
                prompt_lines.append("")

        prompt = "\n".join(prompt_lines)

        logger.log(
            "InteractionSummaryAgent",
            f"为单个策略生成总结时使用的提示: {prompt[:800]}...",
            "PLAN_SUMMARY_DEBUG"
        )

        try:
            response = await self.model_client.create(
                messages=[
                    self.plan_summary_system_message,
                    UserMessage(content=prompt, source="user"),
                ],
                cancellation_token=None,
            )
            logger.log_llm_interaction(
                source="InteractionSummaryAgent (Plan Summary)",
                prompt=prompt,
                response=response.content,
                system_message=self.plan_summary_system_message.content
                if self.plan_summary_system_message
                else None,
            )
            return _normalize_plan_summary_llm_output(response.content)
        except Exception as e:
            logger.log(
                "InteractionSummaryAgent",
                f"调用大模型生成单个策略总结时出错: {e}",
                "ERROR",
            )
            return json.dumps(
                {"answer": "", "suggestion": f"Error while generating plan summary: {e}"},
                ensure_ascii=False,
            )

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
                        content_str = str(content) if content else "(no content)"
                        prompt += f"    - **Result {k+1}**: {content_str[:100]}...\n"
                        if rag_result.evaluation:
                            prompt += f"      - **Evaluation**: {rag_result.evaluation.branch_action}\n"
                            prompt += f"      - **Scores**: {rag_result.evaluation.scores}\n"
                            # 安全获取extracted_insight
                            insight = rag_result.evaluation.extracted_insight
                            insight_str = str(insight) if insight else "(no insight)"
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
                positive_meaning="No retrieval was performed.",
                contribution_to_knowledge="No contribution yet.",
                strengths=[],
                weaknesses=["No retrieval executed"],
                suggestions=["Run retrieval again with clearer intents"],
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
        positive_meaning = (
            f"The question targets '{experiment_result.root_goal}' with multi-round retrieval to gather relevant material."
        )
        contribution_to_knowledge = (
            "Systematic retrieval across tools produced a multi-faceted evidence set with moderate knowledge value."
        )

        strengths = [
            "Multi-round retrieval",
            "Mixed retrieval tools",
            "Evaluator-based filtering of hits",
        ]
        weaknesses = []
        suggestions = []
        
        # 根据评估结果分析不足和建议
        if relevance_score < 0.6:
            weaknesses.append("Low relevance between hits and the question")
            suggestions.append("Tighten query intents and add domain-specific terms")

        if accuracy_score < 0.6:
            weaknesses.append("Accuracy of retrieved statements is uncertain")
            suggestions.append("Prioritize peer-reviewed sources and cross-check claims")

        if authority_score < 0.6:
            weaknesses.append("Limited authority of sources")
            suggestions.append("Bias retrieval toward established venues and datasets")

        if completeness_score < 0.6:
            weaknesses.append("Coverage gaps across subtopics")
            suggestions.append("Broaden strategies (semantic + metadata + exact) to fill gaps")

        if not weaknesses:
            weaknesses.append("No major weaknesses detected heuristically")
            suggestions.append("Keep the current retrieval mix while monitoring PRUNE rate")
        
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
        3. Write a focused paragraph (about 150–280 English words unless evidence is unusually rich).
        4. Cite evidence inline using `[Evidence: node_id]`.

        # Writing Requirements
        1. Synthesize evidence instead of listing fragments.
        2. Every key claim must be evidence-backed.
        3. Keep structure and logic clear.
        4. Use natural academic English only (no Chinese or mixed-language prose in the section body).
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
        4. Use fluent academic English.
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
                        topic_name=f"Topic {i + 1}",
                        description="",
                        sub_questions=[f"Sub-question {i + 1}"],
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
            self.report_content = f"Report generation failed: {str(e)}"
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
    plans_per_round: int = 2,
    rag_result_per_plan: int = 10,
    max_rounds: int = 3,
    interactive_mode: bool = False,
    run_id: str = None,
    pause_gate = None,
    rag_allowed_chunk_ids: Optional[List[str]] = None,
    map_box_rect_2d: Optional[List[List[float]]] = None,
    session_id: str = "",
    batch_id: str = "",
    skip_evaluation: bool = False,
    experiment_save_path: Optional[str] = None,
    use_multi_agent_rewrite_streams: bool = False,
    rewrite_variant_count: Optional[int] = None,
):
    set_active_collection_name(collection_name)
    set_rag_allowed_chunk_ids(rag_allowed_chunk_ids)
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
        model_client = OpenAIChatCompletionClient(
            model="gpt-4o",
            base_url="http://38.147.105.35:3030/v1",
            api_key="sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
        )
        # model_client = OpenAIChatCompletionClient(
        #     model="deepseek-r1:671b-0528",
        #     base_url="https://uni-api.cstcloud.cn/v1",
        #     api_key="f24a9af08a33a9649b3f149706c8c45e8602a884b8beab6abae0d608226477f8",
        #     model_info=ModelInfo(
        #         vision=False,                  # 根据实际情况
        #         structured_output=False,
        #         function_calling=True,         # 大多数支持工具调用的模型设 True
        #         streaming=True,
        #         json_output=False,
        #         family="deepseek",
        #         context_length=65536,          # 64k
        #         # max_output_tokens=8192       # 可选
        #     )
        # )

        runtime = SingleThreadedAgentRuntime()
        _esp = experiment_save_path
        await OrchestratorAgent.register(
            runtime,
            type=TOPIC_ORCHESTRATOR,
            factory=lambda: OrchestratorAgent(
                model_client,
                manager,
                pause_gate=pause_gate,
                interactive_mode=interactive_mode,
                run_id=run_id,
                experiment_save_path=_esp,
            ),
        )
        await ToolExecutorAgent.register(runtime, type=TOPIC_TOOL, factory=lambda: ToolExecutorAgent())
        await EvaluatorAgent.register(runtime, type=TOPIC_EVALUATOR, factory=lambda: EvaluatorAgent(model_client))
        # [暂时关闭 Hypothesis 以加快调试；恢复时取消下面一行注释]
        # await HypothesisGeneratorAgent.register(runtime, type=TOPIC_HYPOTHESIS, factory=lambda: HypothesisGeneratorAgent(model_client, manager))
        # InteractionSummaryAgent 改由 Orchestrator 内联 await，不再注册到 runtime（避免与 publish 双跑）

        runtime.start()
        _rvc_pub = rewrite_variant_count
        if _rvc_pub is None:
            try:
                _rvc_pub = int(plans_per_round)
            except Exception:
                _rvc_pub = 2
            _rvc_pub = max(1, min(10, _rvc_pub))
        else:
            try:
                _rvc_pub = max(1, min(10, int(_rvc_pub)))
            except Exception:
                _rvc_pub = max(1, min(10, int(plans_per_round)))
        # 使用传入的查询参数，而不是硬编码的内容
        await runtime.publish_message(
            UserRequest(
                query=query,
                plans_per_round=plans_per_round,
                rag_result_per_plan=rag_result_per_plan,
                max_rounds=max_rounds,
                interactive=interactive_mode,
                rag_allowed_chunk_ids=rag_allowed_chunk_ids,
                map_box_rect_2d=normalize_map_box_rect_2d(map_box_rect_2d),
                collection_name=collection_name,
                session_id=(session_id or "").strip(),
                batch_id=(batch_id or "").strip(),
                skip_evaluation=bool(skip_evaluation),
                use_multi_agent_rewrite_streams=bool(use_multi_agent_rewrite_streams),
                rewrite_variant_count=_rvc_pub,
            ),
            topic_id=TopicId(TOPIC_ORCHESTRATOR, source="User")
        )
        
        await runtime.stop_when_idle()

    except KeyboardInterrupt:
        print("User Interrupted.")
    finally:
        set_rag_allowed_chunk_ids(None)
        await rag.close()

async def run_rag_workflow_expand(
    parent_node_id: str,
    search_type: str,
    search_query: str,
    manager: ConnectionManager,
    collection_name: str = "multimodal2text",
    experiment_save_path: Optional[str] = None,
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
            model="gpt-4o",
            base_url="http://38.147.105.35:3030/v1",
            api_key="sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
        )
        # model_client = OpenAIChatCompletionClient(
        #     model="deepseek-r1:671b-0528",
        #     base_url="https://uni-api.cstcloud.cn/v1",
        #     api_key="f24a9af08a33a9649b3f149706c8c45e8602a884b8beab6abae0d608226477f8",
        #     model_info=ModelInfo(
        #         vision=False,
        #         structured_output=False,
        #         function_calling=True,
        #         streaming=True,
        #         json_output=False,
        #         family="deepseek",
        #     ),
        # )

        runtime = SingleThreadedAgentRuntime()
        _esp_e = experiment_save_path
        await OrchestratorAgent.register(
            runtime,
            type=TOPIC_ORCHESTRATOR,
            factory=lambda: OrchestratorAgent(model_client, manager, experiment_save_path=_esp_e),
        )
        await ToolExecutorAgent.register(runtime, type=TOPIC_TOOL, factory=lambda: ToolExecutorAgent())
        await EvaluatorAgent.register(runtime, type=TOPIC_EVALUATOR, factory=lambda: EvaluatorAgent(model_client))
        # [暂时关闭 Hypothesis 以加快调试]
        # await HypothesisGeneratorAgent.register(
        #     runtime, type=TOPIC_HYPOTHESIS, factory=lambda: HypothesisGeneratorAgent(model_client, manager)
        # )
        # InteractionSummaryAgent 改由 Orchestrator 内联 await，不再注册到 runtime（避免与 publish 双跑）

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
    rag_allowed_chunk_ids: Optional[List[str]] = None,
    map_box_rect_2d: Optional[List[List[float]]] = None,
    skip_evaluation: bool = False,
    session_id: str = "",
    batch_id: str = "",
    root_goal: str = "",
    experiment_save_path: Optional[str] = None,
    follow_up_tool: str = "strategy_semantic_search",
):
    """
    追问工作流：只做一次检索 + 评估（不走多轮规划）。
    round_number 为前端「新一行」对应的 iteration 编号（通常为 max(round)+1）。
    """
    set_active_collection_name(collection_name)
    set_rag_allowed_chunk_ids(rag_allowed_chunk_ids)
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        base_url="http://38.147.105.35:3030/v1",
        api_key="sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
    )
    # model_client = OpenAIChatCompletionClient(
    #     model="deepseek-r1:671b-0528",
    #     base_url="https://uni-api.cstcloud.cn/v1",
    #     api_key="f24a9af08a33a9649b3f149706c8c45e8602a884b8beab6abae0d608226477f8",
    #     model_info=ModelInfo(
    #         vision=False,
    #         structured_output=False,
    #         function_calling=True,
    #         streaming=True,
    #         json_output=False,
    #         family="deepseek",
    #     )
    # )

    runtime = SingleThreadedAgentRuntime()
    _esp_fu = experiment_save_path
    await OrchestratorAgent.register(
        runtime,
        type=TOPIC_ORCHESTRATOR,
        factory=lambda: OrchestratorAgent(model_client, manager, is_follow_up_mode=True, experiment_save_path=_esp_fu),
    )
    await ToolExecutorAgent.register(runtime, type=TOPIC_TOOL, factory=lambda: ToolExecutorAgent())
    await EvaluatorAgent.register(runtime, type=TOPIC_EVALUATOR, factory=lambda: EvaluatorAgent(model_client))
    # [暂时关闭 Hypothesis 以加快调试]
    # await HypothesisGeneratorAgent.register(runtime, type=TOPIC_HYPOTHESIS, factory=lambda: HypothesisGeneratorAgent(model_client, manager))
    # InteractionSummaryAgent 由 Orchestrator 内联 await，不注册

    runtime.start()
    try:
        await runtime.publish_message(
            FollowUpRequest(
                query=query,
                follow_up_tool=(follow_up_tool or "strategy_semantic_search").strip(),
                parent_node_id=parent_node_id,
                round_number=round_number,
                rag_result_per_plan=rag_result_per_plan,
                rag_allowed_chunk_ids=rag_allowed_chunk_ids,
                map_box_rect_2d=normalize_map_box_rect_2d(map_box_rect_2d),
                collection_name=collection_name,
                skip_evaluation=bool(skip_evaluation),
                session_id=(session_id or "").strip(),
                batch_id=(batch_id or "").strip(),
                root_goal=(root_goal or "").strip(),
            ),
            topic_id=TopicId(TOPIC_ORCHESTRATOR, source="User"),
        )
        await runtime.stop_when_idle()
    finally:
        set_rag_allowed_chunk_ids(None)

if __name__ == "__main__":
    asyncio.run(main())