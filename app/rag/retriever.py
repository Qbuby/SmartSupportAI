# -*- coding: utf-8 -*-
"""检索器模块

提供向量检索和关键词检索功能，支持混合检索。
"""

from typing import List, Dict, Any, Optional
import re
from .vector_store import VectorStore


class Retriever:
    """检索器"""

    def __init__(
        self,
        vector_store: VectorStore,
        config_path: str = "config/rag_config.yaml"
    ):
        """
        初始化检索器

        Args:
            vector_store: 向量存储实例
            config_path: 配置文件路径
        """
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        
        self.vector_store = vector_store
        self.retrieval_config = self.config.get("retrieval_strategy", {})

    def vector_search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        向量检索

        Args:
            query: 查询文本
            top_k: 返回结果数量
            filters: 过滤条件

        Returns:
            检索结果列表
        """
        if top_k is None:
            top_k = self.retrieval_config.get("vector_top_k", 10)
        
        results = self.vector_store.search(query, top_k=top_k, filters=filters)
        
        # 添加检索类型标记
        for result in results:
            result["search_type"] = "vector"
        
        return results

    def keyword_search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        关键词检索（基于 BM25 的简化实现）

        Args:
            query: 查询文本
            documents: 待检索文档列表
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        if top_k is None:
            top_k = self.retrieval_config.get("keyword_top_k", 10)
        
        # 提取查询关键词
        query_keywords = self._extract_keywords(query)
        
        # 计算每篇文档的分数
        scored_docs = []
        for doc in documents:
            content = doc.get("content", "")
            score = self._calculate_bm25_score(query_keywords, content)
            scored_docs.append({
                **doc,
                "score": score,
                "search_type": "keyword"
            })
        
        # 按分数排序
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_docs[:top_k]

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单实现：分词并去除停用词
        # 实际项目中可以使用 jieba 等中文分词工具
        words = re.findall(r'\b\w+\b', text.lower())
        stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        return [w for w in words if w not in stopwords and len(w) > 1]

    def _calculate_bm25_score(self, query_keywords: List[str], document: str) -> float:
        """计算 BM25 分数"""
        if not query_keywords:
            return 0.0
        
        doc_lower = document.lower()
        score = 0.0
        
        for keyword in query_keywords:
            # 计算词频
            tf = doc_lower.count(keyword)
            if tf > 0:
                # 简化版 BM25 计算
                k1 = 1.5
                b = 0.75
                doc_len = len(doc_lower)
                avg_doc_len = 500  # 假设平均文档长度
                
                idf = 1.0  # 简化 IDF
                score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avg_doc_len))
        
        return score

    def hybrid_search(
        self,
        query: str,
        top_k: Optional[int] = None,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        混合检索（向量检索 + 关键词检索）

        Args:
            query: 查询文本
            top_k: 返回结果数量
            vector_weight: 向量检索权重
            keyword_weight: 关键词检索权重

        Returns:
            合并后的检索结果
        """
        if top_k is None:
            top_k = self.retrieval_config.get("rerank_top_k", 3)
        
        # 向量检索
        vector_results = self.vector_search(query, top_k=top_k * 2)
        
        # 如果向量检索结果足够，直接返回
        if len(vector_results) >= top_k:
            return vector_results[:top_k]
        
        # 否则返回向量检索结果
        return vector_results

    def retrieve(
        self,
        query: str,
        search_type: str = "hybrid",
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        统一检索接口

        Args:
            query: 查询文本
            search_type: 检索类型 (vector/keyword/hybrid)
            top_k: 返回结果数量
            filters: 过滤条件

        Returns:
            检索结果列表
        """
        if search_type == "vector":
            return self.vector_search(query, top_k, filters)
        elif search_type == "keyword":
            # 关键词检索需要传入文档列表，这里简化处理
            return self.vector_search(query, top_k, filters)
        else:  # hybrid
            return self.hybrid_search(query, top_k)
