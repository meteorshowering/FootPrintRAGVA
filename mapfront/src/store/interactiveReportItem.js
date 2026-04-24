/**
 * 用当前河流图已加载的 embedding 点（与全局/策略小地图同源）覆盖证据 metadata 中的 coordinates_2d / full_json，
 * 避免 Chroma 内嵌的 full_json 仍为旧降维坐标。
 * @param {function(string): {x:number,y:number}|null|undefined} mapPointForId
 */
export function patchRagMetadataWithMapPoint(ragResult, mapPointForId) {
  if (!ragResult || !mapPointForId || typeof mapPointForId !== 'function') {
    return ragResult;
  }
  const mp = mapPointForId(ragResult.id);
  if (!mp || !Number.isFinite(mp.x) || !Number.isFinite(mp.y)) {
    return ragResult;
  }
  const xy = [mp.x, mp.y];
  const baseMeta = ragResult.metadata && typeof ragResult.metadata === 'object' ? ragResult.metadata : {};
  let metadata = { ...baseMeta, coordinates_2d: xy };
  if (metadata.full_json && typeof metadata.full_json === 'string') {
    try {
      const fj = JSON.parse(metadata.full_json);
      if (fj && typeof fj === 'object') {
        fj.coordinates_2d = xy;
        metadata = { ...metadata, full_json: JSON.stringify(fj) };
      }
    } catch (e) {
      /* ignore */
    }
  }
  return { ...ragResult, metadata };
}

/**
 * 将 RAG retrieval_result（可含 evaluation）转为 Interactive Report / ItemDetail 使用的 item 结构。
 * 与 selectRiverResult 中 processedData 逻辑一致。
 * @param {{ mapPointForId?: function(string): object }} [options]
 */
export function buildInteractiveReportItemFromRag(getters, ragResult, options = {}) {
  if (!ragResult || !ragResult.id) return null;

  const mapPointForId = options && options.mapPointForId;
  const sourceRag = mapPointForId ? patchRagMetadataWithMapPoint(ragResult, mapPointForId) : ragResult;

  let parsedMetadata = null;
  if (sourceRag.metadata?.metadata) {
    if (typeof sourceRag.metadata.metadata === 'string') {
      try {
        parsedMetadata = JSON.parse(sourceRag.metadata.metadata);
      } catch (e) {
        console.warn('Failed to parse metadata:', e);
      }
    } else {
      parsedMetadata = sourceRag.metadata.metadata;
    }
  }

  let dataType = sourceRag.metadata?.type || parsedMetadata?.type || 'unknown';
  if (!sourceRag.metadata?.type && !parsedMetadata?.type && (sourceRag.metadata?.full_json || sourceRag.metadata?.savepath || sourceRag.metadata?.save_path)) {
    dataType = 'picture';
  }

  if (dataType === 'text') dataType = 'texture';
  if (dataType === 'figure' || dataType === 'image') dataType = 'picture';

  let savePath = parsedMetadata?.save_path || sourceRag.metadata?.save_path || sourceRag.metadata?.savepath;
  if (!savePath && sourceRag.metadata?.full_json) {
    try {
      const fullJson = JSON.parse(sourceRag.metadata.full_json);
      savePath = fullJson.save_path || fullJson.savepath;
    } catch (e) {
      // ignore
    }
  }

  // 与 EnhancedRiverChart.processRagResultForDetail 一致：正文可能在 content / metadata / 解析后的 metadata 中
  let textContent = '';
  if (sourceRag.content) {
    if (typeof sourceRag.content === 'string') {
      textContent = sourceRag.content;
    } else if (typeof sourceRag.content === 'object' && sourceRag.content.text != null) {
      textContent = String(sourceRag.content.text);
    }
  }
  if (!textContent && typeof sourceRag.metadata?.content === 'string') {
    textContent = sourceRag.metadata.content;
  }
  if (!textContent && typeof parsedMetadata?.content === 'string') {
    textContent = parsedMetadata.content;
  }

  const paperTitle = parsedMetadata?.paper_title || '';
  const titleFromMeta =
    parsedMetadata?.figure_title ||
    sourceRag.content?.title ||
    sourceRag.metadata?.title ||
    paperTitle ||
    '';
  const title =
    (titleFromMeta && String(titleFromMeta).trim()) ||
    (textContent ? String(textContent).replace(/\s+/g, ' ').trim() : '') ||
    sourceRag.id ||
    'No Title';

  return {
    id: sourceRag.id,
    type: dataType,
    title,
    relative_path: savePath ? getters.extractRelativePath(savePath) : '',
    key_entities: parsedMetadata?.key_entities || sourceRag.metadata?.key_entities || [],
    text_content: textContent,
    concise_summary: parsedMetadata?.concise_summary || sourceRag.metadata?.concise_summary || '',
    inferred_insight: parsedMetadata?.inferred_insight || sourceRag.metadata?.inferred_insight || '',
    paper_title: paperTitle,
    score: sourceRag.score,
    branch_action: sourceRag.evaluation?.branch_action || 'UNKNOWN',
    parsed_metadata: parsedMetadata || null,
    original_data: {
      ...sourceRag,
      evaluation: sourceRag.evaluation || null,
    },
  };
}
