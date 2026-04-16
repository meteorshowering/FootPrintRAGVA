"""
【功能】RAG Lens 后端 HTTP/WebSocket 入口：挂载静态资源（paper_md、md-llmvis 图片）、暴露 prompts 读取、启动多轮 RAG 工作流与追问/扩展等 WebSocket 动作。
【长期价值】核心长期维护；部署与路由以本文件为边界。
"""
import uvicorn
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
# 导入拆分出去的模块
from connection import ConnectionManager
from engine import run_rag_workflow, run_rag_workflow_expand, run_rag_workflow_follow_up
from fastapi.staticfiles import StaticFiles
import os
import re
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
image_dir = os.path.join(here, "paper_md")
llmvis_image_dir = os.path.join(here, "md-llmvis", "images")

# 访问 http://127.0.0.1:8000/static/xxx.jpg 就会映射到 本地/predataprocess/paper_md/xxx.jpg
app.mount("/static", StaticFiles(directory=image_dir), name="static")
app.mount("/static-llmvis", StaticFiles(directory=llmvis_image_dir), name="static_llmvis")

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
# ⚡️ 新增：列出前端 public 下的 experiment*.json
# ==========================================
def _get_frontend_public_dir() -> str:
    """
    返回 mapfront/public 的绝对路径。
    约定 server.py 位于 backandfront/ToRAGLENSBack/ 下。
    """
    here = os.path.dirname(os.path.abspath(__file__))
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
    返回前端 public 目录下所有 experiment*.json 文件（递归）。
    结果为相对 public 的路径（使用 / 分隔），可直接被前端用 `fetch('/<path>')` 读取。
    """
    public_dir = _get_frontend_public_dir()
    files = []
    try:
        for root, _, filenames in os.walk(public_dir):
            for fn in filenames:
                if not fn.lower().endswith(".json"):
                    continue
                if not fn.lower().startswith("experiment"):
                    continue
                abs_path = os.path.join(root, fn)
                rel_path = os.path.relpath(abs_path, public_dir).replace("\\", "/")
                files.append(rel_path)
    except Exception as e:
        return {"public_dir": public_dir, "files": [], "error": str(e)}

    # 按时间戳倒序；未匹配到时间戳的放后面
    def sort_key(p: str):
        ts = _parse_experiment_ts(p)
        return (0, ts) if ts else (1, p)

    files.sort(key=sort_key, reverse=True)
    return {"public_dir": public_dir, "files": files}

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
                plans_per_round = data.get("plans_per_round", 3)
                rag_result_per_plan = data.get("rag_result_per_plan", 10)
                max_rounds = data.get("max_rounds", 7)
                interactive = data.get("interactive", False)
                rag_allowed_chunk_ids = _normalize_rag_allowed_chunk_ids(data.get("rag_allowed_chunk_ids"))
                try:
                    plans_per_round = int(plans_per_round)
                except Exception:
                    plans_per_round = 3
                try:
                    rag_result_per_plan = int(rag_result_per_plan)
                except Exception:
                    rag_result_per_plan = 10
                try:
                    max_rounds = int(max_rounds)
                except Exception:
                    max_rounds = 7
                if query:
                    import uuid
                    from engine import InteractivePauseGate
                    
                    run_id = str(uuid.uuid4())
                    pause_gate = InteractivePauseGate() if interactive else None
                    
                    if interactive:
                        manager.register_pause_gate(run_id, pause_gate)
                    
                    # 4. 调用 Engine (异步任务)
                    # 关键点：把 manager 传进去，让 engine 内部可以发消息回来
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
                # 追问：只做一次检索 + 评估，把结果放到前端指定的 round_number（通常是最后一轮）
                query = data.get("query")
                collection_name = data.get("collection_name", "multimodal2text")
                parent_node_id = data.get("parent_node_id", "0")
                round_number = data.get("round_number", 0)
                rag_result_per_plan = data.get("rag_result_per_plan", 10)
                rag_allowed_chunk_ids = _normalize_rag_allowed_chunk_ids(data.get("rag_allowed_chunk_ids"))
                try:
                    round_number = int(round_number)
                except Exception:
                    round_number = 0
                try:
                    rag_result_per_plan = int(rag_result_per_plan)
                except Exception:
                    rag_result_per_plan = 10
                if query:
                    asyncio.create_task(
                        run_rag_workflow_follow_up(
                            query=str(query),
                            manager=manager,
                            collection_name=collection_name,
                            parent_node_id=str(parent_node_id or "0"),
                            round_number=round_number,
                            rag_result_per_plan=rag_result_per_plan,
                            rag_allowed_chunk_ids=rag_allowed_chunk_ids,
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
                    asyncio.create_task(run_rag_workflow_expand(
                        parent_node_id=parent_node_id,
                        search_type=search_type,
                        search_query=search_query,
                        manager=manager,
                        collection_name=collection_name
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