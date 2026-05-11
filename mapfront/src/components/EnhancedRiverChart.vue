<template>
  <div id="enhanced-river-chart">
    <div
      ref="gridViewport"
      class="river-grid-viewport"
      @click="handleViewportClick"
      @wheel.prevent="handleGridWheel"
      @mousedown="startViewportPan"
    >
      <div v-if="!hasGridContent" class="river-empty-state">Lack of Data</div>

      <div
        v-else
        ref="gridScene"
        class="river-grid-scene"
        :style="sceneStyleObject"
      >
        <svg
          ref="gridBgSvg"
          class="river-bg-svg"
          :width="sceneCanvasSize.width"
          :height="sceneCanvasSize.height"
        ></svg>

        <svg
          ref="connectionSvg"
          class="river-connection-svg"
          :width="sceneCanvasSize.width"
          :height="sceneCanvasSize.height"
        ></svg>

        <div
          class="river-grid-surface"
          :style="{ width: sceneCanvasSize.width + 'px', height: sceneCanvasSize.height + 'px' }"
        >
          <div
            v-for="sh in sessionHeaderOverlays"
            :key="sh.key"
            class="session-header-overlay"
            :class="{ 'is-empty-prompt': sh.isEmptyPlaceholder }"
            :style="sh.style"
            :title="sh.isEmptyPlaceholder ? 'Click to add a question' : ''"
            @click="onSessionHeaderOverlayClick(sh)"
          >{{ sh.title }}</div>

          <button
            v-for="b in sessionAddButtonsBelow"
            :key="b.key"
            type="button"
            class="session-large-followup-btn"
            :style="b.style"
            :disabled="isSubmitting"
            title="在当前问题下方新开一行（大追问：新会话列）"
            @click.stop="openAddQuestionPrompt"
          >
            大追问
          </button>

          <!-- NOTE: 按需求隐藏中间网格的「小追问」入口与面板 -->

          <div
            v-for="header in headerCells"
            :key="header.key"
            class="grid-header-cell"
            :style="header.style"
          >
            <div class="grid-header-title">Round {{ header.roundNumber }}</div>
            <div class="grid-header-subtitle">{{ header.count }} strategy cells</div>
          </div>


          <div
            v-for="slot in gridSlotCells"
            :key="slot.slotKey"
            class="grid-slot-cell"
            :class="slotClass(slot)"
            :style="slot.style"
          ></div>

          <div
            v-for="card in strategyCards"
            :key="card.key"
            class="strategy-card"
            :class="cardClass(card)"
            :data-round="card.roundNumber"
            :data-query="card.queryIndex"
            :data-card-key="card.key"
            :style="cardStyle(card)"
            @click.stop="handleCardClick(card)"
          >
            <div v-if="card.edges.includes('top')" class="strategy-edge top"></div>
            <div v-if="card.edges.includes('right')" class="strategy-edge right"></div>
            <div v-if="card.edges.includes('bottom')" class="strategy-edge bottom"></div>
            <div v-if="card.edges.includes('left')" class="strategy-edge left"></div>

            <div
              class="strategy-card-header"
              @mousedown.stop.prevent="startCardDrag($event, card)"
            >
              <div class="strategy-card-header-top">
                <div class="strategy-card-header-left">
                  <span
                    class="strategy-type-badge"
                    :class="'is-' + strategyCardSearchBadge(card).kind"
                    :title="strategyCardSearchBadge(card).tooltip"
                  >{{ strategyCardSearchBadge(card).letter }}</span>
                  <!-- 此处只显示 title；勿改回 subtitle||title -->
                  <div class="strategy-card-subtitle-main">{{ card.title }}</div>
                </div>
                <div class="strategy-card-header-actions">
                  <button
                    type="button"
                    class="card-circle-btn card-circle-btn-danger"
                    title="删除本策略：写入 userdo.strategy_delete、grid_pos=[0,0]，同行后续列坐标左移"
                    @mousedown.stop
                    @click.stop="handleStrategyHeaderAction('D', card)"
                  >D</button>
                  <button
                    type="button"
                    class="card-circle-btn"
                    title="Continue"
                    @mousedown.stop
                    @click.stop="handleStrategyHeaderAction('C', card)"
                  >C</button>
                  <button
                    type="button"
                    class="card-circle-btn card-circle-btn-primary"
                    title="Rewrite：用编辑后的问题重新检索"
                    @mousedown.stop
                    @click.stop="handleStrategyHeaderAction('R', card)"
                  >R</button>
                </div>
              </div>

              <div class="strategy-card-header-line">
                <textarea
                  :value="getStrategyCardDraftQuery(card)"
                  class="strategy-card-query-input"
                  spellcheck="false"
                  rows="2"
                  @input="setStrategyCardDraftQuery(card, $event.target.value)"
                  @mousedown.stop
                  @click.stop
                  @keyup.enter.stop="handleStrategyHeaderAction('R', card)"
                ></textarea>
              </div>
            </div>

            <div class="strategy-card-map-wrap">
              <svg
                :ref="miniMapRefName(card.gridColKey, card.queryIndex)"
                class="strategy-mini-svg"
              ></svg>
              <button
                v-if="card.query && card.query._continue_auto_pending"
                type="button"
                class="strategy-auto-btn"
                title="Auto continue"
                @click.stop="runContinueAuto(card)"
              >auto</button>
            </div>

            <div class="strategy-card-footer strategy-card-footer--eval">
              <div class="strategy-card-footer-eval-left">
                <span
                  v-for="seg in strategyCardEvalStatSegments(card)"
                  :key="seg.action"
                  class="strategy-eval-stat strategy-eval-stat--filterable"
                  :class="{
                    'is-mini-map-filter-selected': strategyMiniMapEvalFilterIsActive(card, seg.action),
                  }"
                  role="button"
                  tabindex="0"
                  title="点击查看小地图中该评估结果的点；再点一次取消筛选"
                  @click.stop="toggleStrategyMiniMapEvalFilter(card, seg.action)"
                  @mousedown.stop
                  @keyup.enter.prevent.stop="toggleStrategyMiniMapEvalFilter(card, seg.action)"
                >
                  <span
                    class="strategy-eval-dot"
                    :style="{ background: seg.color }"
                  ></span>
                  <span>{{ seg.count }}</span>
                </span>
              </div>
              <span class="strategy-card-footer-media-right">{{
                strategyCardMediaStatsLine(card)
              }}</span>
            </div>
          </div>

          <div
            v-for="handle in columnResizeHandles"
            :key="`col-${handle.key}`"
            class="grid-resize-handle col"
            :style="columnHandleStyle(handle)"
            @mousedown.stop.prevent="startColumnResize($event, handle.key)"
          ></div>

          <div
            v-for="handle in rowResizeHandles"
            :key="`row-${handle.key}`"
            class="grid-resize-handle row"
            :style="rowHandleStyle(handle)"
            @mousedown.stop.prevent="startRowResize($event, handle.key)"
          ></div>
        </div>
      </div>

      <div
        v-if="dragState.active && dragState.hoverTarget"
        class="drag-drop-hint"
        :style="dragHintStyle"
      >
        {{ dragState.hoverTarget.mode === 'merge' ? 'release to merge' : 'release to swap positions' }}
      </div>
    </div>

    <div v-if="addQuestionDialog" class="modal add-q-modal" @click.self="cancelAddQuestionDialog">
      <div class="modal-content add-q-modal-inner">
        <div class="modal-header">
          <h2>Add a new question</h2>
          <button type="button" class="close-btn" @click="cancelAddQuestionDialog">×</button>
        </div>
        <div class="modal-body">
          <textarea
            v-model="addQuestionDraft"
            class="question-input add-q-textarea"
            rows="4"
            placeholder="Enter your new question…"
            @keydown.ctrl.enter.prevent="confirmAddQuestionDialog"
          ></textarea>
          <div class="add-q-actions">
            <button type="button" class="btn btn-submit" @click="confirmAddQuestionDialog">OK</button>
            <button type="button" class="btn" @click="cancelAddQuestionDialog">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- PlanSummary 弹窗 -->
    <div v-if="showPlanSummaryModal" class="modal" @click.self="closePlanSummaryModal">
      <div class="modal-content plan-summary-modal">
        <div class="modal-header plan-summary-modal-header">
          <h2>策略总结 - 轮次 {{ selectedPlanSummary?.roundNumber }} 查询 {{ selectedPlanSummary?.queryIndex + 1 }}</h2>
          <div class="plan-summary-header-actions">
            <button
              type="button"
              class="plan-summary-delete-btn"
              title="从当前行移除该策略（JSON 同步删除，后方策略前移）"
              :disabled="deletingStrategy"
              @click="deleteSelectedStrategy"
            >删除策略</button>
            <button type="button" @click="closePlanSummaryModal" class="close-btn">×</button>
          </div>
        </div>
        <div class="modal-body">
          <div class="plan-summary-meta">
            <div class="meta-row">
              <div class="meta-label">ParentNode</div>
              <div class="meta-value">{{ selectedPlanSummary?.parentNode ?? '-' }}</div>
            </div>
            <div class="meta-row meta-row-top">
              <div class="meta-label">Reason</div>
              <div class="meta-value">{{ selectedPlanSummary?.reason ?? '-' }}</div>
            </div>
            <div class="meta-row meta-row-top">
              <div class="meta-label">Args</div>
            </div>
            <pre class="meta-pre">{{ formatArgs(selectedPlanSummary?.args) }}</pre>
          </div>
          <div
            v-if="(selectedPlanSummary?.hydeText || '').trim()"
            class="plan-summary-hyde"
          >
            <div class="plan-summary-hyde-title">HyDE</div>
            <pre class="plan-summary-hyde-body">{{ selectedPlanSummary.hydeText }}</pre>
          </div>
          <div class="summary-content" v-html="formatSummary(selectedPlanSummary?.summary)"></div>
        </div>
      </div>
    </div>

    <!-- 数据点详情弹窗 -->
    <div v-if="showPointDetailModal" class="modal" @click.self="closePointDetailModal">
      <div class="modal-content point-detail-modal">
        <div class="modal-header">
          <h2>Data point details</h2>
          <button @click="closePointDetailModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <ItemDetail v-if="selectedPointDetail" :item="selectedPointDetail" />
          <div v-if="selectedPointContext" class="point-detail-actions-group">
            <button 
              type="button" 
              class="btn-eval btn-grow" 
              :class="{ active: currentPointEvalAction === 'GROW' }"
              @click="changePointEvalAction('GROW')"
            >GROW</button>
            <button 
              type="button" 
              class="btn-eval btn-keep" 
              :class="{ active: currentPointEvalAction === 'KEEP' }"
              @click="changePointEvalAction('KEEP')"
            >KEEP</button>
            <button 
              type="button" 
              class="btn-eval btn-prune" 
              :class="{ active: currentPointEvalAction === 'PRUNE' }"
              @click="changePointEvalAction('PRUNE')"
            >PRUNE</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 轮次总结弹窗（词云图和词频图） -->
    <div v-if="showRoundSummaryModal" class="modal" @click.self="closeRoundSummaryModal">
      <div class="modal-content round-summary-modal">
        <div class="modal-header">
          <h2>轮次 {{ selectedRoundSummary?.roundNumber }} 总结</h2>
          <button @click="closeRoundSummaryModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="summary-charts">
            <div class="chart-container">
              <h3>词频图</h3>
              <div ref="wordFreqChart" class="chart"></div>
            </div>
            <div class="chart-container">
              <h3>词云图</h3>
              <div ref="wordCloudChart" class="chart"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 全局地图框选工具栏在 LeftPanel 中渲染，由 App 转发事件并同步 map-toolbar 状态 -->
  </div>
</template>


<script>
import * as d3 from 'd3';
import * as riverGrid from '../lib/riverGridLayout';
import ragService from '../api/ragService';
import { marked } from 'marked';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import ItemDetail from './ItemDetail.vue';
import { buildInteractiveReportItemFromRag, patchRagMetadataWithMapPoint } from '../store/interactiveReportItem';

// 策略画布位置管理类
class StrategyCanvas {
  constructor(roundNumber, queryIndex, x, y, width, height) {
    this.roundNumber = roundNumber;
    this.queryIndex = queryIndex;
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    this.centerX = x + width / 2;
    this.centerY = y + height / 2;
  }
  
  getLeftEdge() {
    return { x: this.x, y: this.centerY };
  }
  
  getRightEdge() {
    return { x: this.x + this.width, y: this.centerY };
  }
  
  getTopEdge() {
    return { x: this.centerX, y: this.y };
  }
  
  getBottomEdge() {
    return { x: this.centerX, y: this.y + this.height };
  }
}

export default {
  name: 'EnhancedRiverChart',
  emits: ['map-toolbar', 'user-operations-change', 'backend-status-change'],
  props: {
    plansPerRound: {
      type: Number,
      default: 2
    },
    ragResultsPerPlan: {
      type: Number,
      default: 10
    },
    maxRounds: {
      type: Number,
      default: 3
    },
    // 全局地图嵌入的容器 id（如 left-global-map）；未传则不绘制全局地图
    globalMapMountId: {
      type: String,
      default: ''
    },
    ragCollection: {
      type: String,
      default: 'multimodal2text'
    },
    /**
     * 与左栏「跳过评估」同步：为 true 时后端不跑 Evaluator LLM（占位 KEEP），
     * 小地图按 HyDE/Rerank 浅蓝/深蓝着色；为 false 时小地图按评估分支色着色。
     */
    skipEvaluation: {
      type: Boolean,
      default: true
    },
    /** 为 true 时 start_query 走 engine_multi_agent（多路改写 + 每轨每轮单策略） */
    useMultiAgentRewriteStreams: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      /** 已完成归档的问题列（左侧已固化），每项含独立 sessionId 与 roundsData */
      completedQuestionColumns: [],
      /** 当前正在跑或刚提交的问题对应的会话 id（与后端 experiment_result.session_id 对齐） */
      activeSessionId: '',
      /** 多问题共用的批次 id（元数据）；后端 server 在 experiment_data 下固定一个 experiment_results_*.json，按 session 合并 */
      sessionBatchId: '',
      /**
       * 从后端拉取的实验 JSON 相对路径（与 selectedDataFile 一致，经 /api/experiment-file 读取）。
       * 非空时 WebSocket 会带 fork_experiment_source，后端复制为 experiment_data/<stem>_user2.json 并合并保存追问/新会话。
       */
      forkExperimentSource: '',
      /** 添加问题：输入框与插入位置（null | { afterColumnIndex: number }） */
      addQuestionDialog: null,
      addQuestionDraft: '',
      /** 小追问：在对应会话首行末列旁打开的面板 { sessionId, strategy, paramText } */
      miniFollowUpDraft: null,
      /** 策略卡片可编辑检索问题：{ [cardKey]: string } */
      strategyCardDraftQueries: {},
      /** 底栏评估色点 → 小地图仅显示该类：{ [cardKey]: 'KEEP'|'GROW'|'PRUNE'|'UNKNOWN' } */
      strategyMiniMapEvalFilter: {},
      roundsData: [],
      svgWidth: 0,
      svgHeight: 0,
      showLabels: true,
      showConnections: true,
      hidePrunePoints: false,  // 是否隐藏PRUNE节点
      selectedDataFile: '',
      experimentFiles: [],
      // 布局参数 - 重新设计更美观的布局
      strategyWidth: 400,        // 每个策略画布的宽度
      strategyHeight: 350,        // 每个策略画布的高度
      strategyMargin: 20,         // 策略之间的间距
      roundMargin: 120,           // 轮次之间的间距
      /** label 列右缘 → 第一列 Round 的额外水平间距（px）；传给 riverGrid.buildGridMetrics */
      labelToFirstRoundGapExtra: 28,
      roundHeaderHeight: 50,      // 轮次标题区域高度
      // 地图相关
      mapPoints: [],
      idToPointMap: {},          // ID到点的映射（支持多种ID格式）
      globalXExtent: null,
      globalYExtent: null,
      // 连线相关
      connectionGroup: null,
      containerGroup: null,       // 存储容器组引用
      strategyCanvases: {},       // 存储所有策略画布位置
      strategyOffsets: {},        // 存储策略卡片的拖拽偏移量 { roundNumber: { queryIndex: { x: 0, y: 0 } } }
      draggingStrategy: null,     // 当前正在拖拽的策略卡片 { roundNumber, queryIndex }，用于防止点击事件
      /** 指针拖入 Interactive Report 后抑制紧随其后的 click，避免重复打开详情 */
      suppressNextRagDotClick: false,
      // 弹窗相关
      showPlanSummaryModal: false,
      selectedPlanSummary: null,
      deletingStrategy: false,
      showRoundSummaryModal: false,
      selectedRoundSummary: null,
      showPointDetailModal: false,
      selectedPointDetail: null,
      selectedPointContext: null,
      pendingPointOperations: [],
      // 用户输入相关
      userQuestion: '',
      isSubmitting: false,
      // 新增的轮次（用于追问功能）
      newRounds: {},
      // 全局地图相关
      globalMapPoints: [],
      clusterKeywords: [],
      globalMapXScale: null,
      globalMapYScale: null,
      // WebSocket 与后端实时联调
      ws: null,
      wsConnected: false,
      lastSummary: null,
      // 逐步渲染状态：存储 plan、retrieval、evaluation 的状态
      planStates: {}, // { plan_id: { round_number, orchestrator_plan, node_ids: [], evaluated_nodes: {} } }
      incrementalRoundsData: [], // 逐步构建的轮次数据
      // 全局地图高亮相关
      highlightedPlanPoints: {}, // { [nodeId]: { branch_action: 'GROW'|'KEEP'|'PRUNE', ... } } 存储当前高亮的点
      // 点击聚类文本标签：只保留该标签，并高亮该聚类内的点（最近质心归属）
      globalMapSelectedClusterId: null,
      // 存储 experiment_result 以便获取 plansummary
      experimentResult: null, // 存储完整的 experiment_result 数据
      // spreadsheet-like layout state
      showLegacyConnections: false,
      persistZoomTransform: { x: 0, y: 0, k: 1 },
      focusedStrategyKey: null,
      hoveredStrategyKey: null,
      useSpreadsheetLayout: true,
      gridState: riverGrid.createDefaultGridState(),
      gridMetrics: null,
      dragState: {
        active: false,
        cardKey: null,
        sessionId: null,
        roundNumber: null,
        queryIndex: null,
        startClientX: 0,
        startClientY: 0,
        dx: 0,
        dy: 0,
        hoverTarget: null,
        moved: false
      },
      panState: {
        active: false,
        startClientX: 0,
        startClientY: 0,
        originX: 0,
        originY: 0,
        moved: false
      },
      // 小地图框选 → RAG 仅检索这些 chunk id（与 embedding 点 id 一致）
      mapBoxSelectMode: false,
      mapBoxDragging: false,
      mapBoxDragRect: null,
      mapRagPendingIds: [],
      mapRagFilterIds: [],
      /** 与 embedding 二维坐标一致：[[xmin,ymin],[xmax,ymax]]，供后端 experiment JSON 记录 */
      mapRagRect2d: null,
      globalMapZoomTransform: null,
      /** 全局地图 contentGroup（含 zoom transform），用于 d3.pointer 与圆点 cx/cy 同一坐标系 */
      globalMapContentGroupNode: null
    };
  },
  watch: {
    ragCollection(newVal) {
      console.log('ragCollection changed to', newVal);
      this.loadMapData();
      this.loadGlobalMapData();
    },
    mapBoxSelectMode() {
      this.$nextTick(() => this.drawGlobalMap());
    },
    skipEvaluation() {
      if (this.roundsData.length > 0 || this.completedQuestionColumns.length > 0) {
        this.$nextTick(() => this.drawRiverChart());
      }
    }
  },
  components: {
    ItemDetail
  },
  computed: {
    currentPointEvalAction() {
      const ctx = this.selectedPointContext;
      const resultId = this.selectedPointDetail?.id || ctx?.rag?.retrieval_result?.id;
      if (!ctx || !resultId) return 'UNKNOWN';

      const pending = this.pendingPointOperations.find(p => p.target_evidence_id === resultId);
      if (pending) return pending.after;

      return ctx.rag?.evaluation?.branch_action || 'UNKNOWN';
    },
    totalWidth() {
      const maxRound = Math.max(...this.roundsData.map(r => r.round_number), 0);
      return (maxRound + 1) * (this.strategyWidth + this.roundMargin) + this.roundMargin;
    },
    showEmptySessionChrome() {
      return (
        this.completedQuestionColumns.length === 0 &&
        (!this.roundsData || this.roundsData.length === 0) &&
        !this.isSubmitting
      );
    },
    hasGridContent() {
      if (this.showEmptySessionChrome) return !!this.gridMetrics;
      return !!(
        this.gridMetrics &&
        ((this.roundsData && this.roundsData.length > 0) || this.completedQuestionColumns.length > 0)
      );
    },
    sceneSize() {
      return {
        width: this.gridMetrics?.totalWidth || Math.max(this.svgWidth || 0, 1200),
        height: this.gridMetrics?.totalHeight || Math.max(this.svgHeight || 0, 800)
      };
    },
    sceneCanvasSize() {
      const extraW = Math.max(this.svgWidth || 0, 1200);
      const extraH = Math.max(this.svgHeight || 0, 900);
      return {
        width: Math.max(this.sceneSize.width + extraW, (this.svgWidth || 1200) * 2.4),
        height: Math.max(this.sceneSize.height + extraH, (this.svgHeight || 800) * 2.2)
      };
    },
    sceneStyleObject() {
      const t = this.persistZoomTransform || { x: 0, y: 0, k: 1 };
      return {
        transform: `translate(${t.x}px, ${t.y}px) scale(${t.k})`,
        transformOrigin: '0 0'
      };
    },
    headerCells() {
      if (!this.gridMetrics) return [];
      return this.getAllRounds().map((round) => {
        const gck = round.__gridColKey || riverGrid.gridColumnKey(round);
        const rect = riverGrid.getRoundHeaderRect(this.gridMetrics, round.round_number, gck);
        return {
          key: `header-${gck}`,
          roundNumber: round.round_number,
          sessionId: round._sessionId,
          gridColKey: gck,
          count: round.query_results?.length || 0,
          style: rect ? {
            left: `${rect.x}px`,
            top: `${rect.y}px`,
            width: `${rect.width}px`,
            height: `${rect.height}px`
          } : {}
        };
      }).filter(Boolean);
    },
    /** 每个问题会话一条合并表头（横跨该问题下所有 Round 列） */
    sessionHeaderOverlays() {
      if (!this.gridMetrics) return [];
      const rounds = this.getAllRounds();
      if (!rounds.length) return [];
      const bySid = new Map();
      rounds.forEach((r) => {
        const sid = r._sessionId || 'default';
        if (!bySid.has(sid)) bySid.set(sid, []);
        bySid.get(sid).push(r);
      });
      const out = [];
      bySid.forEach((list, sid) => {
        list.sort((a, b) => a.round_number - b.round_number);
        let minX = Infinity;
        let maxX = -Infinity;
        let title = '';
        list.forEach((r) => {
          const gck = r.__gridColKey || riverGrid.gridColumnKey(r);
          const rect = riverGrid.getRoundHeaderRect(this.gridMetrics, r.round_number, gck);
          if (!rect) return;
          minX = Math.min(minX, rect.x);
          maxX = Math.max(maxX, rect.x + rect.width);
        });
        if (sid === 'empty') {
          title = '+ Add question';
          const strip = this.gridMetrics.strips && this.gridMetrics.strips[0];
          const rowYs = strip && strip.rowYs;
          const row0 = rowYs && rowYs[0];
          const lastR = rowYs && rowYs.length ? rowYs[rowYs.length - 1] : null;
          const label = this.gridMetrics.colPositions.label;
          const firstR = list[0];
          const gck0 = firstR.__gridColKey || riverGrid.gridColumnKey(firstR);
          const firstCol = this.gridMetrics.colPositions[`round-${gck0}`];
          if (!row0 || !lastR || !label || !firstCol) return;
          const contentTop = row0.y + riverGrid.STRATEGY_CELL_PAD_Y;
          const contentH =
            lastR.y + lastR.height - riverGrid.STRATEGY_CELL_PAD_Y - contentTop;
          out.push({
            key: `sess-head-${sid}`,
            sessionId: sid,
            title,
            isEmptyPlaceholder: true,
            /** 与左侧 Question 条同列对齐时，下层条不再重复渲染 Question/题干 */
            hidesLeftStripDuplicate: true,
            style: {
              left: `${label.x}px`,
              top: `${contentTop}px`,
              width: `${Math.max(
                72,
                firstCol.x - label.x - riverGrid.SESSION_HEADER_TO_ROUND_GAP
              )}px`,
              height: `${Math.max(0, contentH)}px`
            }
          });
          return;
        }
        const col = this.completedQuestionColumns.find((c) => c.sessionId === sid);
        if (col && col.rootGoal) title = col.rootGoal;
        if (sid === this.activeSessionId) {
          title =
            (this.experimentResult && this.experimentResult.root_goal) ||
            title ||
            (this.userQuestion && this.userQuestion.trim()) ||
            'Current question';
        }
        if (!title) title = 'Question';
        if (minX === Infinity) return;
        const strip = this.gridMetrics.strips && this.gridMetrics.strips.find((s) => s.sessionId === sid);
        const rowYs = strip && strip.rowYs;
        const row0 = rowYs && rowYs[0];
        const lastRow = rowYs && rowYs.length ? rowYs[rowYs.length - 1] : null;
        const label = this.gridMetrics.colPositions.label;
        if (!row0 || !lastRow || !label) return;
        const contentTop = row0.y + riverGrid.STRATEGY_CELL_PAD_Y;
        const contentH =
          lastRow.y + lastRow.height - riverGrid.STRATEGY_CELL_PAD_Y - contentTop;
        const stripMaxW = 240;
        const gap = riverGrid.SESSION_HEADER_TO_ROUND_GAP;
        const rightEdge = minX - gap;
        const left = Math.max(label.x, rightEdge - stripMaxW);
        const stripW = Math.max(72, rightEdge - left);
        const hidesLeftStripDuplicate = left <= label.x + 0.5;
        out.push({
          key: `sess-head-${sid}`,
          sessionId: sid,
          title,
          isEmptyPlaceholder: false,
          hidesLeftStripDuplicate,
          style: {
            left: `${left}px`,
            top: `${contentTop}px`,
            width: `${stripW}px`,
            height: `${Math.max(0, contentH)}px`
          }
        });
      });
      return out;
    },
    /** 整张表最下方居中一个「大追问」：不在两题之间重复出现 */
    sessionAddButtonsBelow() {
      if (!this.gridMetrics) return [];
      const m = this.gridMetrics;
      const rounds = this.getAllRounds().filter((r) => r._sessionId && r._sessionId !== 'empty');
      if (!rounds.length) return [];
      const strips = m.strips;
      if (!strips || !strips.length) return [];
      const lastStrip = strips[strips.length - 1];
      const rows = (lastStrip && lastStrip.rowYs) || [];
      const rowLast = rows.length ? rows[rows.length - 1] : null;
      if (!rowLast) return [];
      const bottomY = rowLast.y + rowLast.height + 10;
      let minX = Infinity;
      let maxX = -Infinity;
      rounds.forEach((r) => {
        const gck = r.__gridColKey || riverGrid.gridColumnKey(r);
        const rect = riverGrid.getRoundHeaderRect(this.gridMetrics, r.round_number, gck);
        if (!rect) return;
        minX = Math.min(minX, rect.x);
        maxX = Math.max(maxX, rect.x + rect.width);
      });
      if (minX === Infinity) return [];
      const btnW = 88;
      const btnH = 36;
      const cx = (minX + maxX) / 2 - btnW / 2;
      return [
        {
          key: 'add-below-global',
          sessionId: '__all__',
          style: {
            left: `${cx}px`,
            top: `${bottomY}px`,
            width: `${btnW}px`,
            height: `${btnH}px`
          }
        }
      ];
    },
    /** 每个非空会话：首行最后一列策略格右上外侧「小追问」入口 */
    miniFollowUpTriggerButtons() {
      if (!this.gridMetrics || this.showEmptySessionChrome) return [];
      const sm = this.strategyMargin != null ? this.strategyMargin : 10;
      const btnW = 52;
      const btnH = 24;
      const out = [];
      (this.gridMetrics.strips || []).forEach((strip) => {
        const sid = strip.sessionId;
        if (!sid || sid === 'empty') return;
        const sessionRounds = this.getAllRounds().filter((r) => r._sessionId === sid);
        if (!sessionRounds.length) return;
        const lastRound = sessionRounds.reduce((a, b) =>
          Number(a.round_number) > Number(b.round_number) ? a : b
        );
        const gck = lastRound.__gridColKey || riverGrid.gridColumnKey(lastRound);
        const rect = riverGrid.getStrategyCellRect(
          this,
          this.gridMetrics,
          lastRound.round_number,
          0,
          gck
        );
        if (!rect) return;
        const left = rect.x + rect.width + sm;
        const top = Math.max((strip.stripTop || 0) + 2, rect.y - btnH - 4);
        out.push({
          key: `mini-fu-${sid}`,
          sessionId: sid,
          style: {
            left: `${left}px`,
            top: `${top}px`,
            width: `${btnW}px`,
            height: `${btnH}px`
          }
        });
      });
      return out;
    },
    miniFollowUpPanelLayout() {
      const d = this.miniFollowUpDraft;
      if (!d || !this.gridMetrics) return null;
      const sid = d.sessionId;
      const sessionRounds = this.getAllRounds().filter((r) => r._sessionId === sid);
      if (!sessionRounds.length) return null;
      const lastRound = sessionRounds.reduce((a, b) =>
        Number(a.round_number) > Number(b.round_number) ? a : b
      );
      const gck = lastRound.__gridColKey || riverGrid.gridColumnKey(lastRound);
      const rect = riverGrid.getStrategyCellRect(
        this,
        this.gridMetrics,
        lastRound.round_number,
        0,
        gck
      );
      if (!rect) return null;
      const sm = this.strategyMargin != null ? this.strategyMargin : 10;
      const w = Math.min(340, Math.max(240, rect.width));
      return {
        style: {
          left: `${rect.x + rect.width + sm}px`,
          top: `${rect.y}px`,
          width: `${w}px`
        }
      };
    },
    miniFollowUpParamPlaceholder() {
      const d = this.miniFollowUpDraft;
      if (!d) return '';
      if (d.strategy === 'metadata') {
        return '例：paper_023 或 关键词1, 关键词2';
      }
      if (d.strategy === 'exact') {
        return '精确匹配短语（宜短）';
      }
      return '用自然语言描述检索意图';
    },
    /** 每个 session 一条左侧长条：单块铺满该条带全部策略行（与右侧 Row1–RowN 总高度一致） */
    rowLabelStrips() {
      if (!this.gridMetrics || !this.gridMetrics.strips) return [];
      const out = [];
      this.gridMetrics.strips.forEach((strip, si) => {
        const merged = riverGrid.getMergedRowLabelStripRect(this.gridMetrics, si);
        if (!merged) return;
        out.push({
          key: `row-strip-${strip.sessionId}`,
          sessionId: strip.sessionId,
          stripIndex: si,
          style: {
            left: `${merged.x}px`,
            top: `${merged.y}px`,
            width: `${merged.width}px`,
            height: `${merged.height}px`
          }
        });
      });
      return out;
    },
    strategyCards() {
      if (!this.gridMetrics) return [];
      /** 单条策略：语义检索优先，否则展示 metadata 的 paper_id 等 */
      const pickStrategySearchDisplay = (q) => {
        const a = q?.orchestrator_plan?.args;
        if (!a || typeof a !== 'object') return '';
        const sem =
          a.query_intent ??
          a.query ??
          a.user_question ??
          a.userQuery ??
          a.search_query;
        if (sem != null && String(sem).trim()) return String(sem).trim();
        if (a.paper_id != null && String(a.paper_id).trim()) {
          return String(a.paper_id).trim();
        }
        return '';
      };
      /** 合并后：主策略 + mergedSourcesData 里每条来源各一行 */
      const collectSearchLines = (query) => {
        const lines = [];
        const add = (s) => {
          const t = String(s || '').trim();
          if (t) lines.push(t);
        };
        add(pickStrategySearchDisplay(query));
        const merged = query.mergedSourcesData || query._merged_sources_data;
        if (merged && merged.length) {
          merged.forEach((src) => {
            if (src && src.queryData) add(pickStrategySearchDisplay(src.queryData));
          });
        }
        return lines;
      };
      const cards = [];
      const allRounds = this.getAllRounds();
      allRounds.forEach((round) => {
        const gck = round.__gridColKey || riverGrid.gridColumnKey(round);
        (round.query_results || []).forEach((query, queryIndex) => {
          if (riverGrid.isStrategySlotTombstone(query)) return;
          const rowSlot0 = riverGrid.strategyVisualRowSlot0(query, queryIndex);
          if (rowSlot0 < 0) return;
          const rect = riverGrid.getStrategyCellRect(this, this.gridMetrics, round.round_number, rowSlot0, gck);
          if (!rect) return;
          const key = this.getStrategyKey(round, queryIndex);
          cards.push({
            key,
            gridColKey: gck,
            sessionId: round._sessionId,
            roundNumber: round.round_number,
            queryIndex,
            query,
            rect,
            title: `R${queryIndex + 1}.${round.round_number}`,
            searchLines: collectSearchLines(query),
            subtitle: this.strategyCardSubtitleText(query, round.round_number),
            edges: this.getCardHighlightEdges(round, queryIndex),
            planSummaryPayload: {
              sessionId: round._sessionId,
              roundNumber: round.round_number,
              queryIndex,
              parentNode: query?.orchestrator_plan?.ParentNode ?? query?.orchestrator_plan?.parentNode ?? null,
              reason: query?.orchestrator_plan?.reason ?? '',
              args: query?.orchestrator_plan?.args ?? null,
              summary: query?.orchestrator_plan?.plansummary ?? '',
              hydeText:
                query?.orchestrator_plan?.hyde_hypothetical_paragraph_full_text ??
                query?.orchestrator_plan?.hydeHypotheticalParagraphFullText ??
                ''
            }
          });
        });
      });
      return cards;
    },
    gridSlotCells() {
      if (!this.gridMetrics) return [];
      const allRounds = this.getAllRounds();
      const byColKey = new Map(allRounds.map((r) => [r.__gridColKey || riverGrid.gridColumnKey(r), r]));
      const cells = [];
      this.gridMetrics.roundNumbers.forEach((roundKey) => {
        const round = byColKey.get(roundKey);
        if (!round) return;
        const gck = round.__gridColKey || riverGrid.gridColumnKey(round);
        const colPos = this.gridMetrics.colPositions[`round-${gck}`];
        const si = colPos && colPos.stripIndex != null ? colPos.stripIndex : 0;
        const stripForRound =
          this.gridMetrics.strips && this.gridMetrics.strips[si]
            ? this.gridMetrics.strips[si]
            : null;
        const nRows =
          stripForRound && stripForRound.rowYs && stripForRound.rowYs.length
            ? stripForRound.rowYs.length
            : this.gridMetrics.maxQueryCount;
        for (let queryIndex = 0; queryIndex < nRows; queryIndex += 1) {
          const rect = riverGrid.getStrategyCellRect(this, this.gridMetrics, round.round_number, queryIndex, gck);
          if (!rect) continue;
          const occupied = (round.query_results || []).some((q, idx) => {
            if (!q || riverGrid.isStrategySlotTombstone(q)) return false;
            return riverGrid.strategyVisualRowSlot0(q, idx) === queryIndex;
          });
          cells.push({
            slotKey: `slot-${roundKey}-${queryIndex}`,
            roundNumber: round.round_number,
            gridColKey: gck,
            sessionId: round._sessionId,
            queryIndex,
            occupied,
            sceneRect: rect,
            style: {
              left: `${rect.x}px`,
              top: `${rect.y}px`,
              width: `${rect.width}px`,
              height: `${rect.height}px`
            }
          });
        }
      });
      return cells;
    },
    columnResizeHandles() {
      return this.gridMetrics ? riverGrid.getColumnResizeHandles(this.gridMetrics) : [];
    },
    rowResizeHandles() {
      return this.gridMetrics ? riverGrid.getRowResizeHandles(this.gridMetrics) : [];
    },
    dragHintStyle() {
      const target = this.dragState?.hoverTarget;
      if (!target?.rect) return {};
      return {
        left: `${target.rect.left + target.rect.width / 2}px`,
        top: `${target.rect.top - 14}px`
      };
    }
  },
  methods: {
    emitUserOperationsChange() {
      const rowsMap = new Map(); // key -> row
      const layoutPoints = this.getCanonicalLayoutPoints() || [];
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      layoutPoints.forEach(pt => {
        if (pt.x < minX) minX = pt.x;
        if (pt.x > maxX) maxX = pt.x;
        if (pt.y < minY) minY = pt.y;
        if (pt.y > maxY) maxY = pt.y;
      });

      const getOrCreateRow = (sessionId, roundNumber, queryIndex, toolName) => {
        const key = `${sessionId || 'default'}-${roundNumber}-${queryIndex}`;
        if (!rowsMap.has(key)) {
          rowsMap.set(key, {
            key,
            sessionId: sessionId || '',
            roundNumber: Number(roundNumber),
            queryIndex,
            label: `R ${roundNumber}.${queryIndex + 1}`,
            toolName: toolName || '',
            operationsMap: new Map(), // resultId -> op
            hasPending: false,
            thumbnailPointsMap: new Map(), // resultId -> {x, y, action}
          });
        }
        return rowsMap.get(key);
      };

      const pushFromRounds = (rounds, sessionId = '') => {
        (rounds || []).forEach((round) => {
          if (!round || round.round_number === undefined) return;
          (round.query_results || []).forEach((query, queryIndex) => {
            const toolName = query?.orchestrator_plan?.tool_name || '';
            const userdo = query?.orchestrator_plan?.userdo || {};
            const deletes = userdo.delete || [];
            const points = userdo.point || [];
            
            const row = getOrCreateRow(sessionId, round.round_number, queryIndex, toolName);

            if (query && Array.isArray(query.rag_results)) {
              query.rag_results.forEach(rag => {
                const pt = this.findLayoutPointForRetrieval(layoutPoints, rag.retrieval_result);
                if (pt) {
                  const resultId = rag.retrieval_result.id;
                  const action = rag.evaluation?.branch_action || 'UNKNOWN';
                  const px = (maxX > minX) ? ((pt.x - minX) / (maxX - minX)) * 100 : 50;
                  const py = (maxY > minY) ? (100 - ((pt.y - minY) / (maxY - minY)) * 100) : 50;
                  const ctx = {
                    sessionId,
                    roundNumber: round.round_number,
                    queryIndex,
                    query,
                    rag
                  };
                  row.thumbnailPointsMap.set(resultId, {
                    x: px,
                    y: py,
                    action: action,
                    ctx: ctx
                  });
                }
              });
            }

            deletes.forEach(op => {
              if (op?.target_evidence_id) {
                row.operationsMap.set(op.target_evidence_id, {
                  type: 'delete',
                  action: 'PRUNE',
                  targetEvidenceId: op.target_evidence_id,
                  timestamp: op.timestamp || '',
                });
              }
            });

            points.forEach(op => {
              if (op?.target_evidence_id) {
                row.operationsMap.set(op.target_evidence_id, {
                  type: 'point',
                  action: op.after || 'UNKNOWN',
                  targetEvidenceId: op.target_evidence_id,
                  timestamp: op.timestamp || '',
                });
              }
            });
          });
        });
      };

      (this.completedQuestionColumns || []).forEach((col) => {
        pushFromRounds(col.roundsData || [], col.sessionId || '');
      });
      pushFromRounds(this.roundsData || [], this.activeSessionId || 'default');

      const er = this.experimentResult;
      if (er && Array.isArray(er.iterations)) {
        pushFromRounds(er.iterations || [], er.session_id || this.activeSessionId || 'experiment');
      }

      this.pendingPointOperations.forEach(pending => {
        const row = getOrCreateRow(pending.sessionId, pending.roundNumber, pending.ctx?.queryIndex || 0, pending.planTool);
        row.hasPending = true;
        
        row.operationsMap.set(pending.target_evidence_id, {
          type: 'point',
          action: pending.after,
          targetEvidenceId: pending.target_evidence_id,
          timestamp: pending.timestamp,
        });

        if (row.thumbnailPointsMap.has(pending.target_evidence_id)) {
           row.thumbnailPointsMap.get(pending.target_evidence_id).action = pending.after;
        }
      });

      const finalRows = [];
      for (const row of rowsMap.values()) {
        if (row.operationsMap.size === 0 && !row.hasPending) continue;
        
        const operations = Array.from(row.operationsMap.values()).map((op, idx) => ({
          key: `${row.key}-op-${idx}`,
          type: op.type,
          action: op.action,
          targetEvidenceId: op.targetEvidenceId,
          timestamp: op.timestamp,
        }));
        
        const thumbnailPoints = Array.from(row.thumbnailPointsMap.values());

        finalRows.push({
          ...row,
          operations,
          thumbnailPoints
        });
      }

      finalRows.sort((a, b) => {
        if (String(a.sessionId) !== String(b.sessionId)) {
          return String(a.sessionId).localeCompare(String(b.sessionId));
        }
        if (a.roundNumber !== b.roundNumber) return a.roundNumber - b.roundNumber;
        return a.queryIndex - b.queryIndex;
      });

      this.$emit('user-operations-change', finalRows);
    },

    /**
     * 左侧 Question 区：与上方 session 表头同源，展示该会话完整题干（含大追问后归档到 completed 的 rootGoal）。
     */
    sessionQuestionText(sessionId) {
      if (!sessionId || sessionId === 'empty') return 'Click to add a question';
      const col = this.completedQuestionColumns.find((c) => c.sessionId === sessionId);
      let t = '';
      if (col && col.rootGoal) t = String(col.rootGoal).trim();
      if (sessionId === this.activeSessionId) {
        t =
          (this.experimentResult && this.experimentResult.root_goal) ||
          t ||
          (this.userQuestion && String(this.userQuestion).trim()) ||
          '';
      }
      return t || 'Question';
    },
    /** 会话标题 overlay 从 label 列左缘起铺时，与左侧 Question 条叠层，隐藏条内重复文案 */
    overlayCoversLeftQuestionStrip(sessionId) {
      const sh = (this.sessionHeaderOverlays || []).find((x) => x.sessionId === sessionId);
      return !!(sh && sh.hidesLeftStripDuplicate);
    },
    // LeftPanel 控制用：切换实验文件
    setSelectedDataFile(file) {
      if (!file) return;
      this.selectedDataFile = String(file);
    },
    /**
     * 与 /api/experiment-files 返回的相对路径一致。
     * 使用 GET /api/experiment-file?path=…（与 fork 同源解析），避免仅配置了 /api 代理、未代理 /experiment-data 时出现 404。
     */
    experimentDataFetchUrl(relPath) {
      const p = String(relPath || '')
        .trim()
        .replace(/\\/g, '/');
      if (!p || p.includes('..')) return '';
      return `/api/experiment-file?path=${encodeURIComponent(p)}`;
    },

    async loadExperimentFileList() {
      try {
        const resp = await fetch('/api/experiment-files');
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        const files = Array.isArray(data?.files) ? data.files : [];
        const filtered = files.filter(f => typeof f === 'string' && /^experiment.*\.json$/i.test(f));
        if (filtered.length > 0) {
          this.experimentFiles = filtered;
          // 默认选择最新的（接口已倒序）；如果当前 selected 不在列表中则切换到最新
          if (!this.experimentFiles.includes(this.selectedDataFile)) {
            this.selectedDataFile = this.experimentFiles[0];
          }
        } else {
          // 保底：至少让下拉框里有一个当前值
          this.experimentFiles = this.selectedDataFile ? [this.selectedDataFile] : [];
        }
      } catch (e) {
        console.warn('加载 experiment 文件列表失败，使用默认选项。', e);
        this.experimentFiles = this.selectedDataFile ? [this.selectedDataFile] : [];
      }
    },

    formatExperimentLabel(path) {
      if (!path) return '';
      const name = String(path).split('/').pop() || String(path);
      const m = name.match(/(\\d{8})_(\\d{6})/);
      if (m) return `${name} (${m[1]} ${m[2]})`;
      return name;
    },

    getWsUrl() {
      // 始终直接连接后端 WebSocket（不使用代理，避免代理问题）
      // 开发和生产环境都直接连接后端
      const url = 'ws://127.0.0.1:8000/ws/rag-tree';
      console.log('[WS] 使用直接连接（绕过代理）:', url);
      return url;
    },
    connectWebSocket() {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        console.log('[WS] 已存在连接，跳过');
        this.emitBackendStatus();
        return;
      }
      const url = this.getWsUrl();
      console.log('[WS] 正在连接后端:', url);
      try {
        this.ws = new WebSocket(url);
        this.ws.onopen = () => {
          this.wsConnected = true;
          this.emitBackendStatus();
          console.log('[WS] ✅ 连接成功:', url);
        };
        this.ws.onclose = (event) => {
          this.wsConnected = false;
          this.emitBackendStatus();
          console.log('[WS] ❌ 连接关闭:', event.code, event.reason);
        };
        this.ws.onerror = (e) => {
          this.wsConnected = false;
          this.emitBackendStatus();
          console.error('[WS] ❌ 连接错误:', e);
          console.error('[WS] 尝试连接的URL:', url);
        };
        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('[WS] 收到消息:', data.type || 'graph');
            
            // 处理总结消息（整个实验的总结，不是单个 plan 的 plansummary）
            // 注意：summary 消息是整个实验的总结，不应该触发 plansummary 弹窗
            // plansummary 应该通过 experiment_result 消息传递，并在用户点击小矩形按钮时显示
            if (data.type === 'summary') {
              this.lastSummary = data.content;
              // 不再自动显示 plansummary 弹窗，因为这是整个实验的总结
              // 如果需要显示整个实验的总结，可以使用其他方式（如轮次总结弹窗）
              console.log('[WS] 收到整个实验的总结，不自动显示 plansummary 弹窗');
              return;
            }
            
            // 处理策略计划创建（第一步：画空框）
            if (data.type === 'plan_created') {
              this.handlePlanCreated(data.data);
              return;
            }
            
            // 处理检索完成（第二步：画灰色点）
            if (data.type === 'retrieval_complete') {
              this.handleRetrievalComplete(data.plan_id, data.node_ids);
              return;
            }
            
            // 处理评估完成（第三步：给点上色）
            if (data.type === 'evaluation_complete') {
              this.handleEvaluationComplete(data.node_id, data.evaluation);
              return;
            }
            
            // 处理 experiment_result 更新（包含 plansummary）
            if (data.type === 'experiment_result') {
              if (data.session_id && this.activeSessionId && data.session_id !== this.activeSessionId) {
                return;
              }
              if (data.follow_up && this.experimentResult && Array.isArray(this.experimentResult.iterations) && data.data) {
                this.experimentResult = this.mergeExperimentResultFromFollowUp(this.experimentResult, data.data);
              } else {
                this.experimentResult = data.data;
              }
              console.log('[WS] 收到 experiment_result，包含 plansummary');
              this.syncPlanSummariesFromExperimentResult();
              this.syncInteractiveReportFromHypothesis(this.experimentResult);
              if (this.roundsData.length > 0 || this.completedQuestionColumns.length > 0) {
                this.$nextTick(() => this.drawRiverChart());
              }
              return;
            }
            
            // 兜底：完整 graph 更新（兼容旧逻辑，也用于逐步渲染时获取节点数据）
            if (data.root_goal != null && data.nodes != null) {
              const gsid = (data.session_id || '').trim();
              const col =
                gsid && (this.completedQuestionColumns || []).find((c) => c.sessionId === gsid);
              const rounds = this.graphToRoundsData(data);
              const followMerge = !!data.follow_up;

              if (followMerge && col && gsid) {
                const baseCol = col.roundsData || [];
                const merged =
                  baseCol && baseCol.length > 0
                    ? this.mergeRoundsDataFromFollowUp(baseCol, rounds)
                    : rounds;
                col.roundsData = merged;
                this.syncPlanStatesWithGraph(data);
                this.syncPlanSummariesFromExperimentResult();
                this.syncInteractiveReportFromHypothesis(this.experimentResult);
                this.incrementalRoundsData = JSON.parse(
                  JSON.stringify(this.getActiveSessionBaseRounds())
                );
                this.$nextTick(() => this.drawRiverChart());
                return;
              }

              if (gsid && this.activeSessionId && gsid !== this.activeSessionId && !col) {
                return;
              }
              let nextRounds = rounds;
              // 追问单独 runtime 的图谱只有本轮新证据，必须与本地已有 rounds 合并（含从文件加载的多会话列）
              const baseRounds = this.getActiveSessionBaseRounds();
              if (data.follow_up && baseRounds && baseRounds.length > 0) {
                nextRounds = this.mergeRoundsDataFromFollowUp(baseRounds, rounds);
              }
              // 如果使用逐步渲染，需要合并 planStates 中的状态
              if (Object.keys(this.planStates).length > 0) {
                // 逐步渲染模式：保留 planStates，更新活跃会话轮次
                this.setActiveSessionRounds(nextRounds);
                // 确保 planStates 中的节点信息与 graph 同步
                this.syncPlanStatesWithGraph(data);
              } else {
                // 完整更新模式
                this.setActiveSessionRounds(nextRounds);
              }
              this.syncPlanSummariesFromExperimentResult();
              this.syncInteractiveReportFromHypothesis(this.experimentResult);
              this.incrementalRoundsData = JSON.parse(JSON.stringify(nextRounds));
              this.$nextTick(() => this.drawRiverChart());
            }
          } catch (e) {
            console.error('[WS] 解析消息失败', e);
          }
        };
      } catch (e) {
        this.wsConnected = false;
        this.emitBackendStatus();
        console.error('[WS] 连接失败', e);
      }
    },

    emitBackendStatus() {
      this.$emit('backend-status-change', {
        connected: !!this.wsConnected,
      });
    },
    _ingestPlanCreatedIntoRoundsArray(roundsArray, planData) {
      const { round_number, plan_id, orchestrator_plan } = planData;
      const rewriteMode = !!planData.rewrite_mode;
      const rewriteIndex =
        planData.rewrite_target_query_index != null
          ? Number(planData.rewrite_target_query_index)
          : null;
      this.planStates[plan_id] = {
        round_number,
        orchestrator_plan,
        node_ids: [],
        evaluated_nodes: {}
      };
      let round = roundsArray.find((r) => r.round_number === round_number);
      if (!round) {
        round = { round_number, query_results: [] };
        roundsArray.push(round);
        roundsArray.sort((a, b) => a.round_number - b.round_number);
      }
      if (rewriteMode && rewriteIndex != null && rewriteIndex >= 0) {
        while (round.query_results.length <= rewriteIndex) {
          round.query_results.push({ orchestrator_plan: null, rag_results: [] });
        }
        round.query_results.splice(rewriteIndex, 1, {
          orchestrator_plan,
          rag_results: []
        });
        return;
      }
      round.query_results.push({
        orchestrator_plan,
        rag_results: []
      });
    },
    handlePlanCreated(planData) {
      const sid = (planData.session_id || '').trim();
      const col =
        sid && (this.completedQuestionColumns || []).find((c) => c.sessionId === sid);
      const useColumn =
        col &&
        sid &&
        (sid !== this.activeSessionId ||
          !this.roundsData ||
          this.roundsData.length === 0);

      if (useColumn) {
        this._ingestPlanCreatedIntoRoundsArray(col.roundsData, planData);
        col.roundsData = [...col.roundsData];
        this.$nextTick(() => this.drawRiverChart());
        console.log('[前端] 策略框已创建(归档列):', planData.plan_id);
        return;
      }

      if (sid && this.activeSessionId && sid !== this.activeSessionId && !col) {
        console.warn('[前端] plan_created 忽略未知 session', sid);
        return;
      }

      this._ingestPlanCreatedIntoRoundsArray(this.incrementalRoundsData, planData);
      this.roundsData = [...this.incrementalRoundsData];
      this.$nextTick(() => this.drawRiverChart());
      console.log('[前端] 策略框已创建:', planData.plan_id);
    },
    
    async handleRetrievalComplete(planId, nodeIds) {
      // 第二步：检索完成，添加灰色点（未评估状态）
      const planState = this.planStates[planId];
      if (!planState) {
        console.warn('[前端] 未找到 plan_id:', planId);
        return;
      }
      
      // 需要从 graph 中获取节点数据（如果后端同时发送了 graph）
      // 或者等待后端发送完整的 graph 更新
      // 暂时先标记这些节点为待评估状态
      planState.node_ids.push(...nodeIds);
      
      // 从当前 graph 或等待下一次 graph 更新来获取节点详情
      // 这里我们先更新状态，等待 graph 更新时再渲染点
      console.log('[前端] 检索完成，节点ID:', nodeIds);
      
      // 如果地图数据已加载，可以立即渲染灰色点
      if (this.mapPoints.length > 0) {
        await this.updateRoundsDataWithNodes();
      }
    },
    
    async handleEvaluationComplete(nodeId, evaluation) {
      // 第三步：评估完成，给点上色
      // 找到包含该节点的 plan
      let targetPlanId = null;
      for (const [planId, state] of Object.entries(this.planStates)) {
        if (state.node_ids.includes(nodeId)) {
          targetPlanId = planId;
          state.evaluated_nodes[nodeId] = evaluation;
          break;
        }
      }
      
      if (!targetPlanId) {
        console.warn('[前端] 未找到节点所属的 plan:', nodeId);
        return;
      }
      
      // 更新该节点的评估状态
      await this.updateRoundsDataWithNodes();
      console.log('[前端] 评估完成，节点:', nodeId, '动作:', evaluation.branch_action);
    },
    
    syncPlanStatesWithGraph(graph) {
      // 同步 planStates 与 graph 中的节点信息
      const nodes = graph.nodes || {};
      for (const [, planState] of Object.entries(this.planStates)) {
        // 确保 node_ids 中的节点都在 graph 中存在
        planState.node_ids = planState.node_ids.filter(nodeId => nodeId in nodes);
      }
    },
    
    async updateRoundsDataWithNodes() {
      // 更新 roundsData 中对应节点的状态
      // 简化方案：等待后端发送完整的 graph 更新
      // 但我们可以先标记状态，让渲染函数知道哪些节点需要特殊处理
      this.$nextTick(() => {
        // 重新绘制，这次会根据 planStates 中的状态来渲染
        this.drawRiverChart();
      });
    },
    
    graphToRoundsData(graph) {
      const rawNodes = graph.nodes || {};
      const nodes = typeof rawNodes === 'object' && !Array.isArray(rawNodes) ? rawNodes : {};
      const evidenceList = Object.values(nodes).filter(n => n && n.type === 'EVIDENCE');
      if (evidenceList.length === 0) return [];
      const byRound = {};
      evidenceList.forEach(node => {
        const r = node.created_at_round ?? 0;
        if (!byRound[r]) byRound[r] = [];
        byRound[r].push(node);
      });
      const rounds = [];
      Object.keys(byRound).sort((a, b) => Number(a) - Number(b)).forEach(roundKey => {
        const roundNum = Number(roundKey);
        const groupByPlan = {};
        byRound[roundKey].forEach(node => {
          // 这里处理左边/右边节点合并回 plan 的逻辑。如果 source_tool 不规范，兜底给 semantic
          let tool = node.source_tool || 'strategy_semantic_search';
          
          // 如果 source_tool 是 "Left_Path(ExactSearch)"，需要映射回 plan 中的 "strategy_exact_search"
          if (tool === "Left_Path(ExactSearch)") tool = "strategy_exact_search";
          // 如果 source_tool 是 "Left_Path(Semantic)"，映射回 "strategy_semantic_search"
          else if (tool === "Left_Path(Semantic)") tool = "strategy_semantic_search";
          // 如果 source_tool 是 "Right_Path(LocalFilter)"，映射回 "strategy_metadata_search"
          else if (tool === "Right_Path(LocalFilter)") tool = "strategy_metadata_search";

          const args = node.source_args || {};
          const key = tool + '|' + JSON.stringify(args);
          if (!groupByPlan[key]) groupByPlan[key] = { plan: { tool, args, ParentNode: node.ParentNode, reason: node.source_reason || '' }, nodes: [] };
          groupByPlan[key].nodes.push(node);
        });
        const queryResults = Object.values(groupByPlan).map(({ plan, nodes: nodeList }) => {
          // 从 experimentResult 对齐完整 orchestrator_plan（含 HyDE / rerank id，供跳过评估时小地图着色）
          let plansummary = null;
          let matchingQuery = null;
          const er = this.experimentResult;
          const erOk =
            er &&
            er.iterations &&
            (!er.session_id || !this.activeSessionId || er.session_id === this.activeSessionId);
          if (erOk) {
            const iteration = er.iterations.find(iter => iter.round_number === roundNum);
            if (iteration && iteration.query_results) {
              matchingQuery = iteration.query_results.find(qr => {
                const qrPlan = qr.orchestrator_plan;
                return qrPlan &&
                       qrPlan.tool_name === plan.tool &&
                       JSON.stringify(qrPlan.args) === JSON.stringify(plan.args);
              });
              if (matchingQuery && matchingQuery.orchestrator_plan) {
                plansummary = matchingQuery.orchestrator_plan.plansummary || null;
              }
            }
          }

          const fromGraph = {
            action: 'call_tool',
            tool_name: plan.tool,
            args: plan.args,
            ParentNode: plan.ParentNode,
            reason: plan.reason
          };
          const userdo = matchingQuery?.orchestrator_plan?.userdo || null;
          let orchestrator_plan;
          if (matchingQuery?.orchestrator_plan && typeof matchingQuery.orchestrator_plan === 'object') {
            orchestrator_plan = { ...matchingQuery.orchestrator_plan, ...fromGraph };
            if (plansummary != null && plansummary !== '') {
              orchestrator_plan.plansummary = plansummary;
            }
          } else {
            orchestrator_plan = { ...fromGraph, plansummary };
          }
          if (userdo) {
            orchestrator_plan.userdo = JSON.parse(JSON.stringify(userdo));
          }

          return {
            orchestrator_plan,
          rag_results: nodeList.map(n => ({
            retrieval_result: {
              id: n.id,
              content: n.content || {},
              metadata: n.metadata || {},
              score: (n.metadata && n.metadata.score) != null ? n.metadata.score : 0,
              source_tool: n.source_tool,
              source_args: n.source_args || {}
            },
            evaluation: n.evaluation || null
          }))
          };
        });
        // 使用 orchestrator_plan.grid_pos[0] 将策略固定到对应“行”（并行轨）
        const positioned = [];
        queryResults.forEach((qr) => {
          if (riverGrid.isStrategySlotTombstone(qr)) return;
          const gp = qr?.orchestrator_plan?.grid_pos;
          if (Array.isArray(gp) && gp.length >= 1) {
            const row = Number(gp[0]);
            if (Number.isFinite(row) && row >= 1) {
              const idx = row - 1;
              while (positioned.length <= idx) positioned.push(null);
              positioned[idx] = qr;
              return;
            }
          }
          positioned.push(qr);
        });
        while (positioned.length > 1 && positioned[positioned.length - 1] == null) positioned.pop();
        rounds.push({ round_number: roundNum, query_results: positioned.filter((x) => x != null) });
      });
      rounds.sort((a, b) => a.round_number - b.round_number);
      return rounds;
    },

    queryResultPlanKey(qr) {
      const p = qr && qr.orchestrator_plan;
      if (!p) return '';
      return `${p.tool_name || ''}|${JSON.stringify(p.args || {})}`;
    },

    /**
     * 小矩形副标题：结果条数以 experiment_result 为准（图推送过程中可能少于最终条数）；
     * 若有 rerank 前候选 id 列表，附加 HyDE/向量池规模（与 rag 日志「候选池 top-K」一致）。
     */
    strategyCardSubtitleText(query, roundNumber) {
      if (query && query._continue_auto_pending) {
        return 'new strategy';
      }
      const graphN = (query?.rag_results || []).length;
      let expN = 0;
      const er = this.experimentResult;
      if (er && Array.isArray(er.iterations)) {
        const sid = this.activeSessionId;
        if (!er.session_id || !sid || er.session_id === sid) {
          const it = er.iterations.find((i) => Number(i.round_number) === Number(roundNumber));
          const m = it?.query_results?.find((x) => this.queryResultPlanKey(x) === this.queryResultPlanKey(query));
          expN = (m?.rag_results || []).length;
        }
      }
      const tr = Number(query?.orchestrator_plan?.total_results);
      const totalResults = Number.isFinite(tr) && tr > 0 ? tr : 0;
      const n = Math.max(graphN, expN, totalResults);
      const op = query?.orchestrator_plan || {};
      const rb = Array.isArray(op.rerank_before_ids)
        ? op.rerank_before_ids
        : Array.isArray(op.rerankBeforeIds)
          ? op.rerankBeforeIds
          : [];
      const pool = rb.length;
      let s = `${n} results`;
      if (pool > 0) {
        s += ` · HyDE向量池 ${pool}`;
      }
      return s;
    },

    /**
     * 该轮是否跳过评估：优先读 experiment_result.parameters 中与 round_number 对齐的快照（落盘 JSON），
     * 否则回退当前左栏 prop（实时跑数时可能尚未写入 parameters）。
     */
    getSkipEvaluationForRound(roundNumber) {
      const er = this.experimentResult;
      const rn = Number(roundNumber);
      if (er && Array.isArray(er.parameters) && er.parameters.length) {
        const row = er.parameters.find((x) => Number(x.round_number) === rn);
        if (row != null && typeof row.skip_evaluation === 'boolean') {
          return !!row.skip_evaluation;
        }
      }
      return !!this.skipEvaluation;
    },

    /** 小矩形 Σ 按钮：支持 plansummary 为 JSON 字符串或已解析对象 */
    orchestratorPlanHasPlanSummary(plan) {
      if (!plan) return false;
      const hy = plan.hyde_hypothetical_paragraph_full_text ?? plan.hydeHypotheticalParagraphFullText;
      if (hy != null && String(hy).trim()) return true;
      const p = plan.plansummary;
      if (p == null) return false;
      if (typeof p === 'string') return p.trim().length > 0;
      if (typeof p === 'object') {
        return !!(p.answer || p.suggestion);
      }
      return true;
    },

    /**
     * 将 experimentResult.iterations 中的 plansummary 写回当前展示的 rounds（graph 路径下曾缺此字段）。
     */
    syncPlanSummariesFromExperimentResult() {
      const er = this.experimentResult;
      if (!er || !Array.isArray(er.iterations)) return;
      const sid = this.activeSessionId;
      if (er.session_id && sid && er.session_id !== sid) return;

      const patchRound = (round) => {
        if (!round || round.query_results == null) return;
        const it = er.iterations.find((i) => Number(i.round_number) === Number(round.round_number));
        if (!it || !it.query_results) return;
        round.query_results.forEach((qr) => {
          const k = this.queryResultPlanKey(qr);
          const m = it.query_results.find((x) => this.queryResultPlanKey(x) === k);
          if (!m || !m.orchestrator_plan) return;
          const ps = m.orchestrator_plan.plansummary;
          const hy = m.orchestrator_plan.hyde_hypothetical_paragraph_full_text;
          const rb = m.orchestrator_plan.rerank_before_ids;
          const ra = m.orchestrator_plan.rerank_after_ids;
          const hasPs = ps != null && ps !== '';
          const hasHy = hy != null && String(hy).trim() !== '';
          const hasRb = Array.isArray(rb) && rb.length > 0;
          const hasRa = Array.isArray(ra) && ra.length > 0;
          if (!hasPs && !hasHy && !hasRb && !hasRa) {
            const expRag = m.rag_results || [];
            const curRag = qr.rag_results || [];
            if (expRag.length <= curRag.length) return;
            qr.rag_results = JSON.parse(JSON.stringify(expRag));
            return;
          }
          if (!qr.orchestrator_plan) qr.orchestrator_plan = { ...m.orchestrator_plan };
          if (ps != null && ps !== '') qr.orchestrator_plan.plansummary = ps;
          const tr = Number(m.orchestrator_plan.total_results);
          if (Number.isFinite(tr) && tr > 0) {
            const curTr = Number(qr.orchestrator_plan.total_results);
            if (!Number.isFinite(curTr) || curTr < tr) {
              qr.orchestrator_plan.total_results = tr;
            }
          }
          if (hy != null && (qr.orchestrator_plan.hyde_hypothetical_paragraph_full_text == null || qr.orchestrator_plan.hyde_hypothetical_paragraph_full_text === '')) {
            qr.orchestrator_plan.hyde_hypothetical_paragraph_full_text = hy;
          }
          if (rb != null && (!Array.isArray(qr.orchestrator_plan.rerank_before_ids) || qr.orchestrator_plan.rerank_before_ids.length === 0)) {
            qr.orchestrator_plan.rerank_before_ids = Array.isArray(rb) ? [...rb] : rb;
          }
          if (ra != null && (!Array.isArray(qr.orchestrator_plan.rerank_after_ids) || qr.orchestrator_plan.rerank_after_ids.length === 0)) {
            qr.orchestrator_plan.rerank_after_ids = Array.isArray(ra) ? [...ra] : ra;
          }
          const expRag = m.rag_results || [];
          const curRag = qr.rag_results || [];
          if (expRag.length > curRag.length) {
            qr.rag_results = JSON.parse(JSON.stringify(expRag));
          }
        });
      };

      (this.roundsData || []).forEach(patchRound);
      (this.completedQuestionColumns || []).forEach((col) => {
        (col.roundsData || []).forEach(patchRound);
      });
    },

    mergeQueryResultsInRound(existing, incoming) {
      const map = new Map();
      (existing || []).forEach((qr) => {
        map.set(this.queryResultPlanKey(qr), qr);
      });
      (incoming || []).forEach((qr) => {
        const k = this.queryResultPlanKey(qr);
        const prev = map.get(k);
        if (!prev) {
          map.set(k, qr);
          return;
        }
        const pr = (prev.rag_results || []).length;
        const ir = (qr.rag_results || []).length;
        const pick = ir >= pr ? qr : prev;
        const other = ir >= pr ? prev : qr;
        if (pick && pick.orchestrator_plan && other && other.orchestrator_plan) {
          const psP = pick.orchestrator_plan.plansummary;
          const psO = other.orchestrator_plan.plansummary;
          if ((psP == null || psP === '') && psO != null && psO !== '') {
            pick.orchestrator_plan.plansummary = psO;
          }
          const hyFields = [
            ['hyde_hypothetical_paragraph_full_text', 'hydeHypotheticalParagraphFullText'],
            ['rerank_before_ids', 'rerankBeforeIds'],
            ['rerank_after_ids', 'rerankAfterIds']
          ];
          hyFields.forEach(([snake, camel]) => {
            const cur = pick.orchestrator_plan[snake] ?? pick.orchestrator_plan[camel];
            const inc = other.orchestrator_plan[snake] ?? other.orchestrator_plan[camel];
            const curMissing =
              cur == null ||
              cur === '' ||
              (Array.isArray(cur) && cur.length === 0);
            const incPresent = inc != null && !(typeof inc === 'string' && inc === '');
            if (curMissing && incPresent) {
              pick.orchestrator_plan[snake] = inc;
            }
          });
        }
        map.set(k, pick);
      });
      return Array.from(map.values());
    },

    mergeRoundsDataFromFollowUp(existing, incoming) {
      const clone = (o) => JSON.parse(JSON.stringify(o));
      const byRound = new Map();
      (existing || []).forEach((r) => {
        byRound.set(Number(r.round_number), clone(r));
      });
      (incoming || []).forEach((inc) => {
        const rn = Number(inc.round_number);
        if (!byRound.has(rn)) {
          byRound.set(rn, clone(inc));
        } else {
          const cur = byRound.get(rn);
          cur.query_results = this.mergeQueryResultsInRound(cur.query_results || [], inc.query_results || []);
        }
      });
      return Array.from(byRound.values()).sort((a, b) => a.round_number - b.round_number);
    },

    mergeExperimentResultFromFollowUp(existing, incoming) {
      const out = JSON.parse(JSON.stringify(existing));
      if (!incoming || !incoming.iterations) return out;
      incoming.iterations.forEach((it) => {
        const rn = Number(it.round_number);
        const idx = out.iterations.findIndex((x) => Number(x.round_number) === rn);
        if (idx < 0) {
          out.iterations.push(JSON.parse(JSON.stringify(it)));
        } else {
          const cur = out.iterations[idx];
          cur.query_results = this.mergeQueryResultsInRound(cur.query_results || [], it.query_results || []);
        }
      });
      out.iterations.sort((a, b) => a.round_number - b.round_number);
      if (incoming.root_goal && !out.root_goal) {
        out.root_goal = incoming.root_goal;
      }
      if (incoming.hypothesis) {
        out.hypothesis = JSON.parse(JSON.stringify(incoming.hypothesis));
      }
      return out;
    },

    /**
     * 当前「活跃会话」的轮次数据：在线跑在 roundsData；从本地多会话 JSON 读入时在 completedQuestionColumns 中。
     */
    getActiveSessionBaseRounds() {
      const sid = String(this.activeSessionId || '').trim();
      if (!sid) return this.roundsData || [];
      if (this.roundsData && this.roundsData.length > 0) {
        return this.roundsData;
      }
      const col = (this.completedQuestionColumns || []).find(
        (c) => String(c.sessionId || '').trim() === sid,
      );
      return col && Array.isArray(col.roundsData) ? col.roundsData : [];
    },
    /** 将合并后的轮次写回活跃会话（与 getActiveSessionBaseRounds 对称） */
    setActiveSessionRounds(nextRounds) {
      const sid = this.activeSessionId;
      if (!sid) {
        this.roundsData = nextRounds;
        return;
      }
      if (this.roundsData && this.roundsData.length > 0) {
        this.roundsData = nextRounds;
        return;
      }
      const col = (this.completedQuestionColumns || []).find((c) => c.sessionId === sid);
      if (col) {
        col.roundsData = nextRounds;
      } else {
        this.roundsData = nextRounds;
      }
    },

    /** 与全局底图同源：优先用 globalMapPoints 建立 id→点，避免 mapPoints 与全局 JSON 版本不一致时证据坐标错位 */
    rebuildIdToPointMap() {
      const src =
        this.globalMapPoints && this.globalMapPoints.length > 0
          ? this.globalMapPoints
          : this.mapPoints;
      this.idToPointMap = {};
      (src || []).forEach((item) => {
        const point = item;
        if (!point) return;
        if (point.id) {
          this.idToPointMap[point.id] = point;
        }
        if (point.chunk_id) {
          this.idToPointMap[point.chunk_id] = point;
        }
        try {
          if (point.metadata) {
            let metadataObj = point.metadata;
            if (typeof metadataObj === 'string') {
              metadataObj = JSON.parse(metadataObj);
            }
            if (metadataObj.figure_id) {
              this.idToPointMap[metadataObj.figure_id] = point;
            }
            if (metadataObj.chunkid != null) {
              this.idToPointMap[String(metadataObj.chunkid)] = point;
            }
            if (metadataObj.chunk_id != null) {
              this.idToPointMap[String(metadataObj.chunk_id)] = point;
            }
            if (metadataObj.metadata && typeof metadataObj.metadata === 'string') {
              const innerMetadata = JSON.parse(metadataObj.metadata);
              if (innerMetadata.figure_id) {
                this.idToPointMap[innerMetadata.figure_id] = point;
              }
              if (innerMetadata.chunkid != null) {
                this.idToPointMap[String(innerMetadata.chunkid)] = point;
              }
              if (innerMetadata.chunk_id != null) {
                this.idToPointMap[String(innerMetadata.chunk_id)] = point;
              }
            }
          }
        } catch (e) {
          /* ignore */
        }
      });
    },

    async loadMapData() {
      try {
        const fileName = this.ragCollection === 'LLMvisDataset' 
          ? '/LLMvisDataset_embedding.json' 
          : '/multimodal2text_embeddings_2d.json';
        const response = await fetch(fileName);
        const rawData = await response.json();
        
        this.mapPoints = [];
        rawData.forEach((item) => {
          const coords = item.coordinates_2d || [0, 0];
          const point = {
            ...item,
            x: coords[0],
            y: coords[1],
            id: item.id,
            chunk_id: item.chunk_id || item.id
          };
          this.mapPoints.push(point);
        });

        this.rebuildIdToPointMap();
        
        console.log('地图数据加载完成，共', this.mapPoints.length, '个点');
        console.log('ID映射表大小:', Object.keys(this.idToPointMap).length);
        
        this.globalXExtent = d3.extent(this.mapPoints, d => d.x);
        this.globalYExtent = d3.extent(this.mapPoints, d => d.y);
      } catch (error) {
        console.error('加载地图数据失败:', error);
      }
    },

    // 根据ID查找点（支持多种ID格式）
    findPointById(id) {
      if (!id) return null;
      
      // 尝试多种匹配方式
      const idStr = id.toString();
      
      // 1. 直接匹配
      if (this.idToPointMap[idStr]) {
        return this.idToPointMap[idStr];
      }
      
      // 2. 尝试img_前缀
      if (!idStr.startsWith('img_')) {
        const imgId = `img_${idStr}`;
        if (this.idToPointMap[imgId]) {
          return this.idToPointMap[imgId];
        }
      }
      
      // 3. 尝试去掉img_前缀
      if (idStr.startsWith('img_')) {
        const numId = idStr.replace('img_', '');
        if (this.idToPointMap[numId]) {
          return this.idToPointMap[numId];
        }
      }
      
      const scanList =
        this.globalMapPoints && this.globalMapPoints.length > 0
          ? this.globalMapPoints
          : this.mapPoints;
      for (const point of scanList) {
        try {
          if (String(point.id) === idStr || String(point.chunk_id) === idStr) {
            return point;
          }
          if (point.metadata) {
            let metadataObj = point.metadata;
            if (typeof metadataObj === 'string') {
              metadataObj = JSON.parse(metadataObj);
            }
            
            if (metadataObj.figure_id === idStr || metadataObj.id === idStr) {
              return point;
            }
            if (String(metadataObj.chunkid) === idStr || String(metadataObj.chunk_id) === idStr) {
              return point;
            }
            
            if (metadataObj.metadata && typeof metadataObj.metadata === 'string') {
              const innerMetadata = JSON.parse(metadataObj.metadata);
              if (innerMetadata.figure_id === idStr || innerMetadata.id === idStr) {
                return point;
              }
              if (String(innerMetadata.chunkid) === idStr || String(innerMetadata.chunk_id) === idStr) {
                return point;
              }
            }
          }
        } catch (e) {
          // 忽略解析错误
        }
      }
      
      return null;
    },

    /** 与 drawStrategyMap / drawGlobalMap 底图同源的点数组（仅引用，不拷贝） */
    getCanonicalLayoutPoints() {
      if (this.globalMapPoints && this.globalMapPoints.length > 0) {
        return this.globalMapPoints;
      }
      return this.mapPoints || [];
    },

    /** 从一条检索结果收集所有可能与 embedding 点匹配的 id（本地实验 JSON 与 Chroma 字段可能不一致） */
    _collectEvidenceMapIdCandidates(retrievalResult) {
      const out = [];
      const push = (v) => {
        if (v === null || v === undefined) return;
        const s = String(v).trim();
        if (s && !out.includes(s)) out.push(s);
      };
      if (!retrievalResult) return out;
      const rr = retrievalResult;
      push(rr.id);
      const meta = rr.metadata;
      if (meta && typeof meta === 'object') {
        push(meta.id);
        push(meta.chunkid);
        push(meta.chunk_id);
        push(meta.figure_id);
        if (typeof meta.metadata === 'string') {
          try {
            const inner = JSON.parse(meta.metadata);
            if (inner && typeof inner === 'object') {
              push(inner.id);
              push(inner.chunkid);
              push(inner.chunk_id);
              push(inner.figure_id);
            }
          } catch (e) {
            /* ignore */
          }
        }
        if (typeof meta.full_json === 'string') {
          try {
            const fj = JSON.parse(meta.full_json);
            if (fj && typeof fj === 'object') {
              push(fj.id);
              push(fj.chunk_id);
              push(fj.chunkid);
            }
          } catch (e) {
            /* ignore */
          }
        }
      }
      return out;
    },

    _layoutPointRowMatchesEvidenceId(point, idStr) {
      if (!point || !idStr) return false;
      if (String(point.id) === idStr || String(point.chunk_id) === idStr) return true;
      const m = point.metadata;
      if (!m) return false;
      let mo = m;
      if (typeof mo === 'string') {
        try {
          mo = JSON.parse(mo);
        } catch (e) {
          return false;
        }
      }
      if (!mo || typeof mo !== 'object') return false;
      const fields = [mo.id, mo.chunkid, mo.chunk_id, mo.figure_id];
      for (const f of fields) {
        if (f != null && String(f) === idStr) return true;
      }
      if (typeof mo.metadata === 'string') {
        try {
          const inner = JSON.parse(mo.metadata);
          if (inner && typeof inner === 'object') {
            const innerFields = [inner.id, inner.chunkid, inner.chunk_id, inner.figure_id];
            for (const f of innerFields) {
              if (f != null && String(f) === idStr) return true;
            }
          }
        } catch (e) {
          /* ignore */
        }
      }
      return false;
    },

    /**
     * 仅在「当前全局/底图使用的 layout 点集」内解析坐标，保证策略小地图与左侧整体绘制一致。
     */
    findLayoutPointForRetrieval(layoutPoints, retrievalResult) {
      if (!layoutPoints || !layoutPoints.length || !retrievalResult) return null;
      const cands = this._collectEvidenceMapIdCandidates(retrievalResult);
      for (const idStr of cands) {
        for (const p of layoutPoints) {
          if (String(p.id) === idStr || String(p.chunk_id) === idStr) {
            return p;
          }
        }
      }
      for (const idStr of cands) {
        for (const p of layoutPoints) {
          if (this._layoutPointRowMatchesEvidenceId(p, idStr)) {
            return p;
          }
        }
      }
      return null;
    },

    async loadAllRounds() {
      if (!String(this.selectedDataFile || '').trim()) {
        await this.loadExperimentFileList();
        if (!String(this.selectedDataFile || '').trim() && this.experimentFiles.length > 0) {
          this.selectedDataFile = this.experimentFiles[0];
        }
        if (!String(this.selectedDataFile || '').trim()) {
          alert(
            '未选择实验文件且 experiment_data 目录下暂无 experiment*.json。\n请将 JSON 放到后端 ToRAGLENSBack/experiment_data，并确认已运行 python server.py（加载最新代码后需重启）与前端 devServer 的 /api 代理。'
          );
          return;
        }
      }

      this.clearChart();
      await this.loadMapData();

      try {
        const url = this.experimentDataFetchUrl(this.selectedDataFile);
        if (!url) throw new Error('无效的实验文件路径');
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}，无法读取：${this.selectedDataFile}`);
        }
        const experimentData = await response.json();
        this.completedQuestionColumns = [];
        this.activeSessionId = '';
        if (experimentData.batch_id != null && String(experimentData.batch_id).trim()) {
          this.sessionBatchId = String(experimentData.batch_id).trim();
          try {
            if (typeof sessionStorage !== 'undefined') {
              sessionStorage.setItem('rag_lens_batch_id', this.sessionBatchId);
            }
          } catch (e) {
            /* ignore */
          }
        }
        if (experimentData.sessions && Array.isArray(experimentData.sessions)) {
          this.experimentResult = experimentData.sessions[0] || experimentData;
          this.$store.commit('setExperimentResult', this.experimentResult);
          this.completedQuestionColumns = experimentData.sessions.map((s, i) => ({
            sessionId: s.session_id || `import-${i}`,
            rootGoal: s.root_goal || '',
            roundsData: (s.iterations || [])
              .filter((round) => round && round.round_number !== undefined)
              .sort((a, b) => a.round_number - b.round_number)
          }));
          this.roundsData = [];
          const s0 = experimentData.sessions[0];
          if (s0) {
            const rawSid = s0.session_id;
            this.activeSessionId =
              rawSid != null && String(rawSid).trim()
                ? String(rawSid).trim()
                : 'import-0';
          } else {
            this.activeSessionId = '';
          }
        } else {
          this.experimentResult = experimentData;
          this.$store.commit('setExperimentResult', experimentData);
          this.roundsData = (experimentData.iterations || []).filter(round => round && round.round_number !== undefined);
          this.roundsData.sort((a, b) => a.round_number - b.round_number);
          this.activeSessionId =
            experimentData.session_id != null && String(experimentData.session_id).trim()
              ? String(experimentData.session_id).trim()
              : 'default';
        }
        
        console.log('加载的实验数据:', this.roundsData);
        console.log('Hypothesis 数据:', this.experimentResult?.hypothesis);
        
        this.syncInteractiveReportFromHypothesis(this.experimentResult);
        
        this.forkExperimentSource = String(this.selectedDataFile || '')
          .trim()
          .replace(/\\/g, '/');
        this.$store.commit('setExperimentSourceFile', this.forkExperimentSource);
        this.syncPlanSummariesFromExperimentResult();
        this.drawRiverChart();
      } catch (error) {
        console.error('加载实验数据失败:', error);
        alert(`加载实验数据失败：${error.message || error}`);
      }
    },

    syncInteractiveReportFromHypothesis(experimentData) {
      console.log('[syncInteractiveReport] start, hypothesis:', experimentData?.hypothesis);
      if (!experimentData || !experimentData.hypothesis || !experimentData.hypothesis.sections) {
        console.log('[syncInteractiveReport] skipping, invalid data');
        return;
      }
      
      console.log('[syncInteractiveReport] clearing old and processing sections...', experimentData.hypothesis.sections.length);
      this.$store.commit('clearInteractiveReport');
      experimentData.hypothesis.sections.forEach(sec => {
        this.$store.commit('addInteractiveReportSection', { 
          title: sec.step_name, 
          text: sec.response 
        });
        // Try to extract chunk IDs using regex \[([^\]]+)\]
        const chunkIdRegex = /\[([^\]]+)\]/g;
        let match;
        const chunkIds = [];
        while ((match = chunkIdRegex.exec(sec.response)) !== null) {
          chunkIds.push(match[1]);
        }
        // If we have chunk IDs, we need to map them to real item objects
        if (chunkIds.length > 0) {
          // We'll search across all query results for matching chunk_ids
          const allResults = [];
          
          const pushResultsFromRounds = (rounds) => {
            (rounds || []).forEach(r => {
              (r.query_results || []).forEach(qr => {
                (qr.rag_results || []).forEach(rag => {
                   allResults.push(rag);
                });
              });
            });
          };

          (this.completedQuestionColumns || []).forEach(col => {
            pushResultsFromRounds(col.roundsData);
          });
          
          if (experimentData && experimentData.iterations) {
            pushResultsFromRounds(experimentData.iterations);
          } else {
            pushResultsFromRounds(this.roundsData);
          }
          
          const sectionsList = this.$store.state.interactiveReportSections;
          if (sectionsList.length > 0) {
            const sectionId = sectionsList[sectionsList.length - 1].id;
            
            chunkIds.forEach(cid => {
               const matchedRag = allResults.find(rag => {
                  const ret = rag.retrieval_result || {};
                  return ret.id === cid || ret.chunk_id === cid || rag.chunk_id === cid || (ret.metadata && ret.metadata.chunk_id === cid);
               });
               if (matchedRag) {
                 const rr = matchedRag.retrieval_result || {};
                 const ragForBuild = { ...rr, evaluation: matchedRag.evaluation || null };
                 const item = buildInteractiveReportItemFromRag(this.$store.getters, ragForBuild, {
                   mapPointForId: (id) => this.findPointById(id)
                 });
                 if (item) {
                   this.$store.commit('addPointToInteractiveReportSection', { sectionId, item });
                 }
               } else {
                 // Fallback: Add a mock point just to show it was cited
                 this.$store.commit('addPointToInteractiveReportSection', { 
                   sectionId, 
                   item: { id: cid, title: `Cited: ${cid}`, type: 'text', branch_action: 'UNKNOWN' } 
                 });
               }
            });
          }
        }
      });
    },
    _ensureArrowhead(svg) {
      const defs = svg.select('defs').empty() ? svg.append('defs') : svg.select('defs');
      if (defs.select('#river-arrowhead').empty()) {
        const marker = defs.append('marker')
          .attr('id', 'river-arrowhead')
          .attr('viewBox', '0 0 10 10')
          .attr('refX', 8)
          .attr('refY', 5)
          .attr('markerWidth', 6)
          .attr('markerHeight', 6)
          .attr('orient', 'auto');
        
        marker.append('path')
          .attr('d', 'M 0 0 L 10 5 L 0 10 z')
          .attr('fill', 'rgba(130,140,150,0.75)'); // FootprintRAG风格
      }
    },

    // 绘制双边框矩形（FootprintRAG风格）
    _drawInsetRect(g, x, y, w, h, rx, fill, strokeOuter, strokeInner, outerW = 1.2, innerW = 1.0) {
      // 外边框
      g.append('rect')
        .attr('x', x)
        .attr('y', y)
        .attr('width', w)
        .attr('height', h)
        .attr('rx', rx)
        .attr('fill', fill)
        .attr('stroke', strokeOuter)
        .attr('stroke-width', outerW);

      // 内边框（稍微内缩）
      const inset = 0.8;
      g.append('rect')
        .attr('x', x + inset)
        .attr('y', y + inset)
        .attr('width', Math.max(0, w - inset * 2))
        .attr('height', Math.max(0, h - inset * 2))
        .attr('rx', Math.max(0, rx - inset))
        .attr('fill', 'none')
        .attr('stroke', strokeInner)
        .attr('stroke-width', innerW);
    },
    getAllRounds() {
      const out = [];
      const pushAnnotated = (rounds, sessionId) => {
        (rounds || []).forEach((r) => {
          if (!r || r.round_number === undefined) return;
          out.push({
            ...r,
            _sessionId: sessionId,
            __gridColKey: `${sessionId}__${r.round_number}`
          });
        });
      };
      (this.completedQuestionColumns || []).forEach((col) => {
        pushAnnotated(col.roundsData, col.sessionId);
      });
      const sid = this.activeSessionId || 'default';
      pushAnnotated(this.roundsData, sid);
      const orderIndex = (sessionId) => {
        const i = (this.completedQuestionColumns || []).findIndex((c) => c.sessionId === sessionId);
        return i >= 0 ? i : 999;
      };
      out.sort((a, b) => {
        const ao = orderIndex(a._sessionId);
        const bo = orderIndex(b._sessionId);
        if (ao !== bo) return ao - bo;
        if (String(a._sessionId) !== String(b._sessionId)) {
          return String(a._sessionId).localeCompare(String(b._sessionId));
        }
        return a.round_number - b.round_number;
      });
      if (
        out.length === 0 &&
        this.completedQuestionColumns.length === 0 &&
        (!this.roundsData || this.roundsData.length === 0) &&
        !this.isSubmitting
      ) {
        return [
          {
            round_number: 0,
            query_results: [],
            _sessionId: 'empty',
            __gridColKey: 'empty__0'
          }
        ];
      }
      return riverGrid.dedupeRoundsByGridColumnKey(out);
    },

    handleViewportClick() {
      if (this.dragState.active || this.panState.moved) return;
      this.focusedStrategyKey = null;
      this.hoveredStrategyKey = null;
      this.drawRiverChart();
    },

    startViewportPan(event) {
      if (event.button !== 0) return;
      if (
        event.target.closest(
          '.strategy-card, .grid-resize-handle, .card-icon-btn, .session-add-below-btn, .session-large-followup-btn, .mini-followup-trigger, .mini-followup-panel, .session-header-overlay'
        )
      ) {
        return;
      }
      this.panState = {
        active: true,
        startClientX: event.clientX,
        startClientY: event.clientY,
        originX: this.persistZoomTransform?.x || 0,
        originY: this.persistZoomTransform?.y || 0,
        moved: false
      };
      const move = (e) => this.onViewportPanMove(e);
      const up = () => this.onViewportPanEnd(move, up);
      window.addEventListener('mousemove', move);
      window.addEventListener('mouseup', up, { once: true });
    },

    onViewportPanMove(event) {
      if (!this.panState.active) return;
      const dx = event.clientX - this.panState.startClientX;
      const dy = event.clientY - this.panState.startClientY;
      this.panState.moved = this.panState.moved || Math.abs(dx) > 3 || Math.abs(dy) > 3;
      this.persistZoomTransform = {
        ...(this.persistZoomTransform || { k: 1 }),
        x: this.panState.originX + dx,
        y: this.panState.originY + dy
      };
    },

    onViewportPanEnd(move, up) {
      window.removeEventListener('mousemove', move);
      if (up) window.removeEventListener('mouseup', up);
      const moved = this.panState.moved;
      this.panState = {
        active: false,
        startClientX: 0,
        startClientY: 0,
        originX: 0,
        originY: 0,
        moved
      };
      window.setTimeout(() => {
        this.panState.moved = false;
      }, 0);
    },

    handleGridWheel(event) {
      const viewport = this.$refs.gridViewport;
      if (!viewport) return;
      const rect = viewport.getBoundingClientRect();
      const t = this.persistZoomTransform || { x: 0, y: 0, k: 1 };
      const factor = event.deltaY < 0 ? 1.08 : 0.92;
      const nextK = Math.max(0.35, Math.min(3, t.k * factor));
      const px = event.clientX - rect.left;
      const py = event.clientY - rect.top;
      const sceneX = (px - t.x) / t.k;
      const sceneY = (py - t.y) / t.k;
      this.persistZoomTransform = {
        k: nextK,
        x: px - sceneX * nextK,
        y: py - sceneY * nextK
      };
    },

    miniMapRefName(gridColKey, queryIndex) {
      const safe = String(gridColKey || 'r').replace(/[^a-zA-Z0-9_-]/g, '_');
      return `miniMap_${safe}_${queryIndex}`;
    },

    getMiniMapEl(gridColKey, queryIndex) {
      const raw = this.$refs[this.miniMapRefName(gridColKey, queryIndex)];
      return Array.isArray(raw) ? raw[0] : raw;
    },

    cardClass(card) {
      const safe = String(card.gridColKey || card.roundNumber).replace(/[^a-zA-Z0-9_-]/g, '_');
      const classes = [
        `strategy-${safe}-${card.queryIndex}`
      ];
      if ((this.focusedStrategyKey || this.hoveredStrategyKey) === card.key) classes.push('is-active');
      if (card.query?.orchestrator_plan?.tool_name === 'strategy_metadata_search') classes.push('is-metadata');
      if (this.dragState.active && this.dragState.cardKey === card.key) classes.push('is-dragging');
      if (this.dragState.hoverTarget?.key === card.key) classes.push(`drop-${this.dragState.hoverTarget.mode}`);
      return classes;
    },

    slotClass(slot) {
      const classes = [];
      if (slot.occupied) classes.push('is-occupied');
      else classes.push('is-empty');
      if (this.dragState.hoverTarget?.slotKey === slot.slotKey) {
        classes.push(`drop-${this.dragState.hoverTarget.mode}`);
      }
      return classes;
    },

    cardStyle(card) {
      const style = {
        left: `${card.rect.x}px`,
        top: `${card.rect.y}px`,
        width: `${card.rect.width}px`,
        height: `${card.rect.height}px`
      };
      if (this.dragState.active && this.dragState.cardKey === card.key) {
        if (this.dragState.hoverTarget?.sceneRect) {
          style.transform = `translate3d(${this.dragState.hoverTarget.sceneRect.x - card.rect.x}px, ${this.dragState.hoverTarget.sceneRect.y - card.rect.y}px, 0)`;
        } else {
          style.transform = `translate3d(${this.dragState.dx}px, ${this.dragState.dy}px, 0)`;
        }
        style.zIndex = 40;
      }
      return style;
    },

    columnHandleStyle(handle) {
      return {
        left: `${handle.x - 4}px`,
        top: `${handle.y}px`,
        width: `${handle.width}px`,
        height: `${handle.height}px`
      };
    },

    rowHandleStyle(handle) {
      return {
        left: `${handle.x}px`,
        top: `${handle.y - 4}px`,
        width: `${handle.width}px`,
        height: `${handle.height}px`
      };
    },

    startColumnResize(event, colKey) {
      const startX = event.clientX;
      const startWidth = this.gridState.columnWidths[colKey];
      const onMove = (e) => {
        this.gridState.columnWidths[colKey] = Math.max(220, startWidth + (e.clientX - startX));
        this.drawRiverChart();
      };
      const onUp = () => {
        window.removeEventListener('mousemove', onMove);
        window.removeEventListener('mouseup', onUp);
      };
      window.addEventListener('mousemove', onMove);
      window.addEventListener('mouseup', onUp);
    },

    startRowResize(event, rowKey) {
      const startY = event.clientY;
      const startHeight = this.gridState.rowHeights[rowKey];
      const onMove = (e) => {
        this.gridState.rowHeights[rowKey] = Math.max(180, startHeight + (e.clientY - startY));
        this.drawRiverChart();
      };
      const onUp = () => {
        window.removeEventListener('mousemove', onMove);
        window.removeEventListener('mouseup', onUp);
      };
      window.addEventListener('mousemove', onMove);
      window.addEventListener('mouseup', onUp);
    },

    getStrategyKey(roundOrNumber, queryIndex) {
      if (typeof roundOrNumber === 'object' && roundOrNumber !== null) {
        const gck = roundOrNumber.__gridColKey || riverGrid.gridColumnKey(roundOrNumber);
        return `${gck}#${queryIndex}`;
      }
      const roundNumber = roundOrNumber;
      return `r${roundNumber}#${queryIndex}`;
    },

    getActiveStrategyInfo() {
      const activeKey = this.focusedStrategyKey || this.hoveredStrategyKey;
      if (!activeKey) return null;
      const hash = activeKey.lastIndexOf('#');
      if (hash <= 0) return null;
      const gck = activeKey.slice(0, hash);
      const queryIndex = Number(activeKey.slice(hash + 1));
      const round = this.getAllRounds().find(
        (r) => (r.__gridColKey || riverGrid.gridColumnKey(r)) === gck
      );
      const query = round?.query_results?.[queryIndex];
      if (!query) return null;
      return {
        key: activeKey,
        roundNumber: round.round_number,
        queryIndex,
        query,
        sessionId: round._sessionId,
        gridColKey: gck
      };
    },

    findDirectParentKey(round, queryIndex, query) {
      const roundNumber = typeof round === 'object' && round !== null ? round.round_number : round;
      const sessionId = typeof round === 'object' && round !== null ? round._sessionId : this.activeSessionId;
      const parentNode = query?.orchestrator_plan?.ParentNode ?? query?.orchestrator_plan?.parentNode ?? null;
      if (parentNode == null) return null;
      const prevRoundNumber = roundNumber - 1;
      if (prevRoundNumber < 0) return null;
      const prevRound = this.getAllRounds().find(
        (r) => r.round_number === prevRoundNumber && r._sessionId === sessionId
      );
      if (!prevRound || !Array.isArray(prevRound.query_results)) return null;
      const parentId = String(parentNode).trim();
      if (!parentId || parentId === 'ROOT' || parentId === '0') return null;
      if (/^\d+$/.test(parentId)) {
        const prevIdx = parseInt(parentId, 10) - 1;
        if (prevIdx >= 0 && prevIdx < prevRound.query_results.length) return this.getStrategyKey(prevRound, prevIdx);
      }
      for (let i = 0; i < prevRound.query_results.length; i++) {
        const prevQuery = prevRound.query_results[i];
        const hit = (prevQuery?.rag_results || []).some((rag) => {
          const id = rag?.retrieval_result?.id;
          if (id == null) return false;
          const sid = String(id);
          return sid === parentId || sid === `img_${parentId}` || (parentId.startsWith('img_') && sid === parentId.replace('img_', ''));
        });
        if (hit) return this.getStrategyKey(prevRound, i);
      }
      return null;
    },

    findDirectChildrenKeys(round, queryIndex) {
      const roundNumber = typeof round === 'object' && round !== null ? round.round_number : round;
      const sessionId = typeof round === 'object' && round !== null ? round._sessionId : this.activeSessionId;
      const currentKey = this.getStrategyKey(round, queryIndex);
      const nextRound = this.getAllRounds().find(
        (r) => r.round_number === roundNumber + 1 && r._sessionId === sessionId
      );
      if (!nextRound || !Array.isArray(nextRound.query_results)) return [];
      const children = [];
      nextRound.query_results.forEach((q, idx) => {
        const parentKey = this.findDirectParentKey(nextRound, idx, q);
        if (parentKey === currentKey) children.push(this.getStrategyKey(nextRound, idx));
      });
      return children;
    },

    getCardHighlightEdges(round, queryIndex) {
      const active = this.getActiveStrategyInfo();
      if (!active) return [];
      const selfKey = this.getStrategyKey(round, queryIndex);
      if (selfKey === active.key) return ['top', 'right', 'bottom', 'left'];
      const activeRound = this.getAllRounds().find(
        (r) =>
          r.round_number === active.roundNumber &&
          (r._sessionId || 'default') === (active.sessionId || 'default')
      );
      const activeParentKey = activeRound
        ? this.findDirectParentKey(activeRound, active.queryIndex, active.query)
        : null;
      if (activeParentKey && selfKey === activeParentKey) return ['right'];
      const activeChildrenKeys = activeRound
        ? this.findDirectChildrenKeys(activeRound, active.queryIndex)
        : [];
      if (activeChildrenKeys.includes(selfKey)) return ['left'];
      return [];
    },

    handleCardClick(card) {
      if (this.dragState.moved) return;
      this.focusedStrategyKey = card.key;
      this.highlightPlanPointsInGlobalMap(card.query);
      this.drawRiverChart();
    },

    drawRiverChart() {
      this.emitUserOperationsChange();
      const viewport = this.$refs.gridViewport;
      this.svgWidth = viewport?.clientWidth || this.$el.clientWidth;
      this.svgHeight = viewport?.clientHeight || this.$el.clientHeight;

      const allRounds = this.getAllRounds();
      if (allRounds.length === 0) {
        this.gridMetrics = null;
        this.strategyCanvases = {};
        const connectionSvg = this.$refs.connectionSvg;
        const bgSvg = this.$refs.gridBgSvg;
        if (connectionSvg) d3.select(connectionSvg).selectAll('*').remove();
        if (bgSvg) d3.select(bgSvg).selectAll('*').remove();
        return;
      }

      const metrics = riverGrid.buildGridMetrics(this, allRounds);
      this.gridMetrics = metrics;
      this.strategyCanvases = {};

      allRounds.forEach((round) => {
        const gck = round.__gridColKey || riverGrid.gridColumnKey(round);
        (round.query_results || []).forEach((query, queryIndex) => {
          if (riverGrid.isStrategySlotTombstone(query)) return;
          const rowSlot0 = riverGrid.strategyVisualRowSlot0(query, queryIndex);
          if (rowSlot0 < 0) return;
          const rect = riverGrid.getStrategyCellRect(this, metrics, round.round_number, rowSlot0, gck);
          if (!rect) return;
          const canvas = new StrategyCanvas(round.round_number, queryIndex, rect.x, rect.y, rect.width, rect.height);
          canvas.parentNode = query?.orchestrator_plan?.ParentNode ?? query?.orchestrator_plan?.parentNode ?? null;
          canvas.gridColKey = gck;
          canvas.sessionId = round._sessionId;
          if (!this.strategyCanvases[gck]) this.strategyCanvases[gck] = {};
          this.strategyCanvases[gck][queryIndex] = canvas;
        });
      });

      this.$nextTick(() => {
        this.renderBackgroundSvg();
        this.renderAllMiniMaps();
        this.drawConnections();
      });
    },
    renderBackgroundSvg() {
      const bgSvg = this.$refs.gridBgSvg;
      if (!bgSvg) return;
      const svg = d3.select(bgSvg);
      svg.selectAll('*').remove();
      svg.attr('width', this.sceneCanvasSize.width).attr('height', this.sceneCanvasSize.height);
    },

    renderAllMiniMaps() {
      this.strategyCards.forEach((card) => {
        const svgEl = this.getMiniMapEl(card.gridColKey, card.queryIndex);
        if (!svgEl) return;
        const svg = d3.select(svgEl);
        svg.selectAll('*').remove();
        const wrap = svgEl.parentElement;
        const measuredH = wrap && wrap.clientHeight > 0 ? wrap.clientHeight : null;
        const measuredW = wrap && wrap.clientWidth > 0 ? wrap.clientWidth : null;
        const fallbackH = Math.max(140, card.rect.height - 52 - 24);
        const mapHeight = Math.max(120, measuredH ?? fallbackH);
        const mapWidth = Math.max(80, measuredW ?? card.rect.width);
        svg.attr('width', mapWidth).attr('height', mapHeight);
        const rootG = svg.append('g');
        if (card.query?.rag_results?.length) {
          const miniMapEvalFilter = this.strategyMiniMapEvalFilter[card.key] || null;
          this.drawStrategyMap(
            rootG,
            card.query,
            0,
            0,
            mapWidth,
            mapHeight,
            card.roundNumber,
            card.queryIndex,
            card.sessionId,
            miniMapEvalFilter
          );
        } else {
          svg.append('text')
            .attr('x', mapWidth / 2)
            .attr('y', mapHeight / 2)
            .attr('text-anchor', 'middle')
            .attr('font-size', '12px')
            .attr('fill', '#999')
            .text('暂无结果');
        }
      });
    },

    /** 只读 DOM，与 drawGlobalMap 中 margin=10 的内容区一致，供小地图匹配全局图的 x/y 拉伸比例（不改全局地图代码） */
    readGlobalMapContentSizeForMiniMap() {
      const id = this.globalMapMountId || 'left-global-map';
      const el = typeof document !== 'undefined' ? document.getElementById(id) : null;
      const margin = 10;
      const fallbackW = 380;
      const fallbackH = 260;
      if (!el || el.clientWidth < 8 || el.clientHeight < 8) {
        return { cw: fallbackW, ch: fallbackH };
      }
      return {
        cw: Math.max(1, el.clientWidth - margin * 2),
        ch: Math.max(1, el.clientHeight - margin * 2),
      };
    },

    drawStrategyMap(
      strategyGroup,
      query,
      rectX,
      rectY,
      rectWidth,
      rectHeight,
      roundNumber,
      queryIndex,
      sessionId = '',
      miniMapEvalFilter = null
    ) {
      const layoutPoints = this.getCanonicalLayoutPoints();
      // const isEmptyQuery = !query.rag_results || query.rag_results.length === 0;
      const ragPoints = [];
      const missingIds = [];
      
      query.rag_results.forEach(rag => {
        const normEval = miniMapEvalFilter ? this.strategyCardNormalizeBranchAction(rag) : null;
        if (miniMapEvalFilter && normEval !== miniMapEvalFilter) {
          return;
        }

        // 如果启用了隐藏PRUNE，跳过PRUNE节点
        if (this.hidePrunePoints) {
          const branchAction = rag.evaluation?.branch_action || 'UNKNOWN';
          if (branchAction === 'PRUNE') {
            return; // 跳过PRUNE节点
          }
        }
        
        const pointId = rag.retrieval_result.id;
        const point = this.findLayoutPointForRetrieval(layoutPoints, rag.retrieval_result);
        
        if (point) {
          ragPoints.push({ 
            x: point.x, 
            y: point.y, 
            id: point.id,
            rag: rag,
            originalPoint: point
          });
        } else {
          missingIds.push(pointId);
        }
      });
      
      if (missingIds.length > 0) {
        console.warn(`轮次${roundNumber}查询${queryIndex}: 未找到以下ID的点:`, missingIds);
      }
      
      if (ragPoints.length === 0) {
        // 如果没有找到点，显示提示
        strategyGroup.append('text')
          .attr('x', rectX + rectWidth / 2)
          .attr('y', rectY + rectHeight / 2)
          .attr('text-anchor', 'middle')
          .attr('font-size', '12px')
          .attr('fill', '#999')
          .text('未找到匹配的点');
        return;
      }

      // 统计新证据与重复证据（UNKNOWN 视为重复）
      // let duplicateCount = 0;
      // let uniqueCount = 0;
      // ragPoints.forEach(p => {
      //   const action = p.rag.evaluation?.branch_action || 'UNKNOWN';
      //   if (action === 'UNKNOWN') {
      //     duplicateCount += 1;
      //   } else {
      //     uniqueCount += 1;
      //   }
      // });
      
      // 标题/页脚已在模板中置于 SVG 外（.strategy-card-header / .strategy-card-footer），
      // 传入的 rectWidth×rectHeight 即整块小地图画布；若再扣「虚拟标题/页脚」高度会导致图区过矮、上下大片留白。
      const cardPad = 0;
      const mapX = rectX + cardPad;
      const mapY = rectY + cardPad;
      const mapW = rectWidth - cardPad * 2;
      const mapH = rectHeight - cardPad * 2;
      
      // 创建裁剪路径
      const clipId = `clip-map-r${roundNumber}-q${queryIndex}`.replace(/[^a-zA-Z0-9_-]/g, '_');
      const defs = strategyGroup.append('defs');
      defs.append('clipPath')
        .attr('id', clipId)
        .attr('clipPathUnits', 'userSpaceOnUse')
        .append('rect')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', mapW)
        .attr('height', mapH)
        .attr('rx', 0); // 直角裁剪
      
      // 地图外层组
      const mapOuter = strategyGroup.append('g')
        .attr('class', 'strategy-map-outer')
        .attr('transform', `translate(${mapX}, ${mapY})`);
      
      // 不再绘制地图边框（圆角框已去掉，只保留外层的直角框）
      
      // 地图内容组（带裁剪）
      const contentG = mapOuter.append('g')
        .attr('class', 'strategy-map-content')
        .attr('clip-path', `url(#${clipId})`);

      // 添加一个用于接收缩放和拖拽事件的透明背景矩形
      contentG.append('rect')
        .attr('width', mapW)
        .attr('height', mapH)
        .attr('fill', 'transparent')
        .on('mouseenter', () => {
          const parentNode = query?.orchestrator_plan?.ParentNode;
          if (parentNode && parentNode !== "0") {
            const point = this.findPointById(parentNode);
            const matchId = point ? point.id : parentNode;
            
            // 寻找所有包含了该ID的卡片（包括被合并的）
            this.getAllRounds().forEach((r) => {
              if (!r.query_results) return;
              const gck = r.__gridColKey || riverGrid.gridColumnKey(r);
              const safe = String(gck).replace(/[^a-zA-Z0-9_-]/g, '_');
              r.query_results.forEach((q, qIdx) => {
                if (q.rag_results && q.rag_results.some(rag => {
                  const ragPoint = this.findPointById(rag.retrieval_result.id);
                  return (ragPoint && ragPoint.id === matchId) || rag.retrieval_result.id === matchId;
                })) {
                  const targetCardEl = this.$el?.querySelector(`.strategy-${safe}-${qIdx}`);
                  if (targetCardEl) targetCardEl.classList.add('highlight-parent-source');
                }
              });
            });
          }
        })
        .on('mouseleave', () => {
          // 恢复所有被高亮的卡片
          this.$el?.querySelectorAll('.strategy-card.highlight-parent-source').forEach((el) => {
            el.classList.remove('highlight-parent-source');
          });
        });

      // 实际渲染内容的组（被缩放影响）
      const zoomG = contentG.append('g').attr('class', 'strategy-map-zoom-group');

      // 小地图独立缩放行为
      const zoom = d3.zoom()
        .scaleExtent([0.1, 10])
        .on('zoom', (event) => {
          zoomG.attr('transform', event.transform);
        });

      // 应用缩放行为到 contentG，并关闭双击放大（以防止覆盖卡片的双击展示 summary 功能）
      contentG.call(zoom).on('dblclick.zoom', null);

      // 与左栏全局图相同的「数据→像素」比例（readGlobalMapContentSizeForMiniMap 对齐 drawGlobalMap 的 content 宽高），
      // 再整体 scale+居中塞进小地图，避免策略卡偏横时把小地图拉得比全局更「扁」。
      // 底图点集与全局一致：与上方 rag 点解析同源（layoutPoints === getCanonicalLayoutPoints()）
      const allPoints = layoutPoints && layoutPoints.length > 0 ? layoutPoints : this.getCanonicalLayoutPoints();
      const xExtent = d3.extent(allPoints, (d) => d.x);
      const yExtent = d3.extent(allPoints, (d) => d.y);
      const { cw: gCW, ch: gCH } = this.readGlobalMapContentSizeForMiniMap();
      const xRef = d3.scaleLinear().domain(xExtent).range([0, gCW]);
      const yRef = d3.scaleLinear().domain(yExtent).range([gCH, 0]);
      const k = Math.min(mapW / gCW, mapH / gCH);
      const tx = (mapW - k * gCW) / 2;
      const ty = (mapH - k * gCH) / 2;
      const plotG = zoomG
        .append('g')
        .attr('class', 'strategy-plot-fit')
        .attr('transform', `translate(${tx},${ty}) scale(${k})`);

      const dotSamplePx = allPoints
        .map((p) => ({ x: xRef(p.x), y: yRef(p.y) }))
        .filter((p) => Number.isFinite(p.x) && Number.isFinite(p.y));

      const densityPts = allPoints
        .map((p) => ({ x: xRef(p.x), y: yRef(p.y) }))
        .filter((p) => Number.isFinite(p.x) && Number.isFinite(p.y));

      let contours = [];
      if (densityPts.length >= 10) {
        contours = d3
          .contourDensity()
          .x((d) => d.x)
          .y((d) => d.y)
          .size([gCW, gCH])
          .bandwidth(15)
          .thresholds(35)(densityPts);
      }

      if (contours && contours.length > 0) {
        const path = d3.geoPath();
        const cs = [...contours].sort((a, b) => (a?.value ?? 0) - (b?.value ?? 0));
        const color = d3
        .scaleSequential((t) => d3.interpolateBlues(0.05 + 0.55 * t))
        .domain([0, d3.max(cs, (d) => d.value) || 1]);

        const contourGroup = plotG.append('g').attr('class', 'density-contours');
        contourGroup
          .selectAll('path')
          .data(cs)
          .enter()
          .append('path')
          .attr('d', path)
          .attr('fill', (d) => color(d.value))
          .attr('opacity', 0.2)
          .attr('stroke', 'none');
      }

      if (dotSamplePx.length > 0) {
        plotG
          .append('g')
          .attr('class', 'global-dots')
          .selectAll('circle')
          .data(dotSamplePx)
          .enter()
          .append('circle')
          .attr('cx', (d) => d.x)
          .attr('cy', (d) => d.y)
          .attr('r', 1)
          .attr('fill', 'rgb(148,163,184,0.32)');
      }

      const op = query?.orchestrator_plan || {};
      const beforeIds =
        Array.isArray(op.rerank_before_ids) ? op.rerank_before_ids
        : Array.isArray(op.rerankBeforeIds) ? op.rerankBeforeIds
        : null;
      const afterIds =
        Array.isArray(op.rerank_after_ids) ? op.rerank_after_ids
        : Array.isArray(op.rerankAfterIds) ? op.rerankAfterIds
        : null;
      const skipSemanticNoEval =
        this.getSkipEvaluationForRound(roundNumber) &&
        op.tool_name === 'strategy_semantic_search';
      const useRerankLayer =
        skipSemanticNoEval &&
        beforeIds &&
        beforeIds.length > 0;

      let beforeSet = null;
      let afterIdSet = null;
      if (useRerankLayer) {
        beforeSet = new Set(beforeIds.map(String));
        const idListAfter =
          afterIds && afterIds.length
            ? afterIds.map(String)
            : (query.rag_results || []).map((r) => String(r?.retrieval_result?.id || '')).filter(Boolean);
        afterIdSet = new Set(idListAfter);

        const droppedPts = [];
        beforeSet.forEach((sid) => {
          if (afterIdSet.has(sid)) return;
          const pt = this.findLayoutPointForRetrieval(layoutPoints, { id: sid });
          if (pt && Number.isFinite(pt.x) && Number.isFinite(pt.y)) droppedPts.push(pt);
        });
        if (droppedPts.length) {
          // 与 global-dots 一致：圆心在 plotG 的「参考坐标系」内用 xRef/yRef；
          // plotG 已带 translate(tx,ty) scale(k)，切勿再写 tx+k*… 否则会双重变换飞到图外。
          plotG
            .append('g')
            .attr('class', 'rerank-candidate-dropped')
            .selectAll('circle')
            .data(droppedPts)
            .enter()
            .append('circle')
            .attr('cx', (d) => xRef(d.x))
            .attr('cy', (d) => yRef(d.y))
            .attr('r', 2.35)
            .attr('fill', '#b8deff')
            .attr('stroke', 'rgba(40,50,60,0.25)')
            .attr('stroke-width', 0.55)
            .attr('opacity', 0.88);
        }
      }

      // 绘制RAG结果点（FootprintRAG风格）
      const colorOf = (action) => {
        if (action === 'GROW') return '#379b61';
        if (action === 'PRUNE') return '#dc3545';
        if (action === 'KEEP') return '#eec316';
        return '#9AA3AD'; // UNKNOWN
      };

      const resolveCoreFill = (action, evidenceId) => {
        if (useRerankLayer && beforeSet && afterIdSet) {
          const pid = String(evidenceId || '');
          if (afterIdSet.has(pid)) return '#123f6e';
          if (beforeSet.has(pid)) return '#b8deff';
        }
        if (skipSemanticNoEval) {
          return '#123f6e';
        }
        return colorOf(action);
      };
      
      const ragPointsData = ragPoints.map(p => {
        const rr = p.rag?.retrieval_result || {};
        const score = Number(rr.score || 0);
        let action = p.rag?.evaluation?.branch_action || 'UNKNOWN';
        
        // 识别该点是否为图片类型（兼顾新旧格式）
        let rawType = rr?.metadata?.type || null;
        try {
          if (!rawType && rr?.metadata?.metadata) {
            const nested = rr.metadata.metadata;
            if (typeof nested === 'string') {
              const parsed = JSON.parse(nested);
              rawType = parsed?.type || null;
            } else if (typeof nested === 'object') {
              rawType = nested?.type || null;
            }
          }
          // 处理 LLMvisDataset 格式：如果有 full_json 或者是 savepath 则是图片
          if (!rawType && (rr?.metadata?.full_json || rr?.metadata?.savepath || rr?.metadata?.save_path)) {
            rawType = 'picture';
          }
          if (!rawType && rr?.metadata?.metadata && typeof rr.metadata.metadata === 'string') {
            const parsed = JSON.parse(rr.metadata.metadata);
            if (parsed.full_json || parsed.savepath || parsed.save_path) {
              rawType = 'picture';
            }
          }
        } catch (e) {
          // 忽略解析错误
        }
        if (rawType === 'text') rawType = 'texture';
        if (rawType === 'figure' || rawType === 'image') rawType = 'picture';
        if (!rawType) {
           try {
              if (rr.metadata && typeof rr.metadata === 'string') {
                 const meta = JSON.parse(rr.metadata);
                 if (meta.type === 'texture' || meta.type === 'text') rawType = 'texture';
                 else if (meta.type === 'picture' || meta.type === 'figure' || meta.type === 'image') rawType = 'picture';
              }
              if (!rawType && rr.id && rr.id.includes('Figure')) rawType = 'picture';
           } catch(e) {
             // ignore
           }
        }
        
        // 最后一次兜底检测
        if (!rawType) {
           try {
              if (rr.metadata && typeof rr.metadata === 'object') {
                 if (rr.metadata.type === 'texture' || rr.metadata.type === 'text') rawType = 'texture';
                 else if (rr.metadata.type === 'picture' || rr.metadata.type === 'figure' || rr.metadata.type === 'image') rawType = 'picture';
              }
           } catch(e) {
             // ignore
           }
        }
        
        const isPicture = rawType === 'picture';
        
        // 检查 planStates
        const nodeId = rr.id;
        for (const [, planState] of Object.entries(this.planStates)) {
          if (planState.node_ids.includes(nodeId)) {
            if (planState.evaluated_nodes[nodeId]) {
              action = planState.evaluated_nodes[nodeId].branch_action || 'UNKNOWN';
            } else {
              action = 'PENDING';
            }
            break;
          }
        }
        
        // FootprintRAG风格：半径计算（3-5像素）
        const r0 = 3.0 + Math.max(0, Math.min(1, score)) * 2.0;
        let radius = action === 'UNKNOWN' ? 2.6 : r0;

        // 如果该点来自 Evidence/chunk 点击：半径加倍
        const highlightInfo = this.highlightedPlanPoints?.[p.id];
        if (highlightInfo?.boostRadius) {
          radius = radius * 2;
        }
        
        const px = xRef(p.x);
        const py = yRef(p.y);
        return {
          x: tx + k * px,
          y: ty + k * py,
          radius,
          score,
          action,
          isPicture,
          rag: p.rag,
          coreFill: resolveCoreFill(action, rr.id),
        };
      });

      const ragG = zoomG.append('g').attr('class', 'rag-points');
      
      const dotGroups = ragG.selectAll('.rag-dot-group')
        .data(ragPointsData)
        .enter()
        .append('g')
        .attr('class', 'rag-dot-group')
        .style('cursor', 'pointer');
      
      // FootprintRAG风格：点的样式
      dotGroups.append('circle')
        .attr('class', 'rag-dot-core')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
        .attr('r', d => d.radius)
        .attr('fill', d => d.coreFill)
        .attr('stroke', 'rgba(40,50,60,0.35)') // FootprintRAG风格
        .attr('stroke-width', 0.8)
        .attr('opacity', d => (d.action === 'UNKNOWN' ? 0.45 : 0.92));

      // 图片点：额外加蓝色外圈（不改变原有填充色编码）
      dotGroups
        .filter(d => d.isPicture)
        .append('circle')
        .attr('class', 'rag-dot-ring')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
        .attr('r', d => d.radius + 2.0)
        .attr('fill', 'none')
        .attr('stroke', 'rgba(40, 140, 255, 0.95)')
        .attr('stroke-width', 1.2)
        .attr('opacity', 0.95)
        .attr('vector-effect', 'non-scaling-stroke');
      
      // FootprintRAG风格：事件处理
      dotGroups
        .on('mouseover', function(event, d) {
          d3.select(this).select('.rag-dot-core')
            .attr('r', d.radius + 2)
            .attr('stroke-width', 1.2)
            .attr('opacity', 1);

          d3.select(this).select('.rag-dot-ring')
            .attr('r', d.radius + 4.0)
            .attr('stroke-width', 1.6)
            .attr('opacity', 1);
        })
        .on('mouseout', function(event, d) {
          d3.select(this).select('.rag-dot-core')
            .attr('r', d.radius)
            .attr('stroke-width', 0.8)
            .attr('opacity', (d.action === 'UNKNOWN' ? 0.45 : 0.92));

          d3.select(this).select('.rag-dot-ring')
            .attr('r', d.radius + 2.0)
            .attr('stroke-width', 1.2)
            .attr('opacity', 0.95);
        })
        .on('click', (event, d) => {
          if (this.suppressNextRagDotClick) {
            this.suppressNextRagDotClick = false;
            event.stopPropagation();
            event.preventDefault();
            return;
          }
          const rr = d.rag?.retrieval_result;
          if (!rr) return;
          const evaluation = d.rag?.evaluation ?? null;
          this.showDetail(rr, evaluation, {
            sessionId,
            roundNumber,
            queryIndex,
            query,
            rag: d.rag,
          });
        })
        .on('pointerdown', (event, d) => {
          if (event.button !== 0) return;
          event.stopPropagation();
          const rr = d.rag?.retrieval_result;
          if (!rr || !rr.id) return;
          const evaluation = d.rag?.evaluation ?? null;
          if (this.hidePrunePoints) {
            const branchAction = evaluation?.branch_action || rr.evaluation?.branch_action || 'UNKNOWN';
            if (branchAction === 'PRUNE') return;
          }
          const ragForBuild = { ...rr, evaluation: evaluation || rr.evaluation || null };
          const item = buildInteractiveReportItemFromRag(this.$store.getters, ragForBuild, {
            mapPointForId: (id) => this.findPointById(id)
          });
          if (!item) return;

          const startX = event.clientX;
          const startY = event.clientY;
          const ptrId = event.pointerId;
          let moved = false;
          const IR_DRAG_THRESHOLD = 8;
          const gNode = event.currentTarget;
          try {
            gNode.setPointerCapture(ptrId);
          } catch (e) {
            /* ignore */
          }

          const setDropZonesActive = (on) => {
            document.querySelectorAll('.interactive-report-drop-zone').forEach((z) => {
              if (on) z.classList.add('interactive-report-drop-active');
              else z.classList.remove('interactive-report-drop-active');
            });
          };

          const cleanup = () => {
            window.removeEventListener('pointermove', onMove);
            window.removeEventListener('pointerup', onUp);
            setDropZonesActive(false);
            try {
              gNode.releasePointerCapture(ptrId);
            } catch (e) {
              /* ignore */
            }
          };

          const onMove = (ev) => {
            if (ev.pointerId !== ptrId) return;
            if (Math.hypot(ev.clientX - startX, ev.clientY - startY) > IR_DRAG_THRESHOLD) {
              moved = true;
              setDropZonesActive(true);
            }
          };

          const vm = this;
          const onUp = (ev) => {
            if (ev.pointerId !== ptrId) return;
            cleanup();
            if (moved) {
              ev.preventDefault();
              ev.stopPropagation();
              const target = document.elementFromPoint(ev.clientX, ev.clientY);
              const zone = target && target.closest && target.closest('.interactive-report-drop-zone');
              if (zone) {
                const sectionId = zone.getAttribute('data-section-id');
                if (sectionId) {
                  vm.$store.commit('addPointToInteractiveReportSection', { sectionId, item });
                }
              }
              vm.suppressNextRagDotClick = true;
            }
          };

          window.addEventListener('pointermove', onMove);
          window.addEventListener('pointerup', onUp);
        });
    },


    drawConnections() {
      const svgEl = this.$refs.connectionSvg;
      if (!svgEl) return;
      const svg = d3.select(svgEl);
      svg.selectAll('*').remove();

      if (!this.showConnections || !this.showLegacyConnections) {
        this.connectionGroup = null;
        return;
      }

      this._ensureArrowhead(svg);
      this.connectionGroup = svg.append('g').attr('class', 'river-connections');
      const allRounds = this.getAllRounds().filter((r) => r && r.round_number !== undefined);
      const roundBySession = new Map();
      allRounds.forEach((r) => {
        const sid = r._sessionId || 'default';
        if (!roundBySession.has(sid)) roundBySession.set(sid, []);
        roundBySession.get(sid).push(r);
      });
      const activeKey = this.focusedStrategyKey || this.hoveredStrategyKey;
      roundBySession.forEach((sessionRounds) => {
        sessionRounds.sort((a, b) => a.round_number - b.round_number);
        const m = new Map(sessionRounds.map((r) => [r.round_number, r]));
        const maxR = Math.max(...sessionRounds.map((x) => x.round_number), 0);
        for (let r = 1; r <= maxR; r++) {
          const curRound = m.get(r);
          const prevRound = m.get(r - 1);
          if (!curRound || !prevRound) continue;
          const gckCur = curRound.__gridColKey || riverGrid.gridColumnKey(curRound);
          const gckPrev = prevRound.__gridColKey || riverGrid.gridColumnKey(prevRound);
          const cur = this.strategyCanvases[gckCur];
          const prev = this.strategyCanvases[gckPrev];
          if (!cur || !prev) continue;
          const roundByNum = new Map(sessionRounds.map((rr) => [rr.round_number, rr]));
          Object.entries(cur).forEach(([curIndex, curCanvas]) => {
            const parent = curCanvas.parentNode;
            if (parent === null || parent === undefined) return;
            const parentId = String(parent).trim();
            if (parentId === '' || parentId === '0' || parentId === 'ROOT') return;
            const curKey = this.getStrategyKey(curRound, Number(curIndex));
            if (/^\d+$/.test(parentId)) {
              const pqIdx = parseInt(parentId, 10) - 1;
              if (pqIdx >= 0) {
                const prevCanvas = prev[pqIdx];
                if (prevCanvas) {
                  const prevKey = this.getStrategyKey(prevRound, prevCanvas.queryIndex);
                  const related = activeKey ? (curKey === activeKey || prevKey === activeKey) : false;
                  this.drawSmoothConnection(prevCanvas, curCanvas, related);
                  return;
                }
              }
            }
            Object.entries(prev).forEach(([prevIndex, prevCanvas]) => {
              const pr = roundByNum.get(prevCanvas.roundNumber);
              if (!pr) return;
              const prevQuery = pr.query_results?.[prevCanvas.queryIndex];
              if (!prevQuery?.rag_results) return;
              const hit = prevQuery.rag_results.some((rag) => {
                const id = rag?.retrieval_result?.id;
                if (id === undefined || id === null) return false;
                const sid = String(id);
                return sid === parentId || sid === `img_${parentId}` || (parentId.startsWith('img_') && sid === parentId.replace('img_', ''));
              });
              if (hit) {
                const prevKey = this.getStrategyKey(prevRound, Number(prevIndex));
                const related = activeKey ? (curKey === activeKey || prevKey === activeKey) : false;
                this.drawSmoothConnection(prevCanvas, curCanvas, related);
              }
            });
          });
        }
      });
    },

    drawSmoothConnection(sourceCanvas, targetCanvas, related = false) {
      if (!this.connectionGroup) return;
      const s = sourceCanvas.getRightEdge();
      const t = targetCanvas.getLeftEdge();
      const dx = t.x - s.x;
      const dy = t.y - s.y;
      const cpx = Math.min(dx * 0.5, 160);
      const cpy = Math.abs(dy) > 60 ? dy * 0.28 : 0;
      const path = d3.path();
      path.moveTo(s.x, s.y);
      path.bezierCurveTo(s.x + cpx, s.y + cpy, t.x - cpx, t.y - cpy, t.x, t.y);
      const baseStroke = related ? 'rgba(14,165,233,0.88)' : 'rgba(148,163,184,0.32)';
      const baseWidth = related ? 2.6 : 1.2;
      const p = this.connectionGroup.append('path').attr('d', path.toString()).attr('fill', 'none').attr('stroke', baseStroke).attr('stroke-width', baseWidth).attr('marker-end', related ? 'url(#river-arrowhead)' : null);
      p.on('mouseover', function() { d3.select(this).attr('stroke-width', related ? 3.0 : 2.0).attr('stroke', related ? 'rgba(2,132,199,0.96)' : 'rgba(100,116,139,0.62)'); })
        .on('mouseout', function() { d3.select(this).attr('stroke-width', baseWidth).attr('stroke', baseStroke); });
    },

    startCardDrag(event, card) {
      if (card.sessionId && this.activeSessionId && card.sessionId !== this.activeSessionId) {
        return;
      }
      const t = this.persistZoomTransform || { x: 0, y: 0, k: 1 };
      this.dragState = {
        active: true,
        cardKey: card.key,
        sessionId: card.sessionId,
        roundNumber: card.roundNumber,
        queryIndex: card.queryIndex,
        startClientX: event.clientX,
        startClientY: event.clientY,
        dx: 0,
        dy: 0,
        hoverTarget: null,
        moved: false
      };
      const move = (e) => this.onCardDragMove(e, t.k || 1);
      const up = () => this.onCardDragEnd(move, up);
      window.addEventListener('mousemove', move);
      window.addEventListener('mouseup', up, { once: true });
    },

    onCardDragMove(event, scale = 1) {
      if (!this.dragState.active) return;
      const dx = (event.clientX - this.dragState.startClientX) / scale;
      const dy = (event.clientY - this.dragState.startClientY) / scale;
      this.dragState.dx = dx;
      this.dragState.dy = dy;
      this.dragState.moved = this.dragState.moved || Math.abs(dx) > 4 || Math.abs(dy) > 4;
      this.dragState.hoverTarget = this.detectDropTarget(event.clientX, event.clientY);
    },

    onCardDragEnd(move, up) {
      window.removeEventListener('mousemove', move);
      if (up) window.removeEventListener('mouseup', up);
      const active = JSON.parse(JSON.stringify(this.dragState));
      if (active.active && active.hoverTarget) {
        const sid =
          active.hoverTarget.sessionId || active.sessionId || this.activeSessionId;
        if (active.hoverTarget.mode === 'merge' && active.cardKey !== active.hoverTarget.key) {
          this.mergeStrategies(
            active.roundNumber,
            active.queryIndex,
            active.hoverTarget.roundNumber,
            active.hoverTarget.queryIndex,
            sid
          );
        } else if (active.hoverTarget.mode === 'swap' && active.cardKey !== active.hoverTarget.key) {
          this.swapStrategies(
            active.roundNumber,
            active.queryIndex,
            active.hoverTarget.roundNumber,
            active.hoverTarget.queryIndex,
            sid
          );
        } else if (active.hoverTarget.mode === 'move') {
          this.moveStrategy(
            active.roundNumber,
            active.queryIndex,
            active.hoverTarget.roundNumber,
            active.hoverTarget.queryIndex,
            sid
          );
        }
      }
      this.dragState = {
        active: false,
        cardKey: null,
        sessionId: null,
        roundNumber: null,
        queryIndex: null,
        startClientX: 0,
        startClientY: 0,
        dx: 0,
        dy: 0,
        hoverTarget: null,
        moved: false
      };
      this.$nextTick(() => this.drawRiverChart());
    },

    clientToScene(clientX, clientY) {
      const viewport = this.$refs.gridViewport;
      const rect = viewport?.getBoundingClientRect?.();
      const t = this.persistZoomTransform || { x: 0, y: 0, k: 1 };
      if (!rect) return { x: 0, y: 0 };
      return {
        x: (clientX - rect.left - t.x) / t.k,
        y: (clientY - rect.top - t.y) / t.k
      };
    },

    sceneRectToViewportRect(sceneRect) {
      const viewport = this.$refs.gridViewport;
      const rect = viewport?.getBoundingClientRect?.();
      const t = this.persistZoomTransform || { x: 0, y: 0, k: 1 };
      if (!rect) return { left: 0, top: 0, width: 0, height: 0 };
      return {
        left: rect.left + sceneRect.x * t.k + t.x,
        top: rect.top + sceneRect.y * t.k + t.y,
        width: sceneRect.width * t.k,
        height: sceneRect.height * t.k
      };
    },

    detectDropTarget(clientX, clientY) {
      const point = this.clientToScene(clientX, clientY);
      let contained = null;
      let nearest = null;

      this.gridSlotCells.forEach((slot) => {
        if (slot.roundNumber === this.dragState.roundNumber && slot.queryIndex === this.dragState.queryIndex) return;
        const rect = slot.sceneRect;
        const within = point.x >= rect.x && point.x <= rect.x + rect.width && point.y >= rect.y && point.y <= rect.y + rect.height;
        const cx = rect.x + rect.width / 2;
        const cy = rect.y + rect.height / 2;
        const dist = Math.hypot(point.x - cx, point.y - cy);
        if (!nearest || dist < nearest.dist) nearest = { slot, dist };

        if (within) {
          const rx = (point.x - rect.x) / rect.width;
          const ry = (point.y - rect.y) / rect.height;
          const centerZone = rx > 0.22 && rx < 0.78 && ry > 0.22 && ry < 0.78;
          contained = {
            slotKey: slot.slotKey,
            key: slot.occupied
              ? this.getStrategyKey(
                  { round_number: slot.roundNumber, __gridColKey: slot.gridColKey, _sessionId: slot.sessionId },
                  slot.queryIndex
                )
              : null,
            roundNumber: slot.roundNumber,
            queryIndex: slot.queryIndex,
            sessionId: slot.sessionId,
            mode: slot.occupied ? (centerZone ? 'merge' : 'swap') : 'move',
            sceneRect: rect,
            rect: this.sceneRectToViewportRect(rect)
          };
        }
      });

      if (contained) return contained;
      if (nearest && nearest.dist < 90) {
        const slot = nearest.slot;
        return {
          slotKey: slot.slotKey,
          key: slot.occupied
            ? this.getStrategyKey(
                { round_number: slot.roundNumber, __gridColKey: slot.gridColKey, _sessionId: slot.sessionId },
                slot.queryIndex
              )
            : null,
          roundNumber: slot.roundNumber,
          queryIndex: slot.queryIndex,
          sessionId: slot.sessionId,
          mode: slot.occupied ? 'swap' : 'move',
          sceneRect: slot.sceneRect,
          rect: this.sceneRectToViewportRect(slot.sceneRect)
        };
      }
      return null;
    },

    /** 合并来源条数（兼容旧字段 _merged_sources_data） */
    mergeSourceCount(query) {
      if (!query) return 0;
      const n = (query.mergedSourcesData && query.mergedSourcesData.length) || 0;
      const legacy = (query._merged_sources_data && query._merged_sources_data.length) || 0;
      return Math.max(n, legacy);
    },

    /** 按 session 定位 round（与 getActiveSessionBaseRounds 对齐：sessions[] 载入时节轮次在 completedQuestionColumns） */
    getRoundRef(roundNumber, sessionId) {
      const rn = Number(roundNumber);
      const sid = String(sessionId || '').trim();
      const activeSid = String(this.activeSessionId || '').trim();
      const matchRound = (x) => x != null && Number(x.round_number) === rn;
      if (sid && activeSid && sid !== activeSid) {
        const col = (this.completedQuestionColumns || []).find((c) => String(c.sessionId || '').trim() === sid);
        return (col && (col.roundsData || []).find(matchRound)) || null;
      }
      const pool = this.getActiveSessionBaseRounds() || [];
      const hit = pool.find(matchRound);
      if (hit) return hit;
      return this.newRounds?.[rn] ?? this.newRounds?.[roundNumber] ?? null;
    },

    cloneQueryData(query) {
      return JSON.parse(JSON.stringify(query));
    },

    dedupeRagResults(results) {
      const seen = new Set();
      return (results || []).filter((item) => {
        const id = item?.retrieval_result?.id;
        const key = String(id ?? Math.random());
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
    },

    mergeStrategies(sourceRoundNumber, sourceIndex, targetRoundNumber, targetIndex, sessionId) {
      if (sourceRoundNumber === targetRoundNumber && sourceIndex === targetIndex) return;
      const sid = sessionId || this.activeSessionId || 'default';
      const sourceRound = this.getRoundRef(sourceRoundNumber, sid);
      const targetRound = this.getRoundRef(targetRoundNumber, sid);
      if (!sourceRound || !targetRound) return;
      const sourceQuery = sourceRound.query_results?.[sourceIndex];
      const targetQuery = targetRound.query_results?.[targetIndex];
      if (!sourceQuery || !targetQuery) return;

      if (!targetQuery._original_rag_results) {
        targetQuery._original_rag_results = this.cloneQueryData(targetQuery.rag_results || []);
      }
      if (!targetQuery.mergedSourcesData) {
        targetQuery.mergedSourcesData = [];
        if (targetQuery._merged_sources_data && targetQuery._merged_sources_data.length) {
          targetQuery.mergedSourcesData.push(...targetQuery._merged_sources_data);
          delete targetQuery._merged_sources_data;
        }
      }
      targetQuery.mergedSourcesData.push({
        originalRound: sourceRoundNumber,
        originalIndex: sourceIndex,
        queryData: this.cloneQueryData(sourceQuery)
      });
      targetQuery.merged_from = [...(targetQuery.merged_from || []), `${sourceRoundNumber}__${sourceIndex}`];
      targetQuery.rag_results = this.dedupeRagResults([...(targetQuery.rag_results || []), ...(sourceQuery.rag_results || [])]);

      sourceRound.query_results.splice(sourceIndex, 1);
      this.focusedStrategyKey = this.getStrategyKey(targetRoundNumber, targetIndex);
      this.roundsData = [...this.roundsData];
    },

    swapStrategies(sourceRoundNumber, sourceIndex, targetRoundNumber, targetIndex, sessionId) {
      const sid = sessionId || this.activeSessionId || 'default';
      const sourceRound = this.getRoundRef(sourceRoundNumber, sid);
      const targetRound = this.getRoundRef(targetRoundNumber, sid);
      if (!sourceRound || !targetRound) return;
      const sourceQuery = sourceRound.query_results?.[sourceIndex];
      const targetQuery = targetRound.query_results?.[targetIndex];
      if (!sourceQuery || !targetQuery) return;
      sourceRound.query_results.splice(sourceIndex, 1, targetQuery);
      targetRound.query_results.splice(targetIndex, 1, sourceQuery);
      this.focusedStrategyKey = this.getStrategyKey(targetRoundNumber, targetIndex);
    },

    moveStrategy(sourceRoundNumber, sourceIndex, targetRoundNumber, targetIndex, sessionId) {
      const sid = sessionId || this.activeSessionId || 'default';
      const sourceRound = this.getRoundRef(sourceRoundNumber, sid);
      const targetRound = this.getRoundRef(targetRoundNumber, sid);
      if (!sourceRound || !targetRound || !sourceRound.query_results) return;
      const movingQuery = sourceRound.query_results[sourceIndex];
      if (!movingQuery) return;

      sourceRound.query_results.splice(sourceIndex, 1);

      if (!targetRound.query_results) targetRound.query_results = [];
      let insertIndex = Math.max(0, Math.min(targetIndex, targetRound.query_results.length));
      if (sourceRoundNumber === targetRoundNumber && sourceIndex < insertIndex) {
        insertIndex -= 1;
      }
      targetRound.query_results.splice(insertIndex, 0, movingQuery);
      this.focusedStrategyKey = this.getStrategyKey(targetRoundNumber, insertIndex);
    },

    splitMergedStrategies(roundNumber, queryIndex, sessionId) {
      const round = this.getRoundRef(roundNumber, sessionId);
      if (!round || !round.query_results) return;
      const targetQuery = round.query_results[queryIndex];
      const sourcesToRestore =
        (targetQuery.mergedSourcesData && targetQuery.mergedSourcesData.length
          ? targetQuery.mergedSourcesData
          : null) ||
        (targetQuery._merged_sources_data && targetQuery._merged_sources_data.length
          ? targetQuery._merged_sources_data
          : null);
      if (!sourcesToRestore || sourcesToRestore.length === 0) return;

      // 恢复 targetQuery 自身的 rag_results 
      if (targetQuery._original_rag_results) {
         targetQuery.rag_results = [...targetQuery._original_rag_results];
         delete targetQuery._original_rag_results;
      }
      
      // 清除合并相关的标记
      delete targetQuery.merged_from;
      delete targetQuery.mergedSourcesData;
      delete targetQuery._merged_sources_data;
      
      // 按原始索引从小到大排序，这样在同一个 round 插入时顺移不会出错
      sourcesToRestore.sort((a, b) => a.originalIndex - b.originalIndex);
      
      const sid = sessionId || this.activeSessionId || 'default';
      sourcesToRestore.forEach(src => {
         const destRound = this.getRoundRef(src.originalRound, sid);
         if (destRound && destRound.query_results) {
            // 在目标 round 的原始索引处插入被拆分出来的卡片（如果有冲突则顺移）
            const insertIndex = Math.min(src.originalIndex, destRound.query_results.length);
            destRound.query_results.splice(insertIndex, 0, src.queryData);
         }
      });
      
      this.roundsData = [...this.roundsData];
      this.$nextTick(() => {
        this.drawRiverChart();
      });
    },

    showPlanSummary(data) {
      this.selectedPlanSummary = data;
      this.showPlanSummaryModal = true;
    },

    closePlanSummaryModal() {
      this.showPlanSummaryModal = false;
      this.selectedPlanSummary = null;
      this.deletingStrategy = false;
    },

    async deleteSelectedStrategy() {
      const p = this.selectedPlanSummary;
      if (!p) return;
      const sourcePath = this.forkExperimentSource || this.selectedDataFile;
      if (!sourcePath) {
        window.alert('请先加载实验 JSON（或设置 fork 源路径），才能同步删除落盘。');
        return;
      }
      if (!window.confirm(`确定删除轮次 ${p.roundNumber} 的第 ${p.queryIndex + 1} 个策略？同行后续策略会前移。`)) {
        return;
      }
      const sessionIdRaw =
        p.sessionId != null && String(p.sessionId).trim() !== ''
          ? String(p.sessionId).trim()
          : String(this.activeSessionId || '').trim();
      this.deletingStrategy = true;
      try {
        const resp = await fetch('/api/experiment-remove-strategy', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            source_path: sourcePath,
            session_id: sessionIdRaw,
            round_number: p.roundNumber,
            query_index: p.queryIndex,
          }),
        });
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok || !data.ok) {
          throw new Error(data.detail || `HTTP ${resp.status}`);
        }
        if (data.path) {
          this.forkExperimentSource = data.path;
          this.selectedDataFile = data.path;
        }

        const sid = sessionIdRaw || this.activeSessionId || 'default';
        const round = this.getRoundRef(p.roundNumber, sid);
        if (round && Array.isArray(round.query_results)) {
          const qi = p.queryIndex;
          if (qi >= 0 && qi < round.query_results.length) {
            round.query_results.splice(qi, 1);
          }
        }
        const activeSid = this.activeSessionId || 'default';
        if (sid !== activeSid) {
          const col = (this.completedQuestionColumns || []).find((c) => c.sessionId === sid);
          if (col && col.roundsData) {
            col.roundsData = [...col.roundsData];
          }
        } else {
          this.roundsData = [...(this.roundsData || [])];
        }

        this.closePlanSummaryModal();
        this.$nextTick(() => {
          this.drawRiverChart();
          if (typeof this.emitUserOperationsChange === 'function') {
            this.emitUserOperationsChange();
          }
        });
      } catch (e) {
        window.alert(`删除策略失败: ${e.message || e}`);
        this.deletingStrategy = false;
      }
    },

    formatArgs(args) {
      if (args === undefined || args === null) return '';
      if (typeof args === 'string') return args;
      try {
        return JSON.stringify(args, null, 2);
      } catch (e) {
        return String(args);
      }
    },

    cleanPlanArgs(args) {
      if (!args || typeof args !== 'object') return args ?? null;
      const cleaned = { ...args };
      // 防御：某些模型会把 reason / tool_name 等混进 args
      delete cleaned.reason;
      delete cleaned.Reason;
      delete cleaned.tool_name;
      delete cleaned.toolName;
      delete cleaned.ParentNode;
      delete cleaned.parentNode;
      delete cleaned.action;
      return cleaned;
    },

    showRoundSummary(round) {
      this.selectedRoundSummary = round;
      this.showRoundSummaryModal = true;
      this.$nextTick(() => {
        this.drawWordFreqChart(round);
        this.drawWordCloudChart(round);
      });
    },

    closeRoundSummaryModal() {
      this.showRoundSummaryModal = false;
      this.selectedRoundSummary = null;
    },

    // 导航到指定的chunk并高亮显示
    navigateToChunk(chunkId) {
      console.log('导航到chunk:', chunkId);
      
      // 1. 在roundsData中查找包含该chunk的query
      let targetCanvas = null;
      let targetRound = null;
      let targetQueryIndex = null;
      
      for (const round of this.roundsData) {
        if (!round.query_results) continue;
        
        for (let queryIndex = 0; queryIndex < round.query_results.length; queryIndex++) {
          const query = round.query_results[queryIndex];
          if (!query.rag_results) continue;
          
          // 检查是否包含该chunk
          const hasChunk = query.rag_results.some(rag => {
            const ragId = rag.retrieval_result?.id;
            return ragId === chunkId || 
                   ragId === `img_${chunkId}` ||
                   ragId === chunkId.replace('img_', '') ||
                   ragId?.toString() === chunkId.toString();
          });
          
          if (hasChunk) {
            targetRound = round.round_number;
            targetQueryIndex = queryIndex;
            targetCanvas = this.strategyCanvases[targetRound]?.[targetQueryIndex];
            break;
          }
        }
        
        if (targetCanvas) break;
      }
      
      if (!targetCanvas) {
        console.warn('未找到chunk:', chunkId);
        alert(`未找到chunk: ${chunkId}`);
        return;
      }

      // 2. 在全局地图中高亮显示该chunk
      const point = this.findPointById(chunkId);
      if (point) {
        // 高亮该点，使用多种ID格式确保能匹配到
        const highlightInfo = {
          branch_action: 'GROW', // 默认高亮为GROW
          score: 1.0,
          boostRadius: true // Evidence 点击后：半径加倍
        };
        
        // 使用多种ID格式设置高亮，确保能被getHighlightInfo找到
        this.highlightedPlanPoints[chunkId] = highlightInfo;
        if (point.id && point.id !== chunkId) {
          this.highlightedPlanPoints[point.id] = highlightInfo;
        }
        
        // 尝试从metadata中提取figure_id
        try {
          if (point.metadata) {
            let metadataObj = point.metadata;
            if (typeof metadataObj === 'string') {
              metadataObj = JSON.parse(metadataObj);
            }
            const figureId = metadataObj.figure_id || metadataObj.id;
            if (figureId && figureId !== chunkId) {
              this.highlightedPlanPoints[figureId] = highlightInfo;
            }
            // 检查嵌套的metadata
            if (metadataObj.metadata && typeof metadataObj.metadata === 'string') {
              const innerMetadata = JSON.parse(metadataObj.metadata);
              const innerFigureId = innerMetadata.figure_id || innerMetadata.id;
              if (innerFigureId && innerFigureId !== chunkId) {
                this.highlightedPlanPoints[innerFigureId] = highlightInfo;
              }
            }
          }
        } catch (e) {
          console.warn('解析metadata失败:', e);
        }
        
        if (this.globalMapMountId) {
          this.drawGlobalMap();
        }
      } else {
        console.warn('未找到chunk对应的点:', chunkId);
      }

      // 3. 重新绘制 river 图：让策略小矩形里的对应点也同步变大
      this.drawRiverChart();

      // 4. 重新缩放定位到目标策略画布中心
      this.$nextTick(() => {
        const refreshedTargetCanvas = this.strategyCanvases?.[targetRound]?.[targetQueryIndex];
        if (!refreshedTargetCanvas) return;
        const scale = 2.0;
        this.persistZoomTransform = {
          k: scale,
          x: this.svgWidth / 2 - refreshedTargetCanvas.centerX * scale,
          y: this.svgHeight / 2 - refreshedTargetCanvas.centerY * scale
        };
      });

      console.log(`已导航到chunk ${chunkId}，位置: 轮次${targetRound}，查询${targetQueryIndex}`);
    },

    drawWordFreqChart(round) {
      const container = d3.select(this.$refs.wordFreqChart);
      container.selectAll('*').remove();
      
      const wordFreq = this.extractKeywords(round);
      const data = Object.entries(wordFreq)
        .map(([word, freq]) => ({ word, freq }))
        .sort((a, b) => b.freq - a.freq)
        .slice(0, 20);
      
      if (data.length === 0) {
        container.append('p').text('暂无关键词数据');
        return;
      }
      
      const width = 400;
      const height = 300;
      const margin = { top: 20, right: 20, bottom: 60, left: 60 };
      
      const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);
      
      const xScale = d3.scaleBand()
        .domain(data.map(d => d.word))
        .range([margin.left, width - margin.right])
        .padding(0.2);
      
      const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.freq)])
        .nice()
        .range([height - margin.bottom, margin.top]);
      
      svg.selectAll('rect')
        .data(data)
        .enter()
        .append('rect')
        .attr('x', d => xScale(d.word))
        .attr('y', d => yScale(d.freq))
        .attr('width', xScale.bandwidth())
        .attr('height', d => height - margin.bottom - yScale(d.freq))
        .attr('fill', '#4A90E2')
        .attr('rx', 3);
      
      svg.append('g')
        .attr('transform', `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(xScale))
        .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .attr('text-anchor', 'end')
        .attr('dx', '-0.5em')
        .attr('dy', '0.5em');
      
      svg.append('g')
        .attr('transform', `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(yScale));
    },

    drawWordCloudChart(round) {
      const container = d3.select(this.$refs.wordCloudChart);
      container.selectAll('*').remove();
      
      const wordFreq = this.extractKeywords(round);
      const data = Object.entries(wordFreq)
        .map(([word, freq]) => ({ text: word, size: freq * 10 }))
        .sort((a, b) => b.size - a.size)
        .slice(0, 30);
      
      if (data.length === 0) {
        container.append('p').text('暂无关键词数据');
        return;
      }
      
      const width = 400;
      const height = 300;
      
      const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);
      
      const maxSize = d3.max(data, d => d.size);
      const sizeScale = d3.scaleLinear()
        .domain([0, maxSize])
        .range([12, 40]);
      
      // 改进的词云布局（螺旋布局）
      const centerX = width / 2;
      const centerY = height / 2;
      const maxRadius = Math.min(width, height) / 2.5;
      
      data.forEach((d, i) => {
        const angle = (i / data.length) * Math.PI * 2;
        const radius = (i / data.length) * maxRadius;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        
        svg.append('text')
          .attr('x', x)
          .attr('y', y)
          .attr('font-size', sizeScale(d.size))
          .attr('fill', d3.schemeCategory10[i % 10])
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .attr('font-weight', d.size > maxSize * 0.5 ? 'bold' : 'normal')
          .text(d.text);
      });
    },

    extractKeywords(round) {
      const wordFreq = {};
      const stopWords = new Set(['的', '是', '在', '了', '和', '与', '及', '等', '等', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'this', 'that', 'these', 'those']);
      
      if (round.query_results) {
        round.query_results.forEach(query => {
          if (query.orchestrator_plan?.plansummary) {
            let text = query.orchestrator_plan.plansummary;
            if (typeof text === 'string' && text.trim().startsWith('{')) {
              try {
                const o = JSON.parse(text.trim());
                if (o && typeof o === 'object') {
                  text = [o.answer, o.suggestion].filter(Boolean).join(' ');
                }
              } catch (e) {
                /* 保持原文 */
              }
            }
            const words = String(text).match(/[\u4e00-\u9fa5]+|[a-zA-Z]{2,}/g) || [];
            words.forEach(word => {
              const lowerWord = word.toLowerCase();
              if (word.length > 1 && !stopWords.has(lowerWord)) {
                wordFreq[word] = (wordFreq[word] || 0) + 1;
              }
            });
          }
          
          if (query.orchestrator_plan?.args?.query_intent) {
            const text = query.orchestrator_plan.args.query_intent;
            const words = text.match(/[\u4e00-\u9fa5]+|[a-zA-Z]{2,}/g) || [];
            words.forEach(word => {
              const lowerWord = word.toLowerCase();
              if (word.length > 1 && !stopWords.has(lowerWord)) {
                wordFreq[word] = (wordFreq[word] || 0) + 1;
              }
            });
          }
        });
      }
      
      return wordFreq;
    },

    showDetail(retrievalResult, evaluation = null, context = null) {
      // 如果传入了 evaluation，将其附加到 retrievalResult 上
      const dataWithEvaluation = {
        ...retrievalResult,
        evaluation: evaluation || retrievalResult.evaluation
      };
      
      // 转换数据格式为ItemDetail需要的格式（复用store中的逻辑）
      const processedData = this.processRagResultForDetail(dataWithEvaluation);
      
      // 显示弹窗
      this.selectedPointDetail = processedData;
      this.selectedPointContext = context || null;
      this.showPointDetailModal = true;
    },
    
    // 处理RAG结果为ItemDetail需要的格式（复用store中的逻辑）
    processRagResultForDetail(ragResult) {
      ragResult = patchRagMetadataWithMapPoint(ragResult, (id) => this.findPointById(id));
      // 解析metadata（可能是JSON字符串）
      let parsedMetadata = null;
      if (ragResult.metadata?.metadata) {
        if (typeof ragResult.metadata.metadata === 'string') {
          try {
            parsedMetadata = JSON.parse(ragResult.metadata.metadata);
          } catch (e) {
            console.warn('Failed to parse metadata:', e);
          }
        } else {
          parsedMetadata = ragResult.metadata.metadata;
        }
      }
      
      // 获取数据类型
      // 注意：metadata_search 的 type 可能在嵌套的 metadata.metadata 里
      let dataType = ragResult.metadata?.type || parsedMetadata?.type || 'unknown';
      if (!ragResult.metadata?.type && !parsedMetadata?.type && (ragResult.metadata?.full_json || ragResult.metadata?.savepath || ragResult.metadata?.save_path)) {
        dataType = 'picture';
      }
      
      // 兼容不同数据源的 type 命名
      if (dataType === 'text') dataType = 'texture';
      if (dataType === 'figure' || dataType === 'image') dataType = 'picture';
      
      // 获取save_path（从parsedMetadata或metadata中）
      let savePath = parsedMetadata?.save_path || ragResult.metadata?.save_path || ragResult.metadata?.savepath;
      if (!savePath && ragResult.metadata?.full_json) {
        try {
          const fullJson = JSON.parse(ragResult.metadata.full_json);
          savePath = fullJson.save_path || fullJson.savepath;
        } catch (e) {
          // ignore
        }
      }
      
      // chunk 正文在不同工具返回结构可能不同（与 interactiveReportItem.js 一致）
      let textContent = '';
      if (ragResult.content) {
        if (typeof ragResult.content === 'string') {
          textContent = ragResult.content;
        } else if (typeof ragResult.content === 'object' && ragResult.content.text != null) {
          textContent = String(ragResult.content.text);
        }
      }
      if (!textContent && typeof ragResult.metadata?.content === 'string') {
        textContent = ragResult.metadata.content;
      }
      if (!textContent && typeof parsedMetadata?.content === 'string') {
        textContent = parsedMetadata.content;
      }

      const paperTitleForDetail = parsedMetadata?.paper_title || '';
      const titleFromMeta =
        parsedMetadata?.figure_title ||
        ragResult.content?.title ||
        ragResult.metadata?.title ||
        paperTitleForDetail ||
        '';
      const displayTitle =
        (titleFromMeta && String(titleFromMeta).trim()) ||
        (textContent ? String(textContent).replace(/\s+/g, ' ').trim() : '') ||
        ragResult.id ||
        'No Title';

      // 提取相对路径
      let relativePath = '';
      if (savePath) {
        const normalizedPath = savePath.replace(/\\/g, '/');
        // 处理新的 llmvis 数据源
        const mdLlmvisIndex = normalizedPath.indexOf('md-llmvis');
        const paperMdIndex = normalizedPath.indexOf('paper_md');
        
        if (mdLlmvisIndex !== -1) {
          // 由于 md-llmvis 里的图片路径通常是: md-llmvis/images/MinerU_markdown_PaperName/figure_2.jpg
          // 我们只需要 "MinerU_markdown_PaperName/figure_2.jpg"
          const subPath = normalizedPath.substring(mdLlmvisIndex + 'md-llmvis'.length + 1);
          // 去掉开头的 "images/"
          if (subPath.startsWith('images/')) {
            relativePath = `/static-llmvis/${subPath.substring('images/'.length)}`;
          } else {
            relativePath = `/static-llmvis/${subPath}`;
          }
        } else if (paperMdIndex !== -1) {
          relativePath = normalizedPath.substring(paperMdIndex + 'paper_md'.length + 1);
        } else {
          const pathParts = normalizedPath.split('/');
          if (pathParts.length >= 2) {
            const paperName = pathParts[pathParts.length - 2];
            const figureName = pathParts[pathParts.length - 1];
            relativePath = `${paperName}/${figureName}`;
          }
        }
      }
      
      // 处理河流图数据，转换为DetailView需要的格式
      return {
        id: ragResult.id,
        type: dataType,
        title: displayTitle,
        relative_path: relativePath,
        key_entities: parsedMetadata?.key_entities || ragResult.metadata?.key_entities || [],
        text_content: textContent,
        concise_summary: parsedMetadata?.concise_summary || ragResult.metadata?.concise_summary || '',
        inferred_insight: parsedMetadata?.inferred_insight || ragResult.metadata?.inferred_insight || '',
        paper_title: paperTitleForDetail,
        score: ragResult.score,
        branch_action: ragResult.evaluation?.branch_action || 'UNKNOWN',
        parsed_metadata: parsedMetadata || null,
        original_data: {
          ...ragResult,
          evaluation: ragResult.evaluation || null
        }
      };
    },
    
    closePointDetailModal() {
      this.showPointDetailModal = false;
      this.selectedPointDetail = null;
      this.selectedPointContext = null;
    },

    isRagResultUserDeleted(query, rag) {
      const id = rag?.retrieval_result?.id;
      if (!id) return false;
      const deletes = query?.orchestrator_plan?.userdo?.delete;
      return Array.isArray(deletes) && deletes.some((x) => String(x?.target_evidence_id || '') === String(id));
    },

    ensurePlanUserDelete(query, resultId) {
      if (!query || !query.orchestrator_plan || !resultId) return;
      const op = query.orchestrator_plan;
      if (!op.userdo || typeof op.userdo !== 'object') {
        op.userdo = {};
      }
      if (!Array.isArray(op.userdo.delete)) {
        op.userdo.delete = [];
      }
      if (!op.userdo.delete.some((x) => String(x?.target_evidence_id || '') === String(resultId))) {
        op.userdo.delete.push({
          action: 'delete',
          target_evidence_id: String(resultId),
          timestamp: new Date().toISOString(),
        });
      }
    },

    markRagResultPruned(rag, resultId) {
      if (!rag) return;
      if (!rag.evaluation || typeof rag.evaluation !== 'object') {
        rag.evaluation = {
          target_evidence_id: resultId,
          branch_action: 'PRUNE',
          extracted_insight: '',
          scores: {},
          reason: 'User deleted this evidence item.',
          suggested_keywords: [],
        };
      } else {
        rag.evaluation.branch_action = 'PRUNE';
        if (!rag.evaluation.target_evidence_id) {
          rag.evaluation.target_evidence_id = resultId;
        }
        if (!rag.evaluation.reason) {
          rag.evaluation.reason = 'User deleted this evidence item.';
        }
      }
      rag.evaluation.user_action = 'delete';
    },

    applyRagDeleteLocally(ctx, resultId) {
      const query = ctx?.query;
      const rag = ctx?.rag;
      this.ensurePlanUserDelete(query, resultId);
      this.markRagResultPruned(rag, resultId);
      this.syncDeleteIntoExperimentResult(ctx, resultId);
    },

    syncDeleteIntoExperimentResult(ctx, resultId) {
      const er = this.experimentResult;
      if (!er || !Array.isArray(er.iterations) || !ctx || !ctx.query) return;
      if (er.session_id && ctx.sessionId && er.session_id !== ctx.sessionId) return;
      const it = er.iterations.find((x) => Number(x.round_number) === Number(ctx.roundNumber));
      const qr = it?.query_results?.find((x) => this.queryResultPlanKey(x) === this.queryResultPlanKey(ctx.query));
      if (!qr) return;
      this.ensurePlanUserDelete(qr, resultId);
      const rag = (qr.rag_results || []).find((x) => String(x?.retrieval_result?.id || '') === String(resultId));
      if (rag) this.markRagResultPruned(rag, resultId);
    },

    /** 与底栏 / 筛选一致：evaluation.branch_action → KEEP | GROW | PRUNE | UNKNOWN */
    strategyCardNormalizeBranchAction(rag) {
      const raw = rag?.evaluation?.branch_action;
      const a =
        raw == null || String(raw).trim() === ''
          ? 'UNKNOWN'
          : String(raw).trim().toUpperCase();
      if (a === 'KEEP' || a === 'GROW' || a === 'PRUNE') return a;
      return 'UNKNOWN';
    },

    strategyMiniMapEvalFilterIsActive(card, action) {
      return !!(card && card.key && this.strategyMiniMapEvalFilter[card.key] === action);
    },

    toggleStrategyMiniMapEvalFilter(card, action) {
      if (!card || !card.key) return;
      const k = card.key;
      const next = { ...this.strategyMiniMapEvalFilter };
      if (next[k] === action) delete next[k];
      else next[k] = action;
      this.strategyMiniMapEvalFilter = next;
      this.$nextTick(() => this.renderAllMiniMaps());
    },

    /** 策略卡底栏：按 evaluation.branch_action 聚合（与小地图筛选一致） */
    strategyCardEvalCounts(card) {
      const q = card?.query;
      const list = q?.rag_results;
      const out = { KEEP: 0, GROW: 0, PRUNE: 0, UNKNOWN: 0 };
      if (!Array.isArray(list)) return out;
      for (const rag of list) {
        const a = this.strategyCardNormalizeBranchAction(rag);
        if (a === 'KEEP') out.KEEP += 1;
        else if (a === 'GROW') out.GROW += 1;
        else if (a === 'PRUNE') out.PRUNE += 1;
        else out.UNKNOWN += 1;
      }
      return out;
    },

    strategyCardEvalStatSegments(card) {
      const c = this.strategyCardEvalCounts(card);
      return [
        { action: 'KEEP', label: 'KEEP', count: c.KEEP, color: '#eec316' },
        { action: 'GROW', label: 'GROW', count: c.GROW, color: '#379b61' },
        { action: 'PRUNE', label: 'PRUNE', count: c.PRUNE, color: '#dc3545' },
        { action: 'UNKNOWN', label: 'UNKNOWN', count: c.UNKNOWN, color: '#9AA3AD' },
      ];
    },

    /** 与 drawStrategyMap 中单个 RAG 点的类型推断一致（picture ⇔ pic，其余⇔text） */
    strategyCardResolveRagIsPicture(rr) {
      if (!rr || typeof rr !== 'object') return false;
      let rawType = rr?.metadata?.type || null;
      try {
        if (!rawType && rr?.metadata?.metadata) {
          const nested = rr.metadata.metadata;
          if (typeof nested === 'string') {
            const parsed = JSON.parse(nested);
            rawType = parsed?.type || null;
          } else if (typeof nested === 'object') {
            rawType = nested?.type || null;
          }
        }
        if (!rawType && (rr?.metadata?.full_json || rr?.metadata?.savepath || rr?.metadata?.save_path)) {
          rawType = 'picture';
        }
        if (!rawType && rr?.metadata?.metadata && typeof rr.metadata.metadata === 'string') {
          const parsed = JSON.parse(rr.metadata.metadata);
          if (parsed.full_json || parsed.savepath || parsed.save_path) {
            rawType = 'picture';
          }
        }
      } catch (e) {
        /* ignore */
      }
      if (rawType === 'text') rawType = 'texture';
      if (rawType === 'figure' || rawType === 'image') rawType = 'picture';
      if (!rawType) {
        try {
          if (rr.metadata && typeof rr.metadata === 'string') {
            const meta = JSON.parse(rr.metadata);
            if (meta.type === 'texture' || meta.type === 'text') rawType = 'texture';
            else if (meta.type === 'picture' || meta.type === 'figure' || meta.type === 'image') {
              rawType = 'picture';
            }
          }
          if (!rawType && rr.id && String(rr.id).includes('Figure')) rawType = 'picture';
        } catch (e) {
          /* ignore */
        }
      }
      if (!rawType) {
        try {
          if (rr.metadata && typeof rr.metadata === 'object') {
            if (rr.metadata.type === 'texture' || rr.metadata.type === 'text') rawType = 'texture';
            else if (rr.metadata.type === 'picture' || rr.metadata.type === 'figure' || rr.metadata.type === 'image') {
              rawType = 'picture';
            }
          }
        } catch (e) {
          /* ignore */
        }
      }
      return rawType === 'picture';
    },

    strategyCardMediaCounts(card) {
      const list = card?.query?.rag_results;
      let pic = 0;
      let text = 0;
      if (!Array.isArray(list)) return { pic: 0, text: 0 };
      for (const rag of list) {
        const rr = rag?.retrieval_result || {};
        if (this.strategyCardResolveRagIsPicture(rr)) pic += 1;
        else text += 1;
      }
      return { pic, text };
    },

    strategyCardMediaStatsLine(card) {
      const { pic, text } = this.strategyCardMediaCounts(card);
      return `pic:${pic} text:${text}`;
    },

    resolvePlanGridRowCol(query, iterationRoundNumber, queryArrIndex) {
      const rn = Number(iterationRoundNumber);
      let row = Number(queryArrIndex) + 1;
      let col = Number.isFinite(rn) ? rn : 0;
      const gp = query?.orchestrator_plan?.grid_pos;
      if (Array.isArray(gp) && gp.length >= 1) {
        const r0 = Number(gp[0]);
        if (Number.isFinite(r0) && r0 >= 1) row = Math.floor(r0);
      }
      if (Array.isArray(gp) && gp.length >= 2) {
        const c0 = Number(gp[1]);
        if (Number.isFinite(c0) && c0 >= 1) col = Math.floor(c0);
      }
      return [row, col];
    },

    iterRoundsMutableForSession(sessionId) {
      const sid = String(sessionId || '').trim();
      const activeSid = String(this.activeSessionId || '').trim();
      if (sid && activeSid && sid !== activeSid) {
        const col = (this.completedQuestionColumns || []).find((c) => String(c.sessionId || '').trim() === sid);
        return col ? col.roundsData : null;
      }
      if (sid && activeSid && sid === activeSid) {
        return this.getActiveSessionBaseRounds() || [];
      }
      return this.roundsData || [];
    },

    shiftSessionStrategyColsAfterPlanDelete(sessionId, targetQr, iterationRn, queryArrIndex) {
      const [delRow, delCol] = this.resolvePlanGridRowCol(targetQr, iterationRn, queryArrIndex);
      const rounds = this.iterRoundsMutableForSession(sessionId);
      if (!Array.isArray(rounds)) return;
      rounds.forEach((round) => {
        if (!round?.query_results) return;
        const rn = Number(round.round_number);
        round.query_results.forEach((qr, j) => {
          if (!qr || qr === targetQr || riverGrid.isStrategySlotTombstone(qr)) return;
          const [r2, c2] = this.resolvePlanGridRowCol(qr, rn, j);
          if (r2 === delRow && c2 > delCol) {
            qr.orchestrator_plan = { ...(qr.orchestrator_plan || {}) };
            qr.orchestrator_plan.grid_pos = [r2, c2 - 1];
          }
        });
      });
    },

    /** 将策略挪到 round_number === grid_pos[1] 的列（否则仅改 grid_pos 不会触发小矩形水平左移） */
    repackRoundQueryResultsByGridRow(round) {
      if (!round?.query_results) return;
      const raw = [...round.query_results].filter((x) => x != null);
      raw.sort((a, b) => {
        const ta = riverGrid.isStrategySlotTombstone(a);
        const tb = riverGrid.isStrategySlotTombstone(b);
        if (ta && !tb) return 1;
        if (!ta && tb) return -1;
        const ra = (() => {
          const gp = a?.orchestrator_plan?.grid_pos;
          if (Array.isArray(gp) && gp.length >= 1) {
            const r0 = Number(gp[0]);
            if (Number.isFinite(r0) && r0 >= 1) return r0;
          }
          return 1e6;
        })();
        const rb = (() => {
          const gp = b?.orchestrator_plan?.grid_pos;
          if (Array.isArray(gp) && gp.length >= 1) {
            const r0 = Number(gp[0]);
            if (Number.isFinite(r0) && r0 >= 1) return r0;
          }
          return 1e6;
        })();
        return ra - rb;
      });
      round.query_results = raw;
    },

    migrateOrchestratorPlansToGridColumnRounds(sessionId) {
      const rounds = this.iterRoundsMutableForSession(sessionId);
      if (!Array.isArray(rounds) || !rounds.length) return;
      const byCol = new Map();
      rounds.forEach((r) => {
        if (r && r.round_number != null) byCol.set(Number(r.round_number), r);
      });
      const pending = [];
      rounds.forEach((round) => {
        const hrs = Number(round.round_number);
        (round.query_results || []).forEach((qr) => {
          if (!qr || riverGrid.isStrategySlotTombstone(qr)) return;
          const gp = qr?.orchestrator_plan?.grid_pos;
          let desired = hrs;
          if (Array.isArray(gp) && gp.length >= 2) {
            const c = Number(gp[1]);
            if (Number.isFinite(c) && c >= 1) desired = Math.floor(c);
          }
          if (desired !== hrs) pending.push({ qr, fromRound: round, toCol: desired });
        });
      });
      pending.forEach(({ qr, fromRound, toCol }) => {
        const dest = byCol.get(toCol);
        if (!dest || dest === fromRound) return;
        fromRound.query_results = (fromRound.query_results || []).filter((x) => x !== qr);
        dest.query_results = dest.query_results || [];
        dest.query_results.push(qr);
      });
      rounds.forEach((r) => this.repackRoundQueryResultsByGridRow(r));
    },

    applyPlanStrategyDeleteLocal(card, ts) {
      const sid = String(card?.sessionId || '').trim();
      const round = this.getRoundRef(card.roundNumber, sid);
      if (!round || !Array.isArray(round.query_results)) return false;
      let qi = Number(card.queryIndex);
      let targetQr = null;
      if (card.query) {
        const i0 = round.query_results.indexOf(card.query);
        if (i0 >= 0) {
          qi = i0;
          targetQr = card.query;
        }
      }
      if (!targetQr) {
        if (!Number.isFinite(qi) || qi < 0 || qi >= round.query_results.length) return false;
        targetQr = round.query_results[qi];
      }
      if (!targetQr || riverGrid.isStrategySlotTombstone(targetQr)) return false;
      this.shiftSessionStrategyColsAfterPlanDelete(sid, targetQr, Number(card.roundNumber), qi);
      const op = { ...(targetQr.orchestrator_plan || {}) };
      const userdo = { ...(op.userdo || {}) };
      const stratDel = Array.isArray(userdo.strategy_delete) ? [...userdo.strategy_delete] : [];
      stratDel.push({ action: 'delete', timestamp: String(ts || '').trim() });
      userdo.strategy_delete = stratDel;
      op.userdo = userdo;
      op.grid_pos = [0, 0];
      targetQr.orchestrator_plan = op;
      this.migrateOrchestratorPlansToGridColumnRounds(sid);
      const k = card.key != null ? String(card.key) : '';
      if (k && this.strategyMiniMapEvalFilter && typeof this.strategyMiniMapEvalFilter === 'object') {
        const nextF = { ...this.strategyMiniMapEvalFilter };
        delete nextF[k];
        this.strategyMiniMapEvalFilter = nextF;
      }
      if (k && this.strategyCardDraftQueries && typeof this.strategyCardDraftQueries === 'object') {
        const nextD = { ...this.strategyCardDraftQueries };
        delete nextD[k];
        this.strategyCardDraftQueries = nextD;
      }
      return true;
    },

    async deleteStrategyCard(card) {
      const sid = String(card?.sessionId || '').trim();
      if (!sid || sid === 'empty') {
        window.alert('无法删除：缺少会话信息。');
        return;
      }
      const sourcePath = (this.forkExperimentSource || this.selectedDataFile || '').trim();
      if (!sourcePath) {
        window.alert('请先加载实验 JSON（fork 源路径），以便落盘删除记录。');
        return;
      }
      if (
        !window.confirm(
          '确定删除该策略卡片？将写入 userdo.strategy_delete，并把 grid_pos 置为 [0,0]；同行列坐标更大的策略会整体左移（grid_pos 第二维 -1）。',
        )
      ) {
        return;
      }
      const ts = new Date().toISOString().split('.')[0];
      if (!this.applyPlanStrategyDeleteLocal(card, ts)) {
        window.alert('删除未能应用（可能已为删除占位或索引无效）。');
        return;
      }
      try {
        await this.persistPlanUserdoBatch([
          {
            action: 'plan_strategy_delete',
            session_id: sid,
            round_number: card.roundNumber,
            query_index: card.queryIndex,
            timestamp: ts,
          },
        ]);
        const activeSid = String(this.activeSessionId || '').trim();
        if (sid && activeSid && sid !== activeSid) {
          const col = (this.completedQuestionColumns || []).find((c) => String(c.sessionId || '').trim() === sid);
          if (col && col.roundsData) col.roundsData = [...col.roundsData];
        } else if (this.roundsData && this.roundsData.length > 0) {
          this.roundsData = [...(this.roundsData || [])];
        } else {
          const col = (this.completedQuestionColumns || []).find((c) => String(c.sessionId || '').trim() === sid);
          if (col && col.roundsData) col.roundsData = [...col.roundsData];
          else this.completedQuestionColumns = [...(this.completedQuestionColumns || [])];
        }
        this.$nextTick(() => {
          this.drawRiverChart();
          if (typeof this.emitUserOperationsChange === 'function') {
            this.emitUserOperationsChange();
          }
        });
      } catch (e) {
        window.alert(`删除已在前端生效，但落盘失败（请重启后端并重试）：${e.message || e}`);
      }
    },

    /** 策略卡 userdo：在 orchestrator_plan.userdo 下追加 continue / regenerate 记录并落盘 fork JSON */
    appendPlanUserdoContinueLocal(roundNumber, sessionId, queryIndex, newIntent) {
      const sid = String(sessionId || '').trim();
      const rr = this.getRoundRef(Number(roundNumber), sid);
      const q = rr?.query_results?.[Number(queryIndex)];
      const op = q?.orchestrator_plan;
      if (!op || typeof op !== 'object') return;
      if (!op.userdo || typeof op.userdo !== 'object') {
        op.userdo = {};
      }
      if (!Array.isArray(op.userdo.continue)) {
        op.userdo.continue = [];
      }
      const ts = new Date().toISOString().split('.')[0];
      op.userdo.continue.push({
        action: 'continue',
        new: String(newIntent || '').trim(),
        timestamp: ts,
      });
    },

    appendPlanUserdoRegenerateLocal(roundNumber, sessionId, queryIndex, beforeIntent) {
      const sid = String(sessionId || '').trim();
      const rr = this.getRoundRef(Number(roundNumber), sid);
      const q = rr?.query_results?.[Number(queryIndex)];
      const op = q?.orchestrator_plan;
      if (!op || typeof op !== 'object') return;
      if (!op.userdo || typeof op.userdo !== 'object') {
        op.userdo = {};
      }
      if (!Array.isArray(op.userdo.regenerate)) {
        op.userdo.regenerate = [];
      }
      const ts = new Date().toISOString().split('.')[0];
      op.userdo.regenerate.push({
        action: 'regenerate',
        before: String(beforeIntent || '').trim(),
        timestamp: ts,
      });
    },

    async persistPlanUserdoBatch(operations) {
      const sourcePath = (this.forkExperimentSource || this.selectedDataFile || '').trim();
      if (!sourcePath || !Array.isArray(operations) || operations.length === 0) return;
      const sid0 = String(operations[0]?.session_id || this.activeSessionId || '').trim();
      const resp = await fetch('/api/experiment-rag-actions-batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_path: sourcePath,
          session_id: sid0,
          operations,
        }),
      });
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok || data.ok === false) {
        throw new Error(data.detail || data.error || `HTTP ${resp.status}`);
      }
      if (data.path) {
        this.forkExperimentSource = data.path;
        this.selectedDataFile = data.path;
      }
    },

    async persistRagDelete(ctx, resultId) {
      const sourcePath = (this.forkExperimentSource || this.selectedDataFile || '').trim();
      if (!sourcePath) {
        throw new Error('未找到当前实验 JSON 来源文件');
      }
      const plan = ctx?.query?.orchestrator_plan || {};
      const resp = await fetch('/api/experiment-rag-action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'delete',
          source_path: sourcePath,
          session_id: ctx?.sessionId || this.activeSessionId || '',
          round_number: ctx?.roundNumber,
          plan_tool: plan.tool_name || '',
          plan_args: plan.args || {},
          result_id: resultId,
        }),
      });
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok || !data.ok) {
        if (resp.status === 404) {
          throw new Error('后端删除保存接口未生效或目标点未找到；请先重启 python server.py 后再试');
        }
        throw new Error(data.detail || `HTTP ${resp.status}`);
      }
      if (data.path) {
        this.forkExperimentSource = data.path;
        this.selectedDataFile = data.path;
      }
      return data;
    },

    async deleteSelectedRagPoint() {
      const ctx = this.selectedPointContext;
      const resultId = this.selectedPointDetail?.id || ctx?.rag?.retrieval_result?.id;
      if (!ctx || !resultId) return;
      try {
        this.applyRagDeleteLocally(ctx, resultId);
        await this.persistRagDelete(ctx, resultId);
        this.closePointDetailModal();
        this.$nextTick(() => this.drawRiverChart());
      } catch (error) {
        console.error('Failed to delete evidence point:', error);
        alert(`Failed to delete evidence point: ${error.message || 'unknown error'}`);
      }
    },

    changePointEvalAction(newAction) {
      const ctx = this.selectedPointContext;
      const resultId = this.selectedPointDetail?.id || ctx?.rag?.retrieval_result?.id;
      if (!ctx || !resultId) return;

      const originalAction = ctx.rag?.evaluation?.branch_action || 'UNKNOWN';

      const existingIdx = this.pendingPointOperations.findIndex(p => p.target_evidence_id === resultId);

      if (newAction === originalAction) {
        if (existingIdx >= 0) this.pendingPointOperations.splice(existingIdx, 1);
      } else {
        const ts = new Date().toISOString().split('.')[0];
        const plan = ctx.query?.orchestrator_plan || {};
        if (existingIdx >= 0) {
          this.pendingPointOperations[existingIdx].after = newAction;
          this.pendingPointOperations[existingIdx].timestamp = ts;
        } else {
          this.pendingPointOperations.push({
            action: 'point',
            target_evidence_id: resultId,
            timestamp: ts,
            before: originalAction,
            after: newAction,
            ctx: ctx,
            sessionId: ctx.sessionId || this.activeSessionId || '',
            roundNumber: ctx.roundNumber,
            planTool: plan.tool_name || '',
            planArgs: plan.args || {}
          });
        }
      }
      this.emitUserOperationsChange();
    },

    async applyPendingOperations(row) {
      const opsToApply = this.pendingPointOperations.filter(
        p => p.sessionId === row.sessionId && p.roundNumber === row.roundNumber && p.planTool === row.toolName
      );
      if (opsToApply.length === 0) return;

      const sourcePath = this.forkExperimentSource || this.selectedDataFile;
      if (!sourcePath) return;

      try {
        const resp = await fetch('/api/experiment-rag-actions-batch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            source_path: sourcePath,
            session_id: row.sessionId,
            operations: opsToApply
          }),
        });
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok || !data.ok) {
          throw new Error(data.detail || `HTTP ${resp.status}`);
        }
        if (data.path) {
          this.forkExperimentSource = data.path;
          this.selectedDataFile = data.path;
        }

        // Apply locally
        opsToApply.forEach(op => {
          if (!op.ctx || !op.ctx.rag) return;
          const ev = op.ctx.rag.evaluation;
          if (ev) {
             ev.branch_action = op.after;
          }
          
          if (!op.ctx.query || !op.ctx.query.orchestrator_plan) return;
          const planUserDo = op.ctx.query.orchestrator_plan.userdo || {};
          const points = planUserDo.point || [];
          const existing = points.find(p => p.target_evidence_id === op.target_evidence_id);
          if (existing) {
             existing.after = op.after;
             existing.timestamp = op.timestamp;
          } else {
             points.push({
               action: 'point',
               target_evidence_id: op.target_evidence_id,
               timestamp: op.timestamp,
               before: op.before,
               after: op.after
             });
          }
          planUserDo.point = points;
          op.ctx.query.orchestrator_plan.userdo = planUserDo;
        });

        this.pendingPointOperations = this.pendingPointOperations.filter(p => !opsToApply.includes(p));
        
        this.closePointDetailModal();
        this.$nextTick(() => {
          this.drawRiverChart();
          this.emitUserOperationsChange();
        });
      } catch (error) {
        console.error('Failed to apply pending operations:', error);
        alert(`Failed to apply: ${error.message}`);
      }
    },
    
    // 高亮全局地图中策略卡片对应的点
    highlightPlanPointsInGlobalMap(query) {
      if (!query.rag_results || query.rag_results.length === 0) {
        return;
      }

      // 清空之前的高亮
      this.highlightedPlanPoints = {};

      // 遍历策略的所有结果，提取节点ID和评估信息
      query.rag_results.forEach(rag => {
        const nodeId = rag.retrieval_result?.id;
        if (!nodeId) return;

        // 获取评估信息
        let branchAction = rag.evaluation?.branch_action || 'UNKNOWN';
        
        // 如果是在逐步渲染模式下，检查 planStates
        for (const [, planState] of Object.entries(this.planStates)) {
          if (planState.node_ids.includes(nodeId)) {
            if (planState.evaluated_nodes[nodeId]) {
              branchAction = planState.evaluated_nodes[nodeId].branch_action || 'UNKNOWN';
            } else {
              branchAction = 'PENDING'; // 检索完成但未评估
            }
            break;
          }
        }

        // 在全局地图中查找匹配的点（支持多种ID格式）
        const idStr = nodeId.toString();
        let matchedPoint = null;
        
        // 方法1: 直接匹配 id 字段
        matchedPoint = this.globalMapPoints.find(p => {
          if (p.id === idStr || p.id === nodeId) return true;
          return false;
        });
        
        // 方法2: 匹配 metadata 中的 figure_id 或 id
        if (!matchedPoint) {
          matchedPoint = this.globalMapPoints.find(p => {
            try {
              if (p.metadata) {
                let metadataObj = p.metadata;
                if (typeof metadataObj === 'string') {
                  metadataObj = JSON.parse(metadataObj);
                }
                if (metadataObj.figure_id === idStr || metadataObj.id === idStr) {
                  return true;
                }
                // 检查嵌套的metadata
                if (metadataObj.metadata && typeof metadataObj.metadata === 'string') {
                  const innerMetadata = JSON.parse(metadataObj.metadata);
                  if (innerMetadata.figure_id === idStr || innerMetadata.id === idStr) {
                    return true;
                  }
                }
              }
            } catch (e) {
              // 忽略解析错误
            }
            return false;
          });
        }

        // 如果找到匹配的点，存储高亮信息（使用全局地图点的实际ID）
        if (matchedPoint) {
          const actualId = matchedPoint.id || idStr;
          this.highlightedPlanPoints[actualId] = {
            branch_action: branchAction,
            evaluation: rag.evaluation
          };
        } else {
          // 如果没找到，也存储原始ID（可能后续会匹配）
          this.highlightedPlanPoints[idStr] = {
            branch_action: branchAction,
            evaluation: rag.evaluation
          };
        }
      });

      const highlightedCount = Object.keys(this.highlightedPlanPoints).length;
      console.log(`高亮了 ${highlightedCount} 个点在全局地图中`);
      
      // 重新绘制全局地图以应用高亮效果
      if (this.globalMapPoints.length > 0) {
        this.drawGlobalMap();
      }
    },

    // 取消全局地图的高亮
    clearGlobalMapHighlight() {
      this.highlightedPlanPoints = {};
      this.globalMapSelectedClusterId = null;
      if (this.globalMapPoints.length > 0) {
        this.drawGlobalMap();
      }
    },

    /** 将每个点归属到最近的聚类质心（与 cluster_keywords 中 centroid_2d 同坐标系） */
    assignClusterIdsToPoints() {
      const clusters = this.clusterKeywords || [];
      if (!clusters.length || !this.globalMapPoints.length) {
        this.globalMapPoints.forEach((p) => {
          delete p._clusterId;
        });
        return;
      }
      const centroids = clusters.map((c) => ({
        id: c.cluster_id,
        cx: c.centroid_2d[0],
        cy: c.centroid_2d[1],
      }));
      this.globalMapPoints.forEach((p) => {
        let bestId = centroids[0].id;
        let bestD = Infinity;
        for (const c of centroids) {
          const dx = p.x - c.cx;
          const dy = p.y - c.cy;
          const dist = dx * dx + dy * dy;
          if (dist < bestD) {
            bestD = dist;
            bestId = c.id;
          }
        }
        p._clusterId = bestId;
      });
    },

    /**
     * 聚类标签锚点：使用当前底图上归属该聚类的数据点 (x,y) 的均值（与散点一致）。
     * 无归属点时回退到 cluster_keywords 中的 centroid_2d。
     */
    getClusterLabelAnchorDataXY(cluster) {
      const id = cluster && cluster.cluster_id;
      const pts = (this.globalMapPoints || []).filter((p) => p && p._clusterId === id);
      if (pts.length === 0) {
        if (cluster && cluster.centroid_2d && cluster.centroid_2d.length >= 2) {
          return [cluster.centroid_2d[0], cluster.centroid_2d[1]];
        }
        return [0, 0];
      }
      let sx = 0;
      let sy = 0;
      for (const p of pts) {
        sx += p.x;
        sy += p.y;
      }
      const n = pts.length;
      return [sx / n, sy / n];
    },

    globalMapPointerToLocalPlot(event) {
      // 必须用 contentGroup：与圆点/密度同一「绘图局部坐标系」。用 outerGroup + invert(zoom)
      // 在部分浏览器/SVG CTM 链路上会与 cx/cy 不一致，导致框选矩形不显示、选点为空。
      if (!this.globalMapContentGroupNode) return null;
      return d3.pointer(event, this.globalMapContentGroupNode);
    },

    computeIdsInRect(r) {
      const xa = Math.min(r.x1, r.x2);
      const xb = Math.max(r.x1, r.x2);
      const ya = Math.min(r.y1, r.y2);
      const yb = Math.max(r.y1, r.y2);
      const ids = [];
      const seen = new Set();
      for (const p of this.globalMapPoints || []) {
        const px = this.globalMapXScale(p.x);
        const py = this.globalMapYScale(p.y);
        if (px >= xa && px <= xb && py >= ya && py <= yb) {
          const id = String(p.id);
          if (!seen.has(id)) {
            seen.add(id);
            ids.push(id);
          }
        }
      }
      return ids;
    },

    /** 将小地图绘图局部坐标中的矩形转为数据域 (x,y)，与 globalMapPoints 一致 */
    plotRectToDataRect2d(r) {
      if (!r || !this.globalMapXScale || !this.globalMapYScale) return null;
      const xa = Math.min(r.x1, r.x2);
      const xb = Math.max(r.x1, r.x2);
      const ya = Math.min(r.y1, r.y2);
      const yb = Math.max(r.y1, r.y2);
      if (Math.abs(xb - xa) <= 2 || Math.abs(yb - ya) <= 2) return null;
      const yA = this.globalMapYScale.invert(ya);
      const yB = this.globalMapYScale.invert(yb);
      return [
        [this.globalMapXScale.invert(xa), Math.min(yA, yB)],
        [this.globalMapXScale.invert(xb), Math.max(yA, yB)]
      ];
    },

    _mapBoxDragStartLocalPlot(event) {
      const p = this.globalMapPointerToLocalPlot(event);
      if (!p) return;
      this.mapBoxDragging = true;
      this.mapBoxDragRect = { x1: p[0], y1: p[1], x2: p[0], y2: p[1] };
      const move = (ev) => {
        if (!this.mapBoxDragging) return;
        const q = this.globalMapPointerToLocalPlot(ev);
        if (!q) return;
        this.mapBoxDragRect = {
          x1: this.mapBoxDragRect.x1,
          y1: this.mapBoxDragRect.y1,
          x2: q[0],
          y2: q[1]
        };
        this.drawGlobalMap();
      };
      const up = () => {
        this.mapBoxDragging = false;
        window.removeEventListener('mousemove', move);
        window.removeEventListener('mouseup', up);
        const r = this.mapBoxDragRect;
        if (r && Math.abs(r.x2 - r.x1) > 2 && Math.abs(r.y2 - r.y1) > 2) {
          this.mapRagPendingIds = this.computeIdsInRect(r);
          this.mapRagRect2d = this.plotRectToDataRect2d(r);
        } else {
          this.mapRagPendingIds = [];
          this.mapRagRect2d = null;
        }
        this.mapBoxDragRect = null;
        this.drawGlobalMap();
        this.$nextTick(() => this.emitMapToolbar());
      };
      window.addEventListener('mousemove', move);
      window.addEventListener('mouseup', up);
    },

    emitMapToolbar() {
      this.$emit('map-toolbar', {
        mapBoxSelectMode: this.mapBoxSelectMode,
        mapRagPendingIds: Array.isArray(this.mapRagPendingIds) ? [...this.mapRagPendingIds] : [],
        mapRagFilterIds: Array.isArray(this.mapRagFilterIds) ? [...this.mapRagFilterIds] : [],
      });
    },

    toggleMapBoxSelectMode() {
      this.mapBoxSelectMode = !this.mapBoxSelectMode;
      if (!this.mapBoxSelectMode) {
        this.mapBoxDragRect = null;
        this.mapBoxDragging = false;
      }
      this.$nextTick(() => this.emitMapToolbar());
    },

    confirmMapRagSelection() {
      this.mapRagFilterIds = (this.mapRagPendingIds || []).slice();
      this.mapRagPendingIds = [];
      this.drawGlobalMap();
      this.$nextTick(() => this.emitMapToolbar());
    },

    clearMapRagFilter() {
      this.mapRagFilterIds = [];
      this.mapRagPendingIds = [];
      this.mapRagRect2d = null;
      this.drawGlobalMap();
      this.$nextTick(() => this.emitMapToolbar());
    },

    /**
     * 聚类标签透明度：选中某聚类时只显示该标签；否则按视口裁剪显示
     */
    applyGlobalMapClusterLabelOpacity(contentGroup, contentWidth, contentHeight, transform) {
      const self = this;
      contentGroup.selectAll('.cluster-node').style('opacity', function (d) {
        if (!d || !d.centroid_2d) return 0;
        const sel = self.globalMapSelectedClusterId;
        if (sel !== null && sel !== undefined) {
          return d.cluster_id === sel ? 1 : 0;
        }
        const [dx, dy] = self.getClusterLabelAnchorDataXY(d);
        const cx = self.globalMapXScale(dx);
        const cy = self.globalMapYScale(dy);
        const [mappedX, mappedY] = transform.apply([cx, cy]);
        const padding = 60;
        if (
          mappedX >= -padding &&
          mappedX <= contentWidth + padding &&
          mappedY >= -padding &&
          mappedY <= contentHeight + padding
        ) {
          return 1;
        }
        return 0;
      });
    },

    // 提交用户查询到后端（优先 WebSocket，与后端一组一组收数据）
    ensureSessionBatchId() {
      if (this.sessionBatchId) return;
      try {
        let bid = typeof sessionStorage !== 'undefined' ? sessionStorage.getItem('rag_lens_batch_id') : '';
        if (!bid) {
          bid =
            typeof crypto !== 'undefined' && crypto.randomUUID
              ? crypto.randomUUID()
              : `b_${Date.now()}`;
          if (typeof sessionStorage !== 'undefined') sessionStorage.setItem('rag_lens_batch_id', bid);
        }
        this.sessionBatchId = bid;
      } catch (e) {
        this.sessionBatchId = `b_${Date.now()}`;
      }
    },

    /** 归档当前会话到左侧列并清空缓冲区，用于「添加问题」 */
    archiveCurrentSessionColumn() {
      if (this.roundsData && this.roundsData.length > 0 && this.activeSessionId) {
        const goal =
          (this.experimentResult && this.experimentResult.root_goal) ||
          (this.userQuestion && String(this.userQuestion).trim()) ||
          '';
        this.completedQuestionColumns.push({
          sessionId: this.activeSessionId,
          rootGoal: goal,
          roundsData: JSON.parse(JSON.stringify(this.roundsData))
        });
      }
      this.planStates = {};
      this.incrementalRoundsData = [];
      this.roundsData = [];
      this.activeSessionId = '';
    },

    onSessionHeaderOverlayClick(sh) {
      if (sh && sh.isEmptyPlaceholder) {
        this.openAddQuestionPrompt();
      }
    },

    openAddQuestionPrompt() {
      if (this.isSubmitting) {
        alert('Please wait until the current run finishes before adding a new question.');
        return;
      }
      this.addQuestionDraft = '';
      this.addQuestionDialog = { mode: 'inline' };
    },

    cancelAddQuestionDialog() {
      this.addQuestionDialog = null;
      this.addQuestionDraft = '';
    },

    confirmAddQuestionDialog() {
      const q = String(this.addQuestionDraft || '').trim();
      if (!q) return;
      this.archiveCurrentSessionColumn();
      this.userQuestion = q;
      this.addQuestionDialog = null;
      this.addQuestionDraft = '';
      this.submitUserQuery({ skipBufferReset: true });
    },

    getSessionRootGoal(sessionId) {
      if (!sessionId) return '';
      const col = (this.completedQuestionColumns || []).find((c) => c.sessionId === sessionId);
      if (col && col.rootGoal) return String(col.rootGoal).trim();
      if (sessionId === this.activeSessionId) {
        return (
          (this.experimentResult && this.experimentResult.root_goal) ||
          (this.userQuestion && String(this.userQuestion).trim()) ||
          ''
        );
      }
      return '';
    },
    openMiniFollowUp(sessionId) {
      if (this.isSubmitting) {
        alert('请等待当前任务完成后再使用小追问');
        return;
      }
      const sid = String(sessionId || '').trim();
      if (!sid || sid === 'empty') return;
      this.miniFollowUpDraft = {
        sessionId: sid,
        strategy: 'semantic',
        paramText: ''
      };
    },
    closeMiniFollowUp() {
      this.miniFollowUpDraft = null;
    },
    submitMiniFollowUp() {
      const d = this.miniFollowUpDraft;
      if (!d) return;
      const text = String(d.paramText || '').trim();
      if (!text) {
        alert('请输入检索内容');
        return;
      }
      if (!this.wsConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
        alert('WebSocket 未连接，无法发送小追问');
        return;
      }
      const sid = String(d.sessionId || '').trim();
      const toolMap = {
        semantic: 'strategy_semantic_search',
        exact: 'strategy_exact_search',
        metadata: 'strategy_metadata_search'
      };
      const follow_up_tool = toolMap[d.strategy] || 'strategy_semantic_search';
      const withData = this.getAllRounds().filter(
        (r) =>
          r._sessionId === sid &&
          Array.isArray(r.query_results) &&
          r.query_results.length > 0
      );
      const lastRound =
        withData.length > 0
          ? Math.max(...withData.map((r) => Number(r.round_number ?? 0)))
          : 0;
      const nextRound = lastRound + 1;
      const root_goal = this.getSessionRootGoal(sid) || text;
      const followPayload = {
        action: 'follow_up',
        query: text,
        follow_up_tool,
        collection_name: this.ragCollection,
        parent_node_id: '0',
        round_number: nextRound,
        rag_result_per_plan: Math.max(1, Math.floor(Number(this.ragResultsPerPlan) || 10)),
        skip_evaluation: !!this.skipEvaluation,
        session_id: sid,
        batch_id: this.sessionBatchId || '',
        root_goal,
        ...this.wsForkPayload()
      };
      if (this.mapRagFilterIds && this.mapRagFilterIds.length > 0) {
        followPayload.rag_allowed_chunk_ids = this.mapRagFilterIds.map((x) => String(x));
      }
      if (this.mapRagRect2d && Array.isArray(this.mapRagRect2d) && this.mapRagRect2d.length === 2) {
        followPayload.map_box_rect_2d = this.mapRagRect2d;
      }
      this.ws.send(JSON.stringify(followPayload));
      this.miniFollowUpDraft = null;
    },

    getStrategyCardDraftQuery(card) {
      const key = card?.key != null ? String(card.key) : '';
      const existing = key ? this.strategyCardDraftQueries[key] : null;
      if (existing != null && String(existing).trim() !== '') return String(existing);
      const firstLine = Array.isArray(card?.searchLines) && card.searchLines.length > 0 ? card.searchLines[0] : '';
      if (firstLine != null && String(firstLine).trim() !== '') return String(firstLine);
      const a = card?.query?.orchestrator_plan?.args || {};
      const fallback =
        a.query_intent ?? a.query ?? a.user_question ?? a.userQuery ?? a.search_query ?? '';
      return String(fallback || '');
    },

    /** 小矩形标题行：检索类型方框字母（与 orchestrator_plan.tool_name 对齐） */
    strategyCardSearchBadge(card) {
      const t = String(card?.query?.orchestrator_plan?.tool_name || '').trim();
      if (t.includes('metadata')) {
        return { letter: 'M', kind: 'metadata', tooltip: 'Metadata search' };
      }
      if (t.includes('exact')) {
        return { letter: 'E', kind: 'exact', tooltip: 'Exact search' };
      }
      if (t.includes('semantic')) {
        return { letter: 'S', kind: 'semantic', tooltip: 'Semantic search' };
      }
      if (t === 'auto_continue_pending') {
        return { letter: 'A', kind: 'auto', tooltip: 'Auto continue (pending)' };
      }
      const short = t ? t.slice(0, 18) : '';
      return {
        letter: '?',
        kind: 'unknown',
        tooltip: short ? `Tool: ${short}` : 'Unknown strategy',
      };
    },

    setStrategyCardDraftQuery(card, value) {
      const key = card?.key != null ? String(card.key) : '';
      if (!key) return;
      if (!this.strategyCardDraftQueries || typeof this.strategyCardDraftQueries !== 'object') {
        this.strategyCardDraftQueries = {};
      }
      this.strategyCardDraftQueries[key] = String(value ?? '');
    },

    resolveFollowUpToolForCard(card) {
      const tool = String(card?.query?.orchestrator_plan?.tool_name || '').trim();
      if (tool === 'strategy_exact_search') return 'strategy_exact_search';
      if (tool === 'strategy_metadata_search') return 'strategy_metadata_search';
      return 'strategy_semantic_search';
    },

    handleStrategyHeaderAction(action, card) {
      const a = String(action || '').toUpperCase();
      try {
        console.log('[UI] header action', a, {
          key: card?.key,
          sessionId: card?.sessionId,
          roundNumber: card?.roundNumber,
          queryIndex: card?.queryIndex,
          gridPos: card?.query?.orchestrator_plan?.grid_pos,
        });
      } catch (e) {
        /* ignore */
      }
      if (a === 'R') {
        this.rewriteStrategyCard(card);
        return;
      }
      if (a === 'D') {
        this.deleteStrategyCard(card);
        return;
      }
      if (a === 'C') {
        this.insertContinuePlaceholder(card);
        return;
      }
    },

    getCardGridRow(card) {
      const gp = card?.query?.orchestrator_plan?.grid_pos;
      if (Array.isArray(gp) && gp.length >= 1) {
        const r = Number(gp[0]);
        if (Number.isFinite(r) && r >= 1) return Math.floor(r);
      }
      const qi = Number(card?.queryIndex ?? -1);
      if (Number.isFinite(qi) && qi >= 0) return qi + 1;
      return 1;
    },

    getSessionRoundsMutable(sid) {
      const sessionId = String(sid || '').trim();
      const activeSid = String(this.activeSessionId || '').trim();
      if (sessionId && sessionId !== 'empty' && sessionId !== activeSid) {
        const col = (this.completedQuestionColumns || []).find((c) => c.sessionId === sessionId);
        if (col) return col.roundsData;
      }
      return this.roundsData;
    },

    insertContinuePlaceholder(baseCard) {
      try {
        console.log('[UI] insertContinuePlaceholder baseCard', {
          key: baseCard?.key,
          sessionId: baseCard?.sessionId,
          roundNumber: baseCard?.roundNumber,
          queryIndex: baseCard?.queryIndex,
          gridPos: baseCard?.query?.orchestrator_plan?.grid_pos,
        });
      } catch (e) {
        /* ignore */
      }
      if (this.isSubmitting) {
        alert('请等待当前任务完成后再使用 Continue');
        return;
      }
      const sid = String(baseCard?.sessionId || '').trim();
      if (!sid || sid === 'empty') {
        alert(`Continue 无法执行：缺少 sessionId（sid=${sid || '(empty)'}）`);
        return;
      }
      const row = this.getCardGridRow(baseCard);
      const roundsArr = this.getSessionRoundsMutable(sid);
      if (!Array.isArray(roundsArr)) {
        alert('Continue 无法执行：roundsData 不可用（请看控制台日志）');
        return;
      }
      const existingRounds = (roundsArr || []).filter((r) => r && r._sessionId === sid);
      // 关键：nextRound 必须基于“该行(row)的最大 round”，而不是全局最大 round
      const roundsForScan = existingRounds.length > 0 ? existingRounds : (roundsArr || []);
      const rowMaxRoundFromLoaded = (() => {
        let m = 0;
        for (const r of roundsForScan) {
          if (!r || r.round_number == null) continue;
          const rn = Number(r.round_number);
          if (!Number.isFinite(rn) || rn <= 0) continue;
          const qrs = Array.isArray(r.query_results) ? r.query_results : [];
          // 优先用 grid_pos[0]（更稳），其次才用数组槽位 idx
          const hasRow =
            qrs.some((q) => {
              const gp = q?.orchestrator_plan?.grid_pos;
              return Array.isArray(gp) && Number(gp?.[0]) === Number(row);
            }) ||
            (qrs[row - 1] && qrs[row - 1].orchestrator_plan != null);
          if (hasRow) m = Math.max(m, rn);
        }
        return m;
      })();

      // 注意：roundsArr 可能只包含“已加载到前端内存”的轮次（例如用户未点击“加载所有轮次”）。
      // baseCard 本身带有 roundNumber / grid_pos[1]，应兜底保证 nextRound >= baseRound + 1。
      const baseRoundFromCard = Number(baseCard?.roundNumber ?? 0);
      const baseRoundFromGridPos = Number(baseCard?.query?.orchestrator_plan?.grid_pos?.[1] ?? 0);
      const lastRoundResolved = Math.max(
        Number.isFinite(rowMaxRoundFromLoaded) ? rowMaxRoundFromLoaded : 0,
        Number.isFinite(baseRoundFromCard) ? baseRoundFromCard : 0,
        Number.isFinite(baseRoundFromGridPos) ? baseRoundFromGridPos : 0,
      );
      const nextRound = lastRoundResolved + 1;

      let roundObj = (roundsArr || []).find((r) => Number(r?.round_number) === Number(nextRound));
      if (!roundObj) {
        roundObj = { round_number: nextRound, query_results: [] };
        // 保持 _sessionId 一致（用于 gridColumnKey 与 strip 分组）
        roundObj._sessionId = sid;
        roundsArr.push(roundObj);
        roundsArr.sort((a, b) => Number(a.round_number ?? 0) - Number(b.round_number ?? 0));
      }
      if (!Array.isArray(roundObj.query_results)) roundObj.query_results = [];
      const idx = Math.max(0, row - 1);
      while (roundObj.query_results.length <= idx) {
        roundObj.query_results.push({ orchestrator_plan: null, rag_results: [] });
      }

      const baseText = String(this.getStrategyCardDraftQuery(baseCard) || '').trim();
      const basePlan = baseCard?.query?.orchestrator_plan || null;

      const baseRn = Number(baseCard?.roundNumber ?? 0);
      const baseQi = Number(baseCard?.queryIndex ?? -1);
      if (Number.isFinite(baseRn) && baseRn > 0 && Number.isFinite(baseQi) && baseQi >= 0) {
        try {
          this.appendPlanUserdoContinueLocal(baseRn, sid, baseQi, baseText);
          void this.persistPlanUserdoBatch([
            {
              action: 'plan_continue',
              session_id: sid,
              round_number: baseRn,
              query_index: baseQi,
              new: baseText,
              timestamp: new Date().toISOString().split('.')[0],
            },
          ]).catch((e) => console.warn('persist plan_continue userdo failed', e));
        } catch (e) {
          console.warn('append plan_continue userdo failed', e);
        }
      }

      roundObj.query_results.splice(idx, 1, {
        orchestrator_plan: {
          action: 'call_tool',
          tool_name: 'auto_continue_pending',
          ParentNode: '0',
          args: { note: 'pending auto', query_intent: baseText },
          reason: 'Continue: pending auto execution',
          grid_pos: [row, nextRound],
        },
        rag_results: [],
        _continue_auto_pending: true,
        _continue_base: {
          session_id: sid,
          row,
          base_round_number: Number(baseCard?.roundNumber ?? 0),
          base_query_index: Number(baseCard?.queryIndex ?? 0),
          base_query_text: baseText,
          base_plan: basePlan,
        }
      });
      try {
        window.alert(`已创建 new strategy：session=${sid} 行=${row} 列(round)=${nextRound}（在最右侧）`);
      } catch (e) {
        /* ignore */
      }

      if (sid && sid !== this.activeSessionId) {
        const col = (this.completedQuestionColumns || []).find((c) => c.sessionId === sid);
        if (col) col.roundsData = [...(col.roundsData || [])];
        this.completedQuestionColumns = [...(this.completedQuestionColumns || [])];
      } else {
        this.roundsData = [...(this.roundsData || [])];
      }
      this.$nextTick(() => this.drawRiverChart());
    },

    runContinueAuto(card) {
      if (this.isSubmitting) {
        alert('请等待当前任务完成后再使用 auto');
        return;
      }
      if (!this.wsConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
        alert('WebSocket 未连接，无法发送 continue');
        return;
      }
      const q = card?.query;
      const base = q?._continue_base || null;
      const sid = String(card?.sessionId || base?.session_id || '').trim();
      if (!sid) return;
      const row = Number(base?.row ?? this.getCardGridRow(card));
      const nextRound = Number(card?.roundNumber ?? 0);
      const rewriteTargetIndex = Math.max(0, Math.floor(row - 1));

      const root_goal = this.getSessionRootGoal(sid) || String(base?.base_query_text || '').trim();
      const continue_context = {
        base_round_number: base?.base_round_number,
        base_query_index: base?.base_query_index,
        base_query_text: base?.base_query_text,
        base_plan: base?.base_plan,
      };

      const followPayload = {
        action: 'follow_up',
        query: String(base?.base_query_text || root_goal || 'continue').trim() || 'continue',
        follow_up_tool: 'auto_continue',
        collection_name: this.ragCollection,
        parent_node_id: '0',
        round_number: nextRound,
        rag_result_per_plan: Math.max(1, Math.floor(Number(this.ragResultsPerPlan) || 10)),
        skip_evaluation: !!this.skipEvaluation,
        session_id: sid,
        batch_id: this.sessionBatchId || '',
        root_goal,
        rewrite_mode: true,
        rewrite_target_query_index: rewriteTargetIndex,
        grid_row: Math.max(1, Math.floor(row)),
        continue_context,
        ...this.wsForkPayload()
      };
      if (this.mapRagFilterIds && this.mapRagFilterIds.length > 0) {
        followPayload.rag_allowed_chunk_ids = this.mapRagFilterIds.map((x) => String(x));
      }
      if (this.mapRagRect2d && Array.isArray(this.mapRagRect2d) && this.mapRagRect2d.length === 2) {
        followPayload.map_box_rect_2d = this.mapRagRect2d;
      }
      this.ws.send(JSON.stringify(followPayload));
    },

    rewriteStrategyCard(card) {
      if (this.isSubmitting) {
        alert('请等待当前任务完成后再重写策略');
        return;
      }
      const text = String(this.getStrategyCardDraftQuery(card) || '').trim();
      if (!text) {
        alert('请输入策略问题');
        return;
      }
      if (!this.wsConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
        alert('WebSocket 未连接，无法重写策略');
        return;
      }
      const sid = String(card?.sessionId || '').trim();
      if (!sid || sid === 'empty') {
        alert('未找到 session_id，无法重写策略');
        return;
      }
      const follow_up_tool = this.resolveFollowUpToolForCard(card);
      const nextRound = Number(card?.roundNumber ?? 0);
      const rewriteTargetIndex = Number(card?.queryIndex ?? -1);
      if (!Number.isFinite(nextRound) || nextRound <= 0 || !Number.isFinite(rewriteTargetIndex) || rewriteTargetIndex < 0) {
        alert('未找到目标策略位置（round/queryIndex），无法重写');
        return;
      }
      const root_goal = this.getSessionRootGoal(sid) || text;

      // 就地清空：立刻移除旧 rag_results，等待后端回推覆盖
      try {
        const roundRef = this.getRoundRef(nextRound, sid);
        const q = roundRef?.query_results?.[rewriteTargetIndex];
        let beforeIntent = '';
        if (q?.orchestrator_plan?.args && typeof q.orchestrator_plan.args === 'object') {
          const a = q.orchestrator_plan.args;
          beforeIntent = String(
            a.query_intent ?? a.query ?? a.user_question ?? a.userQuery ?? a.search_query ?? ''
          ).trim();
        }
        if (q && beforeIntent) {
          try {
            this.appendPlanUserdoRegenerateLocal(nextRound, sid, rewriteTargetIndex, beforeIntent);
            void this.persistPlanUserdoBatch([
              {
                action: 'plan_regenerate',
                session_id: sid,
                round_number: nextRound,
                query_index: rewriteTargetIndex,
                before: beforeIntent,
                timestamp: new Date().toISOString().split('.')[0],
              },
            ]).catch((e) => console.warn('persist plan_regenerate userdo failed', e));
          } catch (e) {
            console.warn('append plan_regenerate userdo failed', e);
          }
        }
        if (q) {
          q.rag_results = [];
          if (q.orchestrator_plan && q.orchestrator_plan.args && typeof q.orchestrator_plan.args === 'object') {
            const args = { ...(q.orchestrator_plan.args || {}) };
            if (args.query_intent != null || args.query != null || args.user_question != null) {
              args.query_intent = text;
            }
            q.orchestrator_plan.args = args;
          }
          this.roundsData = [...this.roundsData];
          this.$nextTick(() => this.drawRiverChart());
        }
      } catch (e) {
        // ignore
      }

      const followPayload = {
        action: 'follow_up',
        query: text,
        follow_up_tool,
        collection_name: this.ragCollection,
        parent_node_id: '0',
        round_number: nextRound,
        rewrite_mode: true,
        rewrite_target_query_index: rewriteTargetIndex,
        rag_result_per_plan: Math.max(1, Math.floor(Number(this.ragResultsPerPlan) || 10)),
        skip_evaluation: !!this.skipEvaluation,
        session_id: sid,
        batch_id: this.sessionBatchId || '',
        root_goal,
        ...this.wsForkPayload()
      };
      if (this.mapRagFilterIds && this.mapRagFilterIds.length > 0) {
        followPayload.rag_allowed_chunk_ids = this.mapRagFilterIds.map((x) => String(x));
      }
      if (this.mapRagRect2d && Array.isArray(this.mapRagRect2d) && this.mapRagRect2d.length === 2) {
        followPayload.map_box_rect_2d = this.mapRagRect2d;
      }
      this.ws.send(JSON.stringify(followPayload));
    },

    async submitUserQuery(options = {}) {
      if (!this.userQuestion.trim() || this.isSubmitting) {
        return;
      }

      this.isSubmitting = true;
      const question = this.userQuestion.trim();

      try {
        console.log('提交用户查询:', question);
        if (this.wsConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ensureSessionBatchId();
          if (!options.skipBufferReset) {
            this.planStates = {};
            this.incrementalRoundsData = [];
            this.roundsData = [];
            this.gridMetrics = null;
          }
          if (!this.activeSessionId) {
            this.activeSessionId =
              typeof crypto !== 'undefined' && crypto.randomUUID
                ? crypto.randomUUID()
                : `s_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
          }
          const payload = {
            action: 'start_query',
            query: question,
            collection_name: this.ragCollection,
            plans_per_round: Math.max(1, Math.min(10, Math.floor(Number(this.plansPerRound) || 2))),
            rag_result_per_plan: Math.max(1, Math.floor(Number(this.ragResultsPerPlan) || 10)),
            max_rounds: Math.max(1, Math.min(10, Math.floor(Number(this.maxRounds) || 3))),
            interactive: this.isInteractiveMode === true,
            session_id: this.activeSessionId,
            batch_id: this.sessionBatchId || '',
            skip_evaluation: !!this.skipEvaluation,
            use_multi_agent_rewrite_streams: !!this.useMultiAgentRewriteStreams,
            rewrite_variant_count: Math.max(1, Math.min(10, Math.floor(Number(this.plansPerRound) || 2))),
            ...this.wsForkPayload()
          };
          if (this.mapRagFilterIds && this.mapRagFilterIds.length > 0) {
            payload.rag_allowed_chunk_ids = this.mapRagFilterIds.map((x) => String(x));
          }
          if (this.mapRagRect2d && Array.isArray(this.mapRagRect2d) && this.mapRagRect2d.length === 2) {
            payload.map_box_rect_2d = this.mapRagRect2d;
          }
          this.ws.send(JSON.stringify(payload));
          this.userQuestion = '';
          // 后端会通过 WebSocket 逐步推送：plan_created → retrieval_complete → evaluation_complete
          return;
        }
        // 降级：走 HTTP API（若后端提供 /api/rag/query）
        const queryResult = await ragService.submitUserQuery(question, {
          parentNode: '0',
          strategy: 'strategy_semantic_search'
        });
        if (!queryResult.orchestrator_plan || !queryResult.rag_results) {
          throw new Error('返回数据结构不完整');
        }
        await this.addUserQueryResult(queryResult);
        this.userQuestion = '';
        alert('查询成功！结果已添加到图表中。');
      } catch (error) {
        console.error('提交查询失败:', error);
        alert(`提交查询失败: ${error.message || '未知错误'}。请确保已连接 WebSocket 或后端 API 可用。`);
      } finally {
        this.isSubmitting = false;
      }
    },

    // 将用户查询结果添加到图表
    async addUserQueryResult(queryResult) {
      // 确保地图数据已加载
      if (this.mapPoints.length === 0) {
        await this.loadMapData();
      }

      // 计算新的轮次号（当前最大轮次 + 1）
      const maxRound = this.roundsData.length > 0 
        ? Math.max(...this.roundsData.map(r => r.round_number), -1)
        : -1;
      const newRoundNumber = maxRound + 1;

      // 创建新的轮次数据
      const newRound = {
        round_number: newRoundNumber,
        query_results: [queryResult]
      };

      // 添加到轮次数据
      this.roundsData.push(newRound);
      this.roundsData.sort((a, b) => a.round_number - b.round_number);

      // 重新绘制图表
      this.drawRiverChart();
    },


    extractRelativePath(fullPath) {
      if (!fullPath) return '';
      const paperMdIndex = fullPath.indexOf('paper_md');
      if (paperMdIndex !== -1) {
        return fullPath.substring(paperMdIndex + 'paper_md'.length + 1);
      }
      return fullPath;
    },

    getImageUrl(relativePath) {
      // 后端在 server.py 中把静态图片挂载到了 /static
      return `/static/${relativePath}`;
    },

    /** 本地载入实验后，追问/大追问/新查询合并保存到 experiment_data/<原名>_user2.json */
    wsForkPayload() {
      const s = (this.forkExperimentSource || '').trim();
      if (!s) return {};
      return { fork_experiment_source: s };
    },

    async loadGlobalMapData() {
      try {
        this.globalMapSelectedClusterId = null;
        this.mapRagFilterIds = [];
        this.mapRagPendingIds = [];
        this.mapRagRect2d = null;
        this.mapBoxSelectMode = false;
        this.mapBoxDragRect = null;

        const fileName = this.ragCollection === 'LLMvisDataset' 
          ? '/LLMvisDataset_embedding.json' 
          : '/multimodal2text_embeddings_2d.json';
        const response = await fetch(fileName);
        const rawData = await response.json();
        
        // 处理数据格式
        this.globalMapPoints = rawData.map(item => {
          const coords = item.coordinates_2d || [0, 0];
          return {
            ...item,
            x: coords[0],
            y: coords[1]
          };
        });

        // 尝试加载聚类关键词
        try {
          const kwFileName = this.ragCollection === 'LLMvisDataset' 
            ? '/LLMvisDataset_cluster_keywords.json' 
            : '/multimodal2text_cluster_keywords.json';
          if (kwFileName) {
            const kwResponse = await fetch(kwFileName);
            if (kwResponse.ok) {
              const kwData = await kwResponse.json();
              this.clusterKeywords = kwData.clusters || [];
            } else {
              this.clusterKeywords = [];
            }
          } else {
            this.clusterKeywords = [];
          }
        } catch (kwError) {
          console.warn('加载聚类关键词失败:', kwError);
          this.clusterKeywords = [];
        }

        this.assignClusterIdsToPoints();
        this.rebuildIdToPointMap();
        
        console.log('全局地图数据加载完成，共', this.globalMapPoints.length, '个点');
        this.$nextTick(() => {
          this.drawGlobalMap();
          this.emitMapToolbar();
        });
      } catch (error) {
        console.error('加载全局地图数据失败:', error);
      }
    },

    drawGlobalMap() {
      if (!this.globalMapMountId) {
        return;
      }
      const mountEl = document.getElementById(this.globalMapMountId);
      if (!mountEl) return;
      let svg = d3.select(mountEl).select('svg.global-map-svg');
      if (svg.empty()) {
        const svgEl = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svgEl.setAttribute('class', 'global-map-svg');
        mountEl.innerHTML = '';
        mountEl.appendChild(svgEl);
        svg = d3.select(svgEl);
      }

      let preserveZoomTransform = d3.zoomIdentity;
      try {
        if (svg.node()) preserveZoomTransform = d3.zoomTransform(svg.node());
      } catch (e) {
        preserveZoomTransform = d3.zoomIdentity;
      }

      svg.selectAll('*').remove();
      this.globalMapContentGroupNode = null;

      if (this.globalMapPoints.length === 0) {
        return;
      }

      // 获取 SVG 容器尺寸
      const container = svg.node().parentElement;
      const width = container.clientWidth || 400;
      const height = container.clientHeight || 300;

      svg
        .attr('width', width)
        .attr('height', height)
        .style('pointer-events', 'all');

      // 计算数据范围（原始行为）：x、y 各自线性映射到整块绘图区，填满视口，不保持数据平面上的长宽比。
      // 若改成「等比例缩放 + 居中留白」，点云在矩形里的轮廓会与现在不同；策略卡小地图可与本处策略不同。
      const xExtent = d3.extent(this.globalMapPoints, d => d.x);
      const yExtent = d3.extent(this.globalMapPoints, d => d.y);

      const margin = 10;
      const contentWidth = width - margin * 2;
      const contentHeight = height - margin * 2;

      this.globalMapXScale = d3.scaleLinear()
        .domain(xExtent)
        .range([0, contentWidth]);

      this.globalMapYScale = d3.scaleLinear()
        .domain(yExtent)
        .range([contentHeight, 0]);

      const outerGroup = svg.append('g')
        .attr('class', 'global-map-outer-group')
        .attr('transform', `translate(${margin}, ${margin})`);
        
      // 增加clip path防止缩放拖动时溢出到边框外
      const clipId = 'global-map-clip-' + Math.random().toString(36).substr(2, 9);
      svg.append('defs').append('clipPath')
        .attr('id', clipId)
        .append('rect')
        .attr('width', contentWidth)
        .attr('height', contentHeight);
        
      outerGroup.attr('clip-path', `url(#${clipId})`);
      
      // 增加透明背景捕获鼠标缩放/拖动事件
      outerGroup.append('rect')
        .attr('width', contentWidth)
        .attr('height', contentHeight)
        .attr('fill', 'transparent')
        .style('pointer-events', 'all');

      const contentGroup = outerGroup.append('g')
        .attr('class', 'global-map-content-group');
        
      // 定义缩放和拖动行为
      const zoom = d3.zoom()
        .scaleExtent([0.2, 10]) // 允许缩放的范围
        .extent([[0, 0], [contentWidth, contentHeight]])
        .on('zoom', (event) => {
          contentGroup.attr('transform', event.transform);
          this.globalMapZoomTransform = event.transform;
          this.applyGlobalMapClusterLabelOpacity(contentGroup, contentWidth, contentHeight, event.transform);
        });

      // 必须先卸掉上一次绑在 svg 上的 zoom（.zoom 命名空间），否则进入框选时若未 call(zoom)，
      // 旧的 d3-zoom 仍会拦截 mousedown/move，框选拖拽无任何反应；退出框选后重新 call(zoom) 才恢复平移。
      svg.on('.zoom', null);

      // 将行为应用到 svg 上（框选模式下禁用平移/缩放）
      if (!this.mapBoxSelectMode) {
        svg.call(zoom);
      }
      svg.on('dblclick.zoom', null);
      svg.on('dblclick', () => {
        if (!this.mapBoxSelectMode) {
          svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
        }
      });

      // 绘制密度地图
      this.drawGlobalDensityMap(contentGroup, contentWidth, contentHeight);

      // 绘制所有数据点（灰色小点），根据高亮状态设置颜色和大小
      const points = contentGroup.selectAll('circle.data-point')
        .data(this.globalMapPoints);
      
        // 辅助函数：检查点是否被高亮（支持多种ID格式）
      const getHighlightInfo = (point) => {
        // 方法1: 直接匹配 id 字段
        let highlightInfo = this.highlightedPlanPoints[point.id];
        if (highlightInfo) return highlightInfo;
        
        // 方法2: 匹配 metadata 中的 figure_id 或 id
        try {
          if (point.metadata) {
            let metadataObj = point.metadata;
            if (typeof metadataObj === 'string') {
              metadataObj = JSON.parse(metadataObj);
            }
            const figureId = metadataObj.figure_id || metadataObj.id;
            if (figureId) {
              highlightInfo = this.highlightedPlanPoints[figureId];
              if (highlightInfo) return highlightInfo;
            }
            // 检查嵌套的metadata
            if (metadataObj.metadata && typeof metadataObj.metadata === 'string') {
              const innerMetadata = JSON.parse(metadataObj.metadata);
              const innerFigureId = innerMetadata.figure_id || innerMetadata.id;
              if (innerFigureId) {
                highlightInfo = this.highlightedPlanPoints[innerFigureId];
                if (highlightInfo) return highlightInfo;
              }
            }
          }
        } catch (e) {
          // 忽略解析错误
        }
        
        return null;
      };
      
      const getPointType = (point) => {
        let rawType = point.type || null;
        try {
          if (!rawType && point.metadata) {
            const metadataObj = typeof point.metadata === 'string' ? JSON.parse(point.metadata) : point.metadata;
            rawType = metadataObj.type || null;
            if (!rawType && metadataObj.metadata && typeof metadataObj.metadata === 'string') {
              const inner = JSON.parse(metadataObj.metadata);
              rawType = inner.type || null;
            }
            // 处理 LLMvisDataset
            if (!rawType && (metadataObj.full_json || metadataObj.savepath || metadataObj.save_path)) {
              rawType = 'picture';
            }
            if (!rawType && metadataObj.metadata && typeof metadataObj.metadata === 'string') {
              const inner = JSON.parse(metadataObj.metadata);
              if (inner.full_json || inner.savepath || inner.save_path) {
                rawType = 'picture';
              }
            }
          }
        } catch (e) {
          // ignore
        }
        if (rawType === 'text') rawType = 'texture';
        if (rawType === 'figure' || rawType === 'image') rawType = 'picture';
        
        if (!rawType) {
           try {
              if (point.metadata && typeof point.metadata === 'string') {
                 const meta = JSON.parse(point.metadata);
                 if (meta.type === 'texture' || meta.type === 'text') rawType = 'texture';
                 else if (meta.type === 'picture' || meta.type === 'figure' || meta.type === 'image') rawType = 'picture';
              }
           } catch(e) {
             // ignore
           }
        }
        
        // 最后一次兜底检测
        if (!rawType) {
           try {
              if (point.metadata && typeof point.metadata === 'object') {
                 if (point.metadata.type === 'texture' || point.metadata.type === 'text') rawType = 'texture';
                 else if (point.metadata.type === 'picture' || point.metadata.type === 'figure' || point.metadata.type === 'image') rawType = 'picture';
              }
           } catch(e) {
             // ignore
           }
        }
        
        if (!rawType && point.id && point.id.includes('Figure')) rawType = 'picture';
        
        return rawType;
      };

      const clusterSelId = this.globalMapSelectedClusterId;
      const isClusterDimmed = (d) =>
        clusterSelId !== null &&
        clusterSelId !== undefined &&
        d._clusterId !== clusterSelId;

      const ragFilterSet =
        this.mapRagFilterIds && this.mapRagFilterIds.length
          ? new Set(this.mapRagFilterIds.map((x) => String(x)))
          : null;

      points.enter()
        .append('circle')
        .attr('class', 'data-point')
        .merge(points)
        .attr('cx', d => this.globalMapXScale(d.x))
        .attr('cy', d => this.globalMapYScale(d.y))
        .attr('r', d => {
          if (isClusterDimmed(d)) return 0.65;
          const highlightInfo = getHighlightInfo(d);
          return highlightInfo ? (highlightInfo.boostRadius ? 8 : 4) : clusterSelId != null && d._clusterId === clusterSelId ? 2.2 : 0.8;
        })
        .attr('fill', d => {
          if (isClusterDimmed(d)) return '#bbbbbb';
          if (ragFilterSet && ragFilterSet.has(String(d.id))) {
            return '#e67e22';
          }
          const highlightInfo = getHighlightInfo(d);
          if (highlightInfo) {
            const action = highlightInfo.branch_action;
            if (action === 'GROW') {
              return '#379b61'; // 绿色
            } else if (action === 'PRUNE') {
              return '#dc3545'; // 红色
            } else if (action === 'KEEP') {
              return '#eec316'; // 黄色
            } else if (action === 'PENDING') {
              return '#6c757d'; // 灰色（待评估）
            }
            return '#999999';
          }
          if (clusterSelId != null && d._clusterId === clusterSelId) {
            return '#1e6bb8'; // 聚类选中高亮       TODOLIST
          }
          return '#999999'; // 普通点灰色
        })
        .attr('opacity', d => {
          if (isClusterDimmed(d)) return 0.08;
          const highlightInfo = getHighlightInfo(d);
          if (highlightInfo) {
            return 0.9; // 高亮点不透明
          }
          return clusterSelId != null && d._clusterId === clusterSelId ? 0.92 : 0.4;
        })
        .attr('stroke', d => {
          if (isClusterDimmed(d)) return 'none';
          const highlightInfo = getHighlightInfo(d);
          if (highlightInfo && getPointType(d) === 'picture') {
             return 'rgba(40, 140, 255, 0.95)';
          }
          if (highlightInfo) {
            // 高亮点添加描边
            const action = highlightInfo.branch_action;
            if (action === 'GROW') {
              return '#1e7e34';
            } else if (action === 'PRUNE') {
              return '#bd2130';
            } else if (action === 'KEEP') {
              return '#d39e00';
            } else if (action === 'PENDING') {
              return '#545b62';
            }
          }
          if (clusterSelId != null && d._clusterId === clusterSelId) {
            return 'rgba(30, 107, 184, 0.9)';
          }
          return 'none';
        })
        .attr('stroke-width', d => {
          if (isClusterDimmed(d)) return 0;
          const highlightInfo = getHighlightInfo(d);
          if (highlightInfo && getPointType(d) === 'picture') {
             return 1.5;
          }
          if (highlightInfo) {
            return 1.5;
          }
          if (clusterSelId != null && d._clusterId === clusterSelId) {
            return 1.2;
          }
          return 0;
        });

      // 绘制聚类关键词 (渲染在散点上层)
      if (this.clusterKeywords && this.clusterKeywords.length > 0) {
        const keywordsGroup = contentGroup.append('g')
          .attr('class', 'cluster-keywords-group');

        const clusterNodes = keywordsGroup.selectAll('g.cluster-node')
          .data(this.clusterKeywords)
          .enter()
          .append('g')
          .attr('class', 'cluster-node')
          .attr('transform', d => {
            const [dx, dy] = this.getClusterLabelAnchorDataXY(d);
            const cx = this.globalMapXScale(dx);
            const cy = this.globalMapYScale(dy);
            return `translate(${cx}, ${cy})`;
          });

        clusterNodes.each(function(d) {
          if (!d.top_keywords || d.top_keywords.length === 0) return;
          
          const g = d3.select(this);
          // 仅显示出现频率最高的第一个标签
          const topWords = d.top_keywords[0].term;
          
          // 测量文本
          const textEl = g.append('text')
            .attr('class', 'cluster-keyword-text')
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'middle')
            .style('font-size', '12px')
            .style('font-weight', 'bold')
            .style('fill', '#2c3e50')
            .style('pointer-events', 'all')
            .text(topWords);
            
          const bbox = textEl.node().getBBox();
          
          // 背景
          g.insert('rect', 'text')
            .attr('x', bbox.x - 6)
            .attr('y', bbox.y - 3)
            .attr('width', bbox.width + 12)
            .attr('height', bbox.height + 6)
            .attr('rx', 4)
            .attr('ry', 4)
            .style('fill', 'rgba(255, 255, 255, 0.85)')
            .style('stroke', 'rgba(150, 150, 150, 0.5)')
            .style('stroke-width', '1px')
            .style('pointer-events', 'all');
        });

        clusterNodes
          .style('cursor', 'pointer')
          .on('click', (event, d) => {
            event.stopPropagation();
            const id = d.cluster_id;
            if (this.globalMapSelectedClusterId === id) {
              this.globalMapSelectedClusterId = null;
            } else {
              this.globalMapSelectedClusterId = id;
            }
            this.drawGlobalMap();
          });
      }

      // 框选模式：在最上层铺透明矩形，保证拖拽从任意位置开始都能命中（否则密度/点层可能抢不到事件）
      if (this.mapBoxSelectMode) {
        contentGroup
          .append('rect')
          .attr('class', 'map-box-hit-layer')
          .attr('x', 0)
          .attr('y', 0)
          .attr('width', contentWidth)
          .attr('height', contentHeight)
          .attr('fill', 'transparent')
          .attr('pointer-events', 'all')
          .style('cursor', 'crosshair');
      }

      if (!this.mapBoxSelectMode) {
        svg.call(zoom.transform, preserveZoomTransform);
      } else {
        contentGroup.attr('transform', preserveZoomTransform);
      }
      // 框选模式下未把 zoom 绑到 svg，d3.zoomTransform(svg.node()) 可能与 contentGroup 实际 transform 不一致，
      // 导致坐标 invert 错误、拖拽矩形看不见、选点为空。始终以本次绘制应用的 preserve 为准。
      this.globalMapZoomTransform = preserveZoomTransform;
      // 必须在设置 transform 之后再挂节点，保证 pointer 与圆点坐标一致
      this.globalMapContentGroupNode = contentGroup.node();

      if (this.mapBoxDragRect) {
        const r = this.mapBoxDragRect;
        const rx = Math.min(r.x1, r.x2);
        const ry = Math.min(r.y1, r.y2);
        const rw = Math.abs(r.x2 - r.x1);
        const rh = Math.abs(r.y2 - r.y1);
        contentGroup
          .append('rect')
          .attr('class', 'map-box-drag-rect')
          .attr('x', rx)
          .attr('y', ry)
          .attr('width', rw)
          .attr('height', rh)
          .attr('fill', 'rgba(255, 107, 0, 0.22)')
          .attr('stroke', '#ff6b00')
          .attr('stroke-width', 2)
          .attr('stroke-dasharray', '6 4')
          .attr('pointer-events', 'none');
      }

      if (this.mapBoxSelectMode) {
        const self = this;
        svg.on('mousedown.mapbox', function (event) {
          if (event.button !== 0) return;
          self._mapBoxDragStartLocalPlot(event);
        });
      } else {
        svg.on('mousedown.mapbox', null);
      }
    },

    drawGlobalDensityMap(contentGroup, width, height) {
      // 将点转换为缩放后的坐标
      const scaledPoints = this.globalMapPoints.map(d => [
        this.globalMapXScale(d.x),
        this.globalMapYScale(d.y)
      ]);

      // 创建密度等高线
      const density = d3.contourDensity()
        .x(d => d[0])
        .y(d => d[1])
        .size([width, height])
        .bandwidth(15)  // 带宽：减小以捕捉更多局部细节和密集区域
        .thresholds(35);  // 层数：增加以获得更细腻的渐变效果

      const contours = density(scaledPoints);

      // 创建颜色比例尺
      const color = d3.scaleSequential(d3.interpolateBlues)
        .domain([0, d3.max(contours, d => d.value)]);

      // 绘制等高线
      contentGroup.selectAll('path.density')
        .data(contours)
        .enter()
        .append('path')
        .attr('class', 'density')
        .attr('d', d3.geoPath())
        .attr('fill', d => color(d.value))
        .attr('opacity', 0.5)
        .attr('stroke', 'none');
    },

    formatSummary(summary) {
      if (!summary) return '';
      const trimmed = String(summary).trim();
      if (trimmed.startsWith('{')) {
        try {
          const o = JSON.parse(trimmed);
          if (o && typeof o === 'object' && ('answer' in o || 'suggestion' in o)) {
            const a = o.answer != null ? String(o.answer) : '';
            const s = o.suggestion != null ? String(o.suggestion) : '';
            const md = `### 基于数据的回答\n\n${a}\n\n---\n\n### 策略选择评价\n\n${s}`;
            return this.formatSummary(md);
          }
        } catch (e) {
          /* 非 JSON 或解析失败，走下方 Markdown */
        }
      }

      try {
        // 配置 marked renderer 以支持数学公式
        const renderer = new marked.Renderer();
        
        // 处理行内数学公式 $...$ 或 \(...\)
        const originalParagraph = renderer.paragraph;
        renderer.paragraph = (text) => {
          const inlineMathRegex = /\$([^$\n]+)\$|\\(([^)]+)\\)/g;
          text = text.replace(inlineMathRegex, (match, dollarContent, parenContent) => {
            const mathContent = dollarContent || parenContent;
            try {
              return katex.renderToString(mathContent, { throwOnError: false, displayMode: false });
            } catch (e) {
              return match;
            }
          });
          return originalParagraph(text);
        };
        
        // 处理块级数学公式 $$...$$ 或 \[...\]
        const originalCode = renderer.code;
        renderer.code = (code, language) => {
          if (language === 'math' || language === 'latex') {
            try {
              return `<div class="math-block">${katex.renderToString(code, { throwOnError: false, displayMode: true })}</div>`;
            } catch (e) {
              return `<pre><code>${code}</code></pre>`;
            }
          }
          return originalCode(code, language);
        };
        
        marked.setOptions({ renderer, gfm: true, breaks: true });
        
        // 先处理块级公式
        let processedText = summary.replace(/\$\$([^$]+)\$\$/g, (match, content) => {
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
          if (match.includes('math-block') || match.includes('katex')) return match;
          try {
            return katex.renderToString(content.trim(), { throwOnError: false, displayMode: false });
          } catch (e) {
            return match;
          }
        });
        
        return finalHtml;
      } catch (error) {
        console.error('Error rendering markdown:', error);
        // 如果渲染失败，返回简单的 HTML 转义
        return summary
          .replace(/\n/g, '<br>')
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      }
    },

    addZoomBehavior() {
      if (!this.persistZoomTransform) {
        this.persistZoomTransform = { x: 0, y: 0, k: 1 };
      }
    },

     clearChart() {
      const connectionSvg = this.$refs.connectionSvg;
      if (connectionSvg) {
        d3.select(connectionSvg).selectAll('*').remove();
      }
      this.completedQuestionColumns = [];
      this.activeSessionId = '';
      this.forkExperimentSource = '';
      this.roundsData = [];
      this.newRounds = {};
      this.strategyCanvases = {};
      this.strategyOffsets = {};
      this.draggingStrategy = null;
      this.gridMetrics = null;
    },

    toggleLabels() {
      this.showLabels = !this.showLabels;
      if (this.roundsData.length > 0) {
        this.drawRiverChart();
      }
    },

    handleResize() {
      this.gridMetrics = null;
      if (
        this.roundsData.length > 0 ||
        this.completedQuestionColumns.length > 0 ||
        this.showEmptySessionChrome
      ) {
        this.drawRiverChart();
      }
      if (this.globalMapPoints.length > 0) {
        this.drawGlobalMap();
      }
    },

    /** 左栏「重置」：按当前嵌入容器尺寸重绘全局地图 */
    resetGlobalMapSize() {
      this.$nextTick(() => {
        if (this.globalMapPoints.length > 0) {
          this.drawGlobalMap();
        }
      });
    }
  },

  mounted() {
    this.ensureSessionBatchId();
    this.loadExperimentFileList().then(() => {
      this.$nextTick(() => {
        this.emitMapToolbar();
        this.drawRiverChart();
      });
    });
    this.loadMapData();
    this.connectWebSocket();
    this.emitBackendStatus();
    this.loadGlobalMapData();
    window.addEventListener('resize', this.handleResize);
  },

  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
  }
};
</script>

<style scoped>
#enhanced-river-chart {
  position: relative;
  width: 100%;
  height: 100%; /* 改为100%以适应父容器 */
  overflow: hidden;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

svg {
  width: 100%;
  height: 100%;
  display: block;
}

.river-grid-viewport {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.river-empty-state {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: rgba(120,130,140,0.8);
}

.river-grid-scene {
  position: absolute;
  left: 0;
  top: 0;
  will-change: transform;
}

.river-connection-svg {
  position: absolute;
  inset: 0;
  overflow: visible;
  pointer-events: none;
  z-index: 1;
}

.river-grid-surface {
  position: relative;
  z-index: 2;
  background-image:
    linear-gradient(to right, rgba(148,163,184,0.12) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(148,163,184,0.10) 1px, transparent 1px);
  background-size: 40px 40px;
}

.btn-add-question {
  margin-left: 0.5rem;
  padding: 0.45rem 0.9rem;
  border-radius: 10px;
  border: 1px solid rgba(203, 213, 225, 0.95);
  background: rgba(255, 255, 255, 0.9);
  color: #0f172a;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 0 0 1px rgba(148, 163, 184, 0.25);
}
.btn-add-question:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.session-header-overlay {
  position: absolute;
  z-index: 4;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  font-size: 11px;
  font-weight: 800;
  color: #0e1629;
  background:#bae5fd37;
  border: 1px solid #bae5fd;
  border-radius: 10px;
  box-shadow: 0 0 0 1px rgba(148, 163, 184, 0.25);
  pointer-events: none;
  overflow: hidden;
}
.session-header-overlay:not(.is-empty-prompt) {
  white-space: normal;
  word-break: break-word;
  overflow-wrap: break-word;
  overflow-x: hidden;
  overflow-y: auto;
  line-height: 1.35;
  text-align: center;
}
.session-header-overlay.is-empty-prompt {
  pointer-events: auto;
  cursor: pointer;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.session-header-overlay.is-empty-prompt:hover {
  border-color: rgba(99, 102, 241, 0.75);
}

.session-add-below-btn {
  position: absolute;
  z-index: 6;
  box-sizing: border-box;
  border: none;
  border-radius: 999px;
  padding: 0;
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
  color: #4f46e5;
  background: rgba(255, 255, 255, 0.95);
  box-shadow:
    0 0 0 2px rgba(148, 163, 184, 0.45),
    0 10px 22px rgba(15, 23, 42, 0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
  transition: transform 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
}
.session-add-below-btn:hover {
  background: rgba(99, 102, 241, 0.14);
  transform: scale(1.06);
  box-shadow:
    0 0 0 2px rgba(99, 102, 241, 0.45),
    0 12px 24px rgba(15, 23, 42, 0.12);
}
.session-add-below-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.mini-followup-trigger {
  position: absolute;
  z-index: 7;
  box-sizing: border-box;
  border: none;
  border-radius: 8px;
  padding: 0 6px;
  margin: 0;
  font-size: 11px;
  font-weight: 700;
  line-height: 1.2;
  color: #0f172a;
  background: linear-gradient(135deg, rgb(248, 250, 252), rgb(224, 231, 255));
  box-shadow:
    0 0 0 1px rgba(99, 102, 241, 0.35),
    0 4px 12px rgba(15, 23, 42, 0.08);
  cursor: pointer;
  pointer-events: auto;
  white-space: nowrap;
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.mini-followup-trigger:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow:
    0 0 0 1px rgba(99, 102, 241, 0.55),
    0 6px 14px rgba(15, 23, 42, 0.1);
}
.mini-followup-trigger:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.mini-followup-panel {
  position: absolute;
  z-index: 8;
  box-sizing: border-box;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(148, 163, 184, 0.55);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.12);
  pointer-events: auto;
}
.mini-followup-panel-title {
  font-size: 12px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 8px;
}
.mini-followup-label {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin: 6px 0 4px;
}
.mini-followup-select,
.mini-followup-input {
  width: 100%;
  box-sizing: border-box;
  font-size: 12px;
  padding: 6px 8px;
  border-radius: 8px;
  border: 1px solid rgba(203, 213, 225, 0.95);
}
.mini-followup-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  justify-content: flex-end;
}
.mini-followup-run {
  padding: 6px 12px;
  font-size: 12px;
}

/* 加号位置改为「大追问」文案按钮；新问题条带在整网下方新行展示 */
.session-large-followup-btn {
  position: absolute;
  z-index: 6;
  box-sizing: border-box;
  border: none;
  border-radius: 10px;
  padding: 0 10px;
  margin: 0;
  font-size: 13px;
  font-weight: 700;
  line-height: 1.2;
  color: #4f46e5;
  background: rgba(255, 255, 255, 0.95);
  box-shadow:
    0 0 0 2px rgba(148, 163, 184, 0.45),
    0 10px 22px rgba(15, 23, 42, 0.1);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
  white-space: nowrap;
  transition: transform 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
}
.session-large-followup-btn:hover {
  background: rgba(99, 102, 241, 0.14);
  transform: scale(1.04);
  box-shadow:
    0 0 0 2px rgba(99, 102, 241, 0.45),
    0 12px 24px rgba(15, 23, 42, 0.12);
}
.session-large-followup-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.add-q-modal {
  z-index: 120;
}
.add-q-modal-inner {
  max-width: 480px;
}
.add-q-textarea {
  width: 100%;
  min-height: 88px;
  resize: vertical;
  line-height: 1.4;
  box-sizing: border-box;
}
.add-q-actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
  justify-content: flex-end;
}

.grid-header-cell {
  position: absolute;
  box-sizing: border-box;
  border: 1px solid rgba(203,213,225,0.85);
  background: rgba(248,250,252,0.96);
  border-radius: 12px;
  padding: 10px 14px;
  color: rgba(51,65,85,0.98);
}


.grid-row-label-segment {
  box-sizing: border-box;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0;
  border-bottom: 1px solid rgba(226,232,240,0.85);
}

.grid-row-label-segment--full {
  flex: 1 1 auto;
  min-height: 0;
  width: 100%;
  min-width: 0;
  align-self: stretch;
  justify-content: flex-start;
  border-bottom: none;
  overflow-x: hidden;
  overflow-y: auto;
  padding-top: 0;
  padding-bottom: 12px;
}

.grid-row-label-segment--full .session-question-body {
  white-space: normal;
  word-break: break-word;
  overflow-wrap: break-word;
  line-height: 1.4;
  margin-top: 6px;
}

.grid-row-label-segment:last-child {
  border-bottom: none;
}

.grid-header-title,
.grid-row-title {
  font-size: 13px;
  font-weight: 800;
}

.grid-header-subtitle,
.grid-row-subtitle {
  margin-top: 4px;
  font-size: 11px;
  color: rgba(100,116,139,0.95);
}

.strategy-card {
  position: absolute;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  border-radius: 14px;
  border: 1px solid rgba(191,219,254,0.95);
  background: rgba(255,255,255,0.98);
  box-shadow: 0 10px 24px rgba(15,23,42,0.08);
  overflow: hidden;
  transition: box-shadow 0.18s ease, border-color 0.18s ease;
}

.strategy-card.is-metadata {
  border-color: rgba(40,167,69,0.92);
}

.strategy-card.is-active {
  border-color: rgba(14,165,233,0.9);
  box-shadow: 0 12px 28px rgba(14,165,233,0.18);
}

.strategy-card.highlight-parent-source {
  border-color: #f59e0b !important;
  box-shadow: 0 0 0 3px rgba(245,158,11,0.18), 0 12px 28px rgba(245,158,11,0.12);
}

.strategy-card.is-dragging {
  opacity: 0.94;
  box-shadow: 0 18px 32px rgba(15,23,42,0.18);
}

.strategy-card.drop-merge {
  box-shadow: 0 0 0 3px rgba(59,130,246,0.24), 0 16px 30px rgba(59,130,246,0.12);
}

.strategy-card.drop-swap {
  box-shadow: 0 0 0 3px rgba(16,185,129,0.24), 0 16px 30px rgba(16,185,129,0.12);
}

.strategy-edge {
  position: absolute;
  background: rgba(14,165,233,0.96);
  box-shadow: 0 0 4px rgba(14,165,233,0.22);
  z-index: 5;
}
.strategy-edge.top { left: 0; top: 0; width: 100%; height: 3px; }
.strategy-edge.right { right: 0; top: 0; width: 3px; height: 100%; }
.strategy-edge.bottom { left: 0; bottom: 0; width: 100%; height: 3px; }
.strategy-edge.left { left: 0; top: 0; width: 3px; height: 100%; }

.strategy-card-header {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  gap: 6px;
  padding: 6px 4px;
  background: #f4f6f8;
  border-bottom: 1px solid rgba(226,232,240,0.95);
  cursor: grab;
  user-select: none;
}

.strategy-card-header:active {
  cursor: grabbing;
}

.strategy-card-header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  min-width: 0;
}

.strategy-card-header-left {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 6px;
  min-width: 0;
  flex: 1 1 auto;
}

.strategy-type-badge {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 3px;
  border: 1px solid rgba(148, 163, 184, 0.9);
  background: rgba(255, 255, 255, 0.95);
  font-size: 9px;
  font-weight: 800;
  line-height: 1;
  color: #475569;
  box-sizing: border-box;
}

.strategy-type-badge.is-semantic {
  border-color: rgba(99, 102, 241, 0.45);
  color: rgba(67, 56, 202, 0.95);
  background: rgba(99, 102, 241, 0.1);
}

.strategy-type-badge.is-metadata {
  border-color: rgba(14, 165, 233, 0.5);
  color: rgba(3, 105, 161, 0.95);
  background: rgba(14, 165, 233, 0.1);
}

.strategy-type-badge.is-exact {
  border-color: rgba(234, 179, 8, 0.55);
  color: rgba(161, 98, 7, 0.95);
  background: rgba(250, 204, 21, 0.12);
}

.strategy-type-badge.is-auto {
  border-color: rgba(15, 23, 42, 0.35);
  color: rgba(15, 23, 42, 0.85);
}

.strategy-type-badge.is-unknown {
  opacity: 0.85;
}

.strategy-card-subtitle-main {
  font-size: 11px;
  line-height: 1.15;
  font-weight: 700;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
  flex: 1 1 auto;
  text-align: left;
}

.strategy-card-header-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex: 0 0 auto;
  margin-left: auto;
}

.card-circle-btn {
  width: 20px;
  height: 20px;
  border-radius: 999px;
  border: none;
  background: rgba(255,255,255,0.92);
  color: #475569;
  cursor: pointer;
  font-size: 10px;
  font-weight: 800;
  box-shadow: inset 0 0 0 1px rgba(203,213,225,0.95);
}

.card-circle-btn:hover {
  box-shadow: inset 0 0 0 1px rgba(148,163,184,0.95);
}

.card-circle-btn-primary {
  background: rgba(99,102,241,0.12);
  color: rgba(67,56,202,0.95);
  box-shadow: inset 0 0 0 1px rgba(99,102,241,0.25);
}

.card-circle-btn-danger {
  background: rgba(239,68,68,0.10);
  color: rgba(185,28,28,0.95);
  box-shadow: inset 0 0 0 1px rgba(239,68,68,0.22);
}

.strategy-card-header-line {
  display: flex;
  align-items: center;
  margin: 0 -10px;
  width: 100%;
}

.strategy-card-query-input {
  width: 100%;
  flex: 1;
  min-height: 38px;
  max-height: 120px;
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid rgba(203,213,225,0.95);
  background: rgba(255,255,255,0.95);
  font-size: 12px;
  line-height: 1.25;
  color: #334155;
  outline: none;
  resize: none;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: hidden;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.strategy-card-query-input::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}

.strategy-card-query-input:focus {
  border-color: rgba(99,102,241,0.55);
  box-shadow: 0 0 0 2px rgba(99,102,241,0.14);
}

.strategy-card-title-wrap,
.strategy-card-title,
.strategy-card-subtitle,
.strategy-card-tools,
.card-icon-btn {
  display: none;
}

.strategy-card-map-wrap {
  position: relative;
  flex: 1;
  min-height: 120px;
  overflow: hidden;
}

.strategy-auto-btn {
  position: absolute;
  left: 10px;
  top: 10px;
  z-index: 4;
  height: 22px;
  padding: 0 10px;
  border: none;
  border-radius: 999px;
  background: rgba(15,23,42,0.72);
  color: rgba(226,232,240,0.98);
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(15,23,42,0.20);
}

.strategy-auto-btn:hover {
  background: rgba(15,23,42,0.82);
}

.strategy-mini-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.strategy-card-footer {
  flex: 0 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 0 10px;
  background: #e2e8f0;
  font-size: 10px;
  color: #475569;
}

.strategy-card-footer--eval {
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
}

.strategy-card-footer-eval-left {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 10px;
  min-width: 0;
  flex: 1 1 auto;
}

.strategy-card-footer-media-right {
  flex: 0 0 auto;
  white-space: nowrap;
  font-size: 10px;
  line-height: 1.2;
  color: #64748b;
}

.strategy-eval-stat {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.strategy-eval-stat--filterable {
  cursor: pointer;
  user-select: none;
  border-radius: 4px;
  padding: 1px 4px;
  margin: -1px -4px;
  outline: none;
}

.strategy-eval-stat--filterable:hover {
  background: rgba(15, 23, 42, 0.06);
}

.strategy-eval-stat--filterable.is-mini-map-filter-selected {
  background: rgba(59, 130, 246, 0.12);
  box-shadow: inset 0 0 0 1px rgba(59, 130, 246, 0.38);
}

.strategy-eval-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.grid-resize-handle {
  position: absolute;
  z-index: 8;
}

.grid-resize-handle.col { cursor: col-resize; }
.grid-resize-handle.row { cursor: row-resize; }

.drag-drop-hint {
  position: fixed;
  transform: translate(-50%, -100%);
  z-index: 1200;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(15,23,42,0.88);
  color: #fff;
  font-size: 12px;
  pointer-events: none;
  box-shadow: 0 10px 24px rgba(15,23,42,0.18);
}

/* 注意：不要强行让 svg rect 继承 stroke（会覆盖 d3 里对外框/内框的动态着色）。 */

.question-input {
  flex: 1;
  padding: 10px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s;
}

.question-input:focus {
  outline: none;
  border-color: #4A90E2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.question-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.btn-submit {
  padding: 10px 20px;
  background: #4A90E2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-submit:hover:not(:disabled) {
  background: #357ABD;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
}

.btn-submit:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-secondary {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.btn-tertiary {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.btn-quaternary {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 90%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.plan-summary-modal {
  width: 850px;
}

.plan-summary-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.plan-summary-modal-header h2 {
  margin: 0;
  flex: 1;
  min-width: 0;
}

.plan-summary-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.plan-summary-delete-btn {
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: #c62828;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.plan-summary-delete-btn:hover:not(:disabled) {
  background: #b71c1c;
}

.plan-summary-delete-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.plan-summary-hyde {
  margin: 0 0 12px 0;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(230, 244, 255, 0.65);
  border: 1px solid rgba(100, 170, 230, 0.45);
}

.plan-summary-hyde-title {
  font-size: 12px;
  font-weight: 700;
  color: rgba(45, 75, 105, 0.95);
  margin-bottom: 6px;
}

.plan-summary-hyde-body {
  margin: 0;
  padding: 8px 10px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(135, 206, 250, 0.35);
  font-size: 12px;
  line-height: 1.45;
  color: rgba(35, 55, 75, 0.95);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 260px;
  overflow: auto;
}

.plan-summary-meta {
  padding: 10px 12px;
  margin-bottom: 10px;
  border-radius: 8px;
  background: rgba(248, 249, 250, 1);
  border: 1px solid rgba(135, 206, 250, 0.35);
}

.plan-summary-meta .meta-row {
  display: flex;
  gap: 10px;
  align-items: baseline;
}

.plan-summary-meta .meta-row-top {
  margin-top: 8px;
}

.plan-summary-meta .meta-label {
  width: 92px;
  flex: 0 0 auto;
  font-size: 12px;
  font-weight: 700;
  color: rgba(65, 75, 85, 0.95);
}

.plan-summary-meta .meta-value {
  font-size: 12px;
  color: rgba(95, 105, 115, 0.95);
  word-break: break-word;
}

.plan-summary-meta .meta-pre {
  margin: 6px 0 0 0;
  padding: 8px 10px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 1);
  border: 1px solid rgba(135, 206, 250, 0.35);
  font-size: 12px;
  line-height: 1.35;
  color: rgba(55, 65, 75, 0.95);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 220px;
  overflow: auto;
}

.round-summary-modal {
  width: 950px;
}

.hypothesis-modal {
  width: 1000px;
  max-height: 90vh;
}

.detail-modal {
  width: 750px;
}

.point-detail-modal {
  width: 800px;
  max-width: 90vw;
  max-height: 90vh;
}

.point-detail-modal .modal-header {
  padding: 10px 16px;
  border-bottom-width: 1px;
  border-radius: 12px 12px 0 0;
}

.point-detail-modal .modal-header h2 {
  font-size: 16px;
  font-weight: 600;
}

.point-detail-modal .close-btn {
  font-size: 22px;
  padding: 2px 8px;
  border-radius: 4px;
}

.point-detail-actions-group {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.btn-eval {
  flex: 1;
  padding: 8px;
  border: 1px solid #ccc;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  font-size: 13px;
  transition: all 0.2s;
  color: #64748b;
}

.btn-eval.btn-grow.active { background: #22c55e; color: #fff; border-color: #22c55e; }
.btn-eval.btn-keep.active { background: #0ea5e9; color: #fff; border-color: #0ea5e9; }
.btn-eval.btn-prune.active { background: #ef4444; color: #fff; border-color: #ef4444; }

.point-detail-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(226, 232, 240, 0.9);
}

.btn.danger,
.point-delete-btn {
  background: #dc2626;
  color: #fff;
  border-color: #b91c1c;
}

.btn.danger:hover,
.point-delete-btn:hover {
  background: #b91c1c;
}

/* Hypothesis 弹窗样式 */
.hypothesis-content {
  padding: 20px;
}

.hypothesis-step {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.hypothesis-step h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
  font-size: 18px;
}

.hypothesis-step h4 {
  margin-top: 15px;
  margin-bottom: 10px;
  color: #555;
  font-size: 16px;
}

.hypothesis-step h5 {
  margin-top: 10px;
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
}

.section-item {
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #764ba2;
}

.step-info {
  margin-bottom: 15px;
}

.timestamp {
  font-size: 12px;
  color: #999;
  font-style: italic;
}

.prompt-section {
  margin-bottom: 20px;
}

.prompt-text {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow-y: auto;
  color: #333;
}

.response-section {
  margin-bottom: 20px;
}

.response-text {
  background: #f0f7ff;
  border: 1px solid #b3d9ff;
  border-radius: 4px;
  padding: 15px;
  line-height: 1.8;
  color: #333;
  max-height: 400px;
  overflow-y: auto;
}

.no-hypothesis {
  text-align: center;
  padding: 40px;
  color: #999;
}

.btn-hypothesis {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.btn-hypothesis:hover:not(:disabled) {
  background: linear-gradient(135deg, #5568d3 0%, #653a91 100%);
  transform: translateY(-1px);
}

.btn-hypothesis:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 2px solid #e9ecef;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
}

.modal-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
}

.close-btn {
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

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.modal-body {
  padding: 30px;
  overflow-y: auto;
}

.summary-content {
  line-height: 1.8;
  color: #495057;
  font-size: 15px;
}

.summary-content h1 {
  color: #212529;
  margin-top: 25px;
  margin-bottom: 15px;
  font-size: 24px;
  font-weight: 700;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 10px;
}

.summary-content h2 {
  color: #212529;
  margin-top: 25px;
  margin-bottom: 15px;
  font-size: 20px;
  font-weight: 600;
}

.summary-content h3 {
  color: #495057;
  margin-top: 20px;
  margin-bottom: 10px;
  font-size: 18px;
  font-weight: 600;
}

.summary-content p {
  margin-bottom: 12px;
}

.summary-content ul,
.summary-content ol {
  margin-bottom: 15px;
  padding-left: 25px;
}

.summary-content li {
  margin-bottom: 8px;
}

.summary-content strong {
  color: #212529;
  font-weight: 600;
}

.summary-content em {
  font-style: italic;
  color: #6c757d;
}

.summary-content code {
  background: #f1f3f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #e83e8c;
}

.summary-content pre {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
  border-left: 4px solid #4A90E2;
  margin: 15px 0;
}

.summary-content pre code {
  background: transparent;
  padding: 0;
  color: #495057;
}

.summary-content blockquote {
  border-left: 4px solid #4A90E2;
  padding-left: 15px;
  margin: 15px 0;
  color: #6c757d;
  font-style: italic;
}

.summary-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
}

.summary-content table th,
.summary-content table td {
  border: 1px solid #dee2e6;
  padding: 8px 12px;
  text-align: left;
}

.summary-content table th {
  background: #f8f9fa;
  font-weight: 600;
}

.summary-content .math-block {
  margin: 15px 0;
  text-align: center;
  overflow-x: auto;
}

.summary-content .math-block .katex {
  font-size: 1.1em;
}

.summary-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
}

.chart-container {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-container h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 18px;
}

.chart {
  width: 100%;
  height: 300px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.image-section {
  text-align: center;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 12px;
}

.detail-image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.info-item {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 12px;
  border-left: 4px solid #4A90E2;
}

.info-item h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
}

.entities-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.entities-list li {
  padding: 8px 15px;
  background: white;
  border-radius: 20px;
  border-left: 3px solid #3498db;
  font-size: 14px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.summary-text,
.insight-text {
  line-height: 1.8;
  color: #555;
  margin: 0;
  font-size: 14px;
}

.text-section {
  margin-bottom: 25px;
}

.text-content {
  line-height: 1.8;
  color: #333;
  margin: 0;
  font-size: 14px;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #6c757d;
}

.paper-info {
  line-height: 1.6;
  color: #555;
  margin: 0;
  font-size: 14px;
  font-style: italic;
}

.score-text {
  line-height: 1.6;
  color: #2e7d32;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.follow-up-section {
  background: linear-gradient(135deg, #e8f4f8 0%, #d1ecf1 100%);
  padding: 20px;
  border-radius: 12px;
  border-left: 5px solid #007bff;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
}

.follow-up-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
}

.follow-up-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 15px;
  transition: all 0.3s;
}

.follow-up-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.follow-up-btn {
  width: 100%;
  padding: 12px;
}

.rag-dot {
  transition: all 0.2s ease;
}

.rag-dot:hover {
  filter: brightness(1.3);
}

.river-grid-viewport {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.river-empty-state {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: rgba(120,130,140,0.8);
}

.river-grid-scene {
  position: absolute;
  left: 0;
  top: 0;
  will-change: transform;
}

.river-connection-svg {
  position: absolute;
  inset: 0;
  overflow: visible;
  pointer-events: none;
  z-index: 1;
}

.river-grid-surface {
  position: relative;
  z-index: 2;
  background-image:
    linear-gradient(to right, rgba(148,163,184,0.12) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(148,163,184,0.10) 1px, transparent 1px);
  background-size: 40px 40px;
}

.grid-header-cell {
  position: absolute;
  box-sizing: border-box;
  border: 1px solid rgba(203,213,225,0.85);
  background: rgba(248,250,252,0.96);
  border-radius: 12px;
  padding: 10px 14px;
  color: rgba(51,65,85,0.98);
}



.grid-row-label-segment {
  box-sizing: border-box;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 8px;
  border-bottom: 1px solid rgba(226,232,240,0.85);
}

.grid-row-label-segment--full {
  flex: 1 1 auto;
  min-height: 0;
  width: 80%;
  min-width: 0;
  align-self: stretch;
  justify-content: flex-start;
  border-bottom: none;
  overflow-x: hidden;
  overflow-y: auto;
  padding-top: 12px;
  padding-bottom: 12px;
}

.grid-row-label-segment--full .session-question-body {
  white-space: normal;
  word-break: break-word;
  overflow-wrap: break-word;
  line-height: 1.4;
  margin-top: 6px;
}

.grid-row-label-segment:last-child {
  border-bottom: none;
}

.grid-header-title,
.grid-row-title {
  font-size: 13px;
  font-weight: 800;
}

.grid-header-subtitle,
.grid-row-subtitle {
  margin-top: 4px;
  font-size: 11px;
  color: rgba(100,116,139,0.95);
}

.strategy-card {
  position: absolute;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  border-radius: 14px;
  border: 1px solid rgba(191,219,254,0.95);
  background: rgba(255,255,255,0.98);
  box-shadow: 0 10px 24px rgba(15,23,42,0.08);
  overflow: hidden;
  transition: box-shadow 0.18s ease, border-color 0.18s ease;
}

.strategy-card.is-metadata {
  border-color: rgba(40,167,69,0.92);
}

.strategy-card.is-active {
  border-color: rgba(14,165,233,0.9);
  box-shadow: 0 12px 28px rgba(14,165,233,0.18);
}

.strategy-card.highlight-parent-source {
  border-color: #f59e0b !important;
  box-shadow: 0 0 0 3px rgba(245,158,11,0.18), 0 12px 28px rgba(245,158,11,0.12);
}

.strategy-card.is-dragging {
  opacity: 0.94;
  box-shadow: 0 18px 32px rgba(15,23,42,0.18);
}

.strategy-card.drop-merge {
  box-shadow: 0 0 0 3px rgba(59,130,246,0.24), 0 16px 30px rgba(59,130,246,0.12);
}

.strategy-card.drop-swap {
  box-shadow: 0 0 0 3px rgba(16,185,129,0.24), 0 16px 30px rgba(16,185,129,0.12);
}

.strategy-edge {
  position: absolute;
  background: rgba(14,165,233,0.96);
  box-shadow: 0 0 4px rgba(14,165,233,0.22);
  z-index: 5;
}
.strategy-edge.top { left: 0; top: 0; width: 100%; height: 3px; }
.strategy-edge.right { right: 0; top: 0; width: 3px; height: 100%; }
.strategy-edge.bottom { left: 0; bottom: 0; width: 100%; height: 3px; }
.strategy-edge.left { left: 0; top: 0; width: 3px; height: 100%; }

.strategy-card-header {
  flex: 0 0 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0;
  padding: 4px 12px;
  background: #f4f6f8;
  border-bottom: 1px solid rgba(226,232,240,0.95);
  cursor: grab;
  user-select: none;
}

.strategy-card-header:active {
  cursor: grabbing;
}

.strategy-card-title-wrap {
  min-width: 0;
  flex: 1;
}

.strategy-card-title {
  font-size: 13px;
  line-height: 1.2;
  font-weight: 700;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.strategy-card-subtitle {
  margin-top: 2px;
  font-size: 11px;
  color: rgba(100,116,139,0.95);
}

.strategy-card-tools {
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-icon-btn {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 8px;
  background: rgba(255,255,255,0.92);
  color: #475569;
  cursor: pointer;
  box-shadow: inset 0 0 0 1px rgba(203,213,225,0.95);
}

.strategy-card-map-wrap {
  position: relative;
  flex: 1;
  min-height: 120px;
  overflow: hidden;
}

.strategy-mini-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.strategy-card-footer {
  flex: 0 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 0 10px;
  background: #e2e8f0;
  font-size: 10px;
  color: #475569;
}

.strategy-card-footer--eval {
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
}

.strategy-card-footer-eval-left {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 10px;
  min-width: 0;
  flex: 1 1 auto;
}

.strategy-card-footer-media-right {
  flex: 0 0 auto;
  white-space: nowrap;
  font-size: 10px;
  line-height: 1.2;
  color: #64748b;
}

.strategy-eval-stat {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.strategy-eval-stat--filterable {
  cursor: pointer;
  user-select: none;
  border-radius: 4px;
  padding: 1px 4px;
  margin: -1px -4px;
  outline: none;
}

.strategy-eval-stat--filterable:hover {
  background: rgba(15, 23, 42, 0.06);
}

.strategy-eval-stat--filterable.is-mini-map-filter-selected {
  background: rgba(59, 130, 246, 0.12);
  box-shadow: inset 0 0 0 1px rgba(59, 130, 246, 0.38);
}

.strategy-eval-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.grid-resize-handle {
  position: absolute;
  z-index: 8;
}

.grid-resize-handle.col { cursor: col-resize; }
.grid-resize-handle.row { cursor: row-resize; }

.drag-drop-hint {
  position: fixed;
  transform: translate(-50%, -100%);
  z-index: 1200;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(15,23,42,0.88);
  color: #fff;
  font-size: 12px;
  pointer-events: none;
  box-shadow: 0 10px 24px rgba(15,23,42,0.18);
}

.global-map-content-group {
  cursor: default;
}

.spreadsheet-grid-bg rect {
  shape-rendering: crispEdges;
}

.grid-resize-overlay rect:hover {
  fill: rgba(14, 165, 233, 0.08);
}

.river-connections path {
  pointer-events: stroke;
}

#enhanced-river-chart {
  background: #f8fafc;
}

.river-bg-svg {
  position: absolute;
  inset: 0;
  overflow: visible;
  pointer-events: none;
  z-index: 0;
}

.river-grid-surface {
  position: relative;
  z-index: 2;
  background: transparent !important;
}

.grid-slot-cell {
  position: absolute;
  box-sizing: border-box;
  border-radius: 14px;
  pointer-events: none;
  transition: box-shadow 0.16s ease, border-color 0.16s ease, background-color 0.16s ease;
  z-index: 1;
}

.grid-slot-cell.is-empty {
  border: 1px dashed rgba(203,213,225,0.72);
  background: rgba(255,255,255,0.18);
}

.grid-slot-cell.is-occupied {
  border: 1px solid rgba(203,213,225,0.18);
  background: transparent;
}

.grid-slot-cell.drop-merge {
  border-color: rgba(59,130,246,0.9);
  box-shadow: inset 0 0 0 2px rgba(59,130,246,0.22);
  background: rgba(59,130,246,0.05);
}

.grid-slot-cell.drop-swap,
.grid-slot-cell.drop-move {
  border-color: rgba(16,185,129,0.92);
  box-shadow: inset 0 0 0 2px rgba(16,185,129,0.20);
  background: rgba(16,185,129,0.05);
}

.strategy-card.is-dragging {
  transition: none !important;
}



/* ===== visual cleanup overrides ===== */
#enhanced-river-chart {
  background: #f8fafc !important;
}

.river-grid-viewport {
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
}

.river-bg-svg {
  display: none !important;
}

.river-grid-surface {
  background: none !important;
}

.grid-slot-cell {
  opacity: 0 !important;
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  pointer-events: none !important;
}

.grid-slot-cell.drop-merge,
.grid-slot-cell.drop-swap,
.grid-slot-cell.drop-move {
  opacity: 1 !important;
  border-radius: 16px !important;
}

.grid-slot-cell.drop-merge {
  border: 1.5px solid rgba(59,130,246,0.95) !important;
  background: rgba(59,130,246,0.08) !important;
  box-shadow: inset 0 0 0 2px rgba(59,130,246,0.16) !important;
}

.grid-slot-cell.drop-swap,
.grid-slot-cell.drop-move {
  border: 1.5px solid rgba(16,185,129,0.96) !important;
  background: rgba(16,185,129,0.08) !important;
  box-shadow: inset 0 0 0 2px rgba(16,185,129,0.15) !important;
}

.grid-header-cell {
  border: 1px solid rgba(226,232,240,0.95) !important;
  background: rgba(255,255,255,0.88) !important;
  box-shadow: 0 4px 12px rgba(15,23,42,0.04) !important;
  backdrop-filter: blur(6px);
}


.grid-row-label-segment {
  border-bottom-color: rgba(226,232,240,0.75) !important;
}

.grid-row-label-segment--full {
  border-bottom: none !important;
}

.grid-header-title,
.grid-row-title {
  color: #334155 !important;
}

.grid-header-subtitle,
.grid-row-subtitle {
  color: #94a3b8 !important;
}

.strategy-card {
  border: 1px solid rgba(226,232,240,0.96) !important;
  border-radius: 16px !important;
  background: rgba(255,255,255,0.98) !important;
  box-shadow: 0 10px 28px rgba(15,23,42,0.07) !important;
}

.strategy-card:hover {
  box-shadow: 0 14px 34px rgba(15,23,42,0.10) !important;
}

.strategy-card.is-active {
  border-color: rgba(14,165,233,0.92) !important;
  box-shadow: 0 0 0 3px rgba(14,165,233,0.10), 0 14px 34px rgba(14,165,233,0.10) !important;
}

.strategy-card.is-metadata {
  border-color: rgba(34,197,94,0.72) !important;
}

.strategy-card-header {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
  border-bottom: 1px solid rgba(226,232,240,0.95) !important;
}

.strategy-card-title {
  font-size: 12px !important;
  font-weight: 700 !important;
}

.strategy-card-subtitle {
  color: #94a3b8 !important;
}

.strategy-card-map-wrap {
  background: #ffffff !important;
}

.strategy-card-footer {
  background: #f8fafc !important;
  border-top: 1px solid rgba(226,232,240,0.9);
  color: #64748b !important;
}

.card-icon-btn {
  background: #ffffff !important;
  box-shadow: inset 0 0 0 1px rgba(226,232,240,0.95) !important;
  transition: background 0.15s ease, color 0.15s ease, transform 0.15s ease;
}

.card-icon-btn:hover {
  background: #eff6ff !important;
  color: #0369a1 !important;
  transform: translateY(-1px);
}

.question-input {
  border: 1px solid rgba(203,213,225,0.96) !important;
  box-shadow: none !important;
}

.question-input:focus {
  border-color: rgba(14,165,233,0.8) !important;
  box-shadow: 0 0 0 3px rgba(14,165,233,0.10) !important;
}

.btn-submit {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
  box-shadow: 0 10px 22px rgba(15,23,42,0.16) !important;
}

.btn-submit:hover:not(:disabled) {
  background: linear-gradient(135deg, #111827 0%, #0f172a 100%) !important;
}

.drag-drop-hint {
  background: rgba(15,23,42,0.92) !important;
  box-shadow: 0 12px 26px rgba(15,23,42,0.18) !important;
}

</style>