#!/usr/bin/env python3
"""
聚类全局地图坐标，并使用 TF-IDF 提取每簇的关键词。
读取: LLMvisDataset_embedding.json
输出: LLMvisDataset_cluster_keywords.json，并自动拷贝到前端 mapfront/public/
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

    print("提取全局 TF-IDF 关键词...")
    
    # 1. 准备全局语料库，每个簇合并为一个大文档
    sorted_labs = sorted(clusters.keys())
    macro_corpus = []
    centroids = []
    sizes = []
    
    for lab in sorted_labs:
        indices = clusters[lab]
        sizes.append(len(indices))
        
        # 质心
        sub_X = X[indices]
        centroids.append(sub_X.mean(axis=0).tolist())
        
        # 合并簇内的所有文本为一个大文档
        macro_text = " ".join([texts[i] for i in indices])
        macro_corpus.append(macro_text)
        
    # 2. 计算基于簇维度的 TF-IDF
    # 用户要求：找到自己内部多而在别的聚类中少的 -> "除了自己之外所有的(都不出现)" -> max_df=1
    vec = TfidfVectorizer(
        max_features=5000,
        stop_words=list(STOP),
        token_pattern=r"(?u)\b[a-z][a-z0-9\-]{2,}\b",
        ngram_range=(1, 2),
        min_df=1,
        max_df=1, # 强制要求：只在当前1个聚类中出现，其他聚类均不出现
    )
    
    try:
        tfidf_matrix = vec.fit_transform(macro_corpus)
        terms = np.array(vec.get_feature_names_out())
    except ValueError:
        tfidf_matrix = None
        terms = []

    out_clusters = []
    for i, lab in enumerate(sorted_labs):
        if tfidf_matrix is not None:
            # 取当前聚类的 TF-IDF 分数
            scores = np.asarray(tfidf_matrix[i].todense()).ravel()
            top_idx = scores.argsort()[::-1][: args.top_n]
            top_keywords = [
                {"term": str(terms[j]), "score": float(scores[j])}
                for j in top_idx
                if scores[j] > 0
            ]
        else:
            top_keywords = []

        out_clusters.append({
            "cluster_id": lab,
            "size": sizes[i],
            "centroid_2d": centroids[i],
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
