"""
工作流模型
"""
from sqlalchemy import Column, String, Text, Enum, Integer, JSON
from .base import BaseModel
from .enums import WorkflowStatus


class Workflow(BaseModel):
    """工作流模型"""
    __tablename__ = 'workflows'
    
    name = Column(String(255), nullable=False, comment='工作流名称')
    description = Column(Text, comment='工作流描述')
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.PENDING, comment='状态')
    current_step = Column(Integer, default=0, comment='当前步骤')
    total_steps = Column(Integer, default=0, comment='总步骤数')
    steps = Column(JSON, default=list, comment='工作流步骤')
    context = Column(JSON, default=dict, comment='工作流上下文')
    
    def __repr__(self):
        return f"<Workflow(id={self.id}, name={self.name}, status={self.status})>"


class WorkflowStep(BaseModel):
    """工作流步骤"""
    __tablename__ = 'workflow_steps'
    
    workflow_id = Column(String(64), nullable=False, index=True, comment='工作流ID')
    name = Column(String(255), nullable=False, comment='步骤名称')
    description = Column(Text, comment='步骤描述')
    agent_role = Column(String(50), comment='执行者角色')
    action = Column(String(100), comment='动作类型')
    input_data = Column(JSON, default=dict, comment='输入数据')
    output_data = Column(JSON, default=dict, comment='输出数据')
    status = Column(String(50), default='pending', comment='步骤状态')
    order = Column(Integer, default=0, comment='步骤顺序')
    
    def __repr__(self):
        return f"<WorkflowStep(id={self.id}, name={self.name}, status={self.status})>"
