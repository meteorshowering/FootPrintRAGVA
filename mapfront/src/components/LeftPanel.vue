<template>
  <div class="panel">
    <section class="block block-compact">
      <div class="block-title">DataSets</div>
      <div class="row row-top">
        <select class="select" v-model="selectedRagCollection" @change="$emit('rag-collection-change', selectedRagCollection)">
          <option v-for="c in ragCollections" :key="c.value" :value="c.value">
            {{ c.label }}
          </option>
        </select>
      </div>
    </section>

    <section class="block">
      <div class="block-title-row">
        <div class="block-title">Global Map</div>
        <div class="left-global-map-toolbar embed-map-toolbar">
        <button
          type="button"
          class="map-box-toggle"
          :class="{ 'is-active': mapToolbar.mapBoxSelectMode }"
          title="Select box to confirm, only search within these points"
          @click="$emit('map-box-toggle')"
        >Select Box</button>
        <button
          v-if="(mapToolbar.mapRagPendingIds || []).length"
          type="button"
          class="map-box-confirm"
          title="Set the current selected box as the search range"
          @click="$emit('map-box-confirm')"
        >Confirm({{ (mapToolbar.mapRagPendingIds || []).length }})</button>
        <button
          v-if="(mapToolbar.mapRagFilterIds || []).length"
          type="button"
          class="map-box-clear-filter"
          title="Cancel the limit, restore full library search"
          @click="$emit('map-box-clear-filter')"
        >Selected({{ (mapToolbar.mapRagFilterIds || []).length }})</button>
        </div>
      </div>
      <div id="left-global-map" class="global-map-embed"></div>
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

      <div class="slider-row">
        <div class="slider-label">top k</div>
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

    </section>

    <section class="block">
      <div class="block-title">LLM Chat</div>
      <div class="llm-chat-box">
        <div class="llm-chat-messages">
          <div
            v-for="(m, idx) in llmChatMessages"
            :key="`m-${idx}`"
            class="llm-chat-msg"
            :class="m.role === 'user' ? 'is-user' : 'is-assistant'"
          >
            <div class="llm-chat-msg-role">{{ m.role === 'user' ? '你' : '模型' }}</div>
            <div class="llm-chat-msg-text">{{ m.content }}</div>
          </div>
          <div v-if="llmChatSending" class="llm-chat-msg is-assistant is-pending">
            <div class="llm-chat-msg-role">Model</div>
            <div class="llm-chat-msg-text">Generating…</div>
          </div>
        </div>
        <div class="llm-chat-input-row">
          <textarea
            v-model="llmChatDraft"
            class="llm-chat-input"
            rows="2"
            placeholder="Enter a message, send with Enter (Shift+Enter to newline)"
            :disabled="llmChatSending"
            @keydown.enter.exact.prevent="sendLlmChat"
            @keydown.enter.shift.exact.stop
          ></textarea>
          <div class="llm-chat-actions">
            <button type="button" class="btn btn-submit" :disabled="llmChatSending || !llmChatDraft.trim()" @click="sendLlmChat">
              Send
            </button>
            <button type="button" class="btn" :disabled="llmChatSending || llmChatMessages.length === 0" @click="clearLlmChat">
              Clear
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="block">
      <div class="block-title">Research History</div>
      <div class="row row-top research-history-row">
        <select class="select" v-model="selectedExperimentFile" @change="$emit('river-select-file', selectedExperimentFile)">
          <option v-for="f in experimentFiles" :key="f" :value="f">
            {{ formatExperimentLabel(f) }}
          </option>
        </select>
        <button class="btn research-history-load-btn" @click="$emit('river-load-all')">Load</button>
      </div>
    </section>

    <section class="backend-status-footer">
      <span class="backend-status-dot" :class="{ connected: backendConnected }"></span>
      <span>{{ backendConnected ? 'Backend Connected' : 'Backend Disconnected' }}</span>
    </section>

  </div>
</template>

<script>
import { marked } from 'marked';

export default {
  name: 'LeftPanel',
  props: {
    mapToolbar: {
      type: Object,
      default: () => ({
        mapBoxSelectMode: false,
        mapRagPendingIds: [],
        mapRagFilterIds: [],
      }),
    },
    multiAgentRewriteStreams: {
      type: Boolean,
      default: true,
    },
    backendConnected: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      // value 仍发给后端/子组件；label 仅用于下拉展示
      ragCollections: [
        { value: 'multimodal2text', label: 'AIRVisDataset' },
        { value: 'LLMvisDataset', label: 'LLMvisDataset' },
      ],
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
      searchPlanIteration: 3,
      ragResultPerPlan: 10,
      plansPerRound: 2,
      // 固定为默认评估：不再提供 UI 关闭评估
      skipEvaluation: false,
      llmChatDraft: '',
      llmChatSending: false,
      llmChatMessages: [],
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
          // 父组件 ref 可能尚未就绪，下一帧再同步到 EnhancedRiverChart.selectedDataFile
          this.$nextTick(() => {
            this.$emit('river-select-file', this.selectedExperimentFile);
          });
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

    async sendLlmChat() {
      const text = String(this.llmChatDraft || '').trim();
      if (!text || this.llmChatSending) return;
      this.llmChatDraft = '';
      if (!Array.isArray(this.llmChatMessages)) this.llmChatMessages = [];
      this.llmChatMessages.push({ role: 'user', content: text });
      this.llmChatSending = true;
      try {
        const resp = await fetch('/api/llm-chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            messages: this.llmChatMessages.slice(-16),
          }),
        });
        if (!resp.ok) {
          const t = await resp.text();
          throw new Error(`HTTP ${resp.status}: ${t}`);
        }
        const data = await resp.json();
        const ans = String(data?.reply || '').trim();
        this.llmChatMessages.push({ role: 'assistant', content: ans || '(empty)' });
        this.$nextTick(() => {
          try {
            const el = this.$el?.querySelector?.('.llm-chat-messages');
            if (el) el.scrollTop = el.scrollHeight;
          } catch (e) {
            /* ignore */
          }
        });
      } catch (e) {
        this.llmChatMessages.push({ role: 'assistant', content: `（请求失败）${e?.message || e}` });
      } finally {
        this.llmChatSending = false;
      }
    },

    clearLlmChat() {
      this.llmChatDraft = '';
      this.llmChatMessages = [];
    },
  },
  mounted() {
    this.loadExperimentFileList();
    this.loadAgentPrompts();
  }
};
</script>

<style scoped>
.skip-eval-row,
.default-option-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 10px;
  font-size: 12px;
  line-height: 1.35;
  color: rgba(51, 65, 85, 0.95);
  cursor: pointer;
}
.skip-eval-row input,
.default-option-row input {
  margin-top: 2px;
}

.multi-agent-footer,
.multi-agent-hint,
.default-run-hint {
  margin: 6px 0 0;
  font-size: 11px;
  line-height: 1.35;
  color: rgba(100, 116, 139, 0.95);
}

.backend-status-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  margin-top: 8px;
  font-size: 12px;
  color: rgba(51, 65, 85, 0.95);
}

.backend-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #94a3b8;
  box-shadow: 0 0 0 3px rgba(148, 163, 184, 0.15);
}

.backend-status-dot.connected {
  background: #22c55e;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.16);
}

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

.block-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 6px;
}

.block-title-row .block-title {
  margin-bottom: 0;
  flex: 0 0 auto;
}

.block-title-row .left-global-map-toolbar {
  margin-bottom: 0;
  flex: 0 0 auto;
}

.block-title-row .embed-map-toolbar {
  justify-content: flex-end;
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

.research-history-row .select {
  flex: 1 1 auto;
  min-width: 0;
}

.research-history-load-btn {
  flex: 0 0 auto;
  padding: 6px 10px;
  font-size: 11px;
  line-height: 1.1;
  border-radius: 999px;
  white-space: nowrap;
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

.chat-input {
  flex: 1;
  min-width: 0;
  padding: 8px;
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  font-size: 12px;
  font-family: inherit;
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

.left-global-map-toolbar {
  margin-bottom: 8px;
  min-height: 0;
}

.embed-map-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.embed-map-toolbar .map-box-toggle,
.embed-map-toolbar .map-box-confirm,
.embed-map-toolbar .map-box-clear-filter {
  padding: 6px 10px;
  font-size: 12px;
  border-radius: 6px;
  border: 1px solid #e6e6e6;
  background: #fff;
  color: #333;
  cursor: pointer;
}

.embed-map-toolbar .map-box-toggle.is-active {
  background: #e67e22;
  color: #fff;
  border-color: #d35400;
}

.embed-map-toolbar .map-box-confirm {
  background: #28a745;
  color: #fff;
  border-color: #1e7e34;
}

.embed-map-toolbar .map-box-clear-filter {
  background: #6c757d;
  color: #fff;
  border-color: #545b62;
}

.llm-chat-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 200px;
  min-height: 140px;
  max-height: 240px;
}

.llm-chat-messages {
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  background: #fff;
  padding: 8px;
  flex: 1 1 auto;
  min-height: 0;
  overflow: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge legacy */
}

.llm-chat-messages::-webkit-scrollbar {
  width: 0;
  height: 0;
  display: none; /* Chrome/Safari */
}

.llm-chat-msg {
  display: grid;
  grid-template-columns: 42px 1fr;
  gap: 8px;
  padding: 6px 6px;
  border-radius: 8px;
  margin-bottom: 6px;
  border: 1px solid transparent;
}

.llm-chat-msg:last-child {
  margin-bottom: 0;
}

.llm-chat-msg.is-user {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.18);
}

.llm-chat-msg.is-assistant {
  background: rgba(15, 23, 42, 0.04);
  border-color: rgba(148, 163, 184, 0.22);
}

.llm-chat-msg.is-pending {
  opacity: 0.85;
}

.llm-chat-msg-role {
  font-size: 11px;
  font-weight: 700;
  color: #334155;
  padding-top: 1px;
}

.llm-chat-msg-text {
  font-size: 12px;
  line-height: 1.4;
  color: #0f172a;
  white-space: pre-wrap;
  word-break: break-word;
}

.llm-chat-input-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.llm-chat-input {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 12px;
  line-height: 1.4;
  resize: vertical;
  background: #fff;
  font-family: inherit;
}

.llm-chat-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.map-box-hint {
  margin: 0 0 8px;
  padding: 8px 10px;
  font-size: 11px;
  line-height: 1.45;
  color: #334155;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
}

.map-box-hint strong {
  color: #1d4ed8;
  font-weight: 600;
}

.map-box-hint--muted {
  background: #f8fafc;
  border-color: #e2e8f0;
  color: #64748b;
}

.global-map-embed svg.global-map-svg {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
