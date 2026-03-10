# SmartSupport AI

<p align="center">
  <strong>企业级智能客服 Agent（RAG + Memory + Tool Calling）</strong>
</p>

<p align="center">
  <a href="#-核心功能">核心功能</a> •
  <a href="#-系统架构">系统架构</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-项目结构">项目结构</a> •
  <a href="#-api文档">API文档</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18+-61dafb.svg" alt="React">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

---

## 核心功能

### 后端能力

| 功能 | 描述 | 状态 |
|------|------|------|
| RAG知识库 | 基于向量检索的文档问答 | 完成 |
| Hybrid检索 | 向量+关键词混合搜索 | 完成 |
| Rerank排序 | Cross-Encoder重排序优化 | 完成 |
| Agent决策 | 意图识别与任务路由 | 完成 |
| Tool调用 | 订单/工单查询工具 | 完成 |
| 用户记忆 | 短期+长期记忆系统 | 完成 |
| 策略配置 | Chunk/检索/记忆策略管理 | 完成 |
| 会话持久化 | 会话历史持久化存储 | 完成 |

### Web端能力

| 功能 | 描述 | 状态 |
|------|------|------|
| 用户端 | 智能客服对话界面 | 完成 |
| 企业端 | 知识库管理后台 | 完成 |
| 数据监控 | 对话统计与日志 | 完成 |
| 策略配置 | 可视化配置管理 | 完成 |

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Frontend                             │
│  ┌──────────────┐              ┌──────────────────────┐         │
│  │  用户端       │              │      企业端           │         │
│  │  (React)     │              │      (React)         │         │
│  │              │              │                      │         │
│  │ • 聊天界面   │              │ • 知识库管理         │         │
│  │ • 会话管理   │              │ • 策略配置           │         │
│  │ • Markdown  │              │ • 数据统计           │         │
│  └──────────────┘              └──────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   Chat API       │    │   Admin API      │                  │
│  │   (对话服务)      │    │   (管理服务)      │                  │
│  └────────┬─────────┘    └──────────────────┘                  │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────────────────────────────────┐               │
│  │           Agent Controller                    │               │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │               │
│  │  │  Intent  │→ │  Router  │→ │  Handler │   │               │
│  │  │Detection │  │          │  │          │   │               │
│  │  └──────────┘  └──────────┘  └──────────┘   │               │
│  └────────┬────────────────────────────────────┘               │
│           │                                                      │
│     ┌─────┴─────┬─────────────┬─────────────┐                  │
│     ▼           ▼             ▼             ▼                  │
│  ┌──────┐  ┌────────┐   ┌──────────┐  ┌──────────┐           │
│  │ RAG  │  │ Memory │   │  Order   │  │  Ticket  │           │
│  │System│  │Manager │   │   Tool   │  │   Tool   │           │
│  └──────┘  └────────┘   └──────────┘  └──────────┘           │
│     │           │                                                  │
│     ▼           ▼                                                  │
│  ┌────────┐  ┌────────┐                                          │
│  │ChromaDB│  │SQLite  │                                          │
│  │(Vector)│  │(Memory)│                                          │
│  └────────┘  └────────┘                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/smartsupport-ai.git
cd smartsupport-ai
```

### 2. 配置环境

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# ANTHROPIC_API_KEY=your_api_key_here
# 或
# OPENAI_API_KEY=your_api_key_here
```

### 3. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装前端依赖（用户端）
cd web/user-portal
npm install

# 安装前端依赖（企业端）
cd ../admin-portal
npm install
```

### 4. 启动服务

```bash
# 启动后端 API（端口 8000）
uvicorn app.api.chat_api:app --reload

# 启动用户端（端口 5173）
cd web/user-portal
npm run dev

# 启动企业端（端口 5174）
cd web/admin-portal
npm run dev
```

### 5. 访问服务

- API文档: http://localhost:8000/docs
- 用户端: http://localhost:5173
- 企业端: http://localhost:5174

---

## 项目结构

```
smartsupport-ai/
├── app/                          # 后端应用
│   ├── agent/                    # Agent模块
│   │   ├── agent_manager.py      # Agent管理器
│   │   └── tool_router.py        # 工具路由
│   ├── api/                      # API接口
│   │   ├── chat_api.py           # 对话API
│   │   └── admin_api.py          # 管理API
│   ├── db/                       # 数据持久化
│   │   ├── document_store.py     # 文档存储
│   │   └── session_store.py      # 会话存储
│   ├── memory/                   # 记忆系统
│   │   ├── short_memory.py       # 短期记忆
│   │   └── long_memory.py        # 长期记忆
│   ├── rag/                      # RAG系统
│   │   ├── chunker.py            # 文档分块
│   │   └── vector_store.py       # 向量存储
│   └── tools/                    # 工具模块
│       ├── order_tool.py         # 订单工具
│       └── ticket_tool.py        # 工单工具
│
├── web/                          # 前端应用
│   ├── user-portal/              # 用户端
│   │   ├── src/
│   │   │   ├── components/       # 组件
│   │   │   ├── pages/            # 页面
│   │   │   └── api/              # API封装
│   │   └── package.json
│   └── admin-portal/             # 企业端
│       ├── src/
│       │   ├── pages/            # 页面
│       │   │   ├── Dashboard.tsx
│       │   │   ├── Knowledge.tsx
│       │   │   └── Settings.tsx
│       └── package.json
│
├── config/                       # 配置文件
│   └── rag_config.yaml           # RAG配置
│
├── data/                         # 数据目录
│   ├── chroma_db/                # 向量数据库
│   ├── uploaded_docs/            # 上传的文档
│   └── *.db                      # SQLite数据库
│
├── tests/                        # 测试用例
│   ├── test_agent.py
│   ├── test_rag.py
│   └── test_admin_api.py
│
├── README.md                     # 项目说明
├── SmartSupport AI.md            # 项目知识文档
├── 技术选型.md                    # 技术方案
├── 详细说明.md                    # 详细设计
└── requirements.txt              # Python依赖
```

---

## API文档

### 对话API

```http
POST /chat
Content-Type: application/json

{
  "user_id": "user_001",
  "message": "我的订单12345什么时候发货？",
  "session_id": "optional-session-id"
}
```

**响应:**
```json
{
  "success": true,
  "reply": "订单12345的状态是：已发货...",
  "intent": "order_query",
  "tool_used": "order",
  "session_id": "sess_xxx",
  "timestamp": "2025-03-11T12:00:00"
}
```

### 会话管理API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/sessions` | GET | 获取会话列表 |
| `/sessions/{id}/history` | GET | 获取会话历史 |
| `/sessions/{id}` | DELETE | 删除会话 |

### 管理API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/admin/documents` | GET | 获取文档列表 |
| `/api/admin/documents/upload` | POST | 上传文档 |
| `/api/admin/config/rag` | GET/PUT | RAG配置管理 |
| `/api/admin/config/memory` | GET/PUT | 记忆配置管理 |
| `/api/admin/stats/overview` | GET | 概览统计 |

完整API文档请访问: http://localhost:8000/docs

---

## 技术栈

### 后端
- **Python 3.10+**
- **FastAPI** - Web框架
- **ChromaDB** - 向量数据库
- **SQLite** - 关系数据库
- **BAAI/bge-small-zh** - Embedding模型
- **Claude API / OpenAI API** - LLM接口

### 前端
- **React 18** + **TypeScript**
- **Ant Design 5** - UI组件库
- **Vite** - 构建工具
- **Axios** - HTTP客户端

---

## 配置说明

### RAG配置 (`config/rag_config.yaml`)

```yaml
chunk_strategy:
  chunk_size: 500          # 分块大小
  chunk_overlap: 100       # 重叠大小
  separators: ["\n\n", "\n", "。", "，", " ", ""]

retrieval_strategy:
  search_type: hybrid      # 搜索类型
  top_k: 5                 # 检索数量

embedding:
  model_name: "BAAI/bge-small-zh"
  device: "cpu"
```

---

## 测试

```bash
# 运行Agent测试
python tests/test_agent.py

# 运行RAG测试
python tests/test_rag.py

# 运行管理API测试（需先启动服务）
python tests/test_admin_api.py
```

---

## 界面预览

### 用户端 - 智能客服对话
```
┌─────────────────────────────────────────────────────┐
│  SmartSupport AI                              [≡]   │
├────────────┬────────────────────────────────────────┤
│ [+ 新对话] │                                        │
│            │  助手：您好！有什么可以帮助您？          │
│ 会话历史   │                                        │
│ ├─ 会话1   │  用户：我的订单12345什么时候发货？      │
│ ├─ 会话2   │                                        │
│ └─ 会话3   │  助手：订单12345的状态是：已发货        │
└────────────┴────────────────────────────────────────┘
```

### 企业端 - 管理后台
```
┌─────────────────────────────────────────────────────────────┐
│  SmartSupport AI 管理后台          [通知] [用户] [退出]       │
├──────────┬──────────────────────────────────────────────────┤
│          │  仪表盘                                           │
│  仪表盘   │  ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  知识库   │  │今日对话 │ │ 用户数  │ │ 文档数  │           │
│  策略配置 │  │   128   │ │   45    │ │   23    │           │
└──────────┴──────────────────────────────────────────────────┘
```

---

## 许可证

MIT License

---

## 贡献

欢迎提交Issue和Pull Request！

---

<p align="center">
  Made with by SmartSupport AI Team
</p>
