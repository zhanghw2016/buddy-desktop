# 前端开发快速指南

## 📦 安装步骤

### 方法 1: 使用 npm（推荐）

```bash
# 1. 进入前端目录
cd buddy-desktop/frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 4. 浏览器访问
# http://localhost:3000
```

### 方法 2: 使用 yarn

```bash
cd buddy-desktop/frontend
yarn install
yarn dev
```

### 方法 3: 如果没有 Node.js

**下载安装 Node.js:**
- 官网: https://nodejs.org/
- 推荐版本: LTS (长期支持版)
- 安装后会自动包含 npm

**验证安装:**
```bash
node --version  # 应显示 v18.x 或更高
npm --version   # 应显示 9.x 或更高
```

## 🎯 功能演示

### 1. 看板总览
- 显示 4 个 Agent 状态
- 项目进度可视化
- 任务统计数据

### 2. Agent 管理
- 查看每个 Agent 的能力
- 当前工作状态
- 完成的任务数量

### 3. 项目管理
- 查看项目列表
- 新建项目
- 跟踪项目进度

### 4. 任务看板
- 看板视图（4 列）
- 创建新任务
- 任务分配和优先级

## 🔧 常见问题

### Q: npm install 很慢怎么办？
A: 使用国内镜像：
```bash
npm config set registry https://registry.npmmirror.com
npm install
```

### Q: 启动后看不到数据？
A: 前端已内置模拟数据，无需后端即可查看界面。
如需真实数据，请启动后端：
```bash
python buddy/scripts/start_api.py
```

### Q: 端口 3000 被占用？
A: 修改 `vite.config.js`:
```javascript
server: {
  port: 3001  // 改为其他端口
}
```

### Q: 如何连接真实后端？
A: 编辑 `src/services/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000'
```

## 📱 界面截图（模拟）

```
┌─────────────────────────────────────────┐
│  Buddy Dashboard          [消息]        │
├─────────────────────────────────────────┤
│ [看板总览]                              │
│ [Agent管理]                             │
│ [项目管理]                              │
│ [任务看板]                              │
├─────────────────────────────────────────┤
│                                         │
│  Agent 总数: 4    项目总数: 2           │
│  任务总数: 9      已完成: 1             │
│                                         │
│  [Agent 状态]       [项目进度]          │
│  ● 林经理 (空闲)    VDI优化 65%         │
│  ● 秦设计 (工作中)  看板开发 30%        │
│  ● 张开发 (工作中)                      │
│  ● 王测试 (空闲)                        │
│                                         │
└─────────────────────────────────────────┘
```

## 🚀 下一步

1. **启动前端**: `npm run dev`
2. **启动后端**: `python buddy/scripts/start_api.py`
3. **运行测试**: `python buddy/scripts/test_agent_workflow.py`
4. **查看结果**: http://localhost:3000

## 💡 提示

- 前端使用 Vite，启动速度很快
- 支持热更新，修改代码自动刷新
- 已集成 Ant Design 组件库
- 使用模拟数据，无需后端即可预览

---

**有问题？查看完整文档:**
- `frontend/README.md` - 前端详细文档
- `PROJECT_BOARD.md` - 项目看板
- `TEST_REPORT.md` - 测试报告
