"""
【功能】多路改写 + 独立追问轨（实验性）：与主 engine.py 并行，不修改 engine 源码。
流程：用户问题 → LLM 生成 N 条相关且不重复的改写 → 每条改写独立成一行；同一「波次」内多轨并行各跑一步检索，
每轨在满足 **本轨 max_rounds** 或 **本轨** LLM 判定可结束时停止（不再执行检索），之后在后续波次对该轨写入占位格。
迭代列（iteration.round_number）仍表示时间上的第几波（全局对齐），网格坐标 grid_pos[1] 表示该轨已完成的检索轮序号。
经 WebSocket 推送 graph / experiment_result 与主流程一致。
"""
from __future__ import annotations

import asyncio
import json
import os
import traceback
import uuid
from typing import Any, Dict, List, Optional

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import SystemMessage, UserMessage

from protocols import (
    ExperimentResult,
    ExperimentRoundParameters,
    GraphNode,
    IterationResult,
    NodeSearchRecord,
    OrchestratorPlan,
    QueryResult,
    ResearchGraph,
)
from rag_service import get_rag_service
from scientific_tools import set_active_collection_name, set_rag_allowed_chunk_ids
from single_strategy_api import SingleStrategyExecutor

# 复用 engine 内工具函数（import 不修改 engine.py 文件）
from engine import (
    apply_rag_result_per_plan_to_plans,
    model_create_with_retry,
    normalize_map_box_rect_2d,
    _merge_session_dict_on_disk,
    _sessions_list_from_experiment_root,
)


def _make_model_client() -> OpenAIChatCompletionClient:
    """与 engine.run_rag_workflow 使用同一网关配置，便于对比实验。"""
    return OpenAIChatCompletionClient(
        model="gpt-4o",
        base_url="https://ssvip.dmxapi.com/v1",
        api_key="sk-8S92KJLEQcfF9TbjsLfSPrP3LRz6tsuzbRRpHXVH12Gp4SZc",
    )
    # return OpenAIChatCompletionClient(
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
    #         context_length=65536,
    #     ),
    # )


_REWRITE_SYSTEM = SystemMessage(
    content="""You rewrite a user's scientific / visualization question into multiple retrieval-oriented variants.
Rules:
- All variants must stay on-topic relative to the original question.
- Maximize diversity (different angles, methods, datasets, or sub-questions); avoid near-duplicates.
- Output **only** a JSON array of strings, length exactly N (given in the user message). No markdown fences."""
)

_ORCHESTRATOR_LITE_SYSTEM = SystemMessage(
    content="""You are a retrieval planner. Output **exactly ONE** JSON object (not an array) describing a single next tool call.
Fields:
- "action": must be "call_tool"
- "tool_name": one of
  strategy_semantic_search | strategy_exact_search
- "args": object. Parameter rules:
  - For strategy_semantic_search:
    - Required: "query_intent" string.
    - Use a natural-language retrieval question or phrase that describes the information need.
    - Good for broad conceptual retrieval, method comparisons, dataset/model discovery, or follow-up exploration.
  - For strategy_exact_search:
    - Required: "query_intent" string.
    - Use ONLY a short exact-match expression: preferably one specific proper noun, acronym, method name, model name, dataset name, pollutant name, or paper/entity term.
    - Do NOT use a long sentence for exact search. Bad: "datasets used to model CO2 pollution in cities". Good: "AERMOD", "WRF-Chem", "CO2", "CALPUFF", "traffic census".
- "reason": short English rationale tied to the **track question** (not other tracks).

Continuation rounds: if the user message includes a **previous round search query**, your new "query_intent" must **not** be the same string (nor a trivial paraphrase). Formulate a **follow-up** retrieval phrase that closes gaps, drills into methods/datasets/entities implied by the prior summaries, or pivots to what is still missing for the track question. If using exact search in a continuation round, extract one concise term from the prior summaries or track question.

No markdown, no extra keys, no array wrapper — only one JSON object."""
)

_REFINE_TRACK_SYSTEM = SystemMessage(
    content="""You update one track's working question for the **next** retrieval round (feedback loop).
Input: original user question, current track focus, and what was just retrieved/summarized.
Output **only** JSON: {"track_question": "..."} — one string, English, retrieval-oriented (not a full essay).

Rules:
- Incorporate concrete gaps, methods, dataset names, or sub-problems suggested by the summary/evidence.
- Must **not** be identical to the current track focus; reflect what was learned and what to ask next.
- Stay on the same thematic track as the rest of the session (do not switch to another sub-topic unrelated to this stream).
No markdown."""
)

_STOP_CHECK_SYSTEM = SystemMessage(
    content="""You decide whether further retrieval rounds are still needed globally (legacy).
Given the original user question and short summaries of the latest round per track, respond with **only** JSON:
{"stop": true|false, "rationale": "one short English sentence"}"""
)

_STOP_SINGLE_TRACK_SYSTEM = SystemMessage(
    content="""You decide whether THIS ONE retrieval track needs another round after its latest summaries.
Respond with **only** JSON:
{"stop": true|false, "rationale": "one short English sentence"}
Rules:
- Judge only this track; other tracks are irrelevant.
- If the track still has clear gaps, conflicting evidence, or missing methods/datasets/entities, set stop=false.
- If the track already has enough evidence to answer its sub-question for the overall user goal, set stop=true."""
)

# 已结束轨在后续波次的占位策略名（不写图谱、不参与报告计划列表）
TRACK_INACTIVE_TOOL = "_track_inactive"


async def _llm_json_array_strings(
    client: OpenAIChatCompletionClient, user_text: str, n: int
) -> List[str]:
    msg = UserMessage(
        content=f"N={n}\nOriginal question:\n{user_text}\n\nProduce exactly {n} strings in a JSON array.",
        source="user",
    )
    resp = await model_create_with_retry(
        client,
        messages=[_REWRITE_SYSTEM, msg],
        cancellation_token=None,
        source="MultiAgentRewrite",
    )
    cleaned = resp.content.replace("```json", "").replace("```", "").strip()
    data = json.loads(cleaned)
    if not isinstance(data, list):
        raise ValueError("rewrite response is not a JSON array")
    out = [str(x).strip() for x in data if str(x).strip()]
    if len(out) < n:
        raise ValueError(f"expected {n} rewrites, got {len(out)}")
    return out[:n]


async def _llm_single_plan(
    client: OpenAIChatCompletionClient,
    *,
    root_goal: str,
    track_question: str,
    track_prior_summary: str,
    rag_n: int,
    previous_query_intent: Optional[str] = None,
    round_number: int = 1,
) -> OrchestratorPlan:
    prev_q = (previous_query_intent or "").strip()
    prev_block = ""
    if round_number > 1 and prev_q:
        prev_block = f"""
Previous round search query for THIS track (do not repeat verbatim; plan a complementary follow-up):
{prev_q}
"""
    user = f"""Original user question (context only, do not optimize for other tracks):
{root_goal}

Track question (optimize this step ONLY for this sub-question):
{track_question}
{prev_block}
Prior summaries for THIS track only (may be empty on first round):
{track_prior_summary or "(none yet)"}

Hyperparameter: n_results for semantic/exact tools must be {rag_n}.

Return one JSON object as specified in the system message."""
    resp = await model_create_with_retry(
        client,
        messages=[_ORCHESTRATOR_LITE_SYSTEM, UserMessage(content=user, source="user")],
        cancellation_token=None,
        source="MultiAgentPlan",
    )
    cleaned = resp.content.replace("```json", "").replace("```", "").strip()
    obj = json.loads(cleaned)
    if isinstance(obj, list) and obj:
        obj = obj[0]
    if not isinstance(obj, dict):
        raise ValueError("plan response not a JSON object")
    if obj.get("action") != "call_tool":
        obj["action"] = "call_tool"
    plan = OrchestratorPlan(
        action="call_tool",
        tool_name=str(obj.get("tool_name") or "strategy_semantic_search"),
        args=dict(obj.get("args") or {}),
        reason=str(obj.get("reason") or ""),
        ParentNode=str(obj.get("ParentNode") or "0"),
    )
    plans = apply_rag_result_per_plan_to_plans([plan], rag_n)
    return plans[0]


async def _llm_refine_track_question(
    client: OpenAIChatCompletionClient,
    *,
    root_goal: str,
    track_question: str,
    plansummary: str,
    rag_titles: List[str],
) -> str:
    """根据本轮检索与总结改写轨道子问题，供下一轮作为 track_question。"""
    titles = "\n".join(f"- {t}" for t in (rag_titles or [])[:6] if t)
    body = f"""Original user question:
{root_goal}

Current track focus (refine this, do not copy verbatim):
{track_question}

Latest round retrieval summary (truncated):
{(plansummary or "")[:3500]}

Sample evidence titles (if any):
{titles or "(none)"}
"""
    resp = await model_create_with_retry(
        client,
        messages=[_REFINE_TRACK_SYSTEM, UserMessage(content=body, source="user")],
        cancellation_token=None,
        source="MultiAgentRefineTrack",
    )
    cleaned = resp.content.replace("```json", "").replace("```", "").strip()
    obj = json.loads(cleaned)
    if not isinstance(obj, dict):
        raise ValueError("refine track response not a JSON object")
    nq = str(obj.get("track_question") or "").strip()
    if not nq:
        raise ValueError("empty track_question")
    return nq


def _log_hypothesis_prompt_and_response(agent_name: str, sys_msg: str, user_msg: str, response: str):
    import datetime
    import os
    os.makedirs("logs", exist_ok=True)
    timestamp_day = datetime.datetime.now().strftime("%Y%m%d")
    timestamp_exact = datetime.datetime.now().strftime("%H:%M:%S")
    filename = f"logs/hypothesis_prompts_{timestamp_day}.md"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"## [{timestamp_exact}] {agent_name}\n\n")
        f.write("### System Prompt\n```text\n" + sys_msg + "\n```\n\n")
        f.write("### User Prompt\n```text\n" + user_msg + "\n```\n\n")
        f.write("### LLM Response\n```text\n" + response + "\n```\n\n")
        f.write("---\n\n")

async def _llm_interactive_report_outline(client: OpenAIChatCompletionClient, plan_summaries: List[Dict]) -> List[Dict]:
    _SYS = SystemMessage(
        content="""You are a scientific report architect.
You will be given a list of query strategies and their summaries (each with a plan_id).
Group these strategies logically into a 2-level outline for a scientific review report.
Output ONLY a JSON list, e.g.:
[
  {
    "level1_title": "Broad Theme 1",
    "subsections": [
      {
        "level2_title": "Specific Topic 1",
        "assigned_plan_ids": ["plan_id_1", "plan_id_2"]
      }
    ]
  }
]
Do NOT use markdown fences."""
    )
    plans_text = ""
    for p in plan_summaries:
        plans_text += f"Plan ID: {p['plan_id']}\nStrategy: {p['tool_name']}\nSummary: {p['plansummary']}\n---\n"
    
    msg = UserMessage(content=f"Plan Summaries:\n{plans_text}\nGenerate the 2-level outline JSON array.", source="user")
    resp = await model_create_with_retry(
        client,
        messages=[_SYS, msg],
        cancellation_token=None,
        source="MultiAgentReportOutline"
    )
    
    _log_hypothesis_prompt_and_response("MultiAgentReportOutline", _SYS.content, msg.content, resp.content)
    
    cleaned = resp.content.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return []

async def _llm_interactive_report_section(client: OpenAIChatCompletionClient, title: str, rag_results: List[Dict]) -> str:
    _SYS = SystemMessage(
        content="""You are a scientific writer.
You are given a subsection title and a set of retrieved evidence items (each with a CHUNK_ID).
Write a concise, professional English literature review paragraph (3-6 sentences) synthesizing this evidence.
CRITICAL: You MUST cite the evidence using EXACTLY the format `[CHUNK_ID]` (e.g. `[doc1_chunk4]`) where appropriate.
Output ONLY the paragraph text. No JSON, no markdown formatting."""
    )
    evidence_text = ""
    for item in rag_results:
        chunk_id = item.get("chunk_id", "Unknown_ID")
        content = item.get("content", "")
        evidence_text += f"CHUNK_ID: {chunk_id}\nContent: {content}\n---\n"
        
    msg = UserMessage(content=f"Subsection Title: {title}\n\nEvidence:\n{evidence_text}\n\nWrite the synthesis paragraph with [CHUNK_ID] citations.", source="user")
    resp = await model_create_with_retry(
        client,
        messages=[_SYS, msg],
        cancellation_token=None,
        source="MultiAgentReportSection"
    )
    
    _log_hypothesis_prompt_and_response("MultiAgentReportSection", _SYS.content, msg.content, resp.content)
    
    return resp.content.strip()

async def _llm_interactive_report_synthesis(client: OpenAIChatCompletionClient, root_goal: str, sections_text: str) -> str:
    _SYS = SystemMessage(
        content="""You are a scientific synthesizer.
You are given the user's original question and several written sections based on retrieved evidence.
Integrate these sections into a cohesive final scientific report.
Write a 'Core Hypothesis', 'Evidence Analysis', 'Critical Gaps', and 'Conclusion'.
Maintain all the [CHUNK_ID] citations from the original sections.
Output ONLY the final report text."""
    )
    msg = UserMessage(content=f"Original Question: {root_goal}\n\nSections:\n{sections_text}", source="user")
    resp = await model_create_with_retry(
        client, messages=[_SYS, msg], cancellation_token=None, source="MultiAgentReportSynthesis"
    )
    
    _log_hypothesis_prompt_and_response("MultiAgentReportSynthesis", _SYS.content, msg.content, resp.content)
    
    return resp.content.strip()

async def _llm_should_stop(
    client: OpenAIChatCompletionClient, root_goal: str, summaries: List[str]
) -> bool:
    body = {
        "original_question": root_goal,
        "latest_round_track_summaries": summaries,
    }
    resp = await model_create_with_retry(
        client,
        messages=[
            _STOP_CHECK_SYSTEM,
            UserMessage(content=json.dumps(body, ensure_ascii=False), source="user"),
        ],
        cancellation_token=None,
        source="MultiAgentStop",
    )
    cleaned = resp.content.replace("```json", "").replace("```", "").strip()
    obj = json.loads(cleaned)
    return bool(obj.get("stop"))


async def _llm_should_stop_for_track(
    client: OpenAIChatCompletionClient,
    *,
    root_goal: str,
    track_index_one_based: int,
    latest_summary_snippet: str,
) -> bool:
    """单轨停止判定（与全局 _llm_should_stop 区分）。"""
    body = {
        "original_question": root_goal,
        "track_index": track_index_one_based,
        "latest_round_summary_snippet": (latest_summary_snippet or "")[:1200],
    }
    resp = await model_create_with_retry(
        client,
        messages=[
            _STOP_SINGLE_TRACK_SYSTEM,
            UserMessage(content=json.dumps(body, ensure_ascii=False), source="user"),
        ],
        cancellation_token=None,
        source="MultiAgentStopTrack",
    )
    cleaned = resp.content.replace("```json", "").replace("```", "").strip()
    obj = json.loads(cleaned)
    return bool(obj.get("stop"))


def _stub_inactive_track_query_result(*, wave: int) -> QueryResult:
    return QueryResult(
        orchestrator_plan=OrchestratorPlan(
            action="call_tool",
            tool_name=TRACK_INACTIVE_TOOL,
            ParentNode="0",
            args={"wave": wave},
            reason="Track finished earlier; padded cell for grid alignment.",
        ),
        rag_results=[],
    )


def _last_query_intent_for_track(experiment: ExperimentResult, track_index: int) -> Optional[str]:
    """该轨最近一次真实检索使用的 query_intent（跳过占位格）。"""
    for it in reversed(experiment.iterations or []):
        qrs = it.query_results or []
        if track_index >= len(qrs):
            continue
        qr = qrs[track_index]
        if (qr.orchestrator_plan.tool_name or "") == TRACK_INACTIVE_TOOL:
            continue
        args0 = qr.orchestrator_plan.args if isinstance(qr.orchestrator_plan.args, dict) else {}
        q = str(args0.get("query_intent") or "").strip()
        if q:
            return q
    return None


def _track_prior_text(experiment: ExperimentResult, track_index: int) -> str:
    """仅拼接该 track（query_results 固定下标）在各已完成轮中的 plansummary 摘要。"""
    lines: List[str] = []
    for it in experiment.iterations or []:
        qrs = it.query_results or []
        if track_index >= len(qrs):
            continue
        if (qrs[track_index].orchestrator_plan.tool_name or "") == TRACK_INACTIVE_TOOL:
            continue
        ps = (qrs[track_index].orchestrator_plan.plansummary or "").strip()
        if not ps:
            continue
        if ps.startswith("{"):
            try:
                o = json.loads(ps)
                if isinstance(o, dict):
                    a = str(o.get("answer", ""))[:800]
                    lines.append(f"- round {it.round_number}: {a}")
                    continue
            except Exception:
                pass
        lines.append(f"- round {it.round_number}: {ps[:800]}")
    return "\n".join(lines)


def _merge_rag_into_graph(
    graph: ResearchGraph,
    *,
    round_num: int,
    plan: OrchestratorPlan,
    qr: QueryResult,
) -> None:
    """将单条 QueryResult 写入图谱（与 engine 行为简化对齐，供 graphToRoundsData）。"""
    if (plan.tool_name or "") == TRACK_INACTIVE_TOOL:
        return
    parent = plan.ParentNode or "0"
    if parent in ("ROOT", "", None):
        parent = "0"
    tool = plan.tool_name or "strategy_semantic_search"
    args = plan.args if isinstance(plan.args, dict) else {}
    reason = plan.reason or ""
    rec = NodeSearchRecord(
        round_index=round_num,
        source_tool=tool,
        source_args=args,
        parent_id=str(parent),
    )
    for rag in qr.rag_results or []:
        item = rag.retrieval_result
        ev = rag.evaluation
        if item.id in graph.nodes:
            node = graph.nodes[item.id]
            if node.type == "EVIDENCE":
                node.hit_count += 1
                node.search_history.append(rec)
            continue
        if item.id == "0" and "0" in graph.nodes:
            item.id = str(len(graph.nodes))
        meta = item.metadata if isinstance(getattr(item, "metadata", None), dict) else {}
        if meta:
            if not meta.get("paper_id") and meta.get("paperid"):
                meta["paper_id"] = meta.get("paperid")
            if not meta.get("paperid") and meta.get("paper_id"):
                meta["paperid"] = meta.get("paper_id")
            if not meta.get("chunkid") and isinstance(item.id, str) and item.id.startswith("chunk_"):
                meta["chunkid"] = item.id
            item.metadata = meta
        node = GraphNode(
            id=item.id,
            type="EVIDENCE",
            status="ACTIVE",
            content=item.content,
            metadata=item.metadata,
            ParentNode=str(parent),
            created_at_round=round_num,
            source_tool=tool,
            source_reason=reason,
            source_args=args,
            search_history=[rec],
            evaluation=ev,
        )
        graph.nodes[item.id] = node
        if parent in graph.nodes:
            graph.nodes[parent].children_ids.append(item.id)
        elif parent == "0" and "0" in graph.nodes:
            graph.nodes["0"].children_ids.append(item.id)


def _save_experiment_merged(
    path: str, experiment: ExperimentResult, batch_id: str
) -> None:
    if not path:
        return
    payload = json.loads(experiment.model_dump_json())
    sid = (payload.get("session_id") or "").strip()
    doc: Dict[str, Any] = {"sessions": []}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as rf:
            raw = json.load(rf)
        if isinstance(raw, dict):
            for k, v in raw.items():
                if k == "sessions":
                    continue
                doc[k] = v
            doc["sessions"] = _sessions_list_from_experiment_root(raw)
    if batch_id:
        doc["batch_id"] = batch_id
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
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"\n💾 [MultiAgent] 实验结果已保存: {path}")


def _interactive_report_rag_branch_action(rag: Any) -> str:
    """从 RagResult（Pydantic 或 dict）读取 evaluation.branch_action，归一为大写。"""
    ev = rag.get("evaluation") if isinstance(rag, dict) else getattr(rag, "evaluation", None)
    if not ev:
        return ""
    if isinstance(ev, dict):
        raw = ev.get("branch_action")
    else:
        raw = getattr(ev, "branch_action", None)
    return str(raw or "").strip().upper()


def _interactive_report_rag_allowed_for_section_llm(rag: Any) -> bool:
    """Interactive Report 小节撰写：仅使用 GROW / KEEP，排除 PRUNE、UNKNOWN、无评估等。"""
    return _interactive_report_rag_branch_action(rag) in ("GROW", "KEEP")


async def generate_interactive_report_for_experiment(experiment: ExperimentResult) -> ExperimentResult:
    """给定一个完整的实验记录，重新跑一遍大纲和内容生成。"""
    client = _make_model_client()
    from protocols import HypothesisData, HypothesisStep
    import json
    
    print("\n📝 [MultiAgent] 收集所有 plansummaries 生成交互式报告 (Interactive Report)...")
    
    # 1. 收集 plan_summaries
    all_plans = []
    plan_id_to_rag = {}
    for it in experiment.iterations:
        for qr_idx, qr in enumerate(it.query_results):
            if (qr.orchestrator_plan.tool_name or "") == TRACK_INACTIVE_TOOL:
                continue
            pid = f"round_{it.round_number}_track_{qr_idx}"
            all_plans.append({
                "plan_id": pid,
                "tool_name": qr.orchestrator_plan.tool_name,
                "plansummary": qr.orchestrator_plan.plansummary or ""
            })
            plan_id_to_rag[pid] = qr.rag_results or []
    
    # 2. 生成大纲
    outline_json = await _llm_interactive_report_outline(client, all_plans)
    outline_step = HypothesisStep(
        step_name="Outline",
        prompt="Interactive Report Outline",
        response=json.dumps(outline_json, ensure_ascii=False, indent=2),
        agent_name="MultiAgentReportOutline"
    )
    
    # 3. 按照大纲的二级标题，为每个小标题生成段落
    sections = []
    for l1 in outline_json:
        for l2 in l1.get("subsections", []):
            title = l2.get("level2_title", "Untitled")
            pids = l2.get("assigned_plan_ids", [])
            # 收集 evidence
            rag_results = []
            for pid in pids:
                for rag in plan_id_to_rag.get(pid, []):
                    if not _interactive_report_rag_allowed_for_section_llm(rag):
                        continue
                    ret = getattr(rag, "retrieval_result", {})
                    if isinstance(ret, dict):
                        chunk_id = ret.get("id", "")
                        content = ret.get("content", "")
                    else:
                        chunk_id = getattr(ret, "id", "")
                        content = getattr(ret, "content", "")
                    rag_results.append({"chunk_id": chunk_id, "content": str(content)[:300]})
            
            if rag_results:
                text = await _llm_interactive_report_section(client, title, rag_results)
                plan_ids_meta = (
                    [str(x).strip() for x in pids if str(x).strip()]
                    if isinstance(pids, list)
                    else []
                )
                sections.append(HypothesisStep(
                    step_name=title,
                    prompt="Interactive Report Subsection",
                    response=text,
                    agent_name="MultiAgentReportSection",
                    assigned_plan_ids=plan_ids_meta if plan_ids_meta else None,
                ))
    
    # 4. 生成综合报告 synthesis
    synthesis_step = None
    final_report_text = None
    if sections:
        sections_text = "\n\n".join([f"### {s.step_name}\n{s.response}" for s in sections])
        final_report_text = await _llm_interactive_report_synthesis(client, experiment.root_goal, sections_text)
        synthesis_step = HypothesisStep(
            step_name="Synthesis",
            prompt="Interactive Report Synthesis",
            response=final_report_text,
            agent_name="MultiAgentReportSynthesis"
        )

    experiment.hypothesis = HypothesisData(
        outline=outline_step,
        sections=sections,
        synthesis=synthesis_step,
        final_report=final_report_text
    )
    return experiment

async def run_multi_agent_parallel_rewrite_workflow(
    query: str,
    manager,
    *,
    collection_name: str = "multimodal2text",
    rewrite_variant_count: int = 3,
    rag_result_per_plan: int = 10,
    max_rounds: int = 3,
    rag_allowed_chunk_ids: Optional[List[str]] = None,
    map_box_rect_2d: Optional[List[List[float]]] = None,
    session_id: str = "",
    batch_id: str = "",
    skip_evaluation: bool = False,
    experiment_save_path: Optional[str] = None,
) -> None:
    """
    多路改写 + 独立轨编排入口（由 server.py 在 start_query 中按开关调用）。
    """
    set_active_collection_name(collection_name)
    set_rag_allowed_chunk_ids(rag_allowed_chunk_ids)
    rag_service = await get_rag_service(
        collection_name=collection_name,
        multimodal_collection_name="scientific_rag_multimodal_collection_new",
    )
    client = _make_model_client()
    executor = SingleStrategyExecutor()

    n_variants = max(1, min(10, int(rewrite_variant_count or 3)))
    try:
        rag_n = int(rag_result_per_plan)
    except Exception:
        rag_n = 10
    rag_n = max(1, min(rag_n, 20))
    try:
        max_depth = int(max_rounds)
    except Exception:
        max_depth = 3
    max_depth = max(1, min(max_depth, 10))

    sid = (session_id or "").strip() or str(uuid.uuid4())
    bid = (batch_id or "").strip()
    mb = normalize_map_box_rect_2d(map_box_rect_2d)

    experiment = ExperimentResult(
        root_goal=query,
        session_id=sid,
        use_multi_agent_rewrite_streams=True,
        rewrite_variant_count=n_variants,
    )
    graph = ResearchGraph(
        root_goal=query,
        nodes={
            "0": GraphNode(
                id="0",
                type="ROOT",
                status="ACTIVE",
                content={"goal": query},
            )
        },
    )

    async def _push():
        if manager:
            await manager.broadcast_graph(graph, session_id=sid, follow_up=False)
            await manager.broadcast_experiment_result(
                experiment, session_id=sid, batch_id=bid or None, follow_up=False
            )

    try:
        print(f"\n🧭 [MultiAgent] 改写条数={n_variants}, max_rounds={max_depth}, rag_n={rag_n}")
        try:
            variants = await _llm_json_array_strings(client, query, n_variants)
        except Exception as e:
            print(f"⚠️ [MultiAgent] 改写失败，使用均分兜底: {e}")
            variants = [f"{query} (focus angle {i + 1})" for i in range(n_variants)]

        # 每轨独立：本轨 retrieval 计数、停止标记；iteration 列为「波次」对齐整张表。
        track_stopped = [False] * n_variants
        track_local_round = [0] * n_variants  # 已完成的检索轮数（仅此轨）
        wave = 0

        while True:
            active = [
                ti
                for ti in range(n_variants)
                if (not track_stopped[ti]) and track_local_round[ti] < max_depth
            ]
            if not active:
                break
            wave += 1

            experiment.parameters.append(
                ExperimentRoundParameters(
                    round_number=wave,
                    max_rounds=max_depth,
                    plans_per_round=n_variants,
                    rag_result_per_plan=rag_n,
                    collection_name=collection_name,
                    interactive=False,
                    rag_allowed_chunk_ids=rag_allowed_chunk_ids,
                    map_box_rect_2d=mb,
                    skip_evaluation=bool(skip_evaluation),
                )
            )

            query_results_row: List[QueryResult] = []

            for ti, tq in enumerate(variants):
                if track_stopped[ti] or track_local_round[ti] >= max_depth:
                    query_results_row.append(_stub_inactive_track_query_result(wave=wave))
                    continue

                track_local_round[ti] += 1
                depth = track_local_round[ti]

                prior = _track_prior_text(experiment, ti)
                prev_qi = (
                    _last_query_intent_for_track(experiment, ti) if depth > 1 else None
                )

                try:
                    plan = await _llm_single_plan(
                        client,
                        root_goal=query,
                        track_question=tq,
                        track_prior_summary=prior,
                        rag_n=rag_n,
                        previous_query_intent=prev_qi,
                        round_number=depth,
                    )
                except Exception as e:
                    print(f"⚠️ [MultiAgent] track {ti} plan LLM 失败，用语义默认: {e}")
                    plan = OrchestratorPlan(
                        action="call_tool",
                        tool_name="strategy_semantic_search",
                        args={"query_intent": tq, "n_results": rag_n},
                        reason="fallback after planner parse error",
                        ParentNode="0",
                    )
                plan = apply_rag_result_per_plan_to_plans([plan], rag_n)[0]
                try:
                    plan = plan.model_copy(
                        update={"grid_pos": [int(ti) + 1, int(depth)]}
                    )
                except Exception:
                    pass
                qr = await executor.execute_to_query_result(
                    plan, root_goal=query, skip_evaluation=skip_evaluation
                )
                query_results_row.append(qr)
                _merge_rag_into_graph(
                    graph, round_num=wave, plan=qr.orchestrator_plan, qr=qr
                )
                ps = (qr.orchestrator_plan.plansummary or "")[:400]

                if depth >= max_depth:
                    track_stopped[ti] = True
                    print(
                        f"🛑 [MultiAgent] 轨道 {ti + 1} 已达 max_rounds={max_depth}，停止检索。"
                    )
                else:
                    try:
                        if await _llm_should_stop_for_track(
                            client,
                            root_goal=query,
                            track_index_one_based=ti + 1,
                            latest_summary_snippet=ps,
                        ):
                            track_stopped[ti] = True
                            print(
                                f"🛑 [MultiAgent] 轨道 {ti + 1} LLM 判定信息已足够，提前结束。"
                            )
                    except Exception as e:
                        print(
                            f"⚠️ [MultiAgent] 轨道 {ti + 1} 停止判定失败，将继续: {e}"
                        )

                if (not track_stopped[ti]) and depth < max_depth:
                    titles: List[str] = []
                    for rag_res in qr.rag_results or []:
                        item = rag_res.retrieval_result
                        c = getattr(item, "content", None)
                        if isinstance(c, dict):
                            t = c.get("title") or c.get("text")
                            if isinstance(t, str) and t.strip():
                                titles.append(t.strip()[:200])
                    try:
                        variants[ti] = await _llm_refine_track_question(
                            client,
                            root_goal=query,
                            track_question=tq,
                            plansummary=qr.orchestrator_plan.plansummary or "",
                            rag_titles=titles,
                        )
                    except Exception as e:
                        print(
                            f"⚠️ [MultiAgent] track {ti} 子问题精炼失败，保留本轮 track 文案: {e}"
                        )

            experiment.iterations.append(
                IterationResult(round_number=wave, query_results=query_results_row)
            )
            await _push()
            if experiment_save_path:
                _save_experiment_merged(experiment_save_path, experiment, bid)

        try:
            experiment = await generate_interactive_report_for_experiment(experiment)
            await _push()
            if experiment_save_path:
                _save_experiment_merged(experiment_save_path, experiment, bid)
        except Exception as e:
            print(f"⚠️ [MultiAgent] 交互式报告生成失败: {e}")
            traceback.print_exc()

    except asyncio.CancelledError:
        raise
    except Exception as e:
        print(f"❌ [MultiAgent] 流程异常: {e}")
        print(traceback.format_exc())
    finally:
        set_rag_allowed_chunk_ids(None)
        await rag_service.close()
