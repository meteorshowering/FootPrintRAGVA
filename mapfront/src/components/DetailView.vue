<template>
  <div class="detail-container">
    <div class="toolbar">
      <button
        type="button"
        @click="showHypothesis"
        class="btn btn-hypothesis"
        :disabled="!hasHypothesis"
        :title="hasHypothesis ? '查看核心科学假设' : '暂无Hypothesis数据'"
      >
        📊 查看 Hypothesis
      </button>
    </div>

    <InteractiveReportPanel />
  </div>
</template>

<script setup>
import { useStore } from 'vuex';
import { computed, defineEmits } from 'vue';
import InteractiveReportPanel from './InteractiveReportPanel.vue';

const store = useStore();

const emit = defineEmits(['show-hypothesis']);

const hasHypothesis = computed(() => {
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
</script>

<style scoped>
.detail-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  min-height: 0;
}

.toolbar {
  padding: 15px;
  background: white;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  flex-shrink: 0;
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

.detail-container > :deep(.ir-panel) {
  margin: 12px;
}
</style>
