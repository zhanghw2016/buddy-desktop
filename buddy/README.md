# Buddy Agent Directory

这个目录用于存放所有 Agent 相关的功能模块和配置。

## 目录结构

```
buddy/
├── agents/          # Agent 实现代码
├── prompts/         # Agent 提示词模板
├── workflows/       # Agent 工作流定义
├── tools/           # Agent 工具集
├── config/          # Agent 配置文件
└── README.md        # 本文档
```

## 功能说明

- **agents/**: 各个 Agent 的具体实现
- **prompts/**: Agent 使用的系统提示词和角色定义
- **workflows/**: Agent 之间的协作流程和任务编排
- **tools/**: Agent 可调用的工具函数和外部接口
- **config/**: Agent 的配置参数和环境变量

## 已初始化的 Agent

根据系统配置，已初始化以下 Agent：

1. **林经理 (PM)** - 项目经理 Agent
2. **秦设计 (UI)** - UI 设计师 Agent  
3. **张开发 (Backend)** - 后端开发 Agent
4. **王测试 (QA)** - 测试工程师 Agent

## 开发指南

在添加新的 Agent 或修改现有 Agent 时，请遵循以下规范：

1. 每个 Agent 应有独立的配置文件
2. 提示词应模块化，便于维护和迭代
3. 工作流应清晰定义 Agent 之间的协作方式
4. 工具函数应具有良好的错误处理和日志记录
