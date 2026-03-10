# -*- coding: utf-8 -*-
"""重排序模块

提供基于 Cross-Encoder 的重排序功能。
"""

from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
import yaml


class Reranker:
    """重排序器"""

    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """
        初始化重排序器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.rerank_config = self.config.get("rerank", {})
        self.model = self._init_model()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config

    def _init_model(self) -> CrossEncoder:
        """初始化重排序模型"""
        model_name = self.rerank_config.get("model_name", "BAAI/bge-reranker-base")
        device = self.rerank_config.get("device", "cpu")
        
        print(f"正在加载 Rerank 模型: {model_name}...")
        model = CrossEncoder(model_name, device=device)
        print("Rerank 模型加载完成")
        return model

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        对检索结果进行重排序

        Args:
            query: 查询文本
            documents: 待排序文档列表
            top_k: 返回前 k 个结果

        Returns:
            重排序后的文档列表
        """
        if not documents:
            return []
        
        # 准备输入数据
        pairs = []
        for doc in documents:
            content = doc.get("content", "")
            pairs.append([query, content])
        
        # 计算相关性分数
        scores = self.model.predict(pairs)
        
        # 将分数添加到文档中
        for i, doc in enumerate(documents):
            doc["rerank_score"] = float(scores[i])
        
        # 按重排序分数排序
        sorted_docs = sorted(
            documents,
            key=lambda x: x["rerank_score"],
            reverse=True
        )
        
        return sorted_docs[:top_k]

    def rerank_with_threshold(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 3,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        带阈值的重排序

        Args:
            query: 查询文本
            documents: 待排序文档列表
            top_k: 返回前 k 个结果
            threshold: 相关性分数阈值

        Returns:
            重排序后的文档列表（只返回超过阈值的）
        """
        reranked = self.rerank(query, documents, top_k=len(documents))
        
        # 过滤低于阈值的结果
        filtered = [doc for doc in reranked if doc["rerank_score"] >= threshold]
        
        return filtered[:top_k]
