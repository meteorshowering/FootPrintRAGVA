# 增强版河流图组件使用说明

## 组件概述

`EnhancedRiverChart.vue` 是一个功能完整的实验数据可视化组件，基于原有的 `RiverChart.vue` 进行了全面增强，实现了以下功能：

## 主要功能

### 1. 河流图布局
- **从左到右**：表示轮次增加（Round 0, 1, 2, ...）
- **纵向排列**：每轮中的多个检索策略（query_results）垂直排列
- **独立画布**：每个策略是一个独立的画布区域

### 2. 底图与检索结果可视化
- **统一底图**：使用 `multimodal2text_embeddings_2d.json` 作为底图数据源
- **底图点**：所有数据库点以浅灰色小点显示
- **检索结果高亮**：检索到的结果点以不同颜色和大小突出显示
- **颜色编码**：
  - 🟢 **绿色 (GROW)**：结果被标记为增长
  - 🔴 **红色 (PRUNE)**：结果被标记为修剪
  - 🟡 **黄色 (KEEP)**：结果被标记为保留
- **大小编码**：点的大小根据 `score` 值动态调整（score越高，点越大）

### 3. 连线功能
- **自动连线**：如果第 i+1 轮中某个策略的 `ParentNode` 在第 i 轮的某个策略的检索结果中，自动用平滑曲线连接
- **双线连接**：使用两条贝塞尔曲线（上边和下边）连接，颜色分别为蓝色和绿色
- **可切换显示**：通过"隐藏连线/显示连线"按钮控制

### 4. 策略总结弹窗
- **点击画布**：点击任意策略画布，弹出该策略的 `plansummary` 总结
- **格式化显示**：支持 Markdown 格式，包括标题、加粗、代码块等
- **完整信息**：显示轮次号、查询序号和完整的策略总结内容

### 5. 轮次总结可视化
- **词频图**：显示该轮次中出现频率最高的前20个关键词
- **词云图**：以词云形式展示关键词，字体大小反映频率
- **关键词提取**：从 `plansummary` 和 `query_intent` 中自动提取关键词
- **访问方式**：点击每轮次标签旁的"总结"按钮

### 6. 检索结果详情
- **点击查看**：点击任意检索结果点，弹出详情弹窗
- **详细信息**：显示图片、关键实体、摘要、洞察等信息
- **格式兼容**：与原有 `DetailView` 组件格式完全兼容

### 7. 追问功能
- **追问按钮**：在详情弹窗底部提供"追问"输入框和提交按钮
- **自动添加**：提交追问后，系统会在下一轮次自动添加一个空画布
- **问题记录**：追问内容会作为新策略的 `query_intent` 保存
- **父节点关联**：新策略的 `ParentNode` 自动关联到当前查看的检索结果

## 使用方法

### 方法1：替换现有组件（推荐用于测试）

1. 打开 `src/App.vue`
2. 修改导入：
```vue
<script>
import EnhancedRiverChart from './components/EnhancedRiverChart';
// import RiverChart from './components/RiverChart';
// import DetailView from './components/DetailView';
// import MapView from './components/MapView';

export default {
  name: 'App',
  components: {
    EnhancedRiverChart
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
    <div class="container">
      <div class="left-pane">
        <div class="top-section">
          <EnhancedRiverChart />
        </div>
      </div>
      <div class="right-pane">
        <!-- 详情面板可以保留或移除 -->
      </div>
    </div>
  </div>
</template>
```

4. 运行 `npm run serve`

### 方法2：创建独立页面

参考 `AppDashboard.vue` 的方式，创建新的入口文件。

## 数据文件要求

### 必需文件
- `public/multimodal2text_embeddings_2d.json` - 底图坐标数据
- `public/experiment_results_*.json` - 实验结果数据

### 数据格式
- 底图数据应包含 `coordinates_2d` 字段和 `metadata.id` 字段
- 实验结果数据应包含 `iterations` 数组，每个迭代包含 `round_number` 和 `query_results`

## 交互说明

### 鼠标操作
- **点击画布**：显示策略总结
- **点击检索结果点**：显示详情
- **鼠标悬停**：显示点的基本信息（ID、Score、Action）
- **滚轮缩放**：支持画布缩放和平移

### 按钮功能
- **加载所有轮次**：重新加载并绘制所有数据
- **清除图表**：清空当前显示
- **隐藏/显示标签**：切换轮次和查询标签的显示
- **隐藏/显示连线**：切换策略间连线的显示
- **数据文件选择**：切换不同的实验结果文件

## 技术特性

### 性能优化
- 使用 D3.js 进行高效的数据绑定和DOM操作
- 底图点使用轻量级渲染（小点、低透明度）
- 检索结果点按需渲染，支持大量数据

### 响应式设计
- 自动适应窗口大小变化
- 支持不同屏幕尺寸
- 弹窗自适应内容大小

### 数据兼容性
- 兼容新旧数据格式
- 自动处理缺失字段
- 支持空查询显示

## 注意事项

1. **底图文件**：确保 `multimodal2text_embeddings_2d.json` 文件存在于 `public` 目录
2. **数据格式**：确保实验结果 JSON 文件格式正确
3. **浏览器兼容性**：建议使用现代浏览器（Chrome、Firefox、Edge 最新版）
4. **性能考虑**：如果数据量很大，可能需要调整渲染参数

## 扩展功能建议

如果需要进一步扩展，可以考虑：
1. 添加筛选功能（按策略类型、分数范围等）
2. 添加导出功能（导出图片、PDF等）
3. 添加动画效果（轮次切换动画）
4. 添加搜索功能（搜索特定关键词或ID）
5. 添加统计面板（显示整体统计信息）

## 故障排除

### 问题：底图不显示
- 检查 `multimodal2text_embeddings_2d.json` 文件是否存在
- 检查浏览器控制台是否有错误信息
- 确认文件格式正确

### 问题：连线不显示
- 检查数据中是否包含 `ParentNode` 字段
- 确认 `ParentNode` 的值在上一轮的检索结果中存在
- 点击"显示连线"按钮

### 问题：弹窗不显示
- 检查浏览器控制台是否有 JavaScript 错误
- 确认数据中包含 `plansummary` 字段（对于策略总结）
- 确认点击的是有效的检索结果点（对于详情）

## 更新日志

### v1.0.0 (2024-02-03)
- 初始版本发布
- 实现所有核心功能
- 支持策略总结、轮次总结、详情查看、追问功能
