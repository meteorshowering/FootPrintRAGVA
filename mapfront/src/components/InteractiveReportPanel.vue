<template>
  <div class="ir-panel">
    <div class="ir-panel-head">
      <span class="ir-panel-title">Interactive Report</span>
      <div style="display: flex; gap: 8px;">
        <button type="button" class="ir-btn-action" @click="generateReport" :disabled="isGenerating">
          {{ isGenerating ? 'generating...' : 'generate report (LLM)' }}
        </button>
        <button type="button" class="ir-btn-clear" @click="clearAll" :disabled="sections.length === 0">
          clear
        </button>
      </div>
    </div>

    <div class="ir-sections">
      <div
        v-for="section in sections"
        :key="section.id"
        class="ir-section"
      >
        <div class="ir-section-bar">
          <input
            type="text"
            class="ir-section-title-input"
            :value="section.title"
            aria-label="版块标题"
            placeholder="版块标题"
            @input="updateSectionTitle(section.id, $event.target.value)"
          />
          <div class="ir-view-toolbar" @mousedown.stop>
            <button
              type="button"
              class="ir-circle-btn ir-circle-btn--pt"
              :title="section.showText ? '当前：文本视图，点击查看要点视图' : '当前：要点视图，点击查看文本视图'"
              @click.stop="toggleText(section.id)"
            >
              {{ section.showText ? 'T' : 'P' }}
            </button>
            <button
              type="button"
              class="ir-circle-btn ir-circle-btn--ghost"
              title="重置（即将推出）"
              aria-label="重置"
              @click.prevent.stop
            >
              <svg class="ir-circle-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"
                />
              </svg>
            </button>
            <button
              type="button"
              class="ir-circle-btn ir-circle-btn--ghost ir-circle-btn--danger-hover"
              title="删除版块"
              aria-label="删除版块"
              @click.stop="removeSection(section.id)"
            >
              <svg class="ir-circle-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"
                />
              </svg>
            </button>
          </div>
        </div>
        <div
          class="interactive-report-drop-zone ir-drop-body"
          :data-section-id="section.id"
          @dragover.prevent="onDragOver"
          @drop.prevent="onDrop($event, section.id)"
        >
          <div v-if="section.showText" class="ir-text-edit-stack">
            <textarea
              v-show="textEditingSectionId === section.id"
              class="ir-section-textarea"
              :data-section-text="section.id"
              rows="6"
              :value="section.text"
              aria-label="版块正文"
              placeholder="正文…（支持 [chunk_id] 引用）"
              @input="updateSectionText(section.id, $event.target.value)"
              @blur="endSectionTextEdit"
            />
            <div
              v-show="textEditingSectionId !== section.id"
              class="ir-section-text ir-section-text--preview"
              tabindex="0"
              role="button"
              title="单击编辑正文"
              @click="startSectionTextEdit(section.id)"
              @keydown.enter.prevent="startSectionTextEdit(section.id)"
            >
              <template v-if="(section.text || '').trim().length">
                <template v-for="(seg, si) in parseSectionCitations(section)" :key="'s-' + section.id + '-' + si">
                  <span v-if="seg.type === 'text'" class="ir-text-run">{{ seg.text }}</span>
                  <span v-else class="ir-cite-wrap" :title="citeGroupTitle(seg)">
                    <span class="ir-cite-bracket">[</span>
                    <template v-for="(t, ti) in seg.tokens" :key="'t-' + section.id + '-' + si + '-' + ti">
                      <span v-if="ti > 0" class="ir-cite-sep">; </span>
                      <button
                        v-if="t.canonicalId"
                        type="button"
                        class="ir-cite-link"
                        @click.stop="onCitationJump(t.canonicalId)"
                      >
                        {{ t.token }}
                      </button>
                      <span v-else class="ir-cite-miss">{{ t.token }}</span>
                    </template>
                    <span class="ir-cite-bracket">]</span>
                  </span>
                </template>
              </template>
              <span v-else class="ir-text-placeholder">单击输入正文…</span>
            </div>
          </div>
          <div v-else-if="section.items.length === 0" class="ir-empty">Drag Evidence Point</div>
          <div v-else class="ir-dots">
            <div
              v-for="item in section.items"
              :key="item.id"
              class="ir-dot-wrap"
              role="button"
              tabindex="0"
              :title="(item.title || item.id) + ' — click to view details'"
              @click="openPointDetail(item)"
              @keydown.enter.prevent="openPointDetail(item)"
              @keydown.space.prevent="openPointDetail(item)"
            >
              <span class="ir-dot-visual">
                <span
                  class="ir-dot-core"
                  :class="[branchClass(item), { 'is-picture': item.type === 'picture' }]"
                />
              </span>
              <span class="ir-dot-label">{{ displayLabel(item) }}</span>
              <button type="button" class="ir-dot-remove" @click.stop="removePoint(section.id, item.id)">×</button>
            </div>
          </div>
        </div>
      </div>

      <button type="button" class="ir-add-placeholder" @click="promptAddSection" title="add section">
        <span class="ir-add-plus">+</span>
        <span class="ir-add-text">new section</span>
      </button>
    </div>

    <Teleport to="body">
      <div v-if="showPointDetailModal" class="ir-modal" @click.self="closePointDetailModal">
        <div class="ir-modal-content ir-point-detail-modal">
          <div class="ir-modal-header">
            <h2>Data point details</h2>
            <button type="button" @click="closePointDetailModal" class="ir-modal-close">×</button>
          </div>
          <div class="ir-modal-body">
            <ItemDetail v-if="selectedPointDetail" :item="selectedPointDetail" />
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue';
import { useStore } from 'vuex';
import ItemDetail from './ItemDetail.vue';

const store = useStore();

/** Text view：预览（可点引用）与单击后的 textarea 编辑互斥 */
const textEditingSectionId = ref(null);

function updateSectionTitle(sectionId, title) {
  store.commit('updateInteractiveReportSectionTitle', { sectionId, title });
}

function updateSectionText(sectionId, text) {
  store.commit('updateInteractiveReportSectionText', { sectionId, text });
}

async function startSectionTextEdit(sectionId) {
  textEditingSectionId.value = sectionId;
  await nextTick();
  const ta =
    typeof document !== 'undefined'
      ? document.querySelector(`textarea.ir-section-textarea[data-section-text="${sectionId}"]`)
      : null;
  ta?.focus();
}

function endSectionTextEdit() {
  textEditingSectionId.value = null;
}

/** 与地图 / 报告中 id 对齐（去 img_ 等） */
function normalizeEvidenceId(raw) {
  let s = String(raw ?? '').trim();
  if (!s) return '';
  if (s.startsWith('img_')) s = s.slice(4);
  return s;
}

/** 括号内引用串：按英文/中文分号切段（与后端 [chunk_a; chunk_b] 一致） */
function splitCitationInnerTokens(inner) {
  return String(inner ?? '')
    .split(/[;\uff1b]/)
    .map((t) => t.trim())
    .filter(Boolean);
}

/** section.items 建立 normId -> 规范 id（items[].id） */
function buildEvidenceIdResolver(section) {
  const map = new Map();
  (section.items || []).forEach((item) => {
    if (!item || !item.id) return;
    const n = normalizeEvidenceId(item.id);
    if (n && !map.has(n)) map.set(n, item.id);
  });
  return map;
}

/**
 * 按 [ ... ] 切段；括号内按 ; 分割为多个引用 token。
 * 仅当 token 能对应 section.items 中某条时为可点击链接。
 */
function parseSectionCitations(section) {
  const text = section.text || '';
  const resolver = buildEvidenceIdResolver(section);
  const re = /\[([^\]]+)\]/g;
  const segments = [];
  let last = 0;
  let m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) {
      segments.push({ type: 'text', text: text.slice(last, m.index) });
    }
    const inner = m[1];
    const tokens = splitCitationInnerTokens(inner).map((token) => {
      const norm = normalizeEvidenceId(token);
      const canonicalId = norm && resolver.has(norm) ? resolver.get(norm) : null;
      return { token, canonicalId };
    });
    segments.push({ type: 'cite', tokens });
    last = m.index + m[0].length;
  }
  if (last < text.length) {
    segments.push({ type: 'text', text: text.slice(last) });
  }
  return segments.length ? segments : [{ type: 'text', text }];
}

function citeGroupTitle(seg) {
  if (!seg.tokens || seg.type !== 'cite') return '';
  const linked = seg.tokens.filter((t) => t.canonicalId).length;
  return linked ? 'Jump to evidence on river chart' : '';
}

function onCitationJump(canonicalId) {
  if (!canonicalId) return;
  store.commit('setInteractiveReportCitationFocus', canonicalId);
}

const showPointDetailModal = ref(false);
const selectedPointDetail = ref(null);
const isGenerating = ref(false);

const generateReport = async () => {
  const sourcePath = store.state.experimentSourceFile;
  const sessionId = store.state.experimentResult?.session_id || '';
  if (!sourcePath) {
    window.alert('请先在左侧选择一个实验文件后再生成报告。');
    return;
  }
  isGenerating.value = true;
  try {
    const res = await fetch('/api/generate-interactive-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_path: sourcePath, session_id: sessionId })
    });
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    // The backend processes this asynchronously and broadcasts the result via WebSocket.
    // It will be reflected in the UI when the WS message arrives.
    window.alert('报告生成已在后台启动，完成后将自动刷新面板，请稍候...');
  } catch (error) {
    console.error('Failed to trigger report generation:', error);
    window.alert('生成报告请求失败，请检查网络或后端日志。');
  } finally {
    isGenerating.value = false;
  }
};

const openPointDetail = (item) => {
  selectedPointDetail.value = item;
  showPointDetailModal.value = true;
};

const closePointDetailModal = () => {
  showPointDetailModal.value = false;
  selectedPointDetail.value = null;
};

const sections = computed(() => store.state.interactiveReportSections || []);

const promptAddSection = () => {
  const title = window.prompt('请输入该版块的小主题标题：', '');
  if (title === null) return;
  const t = String(title).trim();
  if (!t) {
    window.alert('标题不能为空');
    return;
  }
  store.commit('addInteractiveReportSection', { title: t });
};

const removeSection = (sectionId) => {
  if (!window.confirm('确定删除该版块及其中的点？')) return;
  store.commit('removeInteractiveReportSection', sectionId);
};

const removePoint = (sectionId, itemId) => {
  store.commit('removePointFromInteractiveReportSection', { sectionId, itemId });
};

const toggleText = (sectionId) => {
  textEditingSectionId.value = null;
  store.commit('toggleInteractiveReportSectionText', sectionId);
};

const clearAll = () => {
  if (!window.confirm('确定清空所有 Interactive Report 版块？')) return;
  store.commit('clearInteractiveReport');
};

const onDragOver = (e) => {
  e.dataTransfer.dropEffect = 'copy';
};

const onDrop = (e, sectionId) => {
  const raw = e.dataTransfer?.getData('application/json');
  if (!raw) return;
  try {
    const payload = JSON.parse(raw);
    if (payload.type !== 'interactive-report-item' || !payload.item) return;
    store.commit('addPointToInteractiveReportSection', { sectionId, item: payload.item });
  } catch (err) {
    console.warn('Interactive Report drop 解析失败', err);
  }
};

const branchClass = (item) => {
  const action = item.branch_action || 'UNKNOWN';
  if (action === 'GROW') return 'action-grow';
  if (action === 'KEEP') return 'action-keep';
  if (action === 'PRUNE') return 'action-prune';
  if (action === 'PENDING') return 'action-pending';
  return 'action-unknown';
};

/** 列表展示：不截断；标题缺省时用正文或 id */
const displayLabel = (item) => {
  const raw = (item.title && String(item.title).trim()) || '';
  const text = (item.text_content && String(item.text_content).replace(/\s+/g, ' ').trim()) || '';
  if (raw && raw !== 'No Title') return raw;
  if (text) return text;
  return item.id || '';
};
</script>

<style scoped>
.ir-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px 14px;
  background: linear-gradient(180deg, #f0f9ff 0%, #f8fafc 100%);
  border: 1px solid #bae6fd;
  border-radius: 10px;
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.ir-panel-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 12px;
}

.ir-panel-title {
  font-weight: 700;
  font-size: 15px;
  color: #0c4a6e;
}

.ir-panel-hint {
  font-size: 12px;
  color: #64748b;
  flex: 1;
  min-width: 140px;
}

.ir-btn-clear, .ir-btn-action {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  background: #fff;
  color: #475569;
  cursor: pointer;
}

.ir-btn-action {
  background: #e0f2fe;
  border-color: #bae6fd;
  color: #0284c7;
  font-weight: 600;
}

.ir-btn-clear:hover:not(:disabled) {
  background: #f1f5f9;
}

.ir-btn-action:hover:not(:disabled) {
  background: #bae6fd;
}

.ir-btn-clear:disabled, .ir-btn-action:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.ir-sections {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ir-section {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  background: #fff;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
}

.ir-section-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 12px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.ir-section-title-input {
  flex: 1;
  min-width: 0;
  margin: 0;
  padding: 6px 10px;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  transition:
    border-color 0.15s,
    box-shadow 0.15s,
    background 0.15s;
}

.ir-section-title-input:hover {
  border-color: #e2e8f0;
  background: #fff;
}

.ir-section-title-input:focus {
  outline: none;
  border-color: #7dd3fc;
  box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.22);
  background: #fff;
}

.ir-section-title-input::placeholder {
  color: #94a3b8;
  font-weight: 500;
}

.ir-view-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.ir-circle-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition:
    background 0.15s,
    border-color 0.15s,
    color 0.15s,
    box-shadow 0.15s;
  flex-shrink: 0;
}

.ir-circle-btn--pt {
  border: 1px solid #7dd3fc;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.ir-circle-btn--pt:hover {
  background: #bae6fd;
  border-color: #38bdf8;
  box-shadow: 0 1px 4px rgba(14, 165, 233, 0.35);
}

.ir-circle-btn--ghost {
  border: 1px solid #e2e8f0;
  background: #fff;
  color: #64748b;
}

.ir-circle-btn--ghost:hover {
  border-color: #cbd5e1;
  color: #475569;
  background: #f8fafc;
}

.ir-circle-btn--danger-hover:hover {
  border-color: #fecaca;
  color: #dc2626;
  background: #fef2f2;
}

.ir-circle-icon {
  width: 17px;
  height: 17px;
  display: block;
}

.ir-text-edit-stack {
  position: relative;
  min-height: 120px;
}

.ir-section-textarea {
  width: 100%;
  box-sizing: border-box;
  min-height: 140px;
  resize: vertical;
  margin: 0;
  padding: 10px 12px;
  font-size: 13px;
  line-height: 1.6;
  color: #475569;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  font-family: inherit;
}

.ir-section-textarea:focus {
  outline: none;
  border-color: #7dd3fc;
  box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.18);
}

.ir-section-text--preview {
  min-height: 120px;
  cursor: text;
  padding: 8px 6px;
  border-radius: 8px;
  border: 1px dashed transparent;
  transition:
    border-color 0.15s,
    background 0.15s;
}

.ir-section-text--preview:hover {
  border-color: #bae6fd;
  background: #fafdff;
}

.ir-text-placeholder {
  font-size: 13px;
  color: #94a3b8;
}

.ir-section-text {
  font-size: 13px;
  color: #475569;
  line-height: 1.6;
  padding: 8px 4px;
  white-space: pre-wrap;
}

.ir-text-run {
  white-space: pre-wrap;
}

.ir-cite-wrap {
  white-space: pre-wrap;
  font-weight: 500;
}

.ir-cite-bracket {
  color: #64748b;
  font-weight: 600;
}

.ir-cite-sep {
  color: #64748b;
}

.ir-cite-link {
  display: inline;
  padding: 0;
  margin: 0;
  border: none;
  background: none;
  color: #2563eb;
  text-decoration: underline;
  text-underline-offset: 2px;
  cursor: pointer;
  font: inherit;
  vertical-align: baseline;
}

.ir-cite-link:hover {
  color: #1d4ed8;
}

.ir-cite-miss {
  color: #64748b;
}

.ir-btn-icon {
  width: 26px;
  height: 26px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #94a3b8;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
}

.ir-btn-icon:hover {
  background: #fee2e2;
  color: #b91c1c;
}

.ir-drop-body {
  min-height: 100px;
  padding: 10px;
  transition: box-shadow 0.15s ease, background 0.15s ease;
}

.ir-drop-body:hover {
  background: #fafbff;
}

:global(.interactive-report-drop-active) {
  outline: 2px dashed #0ea5e9;
  outline-offset: -2px;
  background: #eff6ff !important;
}

.ir-empty {
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
  padding: 24px 8px;
}

.ir-dots {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 14px;
  align-items: flex-start;
}

.ir-dot-wrap {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
  padding: 4px 8px 4px 4px;
  border-radius: 999px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  font-size: 11px;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, box-shadow 0.15s;
}

.ir-dot-wrap:hover {
  background: #e8f4fc;
  border-color: #93c5fd;
  box-shadow: 0 1px 4px rgba(14, 165, 233, 0.2);
}

.ir-dot-visual {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  flex-shrink: 0;
}

.ir-dot-core {
  display: block;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid rgba(40, 50, 60, 0.35);
  box-sizing: border-box;
  position: relative;
}

.ir-dot-core.is-picture::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  width: 20px;
  height: 20px;
  margin-left: -10px;
  margin-top: -10px;
  border-radius: 50%;
  border: 1.5px solid rgba(40, 140, 255, 0.95);
  pointer-events: none;
}

.ir-dot-core.action-grow {
  background: #28a745;
}
.ir-dot-core.action-keep {
  background: #ffc107;
}
.ir-dot-core.action-prune {
  background: #dc3545;
}
.ir-dot-core.action-pending {
  background: #6c757d;
}
.ir-dot-core.action-unknown {
  background: #9aa3ad;
}

.ir-dot-label {
  color: #475569;
  white-space: normal;
  word-break: break-word;
  max-width: none;
  min-width: 0;
}

.ir-dot-remove {
  width: 18px;
  height: 18px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: #e2e8f0;
  color: #64748b;
  font-size: 12px;
  line-height: 1;
  cursor: pointer;
  flex-shrink: 0;
}

.ir-dot-remove:hover {
  background: #fecaca;
  color: #b91c1c;
}

.ir-add-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 88px;
  border: 2px dashed #cbd5e1;
  border-radius: 10px;
  background: #fff;
  color: #64748b;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}

.ir-add-placeholder:hover {
  border-color: #0ea5e9;
  color: #0284c7;
  background: #f0f9ff;
}

.ir-add-plus {
  font-size: 28px;
  font-weight: 300;
  line-height: 1;
}

.ir-add-text {
  font-size: 12px;
  font-weight: 500;
}

/* 与 EnhancedRiverChart 中「数据点详情」弹窗视觉一致 */
.ir-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2100;
  backdrop-filter: blur(4px);
}

.ir-modal-content {
  background: white;
  border-radius: 16px;
  max-width: 90%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: ir-modal-fade-in 0.3s ease;
}

@keyframes ir-modal-fade-in {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.ir-point-detail-modal {
  width: 800px;
  max-width: 90vw;
  max-height: 90vh;
}

.ir-point-detail-modal .ir-modal-header {
  padding: 10px 16px;
  border-bottom-width: 1px;
  border-radius: 12px 12px 0 0;
}

.ir-point-detail-modal .ir-modal-header h2 {
  font-size: 16px;
  font-weight: 600;
}

.ir-point-detail-modal .ir-modal-close {
  font-size: 22px;
  padding: 2px 8px;
  border-radius: 4px;
}

.ir-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 2px solid #e9ecef;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  flex-shrink: 0;
}

.ir-modal-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
}

.ir-modal-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: white;
  line-height: 1;
  padding: 5px 10px;
  border-radius: 6px;
  transition: all 0.3s;
}

.ir-modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.ir-modal-body {
  padding: 30px;
  overflow-y: auto;
  min-height: 0;
}
</style>
