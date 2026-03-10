# -*- coding: utf-8 -*-
"""工单工具模块

模拟企业内部工单系统，提供工单查询功能。
"""

import random
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta


class TicketTool:
    """工单查询工具

    模拟企业工单系统的查询接口（如技术支持、售后服务等）。
    """

    # 工单状态定义
    TICKET_STATUSES = [
        "open",             # 待处理
        "in_progress",      # 处理中
        "waiting_customer", # 等待客户回复
        "resolved",         # 已解决
        "closed"            # 已关闭
    ]

    # 工单优先级
    PRIORITIES = ["low", "normal", "high", "urgent"]

    # 示例工单主题
    SAMPLE_SUBJECTS = [
        "API 接口返回 500 错误",
        "无法登录管理后台",
        "数据导出功能异常",
        "需要增加用户账号",
        "系统访问速度很慢",
        "申请开通高级功能",
        "账单金额有疑问",
        "需要技术支持培训",
        "集成 SDK 遇到问题",
        "请求数据备份"
    ]

    # 示例工单描述
    SAMPLE_DESCRIPTIONS = [
        "从昨天开始，调用 /api/v1/orders 接口一直返回 500 错误，请尽快处理。",
        "使用正确的账号密码无法登录，提示'认证失败'，已尝试清除缓存。",
        "导出 Excel 报告时数据不完整，只显示前 100 条记录。",
        "新入职 5 名员工，需要创建系统访问账号。",
        "页面加载时间超过 10 秒，严重影响工作效率。",
        "希望开通数据分析模块和自动化报告功能。",
        "本月账单金额与合同约定不符，请核实。",
        "希望安排一次产品使用培训，约 10 人参加。",
        "按照文档集成时遇到回调签名验证失败的问题。",
        "需要导出过去一年的全部数据进行本地备份。"
    ]

    def __init__(self):
        """初始化工单工具"""
        # 模拟工单数据库
        self._mock_tickets: Dict[str, Dict[str, Any]] = {}
        self._generate_mock_data()

    def _generate_mock_data(self):
        """生成模拟工单数据"""
        sample_tickets = [
            # 原有5条工单
            {
                "ticket_id": "67890",
                "status": "in_progress",
                "subject": "API 接口返回 500 错误",
                "description": "从昨天开始，调用 /api/v1/orders 接口一直返回 500 错误...",
                "priority": "high",
                "assignee": "技术工程师-张三",
                "create_time": "2025-03-08T09:30:00",
                "update_time": "2025-03-09T14:20:00",
                "comments": [
                    {
                        "time": "2025-03-08T10:00:00",
                        "author": "技术工程师-张三",
                        "content": "已收到反馈，正在排查问题。"
                    }
                ]
            },
            {
                "ticket_id": "T-2025-0158",
                "status": "resolved",
                "subject": "无法登录管理后台",
                "description": "使用正确的账号密码无法登录...",
                "priority": "urgent",
                "assignee": "客服专员-李四",
                "create_time": "2025-03-05T16:45:00",
                "update_time": "2025-03-06T10:30:00",
                "comments": [
                    {
                        "time": "2025-03-05T17:00:00",
                        "author": "客服专员-李四",
                        "content": "已重置密码并发送邮件。"
                    },
                    {
                        "time": "2025-03-06T10:30:00",
                        "author": "用户",
                        "content": "已解决，可以正常登录了。"
                    }
                ]
            },
            {
                "ticket_id": "TK99999",
                "status": "open",
                "subject": "数据导出功能异常",
                "description": "导出 Excel 报告时数据不完整...",
                "priority": "normal",
                "assignee": None,
                "create_time": "2025-03-10T11:00:00",
                "update_time": "2025-03-10T11:00:00",
                "comments": []
            },
            {
                "ticket_id": "SUPPORT-00123",
                "status": "waiting_customer",
                "subject": "需要增加用户账号",
                "description": "新入职 5 名员工，需要创建系统访问账号...",
                "priority": "low",
                "assignee": "客服专员-王五",
                "create_time": "2025-03-07T10:00:00",
                "update_time": "2025-03-08T09:00:00",
                "comments": [
                    {
                        "time": "2025-03-08T09:00:00",
                        "author": "客服专员-王五",
                        "content": "请提供新员工的邮箱和姓名，我会尽快创建账号。"
                    }
                ]
            },
            {
                "ticket_id": "20240310001",
                "status": "closed",
                "subject": "系统访问速度很慢",
                "description": "页面加载时间超过 10 秒...",
                "priority": "high",
                "assignee": "运维工程师-赵六",
                "create_time": "2025-03-01T14:00:00",
                "update_time": "2025-03-02T16:00:00",
                "comments": [
                    {
                        "time": "2025-03-01T15:00:00",
                        "author": "运维工程师-赵六",
                        "content": "已完成服务器扩容。"
                    },
                    {
                        "time": "2025-03-02T16:00:00",
                        "author": "系统",
                        "content": "工单已关闭（超过24小时无回复）"
                    }
                ]
            },
            # 新增短编号工单（方便测试）
            {
                "ticket_id": "11",
                "status": "open",
                "subject": "账户余额显示异常",
                "description": "账户余额显示为负数，请核实。",
                "priority": "high",
                "assignee": "财务专员-小陈",
                "create_time": "2025-03-11T09:00:00",
                "update_time": "2025-03-11T09:00:00",
                "comments": []
            },
            {
                "ticket_id": "22",
                "status": "in_progress",
                "subject": "发票申请",
                "description": "需要开具上月服务费的增值税专用发票。",
                "priority": "normal",
                "assignee": "财务专员-小陈",
                "create_time": "2025-03-10T14:30:00",
                "update_time": "2025-03-11T10:00:00",
                "comments": [
                    {
                        "time": "2025-03-11T10:00:00",
                        "author": "财务专员-小陈",
                        "content": "已收到申请，正在处理中。"
                    }
                ]
            },
            {
                "ticket_id": "666",
                "status": "resolved",
                "subject": "API 限流咨询",
                "description": "想了解 API 调用的频率限制是多少。",
                "priority": "low",
                "assignee": "技术支持-小刘",
                "create_time": "2025-03-08T11:00:00",
                "update_time": "2025-03-08T16:00:00",
                "comments": [
                    {
                        "time": "2025-03-08T16:00:00",
                        "author": "技术支持-小刘",
                        "content": "已发送 API 文档，请参考限流章节。"
                    }
                ]
            },
            {
                "ticket_id": "8888",
                "status": "waiting_customer",
                "subject": "合同续签",
                "description": "服务即将到期，希望了解续签优惠政策。",
                "priority": "normal",
                "assignee": "客户经理-老周",
                "create_time": "2025-03-09T10:00:00",
                "update_time": "2025-03-10T15:00:00",
                "comments": [
                    {
                        "time": "2025-03-10T15:00:00",
                        "author": "客户经理-老周",
                        "content": "已发送续签方案，请查收邮件。"
                    }
                ]
            },
            {
                "ticket_id": "10086",
                "status": "closed",
                "subject": "数据迁移完成确认",
                "description": "历史数据迁移后需要确认完整性。",
                "priority": "urgent",
                "assignee": "数据工程师-小吴",
                "create_time": "2025-03-05T09:00:00",
                "update_time": "2025-03-06T18:00:00",
                "comments": [
                    {
                        "time": "2025-03-06T18:00:00",
                        "author": "数据工程师-小吴",
                        "content": "数据验证通过，迁移完成。"
                    }
                ]
            },
            {
                "ticket_id": "TK-001",
                "status": "open",
                "subject": "系统使用培训申请",
                "description": "新员工入职，需要安排系统使用培训。",
                "priority": "normal",
                "assignee": None,
                "create_time": "2025-03-11T08:00:00",
                "update_time": "2025-03-11T08:00:00",
                "comments": []
            },
            {
                "ticket_id": "TK-002",
                "status": "in_progress",
                "subject": "自定义报表需求",
                "description": "希望增加按区域统计的自定义报表功能。",
                "priority": "high",
                "assignee": "产品经理-小郑",
                "create_time": "2025-03-07T16:00:00",
                "update_time": "2025-03-09T11:00:00",
                "comments": [
                    {
                        "time": "2025-03-09T11:00:00",
                        "author": "产品经理-小郑",
                        "content": "需求已评估，排期在下个迭代。"
                    }
                ]
            },
            {
                "ticket_id": "TK-003",
                "status": "resolved",
                "subject": "密码重置",
                "description": "忘记管理员密码，需要重置。",
                "priority": "urgent",
                "assignee": "客服专员-李四",
                "create_time": "2025-03-10T09:30:00",
                "update_time": "2025-03-10T10:00:00",
                "comments": [
                    {
                        "time": "2025-03-10T10:00:00",
                        "author": "客服专员-李四",
                        "content": "已重置密码并短信通知。"
                    }
                ]
            },
            {
                "ticket_id": "2025-001",
                "status": "open",
                "subject": "集成 SDK 技术支持",
                "description": "移动端 SDK 集成过程中遇到问题，需要技术指导。",
                "priority": "high",
                "assignee": "技术工程师-张三",
                "create_time": "2025-03-11T10:30:00",
                "update_time": "2025-03-11T10:30:00",
                "comments": []
            },
            {
                "ticket_id": "2025-002",
                "status": "waiting_customer",
                "subject": "服务升级咨询",
                "description": "想了解从标准版升级到企业版的流程和费用。",
                "priority": "normal",
                "assignee": "客户经理-老周",
                "create_time": "2025-03-09T14:00:00",
                "update_time": "2025-03-10T09:00:00",
                "comments": [
                    {
                        "time": "2025-03-10T09:00:00",
                        "author": "客户经理-老周",
                        "content": "已发送升级方案和报价单。"
                    }
                ]
            }
        ]

        for ticket in sample_tickets:
            self._mock_tickets[ticket["ticket_id"]] = ticket

    def get_ticket_status(self, ticket_id: str) -> Dict[str, Any]:
        """
        获取工单状态

        Args:
            ticket_id: 工单号

        Returns:
            工单信息或错误信息
        """
        if not ticket_id:
            return {
                "success": False,
                "error": "工单号不能为空"
            }

        # 模拟 API 延迟
        time.sleep(0.1)

        # 查询工单
        ticket = self._mock_tickets.get(ticket_id)

        if ticket:
            return {
                "success": True,
                "data": ticket
            }

        # 如果工单不存在，生成一个随机工单
        if self._is_valid_ticket_format(ticket_id):
            new_ticket = self._generate_random_ticket(ticket_id)
            self._mock_tickets[ticket_id] = new_ticket
            return {
                "success": True,
                "data": new_ticket
            }

        return {
            "success": False,
            "error": f"工单 {ticket_id} 不存在"
        }

    def get_ticket_details(self, ticket_id: str) -> Dict[str, Any]:
        """
        获取工单详细信息（包含评论历史）

        Args:
            ticket_id: 工单号

        Returns:
            工单详细信息
        """
        result = self.get_ticket_status(ticket_id)

        if not result["success"]:
            return result

        # 基本信息已在 get_ticket_status 中返回
        return result

    def list_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        列出工单

        Args:
            status: 按状态筛选
            priority: 按优先级筛选
            limit: 返回数量限制

        Returns:
            工单列表
        """
        tickets = list(self._mock_tickets.values())

        if status:
            tickets = [t for t in tickets if t["status"] == status]

        if priority:
            tickets = [t for t in tickets if t["priority"] == priority]

        tickets = tickets[:limit]

        return {
            "success": True,
            "data": tickets,
            "total": len(tickets)
        }

    def create_ticket(
        self,
        subject: str,
        description: str,
        priority: str = "normal",
        customer_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建工单（模拟）

        Args:
            subject: 工单主题
            description: 工单描述
            priority: 优先级
            customer_info: 客户信息

        Returns:
            创建的工单信息
        """
        ticket_id = f"TK-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        ticket = {
            "ticket_id": ticket_id,
            "status": "open",
            "subject": subject,
            "description": description,
            "priority": priority,
            "assignee": None,
            "create_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "update_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "comments": [],
            "customer_info": customer_info or {}
        }

        self._mock_tickets[ticket_id] = ticket

        return {
            "success": True,
            "data": ticket
        }

    def add_comment(
        self,
        ticket_id: str,
        content: str,
        author: str = "用户"
    ) -> Dict[str, Any]:
        """
        添加工单评论

        Args:
            ticket_id: 工单号
            content: 评论内容
            author: 评论作者

        Returns:
            更新后的工单信息
        """
        ticket = self._mock_tickets.get(ticket_id)

        if not ticket:
            return {
                "success": False,
                "error": f"工单 {ticket_id} 不存在"
            }

        comment = {
            "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "author": author,
            "content": content
        }

        if "comments" not in ticket:
            ticket["comments"] = []

        ticket["comments"].append(comment)
        ticket["update_time"] = comment["time"]

        return {
            "success": True,
            "data": ticket
        }

    def _is_valid_ticket_format(self, ticket_id: str) -> bool:
        """检查工单号格式是否有效"""
        if not ticket_id or len(ticket_id) < 2 or len(ticket_id) > 20:
            return False
        return True

    def _generate_random_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """生成随机工单数据"""
        idx = random.randint(0, len(self.SAMPLE_SUBJECTS) - 1)
        subject = self.SAMPLE_SUBJECTS[idx]
        description = self.SAMPLE_DESCRIPTIONS[idx]
        status = random.choice(self.TICKET_STATUSES)
        priority = random.choice(self.PRIORITIES)

        # 生成随机时间
        days_ago = random.randint(1, 30)
        create_time = datetime.now() - timedelta(days=days_ago)
        update_time = create_time + timedelta(days=random.randint(0, days_ago))

        ticket = {
            "ticket_id": ticket_id,
            "status": status,
            "subject": subject,
            "description": description,
            "priority": priority,
            "assignee": random.choice(["技术工程师-张三", "客服专员-李四", "运维工程师-赵六", None]),
            "create_time": create_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "update_time": update_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "comments": []
        }

        return ticket
