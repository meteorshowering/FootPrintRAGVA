<template>
  <div id="experiment-dashboard">
    <div class="dashboard-header">
      <h1>实验数据可视化面板</h1>
      <div class="controls">
        <button @click="loadData" class="btn btn-primary">加载数据</button>
        <select v-model="selectedFile" @change="loadData" class="file-selector">
          <option value="experiment_results_20260204_181124.json">最新数据 (20260204 181124)</option>
          <option value="experiment_results_20260204_122406.json">历史数据 (20260204 122406)</option>
          <option value="experiment_results_20260203_173057.json">历史数据 (20260203)</option>
          <option value="experiment_results_20260129_114431.json">历史数据 (20260129)</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <p>正在加载数据...</p>
    </div>

    <div v-else-if="experimentData" class="dashboard-content">
      <!-- 实验概览 -->
      <section class="overview-section">
        <h2>实验概览</h2>
        <div class="overview-cards">
          <div class="card">
            <div class="card-icon">🎯</div>
            <div class="card-content">
              <div class="card-label">实验目标</div>
              <div class="card-value">{{ experimentData.root_goal }}</div>
            </div>
          </div>
          <div class="card">
            <div class="card-icon">🔄</div>
            <div class="card-content">
              <div class="card-label">总轮次</div>
              <div class="card-value">{{ stats.totalRounds }}</div>
            </div>
          </div>
          <div class="card">
            <div class="card-icon">🔍</div>
            <div class="card-content">
              <div class="card-label">总查询数</div>
              <div class="card-value">{{ stats.totalQueries }}</div>
            </div>
          </div>
          <div class="card">
            <div class="card-icon">📊</div>
            <div class="card-content">
              <div class="card-label">总结果数</div>
              <div class="card-value">{{ stats.totalResults }}</div>
            </div>
          </div>
          <div class="card">
            <div class="card-icon">⭐</div>
            <div class="card-content">
              <div class="card-label">平均分数</div>
              <div class="card-value">{{ stats.avgScore.toFixed(3) }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 图表区域 -->
      <div class="charts-grid">
        <!-- 策略使用统计 -->
        <section class="chart-section">
          <h3>策略使用统计</h3>
          <div ref="strategyChart" class="chart-container"></div>
        </section>

        <!-- 检索分数分布 -->
        <section class="chart-section">
          <h3>检索分数分布</h3>
          <div ref="scoreChart" class="chart-container"></div>
        </section>

        <!-- 轮次演进趋势 -->
        <section class="chart-section full-width">
          <h3>轮次演进趋势</h3>
          <div ref="roundTrendChart" class="chart-container"></div>
        </section>

        <!-- 评估分数分析 -->
        <section class="chart-section">
          <h3>相关性分数分布</h3>
          <div ref="relevanceChart" class="chart-container"></div>
        </section>

        <section class="chart-section">
          <h3>可信度分数分布</h3>
          <div ref="credibilityChart" class="chart-container"></div>
        </section>

        <!-- 策略效果对比 -->
        <section class="chart-section full-width">
          <h3>策略效果对比（平均分数）</h3>
          <div ref="strategyEffectChart" class="chart-container"></div>
        </section>
      </div>

      <!-- 详细数据表格 -->
      <section class="table-section">
        <h2>轮次详情</h2>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>轮次</th>
                <th>查询数</th>
                <th>结果数</th>
                <th>平均分数</th>
                <th>主要策略</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="round in experimentData.iterations" :key="round.round_number">
                <td>{{ round.round_number }}</td>
                <td>{{ round.query_results.length }}</td>
                <td>{{ getRoundTotalResults(round) }}</td>
                <td>{{ getRoundAvgScore(round).toFixed(3) }}</td>
                <td>{{ getRoundMainStrategy(round) }}</td>
                <td>
                  <button @click="viewRoundDetail(round)" class="btn-small">查看详情</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <!-- 轮次详情模态框 -->
    <div v-if="selectedRound" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>轮次 {{ selectedRound.round_number }} 详情</h2>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div v-for="(query, idx) in selectedRound.query_results" :key="idx" class="query-detail">
            <h4>查询 {{ idx + 1 }}</h4>
            <div class="query-info">
              <p><strong>策略:</strong> {{ query.orchestrator_plan.tool_name }}</p>
              <p><strong>原因:</strong> {{ query.orchestrator_plan.reason }}</p>
              <p><strong>结果数:</strong> {{ query.rag_results.length }}</p>
              <p><strong>平均分数:</strong> {{ getQueryAvgScore(query).toFixed(3) }}</p>
            </div>
            <div v-if="query.orchestrator_plan.plansummary" class="summary-box">
              <strong>策略总结:</strong>
              <div class="summary-content" v-html="formatSummary(query.orchestrator_plan.plansummary)"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3';

export default {
  name: 'ExperimentDashboard',
  data() {
    return {
      experimentData: null,
      loading: false,
      selectedFile: 'experiment_results_20260204_181124.json',
      selectedRound: null,
      stats: {
        totalRounds: 0,
        totalQueries: 0,
        totalResults: 0,
        avgScore: 0
      }
    };
  },
  methods: {
    async loadData() {
      this.loading = true;
      try {
        const response = await fetch(`/${this.selectedFile}`);
        this.experimentData = await response.json();
        this.calculateStats();
        this.$nextTick(() => {
          this.drawAllCharts();
        });
      } catch (error) {
        console.error('加载数据失败:', error);
        alert('加载数据失败，请检查文件是否存在');
      } finally {
        this.loading = false;
      }
    },

    calculateStats() {
      if (!this.experimentData || !this.experimentData.iterations) return;

      this.stats.totalRounds = this.experimentData.iterations.length;
      this.stats.totalQueries = this.experimentData.iterations.reduce(
        (sum, round) => sum + round.query_results.length, 0
      );
      
      let totalResults = 0;
      let totalScore = 0;
      let scoreCount = 0;

      this.experimentData.iterations.forEach(round => {
        round.query_results.forEach(query => {
          totalResults += query.rag_results.length;
          query.rag_results.forEach(rag => {
            if (rag.retrieval_result && rag.retrieval_result.score !== undefined) {
              totalScore += rag.retrieval_result.score;
              scoreCount++;
            }
          });
        });
      });

      this.stats.totalResults = totalResults;
      this.stats.avgScore = scoreCount > 0 ? totalScore / scoreCount : 0;
    },

    drawAllCharts() {
      this.drawStrategyChart();
      this.drawScoreChart();
      this.drawRoundTrendChart();
      this.drawRelevanceChart();
      this.drawCredibilityChart();
      this.drawStrategyEffectChart();
    },

    drawStrategyChart() {
      const container = d3.select(this.$refs.strategyChart);
      container.selectAll('*').remove();

      if (!this.experimentData) return;

      // 统计策略使用次数
      const strategyCount = {};
      this.experimentData.iterations.forEach(round => {
        round.query_results.forEach(query => {
          const tool = query.orchestrator_plan.tool_name || 'unknown';
          strategyCount[tool] = (strategyCount[tool] || 0) + 1;
        });
      });

      const data = Object.entries(strategyCount).map(([name, value]) => ({ name, value }));

      const width = 400;
      const height = 300;
      const margin = { top: 20, right: 20, bottom: 60, left: 60 };

      const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);

      const xScale = d3.scaleBand()
        .domain(data.map(d => d.name))
        .range([margin.left, width - margin.right])
        .padding(0.2);

      const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.value)])
        .nice()
        .range([height - margin.bottom, margin.top]);

      // 绘制柱状图
      svg.selectAll('rect')
        .data(data)
        .enter()
        .append('rect')
        .attr('x', d => xScale(d.name))
        .attr('y', d => yScale(d.value))
        .attr('width', xScale.bandwidth())
        .attr('height', d => height - margin.bottom - yScale(d.value))
        .attr('fill', '#4A90E2')
        .attr('rx', 4);

      // 添加数值标签
      svg.selectAll('text.value')
        .data(data)
        .enter()
        .append('text')
        .attr('class', 'value')
        .attr('x', d => xScale(d.name) + xScale.bandwidth() / 2)
        .attr('y', d => yScale(d.value) - 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', '12px')
        .attr('fill', '#333')
        .text(d => d.value);

      // 添加坐标轴
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

    drawScoreChart() {
      const container = d3.select(this.$refs.scoreChart);
      container.selectAll('*').remove();

      if (!this.experimentData) return;

      // 收集所有分数
      const scores = [];
      this.experimentData.iterations.forEach(round => {
        round.query_results.forEach(query => {
          query.rag_results.forEach(rag => {
            if (rag.retrieval_result && rag.retrieval_result.score !== undefined) {
              scores.push(rag.retrieval_result.score);
            }
          });
        });
      });

      if (scores.length === 0) return;

      const width = 400;
      const height = 300;
      const margin = { top: 20, right: 20, bottom: 40, left: 40 };

      const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);

      // 创建直方图
      const bins = d3.histogram()
        .domain(d3.extent(scores))
        .thresholds(20)(scores);

      const xScale = d3.scaleLinear()
        .domain(d3.extent(scores))
        .range([margin.left, width - margin.right]);

      const yScale = d3.scaleLinear()
        .domain([0, d3.max(bins, d => d.length)])
        .nice()
        .range([height - margin.bottom, margin.top]);

      // 绘制柱状图
      svg.selectAll('rect')
        .data(bins)
        .enter()
        .append('rect')
        .attr('x', d => xScale(d.x0))
        .attr('width', d => xScale(d.x1) - xScale(d.x0) - 1)
        .attr('y', d => yScale(d.length))
        .attr('height', d => height - margin.bottom - yScale(d.length))
        .attr('fill', '#50C878')
        .attr('rx', 2);

      // 添加坐标轴
      svg.append('g')
        .attr('transform', `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(xScale));

      svg.append('g')
        .attr('transform', `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(yScale));

      svg.append('text')
        .attr('x', width / 2)
        .attr('y', height - 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', '12px')
        .text('分数');
    },

    drawRoundTrendChart() {
      const container = d3.select(this.$refs.roundTrendChart);
      container.selectAll('*').remove();

      if (!this.experimentData) return;

      const data = this.experimentData.iterations.map(round => ({
        round: round.round_number,
        queries: round.query_results.length,
        results: this.getRoundTotalResults(round),
        avgScore: this.getRoundAvgScore(round)
      }));

      const width = 800;
      const height = 300;
      const margin = { top: 20, right: 80, bottom: 40, left: 60 };

      const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);

      const xScale = d3.scaleLinear()
        .domain(d3.extent(data, d => d.round))
        .range([margin.left, width - margin.right]);

      const yScale1 = d3.scaleLinear()
        .domain([0, d3.max(data, d => Math.max(d.queries, d.results))])
        .nice()
        .range([height - margin.bottom, margin.top]);

      const yScale2 = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.avgScore)])
        .nice()
        .range([height - margin.bottom, margin.top]);

      // 绘制查询数折线
      const line1 = d3.line()
        .x(d => xScale(d.round))
        .y(d => yScale1(d.queries))
        .curve(d3.curveMonotoneX);

      svg.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', '#4A90E2')
        .attr('stroke-width', 2)
        .attr('d', line1);

      // 绘制结果数折线
      const line2 = d3.line()
        .x(d => xScale(d.round))
        .y(d => yScale1(d.results))
        .curve(d3.curveMonotoneX);

      svg.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', '#50C878')
        .attr('stroke-width', 2)
        .attr('d', line2);

      // 绘制平均分数折线（使用右侧Y轴）
      const line3 = d3.line()
        .x(d => xScale(d.round))
        .y(d => yScale2(d.avgScore))
        .curve(d3.curveMonotoneX);

      svg.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', '#FF6B6B')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5')
        .attr('d', line3);

      // 添加数据点
      svg.selectAll('circle.queries')
        .data(data)
        .enter()
        .append('circle')
        .attr('class', 'queries')
        .attr('cx', d => xScale(d.round))
        .attr('cy', d => yScale1(d.queries))
        .attr('r', 4)
        .attr('fill', '#4A90E2');

      svg.selectAll('circle.results')
        .data(data)
        .enter()
        .append('circle')
        .attr('class', 'results')
        .attr('cx', d => xScale(d.round))
        .attr('cy', d => yScale1(d.results))
        .attr('r', 4)
        .attr('fill', '#50C878');

      // 添加坐标轴
      svg.append('g')
        .attr('transform', `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(xScale));

      svg.append('g')
        .attr('transform', `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(yScale1));

      svg.append('g')
        .attr('transform', `translate(${width - margin.right}, 0)`)
        .call(d3.axisRight(yScale2));

      // 添加图例
      const legend = svg.append('g')
        .attr('transform', `translate(${width - margin.right - 70}, ${margin.top})`);

      legend.append('line')
        .attr('x1', 0)
        .attr('x2', 20)
        .attr('y1', 0)
        .attr('y2', 0)
        .attr('stroke', '#4A90E2')
        .attr('stroke-width', 2);
      legend.append('text')
        .attr('x', 25)
        .attr('y', 4)
        .attr('font-size', '12px')
        .text('查询数');

      legend.append('line')
        .attr('x1', 0)
        .attr('x2', 20)
        .attr('y1', 20)
        .attr('y2', 20)
        .attr('stroke', '#50C878')
        .attr('stroke-width', 2);
      legend.append('text')
        .attr('x', 25)
        .attr('y', 24)
        .attr('font-size', '12px')
        .text('结果数');

      legend.append('line')
        .attr('x1', 0)
        .attr('x2', 20)
        .attr('y1', 40)
        .attr('y2', 40)
        .attr('stroke', '#FF6B6B')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5');
      legend.append('text')
        .attr('x', 25)
        .attr('y', 44)
        .attr('font-size', '12px')
        .text('平均分数');
    },

    drawRelevanceChart() {
      const container = d3.select(this.$refs.relevanceChart);
      container.selectAll('*').remove();

      if (!this.experimentData) return;

      const scores = [];
      this.experimentData.iterations.forEach(round => {
        round.query_results.forEach(query => {
          query.rag_results.forEach(rag => {
            if (rag.evaluation && rag.evaluation.scores && rag.evaluation.scores.relevance !== undefined) {
              scores.push(rag.evaluation.scores.relevance);
            }
          });
        });
      });

      if (scores.length === 0) return;

      this.drawHistogram(container, scores, '相关性分数', '#FF6B6B');
    },

    drawCredibilityChart() {
      const container = d3.select(this.$refs.credibilityChart);
      container.selectAll('*').remove();

      if (!this.experimentData) return;

      const scores = [];
      this.experimentData.iterations.forEach(round => {
        round.query_results.forEach(query => {
          query.rag_results.forEach(rag => {
            if (rag.evaluation && rag.evaluation.scores && rag.evaluation.scores.credibility !== undefined) {
              scores.push(rag.evaluation.scores.credibility);
            }
          });
        });
      });

      if (scores.length === 0) return;

      this.drawHistogram(container, scores, '可信度分数', '#9B59B6');
    },

    drawHistogram(container, scores, label, color) {
      const width = 400;
      const height = 300;
      const margin = { top: 20, right: 20, bottom: 40, left: 40 };

      const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);

      const bins = d3.histogram()
        .domain(d3.extent(scores))
        .thresholds(10)(scores);

      const xScale = d3.scaleLinear()
        .domain(d3.extent(scores))
        .range([margin.left, width - margin.right]);

      const yScale = d3.scaleLinear()
        .domain([0, d3.max(bins, d => d.length)])
        .nice()
        .range([height - margin.bottom, margin.top]);

      svg.selectAll('rect')
        .data(bins)
        .enter()
        .append('rect')
        .attr('x', d => xScale(d.x0))
        .attr('width', d => xScale(d.x1) - xScale(d.x0) - 1)
        .attr('y', d => yScale(d.length))
        .attr('height', d => height - margin.bottom - yScale(d.length))
        .attr('fill', color)
        .attr('rx', 2);

      svg.append('g')
        .attr('transform', `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(xScale));

      svg.append('g')
        .attr('transform', `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(yScale));

      svg.append('text')
        .attr('x', width / 2)
        .attr('y', height - 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', '12px')
        .text(label);
    },

    drawStrategyEffectChart() {
      const container = d3.select(this.$refs.strategyEffectChart);
      container.selectAll('*').remove();

      if (!this.experimentData) return;

      // 统计每个策略的平均分数
      const strategyScores = {};
      const strategyCounts = {};

      this.experimentData.iterations.forEach(round => {
        round.query_results.forEach(query => {
          const tool = query.orchestrator_plan.tool_name || 'unknown';
          query.rag_results.forEach(rag => {
            if (rag.retrieval_result && rag.retrieval_result.score !== undefined) {
              if (!strategyScores[tool]) {
                strategyScores[tool] = 0;
                strategyCounts[tool] = 0;
              }
              strategyScores[tool] += rag.retrieval_result.score;
              strategyCounts[tool]++;
            }
          });
        });
      });

      const data = Object.keys(strategyScores).map(tool => ({
        name: tool,
        avgScore: strategyScores[tool] / strategyCounts[tool],
        count: strategyCounts[tool]
      })).sort((a, b) => b.avgScore - a.avgScore);

      const width = 800;
      const height = 300;
      const margin = { top: 20, right: 20, bottom: 60, left: 60 };

      const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);

      const xScale = d3.scaleBand()
        .domain(data.map(d => d.name))
        .range([margin.left, width - margin.right])
        .padding(0.2);

      const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.avgScore)])
        .nice()
        .range([height - margin.bottom, margin.top]);

      svg.selectAll('rect')
        .data(data)
        .enter()
        .append('rect')
        .attr('x', d => xScale(d.name))
        .attr('y', d => yScale(d.avgScore))
        .attr('width', xScale.bandwidth())
        .attr('height', d => height - margin.bottom - yScale(d.avgScore))
        .attr('fill', '#FFA500')
        .attr('rx', 4);

      svg.selectAll('text.value')
        .data(data)
        .enter()
        .append('text')
        .attr('class', 'value')
        .attr('x', d => xScale(d.name) + xScale.bandwidth() / 2)
        .attr('y', d => yScale(d.avgScore) - 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', '11px')
        .attr('fill', '#333')
        .text(d => d.avgScore.toFixed(3));

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

    getRoundTotalResults(round) {
      return round.query_results.reduce((sum, query) => sum + query.rag_results.length, 0);
    },

    getRoundAvgScore(round) {
      let totalScore = 0;
      let count = 0;
      round.query_results.forEach(query => {
        query.rag_results.forEach(rag => {
          if (rag.retrieval_result && rag.retrieval_result.score !== undefined) {
            totalScore += rag.retrieval_result.score;
            count++;
          }
        });
      });
      return count > 0 ? totalScore / count : 0;
    },

    getRoundMainStrategy(round) {
      const strategies = {};
      round.query_results.forEach(query => {
        const tool = query.orchestrator_plan.tool_name || 'unknown';
        strategies[tool] = (strategies[tool] || 0) + 1;
      });
      return Object.entries(strategies).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A';
    },

    getQueryAvgScore(query) {
      if (query.rag_results.length === 0) return 0;
      const scores = query.rag_results
        .map(rag => rag.retrieval_result?.score)
        .filter(score => score !== undefined);
      return scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
    },

    viewRoundDetail(round) {
      this.selectedRound = round;
    },

    closeModal() {
      this.selectedRound = null;
    },

    formatSummary(summary) {
      if (!summary) return '';
      // 简单的Markdown转HTML（基础处理）
      return summary
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/#{3}\s+(.*?)(<br>|$)/g, '<h3>$1</h3>')
        .replace(/#{2}\s+(.*?)(<br>|$)/g, '<h2>$1</h2>')
        .replace(/\|(.*?)\|/g, '<code>$1</code>');
    }
  },

  mounted() {
    this.loadData();
    window.addEventListener('resize', () => {
      if (this.experimentData) {
        this.$nextTick(() => {
          this.drawAllCharts();
        });
      }
    });
  }
};
</script>

<style scoped>
#experiment-dashboard {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dashboard-header h1 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #4A90E2;
  color: white;
}

.btn-primary:hover {
  background-color: #357ABD;
}

.file-selector {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.loading {
  text-align: center;
  padding: 50px;
  font-size: 18px;
  color: #666;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.overview-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.overview-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card:nth-child(1) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.card:nth-child(2) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.card:nth-child(3) {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.card:nth-child(4) {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.card:nth-child(5) {
  background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
}

.card-icon {
  font-size: 36px;
}

.card-content {
  flex: 1;
}

.card-label {
  font-size: 12px;
  opacity: 0.9;
  margin-bottom: 5px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart-section.full-width {
  grid-column: 1 / -1;
}

.chart-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
  font-size: 18px;
}

.chart-container {
  width: 100%;
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.table-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.table-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8f9fa;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  font-weight: 600;
  color: #333;
}

tbody tr:hover {
  background: #f8f9fa;
}

.btn-small {
  padding: 6px 12px;
  background: #4A90E2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-small:hover {
  background: #357ABD;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 800px;
  max-height: 80vh;
  width: 90%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #ddd;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 32px;
  cursor: pointer;
  color: #999;
  line-height: 1;
  padding: 0;
  width: 32px;
  height: 32px;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.query-detail {
  margin-bottom: 30px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
}

.query-detail h4 {
  margin-top: 0;
  color: #333;
}

.query-info {
  margin-bottom: 15px;
}

.query-info p {
  margin: 8px 0;
  color: #666;
}

.summary-box {
  margin-top: 15px;
  padding: 15px;
  background: white;
  border-left: 4px solid #4A90E2;
  border-radius: 4px;
}

.summary-content {
  margin-top: 10px;
  color: #555;
  line-height: 1.6;
  font-size: 14px;
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .chart-section.full-width {
    grid-column: 1;
  }

  .dashboard-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
}
</style>