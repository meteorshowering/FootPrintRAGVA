# RAG Lens 交互术语索引（草案）

> 面向后续「小追问」相关交互与**第二套多智能体流程**（`engine_multi_agent.py`：多路改写 + 并行追问轨）的讨论约定。  
> 若与产品最终命名不一致，可在本文件直接修订并保留变更记录。

---

## 大追问

**解读**：在**当前会话**已有河流图 / 检索结果的前提下，**归档**当前这一列（或当前缓冲区）的实验轨迹，**新开一条会话列**（新的 `session_id` / 网格列），从新的用户问题重新开始多轮检索。  
**代码/UI 线索**：前端 `EnhancedRiverChart` 中「大追问」类按钮、`openAddQuestionPrompt`；语义上对应「加一题、新列、新会话」，与在同一列内继续追问相对。

---

## 小追问

**解读**：在**不新开会话列**的前提下，基于当前问题与已有证据，发起**下一轮或补充一轮**检索 / 编排（同一 `session` 下的后续 `iteration` 或等价增量）。  
**代码/UI 线索**：河流图上的「追」、`openFollowUpDialog`、行末/表头旁的追问入口等；后端上可与 `start_query` 的 follow-up、或 `engine` / `engine_multi_agent` 中「同一 `root_goal` 下的下一轮」对齐讨论。  
**与第二套多智能体**：`run_multi_agent_parallel_rewrite_workflow` 里按 `max_rounds` 推进的**轨道内多轮**，若产品上称为「小追问」的自动化版本，可在实现章节再钉死映射。

---

## RAG 策略

**解读**：一次检索步骤中，编排器选择的**工具类型 + 参数**（如 `strategy_semantic_search` 的 `query_intent`、`n_results`），以及附带的 `reason`、`ParentNode` 等计划字段；落盘在 `orchestrator_plan` 中。  
**代码/UI 线索**：`OrchestratorPlan`、`strategyCards` 卡片标题中的 tool 名、HyDE / rerank 等与单次语义管线相关的元数据。  
**注意**：与「大/小追问」不同粒度——**追问**是用户或系统触发的流程动作；**RAG 策略**是该流程里**一步**的计划。

---

## 小地图

**解读**：嵌在**每个 RAG 策略小矩形**（见下）内部的缩略地图视图，用于展示与该策略检索结果相关的点分布（如 chunk 在嵌入空间/地理上的示意）。  
**代码/UI 线索**：`EnhancedRiverChart` 中 `strategy-mini-svg`、`strategy-card-map-wrap`；与左侧「全局地图」相对，仅局部、随卡片走。

---

## 小矩形

**解读**：河流网格中代表**单条 QueryResult / 单次策略执行单元**的卡片 UI（含策略标题、检索摘要行、小地图区域、脚标等）。  
**代码/UI 线索**：`strategy-card`、由 `strategyCards` 计算布局；与 Round 表头、左侧 Question 条、会话表头 overlay 并列的网格主体元素。

---

## 全局地图

**解读**：布局在**左侧栏**（`LeftPanel`）内、与河流图同页的**大地图**，展示全库或当前实验相关的点集；支持框选限定 RAG chunk 等能力。  
**代码/UI 线索**：`#left-global-map`、`globalMapPoints`、`mapToolbar` 状态；与卡片内「小地图」互补：全局浏览 vs 单策略局部。

---

## 与第二套多智能体的对应关系（备忘）

| 术语     | 在 `engine_multi_agent` 中的典型锚点 |
|----------|--------------------------------------|
| 大追问   | 新 `session` / 新列（产品层）；后端需单独 `start_query` 或扩展 API 时再对齐。 |
| 小追问   | 同一会话内 `depth` 递增、`variants[ti]` 精炼、`prior` / `previous_query_intent` 反馈环。 |
| RAG 策略 | `_llm_single_plan` → `OrchestratorPlan` → `SingleStrategyExecutor.execute_to_query_result`。 |
| 小地图   | 主要为前端 `EnhancedRiverChart`；后端可继续只提供 chunk 元数据。 |
| 小矩形   | 前端展示 `iterations[].query_results[]` 的单元格。 |
| 全局地图 | 前端 + 与 `rag_allowed_chunk_ids`、框选等参数的后端协议。 |

---

*文档版本：初稿，待你补充「小追问」交互需求后与本索引一起迭代。*
