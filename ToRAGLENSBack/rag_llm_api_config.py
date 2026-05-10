"""
【功能】RAG 相关 LLM 网关（报告、HyDE、Rerank）的配置入口。
【用法】日常改模型或地址：直接改下面「主配置」常量即可，不必设置系统环境变量。
      若部署时需要不把密钥写进代码，可再设置同名环境变量，会覆盖这里的默认值。
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Final, Optional

# =============================================================================
# 主配置 —— 直接改这里（未设置环境变量时使用）
# =============================================================================
GATEWAY_BASE_URL: Final[str] = "https://ssvip.dmxapi.com/v1"
GATEWAY_API_KEY: Final[str] = (
    "sk-8S92KJLEQcfF9TbjsLfSPrP3LRz6tsuzbRRpHXVH12Gp4SZc"
)
# 与主编排 / single_strategy 使用的 chat 模型对齐；可用环境变量 RAG_REPORT_MODEL 覆盖
REPORT_MODEL: Final[str] = "gpt-4o"
# HyDE 用的 chat 模型；空字符串表示与 REPORT_MODEL 相同
HYDE_MODEL: Final[str] = ""
RERANK_MODEL: Final[str] = "qwen3-reranker:8b"
# Rerank 与主编排网关分离：默认仍走原 uni-api（chat/HyDE/报告用 GATEWAY_*）
RERANK_GATEWAY_URL: Final[str] = "https://uni-api.cstcloud.cn/v1/rerank"
RERANK_GATEWAY_API_KEY: Final[str] = (
    "f24a9af08a33a9649b3f149706c8c45e8602a884b8beab6abae0d608226477f8"
)
# Rerank 完整 URL；空则使用 RERANK_GATEWAY_URL（不用 GATEWAY_BASE_URL + /rerank）
RERANK_URL: Final[str] = ""
# Rerank 专用 Key；空则使用 RERANK_GATEWAY_API_KEY（不用 GATEWAY_API_KEY）
RERANK_API_KEY: Final[str] = ""

# =============================================================================
# 语义检索：向量召回池与阈值（配合 HyDE + Rerank）
# =============================================================================
# 开启 Rerank 时，从 Chroma 多取候选再重排；最终返回条数仍由 query_by_semantic(n_results) 决定。
SEMANTIC_RERANK_POOL_MULTIPLIER: Final[int] = 5
SEMANTIC_RERANK_POOL_MIN: Final[int] = 20
SEMANTIC_RERANK_POOL_MAX: Final[int] = 80
# 开启 Rerank 时，向量阶段有效阈值 = min(调用方 score_threshold, 下列值)。
# 0.0 表示不在向量阶段按分数再筛（保留本次 query 的 top-k 全体交给 Rerank）；若需省 rerank 费用可改为 0.05～0.1。
SEMANTIC_VECTOR_THRESHOLD_CAP_WHEN_RERANK: Final[float] = 0.0

# =============================================================================
# 可选环境变量（有值则覆盖上面常量，便于 CI/服务器注入）
#   RAG_REPORT_BASE_URL, RAG_REPORT_API_KEY, RAG_REPORT_MODEL
#   RAG_SEMANTIC_API_BASE_URL, RAG_SEMANTIC_API_KEY
#   RAG_HYDE_MODEL, RAG_RERANK_URL, RAG_RERANK_MODEL, RAG_RERANK_API_KEY
#   （未设 RAG_RERANK_* 时 Rerank 默认走 uni-api，与 RERANK_GATEWAY_* 一致）
# 开关（在 rag_service 等调用方读取）: RAG_HYDE_ENABLED, RAG_RERANK_ENABLED
# =============================================================================


def _env_first(*keys: str) -> Optional[str]:
    for k in keys:
        v = os.getenv(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return None


def env_flag(key: str, default: str = "true") -> bool:
    return os.getenv(key, default).strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class RAGLLMAPISettings:
    """解析后的 LLM 网关与语义增强参数（不可变）。"""

    base_url: str
    api_key: str
    report_model: str
    hyde_model: str
    rerank_url: str
    rerank_model: str
    rerank_api_key: str

    def chat_completions_url(self) -> str:
        return f"{self.base_url}/chat/completions"

    @classmethod
    def from_env(cls) -> RAGLLMAPISettings:
        """文件常量 + 可选环境变量覆盖。"""
        base = (
            _env_first("RAG_SEMANTIC_API_BASE_URL", "RAG_REPORT_BASE_URL")
            or GATEWAY_BASE_URL
        ).rstrip("/")
        key = (
            _env_first("RAG_SEMANTIC_API_KEY", "RAG_REPORT_API_KEY") or GATEWAY_API_KEY
        )
        report_model = _env_first("RAG_REPORT_MODEL") or REPORT_MODEL
        hyde_model = _env_first("RAG_HYDE_MODEL") or (HYDE_MODEL or report_model)
        rerank_model = _env_first("RAG_RERANK_MODEL") or RERANK_MODEL
        rerank_url = _env_first("RAG_RERANK_URL") or (
            RERANK_URL.strip() or RERANK_GATEWAY_URL
        )
        rerank_key = _env_first("RAG_RERANK_API_KEY") or (
            RERANK_API_KEY.strip() if RERANK_API_KEY.strip() else RERANK_GATEWAY_API_KEY
        )
        return cls(
            base_url=base,
            api_key=key,
            report_model=report_model,
            hyde_model=hyde_model,
            rerank_url=rerank_url,
            rerank_model=rerank_model,
            rerank_api_key=rerank_key,
        )


def get_rag_llm_api_settings() -> RAGLLMAPISettings:
    return RAGLLMAPISettings.from_env()


def semantic_vector_threshold(score_threshold: float, rerank_enabled: bool) -> float:
    """Rerank 开启时放宽向量门限，避免 HyDE/长查询下误杀 rerank 候选。"""
    t = float(score_threshold)
    if not rerank_enabled:
        return t
    cap = float(SEMANTIC_VECTOR_THRESHOLD_CAP_WHEN_RERANK)
    return min(t, cap)


def semantic_chroma_pool_size(n_results: int, rerank_enabled: bool) -> tuple[int, int]:
    """
    返回 (chroma_n_results, cap_after_threshold_filter)。
    未开 Rerank 时二者均等于 n_results；开启时放大池子供 rerank 使用。
    """
    n_out = max(1, int(n_results))
    if not rerank_enabled:
        return n_out, n_out
    fetch = min(
        SEMANTIC_RERANK_POOL_MAX,
        max(SEMANTIC_RERANK_POOL_MIN, n_out * SEMANTIC_RERANK_POOL_MULTIPLIER),
    )
    return fetch, fetch
