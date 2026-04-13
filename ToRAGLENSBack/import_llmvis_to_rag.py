import os
import sys
import json
import asyncio
from PIL import Image
import torch
import uuid

# 导入现有系统代码
from rag_collection_manager import MultimodalRAGManager, PaperRAGManager

async def import_llmvis_data():
    input_file = "llmvis_enhanced_afterllm.json"
    collection_name = "LLMvisDataset"
    
    if not os.path.exists(input_file):
        print(f"❌ 找不到文件: {input_file}")
        return
        
    with open(input_file, "r", encoding="utf-8") as f:
        figures = json.load(f)
        
    print(f"✅ 成功读取 {len(figures)} 条 llmvis 图片数据")
    
    # ------------------ 1. 导入论文 Markdown 文本数据 ------------------
    # 这一步会自动处理创建标准集合（384维度）并进行分段插入
    print("\n--- 开始加载 Markdown 文本数据 ---")
    paper_manager = PaperRAGManager(paper_md_path="md-llmvis")
    await paper_manager.initialize()
    # 使用 load_papers_to_collection 加载并分块 MD 文本
    await paper_manager.load_papers_to_collection(collection_name, reset_data=True)
    print("--- Markdown 文本数据加载完成 ---\n")

    # ------------------ 2. 获取刚才创建的集合 ------------------
    # 初始化管理器
    manager = MultimodalRAGManager()
    await manager.initialize()
    
    collection = await manager.get_collection(collection_name)
    if not collection:
        print(f"❌ 获取集合 {collection_name} 失败！")
        return
        
    print(f"📂 目标集合 {collection_name} 目前共有 {collection.count()} 条数据")

    # ------------------ 3. 导入图片多模态数据 ------------------
    print("--- 开始导入图片多模态数据 ---")
    
    # 逐条添加数据
    added_count = 0
    failed_count = 0
    
    for i, figure in enumerate(figures):
        try:
            if not figure.get('llm_processed', False):
                print(f"⚠️  跳过第 {i+1} 条: llm_processed 为 False")
                continue
                
            # 提取元数据
            source_md = figure.get("source_md", "unknown_md")
            paper_id = source_md.replace("MinerU_markdown_", "").replace(".md", "")
            
            # 使用唯一 ID
            figure_id = f"llmvis_{paper_id}_{i}"
            
            abs_image_path = figure.get("save_path", "")
            title = str(figure.get("title", ""))
            summary = str(figure.get("concise_summary", ""))
            insight = str(figure.get("inferred_insight", ""))
            keywords_list = figure.get("key_entities", [])
            
            # 构建多模态内容 (这就是会被转化为向量的文本内容)
            multimodal_content = f"Title: {title}\nSummary: {summary}\nInsight: {insight}"
            
            # 存入完整的 JSON 方便前端解析
            metadata = {
                "id": figure_id,
                "paper_id": paper_id,
                "savepath": abs_image_path,
                "image_path": abs_image_path,
                "keywords": manager._sanitize_metadata_value(keywords_list),
                "source": "llmvis",
                "type": "picture",
                "full_json": json.dumps(figure, ensure_ascii=False)
            }
            
            if multimodal_content.strip():
                # 统一使用 Chroma 默认的 Text Embedding (384维) 来存图文分析结果，
                # 保证它和上面用 PaperRAGManager 存入的 MD 文本维度一致，可以混合检索。
                collection.add(
                    ids=[figure_id],
                    metadatas=[metadata],
                    documents=[multimodal_content]
                )
                print(f"   [{i+1}/{len(figures)}] ✅ 添加成功 (图文解析): {title[:20]}...")
                
            added_count += 1
            
        except Exception as e:
            print(f"   [{i+1}/{len(figures)}] ❌ 添加失败: {e}")
            failed_count += 1
            
    print("\n===============================")
    print(f"🚀 导入完成！")
    print(f"   成功插入图片分析数据: {added_count} 条")
    print(f"   失败图片: {failed_count} 条")
    print(f"   集合 {collection_name} 现在共有(含文本块): {collection.count()} 条数据")
    print("===============================")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    asyncio.run(import_llmvis_data())