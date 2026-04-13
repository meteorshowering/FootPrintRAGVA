# RAG嵌入向量降维操作记录

## 项目概述

本项目实现了对`scientific_rag_collection_new` RAG库的嵌入向量降维处理，将高维嵌入向量降维到二维，并生成可视化图表。

## 完成的功能

### 1. Python处理脚本 (`embedding_dimension_reduction.py`)

**主要功能：**
- 读取ChromaDB中的`scientific_rag_collection_new`集合数据
- 支持使用现有嵌入向量或通过API获取新嵌入向量
- 提供t-SNE和PCA两种降维方法
- 生成包含完整信息的JSON文件

**数据字段：**
- `id`: 原始文档ID
- `paper_id`: 论文ID（从metadata中提取）
- `chunk_id`: 文档块ID
- `content`: 文档内容摘要（前200字符）
- `metadata`: 完整的元数据
- `coordinates_2d`: 降维后的二维坐标

### 2. HTML可视化页面 (`visualize_embeddings.html`)

**主要功能：**
- 按paper_id分组着色显示
- 交互式图表（缩放、拖动、悬停）
- 统计信息面板
- 自定义控制（点大小、透明度）
- 图例显示

## 技术实现

### 使用的技术栈
- **后端处理**: Python + ChromaDB + scikit-learn
- **降维算法**: t-SNE（默认）和PCA
- **可视化**: Plotly.js
- **数据格式**: JSON

### API配置
脚本支持自定义API配置：
```python
processor.openai_config = {
    "url": "https://uni-api.cstcloud.cn/v1/embeddings",
    "api_key": "your-token-here",
    "model": "bge-large-zh:latest"
}
```

## 操作步骤

### 1. 运行处理脚本
```bash
cd "c:\liuxingyu\multisubspace-data\ToRAGLENS\ToRAGLENSBack"
python embedding_dimension_reduction.py
```

### 2. 查看处理结果
脚本会生成`scientific_rag_embeddings_2d.json`文件，包含：
- 266条RAG记录
- 每个记录的二维坐标
- 按paper_id分组的信息

### 3. 可视化查看
1. 在浏览器中打开`visualize_embeddings.html`
2. 上传生成的JSON文件
3. 查看按paper_id着色的嵌入向量分布

## 遇到的问题和解决方案

### 问题1: ChromaDB API版本兼容性
**错误信息**: `Expected include item to be one of documents, embeddings, metadatas, distances, uris, data, got ids in get`

**解决方案**: 移除了`ids`参数，因为新版本ChromaDB默认返回ids

### 问题2: NumPy数组布尔判断
**错误信息**: `The truth value of an array with more than one element is ambiguous`

**解决方案**: 使用明确的数组长度判断代替直接布尔判断

### 问题3: 字段命名冲突
**错误信息**: `KeyError: 'id'`

**解决方案**: 同时保留`id`和`chunk_id`字段，确保兼容性

## 处理结果统计

- **总数据点**: 266条
- **论文数量**: 多个（具体数量取决于paper_id分布）
- **降维方法**: t-SNE
- **输出维度**: 2维

## 文件结构

```
ToRAGLENS/ToRAGLENSBack/
├── embedding_dimension_reduction.py    # 主处理脚本
├── scientific_rag_embeddings_2d.json   # 处理结果数据
├── visualize_embeddings.html          # 可视化页面
└── RAG嵌入向量降维操作记录.md          # 本文档
```

## 后续优化建议

1. **性能优化**: 对于大量数据，可以考虑分批处理
2. **缓存机制**: 缓存API请求结果，避免重复调用
3. **更多可视化选项**: 添加聚类分析、热力图等功能
4. **交互功能**: 支持点击数据点查看详细信息

## 总结

本项目成功实现了RAG嵌入向量的降维处理和可视化，为后续的数据分析和可视化提供了基础。HTML可视化页面已经可以正常运行，展示了按paper_id分组的嵌入向量分布。