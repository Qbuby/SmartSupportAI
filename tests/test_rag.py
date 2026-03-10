# -*- coding: utf-8 -*-
"""RAG 功能测试脚本

测试 SmartSupport AI 的 RAG 核心功能。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.rag.chunker import Chunker
from app.rag.vector_store import VectorStore
from app.rag.retriever import Retriever
from app.rag.reranker import Reranker
from app.rag.rag_pipeline import RAGPipeline


def test_chunker():
    """测试文档分块功能"""
    print("\n" + "=" * 50)
    print("测试1: 文档分块")
    print("=" * 50)

    chunker = Chunker()

    # 测试文本
    test_text = """
# 欢迎使用 SmartSupport AI

这是一个测试文档，用于验证分块功能。

## 功能介绍

SmartSupport AI 是一个企业级智能客服系统。

1. RAG 知识库问答
2. 用户上下文记忆
3. Tool 调用支持

## 技术架构

系统使用以下技术：
- FastAPI
- ChromaDB
- BGE Embedding
"""

    chunks = chunker.split_text(test_text, metadata={"source": "test.md"})

    print(f"原文档长度: {len(test_text)} 字符")
    print(f"分块数量: {len(chunks)}")
    print(f"每块平均长度: {sum(len(c['content']) for c in chunks) / len(chunks):.0f} 字符")

    for i, chunk in enumerate(chunks[:3]):
        print(f"\n块 {i + 1} ({len(chunk['content'])} 字符):")
        print(f"  {chunk['content'][:80]}...")

    assert len(chunks) > 0, "分块失败"
    assert all('content' in c for c in chunks), "块缺少内容"
    assert all('chunk_id' in c for c in chunks), "块缺少 ID"
    print("\n文档分块测试通过!")


def test_vector_store():
    """测试向量存储功能"""
    print("\n" + "=" * 50)
    print("测试2: 向量存储")
    print("=" * 50)

    # 使用测试集合
    store = VectorStore(collection_name="test_collection")

    # 准备测试文档
    test_chunks = [
        {
            "content": "如何创建 API Key？",
            "chunk_id": "doc_1_0",
            "source": "api_guide.md",
            "title": "API 指南"
        },
        {
            "content": "API Key 是访问接口的凭证，可以在用户设置页面创建。",
            "chunk_id": "doc_1_1",
            "source": "api_guide.md",
            "title": "API 指南"
        },
        {
            "content": "如何申请退款？",
            "chunk_id": "doc_2_0",
            "source": "refund_policy.md",
            "title": "退款政策"
        },
        {
            "content": "如需退款，请在订单页面点击申请退款按钮。",
            "chunk_id": "doc_2_1",
            "source": "refund_policy.md",
            "title": "退款政策"
        }
    ]

    # 添加文档
    store.add_documents(test_chunks)

    # 检查统计
    stats = store.get_collection_stats()
    print(f"集合名称: {stats['collection_name']}")
    print(f"文档数量: {stats['document_count']}")

    assert stats['document_count'] == 4, f"文档数量错误: {stats['document_count']}"

    # 搜索测试
    print("\n搜索测试: 'API Key'")
    results = store.search("API Key", top_k=2)

    for i, r in enumerate(results):
        print(f"  {i + 1}. [{r['score']:.3f}] {r['content'][:40]}...")

    assert len(results) > 0, "搜索失败"
    assert results[0]['score'] > 0.5, "相关性分数过低"

    print("\n向量存储测试通过!")

    # 清理测试集合
    store.delete_collection()


def test_retriever():
    """测试检索器功能"""
    print("\n" + "=" * 50)
    print("测试3: 检索器")
    print("=" * 50)

    # 准备测试数据
    store = VectorStore(collection_name="test_retriever")

    chunks = [
        {"content": "Python 是一种编程语言", "chunk_id": "py_1", "source": "python.md"},
        {"content": "JavaScript 用于网页开发", "chunk_id": "js_1", "source": "js.md"},
        {"content": "Python 适合数据分析", "chunk_id": "py_2", "source": "python.md"},
        {"content": "TypeScript 是 JavaScript 的超集", "chunk_id": "ts_1", "source": "ts.md"},
    ]
    store.add_documents(chunks)

    # 创建检索器
    retriever = Retriever(store)

    # 向量检索
    print("向量检索: 'Python 编程'")
    results = retriever.vector_search("Python 编程", top_k=2)

    for r in results:
        print(f"  [{r['score']:.3f}] {r['content']}")

    assert len(results) == 2, "向量检索结果数量错误"
    assert any('Python' in r['content'] for r in results), "未找到 Python 相关内容"

    # 混合检索
    print("\n混合检索: 'JavaScript'")
    results = retriever.hybrid_search("JavaScript", top_k=2)

    for r in results:
        print(f"  [{r.get('score', 0):.3f}] {r['content']}")

    print("\n检索器测试通过!")

    # 清理
    store.delete_collection()


def test_reranker():
    """测试重排序功能"""
    print("\n" + "=" * 50)
    print("测试4: 重排序")
    print("=" * 50)

    reranker = Reranker()

    # 模拟检索结果
    query = "如何创建 API Key"
    documents = [
        {"content": "用户可以在设置页面创建 API Key", "id": "doc1"},
        {"content": "订单退款流程说明", "id": "doc2"},
        {"content": "API Key 是访问接口的凭证，在开发者中心创建", "id": "doc3"},
        {"content": "系统架构介绍", "id": "doc4"},
    ]

    print(f"查询: {query}")
    print("原始顺序:")
    for i, d in enumerate(documents):
        print(f"  {i + 1}. {d['content'][:30]}...")

    # 重排序
    reranked = reranker.rerank(query, documents, top_k=2)

    print("\n重排序后:")
    for i, d in enumerate(reranked):
        print(f"  {i + 1}. [{d['rerank_score']:.3f}] {d['content'][:30]}...")

    # 验证最相关的结果排在前面
    assert len(reranked) == 2, "重排序结果数量错误"
    assert 'API Key' in reranked[0]['content'], "最相关结果不是 API Key 相关内容"

    print("\n重排序测试通过!")


def test_rag_pipeline():
    """测试 RAG 完整流水线"""
    print("\n" + "=" * 50)
    print("测试5: RAG 流水线集成")
    print("=" * 50)

    # 创建流水线（使用测试集合）
    rag = RAGPipeline(collection_name="test_pipeline")

    # 添加测试文档
    documents = [
        {
            "content": """# SmartSupport AI 介绍

SmartSupport AI 是一个企业级智能客服系统。

主要功能包括：
1. RAG 知识库问答
2. 订单查询
3. 工单查询
4. 用户记忆""",
            "metadata": {"source": "intro.md", "title": "系统介绍"}
        },
        {
            "content": """# 订单查询功能

用户可以通过输入订单号查询订单状态。

支持的功能：
- 查看订单状态（待处理、已发货、已完成）
- 查看物流信息
- 申请退款""",
            "metadata": {"source": "order.md", "title": "订单功能"}
        },
        {
            "content": """# 工单系统

工单系统用于处理技术支持请求。

工单状态包括：
- 待处理
- 处理中
- 等待客户回复
- 已解决
- 已关闭""",
            "metadata": {"source": "ticket.md", "title": "工单系统"}
        }
    ]

    print("添加测试文档...")
    rag.add_documents(documents)

    stats = rag.get_stats()
    print(f"知识库统计: {stats}")

    # 测试检索
    print("\n检索测试: '订单状态'")
    contexts = rag.retrieve("订单状态", top_k=2)

    for i, ctx in enumerate(contexts):
        print(f"  {i + 1}. [{ctx.get('rerank_score', ctx.get('score', 0)):.3f}] {ctx['content'][:50]}...")

    assert len(contexts) > 0, "检索失败"

    print("\nRAG 流水线测试通过!")


if __name__ == "__main__":
    print("SmartSupport AI - RAG 功能测试")
    print("=" * 50)

    try:
        test_chunker()
        test_vector_store()
        test_retriever()
        test_reranker()
        test_rag_pipeline()

        print("\n" + "=" * 50)
        print("所有 RAG 测试通过!")
        print("=" * 50)

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
