<template>
  <div id="app">
    <div class="app-shell">
      <!-- 外框标题栏（FootprintRAG风格：黑色外框） -->
      <header class="app-header">
        <div class="app-title">FootPrintRAG</div>
      </header>
      
      <div class="app-body">
        <!-- 左侧栏：控制面板 -->
        <aside class="left-panel">
          <LeftPanel
            :map-toolbar="mapToolbarState"
            :backend-connected="backendConnected"
            @system-prompt-change="handleSystemPromptChange"
            @rag-collection-change="handleRagCollectionChange"
            @plans-per-round-change="handlePlansPerRoundChange"
            @max-rounds-change="handleMaxRoundsChange"
            @rag-results-per-plan-change="handleRagResultsPerPlanChange"
            @river-load-all="handleRiverLoadAll"
            @river-select-file="handleRiverSelectFile"
            @map-box-toggle="handleMapBoxToggle"
            @map-box-confirm="handleMapBoxConfirm"
            @map-box-clear-filter="handleMapBoxClearFilter"
          />
        </aside>

        <!-- 中间栏：河流图 -->
        <main class="center-panel">
          <EnhancedRiverChart
            ref="riverChart"
            :rag-collection="ragCollection"
            :plans-per-round="plansPerRound"
            :rag-results-per-plan="ragResultsPerPlan"
            :max-rounds="maxRounds"
            :skip-evaluation="false"
            :use-multi-agent-rewrite-streams="true"
            :global-map-mount-id="'left-global-map'"
            @map-toolbar="handleMapToolbar"
            @user-operations-change="handleUserOperationsChange"
            @backend-status-change="handleBackendStatusChange"
          />
        </main>

        <!-- 右侧栏：详情视图 -->
        <aside class="right-panel">
          <section class="user-operation-panel">
            <div class="user-operation-title">用户操作记录</div>
            <div v-if="userOperationRows.length === 0" class="user-operation-empty">
              暂无用户操作
            </div>
            <div v-else class="user-operation-list">
              <div
                v-for="row in userOperationRows"
                :key="row.key"
                class="user-operation-row"
              >
                <div class="strategy-square" :title="row.toolName || ''">
                  <svg v-if="row.thumbnailPoints && row.thumbnailPoints.length" width="100%" height="100%" viewBox="-5 -5 110 110">
                    <circle
                      v-for="(pt, i) in row.thumbnailPoints"
                      :key="i"
                      :cx="pt.x"
                      :cy="pt.y"
                      :r="pt.action === 'UNKNOWN' ? 2.5 : 5"
                      :fill="getPointColor(pt.action)"
                      :opacity="pt.action === 'UNKNOWN' ? 0.45 : 0.9"
                      stroke="rgba(40,50,60,0.35)"
                      stroke-width="1"
                    />
                  </svg>
                  <span v-else>{{ row.label }}</span>
                </div>
                <div class="row-content-right">
                  <div class="thumbnail-dots-area">
                    <div 
                      v-for="(pt, i) in row.thumbnailPoints"
                      :key="'dot-'+i"
                      class="interactive-dot"
                      :style="{ backgroundColor: getPointColor(pt.action), opacity: pt.action === 'UNKNOWN' ? 0.45 : 0.9 }"
                      @click="openPointDetailFromApp(pt.ctx)"
                      :title="pt.id"
                    ></div>
                  </div>
                  <div class="operation-bars">
                    <div
                      v-for="op in row.operations"
                      :key="op.key"
                      class="operation-bar"
                      :style="{ background: getPointColor(op.after || op.action) }"
                      :title="`${op.after || op.action} ${op.targetEvidenceId || ''}`"
                    ></div>
                    <button 
                      v-if="row.hasPending"
                      class="operation-apply-btn"
                      @click="applyRowOperations(row)"
                      title="Apply pending changes"
                    >Apply</button>
                  </div>
                </div>
              </div>
            </div>
          </section>
          <DetailView />
        </aside>
      </div>
    </div>
  </div>
</template>

<script>
import DetailView from './components/DetailView';
import EnhancedRiverChart from './components/EnhancedRiverChart';
import LeftPanel from './components/LeftPanel.vue';

export default {
  name: 'App',
  components: {
    EnhancedRiverChart,
    DetailView,
    LeftPanel,
  },
  data() {
    return {
      ragCollection: 'multimodal2text',
      plansPerRound: 2,
      ragResultsPerPlan: 10,
      maxRounds: 3,
      skipEvaluation: false,
      useMultiAgentRewriteStreams: true,
      vizHydeRerankMapColors: false,
      showHydeInPlanSummary: false,
      mapToolbarState: {
        mapBoxSelectMode: false,
        mapRagPendingIds: [],
        mapRagFilterIds: [],
      },
      userOperationRows: [],
      backendConnected: false,
    };
  },
  methods: {
    openPointDetailFromApp(ctx) {
      if (this.$refs.riverChart && typeof this.$refs.riverChart.showDetail === 'function' && ctx && ctx.rag) {
        this.$refs.riverChart.showDetail(ctx.rag.retrieval_result, ctx.rag.evaluation, ctx);
      }
    },
    applyRowOperations(row) {
      if (this.$refs.riverChart && typeof this.$refs.riverChart.applyPendingOperations === 'function') {
        this.$refs.riverChart.applyPendingOperations(row);
      }
    },
    getPointColor(action) {
      if (action === 'GROW') return '#22c55e';
      if (action === 'KEEP') return '#0ea5e9';
      if (action === 'PRUNE') return '#ef4444';
      return '#cbd5e1';
    },
    handleSystemPromptChange(prompt) {
      // 处理全局系统提示变化
      console.log('System prompt changed:', prompt);
      // TODO: 可以发送到store或传递给其他组件
    },
    handleRagCollectionChange(val) {
      if (val) {
        this.ragCollection = val;
      }
    },
    handlePlansPerRoundChange(n) {
      const value = Number(n);
      if (!Number.isFinite(value)) return;
      this.plansPerRound = Math.max(1, Math.min(10, value));
    },
    handleRagResultsPerPlanChange(n) {
      const value = Number(n);
      if (!Number.isFinite(value)) return;
      this.ragResultsPerPlan = value;
    },

    handleMaxRoundsChange(n) {
      const value = Number(n);
      if (!Number.isFinite(value)) return;
      // 与后端一致：1–10
      this.maxRounds = Math.max(1, Math.min(10, value));
    },

    handleRiverLoadAll() {
      this.$refs.riverChart?.loadAllRounds?.();
    },
    handleRiverSelectFile(file) {
      this.$refs.riverChart?.setSelectedDataFile?.(file);
    },
    handleMapToolbar(payload) {
      if (!payload || typeof payload !== 'object') return;
      this.mapToolbarState = {
        mapBoxSelectMode: !!payload.mapBoxSelectMode,
        mapRagPendingIds: Array.isArray(payload.mapRagPendingIds) ? payload.mapRagPendingIds : [],
        mapRagFilterIds: Array.isArray(payload.mapRagFilterIds) ? payload.mapRagFilterIds : [],
      };
    },
    handleUserOperationsChange(rows) {
      this.userOperationRows = Array.isArray(rows) ? rows : [];
    },
    handleBackendStatusChange(payload) {
      this.backendConnected = !!(payload && payload.connected);
    },
    handleMapBoxToggle() {
      this.$refs.riverChart?.toggleMapBoxSelectMode?.();
    },
    handleMapBoxConfirm() {
      this.$refs.riverChart?.confirmMapRagSelection?.();
    },
    handleMapBoxClearFilter() {
      this.$refs.riverChart?.clearMapRagFilter?.();
    },
  }
};
</script>

<style scoped>
/* 全局布局 */
#app {
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.app-shell {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  border: 2px solid #000000; /* FootprintRAG风格：黑色外框 */
  box-sizing: border-box;
}

/* 外框标题栏（FootprintRAG风格：黑色背景） */
.app-header {
  height: 44px;
  display: flex;
  align-items: center;
  padding: 0 14px;
  background: #000000; /* FootprintRAG风格：黑色背景 */
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  border-bottom: 2px solid #000000;
}

.app-title {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

/* 三栏主体布局 */
.app-body {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr) 25%; /* 左固定 | 中间自适应 | 右 25% 屏宽 */
  gap: 0;
  overflow: hidden;
  height: calc(100% - 44px); /* 减去标题栏高度 */
}

/* 三栏基础样式 */
.left-panel,
.center-panel,
.right-panel {
  min-height: 0;
  overflow: hidden;
  background: #fff;
  display: flex;
  flex-direction: column;
}

.left-panel {
  border-right: 1px solid #e6e6e6;
  overflow-y: auto;
}

.center-panel {
  border-right: 1px solid #e6e6e6;
  position: relative;
  overflow: hidden;
}

.right-panel {
  background-color: #f8f9fa;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

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
}

.user-operation-list {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-auto-rows: calc((100% - 24px) / 4);
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
}

.strategy-square {
  height: 100%;
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
  gap: 4px;
}

.thumbnail-dots-area {
  flex: 0 0 calc(75% - 2px);
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  align-items: flex-start;
  gap: 4px;
  overflow-y: auto;
  padding-right: 2px;
}

.interactive-dot {
  height: calc(50% - 2px);
  aspect-ratio: 1;
  border-radius: 50%;
  box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.15);
  cursor: pointer;
  flex-shrink: 0;
  transition: filter 0.2s;
}

.interactive-dot:hover {
  filter: brightness(1.15) drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.operation-bars {
  flex: 0 0 calc(25% - 2px);
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

.operation-bar-delete {
  background: #dc2626;
}
</style>
