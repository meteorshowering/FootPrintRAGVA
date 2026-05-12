"""
从 Chroma 中各取一条记录，写入 JSON，便于查看 multimodal2text / LLMvisDataset 的字段结构。
用法（在 ToRAGLENSBack 目录下）:  python dump_rag_collection_samples.py
输出: docs/rag_collection_sample_structures.json
"""
from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from rag_collection_manager import get_rag_collection_manager

COLLECTIONS: List[str] = ["multimodal2text", "LLMvisDataset"]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "docs", "rag_collection_sample_structures.json")


def json_friendly(obj: Any, depth: int = 0) -> Any:
    """尽量转成可 JSON 序列化的结构；避免整段 embedding 撑爆文件。"""
    if depth > 14:
        return "<max_depth>"
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if hasattr(obj, "tolist"):
        try:
            return json_friendly(obj.tolist(), depth + 1)
        except Exception:
            return str(obj)[:400]
    if isinstance(obj, dict):
        return {str(k): json_friendly(v, depth + 1) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_friendly(x, depth + 1) for x in obj]
    return str(obj)[:800]


def embedding_summary(emb: Any) -> Dict[str, Any]:
    if emb is None:
        return {"present": False}
    if hasattr(emb, "tolist"):
        try:
            emb = emb.tolist()
        except Exception:
            return {"present": True, "note": "tolist failed", "repr": repr(emb)[:200]}
    if isinstance(emb, list):
        flat: List[Any] = emb
        if emb and isinstance(emb[0], list):
            flat = emb[0]
        n = len(flat)
        head: List[Any] = []
        for x in flat[:8]:
            try:
                head.append(float(x))
            except (TypeError, ValueError):
                head.append(str(x)[:24])
        return {"present": True, "dimension": n, "first_8_values": head}
    return {"present": True, "note": "unknown shape", "repr": repr(emb)[:200]}


def truncate_doc(s: Optional[str], max_len: int = 2400) -> Optional[str]:
    if s is None:
        return None
    t = str(s)
    if len(t) <= max_len:
        return t
    return t[:max_len] + f"\n... [truncated, total {len(t)} chars]"


async def sample_one_collection(name: str) -> Dict[str, Any]:
    mgr = await get_rag_collection_manager()
    if not await mgr.check_collection_exists(name):
        return {"collection_name": name, "exists": False, "note": "Chroma 中无此集合"}

    coll = await mgr.get_collection(name)
    if coll is None:
        return {"collection_name": name, "exists": False, "note": "get_collection 返回 None"}

    try:
        count = coll.count()
    except Exception as e:
        count = None
        err_count = str(e)
    else:
        err_count = None

    coll_meta = getattr(coll, "metadata", None)
    if not isinstance(coll_meta, dict):
        coll_meta = {}

    try:
        raw = coll.get(limit=1, include=["embeddings", "metadatas", "documents"])
    except Exception as e:
        return {
            "collection_name": name,
            "exists": True,
            "chroma_collection_metadata": json_friendly(coll_meta),
            "approximate_count": count,
            "count_error": err_count,
            "sample_error": str(e),
        }

    ids = raw.get("ids") or []
    docs = raw.get("documents") or []
    metas = raw.get("metadatas") or []
    embs_raw = raw.get("embeddings")
    if embs_raw is None:
        embs = []
    elif isinstance(embs_raw, list):
        embs = embs_raw
    else:
        embs = [embs_raw]

    sample: Dict[str, Any] = {}
    if ids:
        sample["id"] = ids[0]
    if docs:
        sample["document_text"] = truncate_doc(docs[0] if docs else None)
    if metas:
        sample["metadata"] = json_friendly(metas[0] if metas else {})
    if embs:
        sample["embedding"] = embedding_summary(embs[0] if embs else None)

    return {
        "collection_name": name,
        "exists": True,
        "chroma_collection_metadata": json_friendly(coll_meta),
        "approximate_count": count,
        "count_error": err_count,
        "sample_one_record": sample,
        "note": "与 rag_service._format_results 消费的是同一套 Chroma get/query 字段；前端 experiment JSON 的 retrieval_result 由该格式化逻辑再映射。",
    }


async def main() -> None:
    os.makedirs(os.path.join(HERE, "docs"), exist_ok=True)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "chromadb_persistence": os.path.join(HERE, ".chromadb_autogen"),
        "collections": {},
    }
    for name in COLLECTIONS:
        payload["collections"][name] = await sample_one_collection(name)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"已写入: {OUT_JSON}")


if __name__ == "__main__":
    asyncio.run(main())
