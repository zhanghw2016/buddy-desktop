"""
Agent 基类
"""
import json
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from buddy.models import Agent as AgentModel, Task, Message
from buddy.models.enums import AgentStatus, AgentRole, TaskStatus, MessageType
from buddy.core.config import settings
from buddy.services.agent_bridge import get_bridge


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, agent_id: str, db: Session):
        """
        初始化 Agent
        
        Args:
            agent_id: Agent ID
            db: 数据库会话
        """
        self.db = db
        self.agent_id = agent_id
        self.agent_info = self._load_agent_info()
        self.role = self.agent_info.role
        self.name = self.agent_info.name
        self.capabilities = self.agent_info.capabilities
        self.config = self.agent_info.config
        
        # AI 桥接器 - 连接到当前会话的 AI
        self.ai_bridge = get_bridge(db)
        
    def _load_agent_info(self) -> AgentModel:
        """从数据库加载 Agent 信息"""
        agent = self.db.query(AgentModel).filter(
            AgentModel.id == self.agent_id
        ).first()
        if not agent:
            raise ValueError(f"Agent {self.agent_id} not found")
        return agent
    
    def update_status(self, status: AgentStatus):
        """更新 Agent 状态"""
        self.agent_info.status = status
        self.agent_info.updated_at = datetime.utcnow()
        self.db.commit()
        
    def set_current_task(self, task_id: Optional[str]):
        """设置当前任务"""
        self.agent_info.current_task = task_id
        self.agent_info.updated_at = datetime.utcnow()
        self.db.commit()
        
    def send_message(self, receiver_id: str, content: str, 
                     message_type: MessageType, metadata: Optional[Dict] = None):
        """发送消息给其他 Agent"""
        message = Message(
            id=str(uuid.uuid4()),
            sender=self.agent_id,
            receiver=receiver_id,
            content=content,
            type=message_type,
            metadata=metadata or {},
            read='unread'
        )
        self.db.add(message)
        self.db.commit()
        return message.id
    
    def receive_messages(self) -> List[Message]:
        """接收未读消息"""
        messages = self.db.query(Message).filter(
            Message.receiver == self.agent_id,
            Message.read == 'unread'
        ).order_by(Message.created_at).all()
        
        # 标记为已读
        for msg in messages:
            msg.read = 'read'
        self.db.commit()
        
        return messages
    
    def get_assigned_tasks(self) -> List[Task]:
        """获取分配给自己的任务"""
        tasks = self.db.query(Task).filter(
            Task.assignee == self.agent_id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        ).order_by(Task.priority, Task.due_date).all()
        return tasks
    
    def complete_task(self, task_id: str, output: Optional[Dict] = None):
        """完成任务"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.COMPLETED
            task.updated_at = datetime.utcnow()
            if output:
                task.task_metadata = {**task.task_metadata, **{'output': output}}  # 使用 task_metadata
            self.db.commit()
            
            # 清空当前任务
            if self.agent_info.current_task == task_id:
                self.set_current_task(None)
                
            # 发送任务完成消息
            # 这里可以发送给 PM Agent
            pass
    
    async def request_ai_analysis(self, task: Task, analysis_type: str) -> Dict[str, Any]:
        """
        请求 AI 分析（使用桥接器连接到我）
        
        Args:
            task: 任务对象
            analysis_type: 分析类型 (requirement/design/code/test/bug)
            
        Returns:
            请求 ID 和状态
        """
        result = await self.ai_bridge.request_analysis(
            agent_id=self.agent_id,
            task=task,
            analysis_type=analysis_type
        )
        
        print(f"[{self.name}] 已提交 AI 分析请求: {result['request_id']}")
        return result
    
    async def get_ai_response(self, request_id: str, timeout: int = 60) -> Optional[Dict[str, Any]]:
        """
        获取 AI 响应（轮询）
        
        Args:
            request_id: 请求 ID
            timeout: 超时时间（秒）
            
        Returns:
            AI 响应内容
        """
        import asyncio
        
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).seconds < timeout:
            response = await self.ai_bridge.get_response(request_id)
            if response:
                print(f"[{self.name}] 收到 AI 响应: {request_id}")
                return response
            
            # 等待 2 秒后重试
            await asyncio.sleep(2)
        
        print(f"[{self.name}] AI 响应超时: {request_id}")
        return None
    
    @abstractmethod
    def process_task(self, task: Task) -> Dict[str, Any]:
        """
        处理任务（子类实现）
        
        Args:
            task: 任务对象
            
        Returns:
            处理结果
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        获取系统提示词（子类实现）
        
        Returns:
            系统提示词
        """
        pass
    
    def work(self):
        """工作循环"""
        # 更新状态为工作状态
        self.update_status(AgentStatus.WORKING)
        
        try:
            # 接收消息
            messages = self.receive_messages()
            for msg in messages:
                self.handle_message(msg)
            
            # 获取待处理任务
            tasks = self.get_assigned_tasks()
            if tasks:
                # 处理优先级最高的任务
                task = tasks[0]
                self.set_current_task(task.id)
                
                # 更新任务状态
                task.status = TaskStatus.IN_PROGRESS
                task.updated_at = datetime.utcnow()
                self.db.commit()
                
                # 处理任务
                result = self.process_task(task)
                
                # 完成任务
                self.complete_task(task.id, result)
                
        finally:
            # 更新状态为空闲
            self.update_status(AgentStatus.IDLE)
    
    def handle_message(self, message: Message):
        """处理消息（子类可重写）"""
        # 默认实现：记录日志
        print(f"[{self.name}] 收到消息: {message.type} - {message.content[:50]}")
