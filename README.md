# SmartSupport AI

## 企业级智能客服 Agent（RAG + Agent + Memory + Tool Calling）

---

# 一、项目简介

SmartSupport AI 是一个基于 **Agent 架构 + RAG（Retrieval-Augmented Generation）** 的企业知识库智能客服系统。

系统用于模拟 SaaS 企业常见的智能客服场景，并支持企业级 AI 平台中常见的配置化能力，包括：

* RAG 知识库问答
* Agent任务决策
* 工具调用（Tool Calling）
* 用户上下文记忆
* **Chunk策略管理**
* **检索策略管理**
* **记忆策略管理**

系统目标是实现一个 **具备完整 AI Agent 架构能力的客服系统原型**，并且支持 **策略配置化管理**，模拟真实企业 AI 平台的能力。

---

# 二、业务背景

在 SaaS 企业中，客服团队需要回答大量重复问题，例如：

* 产品功能使用
* API 接入方式
* 价格方案
* 常见错误排查
* 技术文档查询
* 订单状态
* 工单处理进度

传统客服流程：

用户提问
↓
客服查文档
↓
客服查询内部系统
↓
返回结果

这种方式效率低、成本高。

因此企业希望构建 **AI 客服 Agent 系统**，具备以下能力：

1. 基于企业知识库回答问题（RAG）
2. 记住用户对话上下文（Memory）
3. 自动调用企业内部工具（Tool Calling）
4. 根据问题类型进行任务推理（Agent Reasoning）
5. 支持企业对 **RAG策略和记忆策略进行配置管理**

---

# 三、系统核心能力

系统需要实现以下核心能力。

---

# 1 RAG知识库问答

系统能够从企业文档中检索答案并生成回复。

流程：

User Query
↓
Query Embedding
↓
Vector Search
↓
Context Retrieval
↓
LLM Answer

---

# 2 Chunk策略管理（可配置）

企业可以配置文档分块策略，而不是写死在代码中。

Chunk策略用于控制：

* 文档切分方式
* Chunk大小
* 重叠长度
* Metadata信息

示例配置：

```id="1f5lq2"
chunk_strategy:
  chunk_size: 500
  chunk_overlap: 100
  split_method: "paragraph"
  metadata_fields:
    - title
    - section
    - source
```

系统需要支持企业修改这些策略，以优化检索效果。

Chunk流程：

Document
↓
Chunk Strategy
↓
Text Split
↓
Chunk Metadata
↓
Embedding

---

# 3 检索策略管理（可配置）

企业可以配置不同的检索策略。

支持以下策略：

* Vector Search
* Keyword Search
* Hybrid Search
* Rerank

示例配置：

```id="fl19q4"
retrieval_strategy:
  search_type: hybrid
  vector_top_k: 5
  keyword_top_k: 5
  rerank: true
```

系统流程：

User Query
↓
Embedding
↓
Vector Search
↓
Keyword Search
↓
Merge Results
↓
Rerank
↓
Top Context

企业可以根据业务需求调整检索参数。

---

# 4 Agent决策

Agent负责判断用户问题类型，并决定调用：

* RAG
* Tool
* LLM直接回答

决策逻辑示例：

```id="02u3d1"
if query contains "订单":
    call order_tool

elif query contains "工单":
    call ticket_tool

else:
    use RAG
```

未来可以扩展：

* LLM Intent Classification
* 多Agent协作

---

# 5 Tool Calling

系统支持调用企业内部工具。

需要实现两个示例工具：

---

## 订单查询工具

函数：

get_order_status(order_id)

返回示例：

```id="mwj0db"
{
 "order_id": "12345",
 "status": "已发货",
 "shipping_company": "SF Express"
}
```

---

## 工单查询工具

函数：

get_ticket_status(ticket_id)

返回示例：

```id="ewig7d"
{
 "ticket_id": "888",
 "status": "处理中",
 "assigned_to": "Support Team"
}
```

---

# 6 Memory系统

系统需要支持 **企业可配置的记忆管理策略**。

包括：

* 短期记忆（Session Memory）
* 长期记忆（User Memory）

---

## 短期记忆管理（可配置）

用于记录当前会话上下文。

企业可以配置：

```id="kzsjfl"
memory_strategy:
  session_history_length: 5
  enable_summary: true
```

功能：

* 保存最近 N 轮对话
* 支持上下文理解

示例：

User：如何创建API Key
Assistant：回答

User：这个Key有效多久

系统需要理解：

“这个Key” 指代 API Key。

---

## 长期记忆管理（可配置）

用于存储用户长期信息，例如：

* 用户ID
* 公司
* 常见问题
* 产品版本

示例配置：

```id="5vexi2"
long_memory:
  enabled: true
  storage: sqlite
  fields:
    - user_id
    - topic
    - last_question
```

数据存储：

SQLite。

---

# 四、系统架构

整体系统架构：

```id="6jv2sk"
User
 │
 ▼
API Gateway
 │
 ▼
Agent Controller
 │
 ├── Memory Manager
 │
 ├── RAG System
 │
 │     ├── Chunk Strategy Manager
 │     └── Retrieval Strategy Manager
 │
 └── Tool Router
        │
        ├── Order Tool
        └── Ticket Tool
```

---

# 五、技术架构

系统技术栈：

Python

OpenClaw Agent

LLM API

Chroma Vector Database

SQLite

FastAPI

SentenceTransformers (Embedding)

---
