"""
【功能】FastAPI WebSocket 连接管理：维护活跃连接、broadcast 科研图状态与实验结果；登记 interactive 模式下的 pause gate，供引擎在审批点挂起/恢复。
【长期价值】核心长期维护（与 server.py / engine 强绑定）；若弃用交互式暂停，可删减 pause_gate 相关逻辑。
"""
# connection.py
from typing import List
from fastapi import WebSocket
from protocols import ResearchGraph # 确保你有这个类定义
import json
import traceback

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # ✨ 新增：存储 interactive 模式的 pause gates
        self._pause_gates = {}

    def register_pause_gate(self, run_id: str, pause_gate):
        self._pause_gates[run_id] = pause_gate

    def get_pause_gate(self, run_id: str):
        return self._pause_gates.get(run_id)

    def unregister_pause_gate(self, run_id: str):
        if run_id in self._pause_gates:
            del self._pause_gates[run_id]

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_graph(self, graph: ResearchGraph):
        """推送 Graph 对象"""
        # #region agent log
        try:
            with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps({"id":"log_broadcast_graph_entry","timestamp":__import__("time").time()*1000,"location":"connection.py:18","message":"broadcast_graph调用","data":{"active_connections_count":len(self.active_connections)},"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+"\n")
        except: pass
        # #endregion
        if not self.active_connections:
            # #region agent log
            try:
                with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"id":"log_broadcast_graph_no_connections","timestamp":__import__("time").time()*1000,"location":"connection.py:21","message":"无活跃连接，提前返回","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+"\n")
            except: pass
            # #endregion
            return
        try:
            # 序列化 Graph，使用 JSON 模式以兼容 set 等类型
            # #region agent log
            try:
                with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"id":"log_broadcast_graph_before_dump","timestamp":__import__("time").time()*1000,"location":"connection.py:25","message":"准备序列化graph","data":{"graph_type":type(graph).__name__},"sessionId":"debug-session","runId":"run1","hypothesisId":"B"})+"\n")
            except: pass
            # #endregion
            graph_data = graph.model_dump(mode="json")
            # #region agent log
            try:
                with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"id":"log_broadcast_graph_after_dump","timestamp":__import__("time").time()*1000,"location":"connection.py:26","message":"graph序列化成功","data":{"graph_data_keys":list(graph_data.keys()) if isinstance(graph_data,dict) else "not_dict"},"sessionId":"debug-session","runId":"run1","hypothesisId":"B"})+"\n")
            except: pass
            # #endregion
            await self.broadcast_json(graph_data)
        except Exception as e:
            # #region agent log
            try:
                with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"id":"log_broadcast_graph_error","timestamp":__import__("time").time()*1000,"location":"connection.py:27","message":"broadcast_graph异常","data":{"error":str(e),"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"B"})+"\n")
            except: pass
            # #endregion
            print(f"❌ WebSocket 推送 Graph 失败: {e}")

    async def broadcast_json(self, data: dict):
        """推送普通 JSON"""
        # #region agent log
        try:
            with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps({"id":"log_broadcast_json_entry","timestamp":__import__("time").time()*1000,"location":"connection.py:29","message":"broadcast_json调用","data":{"connections_count":len(self.active_connections),"data_type":type(data).__name__},"sessionId":"debug-session","runId":"run1","hypothesisId":"A"})+"\n")
        except: pass
        # #endregion
        # 复制一份列表进行遍历，防止发送过程中有连接断开导致 list size changed
        for connection in list(self.active_connections):
            # #region agent log
            try:
                with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"id":"log_broadcast_json_before_send","timestamp":__import__("time").time()*1000,"location":"connection.py:34","message":"准备发送JSON","data":{"connection_type":type(connection).__name__},"sessionId":"debug-session","runId":"run1","hypothesisId":"A"})+"\n")
            except: pass
            # #endregion
            try:
                await connection.send_json(data)
                # #region agent log
                try:
                    with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps({"id":"log_broadcast_json_send_success","timestamp":__import__("time").time()*1000,"location":"connection.py:35","message":"JSON发送成功","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"A"})+"\n")
                except: pass
                # #endregion
            except Exception as e:
                # #region agent log
                try:
                    with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps({"id":"log_broadcast_json_send_error","timestamp":__import__("time").time()*1000,"location":"connection.py:35","message":"JSON发送失败","data":{"error":str(e),"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"A"})+"\n")
                except: pass
                # #endregion
                print(f"发送消息错误 (移除失效连接): {e}")
                self.disconnect(connection)
                # 移除失效连接后，继续遍历下一个
    async def broadcast_plan_created(self, plan_data: dict):
        """推送策略计划创建消息"""
        print(f"📤 [Connection] 推送 plan_created: round={plan_data.get('round_number')}, plan_id={plan_data.get('plan_id')}")
        await self.broadcast_json({
            "type": "plan_created",
            "data": plan_data
        })
    
    async def broadcast_retrieval_complete(self, plan_id: str, node_ids: list):
        """推送检索完成消息（节点已添加但未评估）"""
        print(f"📤 [Connection] 推送 retrieval_complete: plan_id={plan_id}, node_count={len(node_ids)}")
        await self.broadcast_json({
            "type": "retrieval_complete",
            "plan_id": plan_id,
            "node_ids": node_ids
        })
    
    async def broadcast_evaluation_complete(self, node_id: str, evaluation: dict):
        """推送评估完成消息（节点已评估）"""
        print(f"📤 [Connection] 推送 evaluation_complete: node_id={node_id}, action={evaluation.get('branch_action')}")
        await self.broadcast_json({
            "type": "evaluation_complete",
            "node_id": node_id,
            "evaluation": evaluation
        })

    async def broadcast_summary(self, summary):
        """推送总结报告"""
        # #region agent log
        try:
            with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps({"id":"log_broadcast_summary_entry","timestamp":__import__("time").time()*1000,"location":"connection.py:39","message":"broadcast_summary调用","data":{"active_connections_count":len(self.active_connections),"summary_type":type(summary).__name__,"has_model_dump":hasattr(summary,"model_dump")},"sessionId":"debug-session","runId":"run1","hypothesisId":"D"})+"\n")
        except: pass
        # #endregion
        if not self.active_connections:
            # #region agent log
            try:
                with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"id":"log_broadcast_summary_no_connections","timestamp":__import__("time").time()*1000,"location":"connection.py:42","message":"无活跃连接，提前返回","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+"\n")
            except: pass
            # #endregion
            return
        try:
            # 检查summary类型
            if hasattr(summary, 'model_dump'):
                # #region agent log
                try:
                    with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps({"id":"log_broadcast_summary_before_dump","timestamp":__import__("time").time()*1000,"location":"connection.py:47","message":"准备序列化SummaryResponse","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"B"})+"\n")
                except: pass
                # #endregion
                # 是SummaryResponse类型
                summary_data = summary.model_dump(mode="json")
                # #region agent log
                try:
                    with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps({"id":"log_broadcast_summary_after_dump","timestamp":__import__("time").time()*1000,"location":"connection.py:48","message":"SummaryResponse序列化成功","data":{"summary_data_keys":list(summary_data.keys()) if isinstance(summary_data,dict) else "not_dict"},"sessionId":"debug-session","runId":"run1","hypothesisId":"B"})+"\n")
                except: pass
                # #endregion
                await self.broadcast_json({"type": "summary", "content": summary_data})
            else:
                # #region agent log
                try:
                    with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps({"id":"log_broadcast_summary_string","timestamp":__import__("time").time()*1000,"location":"connection.py:51","message":"summary是字符串类型","data":{"summary_length":len(str(summary)) if summary else 0},"sessionId":"debug-session","runId":"run1","hypothesisId":"D"})+"\n")
                except: pass
                # #endregion
                # 是字符串类型
                await self.broadcast_json({"type": "summary", "content": summary})
            # #region agent log
            try:
                with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"id":"log_broadcast_summary_success","timestamp":__import__("time").time()*1000,"location":"connection.py:52","message":"总结报告发送成功","data":{},"sessionId":"debug-session","runId":"run1","hypothesisId":"D"})+"\n")
            except: pass
            # #endregion
            print("[DEBUG] 总结报告已发送到前端")
        except Exception as e:
            # #region agent log
            try:
                with open(r"c:\liuxingyu\multisubspace-data\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"id":"log_broadcast_summary_error","timestamp":__import__("time").time()*1000,"location":"connection.py:54","message":"broadcast_summary异常","data":{"error":str(e),"traceback":traceback.format_exc()},"sessionId":"debug-session","runId":"run1","hypothesisId":"B"})+"\n")
            except: pass
            # #endregion
            print(f"❌ WebSocket 推送总结报告失败: {e}")
    
    async def broadcast_experiment_result(self, experiment_result):
        """推送 ExperimentResult 对象（包含 plansummary）"""
        if not self.active_connections:
            return
        try:
            experiment_data = experiment_result.model_dump(mode="json")
            await self.broadcast_json({
                "type": "experiment_result",
                "data": experiment_data
            })
            print(f"📤 [Connection] 推送 experiment_result: {len(experiment_result.iterations)} 轮迭代")
        except Exception as e:
            print(f"❌ WebSocket 推送 ExperimentResult 失败: {e}")