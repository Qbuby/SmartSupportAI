# -*- coding: utf-8 -*-
"""文档分块模块

提供文档分块功能，支持多种分块策略。
"""

from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
import yaml


class Chunker:
    """文档分块器"""

    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """
        初始化分块器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.splitter = self._create_splitter()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config.get("chunk_strategy", {})

    def _create_splitter(self) -> RecursiveCharacterTextSplitter:
        """创建文本分割器"""
        chunk_size = self.config.get("chunk_size", 500)
        chunk_overlap = self.config.get("chunk_overlap", 100)
        separators = self.config.get("separators", ["\n\n", "\n", "。", "，", " ", ""])

        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False,
        )

    def split_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        将文本分割成块

        Args:
            text: 输入文本
            metadata: 元数据信息

        Returns:
            分块结果列表，每块包含内容和元数据
        """
        if metadata is None:
            metadata = {}

        chunks = self.splitter.split_text(text)

        result = []
        for idx, chunk in enumerate(chunks):
            chunk_info = {
                "content": chunk,
                "chunk_id": f"{metadata.get('source', 'doc')}_{idx}",
                "chunk_index": idx,
                **metadata
            }
            result.append(chunk_info)

        return result

    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量分割文档

        Args:
            documents: 文档列表，每篇包含 content 和 metadata

        Returns:
            所有分块结果
        """
        all_chunks = []
        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            chunks = self.split_text(content, metadata)
            all_chunks.extend(chunks)
        return all_chunks
