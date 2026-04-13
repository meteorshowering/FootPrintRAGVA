#!/usr/bin/env python3
"""
生成包含正确paper_id的JSON文件
从save_path中提取倒数第二个目录名称作为paper_id
"""

import json
import os

# 定义文件路径
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file_path = os.path.join(script_dir, "enhanced_figures_afterllm_reassigned_ids.json")
output_file_path = os.path.join(script_dir, "enhanced_figures_with_paperid.json")

def generate_paperid_json():
    """生成包含正确paper_id的JSON文件"""
    print("=== 生成包含paper_id的JSON文件 ===")
    
    try:
        # 读取现有JSON文件
        with open(input_file_path, "r", encoding="utf-8") as f:
            figures = json.load(f)
        
        print(f"📦 成功读取 {len(figures)} 条数据")
        
        # 遍历每个条目，添加paper_id
        updated_figures = []
        for figure in figures:
            # 获取save_path
            save_path = figure.get("save_path", "")
            if not save_path:
                print(f"⚠️  跳过缺少save_path的条目: {figure.get('id', 'unknown')}")
                continue
            
            # 解析路径，提取倒数第二个目录名称作为paper_id
            try:
                # 使用os.path.normpath处理路径，确保跨平台兼容性
                norm_path = os.path.normpath(save_path)
                # 分割路径
                path_parts = norm_path.split(os.path.sep)
                # 倒数第二个目录是paper_id
                if len(path_parts) >= 2:
                    paper_id = path_parts[-2]
                    # 更新figure的paper_id字段
                    figure["paper_id"] = paper_id
                    updated_figures.append(figure)
                    print(f"✅ 处理成功: {figure.get('id')} -> paper_id: {paper_id}")
                else:
                    print(f"⚠️  路径格式不正确，跳过: {save_path}")
            except Exception as e:
                print(f"❌ 解析路径失败 ({save_path}): {e}")
        
        # 写入新的JSON文件
        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(updated_figures, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 生成成功！")
        print(f"📄 输入文件: {input_file_path}")
        print(f"📄 输出文件: {output_file_path}")
        print(f"📊 总条目数: {len(updated_figures)}")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_paperid_json()