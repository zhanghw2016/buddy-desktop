"""
任务模型
"""
from sqlalchemy import Column, String, Text, Enum, Float, DateTime, JSON
from .base import BaseModel
from .enums import TaskType, TaskPriority, TaskStatus


class Task(BaseModel):
    """任务模型"""
    __tablename__ = 'tasks'
    
    project_id = Column(String(64), nullable=False, index=True, comment='所属项目ID')
    title = Column(String(255), nullable=False, comment='任务标题')
    description = Column(Text, comment='任务描述')
    type = Column(Enum(TaskType), default=TaskType.DEVELOPMENT, comment='任务类型')
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, comment='优先级')
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, comment='任务状态')
    assignee = Column(String(64), index=True, comment='负责人agent_id')
    estimated_hours = Column(Float, comment='预估工时')
    actual_hours = Column(Float, comment='实际工时')
    due_date = Column(DateTime, comment='截止日期')
    tags = Column(JSON, default=list, comment='标签')
    dependencies = Column(JSON, default=list, comment='依赖任务ID列表')
    task_metadata = Column(JSON, default=dict, comment='任务元数据')  # 改名为 task_metadata
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"

