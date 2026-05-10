"""
【功能】高层 RAG 服务：封装 Chroma 语义查询、多模态检索、结果格式化、与 figures 坐标 JSON 联动；为 scientific_tools 与实验管线提供统一入口。
【长期价值】核心长期维护。
"""
import re
import contextvars
from typing import List, Dict, Any, Optional, Union, Tuple
import asyncio
import os
import json

# 尝试导入PIL和torch，但不强制要求
PIL_AVAILABLE = False
torch_AVAILABLE = False
CLIP_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    print("[Warning] PIL库未安装，将无法处理图片")

try:
    import torch
    torch_AVAILABLE = True
except ImportError:
    print("[Warning] torch库未安装，将无法使用CLIP模型")

try:
    from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig
    from autogen_core.memory import MemoryContent, MemoryMimeType
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    import chromadb 
    
    # 只有当PIL和torch都可用时，才尝试导入CLIP相关库
    if PIL_AVAILABLE and torch_AVAILABLE:
        try:
            from transformers import CLIPProcessor, CLIPModel
            CLIP_AVAILABLE = True
        except ImportError as e:
            print(f"[Warning] CLIP模型导入失败: {e}，将无法使用多模态检索功能")
    else:
        print("[Warning] PIL或torch库未安装，将无法使用CLIP模型")
except ImportError as e:
    print(f"[RAGService Error] 核心依赖库导入失败: {e}")
    exit()

# 导入集合管理器
from rag_collection_manager import get_rag_collection_manager
from rag_llm_api_config import (
    env_flag,
    get_rag_llm_api_settings,
    semantic_chroma_pool_size,
    semantic_vector_threshold,
)

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    aiohttp = None  # type: ignore
    AIOHTTP_AVAILABLE = False

# 与 asyncio.Task 绑定的语义检索 trace，避免同一 RAGService 上并发 plan 互相覆盖
_semantic_pipeline_trace_cv: contextvars.ContextVar[Optional[Dict[str, Any]]] = contextvars.ContextVar(
    "_semantic_pipeline_trace_cv", default=None
)


def consume_semantic_pipeline_trace() -> Optional[Dict[str, Any]]:
    """由 ToolExecutor 在同一次 await 工具链结束后读取并清空，供写回 OrchestratorPlan。"""
    try:
        cur = _semantic_pipeline_trace_cv.get()
    except LookupError:
        return None
    _semantic_pipeline_trace_cv.set(None)
    return cur


def _log_rag_semantic_pipeline_to_run_md(payload: Dict[str, Any]) -> None:
    """
    将 HyDE / Rerank 追踪写入 engine 的 logs/run_*.md（与编排日志同文件）。
    使用惰性 import，避免 rag_service 与 engine 顶层循环依赖。
    """
    try:
        from engine import logger  # noqa: WPS433 (runtime import)

        detail = json.dumps(payload, ensure_ascii=False, indent=2)
        uq = payload.get("user_query") or ""
        summary = (
            f"HyDE_used={payload.get('hyde_used_hypothetical_paragraph')} "
            f"rerank_applied={payload.get('rerank_applied_to_results')} "
            f"user_query_len={len(uq)}"
        )
        logger.log("RAGSemantic", summary, "RAG_PIPELINE", detail_data=detail)
    except Exception as e:
        print(f"[RAG] 无法写入 run.md（HyDE/Rerank 追踪）: {e}")


async def _openai_chat_completion_text(
    messages: List[Dict[str, str]],
    *,
    model: str,
    temperature: float = 0.35,
    max_tokens: int = 512,
) -> str:
    if not AIOHTTP_AVAILABLE:
        raise RuntimeError("aiohttp 未安装，无法调用 HyDE")
    cfg = get_rag_llm_api_settings()
    url = cfg.chat_completions_url()
    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    timeout = aiohttp.ClientTimeout(total=120)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            text_body = await resp.text()
            if resp.status != 200:
                raise RuntimeError(f"chat/completions HTTP {resp.status}: {text_body[:500]}")
            data = json.loads(text_body)
    choices = data.get("choices") or []
    if not choices:
        return ""
    msg = choices[0].get("message") or {}
    content = msg.get("content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, dict) and p.get("text"):
                parts.append(str(p["text"]))
            elif isinstance(p, str):
                parts.append(p)
        return "\n".join(parts).strip()
    return str(content or "").strip()


async def _hyde_hypothetical_paragraph(user_query: str) -> Optional[str]:
    """HyDE：生成与短查询对齐的假想学术段落，用于向量检索。"""
    q = (user_query or "").strip()
    if len(q) < 3:
        return None
    cfg = get_rag_llm_api_settings()
    system = (
        "You help scientific literature retrieval. Write ONE short paragraph (3–6 sentences) "
        "that could appear in a research paper and that directly addresses the user's topic. "
        "Use precise technical terms. Output only the paragraph: no title, no quotes, no preamble."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Topic / question:\n{q}"},
    ]
    try:
        hypo = await _openai_chat_completion_text(
            messages,
            model=cfg.hyde_model,
            temperature=0.35,
            max_tokens=480,
        )
        if len(hypo) < 24:
            return None
        return hypo[:6000]
    except Exception as e:
        print(f"⚠️ [HyDE] 生成失败，将使用原查询检索: {e}")
        return None


def _item_to_rerank_document_text(item: Dict[str, Any]) -> str:
    c = item.get("content") if isinstance(item.get("content"), dict) else {}
    parts: List[str] = []
    for k in ("title", "summary", "insight", "text"):
        v = c.get(k) if isinstance(c, dict) else None
        if v:
            parts.append(str(v))
    if not parts:
        try:
            return json.dumps(c, ensure_ascii=False)[:8000]
        except Exception:
            return str(item.get("content", ""))[:8000]
    return "\n".join(parts)[:8000]


def _parse_rerank_response(data: Any) -> List[tuple]:
    """解析常见 rerank JSON：results[{index, relevance_score|score}] 或 data 同结构。"""
    rows: List[tuple] = []
    if not isinstance(data, dict):
        return rows
    blob = data.get("results") or data.get("data") or data.get("output") or []
    if isinstance(blob, dict) and "results" in blob:
        blob = blob["results"]
    if not isinstance(blob, list):
        return rows
    for entry in blob:
        if not isinstance(entry, dict):
            continue
        idx = entry.get("index")
        if idx is None:
            continue
        try:
            idx = int(idx)
        except (TypeError, ValueError):
            continue
        sc = entry.get("relevance_score")
        if sc is None:
            sc = entry.get("score")
        try:
            sc = float(sc)
        except (TypeError, ValueError):
            sc = 0.0
        rows.append((idx, sc))
    rows.sort(key=lambda x: -x[1])
    return rows


async def _rerank_semantic_items(
    original_query: str,
    items: List[Dict[str, Any]],
    top_n: int,
) -> List[Dict[str, Any]]:
    """调用 rerank API，按相关性重排并截断为 top_n。"""
    if not items or top_n <= 0:
        return items
    if not AIOHTTP_AVAILABLE:
        print("⚠️ [Rerank] aiohttp 未安装，跳过重排")
        return items[:top_n]
    cfg = get_rag_llm_api_settings()
    documents = [_item_to_rerank_document_text(it) for it in items]
    payload = {
        "model": cfg.rerank_model,
        "query": original_query.strip(),
        "documents": documents,
    }
    headers = {
        "Authorization": f"Bearer {cfg.rerank_api_key}",
        "Content-Type": "application/json",
    }
    try:
        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(cfg.rerank_url, headers=headers, json=payload) as resp:
                body = await resp.text()
                if resp.status != 200:
                    print(f"⚠️ [Rerank] HTTP {resp.status}: {body[:400]}")
                    return items[:top_n]
                data = json.loads(body)
    except Exception as e:
        print(f"⚠️ [Rerank] 请求失败，保持向量顺序: {e}")
        return items[:top_n]

    order = _parse_rerank_response(data)
    if not order:
        print("⚠️ [Rerank] 响应中无有效排序，保持向量顺序")
        return items[:top_n]

    ranked: List[Dict[str, Any]] = []
    seen: set = set()
    for idx, sc in order:
        if 0 <= idx < len(items):
            it = dict(items[idx])
            it["score"] = float(sc)
            iid = str(it.get("id", idx))
            if iid in seen:
                continue
            seen.add(iid)
            ranked.append(it)
            if len(ranked) >= top_n:
                break
    if len(ranked) < top_n:
        for it in items:
            iid = str(it.get("id", ""))
            if iid in seen:
                continue
            ranked.append(dict(it))
            seen.add(iid)
            if len(ranked) >= top_n:
                break
    return ranked[:top_n]


class RAGService:
    def __init__(self, collection_name: str = None, multimodal_collection_name: str = None):
        self.rag_memory: Optional[ChromaDBVectorMemory] = None
        # ✨ 新增：多模态内存数据库
        self.multimodal_memory: Optional[ChromaDBVectorMemory] = None
        self.chroma_client = None
        self.raw_collection = None 
        # ✨ 新增：多模态原始集合
        self.multimodal_collection = None
        self.model_client = None
        self.initialized = False
        self.figures_file_path = None
        self.db_persistence_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".chromadb_autogen")
        # ✨ 支持传入自定义集合名称，默认为论文RAG集合
        self.collection_name = "multimodal2text"
        # ✨ 新增：多模态集合名称，支持自定义
        self.multimodal_collection_name = multimodal_collection_name or "scientific_rag_multimodal_collection_new"
        
        # ✨ 新增：本地数据缓存 (直接存 JSON 对象)
        self.local_data_cache: List[Dict[str, Any]] = []
        # 供 single_strategy 等在 consume_semantic_pipeline_trace 之外读取最近一次语义 trace（同实例并发语义检索时仍可能竞态，主流程以 ContextVar 为准）
        self._last_semantic_pipeline_trace: Optional[Dict[str, Any]] = None
    
    async def initialize(self, figures_file_path: Optional[str] = None, collection_name: str = None, multimodal_collection_name: str = None, reset_data: bool = False):
        if self.initialized: return
        
        # 如果传入了集合名称，使用传入的集合名称
        if collection_name:
            self.collection_name = collection_name
        if multimodal_collection_name:
            self.multimodal_collection_name = multimodal_collection_name
        
        # 1. 设置路径
        if self.collection_name == "LLMvisDataset":
            default_json = "LLMvisDataset_embedding.json"
        else:
            default_json = "multimodal2text_embeddings_2d.json"
            
        self.figures_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), default_json)
        if figures_file_path:
            self.figures_file_path = figures_file_path

        # 2. ✨ 总是加载本地 JSON 到内存 (用于右路搜索)
        if os.path.exists(self.figures_file_path):
            try:
                with open(self.figures_file_path, "r", encoding="utf-8") as f:
                    self.local_data_cache = json.load(f)
                print(f"📦 [Cache] 已将 {len(self.local_data_cache)} 条数据加载到内存缓存。")
            except Exception as e:
                print(f"❌ [Cache] 读取本地 JSON 失败: {e}")

        # 3. 获取集合管理器
        self.collection_manager = await get_rag_collection_manager()
        
        # 4. 初始化文本rag的集合
        print("🔍 初始化文本集合...")
        # 只尝试获取现有集合，不创建新集合
        collection_exists = await self.collection_manager.check_collection_exists(self.collection_name)
        if collection_exists:
            self.raw_collection = await self.collection_manager.get_collection(self.collection_name)
            print(f"   使用集合: {self.collection_name}，当前记录数: {self.raw_collection.count()}")
        else:
            print(f"   集合 {self.collection_name} 不存在，请先使用 rag_collection_manager.py 创建集合")
            # 设置为 None，后续操作会检查
            self.raw_collection = None
        
        # 5. 创建RAG内存实例
        if self.raw_collection:
            self.rag_memory = await self.collection_manager.create_rag_memory(self.collection_name)
        
        # 6. ✨ 新增：初始化多模态内存数据库
        print("🔍 初始化多模态集合...")
        # 只尝试获取现有集合，不创建新集合
        multimodal_exists = await self.collection_manager.check_collection_exists(self.multimodal_collection_name)
        if multimodal_exists:
            self.multimodal_collection = await self.collection_manager.get_collection(self.multimodal_collection_name)
            print(f"   使用多模态集合: {self.multimodal_collection_name}，当前记录数: {self.multimodal_collection.count()}")
        else:
            print(f"   集合 {self.multimodal_collection_name} 不存在，请先使用 rag_collection_manager.py 创建集合")
            # 设置为 None，后续操作会检查
            self.multimodal_collection = None
        
        # 7. 创建多模态RAG内存实例
        if self.multimodal_collection:
            self.multimodal_memory = ChromaDBVectorMemory(
                config=PersistentChromaDBVectorMemoryConfig(
                    collection_name=self.multimodal_collection_name,
                    persistence_path=self.db_persistence_path,
                    k=4, 
                    score_threshold=0.1,
                )
            )
        
        # 8. ✨ 新增：可用的向量库列表
        self.available_collections = [
            "multimodal2text",
            "LLMvisDataset"
        ]
        print(f"   可用的向量库: {self.available_collections}")
        self.initialized = True
    
    async def _get_chroma_collection(self, collection_name: Optional[str] = None):
        """
        解析 Chroma Collection：当前服务主集合用 self.raw_collection；
        其它名称通过 collection_manager 按需打开（exact / local-filter 补全等）。
        """
        if not self.initialized:
            await self.initialize()
        name = (collection_name or self.collection_name or "").strip()
        if not name:
            return None
        if name == self.collection_name and self.raw_collection is not None:
            return self.raw_collection
        if not getattr(self, "collection_manager", None):
            self.collection_manager = await get_rag_collection_manager()
        ok = await self.collection_manager.check_collection_exists(name)
        if not ok:
            print(f"⚠️ Chroma 集合不存在: {name}")
            return None
        return await self.collection_manager.get_collection(name)
    
    # ... _sanitize_metadata_value 保持不变 ...
    def _sanitize_metadata_value(self, value: Any) -> Union[str, int, float, bool]:
        if value is None: return ""
        if isinstance(value, (list, dict, tuple)):
            return json.dumps(value, ensure_ascii=False)
        return value

    def _lookup_coordinates_2d_from_local_cache(self, item_id: str) -> Optional[List[float]]:
        """
        用当前 figures_file_path 加载的 local_data_cache（与前端底图同源）覆盖二维坐标，
        避免 Chroma 里 full_json 仍为旧降维结果而地图已更新 embeddings JSON。
        """
        if not item_id or not self.local_data_cache:
            return None
        sid = str(item_id).strip()
        if not sid:
            return None
        for row in self.local_data_cache:
            if not isinstance(row, dict):
                continue
            rid = row.get("id") or row.get("chunk_id")
            if rid is None:
                continue
            if str(rid).strip() != sid:
                continue
            c = row.get("coordinates_2d")
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                try:
                    return [float(c[0]), float(c[1])]
                except (TypeError, ValueError):
                    return None
            return None
        return None
    
    # ... _load_data_to_memory 保持不变 ...
    async def _load_data_to_memory(self):
        if not os.path.exists(self.figures_file_path): return
        try:
            with open(self.figures_file_path, "r", encoding="utf-8") as f:
                figures = json.load(f)
            
            # 检查集合是否已经包含数据，如果有则不重复加载
            if self.raw_collection.count() > 0:
                print(f"📊 集合 {self.collection_name} 中已有 {self.raw_collection.count()} 条数据，跳过加载。")
                return
            
            count = 0
            for figure in figures:
                figure_id = str(figure.get("id", f"unknown_{count}"))
                paper_id = str(figure.get("paper_id", "unknown"))
                keywords_list = figure.get("key_entities", []) # 确保这里对应 JSON 字段
                
                title = str(figure.get("title", ""))
                summary = str(figure.get("concise_summary", ""))
                insight = str(figure.get("inferred_insight", ""))
                if isinstance(summary, list): summary = " ".join(map(str, summary))
                if isinstance(insight, list): insight = " ".join(map(str, insight))
                searchable_content = f"Title: {title}\nSummary: {summary}\nInsight: {insight}"
                
                raw_savepath = figure.get("save_path", "") 
                abs_image_path = ""
                if raw_savepath and isinstance(raw_savepath, str):
                    if os.path.exists(raw_savepath):
                        abs_image_path = raw_savepath
                    else:
                        base_dir = os.path.dirname(self.figures_file_path)
                        possible_path = os.path.join(base_dir, raw_savepath)
                        if os.path.exists(possible_path):
                            abs_image_path = possible_path

                metadata = {
                    "id": figure_id,
                    "paper_id": paper_id,
                    "savepath": str(raw_savepath),
                    "image_path": abs_image_path,
                    "keywords": self._sanitize_metadata_value(keywords_list),
                    "full_json": json.dumps(figure, ensure_ascii=False)
                }
                if searchable_content.strip():
                    await self.rag_memory.add(
                        MemoryContent(content=searchable_content, mime_type=MemoryMimeType.TEXT, metadata=metadata)
                    )
                    count += 1
            print(f"📊 成功加载 {count} 条向量数据到集合 {self.collection_name}。")
        except Exception as e:
            print(f"❌ 加载数据出错: {e}")

    # =========================================================================
    #  接口 A: 语义检索 (查库)
    # =========================================================================
    async def query_by_semantic(
        self,
        query_text: str,
        n_results: int = 3,
        score_threshold: float = 0.1,
        collection_name: str = None,
        use_multimodal: bool = False,
        allowed_chunk_ids: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        if not self.initialized: await self.initialize()
        _semantic_pipeline_trace_cv.set(None)
        self._last_semantic_pipeline_trace = None

        # 智能选择集合
        target_collection = None
        
        # 优先使用指定的集合名称
        if collection_name:
            exists = await self.collection_manager.check_collection_exists(collection_name)
            if exists:
                target_collection = await self.collection_manager.get_collection(collection_name)
                print(f"   使用指定集合: {collection_name}")
            else:
                print(f"❌ 集合 {collection_name} 不存在，请先创建该集合")
                return [], None, None
        
        # 如果没有指定集合名称，使用实例初始化时设置的默认集合
        if not target_collection:
            if self.raw_collection:
                target_collection = self.raw_collection
                print(f"   使用实例默认集合: {self.collection_name}")
            else:
                print("❌ 没有可用的集合，请先确保集合已创建")
                return [], None
        
        # 检查集合是否可用
        if not target_collection:
            print("❌ 集合不可用，请先确保集合已创建")
            return [], None

        user_query_for_rerank = (query_text or "").strip()
        if not user_query_for_rerank:
            return [], None

        use_hyde = env_flag("RAG_HYDE_ENABLED", "true")
        use_rerank = env_flag("RAG_RERANK_ENABLED", "true")
        effective_query = user_query_for_rerank
        hyde_hypothetical_paragraph: Optional[str] = None
        if use_hyde and AIOHTTP_AVAILABLE:
            hypo = await _hyde_hypothetical_paragraph(user_query_for_rerank)
            if hypo:
                effective_query = hypo
                hyde_hypothetical_paragraph = hypo
                print(f"🧪 [HyDE] 使用假想段落做向量查询（前 100 字）: {hypo[:100]}...")
        elif use_hyde and not AIOHTTP_AVAILABLE:
            print("⚠️ [HyDE] 已启用但 aiohttp 不可用，跳过 HyDE")

        n_out = max(1, int(n_results))
        fetch_n, cap_after_filter = semantic_chroma_pool_size(n_out, use_rerank)
        recall_threshold = semantic_vector_threshold(score_threshold, use_rerank)
        if use_rerank and abs(recall_threshold - float(score_threshold)) > 1e-9:
            print(
                f"📉 [Semantic+Rerank] 向量分数门槛: {score_threshold} → {recall_threshold} "
                f"（候选池 top-{fetch_n}，目标最多返回 {n_out} 条；实际命中数以日志末行为准）"
            )

        def _sync_semantic():
            try:
                local_threshold = recall_threshold
                initial_n = int(fetch_n)
                where_filter = None
                if allowed_chunk_ids is not None and len(allowed_chunk_ids) > 0:
                    str_ids = [str(x) for x in allowed_chunk_ids]
                    where_filter = {"id": {"$in": str_ids}}

                raw_results = target_collection.query(
                    query_texts=[effective_query],
                    n_results=initial_n,
                    include=["metadatas", "documents", "distances"],
                    where=where_filter,
                )

                if not raw_results or not raw_results.get("ids") or not raw_results["ids"][0]:
                    wf = f"where id∈{len(allowed_chunk_ids)} 条" if where_filter else "无 where 过滤"
                    print(
                        f"⚠️ [Semantic] Chroma 未返回命中（{wf}）。"
                        "若框选了地图：框内 id 与集合中 id 不一致、或 HyDE 向量与框内文本都不相似，会得到 0 条。"
                    )
                    return raw_results

                filtered_results = {
                    "ids": [[]],
                    "metadatas": [[]],
                    "documents": [[]],
                    "distances": [[]]
                }

                ids = raw_results["ids"][0]
                metadatas = raw_results["metadatas"][0]
                documents = raw_results["documents"][0]
                distances = raw_results["distances"][0]

                below = 0
                bad_dist = 0
                for i, (id, metadata, document, distance) in enumerate(zip(ids, metadatas, documents, distances)):
                    if distance is None:
                        bad_dist += 1
                        continue
                    try:
                        dnum = float(distance)
                    except (TypeError, ValueError):
                        bad_dist += 1
                        continue
                    score = 1.0 / (1.0 + dnum)
                    if score >= local_threshold:
                        filtered_results["ids"][0].append(id)
                        filtered_results["metadatas"][0].append(metadata)
                        filtered_results["documents"][0].append(document)
                        filtered_results["distances"][0].append(distance)
                    else:
                        below += 1

                if not filtered_results["ids"][0] and ids:
                    print(
                        f"⚠️ [Semantic] Chroma 召回 {len(ids)} 条，但向量分数过滤后 0 条 "
                        f"(门槛={local_threshold:.4f}, 低于门槛={below}, 无效距离={bad_dist})。"
                    )

                cap = int(cap_after_filter)
                if len(filtered_results["ids"][0]) > cap:
                    filtered_results["ids"][0] = filtered_results["ids"][0][:cap]
                    filtered_results["metadatas"][0] = filtered_results["metadatas"][0][:cap]
                    filtered_results["documents"][0] = filtered_results["documents"][0][:cap]
                    filtered_results["distances"][0] = filtered_results["distances"][0][:cap]

                return filtered_results
            except Exception as e:
                print(f"❌ Semantic Query Error: {e}")
                return None

        results = await asyncio.to_thread(_sync_semantic)
        formatted = self._format_results(results, is_semantic=True)
        before_rerank = [
            {"id": str(x.get("id", "")), "score": float(x.get("score") or 0.0)}
            for x in formatted
        ]
        rerank_applied = False
        if use_rerank and len(formatted) >= 2 and AIOHTTP_AVAILABLE:
            formatted = await _rerank_semantic_items(
                user_query_for_rerank, formatted, n_out
            )
            rerank_applied = True
            print(f"📊 [Rerank] 已对 {len(formatted)} 条结果重排（目标 top {n_out}）")
        elif use_rerank and not AIOHTTP_AVAILABLE:
            print("⚠️ [Rerank] 已启用但 aiohttp 不可用，跳过重排")
            formatted = formatted[:n_out]
        else:
            formatted = formatted[:n_out]
        after_rerank = [
            {"id": str(x.get("id", "")), "score": float(x.get("score") or 0.0)}
            for x in formatted
        ]
        ids_b = [x["id"] for x in before_rerank]
        ids_a = [x["id"] for x in after_rerank]
        ncmp = min(len(ids_b), len(ids_a))
        order_changed = bool(
            rerank_applied and ncmp > 0 and ids_b[:ncmp] != ids_a[:ncmp]
        )
        _log_rag_semantic_pipeline_to_run_md(
            {
                "user_query": user_query_for_rerank,
                "hyde_env_enabled": use_hyde,
                "hyde_aiohttp_available": AIOHTTP_AVAILABLE,
                "hyde_used_hypothetical_paragraph": hyde_hypothetical_paragraph is not None,
                "hyde_hypothetical_paragraph_full_text": hyde_hypothetical_paragraph or "",
                "effective_query_embedded_in_chroma": effective_query,
                "vector_recall_threshold": float(recall_threshold),
                "chroma_pool_fetch_n": int(fetch_n),
                "chroma_cap_after_filter": int(cap_after_filter),
                "n_results_requested": int(n_out),
                "rerank_env_enabled": use_rerank,
                "rerank_applied_to_results": rerank_applied,
                "before_rerank_ids_and_vector_scores": before_rerank,
                "after_rerank_ids_and_scores": after_rerank,
                "rerank_order_changed_vs_vector_stage": order_changed,
            }
        )
        trace_dict = {
            "hyde_hypothetical_paragraph_full_text": hyde_hypothetical_paragraph or "",
            "rerank_before_ids": ids_b,
            "rerank_after_ids": ids_a,
        }
        _semantic_pipeline_trace_cv.set(trace_dict)
        self._last_semantic_pipeline_trace = trace_dict
        return formatted, trace_dict

    # =========================================================================
    #  接口 C: 精确关键字检索 (非向量相似度，纯文本匹配)
    # =========================================================================
    async def query_by_exact_match(
        self,
        query_text: str,
        n_results: int = 10,
        collection_name: str = None,
        allowed_chunk_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        在Chroma数据中进行精确的子串匹配检索（非向量相似度）。
        适合需要包含特定关键词的硬性召回。
        """
        if not self.initialized: await self.initialize()
        
        if not query_text or not query_text.strip():
            return []
            
        search_term = query_text.strip()
        needle_lower = search_term.lower()

        c_name = collection_name or self.collection_name
        target_collection = await self._get_chroma_collection(c_name)
        if not target_collection:
            return []

        print(f"⚡ [Exact Search] 在Chroma库中进行文本匹配: '{search_term}'")
        str_ids = (
            [str(x) for x in allowed_chunk_ids]
            if allowed_chunk_ids is not None and len(allowed_chunk_ids) > 0
            else None
        )

        def _sync_exact():
            try:
                # 小追问 / 框选：同时带 where_document + metadata where 在部分 Chroma 版本上会 0 命中；
                # 改为按 id 批量拉取正文后在内存做不区分大小写子串匹配（与旧版 local JSON 行为一致）。
                if str_ids:
                    res = target_collection.get(
                        ids=str_ids,
                        include=["metadatas", "documents"],
                    )
                    ids = res.get("ids") or []
                    docs = res.get("documents") or []
                    metas = res.get("metadatas") or []
                    f_ids, f_docs, f_metas = [], [], []
                    for i, doc in enumerate(docs):
                        text = "" if doc is None else str(doc)
                        if needle_lower in text.lower():
                            f_ids.append(ids[i])
                            f_docs.append(doc)
                            f_metas.append(metas[i] if i < len(metas) else {})
                    return {"ids": f_ids, "documents": f_docs, "metadatas": f_metas}

                # 全库：先 FTS $contains（区分大小写），再小写短语、再不区分大小写正则
                res = target_collection.get(
                    where_document={"$contains": search_term},
                    include=["metadatas", "documents"],
                )
                if not (res and res.get("ids")) and search_term != needle_lower:
                    res = target_collection.get(
                        where_document={"$contains": needle_lower},
                        include=["metadatas", "documents"],
                    )
                if not (res and res.get("ids")):
                    try:
                        rx = "(?i)" + re.escape(search_term)
                        res = target_collection.get(
                            where_document={"$regex": rx},
                            include=["metadatas", "documents"],
                        )
                    except Exception as _rx_e:
                        print(f"⚠️ Exact Search $regex 回退未使用: {_rx_e}")
                        res = {"ids": [], "documents": [], "metadatas": []}
                return res
            except Exception as e:
                print(f"❌ Exact Search Query Error: {e}")
                return None

        raw_results = await asyncio.to_thread(_sync_exact)
        if not raw_results or not raw_results.get("ids"):
            print(f"   ✅ 精确匹配到 0 条数据")
            return []
            
        # 包装成 query 返回的格式以便复用 _format_results
        wrapped_results = {
            "ids": [raw_results["ids"]],
            "metadatas": [raw_results["metadatas"]],
            "documents": [raw_results["documents"]],
            "distances": [[None] * len(raw_results["ids"])]
        }
        
        formatted = self._format_results(wrapped_results, is_semantic=False)
        
        # 按需截断返回数量
        if n_results and n_results > 0:
            formatted = formatted[:n_results]

        print(f"   ✅ 精确匹配到 {len(formatted)} 条数据")
        return formatted

    # =========================================================================
    #  ✨ 接口 B: 本地内存检索 (不查库，只查 List)
    # =========================================================================
    async def query_by_local_filter(
        self,
        keywords: List[str] = None,
        paper_id: str = None,
        figure_type: str = None,
        n_results: Optional[int] = None,
        allowed_chunk_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        直接在 self.local_data_cache (JSON 列表) 中进行 Python 过滤。
        精准、快速、无类型烦恼。
        """
        if not self.initialized: await self.initialize()
        
        allow_set = None
        if allowed_chunk_ids is not None and len(allowed_chunk_ids) > 0:
            allow_set = {str(x) for x in allowed_chunk_ids}

        # 🔒 若未指定 paper/关键词/type 且也无 id 白名单，则避免返回全表
        if not paper_id and not keywords and not figure_type:
            if allow_set is None:
                print(f"⚠️ [Local Search] 警告：所有过滤参数均为 None，返回空列表以避免返回所有数据")
                return []
        
        results = []

        print(f"⚡ [Local Search] 在 {len(self.local_data_cache)} 条数据中过滤: P={paper_id}, K={keywords}")

        for item in self.local_data_cache:
            if allow_set is not None and str(item.get("id", "")) not in allow_set:
                continue
            # --- 解析真实元数据 ---
            # 因为数据可能被打包在 metadata 或 metadata.full_json 中
            real_item = item
            meta = item.get("metadata", {})
            if "full_json" in meta:
                try:
                    real_item = json.loads(meta["full_json"])
                except:
                    pass
            elif "key_entities" not in item and "keywords" in meta:
                # 尝试从 metadata.keywords 解析
                pass

            # 1. Paper ID 匹配 (转字符串比较，防坑)
            if paper_id:
                # 如果 item 里没 paper_id 或者 不相等，跳过
                item_pid = str(item.get("paper_id", ""))
                # 统一转为小写进行匹配，解决大小写不一致导致的问题
                if item_pid.lower() != str(paper_id).lower():
                    continue
            
            # 2. Figure Type 匹配
            if figure_type:
                item_type = str(real_item.get("visual_type", "") or real_item.get("figure_type", ""))
                if str(figure_type).lower() not in item_type.lower():
                    continue

            # 3. Keywords 匹配 (求交集)
            if keywords:
                # 你的 json 里可能是 "key_entities" 或 "keywords"
                item_kws = real_item.get("key_entities", [])
                # 确保 item_kws 是列表
                if not isinstance(item_kws, list): item_kws = []
                
                # 如果依然没找到，尝试从 metadata 找
                if not item_kws:
                    meta_kws = meta.get("keywords", [])
                    if isinstance(meta_kws, str):
                        try:
                            meta_kws = json.loads(meta_kws)
                        except:
                            meta_kws = [meta_kws]
                    item_kws = meta_kws

                # 只要命中一个词就保留
                common = set(keywords) & set(item_kws)
                if not common:
                    continue # 一个都没命中，跳过

            # --- 匹配成功 ---
            # 构造返回格式，使其与 query_by_semantic 的输出格式一致
            if "full_json" in meta:
                content = {
                    "title": real_item.get("title", item.get("title", "")),
                    "summary": real_item.get("concise_summary", item.get("summary", "")),
                    "insight": real_item.get("inferred_insight", item.get("insight", ""))
                }
            else:
                raw_content = item.get("content", "")
                content = {
                    "title": meta.get("paper_name", meta.get("file_name", "Text Chunk")),
                    "text": raw_content,
                    "summary": raw_content[:150] + "..." if len(raw_content) > 150 else raw_content
                }

            results.append({
                "id": str(item.get("id", "")),
                "content": content, # 原始对象
                "score": 1.0,    # 规则命中，置信度 100%
                "metadata": item
            })
        
        # 可选：限制返回数量（用于与前端/策略超参数联动）
        if n_results is not None:
            try:
                n = int(n_results)
                if n > 0:
                    results = results[:n]
            except Exception:
                pass

        # 🚀 改进：因为 local_data_cache 的 content 字段可能是截断的（200字符），
        # 我们用匹配到的 id 去 Chroma 取完整的 documents，以便下游能够获得不被截断的完整数据。
        matched_ids = [str(r["id"]) for r in results]
        if matched_ids:
            try:
                target_collection = await self._get_chroma_collection(self.collection_name)
                if target_collection:
                    def _sync_get():
                        return target_collection.get(
                            ids=matched_ids,
                            include=["metadatas", "documents"]
                        )
                    raw_results = await asyncio.to_thread(_sync_get)
                    if raw_results and raw_results.get("ids"):
                        wrapped_results = {
                            "ids": [raw_results["ids"]],
                            "metadatas": [raw_results["metadatas"]],
                            "documents": [raw_results["documents"]],
                            "distances": [[None] * len(raw_results["ids"])]
                        }
                        formatted = self._format_results(wrapped_results, is_semantic=False)
                        return formatted
            except Exception as e:
                print(f"❌ Local Filter fallback to Chroma Error: {e}")

        return results
    
# =========================================================================
    #  ✨ 接口 D: 基于直接向量输入的相似度检索 (查库)
    # =========================================================================
    async def query_by_vector(self, vector: List[float], n_results: int = 5, score_threshold: float = 0.1) -> List[Dict[str, Any]]:
        """
        基于直接输入的向量进行相似度检索
        
        参数:
        - vector: 输入的向量
        - n_results: 返回结果数量
        - score_threshold: 分数阈值
        
        返回:
        - List[Dict[str, Any]]: 检索结果列表
        """
        if not self.initialized: await self.initialize()
        
        def _sync_query():
            try:
                raw_results = self.raw_collection.query(
                    query_embeddings=[vector],
                    n_results=n_results,
                    include=["metadatas", "documents", "distances"]
                )
                return raw_results
            except Exception as e:
                print(f"❌ Vector Query Error: {e}")
                return None
        
        results = await asyncio.to_thread(_sync_query)
        return self._format_results(results, is_semantic=True)
    
    # =========================================================================
    #  ✨ 接口 E: 基于证据ID的嵌入相似度检索 (查库)
    # =========================================================================
    async def query_by_evidence_similarity(self, evidence_id: str, n_results: int = 5, score_threshold: float = 0.1) -> List[Dict[str, Any]]:
        """
        基于现有证据节点的嵌入进行相似证据检索
        
        参数:
        - evidence_id: 现有证据节点的ID
        - n_results: 返回结果数量
        - score_threshold: 分数阈值
        
        返回:
        - List[Dict[str, Any]]: 检索结果列表
        """
        if not self.initialized: await self.initialize()
        
        def _sync_query():
            try:
                # 获取指定证据的嵌入
                result = self.raw_collection.get(
                    ids=[evidence_id],
                    include=["embeddings"]
                )
                
                if not result or not result.get("embeddings") or not result["embeddings"][0]:
                    print(f"❌ 未找到证据 {evidence_id} 的嵌入")
                    return None
                
                # 使用该嵌入进行相似度检索
                vector = result["embeddings"][0]
                raw_results = self.raw_collection.query(
                    query_embeddings=[vector],
                    n_results=n_results + 1,  # +1 是为了排除自身
                    include=["metadatas", "documents", "distances"]
                )
                
                # 过滤掉自身
                if raw_results and raw_results.get("ids") and raw_results["ids"][0]:
                    filtered_ids = []
                    filtered_metadatas = []
                    filtered_documents = []
                    filtered_distances = []
                    
                    for i, id in enumerate(raw_results["ids"][0]):
                        if id != evidence_id:
                            filtered_ids.append(id)
                            filtered_metadatas.append(raw_results["metadatas"][0][i])
                            filtered_documents.append(raw_results["documents"][0][i])
                            filtered_distances.append(raw_results["distances"][0][i])
                    
                    raw_results["ids"][0] = filtered_ids[:n_results]
                    raw_results["metadatas"][0] = filtered_metadatas[:n_results]
                    raw_results["documents"][0] = filtered_documents[:n_results]
                    raw_results["distances"][0] = filtered_distances[:n_results]
                
                return raw_results
            except Exception as e:
                print(f"❌ Evidence Similarity Query Error: {e}")
                return None
        
        results = await asyncio.to_thread(_sync_query)
        return self._format_results(results, is_semantic=True)
    
    # =========================================================================
    #  ✨ 接口 C: 多模态检索 (查多模态库)
    # =========================================================================
    async def query_by_multimodal(self, query_image_path: str = None, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        多模态检索，仅支持基于图片的检索。
        
        参数:
        - query_image_path: 图片查询路径
        - n_results: 返回结果数量
        
        返回:
        - List[Dict[str, Any]]: 检索结果列表
        """
        if not self.initialized: await self.initialize()
        
        # 仅支持图片检索
        if query_image_path and os.path.exists(query_image_path):
            # 检查PIL和CLIP是否可用
            if not PIL_AVAILABLE or not CLIP_AVAILABLE:
                print("[Warning] PIL或CLIP模型不可用，无法处理图片检索请求")
                return []
            
            # 提取查询图片的特征
            try:
                # 直接使用集合管理器的多模态功能
                from rag_collection_manager import MultimodalRAGManager
                multimodal_manager = MultimodalRAGManager()
                await multimodal_manager.initialize_clip_model()
                
                def _sync_extract():
                    try:
                        image = Image.open(query_image_path).convert("RGB")
                        inputs = multimodal_manager.clip_processor(images=image, return_tensors="pt").to(multimodal_manager.device)
                        with torch.no_grad():
                            query_features = multimodal_manager.clip_model.get_image_features(**inputs)
                        query_features = query_features.cpu().numpy().tolist()[0]
                        return query_features
                    except Exception as img_e:
                        print(f"[Warning] 处理图片检索时出错: {img_e}")
                        return None
                
                query_features = await asyncio.to_thread(_sync_extract)
                
                if query_features:
                    # 直接使用CLIP嵌入进行查询
                    print("[Info] 使用CLIP模型提取图片特征，进行真正的多模态检索")
                    
                    def _sync_query():
                        try:
                            return self.multimodal_collection.query(
                                query_embeddings=[query_features],
                                n_results=int(n_results),
                                include=["metadatas", "documents", "distances"]
                            )
                        except Exception as e:
                            print(f"❌ Multimodal Query Error: {e}")
                            return {"ids": [], "metadatas": [], "documents": [], "distances": []}
                    
                    results = await asyncio.to_thread(_sync_query)
                    return self._format_results(results, is_semantic=True)
                else:
                    return []
            except Exception as img_e:
                print(f"[Warning] 处理图片检索时出错: {img_e}")
                return []
        else:
            # 没有提供有效的图片路径
            print("[Warning] 未提供有效的图片路径，无法进行多模态检索")
            return []

    def _format_results(self, raw_results, is_semantic: bool) -> List[Dict[str, Any]]:
        """
        格式化检索结果，将ChromaDB返回的原始结果转换为统一格式。
        
        参数:
        - raw_results: ChromaDB返回的原始结果字典
        - is_semantic: 是否为语义检索
        
        返回:
        - List[Dict[str, Any]]: 格式化后的检索结果列表
        """
        formatted = []
        # 检查raw_results是否为None
        if not raw_results:
            return formatted
        # 检查raw_results是否有ids键，并且ids不为空
        if not isinstance(raw_results, dict) or not raw_results.get("ids"):
            return formatted
        
        # 安全获取数据，防止KeyError
        ids = raw_results.get("ids", [[]])[0] if raw_results.get("ids") else []
        metadatas = raw_results.get("metadatas", [[]])[0] if raw_results.get("metadatas") else []
        documents = raw_results.get("documents", [[]])[0] if raw_results.get("documents") else []
        distances = raw_results.get("distances", [[]])[0] if raw_results.get("distances") else [None] * len(ids)

        # 确保所有列表长度一致
        min_length = min(len(ids), len(metadatas), len(documents), len(distances))
        ids = ids[:min_length]
        metadatas = metadatas[:min_length]
        documents = documents[:min_length]
        distances = distances[:min_length]
        
        # 格式化结果
        seen_ids = set()  # 用于去重
        for id, doc, meta, dist in zip(ids, documents, metadatas, distances):
            # 计算分数
            if is_semantic and dist is not None:
                try:
                    score = 1.0 / (1.0 + float(dist))
                except (ValueError, TypeError):
                    score = 0.0
            else:
                score = 1.0
            
            # 安全获取元数据
            meta_dict = meta if isinstance(meta, dict) else {}
            
            # 获取文档ID
            img_id = meta_dict.get("id", str(id))
            
            # 去重：跳过已经处理过的ID
            if img_id in seen_ids:
                continue
            seen_ids.add(img_id)
            
            # 获取结构化的content对象，只包含图题、insight和summary
            content_obj = {}
            full_obj = meta_dict  # 默认使用meta_dict作为metadata
            
            # 尝试从full_json中解析关键信息（适用于图表数据）
            if meta_dict.get("full_json"):
                try:
                    full_obj = json.loads(meta_dict["full_json"])
                    # 只提取需要的字段
                    content_obj = {
                        "title": full_obj.get("title", ""),
                        "summary": full_obj.get("concise_summary", ""),
                        "insight": full_obj.get("inferred_insight", "")
                    }
                    # 确保summary和insight是字符串
                    if isinstance(content_obj["summary"], list):
                        content_obj["summary"] = " ".join(map(str, content_obj["summary"]))
                    if isinstance(content_obj["insight"], list):
                        content_obj["insight"] = " ".join(map(str, content_obj["insight"]))
                except (json.JSONDecodeError, TypeError):
                    # 如果解析失败，使用文档文本
                    content_obj = {"text": doc if doc else ""}
            # 处理论文文本数据（适用于paper_rag_collection）
            elif meta_dict.get("paper_name") or meta_dict.get("file_name"):
                # 为论文文本创建结构化的content对象
                content_obj = {
                    "title": meta_dict.get("paper_name", ""),
                    "text": doc if doc else "",
                    "summary": doc[:150] + "..." if len(doc) > 150 else doc  # 生成简单摘要
                }
                # 丰富full_obj，确保包含所有必要的字段
                full_obj = {
                    **meta_dict,
                    "type": "paper",
                    "source": meta_dict.get("file_name", ""),
                    "paper_id": meta_dict.get("paper_name", "").lower().replace(" ", "_"),
                    "keywords": meta_dict.get("keywords", []),
                    "content_type": "text"
                }
            else:
                # 其他情况，使用文档文本
                content_obj = {"text": doc if doc else ""}
            
            fresh_coords = self._lookup_coordinates_2d_from_local_cache(str(img_id))
            if fresh_coords is not None and isinstance(full_obj, dict):
                if full_obj is meta_dict:
                    full_obj = dict(meta_dict)
                else:
                    full_obj = dict(full_obj)
                full_obj["coordinates_2d"] = fresh_coords
                if meta_dict.get("full_json"):
                    try:
                        meta_dict = dict(meta_dict)
                        meta_dict["full_json"] = json.dumps(full_obj, ensure_ascii=False)
                    except Exception:
                        pass

            # 确保返回的格式统一，包含所有必要的字段
            formatted.append({
                "id": img_id, 
                "content": content_obj, 
                "score": score, 
                "metadata": full_obj,
                "type": "picture" if "full_json" in meta_dict else "texture",
                "source": meta_dict.get("file_name", meta_dict.get("source_md", ""))
            })
        return formatted

    async def close(self):
        self.initialized = False
        if self.rag_memory: await self.rag_memory.close()
        if self.multimodal_memory: await self.multimodal_memory.close()

rag_service = None
rag_service_instances = {}  # 用于存储多个RAG服务实例

async def get_rag_service(collection_name: str = None, multimodal_collection_name: str = None) -> RAGService:
    """
    获取RAG服务实例，可以指定使用哪个数据库集合
    
    参数:
    - collection_name: 数据库集合名称，如果指定则创建或获取对应的集合
    - multimodal_collection_name: 多模态数据库集合名称，如果指定则创建或获取对应的集合
    
    返回:
    - RAGService: RAG服务实例
    """
    global rag_service, rag_service_instances
    
    # 如果没有指定集合名称，使用默认实例
    if not collection_name:
        if rag_service is None:
            rag_service = RAGService()
            await rag_service.initialize()
        return rag_service
    
    # 如果指定了集合名称，从缓存中获取或创建新实例
    instance_key = f"{collection_name}_{multimodal_collection_name or 'default'}"
    if instance_key not in rag_service_instances:
        # 创建新的RAG服务实例
        new_rag_service = RAGService(collection_name, multimodal_collection_name)
        await new_rag_service.initialize(collection_name=collection_name, multimodal_collection_name=multimodal_collection_name)
        rag_service_instances[instance_key] = new_rag_service
    
    return rag_service_instances[instance_key]

def print_result_summary(title: str, results: List[Dict], expected_count: str = "N/A"):
    print(f"\n{'='*60}")
    print(f"🧪 测试场景: {title}")
    print(f"{'-'*60}")
    print(f"📊 结果数量: {len(results)} (预期: {expected_count})")
    
    if not results:
        print("⚠️ 未找到结果")
        return

    print(f"🔎 前 1 条详情:")
    # first = results[0]
    for first in results:
        print(f"   - ID: {first.get('id')}")
        print(f"   - Score: {first.get('score')}")
        
        # 检查关键字段是否存在
        meta = first.get('metadata', {})
        content = first.get('content', {})
        print(content)
        
        print(f"   - Paper ID: {meta.get('paperid')} (Raw Type: {type(meta.get('paper_id'))})")
        # print(f"   - Image Path: {meta.get('save_path')}")
        # print(f"   - Keywords: {meta.get('key_entities')}")
        # print(f"    -sight: {content.get('insight')}")
    
    # 验证 content 是字典还是字符串


if __name__ == "__main__":
    async def test():
        # 使用新的multimodal2text库进行测试
        service = await get_rag_service(collection_name="multimodal2text")
        
        print("🧪 测试新的multimodal2text库")
        print("=" * 60)
        
        # 测试1: 基本语义搜索
        print("\n[测试1] 基本语义搜索")
        query1 = "PM2.5"
        results1, _t1 = await service.query_by_semantic(query_text=query1, n_results=5, collection_name="multimodal2text")
        print_result_summary(f"语义搜索 (Query={query1})", results1, expected_count=">=1")
        
        # 测试2: 论文标题搜索
        print("\n[测试2] 论文标题搜索")
        query2 = "biomass burning"
        results2, _t2 = await service.query_by_semantic(query_text=query2, n_results=3, collection_name="multimodal2text")
        print_result_summary(f"语义搜索 (Query={query2})", results2, expected_count=">=1")
        
        # 测试3: 图片相关搜索
        print("\n[测试3] 图片相关搜索")
        query3 = "figure chart graph"
        results3, _t3 = await service.query_by_semantic(query_text=query3, n_results=3, collection_name="multimodal2text")
        print_result_summary(f"语义搜索 (Query={query3})", results3, expected_count=">=1")
        
        # 测试4: 具体论文内容搜索
        print("\n[测试4] 具体论文内容搜索")
        query4 = "air quality China"
        results4, _t4 = await service.query_by_semantic(query_text=query4, n_results=3, collection_name="multimodal2text")
        print_result_summary(f"语义搜索 (Query={query4})", results4, expected_count=">=1")
        
        # 测试5: 验证metadata字段
        print("\n[测试5] 验证metadata字段")
        if results1:
            first_result = results1[0]
            metadata = first_result.get('metadata', {})
            print("📋 第一条结果的metadata字段:")
            print(metadata)
        
        print("\n✅ multimodal2text库测试完成")

    
    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        pass