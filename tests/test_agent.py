# -*- coding: utf-8 -*-
"""Agent 功能测试脚本

用于测试 SmartSupport AI 的核心功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.agent.agent_manager import AgentManager


def test_order_query():
    """测试订单查询"""
    print("\n" + "="*50)
    print("测试1: 订单查询")
    print("="*50)

    agent = AgentManager(
        user_id='test_user_001',
        enable_memory=True,
        enable_rag=False,  # 测试时暂时禁用RAG
        enable_tools=True
    )

    # 测试订单查询
    result = agent.chat('我的订单 12345 什么时候发货？')

    print(f"用户: 我的订单 12345 什么时候发货？")
    print(f"意图: {result['intent']}")
    print(f"工具: {result.get('tool_used', '无')}")
    print(f"回复: {result['answer'][:200]}...")

    assert result['intent'] == 'order_query', "意图识别失败"
    assert result.get('tool_used') == 'order', "工具调用失败"
    print("订单查询测试通过!")


def test_ticket_query():
    """测试工单查询"""
    print("\n" + "="*50)
    print("测试2: 工单查询")
    print("="*50)

    agent = AgentManager(
        user_id='test_user_002',
        enable_memory=True,
        enable_rag=False,
        enable_tools=True
    )

    result = agent.chat('帮我查一下工单 T-2025-0158 的状态')

    print(f"用户: 帮我查一下工单 T-2025-0158 的状态")
    print(f"意图: {result['intent']}")
    print(f"工具: {result.get('tool_used', '无')}")
    print(f"回复: {result['answer'][:200]}...")

    assert result['intent'] == 'ticket_query', "意图识别失败"
    assert result.get('tool_used') == 'ticket', "工具调用失败"
    print("工单查询测试通过!")


def test_memory():
    """测试记忆功能"""
    print("\n" + "="*50)
    print("测试3: 记忆功能")
    print("="*50)

    agent = AgentManager(
        user_id='test_user_003',
        enable_memory=True,
        enable_rag=False,
        enable_tools=True
    )

    # 第一轮对话
    agent.chat('我的订单 ORD-2025-001 状态如何？')

    # 第二轮对话（应该保留历史）
    agent.chat('那另一个订单 12345 呢？')

    # 获取历史
    history = agent.get_conversation_history()

    print(f"对话轮数: {len(history)}")
    for i, turn in enumerate(history, 1):
        print(f"  轮次 {i}: 用户: {turn['user'][:30]}...")

    assert len(history) == 2, "历史记录数量不对"
    print("记忆功能测试通过!")


def test_intent_detection():
    """测试意图识别"""
    print("\n" + "="*50)
    print("测试4: 意图识别")
    print("="*50)

    agent = AgentManager(enable_memory=False, enable_rag=False, enable_tools=True)

    test_cases = [
        ("我的订单 12345", "order_query"),
        ("查询订单状态", "order_query"),
        ("工单 67890 怎么样了", "ticket_query"),
        ("技术支持单号 TICKET-001", "ticket_query"),
        ("如何创建 API Key", "knowledge_query"),
        ("你们产品多少钱", "knowledge_query"),
    ]

    for query, expected_intent in test_cases:
        intent, params = agent.detect_intent(query)
        status = "OK" if intent.value == expected_intent else "FAIL"
        print(f"  [{status}] '{query[:20]}...' -> {intent.value}")

    print("意图识别测试完成!")


if __name__ == "__main__":
    print("SmartSupport AI - 功能测试")
    print("="*50)

    try:
        test_order_query()
        test_ticket_query()
        test_memory()
        test_intent_detection()

        print("\n" + "="*50)
        print("所有测试通过!")
        print("="*50)

    except AssertionError as e:
        print(f"\n测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
