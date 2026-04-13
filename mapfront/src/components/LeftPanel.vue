<template>
  <div class="panel">
    <section class="block">
      <div class="block-title">Control Panel</div>
      <details class="prompt-details" :open="openPlanPrompt">
        <summary class="prompt-summary" @click.prevent="openPlanPrompt = !openPlanPrompt">
          Plan Agent Prompt
        </summary>
        <div class="prompt-body">
          <div v-if="editingPlanPrompt" class="prompt-edit-wrap">
            <textarea
              v-model="planPromptDraft"
              class="prompt-textarea"
              rows="10"
            ></textarea>
            <div class="prompt-edit-actions">
              <button class="btn prompt-btn secondary" @click.stop="confirmEditPlanPrompt">
                确认
              </button>
            </div>
          </div>

          <div v-else>
            <div class="prompt-view-wrap">
              <div class="prompt-md" v-html="renderMarkdown(planPrompt || '（未加载）')"></div>
              <div class="prompt-view-actions">
                <button class="btn prompt-btn" @click.stop="startEditPlanPrompt">
                  编辑
                </button>
              </div>
            </div>
          </div>
        </div>
      </details>

      <details class="prompt-details" :open="openEvalPrompt" style="margin-top:8px;">
        <summary class="prompt-summary" @click.prevent="openEvalPrompt = !openEvalPrompt">
          Evaluate Agent Prompt
        </summary>
        <div class="prompt-body">
          <div v-if="editingEvaluatePrompt" class="prompt-edit-wrap">
            <textarea
              v-model="evaluatePromptDraft"
              class="prompt-textarea"
              rows="10"
            ></textarea>
            <div class="prompt-edit-actions">
              <button class="btn prompt-btn secondary" @click.stop="confirmEditEvaluatePrompt">
                确认
              </button>
            </div>
          </div>

          <div v-else>
            <div class="prompt-view-wrap">
              <div class="prompt-md" v-html="renderMarkdown(evaluatePrompt || '（未加载）')"></div>
              <div class="prompt-view-actions">
                <button class="btn prompt-btn" @click.stop="startEditEvaluatePrompt">
                  编辑
                </button>
              </div>
            </div>
          </div>
        </div>
      </details>
    </section>

    <section class="block">
      <div class="block-title">Add PDFs to Dataset</div>
      <input 
        type="file" 
        multiple 
        accept=".pdf"
        @change="handleFileUpload"
      />
      <div v-if="uploadedFiles.length > 0" class="file-list">
        <div v-for="(file, index) in uploadedFiles" :key="index" class="file-item">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-status">{{ file.status }}</span>
        </div>
      </div>
    </section>

    <section class="block">
      <div class="block-title">River Controls</div>
      <div class="row">
        <button class="btn small" @click="$emit('river-load-all')">加载所有轮次</button>
        <button class="btn small secondary" @click="$emit('river-clear')">清除图表</button>
      </div>
      <div class="row row-top">
        <button class="btn small" @click="$emit('river-toggle-prune')">隐藏/显示无用证据</button>
        <button class="btn small" @click="$emit('river-toggle-connections')">显示/隐藏连线</button>
      </div>
      <div class="row row-top">
        <select class="select" v-model="selectedExperimentFile" @change="$emit('river-select-file', selectedExperimentFile)">
          <option v-for="f in experimentFiles" :key="f" :value="f">
            {{ formatExperimentLabel(f) }}
          </option>
        </select>
      </div>
    </section>

    <section class="block block-compact">
      <div class="block-title">RAG Collection</div>
      <div class="row row-top">
        <select class="select" v-model="selectedRagCollection" @change="$emit('rag-collection-change', selectedRagCollection)">
          <option v-for="c in ragCollections" :key="c" :value="c">
            {{ c }}
          </option>
        </select>
      </div>
    </section>

    <section class="block block-compact">
      <div class="block-title">Run Settings</div>

      <div class="slider-row">
        <div class="slider-label">Max rounds</div>
        <input
          class="slider"
          type="range"
          min="1"
          max="10"
          step="1"
          v-model.number="searchPlanIteration"
          @input="handleMaxRoundsChange"
        />
        <div class="slider-value">{{ searchPlanIteration }}</div>
      </div>

      <div class="slider-row">
        <div class="slider-label">RAG / plan</div>
        <input
          class="slider"
          type="range"
          min="1"
          max="20"
          step="1"
          v-model.number="ragResultPerPlan"
          @input="handleRagResultPerPlanChange"
        />
        <div class="slider-value">{{ ragResultPerPlan }}</div>
      </div>

      <div class="slider-row">
        <div class="slider-label">Plans / round</div>
        <input
          class="slider"
          type="range"
          min="1"
          max="10"
          step="1"
          v-model.number="plansPerRound"
          @input="handlePlansPerRoundChange"
        />
        <div class="slider-value">{{ plansPerRound }}</div>
      </div>
    </section>

    <section class="block">
      <div class="block-title">Semantic Source Gallery</div>
      <div class="empty">（占位：后续放缩略图/列表）</div>
    </section>

    <section class="block">
      <div class="block-title">全局地图</div>
      <div class="global-map-controls-row">
        <button class="btn small secondary" @click="$emit('global-map-clear')">清除高亮</button>
        <button class="btn small" @click="$emit('global-map-reset')">↻ 重置</button>
      </div>
      <div id="left-global-map" class="global-map-embed"></div>
    </section>

    <section class="block">
      <div class="block-title">Chat with LLM</div>
      <div class="chatbox">
        <div class="chat-hint">You are chatting with an academic assistant.</div>
        <input 
          v-model="chatInput" 
          class="chat-input" 
          placeholder="Say something..."
          @keyup.enter="handleChatSubmit"
        />
        <div v-if="chatMessages.length > 0" class="chat-messages">
          <div 
            v-for="(msg, index) in chatMessages" 
            :key="index" 
            class="chat-message"
            :class="msg.role"
          >
            <span class="chat-role">{{ msg.role === 'user' ? 'You' : 'Assistant' }}:</span>
            <span class="chat-text">{{ msg.text }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="block">
      <div class="block-title">追问（只做检索+评估）</div>
      <div class="row">
        <input
          v-model="followUpInput"
          class="chat-input"
          placeholder="输入追问，将追加到最后一轮 iteration"
          @keyup.enter="submitFollowUp"
        />
        <button class="btn small" @click="submitFollowUp">发送</button>
      </div>
    </section>
  </div>
</template>

<script>
import { marked } from 'marked';

export default {
  name: 'LeftPanel',
  data() {
    return {
      ragCollections: ['multimodal2text', 'LLMvisDataset'],
      selectedRagCollection: 'multimodal2text',
      planPrompt: '',
      evaluatePrompt: '',
      planPromptDraft: '',
      evaluatePromptDraft: '',
      editingPlanPrompt: false,
      editingEvaluatePrompt: false,
      openPlanPrompt: false,
      openEvalPrompt: false,
      experimentFiles: [],
      selectedExperimentFile: '',
      searchPlanIteration: 7,
      ragResultPerPlan: 10,
      plansPerRound: 3,
      uploadedFiles: [],
      chatInput: '',
      chatMessages: [],
      followUpInput: ''
    };
  },
  methods: {
    normalizePromptIndent(text) {
      const s = String(text || '');
      const lines = s.replace(/\r\n/g, '\n').split('\n');
      const nonEmpty = lines.filter(l => l.trim().length > 0);
      if (nonEmpty.length === 0) return s;
      const indents = nonEmpty.map(l => {
        const m = l.match(/^[ \t]*/);
        return (m ? m[0] : '').length;
      });
      const minIndent = Math.min(...indents);
      if (!Number.isFinite(minIndent) || minIndent <= 0) return s;
      // 第一步：移除公共缩进（来自 python 代码缩进）
      const deindented = lines.map(l => (l.length >= minIndent ? l.slice(minIndent) : l));
      // 第二步：再移除每行残留的左侧缩进，避免被 Markdown 当成代码块
      // 这里用于“展示 prompt”，不需要保留段首缩进排版
      const cleaned = deindented.map(l => (l.trim().length === 0 ? '' : l.replace(/^[ \t]+/, '')));
      return cleaned.join('\n');
    },

    renderMarkdown(text) {
      try {
        const s = this.normalizePromptIndent(text);
        if (marked && marked.setOptions) {
          marked.setOptions({ breaks: true, gfm: true });
        }
        // marked 版本不同，parse 可能不存在；优先兼容 function 调用方式
        if (marked && typeof marked.parse === 'function') return marked.parse(s);
        return marked(s);
      } catch (e) {
        return `<pre>${String(text || '')}</pre>`;
      }
    },

    async loadAgentPrompts() {
      try {
        const resp = await fetch('/api/agent-prompts');
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        this.planPrompt = typeof data?.plan_prompt === 'string' ? data.plan_prompt : '';
        this.evaluatePrompt = typeof data?.evaluate_prompt === 'string' ? data.evaluate_prompt : '';
        this.planPromptDraft = this.planPrompt;
        this.evaluatePromptDraft = this.evaluatePrompt;
      } catch (e) {
        console.warn('LeftPanel: 加载 agent prompts 失败', e);
        this.planPrompt = '';
        this.evaluatePrompt = '';
        this.planPromptDraft = '';
        this.evaluatePromptDraft = '';
      }
    },

    startEditPlanPrompt() {
      this.planPromptDraft = this.planPrompt || '';
      this.editingPlanPrompt = true;
    },

    confirmEditPlanPrompt() {
      // 不把用户修改内容传给后端，只在本地确认显示
      this.planPrompt = this.planPromptDraft || '';
      this.editingPlanPrompt = false;
    },

    startEditEvaluatePrompt() {
      this.evaluatePromptDraft = this.evaluatePrompt || '';
      this.editingEvaluatePrompt = true;
    },

    confirmEditEvaluatePrompt() {
      // 不把用户修改内容传给后端，只在本地确认显示
      this.evaluatePrompt = this.evaluatePromptDraft || '';
      this.editingEvaluatePrompt = false;
    },

    async loadExperimentFileList() {
      try {
        const resp = await fetch('/api/experiment-files');
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        const files = Array.isArray(data?.files) ? data.files : [];
        const filtered = files.filter(f => typeof f === 'string' && /^experiment.*\.json$/i.test(f));
        this.experimentFiles = filtered;
        if (!this.selectedExperimentFile && this.experimentFiles.length > 0) {
          this.selectedExperimentFile = this.experimentFiles[0];
          this.$emit('river-select-file', this.selectedExperimentFile);
        }
      } catch (e) {
        console.warn('LeftPanel: 加载 experiment 文件列表失败', e);
        this.experimentFiles = [];
      }
    },

    formatExperimentLabel(path) {
      if (!path) return '';
      const name = String(path).split('/').pop() || String(path);
      const m = name.match(/(\d{8})_(\d{6})/);
      if (m) return `${name} (${m[1]} ${m[2]})`;
      return name;
    },

    handlePlansPerRoundChange() {
      const n = Number(this.plansPerRound);
      if (!Number.isFinite(n)) return;
      this.$emit('plans-per-round-change', n);
    },

    handleMaxRoundsChange() {
      const n = Number(this.searchPlanIteration);
      if (!Number.isFinite(n)) return;
      this.$emit('max-rounds-change', n);
    },
    handleRagResultPerPlanChange() {
      const n = Number(this.ragResultPerPlan);
      if (!Number.isFinite(n)) return;
      this.$emit('rag-results-per-plan-change', n);
    },
    handleFileUpload(event) {
      const files = Array.from(event.target.files);
      files.forEach(file => {
        this.uploadedFiles.push({
          name: file.name,
          status: '待处理',
          file: file
        });
        // TODO: 实现文件上传逻辑
        console.log('上传文件:', file.name);
      });
    },
    handleChatSubmit() {
      if (!this.chatInput.trim()) return;
      
      // 添加用户消息
      this.chatMessages.push({
        role: 'user',
        text: this.chatInput
      });
      
      // TODO: 发送到LLM API
      console.log('发送聊天消息:', this.chatInput);
      
      // 模拟回复（实际应该调用API）
      setTimeout(() => {
        this.chatMessages.push({
          role: 'assistant',
          text: '这是一个示例回复。实际应该调用LLM API获取回复。'
        });
      }, 500);
      
      this.chatInput = '';
    },
    submitFollowUp() {
      const q = String(this.followUpInput || '').trim();
      if (!q) return;
      this.$emit('follow-up-submit', q);
      this.followUpInput = '';
    }
  },
  mounted() {
    this.loadExperimentFileList();
    this.loadAgentPrompts();
  }
};
</script>

<style scoped>
.panel {
  padding: 8px;
  height: 100%;
  overflow-y: auto;
}

.block {
  border: 1px solid #ededed;
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 8px;
}

.block-title {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 6px;
}

.textarea {
  width: 100%;
  resize: vertical;
  padding: 8px;
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  font-size: 12px;
  font-family: inherit;
}

.prompt-details {
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  background: #fff;
}

.prompt-summary {
  cursor: pointer;
  user-select: none;
  padding: 8px 10px;
  font-size: 12px;
  font-weight: 600;
}

.prompt-pre {
  margin: 0;
  padding: 8px 10px;
  border-top: 1px solid #e6e6e6;
  font-size: 11px;
  line-height: 1.45;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 240px;
  overflow: auto;
  background: #fafafa;
}

.prompt-body {
  margin-top: 8px;
}

.prompt-actions {
  margin-bottom: 8px;
}

.prompt-btn {
  padding: 6px 10px;
  font-size: 12px;
  margin-right: 8px;
}

.prompt-textarea {
  width: 100%;
  resize: vertical;
  padding: 8px 10px;
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  font-size: 12px;
  font-family: inherit;
  background: #fff;
  max-height: 260px;
  overflow: auto;
  padding-bottom: 46px;
}

.prompt-md {
  padding: 8px 10px;
  border-top: 1px solid #e6e6e6;
  background: #fafafa;
  max-height: 260px;
  overflow: auto;
  font-size: 12px;
  line-height: 1.45;
}

.prompt-md :deep(pre) {
  white-space: pre-wrap;
  word-break: break-word;
}

.prompt-view-wrap {
  position: relative;
}

.prompt-view-actions {
  position: absolute;
  right: 8px;
  bottom: 8px;
}

.prompt-edit-wrap {
  position: relative;
}

.prompt-edit-actions {
  position: absolute;
  right: 8px;
  bottom: 8px;
}

.prompt-edit-actions .btn {
  padding: 6px 10px;
}

input[type="file"] {
  width: 100%;
  font-size: 12px;
  padding: 4px;
}

.file-list {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 8px;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 11px;
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-status {
  color: #666;
  font-size: 10px;
}

.row {
  display: flex;
  align-items: center;
  gap: 6px;
}

input[type="range"] {
  flex: 1;
}

.btn {
  padding: 8px 10px;
  border: 1px solid #e6e6e6;
  background: #fff;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}

.btn:hover {
  border-color: #cfd8e3;
}

.btn.small {
  flex: 1;
}

.btn.secondary {
  background: #f7f7f7;
}

.row-top {
  margin-top: 8px;
}

.select {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  font-size: 12px;
  background: #fff;
}

.value {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
  min-width: 50px;
}

.block-compact .block-title {
  margin-bottom: 8px;
}

.slider-row {
  display: grid;
  grid-template-columns: 88px 1fr 44px;
  align-items: center;
  column-gap: 8px;
  padding: 4px 0;
}

.slider-label {
  font-size: 11px;
  color: #555;
  white-space: nowrap;
}

.slider-value {
  text-align: right;
  font-size: 11px;
  color: #666;
  white-space: nowrap;
}

.slider {
  width: 100%;
}

.empty {
  font-size: 12px;
  color: #999;
  padding: 8px 0;
}

.chatbox {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-hint {
  font-size: 12px;
  color: #666;
}

.chat-input {
  padding: 8px;
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  font-size: 12px;
  font-family: inherit;
}

.chat-messages {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 200px;
  overflow-y: auto;
}

.chat-message {
  padding: 6px 8px;
  border-radius: 4px;
  font-size: 11px;
  line-height: 1.4;
}

.chat-message.user {
  background: #e3f2fd;
  text-align: right;
}

.chat-message.assistant {
  background: #f5f5f5;
  text-align: left;
}

.chat-role {
  font-weight: 600;
  margin-right: 4px;
}

.chat-text {
  color: #333;
}

.global-map-embed {
  width: 100%;
  height: 320px;
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  overflow: hidden;
}

.global-map-controls-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.global-map-embed svg.global-map-svg {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
