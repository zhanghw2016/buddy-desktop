"""
Agent-任务关联模型
"""
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from .base import BaseModel


class AgentTask(BaseModel):
    """Agent-任务关联模型"""
    __tablename__ = 'agent_tasks'
    
    agent_id = Column(String(64), nullable=False, index=True, comment='Agent ID')
    task_id = Column(String(64), nullable=False, index=True, comment='任务 ID')
    role = Column(String(50), default='owner', comment='角色: owner/contributor/reviewer')
    assigned_at = Column(DateTime, default=datetime.utcnow, comment='分配时间')
    
    def __repr__(self):
        return f"<AgentTask(agent={self.agent_id}, task={self.task_id}, role={self.role})>"
