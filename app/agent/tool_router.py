# -*- coding: utf-8 -*-
"""工具路由器模块

负责根据意图调用相应的工具（订单查询、工单查询等）。
"""

from typing import Dict, Any, Optional, Callable
import re

from ..tools.order_tool import OrderTool
from ..tools.ticket_tool import TicketTool


class ToolRouter:
    """工具路由器

    管理所有可用工具，根据参数路由到具体工具执行。
    """

    def __init__(self):
        """初始化工具路由器"""
        # 初始化工具实例
        self.order_tool = OrderTool()
        self.ticket_tool = TicketTool()

        # 工具注册表
        self.tools: Dict[str, Callable] = {
            "order": self._handle_order_query,
            "ticket": self._handle_ticket_query,
        }

    def call_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        original_query: str
    ) -> Dict[str, Any]:
        """
        调用指定工具

        Args:
            tool_name: 工具名称
            params: 工具参数
            original_query: 原始查询（用于提取额外信息）

        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            return {
                "answer": f"未知的工具类型: {tool_name}",
                "tool_used": tool_name,
                "success": False
            }

        handler = self.tools[tool_name]
        return handler(params, original_query)

    def _handle_order_query(
        self,
        params: Dict[str, Any],
        original_query: str
    ) -> Dict[str, Any]:
        """
        处理订单查询

        Args:
            params: 参数（可能包含 order_id）
            original_query: 原始查询

        Returns:
            订单查询结果
        """
        order_id = params.get("order_id")

        # 如果没提取到订单号，尝试从查询中再次提取
        if not order_id:
            order_id = self._extract_order_id(original_query)

        if not order_id:
            return {
                "answer": "请提供订单号，例如：我的订单 12345 什么时候发货？",
                "tool_used": "order",
                "success": False,
                "missing_param": "order_id"
            }

        # 调用订单工具
        result = self.order_tool.get_order_status(order_id)

        if result["success"]:
            order_info = result["data"]
            answer = self._format_order_response(order_info)
            return {
                "answer": answer,
                "tool_used": "order",
                "success": True,
                "data": order_info
            }
        else:
            return {
                "answer": f"抱歉，未找到订单 {order_id} 的信息。请检查订单号是否正确。",
                "tool_used": "order",
                "success": False,
                "error": result.get("error")
            }

    def _handle_ticket_query(
        self,
        params: Dict[str, Any],
        original_query: str
    ) -> Dict[str, Any]:
        """
        处理工单查询

        Args:
            params: 参数（可能包含 ticket_id）
            original_query: 原始查询

        Returns:
            工单查询结果
        """
        ticket_id = params.get("ticket_id")

        # 如果没提取到工单号，尝试从查询中再次提取
        if not ticket_id:
            ticket_id = self._extract_ticket_id(original_query)

        if not ticket_id:
            return {
                "answer": "请提供工单号，例如：我的工单 67890 处理得怎么样了？",
                "tool_used": "ticket",
                "success": False,
                "missing_param": "ticket_id"
            }

        # 调用工单工具
        result = self.ticket_tool.get_ticket_status(ticket_id)

        if result["success"]:
            ticket_info = result["data"]
            answer = self._format_ticket_response(ticket_info)
            return {
                "answer": answer,
                "tool_used": "ticket",
                "success": True,
                "data": ticket_info
            }
        else:
            return {
                "answer": f"抱歉，未找到工单 {ticket_id} 的信息。请检查工单号是否正确。",
                "tool_used": "ticket",
                "success": False,
                "error": result.get("error")
            }

    def _extract_order_id(self, query: str) -> Optional[str]:
        """从查询中提取订单号"""
        # 匹配各种格式的订单号
        patterns = [
            r'订单[\s号]*([A-Za-z\d]+)',
            r'order[\s#]*([A-Za-z\d]+)',
            r'#([A-Za-z\d]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_ticket_id(self, query: str) -> Optional[str]:
        """从查询中提取工单号"""
        # 匹配各种格式的工单号
        patterns = [
            r'工单[\s号]*([A-Za-z\d]+)',
            r'ticket[\s#]*([A-Za-z\d]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _format_order_response(self, order_info: Dict[str, Any]) -> str:
        """格式化订单响应"""
        order_id = order_info.get("order_id", "未知")
        status = order_info.get("status", "未知")
        product = order_info.get("product_name", "未知商品")
        create_time = order_info.get("create_time", "")
        update_time = order_info.get("update_time", "")

        status_descriptions = {
            "pending": "待处理",
            "confirmed": "已确认",
            "processing": "处理中",
            "shipped": "已发货",
            "delivered": "已送达",
            "cancelled": "已取消",
            "refunded": "已退款"
        }

        status_cn = status_descriptions.get(status, status)

        response = f"订单 {order_id} 的状态是：**{status_cn}**\n\n"
        response += f"商品：{product}\n"

        if create_time:
            response += f"下单时间：{create_time}\n"
        if update_time and update_time != create_time:
            response += f"更新时间：{update_time}\n"

        # 根据状态添加额外信息
        if status == "shipped":
            tracking = order_info.get("tracking_number")
            if tracking:
                response += f"\n快递单号：{tracking}"
        elif status == "delivered":
            response += "\n订单已完成，感谢您的购买！"
        elif status == "pending":
            response += "\n订单正在等待确认，请耐心等待。"

        return response

    def _format_ticket_response(self, ticket_info: Dict[str, Any]) -> str:
        """格式化工单响应"""
        ticket_id = ticket_info.get("ticket_id", "未知")
        status = ticket_info.get("status", "未知")
        subject = ticket_info.get("subject", "无主题")
        priority = ticket_info.get("priority", "normal")
        create_time = ticket_info.get("create_time", "")
        update_time = ticket_info.get("update_time", "")

        status_descriptions = {
            "open": "待处理",
            "in_progress": "处理中",
            "waiting_customer": "等待客户回复",
            "resolved": "已解决",
            "closed": "已关闭"
        }

        priority_descriptions = {
            "low": "低",
            "normal": "普通",
            "high": "高",
            "urgent": "紧急"
        }

        status_cn = status_descriptions.get(status, status)
        priority_cn = priority_descriptions.get(priority, priority)

        response = f"工单 {ticket_id} 的状态是：**{status_cn}**\n\n"
        response += f"主题：{subject}\n"
        response += f"优先级：{priority_cn}\n"

        if create_time:
            response += f"创建时间：{create_time}\n"
        if update_time and update_time != create_time:
            response += f"更新时间：{update_time}\n"

        # 根据状态添加额外信息
        if status == "resolved":
            response += "\n您的问题已解决，如有其他问题欢迎随时联系。"
        elif status == "in_progress":
            response += "\n技术团队正在处理您的问题，请耐心等待。"
        elif status == "waiting_customer":
            response += "\n需要您提供更多信息，请回复工单补充说明。"

        return response

    def get_available_tools(self) -> list:
        """获取可用工具列表"""
        return [
            {
                "name": "order",
                "description": "查询订单状态和详情",
                "params": ["order_id"]
            },
            {
                "name": "ticket",
                "description": "查询工单状态和进度",
                "params": ["ticket_id"]
            }
        ]
