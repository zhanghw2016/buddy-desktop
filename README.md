# Buddy Dashboard

基于 AI Agent 的项目管理看板系统，用于管理 VDI 桌面系统的开发过程。

## 系统特性

- 🤖 **四个专业 Agent**: PM、UI、Backend、QA
- 📋 **项目管理**: 项目创建、进度跟踪、任务分配
- 🔄 **工作流引擎**: 自动化工作流程
- 💬 **Agent 协作**: Agent 之间的消息传递和协作
- 📊 **数据可视化**: 任务看板、进度统计

## 技术栈

- **后端**: FastAPI + PostgreSQL + Redis
- **AI 集成**: OpenAI API / Claude API
- **前端**: React / Vue (待实现)

## 快速开始

### 1. 安装依赖

```bash
cd buddy-desktop
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
DATABASE_URL=postgresql://buddy_desktop:zhu88jie@172.31.3.199:5432/buddy_dashboard
REDIS_URL=redis://172.31.3.199:6379/0
OPENAI_API_KEY=your_api_key
```

### 3. 初始化数据库

```bash
python -m buddy.scripts.init_db
```

### 4. 启动服务

```bash
python -m buddy.main
```

访问 http://localhost:8000 查看系统。

## 项目结构

```
buddy-desktop/
├── buddy/
│   ├── agents/          # Agent 实现
│   │   ├── base.py
│   │   ├── pm_agent.py
│   │   ├── ui_agent.py
│   │   ├── backend_agent.py
│   │   └── qa_agent.py
│   ├── api/             # API 路由
│   │   ├── projects.py
│   │   ├── tasks.py
│   │   └── agents.py
│   ├── core/            # 核心模块
│   │   ├── config.py
│   │   └── database.py
│   ├── models/          # 数据模型
│   │   ├── project.py
│   │   ├── task.py
│   │   ├── agent.py
│   │   ├── workflow.py
│   │   └── message.py
│   ├── prompts/         # Agent 提示词
│   ├── workflows/       # 工作流定义
│   ├── tools/           # Agent 工具
│   ├── config/          # 配置文件
│   ├── scripts/         # 脚本
│   │   └── init_db.py
│   └── main.py          # 主应用
├── docs/                # 文档
│   ├── ARCHITECTURE.md
│   ├── API_ANALYSIS.md
│   └── API.md
├── tests/               # 测试
├── requirements.txt
└── README.md
```

## Agent 介绍

### 林经理 (PM Agent)
- 需求分析和拆解
- 项目规划和排期
- 任务分配和调度
- 进度跟踪和风险管控

### 秦设计 (UI Agent)
- 用户界面设计
- 交互流程设计
- 原型图制作
- 设计规范制定

### 张开发 (Backend Agent)
- 后端架构设计
- API 接口开发
- 数据库设计
- 核心功能实现

### 王测试 (QA Agent)
- 测试计划制定
- 测试用例设计
- 自动化测试开发
- Bug 跟踪和验证

## API 文档

启动服务后访问 http://localhost:8000/docs 查看完整 API 文档。

### 主要接口

- `GET /api/projects` - 获取项目列表
- `POST /api/projects` - 创建项目
- `GET /api/tasks` - 获取任务列表
- `POST /api/tasks` - 创建任务
- `GET /api/agents` - 获取 Agent 列表

## 开发计划

- [x] 数据库模型设计
- [x] Agent 基础类实现
- [x] API 接口实现
- [ ] Agent AI 集成
- [ ] 工作流引擎
- [ ] 前端界面
- [ ] 测试覆盖

## 许可证

MIT License
