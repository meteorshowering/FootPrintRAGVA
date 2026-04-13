# 实验数据可视化面板使用说明

## 组件说明

`ExperimentDashboard.vue` 是一个全新的实验数据可视化组件，用于展示 `experiment_results_*.json` 文件的详细分析。

## 功能特性

1. **实验概览**
   - 实验目标
   - 总轮次数
   - 总查询数
   - 总结果数
   - 平均检索分数

2. **策略使用统计**
   - 各策略的使用频率柱状图

3. **检索分数分布**
   - 所有检索结果的分数直方图

4. **轮次演进趋势**
   - 每轮的查询数、结果数、平均分数趋势线

5. **评估分数分析**
   - 相关性分数分布
   - 可信度分数分布

6. **策略效果对比**
   - 各策略的平均检索分数对比

7. **轮次详情表格**
   - 每轮的详细统计信息
   - 可点击查看每轮的详细内容

## 快速开始

### 方法1：修改 main.js（最简单，推荐）

1. 打开 `src/main.js`
2. 临时修改为：
```javascript
import { createApp } from 'vue';
import AppDashboard from './AppDashboard';  // 改为导入 AppDashboard

createApp(AppDashboard)  // 使用 AppDashboard
  .use(store)
  .mount('#app');
```

3. 运行 `npm run serve`
4. 访问 `http://localhost:8080` 即可看到实验数据可视化面板

5. 测试完成后，恢复原来的 `main.js`：
```javascript
import { createApp } from 'vue';
import App from './App';  // 恢复为 App

createApp(App)  // 恢复为 App
  .use(store)
  .mount('#app');
```

### 方法2：临时替换组件（如果需要保留原有功能）

1. 打开 `src/App.vue`
2. 临时替换组件导入：
```vue
<script>
import ExperimentDashboard from './components/ExperimentDashboard';
// import RiverChart from './components/RiverChart';
// import DetailView from './components/DetailView';
// import MapView from './components/MapView';

export default {
  name: 'App',
  components: {
    ExperimentDashboard
    // RiverChart,
    // DetailView,
    // MapView
  }
};
</script>
```

3. 修改模板：
```vue
<template>
  <div id="app">
    <ExperimentDashboard />
  </div>
</template>
```

4. 运行 `npm run serve`
5. 访问 `http://localhost:8080`

### 方法2：创建独立路由（需要安装vue-router）

如果需要同时保留原有功能，可以安装 vue-router 并创建路由。

### 方法3：通过URL参数切换（需要修改main.js）

可以修改 `main.js` 来根据URL参数动态加载不同组件。

## 数据文件

组件会自动从 `public` 目录加载以下文件：
- `experiment_results_20260203_173057.json` (默认)
- `experiment_results_20260129_114431.json`

可以在组件顶部的下拉菜单中选择不同的数据文件。

## 注意事项

1. 确保 JSON 文件在 `public` 目录下
2. 组件使用 D3.js 进行图表绘制，确保已安装 d3 依赖
3. 组件响应式设计，支持不同屏幕尺寸
4. 所有图表在窗口大小变化时会自动重绘

## 技术栈

- Vue 3
- D3.js 7.x
- 响应式设计

## 开发建议

如果需要长期使用，建议：
1. 安装 vue-router 创建路由系统
2. 在导航栏添加"实验面板"链接
3. 或者创建独立的页面入口
