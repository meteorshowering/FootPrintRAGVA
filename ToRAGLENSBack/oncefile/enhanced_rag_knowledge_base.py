#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版RAG知识库构建脚本

功能：
1. 整合论文文本内容和图片信息，创建统一的增强版RAG知识库
2. 为文本和图片数据添加类型标记和唯一标识
3. 生成映射关系文件，便于后续检索和管理

作者：AI Assistant
日期：2026-02-02
"""

import json
import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path


class EnhancedRAGKnowledgeBase:
    """增强版RAG知识库构建器"""
    
    def __init__(self, 
                 figures_json_path: str = "enhanced_figures_afterllm_reassigned_ids.json",
                 paper_md_dir: str = "paper_md",
                 output_dir: str = "enhanced_rag_output"):
        """
        初始化增强版RAG知识库构建器
        
        Args:
            figures_json_path: 图片数据JSON文件路径
            paper_md_dir: 论文MD文件目录
            output_dir: 输出文件目录
        """
        self.figures_json_path = figures_json_path
        self.paper_md_dir = paper_md_dir
        self.output_dir = output_dir
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 数据存储
        self.figures_data = []
        self.paper_texts = []
        self.enhanced_rag_data = []
        self.mapping_data = {}
        
        # 计数器
        self.chunk_id_counter = 0
        self.paper_id_counter = 0
        
    def load_figures_data(self) -> List[Dict]:
        """加载图片数据"""
        print("正在加载图片数据...")
        try:
            with open(self.figures_json_path, 'r', encoding='utf-8') as f:
                self.figures_data = json.load(f)
            print(f"成功加载 {len(self.figures_data)} 条图片数据")
            return self.figures_data
        except Exception as e:
            print(f"加载图片数据失败: {e}")
            return []
    
    def extract_paper_title_from_md(self, md_content: str) -> str:
        """从MD文件内容中提取论文标题"""
        # 提取第一个#标题作为论文标题
        lines = md_content.split('\n')
        for line in lines:
            if line.startswith('# ') and not line.startswith('##'):
                # 移除#号和前后空格
                title = line.replace('#', '').strip()
                # 移除可能的作者信息（如果标题包含作者）
                if '**' in title:
                    title = title.split('**')[0].strip()
                return title
        return ""
    
    def load_paper_texts(self) -> List[Dict]:
        """加载论文文本数据"""
        print("正在加载论文文本数据...")
        self.paper_texts = []
        
        paper_md_path = Path(self.paper_md_dir)
        if not paper_md_path.exists():
            print(f"论文MD目录不存在: {paper_md_path}")
            return []
        
        md_files = list(paper_md_path.glob("*.md"))
        print(f"找到 {len(md_files)} 个MD文件")
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取论文标题
                paper_title = self.extract_paper_title_from_md(content)
                if not paper_title:
                    paper_title = md_file.stem  # 使用文件名作为标题
                
                # 创建论文文本记录
                paper_record = {
                    "paper_title": paper_title,
                    "md_filename": md_file.name,
                    "md_filepath": str(md_file),
                    "content": content,
                    "content_length": len(content)
                }
                
                self.paper_texts.append(paper_record)
                
            except Exception as e:
                print(f"加载论文文件 {md_file} 失败: {e}")
        
        print(f"成功加载 {len(self.paper_texts)} 篇论文文本")
        return self.paper_texts
    
    def normalize_title(self, title: str) -> str:
        """标准化标题，用于匹配"""
        # 转换为小写，移除特殊字符和多余空格
        normalized = title.lower()
        normalized = re.sub(r'[^a-zA-Z0-9\s]', '', normalized)  # 移除标点符号
        normalized = re.sub(r'\s+', ' ', normalized).strip()  # 标准化空格
        return normalized
    
    def create_paper_title_mapping(self) -> Dict[str, str]:
        """创建论文标题映射关系"""
        print("正在创建论文标题映射关系...")
        
        # 从图片数据中提取论文标题
        figure_paper_titles = set()
        for figure in self.figures_data:
            source_md = figure.get("source_md", "")
            if source_md:
                # 从MD文件名中提取论文标题（移除.md后缀）
                paper_title = source_md.replace('.md', '')
                figure_paper_titles.add(paper_title)
        
        # 从论文文本中提取论文标题
        text_paper_titles = set()
        for paper in self.paper_texts:
            text_paper_titles.add(paper["paper_title"])
        
        # 合并所有标题并去重
        all_titles = list(figure_paper_titles.union(text_paper_titles))
        
        # 去重处理：合并包含关系的标题
        unique_titles = self._deduplicate_titles(all_titles)
        
        # 创建paperid映射
        paper_id_mapping = {}
        for i, title in enumerate(unique_titles):
            paper_id = f"paper_{i+1:03d}"
            paper_id_mapping[title] = paper_id
        
        self.mapping_data["paper_title_mapping"] = paper_id_mapping
        
        print(f"创建了 {len(paper_id_mapping)} 个论文标题映射（去重后）")
        return paper_id_mapping
    
    def _deduplicate_titles(self, titles: List[str]) -> List[str]:
        """去重处理：合并包含关系的标题"""
        # 按长度排序，长的在前
        sorted_titles = sorted(titles, key=len, reverse=True)
        unique_titles = []
        
        # 特殊处理：paper_005和paper_035的对应关系
        special_mappings = {
            "Striking impacts of biomass burning on  PM": "Striking impacts of biomass burning on  $\\mathrm{PM}_{2.5}$  concentrations in Northeast China through the emission inventory improvement"
        }
        
        for title in sorted_titles:
            # 检查特殊映射关系
            if title in special_mappings:
                target_title = special_mappings[title]
                if target_title in unique_titles:
                    print(f"特殊映射: '{title}' -> '{target_title}'")
                    continue
                elif target_title in sorted_titles:
                    print(f"特殊映射: 将 '{title}' 替换为 '{target_title}'")
                    title = target_title
            
            # 检查当前标题是否已经被更长的标题包含
            is_contained = False
            for existing_title in unique_titles:
                normalized_title = self.normalize_title(title)
                normalized_existing = self.normalize_title(existing_title)
                
                # 如果当前标题是现有标题的子串，则跳过
                if normalized_title in normalized_existing:
                    print(f"合并重复标题: '{title}' -> '{existing_title}'")
                    is_contained = True
                    break
                # 如果现有标题是当前标题的子串，则替换
                elif normalized_existing in normalized_title:
                    print(f"替换为完整标题: '{existing_title}' -> '{title}'")
                    unique_titles.remove(existing_title)
                    unique_titles.append(title)
                    is_contained = True
                    break
            
            if not is_contained:
                unique_titles.append(title)
        
        return unique_titles
    
    def find_paper_id_by_title(self, title: str, paper_id_mapping: Dict) -> Optional[str]:
        """根据标题查找paperid"""
        normalized_title = self.normalize_title(title)
        
        # 直接匹配
        for paper_title, paper_id in paper_id_mapping.items():
            if self.normalize_title(paper_title) == normalized_title:
                return paper_id
        
        # 模糊匹配（包含关系）- 优先匹配更长的标题
        # 按标题长度排序，长的在前
        sorted_titles = sorted(paper_id_mapping.keys(), key=len, reverse=True)
        
        for paper_title in sorted_titles:
            normalized_paper_title = self.normalize_title(paper_title)
            
            # 如果当前标题是论文标题的子串，或者论文标题是当前标题的子串
            if normalized_title in normalized_paper_title or \
               normalized_paper_title in normalized_title:
                return paper_id_mapping[paper_title]
        
        return None
    
    def create_text_chunks(self, paper_record: Dict, paper_id: str) -> List[Dict]:
        """将论文文本分割为chunk"""
        chunks = []
        content = paper_record["content"]
        
        # 简单的段落分割（按空行分割）
        paragraphs = re.split(r'\n\s*\n', content)
        
        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if len(paragraph) < 50:  # 跳过过短的段落
                continue
            
            self.chunk_id_counter += 1
            chunk_id = f"chunk_{self.chunk_id_counter:06d}"
            
            chunk_data = {
                "chunkid": chunk_id,
                "paperid": paper_id,
                "type": "texture",
                "content": paragraph,
                "metadata": {
                    "paper_title": paper_record["paper_title"],
                    "md_filename": paper_record["md_filename"],
                    "paragraph_index": i,
                    "content_length": len(paragraph),
                    "chunk_type": "text"
                }
            }
            
            chunks.append(chunk_data)
        
        return chunks
    
    def create_figure_chunks(self, figure_data: Dict, paper_id: str) -> List[Dict]:
        """创建图片数据chunk"""
        chunks = []
        
        # 拼接concise_summary和inferred_insight作为图片的文本表示
        text_representation = f"{figure_data.get('concise_summary', '')} {figure_data.get('inferred_insight', '')}"
        
        self.chunk_id_counter += 1
        chunk_id = f"chunk_{self.chunk_id_counter:06d}"
        
        chunk_data = {
            "chunkid": chunk_id,
            "paperid": paper_id,
            "type": "picture",
            "content": text_representation,
            "metadata": {
                "paper_title": figure_data.get("source_md", "").replace('.md', ''),
                "figure_id": figure_data.get("id", ""),
                "figure_title": figure_data.get("title", ""),
                "save_path": figure_data.get("save_path", ""),
                "functional_roles": figure_data.get("functional_roles", {}),
                "visual_type": figure_data.get("visual_type", {}),
                "key_entities": figure_data.get("key_entities", []),
                "concise_summary": figure_data.get("concise_summary", ""),
                "inferred_insight": figure_data.get("inferred_insight", ""),
                "references": figure_data.get("references", []),
                "chunk_type": "figure"
            }
        }
        
        chunks.append(chunk_data)
        return chunks
    
    def build_enhanced_rag_data(self) -> List[Dict]:
        """构建增强版RAG数据"""
        print("正在构建增强版RAG数据...")
        
        # 创建论文标题映射
        paper_id_mapping = self.create_paper_title_mapping()
        
        self.enhanced_rag_data = []
        
        # 处理论文文本数据
        print("处理论文文本数据...")
        for paper_record in self.paper_texts:
            paper_title = paper_record["paper_title"]
            paper_id = paper_id_mapping.get(paper_title)
            
            if paper_id:
                text_chunks = self.create_text_chunks(paper_record, paper_id)
                self.enhanced_rag_data.extend(text_chunks)
        
        # 处理图片数据
        print("处理图片数据...")
        for figure_data in self.figures_data:
            source_md = figure_data.get("source_md", "")
            paper_title = source_md.replace('.md', '') if source_md else ""
            
            if paper_title:
                paper_id = self.find_paper_id_by_title(paper_title, paper_id_mapping)
                if paper_id:
                    figure_chunks = self.create_figure_chunks(figure_data, paper_id)
                    self.enhanced_rag_data.extend(figure_chunks)
        
        print(f"构建完成，共生成 {len(self.enhanced_rag_data)} 个数据chunk")
        return self.enhanced_rag_data
    
    def generate_mapping_file(self) -> Dict:
        """生成映射关系文件"""
        print("正在生成映射关系文件...")
        
        mapping_data = {
            "paper_title_to_md": {},
            "paper_title_to_paperid": {},
            "paper_content_summary": {}
        }
        
        # 获取paperid映射
        paper_id_mapping = self.mapping_data.get("paper_title_mapping", {})
        
        # 论文标题与MD文件映射
        for paper_record in self.paper_texts:
            paper_title = paper_record["paper_title"]
            paper_id = paper_id_mapping.get(paper_title)
            
            mapping_data["paper_title_to_md"][paper_title] = {
                "md_filename": paper_record["md_filename"],
                "md_filepath": paper_record["md_filepath"],
                "paperid": paper_id if paper_id else "unknown"
            }
        
        # 论文标题与paperid映射
        mapping_data["paper_title_to_paperid"] = self.mapping_data.get("paper_title_mapping", {})
        
        # 各论文包含的文本内容与图片id清单
        for paper_title, paper_id in mapping_data["paper_title_to_paperid"].items():
            paper_chunks = [chunk for chunk in self.enhanced_rag_data if chunk["paperid"] == paper_id]
            
            text_chunks = [chunk["chunkid"] for chunk in paper_chunks if chunk["type"] == "texture"]
            figure_chunks = [chunk["chunkid"] for chunk in paper_chunks if chunk["type"] == "picture"]
            
            mapping_data["paper_content_summary"][paper_title] = {
                "paperid": paper_id,
                "text_chunk_count": len(text_chunks),
                "figure_chunk_count": len(figure_chunks),
                "text_chunk_ids": text_chunks,
                "figure_chunk_ids": figure_chunks,
                "total_chunks": len(text_chunks) + len(figure_chunks)
            }
        
        return mapping_data
    
    def save_results(self):
        """保存处理结果"""
        print("正在保存处理结果...")
        
        # 保存增强版RAG数据
        rag_output_path = os.path.join(self.output_dir, "enhanced_rag_data.json")
        with open(rag_output_path, 'w', encoding='utf-8') as f:
            json.dump(self.enhanced_rag_data, f, ensure_ascii=False, indent=2)
        print(f"增强版RAG数据已保存到: {rag_output_path}")
        
        # 保存映射关系文件
        mapping_data = self.generate_mapping_file()
        mapping_output_path = os.path.join(self.output_dir, "enhanced_rag_mapping.json")
        with open(mapping_output_path, 'w', encoding='utf-8') as f:
            json.dump(mapping_data, f, ensure_ascii=False, indent=2)
        print(f"映射关系文件已保存到: {mapping_output_path}")
        
        # 保存统计信息
        stats = {
            "total_chunks": len(self.enhanced_rag_data),
            "text_chunks": len([chunk for chunk in self.enhanced_rag_data if chunk["type"] == "texture"]),
            "figure_chunks": len([chunk for chunk in self.enhanced_rag_data if chunk["type"] == "picture"]),
            "total_papers": len(mapping_data["paper_title_to_paperid"]),
            "processing_time": "2026-02-02"  # 可以添加实际时间戳
        }
        
        stats_output_path = os.path.join(self.output_dir, "processing_stats.json")
        with open(stats_output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"统计信息已保存到: {stats_output_path}")
    
    def run(self):
        """运行完整的处理流程"""
        print("开始构建增强版RAG知识库...")
        
        # 1. 加载数据
        self.load_figures_data()
        self.load_paper_texts()
        
        if not self.figures_data or not self.paper_texts:
            print("数据加载失败，无法继续处理")
            return
        
        # 2. 构建增强版RAG数据
        self.build_enhanced_rag_data()
        
        # 3. 保存结果
        self.save_results()
        
        print("增强版RAG知识库构建完成！")
        
        # 打印统计信息
        text_count = len([chunk for chunk in self.enhanced_rag_data if chunk["type"] == "texture"])
        figure_count = len([chunk for chunk in self.enhanced_rag_data if chunk["type"] == "picture"])
        
        print(f"\n=== 处理结果统计 ===")
        print(f"总数据chunk数: {len(self.enhanced_rag_data)}")
        print(f"文本chunk数: {text_count}")
        print(f"图片chunk数: {figure_count}")
        print(f"处理论文数: {len(self.mapping_data.get('paper_title_mapping', {}))}")
        print(f"输出目录: {self.output_dir}")


def main():
    """主函数"""
    # 创建增强版RAG知识库构建器
    builder = EnhancedRAGKnowledgeBase(
        figures_json_path="enhanced_figures_afterllm_reassigned_ids.json",
        paper_md_dir="paper_md",
        output_dir="enhanced_rag_output"
    )
    
    # 运行构建流程
    builder.run()


if __name__ == "__main__":
    main()