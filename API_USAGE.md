# SmartSupport AI - API 使用说明

## 启动服务

```bash
# 构建向量数据库（如果还没构建）
python scripts/build_vector_db.py

# 启动 API 服务
uvicorn app.api.chat_api:app --reload
```

服务启动后：
- API 文档: http://127.0.0.1:8000/docs
- 健康检查: http://127.0.0.1:8000/health

## API 端点

### 1. 主对话接口

```bash
POST /chat
```

请求示例：
```json
{
  "user_id": "user_001",
  "message": "我的订单 12345 什么时候发货？"
}
```

响应示例：
```json
{
  "success": true,
  "reply": "订单 12345 的状态是：已发货...",
  "intent": "order_query",
  "tool_used": "order",
  "session_id": "sess_user_001_20250311120000",
  "timestamp": "2025-03-11T12:00:00"
}
```

### 2. 带会话上下文的对话

```bash
POST /chat
```

请求示例：
```json
{
  "user_id": "user_001",
  "message": "那另一个订单呢？",
  "session_id": "sess_user_001_20250311120000"
}
```

### 3. 获取会话历史

```bash
GET /sessions/{session_id}/history
```

响应示例：
```json
{
  "session_id": "sess_user_001_20250311120000",
  "history": [
    {
      "user": "我的订单 12345 什么时候发货？",
      "assistant": "订单 12345 的状态是：已发货..."
    }
  ],
  "turn_count": 1
}
```

### 4. 清除会话

```bash
DELETE /sessions/{session_id}
```

### 5. 列出活跃会话

```bash
GET /sessions
```

### 6. 系统统计

```bash
GET /stats
```

## 支持的查询类型

### 订单查询
示例消息：
- "我的订单 12345 什么时候发货？"
- "查询订单 ORD-2025-001 状态"
- "订单 12345 发货了吗？"

### 工单查询
示例消息：
- "我的工单 67890 处理得怎么样了？"
-