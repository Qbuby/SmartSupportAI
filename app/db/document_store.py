# -*- coding: utf-8 -*-
"""文档元数据持久化存储模块

使用 SQLite 持久化存储文档元数据，避免服务重启后数据丢失。
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

# 数据库路径
DB_PATH = Path("./data/documents.db")
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        original_name TEXT NOT NULL,
        file_type TEXT NOT NULL,
        size INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        chunk_count INTEGER,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        metadata TEXT
    )
    """)

    conn.commit()
    conn.close()


class DocumentStore:
    """文档存储类"""

    @staticmethod
    def create(doc: Dict[str, Any]) -> Dict[str, Any]:
        """创建文档记录"""
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO documents (id, filename, original_name, file_type, size, status, chunk_count, created_at, updated_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc['id'],
            doc['filename'],
            doc['original_name'],
            doc['file_type'],
            doc['size'],
            doc.get('status', 'pending'),
            doc.get('chunk_count'),
            doc['created_at'],
            doc['updated_at'],
            json.dumps(doc.get('metadata', {}))
        ))

        conn.commit()
        conn.close()
        return doc

    @staticmethod
    def get(doc_id: str) -> Optional[Dict[str, Any]]:
        """获取单个文档"""
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return DocumentStore._row_to_dict(row)

    @staticmethod
    def list_all(status: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出所有文档"""
        conn = get_db()
        cursor = conn.cursor()

        query = "SELECT * FROM documents WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if search:
            query += " AND original_name LIKE ?"
            params.append(f"%{search}%")

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [DocumentStore._row_to_dict(row) for row in rows]

    @staticmethod
    def update(doc_id: str, updates: Dict[str, Any]) -> bool:
        """更新文档记录"""
        conn = get_db()
        cursor = conn.cursor()

        # 构建更新语句
        fields = []
        values = []

        for key, value in updates.items():
            if key == 'metadata' and isinstance(value, dict):
                value = json.dumps(value)
            fields.append(f"{key} = ?")
            values.append(value)

        if not fields:
            return False

        values.append(doc_id)
        query = f"UPDATE documents SET {', '.join(fields)} WHERE id = ?"

        cursor.execute(query, values)
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()

        return updated

    @staticmethod
    def delete(doc_id: str) -> bool:
        """删除文档记录"""
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()

        return deleted

    @staticmethod
    def count_by_status(status: Optional[str] = None) -> int:
        """统计文档数量"""
        conn = get_db()
        cursor = conn.cursor()

        if status:
            cursor.execute("SELECT COUNT(*) FROM documents WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT COUNT(*) FROM documents")

        count = cursor.fetchone()[0]
        conn.close()
        return count

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """将数据库行转换为字典"""
        result = dict(row)
        if 'metadata' in result and result['metadata']:
            try:
                result['metadata'] = json.loads(result['metadata'])
            except:
                result['metadata'] = {}
        return result


# 初始化数据库
init_db()
