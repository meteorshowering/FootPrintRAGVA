/**
 * RAG服务API接口
 * 用于与后端通信，发送用户问题并获取检索结果
 */

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000';

/**
 * 发送用户问题到后端，获取检索结果
 * @param {string} question - 用户输入的问题
 * @param {Object} options - 可选参数
 * @param {string} options.parentNode - 父节点ID，默认为"0"
 * @param {string} options.strategy - 策略名称，默认为"strategy_semantic_search"
 * @returns {Promise<Object>} 返回query_result对象，包含orchestrator_plan和rag_results
 */
export async function submitUserQuery(question, options = {}) {
  const {
    parentNode = '0',
    strategy = 'strategy_semantic_search'
  } = options;

  try {
    const response = await fetch(`${API_BASE_URL}/api/rag/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: question,
        parent_node: parentNode,
        strategy: strategy
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // 验证返回数据结构
    if (!data.orchestrator_plan || !data.rag_results) {
      throw new Error('Invalid response structure: missing orchestrator_plan or rag_results');
    }

    return data;
  } catch (error) {
    console.error('Error submitting user query:', error);
    throw error;
  }
}

/**
 * 获取查询状态（用于轮询长时间运行的查询）
 * @param {string} queryId - 查询ID
 * @returns {Promise<Object>} 查询状态和结果
 */
export async function getQueryStatus(queryId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/rag/query/${queryId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting query status:', error);
    throw error;
  }
}

/**
 * 预期的返回数据结构（用于类型检查和文档）
 * @typedef {Object} QueryResult
 * @property {Object} orchestrator_plan - 编排器计划
 * @property {string} orchestrator_plan.action - 动作类型，通常是"call_tool"
 * @property {string} orchestrator_plan.tool_name - 工具名称，如"strategy_semantic_search"
 * @property {string} orchestrator_plan.ParentNode - 父节点ID
 * @property {Object} orchestrator_plan.args - 参数对象
 * @property {string} orchestrator_plan.args.query_intent - 查询意图
 * @property {string} orchestrator_plan.reason - 选择该策略的原因
 * @property {number} orchestrator_plan.total_results - 总结果数
 * @property {number} orchestrator_plan.duplicate_results - 重复结果数
 * @property {string} orchestrator_plan.plansummary - 计划总结（Markdown格式）
 * @property {Array} rag_results - RAG检索结果数组
 * @property {Object} rag_results[].retrieval_result - 检索结果
 * @property {string} rag_results[].retrieval_result.id - 结果ID
 * @property {string} rag_results[].retrieval_result.source_tool - 来源工具
 * @property {Object} rag_results[].retrieval_result.content - 内容对象
 * @property {string} rag_results[].retrieval_result.content.text - 文本内容
 * @property {Object} rag_results[].retrieval_result.metadata - 元数据
 * @property {string} rag_results[].retrieval_result.metadata.type - 类型（"picture"或"texture"）
 * @property {string} rag_results[].retrieval_result.metadata.metadata - JSON字符串格式的元数据
 * @property {number} rag_results[].retrieval_result.score - 检索分数
 * @property {Object} rag_results[].evaluation - 评估结果
 * @property {string} rag_results[].evaluation.branch_action - 分支动作（"GROW"、"PRUNE"、"KEEP"等）
 * @property {string} rag_results[].evaluation.extracted_insight - 提取的洞察
 * @property {Object} rag_results[].evaluation.scores - 评分对象
 * @property {number} rag_results[].evaluation.scores.relevance - 相关性分数
 * @property {number} rag_results[].evaluation.scores.credibility - 可信度分数
 */

export default {
  submitUserQuery,
  getQueryStatus
};
