"""
【功能】从 llmvis_images_info.json 与 md-llmvis 正文匹配图题、抽取参考文献上下文，输出 llmvis_extracted_refer.json。
【长期价值】数据预处理脚本；管线稳定后可保留作可复现步骤，否则归档。
"""
import os
import json
import re
from collections import defaultdict
from difflib import SequenceMatcher
from tqdm import tqdm

# ----------------- 1. 配置参数 -----------------
# 刚刚生成的 JSON 文件路径
METADATA_JSON_FILE = "llmvis_images_info.json"
# 存储 Markdown 文件的目录
MARKDOWN_DIR = "md-llmvis/"
# 输出的、包含了引用上下文的新 JSON 文件
OUTPUT_JSON_FILE = "llmvis_extracted_refer.json"

# --- 筛选阈值 (您可以根据效果调整) ---
CAPTION_KEYWORD_THRESHOLD = 0.5
CAPTION_DEDUPE_THRESHOLD = 0.8
# -----------------------------------------------

STOPWORDS = {'a', 'an', 'the', 'in', 'on', 'of', 'for', 'with', 'by', 'at', 'about',
             'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
             'to', 'as', 'this', 'that', 'it', 'we', 'they', 'i', 'you', 'he', 'she',
             'fig', 'figure', 'based', 'using', 'shows', 'show'}

def extract_figure_number(path_or_title):
    match = re.search(r'(?:figure|fig|图)\s?_?\.?\s?(\d+)', path_or_title, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def find_references_by_number(paragraphs, fig_num):
    found_paragraphs = []
    pattern = re.compile(r'\b(figure|fig)\.?\s+' + re.escape(fig_num) + r'\b', re.IGNORECASE)
    for p in paragraphs:
        if pattern.search(p):
            found_paragraphs.append(p)
    return found_paragraphs

def get_keywords(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return {word for word in words if word not in STOPWORDS and len(word) > 2}

def find_references_by_caption(paragraphs, caption, threshold):
    caption_keywords = get_keywords(caption)
    if not caption_keywords:
        return []

    found_paragraphs = []
    for p in paragraphs:
        p_keywords = get_keywords(p)
        if len(caption_keywords) == 0:
            continue
        score = len(caption_keywords.intersection(p_keywords)) / len(caption_keywords)
        if score >= threshold:
            found_paragraphs.append(p)
    return found_paragraphs

def process_and_clean_references(references, current_caption, dedupe_threshold):
    image_pattern = re.compile(r'(!\[.*?\]\(.*?\)\n?)(.*)', re.DOTALL)
    final_references = []
    unique_references = list(dict.fromkeys(references))

    for ref in unique_references:
        match = image_pattern.match(ref)
        if match:
            text_after_image = match.group(2).strip()
            similarity = SequenceMatcher(None, text_after_image.lower(), current_caption.lower()).ratio()
            if similarity > dedupe_threshold:
                continue
            else:
                final_references.append(text_after_image)
        else:
            similarity = SequenceMatcher(None, ref.lower(), current_caption.lower()).ratio()
            if similarity < dedupe_threshold:
                final_references.append(ref)
    
    return list(dict.fromkeys(final_references))

if __name__ == "__main__":
    if not os.path.exists(METADATA_JSON_FILE):
        print(f"❌ 找不到输入文件: {METADATA_JSON_FILE}")
        exit()

    with open(METADATA_JSON_FILE, 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    # 按照 source_md 分组
    papers = defaultdict(list)
    for item in all_data:
        papers[item['source_md']].append(item)

    enhanced_data = []
    
    for md_filename, figures_in_paper in tqdm(papers.items(), desc="Processing References"):
        md_file_path = os.path.join(MARKDOWN_DIR, md_filename)
        
        if not os.path.exists(md_file_path):
            for item in figures_in_paper:
                item['references'] = []
                enhanced_data.append(item)
            continue

        with open(md_file_path, 'r', encoding='utf-8') as f:
            paragraphs = [p.strip() for p in re.split(r'\n\s*\n', f.read()) if p.strip()]

        for item in figures_in_paper:
            # MinerU 的编号通常不准确，我们会退而求其次利用图题去匹配
            figure_number = extract_figure_number(item['save_path']) or extract_figure_number(item['title'])
            caption = item['title']
            
            all_found = []
            
            if figure_number:
                all_found.extend(find_references_by_number(paragraphs, figure_number))
            
            all_found.extend(find_references_by_caption(paragraphs, caption, CAPTION_KEYWORD_THRESHOLD))
            
            final_references = process_and_clean_references(all_found, caption, CAPTION_DEDUPE_THRESHOLD)
            item['references'] = final_references
            enhanced_data.append(item)

    with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(enhanced_data, f, ensure_ascii=False, indent=2)

    print(f"\n--- 提取成功！ ---")
    print(f"已将引用数据保存到: {OUTPUT_JSON_FILE}")