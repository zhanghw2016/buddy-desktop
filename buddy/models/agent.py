"""
Agent 模型
"""
from sqlalchemy import Column, String, Enum, JSON
from .base import BaseModel
from .enums import AgentRole, AgentStatus


class Agent(BaseModel):
    """Agent 模型"""
    __tablename__ = 'agents'
    
    name = Column(String(100), nullable=False, comment='Agent名称')
    role = Column(Enum(AgentRole), nullable=False, comment='角色')
    status = Column(Enum(AgentStatus), default=AgentStatus.IDLE, comment='状态')
    current_task = Column(String(64), comment='当前任务ID')
    capabilities = Column(JSON, default=list, comment='能力列表')
    config = Column(JSON, default=dict, comment='配置信息')
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, role={self.role}, status={self.status})>"
