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
          <UserOperationsPanel
            :rows="userOperationRows"
            :rag-collection="ragCollection"
            @open-point-detail="openPointDetailFromApp"
            @apply-operations="applyRowOperations"
            @centroid-neighbors-grow="onCentroidNeighborsGrow"
            @queue-point-eval-from-ctx="onQueuePointEvalFromCtx"
          />
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
import UserOperationsPanel from './components/UserOperationsPanel.vue';

export default {
  name: 'App',
  components: {
    EnhancedRiverChart,
    DetailView,
    LeftPanel,
    UserOperationsPanel,
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
      /** row.key -> GROW 行质心近邻 rag_results[]（与 experiment JSON 同构） */
      userOpsCentroidGrowByRow: {},
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
    onQueuePointEvalFromCtx(payload) {
      const ctx = payload && payload.ctx;
      const newAction = payload && payload.newAction;
      if (!ctx || !newAction) return;
      const rc = this.$refs.riverChart;
      if (rc && typeof rc.queuePointEvalFromContext === 'function') {
        rc.queuePointEvalFromContext(ctx, newAction);
      }
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
      const base = Array.isArray(rows) ? rows : [];
      this.userOperationRows = base.map((r) => ({
        ...r,
        centroidNeighborsGrow: this.userOpsCentroidGrowByRow[r.key] || [],
      }));
    },
    onCentroidNeighborsGrow({ rowKey, neighbors }) {
      if (!rowKey) return;
      this.userOpsCentroidGrowByRow = {
        ...this.userOpsCentroidGrowByRow,
        [rowKey]: Array.isArray(neighbors) ? neighbors : [],
      };
      this.userOperationRows = this.userOperationRows.map((r) =>
        r.key === rowKey
          ? { ...r, centroidNeighborsGrow: this.userOpsCentroidGrowByRow[rowKey] }
          : r
      );
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
</style>
