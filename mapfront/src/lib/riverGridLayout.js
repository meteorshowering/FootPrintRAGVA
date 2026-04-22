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
/** 列唯一键：多问题模式下为 __gridColKey，否则为 round_number */
export function gridColumnKey(r) {
  if (r && r.__gridColKey) return String(r.__gridColKey);
  return `r${r.round_number}`;
}

function _queryResultPlanKey(qr) {
  const p = qr && qr.orchestrator_plan;
  if (!p) return '';
  return `${p.tool_name || ''}|${JSON.stringify(p.args || {})}`;
}

function _mergeQueryResultsInRound(existing, incoming) {
  const map = new Map();
  (existing || []).forEach((qr) => map.set(_queryResultPlanKey(qr), qr));
  (incoming || []).forEach((qr) => {
    const k = _queryResultPlanKey(qr);
    const prev = map.get(k);
    if (!prev) {
      map.set(k, qr);
      return;
    }
    const pr = (prev.rag_results || []).length;
    const ir = (qr.rag_results || []).length;
    map.set(k, ir >= pr ? qr : prev);
  });
  return Array.from(map.values());
}

/**
 * 同一列键（sessionId__round_number）只保留一条 round，合并 query_results。
 * 避免重复列键导致 colPositions 覆盖、格子重叠或挤掉上一行。
 */
export function dedupeRoundsByGridColumnKey(rounds) {
  const map = new Map();
  (rounds || []).forEach((r) => {
    if (!r || r.round_number === undefined) return;
    const ck = gridColumnKey(r);
    if (!map.has(ck)) {
      map.set(ck, { ...r, query_results: [...(r.query_results || [])] });
    } else {
      const cur = map.get(ck);
      cur.query_results = _mergeQueryResultsInRound(cur.query_results || [], r.query_results || []);
    }
  });
  return Array.from(map.values()).sort((a, b) => {
    if (String(a._sessionId) !== String(b._sessionId)) {
      return String(a._sessionId).localeCompare(String(b._sessionId));
    }
    return a.round_number - b.round_number;
  });
}

/** 按会话分组并保持与 getAllRounds 首次出现顺序一致；每个会话独立一条「横带」，多会话上下排列 */
export function sessionGroupsInOrder(allRounds) {
  const bySid = new Map();
  (allRounds || []).forEach((r) => {
    const sid = r._sessionId || 'default';
    if (!bySid.has(sid)) bySid.set(sid, []);
    bySid.get(sid).push(r);
  });
  const order = [];
  const seen = new Set();
  (allRounds || []).forEach((r) => {
    const sid = r._sessionId || 'default';
    if (!seen.has(sid)) {
      seen.add(sid);
      order.push(sid);
    }
  });
  return order.map((sid) => ({
    sessionId: sid,
    rounds: (bySid.get(sid) || []).sort((a, b) => a.round_number - b.round_number)
  }));
}

/** 会话条带之间的竖向间距（第二题起大追问后紧挨上一题，不再重复表头） */
const SESSION_STRIP_GAP = 12;

/**
 * 策略格相对其网格行的上内边距（与 getStrategyCellRect 一致）。
 * 左侧 Question 竖条顶 = 首行 y + 本值，与策略小矩形外框顶对齐；Round 表头整体下移同值、高度减去同值，底边不变、不挤占策略行。
 */
export const STRATEGY_CELL_PAD_Y = 6;

/** Question 竖条右缘与策略列之间的视觉留白（仅缩窄竖条宽度，不改变 round 列 x / 小矩形位置） */
const LABEL_STRIP_RIGHT_INSET = 12;

export function ensureGridSizing(vm, allRounds, maxQueryOverride) {
  const colKeys = allRounds.map((r) => gridColumnKey(r));
  const fromData = Math.max(
    1,
    ...allRounds.map((r) => (Array.isArray(r.query_results) ? r.query_results.length : 0))
  );
  const maxQueryCount =
    typeof maxQueryOverride === 'number' && maxQueryOverride >= 1 ? maxQueryOverride : fromData;

  if (!vm.gridState.columnWidths['label']) vm.gridState.columnWidths['label'] = 92;
  colKeys.forEach((ck) => {
    if (!vm.gridState.columnWidths[`round-${ck}`]) vm.gridState.columnWidths[`round-${ck}`] = vm.strategyWidth;
  });

  if (!vm.gridState.rowHeights['header']) vm.gridState.rowHeights['header'] = 58;
  for (let i = 0; i < maxQueryCount; i++) {
    const key = `row-${i}`;
    if (!vm.gridState.rowHeights[key]) vm.gridState.rowHeights[key] = vm.strategyHeight + 24;
  }

  vm.gridState.rowOrder = Array.from({ length: maxQueryCount }, (_, i) => i);
}

/**
 * 构建列/行位置 metrics（按 session 分条带纵向堆叠：新会话整带在下方，不再向右延伸）
 */
export function buildGridMetrics(vm, allRounds) {
  let maxQueryCount = Math.max(
    1,
    ...allRounds.map((r) => (Array.isArray(r.query_results) ? r.query_results.length : 0))
  );
  const prev = vm.gridMetrics && vm.gridMetrics.maxQueryCount;
  if (typeof prev === 'number' && prev > maxQueryCount && (allRounds || []).length > 0) {
    maxQueryCount = prev;
  }
  ensureGridSizing(vm, allRounds, maxQueryCount);

  const rm = vm.roundMargin != null ? vm.roundMargin : 16;
  const sm = vm.strategyMargin != null ? vm.strategyMargin : 10;
  const labelW = vm.gridState.columnWidths.label || 92;
  const headerH = vm.gridState.rowHeights.header || 58;

  const groups = sessionGroupsInOrder(allRounds);
  const colPositions = {};
  const strips = [];
  const roundNumbers = [];

  colPositions.label = { x: rm, width: labelW };
  const xAfterLabel = colPositions.label.x + colPositions.label.width + sm;

  let yCursor = rm;
  let maxX = colPositions.label.x + colPositions.label.width;

  for (let gi = 0; gi < groups.length; gi += 1) {
    const g = groups[gi];
    const rounds = g.rounds;
    if (!rounds.length) continue;

    const stripTop = yCursor;
    // 仅第一条带占用表头行；后续会话直接接在上一带策略行下方，共享最顶部那一行 Round 表头
    if (gi === 0) {
      yCursor += headerH + 10;
    }

    const rowYs = [];
    for (let i = 0; i < maxQueryCount; i += 1) {
      const rh = vm.gridState.rowHeights[`row-${i}`] || vm.strategyHeight + 24;
      rowYs.push({ y: yCursor, height: rh });
      yCursor += rh + sm;
    }

    const stripBottom = yCursor;
    const stripIndex = strips.length;
    const headerYForStrip =
      stripIndex === 0 ? stripTop + STRATEGY_CELL_PAD_Y : strips[0].headerY;
    const headerHForStrip =
      stripIndex === 0 ? headerH - STRATEGY_CELL_PAD_Y : strips[0].headerH;
    strips.push({
      sessionId: g.sessionId,
      stripTop,
      headerY: headerYForStrip,
      headerH: headerHForStrip,
      rowYs,
      stripBottom
    });

    let x = xAfterLabel;
    rounds.forEach((r) => {
      const ck = gridColumnKey(r);
      roundNumbers.push(ck);
      const ww = vm.gridState.columnWidths[`round-${ck}`] || vm.strategyWidth;
      colPositions[`round-${ck}`] = {
        x,
        width: ww,
        stripIndex
      };
      maxX = Math.max(maxX, x + ww);
      x += ww + sm;
    });

    yCursor += SESSION_STRIP_GAP;
  }

  const rowPositions = {};
  if (strips.length > 0) {
    const s0 = strips[0];
    rowPositions.header = { y: s0.headerY, height: s0.headerH };
    for (let i = 0; i < maxQueryCount; i += 1) {
      const rr = s0.rowYs[i];
      if (rr) rowPositions[`row-${i}`] = { y: rr.y, height: rr.height };
    }
  } else {
    rowPositions.header = { y: rm, height: headerH };
  }

  const totalHeight = yCursor + rm;
  const totalWidth = maxX + rm;

  return {
    roundNumbers,
    maxQueryCount,
    colPositions,
    rowPositions,
    strips,
    roundMargin: rm,
    totalWidth,
    totalHeight
  };
}

/**
 * 获取单元格矩形
 */
export function getStrategyCellRect(vm, metrics, roundNumber, queryIndex, gridColKey = null) {
  const ck = gridColKey != null ? String(gridColKey) : `r${roundNumber}`;
  const col = metrics.colPositions[`round-${ck}`];
  if (!col || col.stripIndex === undefined || !metrics.strips) return null;
  const strip = metrics.strips[col.stripIndex];
  const row = strip && strip.rowYs[queryIndex];
  if (!strip || !row) return null;
  // 与 getRoundHeaderRect 同列：表头为 col.x / col.width，这里不再加 padX，避免小矩形外框与 Round 表头左右不齐
  const padX = 0;
  const padY = STRATEGY_CELL_PAD_Y;
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
export function getRoundHeaderRect(metrics, roundNumber, gridColKey = null) {
  const ck = gridColKey != null ? String(gridColKey) : `r${roundNumber}`;
  const col = metrics.colPositions[`round-${ck}`];
  if (!col || !metrics.strips || !metrics.strips.length) return null;
  const headerStrip = metrics.strips[0];
  return { x: col.x, y: headerStrip.headerY, width: col.width, height: headerStrip.headerH };
}

/**
 * 获取行标签矩形（多会话时须带 stripIndex）
 */
export function getRowLabelRect(metrics, queryIndex, stripIndex = 0) {
  const col = metrics.colPositions['label'];
  if (!metrics.strips || !metrics.strips[stripIndex]) return null;
  const strip = metrics.strips[stripIndex];
  const row = strip.rowYs[queryIndex];
  if (!col || !row) return null;
  return { x: col.x, y: row.y, width: col.width, height: row.height };
}

/**
 * 同一 session 条带内：左侧 Row 列合并为一条纵向长条（覆盖该条带全部策略行）
 */
export function getMergedRowLabelStripRect(metrics, stripIndex) {
  const col = metrics.colPositions['label'];
  if (!metrics.strips || !metrics.strips[stripIndex]) return null;
  const strip = metrics.strips[stripIndex];
  const rows = strip.rowYs || [];
  if (!col || !rows.length) return null;
  const first = rows[0];
  const last = rows[rows.length - 1];
  const py = STRATEGY_CELL_PAD_Y;
  return {
    x: col.x,
    y: first.y + py,
    width: Math.max(48, col.width - LABEL_STRIP_RIGHT_INSET),
    height: last.y + last.height - first.y - py
  };
}

/**
 * 列拖拽句柄
 */
export function getColumnResizeHandles(metrics) {
  const handles = [];
  const headerStrip = metrics.strips && metrics.strips[0];
  if (!headerStrip) return handles;
  Object.entries(metrics.colPositions).forEach(([key, col]) => {
    if (key === 'label') return;
    if (col.stripIndex === undefined || !metrics.strips) return;
    const strip = metrics.strips[col.stripIndex];
    if (!strip) return;
    handles.push({
      key,
      x: col.x + col.width,
      y: headerStrip.headerY,
      width: 8,
      height: Math.max(48, strip.stripBottom - headerStrip.headerY + 20)
    });
  });
  return handles;
}

/**
 * 行拖拽句柄
 */
export function getRowResizeHandles(metrics) {
  const handles = [];
  const labelX = metrics.colPositions.label.x;
  const totalW = metrics.totalWidth || 800;
  (metrics.strips || []).forEach((strip) => {
    (strip.rowYs || []).forEach((row, idx) => {
      handles.push({
        key: `s-${strip.sessionId}-row-${idx}`,
        x: labelX,
        y: row.y + row.height,
        width: totalW - labelX + 20,
        height: 8
      });
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