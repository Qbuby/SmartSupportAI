# -*- coding: utf-8 -*-
"""长期记忆模块

管理用户的长期记忆信息，使用 SQLite 持久化存储。
记录用户的偏好、历史话题等信息。
"""

import os
import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import yaml
import json


class LongMemory:
    """长期记忆

    使用 SQLite 存储用户的长期信息，包括：
    - 用户基本信息
    - 历史查询话题
    - 频繁询问的主题
    """

    def __init__(self, config_path: str = "config/memory_config.yaml"):
        """
        初始化长期记忆

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        lt_config = self.config.get("long_term_memory", {})

        self.enabled = lt_config.get("enabled", True)
        self.db_path = lt_config.get("db_path", "./data/sqlite/memory.db")
        self.max_topics_per_user = lt_config.get("max_topics_per_user", 10)
        self.topic_expiry_days = lt_config.get("topic_expiry_days", 30)

        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # 初始化数据库
        self._init_database()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {
                "long_term_memory": {
                    "enabled": True,
                    "db_path": "./data/sqlite/memory.db",
                    "max_topics_per_user": 10,
                    "topic_expiry_days": 30
                }
            }

    def _init_database(self) -> None:
        """初始化数据库表结构"""
        if not self.enabled:
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 用户记忆主表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    topic TEXT,
                    last_question TEXT,
                    question_count INTEGER DEFAULT 1,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    UNIQUE(user_id, topic)
                )
            """)

            # 用户画像表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    user_id TEXT PRIMARY KEY,
                    company TEXT,
                    contact_email TEXT,
                    preferences TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 对话摘要表（可选的高级功能）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    summary TEXT,
                    key_points TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def update_memory(
        self,
        user_id: str,
        topic: Optional[str] = None,
        last_question: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新用户记忆

        Args:
            user_id: 用户 ID
            topic: 话题类型
            last_question: 最后提问内容
            metadata: 额外元数据

        Returns:
            是否成功
        """
        if not self.enabled or not user_id:
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 检查是否已存在该用户的该话题
                cursor.execute(
                    "SELECT id, question_count FROM user_memory WHERE user_id = ? AND topic = ?",
                    (user_id, topic)
                )
                result = cursor.fetchone()

                if result:
                    # 更新现有记录
                    memory_id, count = result
                    cursor.execute(
                        """
                        UPDATE user_memory
                        SET last_question = ?,
                            question_count = ?,
                            last_seen = CURRENT_TIMESTAMP,
                            metadata = ?
                        WHERE id = ?
                        """,
                        (
                            last_question or "",
                            count + 1,
                            json.dumps(metadata) if metadata else None,
                            memory_id
                        )
                    )
                else:
                    # 检查是否超过最大话题数
                    cursor.execute(
                        "SELECT COUNT(*) FROM user_memory WHERE user_id = ?",
                        (user_id,)
                    )
                    topic_count = cursor.fetchone()[0]

                    if topic_count >= self.max_topics_per_user:
                        # 删除最旧的话题
                        cursor.execute(
                            """
                            DELETE FROM user_memory
                            WHERE user_id = ? AND id = (
                                SELECT id FROM user_memory
                                WHERE user_id = ?
                                ORDER BY last_seen ASC
                                LIMIT 1
                            )
                            """,
                            (user_id, user_id)
                        )

                    # 插入新记录
                    cursor.execute(
                        """
                        INSERT INTO user_memory
                        (user_id, topic, last_question, metadata)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            user_id,
                            topic or "general",
                            last_question or "",
                            json.dumps(metadata) if metadata else None
                        )
                    )

                conn.commit()
                return True

        except sqlite3.Error as e:
            print(f"更新长期记忆失败: {e}")
            return False

    def get_user_memory(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户记忆

        Args:
            user_id: 用户 ID

        Returns:
            用户记忆信息
        """
        if not self.enabled or not user_id:
            return {}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # 获取用户所有话题
                cursor.execute(
                    """
                    SELECT topic, last_question, question_count,
                           first_seen, last_seen, metadata
                    FROM user_memory
                    WHERE user_id = ?
                    ORDER BY question_count DESC, last_seen DESC
                    """,
                    (user_id,)
                )

                topics = []
                for row in cursor.fetchall():
                    topics.append({
                        "topic": row["topic"],
                        "last_question": row["last_question"],
                        "question_count": row["question_count"],
                        "first_seen": row["first_seen"],
                        "last_seen": row["last_seen"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                    })

                # 获取用户画像
                cursor.execute(
                    "SELECT * FROM user_profile WHERE user_id = ?",
                    (user_id,)
                )
                profile_row = cursor.fetchone()

                profile = {}
                if profile_row:
                    profile = {
                        "company": profile_row["company"],
                        "contact_email": profile_row["contact_email"],
                        "preferences": json.loads(profile_row["preferences"]) if profile_row["preferences"] else {}
                    }

                return {
                    "user_id": user_id,
                    "topics": topics,
                    "profile": profile,
                    "total_interactions": sum(t["question_count"] for t in topics),
                    "frequent_topics": [t["topic"] for t in topics[:3]]
                }

        except sqlite3.Error as e:
            print(f"获取长期记忆失败: {e}")
            return {}

    def get_topics_by_type(self, user_id: str, topic: str) -> List[Dict[str, Any]]:
        """
        获取特定类型的历史话题

        Args:
            user_id: 用户 ID
            topic: 话题类型

        Returns:
            相关历史记录
        """
        if not self.enabled or not user_id:
            return []

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT last_question, question_count, last_seen
                    FROM user_memory
                    WHERE user_id = ? AND topic = ?
                    ORDER BY last_seen DESC
                    """,
                    (user_id, topic)
                )

                return [
                    {
                        "last_question": row["last_question"],
                        "question_count": row["question_count"],
                        "last_seen": row["last_seen"]
                    }
                    for row in cursor.fetchall()
                ]

        except sqlite3.Error as e:
            print(f"获取话题历史失败: {e}")
            return []

    def update_user_profile(
        self,
        user_id: str,
        company: Optional[str] = None,
        contact_email: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新用户画像

        Args:
            user_id: 用户 ID
            company: 公司名称
            contact_email: 联系邮箱
            preferences: 偏好设置

        Returns:
            是否成功
        """
        if not self.enabled or not user_id:
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO user_profile (user_id, company, contact_email, preferences)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        company = COALESCE(?, company),
                        contact_email = COALESCE(?, contact_email),
                        preferences = COALESCE(?, preferences),
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        user_id, company, contact_email,
                        json.dumps(preferences) if preferences else None,
                        company, contact_email,
                        json.dumps(preferences) if preferences else None
                    )
                )

                conn.commit()
                return True

        except sqlite3.Error as e:
            print(f"更新用户画像失败: {e}")
            return False

    def cleanup_expired_memories(self) -> int:
        """
        清理过期的记忆

        Returns:
            清理的记录数
        """
        if not self.enabled:
            return 0

        expiry_date = datetime.now() - timedelta(days=self.topic_expiry_days)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "DELETE FROM user_memory WHERE last_seen < ?",
                    (expiry_date.isoformat(),)
                )

                deleted = cursor.rowcount
                conn.commit()
                return deleted

        except sqlite3.Error as e:
            print(f"清理过期记忆失败: {e}")
            return 0

    def clear_user_memory(self, user_id: str) -> bool:
        """
        清除指定用户的所有记忆

        Args:
            user_id: 用户 ID

        Returns:
            是否成功
        """
        if not self.enabled or not user_id:
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "DELETE FROM user_memory WHERE user_id = ?",
                    (user_id,)
                )
                cursor.execute(
                    "DELETE FROM user_profile WHERE user_id = ?",
                    (user_id,)
                )

                conn.commit()
                return True

        except sqlite3.Error as e:
            print(f"清除用户记忆失败: {e}")
            return False
