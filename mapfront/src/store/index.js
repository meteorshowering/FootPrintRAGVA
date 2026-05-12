import { createStore } from 'vuex';
import { buildInteractiveReportItemFromRag } from './interactiveReportItem';

const store = createStore({
  state: {
    selectedData: null,  // 当前选中的数据点（RiverChart 等兼容）
    dataPoints: [],      // 所有数据点
    experimentResult: null,  // 完整的实验数据，包含hypothesis
    experimentSourceFile: '', // 当前加载的实验数据文件路径
    // Interactive Report：版块标题 + 从策略地图拖入的点（与 ItemDetail 同结构，供后续 prompt 总结）
    interactiveReportSections: [],
    /** Text view 点击 [chunk] 引用时：{ id, ts }，由 EnhancedRiverChart watch 后平移画布并红框高亮 */
    interactiveReportCitationFocus: null,
  },
  getters: {
    // 从完整路径中提取相对路径
    extractRelativePath: () => (fullPath) => {
      if (!fullPath) return '';
      
      const normalizedPath = fullPath.replace(/\\/g, '/');
      const mdLlmvisIndex = normalizedPath.indexOf('md-llmvis');
      if (mdLlmvisIndex !== -1) {
        const subPath = normalizedPath.substring(mdLlmvisIndex + 'md-llmvis'.length + 1);
        if (subPath.startsWith('images/')) {
          return `/static-llmvis/${subPath.substring('images/'.length)}`;
        } else {
          return `/static-llmvis/${subPath}`;
        }
      }
      
      // 从完整路径中提取paper_md后面的部分
      const paperMdIndex = normalizedPath.indexOf('paper_md');
      if (paperMdIndex !== -1) {
        return `/static/${normalizedPath.substring(paperMdIndex + 'paper_md'.length + 1)}`; // +1 是为了去掉斜杠
      }
      
      // 如果找不到paper_md，尝试其他方式提取
      const parts = normalizedPath.split('/');
      const paperMdIndexInParts = parts.indexOf('paper_md');
      if (paperMdIndexInParts !== -1 && paperMdIndexInParts < parts.length - 1) {
        return parts.slice(paperMdIndexInParts + 1).join('/');
      }
      
      return fullPath; // 如果无法提取，返回原路径
    }
  },
  mutations: {
    setDataPoints(state, dataPoints) {
      state.dataPoints = dataPoints;
    },
    setSelectedData(state, data) {
      state.selectedData = data;
      console.log("selectdatainindex",state.selectedData)
    },
    setExperimentResult(state, experimentResult) {
      state.experimentResult = experimentResult;
    },
    setExperimentSourceFile(state, file) {
      state.experimentSourceFile = file;
    },
    addInteractiveReportSection(state, { title, text }) {
      const id = `ir-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
      state.interactiveReportSections.push({ id, title: title || '未命名版块', text: text || '', showText: !!text, items: [] });
    },
    toggleInteractiveReportSectionText(state, sectionId) {
      const sec = state.interactiveReportSections.find(s => s.id === sectionId);
      if (sec) {
        sec.showText = !sec.showText;
      }
    },
    updateInteractiveReportSectionTitle(state, { sectionId, title }) {
      const sec = state.interactiveReportSections.find((s) => s.id === sectionId);
      if (sec) sec.title = typeof title === 'string' ? title : '';
    },
    updateInteractiveReportSectionText(state, { sectionId, text }) {
      const sec = state.interactiveReportSections.find((s) => s.id === sectionId);
      if (!sec) return;
      sec.text = typeof text === 'string' ? text : '';
    },
    addPointToInteractiveReportSection(state, { sectionId, item }) {
      if (!item || !item.id) return;
      const sec = state.interactiveReportSections.find(s => s.id === sectionId);
      if (!sec) return;
      if (sec.items.some(i => i && i.id === item.id)) return;
      sec.items.push(item);
    },
    removePointFromInteractiveReportSection(state, { sectionId, itemId }) {
      const sec = state.interactiveReportSections.find(s => s.id === sectionId);
      if (!sec) return;
      sec.items = sec.items.filter(i => i && i.id !== itemId);
    },
    removeInteractiveReportSection(state, sectionId) {
      state.interactiveReportSections = state.interactiveReportSections.filter(s => s.id !== sectionId);
    },
    clearInteractiveReport(state) {
      state.interactiveReportSections = [];
    },
    setInteractiveReportCitationFocus(state, evidenceId) {
      const id = String(evidenceId || '').trim();
      state.interactiveReportCitationFocus = id
        ? { id, ts: Date.now() }
        : null;
    },
  },
  actions: {
    loadDataPoints({ commit }, data) {
      commit('setDataPoints', data);
    },
    selectDataPoint({ commit }, dataPoint) {
      console.log("store action - selectDataPoint:", dataPoint);  // 确认 action 是否被触发
      commit('setSelectedData', dataPoint);
    },
    selectRiverResult({ commit, getters }, ragResult) {
      console.log("store action - selectRiverResult:", ragResult);
      console.log("store action - evaluation:", ragResult.evaluation);
      const processedData = buildInteractiveReportItemFromRag(getters, ragResult);
      if (!processedData) {
        return Promise.resolve(null);
      }
      commit('setSelectedData', processedData);
      return Promise.resolve(processedData);
    },
  },
});

export default store;
