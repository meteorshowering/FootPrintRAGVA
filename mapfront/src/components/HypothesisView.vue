<template>
  <div class="hypothesis-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <button @click="goBack" class="btn btn-back">
        ← 返回详情
      </button>
      <h2 class="title">核心科学假设 (Core Hypothesis)</h2>
    </div>

    <!-- Hypothesis 内容 -->
    <div v-if="hypothesisData" class="hypothesis-content">
      <!-- Final Report 部分 -->
      <section v-if="hypothesisData.final_report" class="hypothesis-section">
        <h3>最终报告 (Final Report)</h3>
        <div class="section-content" v-html="formatHypothesisText(hypothesisData.final_report)"></div>
      </section>

      <!-- Outline 部分 -->
      <section v-if="hypothesisData.outline && hypothesisData.outline.response" class="hypothesis-section">
        <h3>大纲 (Outline)</h3>
        <div class="section-content" v-html="formatHypothesisText(hypothesisData.outline.response)"></div>
        <div v-if="hypothesisData.outline.timestamp" class="timestamp">
          生成时间: {{ hypothesisData.outline.timestamp }}
        </div>
      </section>

      <!-- Sections 部分 -->
      <section v-if="hypothesisData.sections && hypothesisData.sections.length > 0" class="hypothesis-section">
        <h3>子主题 (Sections)</h3>
        <div v-for="(section, index) in hypothesisData.sections" :key="index" class="section-item">
          <h4>子主题 {{ index + 1 }}</h4>
          <div class="section-content" v-html="formatHypothesisText(section.response)"></div>
          <div v-if="section.timestamp" class="timestamp">
            生成时间: {{ section.timestamp }}
          </div>
        </div>
      </section>

      <!-- Synthesis 部分 -->
      <section v-if="hypothesisData.synthesis && hypothesisData.synthesis.response" class="hypothesis-section">
        <h3>整合 (Synthesis)</h3>
        <div class="section-content" v-html="formatHypothesisText(hypothesisData.synthesis.response)"></div>
        <div v-if="hypothesisData.synthesis.timestamp" class="timestamp">
          生成时间: {{ hypothesisData.synthesis.timestamp }}
        </div>
      </section>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <p>暂无 Hypothesis 数据</p>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef, no-unused-vars */
import { onMounted } from 'vue';
import { marked } from 'marked';
import katex from 'katex';
import 'katex/dist/katex.min.css';

const props = defineProps({
  hypothesisData: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['go-back', 'navigate-to-chunk']);

const goBack = () => {
  emit('go-back');
};

// 格式化Hypothesis文本，处理Markdown和Evidence链接
const formatHypothesisText = (text) => {
  if (!text) return '';
  
  // 先处理Evidence链接格式：
  // 1) [Evidence: chunk_000538, chunk_004609]
  // 2) 【Evidence: chunk_000538, chunk_004609】
  // 兼容英文/全角括号，及英文/中文逗号分隔
  const evidenceRegex = /(?:\[|【|［)\s*Evidence:\s*([^\]】］]+?)\s*(?:\]|】|］)/g;
  let processedText = text.replace(evidenceRegex, (match, chunks) => {
    // 提取所有chunk ID
    const chunkIds = String(chunks)
      .split(/,|\uFF0C/g) // 英文逗号 or 中文全角逗号
      .map(id => id.trim())
      .filter(id => id);
    
    // 为每个chunk ID创建链接（不使用Vue指令，使用data属性）
    const chunkLinks = chunkIds.map(chunkId => {
      return `<a href="#" class="evidence-link" data-chunk-id="${chunkId}">${chunkId}</a>`;
    }).join(', ');
    
    return `<span class="evidence-group">[Evidence: ${chunkLinks}]</span>`;
  });
  
  // 使用marked渲染Markdown
  let html = marked(processedText, {
    breaks: true,
    gfm: true
  });
  
  // 处理KaTeX数学公式（如果存在）
  // 行内公式：$...$
  html = html.replace(/\$([^$]+)\$/g, (match, formula) => {
    try {
      return katex.renderToString(formula, { throwOnError: false });
    } catch (e) {
      return match;
    }
  });
  
  // 块级公式：$$...$$
  html = html.replace(/\$\$([^$]+)\$\$/g, (match, formula) => {
    try {
      return katex.renderToString(formula, { displayMode: true, throwOnError: false });
    } catch (e) {
      return match;
    }
  });
  
  return html;
};

// 处理Evidence链接点击事件（需要在mounted后绑定）
onMounted(() => {
  // 使用事件委托处理动态生成的链接点击
  const container = document.querySelector('.hypothesis-content');
  if (container) {
    container.addEventListener('click', (e) => {
      const link = e.target.closest('.evidence-link');
      if (link) {
        e.preventDefault();
        const chunkId = link.getAttribute('data-chunk-id');
        if (chunkId) {
          emit('navigate-to-chunk', chunkId);
        }
      }
    });
  }
});
</script>

<style scoped>
.hypothesis-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.toolbar {
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  gap: 15px;
  flex-shrink: 0;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-back {
  background: #6c757d;
  color: white;
}

.btn-back:hover {
  background: #5a6268;
}

.title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.hypothesis-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.hypothesis-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.hypothesis-section h3 {
  margin: 0 0 15px 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #4A90E2;
  padding-bottom: 10px;
}

.hypothesis-section h4 {
  margin: 15px 0 10px 0;
  font-size: 16px;
  font-weight: 600;
  color: #555;
}

.section-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e9ecef;
}

.section-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-content {
  color: #333;
  line-height: 1.8;
  font-size: 15px;
}

.section-content :deep(p) {
  margin: 10px 0;
}

.section-content :deep(h1),
.section-content :deep(h2),
.section-content :deep(h3),
.section-content :deep(h4),
.section-content :deep(h5),
.section-content :deep(h6) {
  margin-top: 20px;
  margin-bottom: 10px;
  font-weight: 600;
}

.section-content :deep(ul),
.section-content :deep(ol) {
  margin: 10px 0;
  padding-left: 30px;
}

.section-content :deep(li) {
  margin: 5px 0;
}

.section-content :deep(code) {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.section-content :deep(pre) {
  background: #f4f4f4;
  padding: 15px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 15px 0;
}

.section-content :deep(pre code) {
  background: none;
  padding: 0;
}

.section-content :deep(blockquote) {
  border-left: 4px solid #4A90E2;
  padding-left: 15px;
  margin: 15px 0;
  color: #666;
  font-style: italic;
}

.section-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
}

.section-content :deep(th),
.section-content :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.section-content :deep(th) {
  background: #f8f9fa;
  font-weight: 600;
}

/* Evidence链接样式 */
.evidence-group {
  display: inline-block;
  margin: 0 2px;
}

.evidence-link {
  color: #4A90E2;
  text-decoration: none;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  background: #e3f2fd;
  transition: all 0.2s;
  cursor: pointer;
}

.evidence-link:hover {
  background: #bbdefb;
  color: #1976d2;
  text-decoration: underline;
}

.timestamp {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e9ecef;
  font-size: 12px;
  color: #999;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 16px;
}
</style>
