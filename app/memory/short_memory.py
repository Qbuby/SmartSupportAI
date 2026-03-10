# -*- coding: utf-8 -*-
"""短期记忆模块

管理当前会话的对话历史，保存最近 N 轮对话。
"""

from typing import List, Dict, Any, Optional
import yaml
from collections import deque


class ShortMemory:
    """短期记忆（会话记忆）

    保存当前会话的最近 N 轮对话历史。
    当会话结束或超出长度限制时，历史会被清除。
    """

    def __init__(self, config_path: str = "config/memory_config.yaml"):
        """
        初始化短期记忆

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.max_history_length = self.config.get("short_term_memory", {}).get(
            "max_history_length", 5
        )

        # 使用双端队列存储对话历史
        self._history: deque = deque(maxlen=self.max_history_length * 2)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            # 使用默认配置
            return {
                "short_term_memory": {
                    "max_history_length": 5,
                    "enable_summary": False
                }
            }

    def add_turn(self, user_message: str, assistant_message: str) -> None:
        """
        添加一轮对话

        Args:
            user_message: 用户消息
            assistant_message: 助手回复
        """
        self._history.append({
            "role": "user",
            "content": user_message,
            "timestamp": self._get_timestamp()
        })
        self._history.append({
            "role": "assistant",
            "content": assistant_message,
            "timestamp": self._get_timestamp()
        })

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        获取格式化的对话历史

        Args:
            limit: 返回的最大轮数，None 表示全部

        Returns:
            对话历史列表，每项包含 user 和 assistant
        """
        history_list = list(self._history)
        turns = []

        # 按轮组织对话
        for i in range(0, len(history_list), 2):
            if i + 1 < len(history_list):
                turns.append({
                    "user": history_list[i]["content"],
                    "assistant": history_list[i + 1]["content"]
                })

        if limit:
            turns = turns[-limit:]

        return turns

    def get_raw_history(self) -> List[Dict[str, Any]]:
        """
        获取原始对话历史

        Returns:
            原始历史记录列表
        """
        return list(self._history)

    def get_last_user_message(self) -> Optional[str]:
        """获取最近的用户消息"""
        history_list = list(self._history)
        for item in reversed(history_list):
            if item["role"] == "user":
                return item["content"]
        return None

    def get_last_assistant_message(self) -> Optional[str]:
        """获取最近的助手回复"""
        history_list = list(self._history)
        for item in reversed(history_list):
            if item["role"] == "assistant":
                return item["content"]
        return None

    def clear(self) -> None:
        """清除所有历史记录"""
        self._history.clear()

    def is_empty(self) -> bool:
        """检查历史是否为空"""
        return len(self._history) == 0

    def get_turn_count(self) -> int:
        """获取当前对话轮数"""
        return len(self._history) // 2

    def get_context_for_prompt(self, max_turns: Optional[int] = None) -> str:
        """
        获取用于 LLM Prompt 的上下文格式

        Args:
            max_turns: 最大轮数限制

        Returns:
            格式化的对话历史字符串
        """
        turns = self.get_history(limit=max_turns)

        if not turns:
            return ""

        lines = ["【对话历史】"]
        for i, turn in enumerate(turns, 1):
            lines.append(f"第 {i} 轮：")
            lines.append(f"用户：{turn['user']}")
            lines.append(f"助手：{turn['assistant']}")
            lines.append("")

        return "\n".join(lines)

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于序列化）"""
        return {
            "max_history_length": self.max_history_length,
            "history": list(self._history),
            "turn_count": self.get_turn_count()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShortMemory":
        """从字典恢复实例"""
        instance = cls.__new__(cls)
        instance.max_history_length = data.get("max_history_length", 5)
        instance._history = deque(
            data.get("history", []),
            maxlen=instance.max_history_length * 2
        )
        return instance
