#!/usr/bin/env python3
"""
【功能】从本地 Chroma（.chromadb_autogen）全量读取集合 → 降维 → 生成前端底图用 2D 嵌入 JSON → 写入后端并复制到 mapfront/public。

与前端 EnhancedRiverChart 引用的文件名一致：
  - LLMvisDataset      → LLMvisDataset_embedding.json
  - multimodal2text    → multimodal2text_embeddings_2d.json

用法（在 ToRAGLENSBack 目录下）:
  python regenerate_rag_embedding_maps.py
  python regenerate_rag_embedding_maps.py --only LLMvisDataset
  python regenerate_rag_embedding_maps.py --only multimodal2text
  python regenerate_rag_embedding_maps.py --no-api   # Chroma 无嵌入的条目直接跳过，不调用 embedding API

【长期价值】运维/数据管道可保留，建议作为「官方」重建底图入口；与 embedding_dimension_reduction.py 配套。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import sys
from pathlib import Path

# 保证可导入同目录下的 embedding_dimension_reduction
BACK_ROOT = Path(__file__).resolve().parent
if str(BACK_ROOT) not in sys.path:
    sys.path.insert(0, str(BACK_ROOT))

from embedding_dimension_reduction import RAGEmbeddingProcessor

FRONT_PUBLIC = BACK_ROOT.parent / "mapfront" / "public"

TASKS = [
    ("LLMvisDataset", "LLMvisDataset_embedding.json"),
    ("multimodal2text", "multimodal2text_embeddings_2d.json"),
]


def _sync_paper_id_llmvis(file_path: Path) -> None:
    """与 generate_llmvis_embeddings.py 一致：顶层 paper_id 便于前端聚类。"""
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    updated = 0
    for item in data:
        meta = item.get("metadata") or {}
        pid = meta.get("paper_id") or meta.get("paperid") or meta.get("paper_name")
        if pid:
            item["paper_id"] = str(pid).strip()
            updated += 1
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"   已修正 paper_id: {updated} 条。")


async def run_one(
    processor: RAGEmbeddingProcessor,
    collection: str,
    outfile: str,
    *,
    fill_missing: bool,
    reduction: str,
) -> bool:
    out_path = BACK_ROOT / outfile
    print(f"\n=== 集合 {collection} → {out_path.name} ===")
    result = await processor.process_rag_collection(
        collection_name=collection,
        use_existing_embeddings=True,
        reduction_method=reduction,
        output_file=str(out_path),
        fill_missing_embeddings=fill_missing,
    )
    if not result:
        print(f"[ERROR] {collection} 无输出（集合为空或全部失败）")
        return False

    if collection == "LLMvisDataset":
        _sync_paper_id_llmvis(out_path)

    dest = FRONT_PUBLIC / outfile
    FRONT_PUBLIC.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_path, dest)
    print(f"[OK] 已复制到前端: {dest} （共 {len(result)} 条）")
    return True


async def main_async(args: argparse.Namespace) -> None:
    processor = RAGEmbeddingProcessor()
    fill_missing = not args.no_api
    if not fill_missing:
        print("[INFO] 已禁用 API 补全：仅导出 Chroma 中已有 embedding 的条目。")

    tasks = TASKS
    if args.only:
        name = args.only.strip()
        tasks = [(c, f) for c, f in TASKS if c == name]
        if not tasks:
            print(f"[ERROR] 未知集合: {name}，可选: LLMvisDataset, multimodal2text")
            sys.exit(1)

    ok = 0
    for collection, outfile in tasks:
        if await run_one(
            processor,
            collection,
            outfile,
            fill_missing=fill_missing,
            reduction=args.method,
        ):
            ok += 1

    print(f"\n完成：成功 {ok}/{len(tasks)} 个文件。")


def main() -> None:
    p = argparse.ArgumentParser(description="从 Chroma 重建 RAG 2D 嵌入 JSON 并同步到前端 public")
    p.add_argument(
        "--only",
        type=str,
        default="",
        help="只处理一个集合: LLMvisDataset 或 multimodal2text",
    )
    p.add_argument(
        "--no-api",
        action="store_true",
        help="不调用嵌入 API；Chroma 未存储向量的条目将被跳过",
    )
    p.add_argument(
        "--method",
        type=str,
        default="tsne",
        choices=("tsne", "pca"),
        help="降维方法",
    )
    args = p.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
