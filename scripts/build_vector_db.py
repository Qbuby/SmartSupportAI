# -*- coding: utf-8 -*-
"""构建向量数据库脚本

将知识库文档导入 ChromaDB 向量数据库。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.rag.rag_pipeline import RAGPipeline


def load_documents_from_directory(docs_dir: str) -> list:
    """
    从目录加载文档
    
    Args:
        docs_dir: 文档目录路径
        
    Returns:
        文档列表
    """
    documents = []
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        print(f"文档目录不存在: {docs_dir}")
        return documents
    
    # 支持的文件类型
    supported_extensions = {'.txt', '.md', '.markdown'}
    
    for file_path in docs_path.rglob('*'):
        if file_path.suffix.lower() in supported_extensions:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 构建相对路径作为 source
                relative_path = file_path.relative_to(docs_path)
                
                documents.append({
                    'content': content,
                    'metadata': {
                        'source': str(relative_path),
                        'title': file_path.stem,
                        'file_type': file_path.suffix.lower()
                    }
                })
                print(f"已加载文档: {relative_path}")
            except Exception as e:
                print(f"加载文档失败 {file_path}: {e}")
    
    return documents


def main():
    """主函数"""
    print("=" * 50)
    print("SmartSupport AI - 构建向量数据库")
    print("=" * 50)
    
    # 文档目录
    docs_dir = os.getenv("DOCS_DIR", "data/docs")
    
    # 检查文档目录
    if not os.path.exists(docs_dir):
        print(f"\n文档目录不存在: {docs_dir}")
        print("创建示例文档目录...")
        os.makedirs(docs_dir, exist_ok=True)
        
        # 创建示例文档
        example_doc = """# 欢迎使用 SmartSupport AI

这是一个示例文档，用于测试 RAG 系统的功能。

## 功能介绍

SmartSupport AI 是一个企业级智能客服系统，具备以下功能：

1. **RAG 知识库问答**: 基于企业知识库回答用户问题
2. **用户上下文记忆**: 记录用户对话历史
3. **Tool 调用**: 支持查询订单、工单等信息
4. **Agent 决策**: 智能判断用户意图并路由

## 快速开始

1. 将企业文档放入 data/docs 目录
2. 运行本脚本构建向量数据库
3. 启动 API 服务
4. 开始对话测试

## 支持的文档格式

- .txt - 纯文本文件
- .md - Markdown 文件
- .markdown - Markdown 文件

## 联系方式

如有问题，请联系技术支持团队。
"""
        example_path = os.path.join(docs_dir, "欢迎使用.txt")
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write(example_doc)
        print(f"已创建示例文档: {example_path}")
    
    # 加载文档
    print(f"\n正在从 {docs_dir} 加载文档...")
    documents = load_documents_from_directory(docs_dir)
    
    if not documents:
        print("\n没有找到任何文档，请先添加文档到 data/docs 目录")
        return
    
    print(f"\n共加载 {len(documents)} 个文档")
    
    # 初始化 RAG 流水线
    print("\n初始化 RAG 流水线...")
    try:
        rag = RAGPipeline()
    except Exception as e:
        print(f"初始化失败: {e}")
        print("\n可能的原因:")
        print("1. 缺少 DeepSeek API Key，请检查 .env 文件")
        print("2. 配置文件路径错误")
        return
    
    # 添加文档到向量库
    print("\n正在构建向量数据库...")
    print("-" * 50)
    rag.add_documents(documents)
    
    # 显示统计信息
    print("-" * 50)
    stats = rag.get_stats()
    print("\n向量数据库构建完成!")
    print(f"集合名称: {stats['collection_name']}")
    print(f"文档数量: {stats['document_count']}")
    print("\n现在可以启动 API 服务进行测试了:")
    print("  uvicorn app.api.chat_api:app --reload")


if __name__ == "__main__":
    main()
