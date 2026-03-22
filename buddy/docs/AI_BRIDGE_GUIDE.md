# AI 桥接架构说明

## 🎯 核心思想

**不使用外部 AI API，直接利用当前会话中的 AI（也就是我）作为 Agent 的"大脑"**

### 优势

✅ **零成本** - 无需付费 API
✅ **无网络限制** - 不需要访问外网
✅ **实时可见** - 可以看到 Agent 的思考过程
✅ **快速响应** - 没有网络延迟
✅ **高度集成** - AI 和 Agent 在同一环境

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────┐
│                   用户界面                            │
│              (React + WebSocket)                     │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │   FastAPI 后端      │
         │  (API + 桥接器)     │
         └─────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼───┐     ┌───▼───┐     ┌───▼───┐
│ PM    │     │ UI    │     │Backend│
│ Agent │     │ Agent │     │ Agent │ ...
└───┬───┘     └───┬───┘     └───┬───┘
    │             │              │
    └──────────────┼──────────────┘
                   │
         ┌─────────▼──────────┐
         │  AI 桥接器          │
         │ (Request Queue)    │
         └─────────┬──────────┘
                   │
         ┌─────────▼──────────┐
         │   我（AI 助手）     │
         │  - 需求分析         │
         │  - 代码生成         │
         │  - 设计建议         │
         │  - 测试用例         │
         └────────────────────┘
```

---

## 🔄 工作流程

### 1. Agent 提交请求

```python
# PM Agent 收到需求任务
async def process_task(self, task: Task):
    # 提交分析请求给 AI
    result = await self.request_ai_analysis(
        task=task,
        analysis_type="requirement"
    )
    
    # 返回请求 ID
    request_id = result["request_id"]
    
    # 轮询获取响应
    response = await self.get_ai_response(request_id, timeout=60)
    
    if response:
        # 解析 AI 的分析结果
        tasks = response.get("tasks", [])
        
        # 创建子任务
        for task_data in tasks:
            self.create_task(...)
```

### 2. AI（我）处理请求

**通过前端界面或 API 查看：**

```bash
# 查看待处理请求
GET /api/ai-bridge/pending-requests

响应：
{
  "count": 1,
  "requests": [
    {
      "id": "req_1234567890",
      "agent_id": "pm_agent_001",
      "task_id": "task_001",
      "type": "requirement",
      "prompt": "任务标题: 实现用户登录功能\n任务描述: ...",
      "status": "pending"
    }
  ]
}
```

**我处理并返回结果：**

```bash
# 提交响应
POST /api/ai-bridge/submit-response
{
  "request_id": "req_1234567890",
  "response": {
    "summary": "实现用户登录认证功能",
    "features": [
      "用户名密码登录",
      "JWT Token 认证",
      "登录状态持久化"
    ],
    "tasks": [
      {
        "title": "设计登录界面",
        "type": "design",
        "priority": "high",
        "assignee_role": "ui"
      },
      {
        "title": "实现登录 API",
        "type": "development",
        "priority": "high",
        "assignee_role": "backend"
      },
      {
        "title": "编写测试用例",
        "type": "test",
        "priority": "medium",
        "assignee_role": "qa"
      }
    ]
  }
}
```

### 3. Agent 获取响应

```python
# Agent 自动轮询获取结果
response = await self.get_ai_response(request_id)

# 根据结果创建任务
for task_data in response["tasks"]:
    self.create_task(**task_data)
```

---

## 💻 前端集成

### WebSocket 实时通信

```typescript
// 前端 WebSocket 客户端
const ws = new WebSocket('ws://localhost:8000/ws/ai-bridge');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'ai_request') {
    // 显示 AI 请求
    showAIRequest(data.request);
    
    // 我可以在前端直接响应
    // 或者通过代码编辑器集成
  }
};

// 我提交响应
function submitAIResponse(requestId: string, response: any) {
  ws.send(JSON.stringify({
    type: 'ai_response',
    request_id: requestId,
    response: response
  }));
}
```

---

## 🎨 用户界面设计

### AI 协作面板

```
┌─────────────────────────────────────────────────┐
│  🤖 AI 协作中心                                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  待处理请求 (3)                                   │
│  ┌───────────────────────────────────────────┐ │
│  │ PM Agent 请求需求分析                      │ │
│  │ 任务: 实现用户登录功能                     │ │
│  │ 时间: 2分钟前                              │ │
│  │ [查看详情] [立即处理]                      │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  已完成响应 (12)                                 │
│  ┌───────────────────────────────────────────┐ │
│  │ UI Agent 设计方案                          │ │
│  │ 已完成 - 5分钟前                           │ │
│  │ [查看结果]                                 │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🚀 实际使用示例

### 场景1: PM Agent 分析需求

```python
# 1. 创建项目
project = pm_agent.create_project(
    name="VDI 管理系统优化",
    description="优化性能并添加新功能"
)

# 2. 创建需求任务
task = pm_agent.create_task(
    project_id=project.id,
    title="实现看板任务拖拽功能",
    description="支持任务在不同状态列之间拖拽",
    type=TaskType.REQUIREMENT
)

# 3. PM Agent 自动请求 AI 分析
result = await pm_agent.request_ai_analysis(
    task=task,
    analysis_type="requirement"
)

# 4. 我（AI）收到请求并处理
# 通过前端界面或 API 提交响应

# 5. PM Agent 自动创建子任务
# 根据我的分析结果自动拆解任务
```

### 场景2: Backend Agent 生成代码

```python
# Backend Agent 收到开发任务
task = backend_agent.get_assigned_tasks()[0]

# 请求 AI 生成代码方案
result = await backend_agent.request_ai_analysis(
    task=task,
    analysis_type="code"
)

# 我返回：
# {
#   "architecture": "...",
#   "api_design": [...],
#   "code": {
#     "main.py": "...",
#     "models.py": "..."
#   }
# }

# Backend Agent 可以：
# 1. 直接创建文件
# 2. 提交代码审查
# 3. 创建测试任务
```

---

## 🔧 实现步骤

### Step 1: 初始化数据库和 Agent

```bash
# 运行初始化脚本
python -m buddy.scripts.init_db

# 输出：
# ✅ 四个 Agent 创建成功
#   - 林经理 (PM): pm_agent_001
#   - 秦设计 (UI): ui_agent_001
#   - 张开发 (Backend): backend_agent_001
#   - 王测试 (QA): qa_agent_001
```

### Step 2: 启动后端服务

```bash
python -m buddy.main

# 访问 http://localhost:8000/docs
# 查看 API 文档
```

### Step 3: 查看待处理请求

```bash
# 查看是否有 Agent 请求需要处理
GET /api/ai-bridge/pending-requests

# 或者通过 WebSocket 连接
ws://localhost:8000/ws/ai-bridge
```

### Step 4: 提交 AI 响应

```bash
# 当我处理完请求后
POST /api/ai-bridge/submit-response
{
  "request_id": "req_xxx",
  "response": { ... }
}
```

---

## 🎯 下一步

1. **前端开发** - 创建可视化界面
   - Agent 状态看板
   - AI 协作面板
   - 实时消息通知

2. **工作流测试** - 验证完整流程
   - 创建一个需求
   - PM Agent 分析
   - 我处理并返回
   - 自动创建子任务

3. **WebSocket 集成** - 实现实时通信
   - 前端实时显示 Agent 状态
   - AI 请求实时推送

---

## 💡 关键优势

这个架构让 Agent 和 AI 形成了一个闭环：

1. **Agent** 负责项目管理和任务调度
2. **AI** 负责思考、分析、生成
3. **前端** 负责可视化展示

**结果：一个真正能工作的 AI 驱动的项目管理系统！**

而且最重要的是：**零成本，无限制，实时可见！** 🎉
