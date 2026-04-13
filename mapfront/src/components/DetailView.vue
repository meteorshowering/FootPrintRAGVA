<template>
  <div class="detail-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <button 
        @click.stop="savePending" 
        class="btn btn-save" 
        :title="store.state.pendingItems.length === 0 ? '没有待保存的项目' : `点击保存 ${store.state.pendingItems.length} 个项目`"
      >
        💾 保存 ({{ store.state.pendingItems.length }})
      </button>
      <button @click="clearPending" class="btn btn-clear">
        🗑️ 清空待保存
      </button>
      <button @click="clearAll" class="btn btn-clear-all">
        🗑️ 清空已保存
      </button>
      <button 
        @click="showHypothesis" 
        class="btn btn-hypothesis"
        :disabled="!hasHypothesis"
        :title="hasHypothesis ? '查看核心科学假设' : '暂无Hypothesis数据'"
      >
        📊 查看 Hypothesis
      </button>
    </div>

    <!-- 总览统计 -->
    <div v-if="selectedLength > 0 || pendingLength > 0" class="overview-section">
      <h3>总览</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">{{ totalCount }}</div>
          <div class="stat-label">总数据点</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ pictureCount }}</div>
          <div class="stat-label">图片类型</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ textureCount }}</div>
          <div class="stat-label">文本类型</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ avgScore.toFixed(3) }}</div>
          <div class="stat-label">平均分数</div>
        </div>
      </div>
    </div>

    <!-- 已保存的数据点列表 -->
    <div v-if="selectedLength > 0" class="saved-section">
      <h3>已保存 ({{ selectedLength }})</h3>
      <div class="items-list">
        <div 
          v-for="(item, index) in selectedItems" 
          :key="`saved-${item.id}`"
          class="item-card saved"
          :class="{ expanded: expandedItems.includes(`saved-${item.id}`) }"
        >
          <div class="item-header" @click="toggleExpand(`saved-${item.id}`)">
            <div class="item-info">
              <span class="item-index" :class="getBranchActionClass(item)">{{ index + 1 }}</span>
              <span class="item-title">{{ getTitle(item) }}</span>
              <span class="type-badge" :class="getTypeClass(item)">{{ getTypeLabel(item) }}</span>
            </div>
            <div class="item-actions">
              <span class="item-score">Score: {{ getScore(item).toFixed(3) }}</span>
              <button @click.stop="removeItem(item.id)" class="btn-remove">×</button>
            </div>
          </div>
          <div v-if="expandedItems.includes(`saved-${item.id}`)" class="item-details">
            <ItemDetail :item="item" />
          </div>
        </div>
      </div>
    </div>

    <!-- 待保存的数据点列表 -->
    <div v-if="pendingLength > 0" class="pending-section">
      <h3>待保存 ({{ pendingLength }})</h3>
      <div class="items-list">
        <div 
          v-for="(item, index) in pendingItems" 
          :key="`pending-${item.id}`"
          class="item-card pending"
          :class="{ expanded: expandedItems.includes(`pending-${item.id}`) }"
        >
          <div class="item-header" @click="toggleExpand(`pending-${item.id}`)">
            <div class="item-info">
              <span class="item-index" :class="getBranchActionClass(item)">{{ index + 1 }}</span>
              <span class="item-title">{{ getTitle(item) }}</span>
              <span class="type-badge" :class="getTypeClass(item)">{{ getTypeLabel(item) }}</span>
            </div>
            <div class="item-actions">
              <span class="item-score">Score: {{ getScore(item).toFixed(3) }}</span>
              <button @click.stop="removePendingItem(item.id)" class="btn-remove">×</button>
            </div>
          </div>
          <div v-if="expandedItems.includes(`pending-${item.id}`)" class="item-details">
            <ItemDetail :item="item" />
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="selectedLength === 0 && pendingLength === 0" class="empty-state">
      <div class="empty-content">
        <p>📌 提示：</p>
        <ul>
          <li>点击策略卡片可全选该卡片内的所有点</li>
          <li>Ctrl + 点击数据点可连续添加</li>
          <li>点击"保存"按钮将待保存列表添加到已保存列表</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { useStore } from 'vuex';
import { ref, computed, watch } from 'vue';
import ItemDetail from './ItemDetail.vue';

const store = useStore();

// 定义emits
const emit = defineEmits(['show-hypothesis']);

// 检查是否有hypothesis数据（从store获取）
const hasHypothesis = computed(() => {
  // 从store获取experimentResult
  const experimentResult = store.state.experimentResult;
  return !!(experimentResult && experimentResult.hypothesis);
});

const showHypothesis = () => {
  const experimentResult = store.state.experimentResult;
  if (experimentResult && experimentResult.hypothesis) {
    emit('show-hypothesis', experimentResult.hypothesis);
  } else {
    alert('暂无 Hypothesis 数据');
  }
};

const selectedLength = ref(store.state.selectedItems.length); // 初始化值
const pendingLength = ref(store.state.pendingItems.length);
// 使用 ref 存储数组，确保响应式更新
const selectedItems = ref([...(store.state.selectedItems || [])]);
const pendingItems = ref([...(store.state.pendingItems || [])]);
// 响应式数据
const expandedItems = ref([]);

watch(
  () => [store.state.selectedItems, store.state.pendingItems],
  () => {
    const newSelected = store.state.selectedItems || [];
    const newPending = store.state.pendingItems || [];
    const newSelectedLength = newSelected.length;
    const newPendingLength = newPending.length;
    
    console.log('手动监听到 state 变化：', {
      selectedLength: newSelectedLength,
      pendingLength: newPendingLength,
      selectedItems: newSelected,
      pendingItems: newPending
    });
    
    // 同步更新长度 ref
    selectedLength.value = newSelectedLength;
    pendingLength.value = newPendingLength;
    
    // 同步更新数组 ref（创建新数组引用确保响应式）
    selectedItems.value = [...newSelected];
    pendingItems.value = [...newPending];
    
    console.log('自动更新：已保存=', selectedLength.value, '条，待保存=', pendingLength.value);
    console.log('selectedItems ref 更新后长度:', selectedItems.value.length);
    console.log('pendingItems ref 更新后长度:', pendingItems.value.length);
    
    // 触发组件重新渲染
    expandedItems.value = [...expandedItems.value];
  },
  { deep: true, immediate: false }
);

const totalCount = computed(() => selectedLength.value + pendingLength.value);

const pictureCount = computed(() => {
  const all = [...selectedItems.value, ...pendingItems.value];
  return all.filter(item => item && item.type === 'picture').length;
});

const textureCount = computed(() => {
  const all = [...selectedItems.value, ...pendingItems.value];
  return all.filter(item => item && item.type === 'texture').length;
});

const avgScore = computed(() => {
  const all = [...selectedItems.value, ...pendingItems.value];
  if (all.length === 0) return 0;
  const sum = all.reduce((acc, item) => acc + (getScore(item) || 0), 0);
  return sum / all.length;
});

// 方法
const toggleExpand = (itemId) => {
  const index = expandedItems.value.indexOf(itemId);
  if (index > -1) {
    expandedItems.value.splice(index, 1);
  } else {
    expandedItems.value.push(itemId);
  }
};

const savePending = () => {
  // 直接从 store.state 读取最新状态
  const pendingArray = store.state.pendingItems || [];
  const pendingCount = pendingArray.length;
  
  console.log('=== 保存按钮被点击 ===');
  console.log('当前待保存项目数 (store.state):', pendingCount);
  console.log('当前待保存项目 (store.state):', pendingArray);
  console.log('当前待保存项目数 (computed):', pendingItems.value.length);
  console.log('当前待保存项目 (computed):', pendingItems.value);
  
  if (pendingCount === 0) {
    console.warn('没有待保存的项目');
    alert('没有待保存的项目');
    return;
  }
  
  // 执行保存 - 传递当前待保存的项目数组
  console.log('准备保存，待保存项目:', pendingArray);
  store.commit('savePendingItems');
  
  // 使用 nextTick 确保 mutation 完成后再更新
  setTimeout(() => {
    const newSelected = store.state.selectedItems || [];
    const newPending = store.state.pendingItems || [];
    
    // 同步更新长度和数组
    selectedLength.value = newSelected.length;
    pendingLength.value = newPending.length;
    selectedItems.value = [...newSelected];
    pendingItems.value = [...newPending];
    
    console.log('savePending - selectedLength:', selectedLength.value);
    console.log('savePending - pendingLength:', pendingLength.value);
    console.log('savePending - selectedItems.length:', selectedItems.value.length);
    console.log('savePending - pendingItems.length:', pendingItems.value.length);
  }, 0);

  // 清空展开状态
  expandedItems.value = [];
  
  // 立即检查保存结果
  console.log('保存后立即检查:');
  console.log('  - selectedItems.length:', store.state.selectedItems.length);
  console.log('  - pendingItems.length:', store.state.pendingItems.length);
  
  // 使用 nextTick 确保 DOM 更新后再读取
  setTimeout(() => {
    const savedCount = store.state.selectedItems.length;
    console.log('保存完成，已保存项目数:', savedCount);
    console.log('保存后的 selectedItems:', store.state.selectedItems);
    console.log('保存后的 pendingItems:', store.state.pendingItems);
  }, 100);
};

const clearPending = () => {
  store.commit('clearPendingItems');
  expandedItems.value = [];
};

const clearAll = () => {
  if (confirm('确定要清空所有已保存的数据点吗？')) {
    store.commit('clearSelectedItems');
    // 同步更新长度
    setTimeout(() => {
      selectedLength.value = store.state.selectedItems.length;
    }, 0);
    expandedItems.value = [];
  }
};

const removeItem = (itemId) => {
  store.commit('removeSelectedItem', itemId);
  // 同步更新长度
  setTimeout(() => {
    selectedLength.value = store.state.selectedItems.length;
  }, 0);
  // 移除展开状态
  expandedItems.value = expandedItems.value.filter(id => !id.includes(itemId));
};

const removePendingItem = (itemId) => {
  store.commit('removePendingItem', itemId);
  // 同步更新长度
  setTimeout(() => {
    pendingLength.value = store.state.pendingItems.length;
  }, 0);
  // 移除展开状态
  expandedItems.value = expandedItems.value.filter(id => !id.includes(itemId));
};

// 工具函数：优先使用 paper_title（来自 metadata），其次 title
const getTitle = (item) => {
  return item.paper_title || item.title || 'No Title';
};

const getTypeLabel = (item) => {
  if (item.type === 'picture') return '图片';
  if (item.type === 'texture') return '文本';
  return '未知';
};

const getTypeClass = (item) => {
  if (item.type === 'picture') return 'type-picture';
  if (item.type === 'texture') return 'type-texture';
  return '';
};

const getScore = (item) => {
  return item.score || 0;
};

// 根据 branch_action 返回小圆点的样式类（与策略矩形内颜色一致）
const getBranchActionClass = (item) => {
  const action = item.branch_action || 'UNKNOWN';
  if (action === 'GROW') return 'action-grow';
  if (action === 'KEEP') return 'action-keep';
  if (action === 'PRUNE') return 'action-prune';
  if (action === 'PENDING') return 'action-pending';
  return 'action-unknown';
};
</script>

<style scoped>
.detail-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.toolbar {
  padding: 15px;
  background: white;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-save {
  background: #28a745;
  color: white;
}

.btn-save:hover {
  background: #218838;
}

.btn-clear {
  background: #ffc107;
  color: #333;
}

.btn-clear:hover {
  background: #e0a800;
}

.btn-clear-all {
  background: #dc3545;
  color: white;
}

.btn-clear-all:hover {
  background: #c82333;
}

.btn-hypothesis {
  background: #17a2b8;
  color: white;
}

.btn-hypothesis:hover:not(:disabled) {
  background: #138496;
}

.btn-hypothesis:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

.overview-section {
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e9ecef;
}

.overview-section h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #4A90E2;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

.saved-section,
.pending-section {
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e9ecef;
}

.saved-section h3,
.pending-section h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.item-card {
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  transition: all 0.2s;
}

.item-card.saved {
  border-left: 4px solid #28a745;
}

.item-card.pending {
  border-left: 4px solid #ffc107;
}

.item-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.item-card.expanded {
  background: white;
}

.item-header {
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.item-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.item-index {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  background: #4A90E2;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

/* 小圆点按 branch_action 着色，与策略矩形内一致 */
.item-index.action-grow {
  background: #28a745;
  color: white;
}
.item-index.action-keep {
  background: #ffc107;
  color: #333;
}
.item-index.action-prune {
  background: #dc3545;
  color: white;
}
.item-index.action-pending {
  background: #6c757d;
  color: white;
}
.item-index.action-unknown {
  background: #b0b0b0;
  color: white;
}

.item-title {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.item-score {
  font-size: 12px;
  color: #666;
}

.btn-remove {
  width: 24px;
  height: 24px;
  border: none;
  background: #dc3545;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-remove:hover {
  background: #c82333;
  transform: scale(1.1);
}

.item-details {
  padding: 0 15px 15px 15px;
  border-top: 1px solid #e9ecef;
  margin-top: 10px;
  padding-top: 15px;
}

.type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  flex-shrink: 0;
}

.type-picture {
  background-color: #e3f2fd;
  color: #1976d2;
}

.type-texture {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.empty-content {
  text-align: center;
  color: #7f8c8d;
  font-size: 14px;
}

.empty-content p {
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 500;
}

.empty-content ul {
  text-align: left;
  display: inline-block;
  list-style: none;
  padding: 0;
}

.empty-content li {
  margin: 10px 0;
  padding-left: 20px;
  position: relative;
}

.empty-content li:before {
  content: '•';
  position: absolute;
  left: 0;
  color: #4A90E2;
}
</style>