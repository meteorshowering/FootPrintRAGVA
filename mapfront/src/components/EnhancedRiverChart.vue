<template>
  <div id="enhanced-river-chart">
    <!-- 用户输入区域 -->
    <div class="user-input-section">
      <div class="ws-status" :class="{ connected: wsConnected }">
        {{ wsConnected ? '● 已连接后端' : '○ 未连接' }}
      </div>
      <div class="input-container">
        <input 
          v-model="userQuestion" 
          @keyup.enter="submitUserQuery"
          placeholder="输入您的问题..." 
          class="question-input"
          :disabled="isSubmitting"
        />
        <!-- 交互模式开关 -->
        <div class="interactive-toggle">
          <label>
            <input type="checkbox" v-model="isInteractiveMode" :disabled="isSubmitting">
            开启人工审批模式
          </label>
        </div>
        <button 
          @click="submitUserQuery" 
          class="btn btn-submit"
          :disabled="isSubmitting || !userQuestion.trim()"
        >
          {{ isSubmitting ? '提交中...' : '提交查询' }}
        </button>
      </div>
    </div>

    <!-- Interactive Review Modal -->
    <div v-if="showReviewModal" class="modal" @click.self="closeReviewModal">
      <div class="modal-content review-modal" style="max-width: 800px; max-height: 80vh; overflow-y: auto;">
        <div class="modal-header">
          <h2>检索策略审批 (轮次 {{ reviewRoundNumber }})</h2>
        </div>
        <div class="modal-body">
          <p>以下是大模型为您生成的检索策略，请确认或修改后再执行：</p>
          <div v-for="(plan, index) in reviewPlans" :key="index" class="review-plan-item" style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; border-radius: 4px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <strong>策略 {{ index + 1 }}</strong>
              <button @click="removeReviewPlan(index)" style="color: red; cursor: pointer; border: none; background: none;">删除此策略</button>
            </div>
            
            <div class="form-group" style="margin-bottom: 8px;">
              <label>工具:</label>
              <select v-model="plan.tool_name" style="width: 100%; padding: 4px;">
                <option value="strategy_semantic_search">语义检索 (strategy_semantic_search)</option>
                <option value="strategy_exact_search">精确匹配 (strategy_exact_search)</option>
                <option value="strategy_metadata_search">元数据/文献检索 (strategy_metadata_search)</option>
              </select>
            </div>
            
            <div class="form-group" style="margin-bottom: 8px;">
              <label>目标节点 (ParentNode):</label>
              <input type="text" v-model="plan.ParentNode" style="width: 100%; padding: 4px;" />
            </div>
            
            <div class="form-group" style="margin-bottom: 8px;">
              <label>搜索参数 (Args JSON):</label>
              <textarea :value="JSON.stringify(plan.args, null, 2)" @input="updatePlanArgs(index, $event)" rows="3" style="width: 100%; padding: 4px; font-family: monospace;"></textarea>
            </div>
            
            <div class="form-group">
              <label>大模型理由:</label>
              <div style="font-size: 12px; color: #666; background: #f9f9f9; padding: 4px;">{{ plan.reason }}</div>
            </div>
          </div>
          
          <button @click="addEmptyReviewPlan" style="margin-bottom: 15px; cursor: pointer;">+ 新增一个策略</button>
        </div>
        <div class="modal-footer" style="display: flex; justify-content: flex-end; gap: 10px; border-top: 1px solid #eee; padding-top: 15px;">
          <button @click="submitReviewDecision('abort')" class="btn" style="background: #dc3545; color: white;">终止任务</button>
          <button @click="submitReviewDecision('replace')" class="btn btn-submit">确认并继续执行</button>
        </div>
      </div>
    </div>

    <!-- SVG 画布 -->
    <svg ref="svg" :width="svgWidth" :height="svgHeight"></svg>

    <!-- PlanSummary 弹窗 -->
    <div v-if="showPlanSummaryModal" class="modal" @click.self="closePlanSummaryModal">
      <div class="modal-content plan-summary-modal">
        <div class="modal-header">
          <h2>策略总结 - 轮次 {{ selectedPlanSummary?.roundNumber }} 查询 {{ selectedPlanSummary?.queryIndex + 1 }}</h2>
          <button @click="closePlanSummaryModal" class="close-btn">×</button>
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
          <div class="summary-content" v-html="formatSummary(selectedPlanSummary?.summary)"></div>
        </div>
      </div>
    </div>

    <!-- 数据点详情弹窗 -->
    <div v-if="showPointDetailModal" class="modal" @click.self="closePointDetailModal">
      <div class="modal-content point-detail-modal">
        <div class="modal-header">
          <h2>数据点详情</h2>
          <button @click="closePointDetailModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <ItemDetail v-if="selectedPointDetail" :item="selectedPointDetail" />
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

    <!-- 详情弹窗已移除，详情现在在侧边栏显示 -->

    <!-- 全局地图卡片 -->
    <div 
      v-if="globalMapCardVisible && !globalMapMountId"
      ref="globalMapCard"
      class="global-map-card"
      :style="{ 
        left: globalMapCardPosition.x + 'px', 
        bottom: globalMapCardPosition.y + 'px',
        width: globalMapCardSize.width + 'px',
        height: globalMapCardSize.height + 'px'
      }"
    >
      <div 
        class="global-map-header"
        @mousedown="startDrag"
      >
        <h3>全局地图</h3>
        <div class="global-map-controls">
          <button @click="clearGlobalMapHighlight" class="clear-highlight-btn" title="取消高亮" v-if="Object.keys(highlightedPlanPoints).length > 0">清除</button>
          <button @click="resetGlobalMapSize" class="reset-btn" title="重置大小">↻</button>
          <button @click="toggleGlobalMap" class="close-btn" title="关闭">×</button>
        </div>
      </div>
      <div class="global-map-content">
        <svg ref="globalMapSvg" class="global-map-svg"></svg>
      </div>
      <!-- 调整大小的拖拽手柄 -->
      <div 
        class="resize-handle"
        @mousedown="startResize"
      ></div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3';
import ragService from '../api/ragService';
import { marked } from 'marked';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import ItemDetail from './ItemDetail.vue';

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
  props: {
    plansPerRound: {
      type: Number,
      default: 3
    },
    ragResultsPerPlan: {
      type: Number,
      default: 10
    },
    maxRounds: {
      type: Number,
      default: 5
    },
    // 如果传入该容器 id，则把全局地图渲染到该 DOM 容器中，不再显示覆盖层卡片
    globalMapMountId: {
      type: String,
      default: ''
    },
    ragCollection: {
      type: String,
      default: 'multimodal2text'
    }
  },
  data() {
    return {
      roundsData: [],
      svgWidth: 0,
      svgHeight: 0,
      showLabels: true,
      showConnections: true,
      hidePrunePoints: false,  // 是否隐藏PRUNE节点
      selectedDataFile: 'experiment_results_20260303_181558.json',
      experimentFiles: ['experiment_results_20260303_181558.json'],
      // 布局参数 - 重新设计更美观的布局
      strategyWidth: 400,        // 每个策略画布的宽度
      strategyHeight: 350,        // 每个策略画布的高度
      strategyMargin: 20,         // 策略之间的间距
      roundMargin: 120,           // 轮次之间的间距
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
      // 弹窗相关
      showPlanSummaryModal: false,
      selectedPlanSummary: null,
      showRoundSummaryModal: false,
      selectedRoundSummary: null,
      showPointDetailModal: false,
      selectedPointDetail: null,
      // 用户输入相关
      userQuestion: '',
      isSubmitting: false,
      isInteractiveMode: false,
      // 新增的轮次（用于追问功能）
      newRounds: {},
      // 全局地图相关
      globalMapPoints: [],
      clusterKeywords: [],
      globalMapXScale: null,
      globalMapYScale: null,
      globalMapCardVisible: true,
      globalMapCardPosition: { x: 20, y: 20 },
      globalMapCardSize: { width: 400, height: 300 },
      isDragging: false,
      isResizing: false,
      dragStartPos: { x: 0, y: 0 },
      resizeStartSize: { width: 0, height: 0 },
      resizeStartPos: { x: 0, y: 0 },
      // WebSocket 与后端实时联调
      ws: null,
      wsConnected: false,
      lastSummary: null,
      // 逐步渲染状态：存储 plan、retrieval、evaluation 的状态
      planStates: {}, // { plan_id: { round_number, orchestrator_plan, node_ids: [], evaluated_nodes: {} } }
      incrementalRoundsData: [], // 逐步构建的轮次数据
      // 全局地图高亮相关
      highlightedPlanPoints: {}, // { [nodeId]: { branch_action: 'GROW'|'KEEP'|'PRUNE', ... } } 存储当前高亮的点
      // 存储 experiment_result 以便获取 plansummary
      experimentResult: null, // 存储完整的 experiment_result 数据
      
      // 交互模式审批相关
      showReviewModal: false,
      reviewCheckpoint: null, // 存储 run_id, checkpoint_id 等
      reviewPlans: [],        // 当前正在审批的 plan 列表
      
      // spreadsheet-like layout state
      showLegacyConnections: false,
      persistZoomTransform: null,
      focusedStrategyKey: null,
      hoveredStrategyKey: null,
      useSpreadsheetLayout: true,
      gridState: {
        rowHeights: {},
        columnWidths: {},
        rowOrder: [],
        resizing: null,
        hoveredCellKey: null,
        selectedCellKey: null
      },
      gridMetrics: null,
      // Interactive Report：从策略小地图拖到右侧面板
      reportDragGhostEl: null,
      reportDragPayload: null,
      suppressStrategyDotClick: false
    };
  },
  watch: {
    ragCollection(newVal) {
      console.log('ragCollection changed to', newVal);
      this.loadMapData();
      this.loadGlobalMapData();
    }
  },
  components: {
    ItemDetail
  },
  computed: {
    totalWidth() {
      const maxRound = Math.max(...this.roundsData.map(r => r.round_number), 0);
      return (maxRound + 1) * (this.strategyWidth + this.roundMargin) + this.roundMargin;
    }
  },
  methods: {
    // LeftPanel 控制用：切换实验文件
    setSelectedDataFile(file) {
      if (!file) return;
      this.selectedDataFile = String(file);
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
        return;
      }
      const url = this.getWsUrl();
      console.log('[WS] 正在连接后端:', url);
      try {
        this.ws = new WebSocket(url);
        this.ws.onopen = () => {
          this.wsConnected = true;
          console.log('[WS] ✅ 连接成功:', url);
        };
        this.ws.onclose = (event) => {
          this.wsConnected = false;
          console.log('[WS] ❌ 连接关闭:', event.code, event.reason);
        };
        this.ws.onerror = (e) => {
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
            
            // 处理交互模式下的审批请求
            if (data.type === 'awaiting_user_plan') {
              console.log('[WS] 收到审批请求', data);
              this.reviewCheckpoint = {
                run_id: data.run_id,
                checkpoint_id: data.checkpoint_id
              };
              this.reviewRoundNumber = data.round_number;
              // 深拷贝，防止修改直接影响其他地方
              this.reviewPlans = JSON.parse(JSON.stringify(data.plans || []));
              this.showReviewModal = true;
              return;
            }
            
            // 处理 experiment_result 更新（包含 plansummary）
            if (data.type === 'experiment_result') {
              this.experimentResult = data.data;
              console.log('[WS] 收到 experiment_result，包含 plansummary');
              // 如果有 roundsData，重新绘制以显示 plansummary 按钮
              if (this.roundsData.length > 0) {
                this.$nextTick(() => this.drawRiverChart());
              }
              return;
            }
            
            // 兜底：完整 graph 更新（兼容旧逻辑，也用于逐步渲染时获取节点数据）
            if (data.root_goal != null && data.nodes != null) {
              const rounds = this.graphToRoundsData(data);
              // 如果使用逐步渲染，需要合并 planStates 中的状态
              if (Object.keys(this.planStates).length > 0) {
                // 逐步渲染模式：保留 planStates，更新 roundsData
                this.roundsData = rounds;
                // 确保 planStates 中的节点信息与 graph 同步
                this.syncPlanStatesWithGraph(data);
              } else {
                // 完整更新模式
                this.roundsData = rounds;
              }
              this.$nextTick(() => this.drawRiverChart());
            }
          } catch (e) {
            console.error('[WS] 解析消息失败', e);
          }
        };
      } catch (e) {
        console.error('[WS] 连接失败', e);
      }
    },
    handlePlanCreated(planData) {
      // 第一步：创建空策略框
      const { round_number, plan_id, orchestrator_plan } = planData;
      this.planStates[plan_id] = {
        round_number,
        orchestrator_plan,
        node_ids: [],
        evaluated_nodes: {}
      };
      
      // 确保该轮次存在
      let round = this.incrementalRoundsData.find(r => r.round_number === round_number);
      if (!round) {
        round = { round_number, query_results: [] };
        this.incrementalRoundsData.push(round);
        this.incrementalRoundsData.sort((a, b) => a.round_number - b.round_number);
      }
      
      // 添加空的 query_result（只有 plan，没有 rag_results）
      const queryResult = {
        orchestrator_plan,
        rag_results: []
      };
      round.query_results.push(queryResult);
      
      // 更新 roundsData 并重绘
      this.roundsData = [...this.incrementalRoundsData];
      this.$nextTick(() => this.drawRiverChart());
      console.log('[前端] 策略框已创建:', plan_id);
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
          // 尝试从 experimentResult 中查找对应的 plansummary
          let plansummary = null;
          if (this.experimentResult && this.experimentResult.iterations) {
            const iteration = this.experimentResult.iterations.find(iter => iter.round_number === roundNum);
            if (iteration && iteration.query_results) {
              // 查找匹配的 query_result（通过 tool_name 和 args 匹配）
              const matchingQuery = iteration.query_results.find(qr => {
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
          
          return {
            orchestrator_plan: {
              action: 'call_tool',
              tool_name: plan.tool,
              args: plan.args,
              ParentNode: plan.ParentNode,
              reason: plan.reason,
              plansummary: plansummary
            },
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
        rounds.push({ round_number: roundNum, query_results: queryResults });
      });
      rounds.sort((a, b) => a.round_number - b.round_number);
      return rounds;
    },
    async loadMapData() {
      try {
        const fileName = this.ragCollection === 'LLMvisDataset' 
          ? '/LLMvisDataset_embedding.json' 
          : '/multimodal2text_embeddings_2d.json';
        const response = await fetch(fileName);
        const rawData = await response.json();
        
        // 处理数据格式并建立ID映射
        this.mapPoints = [];
        this.idToPointMap = {};
        
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
          
          // 建立多种ID格式的映射
          // 1. 直接ID映射
          if (item.id) {
            this.idToPointMap[item.id] = point;
          }
          if (item.chunk_id) {
            this.idToPointMap[item.chunk_id] = point;
          }
          
          // 2. 从metadata中提取figure_id
          try {
            if (item.metadata) {
              let metadataObj = item.metadata;
              if (typeof metadataObj === 'string') {
                metadataObj = JSON.parse(metadataObj);
              }
              
              // 检查metadata中的figure_id
              if (metadataObj.figure_id) {
                this.idToPointMap[metadataObj.figure_id] = point;
              }
              
              // 检查嵌套的metadata字段
              if (metadataObj.metadata && typeof metadataObj.metadata === 'string') {
                const innerMetadata = JSON.parse(metadataObj.metadata);
                if (innerMetadata.figure_id) {
                  this.idToPointMap[innerMetadata.figure_id] = point;
                }
              }
            }
          } catch (e) {
            // 解析失败，忽略
          }
        });
        
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
      
      // 4. 在mapPoints中查找（通过metadata）
      for (const point of this.mapPoints) {
        try {
          if (point.metadata) {
            let metadataObj = point.metadata;
            if (typeof metadataObj === 'string') {
              metadataObj = JSON.parse(metadataObj);
            }
            
            if (metadataObj.figure_id === idStr || metadataObj.id === idStr) {
              return point;
            }
            
            if (metadataObj.metadata && typeof metadataObj.metadata === 'string') {
              const innerMetadata = JSON.parse(metadataObj.metadata);
              if (innerMetadata.figure_id === idStr || innerMetadata.id === idStr) {
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

    async loadAllRounds() {
      this.clearChart();
      await this.loadMapData();
      
      try {
        const response = await fetch(`/${this.selectedDataFile}`);
        const experimentData = await response.json();
        // 保存完整的 experiment_result，包括 hypothesis
        this.experimentResult = experimentData;
        // 同时保存到store，供DetailView使用
        this.$store.commit('setExperimentResult', experimentData);
        this.roundsData = (experimentData.iterations || []).filter(round => round && round.round_number !== undefined);
        this.roundsData.sort((a, b) => a.round_number - b.round_number);
        
        console.log('加载的实验数据:', this.roundsData);
        console.log('Hypothesis 数据:', experimentData.hypothesis);
        this.drawRiverChart();
      } catch (error) {
        console.error('加载实验数据失败:', error);
      }
    },

    // FootprintRAG风格：确保箭头标记存在
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
      const allRounds = [...(this.roundsData || [])];
      Object.values(this.newRounds || {}).forEach((r) => {
        if (!allRounds.find(x => x.round_number === r.round_number)) {
          allRounds.push(r);
        }
      });
      allRounds.sort((a, b) => a.round_number - b.round_number);
      return allRounds;
    },

    ensureGridSizing(allRounds) {
      const roundNumbers = allRounds.map(r => r.round_number);
      const maxQueryCount = Math.max(1, ...allRounds.map(r => Array.isArray(r.query_results) ? r.query_results.length : 0));
      if (!this.gridState.columnWidths['label']) this.gridState.columnWidths['label'] = 92;
      roundNumbers.forEach(roundNo => {
        if (!this.gridState.columnWidths[`round-${roundNo}`]) this.gridState.columnWidths[`round-${roundNo}`] = this.strategyWidth;
      });
      if (!this.gridState.rowHeights['header']) this.gridState.rowHeights['header'] = 58;
      for (let i = 0; i < maxQueryCount; i++) {
        const key = `row-${i}`;
        if (!this.gridState.rowHeights[key]) this.gridState.rowHeights[key] = this.strategyHeight + 24;
      }
      this.gridState.rowOrder = Array.from({ length: maxQueryCount }, (_, i) => i);
    },

    buildGridMetrics(allRounds) {
      this.ensureGridSizing(allRounds);
      const roundNumbers = allRounds.map(r => r.round_number);
      const maxQueryCount = Math.max(1, ...allRounds.map(r => Array.isArray(r.query_results) ? r.query_results.length : 0));
      const startX = this.roundMargin;
      const startY = this.roundMargin;
      const colPositions = {};
      const rowPositions = {};
      let x = startX;
      colPositions['label'] = { x, width: this.gridState.columnWidths['label'] };
      x += this.gridState.columnWidths['label'];
      roundNumbers.forEach(roundNo => {
        colPositions[`round-${roundNo}`] = { x, width: this.gridState.columnWidths[`round-${roundNo}`] };
        x += this.gridState.columnWidths[`round-${roundNo}`] + this.strategyMargin;
      });
      let y = startY;
      rowPositions['header'] = { y, height: this.gridState.rowHeights['header'] };
      y += this.gridState.rowHeights['header'] + 10;
      for (let i = 0; i < maxQueryCount; i++) {
        rowPositions[`row-${i}`] = { y, height: this.gridState.rowHeights[`row-${i}`] };
        y += this.gridState.rowHeights[`row-${i}`] + this.strategyMargin;
      }
      return { roundNumbers, maxQueryCount, colPositions, rowPositions, totalWidth: x + this.roundMargin, totalHeight: y + this.roundMargin };
    },

    getStrategyCellRect(metrics, roundNumber, queryIndex) {
      const col = metrics.colPositions[`round-${roundNumber}`];
      const row = metrics.rowPositions[`row-${queryIndex}`];
      if (!col || !row) return null;
      const padX = 10;
      const padY = 6;
      return { x: col.x + padX, y: row.y + padY, width: Math.max(180, col.width - padX * 2), height: Math.max(140, row.height - padY * 2) };
    },

    getRoundHeaderRect(metrics, roundNumber) {
      const col = metrics.colPositions[`round-${roundNumber}`];
      const row = metrics.rowPositions['header'];
      if (!col || !row) return null;
      return { x: col.x, y: row.y, width: col.width, height: row.height };
    },

    getRowLabelRect(metrics, queryIndex) {
      const col = metrics.colPositions['label'];
      const row = metrics.rowPositions[`row-${queryIndex}`];
      if (!col || !row) return null;
      return { x: col.x, y: row.y, width: col.width, height: row.height };
    },

    getColumnResizeHandles(metrics) {
      const handles = [];
      Object.entries(metrics.colPositions).forEach(([key, col]) => {
        if (key === 'label') return;
        handles.push({ key, x: col.x + col.width, y: metrics.rowPositions['header'].y, width: 8, height: Object.values(metrics.rowPositions).reduce((acc, r) => Math.max(acc, r.y + r.height), 0) - metrics.rowPositions['header'].y + 20 });
      });
      return handles;
    },

    getRowResizeHandles(metrics) {
      const handles = [];
      Object.entries(metrics.rowPositions).forEach(([key, row]) => {
        if (key === 'header') return;
        handles.push({ key, x: metrics.colPositions['label'].x, y: row.y + row.height, width: Object.values(metrics.colPositions).reduce((acc, c) => Math.max(acc, c.x + c.width), 0) - metrics.colPositions['label'].x + 20, height: 8 });
      });
      return handles;
    },

    getStrategyKey(roundNumber, queryIndex) {
      return `${roundNumber}__${queryIndex}`;
    },

    getActiveStrategyInfo() {
      const activeKey = this.focusedStrategyKey || this.hoveredStrategyKey;
      if (!activeKey) return null;
      const [roundStr, queryStr] = activeKey.split('__');
      const roundNumber = Number(roundStr);
      const queryIndex = Number(queryStr);
      const round = this.getAllRounds().find(r => r.round_number === roundNumber);
      const query = round?.query_results?.[queryIndex];
      if (!query) return null;
      return { key: activeKey, roundNumber, queryIndex, query };
    },

    findDirectParentKey(roundNumber, queryIndex, query) {
      const parentNode = query?.orchestrator_plan?.ParentNode ?? query?.orchestrator_plan?.parentNode ?? null;
      if (parentNode == null) return null;
      const prevRoundNumber = roundNumber - 1;
      if (prevRoundNumber < 0) return null;
      const prevRound = this.getAllRounds().find(r => r.round_number === prevRoundNumber);
      if (!prevRound || !Array.isArray(prevRound.query_results)) return null;
      const parentId = String(parentNode).trim();
      if (!parentId || parentId === 'ROOT' || parentId === '0') return null;
      if (/^\d+$/.test(parentId)) {
        const prevIdx = parseInt(parentId, 10) - 1;
        if (prevIdx >= 0 && prevIdx < prevRound.query_results.length) return this.getStrategyKey(prevRoundNumber, prevIdx);
      }
      for (let i = 0; i < prevRound.query_results.length; i++) {
        const prevQuery = prevRound.query_results[i];
        const hit = (prevQuery?.rag_results || []).some((rag) => {
          const id = rag?.retrieval_result?.id;
          if (id == null) return false;
          const sid = String(id);
          return sid === parentId || sid === `img_${parentId}` || (parentId.startsWith('img_') && sid === parentId.replace('img_', ''));
        });
        if (hit) return this.getStrategyKey(prevRoundNumber, i);
      }
      return null;
    },

    findDirectChildrenKeys(roundNumber, queryIndex) {
      const currentKey = this.getStrategyKey(roundNumber, queryIndex);
      const nextRound = this.getAllRounds().find(r => r.round_number === roundNumber + 1);
      if (!nextRound || !Array.isArray(nextRound.query_results)) return [];
      const children = [];
      nextRound.query_results.forEach((q, idx) => {
        const parentKey = this.findDirectParentKey(roundNumber + 1, idx, q);
        if (parentKey === currentKey) children.push(this.getStrategyKey(roundNumber + 1, idx));
      });
      return children;
    },

    getCardHighlightEdges(roundNumber, queryIndex) {
      const active = this.getActiveStrategyInfo();
      if (!active) return [];
      const selfKey = this.getStrategyKey(roundNumber, queryIndex);
      if (selfKey === active.key) return ['top', 'right', 'bottom', 'left'];
      const activeParentKey = this.findDirectParentKey(active.roundNumber, active.queryIndex, active.query);
      if (selfKey === activeParentKey) return ['right'];
      const activeChildrenKeys = this.findDirectChildrenKeys(active.roundNumber, active.queryIndex);
      if (activeChildrenKeys.includes(selfKey)) return ['left'];
      return [];
    },

    drawHighlightEdges(group, x, y, width, height, edges = []) {
      const edgeColor = 'rgba(14,165,233,0.96)';
      const shadow = 'rgba(14,165,233,0.22)';
      if (edges.includes('top')) group.append('rect').attr('x', x).attr('y', y).attr('width', width).attr('height', 3).attr('fill', edgeColor).style('filter', `drop-shadow(0 0 4px ${shadow})`);
      if (edges.includes('right')) group.append('rect').attr('x', x + width - 3).attr('y', y).attr('width', 3).attr('height', height).attr('fill', edgeColor).style('filter', `drop-shadow(0 0 4px ${shadow})`);
      if (edges.includes('bottom')) group.append('rect').attr('x', x).attr('y', y + height - 3).attr('width', width).attr('height', 3).attr('fill', edgeColor).style('filter', `drop-shadow(0 0 4px ${shadow})`);
      if (edges.includes('left')) group.append('rect').attr('x', x).attr('y', y).attr('width', 3).attr('height', height).attr('fill', edgeColor).style('filter', `drop-shadow(0 0 4px ${shadow})`);
    },

    drawGridBackground(container, metrics) {
      const bg = container.append('g').attr('class', 'spreadsheet-grid-bg');
      Object.entries(metrics.colPositions).forEach(([key, col]) => {
        Object.entries(metrics.rowPositions).forEach(([rowKey, row]) => {
          const isHeader = rowKey === 'header';
          const isLabel = key === 'label';
          bg.append('rect').attr('x', col.x).attr('y', row.y).attr('width', col.width).attr('height', row.height).attr('fill', isHeader ? 'rgba(248,250,252,0.96)' : isLabel ? 'rgba(250,252,255,0.96)' : '#ffffff').attr('stroke', 'rgba(203,213,225,0.85)').attr('stroke-width', 1);
        });
      });
    },

    drawSpreadsheetHeaders(container, allRounds, metrics) {
      const headerRow = metrics.rowPositions['header'];
      allRounds.forEach((round) => {
        const rect = this.getRoundHeaderRect(metrics, round.round_number);
        if (!rect) return;
        const g = container.append('g').attr('class', `grid-round-header-${round.round_number}`);
        g.append('text').attr('x', rect.x + 14).attr('y', rect.y + 25).attr('font-size', '13px').attr('font-weight', '800').attr('fill', 'rgba(51,65,85,0.98)').text(`Round ${round.round_number}`);
        g.append('text').attr('x', rect.x + 14).attr('y', rect.y + 44).attr('font-size', '11px').attr('fill', 'rgba(100,116,139,0.95)').text(`${round.query_results?.length || 0} strategy cells`);
      });
      const labelCol = metrics.colPositions['label'];
      container.append('text').attr('x', labelCol.x + 16).attr('y', headerRow.y + 34).attr('font-size', '12px').attr('font-weight', '800').attr('fill', 'rgba(71,85,105,0.95)').text('Rows');
    },

    drawSpreadsheetRowLabels(container, metrics) {
      const rowKeys = Object.keys(metrics.rowPositions).filter(k => k !== 'header');
      rowKeys.forEach((rowKey, idx) => {
        const rect = this.getRowLabelRect(metrics, idx);
        if (!rect) return;
        container.append('text').attr('x', rect.x + 16).attr('y', rect.y + 26).attr('font-size', '12px').attr('font-weight', '700').attr('fill', 'rgba(71,85,105,0.95)').text(`Row ${idx + 1}`);
        container.append('text').attr('x', rect.x + 16).attr('y', rect.y + 46).attr('font-size', '11px').attr('fill', 'rgba(100,116,139,0.95)').text('Strategy slot');
      });
    },

    addGridResizeHandles(svg, metrics) {
      const overlay = svg.append('g').attr('class', 'grid-resize-overlay');
      this.getColumnResizeHandles(metrics).forEach(handle => {
        overlay.append('rect').attr('x', handle.x - 4).attr('y', handle.y).attr('width', handle.width).attr('height', handle.height).attr('fill', 'transparent').style('cursor', 'col-resize').on('mousedown', (event) => {
          event.stopPropagation();
          const startX = event.clientX;
          const colKey = handle.key;
          const startWidth = this.gridState.columnWidths[colKey];
          const onMove = (e) => { this.gridState.columnWidths[colKey] = Math.max(220, startWidth + (e.clientX - startX)); this.drawRiverChart(); };
          const onUp = () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
          window.addEventListener('mousemove', onMove);
          window.addEventListener('mouseup', onUp);
        });
      });
      this.getRowResizeHandles(metrics).forEach(handle => {
        overlay.append('rect').attr('x', handle.x).attr('y', handle.y - 4).attr('width', handle.width).attr('height', handle.height).attr('fill', 'transparent').style('cursor', 'row-resize').on('mousedown', (event) => {
          event.stopPropagation();
          const startY = event.clientY;
          const rowKey = handle.key;
          const startHeight = this.gridState.rowHeights[rowKey];
          const onMove = (e) => { this.gridState.rowHeights[rowKey] = Math.max(180, startHeight + (e.clientY - startY)); this.drawRiverChart(); };
          const onUp = () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
          window.addEventListener('mousemove', onMove);
          window.addEventListener('mouseup', onUp);
        });
      });
    },

    drawRiverChart() {
      const svg = d3.select(this.$refs.svg);
      svg.selectAll('*').remove();
      svg.style('background', '#FFFFFF');

      if (!this.roundsData || this.roundsData.length === 0) {
        svg.append('text')
          .attr('x', '50%')
          .attr('y', '50%')
          .attr('text-anchor', 'middle')
          .attr('font-size', '14px')
          .attr('fill', 'rgba(120,130,140,0.8)')
          .text('没有可用的实验数据');
        return;
      }

      this.svgWidth = this.$el.clientWidth;
      this.svgHeight = this.$el.clientHeight;
      svg.attr('width', this.svgWidth).attr('height', this.svgHeight);
      this._ensureArrowhead(svg);

      svg.on('click', (event) => {
        if (event.target === svg.node()) {
          this.focusedStrategyKey = null;
          this.hoveredStrategyKey = null;
          this.drawRiverChart();
        }
      });

      this.connectionGroup = svg.append('g').attr('class', 'river-connections');
      const container = svg.append('g').attr('class', 'river-container');
      this.containerGroup = container;
      this.strategyCanvases = {};

      const allRounds = this.getAllRounds();
      const metrics = this.buildGridMetrics(allRounds);
      this.gridMetrics = metrics;

      this.drawGridBackground(container, metrics);
      this.drawSpreadsheetHeaders(container, allRounds, metrics);
      this.drawSpreadsheetRowLabels(container, metrics);

      allRounds.forEach((round) => {
        if (!Array.isArray(round.query_results)) return;
        round.query_results.forEach((query, queryIndex) => {
          const rect = this.getStrategyCellRect(metrics, round.round_number, queryIndex);
          if (!rect) return;

          const isEmptyQuery = !query.rag_results || query.rag_results.length === 0;
          const strategyGroup = container.append('g')
            .attr('class', `strategy-${round.round_number}-${queryIndex}`)
            .attr('data-round', round.round_number)
            .attr('data-query', queryIndex);

          const cardX = rect.x;
          const cardY = rect.y;
          const cardW = rect.width;
          const cardH = rect.height;
          
          const col = metrics.colPositions[`round-${round.round_number}`];
          const row = metrics.rowPositions[`row-${queryIndex}`];
          const outerX = col ? col.x : cardX;
          const outerY = row ? row.y : cardY;
          const outerW = col ? col.width : cardW;
          const outerH = row ? row.height : cardH;

          const selfKey = this.getStrategyKey(round.round_number, queryIndex);
          const activeKey = this.focusedStrategyKey || this.hoveredStrategyKey;
          const isActive = activeKey === selfKey;
          const highlightEdges = this.getCardHighlightEdges(round.round_number, queryIndex);
          const toolNameForFrame = query?.orchestrator_plan?.tool_name;
          const isMetadataSearchForFrame = toolNameForFrame === 'strategy_metadata_search';
          const cardStroke = isActive ? 'rgba(14,165,233,0.9)' : isMetadataSearchForFrame ? 'rgba(40,167,69,0.92)' : 'rgba(191,219,254,0.95)';

          const cardFrame = strategyGroup.append('g')
            .attr('class', 'card-frame')
            .style('cursor', 'pointer')
            .on('mouseenter', () => { this.hoveredStrategyKey = selfKey; })
            .on('mouseleave', () => { if (!this.focusedStrategyKey) this.hoveredStrategyKey = null; })
            .on('click', (event) => {
              if (this.draggingStrategy && this.draggingStrategy.roundNumber === round.round_number && this.draggingStrategy.queryIndex === queryIndex) return;
              event.stopPropagation();
              this.focusedStrategyKey = selfKey;
              this.highlightPlanPointsInGlobalMap(query);
              this.drawRiverChart();
            })
            .on('dblclick', () => {
              if (this.draggingStrategy && this.draggingStrategy.roundNumber === round.round_number && this.draggingStrategy.queryIndex === queryIndex) return;
              if (query.orchestrator_plan && query.orchestrator_plan.plansummary) {
                let argsForModal = this.cleanPlanArgs(query.orchestrator_plan.args);
                if (query?.orchestrator_plan?.tool_name === 'strategy_metadata_search') {
                  const firstRag = query?.rag_results?.[0];
                  const rr = firstRag?.retrieval_result || {};
                  const fallbackPaperId = query?.orchestrator_plan?.args?.paper_id || query?.orchestrator_plan?.args?.paperid || rr?.source_args?.paper_id || rr?.source_args?.paperid || rr?.metadata?.paper_id || rr?.metadata?.paperid || rr?.paper_id || rr?.paperid || '';
                  const isEmptyObj = argsForModal == null || (typeof argsForModal === 'object' && !Array.isArray(argsForModal) && Object.keys(argsForModal).length === 0);
                  if (isEmptyObj && fallbackPaperId) argsForModal = { paper_id: fallbackPaperId };
                }
                this.showPlanSummary({ roundNumber: round.round_number, queryIndex, parentNode: query.orchestrator_plan.ParentNode ?? query.orchestrator_plan.parentNode ?? null, args: argsForModal, reason: query.orchestrator_plan.reason ?? '', summary: query.orchestrator_plan.plansummary });
              }
            });

          // 外框（取代了之前的内框，外框有了颜色变化的功能）
          cardFrame.append('rect')
            .attr('x', outerX)
            .attr('y', outerY)
            .attr('width', outerW)
            .attr('height', outerH)
            .attr('rx', 0)
            .attr('ry', 0)
            .attr('fill', '#ffffff')
            .attr('stroke', cardStroke)
            .attr('stroke-width', isActive ? 1.8 : 1)
            .attr('data-orig-stroke', cardStroke)
            .attr('data-orig-stroke-width', isActive ? 1.8 : 1);

          this.drawHighlightEdges(cardFrame, outerX, outerY, outerW, outerH, highlightEdges);

          const dragHeaderGroup = strategyGroup.append('g').attr('class', 'drag-header').style('cursor', 'grab');
          dragHeaderGroup.append('rect')
            .attr('x', outerX)
            .attr('y', outerY)
            .attr('width', outerW)
            .attr('height', 44) // 顶部区域作为拖动把手
            .attr('fill', 'transparent');

          if (this.showLabels) {
            const toolNameRaw = query?.orchestrator_plan?.tool_name;
            const args = query?.orchestrator_plan?.args || {};
            let argSummary = args.query_intent ? String(args.query_intent) : '';
            if (!argSummary) {
              const entries = Object.entries(args);
              if (entries.length > 0) argSummary = entries.map(([k, v]) => `${k}=${typeof v === 'object' ? JSON.stringify(v) : String(v)}`).join(', ');
            }
            
            const mergedInfo = query.merged_from && query.merged_from.length > 0 ? ` (+ ${query.merged_from.join(' + ')})` : '';
            
            dragHeaderGroup.append('text').attr('x', cardX + 12).attr('y', cardY + 18).attr('font-size', '11px').attr('font-weight', '800').attr('fill', 'rgba(51,65,85,0.96)').style('pointer-events', 'none').text(`R${round.round_number}.${queryIndex + 1}${mergedInfo}`);
            dragHeaderGroup.append('text').attr('x', cardX + 12).attr('y', cardY + 34).attr('font-size', '10px').attr('fill', 'rgba(100,116,139,0.95)').style('pointer-events', 'none').text(String(toolNameRaw || 'strategy').slice(0, 52));
            dragHeaderGroup.append('line').attr('x1', cardX + 10).attr('y1', cardY + 44).attr('x2', cardX + cardW - 10).attr('y2', cardY + 44).attr('stroke', 'rgba(203,213,225,0.9)').attr('stroke-width', 1).style('pointer-events', 'none');
            
            if (argSummary) strategyGroup.append('text').attr('x', cardX + 12).attr('y', cardY + cardH - 12).attr('font-size', '10px').attr('fill', 'rgba(100,116,139,0.92)').text(String(argSummary).slice(0, 60));
          
            // 添加拆分按钮
            if (query.merged_from && query.merged_from.length > 0) {
              const splitBtn = dragHeaderGroup.append('g')
                .attr('class', 'split-btn')
                .style('cursor', 'pointer')
                .attr('transform', `translate(${cardX + cardW - 36}, ${cardY + 8})`);
                
              splitBtn.append('rect')
                .attr('width', 24)
                .attr('height', 14)
                .attr('rx', 2)
                .attr('fill', 'rgba(239, 68, 68, 0.1)')
                .attr('stroke', 'rgba(239, 68, 68, 0.4)');
                
              splitBtn.append('text')
                .attr('x', 12)
                .attr('y', 10)
                .attr('text-anchor', 'middle')
                .attr('font-size', '9px')
                .attr('fill', '#ef4444')
                .text('拆分');
                
              splitBtn.on('mousedown', (event) => {
                event.stopPropagation(); // 阻止触发拖拽
              });
              splitBtn.on('click', (event) => {
                event.stopPropagation();
                this.splitMergedStrategies(round.round_number, queryIndex);
              });
            }
          }

          if (!isEmptyQuery) this.drawStrategyMap(strategyGroup, query, cardX, cardY, cardW, cardH, round.round_number, queryIndex);

          if (!this.strategyCanvases[round.round_number]) this.strategyCanvases[round.round_number] = {};
          this.strategyCanvases[round.round_number][queryIndex] = new StrategyCanvas(round.round_number, queryIndex, cardX, cardY, cardW, cardH);
          const plan = query.orchestrator_plan || {};
          this.strategyCanvases[round.round_number][queryIndex].parentNode = plan.ParentNode ?? plan.parentNode ?? null;
          this.strategyCanvases[round.round_number][queryIndex].isEmptyQuery = isEmptyQuery;
          this._addDragBehavior(dragHeaderGroup, strategyGroup, round.round_number, queryIndex);
        });
      });

      this.addGridResizeHandles(svg, metrics);
      this.addZoomBehavior(svg);
      if (this.showLegacyConnections) this.drawConnections();
    },

    drawStrategyMap(strategyGroup, query, rectX, rectY, rectWidth, rectHeight, roundNumber, queryIndex) {
      // const isEmptyQuery = !query.rag_results || query.rag_results.length === 0;
      const ragPoints = [];
      const missingIds = [];
      let skippedPruneCount = 0;

      query.rag_results.forEach(rag => {
        // 如果启用了隐藏PRUNE，跳过PRUNE节点
        if (this.hidePrunePoints) {
          const branchAction = rag.evaluation?.branch_action || 'UNKNOWN';
          if (branchAction === 'PRUNE') {
            skippedPruneCount += 1;
            return; // 跳过PRUNE节点
          }
        }

        const pointId = rag.retrieval_result.id;
        const point = this.findPointById(pointId);

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
        console.warn(`轮次${roundNumber}查询${queryIndex}: 以下检索ID在当前底图嵌入文件中无坐标，故不绘制（仍可在列表/详情中查看）:`, missingIds);
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
      
      // FootprintRAG风格：地图布局参数
      const cardPad = 12;
      const cardTitleH = 44;
      const cardFooterH = 22;
      
      const mapX = rectX + cardPad;
      const mapY = rectY + cardTitleH + cardPad;
      const mapW = rectWidth - cardPad * 2;
      const mapH = rectHeight - cardTitleH - cardFooterH - cardPad * 2;
      
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
            this.roundsData.forEach(r => {
              if (!r.query_results) return;
              r.query_results.forEach((q, qIdx) => {
                if (q.rag_results && q.rag_results.some(rag => {
                  const ragPoint = this.findPointById(rag.retrieval_result.id);
                  return (ragPoint && ragPoint.id === matchId) || rag.retrieval_result.id === matchId;
                })) {
                  // 找到了包含这个 parentNode 的卡片，高亮它的外框
                  d3.select(`.strategy-${r.round_number}-${qIdx} .card-frame rect`)
                    .classed('highlight-parent-source', true)
                    .attr('stroke', '#f59e0b') // 橙色高亮
                    .attr('stroke-width', 3);
                }
              });
            });
          }
        })
        .on('mouseleave', () => {
          // 恢复所有被高亮的卡片
          d3.selectAll('.card-frame rect.highlight-parent-source')
            .classed('highlight-parent-source', false)
            .each(function() {
               const stroke = d3.select(this).attr('data-orig-stroke');
               const width = d3.select(this).attr('data-orig-stroke-width');
               d3.select(this)
                 .attr('stroke', stroke || 'rgba(191,219,254,0.95)')
                 .attr('stroke-width', width || 1);
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
      
      const xExtent = this.globalXExtent;
      const yExtent = this.globalYExtent;
      const xRange = xExtent[1] - xExtent[0];
      const yRange = yExtent[1] - yExtent[0];
      const marginRatio = 0.12; // FootprintRAG风格：12%边距
      
      const adjustedXExtent = [xExtent[0] - xRange * marginRatio, xExtent[1] + xRange * marginRatio];
      const adjustedYExtent = [yExtent[0] - yRange * marginRatio, yExtent[1] + yRange * marginRatio];
      
      const pad = 6;
      const xScale = d3.scaleLinear()
        .domain(adjustedXExtent)
        .range([pad, mapW - pad]);
      
      const yScale = d3.scaleLinear()
        .domain(adjustedYExtent)
        .range([mapH - pad, pad]);
      
      // 绘制背景点（FootprintRAG风格）
      const baseDotMax = 200;
      let sample = this.mapPoints;
      if (this.mapPoints.length > baseDotMax) {
        const step = Math.ceil(this.mapPoints.length / baseDotMax);
        sample = this.mapPoints.filter((_, i) => i % step === 0);
      }
      
      const dotSamplePx = sample
        .map(p => ({ x: xScale(p.x), y: yScale(p.y) }))
        .filter(p => Number.isFinite(p.x) && Number.isFinite(p.y));
      
      // 绘制等高线（FootprintRAG风格）
      const densityPts = this.mapPoints
        .map(p => ({ x: xScale(p.x), y: yScale(p.y) }))
        .filter(p => Number.isFinite(p.x) && Number.isFinite(p.y));
      
      let contours = [];
      if (densityPts.length >= 10) {
        const contourLevels = 16; // FootprintRAG风格：16层
        const contourBandwidthRatio = 0.070; // FootprintRAG风格：7%带宽
        const bw = Math.max(10, Math.min(mapW, mapH) * contourBandwidthRatio);
        
        contours = d3.contourDensity()
          .x(d => d.x)
          .y(d => d.y)
          .size([mapW, mapH])
          .bandwidth(bw)
          .thresholds(contourLevels)(densityPts);
      }
      
      if (contours && contours.length > 0) {
        const path = d3.geoPath();
        
        // 按值排序（低到高，以便填充层叠正确）
        const cs = [...contours].sort((a, b) => (a?.value ?? 0) - (b?.value ?? 0));
        
        // 归一化值用于填充
        const vMin = d3.min(cs, d => d?.value) ?? 0;
        const vMax = d3.max(cs, d => d?.value) ?? 1;
        const denom = (vMax - vMin) || 1;
        const tOf = (d) => Math.max(0, Math.min(1, ((d?.value ?? vMin) - vMin) / denom));
        
        // 填充层叠：密度越高，颜色越深，透明度越低
        const gamma = 1.25; // <2 保持层可见
        const tAdj = (t) => Math.pow(t, gamma);
        
        // FootprintRAG风格：固定描边样式（不随密度变化）
        const STROKE_COLOR = 'rgba(120,130,140,0.75)';
        const STROKE_W = 0.45;
        const STROKE_OP = 0.85;
        
        const contourGroup = zoomG.append('g').attr('class', 'density-contours');
        
        contourGroup.selectAll('path')
          .data(cs)
          .enter()
          .append('path')
          .attr('d', path)
          // 填充（层叠）
          .attr('fill', d => d3.interpolateGreys(0.02 + 0.28 * tAdj(tOf(d))))
          .attr('fill-opacity', d => 0.03 + 0.10 * tAdj(tOf(d)))
          // 固定描边
          .attr('stroke', STROKE_COLOR)
          .attr('stroke-opacity', STROKE_OP)
          .attr('stroke-width', STROKE_W)
          .attr('stroke-linejoin', 'round')
          .attr('stroke-linecap', 'round')
          // 缩放时线宽不变（论文图风格）
          .attr('vector-effect', 'non-scaling-stroke');
      }
      
      // 绘制背景点（FootprintRAG风格）
      if (dotSamplePx.length > 0) {
        zoomG.append('g')
          .attr('class', 'global-dots')
          .selectAll('circle')
          .data(dotSamplePx)
          .enter()
          .append('circle')
          .attr('cx', d => d.x)
          .attr('cy', d => d.y)
          .attr('r', 1) // baseDotRadius
          .attr('fill', 'rgba(0,0,0,0.35)'); // baseDotColor
      }
      
      // 绘制RAG结果点（FootprintRAG风格）
      const colorOf = (action) => {
        if (action === 'GROW') return '#28a745';
        if (action === 'PRUNE') return '#dc3545';
        if (action === 'KEEP') return '#ffc107';
        return '#9AA3AD'; // UNKNOWN
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
        
        return {
          x: xScale(p.x),
          y: yScale(p.y),
          radius,
          score,
          action,
          isPicture,
          rag: p.rag,
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
        .attr('fill', d => colorOf(d.action))
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
          
          const rr = d.rag?.retrieval_result || {};
          const title = (rr.content?.title || rr.metadata?.title || 'N/A');
          
          let typeLabel = '未知';
          if (d.isPicture) {
            typeLabel = '图片';
          } else {
            typeLabel = '文本';
          }
          
          const tooltip = d3.select('body').append('div')
            .attr('class', 'river-tooltip')
            .style('position', 'absolute')
            .style('background', 'rgba(20, 24, 28, 0.88)')
            .style('color', 'white')
            .style('padding', '8px 10px')
            .style('border-radius', '6px')
            .style('z-index', '1000')
            .style('font-size', '12px')
            .style('pointer-events', 'none')
            .style('left', `${event.pageX + 14}px`)
            .style('top', `${event.pageY - 10}px`);
          
          tooltip.html(`
            <div style="margin-bottom:4px;"><strong>ID:</strong> ${rr.id ?? ''}</div>
            <div style="margin-bottom:4px;"><strong>类型:</strong> ${typeLabel}</div>
            <div style="margin-bottom:4px;"><strong>Score:</strong> ${Number(d.score).toFixed(3)}</div>
            <div style="margin-bottom:4px;"><strong>Action:</strong> ${d.action}</div>
            <div><strong>Title:</strong> ${String(title).slice(0, 60)}${String(title).length > 60 ? '...' : ''}</div>
          `);
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
          d3.selectAll('.river-tooltip').remove();
        })
        .on('pointerdown', (event, d) => {
          event.stopPropagation();
          if (event.button !== 0) return;
          const self = this;
          const startX = event.clientX;
          const startY = event.clientY;
          let moved = false;
          const threshold = 10;
          const onMove = (e) => {
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            if (!moved && (dx * dx + dy * dy) > threshold * threshold) {
              moved = true;
              self._beginReportDragGhost(e, d);
            }
            if (moved) self._moveReportDragGhost(e);
          };
          const onUp = (e) => {
            window.removeEventListener('pointermove', onMove);
            window.removeEventListener('pointerup', onUp);
            self._clearReportDragHover();
            if (moved) {
              self._finishReportDrag(e);
              self.suppressStrategyDotClick = true;
            }
          };
          window.addEventListener('pointermove', onMove);
          window.addEventListener('pointerup', onUp);
        })
        .on('click', (event, d) => {
          if (this.suppressStrategyDotClick) {
            this.suppressStrategyDotClick = false;
            event.stopPropagation();
            return;
          }
          const rr = d.rag?.retrieval_result;
          if (!rr) return;
          const evaluation = d.rag?.evaluation ?? null;
          this.showDetail(rr, evaluation);
        });
      
      // FootprintRAG风格：底部统计（说明：RAG 条数 ≠ 地图点数，见文案）
      const totalRag = query.rag_results?.length ?? 0;
      const plotted = ragPointsData.length;
      const noCoord = missingIds.length;
      const footerParts = [`地图 ${plotted}/${totalRag} 条`];
      if (this.hidePrunePoints && skippedPruneCount > 0) {
        footerParts.push(`已隐藏PRUNE ${skippedPruneCount}`);
      }
      if (noCoord > 0) {
        footerParts.push(`无嵌入坐标 ${noCoord}`);
      }
      const footerStr = footerParts.join(' · ');
      const footerShort = footerStr.length > 72 ? `${footerStr.slice(0, 69)}…` : footerStr;
      const footerG = strategyGroup.append('g').attr('class', 'strategy-map-footer');
      footerG.append('title').text(
        '策略返回的每条 RAG 需在左侧所选数据集的 2D 嵌入文件（如 LLMvisDataset_embedding.json）中有对应 ID，才会在地图中打点。' +
          '查不到的 chunk 仍保留在实验 JSON 中。' +
          (this.hidePrunePoints ? ' 开启「隐藏PRUNE」时不绘制 PRUNE 节点。' : '')
      );
      footerG.append('text')
        .attr('x', rectX + 14)
        .attr('y', rectY + rectHeight - 10)
        .attr('text-anchor', 'start')
        .attr('font-size', '10px')
        .attr('fill', 'rgba(90,100,110,0.92)')
        .text(footerShort);
    },

    drawConnections() {
      if (!this.showConnections || !this.showLegacyConnections) return;
      if (this.connectionGroup) {
        this.connectionGroup.selectAll('*').remove();
      } else {
        const svg = d3.select(this.$refs.svg);
        this.connectionGroup = svg.append('g').attr('class', 'river-connections');
      }
      const allRounds = [...this.roundsData].filter(r => r && r.round_number !== undefined);
      const roundByNum = new Map(allRounds.map(r => [r.round_number, r]));
      const activeKey = this.focusedStrategyKey || this.hoveredStrategyKey;
      const maxRound = Math.max(...Object.keys(this.strategyCanvases).map(Number), 0);
      for (let r = 1; r <= maxRound; r++) {
        const cur = this.strategyCanvases[r];
        const prev = this.strategyCanvases[r - 1];
        if (!cur || !prev) continue;
        Object.entries(cur).forEach(([curIndex, curCanvas]) => {
          const parent = curCanvas.parentNode;
          if (parent === null || parent === undefined) return;
          const parentId = String(parent).trim();
          if (parentId === '' || parentId === '0' || parentId === 'ROOT') return;
          const curKey = this.getStrategyKey(curCanvas.roundNumber, Number(curIndex));
          if (/^\d+$/.test(parentId)) {
            const pqIdx = parseInt(parentId, 10) - 1;
            if (pqIdx >= 0) {
              const prevCanvas = prev[pqIdx];
              if (prevCanvas) {
                const prevKey = this.getStrategyKey(prevCanvas.roundNumber, prevCanvas.queryIndex);
                const related = activeKey ? (curKey === activeKey || prevKey === activeKey) : false;
                this.drawSmoothConnection(prevCanvas, curCanvas, related);
                return;
              }
            }
          }
          Object.entries(prev).forEach(([prevIndex, prevCanvas]) => {
            const prevRound = roundByNum.get(prevCanvas.roundNumber);
            if (!prevRound) return;
            const prevQuery = prevRound.query_results?.[prevCanvas.queryIndex];
            if (!prevQuery?.rag_results) return;
            const hit = prevQuery.rag_results.some((rag) => {
              const id = rag?.retrieval_result?.id;
              if (id === undefined || id === null) return false;
              const sid = String(id);
              return sid === parentId || sid === `img_${parentId}` || (parentId.startsWith('img_') && sid === parentId.replace('img_', ''));
            });
            if (hit) {
              const prevKey = this.getStrategyKey(prevCanvas.roundNumber, Number(prevIndex));
              const related = activeKey ? (curKey === activeKey || prevKey === activeKey) : false;
              this.drawSmoothConnection(prevCanvas, curCanvas, related);
            }
          });
        });
      }
    },

    drawSmoothConnection(sourceCanvas, targetCanvas, related = false) {
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

    // 为策略卡片添加拖拽功能（交换位置模式）    // 为策略卡片上方区域添加拖拽功能（支持换位置和合并）
    _addDragBehavior(dragHandle, strategyGroup, roundNumber, queryIndex) {
      const self = this;
      let dragStartX = 0;
      let dragStartY = 0;
      let isDragging = false;

      const drag = d3.drag()
        .on('start', function(event) {
          isDragging = false;
          const container = self.containerGroup ? self.containerGroup.node() : (self.svg ? self.svg.node() : this.parentElement);
          if (!container) return;
          const [x, y] = d3.pointer(event, container);
          dragStartX = x;
          dragStartY = y;
          self.draggingStrategy = { roundNumber, queryIndex };
          event.sourceEvent.stopPropagation();
          strategyGroup.raise(); // 将整个卡片提升到最上层
          strategyGroup.style('opacity', 0.8);
          d3.select(this).style('cursor', 'grabbing');
        })
        .on('drag', function(event) {
          if (Math.abs(event.dy) > 3 || Math.abs(event.dx) > 3) {
            isDragging = true;
          }
          
          if (!isDragging) return;

          const offsetX = event.x - dragStartX;
          const offsetY = event.y - dragStartY;
          strategyGroup.attr('transform', `translate(${offsetX}, ${offsetY})`);

          // 获取鼠标当前位置，用于检测目标
          const container = self.containerGroup ? self.containerGroup.node() : (self.svg ? self.svg.node() : this.parentElement);
          if (!container) return;
          const [mouseX, mouseY] = d3.pointer(event, container);

          // 移除旧的视觉提示
          d3.selectAll('.drag-indicator-line').remove();
          d3.selectAll('.drag-indicator-plus').remove();
          
          self.dragTarget = null;

          // 遍历所有 round 下的所有卡片寻找放置位置
          for (const targetRound of self.roundsData) {
            if (!targetRound || !targetRound.query_results) continue;
            
            for (let i = 0; i < targetRound.query_results.length; i++) {
              // 跳过自己
              if (targetRound.round_number === roundNumber && i === queryIndex) continue;
              
              const targetRect = self.getStrategyCellRect(self.gridMetrics, targetRound.round_number, i);
              if (!targetRect) continue;

              const tx = targetRect.x;
              const ty = targetRect.y;
              const tw = targetRect.width;
              const th = targetRect.height;
              
              // 判断是否在卡片区域或稍微超出边缘
              const edgeSize = 24; 
              
              if (mouseX >= tx - edgeSize && mouseX <= tx + tw + edgeSize) {
                // 如果在卡片上半部分边缘外部或内部边缘（指示插入到前面）
                if (mouseY >= ty - edgeSize && mouseY <= ty + edgeSize) {
                  self.dragTarget = { type: 'reorder', roundNumber: targetRound.round_number, index: i };
                  self.containerGroup.append('line')
                    .attr('class', 'drag-indicator-line')
                    .attr('x1', tx).attr('y1', ty - (self.gridMetrics.rowGap ? self.gridMetrics.rowGap / 2 : 5))
                    .attr('x2', tx + tw).attr('y2', ty - (self.gridMetrics.rowGap ? self.gridMetrics.rowGap / 2 : 5))
                    .attr('stroke', '#0ea5e9')
                    .attr('stroke-width', 4);
                  break;
                } 
                // 如果在卡片下半部分边缘外部或内部边缘（指示插入到后面）
                else if (mouseY >= ty + th - edgeSize && mouseY <= ty + th + edgeSize) {
                  self.dragTarget = { type: 'reorder', roundNumber: targetRound.round_number, index: i + 1 };
                  self.containerGroup.append('line')
                    .attr('class', 'drag-indicator-line')
                    .attr('x1', tx).attr('y1', ty + th + (self.gridMetrics.rowGap ? self.gridMetrics.rowGap / 2 : 5))
                    .attr('x2', tx + tw).attr('y2', ty + th + (self.gridMetrics.rowGap ? self.gridMetrics.rowGap / 2 : 5))
                    .attr('stroke', '#0ea5e9')
                    .attr('stroke-width', 4);
                  break;
                } 
                // 否则如果在卡片真正的内部，表示合并
                else if (mouseY > ty + edgeSize && mouseY < ty + th - edgeSize) {
                  self.dragTarget = { type: 'merge', roundNumber: targetRound.round_number, index: i };
                  const plusSize = 40;
                  const cx = tx + tw / 2;
                  const cy = ty + th / 2;
                  const plusG = self.containerGroup.append('g').attr('class', 'drag-indicator-plus');
                  
                  plusG.append('rect')
                    .attr('x', tx).attr('y', ty)
                    .attr('width', tw).attr('height', th)
                    .attr('fill', 'rgba(14, 165, 233, 0.08)')
                    .attr('rx', 0);
                    
                  plusG.append('circle')
                    .attr('cx', cx).attr('cy', cy)
                    .attr('r', plusSize / 2 + 5)
                    .attr('fill', 'white')
                    .attr('stroke', '#0ea5e9')
                    .attr('stroke-width', 2);
                  
                  plusG.append('line')
                    .attr('x1', cx - plusSize/2 + 5).attr('y1', cy)
                    .attr('x2', cx + plusSize/2 - 5).attr('y2', cy)
                    .attr('stroke', '#0ea5e9').attr('stroke-width', 4).attr('stroke-linecap', 'round');
                  plusG.append('line')
                    .attr('x1', cx).attr('y1', cy - plusSize/2 + 5)
                    .attr('x2', cx).attr('y2', cy + plusSize/2 - 5)
                    .attr('stroke', '#0ea5e9').attr('stroke-width', 4).attr('stroke-linecap', 'round');
                  break;
                }
              }
            }
            if (self.dragTarget) break; // 如果已经找到目标，不再继续遍历其他 round
          }
        })
        .on('end', function() {
          strategyGroup.style('opacity', 1);
          d3.select(this).style('cursor', 'grab');
          d3.selectAll('.drag-indicator-line').remove();
          d3.selectAll('.drag-indicator-plus').remove();

          if (isDragging && self.dragTarget) {
            const sourceRound = self.roundsData.find(r => r.round_number === roundNumber);
            const targetRound = self.roundsData.find(r => r.round_number === self.dragTarget.roundNumber);
            
            if (sourceRound && sourceRound.query_results && targetRound && targetRound.query_results) {
              const target = self.dragTarget;
              const sourceQueryIndex = queryIndex;
              const targetQueryIndex = target.index;
              
              if (target.type === 'reorder') {
                // 处理重新排序
                const item = sourceRound.query_results.splice(sourceQueryIndex, 1)[0];
                
                let newIndex = targetQueryIndex;
                // 如果是在同一个 round 内部拖拽，并且目标在自己后面，目标索引需要减一
                if (sourceRound.round_number === targetRound.round_number && newIndex > sourceQueryIndex) {
                  newIndex--;
                }
                
                targetRound.query_results.splice(newIndex, 0, item);
                self.$nextTick(() => { self.drawRiverChart(); });
              } else if (target.type === 'merge') {
                // 处理合并
                const targetQuery = targetRound.query_results[targetQueryIndex];
                const sourceQuery = sourceRound.query_results[sourceQueryIndex];
                
                // 备份原始的 rag_results（如果还没有备份过）
                if (!targetQuery._original_rag_results) {
                  targetQuery._original_rag_results = targetQuery.rag_results ? [...targetQuery.rag_results] : [];
                }
                
                // 将源策略的点加入目标策略
                if (!targetQuery.rag_results) targetQuery.rag_results = [];
                if (sourceQuery.rag_results) {
                  targetQuery.rag_results = targetQuery.rag_results.concat(sourceQuery.rag_results);
                }
                
                // 记录源 ID 到合并目标，以显示提示
                if (!targetQuery.merged_from) targetQuery.merged_from = [];
                targetQuery.merged_from.push(`R${roundNumber}.${sourceQueryIndex + 1}`);
                if (sourceQuery.merged_from) {
                  targetQuery.merged_from = targetQuery.merged_from.concat(sourceQuery.merged_from);
                }
                
                // 保存原始的 sourceQuery 数据用于拆分
                if (!targetQuery._merged_sources_data) targetQuery._merged_sources_data = [];
                targetQuery._merged_sources_data.push({
                   originalRound: roundNumber,
                   originalIndex: sourceQueryIndex,
                   queryData: sourceQuery // 保存完整的原对象
                });
                // 如果 sourceQuery 内部也有被合并的数据，也一并转移过去
                if (sourceQuery._merged_sources_data) {
                   targetQuery._merged_sources_data = targetQuery._merged_sources_data.concat(sourceQuery._merged_sources_data);
                }
                
                // 移除被拖拽的源策略
                sourceRound.query_results.splice(sourceQueryIndex, 1);
                
                self.$nextTick(() => { self.drawRiverChart(); });
              }
            }
          } else {
            // 没有目标或者没拖动，重置位置
            strategyGroup.transition().duration(200).attr('transform', 'translate(0, 0)');
          }

          setTimeout(() => {
            self.draggingStrategy = null;
            self.dragTarget = null;
            isDragging = false;
          }, 100);
        });

      dragHandle.call(drag);
    },

    splitMergedStrategies(roundNumber, queryIndex) {
      const round = this.roundsData.find(r => r.round_number === roundNumber);
      if (!round || !round.query_results) return;
      const targetQuery = round.query_results[queryIndex];
      
      if (!targetQuery._merged_sources_data || targetQuery._merged_sources_data.length === 0) return;
      
      const sourcesToRestore = targetQuery._merged_sources_data;
      
      // 恢复 targetQuery 自身的 rag_results 
      if (targetQuery._original_rag_results) {
         targetQuery.rag_results = [...targetQuery._original_rag_results];
         delete targetQuery._original_rag_results;
      }
      
      // 清除合并相关的标记
      delete targetQuery.merged_from;
      delete targetQuery._merged_sources_data;
      
      // 按原始索引从小到大排序，这样在同一个 round 插入时顺移不会出错
      sourcesToRestore.sort((a, b) => a.originalIndex - b.originalIndex);
      
      sourcesToRestore.forEach(src => {
         const destRound = this.roundsData.find(r => r.round_number === src.originalRound);
         if (destRound && destRound.query_results) {
            // 在目标 round 的原始索引处插入被拆分出来的卡片（如果有冲突则顺移）
            const insertIndex = Math.min(src.originalIndex, destRound.query_results.length);
            destRound.query_results.splice(insertIndex, 0, src.queryData);
         }
      });
      
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
        
        // 重新绘制全局地图以显示高亮
        if (this.globalMapCardVisible) {
          this.drawGlobalMap();
        }
      } else {
        console.warn('未找到chunk对应的点:', chunkId);
      }

      // 3. 重新绘制 river 图：让策略小矩形里的对应点也同步变大
      this.drawRiverChart();

      // 4. 重新缩放定位到目标策略画布中心
      this.$nextTick(() => {
        const svg = d3.select(this.$refs.svg);
        const zoom = d3.zoom()
          .scaleExtent([0.3, 4])
          .on('zoom', (event) => {
            const container = svg.select('.river-container');
            container.attr('transform', event.transform);
            if (this.connectionGroup) {
              this.connectionGroup.attr('transform', event.transform);
            }
          });

        const refreshedTargetCanvas = this.strategyCanvases?.[targetRound]?.[targetQueryIndex];
        if (!refreshedTargetCanvas) return;

        const scale = 2.0; // 放大2倍
        const translateX = this.svgWidth / 2 - refreshedTargetCanvas.centerX * scale;
        const translateY = this.svgHeight / 2 - refreshedTargetCanvas.centerY * scale;

        svg.transition()
          .duration(800)
          .call(zoom.transform, d3.zoomIdentity.translate(translateX, translateY).scale(scale));
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
            const text = query.orchestrator_plan.plansummary;
            const words = text.match(/[\u4e00-\u9fa5]+|[a-zA-Z]{2,}/g) || [];
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

    showDetail(retrievalResult, evaluation = null) {
      // 如果传入了 evaluation，将其附加到 retrievalResult 上
      const dataWithEvaluation = {
        ...retrievalResult,
        evaluation: evaluation || retrievalResult.evaluation
      };
      
      // 转换数据格式为ItemDetail需要的格式（复用store中的逻辑）
      const processedData = this.processRagResultForDetail(dataWithEvaluation);
      
      // 显示弹窗
      this.selectedPointDetail = processedData;
      this.showPointDetailModal = true;
    },
    
    // 处理RAG结果为ItemDetail需要的格式（复用store中的逻辑）
    processRagResultForDetail(ragResult) {
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
      
      // chunk 正文在不同工具返回结构可能不同：
      // - strategy_semantic_search: ragResult.content.text
      // - strategy_metadata_search: ragResult.metadata.content（包含正文/段落）
      const textContent =
        ragResult.content?.text ||
        ragResult.metadata?.content ||
        parsedMetadata?.content ||
        '';
      
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
        title: parsedMetadata?.figure_title || 
               ragResult.content?.title || 
               ragResult.metadata?.title || 
               'No Title',
        relative_path: relativePath,
        key_entities: parsedMetadata?.key_entities || ragResult.metadata?.key_entities || [],
        text_content: textContent,
        concise_summary: parsedMetadata?.concise_summary || ragResult.metadata?.concise_summary || '',
        inferred_insight: parsedMetadata?.inferred_insight || ragResult.metadata?.inferred_insight || '',
        paper_title: parsedMetadata?.paper_title || '',
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
    },

    getBranchActionColor(action) {
      if (action === 'GROW') return '#28a745';
      if (action === 'PRUNE') return '#dc3545';
      if (action === 'KEEP') return '#ffc107';
      if (action === 'PENDING') return '#6c757d';
      return '#9AA3AD';
    },

    _clearReportDragHover() {
      document.querySelectorAll('.interactive-report-drop-zone.interactive-report-drop-active').forEach((el) => {
        el.classList.remove('interactive-report-drop-active');
      });
    },

    _beginReportDragGhost(event, d) {
      const rr = d.rag?.retrieval_result;
      if (!rr) return;
      const evaluation = d.rag?.evaluation ?? null;
      const dataWithEvaluation = {
        ...rr,
        evaluation: evaluation || rr.evaluation
      };
      const processed = this.processRagResultForDetail(dataWithEvaluation);
      this.reportDragPayload = processed;
      this._clearReportDragHover();

      const ghost = document.createElement('div');
      ghost.className = 'interactive-report-drag-ghost';
      const color = this.getBranchActionColor(d.action);
      const ring = d.isPicture
        ? '<circle cx="18" cy="18" r="13" fill="none" stroke="rgba(40,140,255,0.95)" stroke-width="1.4"/>'
        : '';
      ghost.innerHTML = `<svg width="36" height="36" style="overflow:visible;opacity:0.92;filter:drop-shadow(0 2px 6px rgba(0,0,0,0.2))"><circle cx="18" cy="18" r="10" fill="${color}" stroke="rgba(40,50,60,0.35)" stroke-width="0.8"/>${ring}</svg>`;
      ghost.style.cssText = `position:fixed;left:${event.clientX}px;top:${event.clientY}px;pointer-events:none;z-index:10050;margin-left:-18px;margin-top:-18px;`;
      document.body.appendChild(ghost);
      this.reportDragGhostEl = ghost;
    },

    _moveReportDragGhost(e) {
      if (!this.reportDragGhostEl) return;
      this.reportDragGhostEl.style.left = `${e.clientX}px`;
      this.reportDragGhostEl.style.top = `${e.clientY}px`;
      this._clearReportDragHover();
      const under = document.elementFromPoint(e.clientX, e.clientY);
      const drop = under && under.closest && under.closest('.interactive-report-drop-zone');
      if (drop) drop.classList.add('interactive-report-drop-active');
    },

    _finishReportDrag(e) {
      const el = this.reportDragGhostEl;
      if (el) {
        el.remove();
        this.reportDragGhostEl = null;
      }
      const payload = this.reportDragPayload;
      this.reportDragPayload = null;
      this._clearReportDragHover();
      if (!payload) return;
      const under = document.elementFromPoint(e.clientX, e.clientY);
      const drop = under && under.closest && under.closest('.interactive-report-drop-zone');
      if (!drop) return;
      const sectionId = drop.getAttribute('data-section-id');
      if (!sectionId) return;
      this.$store.commit('addPointToInteractiveReportSection', { sectionId, item: payload });
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
      if (this.globalMapPoints.length > 0) {
        this.drawGlobalMap();
      }
    },

    // 提交用户查询到后端（优先 WebSocket，与后端一组一组收数据）
    async submitUserQuery() {
      if (!this.userQuestion.trim() || this.isSubmitting) {
        return;
      }

      this.isSubmitting = true;
      const question = this.userQuestion.trim();

      try {
        console.log('提交用户查询:', question);
        if (this.wsConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
          // 清空之前的状态，开始新的查询
          this.planStates = {};
          this.incrementalRoundsData = [];
          this.roundsData = [];
          
              this.ws.send(JSON.stringify({
                action: 'start_query',
                query: question,
                collection_name: this.ragCollection,
                plans_per_round: Math.max(1, Math.min(5, Math.floor(Number(this.plansPerRound) || 3))),
                rag_result_per_plan: Math.max(1, Math.floor(Number(this.ragResultsPerPlan) || 10)),
                max_rounds: Math.max(1, Math.min(5, Math.floor(Number(this.maxRounds) || 5))),
                interactive: this.isInteractiveMode === true
              }));
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


    // 交互模式下相关方法
    closeReviewModal() {
      this.showReviewModal = false;
      this.reviewPlans = [];
      this.reviewCheckpoint = null;
    },
    removeReviewPlan(index) {
      this.reviewPlans.splice(index, 1);
    },
    addEmptyReviewPlan() {
      this.reviewPlans.push({
        action: "call_tool",
        tool_name: "strategy_semantic_search",
        ParentNode: "0",
        args: { query_intent: "在此处输入关键词" },
        reason: "用户手动添加"
      });
    },
    updatePlanArgs(index, event) {
      try {
        const val = event.target.value;
        const parsed = JSON.parse(val);
        this.reviewPlans[index].args = parsed;
      } catch (e) {
        // 用户输入非法的JSON时先不报错，保持原值或只在保存时校验
      }
    },
    submitReviewDecision(decision) {
      if (!this.wsConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
        alert("WebSocket连接已断开，无法提交决策！");
        return;
      }
      
      const payload = {
        action: "interactive_response",
        run_id: this.reviewCheckpoint.run_id,
        checkpoint_id: this.reviewCheckpoint.checkpoint_id,
        decision: decision,
        plans: decision === 'replace' ? this.reviewPlans : []
      };
      
      console.log("[WS] 提交交互模式决策:", payload);
      this.ws.send(JSON.stringify(payload));
      this.closeReviewModal();
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

    handleFollowUp() {
      if (!this.followUpQuestion.trim()) {
        alert('请输入问题');
        return;
      }
      
      const maxRound = Math.max(...this.roundsData.map(r => r.round_number), -1);
      const nextRoundNumber = maxRound + 1;
      
      if (!this.newRounds[nextRoundNumber]) {
        this.newRounds[nextRoundNumber] = {
          round_number: nextRoundNumber,
          query_results: []
        };
      }
      
      this.newRounds[nextRoundNumber].query_results.push({
        orchestrator_plan: {
          action: 'call_tool',
          tool_name: 'user_follow_up',
          ParentNode: this.selectedDetailData?.original_data?.id || '0',
          args: {
            query_intent: this.followUpQuestion
          },
          reason: `用户追问: ${this.followUpQuestion}`,
          plansummary: null
        },
        rag_results: []
      });
      
      this.drawRiverChart();
      this.closeDetailModal();
      alert(`追问已添加到轮次 ${nextRoundNumber}，等待系统处理`);
    },

    // 左侧栏追问：仅执行“检索 + 评估”，结果追加到最后一个 iteration
    submitFollowUp(query) {
      const q = String(query || '').trim();
      if (!q) return;
      if (!this.wsConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
        alert('WebSocket 未连接，无法发送追问');
        return;
      }

      const rounds = (this.roundsData && this.roundsData.length > 0) ? this.roundsData : (this.incrementalRoundsData || []);
      const lastRound = rounds.length > 0 ? Math.max(...rounds.map(r => Number(r.round_number ?? 0))) : 0;

      this.ws.send(JSON.stringify({
        action: 'follow_up',
        query: q,
        collection_name: this.ragCollection,
        parent_node_id: '0',
        round_number: lastRound,
        rag_result_per_plan: Math.max(1, Math.floor(Number(this.ragResultsPerPlan) || 10)),
      }));
    },

    async loadGlobalMapData() {
      try {
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
        
        console.log('全局地图数据加载完成，共', this.globalMapPoints.length, '个点');
        this.$nextTick(() => {
          this.drawGlobalMap();
        });
      } catch (error) {
        console.error('加载全局地图数据失败:', error);
      }
    },

    drawGlobalMap() {
      // 支持两种渲染模式：
      // 1) 默认：渲染到 template 里 ref="globalMapSvg" 的 SVG
      // 2) 嵌入模式：渲染到 props.globalMapMountId 指定的容器内（容器里会自动创建 svg.global-map-svg）
      let svg = null;
      if (this.globalMapMountId) {
        const mountEl = document.getElementById(this.globalMapMountId);
        if (!mountEl) return;
        svg = d3.select(mountEl).select('svg.global-map-svg');
        if (svg.empty()) {
          const svgEl = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
          svgEl.setAttribute('class', 'global-map-svg');
          mountEl.innerHTML = '';
          mountEl.appendChild(svgEl);
          svg = d3.select(svgEl);
        }
      } else {
        svg = d3.select(this.$refs.globalMapSvg);
      }

      svg.selectAll('*').remove();

      if (this.globalMapPoints.length === 0) {
        return;
      }

      // 获取 SVG 容器尺寸
      const container = svg.node().parentElement;
      const width = container.clientWidth || 400;
      const height = container.clientHeight || 300;

      svg.attr('width', width).attr('height', height);

      // 计算数据范围
      const xExtent = d3.extent(this.globalMapPoints, d => d.x);
      const yExtent = d3.extent(this.globalMapPoints, d => d.y);

      // 创建缩放
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
          
          // 根据当前视窗动态显示/隐藏聚类关键词标签
          contentGroup.selectAll('.cluster-node').style('opacity', (d) => {
            if (!d || !d.centroid_2d) return 0;
            const cx = this.globalMapXScale(d.centroid_2d[0]);
            const cy = this.globalMapYScale(d.centroid_2d[1]);
            // 计算当前点在视窗中的实际像素位置
            const [mappedX, mappedY] = event.transform.apply([cx, cy]);
            
            const padding = 60; // 预留边界缓冲，防止字一半在内一半在外时突然消失
            if (mappedX >= -padding && mappedX <= contentWidth + padding &&
                mappedY >= -padding && mappedY <= contentHeight + padding) {
              return 1;
            }
            return 0;
          });
        });
        
      // 将行为应用到 svg 上
      svg.call(zoom);
      
      // 修改默认的双击缩放，改为双击重置视角
      svg.on('dblclick.zoom', null);
      svg.on('dblclick', () => {
        svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
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

      points.enter()
        .append('circle')
        .attr('class', 'data-point')
        .merge(points)
        .attr('cx', d => this.globalMapXScale(d.x))
        .attr('cy', d => this.globalMapYScale(d.y))
        .attr('r', d => {
          // 如果点被高亮，放大显示
          const highlightInfo = getHighlightInfo(d);
          // 高亮点半径：普通高亮=4；点击 Evidence 链接后特殊高亮=8
          return highlightInfo ? (highlightInfo.boostRadius ? 8 : 4) : 0.8;
        })
        .attr('fill', d => {
          // 如果点被高亮，根据 branch_action 设置颜色
          const highlightInfo = getHighlightInfo(d);
          if (highlightInfo) {
            const action = highlightInfo.branch_action;
            if (action === 'GROW') {
              return '#28a745'; // 绿色
            } else if (action === 'PRUNE') {
              return '#dc3545'; // 红色
            } else if (action === 'KEEP') {
              return '#ffc107'; // 黄色
            } else if (action === 'PENDING') {
              return '#6c757d'; // 灰色（待评估）
            }
            return '#999999';
          }
          return '#999999'; // 普通点灰色
        })
        .attr('opacity', d => {
          const highlightInfo = getHighlightInfo(d);
          if (highlightInfo) {
            return 0.9; // 高亮点不透明
          }
          return 0.4; // 普通点半透明
        })
        .attr('stroke', d => {
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
          return 'none';
        })
        .attr('stroke-width', d => {
          const highlightInfo = getHighlightInfo(d);
          if (highlightInfo && getPointType(d) === 'picture') {
             return 1.5;
          }
          if (highlightInfo) {
            return 1.5;
          }
          return 0;
        })
        // 增加 tooltip 提示
        .on('mouseover', function(event, d) {
          const rawType = getPointType(d);
          const typeLabel = rawType === 'picture' ? '图片' : '文本';
          
          // 尝试从 metadata 中提取更有用的 title
          let title = d.id;
          try {
            if (d.metadata) {
               const meta = typeof d.metadata === 'string' ? JSON.parse(d.metadata) : d.metadata;
               title = meta.title || meta.paper_name || d.id;
            }
          } catch(e) { /* ignore */ }
          
          const tooltip = d3.select('body').append('div')
            .attr('class', 'global-map-tooltip')
            .style('position', 'absolute')
            .style('background', 'rgba(20, 24, 28, 0.88)')
            .style('color', 'white')
            .style('padding', '8px 10px')
            .style('border-radius', '6px')
            .style('z-index', '1000')
            .style('font-size', '12px')
            .style('pointer-events', 'none')
            .style('left', `${event.pageX + 14}px`)
            .style('top', `${event.pageY - 10}px`);
          
          tooltip.html(`
            <div style="margin-bottom:4px;"><strong>ID:</strong> ${d.id ?? ''}</div>
            <div style="margin-bottom:4px;"><strong>类型:</strong> ${typeLabel}</div>
            <div><strong>Title:</strong> ${String(title).slice(0, 60)}${String(title).length > 60 ? '...' : ''}</div>
          `);
        })
        .on('mouseout', function() {
          d3.selectAll('.global-map-tooltip').remove();
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
            const cx = this.globalMapXScale(d.centroid_2d[0]);
            const cy = this.globalMapYScale(d.centroid_2d[1]);
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
            .style('pointer-events', 'none')
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
            .style('pointer-events', 'none');
        });
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

    addZoomBehavior(svg) {
      const container = this.containerGroup;
      const connectionGroup = this.connectionGroup;
      const zoom = d3.zoom()
        .scaleExtent([0.3, 3])
        .on('zoom', (event) => {
          this.persistZoomTransform = event.transform;
          if (container) container.attr('transform', event.transform);
          if (connectionGroup) connectionGroup.attr('transform', event.transform);
        });
      svg.call(zoom);
      if (this.persistZoomTransform) {
        svg.call(zoom.transform, this.persistZoomTransform);
      } else {
        const initialTransform = d3.zoomIdentity.translate(0, 0).scale(1);
        this.persistZoomTransform = initialTransform;
        svg.call(zoom.transform, initialTransform);
      }
      this.currentZoom = zoom;
    },

     clearChart() {
      const svg = d3.select(this.$refs.svg);
      svg.selectAll('*').remove();
      this.roundsData = [];
      this.newRounds = {};
      this.strategyCanvases = {};
      this.strategyOffsets = {}; // 清除拖拽偏移量
      this.draggingStrategy = null; // 清除拖拽状态
    },

    toggleLabels() {
      this.showLabels = !this.showLabels;
      if (this.roundsData.length > 0) {
        this.drawRiverChart();
      }
    },

    toggleHidePrunePoints() {
      this.hidePrunePoints = !this.hidePrunePoints;
      if (this.roundsData.length > 0) {
        this.drawRiverChart();
      }
    },

    toggleConnections() {
      this.showConnections = !this.showConnections;
      if (this.showConnections) {
        this.drawConnections();
      } else {
        if (this.connectionGroup) {
          this.connectionGroup.selectAll('*').remove();
        }
      }
    },

    handleResize() {
      this.gridMetrics = null;
      if (this.roundsData.length > 0) {
        this.drawRiverChart();
      }
      if (this.globalMapPoints.length > 0) {
        this.drawGlobalMap();
      }
    },

    // 全局地图卡片拖拽和缩放功能
    startDrag(event) {
      if (event.target.closest('.global-map-controls')) {
        return; // 如果点击的是控制按钮，不触发拖拽
      }
      this.isDragging = true;
      const rect = this.$refs.globalMapCard.getBoundingClientRect();
      this.dragStartPos = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
      };
      document.addEventListener('mousemove', this.onDrag);
      document.addEventListener('mouseup', this.stopDrag);
      event.preventDefault();
    },

    onDrag(event) {
      if (!this.isDragging) return;
      const newX = event.clientX - this.dragStartPos.x;
      const newY = window.innerHeight - (event.clientY - this.dragStartPos.y) - this.globalMapCardSize.height;
      
      // 限制在窗口内
      this.globalMapCardPosition.x = Math.max(0, Math.min(newX, window.innerWidth - this.globalMapCardSize.width));
      this.globalMapCardPosition.y = Math.max(0, Math.min(newY, window.innerHeight - this.globalMapCardSize.height));
    },

    stopDrag() {
      this.isDragging = false;
      document.removeEventListener('mousemove', this.onDrag);
      document.removeEventListener('mouseup', this.stopDrag);
    },

    startResize(event) {
      this.isResizing = true;
      this.resizeStartSize = { ...this.globalMapCardSize };
      this.resizeStartPos = {
        x: event.clientX,
        y: event.clientY
      };
      document.addEventListener('mousemove', this.onResize);
      document.addEventListener('mouseup', this.stopResize);
      event.preventDefault();
      event.stopPropagation();
    },

    onResize(event) {
      if (!this.isResizing) return;
      const deltaX = event.clientX - this.resizeStartPos.x;
      const deltaY = this.resizeStartPos.y - event.clientY; // Y轴方向相反
      
      const minWidth = 300;
      const maxWidth = window.innerWidth - this.globalMapCardPosition.x - 20;
      const minHeight = 200;
      const maxHeight = window.innerHeight - this.globalMapCardPosition.y - 20;
      
      this.globalMapCardSize.width = Math.max(minWidth, Math.min(maxWidth, this.resizeStartSize.width + deltaX));
      this.globalMapCardSize.height = Math.max(minHeight, Math.min(maxHeight, this.resizeStartSize.height + deltaY));
      
      // 重新绘制地图以适应新尺寸
      this.$nextTick(() => {
        if (this.globalMapPoints.length > 0) {
          this.drawGlobalMap();
        }
      });
    },

    stopResize() {
      this.isResizing = false;
      document.removeEventListener('mousemove', this.onResize);
      document.removeEventListener('mouseup', this.stopResize);
    },

    resetGlobalMapSize() {
      this.globalMapCardSize = { width: 400, height: 300 };
      this.$nextTick(() => {
        if (this.globalMapPoints.length > 0) {
          this.drawGlobalMap();
        }
      });
    },

    toggleGlobalMap() {
      this.globalMapCardVisible = !this.globalMapCardVisible;
    }
  },

  mounted() {
    this.loadExperimentFileList();
    this.loadMapData();
    this.connectWebSocket();
    this.loadGlobalMapData();
    // 可选：初始加载静态数据；提交查询后会被 WebSocket 推送的 graph 覆盖
    // this.loadAllRounds();
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

/* 注意：不要强行让 svg rect 继承 stroke（会覆盖 d3 里对外框/内框的动态着色）。 */

.user-input-section {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  padding: 15px 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  min-width: 400px;
}

.ws-status {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}
.ws-status.connected {
  color: #28a745;
}
.input-container {
  display: flex;
  gap: 10px;
  align-items: center;
}

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

.tooltip {
  pointer-events: none;
  font-size: 12px;
  max-width: 250px;
}

/* 全局地图卡片样式 */
.global-map-card {
  position: fixed;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  backdrop-filter: blur(10px);
  user-select: none;
}

.global-map-header {
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: move;
  flex-shrink: 0;
}

.global-map-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  flex: 1;
}

.global-map-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.global-map-controls .reset-btn,
.global-map-controls .close-btn,
.global-map-controls .clear-highlight-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  padding: 0;
}

.global-map-controls .clear-highlight-btn {
  width: auto;
  padding: 0 8px;
  font-size: 12px;
}

.global-map-controls .reset-btn:hover,
.global-map-controls .close-btn:hover,
.global-map-controls .clear-highlight-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.global-map-content {
  flex: 1;
  padding: 10px;
  overflow: hidden;
  background: #f8f9fa;
  position: relative;
  min-height: 0;
}

.global-map-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.global-map-content-group {
  cursor: default;
}

/* 调整大小的拖拽手柄 */
.resize-handle {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 20px;
  height: 20px;
  cursor: nwse-resize;
  background: linear-gradient(135deg, transparent 0%, transparent 40%, rgba(0, 0, 0, 0.2) 40%, rgba(0, 0, 0, 0.2) 60%, transparent 60%);
  z-index: 10;
}

.resize-handle::after {
  content: '';
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 0 12px 12px;
  border-color: transparent transparent rgba(0, 0, 0, 0.3) transparent;
}

.resize-handle:hover {
  background: linear-gradient(135deg, transparent 0%, transparent 40%, rgba(0, 0, 0, 0.3) 40%, rgba(0, 0, 0, 0.3) 60%, transparent 60%);
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

.user-input-section {
  min-width: 420px;
  border: 1px solid rgba(203, 213, 225, 0.9);
  box-shadow: 0 8px 28px rgba(15, 23, 42, 0.08);
}

.interactive-toggle {
  display: flex;
  align-items: center;
  margin: 0 15px;
  font-size: 14px;
  color: #333;
}

.interactive-toggle input[type="checkbox"] {
  margin-right: 6px;
  cursor: pointer;
}

.review-plan-item {
  background: #fdfdfd;
  transition: all 0.2s ease;
}
.review-plan-item:hover {
  background: #f4f6f8;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.form-group label {
  display: block;
  font-size: 12px;
  font-weight: bold;
  color: #555;
  margin-bottom: 4px;
}

.form-group select,
.form-group input,
.form-group textarea {
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
  transition: border-color 0.2s;
}

.form-group select:focus,
.form-group input:focus,
.form-group textarea:focus {
  border-color: #4A90E2;
}

</style>