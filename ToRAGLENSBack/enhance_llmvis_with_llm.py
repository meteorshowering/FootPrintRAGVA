import os
import sys
import json
import time
import base64
import requests 
from tqdm import tqdm
from PIL import Image


# ----------------- 1. 配置参数 -----------------
# 您的输入文件：已包含 x, y 和 references 的数据
INPUT_JSON_FILE = "llmvis_extracted_refer.json" 
# 输出文件：最终增强后的数据
OUTPUT_JSON_FILE = "llmvis_enhanced_afterllm.json" 

# 【OpenAI API 配置】
OPENAI_API_KEY = "sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
OPENAI_MODEL_NAME = "gpt-4o"
API_ENDPOINT = "http://38.147.105.35:3030/v1/chat/completions"
# -----------------------------------------------

def get_mime_type(image_path):
    ext = os.path.splitext(image_path)[1].lower()
    if ext in ['.jpg', '.jpeg']:
        return "image/jpeg"
    elif ext == '.png':
        return "image/png"
    else:
        return "application/octet-stream"

def encode_image_to_base64(image_path):
    try:
        Image.open(image_path).verify()
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"编码图片失败: {e}")
        return None

def get_llm_response_for_single_figure(figure_data):
    full_image_path = figure_data['save_path']
    base64_image = encode_image_to_base64(full_image_path)
    
    if not base64_image:
        return None
    
    mime_type = get_mime_type(figure_data['save_path'])

    system_prompt = '''
    You are an expert Visual Analytics Researcher and Scientific Content Analyzer. Your task is to analyze the provided scientific figure (visuals + context) and generate structured information. Strictly adhere to the required JSON output format and label constraints.
    '''
    text_context = f"caption: {figure_data['title']}\n\n references:\n- " + '\n- '.join(figure_data.get('references', []))
    
    functional_roles = {"Introduction & Background": ["Clarify Research Motivation", "Introduce Background Knowledge", "Exemplify Existing Limitations"],
                        "Methodology & Design": ["Elucidate Model Architecture", "Illustrate Algorithm Process", "Introduce Conceptual Framework", "Describe Data Flow", "Define Mathematical Formula"],
                        "Data & Experimental Setup": ["Showcase Dataset Samples", "Describe Data Distribution", "Introduce Experimental Setup", "Explain Data Preprocessing"],
                        "Results & Findings": ["Present Core Findings", "Compare Experimental Performance", "Present Quantitative Results" ,"Present Qualitative Results", "Showcase Prediction Results"],
                        "Analysis & Discussion": ["Analyze Component Contribution", "Exemplify Application Case", "Analyze Error Sources"],
                        "System & Application": ["Introduce System Functions", "Illustrate User Workflow", "Demonstrate UI Interaction"]}

    visual_types = {"Quantitative Charts": ["Line Chart", "Bar Chart", "Histogram", "Scatter Plot", "Pie Chart","Heatmap", "Box Plot", "Radar Chart"],
                       "Diagrams & Schematics": ["Flowchart", "Architecture Diagram", "Network / Graph Diagram", "Tree Diagram / Hierarchy", "Venn Diagram", "Conceptual Diagram"],
                       "Geospatial Visualizations": ["Map", "Satellite Image", "Space-Time Cube"],
                       "Qualitative & Representational Imagery": ["UI Screenshot", "Photograhp", "3D Rendering"],
                       "Tabular & Textual": ["Table", "Mathematical Equation", "Pseudocode"]}

    user_prompt_structure = f"""
    Task Definition:Please conduct a deep analysis of the scientific figure by combining the image provided and the textual context below.The textual context contains the figure caption and the references cited in the figure.
    You should generate infomation descibed below, and strictly adhere to the required JSON output format.
    Output Schema (Strictly Adhere):

    1. functional_roles: {{ "main_role": string, "sub_roles": [List of strings] }}
    1.1 main_role must be one of the following six main categories: 'Introduction & Background', 'Methodology & Design', 'Data & Experimental Setup', 'Results & Findings', 'Analysis & Discussion', 'System & Application'.
    1.2 sub_roles must be selected from the corresponding sub-category list. {functional_roles}

    2. visual_type: {{ "main_type": string, "sub_types": [List of strings] }}
    2.1 main_type must be one of the following six main categories: 'Quantitative Charts', 'Diagrams & Schematics', 'Geospatial Visualizations', 'Qualitative & Representational Imagery', 'Tabular & Textual', 'Composite & Multi-view'.
    2.2 Each label in the sub_types list must be selected from the corresponding sub-category list. {visual_types}

    3. key_entities: [List of strings] - Extract noun entities that have specific meaning within the scientific domain.

    4. concise_summary: String - Generate a description and summary of the figure's content, no more than 50 words.

    5. inferred_insight: String - Summarize the core argument or effect the author expects the reader to draw from this figure, no more than 50 words.

    6. caption: String - Extract the correct figure caption (e.g., "Figure 1: ...") from the provided text context. If not directly found, infer a short descriptive caption. Do NOT just output "image".

    The overall output must be a valid JSON string that adheres to the above schema, in the form of:
    {{
        "functional_roles": {{ "main_role": "string", "sub_roles": ["string"] }},
        "visual_type": {{ "main_type": "string", "sub_types": ["string"] }},
        "key_entities": ["string"],
        "concise_summary": "String",
        "inferred_insight": "String",
        "caption": "String"
    }}
    Please begin your analysis based on the following context:
    """

    request_payload = {
        "model": OPENAI_MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{user_prompt_structure}\n\n{text_context}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.2,
        "response_format": { "type": "json_object" }
    }

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            response = requests.post(
                API_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=request_payload,
                timeout=120
            )
            response.raise_for_status()
            
            response_json = response.json()
            if "choices" in response_json and len(response_json["choices"]) > 0:
                content_part = response_json["choices"][0]["message"]["content"]
                
                print(f"大模型返回的原始结果:\n{content_part}\n")
                
                # 移除 Markdown 格式的 code block 以防解析错误
                content_part = content_part.strip()
                if content_part.startswith("```json"):
                    content_part = content_part[7:]
                if content_part.startswith("```"):
                    content_part = content_part[3:]
                if content_part.endswith("```"):
                    content_part = content_part[:-3]
                content_part = content_part.strip()
                
                try:
                    parsed_json = json.loads(content_part)
                    return parsed_json
                except json.JSONDecodeError:
                    print(f"解析返回的 JSON 失败: {content_part}")
                    return None
            return None
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"API 请求失败 (尝试 {attempt + 1}/{max_retries})，{retry_delay}秒后重试: {e}")
                time.sleep(retry_delay)
            else:
                print(f"API 请求彻底失败: {e}")
                if 'response' in locals() and hasattr(response, 'text'):
                    print(f"服务器返回: {response.text}")
                return None

def process_figures():
    while True:
        # 如果已经存在上次处理的输出文件，则从输出文件继续加载进度
        if os.path.exists(OUTPUT_JSON_FILE):
            with open(OUTPUT_JSON_FILE, "r", encoding="utf-8") as f:
                figures_data = json.load(f)
        elif os.path.exists(INPUT_JSON_FILE):
            with open(INPUT_JSON_FILE, "r", encoding="utf-8") as f:
                figures_data = json.load(f)
        else:
            print(f"Input file not found: {INPUT_JSON_FILE}")
            return

        unprocessed_count = sum(1 for fig in figures_data if not fig.get('llm_processed', False))
        if unprocessed_count == 0:
            print("\n🎉 所有图片均已成功经过 LLM 处理！")
            break
            
        print(f"\n==============================================")
        print(f"Loaded {len(figures_data)} records, {unprocessed_count} remaining to be processed...")
        print(f"==============================================\n")

        for i, figure_data in enumerate(figures_data):
            if figure_data.get('llm_processed', False):
                continue
                
            print(f"[{i+1}/{len(figures_data)}] Processing figure: {os.path.basename(figure_data['save_path'])}")
            llm_response = get_llm_response_for_single_figure(figure_data)
            
            if llm_response:
                # 使用生成的 caption 覆盖 title
                caption_val = llm_response.get('caption', '').strip()
                if caption_val and caption_val.lower() != 'image':
                    figure_data['title'] = caption_val
                
                figure_data.update(llm_response)
                figure_data['llm_processed'] = True
            else:
                figure_data['llm_processed'] = False
                print(f"  [失败] {os.path.basename(figure_data['save_path'])} 处理失败，将在下一轮重试。")
                
            # 每处理完一个就实时保存
            with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(figures_data, f, ensure_ascii=False, indent=2)

        print(f"\n本轮遍历结束！即将开始下一轮检查遗漏项...\n")
        time.sleep(2)

    print(f"\nCompleted! All data saved to {OUTPUT_JSON_FILE}")

if __name__ == "__main__":
    # 进入脚本所在目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    process_figures()