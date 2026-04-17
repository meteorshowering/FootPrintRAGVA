"""
【功能】Pydantic 模型定义：证据项、评估结果、科研图节点、用户请求、实验结果、Hypothesis 结构等——前后端与 engine 之间的契约层。
【长期价值】核心长期维护；协议变更需同步前端与序列化逻辑。
"""
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
import json

# ==============================================================================
# 1. 底层数据单元：证据项 (Raw Evidence Item)
# ==============================================================================
class RawEvidenceItem(BaseModel):
    id: str                     
    source_tool: str            
    content: Dict[str, Any]     
    metadata: Dict[str, Any]    
    score: float = 0.0   
    source_args: Dict[str, Any] = Field(default_factory=dict)  

class NodeSearchRecord(BaseModel):
    round_index: int
    source_tool: str            # 被哪个工具访问
    source_args: Dict[str, Any] # 具体的参数
    parent_id: str
# ==============================================================================
# 2. 评估结果单元
# ==============================================================================
class ItemEvaluation(BaseModel):
    target_evidence_id: str     
    branch_action: str          # "GROW", "PRUNE", "KEEP"
    extracted_insight: str      
    scores: Dict[str, int]      
    reason: str = ""
    suggested_keywords: List[str] = Field(default_factory=list)  

# ==============================================================================
# 3. 全局状态：科研树 (Research Graph)
# ==============================================================================
class GraphNode(BaseModel):
    id: str
    type: str 
    status: str 
    #数据载荷
    content: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    #结构信息
    ParentNode: Optional[str] = None
    children_ids: List[str] = Field(default_factory=list)
    hit_count: int = 1
    #来源追溯
    created_at_round: int = 0
    search_history: List[NodeSearchRecord] = Field(default_factory=list)
    source_tool: str = ""
    source_args: Dict[str, Any] = Field(default_factory=dict)
    source_reason: str = "" 
    #评估档案
    evaluation: Optional[ItemEvaluation] = None

# ✨ 新增：单步操作记录
class ActionTrace(BaseModel):
    round_index: int            # 第几轮
    tool_name: str              # 用了什么工具
    tool_args: Dict[str, Any]   # 搜了什么词/ID
    ParentNode: Optional[str] = None    # 基于哪个父节点
    generated_evidence_ids: List[str] # 这一步挖出了哪些 ID

class ResearchGraph(BaseModel):
    root_goal: str
    nodes: Dict[str, GraphNode] = Field(default_factory=dict)
    
    # ✨ 新增：操作历史列表
    action_history: List[ActionTrace] = Field(default_factory=list)
    
    # ✨ 新增：用于去重的证据唯一标识集合
    # 使用内容摘要的哈希值作为唯一标识
    evidence_fingerprints: set[str] = Field(default_factory=set)
    
    def get_active_nodes_summary(self) -> str:
        summary = []
        for nid, node in self.nodes.items():
            if node.status == "ACTIVE" and node.type == "EVIDENCE":
                meta_info = f"Paper:{node.metadata.get('paper_id', 'N/A')}, Type:{node.metadata.get('figure_type', 'N/A')}"
                title = node.content.get('title', 'No Title')
                summary.append(f"- ID: {nid} | Title: {title} | Insight: {node.evaluation.extracted_insight[:100]}... | [{meta_info}]")
        return "\n".join(summary) if summary else "暂无活跃证据节点。"
    
    def generate_evidence_fingerprint(self, evidence: RawEvidenceItem) -> str:
        """
        生成证据的唯一标识，用于去重
        基于证据的内容、来源和参数生成哈希值
        """
        # 提取关键信息用于生成指纹
        key_info = {
            'title': evidence.content.get('title', ''),
            'paper_id': evidence.metadata.get('paper_id', ''),
            'source_tool': evidence.source_tool,
            'source_args': evidence.source_args
        }
        # 使用JSON序列化生成字符串，然后返回哈希值
        return str(hash(json.dumps(key_info, sort_keys=True, ensure_ascii=False)))
    
    def is_evidence_duplicate(self, evidence: RawEvidenceItem) -> bool:
        """
        检查证据是否重复
        """
        fingerprint = self.generate_evidence_fingerprint(evidence)
        if fingerprint in self.evidence_fingerprints:
            return True
        # 如果是新证据，添加到集合中
        self.evidence_fingerprints.add(fingerprint)
        return False


# ==============================================================================
# 4. 智能体通信消息 (Agent Messages)
# ==============================================================================
class UserRequest(BaseModel):
    query: str
    # 每轮计划生成多少个 OrchestratorPlan（策略）。用于控制 orchestrator 输出的 call_tool 数量。
    plans_per_round: int = Field(default=2, ge=1, le=10)
    # 每个检索策略（plan）希望返回多少条证据结果（用于 semantic/metadata 等检索的 n_results）。
    rag_result_per_plan: int = Field(default=10, ge=1, le=20)
    # 最大轮次：控制 OrchestratorAgent 一共跑多少轮。
    max_rounds: int = Field(default=3, ge=1, le=10)
    # ✨ 新增：是否启用交互/可中断模式
    interactive: bool = Field(default=False)
    # 小地图框选：仅在这些 Chroma 文档 id（与 embedding JSON 的 id 一致）内检索；None 或空表示不限定
    rag_allowed_chunk_ids: Optional[List[str]] = Field(default=None)
    # 与 embeddings_2d / 小地图散点一致的二维数据坐标系：框选矩形对角两点 [[xmin,ymin],[xmax,ymax]]，未框选则为 null
    map_box_rect_2d: Optional[List[List[float]]] = Field(default=None)
    collection_name: str = Field(default="multimodal2text")
    # 单次提问会话 id（前端生成 UUID），用于多问题并行展示与批量 JSON 合并
    session_id: str = Field(default="")
    # 同一会话页多问题共享的批次 id；设置时落盘 logs/experiment_results_{batch_id}.json（读入后按 session_id 合并 sessions）
    batch_id: str = Field(default="")
    # True 时跳过 Evaluator LLM，检索后自动 KEEP 占位评估（仍走 handle_eval 与后续规划）
    skip_evaluation: bool = Field(default=False)

class FollowUpRequest(BaseModel):
    """
    追问请求：只做一次检索 + 评估（不走多轮规划）。
    round_number 为前端「新一行」对应的迭代轮次编号（通常为当前最大 round + 1）。
    """
    query: str
    parent_node_id: str = "0"
    round_number: int = Field(default=0, ge=0, le=9999)
    rag_result_per_plan: int = Field(default=10, ge=1, le=20)
    rag_allowed_chunk_ids: Optional[List[str]] = Field(default=None)
    map_box_rect_2d: Optional[List[List[float]]] = Field(default=None)
    collection_name: str = Field(default="multimodal2text")
    skip_evaluation: bool = Field(default=False)
    # 与主会话对齐，便于前端合并 experiment_result / 过滤 WS
    session_id: str = Field(default="")
    batch_id: str = Field(default="")
    # 主问题原文（与首轮 UserRequest 一致），追问单独 runtime 仍写入同一语义根目标
    root_goal: str = Field(default="")


class OrchestratorPlan(BaseModel):
    """Orchestrator -> ToolExecutor"""
    action: str 
    tool_name: Optional[str] = None
    ParentNode: Optional[str] = None
    # 🛠️ 修复点 1: 改名为 args，与 Prompt 一致
    # 🛠️ 修复点 2: 使用 default_factory=dict，确保永远不为 None
    args: Dict[str, Any] = Field(default_factory=dict) 
    reason: str = ""
    
    # ⚡️ 新增：策略执行结果统计
    total_results: int = 0  # 总共搜索到的条目数
    duplicate_results: int = 0  # 重复的条目数
    plansummary: Optional[str] = None  # 策略总结结果

    # ✨ 新增：计划批次 (Orchestrator -> ToolExecutor)
class OrchestratorPlanBatch(BaseModel):
    plans: List[OrchestratorPlan]

class ToolOutputMessage(BaseModel):
    """ToolExecutor -> Evaluator"""
    original_plan: OrchestratorPlan
    raw_items: List[RawEvidenceItem] 

# ✨ 新增：单条工具结果容器 (辅助用)
class SingleToolOutput(BaseModel):
    original_plan: OrchestratorPlan
    raw_items: List[RawEvidenceItem]
    error: Optional[str] = None # 记录该工具是否报错

# ✨ 新增：结果批次 (ToolExecutor -> Orchestrator)
class ToolOutputBatchMessage(BaseModel):
    outputs: List[SingleToolOutput]

class EvaluationRequest(BaseModel):
    new_items: List[RawEvidenceItem]

class EvaluationReportMessage(BaseModel):
    """Evaluator -> Orchestrator"""
    evaluations: List[ItemEvaluation] 
    global_suggestion: str            

class TaskComplete(BaseModel):
    graph_snapshot: ResearchGraph
    experiment_result: Optional['ExperimentResult'] = None
    experiment_save_path: Optional[str] = None  # Orchestrator 保存 JSON 的路径，供 Hypothesis 完成后追加保存


# ==============================================================================
# 6. 保存结果数据格式
# ==============================================================================
class RagResult(BaseModel):
    """检索结果信息和评估信息"""
    retrieval_result: RawEvidenceItem
    evaluation: Optional[ItemEvaluation] = None

class QueryResult(BaseModel):
    """策略信息和对应的检索结果列表"""
    orchestrator_plan: OrchestratorPlan
    rag_results: List[RagResult] = Field(default_factory=list)

class IterationSummary(BaseModel):
    """单轮迭代的总结信息"""
    round_number: int                         # 本轮轮次编号
    process_summary: str                      # 本轮的过程总结文本
    timestamp: str                            # 生成时间戳，方便对齐运行日志


class IterationResult(BaseModel):
    """一轮迭代的结果，包含多个策略查询"""
    round_number: int
    query_results: List[QueryResult] = Field(default_factory=list)
    iteration_summary: Optional[IterationSummary] = None  # 本轮对应的总结


class ExperimentRoundParameters(BaseModel):
    """每一轮开始时落盘的运行参数快照（与当轮 IterationResult.round_number 对齐）。"""
    round_number: int
    max_rounds: int
    plans_per_round: int
    rag_result_per_plan: int
    collection_name: str = "multimodal2text"
    interactive: bool = False
    rag_allowed_chunk_ids: Optional[List[str]] = Field(default=None)
    # 嵌入二维与全局小地图一致：[[xmin, ymin], [xmax, ymax]]，未框选则为 null
    map_box_rect_2d: Optional[List[List[float]]] = Field(default=None)


class HypothesisStep(BaseModel):
    """Hypothesis 生成过程中的一个步骤"""
    step_name: str  # 步骤名称，如 "outline", "section_1", "synthesis"
    agent_name: str = ""  # 生成该步骤的 agent，如 "HypothesisCoordinator", "HypothesisSection", "HypothesisSynthesizer"
    prompt: str  # 该步骤的 prompt
    response: str  # LLM 的响应
    system_message: Optional[str] = None  # 系统消息（如果有）
    timestamp: Optional[str] = None  # 时间戳

class HypothesisData(BaseModel):
    """Hypothesis 生成过程的完整数据"""
    outline: Optional[HypothesisStep] = None  # 大纲生成步骤
    sections: List[HypothesisStep] = Field(default_factory=list)  # 子主题撰写步骤列表
    synthesis: Optional[HypothesisStep] = None  # 报告整合步骤
    final_report: Optional[str] = None  # 最终报告内容

class ExperimentResult(BaseModel):
    """整个实验的结果，包含多轮迭代"""
    root_goal: str
    # 与前端/批量 JSON 对齐：同一 batch 内多个问题的区分键
    session_id: str = Field(default="")
    parameters: List[ExperimentRoundParameters] = Field(default_factory=list)
    iterations: List[IterationResult] = Field(default_factory=list)
    summary: Optional['SummaryResponse'] = None  # 整个实验的最终总结结果（通常为最后一轮）
    hypothesis: Optional[HypothesisData] = None  # Hypothesis 生成过程的完整数据


class ExperimentBatchDocument(BaseModel):
    """多问题同一会话落盘：sessions 每项为完整 ExperimentResult（含 root_goal / parameters / iterations）。"""
    sessions: List[ExperimentResult] = Field(default_factory=list)


# ==============================================================================
# 7. 总结相关消息类型
# ==============================================================================
class WordCloudData(BaseModel):
    """词云数据结构"""
    words: List[Dict[str, Any]]  # 格式: [{"text": "关键词", "value": 频率}]
    total_words: int
    top_keywords: List[str]

class RetrievalQualityEvaluation(BaseModel):
    """检索质量评估结果结构"""
    relevance_score: float  # 相关性评分
    accuracy_score: float  # 准确性评分
    authority_score: float  # 权威性评分
    completeness_score: float  # 完整性评分
    overall_score: float  # 总体评分
    positive_meaning: str  # 问题的积极意义和价值
    contribution_to_knowledge: str  # 对知识获取的贡献度
    strengths: List[str]  # 检索过程的优势
    weaknesses: List[str]  # 检索过程的不足
    suggestions: List[str]  # 改进建议

class SummaryRequest(BaseModel):
    """请求生成总结的消息"""
    experiment_result: ExperimentResult
    current_evidence_data: Optional[List[RawEvidenceItem]] = None  # 当前小问题的证据数据
    current_question: Optional[str] = None  # 当前小问题本身
    user_original_input: Optional[str] = None  # 用户原始输入

class SummaryResponse(BaseModel):
    """返回总结结果的消息"""
    process_summary: str  # 过程总结
    word_cloud_data: WordCloudData  # 词云数据
    quality_evaluation: RetrievalQualityEvaluation  # 检索质量评估
    timestamp: str  # 生成时间戳


# 解决循环引用
# 兼容 Pydantic v1 和 v2
try:
    # Pydantic v2
    ExperimentResult.model_rebuild()
except AttributeError:
    # Pydantic v1
    ExperimentResult.update_forward_refs()


# ==============================================================================
# 8. HypothesisGeneratorAgent Team 相关消息类型
# ==============================================================================
class SubTopic(BaseModel):
    """子主题信息"""
    topic_name: str              # 子主题名称
    description: str             # 子主题描述
    sub_questions: List[str]     # 该主题下的子问题列表（从抽象到具体）
    assigned_plan_ids: List[str] = Field(default_factory=list)  # 分配给该子主题的 plan ID 列表（用于后续查找 RAG 结果）
    keywords: List[str]          # 该子主题的关键词

class OutlineRequest(BaseModel):
    """大纲生成请求"""
    graph_snapshot: ResearchGraph
    experiment_result: Optional[ExperimentResult] = None
    plan_summaries: List[Dict[str, Any]] = Field(default_factory=list)  # plan summaries: [{"plan_id": str, "plansummary": str, "tool_name": str, "args": dict, "reason": str}]

class OutlineResponse(BaseModel):
    """大纲生成响应"""
    core_hypothesis_preview: str  # 核心假设的初步提炼
    subtopics: List[SubTopic]     # 子主题列表

class SectionRequest(BaseModel):
    """子主题撰写请求"""
    subtopic: SubTopic           # 子主题信息
    sub_question: str           # 当前要回答的子问题
    rag_results: List[Dict[str, Any]]  # 该子问题对应的 RAG 结果（具体证据）
    root_goal: str               # 用户原始问题
    experiment_result: Optional['ExperimentResult'] = None  # 用于保存生成的内容

class SectionResponse(BaseModel):
    """子主题撰写响应"""
    subtopic_name: str           # 子主题名称
    content: str                 # 该子主题的完整段落
    cited_nodes: List[str]       # 引用的节点ID列表

class SynthesisRequest(BaseModel):
    """报告整合请求"""
    root_goal: str               # 用户原始问题
    outline: OutlineResponse     # 大纲
    section_contents: List[SectionResponse]  # 各子主题内容
    graph_structure_summary: str # 图谱结构概览
    experiment_summary: Optional[str] = None  # 实验总结（如果有）
    experiment_result: Optional['ExperimentResult'] = None  # 用于保存生成的内容

# ==============================================================================
# 5. 卡片扩展检索请求
# ==============================================================================
class ExpandSearchRequest(BaseModel):
    """卡片扩展检索请求"""
    parent_node_id: str          # 父节点ID
    search_type: str             # 检索类型：semantic 或 metadata
    search_query: str            # 检索查询内容
    reason: Optional[str] = "用户在卡片上发起的扩展检索"