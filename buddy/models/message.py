"""
消息模型
"""
from sqlalchemy import Column, String, Text, Enum, JSON
from .base import BaseModel
from .enums import MessageType


class Message(BaseModel):
    """消息模型"""
    __tablename__ = 'messages'
    
    sender = Column(String(64), nullable=False, index=True, comment='发送者agent_id')
    receiver = Column(String(64), nullable=False, index=True, comment='接收者agent_id')
    content = Column(Text, nullable=False, comment='消息内容')
    type = Column(Enum(MessageType), nullable=False, comment='消息类型')
    message_metadata = Column(JSON, default=dict, comment='消息元数据')  # 改名为 message_metadata
    read = Column(String(10), default='unread', comment='已读状态')
    
    def __repr__(self):
        return f"<Message(id={self.id}, type={self.type}, sender={self.sender})>"
