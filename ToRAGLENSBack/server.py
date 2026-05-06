"""
【功能】RAG Lens 后端 HTTP/WebSocket 入口：挂载静态资源（paper_md、md-llmvis 图片）、暴露 prompts 读取、启动多轮 RAG 工作流与追问/扩展等 WebSocket 动作。
【长期价值】核心长期维护；部署与路由以本文件为边界。
"""
import uvicorn
import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
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
from typing import Optional, Dict, List, Any

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