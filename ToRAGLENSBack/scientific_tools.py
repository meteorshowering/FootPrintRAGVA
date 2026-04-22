"""
【功能】供 AutoGen 工具调用的「科学检索」封装：语义检索、元数据检索、本地过滤等，内部调用 rag_service 与协议中的 RawEvidenceItem；含安全解析 JSON/字面量。
【长期价值】核心长期维护；检索策略与工具名变更时必改此文件。
"""
import asyncio
import json
import ast  # ⬅️ 新增：用于解析单引号的 Python 字典字符串
from typing import List, Dict, Any, Optional

try:
    from rag_service import get_rag_service
    from protocols import RawEvidenceItem 
except ImportError as e:
    print(f"[ScientificTools Error] 导入失败: {e}")
    exit()

# ==============================================================================
# 🛡️ 核心辅助函数：万能解析器
# ==============================================================================
def safe_parse_data(data: Any) -> Dict[str, Any]:
    """
    尝试将各种奇怪格式（JSON字符串、Python字典字符串、字典）解析为字典。
    解析失败则返回包含原始内容的包装字典。
    """
    if isinstance(data, dict):
        return data
    
    if isinstance(data, str):
        # 1. 尝试标准 JSON 解析
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            pass
        
        # 2. 尝试 Python字面量解析 (处理单引号 '{...}')
        try:
            parsed = ast.literal_eval(data)
            if isinstance(parsed, dict):
                return parsed
        except (ValueError, SyntaxError):
            pass
            
        # 3. 实在解析不了，就当纯文本返回
        return {"raw_text_content": data}
    
    return {}

def safe_parse_list(data: Any) -> List[str]:
    """尝试解析列表字符串"""
    if isinstance(data, list):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except:
            try:
                parsed = ast.literal_eval(data)
                if isinstance(parsed, list):
                    return parsed
            except:
                return []
    return []

def process_result_item(result: Dict[str, Any], source_tool: str, source_args: Dict[str, Any]) -> RawEvidenceItem:
    """
    公共函数：将检索结果转换为RawEvidenceItem对象
    
    参数:
    - result: 检索结果字典
    - source_tool: 工具名称
    - source_args: 工具参数
    
    返回:
    - RawEvidenceItem: 转换后的证据对象
    """
    # --- 🛡️ 使用万能解析器 ---
    full_data = safe_parse_data(result.get('content'))
    
    # 安全获取字段，支持多种字段名
    title = full_data.get('title', 'No Title')
    summary = full_data.get('summary', full_data.get('concise_summary', ''))
    insight = full_data.get('insight', full_data.get('inferred_insight', ''))
    
    # 构建显示内容
    display_content = {
        "title": title,
        "summary": summary,
        "insight": insight
    }

    # 封装为RawEvidenceItem
    item = RawEvidenceItem(
        id=str(result.get('id', 'unknown')),
        source_tool=source_tool,
        source_args=source_args,
        content=display_content,
        metadata=result.get('metadata', {}), 
        score=float(result.get('score', 0.0))
    )
    
    # 传递图片路径
    if hasattr(item, 'image_path'):
        item.image_path = result['metadata'].get('image_path')
    
    return item

# ==============================================================================
# 新增左路径工具: 精确文本检索
# ==============================================================================

# 全局变量，用于动态切换 RAG 集合
ACTIVE_COLLECTION_NAME = "multimodal2text"
# 小地图框选：仅检索这些 chunk id（与 engine/server 单次 run 对齐；并发多用户需后续改为上下文传递）
ACTIVE_RAG_ALLOWED_CHUNK_IDS: Optional[List[str]] = None

def set_active_collection_name(name: str):
    global ACTIVE_COLLECTION_NAME
    ACTIVE_COLLECTION_NAME = name


def set_rag_allowed_chunk_ids(ids: Optional[List[str]]) -> None:
    """单次检索 run 内有效；None 或空列表表示不限定。"""
    global ACTIVE_RAG_ALLOWED_CHUNK_IDS
    if not ids:
        ACTIVE_RAG_ALLOWED_CHUNK_IDS = None
    else:
        ACTIVE_RAG_ALLOWED_CHUNK_IDS = [str(x) for x in ids]


def get_rag_allowed_chunk_ids() -> Optional[List[str]]:
    return ACTIVE_RAG_ALLOWED_CHUNK_IDS

async def strategy_exact_search(query_intent: str, n_results: int = 10) -> List[RawEvidenceItem]:
    print(f"\n🔍 [Tool: Left Path] 精确文本检索: '{query_intent}', n_results={n_results}, collection={ACTIVE_COLLECTION_NAME}")
    service = await get_rag_service(collection_name=ACTIVE_COLLECTION_NAME)
    
    try:
        results = await service.query_by_exact_match(
            query_text=query_intent,
            n_results=n_results,
            allowed_chunk_ids=get_rag_allowed_chunk_ids(),
        )
    except Exception as e:
        print(f"❌ Exact Search Error: {e}")
        return []
    
    items = []
    for r in results:
        # 封装
        item = RawEvidenceItem(
            id=str(r.get('id', 'unknown')),
            source_tool="Left_Path(ExactSearch)",
            source_args={"query_intent": query_intent},
            content=r.get('content',{}),    
            metadata=r.get('metadata', {}), 
            score=float(r.get('score', 1.0))
        )
        
        # 传递图片路径
        if hasattr(item, 'save_path'):
            item.image_path = r['metadata'].get('save_path')
            
        items.append(item)

    print(f"   ✅ 找到 {len(items)} 条精确匹配证据")
    return items

# ==============================================================================
# 左路径工具: 语义检索
# ==============================================================================
async def strategy_semantic_search(query_intent: str, n_results: int = 10) -> List[RawEvidenceItem]:
    print(f"\n🔍 [Tool: Left Path] 语义检索: '{query_intent}', n_results={n_results}, collection={ACTIVE_COLLECTION_NAME}")
    service = await get_rag_service(collection_name=ACTIVE_COLLECTION_NAME)
    
    try:
        results = await service.query_by_semantic(
            query_text=query_intent,
            n_results=n_results
        )
    except Exception as e:
        print(f"❌ Semantic Search Error: {e}")
        return []
    
    items = []
    for r in results:
        # --- 🛡️ 使用万能解析器 ---
        # full_data = safe_parse_data(r.get('content'))
        # # 安全获取字段
        # display_content = {
        #     "title": full_data.get('title', 'No Title'),
        #     "summary": full_data.get('summary', ''),
        #     "insight": full_data.get('insight', '')
        # }

        # 封装
        item = RawEvidenceItem(
            id=str(r.get('id', 'unknown')),
            source_tool="Left_Path(Semantic)",
            source_args={"query_intent": query_intent},
            content=r.get('content',{}),    
            metadata=r.get('metadata', {}), 
            score=float(r.get('score', 0.0))
        )
        
        # 传递图片路径
        if hasattr(item, 'save_path'):
            item.image_path = r['metadata'].get('save_path')
            
        items.append(item)

    print(f"   ✅ 找到 {len(items)} 条语义证据")
    return items


# ==============================================================================
# 右路径工具: 元数据检索
# ==============================================================================
async def strategy_metadata_search(
    keywords: List[str] = None, 
    paper_id: str = None,
    figure_type: str = None,
    n_results: Optional[int] = None,
) -> List[RawEvidenceItem]:
    print(f"\n🏷️ [Tool: Right Path] 规则筛选: Paper={paper_id}, Type={figure_type}, Key={keywords}, collection={ACTIVE_COLLECTION_NAME}")

    rag_allow = get_rag_allowed_chunk_ids()
    if not paper_id and not keywords and not figure_type:
        if not rag_allow:
            print(f"⚠️ [Tool: Right Path] 警告：所有过滤参数均为 None，返回空列表以避免返回所有数据")
            return []
    
    service = await get_rag_service(collection_name=ACTIVE_COLLECTION_NAME)
    
    try:
        results = await service.query_by_local_filter(
            keywords=keywords,
            paper_id=paper_id,
            figure_type=figure_type,
            n_results=n_results,
            allowed_chunk_ids=get_rag_allowed_chunk_ids(),
        )
    except Exception as e:
        print(f"❌ Metadata Search Error: {e}")
        return []
    
    items = []
    for r in results:
        # --- 🛡️ 使用万能解析器 ---
        full_data = safe_parse_data(r.get('content'))
        
        display_content = {
            "title": full_data.get('title', 'No Title'),
            "summary": full_data.get('concise_summary', ''),
            "insight": full_data.get('inferred_insight', '')
        }

        item = RawEvidenceItem(
            id=str(r.get('id', 'unknown')),
            source_tool="Right_Path(LocalFilter)",
            source_args={
                "keywords": keywords or None,
                "paper_id": paper_id or None,
                "figure_type": figure_type or None
            },
            content=display_content,
            metadata=r.get('metadata', {}),
            score=1.0 
        )
        
        if hasattr(item, 'save_path'):
            item.image_path = r['metadata'].get('save_path')

        items.append(item)

    print(f"   ✅ 筛选后找到 {len(items)} 条精确匹配证据")
    return items



# ==============================================================================
# 多模态检索工具
# ==============================================================================
async def strategy_multimodal_search(query_image_path: str = None, n_results: int = 10) -> List[RawEvidenceItem]:
    print(f"\n📸 [Tool: Multimodal] 多模态检索: Image: {query_image_path}, n_results={n_results}")
    service = await get_rag_service()
    
    try:
        results = await service.query_by_multimodal(     
            query_image_path=query_image_path,
            n_results=n_results
        )
    except Exception as e:
        print(f"❌ Multimodal Search Error: {e}")
        return []
    
    items = []
    for r in results:
        # --- 🛡️ 使用万能解析器 ---
        full_data = safe_parse_data(r.get('content'))
        
        # 安全获取字段
        display_content = {
            "title": full_data.get('title', 'No Title'),
            "summary": full_data.get('summary', ''),
            "insight": full_data.get('insight', '')
        }

        # 封装
        item = RawEvidenceItem(
            id=str(r.get('id', 'unknown')),
            source_tool="Multimodal_Search",
            source_args={
                "query_image_path": query_image_path or None
            },
            content=display_content,
            metadata=r.get('metadata', {}), 
            score=float(r.get('score', 0.0))
        )
        
        # 传递图片路径
        if hasattr(item, 'image_path'):
            item.image_path = r['metadata'].get('image_path')
            
        items.append(item)

    print(f"   ✅ 找到 {len(items)} 条多模态证据")
    return items

# ==============================================================================
# 向量检索工具
# ==============================================================================
async def strategy_vector_search(vector: List[float], n_results: int = 10) -> List[RawEvidenceItem]:
    print(f"\n🔢 [Tool: Vector] 向量相似度检索: 向量维度={len(vector)}，返回数量={n_results}")
    service = await get_rag_service()
    
    try:
        results = await service.query_by_vector(
            vector=vector,
            n_results=n_results
        )
    except Exception as e:
        print(f"❌ Vector Search Error: {e}")
        return []
    
    items = []
    for r in results:
        # --- 🛡️ 使用万能解析器 ---
        full_data = safe_parse_data(r.get('content'))
        
        # 安全获取字段
        display_content = {
            "title": full_data.get('title', 'No Title'),
            "summary": full_data.get('summary', ''),
            "insight": full_data.get('insight', '')
        }

        # 封装
        item = RawEvidenceItem(
            id=str(r.get('id', 'unknown')),
            source_tool="Vector_Search",
            source_args={
                "vector_dimension": len(vector),
                "n_results": n_results
            },
            content=display_content,
            metadata=r.get('metadata', {}), 
            score=float(r.get('score', 0.0))
        )
        
        # 传递图片路径
        if hasattr(item, 'image_path'):
            item.image_path = r['metadata'].get('image_path')
            
        items.append(item)

    print(f"   ✅ 找到 {len(items)} 条向量匹配证据")
    return items

# ==============================================================================
# 证据相似度检索工具
# ==============================================================================
async def strategy_evidence_similarity_search(evidence_id: str, n_results: int = 10) -> List[RawEvidenceItem]:
    print(f"\n🔗 [Tool: Evidence Similarity] 证据相似性检索: 证据ID={evidence_id}，返回数量={n_results}")
    service = await get_rag_service()
    
    try:
        results = await service.query_by_evidence_similarity(
            evidence_id=evidence_id,
            n_results=n_results
        )
    except Exception as e:
        print(f"❌ Evidence Similarity Search Error: {e}")
        return []
    
    items = []
    for r in results:
        # --- 🛡️ 使用万能解析器 ---
        full_data = safe_parse_data(r.get('content'))
        
        # 安全获取字段
        display_content = {
            "title": full_data.get('title', 'No Title'),
            "summary": full_data.get('summary', ''),
            "insight": full_data.get('insight', '')
        }

        # 封装
        item = RawEvidenceItem(
            id=str(r.get('id', 'unknown')),
            source_tool="Evidence_Similarity_Search",
            source_args={
                "evidence_id": evidence_id,
                "n_results": n_results
            },
            content=display_content,
            metadata=r.get('metadata', {}), 
            score=float(r.get('score', 0.0))
        )
        
        # 传递图片路径
        if hasattr(item, 'image_path'):
            item.image_path = r['metadata'].get('image_path')
            
        items.append(item)

    print(f"   ✅ 找到 {len(items)} 条相似证据")
    return items

ALL_TOOLS_MAP = {
    "strategy_semantic_search": strategy_semantic_search,
    "strategy_exact_search": strategy_exact_search,
    "strategy_metadata_search": strategy_metadata_search,
    "strategy_multimodal_search": strategy_multimodal_search,
    "strategy_vector_search": strategy_vector_search,
    "strategy_evidence_similarity_search": strategy_evidence_similarity_search
}