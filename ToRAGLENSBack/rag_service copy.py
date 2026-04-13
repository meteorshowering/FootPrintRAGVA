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

class RAGService:
    def __init__(self, collection_name: str = None, multimodal_collection_name: str = None):
        self.rag_memory: Optional[ChromaDBVectorMemory] = None
        # ✨ 新增：多模态内存数据库
        self.multimodal_memory: Optional[ChromaDBVectorMemory] = None
        self.chroma_client = None
        self.raw_collection = None 
        # ✨ 新增：多模态原始集合
        self.multimodalexisting_collection = None
        self.multimodal_collection = None
        self.model_client = None
        self.initialized = False
        self.figures_file_path = None
        self.db_persistence_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".chromadb_autogen")
        # ✨ 支持传入自定义集合名称，默认为新的集合名称
        self.collection_name = collection_name or "scientific_rag_collection_new"
        # ✨ 新增：多模态集合名称，支持自定义
        self.multimodal_collection_name = multimodal_collection_name or "scientific_multimodal_collection_new"
        
        # ✨ 新增：本地数据缓存 (直接存 JSON 对象)
        self.local_data_cache: List[Dict[str, Any]] = []
        
        # ✨ 新增：CLIP模型相关
        self.clip_model = None
        self.clip_processor = None
        self.device = None 
    
    async def initialize(self, figures_file_path: Optional[str] = None, collection_name: str = None, multimodal_collection_name: str = None, reset_data: bool = False):
        if self.initialized: return
        
        # 如果传入了集合名称，使用传入的集合名称
        if collection_name:
            self.collection_name = collection_name
        if multimodal_collection_name:
            self.multimodal_collection_name = multimodal_collection_name
        
        # 1. 设置路径
        # self.figures_file_path = "c:/liuxingyu/multisubspace-data/figures_afterllm.json"
        self.figures_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "multimodal2text_embeddings_2d.json")
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

        # 3. 初始化 ChromaDB (用于左路语义搜索)
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4o",
            base_url="http://38.147.105.35:3030/v1",
            api_key="sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
        )
        self.chroma_client = chromadb.PersistentClient(path=self.db_persistence_path)
        
        # 初始化文本rag的集合
        # 检查集合是否存在
        try:
            existing_collection = self.chroma_client.get_collection(name=self.collection_name)
            collection_exists = True
        except Exception as e:
            collection_exists = False
        
        # 如果重置数据或集合不存在，创建新集合
        if reset_data or not collection_exists:
            if collection_exists:
                print(f"   删除旧集合: {self.collection_name}")
                self.chroma_client.delete_collection(name=self.collection_name)
            # 创建新集合
            self.raw_collection = self.chroma_client.create_collection(name=self.collection_name)
            print(f"🔄 重新从 {self.figures_file_path} 加载向量数据...")
            await self._load_data_to_memory()
            print("✅ 向量数据重新加载完成。")

            print(f"   成功创建新集合: {self.collection_name}")
        else:
            # 使用现有集合
            self.raw_collection = existing_collection
            print(f"   使用现有集合: {self.collection_name}，当前记录数: {self.raw_collection.count()}")
        
        self.rag_memory = ChromaDBVectorMemory(
            config=PersistentChromaDBVectorMemoryConfig(
                collection_name=self.collection_name,
                persistence_path=self.db_persistence_path,
                k=4, 
                score_threshold=0.3,
            )
        )
        #多模态的rag集合
        # 4. ✨ 新增：首先初始化 CLIP 模型，确保多模态功能可用
        await self._initialize_clip_model()
        
        # 5. ✨ 新增：初始化多模态内存数据库（带版本检查与兼容性处理）
        print("🔍 初始化多模态集合...")

        
        try:
            # 尝试获取现有集合
            self.multimodalexisting_collection = self.chroma_client.get_collection(name=self.multimodal_collection_name)
            multimodalcollection_exists = True
            
            # 获取集合元数据，检查嵌入维度是否兼容
            collection_metadata = self.multimodalexisting_collection.metadata or {}
            embedding_dimension = collection_metadata.get("embedding_dimension", 0)
            
            # 验证兼容性：嵌入维度必须为512（CLIP模型生成的维度）
            if embedding_dimension == 512:
                compatible_version = True
                print(f"   发现兼容的多模态集合，嵌入维度: {embedding_dimension}")
            else:
                print(f"   发现不兼容的多模态集合，嵌入维度: {embedding_dimension} (需要512)")
        except Exception as e:
            print(f"   检查现有集合失败: {e} (将创建新集合)")
        
        # 如果集合不存在、不兼容或需要重置，则创建新集合
        if not multimodalcollection_exists or not compatible_version or reset_data:
            if multimodalcollection_exists:
                # 删除旧集合
                try:
                    self.chroma_client.delete_collection(name=self.multimodal_collection_name)
                    print(f"   删除旧集合: {self.multimodal_collection_name}")
                except Exception as e:
                    print(f"   删除旧集合失败: {e} (忽略)")
            
            # 创建新的支持CLIP嵌入的集合
            self.multimodal_collection = self.chroma_client.create_collection(
                name=self.multimodal_collection_name,
                metadata={"embedding_dimension": 512}  # 显式指定CLIP的512维嵌入
            )
            print(f"🔄 加载多模态数据，确保使用CLIP嵌入...")
            await self._load_multimodal_data_to_memory()
            print(f"✅ 多模态数据加载完成，共 {self.multimodal_collection.count()} 条记录")

            print(f"   成功创建支持512维嵌入的新集合")
        else:
            # 使用兼容的现有集合
            print(f"   使用现有的兼容多模态集合")
        
        self.multimodal_memory = ChromaDBVectorMemory(
            config=PersistentChromaDBVectorMemoryConfig(
                collection_name=self.multimodal_collection_name,
                persistence_path=self.db_persistence_path,
                k=4, 
                score_threshold=0.1,
            )
        )
        
        
        
        self.initialized = True
    
    # ... _sanitize_metadata_value 保持不变 ...
    def _sanitize_metadata_value(self, value: Any) -> Union[str, int, float, bool]:
        if value is None: return ""
        if isinstance(value, (list, dict, tuple)):
            return json.dumps(value, ensure_ascii=False)
        return value
    
    # ✨ 新增：初始化 CLIP 模型
    async def _initialize_clip_model(self):
        # 检查CLIP是否可用
        if not CLIP_AVAILABLE:
            print("[CLIP] CLIP模型不可用，跳过初始化")
            # 即使CLIP不可用，也要确保device变量被初始化
            self.device = "cpu"
            return False
            
        def _sync_init():
            try:
                print("📸 [CLIP] 正在初始化 CLIP 模型...")
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                # 使用轻量级的 CLIP 模型
                self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
                self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                print(f"✅ [CLIP] 模型初始化完成，运行在 {self.device} 设备上")
                return True
            except Exception as e:
                print(f"❌ [CLIP] 模型初始化失败: {e}")
                # 初始化失败时，确保device变量有默认值
                self.device = "cpu"
                return False
        
        return await asyncio.to_thread(_sync_init)
    
    # ✨ 新增：提取图片特征
    async def _extract_image_features(self, image_path: str) -> Optional[List[float]]:
        if not self.clip_model or not self.clip_processor or not CLIP_AVAILABLE:
            return None
        
        def _sync_extract():
            try:
                image = Image.open(image_path).convert("RGB")
                inputs = self.clip_processor(images=image, return_tensors="pt").to(self.device)
                with torch.no_grad():
                    features = self.clip_model.get_image_features(**inputs)
                # 归一化并转换为列表
                features = features.cpu().numpy().tolist()[0]
                return features
            except Exception as e:
                print(f"❌ [CLIP] 提取图片特征失败 ({image_path}): {e}")
                return None
        
        return await asyncio.to_thread(_sync_extract)

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
    
    # ✨ 新增：加载多模态数据到内存
    async def _load_multimodal_data_to_memory(self):
        if not os.path.exists(self.figures_file_path): return
        try:
            with open(self.figures_file_path, "r", encoding="utf-8") as f:
                figures = json.load(f)
            
            # 检查多模态集合是否已经包含数据，如果有则不重复加载
            if self.multimodal_collection.count() > 0:
                print(f"📸 多模态集合 {self.multimodal_collection_name} 中已有 {self.multimodal_collection.count()} 条数据，跳过加载。")
                return
            
            count = 0
            for figure in figures:
                figure_id = str(figure.get("id", f"unknown_{count}"))
                paper_id = str(figure.get("paper_id", "unknown"))
                keywords_list = figure.get("key_entities", []) 
                
                title = str(figure.get("title", ""))
                summary = str(figure.get("concise_summary", ""))
                insight = str(figure.get("inferred_insight", ""))
                if isinstance(summary, list): summary = " ".join(map(str, summary))
                if isinstance(insight, list): insight = " ".join(map(str, insight))
                
                # 处理图片路径
                raw_savepath = figure.get("save_path", "") 
                abs_image_path = ""
                if raw_savepath and isinstance(raw_savepath, str):
                    if os.path.exists(raw_savepath):
                        abs_image_path = raw_savepath
                    else:
                        # 检查allimages目录下的图片
                        # allimages_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "allimages")
                        allimages_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagecase")
                        possible_path = os.path.join(allimages_dir, raw_savepath)
                        if os.path.exists(possible_path):
                            abs_image_path = possible_path
                        else:
                            # 尝试其他可能的路径
                            base_dir = os.path.dirname(self.figures_file_path)
                            possible_path = os.path.join(base_dir, raw_savepath)
                            if os.path.exists(possible_path):
                                abs_image_path = possible_path

                # 提取图片特征（只有CLIP可用时才提取）
                image_features = None
                if CLIP_AVAILABLE and abs_image_path and os.path.exists(abs_image_path):
                    image_features = await self._extract_image_features(abs_image_path)
                
                # 构建多模态内容
                multimodal_content = f"Title: {title}\nSummary: {summary}\nInsight: {insight}"
                
                metadata = {
                    "id": figure_id,
                    "paper_id": paper_id,
                    "savepath": str(raw_savepath),
                    "image_path": abs_image_path,
                    "keywords": self._sanitize_metadata_value(keywords_list),
                    "full_json": json.dumps(figure, ensure_ascii=False)
                }
                
                # 只有当有文本内容或图片特征时才添加
                if multimodal_content.strip() or image_features:
                    # 如果有图片特征，直接使用CLIP嵌入添加到集合
                    if image_features:
                        # 使用CLIP嵌入添加到集合
                        self.multimodal_collection.add(
                            ids=[figure_id],
                            embeddings=[image_features],
                            metadatas=[metadata],
                            documents=[multimodal_content]
                        )
                        count += 1
                        print(f"   添加多模态数据: {figure_id} (CLIP嵌入)")
                    else:
                        # 没有图片特征，使用文本嵌入
                        await self.multimodal_memory.add(
                            MemoryContent(content=multimodal_content, mime_type=MemoryMimeType.TEXT, metadata=metadata)
                        )
                        count += 1
                        print(f"   添加多模态数据: {figure_id} (文本嵌入)")
            print(f"📸 成功加载 {count} 条多模态向量数据到集合 {self.multimodal_collection_name}。")
        except Exception as e:
            print(f"❌ 加载多模态数据出错: {e}")

    # =========================================================================
    #  接口 A: 语义检索 (查库)
    # =========================================================================
    async def query_by_semantic(self, query_text: str, n_results: int = 5, score_threshold: float = 0.4) -> List[Dict[str, Any]]:
        if not self.initialized: await self.initialize()
        def _sync_semantic():
            try:
                # 使用局部变量避免闭包问题
                local_threshold = score_threshold
                max_attempts = 2
                current_attempt = 0
                final_results = None
                
                while current_attempt < max_attempts:
                    # 每次尝试获取更多结果
                    initial_n = int(n_results * (3 + current_attempt))
                    raw_results = self.raw_collection.query(
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
                    
                    # 检查过滤后的结果数量
                    if len(filtered_results["ids"][0]) >= int(n_results):
                        # 如果够了，直接返回
                        final_results = filtered_results
                        break
                    else:
                        # 如果不够，降低分数阈值并继续尝试
                        local_threshold *= 0.8
                        current_attempt += 1
                
                # 如果最终结果还是不够，返回所有过滤后的结果
                if final_results is None:
                    final_results = filtered_results
                
                return final_results
            except Exception as e:
                print(f"❌ Semantic Query Error: {e}")
                return None
        results = await asyncio.to_thread(_sync_semantic)
        return self._format_results(results, is_semantic=True)

    # =========================================================================
    #  ✨ 接口 B: 本地内存检索 (不查库，只查 List)
    # =========================================================================
    async def query_by_local_filter(self, keywords: List[str] = None, paper_id: str = None, figure_type: str = None) -> List[Dict[str, Any]]:
        """
        直接在 self.local_data_cache (JSON 列表) 中进行 Python 过滤。
        精准、快速、无类型烦恼。
        """
        if not self.initialized: await self.initialize()
        
        results = []
        
        print(f"⚡ [Local Search] 在 {len(self.local_data_cache)} 条数据中过滤: P={paper_id}, K={keywords}")
        
        for item in self.local_data_cache:
            # 1. Paper ID 匹配 (转字符串比较，防坑)
            if paper_id:
                # 如果 item 里没 paper_id 或者 不相等，跳过
                item_pid = str(item.get("paper_id", ""))
                if item_pid != str(paper_id):
                    continue
            
            # 2. Figure Type 匹配
            if figure_type:
                item_type = str(item.get("visual_type", "") or item.get("figure_type", ""))
                if str(figure_type).lower() not in item_type.lower():
                    continue

            # 3. Keywords 匹配 (求交集)
            if keywords:
                # 你的 json 里可能是 "key_entities" 或 "keywords"
                item_kws = item.get("key_entities", [])
                # 确保 item_kws 是列表
                if not isinstance(item_kws, list): item_kws = []
                
                # 只要命中一个词就保留
                # 使用 set intersection
                common = set(keywords) & set(item_kws)
                if not common:
                    continue # 一个都没命中，跳过

            # --- 匹配成功 ---
            # 构造返回格式，使其与 query_by_semantic 的输出格式一致
            content = {
                        "title": item.get("title", ""),
                        "summary": item.get("concise_summary", ""),
                        "insight": item.get("inferred_insight", "")
                    }

            results.append({
                "id": str(item.get("id", "")),
                "content": content, # 原始对象
                "score": 1.0,    # 规则命中，置信度 100%
                "metadata": item
            })
            
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
        
        def _sync_multimodal():
            try:
                # 仅支持图片检索
                if query_image_path and os.path.exists(query_image_path):
                    # 检查PIL和CLIP是否可用
                    if not PIL_AVAILABLE or not CLIP_AVAILABLE or not self.clip_model or not self.clip_processor:
                        print("[Warning] PIL或CLIP模型不可用，无法处理图片检索请求")
                        return {"ids": [], "metadatas": [], "documents": [], "distances": []}
                    
                    # 提取查询图片的特征
                    try:
                        image = Image.open(query_image_path).convert("RGB")
                        inputs = self.clip_processor(images=image, return_tensors="pt").to(self.device)
                        with torch.no_grad():
                            query_features = self.clip_model.get_image_features(**inputs)
                        query_features = query_features.cpu().numpy().tolist()[0]
                        
                        # 直接使用CLIP嵌入进行查询
                        print("[Info] 使用CLIP模型提取图片特征，进行真正的多模态检索")
                        return self.multimodal_collection.query(
                            query_embeddings=[query_features],
                            n_results=int(n_results),
                            include=["metadatas", "documents", "distances"]
                        )
                    except Exception as img_e:
                        print(f"[Warning] 处理图片检索时出错: {img_e}")
                        return {"ids": [], "metadatas": [], "documents": [], "distances": []}
                else:
                    # 没有提供有效的图片路径
                    print("[Warning] 未提供有效的图片路径，无法进行多模态检索")
                    return {"ids": [], "metadatas": [], "documents": [], "distances": []}
            except Exception as e:
                print(f"❌ Multimodal Query Error: {e}")
                # Return empty result structure instead of None to prevent TypeError when calling len()
                return {"ids": [], "metadatas": [], "documents": [], "distances": []}
        
        # 调用_sync_multimodal函数并格式化结果
        results = await asyncio.to_thread(_sync_multimodal)
        return self._format_results(results, is_semantic=True)

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
            # 尝试从full_json中解析关键信息
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
            else:
                # 如果没有full_json，使用文档文本
                content_obj = {"text": doc if doc else ""}
            formatted.append({
                "id": img_id, 
                "content": content_obj, 
                "score": score, 
                "metadata": full_obj
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
        
        
        print(f"   - Paper ID: {meta.get('paper_id')} (Raw Type: {type(meta.get('paper_id'))})")
        print(f"   - Image Path: {meta.get('save_path')}")
        print(f"   - Keywords: {meta.get('key_entities')}")
        print(f"    -sight: {content.get('insight')}")
    
    # 验证 content 是字典还是字符串


if __name__ == "__main__":
    async def test():
        service = await get_rag_service()
        # print("Test Semantic:")
        # res = await s.query_by_semantic(query_text="PM2.5")
        # for i in res:
        #     print(i["content"])
        # test_paper_id = "2" 
        # print(f"\n[B1] 测试 Paper ID 过滤: '{test_paper_id}'")
        
        # id_results = await service.query_by_local_filter(paper_id=test_paper_id)
        # print_result_summary(f"本地过滤 (Paper ID={test_paper_id})", id_results, expected_count=">=1")

        # B2. 测试 Keywords (列表交集匹配)
        # 请根据你的真实数据修改，比如 "PM2.5", "Air Quality"
        # test_keyword = ["PM2.5", "Air Quality"] 
        # print(f"\n[B2] 测试 Keywords 过滤: {test_keyword}")
        
        # kw_results = await service.query_by_local_filter(keywords=test_keyword)
        # print_result_summary(f"本地过滤 (Keywords={test_keyword})", kw_results, expected_count=">=1")

        # B3. 测试 混合过滤 (ID + Keyword)
        # print(f"\n[B3] 测试 混合过滤: ID='{test_paper_id}' + KW={test_keyword}")
        
        # mix_results = await service.query_by_local_filter(paper_id=test_paper_id, keywords=test_keyword)
        # print_result_summary("本地过滤 (混合)", mix_results, expected_count="取决于数据")

        # B4. 测试 鲁棒性 (数字 ID 转字符串)
        test_int_id = 2 # 传入整数 10
        print(f"\n[B4] 测试 鲁棒性: 传入整数 ID={test_int_id}")
        
        robust_results = await service.query_by_local_filter(paper_id=test_int_id)
        print_result_summary(f"本地过滤 (Int ID={test_int_id})", robust_results, expected_count="应与 B1 相同")
        
        query = "SO2空气污染"
        semantic_results = await service.query_by_semantic(query_text=query, n_results=3)
        print_result_summary(f"语义搜索 (Query={query})", semantic_results, expected_count="=3")

    
    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        pass