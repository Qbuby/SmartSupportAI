# -*- coding: utf-8 -*-
"""会话持久化存储模块

使用 SQLite 持久化存储会话历史，避免服务重启后数据丢失。
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

# 数据库路径
DB_PATH = Path("./data/sessions.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()

    # 会话表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        last_active TEXT NOT NULL,
        metadata TEXT
    )
    """)

    # 会话历史表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS session_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        metadata TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
    )
    """)

    # 创建索引
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_history_session_id ON session_history(session_id)
    """)

    conn.commit()
    conn.close()


class SessionStore:
    """会话存储类"""

    @staticmethod
    def create_session(session_id: str, user_id: str, metadata: Optional[Dict] = None) -> bool:
        """创建会话记录"""
        conn = get_db()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO sessions (session_id, user_id, created_at, last_active, metadata)
            VALUES (?, ?, ?, ?, ?)
            """, (session_id, user_id, now, now, json.dumps(metadata or {})))
            conn.commit()
            return True
        except Exception as e:
            print(f"创建会话记录失败: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def update_last_active(session_id: str) -> bool:
        """更新最后活跃时间"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""
            UPDATE sessions SET last_active = ? WHERE session_id = ?
            """, (datetime.now().isoformat(), session_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"更新会话活跃时间失败: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def add_message(session_id: str, role: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """添加消息到会话历史"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""
            INSERT INTO session_history (session_id, role, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
            """, (session_id, role, content, datetime.now().isoformat(), json.dumps(metadata or {})))
            conn.commit()
            # 同时更新会话的最后活跃时间
            SessionStore.update_last_active(session_id)
            return True
        except Exception as e:
            print(f"添加消息失败: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM sessions WHERE session_id = ?
        """, (session_id,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return SessionStore._row_to_dict(row)

    @staticmethod
    def get_history(session_id: str) -> List[Dict[str, Any]]:
        """获取会话历史"""
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM session_history
        WHERE session_id = ?
        ORDER BY timestamp ASC
        """, (session_id,))
        rows = cursor.fetchall()
        conn.close()

        return [SessionStore._history_row_to_dict(row) for row in rows]

    @staticmethod
    def list_sessions(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """列会话列表"""
        conn = get_db()
        cursor = conn.cursor()

        if user_id:
            cursor.execute("""
            SELECT * FROM sessions WHERE user_id = ? ORDER BY last_active DESC
            """, (user_id,))
        else:
            cursor.execute("""
            SELECT * FROM sessions ORDER BY last_active DESC
            """)

        rows = cursor.fetchall()
        conn.close()

        return [SessionStore._row_to_dict(row) for row in rows]

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """删除会话"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"删除会话失败: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def clear_old_sessions(days: int = 7) -> int:
        """清理旧的会话数据"""
        conn = get_db()
        cursor = conn.cursor()

        from datetime import timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        try:
            cursor.execute("""
            DELETE FROM sessions WHERE last_active < ?
            """, (cutoff_date,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"清理旧会话失败: {e}")
            return 0
        finally:
            conn.close()

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """将会话行转换为字典"""
        result = dict(row)
        if 'metadata' in result and result['metadata']:
            try:
                result['metadata'] = json.loads(result['metadata'])
            except:
                result['metadata'] = {}
        return result

    @staticmethod
    def _history_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """将历史记录行转换为字典"""
        result = dict(row)
        if 'metadata' in result and result['metadata']:
            try:
                result['metadata'] = json.loads(result['metadata'])
            except:
                result['metadata'] = {}
        return result


# 初始化数据库
init_db()
