"""
Agent 相关 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from buddy.core.database import get_db
from buddy.models import Agent, AgentStatus, AgentRole
from pydantic import BaseModel


router = APIRouter(prefix="/api/agents", tags=["agents"])


class AgentResponse(BaseModel):
    id: str
    name: str
    role: str
    status: str
    current_task: str
    capabilities: List[str]
    
    class Config:
        orm_mode = True


@router.get("/", response_model=List[AgentResponse])
def get_agents(db: Session = Depends(get_db)):
    """获取 Agent 列表"""
    agents = db.query(Agent).all()
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """获取 Agent 详情"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.get("/role/{role}", response_model=List[AgentResponse])
def get_agents_by_role(role: AgentRole, db: Session = Depends(get_db)):
    """根据角色获取 Agent 列表"""
    agents = db.query(Agent).filter(Agent.role == role).all()
    return agents


@router.get("/{agent_id}/tasks")
def get_agent_tasks(agent_id: str, db: Session = Depends(get_db)):
    """获取 Agent 的任务列表"""
    from buddy.models import Task
    tasks = db.query(Task).filter(Task.assignee == agent_id).all()
    return tasks


@router.post("/{agent_id}/activate")
def activate_agent(agent_id: str, db: Session = Depends(get_db)):
    """激活 Agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.status = AgentStatus.IDLE
    db.commit()
    return {"message": f"Agent {agent.name} activated"}
