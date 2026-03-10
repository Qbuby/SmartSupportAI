# -*- coding: utf-8 -*-
"""Agent 管理器模块

负责接收用户问题、判断意图、调度任务到 RAG/Tool/LLM。
"""

import re
from typing import Dict, Any, Optional, Literal
from enum import Enum

from ..rag.rag_pipeline import RAGPipeline
from ..memory.short_memory import ShortMemory
from ..memory.long_memory import LongMemory
from .tool_router import ToolRouter


class IntentType(Enum):
    """意图类型"""
    ORDER_QUERY = "order_query"      # 订单查询
    TICKET_QUERY = "ticket_query"    # 工单查询
    KNOWLEDGE_QUERY = "knowledge_query"  # 知识库查询
    GENERAL_CHAT = "general_chat"    # 普通对话


class AgentManager:
    """Agent 管理器

    核心调度逻辑：
    1. 接收用户输入
    2. 意图识别
    3. 路由到对应处理器
    4. 整合记忆和上下文
    5. 返回最终回答
    """

    def __init__(
        self,
        user_id: Optional[str] = None,
        enable_memory: bool = True,
        enable_rag: bool = True,
        enable_tools: bool = True
    ):
        """
        初始化 Agent 管理器

        Args:
            user_id: 用户 ID，用于记忆管理
            enable_memory: 是否启用记忆系统
            enable_rag: 是否启用 RAG
            enable_tools: 是否启用工具调用
        """
        self.user_id = user_id
        self.enable_memory = enable_memory
        self.enable_rag = enable_rag
        self.enable_tools = enable_tools

        # 初始化各模块
        self.rag_pipeline = RAGPipeline() if enable_rag else None
        self.tool_router = ToolRouter() if enable_tools else None
        self.short_memory = ShortMemory() if enable_memory else None
        self.long_memory = LongMemory() if enable_memory else None

        # 意图识别关键词模式
        self.intent_patterns = {
            IntentType.ORDER_QUERY: [
                r'订单[\s号]*([A-Za-z\d-]+)',
                r'我的订单',
                r'查询订单',
                r'查一下订单',
                r'订单状态',
                r'发货了吗',
                r'什么时候到货',
                r'订单.*查询'
            ],
            IntentType.TICKET_QUERY: [
                r'工单[\s号]*([A-Za-z\d-]+)',
                r'我的工单',
                r'查询工单',
                r'查一下工单',
                r'工单状态',
                r'技术支持',
                r'售后',
                r'工单.*查询',
                r' ticket[\s#]*([A-Za-z\d-]+)'
            ]
        }

    def detect_intent(self, query: str) -> tuple[IntentType, Dict[str, Any]]:
        """
        检测用户意图

        Args:
            query: 用户查询

        Returns:
            (意图类型, 提取的参数)
        """
        query_lower = query.lower()

        # 检查订单相关意图
        for pattern in self.intent_patterns[IntentType.ORDER_QUERY]:
            match = re.search(pattern, query_lower)
            if match:
                params = {}
                if match.groups():
                    params['order_id'] = match.group(1)
                return IntentType.ORDER_QUERY, params

        # 检查工单相关意图
        for pattern in self.intent_patterns[IntentType.TICKET_QUERY]:
            match = re.search(pattern, query_lower)
            if match:
                params = {}
                if match.groups():
                    params['ticket_id'] = match.group(1)
                return IntentType.TICKET_QUERY, params

        # 默认使用知识库查询
        return IntentType.KNOWLEDGE_QUERY, {}

    def chat(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        主对话接口

        Args:
            message: 用户消息
            context: 额外上下文

        Returns:
            包含回答和元信息的字典
        """
        context = context or {}

        # 1. 获取历史上下文
        history_context = ""
        if self.short_memory:
            history = self.short_memory.get_history()
            if history:
                history_context = self._format_history(history)

        # 2. 获取用户长期记忆
        user_profile = {}
        if self.long_memory and self.user_id:
            user_profile = self.long_memory.get_user_memory(self.user_id)

        # 3. 意图识别
        intent, params = self.detect_intent(message)

        # 4. 根据意图路由处理
        response_data = {
            "query": message,
            "intent": intent.value,
            "params": params,
            "user_id": self.user_id
        }

        if intent == IntentType.ORDER_QUERY and self.enable_tools:
            # 订单查询
            result = self.tool_router.call_tool("order", params, message)
            response_data.update(result)

        elif intent == IntentType.TICKET_QUERY and self.enable_tools:
            # 工单查询
            result = self.tool_router.call_tool("ticket", params, message)
            response_data.update(result)

        elif intent == IntentType.KNOWLEDGE_QUERY and self.enable_rag:
            # 知识库查询
            rag_result = self.rag_pipeline.query(
                query=message,
                top_k=3,
                use_rerank=True
            )
            response_data.update({
                "answer": rag_result["answer"],
                "contexts": rag_result["contexts"],
                "context_count": rag_result["context_count"]
            })

        else:
            # 默认直接回答
            response_data["answer"] = "抱歉，我暂时无法处理您的请求。"

        # 5. 更新记忆
        if self.short_memory:
            self.short_memory.add_turn(message, response_data["answer"])

        if self.long_memory and self.user_id:
            # 记录用户查询主题
            self.long_memory.update_memory(
                self.user_id,
                topic=intent.value,
                last_question=message
            )

        return response_data

    def _format_history(self, history: list) -> str:
        """格式化历史对话"""
        formatted = []
        for turn in history:
            formatted.append(f"用户: {turn['user']}")
            formatted.append(f"助手: {turn['assistant']}")
        return "\n".join(formatted)

    def get_conversation_history(self) -> list:
        """获取当前会话历史"""
        if self.short_memory:
            return self.short_memory.get_history()
        return []

    def clear_memory(self) -> None:
        """清除当前会话记忆"""
        if self.short_memory:
            self.short_memory.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取 Agent 统计信息"""
        stats = {
            "memory_enabled": self.enable_memory,
            "rag_enabled": self.enable_rag,
            "tools_enabled": self.enable_tools,
        }

        if self.rag_pipeline:
            stats["rag_stats"] = self.rag_pipeline.get_stats()

        if self.short_memory:
            stats["history_length"] = len(self.short_memory.get_history())

        return stats
