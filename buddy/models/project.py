"""
项目模型
"""
from sqlalchemy import Column, String, Text, Enum, DateTime
from .base import BaseModel
from .enums import ProjectStatus


class Project(BaseModel):
    """项目模型"""
    __tablename__ = 'projects'
    
    name = Column(String(255), nullable=False, comment='项目名称')
    description = Column(Text, comment='项目描述')
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING, comment='项目状态')
    owner = Column(String(64), comment='项目负责人')
    start_date = Column(DateTime, comment='开始日期')
    end_date = Column(DateTime, comment='结束日期')
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
