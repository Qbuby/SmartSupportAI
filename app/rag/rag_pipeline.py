# -*- coding: utf-8 -*-
"""RAG 流水线模块

整合分块、检索、重排序等功能，提供完整的 RAG 流程。
"""

from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI

from .chunker import Chunker
from .vector_store import VectorStore
from .retriever import Retriever
from .reranker import Reranker


class RAGPipeline:
    """RAG 流水线"""

    def __init__(
        self,
        config_path: str = "config/rag_config.yaml",
        collection_name: str = "knowledge_base"
    ):
        """
        初始化 RAG 流水线

        Args:
            config_path: 配置文件路径
            collection_name: 向量集合名称
        """
        # 加载环境变量
        load_dotenv()
        
        # 初始化 LLM 客户端
        self.llm_client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        )
        self.llm_model = os.getenv("LLM_MODEL", "deepseek-chat")
        
        # 初始化 RAG 组件
        self.chunker = Chunker(config_path)
        self.vector_store = VectorStore(collection_name, config_path)
        self.retriever = Retriever(self.vector_store, config_path)
        self.reranker = Reranker(config_path)

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        添加文档到知识库

        Args:
            documents: 文档列表，每个文档包含 content 和 metadata
        """
        # 分块
        chunks = self.chunker.split_documents(documents)
        print(f"文档分块完成，共 {len(chunks)} 个块")
        
        # 添加到向量库
        self.vector_store.add_documents(chunks)

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        use_rerank: bool = True
    ) -> List[Dict[str, Any]]:
        """
        检索相关文档

        Args:
            query: 查询文本
            top_k: 返回结果数量
            use_rerank: 是否使用重排序

        Returns:
            检索结果列表
        """
        # 首先进行向量检索（获取更多结果用于重排序）
        retrieval_top_k = top_k * 3 if use_rerank else top_k
        results = self.retriever.retrieve(
            query,
            search_type="vector",
            top_k=retrieval_top_k
        )
        
        if not use_rerank or not results:
            return results[:top_k]
        
        # 重排序
        reranked_results = self.reranker.rerank(query, results, top_k=top_k)
        return reranked_results

    def generate(
        self,
        query: str,
        contexts: List[Dict[str, Any]],
        temperature: float = 0.7
    ) -> str:
        """
        基于上下文生成回答

        Args:
            query: 用户查询
            contexts: 检索到的上下文
            temperature: 生成温度

        Returns:
            生成的回答
        """
        # 构建上下文文本
        context_text = "\n\n".join([
            f"[文档 {i+1}] {ctx.get('content', '')}"
            for i, ctx in enumerate(contexts)
        ])
        
        # 构建提示词
        system_prompt = """你是一个专业的企业智能客服助手。请基于提供的参考文档回答用户问题。
如果参考文档中没有相关信息，请明确告知用户无法回答。
请用中文回答，保持简洁专业。"""
        
        user_prompt = f"""参考文档：
{context_text}

用户问题：{query}

请基于以上参考文档回答问题。"""
        
        # 调用 LLM
        response = self.llm_client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=1000
        )
        
        return response.choices[0].message.content

    def query(
        self,
        query: str,
        top_k: int = 3,
        use_rerank: bool = True,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        完整的 RAG 查询流程

        Args:
            query: 用户查询
            top_k: 检索结果数量
            use_rerank: 是否使用重排序
            temperature: 生成温度

        Returns:
            包含回答和检索结果的字典
        """
        # 检索相关文档
        contexts = self.retrieve(query, top_k=top_k, use_rerank=use_rerank)
        
        # 生成回答
        answer = self.generate(query, contexts, temperature)
        
        return {
            "query": query,
            "answer": answer,
            "contexts": contexts,
            "context_count": len(contexts)
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        return self.vector_store.get_collection_stats()
