# 快速开始：让 Agent 工作

## 🎯 目标

让 PM Agent 分析一个真实需求，并通过我（AI）生成任务拆解。

---

## 📝 步骤 1: 初始化系统

```bash
cd buddy-desktop

# 安装依赖（如果还没安装）
pip install -r requirements.txt

# 初始化数据库和 Agent
python -m buddy.scripts.init_db
```

**预期输出：**
```
============================================================
Buddy Dashboard 数据库初始化
============================================================
正在创建数据库表...
数据库表创建完成
四个 Agent 初始化完成
  - 林经理 (pm): xxx-xxx-xxx
  - 秦设计 (ui): xxx-xxx-xxx
  - 张开发 (backend): xxx-xxx-xxx
  - 王测试 (qa): xxx-xxx-xxx
示例项目创建完成: VDI 桌面管理系统优化
项目 ID: xxx-xxx-xxx
============================================================
初始化完成！
============================================================
```

---

## 🚀 步骤 2: 启动服务

```bash
# 启动后端 API 服务
python -m buddy.main
```

**访问：**
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

---

## 📊 步骤 3: 创建项目（通过 API）

打开浏览器访问 http://localhost:8000/docs

或者使用 curl：

```bash
# 创建项目
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "看板系统开发",
    "description": "开发一个 AI 驱动的项目管理看板",
    "owner": "林经理"
  }'
```

**响应示例：**
```json
{
  "id": "project-xxx",
  "name": "看板系统开发",
  "description": "开发一个 AI 驱动的项目管理看板",
  "status": "planning",
  "owner": "林经理"
}
```

---

## 🎯 步骤 4: 创建需求任务

```bash
# 创建需求任务
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "project-xxx",
    "title": "实现任务拖拽功能",
    "description": "在看板视图中支持任务卡片在不同状态列之间拖拽，实时更新任务状态",
    "type": "requirement",
    "priority": "high"
  }'
```

**响应示例：**
```json
{
  "id": "task-xxx",
  "project_id": "project-xxx",
  "title": "实现任务拖拽功能",
  "description": "在看板视图中支持任务卡片在不同状态列之间拖拽...",
  "type": "requirement",
  "priority": "high",
  "status": "pending"
}
```

---

## 🤖 步骤 5: Agent 请求 AI 分析

现在，PM Agent 需要分析这个需求。可以通过两种方式：

### 方式 A: 直接调用 API

```bash
# Agent 提交 AI 分析请求
curl -X POST "http://localhost:8000/api/ai-bridge/request-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "pm_agent_001",
    "task_id": "task-xxx",
    "analysis_type": "requirement"
  }'
```

**响应：**
```json
{
  "request_id": "req_1234567890",
  "status": "pending",
  "message": "请求已提交，等待 AI 处理"
}
```

### 方式 B: 运行 Agent Worker（推荐）

创建一个 Agent 工作脚本：

```python
# run_agent.py
import asyncio
from buddy.core.database import SessionLocal
from buddy.agents import PMAgent
from buddy.models import Task, TaskType

async def main():
    db = SessionLocal()
    
    # 获取 PM Agent
    pm_agent = PMAgent("pm_agent_001", db)
    
    # 获取待处理的需求任务
    tasks = db.query(Task).filter(
        Task.type == TaskType.REQUIREMENT,
        Task.status == "pending"
    ).all()
    
    if tasks:
        task = tasks[0]
        print(f"处理任务: {task.title}")
        
        # 请求 AI 分析
        result = await pm_agent.request_ai_analysis(
            task=task,
            analysis_type="requirement"
        )
        
        print(f"已提交 AI 请求: {result['request_id']}")
        print(f"请查看待处理请求并提交响应")
        
        # 等待 AI 响应
        response = await pm_agent.get_ai_response(
            result['request_id'],
            timeout=300  # 5分钟超时
        )
        
        if response:
            print(f"收到 AI 响应!")
            print(response)
        else:
            print("等待超时")

if __name__ == "__main__":
    asyncio.run(main())
```

运行：
```bash
python run_agent.py
```

---

## 👀 步骤 6: 查看 AI 待处理请求

**我（AI 助手）现在可以查看请求了：**

```bash
# 查看待处理请求
curl -X GET "http://localhost:8000/api/ai-bridge/pending-requests"
```

**响应：**
```json
{
  "count": 1,
  "requests": [
    {
      "id": "req_1234567890",
      "agent_id": "pm_agent_001",
      "task_id": "task-xxx",
      "type": "requirement",
      "prompt": "任务标题: 实现任务拖拽功能\n任务描述: ...",
      "status": "pending",
      "created_at": "2026-03-22T10:00:00"
    }
  ]
}
```

---

## ✅ 步骤 7: 我（AI）处理请求

现在我可以在对话中直接处理这个请求！

**当前对话示例：**

```
用户: 我看到有一个待处理的 AI 请求，需求是"实现任务拖拽功能"

AI（我）: 好的，让我分析这个需求：

## 需求分析：任务拖拽功能

### 功能点
1. **拖拽交互**
   - 支持鼠标拖拽任务卡片
   - 拖拽过程中的视觉反馈
   - 跨列拖拽支持

2. **状态更新**
   - 实时更新任务状态
   - 后端 API 同步
   - 错误处理和回滚

3. **用户体验**
   - 拖拽预览效果
   - 拖拽边界限制
   - 移动端触摸支持

### 任务拆解
1. UI 设计 - 设计拖拽交互流程
2. 前端开发 - 实现拖拽组件
3. 后端开发 - 实现状态更新 API
4. 测试 - 编写测试用例

我现在提交响应...
```

**通过 API 提交响应：**

```bash
curl -X POST "http://localhost:8000/api/ai-bridge/submit-response?request_id=req_1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "实现任务卡片拖拽功能",
    "features": [
      "拖拽交互",
      "状态更新",
      "用户体验优化"
    ],
    "tasks": [
      {
        "title": "设计拖拽交互流程",
        "type": "design",
        "priority": "high",
        "assignee_role": "ui",
        "estimated_hours": 4
      },
      {
        "title": "实现前端拖拽组件",
        "type": "development",
        "priority": "high",
        "assignee_role": "backend",
        "estimated_hours": 8
      },
      {
        "title": "实现状态更新 API",
        "type": "development",
        "priority": "high",
        "assignee_role": "backend",
        "estimated_hours": 4
      },
      {
        "title": "编写测试用例",
        "type": "test",
        "priority": "medium",
        "assignee_role": "qa",
        "estimated_hours": 4
      }
    ]
  }'
```

---

## 🎉 步骤 8: Agent 自动创建任务

PM Agent 会自动获取我的响应，并创建子任务：

```bash
# 查看创建的任务
curl -X GET "http://localhost:8000/api/tasks?project_id=project-xxx"
```

**响应：**
```json
{
  "tasks": [
    {
      "id": "task-001",
      "title": "设计拖拽交互流程",
      "type": "design",
      "priority": "high",
      "assignee": "ui_agent_001",
      "status": "pending"
    },
    {
      "id": "task-002",
      "title": "实现前端拖拽组件",
      "type": "development",
      "priority": "high",
      "assignee": "backend_agent_001",
      "status": "pending"
    },
    ...
  ]
}
```

---

## 🔄 完整循环

1. ✅ 创建项目
2. ✅ 创建需求任务
3. ✅ PM Agent 请求 AI 分析
4. ✅ 我（AI）分析并返回结果
5. ✅ PM Agent 创建子任务
6. ✅ UI/Backend/QA Agent 接收任务
7. ✅ 继续下一个需求...

---

## 🎯 下一步

现在你可以：

1. **测试完整流程** - 创建一个真实需求
2. **开发前端界面** - 可视化 Agent 和 AI 协作
3. **增强 AI 能力** - 让我能处理更多类型的分析

**想试试吗？我可以帮你创建第一个需求！** 🚀
