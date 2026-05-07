"""
【功能】多路改写 + 独立追问轨（实验性）：与主 engine.py 并行，不修改 engine 源码。
流程：用户问题 → LLM 生成 N 条相关且不重复的改写 → 每条改写独立多轮、每轮仅 1 个策略（1 行多格）→
达到 max_rounds 或 LLM 判定可结束时停止；经 WebSocket 推送 graph / experiment_result 与主流程一致。
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
        base_url="http://38.147.105.35:3030/v1",
        api_key="sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5",
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
    content="""You decide whether further retrieval rounds are still needed.
Given the original user question and short summaries of the latest round per track, respond with **only** JSON:
{"stop": true|false, "rationale": "one short English sentence"}"""
)


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


def _track_prior_text(experiment: ExperimentResult, track_index: int) -> str:
    """仅拼接该 track（query_results 固定下标）在各已完成轮中的 plansummary 摘要。"""
    lines: List[str] = []
    for it in experiment.iterations or []:
        qrs = it.query_results or []
        if track_index >= len(qrs):
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

        track_summaries_last: List[str] = []

        for depth in range(1, max_depth + 1):
            experiment.parameters.append(
                ExperimentRoundParameters(
                    round_number=depth,
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

            query_results: List[QueryResult] = []
            track_summaries_last = []

            for ti, tq in enumerate(variants):
                prior = _track_prior_text(experiment, ti)
                prev_qi: Optional[str] = None
                if depth > 1 and experiment.iterations:
                    prev_it = experiment.iterations[-1]
                    pqrs = prev_it.query_results or []
                    if ti < len(pqrs):
                        args0 = pqrs[ti].orchestrator_plan.args or {}
                        if isinstance(args0, dict):
                            prev_qi = str(args0.get("query_intent") or "").strip() or None
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
                qr = await executor.execute_to_query_result(
                    plan, root_goal=query, skip_evaluation=skip_evaluation
                )
                query_results.append(qr)
                _merge_rag_into_graph(graph, round_num=depth, plan=qr.orchestrator_plan, qr=qr)
                ps = (qr.orchestrator_plan.plansummary or "")[:400]
                track_summaries_last.append(f"Track {ti + 1}: {ps}")
                if depth < max_depth:
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
                        print(f"⚠️ [MultiAgent] track {ti} 子问题精炼失败，保留本轮 track 文案: {e}")

            experiment.iterations.append(
                IterationResult(round_number=depth, query_results=query_results)
            )
            await _push()
            if experiment_save_path:
                _save_experiment_merged(experiment_save_path, experiment, bid)

            if depth >= max_depth:
                break
            try:
                if await _llm_should_stop(client, query, track_summaries_last):
                    print("🛑 [MultiAgent] LLM 判定信息已足够，提前结束。")
                    break
            except Exception as e:
                print(f"⚠️ [MultiAgent] 停止判定失败，继续下一轮: {e}")

    except asyncio.CancelledError:
        raise
    except Exception as e:
        print(f"❌ [MultiAgent] 流程异常: {e}")
        print(traceback.format_exc())
    finally:
        set_rag_allowed_chunk_ids(None)
        await rag_service.close()
