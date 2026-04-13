<template>
  <div id="mapview">
    <!-- 控制按钮 -->
    <div class="controls">
      <button @click="drawConnections" class="btn btn-primary">显示引用关系</button>
      <button @click="clearConnections" class="btn btn-secondary">清除连线</button>
      <button @click="toggleDensityMap" class="btn btn-tertiary">
        {{ showDensityMap ? '隐藏密度地图' : '显示密度地图' }}
      </button>
      <button @click="toggleDataFormat" class="btn btn-info" :class="{ active: useNewDataFormat }">
        {{ useNewDataFormat ? '新坐标数据' : '旧坐标数据' }}
      </button>
    </div>

    <!-- SVG -->
    <svg ref="svg" :width="svgWidth" :height="svgHeight"></svg>
  </div>
</template>

<script>
import { createMapViewLogic } from '../lib/mapViewLogic';

export default {
  name: 'MapView',
  ...createMapViewLogic(),
};
</script>

<style scoped>
#mapview {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: #f8f9fa;
}

svg {
  width: 100%;
  height: 100%;
  display: block;
}

.controls {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 1000;
  display: flex;
  gap: 12px;
  background: rgba(255, 255, 255, 0.95);
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.btn {
  padding: 10px 18px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  min-width: 100px;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
}

.btn-tertiary {
  background-color: #28a745;
  color: white;
}

.btn-tertiary:hover {
  background-color: #218838;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.btn-info {
  background-color: #17a2b8;
  color: white;
}

.btn-info:hover {
  background-color: #138496;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(23, 162, 184, 0.3);
}

.btn-info.active {
  background-color: #138496;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.content-group {
  cursor: grab;
}

.content-group:active {
  cursor: grabbing;
}

.tooltip {
  background: white;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
  pointer-events: none;
  z-index: 1001;
}
</style>