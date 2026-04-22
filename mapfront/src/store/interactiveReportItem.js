/**
 * 将 RAG retrieval_result（可含 evaluation）转为 Interactive Report / ItemDetail 使用的 item 结构。
 * 与 selectRiverResult 中 processedData 逻辑一致。
 */
export function buildInteractiveReportItemFromRag(getters, ragResult) {
  if (!ragResult || !ragResult.id) return null;

  let parsedMetadata = null;
  if (ragResult.metadata?.metadata) {
    if (typeof ragResult.metadata.metadata === 'string') {
      try {
        parsedMetadata = JSON.parse(ragResult.metadata.metadata);
      } catch (e) {
        console.warn('Failed to parse metadata:', e);
      }
    } else {
      parsedMetadata = ragResult.metadata.metadata;
    }
  }

  let dataType = ragResult.metadata?.type || parsedMetadata?.type || 'unknown';
  if (!ragResult.metadata?.type && !parsedMetadata?.type && (ragResult.metadata?.full_json || ragResult.metadata?.savepath || ragResult.metadata?.save_path)) {
    dataType = 'picture';
  }

  if (dataType === 'text') dataType = 'texture';
  if (dataType === 'figure' || dataType === 'image') dataType = 'picture';

  let savePath = parsedMetadata?.save_path || ragResult.metadata?.save_path || ragResult.metadata?.savepath;
  if (!savePath && ragResult.metadata?.full_json) {
    try {
      const fullJson = JSON.parse(ragResult.metadata.full_json);
      savePath = fullJson.save_path || fullJson.savepath;
    } catch (e) {
      // ignore
    }
  }

  // 与 EnhancedRiverChart.processRagResultForDetail 一致：正文可能在 content / metadata / 解析后的 metadata 中
  let textContent = '';
  if (ragResult.content) {
    if (typeof ragResult.content === 'string') {
      textContent = ragResult.content;
    } else if (typeof ragResult.content === 'object' && ragResult.content.text != null) {
      textContent = String(ragResult.content.text);
    }
  }
  if (!textContent && typeof ragResult.metadata?.content === 'string') {
    textContent = ragResult.metadata.content;
  }
  if (!textContent && typeof parsedMetadata?.content === 'string') {
    textContent = parsedMetadata.content;
  }

  const paperTitle = parsedMetadata?.paper_title || '';
  const titleFromMeta =
    parsedMetadata?.figure_title ||
    ragResult.content?.title ||
    ragResult.metadata?.title ||
    paperTitle ||
    '';
  const title =
    (titleFromMeta && String(titleFromMeta).trim()) ||
    (textContent ? String(textContent).replace(/\s+/g, ' ').trim() : '') ||
    ragResult.id ||
    'No Title';

  return {
    id: ragResult.id,
    type: dataType,
    title,
    relative_path: savePath ? getters.extractRelativePath(savePath) : '',
    key_entities: parsedMetadata?.key_entities || ragResult.metadata?.key_entities || [],
    text_content: textContent,
    concise_summary: parsedMetadata?.concise_summary || ragResult.metadata?.concise_summary || '',
    inferred_insight: parsedMetadata?.inferred_insight || ragResult.metadata?.inferred_insight || '',
    paper_title: paperTitle,
    score: ragResult.score,
    branch_action: ragResult.evaluation?.branch_action || 'UNKNOWN',
    parsed_metadata: parsedMetadata || null,
    original_data: {
      ...ragResult,
      evaluation: ragResult.evaluation || null,
    },
  };
}
