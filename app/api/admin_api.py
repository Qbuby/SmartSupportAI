# -*- coding: utf-8 -*-
"""管理后台API模块

提供企业端管理后台所需的API接口：
- 文档管理（上传/列表/删除/预览）
- 配置管理（RAG/记忆策略CRUD）
- 统计API（对话统计/查询分析）
"""

import os
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..rag.chunker import Chunker
from ..rag.vector_store import VectorStore

# 创建路由
router = APIRouter(prefix="/api/admin", tags=["admin"])

# ============== 数据模型 ==============

class DocumentInfo(BaseModel):
    """文档信息"""
    id: str
    filename: str
    original_name: str
    file_type: str
    size: int
    status: str  # pending, processing, indexed, error
    chunk_count: Optional[int] = None
    created_at: str
    updated_at: str


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    total: int
    items: List[DocumentInfo]
    page: int
    page_size: int


class RAGConfig(BaseModel):
    """RAG配置"""
    chunk_strategy: dict = Field(default_factory=dict)
    retrieval_strategy: dict = Field(default_factory=dict)
    embedding: dict = Field(default_factory=dict)
    rerank: dict = Field(default_factory=dict)


class MemoryConfig(BaseModel):
    """记忆配置"""
    short_term_memory: dict = Field(default_factory=dict)
    long_term_memory: dict = Field(default_factory=dict)
    memory_topics: List[str] = Field(default_factory=list)


class OverviewStats(BaseModel):
    """概览统计"""
    total_conversations: int
    total_users: int
    total_documents: int
    today_conversations: int
    active_users_7d: int
    query_types: dict


class ConversationStats(BaseModel):
    """对话统计"""
    date: str
    count: int
    avg_response_time: Optional[float] = None


# ============== 全局状态（实际项目中应使用数据库）=============

# 文档存储路径
DOCS_STORAGE_PATH = Path("./data/uploaded_docs")
DOCS_STORAGE_PATH.mkdir(parents=True, exist_ok=True)

# 文档元数据存储（模拟数据库）
_documents_db: dict = {}

# 对话日志（用于统计）
_conversation_logs: list = []


# ============== 依赖注入 ==============

async def verify_admin_token():
    """验证管理员token（简化版，实际应使用JWT）"""
    # 简化处理：实际项目中应该验证Authorization header
    return {"admin": True}


# ============== 文档管理API ==============

@router.post("/documents/upload", response_model=DocumentInfo)
async def upload_document(
    file: UploadFile = File(...),
    admin: dict = Depends(verify_admin_token)
):
    """
    上传文档到知识库

    支持格式: .txt, .md, .pdf, .docx
    """
    # 验证文件类型
    allowed_extensions = {'.txt', '.md', '.pdf', '.docx'}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file_ext}"
        )

    # 生成文档ID
    doc_id = str(uuid.uuid4())[:8]

    # 保存文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    storage_name = f"{doc_id}_{timestamp}{file_ext}"
    file_path = DOCS_STORAGE_PATH / storage_name

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # 获取文件大小
        file_size = os.path.getsize(file_path)

        # 创建文档记录
        doc_info = DocumentInfo(
            id=doc_id,
            filename=storage_name,
            original_name=file.filename,
            file_type=file_ext,
            size=file_size,
            status="pending",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        _documents_db[doc_id] = doc_info.dict()

        # TODO: 触发后台任务进行文档处理和向量化

        return doc_info

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    admin: dict = Depends(verify_admin_token)
):
    """
    获取文档列表（支持分页和筛选）
    """
    items = list(_documents_db.values())

    # 状态筛选
    if status:
        items = [item for item in items if item["status"] == status]

    # 搜索
    if search:
        search_lower = search.lower()
        items = [
            item for item in items
            if search_lower in item["original_name"].lower()
        ]

    # 排序（按创建时间倒序）
    items.sort(key=lambda x: x["created_at"], reverse=True)

    # 分页
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = items[start:end]

    return DocumentListResponse(
        total=total,
        items=[DocumentInfo(**item) for item in paginated_items],
        page=page,
        page_size=page_size
    )


@router.get("/documents/{doc_id}", response_model=DocumentInfo)
async def get_document(
    doc_id: str,
    admin: dict = Depends(verify_admin_token)
):
    """获取文档详情"""
    if doc_id not in _documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    return DocumentInfo(**_documents_db[doc_id])


@router.get("/documents/{doc_id}/content")
async def get_document_content(
    doc_id: str,
    admin: dict = Depends(verify_admin_token)
):
    """获取文档内容（预览）"""
    if doc_id not in _documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    doc = _documents_db[doc_id]
    file_path = DOCS_STORAGE_PATH / doc["filename"]

    try:
        # 只支持文本文件预览
        if doc["file_type"] not in ['.txt', '.md']:
            return {"content": "[该文件类型不支持预览]", "type": doc["file_type"]}

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {"content": content, "type": doc["file_type"]}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"读取文件失败: {str(e)}"
        )


@router.get("/documents/{doc_id}/chunks")
async def get_document_chunks(
    doc_id: str,
    admin: dict = Depends(verify_admin_token)
):
    """获取文档分块详情"""
    if doc_id not in _documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    doc = _documents_db[doc_id]
    file_path = DOCS_STORAGE_PATH / doc["filename"]

    try:
        # 读取并分块
        if doc["file_type"] not in ['.txt', '.md']:
            return {"chunks": [], "message": "该文件类型不支持分块预览"}

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        chunker = Chunker()
        chunks = chunker.split_text(content, metadata={"source": doc["original_name"]})

        return {
            "chunks": [
                {
                    "id": chunk["chunk_id"],
                    "content": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
                    "length": len(chunk["content"])
                }
                for chunk in chunks
            ],
            "total_chunks": len(chunks)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分块处理失败: {str(e)}"
        )


@router.post("/documents/{doc_id}/reindex")
async def reindex_document(
    doc_id: str,
    admin: dict = Depends(verify_admin_token)
):
    """重新索引文档"""
    if doc_id not in _documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    doc = _documents_db[doc_id]
    doc["status"] = "processing"
    doc["updated_at"] = datetime.now().isoformat()

    # TODO: 触发重新索引任务

    return {"message": "重新索引任务已启动", "doc_id": doc_id}


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    admin: dict = Depends(verify_admin_token)
):
    """删除文档"""
    if doc_id not in _documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    doc = _documents_db[doc_id]
    file_path = DOCS_STORAGE_PATH / doc["filename"]

    try:
        # 删除文件
        if file_path.exists():
            os.remove(file_path)

        # 删除记录
        del _documents_db[doc_id]

        # TODO: 从向量库中删除相关文档

        return {"message": "文档已删除", "doc_id": doc_id}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}"
        )


# ============== 配置管理API ==============

@router.get("/config/rag", response_model=RAGConfig)
async def get_rag_config(admin: dict = Depends(verify_admin_token)):
    """获取RAG配置"""
    import yaml

    config_path = Path("config/rag_config.yaml")
    if not config_path.exists():
        return RAGConfig()

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        return RAGConfig(**config)
    except Exception:
        return RAGConfig()


@router.put("/config/rag")
async def update_rag_config(
    config: RAGConfig,
    admin: dict = Depends(verify_admin_token)
):
    """更新RAG配置"""
    import yaml

    config_path = Path("config/rag_config.yaml")

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config.dict(exclude_none=True), f, allow_unicode=True, default_flow_style=False)

        return {"message": "RAG配置已更新"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"配置保存失败: {str(e)}"
        )


@router.get("/config/memory", response_model=MemoryConfig)
async def get_memory_config(admin: dict = Depends(verify_admin_token)):
    """获取记忆配置"""
    import yaml

    config_path = Path("config/memory_config.yaml")
    if not config_path.exists():
        return MemoryConfig()

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        return MemoryConfig(**config)
    except Exception:
        return MemoryConfig()


@router.put("/config/memory")
async def update_memory_config(
    config: MemoryConfig,
    admin: dict = Depends(verify_admin_token)
):
    """更新记忆配置"""
    import yaml

    config_path = Path("config/memory_config.yaml")

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config.dict(exclude_none=True), f, allow_unicode=True, default_flow_style=False)

        return {"message": "记忆配置已更新"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"配置保存失败: {str(e)}"
        )


# ============== 统计API ==============

@router.get("/stats/overview", response_model=OverviewStats)
async def get_overview_stats(admin: dict = Depends(verify_admin_token)):
    """获取概览统计"""

    # 计算今日对话数
    today = datetime.now().date().isoformat()
    today_conversations = len([
        log for log in _conversation_logs
        if log["timestamp"].startswith(today)
    ])

    # 计算7天活跃用户数
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    active_users_7d = len(set([
        log["user_id"] for log in _conversation_logs
        if log["timestamp"] >= week_ago
    ]))

    # 查询类型分布（从日志统计）
    query_types = {}
    for log in _conversation_logs:
        intent = log.get("intent", "unknown")
        query_types[intent] = query_types.get(intent, 0) + 1

    return OverviewStats(
        total_conversations=len(_conversation_logs),
        total_users=len(set(log["user_id"] for log in _conversation_logs)),
        total_documents=len(_documents_db),
        today_conversations=today_conversations,
        active_users_7d=active_users_7d,
        query_types=query_types
    )


@router.get("/stats/conversations")
async def get_conversation_stats(
    days: int = Query(7, ge=1, le=90),
    admin: dict = Depends(verify_admin_token)
):
    """获取对话统计（按日期）"""

    # 生成日期范围
    end_date = datetime.now().date()
    dates = [(end_date - timedelta(days=i)).isoformat() for i in range(days)]
    dates.reverse()

    # 统计每日对话数
    stats = []
    for date in dates:
        count = len([
            log for log in _conversation_logs
            if log["timestamp"].startswith(date)
        ])
        stats.append({
            "date": date,
            "count": count
        })

    return {"stats": stats}


@router.get("/stats/queries")
async def get_query_stats(admin: dict = Depends(verify_admin_token)):
    """获取查询类型分布"""

    query_types = {}
    for log in _conversation_logs:
        intent = log.get("intent", "unknown")
        query_types[intent] = query_types.get(intent, 0) + 1

    # 转换为图表数据格式
    chart_data = [
        {"type": k, "count": v}
        for k, v in sorted(query_types.items(), key=lambda x: x[1], reverse=True)
    ]

    return {"distribution": chart_data}


@router.get("/stats/top-questions")
async def get_top_questions(
    limit: int = Query(10, ge=1, le=50),
    admin: dict = Depends(verify_admin_token)
):
    """获取热门问题"""

    from collections import Counter

    questions = [log["message"] for log in _conversation_logs if "message" in log]
    top_questions = Counter(questions).most_common(limit)

    return {
        "top_questions": [
            {"question": q, "count": c}
            for q, c in top_questions
        ]
    }


# ============== 日志API ==============

@router.get("/logs")
async def get_logs(
    level: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    admin: dict = Depends(verify_admin_token)
):
    """获取系统日志（简化版）"""

    # 返回最近的对话日志
    logs = _conversation_logs[-limit:]

    return {"logs": logs}


# ============== 工具函数 ==============

def log_conversation(user_id: str, message: str, intent: str = "unknown"):
    """记录对话日志（供chat_api调用）"""
    _conversation_logs.append({
        "user_id": user_id,
        "message": message,
        "intent": intent,
        "timestamp": datetime.now().isoformat()
    })

    # 限制日志数量
    if len(_conversation_logs) > 10000:
        _conversation_logs[:] = _conversation_logs[-5000:]