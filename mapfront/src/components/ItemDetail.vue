<template>
  <div class="item-detail">
    <!-- 图片类型：显示图片 + 图标题在下方 -->
    <div v-if="isPictureType()" class="image-section">
      <img :src="getImageUrl()" alt="Figure" class="detail-image" />
      <div v-if="getFigureTitle()" class="figure-caption">{{ getFigureTitle() }}</div>
    </div>
    
    <!-- 文本类型：显示文本内容 -->
    <div v-if="shouldShowText()" class="text-section">
      <div class="info-item">
        <h4>Text content</h4>
        <div class="markdown-content" v-html="getRenderedMarkdown()"></div>
      </div>
    </div>
    
    <div class="info-section">
      <!-- Key Entities (如果有) -->
      <div v-if="getKeyEntities().length > 0" class="info-item">
        <h4>Key Entities</h4>
        <ul class="entities-list">
          <li v-for="(entity, idx) in getKeyEntities()" :key="idx">{{ entity }}</li>
        </ul>
      </div>
      
      <!-- Concise Summary (如果有) -->
      <div v-if="getConciseSummary()" class="info-item">
        <h4>Concise Summary</h4>
        <p class="summary-text">{{ getConciseSummary() }}</p>
      </div>
      
      <!-- Inferred Insight (如果有) -->
      <div v-if="getInferredInsight()" class="info-item">
        <h4>Inferred Insight</h4>
        <p class="insight-text">{{ getInferredInsight() }}</p>
      </div>
      
      <!-- Paper信息 (如果有) -->
      <div v-if="getPaperInfo()" class="info-item">
        <h4>Paper</h4>
        <p class="paper-info">{{ getPaperInfo() }}</p>
      </div>
      
      <!-- Evaluation: only when extracted_insight is present -->
      <div v-if="shouldShowEvaluationSection()" class="info-item evaluation-section">
        <h4>Evaluation</h4>
        
        <!-- Branch Action -->
        <div v-if="getBranchAction()" class="evaluation-field">
          <span class="field-label">Branch action:</span>
          <span class="branch-action" :class="getBranchActionClass()">{{ getBranchAction() }}</span>
        </div>
        
        <!-- Extracted Insight -->
        <div v-if="getExtractedInsight()" class="evaluation-field">
          <span class="field-label">Extracted insight:</span>
          <p class="evaluation-text">{{ getExtractedInsight() }}</p>
        </div>
        
        <!-- Scores -->
        <div v-if="getEvaluationScores()" class="evaluation-field">
          <span class="field-label">Scores:</span>
          <div class="scores-container">
            <span class="score-item">
              <span class="score-label">Relevance:</span>
              <span class="score-value">{{ getEvaluationScores().relevance || 'N/A' }}</span>
            </span>
            <span class="score-item">
              <span class="score-label">Credibility:</span>
              <span class="score-value">{{ getEvaluationScores().credibility || 'N/A' }}</span>
            </span>
          </div>
        </div>
        
        <!-- Reason -->
        <div v-if="getEvaluationReason()" class="evaluation-field">
          <span class="field-label">Reason:</span>
          <p class="evaluation-text">{{ getEvaluationReason() }}</p>
        </div>
        
        <!-- Suggested Keywords -->
        <div v-if="getSuggestedKeywords() && getSuggestedKeywords().length > 0" class="evaluation-field">
          <span class="field-label">Suggested keywords:</span>
          <div class="keywords-list">
            <span v-for="(keyword, idx) in getSuggestedKeywords()" :key="idx" class="keyword-tag">
              {{ keyword }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { marked } from 'marked';
import katex from 'katex';
import 'katex/dist/katex.min.css';

const props = defineProps({
  item: {
    type: Object,
    required: true
  }
});

// 调试：打印 item 数据
console.log('ItemDetail - props.item:', props.item);
console.log('ItemDetail - original_data:', props.item.original_data);
console.log('ItemDetail - evaluation:', props.item.original_data?.evaluation);
      
// 解析metadata（可能是JSON字符串）
const parseMetadata = (metadata) => {
  if (!metadata) return null;
  if (typeof metadata === 'string') {
    try {
      return JSON.parse(metadata);
    } catch (e) {
      console.warn('Failed to parse metadata:', e);
      return null;
    }
  }
  return metadata;
};

// 获取数据类型
const getDataType = () => {
  let type = props.item.type || props.item.original_data?.metadata?.type || null;
  
  if (!type && props.item.original_data?.metadata) {
    let meta = props.item.original_data.metadata;
    if (typeof meta === 'string') {
      try { meta = JSON.parse(meta); } catch(e) { /* ignore */ }
    }
    
    if (meta.type) {
      type = meta.type;
    } else if (meta.full_json || meta.savepath || meta.save_path) {
      type = 'picture';
    } else if (meta.metadata && typeof meta.metadata === 'string') {
      try {
        const inner = JSON.parse(meta.metadata);
        if (inner.type) type = inner.type;
        else if (inner.full_json || inner.savepath || inner.save_path) type = 'picture';
      } catch(e) { /* ignore */ }
    }
  }
  
  if (type === 'text') type = 'texture';
  if (type === 'figure' || type === 'image') type = 'picture';
  
  // 兜底基于ID判断
  if (!type && props.item.id) {
    const idStr = String(props.item.id);
    if (idStr.includes('Figure') || idStr.includes('image') || idStr.includes('fig')) {
      type = 'picture';
    }
  }
  
  return type || 'unknown';
};

// 判断是否为图片类型
const isPictureType = () => {
  return getDataType() === 'picture';
};

// 判断是否为文本类型
const isTextureType = () => {
  return getDataType() === 'texture';
};

const shouldShowText = () => {
  // type 可能不稳定时，只要 text_content 有值也应该显示文本
  if (isTextureType()) return true;
  if (isPictureType()) return false;
  return !!getTextContent();
};

// 获取图片URL
const getImageUrl = () => {
  if (!isPictureType()) return '';
  
  // 统一解析函数
  const resolvePath = (pathStr) => {
    if (!pathStr) return '';
    const normalizedPath = pathStr.replace(/\\/g, '/');
    const mdLlmvisIndex = normalizedPath.indexOf('md-llmvis');
    const paperMdIndex = normalizedPath.indexOf('paper_md');
    
    if (mdLlmvisIndex !== -1) {
      const subPath = normalizedPath.substring(mdLlmvisIndex + 'md-llmvis'.length + 1);
      if (subPath.startsWith('images/')) {
        return `/static-llmvis/${subPath.substring('images/'.length)}`;
      } else {
        return `/static-llmvis/${subPath}`;
      }
    } else if (paperMdIndex !== -1) {
      const relativePath = normalizedPath.substring(paperMdIndex + 'paper_md'.length + 1);
      return `/static/${relativePath}`;
    }
    return '';
  };

  // 首先尝试从 original_data 中解析原始绝对路径（因为 relative_path 可能是错误的完整路径）
  const originalData = props.item.original_data;
  if (originalData) {
    const metadata = parseMetadata(originalData.metadata?.metadata) || parseMetadata(originalData.metadata?.full_json) || originalData.metadata;
    if (metadata) {
      const savePath = metadata.save_path || metadata.savepath || '';
      const resolved = resolvePath(savePath);
      if (resolved) return resolved;
    }
  }

  // 兜底：如果 relative_path 已经被正确处理成 '/static' 开头
  if (props.item.relative_path) {
    if (props.item.relative_path.startsWith('/static')) {
      return props.item.relative_path;
    }
    // 如果 relative_path 看起来像绝对路径或包含 md-llmvis，再尝试解析一次
    const resolvedRel = resolvePath(props.item.relative_path);
    if (resolvedRel) return resolvedRel;
    
    return `/static/${props.item.relative_path}`;
  }
  
  return '';
};

// 获取文本内容（原始 Markdown）；与 store / processRagResultForDetail 多源兜底一致
const getTextContent = () => {
  const od = props.item.original_data;
  let parsed = props.item.parsed_metadata;
  if (!parsed && od?.metadata?.metadata) {
    parsed = parseMetadata(od.metadata.metadata);
  }
  return (
    props.item.text_content ||
    (typeof od?.content === 'string' ? od.content : od?.content?.text) ||
    (typeof od?.metadata?.content === 'string' ? od.metadata.content : '') ||
    (typeof parsed?.content === 'string' ? parsed.content : '') ||
    ''
  );
};

// 配置 marked 以支持数学公式
marked.setOptions({
  breaks: true, // 支持 GitHub 风格的换行
  gfm: true,    // 启用 GitHub 风格的 Markdown
});

// 自定义渲染器以支持数学公式
const renderer = new marked.Renderer();

// 处理行内数学公式 $...$
const originalParagraph = renderer.paragraph;
renderer.paragraph = (text) => {
  // 匹配行内公式 $...$ 或 \(...\)
  const inlineMathRegex = /\$([^$\n]+)\$|\\\(([^)]+)\\\)/g;
  text = text.replace(inlineMathRegex, (match, dollarContent, parenContent) => {
    const mathContent = dollarContent || parenContent;
    try {
      return katex.renderToString(mathContent, { throwOnError: false, displayMode: false });
    } catch (e) {
      return match; // 如果渲染失败，返回原始文本
    }
  });
  return originalParagraph(text);
};

// 处理块级数学公式 $$...$$ 或 \[...\]
const originalCode = renderer.code;
renderer.code = (code, language) => {
  // 如果代码块语言是 math 或 latex，渲染为数学公式
  if (language === 'math' || language === 'latex') {
    try {
      return `<div class="math-block">${katex.renderToString(code, { throwOnError: false, displayMode: true })}</div>`;
    } catch (e) {
      return `<pre><code>${code}</code></pre>`;
    }
  }
  return originalCode(code, language);
};

// 处理段落中的块级公式
const originalList = renderer.list;
renderer.list = (body, ordered, start) => {
  // 在列表项中处理数学公式
  const blockMathRegex = /\$\$([^$]+)\$\$|\\\[([^\]]+)\\\]/g;
  body = body.replace(blockMathRegex, (match, dollarContent, bracketContent) => {
    const mathContent = dollarContent || bracketContent;
    try {
      return `<div class="math-block">${katex.renderToString(mathContent, { throwOnError: false, displayMode: true })}</div>`;
    } catch (e) {
      return match;
    }
  });
  return originalList(body, ordered, start);
};

marked.setOptions({ renderer });

// 渲染 Markdown 为 HTML（包括数学公式）
const getRenderedMarkdown = () => {
  const text = getTextContent();
  if (!text) return '';
  
  try {
    // 先处理块级公式 $$...$$ 或 \[...\]
    let processedText = text.replace(/\$\$([^$]+)\$\$/g, (match, content) => {
      try {
        return `<div class="math-block">${katex.renderToString(content.trim(), { throwOnError: false, displayMode: true })}</div>`;
      } catch (e) {
        return match;
      }
    });
    
    processedText = processedText.replace(/\\\[([^\]]+)\\\]/g, (match, content) => {
      try {
        return `<div class="math-block">${katex.renderToString(content.trim(), { throwOnError: false, displayMode: true })}</div>`;
      } catch (e) {
        return match;
      }
    });
    
    // 使用 marked 渲染 Markdown
    const html = marked(processedText);
    
    // 处理行内公式（在 marked 渲染后）
    const inlineMathRegex = /\$([^$\n]+)\$/g;
    const finalHtml = html.replace(inlineMathRegex, (match, content) => {
      // 跳过已经被渲染的块级公式
      if (match.includes('math-block')) return match;
      try {
        return katex.renderToString(content.trim(), { throwOnError: false, displayMode: false });
      } catch (e) {
        return match;
      }
    });
    
    return finalHtml;
  } catch (error) {
    console.error('Error rendering markdown:', error);
    // 如果渲染失败，返回转义的原始文本
    return `<pre>${text}</pre>`;
  }
};

// 获取解析后的 metadata（优先使用已解析的，避免重复解析）
const getParsedMetadata = () => {
  // 优先使用 store 中已经解析好的 parsed_metadata
  if (props.item.parsed_metadata) {
    return props.item.parsed_metadata;
  }
  
  // 如果没有，从 original_data 解析
  const originalData = props.item.original_data;
  if (originalData?.metadata) {
    return parseMetadata(originalData.metadata.metadata);
  }
  
  return null;
};

// 获取Key Entities
const getKeyEntities = () => {
  if (props.item.key_entities && Array.isArray(props.item.key_entities)) {
    return props.item.key_entities;
  }
  
  const metadata = getParsedMetadata();
  if (metadata?.key_entities && Array.isArray(metadata.key_entities)) {
    return metadata.key_entities;
  }
  
  return [];
};

// 获取Concise Summary
const getConciseSummary = () => {
  if (props.item.concise_summary) return props.item.concise_summary;
  
  const metadata = getParsedMetadata();
  if (metadata?.concise_summary) return metadata.concise_summary;
  
  return '';
};

// 获取Inferred Insight
const getInferredInsight = () => {
  if (props.item.inferred_insight) return props.item.inferred_insight;
  
  const metadata = getParsedMetadata();
  if (metadata?.inferred_insight) return metadata.inferred_insight;
  
  return '';
};

// 获取论文标题（用于顶部显示）
const getPaperTitle = () => {
  if (props.item.paper_title) return props.item.paper_title;
  
  const metadata = getParsedMetadata();
  if (metadata?.paper_title) return metadata.paper_title;
  
  return '';
};

// 获取图片的图标题（figure_title，放在图片下方）
const getFigureTitle = () => {
  const metadata = getParsedMetadata();
  return metadata?.figure_title || null;
};

// 获取论文信息
const getPaperInfo = () => {
  return getPaperTitle() || '';
};

// 获取其他 metadata 字段（如 functional_roles, visual_type, references 等）
// const getMetadataField = (fieldName) => {
//   const metadata = getParsedMetadata();
//   return metadata?.[fieldName] || null;
// };

// 获取 evaluation 对象
const getEvaluation = () => {
  const originalData = props.item.original_data;
  return originalData?.evaluation || null;
};

// 获取分支动作
const getBranchAction = () => {
  if (props.item.branch_action && props.item.branch_action !== 'UNKNOWN') {
    return props.item.branch_action;
  }
  const evaluation = getEvaluation();
  if (evaluation?.branch_action) {
    return evaluation.branch_action;
  }
  return null;
};

// 获取提取的洞察
const getExtractedInsight = () => {
  const evaluation = getEvaluation();
  return evaluation?.extracted_insight || null;
};

// 跳过评估占位（与后端占位文案一致则不展示整块 Evaluation）
const isSkippedEvaluationPlaceholder = (insight) => {
  const t = String(insight ?? '').trim();
  if (!t) return true;
  return /^\(?evaluation\s+skipped\)?$/i.test(t);
};

// 仅当存在有意义的 evaluation.extracted_insight 时显示整块 Evaluation
const shouldShowEvaluationSection = () => {
  const insight = getExtractedInsight();
  if (insight == null || insight === undefined) return false;
  return !isSkippedEvaluationPlaceholder(insight);
};

// 获取评估分数
const getEvaluationScores = () => {
  const evaluation = getEvaluation();
  return evaluation?.scores || null;
};

// 获取评估原因
const getEvaluationReason = () => {
  const evaluation = getEvaluation();
  return evaluation?.reason || null;
};

// 获取建议关键词
const getSuggestedKeywords = () => {
  const evaluation = getEvaluation();
  return evaluation?.suggested_keywords || [];
};

// 获取分支动作样式类
const getBranchActionClass = () => {
  const action = getBranchAction();
  if (!action) return 'action-unknown';
  if (action === 'GROW') return 'action-grow';
  if (action === 'PRUNE') return 'action-prune';
  if (action === 'KEEP') return 'action-keep';
  return 'action-unknown';
};
</script>

<style scoped>

.item-detail {
  font-size: 13px;
}

.image-section {
  margin-bottom: 10px;
}

.detail-image {
  width: 100%;
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.figure-caption {
  margin-top: 6px;
  font-size: 12px;
  color: #666;
  line-height: 1.35;
}

.text-section {
  margin-bottom: 10px;
}

.markdown-content {
  line-height: 1.5;
  color: #333;
  margin: 0;
  font-size: 13px;
  background: #f8f9fa;
  padding: 10px;
  border-radius: 6px;
  border-left: 3px solid #6c757d;
}

.markdown-content :deep(p) {
  margin: 0.35em 0;
}

.markdown-content :deep(p:first-child) {
  margin-top: 0;
}

.markdown-content :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  margin-top: 0.6em;
  margin-bottom: 0.35em;
  font-weight: 600;
  color: #495057;
}

.markdown-content :deep(h1) { font-size: 1.5em; }
.markdown-content :deep(h2) { font-size: 1.3em; }
.markdown-content :deep(h3) { font-size: 1.1em; }

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0.35em 0;
  padding-left: 1.5em;
}

.markdown-content :deep(li) {
  margin: 0.2em 0;
}

.markdown-content :deep(code) {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 10px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 0.35em 0;
}

.markdown-content :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #6c757d;
  padding-left: 1em;
  margin: 0.35em 0;
  color: #666;
  font-style: italic;
}

.markdown-content :deep(a) {
  color: #4A90E2;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

.markdown-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.35em 0;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #dee2e6;
  padding: 5px 10px;
  text-align: left;
}

.markdown-content :deep(th) {
  background: #e9ecef;
  font-weight: 600;
}

/* 数学公式样式 */
.markdown-content :deep(.math-block) {
  margin: 0.6em 0;
  text-align: center;
  overflow-x: auto;
}

.markdown-content :deep(.katex) {
  font-size: 1.1em;
}

.markdown-content :deep(.katex-display) {
  margin: 0.6em 0;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 6px;
}

.info-item h4 {
  font-size: 13px;
  color: #495057;
  margin: 0 0 6px 0;
  font-weight: 600;
}

.entities-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.entities-list li {
  padding: 3px 9px;
  background: white;
  border-radius: 12px;
  border-left: 2px solid #4A90E2;
  font-size: 12px;
}

.summary-text,
.insight-text {
  line-height: 1.5;
  color: #555;
  margin: 0;
  font-size: 12px;
}

.paper-info {
  line-height: 1.5;
  color: #555;
  margin: 0;
  font-size: 12px;
  font-style: italic;
}

.branch-action {
  display: inline-block;
  padding: 3px 9px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.action-grow {
  background-color: #d4edda;
  color: #155724;
}

.action-prune {
  background-color: #f8d7da;
  color: #721c24;
}

.action-keep {
  background-color: #fff3cd;
  color: #856404;
}

.action-unknown {
  background-color: #e2e3e5;
  color: #383d41;
}

.functional-roles,
.visual-types {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  align-items: center;
}

.role-tag,
.type-tag {
  display: inline-block;
  padding: 3px 9px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.role-tag.main-role,
.type-tag.main-type {
  background-color: #4A90E2;
  color: white;
  font-weight: 600;
}

.role-tag.sub-role,
.type-tag.sub-type {
  background-color: #e3f2fd;
  color: #1976d2;
  border: 1px solid #90caf9;
}

.references-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.reference-item {
  padding: 7px 10px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #6c757d;
  font-size: 11px;
  line-height: 1.5;
  color: #555;
}

.evaluation-section {
  background: #f0f7ff;
  border-left: 4px solid #4A90E2;
}

.evaluation-field {
  margin-bottom: 8px;
}

.evaluation-field:last-child {
  margin-bottom: 0;
}

.field-label {
  font-weight: 600;
  color: #495057;
  font-size: 12px;
  display: block;
  margin-bottom: 3px;
}

.evaluation-text {
  margin: 0;
  padding: 7px 10px;
  background: white;
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.5;
  color: #555;
}

.scores-container {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  background: white;
  border-radius: 6px;
  font-size: 12px;
}

.score-label {
  color: #666;
  font-weight: 500;
}

.score-value {
  color: #4A90E2;
  font-weight: 600;
  font-size: 13px;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 3px;
}

.keyword-tag {
  display: inline-block;
  padding: 3px 9px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 12px;
  font-size: 11px;
  color: #495057;
  transition: all 0.2s;
}

.keyword-tag:hover {
  background: #e9ecef;
  border-color: #4A90E2;
}
</style>