# -*- coding: utf-8 -*-
"""向量存储模块

提供基于 ChromaDB 的向量存储功能。
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import yaml


class VectorStore:
    """向量存储器"""

    def __init__(
        self,
        collection_name: str = "knowledge_base",
        config_path: str = "config/rag_config.yaml",
    ):
        """
        初始化向量存储

        Args:
            collection_name: 集合名称
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.collection_name = collection_name
        
        # 初始化 embedding 模型
        self.embedding_model = self._init_embedding_model()
        
        # 初始化 ChromaDB 客户端
        self.client = self._init_chroma_client()
        
        # 获取或创建集合
        self.collection = self._get_or_create_collection()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config

    def _init_embedding_model(self) -> SentenceTransformer:
        """初始化 embedding 模型"""
        embedding_config = self.config.get("embedding", {})
        model_name = embedding_config.get("model_name", "BAAI/bge-small-zh")
        device = embedding_config.get("device", "cpu")
        
        print(f"正在加载 Embedding 模型: {model_name}...")
        model = SentenceTransformer(model_name, device=device)
        print("Embedding 模型加载完成")
        return model

    def _init_chroma_client(self) -> chromadb.Client:
        """初始化 ChromaDB 客户端"""
        # 从环境变量或配置获取路径
        db_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
        
        # 确保目录存在
        os.makedirs(db_path, exist_ok=True)
        
        client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )
        return client

    def _get_or_create_collection(self):
        """获取或创建集合"""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            print(f"使用已存在的集合: {self.collection_name}")
        except Exception:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"创建新集合: {self.collection_name}")
        return collection

    def encode_text(self, texts: List[str]) -> List[List[float]]:
        """
        将文本编码为向量

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        embedding_config = self.config.get("embedding", {})
        normalize = embedding_config.get("normalize_embeddings", True)
        
        embeddings = self.embedding_model.encode(
            texts,
            normalize_embeddings=normalize,
            show_progress_bar=len(texts) > 100
        )
        return embeddings.tolist()

    def add_documents(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> None:
        """
        添加文档块到向量库

        Args:
            chunks: 文档块列表
            batch_size: 批量大小
        """
        total = len(chunks)
        print(f"正在添加 {total} 个文档块到向量库...")
        
        for i in range(0, total, batch_size):
            batch = chunks[i:i + batch_size]
            
            # 准备数据
            texts = [chunk["content"] for chunk in batch]
            embeddings = self.encode_text(texts)
            
            ids = [chunk.get("chunk_id", f"chunk_{i + j}") for j, chunk in enumerate(batch)]
            metadatas = [
                {
                    "source": chunk.get("source", "unknown"),
                    "chunk_index": chunk.get("chunk_index", 0),
                    "title": chunk.get("title", ""),
                }
                for chunk in batch
            ]
            
            # 添加到集合
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"已添加 {min(i + batch_size, total)}/{total} 个文档块")
        
        print(f"成功添加 {total} 个文档块")

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索相似文档

        Args:
            query: 查询文本
            top_k: 返回结果数量
            filters: 过滤条件

        Returns:
            搜索结果列表
        """
        # 编码查询
        query_embedding = self.encode_text([query])[0]
        
        # 执行搜索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters,
            include=["documents", "metadatas", "distances"]
        )
        
        # 格式化结果
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "score": 1 - results["distances"][0][i]  # 转换为相似度分数
            })
        
        return formatted_results

    def delete_collection(self) -> None:
        """删除当前集合"""
        self.client.delete_collection(name=self.collection_name)
        print(f"已删除集合: {self.collection_name}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count
        }
