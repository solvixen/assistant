"""
模拟运维操作的工具函数。
实际使用时可以替换为 SSH / Prometheus / K8s API 等。
"""

import time
import random

# 模拟服务器状态数据
MOCK_SERVERS = {
    "lobby-01": {"online_count": 1234, "cpu_usage": 45, "mem_usage": 62},
    "game-01": {"online_count": 567, "cpu_usage": 78, "mem_usage": 81},
    "game-02": {"online_count": 890, "cpu_usage": 32, "mem_usage": 44},
}

def get_server_metric(server_id: str, metric: str):
    """获取服务器指标"""
    if server_id not in MOCK_SERVERS:
        return {"error": f"服务器 {server_id} 不存在"}
    val = MOCK_SERVERS[server_id].get(metric)
    if val is None:
        return {"error": f"指标 {metric} 无效，可选: online_count, cpu_usage, mem_usage"}
    return {"server_id": server_id, "metric": metric, "value": val, "unit": "人" if metric=="online_count" else "%"}

def restart_service(server_id: str):
    """重启服务（模拟）"""
    if server_id not in MOCK_SERVERS:
        return {"error": f"服务器 {server_id} 不存在"}
    # 模拟重启过程
    time.sleep(1)
    return {"status": "success", "message": f"服务器 {server_id} 已重启", "server_id": server_id}

def tail_error_log(server_id: str, lines: int = 50):
    """获取错误日志（模拟）"""
    if server_id not in MOCK_SERVERS:
        return {"error": f"服务器 {server_id} 不存在"}
    # 模拟日志内容
    mock_log = f"[ERROR] 2025-04-09 10:23:45 {server_id} connection pool exhausted\n[ERROR] 2025-04-09 10:24:01 {server_id} timeout reading response\n"
    return {"server_id": server_id, "log_content": mock_log, "lines_requested": lines}