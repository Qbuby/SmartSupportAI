# SmartSupport AI

## 企业级智能客服 Agent（RAG + Memory + Tool Calling）

---

# 一、项目简介

SmartSupport AI 是一个基于 **Agent架构 + RAG（Retrieval-Augmented Generation）** 的企业智能客服系统。

系统支持：

* 企业知识库问答
* 用户上下文记忆
* Tool调用（订单 / 工单）
* Agent决策
* Chunk策略管理
* 检索策略管理
* Rerank检索优化

该项目用于展示 **AI Agent工程能力**。

---

# 二、业务背景

SaaS企业客服需要处理大量问题：

* 产品使用
* API接入
* 技术文档
* 错误排查
* 订单查询
* 工单查询

传统流程：

```
用户提问
↓
客服查文档
↓
客服查后台
↓
回复
```

效率低。

企业希望构建：

**AI客服Agent**

能力包括：

1 RAG知识库
2 用户记忆
3 Tool调用
4 Agent推理

---

# 三、系统核心能力

系统包含：

### 1 RAG知识库

流程：

```
User Query
↓
Embedding
↓
Vector Search
↓
Rerank
↓
Context
↓
LLM Answer
```

---

### 2 Chunk策略管理

企业文档需要分块：

```
chunk_size = 500
chunk_overlap = 100
```

每个Chunk包含：

* title
* section
* source
* chunk_id

---

### 3 检索策略管理

系统采用：

Hybrid Search

```
Vector Search
+
Keyword Search
```

流程：

```
Query
↓
Embedding
↓
Vector Search
↓
Keyword Search
↓
Merge
↓
Rerank
↓
Top Context
```

---

### 4 Agent决策

Agent判断问题类型：

```
if query contains "订单":
    call order_tool

elif query contains "工单":
    call ticket_tool

else:
    use RAG
```

---

### 5 Tool Calling

订单工具：

```
get_order_status(order_id)
```

返回：

```
{
 "order_id":"12345",
 "status":"已发货"
}
```

工单工具：

```
get_ticket_status(ticket_id)
```

---

### 6 Memory系统

系统包含两种记忆。

---

短期记忆：

记录当前对话上下文。

保存：

```
最近5轮对话
```

---

长期记忆：

SQLite存储：

* user_id
* company
* frequently asked topics

---

# 四、系统架构

```
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
 │      ├── Chunk Manager
 │      ├── Retriever
 │      └── Reranker
 │
 └── Tool Router
        │
        ├── Order Tool
        └── Ticket Tool
```

---

# 五、技术架构

技术栈：

* Python
* FastAPI
* Chroma Vector Database
* SQLite
* BGE Embedding
* BGE Reranker