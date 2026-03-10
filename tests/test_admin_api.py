# -*- coding: utf-8 -*-
"""管理后台API测试脚本

测试 SmartSupport AI 管理后台API功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
import json

# API基础URL
BASE_URL = "http://127.0.0.1:8000"


def test_health():
    """测试健康检查"""
    print("\n" + "=" * 50)
    print("测试1: 健康检查")
    print("=" * 50)

    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("健康检查通过!")


def test_document_upload():
    """测试文档上传"""
    print("\n" + "=" * 50)
    print("测试2: 文档上传")
    print("=" * 50)

    # 创建测试文件
    test_content = """# 测试文档

这是一个用于测试的文档。

## 功能介绍

SmartSupport AI 是一个企业级智能客服系统。

主要功能：
1. RAG 知识库问答
2. 订单查询
3. 工单查询
"""

    test_file = Path("test_upload.md")
    test_file.write_text(test_content, encoding='utf-8')

    try:
        with open(test_file, 'rb') as f:
            files = {'file': ('test_upload.md', f, 'text/markdown')}
            response = requests.post(f"{BASE_URL}/api/admin/documents/upload", files=files)

        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"文档ID: {result.get('id')}")
        print(f"文件名: {result.get('original_name')}")
        print(f"状态: {result.get('status')}")

        assert response.status_code == 200
        assert result.get('id') is not None

        print("文档上传测试通过!")
        return result.get('id')

    finally:
        test_file.unlink(missing_ok=True)


def test_document_list():
    """测试文档列表"""
    print("\n" + "=" * 50)
    print("测试3: 文档列表")
    print("=" * 50)

    response = requests.get(f"{BASE_URL}/api/admin/documents")
    print(f"状态码: {response.status_code}")

    result = response.json()
    print(f"总数: {result.get('total')}")
    print(f"当前页: {result.get('page')}")
    print(f"文档数量: {len(result.get('items', []))}")

    for item in result.get('items', []):
        print(f"  - {item['original_name']} ({item['status']})")

    assert response.status_code == 200
    print("文档列表测试通过!")


def test_document_detail(doc_id):
    """测试文档详情"""
    print("\n" + "=" * 50)
    print("测试4: 文档详情")
    print("=" * 50)

    response = requests.get(f"{BASE_URL}/api/admin/documents/{doc_id}")
    print(f"状态码: {response.status_code}")

    result = response.json()
    print(f"文档ID: {result.get('id')}")
    print(f"文件名: {result.get('original_name')}")
    print(f"大小: {result.get('size')} bytes")

    assert response.status_code == 200
    print("文档详情测试通过!")


def test_document_content(doc_id):
    """测试文档内容预览"""
    print("\n" + "=" * 50)
    print("测试5: 文档内容预览")
    print("=" * 50)

    response = requests.get(f"{BASE_URL}/api/admin/documents/{doc_id}/content")
    print(f"状态码: {response.status_code}")

    result = response.json()
    content_preview = result.get('content', '')[:100]
    print(f"内容预览: {content_preview}...")

    assert response.status_code == 200
    print("文档内容预览测试通过!")


def test_document_chunks(doc_id):
    """测试文档分块"""
    print("\n" + "=" * 50)
    print("测试6: 文档分块详情")
    print("=" * 50)

    response = requests.get(f"{BASE_URL}/api/admin/documents/{doc_id}/chunks")
    print(f"状态码: {response.status_code}")

    result = response.json()
    print(f"总分块数: {result.get('total_chunks')}")

    for chunk in result.get('chunks', [])[:3]:
        print(f"  块 {chunk['id']}: {chunk['length']} 字符")

    assert response.status_code == 200
    print("文档分块测试通过!")


def test_rag_config():
    """测试RAG配置"""
    print("\n" + "=" * 50)
    print("测试7: RAG配置")
    print("=" * 50)

    # 获取配置
    response = requests.get(f"{BASE_URL}/api/admin/config/rag")
    print(f"获取配置状态码: {response.status_code}")
    print(f"当前配置: {json.dumps(response.json(), indent=2, ensure_ascii=False)[:200]}...")

    # 更新配置
    new_config = {
        "chunk_strategy": {
            "chunk_size": 800,
            "chunk_overlap": 150
        },
        "retrieval_strategy": {
            "search_type": "hybrid",
            "vector_top_k": 15,
            "rerank_top_k": 5
        }
    }

    response = requests.put(
        f"{BASE_URL}/api/admin/config/rag",
        json=new_config
    )
    print(f"更新配置状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    # 验证更新
    response = requests.get(f"{BASE_URL}/api/admin/config/rag")
    config = response.json()
    assert config['chunk_strategy']['chunk_size'] == 800

    print("RAG配置测试通过!")


def test_memory_config():
    """测试记忆配置"""
    print("\n" + "=" * 50)
    print("测试8: 记忆配置")
    print("=" * 50)

    # 获取配置
    response = requests.get(f"{BASE_URL}/api/admin/config/memory")
    print(f"获取配置状态码: {response.status_code}")
    print(f"当前配置: {json.dumps(response.json(), indent=2, ensure_ascii=False)[:200]}...")

    # 更新配置
    new_config = {
        "short_term_memory": {
            "max_history_length": 10,
            "enable_summary": True
        },
        "long_term_memory": {
            "enabled": True,
            "max_topics_per_user": 20
        }
    }

    response = requests.put(
        f"{BASE_URL}/api/admin/config/memory",
        json=new_config
    )
    print(f"更新配置状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    print("记忆配置测试通过!")


def test_stats():
    """测试统计API"""
    print("\n" + "=" * 50)
    print("测试9: 统计API")
    print("=" * 50)

    # 概览统计
    response = requests.get(f"{BASE_URL}/api/admin/stats/overview")
    print(f"概览统计状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    # 对话统计
    response = requests.get(f"{BASE_URL}/api/admin/stats/conversations?days=7")
    print(f"\n对话统计状态码: {response.status_code}")
    result = response.json()
    print(f"天数: {len(result.get('stats', []))}")

    # 查询类型分布
    response = requests.get(f"{BASE_URL}/api/admin/stats/queries")
    print(f"\n查询类型分布状态码: {response.status_code}")
    result = response.json()
    print(f"分布: {result.get('distribution')}")

    print("统计API测试通过!")


def test_document_delete(doc_id):
    """测试文档删除"""
    print("\n" + "=" * 50)
    print("测试10: 文档删除")
    print("=" * 50)

    response = requests.delete(f"{BASE_URL}/api/admin/documents/{doc_id}")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    assert response.status_code == 200

    # 验证删除
    response = requests.get(f"{BASE_URL}/api/admin/documents/{doc_id}")
    assert response.status_code == 404

    print("文档删除测试通过!")


if __name__ == "__main__":
    print("SmartSupport AI - 管理后台API测试")
    print("=" * 50)

    try:
        # 基础测试
        test_health()

        # 文档管理测试
        doc_id = test_document_upload()
        test_document_list()
        test_document_detail(doc_id)
        test_document_content(doc_id)
        test_document_chunks(doc_id)

        # 配置管理测试
        test_rag_config()
        test_memory_config()

        # 统计测试
        test_stats()

        # 清理
        test_document_delete(doc_id)

        print("\n" + "=" * 50)
        print("所有管理后台API测试通过!")
        print("=" * 50)

    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到服务器。请先启动服务:")
        print("  uvicorn app.api.chat_api:app --reload")
        sys.exit(1)
    except AssertionError as e:
        print(f"\n测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
