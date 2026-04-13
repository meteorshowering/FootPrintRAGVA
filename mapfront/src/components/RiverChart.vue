<template>
  <div id="river-chart">
    <!-- 控制按钮 -->
    <div class="controls">
      <button @click="loadAllRounds" class="btn btn-primary">加载所有轮次</button>
      <button @click="clearChart" class="btn btn-secondary">清除图表</button>
      <button @click="toggleLabels" class="btn btn-tertiary">{{ showLabels ? '隐藏标签' : '显示标签' }}</button>
      <button @click="toggleConnections" class="btn btn-quaternary">{{ showConnections ? '隐藏连线' : '显示连线' }}</button>
      <button @click="toggleEmptyQueries" class="btn btn-quinary">{{ showEmptyQueries ? '隐藏空查询' : '显示空查询' }}</button>
      <button @click="toggleDataFormat" class="btn btn-info" :class="{ active: useNewDataFormat }">
        {{ useNewDataFormat ? '新坐标数据' : '旧坐标数据' }}
      </button>
    </div>
    
    <!-- SVG 画布 -->
    <svg ref="svg" :width="svgWidth" :height="svgHeight"></svg>
  </div>
</template>

<script>
import * as d3 from 'd3';

// 矩形位置管理类 - 在collectRectPositions方法中使用
class RectPosition {
  constructor(roundNumber, queryIndex, x, y, width, height) {
    this.roundNumber = roundNumber;
    this.queryIndex = queryIndex;
    this.x = x; // 矩形中心x坐标
    this.y = y; // 矩形中心y坐标
    this.width = width;
    this.height = height;
    
    // 计算四个角点坐标
    this.corners = this.calculateCorners();
    
    // 计算关键点坐标
    this.keyPoints = this.calculateKeyPoints();
  }
  
  // 计算四个角点坐标
  calculateCorners() {
    const halfWidth = this.width / 2;
    const halfHeight = this.height / 2;
    
    return {
      topLeft: { x: this.x - halfWidth, y: this.y - halfHeight },
      topRight: { x: this.x + halfWidth, y: this.y - halfHeight },
      bottomLeft: { x: this.x - halfWidth, y: this.y + halfHeight },
      bottomRight: { x: this.x + halfWidth, y: this.y + halfHeight }
    };
  }
  
  // 计算关键点坐标（用于连线等）
  calculateKeyPoints() {
    const halfWidth = this.width / 2;
    const halfHeight = this.height / 2;
    
    return {
      // 四个边的中点
      topCenter: { x: this.x, y: this.y - halfHeight },
      bottomCenter: { x: this.x, y: this.y + halfHeight },
      leftCenter: { x: this.x - halfWidth, y: this.y },
      rightCenter: { x: this.x + halfWidth, y: this.y },
      
      // 四个角点（与corners一致，方便使用）
      topLeft: this.corners.topLeft,
      topRight: this.corners.topRight,
      bottomLeft: this.corners.bottomLeft,
      bottomRight: this.corners.bottomRight,
      
      // 中心点
      center: { x: this.x, y: this.y }
    };
  }
  
  // 获取连线起点（右上角和右下角）
  getConnectionStart() {
    // 返回两个起点：右上角和右下角
    return {
      topRight: this.keyPoints.topRight,
      bottomRight: this.keyPoints.bottomRight
    };
  }
  
  // 获取连线终点（左上角和左下角）
  getConnectionEnd() {
    // 返回两个终点：左上角和左下角
    return {
      topLeft: this.keyPoints.topLeft,
      bottomLeft: this.keyPoints.bottomLeft
    };
  }
  
  // 检查点是否在矩形内
  containsPoint(pointX, pointY) {
    const halfWidth = this.width / 2;
    const halfHeight = this.height / 2;
    
    return (
      pointX >= this.x - halfWidth &&
      pointX <= this.x + halfWidth &&
      pointY >= this.y - halfHeight &&
      pointY <= this.y + halfHeight
    );
  }
  
  // 获取矩形边界
  getBounds() {
    return {
      left: this.x - this.width / 2,
      right: this.x + this.width / 2,
      top: this.y - this.height / 2,
      bottom: this.y + this.height / 2
    };
  }
  
  // 转换为简单对象（用于序列化）
  toObject() {
    return {
      roundNumber: this.roundNumber,
      queryIndex: this.queryIndex,
      x: this.x,
      y: this.y,
      width: this.width,
      height: this.height,
      corners: this.corners,
      keyPoints: this.keyPoints
    };
  }
}

export default {
  name: 'RiverChart',
  data() {
    return {
      roundsData: [],
      svgWidth: 0,
      svgHeight: 0,
      showLabels: true,
      showConnections: true, // 是否显示连线
      showEmptyQueries: false, // 是否显示空查询
      useNewDataFormat: true, // 是否使用新数据格式
      // 布局参数
      roundWidth: 300,      // 每个轮次矩形的宽度（增加以容纳地图）
      queryMargin: 10,      // query_results之间的间距
      dotRadius: 32,         // 圆点半径
      dotMargin: 5,         // 圆点之间的间距
      roundMargin: 90,      // 轮次之间的间距
      queryHeight: 300,     // 统一的高度，确保等高线画布大小一致
      // 连线相关
      connectionGroup: null, // 连线容器
      rectPositions: {},    // 存储所有矩形位置信息
      // 地图相关
      mapPoints: [],        // 所有地图点数据
      globalXExtent: null,  // 完整数据库的x范围
      globalYExtent: null,  // 完整数据库的y范围
    };
  },
  computed: {
    // 计算总宽度
    totalWidth() {
      return this.roundsData.length * (this.roundWidth + this.roundMargin) + this.roundMargin;
    }
  },
  methods: {
    // 加载地图数据，支持两种格式
    async loadMapData() {
      try {
        // const dataFile = this.useNewDataFormat ? '/scientific_rag_embeddings_2d.json' : '/enhanced_figures_with_coordinates.json';
        const dataFile = this.useNewDataFormat ? '/scientific_rag_embeddings_2d_papercollection.json' : '/scientific_rag_embeddings_2d.json';
        const response = await fetch(dataFile);
        const rawData = await response.json();
        
        // 处理数据格式
        this.mapPoints = this.processMapData(rawData, this.useNewDataFormat);
        console.log(`地图数据加载完成 (${this.useNewDataFormat ? '新' : '旧'}格式)，共`, this.mapPoints.length, '个点');
        
        // 计算全局范围，用于统一所有小矩形的缩放比例
        this.globalXExtent = d3.extent(this.mapPoints, d => d.x);
        this.globalYExtent = d3.extent(this.mapPoints, d => d.y);
        console.log('全局x范围:', this.globalXExtent);
        console.log('全局y范围:', this.globalYExtent);
      } catch (error) {
        console.error('加载地图数据失败:', error);
      }
    },

    // 处理地图数据，支持两种格式
    processMapData(rawData, useNewFormat = false) {
      if (useNewFormat) {
        // 新格式：使用coordinates_2d数组
        return rawData.map(item => {
          const coords = item.coordinates_2d || [0, 0];
          return {
            ...item,
            x: coords[0],
            y: coords[1],
            // 确保有id字段，使用metadata中的id作为旧格式的对应
            id: item.metadata?.id || item.id
          };
        });
      } else {
        // 旧格式：直接使用x和y字段
        return rawData;
      }
    },

    // 计算凸包（Graham扫描算法）
    computeConvexHull(points) {
      if (points.length < 3) return points;
      
      // 找到最左下角的点
      let startPoint = points[0];
      for (let i = 1; i < points.length; i++) {
        if (points[i].y < startPoint.y || 
            (points[i].y === startPoint.y && points[i].x < startPoint.x)) {
          startPoint = points[i];
        }
      }
      
      // 按极角排序
      const sortedPoints = points
        .filter(p => p !== startPoint)
        .sort((a, b) => {
          const angleA = Math.atan2(a.y - startPoint.y, a.x - startPoint.x);
          const angleB = Math.atan2(b.y - startPoint.y, b.x - startPoint.x);
          return angleA - angleB;
        });
      
      // Graham扫描
      const hull = [startPoint, sortedPoints[0]];
      
      for (let i = 1; i < sortedPoints.length; i++) {
        while (hull.length >= 2) {
          const a = hull[hull.length - 2];
          const b = hull[hull.length - 1];
          const c = sortedPoints[i];
          
          // 计算叉积
          const cross = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
          if (cross <= 0) {
            hull.pop();
          } else {
            break;
          }
        }
        hull.push(sortedPoints[i]);
      }
      
      return hull;
    },

    // 获取查询对应的点数据并计算凸包
    getConvexHullForQuery(query) {
      if (!query.rag_results || query.rag_results.length === 0) return null;
      
      // 获取查询中所有RAG结果对应的点
      const queryPoints = [];
      query.rag_results.forEach(rag => {
        const pointId = rag.retrieval_result.id;
        const point = this.mapPoints.find(p => p.id === pointId || p.id === `img_${pointId}`);
        if (point) {
          queryPoints.push({ x: point.x, y: point.y, id: point.id });
        }
      });
      
      if (queryPoints.length < 3) return null;
      
      // 计算凸包
      return this.computeConvexHull(queryPoints);
    },

    // 加载所有轮次的JSON数据
    async loadAllRounds() {
      this.clearChart();
      
      // 先加载地图数据
      await this.loadMapData();
      
      try {
        // 从统一的experiment_results文件加载数据
        const response = await fetch('/experiment_results_20260129_114431.json');
        const experimentData = await response.json();
        
        // 提取iterations数组作为轮次数据
        this.roundsData = experimentData.iterations || [];
        
        // 过滤掉undefined或无效的轮次数据（更宽松的条件）
        this.roundsData = this.roundsData.filter(round => {
          if (!round || typeof round !== 'object') {
            console.warn('过滤掉无效的轮次对象:', round);
            return false;
          }
          
          // 检查是否有query_results属性（这是连线分析的关键）
          const hasQueryResults = round.query_results !== undefined;
          
          // 如果没有round_number，尝试使用文件名或其他标识
          if (round.round_number === undefined) {
            console.warn('轮次对象缺少round_number属性，但保留用于连线分析:', round);
            // 仍然保留，因为可能有query_results数据
            return hasQueryResults;
          }
          
          return true;
        });
        
        // 按轮次号排序（确保顺序正确）
        this.roundsData.sort((a, b) => a.round_number - b.round_number);
        
        console.log('加载的实验数据:', experimentData);
        console.log('提取的轮次数据:', this.roundsData);
        
        // 绘制河流图
        this.drawRiverChart();
        
      } catch (error) {
        console.error('加载实验数据失败:', error);
        
        // 如果统一文件加载失败，尝试回退到旧的多文件方式
        console.log('尝试回退到旧的多文件加载方式...');
        await this.loadRoundsFallback();
      }
    },
    
    // 回退方法：旧的多文件加载方式
    // async loadRoundsFallback() {
    //   try {
    //     // 查找所有JSON文件
    //     const response = await fetch('/roundresult/');
    //     const text = await response.text();
    //     const parser = new DOMParser();
    //     const html = parser.parseFromString(text, 'text/html');
    //     const links = html.querySelectorAll('a[href$=".json"]');
        
    //     const jsonFiles = Array.from(links).map(link => link.href.split('/').pop());
        
    //     // 加载每个JSON文件
    //     const loadPromises = jsonFiles.map(file => 
    //       fetch(`/roundresult/${file}`)
    //         .then(response => response.json())
    //         .catch(error => {
    //           console.error(`加载文件 ${file} 失败:`, error);
    //           return null;
    //         })
    //     );
        
    //     const results = await Promise.all(loadPromises);
    //     this.roundsData = results.filter(round => round !== null);
        
    //     // 过滤掉undefined或无效的轮次数据（更宽松的条件）
    //     this.roundsData = this.roundsData.filter(round => {
    //       if (!round || typeof round !== 'object') {
    //         console.warn('过滤掉无效的轮次对象:', round);
    //         return false;
    //       }
          
    //       // 检查是否有query_results属性（这是连线分析的关键）
    //       const hasQueryResults = round.query_results !== undefined;
          
    //       // 如果没有round_number，尝试使用文件名或其他标识
    //       if (round.round_number === undefined) {
    //         console.warn('轮次对象缺少round_number属性，但保留用于连线分析:', round);
    //         // 仍然保留，因为可能有query_results数据
    //         return hasQueryResults;
    //       }
          
    //       return true;
    //     });
        
    //     // 按轮次号排序
    //     this.roundsData.sort((a, b) => a.round_number - b.round_number);
        
    //     // 绘制河流图
    //     this.drawRiverChart();
        
    //   } catch (error) {
    //     console.error('回退加载也失败:', error);
    //   }
    // },

    // 绘制河流图
    drawRiverChart() {
      const svg = d3.select(this.$refs.svg);
      svg.selectAll('*').remove();

      // 检查是否有数据
      if (!this.roundsData || this.roundsData.length === 0) {
        console.warn('没有可用的轮次数据，无法绘制河流图');
        
        // 显示提示信息
        svg.append('text')
          .attr('x', '50%')
          .attr('y', '50%')
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .attr('font-size', '16px')
          .attr('fill', '#999')
          .text('没有可用的实验数据，请检查数据文件');
        return;
      }

      // 设置SVG尺寸
      this.svgWidth = this.$el.clientWidth;
      this.svgHeight = this.$el.clientHeight;
      
      svg.attr('width', this.svgWidth).attr('height', this.svgHeight);

      // 创建主容器
      const container = svg.append('g').attr('class', 'river-container');

      // 计算布局
      let currentX = this.roundMargin;
      
      this.roundsData.forEach((round, roundIndex) => {
        // 绘制轮次矩形
        const roundGroup = container.append('g').attr('class', `round-${roundIndex}`);
        
        // 计算轮次矩形的高度（基于所有query_results的高度）
        let roundHeight = 0;
        if (round.query_results && Array.isArray(round.query_results)) {
          round.query_results.forEach(() => {
            const queryHeight = this.calculateQueryHeight();
            roundHeight += queryHeight + this.queryMargin;
          });
          roundHeight -= this.queryMargin; // 减去最后一个间距
        }
        
        // 绘制轮次背景矩形
        roundGroup.append('rect')
          .attr('x', currentX)
          .attr('y', this.roundMargin)
          .attr('width', this.roundWidth)
          .attr('height', roundHeight)
          .attr('fill', 'rgba(240, 240, 240, 0.5)')
          .attr('stroke', '#ccc')
          .attr('stroke-width', 1)
          .attr('rx', 8) // 圆角
          .attr('ry', 8);

        // 添加轮次标签
        if (this.showLabels) {
          roundGroup.append('text')
            .attr('x', currentX + this.roundWidth / 2)
            .attr('y', 20)
            .attr('text-anchor', 'middle')
            .attr('font-size', '14px')
            .attr('font-weight', 'bold')
            .attr('fill', '#333')
            .text(`轮次 ${round.round_number}`);
        }

        // 绘制每个query_result（过滤空查询）
        let currentY = this.roundMargin + 40; // 从轮次标签下方开始
        
        if (round.query_results && Array.isArray(round.query_results)) {
          round.query_results.forEach((query, queryIndex) => {
            // 检查是否为空查询（没有rag_results）
            const isEmptyQuery = !query.rag_results || query.rag_results.length === 0;
            
            // 如果不显示空查询且当前是空查询，则跳过
            if (!this.showEmptyQueries && isEmptyQuery) {
              return;
            }
            
            const queryHeight = this.calculateQueryHeight();
            
            // 绘制query背景矩形（作为地图画布的容器）
            const queryGroup = roundGroup.append('g').attr('class', `query-${queryIndex}`);
          
          // 设置矩形样式（空查询使用不同的样式）
          const rectFill = isEmptyQuery ? 'rgba(248, 249, 250, 0.6)' : 'rgba(255, 255, 255, 0.8)';
          const rectStroke = isEmptyQuery ? '#e9ecef' : '#ddd';
          
          const queryRect = queryGroup.append('rect')
            .attr('x', currentX + 10)
            .attr('y', currentY)
            .attr('width', this.roundWidth - 20)
            .attr('height', queryHeight)
            .attr('fill', rectFill)
            .attr('stroke', rectStroke)
            .attr('stroke-width', 1)
            .attr('rx', 6)
            .attr('ry', 6)
            .style('cursor', 'pointer');
          
          // 添加hover卡片功能（所有查询，包括空查询）
          queryRect.on('mouseover', (event) => {
            this.showStrategyCard(event, query.orchestrator_plan);
          })
          .on('mouseout', () => {
            this.hideStrategyCard();
          });

          // 添加query标签
          if (this.showLabels) {
            const labelText = isEmptyQuery ? `空查询 ${queryIndex + 1}` : `查询 ${queryIndex + 1}`;
            const labelColor = isEmptyQuery ? '#adb5bd' : '#666';
            
            queryGroup.append('text')
              .attr('x', currentX + this.roundWidth / 2)
              .attr('y', currentY + 15)
              .attr('text-anchor', 'middle')
              .attr('font-size', '10px')
              .attr('fill', labelColor)
              .text(labelText);
          }

          // 在小矩形内创建地图画布（仅非空查询）
          if (!isEmptyQuery) {
            this.drawQueryMap(queryGroup, query, currentX, currentY, queryHeight);
          }

          currentY += queryHeight + this.queryMargin;
        });
      }

      currentX += this.roundWidth + this.roundMargin;
    });

      // 添加缩放功能
      this.addZoomBehavior(svg);
      
      // 绘制连线
      this.drawConnections();
    },

    // 计算query_result的高度（统一高度）
    calculateQueryHeight() {
      return this.queryHeight;
    },

    // 根据rag结果获取圆点颜色
    getDotColor(rag) {
      const score = rag.retrieval_result.score;
      if (score >= 0.8) return '#28a745'; // 高分数 - 绿色
      if (score >= 0.5) return '#ffc107'; // 中等分数 - 黄色
      return '#dc3545'; // 低分数 - 红色
    },

    // 选择rag结果
    selectRagResult(rag) {
      console.log('选择了RAG结果:', rag);
      // 触发新的河流图专用action
      this.$store.dispatch('selectRiverResult', rag.retrieval_result);
    },

    // 分析并创建跨轮次连线
    drawConnections() {
      if (!this.showConnections) return;
      
      console.log('=== 开始绘制连线 ===');
      console.log('showConnections:', this.showConnections);
      
      // 清除现有连线
      if (this.connectionGroup) {
        this.connectionGroup.selectAll('*').remove();
      }
      
      // 创建连线容器
      const svg = d3.select(this.$refs.svg);
      this.connectionGroup = svg.append('g').attr('class', 'connections');
      
      // 收集所有矩形的位置信息
      const rectPositions = this.collectRectPositions();
      console.log('收集到的矩形位置数据:', rectPositions);
      
      // 分析并绘制连线
      this.analyzeAndDrawConnections(rectPositions);
      
      console.log('=== 连线绘制完成 ===');
    },

    // 收集所有矩形的位置信息
    collectRectPositions() {
      const positions = {};
      
      console.log('开始收集矩形位置，轮次数据数量:', this.roundsData.length);
      
      this.roundsData.forEach((round, roundIndex) => {
        // 检查round对象是否存在
        if (!round) {
          console.warn(`轮次数据 ${roundIndex} 不存在，跳过`);
          positions[roundIndex] = {}; // 添加空对象以避免连线分析错误
          return;
        }
        
        console.log(`处理轮次 ${round.round_number}，查询数量:`, round.query_results?.length || 0);
        
        positions[round.round_number] = {};
        
        let currentY = this.roundMargin + 40;
        try{
          if (round.query_results && Array.isArray(round.query_results)) {
            round.query_results.forEach((query, queryIndex) => {
              // 检查是否为空查询
              const isEmptyQuery = !query.rag_results || query.rag_results.length === 0;
              
              // 如果不显示空查询且当前是空查询，则跳过
              if (!this.showEmptyQueries && isEmptyQuery) {
                return;
              }
              
              const queryHeight = this.calculateQueryHeight();
              
              // 计算矩形位置
              const x = this.roundMargin + roundIndex * (this.roundWidth + this.roundMargin) + this.roundWidth / 2;
              const y = currentY + queryHeight / 2;
            
              // 使用RectPosition类管理矩形位置数据
              const rectPosition = new RectPosition(
                round.round_number,
                queryIndex,
                x,
                y,
                this.roundWidth,
                queryHeight
              );
              
              // 添加查询相关属性
              rectPosition.parentNode = query.orchestrator_plan?.ParentNode;
              rectPosition.isEmptyQuery = isEmptyQuery;
              rectPosition.topY = currentY;
              rectPosition.bottomY = currentY + queryHeight;
              
              // 存储到位置数据中
              positions[round.round_number][queryIndex] = rectPosition;
              
              currentY += queryHeight + this.queryMargin;
            });
          }
        }catch(error){
          console.error(`处理轮次 ${round.round_number} 时出错:`, error);
        }
      });
      
      console.log('收集到的矩形位置数据:', positions);
      return positions;
    },

    // 分析并绘制连线
    analyzeAndDrawConnections(positions) {
      console.log('=== 开始分析连线 ===');
      console.log('所有轮次:', Object.keys(positions).map(Number));
      
      // 遍历所有轮次（从第一轮开始，与第0轮连接）
      for (let roundNum = 1; roundNum <= Math.max(...Object.keys(positions).map(Number)); roundNum++) {
        const currentRound = positions[roundNum];
        const prevRound = positions[roundNum - 1];
        
        console.log(`\n--- 分析轮次 ${roundNum} 与轮次 ${roundNum - 1} 的连接 ---`);
        console.log('当前轮次矩形数量:', Object.keys(currentRound || {}).length);
        console.log('上一轮次矩形数量:', Object.keys(prevRound || {}).length);
        
        if (!currentRound || !prevRound) {
          console.log('跳过：缺少轮次数据');
          continue;
        }
        
        // 遍历当前轮次的所有矩形
        Object.values(currentRound).forEach(currentRect => {
          if (!currentRect.parentNode) {
            console.log(`轮次${currentRect.roundNumber} 查询${currentRect.queryIndex + 1}: 无ParentNode`);
            return;
          }
          
          // 统一处理ParentNode格式（仅旧数据格式）
          let normalizedParentNode = currentRect.parentNode;
          if (!this.useNewDataFormat) {
            normalizedParentNode = currentRect.parentNode.startsWith('img_') 
              ? currentRect.parentNode 
              : `img_${currentRect.parentNode}`;
          }
          
          console.log(`轮次${currentRect.roundNumber} 查询${currentRect.queryIndex + 1}: ParentNode=${currentRect.parentNode} -> ${normalizedParentNode} (${this.useNewDataFormat ? '新格式' : '旧格式'})`);
          
          // 在上一轮次的所有矩形中查找包含当前ParentNode的矩形
          // 使用filter而不是find，检查所有可能的匹配
          const matchingRects = Object.values(prevRound).filter(prevRect => {
            // 获取上一轮次查询的RAG结果中的所有点ID
            const prevQuery = this.roundsData[prevRect.roundNumber]?.query_results[prevRect.queryIndex];
            if (!prevQuery || !prevQuery.rag_results) return false;
            
            // 检查上一轮次查询的RAG结果中是否包含当前ParentNode
          // 支持新旧数据格式的ID匹配
          const containsParentNode = prevQuery.rag_results.some(rag => {
            const ragId = rag.retrieval_result.id;
            
            // 如果是新数据格式，需要检查ID映射
            if (this.useNewDataFormat) {
              // 方法1：查找对应的新格式ID
              const newFormatPoint = this.mapPoints.find(p => 
                p.metadata && p.metadata.id === currentRect.parentNode
              );
              if (newFormatPoint) {
                return ragId === newFormatPoint.id;
              }
              
              // 方法2：去掉img_前缀后比对（处理ParentNode是数字的情况）
              if (ragId.startsWith('img_')) {
                const ragIdWithoutPrefix = ragId.replace('img_', '');
                return ragIdWithoutPrefix === currentRect.parentNode.toString();
              }
              
              // 方法3：直接比对（处理ParentNode是img_格式的情况）
              return ragId === currentRect.parentNode;
            }
            
            // 旧数据格式：统一处理ParentNode格式
            const normalizedParentNode = currentRect.parentNode.startsWith('img_') 
              ? currentRect.parentNode 
              : `img_${currentRect.parentNode}`;
            
            return ragId === normalizedParentNode;
          });
            
            if (containsParentNode) {
              console.log(`  找到匹配: 轮次${prevRect.roundNumber} 查询${prevRect.queryIndex + 1} 包含点ID=${normalizedParentNode}`);
            }
            return containsParentNode;
          });
          
          // 为所有匹配的矩形绘制连线
          if (matchingRects.length > 0) {
            matchingRects.forEach(matchingRect => {
              // 检查是否涉及空查询（如果当前矩形或匹配矩形是空查询）
              const involvesEmptyQuery = currentRect.isEmptyQuery || matchingRect.isEmptyQuery;
              
              // 如果不显示空查询且连线涉及空查询，则跳过
              if (!this.showEmptyQueries && involvesEmptyQuery) {
                console.log(`  跳过连线: 涉及空查询`);
                return;
              }
              
              console.log(`  绘制连线: 轮次${matchingRect.roundNumber}查询${matchingRect.queryIndex + 1} -> 轮次${currentRect.roundNumber}查询${currentRect.queryIndex + 1}`);
              this.drawBezierConnection(matchingRect, currentRect);
            });
            console.log(`  共找到 ${matchingRects.length} 个匹配的矩形`);
          } else {
            console.log(`  未找到包含点ID=${normalizedParentNode}的矩形`);
          }
        });
      }
      
      console.log('=== 连线分析完成 ===');
    },

    // 绘制贝塞尔曲线连线（右上角-左上角，右下角-左下角）
    drawBezierConnection(sourceRect, targetRect) {
      // 获取源矩形的起点（右上角和右下角）
      const sourcePoints = sourceRect.getConnectionStart();
      
      // 获取目标矩形的终点（左上角和左下角）
      const targetPoints = targetRect.getConnectionEnd();
      
      // 计算水平距离和方向
      const horizontalDistance = targetRect.x - sourceRect.x;
      const isRightDirection = horizontalDistance > 0;
      
      // 计算垂直距离
      const verticalDistance = Math.abs(targetRect.y - sourceRect.y);
      
      // 优化控制点计算，避免交叉
      const controlOffset = Math.min(horizontalDistance * 0.4, verticalDistance * 0.3);
      
      // 上边连线：从源矩形右上角到目标矩形左上角
      const topControlPoint1 = {
        x: sourcePoints.topRight.x + controlOffset * (isRightDirection ? 1 : -1),
        y: sourcePoints.topRight.y - verticalDistance * 0.2
      };
      
      const topControlPoint2 = {
        x: targetPoints.topLeft.x - controlOffset * (isRightDirection ? 1 : -1),
        y: targetPoints.topLeft.y - verticalDistance * 0.2
      };
      
      // 创建上边贝塞尔曲线路径
      const topPath = `M ${sourcePoints.topRight.x} ${sourcePoints.topRight.y} 
                      C ${topControlPoint1.x} ${topControlPoint1.y}, 
                        ${topControlPoint2.x} ${topControlPoint2.y}, 
                        ${targetPoints.topLeft.x} ${targetPoints.topLeft.y}`;
      
      // 绘制上边连线
      this.connectionGroup.append('path')
        .attr('d', topPath)
        .attr('fill', 'none')
        .attr('stroke', '#007bff')
        .attr('stroke-width', 2)
        .attr('stroke-opacity', 0.6)
        .attr('class', 'connection-line');
      
      // 下边连线：从源矩形右下角到目标矩形左下角
      const bottomControlPoint1 = {
        x: sourcePoints.bottomRight.x + controlOffset * (isRightDirection ? 1 : -1),
        y: sourcePoints.bottomRight.y + verticalDistance * 0.2
      };
      
      const bottomControlPoint2 = {
        x: targetPoints.bottomLeft.x - controlOffset * (isRightDirection ? 1 : -1),
        y: targetPoints.bottomLeft.y + verticalDistance * 0.2
      };
      
      const bottomPath = `M ${sourcePoints.bottomRight.x} ${sourcePoints.bottomRight.y} 
                         C ${bottomControlPoint1.x} ${bottomControlPoint1.y}, 
                           ${bottomControlPoint2.x} ${bottomControlPoint2.y}, 
                           ${targetPoints.bottomLeft.x} ${targetPoints.bottomLeft.y}`;
      
      this.connectionGroup.append('path')
        .attr('d', bottomPath)
        .attr('fill', 'none')
        .attr('stroke', '#28a745')
        .attr('stroke-width', 2)
        .attr('stroke-opacity', 0.6)
        .attr('class', 'connection-line');
    },

    // 显示策略卡片
    showStrategyCard(event, orchestratorPlan) {
      // 移除现有卡片
      this.hideStrategyCard();
      
      // 创建卡片容器
      const card = d3.select('body').append('div')
        .attr('class', 'strategy-card')
        .style('position', 'absolute')
        .style('background', 'white')
        .style('border', '1px solid #ccc')
        .style('border-radius', '8px')
        .style('padding', '15px')
        .style('box-shadow', '0 4px 12px rgba(0, 0, 0, 0.15)')
        .style('z-index', '1002')
        .style('max-width', '300px')
        .style('font-size', '12px')
        .style('line-height', '1.4');
      
      // 构建卡片内容
      let cardContent = '<div class="strategy-card-content">';
      
      // 标题
      cardContent += '<h4 style="margin: 0 0 10px 0; color: #333; border-bottom: 1px solid #eee; padding-bottom: 5px;">策略信息</h4>';
      
      // 基本信息
      cardContent += `<div style="margin-bottom: 8px;"><strong>动作:</strong> ${orchestratorPlan.action || 'N/A'}</div>`;
      cardContent += `<div style="margin-bottom: 8px;"><strong>工具:</strong> ${orchestratorPlan.tool_name || 'N/A'}</div>`;
      cardContent += `<div style="margin-bottom: 8px;"><strong>父节点:</strong> ${orchestratorPlan.ParentNode || 'N/A'}</div>`;
      
      // 参数信息
      if (orchestratorPlan.args && Object.keys(orchestratorPlan.args).length > 0) {
        cardContent += '<div style="margin-bottom: 8px;"><strong>参数:</strong></div>';
        cardContent += '<div style="background: #f8f9fa; padding: 5px; border-radius: 4px; margin-bottom: 8px;">';
        for (const [key, value] of Object.entries(orchestratorPlan.args)) {
          cardContent += `<div style="margin-left: 10px;">${key}: ${value || 'N/A'}</div>`;
        }
        cardContent += '</div>';
      }
      
      // 原因
      if (orchestratorPlan.reason) {
        cardContent += `<div style="margin-bottom: 8px;"><strong>原因:</strong></div>`;
        cardContent += `<div style="background: #f0f8ff; padding: 8px; border-radius: 4px; border-left: 3px solid #007bff;">${orchestratorPlan.reason}</div>`;
      }
      
      cardContent += '</div>';
      
      // 设置卡片内容
      card.html(cardContent);
      
      // 定位卡片（在鼠标位置显示）
      const cardWidth = 320;
      const cardHeight = card.node().getBoundingClientRect().height;
      
      let left = event.pageX + 10;
      let top = event.pageY;
      
      // 确保卡片不会超出屏幕边界
      if (left + cardWidth > window.innerWidth) {
        left = event.pageX - cardWidth - 10;
      }
      if (top + cardHeight > window.innerHeight) {
        top = window.innerHeight - cardHeight - 10;
      }
      
      card.style('left', left + 'px').style('top', top + 'px');
    },

    // 隐藏策略卡片
    hideStrategyCard() {
      d3.selectAll('.strategy-card').remove();
    },

    // 在小矩形内绘制地图画布
    drawQueryMap(queryGroup, query, rectX, rectY, rectHeight) {
      // 获取查询对应的RAG结果点数据
      const ragPoints = [];
      query.rag_results.forEach(rag => {
        const pointId = rag.retrieval_result.id;
        const point = this.mapPoints.find(p => p.id === pointId || p.id === `img_${pointId}`);
        if (point) {
          ragPoints.push({ 
            x: point.x, 
            y: point.y, 
            id: point.id,
            rag: rag,
            originalPoint: point
          });
        }
      });
      
      if (ragPoints.length === 0) return;
      
      // 计算地图画布的边界和缩放比例（使用完整数据库的范围）
      const mapMargin = 10;
      const mapWidth = this.roundWidth - 20 - mapMargin * 2;
      const mapHeight = rectHeight - 25; // 留出标签空间
      
      // // 使用RAG结果点的边界范围，避免过度压缩
      // const ragXValues = ragPoints.map(d => d.x);
      // const ragYValues = ragPoints.map(d => d.y);
      
      // 使用全局范围，统一所有小矩形的缩放比例，确保等高线形状一致
      const xExtent = this.globalXExtent;
      const yExtent = this.globalYExtent;
      
      // 添加一些边距，避免点太靠近边界
      const xRange = xExtent[1] - xExtent[0];
      const yRange = yExtent[1] - yExtent[0];
      const marginRatio = 0.1; // 10%边距
      
      const adjustedXExtent = [xExtent[0] - xRange * marginRatio, xExtent[1] + xRange * marginRatio];
      const adjustedYExtent = [yExtent[0] - yRange * marginRatio, yExtent[1] + yRange * marginRatio];
      
      // 创建缩放比例
      const xScale = d3.scaleLinear()
        .domain(adjustedXExtent)
        .range([mapMargin, mapWidth - mapMargin]);
      
      const yScale = d3.scaleLinear()
        .domain(adjustedYExtent)
        .range([mapHeight - mapMargin, mapMargin]);
      
      // 创建地图画布组
      const mapGroup = queryGroup.append('g')
        .attr('class', 'query-map')
        .attr('transform', `translate(${rectX + 10}, ${rectY + 20})`);
      
      // 绘制密度地图（蓝色蒙蒙的轮廓）- 使用完整数据库的点
      const scaledPoints = this.mapPoints.map(d => [xScale(d.x), yScale(d.y)]);
      
      const density = d3.contourDensity()
        .x(d => d[0])
        .y(d => d[1])
        .size([mapWidth, mapHeight])
        .bandwidth(8)  // 较小的带宽适应小尺寸
        .thresholds(8);  // 较少的层数
      
      const contours = density(scaledPoints);
      
      const color = d3.scaleSequential(d3.interpolateBlues)
        .domain([0, d3.max(contours, d => d.value)]);
      
      mapGroup.selectAll('path.density')
        .data(contours)
        .enter()
        .append('path')
        .attr('class', 'density')
        .attr('d', d3.geoPath())
        .attr('fill', d => color(d.value))            
        .attr('opacity', 0.4)  // 较低透明度避免遮挡
        .attr('stroke', 'none');
      
      // 绘制完整数据库的所有点作为底图（浅灰色小点）
      this.mapPoints.forEach(point => {
        mapGroup.append('circle')
          .attr('cx', xScale(point.x))
          .attr('cy', yScale(point.y))
          .attr('r', 0.5) // 更小的点避免遮挡密度地图
          .attr('fill', '#e0e0e0')
          .attr('opacity', 0.4);
      });
      
      // 绘制RAG结果圆点（突出显示）
      ragPoints.forEach(pointData => {
        const dot = mapGroup.append('circle')
          .attr('cx', xScale(pointData.x))
          .attr('cy', yScale(pointData.y))
          .attr('r', 3) // 增大点半径，突出显示
          .attr('fill', this.getDotColor(pointData.rag))
          .attr('stroke', '#fff')
          .attr('stroke-width', 0.5)
          .attr('class', 'rag-dot')
          .style('cursor', 'pointer');
        
        // 添加鼠标交互
        dot.on('mouseover', (event) => {
            d3.select(event.currentTarget).attr('r', 4.5);
            // 显示tooltip
            const tooltip = d3.select('body').append('div')
              .attr('class', 'tooltip')
              .style('position', 'absolute')
              .style('background', 'white')
              .style('padding', '5px')
              .style('border', '1px solid #ccc')
              .style('border-radius', '3px')
              .style('left', `${event.pageX + 10}px`)
              .style('top', `${event.pageY}px`);
            tooltip.html(`ID: ${pointData.rag.retrieval_result.id}<br>Score: ${pointData.rag.retrieval_result.score}`);
          })
          .on('mouseout', (event) => {
            d3.select(event.currentTarget).attr('r', 3);
            d3.selectAll('.tooltip').remove();
          })
          .on('click', () => {
            this.selectRagResult(pointData.rag);
          });
      });
    },

    // 切换空查询显示
    toggleEmptyQueries() {
      this.showEmptyQueries = !this.showEmptyQueries;
      if (this.roundsData.length > 0) {
        this.drawRiverChart();
      }
    },

    toggleDataFormat() {
      this.useNewDataFormat = !this.useNewDataFormat;
      // 重新加载地图数据并重绘图表
      if (this.roundsData.length > 0) {
        this.loadMapData().then(() => {
          this.drawRiverChart();
        });
      }
    },

    // 切换连线显示
    toggleConnections() {
      this.showConnections = !this.showConnections;
      if (this.roundsData.length > 0) {
        if (this.showConnections) {
          this.drawConnections();
        } else {
          if (this.connectionGroup) {
            this.connectionGroup.selectAll('*').remove();
          }
        }
      }
    },

    // 添加缩放行为
    addZoomBehavior(svg) {
      const container = svg.select('.river-container');
      
      const zoom = d3.zoom()
        .scaleExtent([0.5, 3])
        .on('zoom', (event) => {
          container.attr('transform', event.transform);
          // 连线也需要跟随缩放
          if (this.connectionGroup) {
            this.connectionGroup.attr('transform', event.transform);
          }
        });

      svg.call(zoom);

      // 初始缩放和位置
      const initialScale = 0.8;
      const initialX = (this.svgWidth - this.totalWidth * initialScale) / 2;
      const initialY = 50;
      
      svg.call(zoom.transform, d3.zoomIdentity.translate(initialX, initialY).scale(initialScale));
    },

    // 清除图表
    clearChart() {
      const svg = d3.select(this.$refs.svg);
      svg.selectAll('*').remove();
      this.roundsData = [];
    },

    // 切换标签显示
    toggleLabels() {
      this.showLabels = !this.showLabels;
      if (this.roundsData.length > 0) {
        this.drawRiverChart();
      }
    },

    // 处理窗口大小变化
    handleResize() {
      if (this.roundsData.length > 0) {
        this.drawRiverChart();
      }
    }
  },

  mounted() {
    // 初始加载数据
    this.loadAllRounds();
    window.addEventListener('resize', this.handleResize);
  },

  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
  }
};
</script>

<style scoped>
#river-chart {
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

.btn-quaternary {
  background-color: #6f42c1;
  color: white;
}

.btn-quaternary:hover {
  background-color: #5a359c;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(111, 66, 193, 0.3);
}

.btn-quinary {
  background-color: #fd7e14;
  color: white;
}

.btn-quinary:hover {
  background-color: #e36209;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(253, 126, 20, 0.3);
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

.rag-dot:hover {
  filter: brightness(1.2);
}

.connection-line {
  pointer-events: none;
}

.connection-line:hover {
  stroke-opacity: 0.9;
  stroke-width: 3;
}

.tooltip {
  background: white;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  pointer-events: none;
  z-index: 1001;
  font-size: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>