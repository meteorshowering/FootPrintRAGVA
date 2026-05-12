"""
【功能】RAG Lens 后端 HTTP/WebSocket 入口：挂载静态资源（paper_md、md-llmvis 图片）、暴露 prompts 读取、启动多轮 RAG 工作流与追问/扩展等 WebSocket 动作。
【长期价值】核心长期维护；部署与路由以本文件为边界。
"""
import uvicorn
import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
# 导入拆分出去的模块
from connection import ConnectionManager
from engine import run_rag_workflow, run_rag_workflow_expand, run_rag_workflow_follow_up, normalize_map_box_rect_2d
from engine_multi_agent import run_multi_agent_parallel_rewrite_workflow
from fastapi.staticfiles import StaticFiles
import os
import re
import shutil
import datetime
import json
from typing import Optional, Dict, List, Any, Tuple
from pydantic import BaseModel, Field
from rag_service import get_rag_service

app = FastAPI()


def _normalize_rag_allowed_chunk_ids(raw: Any) -> Optional[List[str]]:
    """小地图框选 id 列表；空列表视为不限定（返回 None）。"""
    if raw is None:
        return None
    if not isinstance(raw, list):
        return None
    out = [str(x) for x in raw if x is not None and str(x).strip() != ""]
    return out if len(out) > 0 else None

# 2. 配置 CORS：允许所有来源访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源 (localhost:5173 等)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()

# -----------------------------------------------------------------
# 接口定义 (Interface Definition)
# -----------------------------------------------------------------

# ==========================================
# ⚡️ 新增：挂载静态文件目录
# ==========================================
# 实际图片存储在 predataprocess/paper_md 目录下
# ✅ 已修复：自动获取当前目录下的 paper_md（Mac/Windows 通用）
here = os.path.dirname(os.path.abspath(__file__))
# 实验 JSON 统一目录：保存与前端读取均在此（见 /experiment-data 静态挂载与 /api/experiment-files）
_experiment_data_dir = os.path.join(here, "experiment_data")
os.makedirs(_experiment_data_dir, exist_ok=True)
# 与早期行为一致：本进程启动时固定一个 experiment_results_YYYYMMDD_HHMMSS.json，所有会话/追问都写入该文件（按 session 合并）
_logs_dir = os.path.join(here, "logs")
os.makedirs(_logs_dir, exist_ok=True)
SESSION_EXPERIMENT_JSON = os.path.join(
    _experiment_data_dir,
    f"experiment_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
)
try:
    print(f"📁 [Server] 本会话实验结果 JSON: {SESSION_EXPERIMENT_JSON}")
except Exception:
    print(f"[Server] SESSION_EXPERIMENT_JSON={SESSION_EXPERIMENT_JSON}")

image_dir = os.path.join(here, "paper_md")
llmvis_image_dir = os.path.join(here, "md-llmvis", "images")

# 访问 http://127.0.0.1:8000/static/xxx.jpg 就会映射到 本地/predataprocess/paper_md/xxx.jpg
app.mount("/static", StaticFiles(directory=image_dir), name="static")
app.mount("/static-llmvis", StaticFiles(directory=llmvis_image_dir), name="static_llmvis")
app.mount(
    "/experiment-data",
    StaticFiles(directory=_experiment_data_dir),
    name="experiment_data",
)

# ==========================================
# ⚡️ 新增：给前端展示智能体 prompts
# ==========================================
def _extract_system_prompt_from_engine_py(engine_py_text: str, anchor: str) -> Optional[str]:
    """
    从 engine.py 文本中提取某个 anchor 后面的 SystemMessage(content=\"\"\"...\"\"\") 文本块。
    anchor: 用于定位提取起点的字符串（例如 'self.system_message = SystemMessage(content=\"\"\"'）。
    """
    idx = engine_py_text.find(anchor)
    if idx == -1:
        return None
    start = idx + len(anchor)
    end = engine_py_text.find('"""', start)
    if end == -1:
        return None
    return engine_py_text[start:end]


def _load_agent_prompts() -> Dict[str, str]:
    here = os.path.dirname(os.path.abspath(__file__))
    engine_py = os.path.join(here, "engine.py")
    try:
        with open(engine_py, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        return {"plan_prompt": "", "evaluate_prompt": "", "error": str(e)}

    plan_anchor = 'self.system_message = SystemMessage(content="""'
    eval_anchor = 'class EvaluatorAgent'  # 用类名做二次定位，避免拿到别的 system_message

    # 1) Plan prompt：取 Orchestrator 初始化里的第一段 system_message
    plan_prompt = _extract_system_prompt_from_engine_py(text, plan_anchor) or ""

    # 2) Evaluate prompt：先定位到 EvaluatorAgent，再从该位置向后找 system_message
    eval_pos = text.find(eval_anchor)
    evaluate_prompt = ""
    if eval_pos != -1:
        sub = text[eval_pos:]
        evaluate_prompt = _extract_system_prompt_from_engine_py(sub, plan_anchor) or ""

    return {"plan_prompt": plan_prompt.strip(), "evaluate_prompt": evaluate_prompt.strip()}


@app.get("/api/agent-prompts")
async def get_agent_prompts():
    """
    给前端展示：Plan / Evaluate 两个智能体的 system prompt。
    """
    return _load_agent_prompts()

# ==========================================
# 实验结果 JSON：统一目录 experiment_data（列表 + 静态读取 + 默认保存）
# ==========================================
def _get_experiment_data_dir() -> str:
    """ToRAGLENSBack/experiment_data：与 SESSION_EXPERIMENT_JSON、fork 落盘同目录。"""
    return os.path.abspath(_experiment_data_dir)


def _get_frontend_public_dir() -> str:
    """
    返回 mapfront/public（仅作 fork/旧文件兼容查找，新实验请放在 experiment_data）。
    """
    return os.path.abspath(os.path.join(here, "..", "mapfront", "public"))


def _parse_experiment_ts(path_str: str):
    """
    从 experiment_results_YYYYMMDD_HHMMSS.json 提取排序用的时间戳键。
    如果没有匹配到则返回 None。
    """
    m = re.search(r"experiment[^/\\\\]*?(\\d{8})_(\\d{6})\\.json$", path_str)
    if not m:
        return None
    return m.group(1) + m.group(2)


@app.get("/api/experiment-files")
async def list_experiment_files():
    """
    返回 experiment_data 目录下所有 experiment*.json（递归），相对该目录的路径，使用 / 分隔。
    前端请用 `GET /experiment-data/<相对路径>` 读取（开发环境经 vue 代理到本服务）。
    """
    exp_dir = _get_experiment_data_dir()
    files = []
    try:
        for root, _, filenames in os.walk(exp_dir):
            for fn in filenames:
                if not fn.lower().endswith(".json"):
                    continue
                if not fn.lower().startswith("experiment"):
                    continue
                abs_path = os.path.join(root, fn)
                rel_path = os.path.relpath(abs_path, exp_dir).replace("\\", "/")
                files.append(rel_path)
    except Exception as e:
        return {
            "experiment_data_dir": exp_dir,
            "files": [],
            "error": str(e),
        }

    # 按时间戳倒序；未匹配到时间戳的放后面
    def sort_key(p: str):
        ts = _parse_experiment_ts(p)
        return (0, ts) if ts else (1, p)

    files.sort(key=sort_key, reverse=True)
    return {
        "experiment_data_dir": exp_dir,
        "files": files,
    }


def _experiment_read_allowed_roots() -> List[Path]:
    """允许通过 API 读取实验 JSON 的根目录（与 fork 源解析一致）。"""
    return [
        Path(_get_experiment_data_dir()).resolve(),
        Path(_get_frontend_public_dir()).resolve(),
        Path(_logs_dir).resolve(),
    ]


def _path_is_under_allowed_roots(abs_file: str, roots: List[Path]) -> bool:
    try:
        p = Path(abs_file).resolve()
    except OSError:
        return False
    for root in roots:
        try:
            p.relative_to(root)
            return True
        except ValueError:
            continue
    return False


@app.get("/api/experiment-file")
async def read_experiment_file(
    path: str = Query(
        ...,
        min_length=1,
        description="相对 experiment_data 的路径，或仅 basename；在 experiment_data、mapfront/public、logs 中解析",
    ),
):
    """
    以 JSON 文件形式返回实验数据。与 /experiment-data 静态挂载等价，但走 /api 代理更稳（仅配了 /api 的部署也能用），
    且与 fork 使用相同的 `_resolve_fork_source_abs` 查找顺序。
    """
    rel = (path or "").strip().replace("\\", "/")
    if ".." in rel or rel.startswith("/"):
        raise HTTPException(status_code=400, detail="invalid path")
    bn = os.path.basename(rel)
    if not bn.lower().endswith(".json") or not bn.lower().startswith("experiment"):
        raise HTTPException(status_code=400, detail="invalid path")
    abs_path = _resolve_fork_source_abs(rel)
    if not abs_path:
        raise HTTPException(status_code=404, detail="not found")
    roots = _experiment_read_allowed_roots()
    if not _path_is_under_allowed_roots(abs_path, roots):
        raise HTTPException(status_code=403, detail="forbidden")
    return FileResponse(
        abs_path,
        media_type="application/json",
        filename=os.path.basename(abs_path),
    )


class LlmChatMessage(BaseModel):
    role: str = Field(default="user")  # user | assistant
    content: str = Field(default="")


class LlmChatRequest(BaseModel):
    messages: List[LlmChatMessage] = Field(default_factory=list)


@app.post("/api/llm-chat")
async def api_llm_chat(payload: LlmChatRequest):
    """
    简单对话接口：使用 engine_multi_agent 同款模型配置生成回复。
    前端传入最近若干轮 messages（role/content），后端返回一条 assistant reply。
    """
    try:
        from autogen_core.models import SystemMessage, UserMessage
        from engine_multi_agent import _make_model_client
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"import failed: {e}")

    msgs = payload.messages or []
    msgs = msgs[-16:]

    parts: List[str] = []
    for m in msgs:
        role = (m.role or "").strip().lower()
        if role not in ("user", "assistant"):
            role = "user"
        who = "User" if role == "user" else "Assistant"
        content = (m.content or "").strip()
        if not content:
            continue
        parts.append(f"{who}: {content}")

    prompt = "\n".join(parts).strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="empty messages")

    sys = SystemMessage(
        content="You are a helpful assistant inside a research/RAG visualization tool. Be concise and concrete."
    )
    user = UserMessage(content=prompt + "\nAssistant:", source="user")
    client = _make_model_client()
    try:
        # 这里是独立对话功能：不复用 engine.py 的 model_create_with_retry（避免写入 workflow 日志/污染编排状态）。
        # 简单实现一个本地的退避重试即可。
        last_exc: Optional[BaseException] = None
        for attempt in range(5):
            try:
                resp = await client.create(messages=[sys, user], cancellation_token=None)
                break
            except BaseException as e:
                last_exc = e
                if attempt >= 4:
                    raise
                await asyncio.sleep(min(24.0, 1.6 * (2**attempt)))
        else:
            if last_exc is not None:
                raise last_exc
            raise RuntimeError("llm-chat: no attempt executed")
        reply = (getattr(resp, "content", None) or "").strip()
        return {"ok": True, "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"llm call failed: {e}")


def _user_ops_centroid_item_to_rag_result_row(
    item: Dict[str, Any], *, source_tool: str, source_args: Dict[str, Any]
) -> Dict[str, Any]:
    """将 rag_service._format_results 单条转为与 experiment JSON 中 rag_results[] 同构。"""
    md = item.get("metadata")
    if not isinstance(md, dict):
        md = {}
    content = item.get("content")
    if not isinstance(content, dict):
        content = {"text": str(content or "")}
    return {
        "retrieval_result": {
            "id": str(item.get("id", "")),
            "source_tool": source_tool,
            "content": content,
            "metadata": md,
            "score": float(item.get("score") or 0.0),
            "source_args": source_args if isinstance(source_args, dict) else {},
        },
        "evaluation": None,
    }


@app.post("/api/rag-neighbors-from-centroid")
async def rag_neighbors_from_centroid(payload: Dict[str, Any]):
    """
    User Operations：由若干 chunk 的嵌入质心在向量库中检索近邻（排除已出现的 chunk_id），
    返回与 experiment JSON 中 rag_results 项同构的列表（retrieval_result + evaluation:null）。

    请求体：points[{chunk_id, action}]（必填）；collection_name（可选，可与实验 JSON 交叉校验）；
    experiment_source_path + round_number（可选）：若提供且能解析到 JSON，则优先使用该文件中
    parameters 里与 round_number 对齐的 collection_name，与落盘实验一致。
    另有 centroid_actions（默认 [\"GROW\"]）, target_count（默认 10）。
    """
    collection_name = str(payload.get("collection_name") or "").strip()
    exp_path = str(
        payload.get("experiment_source_path")
        or payload.get("experiment_file")
        or payload.get("source_path")
        or ""
    ).strip()
    exp_rn = payload.get("round_number")
    if exp_path and exp_rn is not None:
        resolved_cn = _collection_name_from_experiment_json_round(exp_path, exp_rn)
        if resolved_cn:
            collection_name = resolved_cn
    if not collection_name:
        raise HTTPException(
            status_code=400,
            detail="missing collection_name (provide collection_name or experiment_source_path+round_number)",
        )
    points = payload.get("points")
    if not isinstance(points, list) or len(points) == 0:
        raise HTTPException(status_code=400, detail="points must be a non-empty list")

    raw_actions = payload.get("centroid_actions")
    if not isinstance(raw_actions, list) or not raw_actions:
        raw_actions = ["GROW"]
    centroid_actions = {str(x).strip().upper() for x in raw_actions if str(x).strip()}
    if not centroid_actions:
        centroid_actions = {"GROW"}

    try:
        target_n = int(payload.get("target_count") or 10)
    except Exception:
        target_n = 10
    target_n = max(1, min(50, target_n))

    norm_points: List[Dict[str, str]] = []
    for p in points:
        if not isinstance(p, dict):
            continue
        cid = p.get("chunk_id")
        if cid is None:
            cid = p.get("id")
        if cid is None or str(cid).strip() == "":
            continue
        act = str(p.get("action") or "UNKNOWN").strip().upper()
        norm_points.append({"chunk_id": str(cid).strip(), "action": act})
    if not norm_points:
        raise HTTPException(status_code=400, detail="no valid chunk_id in points")

    seed_ids = [p["chunk_id"] for p in norm_points if p["action"] in centroid_actions]
    if not seed_ids:
        raise HTTPException(
            status_code=400,
            detail=f"no points with action in {sorted(centroid_actions)}",
        )

    all_ids = [p["chunk_id"] for p in norm_points]

    try:
        service = await get_rag_service(collection_name=collection_name, multimodal_collection_name=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"rag service: {e}") from e

    if service.raw_collection is None:
        raise HTTPException(status_code=503, detail=f"collection not available: {collection_name}")

    items = await service.neighbors_from_centroid_excluding(seed_ids, all_ids, out_n=target_n)
    source_tool = "UserOps(CentroidNeighbors)"
    source_args: Dict[str, Any] = {
        "centroid_seed_chunk_ids": seed_ids,
        "centroid_actions": sorted(centroid_actions),
        "exclude_chunk_ids": all_ids,
        "collection_name": collection_name,
    }
    rows = [
        _user_ops_centroid_item_to_rag_result_row(it, source_tool=source_tool, source_args=source_args)
        for it in items
    ]
    return {"ok": True, "rag_results": rows, "found": len(rows), "collection_name_used": collection_name}


@app.post("/api/experiment-rag-actions-batch")
async def update_experiment_rag_actions_batch(payload: Dict[str, Any]):
    """
    批量保存前端用户操作：
    - delete / point：针对 rag_result（与既有逻辑一致）
    - plan_continue / plan_regenerate：写入对应 query_results[query_index].orchestrator_plan.userdo（策略卡 C/R）
    - plan_strategy_delete：标记策略删除 grid_pos=[0,0]、写入 userdo.strategy_delete，压低同行后续 grid_pos[1]，并将后续策略挪至 round_number=grid_pos[1] 对应列后与前端一致的顺序落盘（repack）
    """
    source_rel = str(payload.get("source_path") or payload.get("fork_experiment_source") or "").strip()
    if not source_rel:
        raise HTTPException(status_code=400, detail="missing source_path")
    dest_path = _ensure_fork_experiment_save_path(source_rel)
    if not dest_path:
        raise HTTPException(status_code=404, detail="source experiment not found")

    operations = payload.get("operations")
    if not isinstance(operations, list):
        raise HTTPException(status_code=400, detail="operations must be a list")

    session_id = str(payload.get("session_id") or "").strip()

    try:
        with open(dest_path, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"read failed: {e}")

    def _is_strategy_plan_tombstone(qr: Dict[str, Any]) -> bool:
        op = qr.get("orchestrator_plan") if isinstance(qr.get("orchestrator_plan"), dict) else {}
        gp = op.get("grid_pos")
        if not isinstance(gp, list) or len(gp) < 2:
            return False
        try:
            return int(gp[0]) == 0 and int(gp[1]) == 0
        except Exception:
            return False

    def _resolve_plan_grid_row_col(qr: Dict[str, Any], it_rn: int, j: int) -> Tuple[int, int]:
        row = int(j) + 1
        col = int(it_rn)
        op = qr.get("orchestrator_plan") if isinstance(qr.get("orchestrator_plan"), dict) else {}
        gp = op.get("grid_pos")
        if isinstance(gp, list) and len(gp) >= 1:
            try:
                r0 = int(gp[0])
                if r0 >= 1:
                    row = r0
            except Exception:
                pass
        if isinstance(gp, list) and len(gp) >= 2:
            try:
                c0 = int(gp[1])
                if c0 >= 1:
                    col = c0
            except Exception:
                pass
        return row, col

    def _iter_session_docs(doc: Any) -> List[Dict[str, Any]]:
        if isinstance(doc, dict) and isinstance(doc.get("sessions"), list):
            return [s for s in doc.get("sessions") if isinstance(s, dict)]
        return [doc] if isinstance(doc, dict) else []

    def _repack_iteration_query_results_by_grid_row(it: Dict[str, Any]) -> None:
        qrs = it.get("query_results")
        if not isinstance(qrs, list):
            return

        def _row_sort_key(qr: Any) -> Tuple[int, float]:
            if not isinstance(qr, dict):
                return (1, 1e6)
            tomb = _is_strategy_plan_tombstone(qr)
            op = qr.get("orchestrator_plan") or {}
            gp = op.get("grid_pos")
            rr = 1e6
            if isinstance(gp, list) and len(gp) >= 1:
                try:
                    r0 = int(gp[0])
                    if r0 >= 1:
                        rr = float(r0)
                except Exception:
                    pass
            return (1 if tomb else 0, rr)

        it["query_results"] = sorted(qrs, key=_row_sort_key)

    def _migrate_qr_to_grid_column_rounds(sess: Dict[str, Any]) -> None:
        iterations = sess.get("iterations")
        if not isinstance(iterations, list):
            return
        by_rn: Dict[int, Dict[str, Any]] = {}
        for it in iterations:
            if not isinstance(it, dict):
                continue
            try:
                rnk = int(it.get("round_number"))
            except Exception:
                continue
            by_rn[rnk] = it

        pending: List[Tuple[Any, Dict[str, Any], int]] = []
        for it in iterations:
            if not isinstance(it, dict):
                continue
            try:
                hrs = int(it.get("round_number"))
            except Exception:
                continue
            qrs = it.get("query_results")
            if not isinstance(qrs, list):
                continue
            for qr in qrs:
                if not isinstance(qr, dict) or _is_strategy_plan_tombstone(qr):
                    continue
                op = qr.get("orchestrator_plan") or {}
                gp = op.get("grid_pos")
                desired = hrs
                if isinstance(gp, list) and len(gp) >= 2:
                    try:
                        c0 = int(gp[1])
                        if c0 >= 1:
                            desired = c0
                    except Exception:
                        pass
                if desired != hrs:
                    pending.append((qr, it, desired))

        for qr, from_it, to_col in pending:
            dest_it = by_rn.get(int(to_col))
            if dest_it is None or dest_it is from_it:
                continue
            from_qrs = from_it.get("query_results")
            if not isinstance(from_qrs, list):
                continue
            from_it["query_results"] = [x for x in from_qrs if x is not qr]
            dest_qrs = dest_it.get("query_results")
            if not isinstance(dest_qrs, list):
                dest_qrs = []
            dest_qrs.append(qr)
            dest_it["query_results"] = dest_qrs

        for it in iterations:
            if isinstance(it, dict):
                _repack_iteration_query_results_by_grid_row(it)

    matched_any = False
    for op_item in operations:
        action = str(op_item.get("action") or "").strip().lower()

        # 策略卡 userdo：Continue / Regenerate（不依赖 rag_result id）
        if action in ("plan_continue", "plan_regenerate"):
            try:
                rn = int(op_item.get("round_number"))
                qi = int(op_item.get("query_index"))
            except Exception:
                continue
            sid_op = str(op_item.get("session_id") or session_id or "").strip()
            now_ts = op_item.get("timestamp") or datetime.datetime.now().isoformat(timespec="seconds")

            for sess in _iter_session_docs(doc):
                if sid_op and str(sess.get("session_id") or "").strip() != sid_op:
                    continue
                for it in sess.get("iterations") or []:
                    try:
                        it_rn = int(it.get("round_number"))
                    except Exception:
                        continue
                    if it_rn != rn:
                        continue
                    qrs = it.get("query_results") or []
                    if not isinstance(qrs, list) or qi < 0 or qi >= len(qrs):
                        continue
                    qr = qrs[qi]
                    op_plan = qr.get("orchestrator_plan") or {}
                    if not isinstance(op_plan, dict):
                        op_plan = {}
                    userdo = op_plan.get("userdo")
                    if not isinstance(userdo, dict):
                        userdo = {}

                    if action == "plan_continue":
                        new_text = str(op_item.get("new") or "").strip()
                        if not new_text:
                            continue
                        cont = userdo.get("continue")
                        if not isinstance(cont, list):
                            cont = []
                        cont.append(
                            {
                                "action": "continue",
                                "new": new_text,
                                "timestamp": now_ts,
                            }
                        )
                        userdo["continue"] = cont
                    else:
                        before_text = str(op_item.get("before") or "").strip()
                        if not before_text:
                            continue
                        reg = userdo.get("regenerate")
                        if not isinstance(reg, list):
                            reg = []
                        reg.append(
                            {
                                "action": "regenerate",
                                "before": before_text,
                                "timestamp": now_ts,
                            }
                        )
                        userdo["regenerate"] = reg

                    op_plan["userdo"] = userdo
                    qr["orchestrator_plan"] = op_plan
                    matched_any = True
            continue

        if action == "plan_strategy_delete":
            try:
                rn = int(op_item.get("round_number"))
                qi = int(op_item.get("query_index"))
            except Exception:
                continue
            sid_op = str(op_item.get("session_id") or session_id or "").strip()
            now_ts = op_item.get("timestamp") or datetime.datetime.now().isoformat(timespec="seconds")

            for sess in _iter_session_docs(doc):
                if sid_op and str(sess.get("session_id") or "").strip() != sid_op:
                    continue

                target_qr: Any = None
                for it in sess.get("iterations") or []:
                    try:
                        it_rn = int(it.get("round_number"))
                    except Exception:
                        continue
                    if it_rn != rn:
                        continue
                    qrs = it.get("query_results") or []
                    if not isinstance(qrs, list) or qi < 0 or qi >= len(qrs):
                        continue
                    cand = qrs[qi]
                    if isinstance(cand, dict):
                        target_qr = cand
                    break

                if not isinstance(target_qr, dict) or _is_strategy_plan_tombstone(target_qr):
                    continue

                del_row, del_col = _resolve_plan_grid_row_col(target_qr, rn, qi)

                for it2 in sess.get("iterations") or []:
                    try:
                        it2_rn = int(it2.get("round_number"))
                    except Exception:
                        continue
                    qrs2 = it2.get("query_results") or []
                    if not isinstance(qrs2, list):
                        continue
                    for j, qr2 in enumerate(qrs2):
                        if qr2 is target_qr or not isinstance(qr2, dict):
                            continue
                        if _is_strategy_plan_tombstone(qr2):
                            continue
                        r2, c2 = _resolve_plan_grid_row_col(qr2, it2_rn, j)
                        if r2 == del_row and c2 > del_col:
                            op2 = qr2.get("orchestrator_plan")
                            if not isinstance(op2, dict):
                                op2 = {}
                            op2["grid_pos"] = [r2, c2 - 1]
                            qr2["orchestrator_plan"] = op2

                op_t = target_qr.get("orchestrator_plan")
                if not isinstance(op_t, dict):
                    op_t = {}
                userdo_t = op_t.get("userdo")
                if not isinstance(userdo_t, dict):
                    userdo_t = {}
                strat_del = userdo_t.get("strategy_delete")
                if not isinstance(strat_del, list):
                    strat_del = []
                strat_del.append({"action": "delete", "timestamp": now_ts})
                userdo_t["strategy_delete"] = strat_del
                op_t["userdo"] = userdo_t
                op_t["grid_pos"] = [0, 0]
                target_qr["orchestrator_plan"] = op_t
                _migrate_qr_to_grid_column_rounds(sess)
                matched_any = True
            continue

        if action not in ("delete", "point"):
            continue
        result_id = str(op_item.get("target_evidence_id") or op_item.get("result_id") or "").strip()
        if not result_id:
            continue

        for sess in _iter_session_docs(doc):
            if session_id and str(sess.get("session_id") or "").strip() != session_id:
                continue

            target: Any = None
            qr: Any = None
            for it in sess.get("iterations") or []:
                if not isinstance(it, dict):
                    continue
                for q in it.get("query_results") or []:
                    if not isinstance(q, dict):
                        continue
                    for rag in q.get("rag_results") or []:
                        if not isinstance(rag, dict):
                            continue
                        rr = rag.get("retrieval_result") or {}
                        if str(rr.get("id") or "").strip() == result_id:
                            target = rag
                            qr = q
                            break
                    if target is not None:
                        break
                if target is not None:
                    break

            if target is None and action == "point":
                rr_snap = op_item.get("retrieval_result")
                if not isinstance(rr_snap, dict) or str(rr_snap.get("id") or "").strip() != result_id:
                    continue
                try:
                    qi_op = int(op_item.get("query_index"))
                    rn_op = int(op_item.get("round_number"))
                except Exception:
                    continue
                for it in sess.get("iterations") or []:
                    if not isinstance(it, dict):
                        continue
                    try:
                        if int(it.get("round_number")) != rn_op:
                            continue
                    except Exception:
                        continue
                    qrs = it.get("query_results") or []
                    if not isinstance(qrs, list) or qi_op < 0 or qi_op >= len(qrs):
                        continue
                    qx = qrs[qi_op]
                    if not isinstance(qx, dict):
                        continue
                    qr = qx
                    rags = qr.get("rag_results")
                    if not isinstance(rags, list):
                        rags = []
                        qr["rag_results"] = rags
                    # 质心近邻首次并入策略：evaluation 仅保留 branch_action
                    ev_new: Dict[str, Any] = {"branch_action": op_item.get("after")}
                    try:
                        rr_copy = json.loads(json.dumps(rr_snap, ensure_ascii=False))
                    except Exception:
                        rr_copy = dict(rr_snap)
                    new_rag = {"retrieval_result": rr_copy, "evaluation": ev_new}
                    rags.append(new_rag)
                    target = new_rag
                    break

            if target is None or qr is None or not isinstance(qr, dict):
                continue

            op_plan = qr.get("orchestrator_plan") or {}
            if not isinstance(op_plan, dict):
                op_plan = {}
            userdo = op_plan.get("userdo")
            if not isinstance(userdo, dict):
                userdo = {}

            if action == "delete":
                deletes = userdo.get("delete", [])
                if not isinstance(deletes, list):
                    deletes = []
                if not any(str(x.get("target_evidence_id") or "") == result_id for x in deletes if isinstance(x, dict)):
                    deletes.append(
                        {
                            "action": "delete",
                            "target_evidence_id": result_id,
                            "timestamp": op_item.get("timestamp")
                            or datetime.datetime.now().isoformat(timespec="seconds"),
                        }
                    )
                userdo["delete"] = deletes

                ev = target.get("evaluation")
                if not isinstance(ev, dict):
                    ev = {"target_evidence_id": result_id, "scores": {}, "suggested_keywords": []}
                ev["branch_action"] = "PRUNE"
                ev["reason"] = "User deleted this evidence item."
                ev["user_action"] = "delete"
                target["evaluation"] = ev

            elif action == "point":
                points = userdo.get("point", [])
                if not isinstance(points, list):
                    points = []
                existing = next(
                    (
                        x
                        for x in points
                        if isinstance(x, dict) and str(x.get("target_evidence_id") or "") == result_id
                    ),
                    None,
                )
                if existing:
                    existing["after"] = op_item.get("after")
                    existing.pop("timestamp", None)
                else:
                    points.append(
                        {
                            "action": "point",
                            "target_evidence_id": result_id,
                            "before": op_item.get("before"),
                            "after": op_item.get("after"),
                        }
                    )
                userdo["point"] = points

                ev = target.get("evaluation")
                if not isinstance(ev, dict):
                    ev = {"target_evidence_id": result_id, "scores": {}, "suggested_keywords": []}
                ev["branch_action"] = op_item.get("after")
                ev["user_action"] = "point"
                target["evaluation"] = ev

                # 仅质心近邻首次纳入评分类别：原检索结果已在 rerank_after_ids，不必改
                if str(op_item.get("before") or "").strip().lower() == "neighbor":
                    ra = op_plan.get("rerank_after_ids")
                    if not isinstance(ra, list):
                        ra = []
                    ra_ids = [str(x).strip() for x in ra if x is not None and str(x).strip()]
                    if result_id not in ra_ids:
                        ra_ids.append(result_id)
                    op_plan["rerank_after_ids"] = ra_ids

            op_plan["userdo"] = userdo
            qr["orchestrator_plan"] = op_plan
            matched_any = True

    try:
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"write failed: {e}")

    rel_out = os.path.relpath(dest_path, _experiment_data_dir).replace("\\", "/")
    return {"ok": True, "path": rel_out, "matched": matched_any}


@app.post("/api/experiment-remove-strategy")
async def experiment_remove_strategy(payload: Dict[str, Any]):
    """
    从某会话的某一迭代中移除一条 query_results（策略卡片），落盘至 fork JSON；同行后续策略 index 自然前移。
    """
    source_rel = str(payload.get("source_path") or payload.get("fork_experiment_source") or "").strip()
    if not source_rel:
        raise HTTPException(status_code=400, detail="missing source_path")
    dest_path = _ensure_fork_experiment_save_path(source_rel)
    if not dest_path:
        raise HTTPException(status_code=404, detail="source experiment not found")

    session_id = str(payload.get("session_id") or "").strip()
    try:
        round_number = int(payload.get("round_number"))
    except Exception:
        raise HTTPException(status_code=400, detail="invalid round_number")
    try:
        query_index = int(payload.get("query_index"))
    except Exception:
        raise HTTPException(status_code=400, detail="invalid query_index")

    try:
        with open(dest_path, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"read failed: {e}")

    target_sessions: List[Dict[str, Any]] = []
    if isinstance(doc, dict) and isinstance(doc.get("sessions"), list) and len(doc["sessions"]) > 0:
        if not session_id:
            raise HTTPException(status_code=400, detail="multi-session document requires session_id")
        for s in doc["sessions"]:
            if isinstance(s, dict) and str(s.get("session_id") or "").strip() == session_id:
                target_sessions.append(s)
        if not target_sessions:
            raise HTTPException(status_code=404, detail="session not found")
    elif isinstance(doc, dict):
        doc_sid = str(doc.get("session_id") or "").strip()
        if session_id and doc_sid and doc_sid != session_id:
            raise HTTPException(status_code=404, detail="session not found")
        target_sessions = [doc]
    else:
        raise HTTPException(status_code=400, detail="invalid document")

    removed = False
    for sess in target_sessions:
        for it in sess.get("iterations") or []:
            try:
                rn = int(it.get("round_number"))
            except Exception:
                continue
            if rn != round_number:
                continue
            qrs = it.get("query_results")
            if not isinstance(qrs, list):
                qrs = []
            if query_index < 0 or query_index >= len(qrs):
                raise HTTPException(status_code=400, detail="query_index out of range")
            qrs.pop(query_index)
            it["query_results"] = qrs
            removed = True
            break
        if removed:
            break

    if not removed:
        raise HTTPException(status_code=404, detail="round not found")

    try:
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"write failed: {e}")

    rel_out = os.path.relpath(dest_path, _experiment_data_dir).replace("\\", "/")
    return {"ok": True, "path": rel_out}


@app.post("/api/experiment-rag-action")
async def update_experiment_rag_action(payload: Dict[str, Any]):
    """
    保存前端对单个 rag_result 的用户操作。
    当前仅支持 delete：不物理删除 rag_result，而是在 orchestrator_plan.userdo.delete 中记录，
    并把对应 evaluation.branch_action 标为 PRUNE，保证实验 JSON 可追溯。
    """
    action = str(payload.get("action") or "").strip().lower()
    if action != "delete":
        raise HTTPException(status_code=400, detail="unsupported action")

    source_rel = str(
        payload.get("source_path")
        or payload.get("fork_experiment_source")
        or ""
    ).strip()
    if not source_rel:
        raise HTTPException(status_code=400, detail="missing source_path")
    dest_path = _ensure_fork_experiment_save_path(source_rel)
    if not dest_path:
        raise HTTPException(status_code=404, detail="source experiment not found")

    result_id = str(payload.get("result_id") or "").strip()
    if not result_id:
        raise HTTPException(status_code=400, detail="missing result_id")
    session_id = str(payload.get("session_id") or "").strip()
    round_number_raw = payload.get("round_number")
    try:
        round_number = int(round_number_raw)
    except Exception:
        round_number = None
    plan_tool = str(payload.get("plan_tool") or "").strip()
    plan_args = payload.get("plan_args") if isinstance(payload.get("plan_args"), dict) else None

    def _same_args(a: Any, b: Any) -> bool:
        try:
            return json.dumps(a or {}, sort_keys=True, ensure_ascii=False) == json.dumps(
                b or {}, sort_keys=True, ensure_ascii=False
            )
        except Exception:
            return False

    def _iter_session_docs(doc: Any) -> List[Dict[str, Any]]:
        if isinstance(doc, dict) and isinstance(doc.get("sessions"), list):
            return [s for s in doc.get("sessions") if isinstance(s, dict)]
        return [doc] if isinstance(doc, dict) else []

    try:
        with open(dest_path, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"read failed: {e}")

    matched = False
    now = datetime.datetime.now().isoformat(timespec="seconds")
    for sess in _iter_session_docs(doc):
        if session_id and str(sess.get("session_id") or "").strip() != session_id:
            continue
        for it in sess.get("iterations") or []:
            if round_number is not None and int(it.get("round_number", -999999)) != round_number:
                continue
            for qr in it.get("query_results") or []:
                op = qr.get("orchestrator_plan") or {}
                if plan_tool and str(op.get("tool_name") or "") != plan_tool:
                    continue
                if plan_args is not None and not _same_args(op.get("args") or {}, plan_args):
                    continue
                target = None
                for rag in qr.get("rag_results") or []:
                    rr = rag.get("retrieval_result") or {}
                    if str(rr.get("id") or "").strip() == result_id:
                        target = rag
                        break
                if target is None:
                    continue

                userdo = op.get("userdo")
                if not isinstance(userdo, dict):
                    userdo = {}
                deletes = userdo.get("delete")
                if not isinstance(deletes, list):
                    deletes = []
                if not any(str(x.get("target_evidence_id") or "") == result_id for x in deletes if isinstance(x, dict)):
                    deletes.append({
                        "action": "delete",
                        "target_evidence_id": result_id,
                        "timestamp": now,
                    })
                userdo["delete"] = deletes
                op["userdo"] = userdo
                qr["orchestrator_plan"] = op

                ev = target.get("evaluation")
                if not isinstance(ev, dict):
                    ev = {
                        "target_evidence_id": result_id,
                        "branch_action": "PRUNE",
                        "extracted_insight": "",
                        "scores": {},
                        "reason": "User deleted this evidence item.",
                        "suggested_keywords": [],
                    }
                else:
                    ev["target_evidence_id"] = ev.get("target_evidence_id") or result_id
                    ev["branch_action"] = "PRUNE"
                    ev["reason"] = ev.get("reason") or "User deleted this evidence item."
                ev["user_action"] = "delete"
                target["evaluation"] = ev
                matched = True

    if not matched:
        raise HTTPException(status_code=404, detail="target rag_result not found")

    try:
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"write failed: {e}")

    rel_out = os.path.relpath(dest_path, _experiment_data_dir).replace("\\", "/")
    return {"ok": True, "path": rel_out}


@app.post("/api/generate-interactive-report")
async def api_generate_interactive_report(payload: Dict[str, Any], background_tasks: BackgroundTasks):
    source_rel = str(payload.get("source_path") or "").strip()
    if not source_rel:
        raise HTTPException(status_code=400, detail="missing source_path")
        
    dest_path = _ensure_fork_experiment_save_path(source_rel)
    if not dest_path:
        dest_path = _resolve_fork_source_abs(source_rel)
        if not dest_path:
            raise HTTPException(status_code=404, detail="source experiment not found")
            
    session_id = str(payload.get("session_id") or "").strip()
    
    try:
        with open(dest_path, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"read failed: {e}")

    from engine_multi_agent import generate_interactive_report_for_experiment
    from protocols import ExperimentResult
    
    # Check if doc has sessions or is single session
    is_batch = isinstance(doc, dict) and "sessions" in doc
    sessions = doc.get("sessions", []) if is_batch else [doc]
    
    target_session = None
    target_idx = -1
    for i, sess in enumerate(sessions):
        if not session_id or str(sess.get("session_id") or "") == session_id:
            target_session = sess
            target_idx = i
            break
            
    if not target_session:
        raise HTTPException(status_code=404, detail="session not found")
        
    async def process_report():
        try:
            exp_model = ExperimentResult.model_validate(target_session)
            exp_model = await generate_interactive_report_for_experiment(exp_model)
            updated_sess = exp_model.model_dump(mode="json")
            
            if is_batch:
                doc["sessions"][target_idx] = updated_sess
            else:
                doc.update(updated_sess)
                
            with open(dest_path, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)
                
            print(f"✅ Interactive report generated and saved to {dest_path}")
            
            # Broadcast update
            if manager:
                await manager.broadcast_experiment_result(
                    exp_model,
                    session_id=exp_model.session_id,
                    batch_id=doc.get("batch_id") if is_batch else None,
                    follow_up=False
                )
        except Exception as e:
            print(f"❌ Failed to generate interactive report: {e}")
            import traceback
            traceback.print_exc()

    background_tasks.add_task(process_report)
    return {"ok": True, "message": "Generation started in background"}


def _fork_dest_basename(source_rel: str) -> Optional[str]:
    """由源 JSON 相对路径得到 experiment_data 下保存文件名：原名 + _user2（若尚未带此后缀）。"""
    rel = (source_rel or "").strip().replace("\\", "/")
    if ".." in rel or rel.startswith("/"):
        return None
    bn = os.path.basename(rel)
    if not re.match(r"^experiment.+\.json$", bn, re.I):
        return None
    stem, ext = os.path.splitext(bn)
    if ext.lower() != ".json":
        return None
    if stem.lower().endswith("_user2"):
        return bn
    return f"{stem}_user2{ext}"


def _resolve_fork_source_abs(source_rel: str) -> Optional[str]:
    """优先 experiment_data，其次兼容 mapfront/public、logs 下的旧路径。"""
    exp_dir = _get_experiment_data_dir()
    public_dir = _get_frontend_public_dir()
    rel = (source_rel or "").strip().replace("\\", "/")
    candidates: List[str] = []
    if rel and ".." not in rel:
        candidates.append(os.path.normpath(os.path.join(exp_dir, rel.replace("/", os.sep))))
        candidates.append(os.path.normpath(os.path.join(public_dir, rel.replace("/", os.sep))))
    bn = os.path.basename(rel) if rel else ""
    if bn:
        candidates.append(os.path.join(exp_dir, bn))
        candidates.append(os.path.join(public_dir, bn))
        candidates.append(os.path.join(_logs_dir, bn))
    seen: set = set()
    for p in candidates:
        ap = os.path.abspath(p)
        if ap in seen:
            continue
        seen.add(ap)
        if os.path.isfile(ap):
            return ap
    return None


def _collection_name_from_experiment_json_round(source_rel: str, round_number: Any) -> Optional[str]:
    """从实验 JSON 的 parameters 中读取与 round_number 对齐的 collection_name（与落盘结构一致）。"""
    abs_path = _resolve_fork_source_abs(str(source_rel or "").strip().replace("\\", "/"))
    if not abs_path:
        return None
    roots = _experiment_read_allowed_roots()
    if not _path_is_under_allowed_roots(abs_path, roots):
        return None
    try:
        rn = int(round_number)
    except Exception:
        return None
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except Exception:
        return None

    def _from_parameters(params: Any) -> Optional[str]:
        if not isinstance(params, list):
            return None
        for row in params:
            if not isinstance(row, dict):
                continue
            try:
                if int(row.get("round_number")) == rn:
                    cn = row.get("collection_name")
                    if cn is not None and str(cn).strip():
                        return str(cn).strip()
            except Exception:
                continue
        return None

    sess_docs: List[Dict[str, Any]] = []
    if isinstance(doc, dict) and isinstance(doc.get("sessions"), list):
        sess_docs = [s for s in doc.get("sessions") if isinstance(s, dict)]
    elif isinstance(doc, dict):
        sess_docs = [doc]
    for sess in sess_docs:
        hit = _from_parameters(sess.get("parameters"))
        if hit:
            return hit
    return None


def _ensure_fork_experiment_save_path(source_rel: str) -> Optional[str]:
    """
    将源文件复制到 experiment_data/<stem>_user2.json（若目标尚不存在），后续追问/新开会话均合并写入该文件。
    找不到源文件时返回 None，由调用方回退到默认 SESSION_EXPERIMENT_JSON。
    """
    dest_bn = _fork_dest_basename(source_rel)
    if not dest_bn:
        return None
    dest = os.path.abspath(os.path.join(_experiment_data_dir, dest_bn))
    if os.path.isfile(dest):
        return dest
    src = _resolve_fork_source_abs(source_rel)
    if not src:
        try:
            print(f"⚠️ [Server] fork_experiment_source 未找到文件: {source_rel!r}，回退默认保存路径")
        except Exception:
            pass
        return None
    try:
        shutil.copy2(src, dest)
        print(f"📋 [Server] 本地实验 fork 已就绪，保存至: {dest}")
    except Exception as e:
        try:
            print(f"❌ [Server] 复制 fork 实验文件失败: {e}")
        except Exception:
            pass
        return None
    return dest


def _experiment_save_path_for_ws(ws_data: Dict[str, Any]) -> str:
    fork = str(ws_data.get("fork_experiment_source") or "").strip()
    if fork:
        p = _ensure_fork_experiment_save_path(fork)
        if p:
            return p
    return SESSION_EXPERIMENT_JSON


# 添加一个兼容路由，防止前端连接 /ws 时出错
@app.websocket("/ws")
async def websocket_endpoint_legacy(websocket: WebSocket):
    """兼容旧的前端连接 /ws 的情况"""
    print(f"⚠️ [Server] 收到旧路径连接请求: {websocket.url.path}，请使用 /ws/rag-tree")
    await websocket.close(code=1008, reason="Please use /ws/rag-tree endpoint")

@app.websocket("/ws/rag-tree")
async def websocket_endpoint(websocket: WebSocket):
    # 1. 建立连接
    print(f"🌐 [Server] WebSocket 连接请求: {websocket.url.path}")
    await manager.connect(websocket)
    print(f"✅ [Server] WebSocket 连接已建立，当前连接数: {len(manager.active_connections)}")
    
    try:
        while True:
            # 2. 监听前端消息
            data = await websocket.receive_json()
            print(f"🌍 [Server] 收到指令: {data}")
            
            # 3. 路由分发
            if data.get("action") == "start_query":
                query = data.get("query")
                collection_name = data.get("collection_name", "multimodal2text")
                plans_per_round = data.get("plans_per_round", 2)
                rag_result_per_plan = data.get("rag_result_per_plan", 10)
                max_rounds = data.get("max_rounds", 3)
                interactive = data.get("interactive", False)
                rag_allowed_chunk_ids = _normalize_rag_allowed_chunk_ids(data.get("rag_allowed_chunk_ids"))
                map_box_rect_2d = normalize_map_box_rect_2d(data.get("map_box_rect_2d"))
                session_id = str(data.get("session_id") or "").strip()
                batch_id = str(data.get("batch_id") or "").strip()
                skip_evaluation = bool(data.get("skip_evaluation", False))
                use_multi_agent_streams = bool(data.get("use_multi_agent_rewrite_streams", False))
                try:
                    plans_per_round = int(plans_per_round)
                except Exception:
                    plans_per_round = 2
                rewrite_variant_count = data.get("rewrite_variant_count", plans_per_round)
                try:
                    rewrite_variant_count = int(rewrite_variant_count)
                except Exception:
                    rewrite_variant_count = plans_per_round
                rewrite_variant_count = max(1, min(10, rewrite_variant_count))
                try:
                    rag_result_per_plan = int(rag_result_per_plan)
                except Exception:
                    rag_result_per_plan = 10
                try:
                    max_rounds = int(max_rounds)
                except Exception:
                    max_rounds = 3
                if query:
                    import uuid
                    from engine import InteractivePauseGate

                    run_id = str(uuid.uuid4())
                    pause_gate = None
                    if interactive and not use_multi_agent_streams:
                        pause_gate = InteractivePauseGate()
                        manager.register_pause_gate(run_id, pause_gate)
                    
                    _save_path = _experiment_save_path_for_ws(data)
                    # 4. 调用编排：默认主 engine；可选多路改写实验流（engine_multi_agent，不改 engine.py）
                    if use_multi_agent_streams:
                        if interactive:
                            print("⚠️ [Server] 多路改写模式暂不支持交互审批，已忽略 interactive")
                        asyncio.create_task(
                            run_multi_agent_parallel_rewrite_workflow(
                                query,
                                manager,
                                collection_name=collection_name,
                                rewrite_variant_count=rewrite_variant_count,
                                rag_result_per_plan=rag_result_per_plan,
                                max_rounds=max_rounds,
                                rag_allowed_chunk_ids=rag_allowed_chunk_ids,
                                map_box_rect_2d=map_box_rect_2d,
                                session_id=session_id,
                                batch_id=batch_id,
                                skip_evaluation=skip_evaluation,
                                experiment_save_path=_save_path,
                            )
                        )
                    else:
                        asyncio.create_task(
                            run_rag_workflow(
                                query,
                                manager,
                                    collection_name=collection_name,
                                plans_per_round=plans_per_round,
                                rag_result_per_plan=rag_result_per_plan,
                                    max_rounds=max_rounds,
                                    interactive_mode=interactive,
                                    run_id=run_id,
                                    pause_gate=pause_gate,
                                    rag_allowed_chunk_ids=rag_allowed_chunk_ids,
                                    map_box_rect_2d=map_box_rect_2d,
                                    session_id=session_id,
                                    batch_id=batch_id,
                                    skip_evaluation=skip_evaluation,
                                    experiment_save_path=_save_path,
                                    use_multi_agent_rewrite_streams=False,
                                    rewrite_variant_count=rewrite_variant_count,
                                )
                            )
            elif data.get("action") == "interactive_response":
                # 前端返回了审批决策
                run_id = data.get("run_id")
                checkpoint_id = data.get("checkpoint_id")
                decision_data = {
                    "decision": data.get("decision", "abort"),
                    "plans": data.get("plans", [])
                }
                pause_gate = manager.get_pause_gate(run_id)
                if pause_gate:
                    pause_gate.resolve_checkpoint(checkpoint_id, decision_data)
                else:
                    print(f"⚠️ [Server] 找不到 run_id: {run_id} 对应的 PauseGate")
            elif data.get("action") == "follow_up":
                # 追问：只做一次检索 + 评估，round_number 为「新一行」迭代（通常 max+1）；会话字段用于前端合并
                query = data.get("query")
                collection_name = data.get("collection_name", "multimodal2text")
                parent_node_id = data.get("parent_node_id", "0")
                round_number = data.get("round_number", 0)
                rag_result_per_plan = data.get("rag_result_per_plan", 10)
                rag_allowed_chunk_ids = _normalize_rag_allowed_chunk_ids(data.get("rag_allowed_chunk_ids"))
                map_box_rect_2d = normalize_map_box_rect_2d(data.get("map_box_rect_2d"))
                skip_evaluation = bool(data.get("skip_evaluation", False))
                session_id_fu = (data.get("session_id") or "").strip()
                batch_id_fu = (data.get("batch_id") or "").strip()
                root_goal_fu = (data.get("root_goal") or "").strip()
                rewrite_mode = bool(data.get("rewrite_mode", False))
                rewrite_target_query_index = data.get("rewrite_target_query_index", None)
                grid_row = data.get("grid_row", None)
                continue_context = data.get("continue_context", None)
                try:
                    round_number = int(round_number)
                except Exception:
                    round_number = 0
                try:
                    rag_result_per_plan = int(rag_result_per_plan)
                except Exception:
                    rag_result_per_plan = 10
                if query:
                    _save_path_fu = _experiment_save_path_for_ws(data)
                    follow_up_tool = str(data.get("follow_up_tool") or "strategy_semantic_search").strip()
                    asyncio.create_task(
                        run_rag_workflow_follow_up(
                            query=str(query),
                            manager=manager,
                            collection_name=collection_name,
                            parent_node_id=str(parent_node_id or "0"),
                            round_number=round_number,
                            rag_result_per_plan=rag_result_per_plan,
                            rag_allowed_chunk_ids=rag_allowed_chunk_ids,
                            map_box_rect_2d=map_box_rect_2d,
                            skip_evaluation=skip_evaluation,
                            session_id=session_id_fu,
                            batch_id=batch_id_fu,
                            root_goal=root_goal_fu,
                            experiment_save_path=_save_path_fu,
                            follow_up_tool=follow_up_tool,
                            rewrite_mode=rewrite_mode,
                            rewrite_target_query_index=rewrite_target_query_index,
                            grid_row=grid_row,
                            continue_context=continue_context,
                        )
                    )
            elif data.get("type") == "expand_search":
                # 处理卡片扩展检索请求
                parent_node_id = data.get("parent_node_id")
                search_type = data.get("search_type")
                search_query = data.get("search_query")
                collection_name = data.get("collection_name", "multimodal2text")
                
                if parent_node_id and search_type and search_query:
                    # 创建一个新的工作流实例处理扩展检索
                    _save_path_ex = _experiment_save_path_for_ws(data)
                    asyncio.create_task(run_rag_workflow_expand(
                        parent_node_id=parent_node_id,
                        search_type=search_type,
                        search_query=search_query,
                        manager=manager,
                        collection_name=collection_name,
                        experiment_save_path=_save_path_ex,
                    ))
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("🔴 [Server] 客户端断开")
    except Exception as e:
        print(f"❌ [Server] Socket 异常: {e}")

# -----------------------------------------------------------------
# 启动入口
# -----------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)