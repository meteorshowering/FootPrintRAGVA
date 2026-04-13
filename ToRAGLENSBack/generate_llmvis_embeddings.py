import asyncio
import os
import sys
import json
import shutil
from pathlib import Path
from embedding_dimension_reduction import RAGEmbeddingProcessor

async def main():
    processor = RAGEmbeddingProcessor()
    
    # 处理RAG集合
    print("开始处理 LLMvisDataset 的降维...")
    result = await processor.process_rag_collection(
        collection_name="LLMvisDataset",
        use_existing_embeddings=True,  # 优先使用现有的嵌入向量
        reduction_method="tsne",  # 使用t-SNE降维
        output_file="LLMvisDataset_embedding.json"
    )
    
    if not result:
        print("❌ 处理失败或集合为空")
        return
        
    print("降维处理完成，开始修正 paper_id...")
    # 按照 sync_paper_id_from_metadata.py 的逻辑修正 paper_id
    back_root = Path(__file__).resolve().parent
    file_path = back_root / "LLMvisDataset_embedding.json"
    
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
        
    updated = 0
    for item in data:
        meta = item.get("metadata", {})
        # 从 metadata 中提取 paper_id，兼容 paperid, paper_id, paper_name 等
        pid = meta.get("paper_id") or meta.get("paperid") or meta.get("paper_name")
        if pid:
            item["paper_id"] = str(pid).strip()
            updated += 1
            
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"已修正 paper_id: {updated} 条。")
    
    # 拷贝到前端 public 目录
    front_dest = back_root.parent / "mapfront" / "public" / "LLMvisDataset_embedding.json"
    shutil.copy2(file_path, front_dest)
    print(f"已将 LLMvisDataset_embedding.json 复制到前端目录: {front_dest}")

if __name__ == "__main__":
    asyncio.run(main())
