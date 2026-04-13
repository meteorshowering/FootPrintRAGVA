#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验数据分析脚本：对 experiment_results_*.json 进行统计与可视化用数据导出。
用于论文中的数据分析与系统评估。
运行：在 backandfront 目录下
  python experiment_analysis.py
  或指定文件： python experiment_analysis.py mapfront/public/experiment_results_20260222_164140.json
"""

import json
import os
import sys
from collections import defaultdict

def load_experiment(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_round_level(data: dict) -> dict:
    """轮次级：每轮检索调用数、总结果数、去重数、策略类型分布"""
    rounds = []
    for it in data.get("iterations", []):
        rn = it.get("round_number", -1)
        query_results = it.get("query_results", [])
        total_retrieved = 0
        total_duplicates = 0
        tools = []
        query_intents = []
        for qr in query_results:
            plan = qr.get("orchestrator_plan") or {}
            total_retrieved += plan.get("total_results", 0)
            total_duplicates += plan.get("duplicate_results", 0)
            tools.append(plan.get("tool_name", ""))
            args = plan.get("args") or {}
            query_intents.append(args.get("query_intent", ""))
        rounds.append({
            "round_number": rn,
            "num_queries": len(query_results),
            "total_results": total_retrieved,
            "duplicate_results": total_duplicates,
            "unique_results": total_retrieved - total_duplicates,
            "tools": tools,
            "query_intents": query_intents,
        })
    return {"rounds": rounds, "num_rounds": len(rounds)}


def analyze_evidence_level(data: dict) -> dict:
    """证据级：branch_action 分布、relevance/credibility 分布及与 retrieval score 的关系"""
    actions = defaultdict(int)
    relevance_list = []
    credibility_list = []
    retrieval_scores = []  # 仅对有 evaluation 的
    action_to_scores = defaultdict(lambda: {"relevance": [], "credibility": []})
    paper_ids = set()
    paper_action_count = defaultdict(lambda: defaultdict(int))
    per_round_actions = []  # 每轮 GROW/KEEP/PRUNE 数量，供按轮次绘图

    for it in data.get("iterations", []):
        rn = it.get("round_number", -1)
        round_actions = defaultdict(int)
        for qr in it.get("query_results", []):
            for item in qr.get("rag_results", []):
                res = item.get("retrieval_result", {})
                ev = item.get("evaluation")
                rid = (res.get("metadata") or {}).get("paperid") or (res.get("metadata") or {}).get("paper_id")
                if rid:
                    paper_ids.add(rid)
                score = res.get("score")
                if ev:
                    act = ev.get("branch_action", "")
                    actions[act] += 1
                    round_actions[act] += 1
                    sc = ev.get("scores") or {}
                    rel, cred = sc.get("relevance"), sc.get("credibility")
                    if rel is not None:
                        relevance_list.append(rel)
                        action_to_scores[act]["relevance"].append(rel)
                    if cred is not None:
                        credibility_list.append(cred)
                        action_to_scores[act]["credibility"].append(cred)
                    if rid:
                        paper_action_count[rid][act] += 1
                    if score is not None:
                        retrieval_scores.append({"retrieval_score": score, "relevance": rel, "credibility": cred, "action": act})
        per_round_actions.append({"round_number": rn, "GROW": round_actions["GROW"], "KEEP": round_actions["KEEP"], "PRUNE": round_actions["PRUNE"]})

    def avg(lst):
        return sum(lst) / len(lst) if lst else None

    return {
        "branch_action_counts": dict(actions),
        "total_evaluated": sum(actions.values()),
        "relevance": {"values": relevance_list, "mean": avg(relevance_list), "min": min(relevance_list) if relevance_list else None, "max": max(relevance_list) if relevance_list else None},
        "credibility": {"values": credibility_list, "mean": avg(credibility_list), "min": min(credibility_list) if credibility_list else None, "max": max(credibility_list) if credibility_list else None},
        "by_action": {act: {"relevance_mean": avg(action_to_scores[act]["relevance"]), "credibility_mean": avg(action_to_scores[act]["credibility"]), "count": len(action_to_scores[act]["relevance"])} for act in action_to_scores},
        "num_unique_papers": len(paper_ids),
        "paper_action_breakdown": {pid: dict(counts) for pid, counts in paper_action_count.items()},
        "retrieval_vs_evaluation": retrieval_scores,
        "per_round_actions": per_round_actions,
    }


def analyze_suggested_keywords(data: dict) -> dict:
    """suggested_keywords 出现频率及与 GROW 的关联"""
    keyword_counts = defaultdict(int)
    action_keyword = defaultdict(list)
    for it in data.get("iterations", []):
        for qr in it.get("query_results", []):
            for item in qr.get("rag_results", []):
                ev = item.get("evaluation")
                if not ev:
                    continue
                act = ev.get("branch_action", "")
                for kw in ev.get("suggested_keywords") or []:
                    keyword_counts[kw] += 1
                    action_keyword[act].append(kw)
    top_keywords = sorted(keyword_counts.items(), key=lambda x: -x[1])[:30]
    return {"keyword_counts": dict(keyword_counts), "top_keywords": top_keywords, "by_action": {k: len(v) for k, v in action_keyword.items()}}


def run_all_analyses(path: str) -> dict:
    data = load_experiment(path)
    root_goal = data.get("root_goal", "")
    round_stats = analyze_round_level(data)
    evidence_stats = analyze_evidence_level(data)
    keyword_stats = analyze_suggested_keywords(data)

    return {
        "root_goal": root_goal,
        "round_level": round_stats,
        "evidence_level": evidence_stats,
        "suggested_keywords": keyword_stats,
    }


def print_report(result: dict, filepath: str = ""):
    print("=" * 60)
    print("实验数据分析报告" + (f"  [{filepath}]" if filepath else ""))
    print("=" * 60)
    print("\n【根目标】", result["root_goal"][:80] + "..." if len(result["root_goal"]) > 80 else result["root_goal"])

    rl = result["round_level"]
    print("\n【轮次级】")
    print(f"  总轮数: {rl['num_rounds']}")
    for r in rl["rounds"]:
        dup_rate = (r["duplicate_results"] / r["total_results"] * 100) if r["total_results"] else 0
        print(f"  Round {r['round_number']}: 检索调用 {r['num_queries']} 次, 返回 {r['total_results']} 条, 重复 {r['duplicate_results']} 条 ({dup_rate:.0f}%), 工具 {r['tools']}")

    el = result["evidence_level"]
    print("\n【证据级】")
    print("  branch_action 分布:", el["branch_action_counts"])
    print(f"  被评估证据总数: {el['total_evaluated']}")
    print("  relevance: mean=%.2f, min=%s, max=%s" % (el["relevance"]["mean"] or 0, el["relevance"]["min"], el["relevance"]["max"]))
    print("  credibility: mean=%.2f, min=%s, max=%s" % (el["credibility"]["mean"] or 0, el["credibility"]["min"], el["credibility"]["max"]))
    print("  按 action 的平均分:")
    for act, v in el["by_action"].items():
        print(f"    {act}: relevance_mean={v['relevance_mean']:.2f}, credibility_mean={v['credibility_mean']:.2f}, count={v['count']}")
    print(f"  涉及唯一论文数: {el['num_unique_papers']}")

    kw = result["suggested_keywords"]
    print("\n【建议关键词】")
    print("  TOP 15:", kw["top_keywords"][:15])
    print("  各 action 产生的关键词条数:", kw["by_action"])

    # 检索分与评估分相关性（简单：同一条目）
    rev = el.get("retrieval_vs_evaluation", [])
    if rev:
        rels = [x["relevance"] for x in rev if x.get("relevance") is not None]
        rets = [x["retrieval_score"] for x in rev if x.get("relevance") is not None]
        if len(rets) > 1 and len(rels) == len(rets):
            try:
                import statistics
                corr_relevance = statistics.correlation(rets, rels)
            except AttributeError:
                # Python < 3.10
                def pearson(a, b):
                    n = len(a)
                    ma, mb = sum(a) / n, sum(b) / n
                    va = sum((x - ma) ** 2 for x in a) ** 0.5
                    vb = sum((x - mb) ** 2 for x in b) ** 0.5
                    if va == 0 or vb == 0:
                        return 0
                    return sum((a[i] - ma) * (b[i] - mb) for i in range(n)) / (va * vb)
                corr_relevance = pearson(rets, rels)
            print("\n【检索分 vs 评估相关性】")
            print("  retrieval_score 与 relevance 的 Pearson 相关系数: %.3f" % corr_relevance)
    print("=" * 60)


def export_for_plots(result: dict, out_dir: str):
    """导出供论文图表使用的简化数据（JSON）"""
    os.makedirs(out_dir, exist_ok=True)
    el = result["evidence_level"]
    # 按轮次统计 action 分布（需要再遍历一次）
    # 这里简化：只导出证据级汇总与关键词
    export = {
        "branch_action_distribution": el["branch_action_counts"],
        "relevance_credibility_by_action": el["by_action"],
        "relevance_summary": {"mean": el["relevance"]["mean"], "min": el["relevance"]["min"], "max": el["relevance"]["max"]},
        "credibility_summary": {"mean": el["credibility"]["mean"], "min": el["credibility"]["min"], "max": el["credibility"]["max"]},
        "top_keywords": result["suggested_keywords"]["top_keywords"][:20],
        "round_summary": [{"round": r["round_number"], "num_queries": r["num_queries"], "total_results": r["total_results"], "duplicate_results": r["duplicate_results"]} for r in result["round_level"]["rounds"]],
        "per_round_actions": el.get("per_round_actions", []),
    }
    out_path = os.path.join(out_dir, "experiment_analysis_export.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(export, f, ensure_ascii=False, indent=2)
    print("已导出图表用数据:", out_path)


def main():
    default_path = os.path.join(os.path.dirname(__file__), "mapfront", "public", "experiment_results_20260222_164140.json")
    path = sys.argv[1] if len(sys.argv) > 1 else default_path
    if not os.path.isfile(path):
        print("文件不存在:", path)
        sys.exit(1)
    result = run_all_analyses(path)
    print_report(result, path)
    export_dir = os.path.join(os.path.dirname(__file__), "analysis_output")
    export_for_plots(result, export_dir)


if __name__ == "__main__":
    main()
