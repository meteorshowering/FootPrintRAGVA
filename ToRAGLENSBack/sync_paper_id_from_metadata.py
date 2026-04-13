#!/usr/bin/env python3
"""
将 multimodal2text_embeddings_2d.json 中每条记录的顶层 paper_id
用 metadata.paperid 覆盖（与 RAG 本地过滤 query_by_local_filter 一致）。

默认处理：
  - ToRAGLENSBack/multimodal2text_embeddings_2d.json（后端 RAG）
  - mapfront/public/multimodal2text_embeddings_2d.json（前端底图 fetch）
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path


def sync_one(path: Path) -> None:
    if not path.is_file():
        print(f"跳过（不存在）: {path}")
        return

    backup = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup)
    print(f"已备份: {backup}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise SystemExit(f"{path}: 根节点应为 JSON 数组")

    updated = 0
    skipped = 0
    for item in data:
        if not isinstance(item, dict):
            skipped += 1
            continue
        meta = item.get("metadata")
        if not isinstance(meta, dict):
            skipped += 1
            continue
        pid = meta.get("paperid")
        if pid is None or (isinstance(pid, str) and not pid.strip()):
            skipped += 1
            continue
        item["paper_id"] = pid.strip() if isinstance(pid, str) else pid
        updated += 1

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已写回: {path}")
    print(f"  已更新 paper_id: {updated} 条；未改: {skipped} 条")


def main() -> None:
    back_root = Path(__file__).resolve().parent
    targets = [
        back_root / "multimodal2text_embeddings_2d.json",
        back_root.parent / "mapfront" / "public" / "multimodal2text_embeddings_2d.json",
    ]
    for p in targets:
        sync_one(p)


if __name__ == "__main__":
    main()
