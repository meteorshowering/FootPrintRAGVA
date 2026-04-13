# Engine Prompt Migration (CN -> EN)

This document records the prompt migration in `engine.py`, including **old (Chinese)** and **new (English)** versions for core prompt blocks.

## 1) Orchestrator `self.system_message`

### Old (CN)
- Role: 首席科学家，构建科研证据树，平衡广度/深度。
- Required fields: `action`, `ParentNode`, `tool_name`, `args`, `reason`.
- Strategy modes: DEEPER / BROADER.
- Historical strategy awareness and novelty constraints.

### New (EN)
- Role: Chief Scientist in a scientific discovery team.
- Mission: plan retrieval directions to grow an evidence tree.
- Explicit JSON strategy schema.
- DEEPER/BROADER rules retained.
- Internal relevance + novelty checks retained.

---

## 2) Orchestrator `self.outputregulate`

### Old (CN)
- “每轮必须输出 __PLANS_PER_ROUND__ 个策略”
- “仅 semantic 严格受 __RAG_RESULT_PER_PLAN__ 控制”
- JSON-only output requirement.

### New (EN)
- Must output exactly `__PLANS_PER_ROUND__` strategies.
- JSON only, no extra text.
- `n_results` control applies strictly to semantic retrieval.

---

## 3) Orchestrator planning context text (`strategyhis`, `searchpro`)

### Old (CN)
- Chinese narrative describing first-round planning and evaluated evidence.

### New (EN)
- English planning context for:
  - first-step after initial retrieval,
  - regular rounds with evaluated evidence,
  - evidence lines for evaluated and pending/duplicate nodes.

---

## 4) Evaluator `self.system_message` + request prefix

### Old (CN)
- 评估员角色，输出 `branch_action`, `extracted_insight`, `scores`, `reason`, `suggested_keywords`。
- Prompt prefix in Chinese.

### New (EN)
- Evaluator role and criteria fully in English.
- Keeps JSON-list output contract unchanged.
- Prefix changed to:
  - `Please evaluate the following newly retrieved evidence items...`

---

## 5) InteractionSummary `self.system_message`

### Old (CN)
- 总结专家：过程总结、词云支持、检索质量评估。

### New (EN)
- Summary specialist role and responsibilities in English.
- Emphasizes concise, structured, actionable summary output.

---

## 6) `generate_plan_summary()` prompt template

### Old (CN)
- “单一检索策略总结任务”中文提示，输出自然语言段落。

### New (EN)
- “Single Strategy Summary Task” in English.
- Keeps same structure:
  - context,
  - strategy info,
  - evidence list,
  - output requirements.

---

## 7) `generate_process_summary()` prompt template

### Old (CN)
- “检索过程总结任务”中文模板，包含轮次、策略、评估和洞察。

### New (EN)
- “Retrieval Process Summary Task” in English.
- Same analytical dimensions retained.

---

## 8) HypothesisCoordinator prompts

### Old (CN)
- 大纲生成：基于 plan summaries 产出 JSON 大纲。

### New (EN)
- Outline generation prompt fully translated.
- JSON schema and constraints preserved.

---

## 9) HypothesisSection prompts

### Old (CN)
- 子主题写作：基于子问题 + RAG 证据，要求引用 `[Evidence: node_id]`。

### New (EN)
- Section writing prompt translated.
- Citation format requirement unchanged.

---

## 10) HypothesisSynthesizer prompts

### Old (CN)
- 报告整合：核心假设、证据链、缺口、结论。

### New (EN)
- Report synthesis prompt translated with same structure.

---

## 11) Hypothesis report coordinator system prompt

### Old (CN)
- 报告协调者，协调大纲/子主题/整合三阶段。

### New (EN)
- Report Coordinator role in English.

---

## Notes

1. This migration focuses on **prompt text passed to LLMs** in `engine.py`.
2. Business logic, data schema, and tool contracts remain unchanged.
3. Existing Chinese comments/log lines may still exist where they are not part of model prompts.

