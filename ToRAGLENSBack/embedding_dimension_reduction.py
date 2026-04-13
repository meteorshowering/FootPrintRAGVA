import asyncio
import json
import os
import numpy as np
from typing import List, Dict, Any, Optional
import chromadb
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import requests

class RAGEmbeddingProcessor:
    def __init__(self, db_persistence_path: Optional[str] = None):
        """
        初始化RAG嵌入向量处理器
        
        参数:
        - db_persistence_path: ChromaDB数据库路径
        """
        self.db_persistence_path = db_persistence_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), ".chromadb_autogen"
        )
        self.chroma_client = None
        self.initialized = False
        
        # OpenAI格式的嵌入请求配置（需要用户填写）
        self.openai_config = {
            "url": "https://uni-api.cstcloud.cn/v1/embeddings",  # 请填写嵌入API的URL
            "api_key": "f24a9af08a33a9649b3f149706c8c45e8602a884b8beab6abae0d608226477f8",  # 请填写API密钥
            "model": "qwen3-embedding:8b"  # 默认模型，可根据需要修改
        }
    
    async def initialize(self):
        """初始化ChromaDB客户端"""
        if self.initialized:
            return
        
        try:
            self.chroma_client = chromadb.PersistentClient(path=self.db_persistence_path)
            self.initialized = True
            print(f"✅ ChromaDB客户端初始化成功，数据库路径: {self.db_persistence_path}")
        except Exception as e:
            print(f"❌ ChromaDB客户端初始化失败: {e}")
            raise
    
    async def get_collection_data(self, collection_name: str = "multimodal2text") -> List[Dict[str, Any]]:
        """
        获取指定集合的所有数据
        
        参数:
        - collection_name: 集合名称，默认为multimodal2text
        
        返回:
        - 包含所有文档数据的列表
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # 获取集合
            collection = self.chroma_client.get_collection(name=collection_name)
            print(f"✅ 成功获取集合: {collection_name}")
            
            # 获取所有数据 - 使用正确的include参数
            results = collection.get(
                include=["metadatas", "documents", "embeddings"]
            )
            print(f"✅ 获取到结果数据，ids数量: {len(results.get('ids', []))}")
            
            data_list = []
            num_ids = len(results.get("ids", []))
            
            for i in range(num_ids):
                # 安全处理metadata和embedding
                metadata = {}
                metadatas = results.get("metadatas", [])
                if metadatas is not None and len(metadatas) > 0 and i < len(metadatas):
                    metadata = metadatas[i] if metadatas[i] is not None else {}
                
                embedding = None
                embeddings = results.get("embeddings", [])
                if embeddings is not None and len(embeddings) > 0 and i < len(embeddings):
                    embedding = embeddings[i]
                
                item = {
                    "id": results["ids"][i],
                    "content": results["documents"][i],
                    "metadata": metadata,
                    "embedding": embedding
                }
                data_list.append(item)
            
            print(f"✅ 成功获取集合 '{collection_name}' 的数据，共 {len(data_list)} 条记录")
            return data_list
            
        except Exception as e:
            print(f"❌ 获取集合数据失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_openai_embedding(self, text: str) -> Optional[List[float]]:
        """
        使用自定义API格式获取文本嵌入向量
        
        参数:
        - text: 要嵌入的文本
        
        返回:
        - 嵌入向量列表，如果失败返回None
        """
        if not self.openai_config["url"] or not self.openai_config["api_key"]:
            print("⚠️ 请先配置API的URL和密钥")
            return None
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_config['api_key']}"
            }
            
            data = {
                "model": self.openai_config["model"],
                "input": text,
                "encoding_format": "float"
            }
            
            response = requests.post(
                self.openai_config["url"],
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "data" in result and len(result["data"]) > 0:
                    return result["data"][0]["embedding"]
                else:
                    print(f"❌ API响应格式异常: {result}")
                    return None
            else:
                print(f"❌ API请求失败，状态码: {response.status_code}, 响应: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 获取嵌入向量失败: {e}")
            return None
    
    def reduce_dimension(self, embeddings: List[List[float]], method: str = "tsne", n_components: int = 2) -> List[List[float]]:
        """
        对嵌入向量进行降维
        
        参数:
        - embeddings: 嵌入向量列表
        - method: 降维方法，可选 "tsne" 或 "pca"
        - n_components: 降维后的维度数
        
        返回:
        - 降维后的二维坐标列表
        """
        if not embeddings:
            print("⚠️ 没有嵌入向量数据")
            return []
        
        # 转换为numpy数组
        embeddings_array = np.array(embeddings)
        
        if method == "tsne":
            # 使用t-SNE进行降维
            tsne = TSNE(n_components=n_components, random_state=42, perplexity=min(30, len(embeddings)-1))
            reduced_embeddings = tsne.fit_transform(embeddings_array)
        elif method == "pca":
            # 使用PCA进行降维
            pca = PCA(n_components=n_components, random_state=42)
            reduced_embeddings = pca.fit_transform(embeddings_array)
        else:
            raise ValueError("不支持的降维方法，请选择 'tsne' 或 'pca'")
        
        # 转换为列表格式
        coordinates = reduced_embeddings.tolist()
        
        print(f"✅ 使用 {method.upper()} 成功将 {len(embeddings)} 个向量降维到 {n_components} 维")
        return coordinates
    
    def save_to_json(self, data: List[Dict[str, Any]], output_file: str = "rag_embeddings_2d.json"):
        """
        将结果保存为JSON文件
        
        参数:
        - data: 要保存的数据
        - output_file: 输出文件名
        """
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 结果已保存到: {output_file}")
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
    
    async def process_rag_collection(
        self, 
        collection_name: str = "multimodal2text",
        use_existing_embeddings: bool = True,
        reduction_method: str = "tsne",
        output_file: str = "rag_embeddings_2d.json"
    ) -> List[Dict[str, Any]]:
        """
        处理RAG集合的主要流程
        
        参数:
        - collection_name: 集合名称
        - use_existing_embeddings: 是否使用现有的嵌入向量
        - reduction_method: 降维方法
        - output_file: 输出文件名
        
        返回:
        - 处理后的数据列表
        """
        print(f"🚀 开始处理RAG集合: {collection_name}")
        
        # 1. 获取集合数据
        collection_data = await self.get_collection_data(collection_name=collection_name)
        if not collection_data:
            print("❌ 无法获取集合数据，处理终止")
            return []
        
        # 2. 获取嵌入向量
        embeddings = []
        valid_data = []
        
        for item in collection_data:
            embedding_value = item.get("embedding")
            if use_existing_embeddings and embedding_value is not None:
                # 使用现有的嵌入向量
                embeddings.append(embedding_value)
                valid_data.append(item)
            else:
                # 使用OpenAI API获取新的嵌入向量
                embedding = self.get_openai_embedding(item["content"])
                if embedding is not None:
                    embeddings.append(embedding)
                    item["embedding"] = embedding  # 更新嵌入向量
                    valid_data.append(item)
        
        if not embeddings:
            print("❌ 没有可用的嵌入向量数据")
            return []
        
        print(f"✅ 成功获取 {len(embeddings)} 个嵌入向量")
        
        # 3. 降维处理
        coordinates_2d = self.reduce_dimension(embeddings, method=reduction_method)
        
        # 4. 构建结果数据
        result_data = []
        for i, item in enumerate(valid_data):
            # 从metadata中提取paper_id
            paper_id = item.get("metadata", {}).get("paper_name", "unknown")
            
            result_item = {
                "id": item["id"],  # 保留原始id
                "paper_id": paper_id,
                "chunk_id": item["id"],
                "content": item["content"][:200] + "..." if len(item["content"]) > 200 else item["content"],  # 截取前200字符
                "metadata": item["metadata"],
                "coordinates_2d": coordinates_2d[i] if i < len(coordinates_2d) else [0, 0]
            }
            result_data.append(result_item)
        
        # 5. 保存结果
        self.save_to_json(result_data, output_file)
        
        print(f"🎉 处理完成！共处理 {len(result_data)} 条记录")
        return result_data


async def main():
    """主函数"""
    # 创建处理器实例
    processor = RAGEmbeddingProcessor()
    
    # # 配置API信息（请根据实际情况填写）
    # processor.openai_config = {
    #     "url": "https://uni-api.cstcloud.cn/v1/embeddings",  # 请替换为实际的API URL
    #     "api_key": "your-token-here",  # 请替换为实际的Token
    #     "model": "bge-large-zh:latest"  # 使用bge-large-zh模型
    # }
    
    # 处理RAG集合
    result = await processor.process_rag_collection(
        collection_name="multimodal2text",
        use_existing_embeddings=True,  # 优先使用现有的嵌入向量
        reduction_method="tsne",  # 使用t-SNE降维
        output_file="multimodal2text_embeddings_2d.json"
    )
    
    # 显示前几条结果作为示例
    if result:
        print("\n📊 前5条处理结果示例:")
        for i, item in enumerate(result[:5]):
            # print(f"{i+1}. Paper ID: {item['metadata']['paper_name']}")
            print(f"   Chunk ID: {item['chunk_id']}")
            print(f"   内容: {item['content']}")
            print(f"   坐标: {item['coordinates_2d']}")
            print("   ---")


if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())