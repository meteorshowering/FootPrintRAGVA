// ===== riverGridLayout.js =====
import * as d3 from 'd3';

/**
 * 初始化默认网格状态
 */
export function createDefaultGridState() {
  return {
    rowHeights: {},
    columnWidths: {},
    rowOrder: [],
    resizing: null,
    hoveredCellKey: null,
    selectedCellKey: null,
    layoutMode: 'grid'
  };
}

/**
 * 确保网格尺寸
 */
export function ensureGridSizing(vm, allRounds) {
  const roundNumbers = allRounds.map(r => r.round_number);
  const maxQueryCount = Math.max(1, ...allRounds.map(r => Array.isArray(r.query_results) ? r.query_results.length : 0));

  if (!vm.gridState.columnWidths['label']) vm.gridState.columnWidths['label'] = 92;
  roundNumbers.forEach(roundNo => {
    if (!vm.gridState.columnWidths[`round-${roundNo}`]) vm.gridState.columnWidths[`round-${roundNo}`] = vm.strategyWidth;
  });

  if (!vm.gridState.rowHeights['header']) vm.gridState.rowHeights['header'] = 58;
  for (let i = 0; i < maxQueryCount; i++) {
    const key = `row-${i}`;
    if (!vm.gridState.rowHeights[key]) vm.gridState.rowHeights[key] = vm.strategyHeight + 24;
  }

  vm.gridState.rowOrder = Array.from({ length: maxQueryCount }, (_, i) => i);
}

/**
 * 构建列/行位置 metrics
 */
export function buildGridMetrics(vm, allRounds) {
  ensureGridSizing(vm, allRounds);

  const roundNumbers = allRounds.map(r => r.round_number);
  const maxQueryCount = Math.max(1, ...allRounds.map(r => Array.isArray(r.query_results) ? r.query_results.length : 0));

  const colPositions = {};
  const rowPositions = {};

  let x = vm.roundMargin;
  colPositions['label'] = { x, width: vm.gridState.columnWidths['label'] };
  x += vm.gridState.columnWidths['label'];

  roundNumbers.forEach(roundNo => {
    colPositions[`round-${roundNo}`] = { x, width: vm.gridState.columnWidths[`round-${roundNo}`] };
    x += vm.gridState.columnWidths[`round-${roundNo}`] + vm.strategyMargin;
  });

  let y = vm.roundMargin;
  rowPositions['header'] = { y, height: vm.gridState.rowHeights['header'] };
  y += vm.gridState.rowHeights['header'] + 10;

  for (let i = 0; i < maxQueryCount; i++) {
    rowPositions[`row-${i}`] = { y, height: vm.gridState.rowHeights[`row-${i}`] };
    y += vm.gridState.rowHeights[`row-${i}`] + vm.strategyMargin;
  }

  return {
    roundNumbers,
    maxQueryCount,
    colPositions,
    rowPositions,
    totalWidth: x + vm.roundMargin,
    totalHeight: y + vm.roundMargin
  };
}

/**
 * 获取单元格矩形
 */
export function getStrategyCellRect(vm, metrics, roundNumber, queryIndex) {
  const col = metrics.colPositions[`round-${roundNumber}`];
  const row = metrics.rowPositions[`row-${queryIndex}`];
  if (!col || !row) return null;
  const padX = 10;
  const padY = 6;
  return {
    x: col.x + padX,
    y: row.y + padY,
    width: Math.max(180, col.width - padX * 2),
    height: Math.max(140, row.height - padY * 2)
  };
}

/**
 * 获取列标题矩形
 */
export function getRoundHeaderRect(metrics, roundNumber) {
  const col = metrics.colPositions[`round-${roundNumber}`];
  const row = metrics.rowPositions['header'];
  if (!col || !row) return null;
  return { x: col.x, y: row.y, width: col.width, height: row.height };
}

/**
 * 获取行标签矩形
 */
export function getRowLabelRect(metrics, queryIndex) {
  const col = metrics.colPositions['label'];
  const row = metrics.rowPositions[`row-${queryIndex}`];
  if (!col || !row) return null;
  return { x: col.x, y: row.y, width: col.width, height: row.height };
}

/**
 * 列拖拽句柄
 */
export function getColumnResizeHandles(metrics) {
  const handles = [];
  Object.entries(metrics.colPositions).forEach(([key, col]) => {
    if (key === 'label') return;
    handles.push({
      key,
      x: col.x + col.width,
      y: metrics.rowPositions['header'].y,
      width: 8,
      height: Object.values(metrics.rowPositions).reduce((acc, r) => Math.max(acc, r.y + r.height), 0) - metrics.rowPositions['header'].y + 20
    });
  });
  return handles;
}

/**
 * 行拖拽句柄
 */
export function getRowResizeHandles(metrics) {
  const handles = [];
  Object.entries(metrics.rowPositions).forEach(([key, row]) => {
    if (key === 'header') return;
    handles.push({
      key,
      x: metrics.colPositions['label'].x,
      y: row.y + row.height,
      width: Object.values(metrics.colPositions).reduce((acc, c) => Math.max(acc, c.x + c.width), 0) - metrics.colPositions['label'].x + 20,
      height: 8
    });
  });
  return handles;
}

/**
 * Header 拖拽逻辑
 */
export function initHeaderDrag(vm, headerKey, svgRoot) {
  const svg = d3.select(svgRoot);
  const headerRect = getRoundHeaderRect(vm.metrics, headerKey);
  if (!headerRect) return;

  function getMouseSVGCoords(event) {
    const point = svg.node().createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    return point.matrixTransform(svg.node().getScreenCTM().inverse());
  }

  function onMouseDown(event) {
    const svgCoords = getMouseSVGCoords(event);
    const offsetX = svgCoords.x - headerRect.x;
    vm.draggingHeader = headerKey;

    function onMouseMove(e) {
      const coords = getMouseSVGCoords(e);
      let newX = coords.x - offsetX;
      const svgWidth = +svgRoot.getAttribute('width');
      newX = Math.max(0, Math.min(newX, svgWidth - headerRect.width));
      const colGroup = svg.select(`.column-group[data-key='${headerKey}']`);
      if (!colGroup.empty()) colGroup.attr('transform', `translate(${newX},0)`);
      vm.metrics.colPositions[`round-${headerKey}`].x = newX;
    }

    function onMouseUp() {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      vm.draggingHeader = null;
    }

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  }

  return onMouseDown;
}