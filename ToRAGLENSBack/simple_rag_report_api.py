"""
【功能】轻量 FastAPI：单问题 → 语义检索 → 拼装报告并写文件；与主 server 分离的简易演示/批注接口。
【长期价值】辅助可保留；非主链路，产品化时可合并或删除重复能力。
"""
import os
import json
import datetime
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from autogen_core.models import ModelInfo, SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from scientific_tools import strategy_semantic_search
from rag_llm_api_config import get_rag_llm_api_settings


app = FastAPI(title="Simple RAG Report API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimpleRagReportRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User question")
    n_results: int = Field(default=8, ge=1, le=30, description="Number of semantic retrieval results")
    max_evidence_in_prompt: int = Field(default=12, ge=1, le=30, description="Maximum evidence items passed to the report model")


class SimpleRagReportResponse(BaseModel):
    query: str
    report: str
    used_evidence_count: int
    evidence: List[Dict[str, Any]]
    saved_path: str = ""


def create_model_client() -> OpenAIChatCompletionClient:
    """
    独立接口专用模型客户端。
    网关与模型见 rag_llm_api_config（RAG_REPORT_* / RAG_SEMANTIC_*）。
    """
    s = get_rag_llm_api_settings()

    return OpenAIChatCompletionClient(
        model=s.report_model,
        base_url=s.base_url,
        api_key=s.api_key,
        model_info=ModelInfo(
            vision=False,
            structured_output=False,
            function_calling=True,
            streaming=True,
            json_output=False,
            family="openai",
            context_length=65536,
        ),
    )


def normalize_model_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict) and p.get("text"):
                parts.append(str(p.get("text")))
        return "\n".join(parts).strip()
    return str(content or "")


def _to_dict(maybe_json: Any) -> Dict[str, Any]:
    if isinstance(maybe_json, dict):
        return maybe_json
    if isinstance(maybe_json, str):
        try:
            parsed = json.loads(maybe_json)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {}
    return {}


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "simple-rag-report-api"}


@app.post("/api/simple-rag-report", response_model=SimpleRagReportResponse)
async def simple_rag_report(req: SimpleRagReportRequest):
    query = req.query.strip()
    if not query:
        return {
            "query": req.query,
            "report": "The query is empty. Unable to generate report.",
            "used_evidence_count": 0,
            "evidence": [],
            "saved_path": "",
        }

    raw_items = await strategy_semantic_search(query_intent=query, n_results=req.n_results)
    evidence_items = raw_items[: max(1, min(req.max_evidence_in_prompt, len(raw_items)))]

    evidence_lines: List[str] = []
    response_evidence: List[Dict[str, Any]] = []
    for idx, item in enumerate(evidence_items, start=1):
        content_dict = item.content if isinstance(item.content, dict) else {}
        metadata_dict = item.metadata if isinstance(item.metadata, dict) else {}
        nested_meta = _to_dict(metadata_dict.get("metadata"))

        # 多来源兜底，避免把有价值字段漏掉
        title = str(
            content_dict.get("title")
            or nested_meta.get("figure_title")
            or nested_meta.get("paper_title")
            or metadata_dict.get("title")
            or ""
        )
        summary = str(
            content_dict.get("summary")
            or nested_meta.get("concise_summary")
            or content_dict.get("raw_text_content")
            or ""
        )
        insight = str(
            content_dict.get("insight")
            or nested_meta.get("inferred_insight")
            or ""
        )

        evidence_lines.append(
            f"[{idx}] id={item.id}\n"
            f"title={title}\n"
            f"summary={summary}\n"
            f"insight={insight}\n"
            f"score={item.score}\n"
        )
        response_evidence.append(
            {
                "id": item.id,
                "score": item.score,
                "title": title,
                "summary": summary,
                "insight": insight,
                "metadata": item.metadata,
            }
        )

    report_system_prompt = """
You are a scientific report writing assistant.
Answer the user question strictly based on the provided evidence and output an English Markdown report.

Requirements:
1) Do not fabricate facts. If evidence is insufficient, explicitly state "insufficient evidence".
2) The report must include the following sections:
   - Key Conclusions (3-5 bullets)
   - Evidence-Based Analysis (organized by themes)
   - Method/Data Limitations
   - Actionable Next Steps (3 items)
3) After each key claim, cite evidence IDs using this format:
   [Evidence: chunk_xxx, chunk_yyy]
4) Keep the writing clear, concise, and academically grounded.
"""

    report_user_prompt = (
        f"User question:\n{query}\n\n"
        f"Available evidence (total {len(evidence_items)} items):\n"
        + "\n".join(evidence_lines)
        + "\nPlease generate the final report."
    )

    if len(evidence_items) == 0:
        fallback_report = (
            "## Key Conclusions\n"
            "- The current retrieval returned no usable evidence for this question.\n\n"
            "## Evidence-Based Analysis\n"
            "- None.\n\n"
            "## Method/Data Limitations\n"
            "- Semantic retrieval returned no usable items. This may be caused by query wording, score threshold, or data coverage.\n\n"
            "## Actionable Next Steps\n"
            "- Rewrite the query with clearer domain keywords and retry.\n"
            "- Relax retrieval constraints to increase recall.\n"
            "- Enrich the corpus with more relevant literature, then regenerate the report.\n"
        )
        payload = {
            "query": query,
            "report": fallback_report,
            "used_evidence_count": 0,
            "evidence": [],
            "saved_path": "",
        }
        saved_path = save_report_payload(payload)
        payload["saved_path"] = saved_path
        # 回写文件中的 saved_path
        save_report_payload(payload, target_path=saved_path)
        return payload

    client = create_model_client()
    try:
        resp = await client.create(
            messages=[
                SystemMessage(content=report_system_prompt),
                UserMessage(content=report_user_prompt, source="user"),
            ],
            cancellation_token=None,
        )
        report_text = normalize_model_text(resp.content).strip() or "Report generation failed: empty model response."
    except Exception as e:
        report_text = f"Report generation failed: {e}"
    finally:
        try:
            await client.close()
        except Exception:
            pass

    payload = {
        "query": query,
        "report": report_text,
        "used_evidence_count": len(evidence_items),
        "evidence": response_evidence,
        "saved_path": "",
    }
    saved_path = save_report_payload(payload)
    payload["saved_path"] = saved_path
    # 回写文件中的 saved_path
    save_report_payload(payload, target_path=saved_path)
    return payload


def save_report_payload(payload: Dict[str, Any], target_path: str = "") -> str:
    """
    保存报告到 logs/simple_reports 目录，返回保存绝对路径。
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, "logs", "simple_reports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = target_path
    if not out_path:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(out_dir, f"simple_report_{ts}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    return out_path


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8010)
