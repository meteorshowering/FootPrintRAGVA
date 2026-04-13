import os
import json
import asyncio
from typing import List, Dict, Any, Optional, Union
import chromadb
from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig
from autogen_core.memory import MemoryContent, MemoryMimeType
from autogen_ext.models.openai import OpenAIChatCompletionClient
import sys
class RAGCollectionManager:
    def __init__(self, db_persistence_path: Optional[str] = None):
        self.chroma_client = None
        self.db_persistence_path = db_persistence_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".chromadb_autogen")
        self.model_client = None
        self.initialized = False
    
    async def initialize(self):
        if self.initialized:
            return
        
        # 初始化ChromaDB客户端
        self.chroma_client = chromadb.PersistentClient(path=self.db_persistence_path)
        
        # 初始化模型客户端
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4o",
            base_url="http://38.147.105.35:3030/v1",
            api_key="sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
        )
        
        self.initialized = True
    
    def _sanitize_metadata_value(self, value: Any) -> Union[str, int, float, bool]:
        if value is None:
            return ""
        if isinstance(value, (list, dict, tuple)):
            return json.dumps(value, ensure_ascii=False)
        return value
    
    async def check_collection_exists(self, collection_name: str) -> bool:
        """检查集合是否存在"""
        if not self.initialized:
            await self.initialize()
        
        try:
            self.chroma_client.get_collection(name=collection_name)
            return True
        except Exception:
            return False
    
    async def create_collection(self, collection_name: str, embedding_dimension: Optional[int] = None) -> chromadb.Collection:
        """创建新集合"""
        if not self.initialized:
            await self.initialize()
        
        # 检查集合是否存在，如果存在则删除
        if await self.check_collection_exists(collection_name):
            await self.delete_collection(collection_name)
        
        # 创建新集合
        metadata = {}
        if embedding_dimension:
            metadata["embedding_dimension"] = embedding_dimension
        else:
            # 即使没有指定嵌入维度，也添加一个默认的元数据
            metadata["created_by"] = "rag_collection_manager"
        
        collection = self.chroma_client.create_collection(
            name=collection_name,
            metadata=metadata
        )
        
        print(f"✅ 成功创建集合: {collection_name}")
        return collection
    
    async def delete_collection(self, collection_name: str) -> bool:
        """删除集合"""
        if not self.initialized:
            await self.initialize()
        
        try:
            self.chroma_client.delete_collection(name=collection_name)
            print(f"✅ 成功删除集合: {collection_name}")
            return True
        except Exception as e:
            print(f"❌ 删除集合失败: {e}")
            return False
    
    async def get_collection(self, collection_name: str) -> Optional[chromadb.Collection]:
        """获取集合"""
        if not self.initialized:
            await self.initialize()
        
        try:
            return self.chroma_client.get_collection(name=collection_name)
        except Exception as e:
            print(f"❌ 获取集合失败: {e}")
            return None
    
    async def get_or_create_collection(self, collection_name: str, embedding_dimension: Optional[int] = None) -> chromadb.Collection:
        """获取集合，如果不存在则创建"""
        if await self.check_collection_exists(collection_name):
            collection = await self.get_collection(collection_name)
            if collection:
                print(f"✅ 使用现有集合: {collection_name}")
                return collection
        
        return await self.create_collection(collection_name, embedding_dimension)
    
    async def create_rag_memory(self, collection_name: str, k: int = 4, score_threshold: float = 0.3) -> ChromaDBVectorMemory:
        """创建RAG内存实例"""
        if not self.initialized:
            await self.initialize()
        
        return ChromaDBVectorMemory(
            config=PersistentChromaDBVectorMemoryConfig(
                collection_name=collection_name,
                persistence_path=self.db_persistence_path,
                k=k,
                score_threshold=score_threshold,
            )
        )
    
    async def add_data_to_collection(self, rag_memory: ChromaDBVectorMemory, content: str, metadata: Dict[str, Any]) -> bool:
        """向集合添加数据"""
        try:
            await rag_memory.add(
                MemoryContent(content=content, mime_type=MemoryMimeType.TEXT, metadata=metadata)
            )
            return True
        except Exception as e:
            print(f"❌ 添加数据失败: {e}")
            return False

class MultimodalRAGManager(RAGCollectionManager):
    def __init__(self, db_persistence_path: Optional[str] = None):
        super().__init__(db_persistence_path)
        # CLIP模型相关
        self.clip_model = None
        self.clip_processor = None
        self.device = None
    
    async def initialize_clip_model(self):
        """初始化CLIP模型"""
        # 检查CLIP是否可用
        try:
            from transformers import CLIPProcessor, CLIPModel
            import torch
            CLIP_AVAILABLE = True
        except ImportError:
            print("[CLIP] CLIP模型不可用，跳过初始化")
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
    
    async def extract_image_features(self, image_path: str) -> Optional[List[float]]:
        """提取图片特征"""
        if not self.clip_model or not self.clip_processor:
            return None
        
        def _sync_extract():
            try:
                from PIL import Image
                import torch
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
    
    async def create_multimodal_collection(self, collection_name: str) -> chromadb.Collection:
        """创建多模态集合"""
        # 创建支持CLIP嵌入的集合
        return await self.create_collection(collection_name, embedding_dimension=512)
    
    async def load_multimodal_data(self, collection_name: str, figures_file_path: str) -> int:
        """加载多模态数据到集合"""
        if not self.initialized:
            await self.initialize()
        
        # 初始化CLIP模型
        await self.initialize_clip_model()
        
        # 检查集合是否存在
        collection = await self.get_collection(collection_name)
        if not collection:
            print(f"❌ 集合 {collection_name} 不存在")
            return 0
        
        # 检查文件是否存在
        if not os.path.exists(figures_file_path):
            print(f"❌ 文件 {figures_file_path} 不存在")
            return 0
        
        try:
            import json
            from PIL import Image
            import torch
            from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig
            from autogen_core.memory import MemoryContent, MemoryMimeType
            
            # 读取数据
            with open(figures_file_path, "r", encoding="utf-8") as f:
                figures = json.load(f)
            
            # 检查集合是否已经包含数据
            if collection.count() > 0:
                print(f"📸 多模态集合 {collection_name} 中已有 {collection.count()} 条数据，跳过加载。")
                return collection.count()
            
            # 创建RAG内存实例
            rag_memory = await self.create_rag_memory(collection_name)
            
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
                        # 检查imagecase目录下的图片
                        imagecase_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagecase")
                        possible_path = os.path.join(imagecase_dir, raw_savepath)
                        if os.path.exists(possible_path):
                            abs_image_path = possible_path
                        else:
                            # 尝试其他可能的路径
                            base_dir = os.path.dirname(figures_file_path)
                            possible_path = os.path.join(base_dir, raw_savepath)
                            if os.path.exists(possible_path):
                                abs_image_path = possible_path
                
                # 提取图片特征（只有CLIP可用时才提取）
                image_features = None
                if self.clip_model and abs_image_path and os.path.exists(abs_image_path):
                    image_features = await self.extract_image_features(abs_image_path)
                
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
                        collection.add(
                            ids=[figure_id],
                            embeddings=[image_features],
                            metadatas=[metadata],
                            documents=[multimodal_content]
                        )
                        count += 1
                        print(f"   添加多模态数据: {figure_id} (CLIP嵌入)")
                    else:
                        # 没有图片特征，使用文本嵌入
                        await self.add_data_to_collection(rag_memory, multimodal_content, metadata)
                        count += 1
                        print(f"   添加多模态数据: {figure_id} (文本嵌入)")
            
            print(f"📸 成功加载 {count} 条多模态向量数据到集合 {collection_name}。")
            return count
        except Exception as e:
            print(f"❌ 加载多模态数据出错: {e}")
            return 0

class PaperRAGManager(RAGCollectionManager):
    def __init__(self, db_persistence_path: Optional[str] = None, paper_md_path: Optional[str] = None):
        super().__init__(db_persistence_path)
        self.paper_md_path = paper_md_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "paper_md")
    
    def _split_into_chunks(self, text: str, chunk_size: int = 2048, overlap: int = 200) -> List[str]:
        """将文本分割成块"""
        import time
        start_time = time.time()
        
        chunks = []
        current_pos = 0
        text_length = len(text)
        
        print(f"   开始分块: 文本长度={text_length}, 块大小={chunk_size}, 重叠={overlap}")
        
        while current_pos < text_length:
            # 找到块结束位置
            end_pos = min(current_pos + chunk_size, text_length)
            
            # 尝试在段落边界分割
            original_end_pos = end_pos
            
            # 优先在段落边界分割
            if end_pos < text_length:
                # 查找从当前位置到结束位置的所有段落边界
                para_ends = []
                pos = current_pos
                while True:
                    para_end = text.find('\n\n', pos)
                    if para_end == -1 or para_end >= end_pos:
                        break
                    para_ends.append(para_end)
                    pos = para_end + 2
                
                # 如果有段落边界，选择最接近结束位置的那个
                if para_ends:
                    # 找到最后一个段落结束位置
                    last_para_end = para_ends[-1]
                    # 确保段落结束位置至少在块的中间位置之后
                    if last_para_end > current_pos + chunk_size * 0.3:
                        end_pos = last_para_end + 2  # 包含段落结束符
                    else:
                        # 如果没有合适的段落边界，尝试在句子边界分割
                        # 搜索句号、问号、感叹号等句子结束符
                        sent_end = text.rfind('.', current_pos, end_pos)
                        if sent_end == -1:
                            sent_end = text.rfind('?', current_pos, end_pos)
                        if sent_end == -1:
                            sent_end = text.rfind('!', current_pos, end_pos)
                        if sent_end != -1 and sent_end > current_pos + chunk_size * 0.5:
                            end_pos = sent_end + 1
            
            # 提取块
            chunk = text[current_pos:end_pos].strip()
            
            # 确保块的开头是完整句子的开始
            if chunk:
                # 查找块中第一个句子开始位置
                # 跳过非字母字符，直到找到第一个大写字母
                start_idx = 0
                while start_idx < len(chunk) and not (chunk[start_idx].isalpha() and chunk[start_idx].isupper()):
                    start_idx += 1
                
                # 如果找到大写字母，从那里开始截取
                if start_idx < len(chunk):
                    # 尝试找到这个大写字母前面的句子结束符
                    prev_end_idx = chunk.rfind('.', 0, start_idx)
                    if prev_end_idx == -1:
                        prev_end_idx = chunk.rfind('?', 0, start_idx)
                    if prev_end_idx == -1:
                        prev_end_idx = chunk.rfind('!', 0, start_idx)
                    if prev_end_idx == -1:
                        prev_end_idx = chunk.rfind('\n\n', 0, start_idx)
                    
                    # 如果找到句子结束符，从结束符之后开始截取
                    if prev_end_idx != -1:
                        # 跳过结束符和空格
                        new_start_idx = prev_end_idx + 1
                        while new_start_idx < len(chunk) and chunk[new_start_idx].isspace():
                            new_start_idx += 1
                        if new_start_idx < len(chunk):
                            chunk = chunk[new_start_idx:].strip()
                    else:
                        # 如果没有找到句子结束符，不截取，视为是一句话
                        pass  # 保持原块不变
                
                if chunk:
                    chunks.append(chunk)
            
            # 更新当前位置，添加重叠
            # 确保 current_pos 能够正确前进，避免无限循环
            new_pos = end_pos - overlap
            # 如果新位置没有前进，或者已经接近文本末尾，直接前进到结束位置
            if new_pos <= current_pos or end_pos >= text_length - 1:
                current_pos = end_pos
            else:
                current_pos = new_pos
            
            # 防止位置回退
            if current_pos < 0:
                current_pos = 0
            
            # 检查是否应该结束循环
            if current_pos >= text_length:
                print(f"   达到文本末尾，结束分块")
                break
        
        split_time = time.time() - start_time
        print(f"   分块完成: 生成 {len(chunks)} 个块, 耗时 {split_time:.2f} 秒")
        
        return chunks
    
    async def process_paper_file(self, file_path: str) -> List[Dict[str, Any]]:
        """处理单个论文文件"""
        import time
        start_time = time.time()
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        print(f"   文件大小: {file_size} 字节")
        
        # 读取文件
        read_start = time.time()
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        read_time = time.time() - read_start
        print(f"   读取时间: {read_time:.2f} 秒")
        print(f"   内容长度: {len(content)} 字符")
        
        # 提取文件名（不含扩展名）
        file_name = os.path.basename(file_path)
        paper_name = os.path.splitext(file_name)[0]
        
        # 分割文本
        split_start = time.time()
        chunks = self._split_into_chunks(content)
        split_time = time.time() - split_start
        print(f"   分块数量: {len(chunks)}，分块时间: {split_time:.2f} 秒")
        
        # 生成块数据
        chunk_data = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{paper_name}_chunk_{i}"
            chunk_data.append({
                "id": chunk_id,
                "content": chunk,
                "metadata": {
                    "paper_name": paper_name,
                    "file_name": file_name,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk),
                    "type": "texture"
                }
            })
        
        total_time = time.time() - start_time
        print(f"   处理完成: {len(chunk_data)} 个块，总时间: {total_time:.2f} 秒")
        
        return chunk_data
    
    async def load_papers_to_collection(self, collection_name: str, reset_data: bool = False) -> int:
        """加载所有论文到集合"""
        if not self.initialized:
            await self.initialize()
        
        # 检查集合是否存在
        if reset_data or not await self.check_collection_exists(collection_name):
            # 创建新集合
            await self.create_collection(collection_name)
        
        # 获取集合
        collection = await self.get_collection(collection_name)
        if not collection:
            return 0
        
        # 创建RAG内存实例
        rag_memory = await self.create_rag_memory(collection_name)
        
        # 遍历所有MD文件
        processed_count = 0
        chunk_count = 0
        
        for root, dirs, files in os.walk(self.paper_md_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    print(f"📄 处理文件: {file}")
                    
                    # 处理文件
                    chunk_data = await self.process_paper_file(file_path)
                    
                    # 添加到集合
                    import time
                    add_start = time.time()
                    added_count = 0
                    for chunk in chunk_data:
                        success = await self.add_data_to_collection(
                            rag_memory,
                            chunk["content"],
                            chunk["metadata"]
                        )
                        if success:
                            added_count += 1
                    add_time = time.time() - add_start
                    chunk_count += added_count
                    print(f"   添加完成: {added_count} 个块, 添加时间: {add_time:.2f} 秒")
                    
                    processed_count += 1
        
        print(f"✅ 处理完成: {processed_count} 个文件, {chunk_count} 个块")
        return chunk_count

# 全局实例
rag_collection_manager = None

async def get_rag_collection_manager() -> RAGCollectionManager:
    """获取RAG集合管理器实例"""
    global rag_collection_manager
    if rag_collection_manager is None:
        rag_collection_manager = RAGCollectionManager()
        await rag_collection_manager.initialize()
    return rag_collection_manager

async def get_paper_rag_manager() -> PaperRAGManager:
    """获取论文RAG管理器实例"""
    manager = PaperRAGManager()
    await manager.initialize()
    return manager

async def process_papers_with_progress():
    """处理论文MD文件并加载到RAG库，显示进度条"""
    print("=== 处理论文MD文件到RAG库 ===\n")
    
    try:
        # 获取论文RAG管理器
        manager = await get_paper_rag_manager()
        print("✅ 成功获取论文RAG管理器实例")
        
        # 论文集合名称
        paper_collection_name = "paper_rag_collection"
        
        # 1. 统计论文文件数量
        print("\n1. 统计论文文件数量:")
        md_files = []
        for root, dirs, files in os.walk(manager.paper_md_path):
            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
        
        total_files = len(md_files)
        print(f"   发现 {total_files} 个MD文件")
        
        if total_files == 0:
            print("❌ 未找到MD文件")
            return
        
        # 2. 创建集合
        print("\n2. 创建论文集合:")
        collection = await manager.create_collection(paper_collection_name)
        print(f"   集合 '{paper_collection_name}' 创建成功")
        
        # 3. 创建RAG内存实例
        rag_memory = await manager.create_rag_memory(paper_collection_name)
        print("   RAG内存实例创建成功")
        
        # 4. 处理每个论文文件
        print("\n3. 处理论文文件:")
        processed_count = 0
        total_chunks = 0
        
        for i, file_path in enumerate(md_files, 1):
            file_name = os.path.basename(file_path)
            print(f"   [{i}/{total_files}] 处理文件: {file_name}")
            
            # 处理文件
            chunk_data = await manager.process_paper_file(file_path)
            
            # 添加到集合
            chunk_count = 0
            for chunk in chunk_data:
                success = await manager.add_data_to_collection(
                    rag_memory,
                    chunk["content"],
                    chunk["metadata"]
                )
                if success:
                    chunk_count += 1
            
            total_chunks += chunk_count
            processed_count += 1
            print(f"   ✅ 完成: {chunk_count} 个块")
        
        # 5. 验证结果
        print("\n4. 验证结果:")
        collection = await manager.get_collection(paper_collection_name)
        if collection:
            actual_count = collection.count()
            print(f"   集合中的实际记录数: {actual_count}")
            print(f"   处理的文件数: {processed_count}")
            print(f"   处理的块数: {total_chunks}")
            
            if actual_count == total_chunks:
                print("   ✅ 数据加载成功，记录数匹配")
            else:
                print(f"   ⚠️  数据加载可能存在问题，记录数不匹配")
        
        print("\n=== 论文处理完成 ===")
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def add_enhanced_rag_to_multimodal2text():
    """
    将增强版RAG数据添加到multimodal2text库
    
    使用enhanced_rag_data.json的数据，content作为检索内容，
    metadata作为RAG的metadata（除了content字段）
    """
    print("=== 开始将增强版RAG数据添加到multimodal2text库 ===")
    
    # 1. 加载enhanced_rag_data.json
    enhanced_rag_file = "enhanced_rag_output/enhanced_rag_data.json"
    if not os.path.exists(enhanced_rag_file):
        print(f"❌ 增强版RAG数据文件不存在: {enhanced_rag_file}")
        return False
    
    try:
        with open(enhanced_rag_file, 'r', encoding='utf-8') as f:
            enhanced_data = json.load(f)
        print(f"✅ 成功加载 {len(enhanced_data)} 条增强版RAG数据")
    except Exception as e:
        print(f"❌ 加载增强版RAG数据失败: {e}")
        return False
    
    # 2. 初始化RAG管理器
    manager = RAGCollectionManager()
    await manager.initialize()
    
    # 3. 创建multimodal2text集合
    collection_name = "multimodal2text"
    print(f"创建/获取集合: {collection_name}")
    
    collection = await manager.get_collection(collection_name)
    if not collection:
        collection = await manager.create_collection(collection_name)
        print(f"✅ 创建新集合: {collection_name}")
    else:
        print(f"✅ 使用现有集合: {collection_name}")
    
    # 4. 直接使用ChromaDB集合添加数据（不使用RAGMemory包装）
    print(f"开始添加 {len(enhanced_data)} 条数据到集合...")
    
    added_count = 0
    failed_count = 0
    
    # 分批处理数据，避免内存问题
    batch_size = 100
    
    for batch_start in range(0, len(enhanced_data), batch_size):
        batch_end = min(batch_start + batch_size, len(enhanced_data))
        batch = enhanced_data[batch_start:batch_end]
        
        batch_ids = []
        batch_documents = []
        batch_metadatas = []
        
        for i, item in enumerate(batch):
            try:
                # 获取content作为检索内容
                content = item.get("content", "")
                if not content:
                    print(f"⚠️  跳过第 {batch_start + i + 1} 条数据: 缺少content字段")
                    failed_count += 1
                    continue
                
                # 准备metadata - 包含所有字段（除了content）
                metadata = {}
                for key, value in item.items():
                    if key != "content":
                        # 处理特殊类型的值
                        if isinstance(value, (dict, list)):
                            metadata[key] = json.dumps(value, ensure_ascii=False)
                        else:
                            metadata[key] = value
                
                # 生成唯一ID
                chunk_id = item.get("chunkid", f"chunk_{batch_start + i + 1}")
                
                batch_ids.append(chunk_id)
                batch_documents.append(content)
                batch_metadatas.append(metadata)
                
            except Exception as e:
                failed_count += 1
                print(f"❌ 处理第 {batch_start + i + 1} 条数据时出错: {e}")
        
        # 批量添加数据到集合
        if batch_ids:
            try:
                collection.add(
                    ids=batch_ids,
                    documents=batch_documents,
                    metadatas=batch_metadatas
                )
                added_count += len(batch_ids)
                print(f"   ✅ 已添加 {batch_start + len(batch_ids)}/{len(enhanced_data)} 条数据")
            except Exception as e:
                failed_count += len(batch_ids)
                print(f"❌ 批量添加数据失败: {e}")
                # 如果批量添加失败，尝试逐条添加
                for j in range(len(batch_ids)):
                    try:
                        collection.add(
                            ids=[batch_ids[j]],
                            documents=[batch_documents[j]],
                            metadatas=[batch_metadatas[j]]
                        )
                        added_count += 1
                        failed_count -= 1
                    except Exception as e2:
                        print(f"❌ 单条添加数据失败: {e2}")
    
    # 6. 验证结果
    print("\n=== 处理完成 ===")
    print(f"总数据条数: {len(enhanced_data)}")
    print(f"成功添加: {added_count}")
    print(f"添加失败: {failed_count}")
    
    # 添加延迟确保数据同步
    import time
    print("等待数据同步到磁盘...")
    time.sleep(2)
    
    # 重新获取集合以刷新状态
    final_collection = await manager.get_collection(collection_name)
    if final_collection:
        try:
            actual_count = final_collection.count()
            print(f"集合中的实际记录数: {actual_count}")
            
            if actual_count == added_count:
                print("✅ 数据加载成功，记录数匹配")
            else:
                print(f"⚠️  记录数不匹配，可能存在重复数据或同步问题")
                print(f"   建议等待几秒后重新检查集合状态")
        except Exception as e:
            print(f"❌ 获取集合记录数失败: {e}")
            actual_count = "未知"
    else:
        print("❌ 无法获取最终集合")
        actual_count = "未知"
    
    success_rate = (added_count / len(enhanced_data) * 100) if len(enhanced_data) > 0 else 0
    print(f"成功率: {success_rate:.2f}%")
    
    # 即使计数不匹配，只要成功添加了数据就返回True
    return added_count > 0


if __name__ == "__main__":
    """主函数，处理论文MD文件到RAG库"""
    # 检查命令行参数，决定执行哪个功能
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "multimodal2text":
        # 执行multimodal2text功能
        result = asyncio.run(add_enhanced_rag_to_multimodal2text())
    else:
        # 默认执行论文处理功能
        result = asyncio.run(process_papers_with_progress())
    
    sys.exit(0 if result else 1)
