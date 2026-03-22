"""
PM Agent - 项目经理
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from buddy.agents.base import BaseAgent
from buddy.models import Task, Project
from buddy.models.enums import TaskType, TaskPriority, TaskStatus, AgentRole


class PMAgent(BaseAgent):
    """项目经理 Agent"""
    
    def __init__(self, agent_id: str, db: Session):
        super().__init__(agent_id, db)
        if self.role != AgentRole.PM:
            raise ValueError(f"Agent {agent_id} is not a PM agent")
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是林经理，一位经验丰富的项目经理。你的职责包括：

1. **需求分析**: 理解和拆解用户需求，识别关键功能点和潜在风险
2. **项目规划**: 制定项目计划，合理安排时间和资源
3. **任务分配**: 根据团队成员的能力和负载，合理分配任务
4. **进度跟踪**: 监控项目进度，及时发现和解决问题
5. **风险管理**: 识别项目风险，制定应对策略

## 你的工作原则

- 始终以项目成功交付为目标
- 关注团队成员的工作状态和协作效率
- 及时沟通，透明化管理
- 预防问题优于解决问题

## 输出规范

你的所有输出应该结构化、清晰，包含：
- 任务标题和描述
- 优先级和预估工时
- 负责人建议
- 潜在风险和注意事项

当前项目: VDI 桌面管理系统优化
"""
    
    def process_task(self, task: Task) -> Dict[str, Any]:
        """处理任务"""
        if task.type == TaskType.REQUIREMENT:
            return self._process_requirement(task)
        elif task.type == TaskType.DOCUMENTATION:
            return self._process_documentation(task)
        else:
            return {"status": "error", "message": "不支持的 任务类型"}
    
    def _process_requirement(self, task: Task) -> Dict[str, Any]:
        """处理需求任务"""
        # TODO: 调用 AI 分析需求
        # 这里需要实现 AI 需求分析逻辑
        
        result = {
            "analysis": "需求分析结果",
            "tasks": [
                {
                    "title": "UI 设计",
                    "type": TaskType.DESIGN.value,
                    "priority": TaskPriority.HIGH.value,
                    "assignee_role": AgentRole.UI.value
                },
                {
                    "title": "后端开发",
                    "type": TaskType.DEVELOPMENT.value,
                    "priority": TaskPriority.HIGH.value,
                    "assignee_role": AgentRole.BACKEND.value
                },
                {
                    "title": "测试",
                    "type": TaskType.TEST.value,
                    "priority": TaskPriority.MEDIUM.value,
                    "assignee_role": AgentRole.QA.value
                }
            ]
        }
        
        return result
    
    def _process_documentation(self, task: Task) -> Dict[str, Any]:
        """处理文档任务"""
        # TODO: 生成项目文档
        return {
            "status": "completed",
            "document": "文档内容"
        }
    
    def create_task(self, project_id: str, title: str, description: str,
                    task_type: TaskType, priority: TaskPriority,
                    assignee_role: AgentRole, estimated_hours: float = 0) -> Task:
        """
        创建新任务
        
        Args:
            project_id: 项目 ID
            title: 任务标题
            description: 任务描述
            task_type: 任务类型
            priority: 优先级
            assignee_role: 分配给的角色
            estimated_hours: 预估工时
            
        Returns:
            创建的任务对象
        """
        import uuid
        from datetime import datetime, timedelta
        
        # 根据角色找到对应的 Agent
        from buddy.models import Agent
        assignee = self.db.query(Agent).filter(
            Agent.role == assignee_role,
            Agent.status == AgentStatus.IDLE
        ).first()
        
        task = Task(
            id=str(uuid.uuid4()),
            project_id=project_id,
            title=title,
            description=description,
            type=task_type,
            priority=priority,
            status=TaskStatus.PENDING,
            assignee=assignee.id if assignee else None,
            estimated_hours=estimated_hours,
            due_date=datetime.utcnow() + timedelta(days=7)  # 默认 7 天截止
        )
        
        self.db.add(task)
        self.db.commit()
        
        # 发送消息通知
        if assignee:
            self.send_message(
                receiver_id=assignee.id,
                content=f"新任务分配: {title}",
                message_type=MessageType.TASK_ASSIGNED,
                metadata={"task_id": task.id}
            )
        
        return task
