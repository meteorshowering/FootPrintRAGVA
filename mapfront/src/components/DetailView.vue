<template>
  <div class="detail-container">
    <InteractiveReportPanel />
  </div>
</template>

<script setup>
import InteractiveReportPanel from './InteractiveReportPanel.vue';
</script>

<style scoped>
.detail-container {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  min-height: 0;
}

.detail-container > :deep(.ir-panel) {
  margin: 12px;
}
</style>
