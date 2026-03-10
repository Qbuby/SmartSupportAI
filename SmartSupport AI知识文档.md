# SmartSupport AI 项目知识文档

## 1. 项目概述

SmartSupport AI 是一个企业级智能客服 Agent 系统，采用模块化架构设计，支持 RAG（检索增强生成）、多工具集成、短期/长期记忆等高级功能。

### 1.1 核心特性

- **智能对话**: 基于大语言模型的自然语言交互
- **RAG 知识检索**: 支持文档上传、分块、向量化和语义检索
- **多工具集成**: 订单查询、工单查询等业务工具
- **记忆系统**: 短期记忆保持对话上下文，长期记忆记录用户画像
- **企业级管理**: 支持知识库管理、配置管理、统计分析

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户交互层                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  用户端Web   │  │  企业端管理  │  │     管理后台API      │ │
│  │  (聊天界面)  │  │   (React)   │  │    (FastAPI)        │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────────┼────────────┘
          │                │                    │
          └────────────────┴────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │    Chat API       │
                    │   (FastAPI)       │
                    └─────────┬─────────┘
                              │
┌─────────────────────────────┼─────────────────────────────┐
│                         Agent 层                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                  Agent Manager                       │ │
│  │   (意图识别 → 任务路由 → 响应生成 → 记忆管理)        │ │
│  └─────────────────────┬───────────────────────────────┘ │
└────────────────────────┼──────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │ RAG模块 │    │ 工具路由 │    │ 记忆系统 │
    └─────────┘    └─────────┘    └─────────┘
```

### 2.2 核心模块

| 模块 | 路径 | 功能描述 |
|------|------|----------|
| Chat API | `app/api/chat_api.py` | FastAPI 主入口，提供对话接口 |
| Admin API | `app/api/admin_api.py` | 管理后台 API，文档/配置/统计管理 |
| Agent Manager | `app/agent/agent_manager.py` | Agent 核心控制器，协调各模块工作 |
| Tool Router | `app/agent/tool_router.py` | 工具路由，管理和调用业务工具 |
| Order Tool | `app/tools/order_tool.py` | 订单查询工具 |
| Ticket Tool | `app/tools/ticket_tool.py` | 工单查询工具 |
| Short Memory | `app/memory/short_memory.py` | 短期记忆管理（对话上下文） |
| Long Memory | `app/memory/long_memory.py` | 长期记忆管理（用户画像） |
| Chunker | `app/rag/chunker.py` | 文档分块处理 |
| Vector Store | `app/rag/vector_store.py` | 向量存储（ChromaDB） |
| Document Store | `app/db/document_store.py` | 文档元数据持久化（SQLite） |

---

## 3. 技术栈

### 3.1 后端

- **框架**: FastAPI (Python 3.9+)
- **向量数据库**: ChromaDB
- **关系数据库**: SQLite（文档元数据）
- **Embedding 模型**: BAAI/bge-small-zh
- **LLM**: Claude API / OpenAI API
- **文本分割**: LangChain Text Splitters

### 3.2 前端

- **框架**: React 18 + TypeScript
- **UI 组件**: Ant Design 5
- **构建工具**: Vite
- **路由**: React Router v6

### 3.3 项目结构

```
SmartSupportAI/
├── app/
│   ├── api/                 # API 层
│   │   ├── chat_api.py      # 主 API
│   │   └── admin_api.py     # 管理后台 API
│   ├── agent/               # Agent 核心
│   │   ├── agent_manager.py # Agent 管理器
│   │   └── tool_router.py   # 工具路由
│   ├── rag/                 # RAG 模块
│   │   ├── chunker.py       # 文档分块
│   │   └── vector_store.py  # 向量存储
│   ├── memory/              # 记忆系统
│   │   ├── short_memory.py  # 短期记忆
│   │   └── long_memory.py   # 长期记忆
│   ├── tools/               # 业务工具
│   │   ├── order_tool.py    # 订单工具
│   │   └── ticket_tool.py   # 工单工具
│   └── db/                  # 数据持久化
│       └── document_store.py # 文档存储
├── web/
│   ├── user-portal/         # 用户端 Web
│   └── admin-portal/        # 企业端管理后台
├── config/
│   └── rag_config.yaml      # RAG 配置
├── tests/                   # 测试用例
└── data/                    # 数据存储
    ├── chroma_db/           # 向量数据库
    ├── uploaded_docs/       # 上传的文档
    └── documents.db         # SQLite 数据库
```

---

## 4. 配置说明

### 4.1 RAG 配置 (config/rag_config.yaml)

```yaml
# Chunk 策略
chunk_strategy:
  chunk_size: 500           # 分块大小（字符数）
  chunk_overlap: 100        # 重叠大小
  separators:               # 分隔符优先级
    - "\n\n"                # 段落
    - "\n"                  # 换行
    - "。"                  # 句号
    - "，"                  # 逗号
    - " "                   # 空格
    - ""                    # 字符

# Embedding 配置
embedding:
  model_name: "BAAI/bge-small-zh"  # Embedding 模型
  device: "cpu"                    # 运行设备
  normalize_embeddings: true       # 是否归一化

# 检索策略
retrieval_strategy:
  top_k: 5                  # 检索结果数量
  score_threshold: 0.7      # 相似度阈值

# 重排序配置
rerank:
  enabled: false            # 是否启用重排序
  model: "cross-encoder/ms-marco-MiniLM-L-6-v2"
```

### 4.2 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ANTHROPIC_API_KEY` | Claude API 密钥 | - |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `CHROMA_DB_PATH` | ChromaDB 存储路径 | `./data/chroma_db` |

---

## 5. 使用指南

### 5.1 启动服务

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动后端 API
uvicorn app.api.chat_api:app --reload

# 3. 启动企业端管理后台
cd web/admin-portal
npm install
npm run dev

# 4. 启动用户端 (可选)
cd web/user-portal
npm install
npm run dev
```

### 5.2 API 接口

#### 对话接口

```http
POST /chat
Content-Type: application/json

{
  "user_id": "user_001",
  "message": "我想查询订单",
  "session_id": "session_001",
  "context": {}
}
```

#### 文档上传

```http
POST /api/admin/documents/upload
Content-Type: multipart/form-data

file: <文件内容>
```

#### 文档列表

```http
GET /api/admin/documents?page=1&page_size=20
```

### 5.3 管理后台功能

1. **知识库管理**
   - 上传文档（支持 .txt, .md, .pdf, .docx）
   - 查看文档列表和状态
   - 预览文档内容
   - 重新索引文档
   - 删除文档

2. **配置管理**
   - RAG 策略配置
   - 记忆策略配置

3. **统计分析**
   - 对话统计
   - 查询类型分布
   - 热门问题分析

---

## 6. 文档索引流程

```
上传文档
    │
    ▼
保存文件到 ./data/uploaded_docs/
    │
    ▼
创建文档记录（SQLite）
    │
    ▼
异步触发索引任务
    │
    ├─► 读取文件内容
    ├─► 文本分块（Chunker）
    ├─► 生成 Embeddings
    ├─► 存储到 ChromaDB
    │
    ▼
更新文档状态为 "indexed"
```

### 6.1 文档状态说明

| 状态 | 说明 |
|------|------|
| `pending` | 待处理，刚上传尚未开始索引 |
| `processing` | 处理中，正在进行分块和向量化 |
| `indexed` | 已索引，可以参与 RAG 检索 |
| `error` | 错误，索引过程中发生异常 |

---

## 7. 开发规范

### 7.1 代码风格

- 使用 Black 格式化代码
- 遵循 PEP 8 规范
- 使用类型注解

### 7.2 提交规范

```
feat: 新功能
fix: 修复问题
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

---

## 8. 注意事项

1. **数据持久化**
   - 文档元数据存储在 SQLite (`data/documents.db`)
   - 向量数据存储在 ChromaDB (`data/chroma_db/`)
   - 上传的文档存储在 `data/uploaded_docs/`

2. **Embedding 模型**
   - 首次使用会自动下载模型
   - 模型缓存目录：`~/.cache/torch/sentence_transformers/`

3. **内存管理**
   - 对话日志仅保留最近 10000 条
   - 向量化使用批处理（batch_size=100）

---

## 9. 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 文档索引失败 | Chunker 或 VectorStore 错误 | 查看终端错误日志，检查配置 |
| 重启后文档丢失 | 使用旧版本（内存存储） | 更新到最新代码（SQLite 存储）|
| Embedding 加载慢 | 首次下载模型 | 等待下载完成或使用已缓存模型 |
| 检索结果为空 | 向量库为空 | 确认文档已索引成功 |

---

## 10. 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v0.9.0 | 2026-03-11 | 完善 RAG 系统，添加文档持久化 |
| v0.8.0 | 2026-03-10 | 添加管理后台 API |
| v0.7.0 | 2026-03-09 | 实现 Agent 核心功能 |

---

**文档维护**: SmartSupport AI Team
**最后更新**: 2026-03-11
