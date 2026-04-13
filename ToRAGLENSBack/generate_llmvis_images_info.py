import os
import json
import re
from urllib.parse import urlparse

def generate_images_info_from_mineru(md_dir, output_json_path):
    """
    遍历 md-llmvis 文件夹中的所有 .md 文件，
    提取 Markdown 中包含的本地图片链接和图题描述，
    生成与 predataprocess 流程兼容的 images_info.json。
    """
    
    if not os.path.exists(md_dir):
        print(f"❌ 找不到输入目录: {md_dir}")
        return

    images_info = []
    
    # 遍历所有的 .md 文件
    md_files = [f for f in os.listdir(md_dir) if f.endswith('.md')]
    print(f"Find {len(md_files)} Markdown files, ready to extract images info...")

    for md_file in md_files:
        md_path = os.path.join(md_dir, md_file)
        
        with open(md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        content = "".join(lines)
        
        # 匹配 Markdown 图片：![alt](url)
        # 此时 URL 应该是上一步我们下载完后替换的本地相对路径 (例如: images/MinerU_xxx/figure_1.jpg)
        image_matches = list(re.finditer(r'!\[(.*?)\]\(([^)]+)\)', content))
        
        for i, img_match in enumerate(image_matches):
            alt_text = img_match.group(1).strip()
            image_rel_path = img_match.group(2).strip()
            
            # 找到图片在文件中的位置，试图提取图片下方的文本作为标题
            img_pos = img_match.end()
            img_line_start = content[:img_pos].count('\n')
            
            caption_lines = []
            title = ""
            
            # 向下查找几行，收集非空行作为图题
            for j in range(img_line_start, min(img_line_start + 10, len(lines))):
                line = lines[j].strip()
                if line:
                    # 如果遇到另一个图片或者标题符则停止收集
                    if line.startswith('!') or line.startswith('#'):
                        break
                    caption_lines.append(line)
                else:
                    if caption_lines:
                        break
            
            if caption_lines:
                title = ' '.join(caption_lines)
            
            if not title:
                title = alt_text if alt_text else f"Figure {i+1}"
                
            # 将相对路径转为绝对路径（以适应后续步骤）
            abs_image_path = os.path.abspath(os.path.join(md_dir, image_rel_path))
            
            images_info.append({
                'source_md': md_file,
                'save_path': abs_image_path,
                'title': title
            })
            
    # 保存结果
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(images_info, f, ensure_ascii=False, indent=4)
        
    print(f"Extraction completed! Found {len(images_info)} images.")
    print(f"Data saved to: {output_json_path}")

if __name__ == "__main__":
    # 配置输入和输出路径
    md_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "md-llmvis")
    output_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "llmvis_images_info.json")
    
    generate_images_info_from_mineru(md_directory, output_json)
