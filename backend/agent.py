import json
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME
import tools

# 初始化 OpenAI 客户端（兼容 DeepSeek）
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# 定义可供 Agent 调用的工具（Function Calling 格式）
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_server_metric",
            "description": "获取某台游戏服务器的运行指标（在线人数、CPU使用率、内存使用率）",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_id": {"type": "string", "description": "服务器标识，如 lobby-01, game-01"},
                    "metric": {"type": "string", "enum": ["online_count", "cpu_usage", "mem_usage"]}
                },
                "required": ["server_id", "metric"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "restart_service",
            "description": "重启指定的游戏服务器（危险操作，需要用户二次确认）",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_id": {"type": "string", "description": "服务器标识"}
                },
                "required": ["server_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tail_error_log",
            "description": "获取服务器最近的错误日志，用于故障排查",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_id": {"type": "string", "description": "服务器标识"},
                    "lines": {"type": "integer", "description": "获取日志行数，默认50"}
                },
                "required": ["server_id"]
            }
        }
    }
]


def run_agent(user_input: str, pending_confirm: dict = None):
    """
    执行 Agent 对话。
    pending_confirm: 用于处理危险操作的二次确认，格式 {"action": "restart", "server_id": "xxx", "confirmed": bool}
    """
    messages = [{"role": "user", "content": user_input}]

    # 如果有待确认项，直接执行而不调用模型
    if pending_confirm and pending_confirm.get("action") == "restart" and pending_confirm.get("confirmed"):
        result = tools.restart_service(pending_confirm["server_id"])
        return {
            "type": "tool_result",
            "content": json.dumps(result, ensure_ascii=False),
            "need_confirm": False
        }

    # 调用大模型选择工具
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    message = response.choices[0].message
    # 如果没有工具调用，直接返回模型回答
    if not message.tool_calls:
        return {"type": "text", "content": message.content, "need_confirm": False}

    # 处理第一个工具调用（简化，实际可循环处理）
    tool_call = message.tool_calls[0]
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)

    # 执行工具函数
    if func_name == "get_server_metric":
        result = tools.get_server_metric(**func_args)
        return {"type": "tool_result", "content": json.dumps(result, ensure_ascii=False), "need_confirm": False}
    elif func_name == "restart_service":
        # 危险操作，返回需要确认
        return {
            "type": "need_confirm",
            "content": f"即将执行危险操作：重启服务器 {func_args['server_id']}，是否确认？(回复 YES 确认)",
            "need_confirm": True,
            "confirm_data": {"action": "restart", "server_id": func_args["server_id"]}
        }
    elif func_name == "tail_error_log":
        result = tools.tail_error_log(**func_args)
        # 获取日志后，可以再调用大模型进行智能分析
        log_content = result.get("log_content", "")
        analysis = analyze_log_with_ai(log_content, func_args["server_id"])
        return {"type": "tool_result", "content": analysis, "need_confirm": False}
    else:
        return {"type": "text", "content": "未知工具调用", "need_confirm": False}


def analyze_log_with_ai(log_content: str, server_id: str):
    """使用大模型分析错误日志"""
    prompt = f"""请分析以下游戏服务器 {server_id} 的错误日志，指出可能的原因和修复建议：

{log_content}
"""
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content