<template>
  <section class="user-operation-panel">
    <div class="user-operation-title">User Operations</div>
    <div v-if="!rows || rows.length === 0" class="user-operation-empty">
      点击河流图中的策略小矩形（与卡片高亮边框为同一操作）后，在此查看该策略的缩略地图与数据点；若有删除或改评记录会显示在下方。
    </div>
    <div v-else class="user-operation-list">
      <div
        v-for="row in rows"
        :key="row.key"
        class="user-operation-row"
      >
        <div class="strategy-square" :title="row.toolName || ''">
          <svg
            v-if="row.thumbnailPoints && row.thumbnailPoints.length"
            width="100%"
            height="100%"
            viewBox="-5 -5 110 110"
          >
            <template v-for="(pt, i) in row.thumbnailPoints" :key="'tp-' + i">
              <rect
                v-if="pt.isPicture"
                v-bind="thumbSvgPictureGeom(pt)"
                :fill="getPointColor(pt.action)"
                :opacity="pt.action === 'UNKNOWN' ? 0.45 : 0.9"
                stroke="rgba(40,50,60,0.35)"
                stroke-width="1"
              />
              <circle
                v-else
                :cx="pt.x"
                :cy="pt.y"
                :r="pt.action === 'UNKNOWN' ? 1 : 2.5"
                :fill="getPointColor(pt.action)"
                :opacity="pt.action === 'UNKNOWN' ? 0.45 : 0.9"
                stroke="rgba(40,50,60,0.35)"
                stroke-width="1"
              />
            </template>
          </svg>
          <span v-else class="user-operation-fallback-label">{{ row.label }}</span>
        </div>
        <div
          class="row-content-right"
          :class="{ 'row-content-right--map-only': !showOperationStrip(row) }"
        >
          <div class="thumbnail-dots-area">
            <div class="user-ops-dot-grid" aria-label="分列数据点 GROW KEEP PRUNE">
              <div
                class="user-ops-dot-cell user-ops-dot-cell--drop-target"
                @dragover.prevent
                @drop.prevent="onDropEvalAction(row, 'GROW')"
              >
                <div class="user-ops-dot-cell-scroll">
                  <div class="user-ops-dot-cell-inner">
                    <div
                      v-for="(pt, i) in thumbnailPointsBucket(row, 'GROW')"
                      :key="'g-' + i + '-' + (pt.id || i)"
                      class="interactive-dot"
                      :class="{
                        'interactive-dot--picture': pt.isPicture,
                        'interactive-dot--eval-changed': evidenceEvalChanged(row, pt.id),
                      }"
                      :style="{
                        backgroundColor: getPointColor(pt.action),
                        opacity: pt.action === 'UNKNOWN' ? 0.45 : 0.8,
                      }"
                      :title="pt.id"
                      draggable="true"
                      @dragstart.stop="onThumbDotDragStart(row, pt, $event)"
                      @dragend="onDotDragEnd"
                      @click="$emit('open-point-detail', pt.ctx)"
                    ></div>
                  </div>
                </div>
              </div>
              <div
                class="user-ops-dot-cell user-ops-dot-cell--centroid"
                aria-label="GROW 质心近邻"
              >
                <button
                  type="button"
                  class="user-ops-centroid-btn"
                  :disabled="
                    centroidLoadingKey === row.key ||
                    !rowCollectionName(row) ||
                    thumbnailPointsBucket(row, 'GROW').length === 0
                  "
                  :title="
                    !rowCollectionName(row)
                      ? '未配置向量库（无 JSON parameters 且无左栏库名）'
                      : thumbnailPointsBucket(row, 'GROW').length === 0
                        ? '无 GROW 点'
                        : `按 GROW 点嵌入质心在「${rowCollectionName(row)}」中检索 10 条近邻`
                  "
                  @click="fetchGrowCentroidNeighbors(row)"
                >
                  {{
                    centroidLoadingKey === row.key
                      ? '…'
                      : `Neighbors (${row.centroidNeighborsGrow?.length || 0})`
                  }}
                </button>
                <div class="user-ops-dot-cell-scroll user-ops-dot-cell-scroll--centroid">
                  <div class="user-ops-dot-cell-inner">
                    <div
                      v-for="(nb, i) in centroidNeighborsVisible(row)"
                      :key="'cn-' + i + '-' + (nb.retrieval_result?.id || i)"
                      class="interactive-dot interactive-dot--centroid"
                      :class="{
                        'interactive-dot--picture': retrievalNeighborIsPicture(nb),
                        'interactive-dot--eval-changed': evidenceEvalChanged(
                          row,
                          nb.retrieval_result?.id
                        ),
                      }"
                      :style="{
                        backgroundColor: '#0ea5e9',
                        opacity: 0.92,
                      }"
                      :title="nb.retrieval_result?.id"
                      draggable="true"
                      @dragstart.stop="onCentroidDotDragStart(row, nb, $event)"
                      @dragend="onDotDragEnd"
                      @click="$emit('open-point-detail', neighborCtx(row, nb))"
                    ></div>
                  </div>
                </div>
              </div>
              <div
                class="user-ops-dot-cell user-ops-dot-cell--drop-target"
                @dragover.prevent
                @drop.prevent="onDropEvalAction(row, 'KEEP')"
              >
                <div class="user-ops-dot-cell-scroll">
                  <div class="user-ops-dot-cell-inner">
                    <div
                      v-for="(pt, i) in thumbnailPointsBucket(row, 'KEEP')"
                      :key="'k-' + i + '-' + (pt.id || i)"
                      class="interactive-dot"
                      :class="{
                        'interactive-dot--picture': pt.isPicture,
                        'interactive-dot--eval-changed': evidenceEvalChanged(row, pt.id),
                      }"
                      :style="{
                        backgroundColor: getPointColor(pt.action),
                        opacity: pt.action === 'UNKNOWN' ? 0.45 : 0.8,
                      }"
                      :title="pt.id"
                      draggable="true"
                      @dragstart.stop="onThumbDotDragStart(row, pt, $event)"
                      @dragend="onDotDragEnd"
                      @click="$emit('open-point-detail', pt.ctx)"
                    ></div>
                  </div>
                </div>
              </div>
              <div class="user-ops-dot-cell user-ops-dot-cell--placeholder" aria-hidden="true"></div>
              <div
                class="user-ops-dot-cell user-ops-dot-cell--drop-target"
                @dragover.prevent
                @drop.prevent="onDropEvalAction(row, 'PRUNE')"
              >
                <div class="user-ops-dot-cell-scroll">
                  <div class="user-ops-dot-cell-inner">
                    <div
                      v-for="(pt, i) in thumbnailPointsBucket(row, 'PRUNE')"
                      :key="'p-' + i + '-' + (pt.id || i)"
                      class="interactive-dot"
                      :class="{
                        'interactive-dot--picture': pt.isPicture,
                        'interactive-dot--eval-changed': evidenceEvalChanged(row, pt.id),
                      }"
                      :style="{
                        backgroundColor: getPointColor(pt.action),
                        opacity: pt.action === 'UNKNOWN' ? 0.45 : 0.8,
                      }"
                      :title="pt.id"
                      draggable="true"
                      @dragstart.stop="onThumbDotDragStart(row, pt, $event)"
                      @dragend="onDotDragEnd"
                      @click="$emit('open-point-detail', pt.ctx)"
                    ></div>
                  </div>
                </div>
              </div>
              <div class="user-ops-dot-cell user-ops-dot-cell--placeholder" aria-hidden="true"></div>
            </div>
          </div>

          <div v-if="showOperationStrip(row)" class="operation-bars">
            <div
              v-for="op in row.operations"
              :key="op.key"
              class="operation-bar"
              :style="{ background: getPointColor(op.after || op.action) }"
              :title="`${op.after || op.action} ${op.targetEvidenceId || ''}`"
            ></div>
            <button
              v-if="row.hasPending"
              type="button"
              class="operation-apply-btn"
              title="Apply pending changes"
              @click="$emit('apply-operations', row)"
            >
              Apply
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'UserOperationsPanel',
  props: {
    rows: {
      type: Array,
      default: () => [],
    },
    ragCollection: {
      type: String,
      default: '',
    },
  },
  emits: [
    'open-point-detail',
    'apply-operations',
    'centroid-neighbors-grow',
    'queue-point-eval-from-ctx',
  ],
  data() {
    return {
      centroidLoadingKey: '',
      /** @type {{ rowKey: string, kind: 'thumb'|'centroid', pt?: any, nb?: any } | null} */
      userOpsDragPayload: null,
    };
  },
  methods: {
    getPointColor(action) {
      if (action === 'GROW') return '#22c55e';
      if (action === 'KEEP') return '#eec316';
      if (action === 'PRUNE') return '#ef4444';
      return '#cbd5e1';
    },
    showOperationStrip(row) {
      const n = row?.operations?.length ?? 0;
      return n > 0 || !!row?.hasPending;
    },
    /** 缩略 SVG：图片证据用正方形，边长 = 原圆直径（2r），与 circle 半径一致 */
    thumbSvgPictureGeom(pt) {
      const r = pt?.action === 'UNKNOWN' ? 1 : 2.5;
      const s = 2 * r;
      return {
        x: Number(pt.x) - r,
        y: Number(pt.y) - r,
        width: s,
        height: s,
      };
    },
    /** GROW / KEEP / PRUNE；非三者并入 PRUNE 桶 */
    thumbnailDotBuckets(row) {
      const list = row?.thumbnailPoints;
      const empty = () => ({ GROW: [], KEEP: [], PRUNE: [], OTHER: [] });
      if (!Array.isArray(list) || !list.length) return empty();
      const norm = (a) => String(a == null ? '' : a).trim().toUpperCase();
      const b = empty();
      list.forEach((pt) => {
        const a = norm(pt?.action);
        if (a === 'GROW') b.GROW.push(pt);
        else if (a === 'KEEP') b.KEEP.push(pt);
        else if (a === 'PRUNE') b.PRUNE.push(pt);
        else b.OTHER.push(pt);
      });
      return {
        GROW: b.GROW,
        KEEP: b.KEEP,
        PRUNE: [...b.PRUNE, ...b.OTHER],
      };
    },
    thumbnailPointsBucket(row, kind) {
      const b = this.thumbnailDotBuckets(row);
      return b[kind] || [];
    },
    /** 与当前策略 round 对应的向量库：优先 row.collectionName（来自 experiment JSON parameters），否则左栏 ragCollection */
    rowCollectionName(row) {
      const fromRow = row && row.collectionName != null ? String(row.collectionName).trim() : '';
      if (fromRow) return fromRow;
      return String(this.ragCollection || '').trim();
    },
    neighborCtx(row, nb) {
      return {
        sessionId: row.sessionId,
        roundNumber: row.roundNumber,
        queryIndex: row.queryIndex,
        query: row.query,
        rag: nb,
      };
    },
    evidenceEvalChanged(row, evidenceId) {
      const id = String(evidenceId == null ? '' : evidenceId).trim();
      if (!id || !row) return false;
      const pend = row.pendingByEvidenceId;
      if (pend && Object.prototype.hasOwnProperty.call(pend, id)) return true;
      const u = row.userdoPointEvidenceIds;
      if (Array.isArray(u) && u.includes(id)) return true;
      return false;
    },
    /** 已在 G/K/P 列待应用改评、或已并入 rag_results 的近邻，从质心列隐藏 */
    centroidNeighborsVisible(row) {
      const pend = row.pendingByEvidenceId || {};
      const inRag = new Set();
      const rags = row.query?.rag_results;
      if (Array.isArray(rags)) {
        rags.forEach((r) => {
          const rid = String(r?.retrieval_result?.id || '').trim();
          if (rid) inRag.add(rid);
        });
      }
      return (row.centroidNeighborsGrow || []).filter((nb) => {
        const id = String(nb?.retrieval_result?.id || '').trim();
        return (
          id &&
          !Object.prototype.hasOwnProperty.call(pend, id) &&
          !inRag.has(id)
        );
      });
    },
    onThumbDotDragStart(row, pt, ev) {
      if (!row?.key || !pt) return;
      this.userOpsDragPayload = { rowKey: row.key, kind: 'thumb', pt };
      try {
        ev.dataTransfer.effectAllowed = 'move';
        ev.dataTransfer.setData('text/plain', String(pt.id || ''));
      } catch (e) {
        /* ignore */
      }
    },
    onCentroidDotDragStart(row, nb, ev) {
      if (!row?.key || !nb) return;
      this.userOpsDragPayload = { rowKey: row.key, kind: 'centroid', nb };
      try {
        ev.dataTransfer.effectAllowed = 'move';
        ev.dataTransfer.setData(
          'text/plain',
          String(nb.retrieval_result?.id || '')
        );
      } catch (e) {
        /* ignore */
      }
    },
    onDotDragEnd() {
      this.userOpsDragPayload = null;
    },
    onDropEvalAction(row, newAction) {
      const d = this.userOpsDragPayload;
      if (!d || !row || d.rowKey !== row.key) return;
      let ctx = null;
      if (d.kind === 'centroid' && d.nb) {
        ctx = this.neighborCtx(row, d.nb);
      } else if (d.kind === 'thumb' && d.pt?.ctx) {
        ctx = d.pt.ctx;
      }
      this.userOpsDragPayload = null;
      if (!ctx) return;
      this.$emit('queue-point-eval-from-ctx', { ctx, newAction });
    },
    retrievalNeighborIsPicture(nb) {
      const m = nb?.retrieval_result?.metadata || {};
      if (m.full_json) return true;
      if (m.save_path || m.savepath) return true;
      const t = String(m.type || m.content_type || '').toLowerCase();
      return t === 'picture' || t === 'figure' || t === 'image';
    },
    async fetchGrowCentroidNeighbors(row) {
      const key = row?.key;
      const collectionName = this.rowCollectionName(row);
      if (!key || !collectionName) return;
      const growPts = this.thumbnailPointsBucket(row, 'GROW');
      if (!growPts.length) return;
      this.centroidLoadingKey = key;
      try {
        const points = (row.thumbnailPoints || []).map((pt) => ({
          chunk_id: pt.id,
          action: pt.action || 'UNKNOWN',
        }));
        const res = await fetch('/api/rag-neighbors-from-centroid', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            collection_name: collectionName,
            experiment_source_path: row.experimentSourcePath || undefined,
            round_number: row.roundNumber,
            points,
            centroid_actions: ['GROW'],
            target_count: 10,
          }),
        });
        let data = {};
        try {
          data = await res.json();
        } catch {
          data = {};
        }
        if (!res.ok) {
          const d = data?.detail;
          const msg = typeof d === 'string' ? d : Array.isArray(d) ? JSON.stringify(d) : res.statusText;
          throw new Error(msg || 'request failed');
        }
        this.$emit('centroid-neighbors-grow', {
          rowKey: key,
          neighbors: data.rag_results || [],
        });
      } catch (e) {
        console.warn('[UserOps] centroid neighbors', e);
        window.alert(`质心近邻失败: ${e?.message || e}`);
      } finally {
        this.centroidLoadingKey = '';
      }
    },
  },
};
</script>

<style scoped>
.user-operation-panel {
  flex: 0 0 30%;
  min-height: 0;
  margin: 12px 14px 0 14px;
  padding: 12px;
  background: #ffffff;
  border: 1px solid #bae6fd;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.user-operation-title {
  flex: 0 0 auto;
  font-size: 13px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 10px;
}

.user-operation-empty {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.45;
}

.user-operation-fallback-label {
  font-size: 10px;
  font-weight: 700;
  color: #64748b;
  padding: 4px;
  text-align: center;
}

.user-operation-list {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  padding-right: 4px;
}

.user-operation-row {
  display: flex;
  align-items: stretch;
  gap: 12px;
  box-sizing: border-box;
  padding: 2px 0;
  flex: 1;
  min-height: 0;
}

.strategy-square {
  height: 100%;
  align-self: center;
  aspect-ratio: 1;
  flex-shrink: 0;
  border: 1px solid rgba(148, 163, 184, 0.8);
  border-radius: 4px;
  background: #ffffff;
  color: #0f172a;
  font-size: 11px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.06);
}

.row-content-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  gap: 4px;
  overflow-y: auto;
}

.thumbnail-dots-area {
  flex: 0 0 calc(95% - 2px);
  width: 100%;
  min-width: 0;
  min-height: 0;
  box-sizing: border-box;
}

/* 2 列 × 3 行：列宽 1fr 拉满；行高由 --uops-cell（当前 75px）统一；height 的 calc 与 gap、边框对齐，避免底边被裁 */
.user-ops-dot-grid {
  --uops-cell: 75px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: var(--uops-cell) var(--uops-cell) var(--uops-cell);
  width: 100%;
  height: calc(3 * var(--uops-cell) + 2px + 2px);
  box-sizing: border-box;
  border: 1px solid #94a3b8;
  background: #cbd5e1;
  gap: 1px;
  flex-shrink: 0;
}

.user-ops-dot-cell {
  box-sizing: border-box;
  min-width: 0;
  min-height: 0;
  background: #ffffff;
  overflow: hidden;
}

.user-ops-dot-cell--placeholder {
  background: #f8fafc;
}

.user-ops-dot-cell--centroid {
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 2px 0 0;
  background: #f0f9ff;
}

.user-ops-centroid-btn {
  flex: 0 0 auto;
  align-self: center;
  margin-bottom: 2px;
  padding: 1px 6px;
  font-size: 10px;
  font-weight: 700;
  color: #0369a1;
  background: #e0f2fe;
  border: 1px solid #7dd3fc;
  border-radius: 4px;
  cursor: pointer;
}

.user-ops-centroid-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.user-ops-dot-cell-scroll--centroid {
  flex: 1 1 auto;
  min-height: 0;
}

.user-ops-dot-cell-scroll {
  height: 100%;
  width: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.user-ops-dot-cell-scroll::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}

.user-ops-dot-cell-inner {
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  align-items: flex-start;
  gap: 5px;
  padding: 4px;
  box-sizing: border-box;
  min-height: min-content;
}

.row-content-right--map-only .thumbnail-dots-area {
  flex: 1 1 auto;
  flex-basis: 0;
  min-height: 0;
}

/* 固定像素：父级分组容器无确定高度时，百分比 height 会塌成 0，圆点不可见 */
.interactive-dot {
  width: 10px;
  height: 10px;
  min-width: 10px;
  min-height: 10px;
  border-radius: 50%;
  box-shadow: inset 0 0 0 0.2px rgba(15, 23, 42, 0.15);
  cursor: grab;
  flex-shrink: 0;
  transition: filter 0.2s, box-shadow 0.15s;
}

.interactive-dot--eval-changed {
  box-shadow:
    0 0 0 2px #dc2626,
    inset 0 0 0 0.2px rgba(15, 23, 42, 0.15);
}

.interactive-dot:active {
  cursor: grabbing;
}

.interactive-dot--picture {
  border-radius: 2px;
}

.interactive-dot:hover {
  filter: brightness(1.15) drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.operation-bars {
  flex: 0 0 calc(5% - 2px);
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  align-items: flex-start;
  gap: 4px;
  overflow: hidden;
}

.operation-bar {
  height: 100%;
  aspect-ratio: 1;
  border-radius: 3px;
  box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.12);
  flex-shrink: 0;
}

.operation-apply-btn {
  height: 100%;
  padding: 0 16px;
  border-radius: 3px;
  background: #3b82f6;
  color: white;
  border: none;
  font-size: 11px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 3px rgba(59, 130, 246, 0.3);
}

.operation-apply-btn:hover {
  background: #2563eb;
}
</style>
