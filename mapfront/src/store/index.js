import { createStore } from 'vuex';

const store = createStore({
  state: {
    selectedData: null,  // 当前选中的数据点（保留用于兼容）
    dataPoints: [],      // 所有数据点
    selectedItems: [],   // 多选列表（保存的数据点）- 必须初始化为空数组
    pendingItems: [],    // 待保存的多选列表（临时选择）- 必须初始化为空数组
    experimentResult: null  // 完整的实验数据，包含hypothesis
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
    addPendingItem(state, item) {
      // 检查是否已存在（根据id）
      if (!item || !item.id) {
        console.warn('addPendingItem: 无效的item', item);
        return;
      }
      const exists = state.pendingItems.some(i => i && i.id === item.id);
      if (!exists) {
        // 使用 push 添加，Vue 3 能检测到（响应式）
        state.pendingItems.push(item);
        console.log('addPendingItem: 已添加', item.id, '当前待保存数量:', state.pendingItems.length);
      } else {
        console.log('addPendingItem: 已存在，跳过', item.id);
      }
    },
    removePendingItem(state, itemId) {
      // 使用 filter 返回新数组（响应式）
      state.pendingItems = state.pendingItems.filter(i => i.id !== itemId);
    },
    clearPendingItems(state) {
      // 直接赋值空数组，响应式
      state.pendingItems = [];
    },
    savePendingItems(state) {
      console.log('savePendingItems mutation 开始执行');
      console.log('当前 pendingItems:', state.pendingItems);
      console.log('当前 selectedItems:', state.selectedItems);
      
      // 将pendingItems添加到selectedItems，去重
      const newItems = state.pendingItems.filter(pending => 
        !state.selectedItems.some(selected => selected && selected.id === pending.id)
      );
      
      console.log('去重后的新项目:', newItems);
      
      // 用新数组替换，Vue能检测到（响应式）
      state.selectedItems = [...state.selectedItems, ...newItems];
      // 直接赋值空数组清空，响应式
      state.pendingItems = [];
      
      console.log('savePendingItems: 已保存', newItems.length, '个项目，当前已保存总数:', state.selectedItems.length);
      console.log('保存后的 selectedItems:', state.selectedItems);
      console.log('保存后的 pendingItems:', state.pendingItems);
    },
    clearSelectedItems(state) {
      // 直接赋值空数组，响应式
      state.selectedItems = [];
    },
    removeSelectedItem(state, itemId) {
      // 使用 filter 返回新数组（响应式）
      state.selectedItems = state.selectedItems.filter(i => i.id !== itemId);
    },
    setExperimentResult(state, experimentResult) {
      state.experimentResult = experimentResult;
    }
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
      
      // 处理河流图数据，转换为DetailView需要的格式
      const processedData = {
        id: ragResult.id, // 添加id用于去重
        type: dataType,
        title: parsedMetadata?.figure_title || 
               ragResult.content?.title || 
               ragResult.metadata?.title || 
               'No Title',
        relative_path: savePath ? getters.extractRelativePath(savePath) : '',
        key_entities: parsedMetadata?.key_entities || ragResult.metadata?.key_entities || [],
        text_content: ragResult.content?.text || '',
        concise_summary: parsedMetadata?.concise_summary || ragResult.metadata?.concise_summary || '',
        inferred_insight: parsedMetadata?.inferred_insight || ragResult.metadata?.inferred_insight || '',
        paper_title: parsedMetadata?.paper_title || '',
        score: ragResult.score,
        branch_action: ragResult.evaluation?.branch_action || 'UNKNOWN',
        // 保留完整的解析后的 metadata，方便访问所有字段
        parsed_metadata: parsedMetadata || null,
        // 保留原始数据用于调试和访问其他字段，确保 evaluation 被包含
        original_data: {
          ...ragResult,
          evaluation: ragResult.evaluation || null  // 确保 evaluation 被保留
        }
      };
      
      commit('setSelectedData', processedData);
      return Promise.resolve(processedData);
    },
    async addToPending({ commit, dispatch }, ragResult) {
      console.log('addToPending action 被调用', ragResult);
      const processedData = await dispatch('selectRiverResult', ragResult);
      console.log('processedData:', processedData);
      commit('addPendingItem', processedData);
    },
    async addMultipleToPending({ commit, dispatch }, ragResults) {
      for (const ragResult of ragResults) {
        const processedData = await dispatch('selectRiverResult', ragResult);
        commit('addPendingItem', processedData);
      }
    }
  },
});

export default store;
