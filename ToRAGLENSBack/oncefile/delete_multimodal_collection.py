import chromadb
import os

# 连接到现有的ChromaDB客户端
db_persistence_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".chromadb_autogen")
chroma_client = chromadb.PersistentClient(path=db_persistence_path)

# 多模态集合名称
multimodal_collection_name = "scientific_multimodal_collection"

print("🔍 检查并删除现有多模态集合...")

try:
    # 尝试获取现有集合
    existing_collection = chroma_client.get_collection(name=multimodal_collection_name)
    print(f"   找到集合: {multimodal_collection_name}")
    
    # 删除集合
    chroma_client.delete_collection(name=multimodal_collection_name)
    print(f"   成功删除集合: {multimodal_collection_name}")
except Exception as e:
    print(f"   集合不存在或删除失败: {e}")

print("\n操作完成！")