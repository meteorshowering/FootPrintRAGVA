#!/usr/bin/env python3
"""
【功能】由 enhanced_figures_with_paperid.json 生成 paper_info.json，并输出数字 paper_id 版 figures JSON。
【长期价值】历史数据修复脚本；可归档。
"""

import json
import os

# 定义文件路径
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file_path = os.path.join(script_dir, "enhanced_figures_with_paperid.json")
paper_info_output_path = os.path.join(script_dir, "paper_info.json")
updated_figures_output_path = os.path.join(script_dir, "enhanced_figures_with_numeric_paperid.json")

def generate_paper_info():
    """生成paper信息JSON文件"""
    print("=== 生成paper信息JSON文件 ===")
    
    try:
        # 读取现有JSON文件
        with open(input_file_path, "r", encoding="utf-8") as f:
            figures = json.load(f)
        
        print(f"📦 成功读取 {len(figures)} 条数据")
        
        # 1. 收集所有唯一的paper名称
        paper_dict = {}
        for figure in figures:
            paper_name = figure.get("paper_id", "unknown")
            if paper_name not in paper_dict:
                paper_dict[paper_name] = []
            paper_dict[paper_name].append(figure)
        
        print(f"📚 共发现 {len(paper_dict)} 个唯一的paper")
        
        # 2. 为每个paper分配唯一的数字ID，并统计图片数量
        paper_info_list = []
        paper_id_map = {}
        
        for i, (paper_name, paper_figures) in enumerate(sorted(paper_dict.items()), 1):
            paper_id = i  # 使用纯数字ID
            image_count = len(paper_figures)
            
            # 构建paper信息
            paper_info = {
                "id": paper_id,
                "name": paper_name,
                "image_count": image_count
            }
            paper_info_list.append(paper_info)
            paper_id_map[paper_name] = paper_id
            
            print(f"✅ 分配ID: {paper_id} -> {paper_name} (图片数量: {image_count})")
        
        # 3. 生成paper信息JSON文件
        with open(paper_info_output_path, "w", encoding="utf-8") as f:
            json.dump(paper_info_list, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 生成paper信息文件成功: {paper_info_output_path}")
        print(f"📊 共 {len(paper_info_list)} 个paper记录")
        
        # 4. 更新原JSON文件，将paper_id从名称改为数字ID
        updated_figures = []
        for figure in figures:
            paper_name = figure.get("paper_id", "unknown")
            figure["paper_id"] = paper_id_map.get(paper_name, "paper_unknown")
            updated_figures.append(figure)
        
        # 写入更新后的JSON文件
        with open(updated_figures_output_path, "w", encoding="utf-8") as f:
            json.dump(updated_figures, f, ensure_ascii=False, indent=2)
        
        print(f"🎉 生成更新后的图片数据文件成功: {updated_figures_output_path}")
        print(f"📊 共 {len(updated_figures)} 条图片记录")
        
        return True
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = generate_paper_info()
    exit(0 if result else 1)