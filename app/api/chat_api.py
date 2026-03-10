# -*- coding: utf-8 -*-
"""Chat API 模块

提供 FastAPI 接口，对外暴露智能客服对话能力。
"""

import os
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..agent.agent_manager import AgentManager
from .admin_api import router as admin_router, log_conversation
from ..db.session_store import SessionStore


# 创建 FastAPI 应用
app = FastAPI(
    title="SmartSupport AI",
    description="企业级智能客服 Agent API",
    version="1.0.0"
)

# 注册管理后台路由
app.include_router(admin_router)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储活跃的 Agent 会话
_active_sessions: dict = {}


# ==================== 请求/响应模型 ====================

class ChatRequest(BaseModel):
    """聊天请求"""
    user_id: str = Field(..., description="用户唯一标识")
    message: str = Field(..., description="用户消息", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="会话ID（用于保持上下文）")
    context: Optional[dict] = Field(None, description="额外上下文信息")


class ChatResponse(BaseModel):
    """聊天响应"""
    success: bool = Field(..., description="是否成功")
    reply: str = Field(..., description="助手回复")
    intent: Optional[str] = Field(None, description="识别到的意图")
    tool_used: Optional[str] = Field(None, description="使用的工具")
    context_count: Optional[int] = Field(None, description="检索到的上下文数量")
    session_id: str = Field(..., description="会话ID")
    timestamp: str = Field(..., description="响应时间")


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str
    user_id: str
    history_length: int
    created_at: str
    last_active: str


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: str
    version: str


# ==================== 依赖注入 ====================

def get_or_create_agent(session_id: Optional[str], user_id: str) -> AgentManager:
    """获取或创建 Agent 实例"""
    if session_id and session_id in _active_sessions:
        return _active_sessions[session_id]["agent"]

    # 创建新的 Agent 实例
    agent = AgentManager(
        user_id=user_id,
        enable_memory=True,
        enable_rag=True,
        enable_tools=True
    )

    return agent


# ==================== API 端点 ====================

@app.get("/", response_model=HealthResponse)
async def root():
    """根路径 - 服务信息"""
    return HealthResponse(
        status="running",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    主对话接口

    处理用户消息，根据意图路由到 RAG/Tool/LLM，返回答复。
    """
    try:
        # 生成或使用现有会话ID
        session_id = request.session_id or f"sess_{request.user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 获取或创建 Agent
        if session_id in _active_sessions:
            agent = _active_sessions[session_id]["agent"]
        else:
            agent = AgentManager(
                user_id=request.user_id,
                enable_memory=True,
                enable_rag=True,
                enable_tools=True
            )
            _active_sessions[session_id] = {
                "agent": agent,
                "user_id": request.user_id,
                "created_at": datetime.now().isoformat()
            }
            # 持久化会话到数据库
            SessionStore.create_session(session_id, request.user_id)

        # 更新最后活跃时间
        _active_sessions[session_id]["last_active"] = datetime.now().isoformat()

        # 持久化用户消息
        SessionStore.add_message(session_id, "user", request.message)

        # 调用 Agent 处理消息
        result = agent.chat(
            message=request.message,
            context=request.context or {}
        )

        # 持久化助手回复
        reply = result.get("answer", "")
        SessionStore.add_message(session_id, "assistant", reply)

        # 记录对话日志（用于统计）
        log_conversation(
            user_id=request.user_id,
            message=request.message,
            intent=result.get("intent", "unknown")
        )

        # 构建响应
        return ChatResponse(
            success=True,
            reply=reply,
            intent=result.get("intent"),
            tool_used=result.get("tool_used"),
            context_count=result.get("context_count"),
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")


@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """
    获取会话历史

    Args:
        session_id: 会话ID

    Returns:
        对话历史列表
    """
    # 优先从数据库加载历史
    db_history = SessionStore.get_history(session_id)
    if db_history:
        # 转换为前端期望的格式
        formatted_history = []
        user_msg = None
        for msg in db_history:
            if msg["role"] == "user":
                user_msg = msg["content"]
            elif msg["role"] == "assistant" and user_msg:
                formatted_history.append({
                    "user": user_msg,
                    "assistant": msg["content"]
                })
                user_msg = None

        return {
            "session_id": session_id,
            "history": formatted_history,
            "turn_count": len(formatted_history)
        }

    # 如果内存中有会话，也从内存获取（Agent可能有更完整的历史）
    if session_id in _active_sessions:
        agent = _active_sessions[session_id]["agent"]
        history = agent.get_conversation_history()
        return {
            "session_id": session_id,
            "history": history,
            "turn_count": len(history)
        }

    raise HTTPException(status_code=404, detail="会话不存在")


@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """
    清除会话（删除历史记录）

    Args:
        session_id: 会话ID

    Returns:
        操作结果
    """
    # 从数据库删除
    deleted = SessionStore.delete_session(session_id)

    # 如果内存中有，也从内存中移除
    if session_id in _active_sessions:
        agent = _active_sessions[session_id]["agent"]
        agent.clear_memory()
        del _active_sessions[session_id]

    if not deleted and session_id not in _active_sessions:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {
        "success": True,
        "message": f"会话 {session_id} 已清除"
    }


@app.get("/sessions", response_model=list[SessionInfo])
async def list_sessions(user_id: Optional[str] = None):
    """
    列出活跃会话

    Args:
        user_id: 可选的用户ID过滤

    Returns:
        会话列表
    """
    # 从数据库加载会话列表
    db_sessions = SessionStore.list_sessions(user_id)

    sessions = []
    for session in db_sessions:
        # 检查内存中是否有该会话
        if session["session_id"] in _active_sessions:
            info = _active_sessions[session["session_id"]]
            agent = info["agent"]
            history_length = len(agent.get_conversation_history())
        else:
            # 从数据库计算历史长度
            history = SessionStore.get_history(session["session_id"])
            # 每两条消息（user+assistant）算作一轮
            history_length = len([h for h in history if h["role"] == "user"])

        sessions.append(SessionInfo(
            session_id=session["session_id"],
            user_id=session["user_id"],
            history_length=history_length,
            created_at=session.get("created_at", ""),
            last_active=session.get("last_active", "")
        ))

    return sessions


@app.get("/stats")
async def get_stats():
    """获取系统统计信息"""
    total_sessions = len(_active_sessions)

    # 统计各用户会话数
    user_sessions = {}
    for info in _active_sessions.values():
        user_id = info["user_id"]
        user_sessions[user_id] = user_sessions.get(user_id, 0) + 1

    return {
        "total_active_sessions": total_sessions,
        "unique_users": len(user_sessions),
        "user_session_counts": user_sessions,
        "timestamp": datetime.now().isoformat()
    }


# ==================== 启动和清理 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("=" * 50)
    print("SmartSupport AI 服务启动")
    print("=" * 50)
    print(f"文档地址: http://127.0.0.1:8000/docs")
    print(f"健康检查: http://127.0.0.1:8000/health")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("正在关闭 SmartSupport AI 服务...")
    # 清理资源
    _active_sessions.clear()


# 如果是直接运行此文件
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
