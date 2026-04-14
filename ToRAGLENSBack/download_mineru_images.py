"""
【功能】解析 Markdown 中外链图片并下载到本地 images 目录，便于离线构建 LLMvis 数据集。
【长期价值】数据准备脚本；一次性爬取后可归档。
"""
import os
import re
import requests
import time
from urllib.parse import urlparse

def download_image(url, save_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"  ❌ 下载失败 {url}: {e}")
        return False

def process_mineru_markdowns(md_dir):
    if not os.path.exists(md_dir):
        print(f"❌ 找不到目录: {md_dir}")
        return

    images_base_dir = os.path.join(md_dir, "images")
    os.makedirs(images_base_dir, exist_ok=True)
    
    md_files = [f for f in os.listdir(md_dir) if f.endswith(".md")]
    print(f"📝 找到 {len(md_files)} 个 Markdown 文件，准备提取图片...")

    for md_file in md_files:
        md_path = os.path.join(md_dir, md_file)
        file_name_without_ext = os.path.splitext(md_file)[0]
        
        # 为每个 md 文件建立一个独立的图片文件夹
        specific_img_dir = os.path.join(images_base_dir, file_name_without_ext)
        
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 匹配 markdown 图片格式 ![alt](url)
        # 这里特别匹配以 http 开头的 URL
        pattern = r'!\[([^\]]*)\]\((https?://[^\)]+)\)'
        matches = re.findall(pattern, content)
        
        if not matches:
            continue
            
        print(f"📄 处理文件: {md_file} (包含 {len(matches)} 张网络图片)")
        os.makedirs(specific_img_dir, exist_ok=True)

        new_content = content
        download_count = 0

        for idx, (alt_text, img_url) in enumerate(matches):
            # 获取图片后缀
            parsed_url = urlparse(img_url)
            ext = os.path.splitext(parsed_url.path)[1]
            if not ext:
                ext = ".jpg"
                
            img_filename = f"figure_{idx+1}{ext}"
            save_path = os.path.join(specific_img_dir, img_filename)
            
            # 使用相对路径替换 md 中的链接
            relative_path = f"images/{file_name_without_ext}/{img_filename}"
            
            # 如果本地还没有这张图，就下载
            if not os.path.exists(save_path):
                print(f"  ⬇️ 下载图片 {idx+1}/{len(matches)}: {img_url}")
                if download_image(img_url, save_path):
                    download_count += 1
                    time.sleep(0.5) # 稍微延迟防封
            
            # 替换 Markdown 内容
            old_str = f"![{alt_text}]({img_url})"
            new_str = f"![{alt_text}]({relative_path})"
            new_content = new_content.replace(old_str, new_str)
            
        # 写回 Markdown 文件
        if download_count > 0 or new_content != content:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ 更新文件: {md_file}\n")
            
    print("🎉 所有 Markdown 文件的图片提取和路径替换完成！")

if __name__ == "__main__":
    # 指向 MinerU 解析结果所在的目录
    md_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "md-llmvis")
    process_mineru_markdowns(md_directory)
