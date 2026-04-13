// utils/alphaShape.js
export function alphaShape(points, alpha = 1.0) {
  if (points.length < 3) return points;

  // 先计算 Delaunay 三角剖分（需要 d3-delaunay）
  const delaunay = Delaunay.from(points);
  const triangles = Array.from(delaunay.triangles);
  const coords = Array.from(delaunay.points);

  const edges = new Map();
  for (let i = 0; i < triangles.length; i += 3) {
    const a = triangles[i], b = triangles[i+1], c = triangles[i+2];
    addEdge(a, b);
    addEdge(b, c);
    addEdge(c, a);
  }

  function addEdge(i, j) {
    const key = i < j ? `${i}-${j}` : `${j}-${i}`;
    if (!edges.has(key)) edges.set(key, { i, j, count: 0 });
    edges.get(key).count++;
  }

  const boundary = [];
  for (const [key, edge] of edges) {
    if (edge.count === 1) {  // 边界边
      boundary.push([coords[edge.i], coords[edge.j]]);
    }
  }

  // 这里可以再做 alpha 过滤（比较复杂），当前先返回所有边界
  // 如果需要严格 alpha shape，可继续实现 circumradius 过滤
  return boundary.flat(); // 简化返回
}