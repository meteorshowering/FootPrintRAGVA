import json
import os
import glob

def remove_img_prefix(value):
    """移除字符串中的img_前缀"""
    if isinstance(value, str) and value.startswith('img_'):
        return value[4:]  # 移除前4个字符 'img_'
    return value

def process_json_file(file_path):
    """处理单个JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        
        # 遍历所有query_results
        if 'query_results' in data:
            for query_result in data['query_results']:
                # 处理orchestrator_plan.ParentNode
                if 'orchestrator_plan' in query_result and 'ParentNode' in query_result['orchestrator_plan']:
                    old_value = query_result['orchestrator_plan']['ParentNode']
                    new_value = remove_img_prefix(old_value)
                    if new_value != old_value:
                        query_result['orchestrator_plan']['ParentNode'] = new_value
                        modified = True
                        print(f"  - ParentNode: {old_value} -> {new_value}")
                
                # 处理rag_results中的retrieval_result.id和retrieval_result.metadata.id
                if 'rag_results' in query_result:
                    for rag_result in query_result['rag_results']:
                        if 'retrieval_result' in rag_result:
                            # 处理retrieval_result.id
                            if 'id' in rag_result['retrieval_result']:
                                old_value = rag_result['retrieval_result']['id']
                                new_value = remove_img_prefix(old_value)
                                if new_value != old_value:
                                    rag_result['retrieval_result']['id'] = new_value
                                    modified = True
                                    print(f"  - retrieval_result.id: {old_value} -> {new_value}")
                            
                            # 处理retrieval_result.metadata.id
                            if 'metadata' in rag_result['retrieval_result'] and 'id' in rag_result['retrieval_result']['metadata']:
                                old_value = rag_result['retrieval_result']['metadata']['id']
                                new_value = remove_img_prefix(old_value)
                                if new_value != old_value:
                                    rag_result['retrieval_result']['metadata']['id'] = new_value
                                    modified = True
                                    print(f"  - retrieval_result.metadata.id: {old_value} -> {new_value}")
        
        if modified:
            # 保存修改后的文件（覆盖原文件）
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ 已处理并保存: {file_path}")
        else:
            print(f"○ 无需修改: {file_path}")
            
    except Exception as e:
        print(f"✗ 处理文件 {file_path} 时出错: {e}")

def main():
    # 设置JSON文件目录
    json_dir = r"c:\liuxingyu\multisubspace-data\mapdesignpre\mapfront\mapfront\public\roundresult"
    
    # 查找所有JSON文件
    json_pattern = os.path.join(json_dir, "*.json")
    json_files = glob.glob(json_pattern)
    
    if not json_files:
        print(f"在目录 {json_dir} 中未找到JSON文件")
        return
    
    print(f"找到 {len(json_files)} 个JSON文件，开始处理...")
    print("=" * 50)
    
    for file_path in json_files:
        print(f"\n处理文件: {os.path.basename(file_path)}")
        process_json_file(file_path)
    
    print("\n" + "=" * 50)
    print("所有文件处理完成！")

if __name__ == "__main__":
    main()