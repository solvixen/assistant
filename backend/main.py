from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import agent

app = FastAPI(title="AI Ops Assistant")

# 允许前端跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储会话中的待确认操作（生产环境应用 Redis 或内存字典，此处简化）
pending_confirmations: Dict[str, Any] = {}

class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    reply: str
    need_confirm: bool = False
    confirm_id: Optional[str] = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session = request.session_id
    # 检查是否有待确认的操作
    pending = pending_confirmations.get(session)
    if pending and request.prompt.strip().upper() == "YES":
        # 用户确认执行危险操作
        result = agent.run_agent("", pending_confirm=pending)
        del pending_confirmations[session]
        return ChatResponse(reply=result["content"], need_confirm=False)
    elif pending and request.prompt.strip().upper() != "YES":
        # 用户取消或输入其他内容，清除待确认
        del pending_confirmations[session]
        return ChatResponse(reply="已取消操作。", need_confirm=False)

    # 正常处理用户输入
    resp = agent.run_agent(request.prompt)
    if resp.get("need_confirm"):
        # 存储确认信息
        pending_confirmations[session] = resp["confirm_data"]
        return ChatResponse(reply=resp["content"], need_confirm=True, confirm_id=session)
    else:
        return ChatResponse(reply=resp["content"], need_confirm=False)

@app.get("/api/health")
async def health():
    return {"status": "ok"}