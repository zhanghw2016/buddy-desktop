# 快速开始指南

## 🚀 三步启动

### Windows 用户

1. **双击运行** `start.bat`
   - 自动安装依赖
   - 自动初始化数据库
   - 自动启动服务

2. **打开浏览器**访问：
   - API 文档: http://localhost:8000/docs
   - 登录页面: 打开 `frontend/index.html`

### Linux/Mac 用户

```bash
chmod +x start.sh
./start.sh
```

---

## 📁 项目结构

```
buddy-desktop/
├── frontend/
│   └── index.html          # VDI 登录页面（纯前端）
├── buddy/
│   ├── agents/             # AI Agent 实现
│   ├── api/                # REST API 接口
│   ├── models/             # 数据模型
│   ├── services/           # AI 服务
│   ├── workflows/          # 工作流引擎
│   └── scripts/            # 工具脚本
├── docs/                   # 文档
├── start.bat               # Windows 启动脚本
├── start.sh                # Linux/Mac 启动脚本
└── requirements.txt        # Python 依赖
```

---

## 🎯 功能演示

### 1. 登录系统

打开 `frontend/index.html`，使用演示账号登录：

- **管理员**: admin / admin123
- **PM Agent**: 林经理 / 123456
- **UI Agent**: 秦设计 / 123456
- **Backend Agent**: 张开发 / 123456
- **QA Agent**: 王测试 / 123456

### 2. 查看 API 文档

访问 http://localhost:8000/docs

- ✅ 项目管理 API
- ✅ 任务管理 API
- ✅ Agent 管理 API
- ✅ AI 桥接 API

### 3. 查看模拟数据

系统已自动创建：

- 4 个 Agent（林经理、秦设计、张开发、王测试）
- 2 个项目
- 7 个任务（不同状态）
- 3 条消息

---

## 📊 数据库连接

默认连接到远程 PostgreSQL：

```
Host: 172.31.3.199
Port: 5432
Database: buddy_dashboard
User: buddy_desktop
Password: zhu88jie
```

如需修改，编辑 `.env` 文件：

```env
DATABASE_URL=postgresql://user:password@host:port/database
```

---

## 🔧 常见问题

### Q: Python 依赖安装失败？

```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 数据库连接失败？

检查：
1. 数据库服务是否启动
2. 网络是否通畅（ping 172.31.3.199）
3. 用户名密码是否正确

### Q: 端口 8000 被占用？

```bash
# 修改端口
python -m buddy.main --port 8001
```

---

## 📝 下一步

1. **开发前端界面**
   - 创建任务看板
   - Agent 状态显示
   - 工作流可视化

2. **完善 AI 功能**
   - 实现 Agent 自动工作
   - 工作流自动执行

3. **部署上线**
   - 容器化部署
   - 配置域名和 HTTPS

---

## 🐛 遇到问题？

查看日志：
- API 日志：控制台输出
- 数据库日志：PostgreSQL 日志

或提交 Issue 到 GitHub 仓库。

---

## 📖 更多文档

- [系统架构](buddy/docs/ARCHITECTURE.md)
- [API 分析](buddy/docs/API_ANALYSIS.md)
- [AI 桥接说明](buddy/docs/AI_BRIDGE_GUIDE.md)
- [开发路线图](buddy/docs/ROADMAP.md)
