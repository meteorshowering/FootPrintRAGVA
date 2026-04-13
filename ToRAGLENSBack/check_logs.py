import json
with open('logs/experiment_results_20260330_111312.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
    
for it in d.get('iterations', []):
    for qr in it.get('query_results', []):
        p = qr.get('orchestrator_plan', {})
        rag = qr.get('rag_results', [])
        print(f"Round {it.get('round_number')}: {p.get('tool_name')} | n_rag: {len(rag)} | dups: {p.get('duplicate_results')} | total: {p.get('total_results')} | intent: {p.get('args', {}).get('query_intent')}")
