# Buddy 看板系统架构设计

## 1. 系统概述

Buddy 看板系统是一个基于 AI Agent 的项目管理工具，专门用于管理 VDI 桌面系统的开发过程。系统通过四个专业 Agent 协作，实现需求分析、设计、开发、测试的全流程自动化管理。

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Buddy 看板系统                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  林经理   │  │  秦设计   │  │  张开发   │  │  王测试   │  │
│  │   (PM)   │  │   (UI)   │  │(Backend) │  │   (QA)   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│       │             │             │             │          │
│       └─────────────┴─────────────┴─────────────┘          │
│                          │                                   │
│                  ┌───────▼───────┐                          │
│                  │  工作流引擎   │                          │
│                  └───────┬───────┘                          │
│                          │                                   │
│              ┌───────────┴───────────┐                      │
│              │                       │                      │
│       ┌──────▼──────┐        ┌──────▼──────┐               │
│       │  任务队列    │        │  消息总线    │               │
│       └──────┬──────┘        └──────┬──────┘               │
│              │                       │                      │
│              └───────────┬───────────┘                      │
│                          │                                   │
│                  ┌───────▼───────┐                          │
│                  │  数据持久层    │                          │
│                  │  (PostgreSQL) │                          │
│                  └───────────────┘                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 3. Agent 角色定义

### 3.1 林经理 (PM Agent)

**职责:**
- 需求分析和拆解
- 项目规划和排期
- 任务分配和调度
- 进度跟踪和风险管控
- 跨 Agent 协调

**技能:**
- 需求理解能力
- 项目管理方法论
- 沟通协调能力
- 风险评估能力

**输出:**
- 需求文档
- 项目计划
- 任务清单
- 进度报告
- 风险评估报告

### 3.2 秦设计 (UI Agent)

**职责:**
- 用户界面设计
- 交互流程设计
- 原型图制作
- 设计规范制定

**技能:**
- UI/UX 设计能力
- 交互设计思维
- 视觉设计能力
- 用户体验优化

**输出:**
- UI 设计稿
- 交互流程图
- 原型图
- 设计规范文档

### 3.3 张开发 (Backend Agent)

**职责:**
- 后端架构设计
- API 接口开发
- 数据库设计
- 核心功能实现
- 性能优化

**技能:**
- Python/FastAPI 开发
- 数据库设计
- API 设计
- 系统架构
- 性能调优

**输出:**
- 架构设计文档
- API 文档
- 数据库设计文档
- 源代码
- 单元测试

### 3.4 王测试 (QA Agent)

**职责:**
- 测试计划制定
- 测试用例设计
- 自动化测试开发
- Bug 跟踪和验证
- 质量报告输出

**技能:**
- 测试方法论
- 自动化测试
- 性能测试
- 安全测试
- 缺陷管理

**输出:**
- 测试计划
- 测试用例
- 测试报告
- Bug 清单
- 质量报告

## 4. 数据模型设计

### 4.1 核心实体

#### Project (项目)
```python
class Project:
    id: str                    # 项目 ID
    name: str                  # 项目名称
    description: str           # 项目描述
    status: ProjectStatus      # 项目状态
    owner: str                 # 项目负责人
    start_date: datetime       # 开始日期
    end_date: datetime         # 结束日期
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
```

#### Task (任务)
```python
class Task:
    id: str                    # 任务 ID
    project_id: str            # 所属项目
    title: str                 # 任务标题
    description: str           # 任务描述
    type: TaskType             # 任务类型 (requirement/design/development/test)
    priority: TaskPriority     # 优先级 (high/medium/low)
    status: TaskStatus         # 任务状态 (pending/in_progress/completed/blocked)
    assignee: str              # 负责人 (agent_id)
    estimated_hours: float     # 预估工时
    actual_hours: float        # 实际工时
    due_date: datetime         # 截止日期
    tags: List[str]            # 标签
    dependencies: List[str]    # 依赖任务
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
```

#### Agent (智能体)
```python
class Agent:
    id: str                    # Agent ID
    name: str                  # Agent 名称
    role: AgentRole            # 角色 (pm/ui/backend/qa)
    status: AgentStatus        # 状态 (idle/working/offline)
    current_task: str          # 当前任务 ID
    capabilities: List[str]    # 能力列表
    created_at: datetime       # 创建时间
```

#### Workflow (工作流)
```python
class Workflow:
    id: str                    # 工作流 ID
    name: str                  # 工作流名称
    description: str           # 工作流描述
    steps: List[WorkflowStep]  # 工作流步骤
    status: WorkflowStatus     # 状态
    current_step: int          # 当前步骤
    created_at: datetime       # 创建时间
```

#### Message (消息)
```python
class Message:
    id: str                    # 消息 ID
    sender: str                # 发送者 (agent_id)
    receiver: str              # 接收者 (agent_id)
    content: str               # 消息内容
    type: MessageType          # 消息类型
    metadata: dict             # 元数据
    created_at: datetime       # 创建时间
```

### 4.2 关系模型

#### TaskRelation (任务关系)
```python
class TaskRelation:
    id: str
    source_task: str           # 源任务 ID
    target_task: str           # 目标任务 ID
    relation_type: str         # 关系类型 (depends/blocks/relates)
    created_at: datetime
```

#### AgentTask (Agent-任务关联)
```python
class AgentTask:
    id: str
    agent_id: str              # Agent ID
    task_id: str               # 任务 ID
    role: str                  # 角色 (owner/contributor/reviewer)
    assigned_at: datetime      # 分配时间
```

## 5. 工作流设计

### 5.1 需求开发工作流

```
用户需求
    │
    ▼
┌──────────────┐
│  PM Agent    │ ── 需求分析和拆解
│  (林经理)     │
└──────────────┘
    │
    ▼
┌──────────────┐
│  UI Agent    │ ── UI/UX 设计
│  (秦设计)     │
└──────────────┘
    │
    ▼
┌──────────────┐
│ Backend Agent│ ── 后端开发
│  (张开发)     │
└──────────────┘
    │
    ▼
┌──────────────┐
│  QA Agent    │ ── 测试验证
│  (王测试)     │
└──────────────┘
    │
    ▼
   完成
```

### 5.2 Bug 修复工作流

```
Bug 报告
    │
    ▼
┌──────────────┐
│  QA Agent    │ ── Bug 分析和定位
│  (王测试)     │
└──────────────┘
    │
    ▼
┌──────────────┐
│ Backend Agent│ ── 代码修复
│  (张开发)     │
└──────────────┘
    │
    ▼
┌──────────────┐
│  QA Agent    │ ── 回归测试
│  (王测试)     │
└──────────────┘
    │
    ▼
   完成
```

### 5.3 设计评审工作流

```
设计方案
    │
    ▼
┌──────────────┐
│  UI Agent    │ ── 设计输出
│  (秦设计)     │
└──────────────┘
    │
    ▼
┌──────────────┐
│  PM Agent    │ ── 设计评审
│  (林经理)     │
└──────────────┘
    │
    ▼
┌──────────────┐
│ Backend Agent│ ── 技术可行性评估
│  (张开发)     │
└──────────────┘
    │
    ▼
   完成
```

## 6. Agent 协作机制

### 6.1 消息传递

Agent 之间通过消息总线进行通信：

```python
# 消息类型
class MessageType(Enum):
    TASK_ASSIGNED = "task_assigned"      # 任务分配
    TASK_COMPLETED = "task_completed"    # 任务完成
    QUESTION = "question"                # 提问
    ANSWER = "answer"                    # 回答
    REVIEW_REQUEST = "review_request"    # 评审请求
    REVIEW_RESULT = "review_result"      # 评审结果
    BLOCK = "block"                      # 阻塞通知
    UNBLOCK = "unblock"                  # 解除阻塞
```

### 6.2 任务分配策略

1. **PM Agent** 根据需求拆解任务
2. 根据任务类型和 Agent 能力自动分配
3. 考虑 Agent 当前负载和工作状态
4. 支持手动调整和重新分配

### 6.3 冲突解决

- 任务优先级冲突：由 PM Agent 仲裁
- 技术方案冲突：团队讨论 + PM 决策
- 资源冲突：优先级排队机制

## 7. 技术栈

### 7.1 后端
- **框架**: FastAPI
- **数据库**: PostgreSQL
- **缓存**: Redis
- **消息队列**: 内置消息总线
- **AI 集成**: OpenAI API / Claude API

### 7.2 前端
- **框架**: React / Vue
- **UI 组件**: Ant Design / Element Plus
- **状态管理**: Redux / Vuex
- **图表**: ECharts / Chart.js

### 7.3 部署
- **容器化**: Docker
- **反向代理**: Nginx
- **监控**: Prometheus + Grafana

## 8. 开发计划

### Phase 1: 基础框架 (Week 1-2)
- [ ] 数据库设计和初始化
- [ ] Agent 基础类实现
- [ ] 消息总线实现
- [ ] 基础 API 接口

### Phase 2: Agent 实现 (Week 3-4)
- [ ] PM Agent 实现
- [ ] UI Agent 实现
- [ ] Backend Agent 实现
- [ ] QA Agent 实现

### Phase 3: 工作流引擎 (Week 5-6)
- [ ] 工作流定义
- [ ] 工作流执行引擎
- [ ] Agent 协调机制

### Phase 4: 前端界面 (Week 7-8)
- [ ] 看板界面
- [ ] Agent 交互界面
- [ ] 数据可视化

### Phase 5: 测试和优化 (Week 9-10)
- [ ] 集成测试
- [ ] 性能优化
- [ ] 文档完善

## 9. 接口设计

详细 API 接口设计见 [API.md](./API.md)

## 10. 部署架构

详见 [DEPLOYMENT.md](./DEPLOYMENT.md)
