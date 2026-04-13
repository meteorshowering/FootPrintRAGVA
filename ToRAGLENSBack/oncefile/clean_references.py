import os
import re

def clean_references_from_md_files(directory):
    """删除md文件中references标题之后的所有内容"""
    # 匹配references标题的正则表达式（大小写不敏感）
    references_pattern = re.compile(r'^#{1,6}\s+references\b', re.IGNORECASE)
    
    # 统计处理的文件数
    processed_count = 0
    modified_count = 0
    
    # 遍历目录下的所有md文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                processed_count += 1
                
                try:
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # 查找references标题的位置
                    references_index = -1
                    for i, line in enumerate(lines):
                        if references_pattern.match(line.strip()):
                            references_index = i
                            break
                    
                    # 如果找到references标题，截取内容
                    if references_index != -1:
                        # 只保留到references标题所在行（包括该行）
                        modified_lines = lines[:references_index + 1]
                        
                        # 写回文件
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.writelines(modified_lines)
                        
                        modified_count += 1
                        print(f"✅ 处理文件: {file} - 删除了references之后的内容")
                    else:
                        print(f"ℹ️ 处理文件: {file} - 未找到references标题")
                
                except Exception as e:
                    print(f"❌ 处理文件 {file} 时出错: {e}")
    
    print(f"\n=== 处理完成 ===")
    print(f"处理的文件数: {processed_count}")
    print(f"修改的文件数: {modified_count}")

if __name__ == "__main__":
    # 指定paper_md目录路径
    paper_md_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paper_md")
    print(f"开始处理目录: {paper_md_dir}")
    clean_references_from_md_files(paper_md_dir)
