#!/usr/bin/env python3
"""
【功能】对嵌入结果做聚类得到全局地图坐标，并用 TF-IDF 提取每簇关键词。
读取 LLMvisDataset_embedding.json，输出 LLMvisDataset_cluster_keywords.json，并拷贝到 mapfront/public/。

【长期价值】运维/数据管道可保留；底图或聚类策略变更后按需运行；与前端全局地图标签联动。
"""
import json
import re
import argparse
from pathlib import Path
import shutil

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

# 额外停用词（学术论文、Markdown 常见噪声等）
EXTRA_STOP = {
    "abstract", "introduction", "section", "figure", "table", "doi", "arxiv",
    "et", "al", "vol", "pp", "fig", "eq", "http", "https", "www", "com", "org",
    "the", "and", "of", "in", "to", "a", "is", "for", "that", "on", "as", "with",
    "by", "this", "are", "be", "we", "can", "an", "from", "it", "which", "or",
    "has", "have", "such", "not", "but", "also", "these", "their", "our", "all",
    "one", "more", "about", "other", "when", "at", "if", "used", "two", "some",
    "use", "using", "based", "paper", "proposed", "method", "results", "data",
    "model", "performance", "approach", "show", "different", "different",
    "time", "new", "each", "both", "only", "many", "well", "through", "how",
    "its", "into", "between", "under", "where", "any", "first", "most", "same",
    "there", "then", "would", "because", "could", "should", "those", "while",
    "during", "since", "until", "after", "before", "very", "even", "much",
    "often", "just", "like", "so", "than", "too", "up", "out", "down", "over",
    "under", "again", "further", "once", "here", "there", "why", "who", "what",
    "where", "when", "how", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "can", "will", "just", "don", "should", "now"
}
STOP = ENGLISH_STOP_WORDS.union(EXTRA_STOP)

def flatten_content(item):
    """提取内容文本"""
    c = item.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, dict):
        parts = [c.get("title"), c.get("summary"), c.get("insight")]
        return "\n".join(str(p) for p in parts if p)
    return ""

def token_prep(text):
    """简单清洗文本"""
    # 移除 URL
    text = re.sub(r"https?://\S+", " ", text)
    # 移除 Markdown 符号
    text = re.sub(r"[#*_`\[\]()]", " ", text)
    # 转小写
    text = text.lower()
    return text

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="LLMvisDataset_embedding.json")
    ap.add_argument("--output", default="LLMvisDataset_cluster_keywords.json")
    ap.add_argument("--k", type=int, default=15, help="KMeans 簇数")
    ap.add_argument("--top-n", type=int, default=5, help="每簇关键词数量")
    args = ap.parse_args()

    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / args.input
    output_path = base_dir / args.output
    
    if not input_path.exists():
        print(f"❌ 找不到输入文件: {input_path}".encode('utf-8', errors='replace').decode('utf-8'))
        return

    print(f"读取数据文件: {input_path}")
    with input_path.open(encoding="utf-8") as f:
        data = json.load(f)

    # 提取坐标和文本
    X = []
    texts = []
    valid_indices = []
    
    for i, item in enumerate(data):
        coords = item.get("coordinates_2d")
        if coords and len(coords) == 2:
            X.append(coords)
            texts.append(token_prep(flatten_content(item)))
            valid_indices.append(i)
            
    if not X:
        print("❌ 未找到包含二维坐标的数据")
        return
        
    X = np.array(X, dtype=np.float64)
    print(f"成功提取 {len(X)} 个点的二维坐标")

    # KMeans 聚类
    print(f"执行 KMeans 聚类，k={args.k}...")
    kmeans = KMeans(n_clusters=args.k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)

    clusters = {}
    for idx, lab in enumerate(labels):
        clusters.setdefault(int(lab), []).append(idx)

    print("使用大模型提取全局语义关键词...")
    
    import requests
    API_URL = "http://38.147.105.35:3030/v1/chat/completions"
    API_KEY = "sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
    MODEL_NAME = "gpt-4o"
    
    # 1. 准备每个簇的样本并计算中心
    sorted_labs = sorted(clusters.keys())
    centroids = []
    sizes = []
    
    out_clusters = []
    
    for lab in sorted_labs:
        indices = clusters[lab]
        sizes.append(len(indices))
        
        # 质心
        sub_X = X[indices]
        centroid = sub_X.mean(axis=0)
        centroids.append(centroid.tolist())
        
        # 找到距离中心最近的前 10 个 chunk 作为样本
        distances = np.linalg.norm(sub_X - centroid, axis=1)
        closest_local_indices = distances.argsort()[:10]
        closest_texts = [texts[indices[i]] for i in closest_local_indices]
        
        sample_content = "\n\n---\n\n".join(closest_texts)
        if len(sample_content) > 8000:
            sample_content = sample_content[:8000]
            
        sys_msg = "You are an expert academic researcher. Read the following scientific paper excerpts from a specific research cluster. Summarize their core research direction or topic using exactly ONE professional English academic term or short phrase (e.g. Visual Analytics, Neural Networks, Contrastive Learning). Return ONLY the term, no quotes, no extra words."
        
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": f"Excerpts:\n{sample_content}"}
            ],
            "max_tokens": 15,
            "temperature": 0.2
        }
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        
        top_keywords = []
        try:
            print(f"正在为簇 {lab} 请求大模型生成标签...")
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                term = resp.json()["choices"][0]["message"]["content"].strip()
                # 简单清理可能包含的标点或换行
                term = term.strip("'\" \n\r")
                top_keywords = [{"term": term, "score": 1.0}]
                print(f"  -> 生成标签: {term}".encode('utf-8', errors='replace').decode('utf-8'))
            else:
                print(f"  -> 请求失败, 状态码: {resp.status_code}".encode('utf-8', errors='replace').decode('utf-8'))
        except Exception as e:
            print(f"  -> API异常: {e}".encode('utf-8', errors='replace').decode('utf-8'))
            
        out_clusters.append({
            "cluster_id": lab,
            "size": len(indices),
            "centroid_2d": centroid.tolist(),
            "top_keywords": top_keywords,
        })

    payload = {
        "source_file": str(input_path.name),
        "method": "kmeans",
        "params": {"k": args.k},
        "n_points": len(X),
        "clusters": out_clusters,
    }
    
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"✅ 生成聚类关键词完成，共 {len(out_clusters)} 个簇，已保存至: {output_path}".encode('utf-8', errors='replace').decode('utf-8'))
    
    # 同步拷贝到前端 public 目录
    front_dest = base_dir.parent / "mapfront" / "public" / args.output
    try:
        front_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output_path, front_dest)
        print(f"✅ 已同步拷贝到前端目录: {front_dest}".encode('utf-8', errors='replace').decode('utf-8'))
    except Exception as e:
        print(f"⚠️ 拷贝到前端目录失败: {e}".encode('utf-8', errors='replace').decode('utf-8'))

if __name__ == "__main__":
    main()
