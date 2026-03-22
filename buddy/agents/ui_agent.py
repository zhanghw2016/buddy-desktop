"""
UI Agent - UI 设计师
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from buddy.agents.base import BaseAgent
from buddy.models import Task
from buddy.models.enums import TaskType, AgentRole


class UIAgent(BaseAgent):
    """UI 设计师 Agent"""
    
    def __init__(self, agent_id: str, db: Session):
        super().__init__(agent_id, db)
        if self.role != AgentRole.UI:
            raise ValueError(f"Agent {agent_id} is not a UI agent")
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是秦设计，一位专业的 UI/UX 设计师。你的职责包括：

1. **界面设计**: 创建美观、易用的用户界面
2. **交互设计**: 设计流畅的用户交互流程
3. **原型制作**: 快速制作可交互的原型图
4. **设计规范**: 建立和维护设计系统和规范

## 你的设计原则

- 以用户为中心，注重用户体验
- 保持设计的简洁性和一致性
- 考虑可用性和可访问性
- 注重细节，追求完美

## 输出规范

你的设计输出应包含：
- 设计理念和思路
- 界面布局和组件
- 交互流程说明
- 设计规范文档
- 原型图（使用 ASCII 或描述）

当前项目: VDI 桌面管理系统优化
"""
    
    def process_task(self, task: Task) -> Dict[str, Any]:
        """处理任务"""
        if task.type == TaskType.DESIGN:
            return self._process_design(task)
        else:
            return {"status": "error", "message": "不支持的 任务类型"}
    
    def _process_design(self, task: Task) -> Dict[str, Any]:
        """处理设计任务"""
        # TODO: 调用 AI 生成设计方案
        # 这里需要实现 AI 设计逻辑
        
        result = {
            "design_concept": "设计理念",
            "wireframes": [
                {
                    "page": "看板主页",
                    "layout": """
┌─────────────────────────────────────────┐
│  Logo  │  项目列表  │  Agent状态  │ 用户 │
├─────────────────────────────────────────┤
│                                         │
│  ┌────────┐ ┌────────┐ ┌────────┐     │
│  │ 待办   │ │ 进行中 │ │ 已完成 │     │
│  │  (3)   │ │  (5)   │ │  (10)  │     │
│  └────────┘ └────────┘ └────────┘     │
│                                         │
│  任务卡片                               │
│  ┌─────────────────────────────────┐   │
│  │ 实现用户登录功能                 │   │
│  │ 负责人: 张开发                   │   │
│  │ 优先级: 高                       │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
"""
                }
            ],
            "interaction_flow": "交互流程说明",
            "design_spec": {
                "colors": {
                    "primary": "#1890ff",
                    "success": "#52c41a",
                    "warning": "#faad14",
                    "error": "#f5222d"
                },
                "fonts": {
                    "title": "16px bold",
                    "body": "14px regular"
                },
                "spacing": "8px grid system"
            }
        }
        
        return result
