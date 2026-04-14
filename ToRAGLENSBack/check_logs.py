"""
【功能】极简脚本：读取写死的某次 experiment_results JSON，按轮次打印 tool、rag 条数等（调试统计）。
【长期价值】一次性调试片段；路径写死后易失效，可删或改为命令行参数。
"""
import json
with open('logs/experiment_results_20260330_111312.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
    
for it in d.get('iterations', []):
    for qr in it.get('query_results', []):
        p = qr.get('orchestrator_plan', {})
        rag = qr.get('rag_results', [])
        print(f"Round {it.get('round_number')}: {p.get('tool_name')} | n_rag: {len(rag)} | dups: {p.get('duplicate_results')} | total: {p.get('total_results')} | intent: {p.get('args', {}).get('query_intent')}")
