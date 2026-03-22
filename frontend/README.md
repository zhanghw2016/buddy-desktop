# Buddy Dashboard 前端

基于 React + Ant Design 的 AI Agent 协作看板界面

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

### 3. 访问界面

- 前端界面: http://localhost:3000
- 后端 API: http://localhost:8000/docs

## 功能模块

### 看板总览 (`/`)
- Agent 状态概览
- 项目进度展示
- 任务统计数据
- 最近任务列表

### Agent 管理 (`/agents`)
- 4 个 Agent 状态展示
- 能力标签显示
- 当前任务和工作状态
- 完成任务统计

### 项目管理 (`/projects`)
- 项目列表和详情
- 项目进度可视化
- 新建项目功能
- 项目周期展示

### 任务看板 (`/tasks`)
- 任务看板视图（待处理/进行中/已完成/阻塞）
- 任务卡片展示
- 新建任务功能
- 任务分配和优先级

## 技术栈

- **React 18**: UI 框架
- **Ant Design 5**: UI 组件库
- **React Router 6**: 路由管理
- **Axios**: HTTP 客户端
- **Vite**: 构建工具
- **Day.js**: 日期处理

## 项目结构

```
frontend/
├── src/
│   ├── pages/           # 页面组件
│   │   ├── Dashboard.jsx
│   │   ├── Agents.jsx
│   │   ├── Projects.jsx
│   │   └── Tasks.jsx
│   ├── services/        # API 服务
│   │   └── api.js
│   ├── App.jsx          # 主应用
│   ├── main.jsx         # 入口文件
│   └── index.css        # 全局样式
├── index.html           # HTML 模板
├── vite.config.js       # Vite 配置
└── package.json         # 依赖配置
```

## 开发指南

### API 配置

编辑 `src/services/api.js` 修改后端 API 地址：

```javascript
const API_BASE_URL = 'http://localhost:8000'
```

### 添加新页面

1. 在 `src/pages/` 创建新组件
2. 在 `src/App.jsx` 添加路由
3. 在侧边栏菜单添加导航

### 自定义样式

编辑 `src/index.css` 添加全局样式

## 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录

## 注意事项

- 确保后端 API 服务已启动（http://localhost:8000）
- 如果使用模拟数据，前端可以独立运行
- WebSocket 实时功能需要后端支持
