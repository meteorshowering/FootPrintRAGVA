import json
from autogen_core.models import SystemMessage, UserMessage
from protocols import HypothesisData, HypothesisStep

_INTERACTIVE_REPORT_OUTLINE_SYSTEM = SystemMessage(
    content="""You are a scientific report architect.
You will be given a list of query strategies and their summaries (each with a plan_id).
Group these strategies logically into a 2-level outline for a scientific review report.
Output ONLY a JSON list, e.g.:
[
  {
    "level1_title": "Broad Theme 1",
    "subsections": [
      {
        "level2_title": "Specific Topic 1",
        "assigned_plan_ids": ["plan_id_1", "plan_id_2"]
      }
    ]
  }
]
Do NOT use markdown fences."""
)

_INTERACTIVE_REPORT_SECTION_SYSTEM = SystemMessage(
    content="""You are a scientific writer.
You are given a subsection title and a set of retrieved evidence items (each with a CHUNK_ID).
Write a concise, professional English literature review paragraph (3-6 sentences) synthesizing this evidence.
CRITICAL: You MUST cite the evidence using EXACTLY the format `[CHUNK_ID]` (e.g. `[doc1_chunk4]`) where appropriate.
Output ONLY the paragraph text. No JSON, no markdown formatting."""
)

async def _llm_interactive_report_outline(client, plan_summaries):
    plans_text = ""
    for p in plan_summaries:
        plans_text += f"Plan ID: {p['plan_id']}\nStrategy: {p['tool_name']}\nSummary: {p['plansummary']}\n---\n"
    
    msg = UserMessage(content=f"Plan Summaries:\n{plans_text}\nGenerate the 2-level outline JSON array.", source="user")
    resp = await client.create(messages=[_INTERACTIVE_REPORT_OUTLINE_SYSTEM, msg])
    cleaned = resp.content.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return []

async def _llm_interactive_report_section(client, title, rag_results):
    evidence_text = ""
    for item in rag_results:
        chunk_id = item.get("chunk_id", "Unknown_ID")
        content = item.get("content", "")
        evidence_text += f"CHUNK_ID: {chunk_id}\nContent: {content}\n---\n"
        
    msg = UserMessage(content=f"Subsection Title: {title}\n\nEvidence:\n{evidence_text}\n\nWrite the synthesis paragraph with [CHUNK_ID] citations.", source="user")
    resp = await client.create(messages=[_INTERACTIVE_REPORT_SECTION_SYSTEM, msg])
    return resp.content.strip()
