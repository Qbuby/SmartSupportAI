# SmartSupport AI - Web开发计划

## 开发优先级

### P0 - 核心功能（必须完成）
1. **后端管理API** - 支撑前端的基础
2. **用户端聊天界面** - 核心用户功能
3. **企业端知识库管理** - 核心企业功能

### P1 - 增强功能（推荐完成）
4. **企业端策略配置** - 提升系统可配置性
5. **企业端仪表盘** - 数据可视化

### P2 - 优化功能（可选）
6. **移动端适配**
7. **深色模式**
8. **国际化**

---

## 详细任务清单

## Phase 6: 后端管理API扩展

### 6.1 文档管理API
```python
# 新增文件: app/api/admin_api.py

GET    /api/admin/documents          # 分页获取文档列表
POST   /api/admin/documents/upload   # 上传文档（支持多文件）
GET    /api/admin/documents/{id}     # 获取文档详情
DELETE /api/admin/documents/{id}     # 删除文档
POST   /api/admin/documents/{id}/reindex  # 重新索引
GET    /api/admin/documents/{id}/chunks   # 获取文档分块详情
```

### 6.2 配置管理API
```python
GET  /api/admin/config/rag           # 获取RAG配置
PUT  /api/admin/config/rag           # 更新RAG配置
GET  /api/admin/config/memory        # 获取记忆配置
PUT  /api/admin/config/memory        # 更新记忆配置
GET  /api/admin/config/llm           # 获取LLM配置
PUT  /api/admin/config/llm           # 更新LLM配置
```

### 6.3 统计API
```python
GET /api/admin/stats/overview        # 概览统计
GET /api/admin/stats/conversations   # 对话统计（时间范围）
GET /api/admin/stats/queries         # 查询类型分布
GET /api/admin/stats/documents       # 文档统计
```

### 6.4 认证中间件
```python
# 简单的API Key或JWT认证
# 用于保护管理后台API
```

---

## Phase 7: 用户端Web界面

### 7.1 项目初始化
```bash
cd web/user-portal
npm create vite@latest . -- --template react-ts
npm install antd @ant-design/icons zustand @tanstack/react-query axios
npm install react-router-dom dayjs lodash-es
npm install -D @types/lodash-es
```

### 7.2 项目结构
```
web/user-portal/src/
├── api/
│   ├── client.ts          # axios配置
│   └── chat.ts            # 对话API
├── components/
│   ├── ChatWindow/        # 聊天窗口
│   ├── MessageList/       # 消息列表
│   ├── MessageItem/       # 单条消息
│   ├── ChatInput/         # 输入框
│   └── Sidebar/           # 会话列表
├── pages/
│   ├── Login/             # 登录页
│   └── Chat/              # 对话页
├── stores/
│   ├── chatStore.ts       # 聊天状态
│   └── sessionStore.ts    # 会话状态
├── types/
│   └── index.ts           # TypeScript类型
├── App.tsx
└── main.tsx
```

### 7.3 核心组件

#### ChatWindow 聊天窗口
- 消息列表展示
- 自动滚动到底部
- 加载状态显示
- 错误重试

#### MessageItem 消息项
- 用户消息（右侧，蓝色背景）
- 助手消息（左侧，白色背景）
- Markdown渲染
- 代码块高亮
- 时间戳

#### ChatInput 输入框
- 多行文本输入
- 发送按钮
- Enter发送 / Shift+Enter换行
- 输入长度限制

#### Sidebar 会话列表
- 新建会话按钮
- 会话列表（标题/时间）
- 删除会话
- 当前会话高亮

---

## Phase 8: 企业端管理后台

### 8.1 项目初始化
```bash
cd web/admin-portal
npm create vite@latest . -- --template react-ts
npm install antd @ant-design/icons zustand @tanstack/react-query axios recharts
npm install react-router-dom dayjs lodash-es
npm install -D @types/lodash-es
```

### 8.2 项目结构
```
web/admin-portal/src/
├── api/
│   ├── client.ts          # axios配置
│   ├── documents.ts       # 文档API
│   ├── config.ts          # 配置API
│   └── stats.ts           # 统计API
├── components/
│   ├── Layout/            # 页面布局
│   ├── StatCard/          # 统计卡片
│   ├── DocumentTable/     # 文档表格
│   └── UploadArea/        # 上传区域
├── pages/
│   ├── Login/
│   ├── Dashboard/         # 仪表盘
│   ├── Knowledge/         # 知识库管理
│   │   ├── DocumentList/
│   │   └── Upload/
│   ├── Settings/          # 策略配置
│   │   ├── ChunkConfig/
│   │   ├── RetrievalConfig/
│   │   └── MemoryConfig/
│   └── Monitor/           # 系统监控
│       ├── Stats/
│       └── Logs/
├── stores/
│   └── authStore.ts
├── types/
│   └── index.ts
├── App.tsx
└── main.tsx
```

### 8.3 核心页面

#### Dashboard 仪表盘
- 统计卡片（今日对话/用户数/文档数）
- 对话趋势图
- 查询类型饼图
- 最近对话列表

#### Knowledge 知识库管理
- 文档列表表格
- 搜索/筛选
- 批量操作
- 上传对话框
- 预览侧边栏

#### Settings 策略配置
- Chunk策略表单
- 检索策略表单
- 记忆策略表单
- 配置保存/重置

#### Monitor 系统监控
- 对话统计图表
- 响应时间分布
- 实时日志
- 日志筛选/导出

---

## 技术规范

### API请求规范
```typescript
// 统一响应格式
interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

// 统一错误处理
// 401 -> 跳转登录
// 500 -> 显示错误消息
```

### 状态管理规范
```typescript
// Zustand Store
interface ChatStore {
  sessions: Session[];
  currentSessionId: string | null;
  messages: Message[];
  loading: boolean;

  // Actions
  createSession: () => void;
  selectSession: (id: string) => void;
  sendMessage: (content: string) => Promise<void>;
}
```

### 组件规范
- 函数组件 + Hooks
- Props类型定义
- 语义化命名
- 样式使用CSS Modules

---

## 开发顺序建议

### Week 1: 后端API
1. 文档管理API（上传/列表/删除）
2. 配置管理API（读取/保存）
3. 统计API基础版本
4. 简单认证中间件

### Week 2: 用户端
1. 项目搭建
2. 聊天界面基础版
3. 会话管理
4. API集成

### Week 3: 企业端
1. 项目搭建
2. 仪表盘
3. 知识库管理
4. 策略配置

### Week 4: 集成测试
1. 端到端测试
2. 性能优化
3. Bug修复
4. 文档完善

---

## 运行命令

```bash
# 后端
uvicorn app.api.chat_api:app --reload --port 8000

# 用户端
cd web/user-portal
npm run dev  # 端口 5173

# 企业端
cd web/admin-portal
npm run dev  # 端口 5174
```

---

## 部署架构

```
Nginx
├── /          -> 用户端静态文件
├── /admin     -> 企业端静态文件
└── /api       -> FastAPI后端代理
```
