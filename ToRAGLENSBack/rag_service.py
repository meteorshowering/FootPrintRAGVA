import re
from typing import List, Dict, Any, Optional, Union
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
    
    # ... _sanitize_metadata_value 保持不变 ...
    def _sanitize_metadata_value(self, value: Any) -> Union[str, int, float, bool]:
        if value is None: return ""
        if isinstance(value, (list, dict, tuple)):
            return json.dumps(value, ensure_ascii=False)
        return value
    
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
    async def query_by_semantic(self, query_text: str, n_results: int = 3, score_threshold: float = 0.1, collection_name: str = None, use_multimodal: bool = False) -> List[Dict[str, Any]]:
        if not self.initialized: await self.initialize()
        
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
                return []
        
        # 如果没有指定集合名称，使用实例初始化时设置的默认集合
        if not target_collection:
            if self.raw_collection:
                target_collection = self.raw_collection
                print(f"   使用实例默认集合: {self.collection_name}")
            else:
                print("❌ 没有可用的集合，请先确保集合已创建")
                return []
        
        # 检查集合是否可用
        if not target_collection:
            print("❌ 集合不可用，请先确保集合已创建")
            return []
        
        def _sync_semantic():
            try:
                # 使用局部变量避免闭包问题
                local_threshold = score_threshold
                # 直接获取所需的 n_results 数量，不再刻意放大范围
                initial_n = int(n_results)
                
                raw_results = target_collection.query(
                    query_texts=[query_text],
                    n_results=initial_n,
                    include=["metadatas", "documents", "distances"]
                )
                
                # 如果结果数量不足，直接返回
                if not raw_results or not raw_results.get("ids") or not raw_results["ids"][0]:
                    return raw_results
                
                # 应用分数阈值过滤
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
                
                for i, (id, metadata, document, distance) in enumerate(zip(ids, metadatas, documents, distances)):
                    # 计算分数：1/(1+distance)
                    score = 1.0 / (1.0 + float(distance))
                    if score >= local_threshold:
                        filtered_results["ids"][0].append(id)
                        filtered_results["metadatas"][0].append(metadata)
                        filtered_results["documents"][0].append(document)
                        filtered_results["distances"][0].append(distance)
                
                # 只返回前n_results个结果
                if len(filtered_results["ids"][0]) > int(n_results):
                    filtered_results["ids"][0] = filtered_results["ids"][0][:int(n_results)]
                    filtered_results["metadatas"][0] = filtered_results["metadatas"][0][:int(n_results)]
                    filtered_results["documents"][0] = filtered_results["documents"][0][:int(n_results)]
                    filtered_results["distances"][0] = filtered_results["distances"][0][:int(n_results)]
                
                return filtered_results
            except Exception as e:
                print(f"❌ Semantic Query Error: {e}")
                return None
        results = await asyncio.to_thread(_sync_semantic)
        return self._format_results(results, is_semantic=True)

    # =========================================================================
    #  接口 C: 精确关键字检索 (非向量相似度，纯文本匹配)
    # =========================================================================
    async def query_by_exact_match(self, query_text: str, n_results: int = 10, collection_name: str = None) -> List[Dict[str, Any]]:
        """
        在本地数据缓存中进行精确的子串匹配检索（非向量相似度）。
        适合需要包含特定关键词的硬性召回。
        """
        if not self.initialized: await self.initialize()
        
        if not query_text or not query_text.strip():
            return []
            
        search_term = query_text.strip().lower()
        results = []
        
        print(f"⚡ [Exact Search] 在本地数据中进行文本匹配: '{search_term}'")
        
        for item in self.local_data_cache:
            # 提取包含整个 chunk 的 content
            content_text = str(item.get("content", "")).lower()
            
            # 判断是否命中，采用纯文本子串包含匹配（只匹配 content）
            if search_term in content_text:
                
                # 解析真实元数据以构造良好的内容结构
                real_item = item
                meta = item.get("metadata", {})
                if "full_json" in meta:
                    try:
                        real_item = json.loads(meta["full_json"])
                    except:
                        pass
                
                # 构造返回格式，与 query_by_semantic 一致
                # 如果是图片(有full_json)，提取title, summary, insight
                if "full_json" in meta:
                    content = {
                        "title": real_item.get("title", item.get("title", "No Title")),
                        "summary": real_item.get("concise_summary", item.get("summary", "")),
                        "insight": real_item.get("inferred_insight", item.get("insight", ""))
                    }
                else:
                    # 文本块
                    raw_content = item.get("content", "")
                    content = {
                        "title": meta.get("paper_name", meta.get("file_name", "Text Chunk")),
                        "text": raw_content,
                        "summary": raw_content[:150] + "..." if len(raw_content) > 150 else raw_content
                    }
                
                results.append({
                    "id": str(item.get("id", "")),
                    "content": content,
                    "score": 1.0,  # 纯文本精确匹配，得分定为 1.0
                    "metadata": item
                })
                
        # 按需截断
        if n_results and n_results > 0:
            results = results[:n_results]
            
        print(f"   ✅ 精确匹配到 {len(results)} 条数据")
        return results

    # =========================================================================
    #  ✨ 接口 B: 本地内存检索 (不查库，只查 List)
    # =========================================================================
    async def query_by_local_filter(
        self,
        keywords: List[str] = None,
        paper_id: str = None,
        figure_type: str = None,
        n_results: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        直接在 self.local_data_cache (JSON 列表) 中进行 Python 过滤。
        精准、快速、无类型烦恼。
        """
        if not self.initialized: await self.initialize()
        
        # 🔒 安全检查：如果所有参数都是 None，返回空列表，避免返回所有数据
        if not paper_id and not keywords and not figure_type:
            print(f"⚠️ [Local Search] 警告：所有过滤参数均为 None，返回空列表以避免返回所有数据")
            return []
        
        results = []
        
        print(f"⚡ [Local Search] 在 {len(self.local_data_cache)} 条数据中过滤: P={paper_id}, K={keywords}")
        
        for item in self.local_data_cache:
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
        results1 = await service.query_by_semantic(query_text=query1, n_results=5, collection_name="multimodal2text")
        print_result_summary(f"语义搜索 (Query={query1})", results1, expected_count=">=1")
        
        # 测试2: 论文标题搜索
        print("\n[测试2] 论文标题搜索")
        query2 = "biomass burning"
        results2 = await service.query_by_semantic(query_text=query2, n_results=3, collection_name="multimodal2text")
        print_result_summary(f"语义搜索 (Query={query2})", results2, expected_count=">=1")
        
        # 测试3: 图片相关搜索
        print("\n[测试3] 图片相关搜索")
        query3 = "figure chart graph"
        results3 = await service.query_by_semantic(query_text=query3, n_results=3, collection_name="multimodal2text")
        print_result_summary(f"语义搜索 (Query={query3})", results3, expected_count=">=1")
        
        # 测试4: 具体论文内容搜索
        print("\n[测试4] 具体论文内容搜索")
        query4 = "air quality China"
        results4 = await service.query_by_semantic(query_text=query4, n_results=3, collection_name="multimodal2text")
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