# -*- coding: utf-8 -*-
"""订单工具模块

模拟企业内部订单系统，提供订单查询功能。
"""

import random
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class OrderTool:
    """订单查询工具

    模拟企业订单系统的查询接口。
    """

    # 订单状态定义
    ORDER_STATUSES = [
        "pending",      # 待处理
        "confirmed",    # 已确认
        "processing",   # 处理中
        "shipped",      # 已发货
        "delivered",    # 已送达
        "cancelled",    # 已取消
        "refunded"      # 已退款
    ]

    # 示例商品数据
    SAMPLE_PRODUCTS = [
        "企业版 SaaS 服务（年度订阅）",
        "API 调用包（100万次）",
        "技术支持服务（高级版）",
        "云存储扩容包（1TB）",
        "数据分析模块授权",
        "定制化开发服务",
        "培训课程（企业内训）",
        "专属客户经理服务"
    ]

    def __init__(self):
        """初始化订单工具"""
        # 模拟订单数据库（实际项目中应连接真实数据库）
        self._mock_orders: Dict[str, Dict[str, Any]] = {}
        self._generate_mock_data()

    def _generate_mock_data(self):
        """生成模拟订单数据"""
        # 创建一些示例订单用于测试
        sample_orders = [
            {
                "order_id": "12345",
                "status": "shipped",
                "product_name": "企业版 SaaS 服务（年度订阅）",
                "amount": 29999.00,
                "create_time": "2025-03-01T10:30:00",
                "update_time": "2025-03-05T14:20:00",
                "tracking_number": "SF1234567890"
            },
            {
                "order_id": "12346",
                "status": "delivered",
                "product_name": "API 调用包（100万次）",
                "amount": 5000.00,
                "create_time": "2025-02-15T09:00:00",
                "update_time": "2025-02-20T16:45:00",
                "tracking_number": None
            },
            {
                "order_id": "ORD-2025-001",
                "status": "processing",
                "product_name": "技术支持服务（高级版）",
                "amount": 15000.00,
                "create_time": "2025-03-08T11:20:00",
                "update_time": "2025-03-08T11:20:00",
                "tracking_number": None
            },
            {
                "order_id": "A10086",
                "status": "pending",
                "product_name": "云存储扩容包（1TB）",
                "amount": 1200.00,
                "create_time": "2025-03-10T16:00:00",
                "update_time": "2025-03-10T16:00:00",
                "tracking_number": None
            },
            {
                "order_id": "B202403001",
                "status": "cancelled",
                "product_name": "数据分析模块授权",
                "amount": 8000.00,
                "create_time": "2025-02-28T10:00:00",
                "update_time": "2025-03-01T09:30:00",
                "tracking_number": None
            }
        ]

        for order in sample_orders:
            self._mock_orders[order["order_id"]] = order

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        获取订单状态

        Args:
            order_id: 订单号

        Returns:
            订单信息或错误信息
        """
        if not order_id:
            return {
                "success": False,
                "error": "订单号不能为空"
            }

        # 模拟 API 延迟
        time.sleep(0.1)

        # 查询订单
        order = self._mock_orders.get(order_id)

        if order:
            return {
                "success": True,
                "data": order
            }

        # 如果订单不存在，生成一个随机订单（用于演示）
        if self._is_valid_order_format(order_id):
            new_order = self._generate_random_order(order_id)
            self._mock_orders[order_id] = new_order
            return {
                "success": True,
                "data": new_order
            }

        return {
            "success": False,
            "error": f"订单 {order_id} 不存在"
        }

    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """
        获取订单详细信息

        Args:
            order_id: 订单号

        Returns:
            订单详细信息
        """
        result = self.get_order_status(order_id)

        if not result["success"]:
            return result

        order_data = result["data"]

        # 添加更多详情
        order_data["customer_info"] = {
            "name": "示例客户",
            "company": "示例科技有限公司",
            "contact": "contact@example.com"
        }

        order_data["payment_info"] = {
            "method": "银行转账",
            "status": "已付款",
            "paid_time": order_data.get("create_time")
        }

        return {
            "success": True,
            "data": order_data
        }

    def list_orders(
        self,
        status: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        列出订单

        Args:
            status: 按状态筛选
            limit: 返回数量限制

        Returns:
            订单列表
        """
        orders = list(self._mock_orders.values())

        if status:
            orders = [o for o in orders if o["status"] == status]

        orders = orders[:limit]

        return {
            "success": True,
            "data": orders,
            "total": len(orders)
        }

    def _is_valid_order_format(self, order_id: str) -> bool:
        """检查订单号格式是否有效"""
        # 简单校验：至少包含一个数字，长度在 4-20 之间
        if not order_id or len(order_id) < 4 or len(order_id) > 20:
            return False

        has_digit = any(c.isdigit() for c in order_id)
        return has_digit

    def _generate_random_order(self, order_id: str) -> Dict[str, Any]:
        """生成随机订单数据"""
        status = random.choice(self.ORDER_STATUSES)
        product = random.choice(self.SAMPLE_PRODUCTS)

        # 生成随机时间
        days_ago = random.randint(1, 30)
        create_time = datetime.now() - timedelta(days=days_ago)
        update_time = create_time + timedelta(days=random.randint(0, days_ago))

        order = {
            "order_id": order_id,
            "status": status,
            "product_name": product,
            "amount": round(random.uniform(1000, 50000), 2),
            "create_time": create_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "update_time": update_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "tracking_number": None
        }

        # 如果状态是 shipped，添加快递单号
        if status == "shipped":
            order["tracking_number"] = f"SF{random.randint(1000000000, 9999999999)}"

        return order

    def create_order(
        self,
        product_name: str,
        amount: float,
        customer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建订单（模拟）

        Args:
            product_name: 商品名称
            amount: 金额
            customer_info: 客户信息

        Returns:
            创建的订单信息
        """
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        order = {
            "order_id": order_id,
            "status": "pending",
            "product_name": product_name,
            "amount": amount,
            "create_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "update_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "tracking_number": None,
            "customer_info": customer_info
        }

        self._mock_orders[order_id] = order

        return {
            "success": True,
            "data": order
        }
