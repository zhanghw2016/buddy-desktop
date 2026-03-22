"""
任务关系模型
"""
from sqlalchemy import Column, String
from .base import BaseModel


class TaskRelation(BaseModel):
    """任务关系模型"""
    __tablename__ = 'task_relations'
    
    source_task = Column(String(64), nullable=False, index=True, comment='源任务ID')
    target_task = Column(String(64), nullable=False, index=True, comment='目标任务ID')
    relation_type = Column(String(50), nullable=False, comment='关系类型: depends/blocks/relates')
    
    def __repr__(self):
        return f"<TaskRelation(source={self.source_task}, target={self.target_task}, type={self.relation_type})>"
