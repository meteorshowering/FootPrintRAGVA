/**
 * 引用关系连线工具（增强版）
 * 支持：
 * 1. 新旧数据格式映射
 * 2. focus 节点高亮相关边
 * 3. 非 focus 边弱化
 */

import * as d3 from 'd3';
import axios from 'axios';

class GraphConnectionManager {
  constructor() {
    this.graphData = null;
    this.pointsData = null;
    this.connections = [];
    this.connectedNodes = new Set();
    this.focusNodeId = null;
  }

  async loadGraphData() {
    try {
      const response = await axios.get('/graph_state_20260129_114431.json');
      this.graphData = response.data;
      return this.graphData;
    } catch (error) {
      console.error('Failed to load graph data:', error);
      return null;
    }
  }

  async loadPointsData(useNewFormat = false) {
    try {
      const dataFile = useNewFormat
        ? '/scientific_rag_embeddings_2d.json'
        : '/scientific_rag_embeddings_2d_papercollection.json';

      const response = await axios.get(dataFile);
      this.pointsData = response.data;
      return this.pointsData;
    } catch (error) {
      console.error('Failed to load points data:', error);
      return null;
    }
  }

  analyzeConnections(useNewFormat = false) {
    if (!this.graphData || !this.pointsData) {
      console.error('Data not loaded yet');
      return [];
    }

    this.connections = [];
    this.connectedNodes.clear();

    const idMapping = {};
    if (useNewFormat) {
      this.pointsData.forEach(point => {
        if (point.metadata && point.metadata.id) {
          idMapping[point.metadata.id] = point.id;
        }
      });
    }

    Object.values(this.graphData.nodes).forEach(node => {
      const nodeId = node.id;
      const childrenIds = node.children_ids || [];

      if (childrenIds.length > 0) {
        const sourceId = useNewFormat ? (idMapping[nodeId] || nodeId) : nodeId;
        this.connectedNodes.add(sourceId);

        childrenIds.forEach(childId => {
          const targetId = useNewFormat ? (idMapping[childId] || childId) : childId;
          this.connectedNodes.add(targetId);

          this.connections.push({
            source: sourceId,
            target: targetId,
            type: 'reference'
          });
        });
      }
    });

    return this.connections;
  }

  getNodeCoordinates(nodeId) {
    if (!this.pointsData) return null;

    const point = this.pointsData.find(p => p.id === nodeId);
    if (!point) return null;

    if (point.coordinates_2d && Array.isArray(point.coordinates_2d) && point.coordinates_2d.length >= 2) {
      return {
        x: point.coordinates_2d[0],
        y: point.coordinates_2d[1],
        umap_id: point.umap_id || 0
      };
    }

    if (point.x !== undefined && point.y !== undefined) {
      return {
        x: point.x,
        y: point.y,
        umap_id: point.umap_id || 0
      };
    }

    return null;
  }

  isNodeConnected(nodeId) {
    return this.connectedNodes.has(nodeId);
  }

  setFocusNode(nodeId) {
    this.focusNodeId = nodeId || null;
  }

  clearFocusNode() {
    this.focusNodeId = null;
  }

  isConnectionRelatedToFocus(connection) {
    if (!this.focusNodeId) return false;
    return connection.source === this.focusNodeId || connection.target === this.focusNodeId;
  }

  drawConnections(svgElement, xScale, yScale) {
    if (!this.connections.length) return;

    const svg = d3.select(svgElement);
    const contentGroup = svg.select('.content-group');
    contentGroup.selectAll('.connections').remove();

    const connectionsGroup = contentGroup.append('g').attr('class', 'connections');

    this.connections.forEach(connection => {
      const sourceCoords = this.getNodeCoordinates(connection.source);
      const targetCoords = this.getNodeCoordinates(connection.target);

      if (!sourceCoords || !targetCoords) return;

      const related = this.isConnectionRelatedToFocus(connection);

      connectionsGroup.append('line')
        .attr('x1', xScale(sourceCoords.x))
        .attr('y1', yScale(sourceCoords.y))
        .attr('x2', xScale(targetCoords.x))
        .attr('y2', yScale(targetCoords.y))
        .attr('stroke', related ? 'rgba(14,165,233,0.9)' : 'rgba(148,163,184,0.28)')
        .attr('stroke-width', related ? 2.2 : 1.1)
        .attr('stroke-dasharray', related ? null : '3,3')
        .attr('opacity', related ? 1 : 0.75);

      if (related) {
        connectionsGroup.append('circle')
          .attr('cx', xScale(targetCoords.x))
          .attr('cy', yScale(targetCoords.y))
          .attr('r', 3.4)
          .attr('fill', '#0ea5e9')
          .attr('opacity', 0.95);
      }
    });
  }

  updateNodeColors(svgElement) {
    const svg = d3.select(svgElement);
    const contentGroup = svg.select('.content-group');

    contentGroup.selectAll('circle')
      .attr('fill', d => {
        if (!d || !d.id) return 'blue';
        if (this.focusNodeId && d.id === this.focusNodeId) return '#0ea5e9';
        if (this.connectedNodes.has(d.id)) return '#ff6b6b';
        return 'blue';
      })
      .attr('stroke', d => {
        if (!d || !d.id) return 'white';
        if (this.focusNodeId && d.id === this.focusNodeId) return '#0369a1';
        return 'white';
      })
      .attr('stroke-width', d => {
        if (!d || !d.id) return 1;
        return this.focusNodeId && d.id === this.focusNodeId ? 2.2 : 1;
      });
  }

  async initializeAndDraw(svgElement, xScale, yScale, useNewFormat = false, focusNodeId = null) {
    this.setFocusNode(focusNodeId);

    await this.loadGraphData();
    await this.loadPointsData(useNewFormat);

    this.analyzeConnections(useNewFormat);
    this.drawConnections(svgElement, xScale, yScale);
    this.updateNodeColors(svgElement);
  }

  clearConnections(svgElement) {
    const svg = d3.select(svgElement);
    const contentGroup = svg.select('.content-group');

    contentGroup.selectAll('.connections').remove();
    this.clearFocusNode();

    contentGroup.selectAll('circle')
      .attr('fill', 'blue')
      .attr('stroke', 'white')
      .attr('stroke-width', 1);
  }
}

export const graphConnectionManager = new GraphConnectionManager();
export default GraphConnectionManager;