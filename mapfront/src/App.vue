<template>
  <div id="app">
    <div class="app-shell">
      <!-- 外框标题栏（FootprintRAG风格：黑色外框） -->
      <header class="app-header">
        <div class="app-title">RAG Lens</div>
      </header>
      
      <div class="app-body">
        <!-- 左侧栏：控制面板 -->
        <aside class="left-panel">
          <LeftPanel
            :map-toolbar="mapToolbarState"
            @system-prompt-change="handleSystemPromptChange"
            @rag-collection-change="handleRagCollectionChange"
            @plans-per-round-change="handlePlansPerRoundChange"
            @max-rounds-change="handleMaxRoundsChange"
            @rag-results-per-plan-change="handleRagResultsPerPlanChange"
            @river-load-all="handleRiverLoadAll"
            @river-clear="handleRiverClear"
            @river-toggle-prune="handleRiverTogglePrune"
            @river-toggle-connections="handleRiverToggleConnections"
            @river-select-file="handleRiverSelectFile"
            @global-map-clear="handleGlobalMapClear"
            @global-map-reset="handleGlobalMapReset"
            @skip-evaluation-change="handleSkipEvaluationChange"
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
            :skip-evaluation="skipEvaluation"
            :global-map-mount-id="'left-global-map'"
            @map-toolbar="handleMapToolbar"
          />
        </main>

        <!-- 右侧栏：详情视图 -->
        <aside class="right-panel">
          <DetailView 
            v-if="!showHypothesisView" 
            @show-hypothesis="handleShowHypothesis"
          />
          <HypothesisView 
            v-else
            :hypothesis-data="hypothesisData"
            @go-back="handleGoBack"
            @navigate-to-chunk="handleNavigateToChunk"
          />
        </aside>
      </div>
    </div>
  </div>
</template>

<script>
import DetailView from './components/DetailView';
import HypothesisView from './components/HypothesisView';
import EnhancedRiverChart from './components/EnhancedRiverChart';
import LeftPanel from './components/LeftPanel.vue';

export default {
  name: 'App',
  components: {
    EnhancedRiverChart,
    DetailView,
    HypothesisView,
    LeftPanel,
  },
  data() {
    return {
      showHypothesisView: false,
      hypothesisData: null,
      ragCollection: 'multimodal2text',
      plansPerRound: 2,
      ragResultsPerPlan: 10,
      maxRounds: 3,
      skipEvaluation: false,
      mapToolbarState: {
        mapBoxSelectMode: false,
        mapRagPendingIds: [],
        mapRagFilterIds: [],
      },
    };
  },
  methods: {
    handleShowHypothesis(hypothesisData) {
      this.hypothesisData = hypothesisData;
      this.showHypothesisView = true;
    },
    handleGoBack() {
      this.showHypothesisView = false;
      this.hypothesisData = null;
    },
    handleNavigateToChunk(chunkId) {
      // 通知EnhancedRiverChart跳转到指定chunk
      if (this.$refs.riverChart) {
        this.$refs.riverChart.navigateToChunk(chunkId);
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
    handleRiverClear() {
      this.$refs.riverChart?.clearChart?.();
    },
    handleRiverTogglePrune() {
      this.$refs.riverChart?.toggleHidePrunePoints?.();
    },
    handleRiverToggleConnections() {
      this.$refs.riverChart?.toggleConnections?.();
    },
    handleRiverSelectFile(file) {
      this.$refs.riverChart?.setSelectedDataFile?.(file);
    },
    handleGlobalMapClear() {
      this.$refs.riverChart?.clearGlobalMapHighlight?.();
    },
    handleGlobalMapReset() {
      this.$refs.riverChart?.resetGlobalMapSize?.();
    },
    handleSkipEvaluationChange(val) {
      this.skipEvaluation = !!val;
    },
    handleMapToolbar(payload) {
      if (!payload || typeof payload !== 'object') return;
      this.mapToolbarState = {
        mapBoxSelectMode: !!payload.mapBoxSelectMode,
        mapRagPendingIds: Array.isArray(payload.mapRagPendingIds) ? payload.mapRagPendingIds : [],
        mapRagFilterIds: Array.isArray(payload.mapRagFilterIds) ? payload.mapRagFilterIds : [],
      };
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
  overflow-y: auto;
  background-color: #f8f9fa;
}
</style>
